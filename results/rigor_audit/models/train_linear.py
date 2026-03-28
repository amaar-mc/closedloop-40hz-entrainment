"""
Train linear autoregressive models for PAC forecasting (architecture exploration).

Implements three variants:
1. Ridge regression on flattened features (simplest baseline)
2. DLinear-style decomposition model (trend + seasonal linear heads)
3. NLinear (last-value normalization + linear)

Uses PAC+Stim features (indices 61-72) from the multiscale temporal dataset.
5-seed averaging for fair comparison.
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from torch.utils.data import DataLoader, TensorDataset

# --- Constants ---
DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "processed" / "multiscale_temporal_lb20_hz5_ts1"
PAC_STIM_INDICES = list(range(61, 73))
SEEDS = [42, 123, 456, 789, 1024]
N_FEATURES = 12
LOOKBACK = 20
BATCH_SIZE = 128
LR = 1e-3
WEIGHT_DECAY = 1e-3
EPOCHS = 40
PATIENCE = 15


def load_data() -> dict:
    """Load and subset PAC+Stim features."""
    splits = {}
    for split in ["train", "val", "test"]:
        d = np.load(DATA_DIR / f"{split}_multiscale.npz", allow_pickle=True)
        x = d["x_seq"][:, :, PAC_STIM_INDICES]  # (N, 20, 12)
        y = d["y_future_norm"]
        y_raw = d["y_future"]
        splits[split] = {"x": x, "y": y, "y_raw": y_raw}

    scalers = np.load(DATA_DIR / "scalers.npz")
    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])
    return splits, yf_mean, yf_std


def denorm(y_norm: np.ndarray, mean: float, std: float) -> np.ndarray:
    return y_norm * std + mean


# ========== Model 1: Ridge Regression ==========

def train_ridge(splits: dict, yf_mean: float, yf_std: float, seed: int) -> dict:
    """Sklearn Ridge on flattened (240-dim) input with normalized targets."""
    x_train = splits["train"]["x"].reshape(len(splits["train"]["x"]), -1)
    x_val = splits["val"]["x"].reshape(len(splits["val"]["x"]), -1)
    x_test = splits["test"]["x"].reshape(len(splits["test"]["x"]), -1)

    model = Ridge(alpha=1.0, random_state=seed)
    model.fit(x_train, splits["train"]["y"])  # normalized targets

    val_pred_norm = model.predict(x_val)
    test_pred_norm = model.predict(x_test)

    val_pred = denorm(val_pred_norm, yf_mean, yf_std)
    test_pred = denorm(test_pred_norm, yf_mean, yf_std)

    return {
        "seed": seed,
        "n_params": x_train.shape[1] + 1,  # weights + bias
        "best_val_r2": float(r2_score(splits["val"]["y_raw"], val_pred)),
        "test_r2": float(r2_score(splits["test"]["y_raw"], test_pred)),
    }


# ========== Model 2: DLinear ==========

class DLinear(nn.Module):
    """DLinear: decomposition-linear model (Zeng et al., AAAI 2023).

    Decomposes input into trend (moving average) and seasonal (residual),
    applies separate linear projections, sums for prediction.
    """

    def __init__(self, seq_len: int, n_features: int, kernel_size: int = 5) -> None:
        super().__init__()
        self.seq_len = seq_len
        self.n_features = n_features
        self.kernel_size = kernel_size
        # Moving average for trend extraction
        self.avg_pool = nn.AvgPool1d(kernel_size=kernel_size, stride=1, padding=0)
        # Linear heads: flatten (seq_len, n_features) -> scalar
        self.trend_linear = nn.Linear(seq_len * n_features, 1)
        self.seasonal_linear = nn.Linear(seq_len * n_features, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, F)
        b = x.shape[0]
        # Compute trend via causal moving average (pad left only)
        x_t = x.transpose(1, 2)  # (B, F, T)
        pad_len = self.kernel_size - 1
        x_padded = nn.functional.pad(x_t, (pad_len, 0), mode="replicate")
        trend = self.avg_pool(x_padded).transpose(1, 2)  # (B, T, F)
        seasonal = x - trend

        trend_flat = trend.reshape(b, -1)
        seasonal_flat = seasonal.reshape(b, -1)

        return (self.trend_linear(trend_flat) + self.seasonal_linear(seasonal_flat)).squeeze(-1)


# ========== Model 3: NLinear ==========

class NLinear(nn.Module):
    """NLinear: last-value normalization + linear (Zeng et al., AAAI 2023).

    Subtracts the last timestep value, applies linear, adds it back.
    """

    def __init__(self, seq_len: int, n_features: int) -> None:
        super().__init__()
        self.linear = nn.Linear(seq_len * n_features, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, F)
        last = x[:, -1:, :]  # (B, 1, F)
        x_norm = x - last
        out = self.linear(x_norm.reshape(x.shape[0], -1))
        # Add back the mean of last timestep as offset
        return out.squeeze(-1) + last.mean(dim=-1).squeeze(-1) * 0  # pure linear on normalized


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def make_loaders(splits: dict, seed: int) -> tuple:
    g = torch.Generator()
    g.manual_seed(seed)
    train_ds = TensorDataset(
        torch.from_numpy(splits["train"]["x"]).float(),
        torch.from_numpy(splits["train"]["y"]).float(),
    )
    val_ds = TensorDataset(
        torch.from_numpy(splits["val"]["x"]).float(),
        torch.from_numpy(splits["val"]["y"]).float(),
    )
    test_ds = TensorDataset(
        torch.from_numpy(splits["test"]["x"]).float(),
        torch.from_numpy(splits["test"]["y"]).float(),
    )
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, generator=g)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False)
    return train_loader, val_loader, test_loader


@torch.no_grad()
def evaluate_torch(model: nn.Module, loader: DataLoader, device: torch.device) -> tuple:
    model.eval()
    preds, trues = [], []
    for x, y in loader:
        pred = model(x.to(device)).cpu().numpy()
        preds.append(pred)
        trues.append(y.numpy())
    return np.concatenate(preds), np.concatenate(trues)


def train_torch_model(
    model: nn.Module,
    splits: dict,
    yf_mean: float,
    yf_std: float,
    seed: int,
    device: torch.device,
) -> dict:
    set_seed(seed)
    model = model.to(device)
    n_params = sum(p.numel() for p in model.parameters())

    train_loader, val_loader, test_loader = make_loaders(splits, seed)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=5)
    criterion = nn.HuberLoss(delta=1.0)

    best_val_r2 = -np.inf
    best_state = None
    no_improve = 0

    for epoch in range(1, EPOCHS + 1):
        model.train()
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            pred = model(x)
            loss = criterion(pred, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        val_pred_norm, val_true_norm = evaluate_torch(model, val_loader, device)
        val_pred = denorm(val_pred_norm, yf_mean, yf_std)
        val_true = denorm(val_true_norm, yf_mean, yf_std)
        val_r2 = r2_score(val_true, val_pred)
        scheduler.step(val_r2)

        if val_r2 > best_val_r2:
            best_val_r2 = val_r2
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            no_improve = 0
        else:
            no_improve += 1

        if no_improve >= PATIENCE:
            break

    model.load_state_dict(best_state)
    model.to(device)
    test_pred_norm, test_true_norm = evaluate_torch(model, test_loader, device)
    test_pred = denorm(test_pred_norm, yf_mean, yf_std)
    test_true = denorm(test_true_norm, yf_mean, yf_std)
    test_r2 = r2_score(test_true, test_pred)

    return {
        "seed": seed,
        "n_params": n_params,
        "best_val_r2": float(best_val_r2),
        "test_r2": float(test_r2),
    }


def run_model_suite(
    model_name: str,
    model_factory,
    splits: dict,
    yf_mean: float,
    yf_std: float,
    device: torch.device,
) -> dict:
    print(f"\n--- {model_name} ---")
    seed_results = []
    for seed in SEEDS:
        t0 = time.time()
        if model_name == "Ridge":
            r = train_ridge(splits, yf_mean, yf_std, seed)
        else:
            model = model_factory()
            r = train_torch_model(model, splits, yf_mean, yf_std, seed, device)
        elapsed = time.time() - t0
        print(f"  seed={seed}: val_R2={r['best_val_r2']:.4f}, test_R2={r['test_r2']:.4f} ({elapsed:.1f}s)")
        seed_results.append(r)

    val_r2s = [r["best_val_r2"] for r in seed_results]
    test_r2s = [r["test_r2"] for r in seed_results]
    summary = {
        "model": model_name,
        "n_params": seed_results[0].get("n_params", "N/A"),
        "seeds": SEEDS,
        "val_r2_mean": float(np.mean(val_r2s)),
        "val_r2_std": float(np.std(val_r2s)),
        "test_r2_mean": float(np.mean(test_r2s)),
        "test_r2_std": float(np.std(test_r2s)),
        "per_seed": seed_results,
    }
    print(f"  {model_name} 5-seed: val_R2={summary['val_r2_mean']:.4f}+/-{summary['val_r2_std']:.4f}, "
          f"test_R2={summary['test_r2_mean']:.4f}+/-{summary['test_r2_std']:.4f}")
    return summary


def main() -> None:
    print("=" * 70)
    print("ARCHITECTURE EXPLORATION: Linear Models (Ridge, DLinear, NLinear)")
    print("=" * 70)

    device = get_device()
    print(f"Device: {device}")

    splits, yf_mean, yf_std = load_data()
    print(f"Train: {splits['train']['x'].shape}, Val: {splits['val']['x'].shape}, Test: {splits['test']['x'].shape}")

    results = {}

    # Ridge regression
    results["ridge"] = run_model_suite("Ridge", None, splits, yf_mean, yf_std, device)

    # DLinear
    results["dlinear"] = run_model_suite(
        "DLinear",
        lambda: DLinear(LOOKBACK, N_FEATURES, kernel_size=5),
        splits, yf_mean, yf_std, device,
    )

    # NLinear
    results["nlinear"] = run_model_suite(
        "NLinear",
        lambda: NLinear(LOOKBACK, N_FEATURES),
        splits, yf_mean, yf_std, device,
    )

    out_path = Path(__file__).resolve().parent / "results_linear.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
