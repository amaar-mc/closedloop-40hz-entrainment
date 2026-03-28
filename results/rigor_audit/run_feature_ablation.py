"""
Feature ablation validation for MultiscaleCausalTCN.

Trains TCN with 30 epochs on four feature subsets:
  1. All 73 features
  2. Spectral only (61 features)
  3. PAC only (7 features)
  4. PAC+Stim (12 features)

Outputs JSON summary to results/rigor_audit/feature_ablation_results.json.
"""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN


# --- Feature group definitions ---
FEATURE_SUBSETS: Dict[str, Tuple[int, int]] = {
    "all":      (0, 73),       # all features
    "spectral": (0, 61),       # spectral only
    "pac":      (61, 68),      # pac only (7 features)
    "pac_stim": (61, 73),      # pac + stim context (12 features)
}


class MaskedSequenceDataset(Dataset):
    """Load multiscale dataset with optional feature column selection."""

    def __init__(self, npz_path: Path, feature_indices: List[int]) -> None:
        d = np.load(npz_path, allow_pickle=True)
        x_full = d["x_seq"]  # (N, T, F)
        self.x = torch.from_numpy(x_full[:, :, feature_indices].copy()).float()
        self.y_future = torch.from_numpy(d["y_future_norm"]).float()
        self.y_delta = torch.from_numpy(d["y_delta_norm"]).float()
        self.last_pac = torch.from_numpy(d["last_pac"]).float()

    def __len__(self) -> int:
        return self.x.shape[0]

    def __getitem__(self, i: int) -> Dict[str, torch.Tensor]:
        return {
            "x_seq": self.x[i],
            "y_future": self.y_future[i],
            "y_delta": self.y_delta[i],
            "last_pac": self.last_pac[i],
        }


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / (ss_tot + 1e-12))


def corr_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if np.std(y_true) < 1e-12 or np.std(y_pred) < 1e-12:
        return 0.0
    return float(np.corrcoef(y_true, y_pred)[0, 1])


def denorm(y_norm: np.ndarray, mean: float, std: float) -> np.ndarray:
    return y_norm * std + mean


def train_one_epoch(
    model: MultiscaleCausalTCN,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    huber: nn.Module,
    device: torch.device,
    grad_clip: float,
) -> float:
    model.train()
    total_loss = 0.0
    n = 0
    for batch in loader:
        x = batch["x_seq"].to(device)
        y_future = batch["y_future"].to(device)

        out = model(x)
        loss = huber(out["future"], y_future)

        optimizer.zero_grad()
        loss.backward()
        if grad_clip > 0:
            nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        optimizer.step()

        total_loss += loss.item()
        n += 1
    return total_loss / max(1, n)


@torch.no_grad()
def evaluate(
    model: MultiscaleCausalTCN,
    loader: DataLoader,
    device: torch.device,
    yf_mean: float,
    yf_std: float,
) -> Dict[str, float]:
    model.eval()
    preds, trues = [], []
    for batch in loader:
        x = batch["x_seq"].to(device)
        y = batch["y_future"].cpu().numpy()
        p = model(x)["future"].cpu().numpy()
        preds.append(p)
        trues.append(y)

    preds = denorm(np.concatenate(preds), yf_mean, yf_std)
    trues = denorm(np.concatenate(trues), yf_mean, yf_std)
    return {
        "r2": r2_score(trues, preds),
        "corr": corr_score(trues, preds),
        "rmse": float(np.sqrt(np.mean((trues - preds) ** 2))),
        "mae": float(np.mean(np.abs(trues - preds))),
    }


