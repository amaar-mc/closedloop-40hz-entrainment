"""
Train and compare TCN models on epoch-level vs sliding-window PAC targets.

Trains the same MultiscaleCausalTCN architecture (h=64, dilations [1,2,4,8])
on both the original epoch-level PAC dataset (12 PAC+Stim features) and the
new sliding-window PAC dataset. Reports side-by-side metrics.

Comparison axes:
    - Number of unique target values
    - Persistence R2 (last-value baseline)
    - Ridge R2 (linear baseline)
    - TCN test R2
    - TCN test R2 on cross-epoch transitions only (original dataset)
"""

from __future__ import annotations

import json
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN


# -- Dataset -----------------------------------------------------------------

class SeqDataset(Dataset):
    """Sequence dataset loading from npz."""

    def __init__(self, npz_path: Path) -> None:
        d = np.load(npz_path, allow_pickle=True)
        self.x = torch.from_numpy(d["x_seq"]).float()
        self.y_future = torch.from_numpy(d["y_future_norm"]).float()
        self.y_delta = torch.from_numpy(d["y_delta_norm"]).float()
        self.last_pac = torch.from_numpy(d["last_pac"]).float()
        self.y_future_raw = d["y_future"].astype(np.float64)
        self.last_pac_raw = d["last_pac"].astype(np.float64)

    def __len__(self) -> int:
        return self.x.shape[0]

    def __getitem__(self, i: int) -> Dict[str, torch.Tensor]:
        return {
            "x_seq": self.x[i],
            "y_future": self.y_future[i],
            "y_delta": self.y_delta[i],
            "last_pac": self.last_pac[i],
        }


# -- Metrics -----------------------------------------------------------------

def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / (ss_tot + 1e-12))


def _corr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if np.std(y_true) < 1e-12 or np.std(y_pred) < 1e-12:
        return 0.0
    return float(np.corrcoef(y_true, y_pred)[0, 1])


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def _denorm(y_norm: np.ndarray, mean: float, std: float) -> np.ndarray:
    return y_norm * std + mean


# -- Persistence and Ridge baselines ----------------------------------------

def persistence_baseline(ds: SeqDataset, yf_mean: float, yf_std: float) -> Dict[str, float]:
    """Last-value baseline: predict y_future = last_pac (current)."""
    y_true = ds.y_future_raw
    y_pred = ds.last_pac_raw
    return {
        "r2": _r2(y_true, y_pred),
        "corr": _corr(y_true, y_pred),
        "rmse": _rmse(y_true, y_pred),
    }


def ridge_baseline(
    train_ds: SeqDataset,
    test_ds: SeqDataset,
    yf_mean: float,
    yf_std: float,
    alpha: float,
) -> Dict[str, float]:
    """Ridge regression on flattened sequence features."""
    from sklearn.linear_model import Ridge

    X_train = train_ds.x.numpy().reshape(len(train_ds), -1)
    y_train = train_ds.y_future.numpy()
    X_test = test_ds.x.numpy().reshape(len(test_ds), -1)

    model = Ridge(alpha=alpha)
    model.fit(X_train, y_train)
    pred_norm = model.predict(X_test)
    pred_raw = _denorm(pred_norm, yf_mean, yf_std)
    y_true = test_ds.y_future_raw

    return {
        "r2": _r2(y_true, pred_raw),
        "corr": _corr(y_true, pred_raw),
        "rmse": _rmse(y_true, pred_raw),
    }


# -- Training ----------------------------------------------------------------

def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


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
    n_batches = 0

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
        n_batches += 1

    return total_loss / max(1, n_batches)


@torch.no_grad()
def evaluate_model(
    model: MultiscaleCausalTCN,
    loader: DataLoader,
    device: torch.device,
    yf_mean: float,
    yf_std: float,
) -> Dict[str, float]:
    model.eval()
    preds_norm = []
    trues_norm = []

    for batch in loader:
        x = batch["x_seq"].to(device)
        y = batch["y_future"].cpu().numpy()
        out = model(x)
        preds_norm.append(out["future"].cpu().numpy())
        trues_norm.append(y)

    preds_norm = np.concatenate(preds_norm)
    trues_norm = np.concatenate(trues_norm)

    preds_raw = _denorm(preds_norm, yf_mean, yf_std)
    trues_raw = _denorm(trues_norm, yf_mean, yf_std)

    return {
        "r2": _r2(trues_raw, preds_raw),
        "corr": _corr(trues_raw, preds_raw),
        "rmse": _rmse(trues_raw, preds_raw),
    }


