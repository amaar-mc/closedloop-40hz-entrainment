"""
Train LSTM and GRU models for PAC forecasting (architecture exploration).

Uses PAC+Stim features (indices 61-72) from the multiscale temporal dataset.
Predicts future PAC 5 seconds ahead from 20 timesteps of 12 features.

Trains both LSTM and GRU variants with 5-seed averaging for fair comparison.
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import r2_score
from torch.utils.data import DataLoader, TensorDataset

# --- Constants ---
DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "processed" / "multiscale_temporal_lb20_hz5_ts1"
PAC_STIM_INDICES = list(range(61, 73))  # 12 features: 7 PAC-derived + 5 stim context
SEEDS = [42, 123, 456, 789, 1024]
N_FEATURES = 12
LOOKBACK = 20
HIDDEN_SIZE = 64
NUM_LAYERS = 2
DROPOUT = 0.2
BATCH_SIZE = 128
LR = 1e-3
WEIGHT_DECAY = 1e-3
EPOCHS = 40
PATIENCE = 15
GRAD_CLIP = 1.0


def load_data() -> dict:
    """Load and subset PAC+Stim features from the multiscale dataset."""
    splits = {}
    for split in ["train", "val", "test"]:
        d = np.load(DATA_DIR / f"{split}_multiscale.npz", allow_pickle=True)
        x = d["x_seq"][:, :, PAC_STIM_INDICES]  # (N, 20, 12)
        y = d["y_future_norm"]                    # (N,)
        y_raw = d["y_future"]                     # (N,) unnormalized
        splits[split] = {"x": x, "y": y, "y_raw": y_raw}

    scalers = np.load(DATA_DIR / "scalers.npz")
    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])
    return splits, yf_mean, yf_std


class LSTMRegressor(nn.Module):
    """LSTM-based PAC forecaster."""

    def __init__(self, rnn_type: str) -> None:
        super().__init__()
        rnn_cls = nn.LSTM if rnn_type == "lstm" else nn.GRU
        self.rnn = rnn_cls(
            input_size=N_FEATURES,
            hidden_size=HIDDEN_SIZE,
            num_layers=NUM_LAYERS,
            batch_first=True,
            dropout=DROPOUT if NUM_LAYERS > 1 else 0.0,
        )
        self.head = nn.Sequential(
            nn.Linear(HIDDEN_SIZE, HIDDEN_SIZE),
            nn.SiLU(),
            nn.Dropout(DROPOUT),
            nn.Linear(HIDDEN_SIZE, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, F)
        out, _ = self.rnn(x)           # (B, T, H)
        last = out[:, -1, :]           # (B, H) - take last timestep
        return self.head(last).squeeze(-1)  # (B,)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if hasattr(torch.backends, "mps"):
        pass  # MPS doesn't have separate seed
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


def denorm(y_norm: np.ndarray, mean: float, std: float) -> np.ndarray:
    return y_norm * std + mean


@torch.no_grad()
def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> tuple:
    model.eval()
    preds, trues = [], []
    for x, y in loader:
        x = x.to(device)
        pred = model(x).cpu().numpy()
        preds.append(pred)
        trues.append(y.numpy())
    return np.concatenate(preds), np.concatenate(trues)


def train_single_run(
    rnn_type: str,
    splits: dict,
    yf_mean: float,
    yf_std: float,
    seed: int,
    device: torch.device,
) -> dict:
    set_seed(seed)
    model = LSTMRegressor(rnn_type).to(device)
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
            nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
            optimizer.step()

        # Validation
        val_pred_norm, val_true_norm = evaluate(model, val_loader, device)
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

    # Test with best model
    model.load_state_dict(best_state)
    model.to(device)
    test_pred_norm, test_true_norm = evaluate(model, test_loader, device)
    test_pred = denorm(test_pred_norm, yf_mean, yf_std)
    test_true = denorm(test_true_norm, yf_mean, yf_std)
    test_r2 = r2_score(test_true, test_pred)

    return {
        "seed": seed,
        "n_params": n_params,
        "best_val_r2": float(best_val_r2),
        "test_r2": float(test_r2),
    }


def main() -> None:
    print("=" * 70)
    print("ARCHITECTURE EXPLORATION: LSTM & GRU")
    print("=" * 70)

    device = get_device()
    print(f"Device: {device}")

    splits, yf_mean, yf_std = load_data()
    print(f"Train: {splits['train']['x'].shape}, Val: {splits['val']['x'].shape}, Test: {splits['test']['x'].shape}")

    results = {}
    for rnn_type in ["lstm", "gru"]:
        print(f"\n--- {rnn_type.upper()} ---")
        seed_results = []
        for seed in SEEDS:
            t0 = time.time()
            r = train_single_run(rnn_type, splits, yf_mean, yf_std, seed, device)
            elapsed = time.time() - t0
            print(f"  seed={seed}: val_R2={r['best_val_r2']:.4f}, test_R2={r['test_r2']:.4f} ({elapsed:.1f}s)")
            seed_results.append(r)

        val_r2s = [r["best_val_r2"] for r in seed_results]
        test_r2s = [r["test_r2"] for r in seed_results]
        summary = {
            "model": rnn_type.upper(),
            "n_params": seed_results[0]["n_params"],
            "seeds": SEEDS,
            "val_r2_mean": float(np.mean(val_r2s)),
            "val_r2_std": float(np.std(val_r2s)),
            "test_r2_mean": float(np.mean(test_r2s)),
            "test_r2_std": float(np.std(test_r2s)),
            "per_seed": seed_results,
        }
        results[rnn_type] = summary
        print(f"  {rnn_type.upper()} 5-seed: val_R2={summary['val_r2_mean']:.4f}+/-{summary['val_r2_std']:.4f}, "
              f"test_R2={summary['test_r2_mean']:.4f}+/-{summary['test_r2_std']:.4f}")

    out_path = Path(__file__).resolve().parent / "results_lstm_gru.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