def train_subset(
    subset_name: str,
    feature_indices: List[int],
    data_dir: Path,
    device: torch.device,
    seed: int,
    epochs: int,
    hidden: int,
    batch_size: int,
    patience: int,
) -> Dict:
    print(f"\n{'='*70}")
    print(f"TRAINING: {subset_name} ({len(feature_indices)} features)")
    print(f"{'='*70}")

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    train_ds = MaskedSequenceDataset(data_dir / "train_multiscale.npz", feature_indices)
    val_ds = MaskedSequenceDataset(data_dir / "val_multiscale.npz", feature_indices)
    test_ds = MaskedSequenceDataset(data_dir / "test_multiscale.npz", feature_indices)

    g = torch.Generator()
    g.manual_seed(seed)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0, generator=g)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    scalers = np.load(data_dir / "scalers.npz")
    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])

    n_features = len(feature_indices)
    cfg = ModelConfig(
        n_features=n_features,
        hidden=hidden,
        kernel_size=3,
        dilations=[1, 2, 4, 8],
        dropout=0.2,
        pool_type="attention",
    )
    model = MultiscaleCausalTCN(cfg).to(device)
    print(f"  Parameters: {model.count_parameters():,}")
    print(f"  Train/Val/Test: {len(train_ds):,} / {len(val_ds):,} / {len(test_ds):,}")

    huber = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-3)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=5)

    best_val_r2 = -np.inf
    best_epoch = 0
    best_state = None
    no_improve = 0
    t0 = time.time()

    for epoch in range(1, epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, huber, device, grad_clip=1.0)
        val_metrics = evaluate(model, val_loader, device, yf_mean, yf_std)
        val_r2 = val_metrics["r2"]
        scheduler.step(val_r2)

        improved = val_r2 > best_val_r2
        if improved:
            best_val_r2 = val_r2
            best_epoch = epoch
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            no_improve = 0
        else:
            no_improve += 1

        if epoch <= 3 or epoch % 10 == 0 or improved:
            mark = " *" if improved else ""
            print(f"  Epoch {epoch:03d} | loss={train_loss:.4f} | val_r2={val_r2:.4f}{mark}")

        if no_improve >= patience:
            print(f"  Early stopping at epoch {epoch}")
            break

    elapsed = time.time() - t0

    # Reload best and evaluate on test
    model.load_state_dict(best_state)
    model.to(device)
    test_metrics = evaluate(model, test_loader, device, yf_mean, yf_std)

    print(f"\n  Best epoch: {best_epoch}")
    print(f"  Val  R²: {best_val_r2:.4f}")
    print(f"  Test R²: {test_metrics['r2']:.4f}")
    print(f"  Test corr: {test_metrics['corr']:.4f}")
    print(f"  Time: {elapsed:.1f}s")

    return {
        "subset": subset_name,
        "n_features": n_features,
        "n_params": model.count_parameters(),
        "best_epoch": best_epoch,
        "val_r2": float(best_val_r2),
        "test_r2": test_metrics["r2"],
        "test_corr": test_metrics["corr"],
        "test_rmse": test_metrics["rmse"],
        "test_mae": test_metrics["mae"],
        "elapsed_sec": elapsed,
    }


def main() -> None:
    data_dir = ROOT / "data" / "processed" / "multiscale_temporal_lb20_hz5_ts1"
    output_path = ROOT / "results" / "rigor_audit" / "feature_ablation_results.json"

    seed = 42
    epochs = 30
    hidden = 64
    batch_size = 128
    patience = 20

    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"Device: {device}")

    # Load feature names to confirm indices
    d = np.load(data_dir / "train_multiscale.npz", allow_pickle=True)
    fn = [str(x) for x in d["feature_names"].tolist()]
    print(f"Total features in dataset: {len(fn)}")

    # Build index lists for each subset
    subsets: Dict[str, List[int]] = {}
    for name, (start, end) in FEATURE_SUBSETS.items():
        subsets[name] = list(range(start, end))
        print(f"  {name}: indices [{start}:{end}] = {end - start} features")
        if end - start <= 12:
            for i in range(start, end):
                print(f"    [{i}] {fn[i]}")

    results = []
    for name in ["all", "spectral", "pac", "pac_stim"]:
        result = train_subset(
            subset_name=name,
            feature_indices=subsets[name],
            data_dir=data_dir,
            device=device,
            seed=seed,
            epochs=epochs,
            hidden=hidden,
            batch_size=batch_size,
            patience=patience,
        )
        results.append(result)

    # Save results
    output_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {output_path}")

    # Summary table
    print(f"\n{'='*70}")
    print("FEATURE ABLATION SUMMARY")
    print(f"{'='*70}")
    print(f"{'Subset':<15} {'N_feat':>6} {'Val R²':>8} {'Test R²':>8} {'Test corr':>9} {'Params':>8}")
    print("-" * 60)
    for r in results:
        print(
            f"{r['subset']:<15} {r['n_features']:>6} "
            f"{r['val_r2']:>8.4f} {r['test_r2']:>8.4f} "
            f"{r['test_corr']:>9.4f} {r['n_params']:>8,}"
        )


if __name__ == "__main__":
    main()