def train_tcn(
    dataset_dir: Path,
    name: str,
    seed: int,
    epochs: int,
    batch_size: int,
    hidden: int,
    lr: float,
    weight_decay: float,
    patience: int,
    device: torch.device,
) -> Dict:
    """Train TCN on a dataset and return results."""
    set_seed(seed)

    train_ds = SeqDataset(dataset_dir / "train_multiscale.npz")
    val_ds = SeqDataset(dataset_dir / "val_multiscale.npz")
    test_ds = SeqDataset(dataset_dir / "test_multiscale.npz")

    scalers = np.load(dataset_dir / "scalers.npz")
    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])

    meta = json.loads((dataset_dir / "metadata.json").read_text())
    n_features = int(meta["n_features"])

    g = torch.Generator()
    g.manual_seed(seed)
    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True, num_workers=0, generator=g
    )
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    cfg = ModelConfig(
        n_features=n_features,
        hidden=hidden,
        kernel_size=3,
        dilations=[1, 2, 4, 8],
        dropout=0.2,
        pool_type="attention",
    )
    model = MultiscaleCausalTCN(cfg)
    model.to(device)

    huber = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=5
    )

    best_val_r2 = -np.inf
    best_epoch = 0
    no_improve = 0
    best_state = None

    t0 = time.time()
    for epoch in range(1, epochs + 1):
        train_loss = train_one_epoch(
            model, train_loader, optimizer, huber, device, grad_clip=1.0
        )
        val_metrics = evaluate_model(model, val_loader, device, yf_mean, yf_std)
        val_r2 = val_metrics["r2"]
        scheduler.step(val_r2)

        if val_r2 > best_val_r2:
            best_val_r2 = val_r2
            best_epoch = epoch
            no_improve = 0
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            no_improve += 1

        if epoch <= 5 or epoch % 10 == 0 or val_r2 == best_val_r2:
            lr_now = optimizer.param_groups[0]["lr"]
            mark = " *" if val_r2 == best_val_r2 else ""
            print(f"    [{name}] Ep {epoch:03d} loss={train_loss:.4f} "
                  f"val_r2={val_r2:.4f} lr={lr_now:.1e}{mark}")

        if no_improve >= patience:
            print(f"    [{name}] Early stopping at epoch {epoch}")
            break

    train_time = time.time() - t0

    # Evaluate best model on test
    model.load_state_dict(best_state)
    model.to(device)
    test_metrics = evaluate_model(model, test_loader, device, yf_mean, yf_std)

    # Baselines
    persist = persistence_baseline(test_ds, yf_mean, yf_std)
    ridge = ridge_baseline(train_ds, test_ds, yf_mean, yf_std, alpha=1.0)

    # Target statistics
    y_test = test_ds.y_future_raw
    n_unique_targets = int(len(np.unique(y_test)))
    adjacent_same = int(np.sum(np.abs(np.diff(y_test)) < 1e-12))
    adjacent_same_pct = float(100 * adjacent_same / max(1, len(y_test) - 1))

    return {
        "name": name,
        "n_features": n_features,
        "n_params": model.count_parameters(),
        "n_train": len(train_ds),
        "n_val": len(val_ds),
        "n_test": len(test_ds),
        "best_epoch": best_epoch,
        "best_val_r2": float(best_val_r2),
        "test_metrics": test_metrics,
        "persistence": persist,
        "ridge": ridge,
        "n_unique_targets": n_unique_targets,
        "adjacent_same_pct": adjacent_same_pct,
        "train_seconds": train_time,
    }


# -- Cross-epoch transition analysis ----------------------------------------

def analyze_cross_epoch_transitions(
    dataset_dir: Path,
    model_state: Dict,
    cfg: ModelConfig,
    device: torch.device,
) -> Dict[str, float] | None:
    """
    Evaluate TCN only on samples where the target crosses an epoch boundary.

    For epoch-level PAC, "cross-epoch" means y_future != last_pac.
    These are the truly hard predictions. Returns None if dataset doesn't
    have enough transitions.
    """
    test_ds = SeqDataset(dataset_dir / "test_multiscale.npz")
    y_true = test_ds.y_future_raw
    last_pac = test_ds.last_pac_raw

    # Cross-epoch = target differs from current PAC
    diff = np.abs(y_true - last_pac)
    cross_mask = diff > 1e-12
    n_cross = int(np.sum(cross_mask))

    if n_cross < 10:
        return None

    scalers = np.load(dataset_dir / "scalers.npz")
    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])

    model = MultiscaleCausalTCN(cfg)
    model.load_state_dict(model_state)
    model.to(device)
    model.eval()

    # Get all predictions
    loader = DataLoader(test_ds, batch_size=256, shuffle=False, num_workers=0)
    all_preds = []
    with torch.no_grad():
        for batch in loader:
            x = batch["x_seq"].to(device)
            out = model(x)
            all_preds.append(out["future"].cpu().numpy())
    all_preds = _denorm(np.concatenate(all_preds), yf_mean, yf_std)

    cross_true = y_true[cross_mask]
    cross_pred = all_preds[cross_mask]
    cross_persist = last_pac[cross_mask]

    return {
        "n_transitions": n_cross,
        "n_total": len(y_true),
        "pct_transitions": float(100 * n_cross / len(y_true)),
        "tcn_r2": _r2(cross_true, cross_pred),
        "persistence_r2": _r2(cross_true, cross_persist),
    }


