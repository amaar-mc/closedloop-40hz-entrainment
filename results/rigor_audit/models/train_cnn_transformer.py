"""
Train 1D CNN and lightweight Transformer for PAC forecasting (architecture exploration).

Uses PAC+Stim features (indices 61-72) from the multiscale temporal dataset.
5-seed averaging for fair comparison.
"""

from __future__ import annotations

import json
import math
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
PAC_STIM_INDICES = list(range(61, 73))
SEEDS = [42, 123, 456, 789, 1024]
N_FEATURES = 12
LOOKBACK = 20
HIDDEN_SIZE = 64
BATCH_SIZE = 128
LR = 1e-3
WEIGHT_DECAY = 1e-3
DROPOUT = 0.2
EPOCHS = 40
PATIENCE = 15
GRAD_CLIP = 1.0


def load_data() -> dict:
    splits = {}
    for split in ["train", "val", "test"]:
        d = np.load(DATA_DIR / f"{split}_multiscale.npz", allow_pickle=True)
        x = d["x_seq"][:, :, PAC_STIM_INDICES]
        y = d["y_future_norm"]
        y_raw = d["y_future"]
        splits[split] = {"x": x, "y": y, "y_raw": y_raw}

    scalers = np.load(DATA_DIR / "scalers.npz")
    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])
    return splits, yf_mean, yf_std


def denorm(y_norm: np.ndarray, mean: float, std: float) -> np.ndarray:
    return y_norm * std + mean


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


# ========== Model 1: Simple 1D CNN ==========

class SimpleCNN1D(nn.Module):
    """1D CNN with causal convolutions for time series regression.

    Applies causal padding so each position only sees current and past.
    """

    def __init__(self) -> None:
        super().__init__()
        # Causal conv blocks
        self.conv1 = nn.Conv1d(N_FEATURES, HIDDEN_SIZE, kernel_size=3, padding=0)
        self.conv2 = nn.Conv1d(HIDDEN_SIZE, HIDDEN_SIZE, kernel_size=3, padding=0)
        self.conv3 = nn.Conv1d(HIDDEN_SIZE, HIDDEN_SIZE, kernel_size=3, padding=0)
        self.norm1 = nn.GroupNorm(1, HIDDEN_SIZE)
        self.norm2 = nn.GroupNorm(1, HIDDEN_SIZE)
        self.norm3 = nn.GroupNorm(1, HIDDEN_SIZE)
        self.dropout = nn.Dropout(DROPOUT)
        self.head = nn.Sequential(
            nn.Linear(HIDDEN_SIZE, HIDDEN_SIZE),
            nn.SiLU(),
            nn.Dropout(DROPOUT),
            nn.Linear(HIDDEN_SIZE, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, F) -> transpose to (B, F, T)
        x = x.transpose(1, 2)

        # Causal conv: pad left only
        x = nn.functional.pad(x, (2, 0))
        x = nn.functional.silu(self.norm1(self.conv1(x)))
        x = self.dropout(x)

        x = nn.functional.pad(x, (2, 0))
        x = nn.functional.silu(self.norm2(self.conv2(x)))
        x = self.dropout(x)

        x = nn.functional.pad(x, (2, 0))
        x = nn.functional.silu(self.norm3(self.conv3(x)))
        x = self.dropout(x)

        # Global average pooling over time
        x = x.mean(dim=-1)  # (B, H)
        return self.head(x).squeeze(-1)


# ========== Model 2: Lightweight Transformer ==========

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 100) -> None:
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))  # (1, max_len, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, :x.size(1), :]


class LightTransformer(nn.Module):
    """Lightweight causal Transformer encoder for time series regression.

    Uses causal attention mask so each position attends only to itself and past.
    Small: 2 layers, 4 heads, d_model=64.
    """

    def __init__(self) -> None:
        super().__init__()
        d_model = HIDDEN_SIZE
        self.in_proj = nn.Linear(N_FEATURES, d_model)
        self.pos_enc = PositionalEncoding(d_model, max_len=LOOKBACK + 10)
        self.norm_in = nn.LayerNorm(d_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=4,
            dim_feedforward=d_model * 2,
            dropout=DROPOUT,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=2)

        self.head = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.SiLU(),
            nn.Dropout(DROPOUT),
            nn.Linear(d_model, 1),
        )

    def _causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """Generate causal attention mask (upper triangle = -inf)."""
        mask = torch.triu(torch.ones(seq_len, seq_len, device=device), diagonal=1)
        mask = mask.masked_fill(mask == 1, float("-inf"))
        return mask

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, F)
        x = self.in_proj(x)
        x = self.pos_enc(x)
        x = self.norm_in(x)

        mask = self._causal_mask(x.size(1), x.device)
        x = self.encoder(x, mask=mask)

        # Use last position (causal: sees all history)
        last = x[:, -1, :]  # (B, d_model)
        return self.head(last).squeeze(-1)


# ========== Training Loop ==========

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
def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> tuple:
    model.eval()
    preds, trues = [], []
    for x, y in loader:
        pred = model(x.to(device)).cpu().numpy()
        preds.append(pred)
        trues.append(y.numpy())
    return np.concatenate(preds), np.concatenate(trues)


def train_single_run(
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
            nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
            optimizer.step()

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
    print("ARCHITECTURE EXPLORATION: 1D CNN & Transformer")
    print("=" * 70)

    device = get_device()
    print(f"Device: {device}")

    splits, yf_mean, yf_std = load_data()
    print(f"Train: {splits['train']['x'].shape}, Val: {splits['val']['x'].shape}, Test: {splits['test']['x'].shape}")

    results = {}

    for model_name, model_factory in [
        ("SimpleCNN1D", SimpleCNN1D),
        ("LightTransformer", LightTransformer),
    ]:
        print(f"\n--- {model_name} ---")
        seed_results = []
        for seed in SEEDS:
            t0 = time.time()
            set_seed(seed)
            model = model_factory()
            r = train_single_run(model, splits, yf_mean, yf_std, seed, device)
            elapsed = time.time() - t0
            print(f"  seed={seed}: val_R2={r['best_val_r2']:.4f}, test_R2={r['test_r2']:.4f} ({elapsed:.1f}s)")
            seed_results.append(r)

        val_r2s = [r["best_val_r2"] for r in seed_results]
        test_r2s = [r["test_r2"] for r in seed_results]
        summary = {
            "model": model_name,
            "n_params": seed_results[0]["n_params"],
            "seeds": SEEDS,
            "val_r2_mean": float(np.mean(val_r2s)),
            "val_r2_std": float(np.std(val_r2s)),
            "test_r2_mean": float(np.mean(test_r2s)),
            "test_r2_std": float(np.std(test_r2s)),
            "per_seed": seed_results,
        }
        results[model_name.lower()] = summary
        print(f"  {model_name} 5-seed: val_R2={summary['val_r2_mean']:.4f}+/-{summary['val_r2_std']:.4f}, "
              f"test_R2={summary['test_r2_mean']:.4f}+/-{summary['test_r2_std']:.4f}")

    out_path = Path(__file__).resolve().parent / "results_cnn_transformer.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
