"""
Baseline and comparison model architectures for the architecture comparison study.

Provides SimpleLSTM, SimpleTransformer, and XGBoost wrappers alongside a generic
PyTorch training loop so that all sequence models are evaluated under identical
conditions (same datasets, same early stopping, same seed).

See run_comparison_study.py for the CLI orchestrator that trains and evaluates all
six architectures (persistence, Ridge, LSTM, XGBoost, Transformer, TCN) across
prediction horizons 1,3,5,8,10s.
"""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any, Dict

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parents[1]

# Re-use utilities from the existing training module to avoid duplication.
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from temporal_multiscale.train_multiscale_tcn import (
    SequenceDataset,
    _denorm,
    _metrics,
    _r2,
)

# _rmse is not exported from train_multiscale_tcn; define it locally.
def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


# ---------------------------------------------------------------------------
# Seed helper
# ---------------------------------------------------------------------------

def set_seed(seed: int) -> None:
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# ---------------------------------------------------------------------------
# SimpleLSTM
# ---------------------------------------------------------------------------

class SimpleLSTM(nn.Module):
    """
    Two-layer LSTM for sequence-to-scalar PAC prediction.

    Input:  (B, T, F)  — batch of feature sequences
    Output: (B,)       — scalar future PAC predictions
    """

    def __init__(
        self,
        n_features: int,
        hidden: int = 64,
        num_layers: int = 2,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        # LSTM requires dropout=0 when num_layers==1
        lstm_dropout = dropout if num_layers > 1 else 0.0
        self.lstm = nn.LSTM(
            n_features,
            hidden,
            num_layers=num_layers,
            batch_first=True,
            dropout=lstm_dropout,
        )
        self.head = nn.Sequential(
            nn.LayerNorm(hidden),
            nn.Linear(hidden, hidden),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, F)
        out, _ = self.lstm(x)   # out: (B, T, H)
        last = out[:, -1, :]    # (B, H) — last timestep only
        return self.head(last).squeeze(-1)  # (B,)


# ---------------------------------------------------------------------------
# SimpleTransformer
# ---------------------------------------------------------------------------

class SimpleTransformer(nn.Module):
    """
    Causal Transformer encoder for sequence-to-scalar PAC prediction.

    A causal attention mask (upper-triangular, True = do-not-attend) prevents
    future positions from influencing predictions at earlier timesteps.

    Input:  (B, T, F)
    Output: (B,)
    """

    def __init__(
        self,
        n_features: int,
        d_model: int = 64,
        nhead: int = 4,
        num_layers: int = 2,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.in_proj = nn.Linear(n_features, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 2,
            dropout=dropout,
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.head = nn.Linear(d_model, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, F)
        T = x.size(1)
        # Causal mask: True positions are blocked (cannot attend forward in time)
        mask = torch.triu(torch.ones(T, T, device=x.device), diagonal=1).bool()
        h = self.in_proj(x)                       # (B, T, d_model)
        h = self.encoder(h, mask=mask)             # (B, T, d_model)
        last = h[:, -1, :]                         # (B, d_model) — last position
        return self.head(last).squeeze(-1)         # (B,)


# ---------------------------------------------------------------------------
# Generic PyTorch training loop
# ---------------------------------------------------------------------------

def train_pytorch_model(
    model: nn.Module,
    train_ds: SequenceDataset,
    val_ds: SequenceDataset,
    test_ds: SequenceDataset,
    scalers: Any,
    device: torch.device,
    epochs: int = 80,
    batch_size: int = 128,
    lr: float = 1e-3,
    weight_decay: float = 1e-3,
    patience: int = 20,
    grad_clip: float = 1.0,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Train any nn.Module that takes (B, T, F) and outputs (B,) scalar predictions.

    Uses HuberLoss, AdamW, and ReduceLROnPlateau with early stopping.
    Evaluates on denormalized predictions to report test R2/RMSE in raw PAC units.

    Returns a dict with: model_name, n_params, best_epoch, val_r2, test_r2,
    test_rmse, test_corr, train_seconds.
    """
    set_seed(seed)

    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])

    g = torch.Generator()
    g.manual_seed(seed)
    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True, num_workers=0, generator=g
    )
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    model = model.to(device)
    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    model_name = type(model).__name__

    criterion = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=5
    )

    best_val_r2 = -np.inf
    best_state = None
    best_epoch = 0
    no_improve = 0
    t0 = time.time()

    for epoch in range(1, epochs + 1):
        # --- train ---
        model.train()
        for batch in train_loader:
            x = batch["x_seq"].to(device)
            y = batch["y_future"].to(device)
            pred = model(x)
            loss = criterion(pred, y)
            optimizer.zero_grad()
            loss.backward()
            if grad_clip > 0:
                nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            optimizer.step()

        # --- validate ---
        val_r2 = _eval_r2_norm(model, val_loader, device)
        scheduler.step(val_r2)

        if val_r2 > best_val_r2:
            best_val_r2 = val_r2
            best_epoch = epoch
            no_improve = 0
            # Save a CPU copy of state dict to avoid holding GPU memory
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            no_improve += 1

        if no_improve >= patience:
            break

    # --- test with best checkpoint ---
    if best_state is not None:
        model.load_state_dict(best_state)
    model.to(device)

    test_metrics = _eval_denorm(model, test_loader, device, yf_mean, yf_std)
    train_seconds = float(time.time() - t0)

    return {
        "model_name": model_name,
        "n_params": n_params,
        "best_epoch": best_epoch,
        "val_r2": float(best_val_r2),
        "test_r2": float(test_metrics["r2"]),
        "test_rmse": float(test_metrics["rmse"]),
        "test_corr": float(test_metrics["corr"]),
        "train_seconds": train_seconds,
    }


@torch.no_grad()
def _eval_r2_norm(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
) -> float:
    """Evaluate R² on normalized targets (for early stopping)."""
    model.eval()
    preds = []
    trues = []
    for batch in loader:
        x = batch["x_seq"].to(device)
        y = batch["y_future"].cpu().numpy()
        p = model(x).cpu().numpy()
        preds.append(p)
        trues.append(y)
    preds = np.concatenate(preds)
    trues = np.concatenate(trues)
    return _r2(trues, preds)


@torch.no_grad()
def _eval_denorm(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    yf_mean: float,
    yf_std: float,
) -> Dict[str, float]:
    """Evaluate metrics on denormalized predictions in raw PAC units."""
    model.eval()
    preds_norm = []
    trues_norm = []
    for batch in loader:
        x = batch["x_seq"].to(device)
        y = batch["y_future"].cpu().numpy()
        p = model(x).cpu().numpy()
        preds_norm.append(p)
        trues_norm.append(y)
    preds_norm = np.concatenate(preds_norm)
    trues_norm = np.concatenate(trues_norm)
    preds = _denorm(preds_norm, yf_mean, yf_std)
    trues = _denorm(trues_norm, yf_mean, yf_std)
    return _metrics(trues, preds)


# ---------------------------------------------------------------------------
# XGBoost
# ---------------------------------------------------------------------------

def train_xgboost_model(
    dataset_dir: Path,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Train XGBoost on flattened (N, T*F) feature sequences.

    Targets are RAW y_future values (not z-scored) loaded directly from NPZ.
    x_seq is already normalized but XGBoost is invariant to input scaling.
    Uses train for fitting, val for early stopping, and reports test metrics.

    Returns the same summary dict format as train_pytorch_model.
    """
    train_npz = np.load(dataset_dir / "train_multiscale.npz", allow_pickle=True)
    val_npz = np.load(dataset_dir / "val_multiscale.npz", allow_pickle=True)
    test_npz = np.load(dataset_dir / "test_multiscale.npz", allow_pickle=True)

    # Flatten sequences: (N, T, F) -> (N, T*F)
    x_train = train_npz["x_seq"].astype(np.float32).reshape(train_npz["x_seq"].shape[0], -1)
    x_val = val_npz["x_seq"].astype(np.float32).reshape(val_npz["x_seq"].shape[0], -1)
    x_test = test_npz["x_seq"].astype(np.float32).reshape(test_npz["x_seq"].shape[0], -1)

    # Use RAW y_future (not y_future_norm) as targets
    y_train = train_npz["y_future"].astype(np.float64)
    y_val = val_npz["y_future"].astype(np.float64)
    y_test = test_npz["y_future"].astype(np.float64)

    t0 = time.time()
    model = XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        n_jobs=-1,
        verbosity=0,
        random_state=seed,
        early_stopping_rounds=20,
        eval_metric="rmse",
    )
    model.fit(x_train, y_train, eval_set=[(x_val, y_val)], verbose=False)
    train_seconds = float(time.time() - t0)

    y_pred = model.predict(x_test).astype(np.float64)
    test_metrics = _metrics(y_test, y_pred)
    n_params = int(model.best_ntree_limit) if hasattr(model, "best_ntree_limit") else 300

    return {
        "model_name": "XGBoost",
        "n_params": n_params,
        "best_epoch": getattr(model, "best_iteration", 0),
        "val_r2": float(_r2(y_val, model.predict(x_val).astype(np.float64))),
        "test_r2": float(test_metrics["r2"]),
        "test_rmse": float(test_metrics["rmse"]),
        "test_corr": float(test_metrics["corr"]),
        "train_seconds": train_seconds,
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    for Model, name, kwargs in [
        (SimpleLSTM, "LSTM", {"n_features": 49}),
        (SimpleTransformer, "Transformer", {"n_features": 49}),
    ]:
        m = Model(**kwargs)
        x = torch.randn(4, 20, 49)
        y = m(x)
        params = sum(p.numel() for p in m.parameters())
        assert y.shape == (4,), f"{name} output shape wrong: {y.shape}"
        print(f"[PASS] {name}: output={y.shape}, params={params:,}")
    print("[PASS] All model shape checks passed")