# -- Main comparison ---------------------------------------------------------

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(
        description="Train and compare epoch-level vs sliding-window PAC."
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--hidden", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-3)
    parser.add_argument("--patience", type=int, default=20)
    parser.add_argument(
        "--original-dir", type=str,
        default="experimental/sliding_pac/dataset_original",
        help="Path to epoch-level PAC dataset with 12 features",
    )
    parser.add_argument(
        "--sliding-dir", type=str,
        default="experimental/sliding_pac/dataset",
        help="Path to sliding-window PAC dataset with 12 features",
    )
    parser.add_argument(
        "--output-dir", type=str,
        default="experimental/sliding_pac/results",
    )
    args = parser.parse_args()

    device = get_device()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("SLIDING PAC vs EPOCH PAC -- TCN COMPARISON")
    print("=" * 70)
    print(f"  Device:  {device}")
    print(f"  Seed:    {args.seed}")
    print(f"  Epochs:  {args.epochs}")
    print()

    results = {}

    # -- Train on original (epoch-level) PAC --
    original_dir = Path(args.original_dir)
    if (original_dir / "metadata.json").exists():
        print("\n--- EPOCH-LEVEL PAC ---")
        results["epoch"] = train_tcn(
            dataset_dir=original_dir,
            name="epoch_pac",
            seed=args.seed,
            epochs=args.epochs,
            batch_size=args.batch_size,
            hidden=args.hidden,
            lr=args.lr,
            weight_decay=args.weight_decay,
            patience=args.patience,
            device=device,
        )
    else:
        print(f"[WARN] Original dataset not found at {original_dir}, skipping.")

    # -- Train on sliding-window PAC --
    sliding_dir = Path(args.sliding_dir)
    if (sliding_dir / "metadata.json").exists():
        print("\n--- SLIDING-WINDOW PAC ---")
        results["sliding"] = train_tcn(
            dataset_dir=sliding_dir,
            name="sliding_pac",
            seed=args.seed,
            epochs=args.epochs,
            batch_size=args.batch_size,
            hidden=args.hidden,
            lr=args.lr,
            weight_decay=args.weight_decay,
            patience=args.patience,
            device=device,
        )
    else:
        print(f"[WARN] Sliding dataset not found at {sliding_dir}, skipping.")

    # -- Summary table --
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)
    print(f"{'Metric':<30} {'Epoch PAC':>15} {'Sliding PAC':>15}")
    print("-" * 62)

    for key, label in [
        ("n_unique_targets", "Unique targets (test)"),
        ("adjacent_same_pct", "Adjacent same (%)"),
        ("n_train", "Train samples"),
        ("n_test", "Test samples"),
    ]:
        vals = []
        for ds_key in ["epoch", "sliding"]:
            if ds_key in results:
                v = results[ds_key].get(key, "N/A")
                vals.append(f"{v}" if isinstance(v, int) else f"{v:.1f}")
            else:
                vals.append("N/A")
        print(f"{label:<30} {vals[0]:>15} {vals[1]:>15}")

    print()
    for metric_group, metric_label in [
        ("persistence", "Persistence R2"),
        ("ridge", "Ridge R2"),
        ("test_metrics", "TCN Test R2"),
    ]:
        vals = []
        for ds_key in ["epoch", "sliding"]:
            if ds_key in results:
                m = results[ds_key].get(metric_group, {})
                r2 = m.get("r2", float("nan"))
                vals.append(f"{r2:.4f}")
            else:
                vals.append("N/A")
        print(f"{metric_label:<30} {vals[0]:>15} {vals[1]:>15}")

    for metric_group, metric_label in [
        ("persistence", "Persistence corr"),
        ("ridge", "Ridge corr"),
        ("test_metrics", "TCN Test corr"),
    ]:
        vals = []
        for ds_key in ["epoch", "sliding"]:
            if ds_key in results:
                m = results[ds_key].get(metric_group, {})
                c = m.get("corr", float("nan"))
                vals.append(f"{c:.4f}")
            else:
                vals.append("N/A")
        print(f"{metric_label:<30} {vals[0]:>15} {vals[1]:>15}")

    # -- Save --
    results_path = output_dir / "comparison_results.json"
    results_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nResults saved to: {results_path}")


if __name__ == "__main__":
    main()
