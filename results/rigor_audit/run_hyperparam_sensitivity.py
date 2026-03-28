"""
Hyperparameter sensitivity sweep for MultiscaleCausalTCN.

Tests whether the TCN result is robust across hyperparameter choices or
fragile to a specific setting.

Sweep axes (one at a time, others at default):
  - Hidden sizes: 16, 32, 64 (default), 128
  - Dropout rates: 0.1, 0.2 (default), 0.3, 0.4
  - Learning rates: 5e-4, 1e-3 (default), 2e-3

Uses PAC+Stim features (indices 61-72, 12 features) which is the
operationally deployed configuration (test R2 ~ 0.57 with seed=42).

Also runs the full 73-feature hidden sweep for comparison.

Outputs JSON to results/rigor_audit/hyperparam_sensitivity_results.json.
"""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN


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


def run_single_config(
    run_name: str,
    feature_indices: List[int],
    data_dir: Path,
    device: torch.device,
    seed: int,
    epochs: int,
    batch_size: int,
    patience: int,
    hidden: int,
    dropout: float,
    lr: float,
    weight_decay: float,
) -> Dict:
    """Train and evaluate a single configuration."""
    print(f"\n{'='*60}")
    print(f"RUN: {run_name}")
    print(f"  hidden={hidden}, dropout={dropout}, lr={lr}")
    print(f"{'='*60}")

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    n_features = len(feature_indices)
    train_ds = MaskedSequenceDataset(data_dir / "train_multiscale.npz", feature_indices)
    val_ds = MaskedSequenceDataset(data_dir / "val_multiscale.npz", feature_indices)
    test_ds = MaskedSequenceDataset(data_dir / "test_multiscale.npz", feature_indices)

    g = torch.Generator()
    g.manual_seed(seed)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              num_workers=0, generator=g)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    scalers = np.load(data_dir / "scalers.npz")
    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])

    cfg = ModelConfig(
        n_features=n_features,
        hidden=hidden,
        kernel_size=3,
        dilations=[1, 2, 4, 8],
        dropout=dropout,
        pool_type="attention",
    )
    model = MultiscaleCausalTCN(cfg).to(device)
    n_params = model.count_parameters()
    print(f"  Parameters: {n_params:,}")

    huber = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=5
    )

    best_val_r2 = -np.inf
    best_epoch = 0
    best_state = None
    no_improve = 0
    t0 = time.time()

    for epoch in range(1, epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, huber, device,
                                     grad_clip=1.0)
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

    print(f"  Best epoch: {best_epoch}, Val R2: {best_val_r2:.4f}, "
          f"Test R2: {test_metrics['r2']:.4f}, Time: {elapsed:.1f}s")

    return {
        "run_name": run_name,
        "n_features": n_features,
        "n_params": n_params,
        "hidden": hidden,
        "dropout": dropout,
        "lr": lr,
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
    output_path = ROOT / "results" / "rigor_audit" / "hyperparam_sensitivity_results.json"

    seed = 42
    epochs = 30
    batch_size = 128
    patience = 20
    weight_decay = 1e-3

    # Default hyperparameters
    default_hidden = 64
    default_dropout = 0.2
    default_lr = 1e-3

    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"Device: {device}")

    # Feature indices for PAC+Stim (12 features) — the deployed configuration
    pac_stim_indices = list(range(61, 73))
    # Full feature set (73 features) — for comparison
    all_indices = list(range(0, 73))

    all_results = []

    # ---------------------------------------------------------------
    # SWEEP 1: Hidden size (PAC+Stim features)
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SWEEP 1: Hidden Size (PAC+Stim, 12 features)")
    print("=" * 70)
    for hidden in [16, 32, 64, 128]:
        result = run_single_config(
            run_name=f"pac_stim_hidden{hidden}",
            feature_indices=pac_stim_indices,
            data_dir=data_dir,
            device=device,
            seed=seed,
            epochs=epochs,
            batch_size=batch_size,
            patience=patience,
            hidden=hidden,
            dropout=default_dropout,
            lr=default_lr,
            weight_decay=weight_decay,
        )
        result["sweep"] = "hidden"
        result["feature_set"] = "pac_stim"
        all_results.append(result)

    # ---------------------------------------------------------------
    # SWEEP 2: Dropout rate (PAC+Stim features)
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SWEEP 2: Dropout Rate (PAC+Stim, 12 features)")
    print("=" * 70)
    for dropout in [0.1, 0.2, 0.3, 0.4]:
        result = run_single_config(
            run_name=f"pac_stim_drop{dropout}",
            feature_indices=pac_stim_indices,
            data_dir=data_dir,
            device=device,
            seed=seed,
            epochs=epochs,
            batch_size=batch_size,
            patience=patience,
            hidden=default_hidden,
            dropout=dropout,
            lr=default_lr,
            weight_decay=weight_decay,
        )
        result["sweep"] = "dropout"
        result["feature_set"] = "pac_stim"
        all_results.append(result)

    # ---------------------------------------------------------------
    # SWEEP 3: Learning rate (PAC+Stim features)
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SWEEP 3: Learning Rate (PAC+Stim, 12 features)")
    print("=" * 70)
    for lr in [5e-4, 1e-3, 2e-3]:
        result = run_single_config(
            run_name=f"pac_stim_lr{lr}",
            feature_indices=pac_stim_indices,
            data_dir=data_dir,
            device=device,
            seed=seed,
            epochs=epochs,
            batch_size=batch_size,
            patience=patience,
            hidden=default_hidden,
            dropout=default_dropout,
            lr=lr,
            weight_decay=weight_decay,
        )
        result["sweep"] = "lr"
        result["feature_set"] = "pac_stim"
        all_results.append(result)

    # ---------------------------------------------------------------
    # SWEEP 4: Hidden size (all 73 features, for comparison)
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SWEEP 4: Hidden Size (All 73 features, comparison)")
    print("=" * 70)
    for hidden in [16, 32, 64, 128]:
        result = run_single_config(
            run_name=f"all_hidden{hidden}",
            feature_indices=all_indices,
            data_dir=data_dir,
            device=device,
            seed=seed,
            epochs=epochs,
            batch_size=batch_size,
            patience=patience,
            hidden=hidden,
            dropout=default_dropout,
            lr=default_lr,
            weight_decay=weight_decay,
        )
        result["sweep"] = "hidden"
        result["feature_set"] = "all"
        all_results.append(result)

    # Save all results
    output_path.write_text(json.dumps(all_results, indent=2))
    print(f"\nAll results saved to {output_path}")

    # Summary tables
    print(f"\n{'='*70}")
    print("HYPERPARAMETER SENSITIVITY SUMMARY")
    print(f"{'='*70}")

    for sweep_name in ["hidden", "dropout", "lr"]:
        sweep_results = [r for r in all_results
                         if r["sweep"] == sweep_name and r["feature_set"] == "pac_stim"]
        if not sweep_results:
            continue
        print(f"\n--- {sweep_name.upper()} sweep (PAC+Stim) ---")
        print(f"{'Config':<25} {'Params':>8} {'Val R2':>8} {'Test R2':>8} {'Corr':>7}")
        print("-" * 60)
        for r in sweep_results:
            print(f"{r['run_name']:<25} {r['n_params']:>8,} "
                  f"{r['val_r2']:>8.4f} {r['test_r2']:>8.4f} {r['test_corr']:>7.4f}")

    # All-features comparison
    print(f"\n--- HIDDEN sweep (All 73 features) ---")
    print(f"{'Config':<25} {'Params':>8} {'Val R2':>8} {'Test R2':>8} {'Corr':>7}")
    print("-" * 60)
    for r in [r for r in all_results if r["feature_set"] == "all"]:
        print(f"{r['run_name']:<25} {r['n_params']:>8,} "
              f"{r['val_r2']:>8.4f} {r['test_r2']:>8.4f} {r['test_corr']:>7.4f}")


if __name__ == "__main__":
    main()
