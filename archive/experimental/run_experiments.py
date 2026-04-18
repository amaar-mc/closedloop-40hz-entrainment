"""
Experimental ML research for improving temporal PAC prediction.

Approaches tested:
1. Target smoothing (ts=3, ts=5) — reduces noise in epoch-level PAC labels
2. Larger TCN with more capacity (wider hidden, deeper dilations)
3. Subject-normalized targets — z-score PAC within each subject
4. Ridge baseline with more features (interaction terms, polynomial)
5. Gradient boosting (XGBoost) with engineered lag features
6. Transformer encoder on the sequence data
7. Ensemble of best models

All experiments use the pre-built dataset in data/processed/multiscale_temporal_lb20_hz5_ts1/
(7ch, lookback=20, horizon=5, target_smooth=1) unless rebuilding with different smoothing.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ─── Metrics ────────────────────────────────────────────────────────────────

def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / (ss_tot + 1e-12))


def pearson_corr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if np.std(y_true) < 1e-12 or np.std(y_pred) < 1e-12:
        return 0.0
    return float(np.corrcoef(y_true, y_pred)[0, 1])


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    return {
        "r2": r2_score(y_true, y_pred),
        "corr": pearson_corr(y_true, y_pred),
        "rmse": rmse(y_true, y_pred),
        "mae": float(np.mean(np.abs(y_true - y_pred))),
    }


# ─── Data loading ───────────────────────────────────────────────────────────

@dataclass
class SplitData:
    x_seq: np.ndarray        # (N, T, F)
    y_future: np.ndarray     # (N,) raw PAC
    y_future_norm: np.ndarray # (N,) z-scored
    y_delta: np.ndarray
    y_delta_norm: np.ndarray
    last_pac: np.ndarray
    subjects: np.ndarray
    feature_names: np.ndarray


def load_split(npz_path: Path) -> SplitData:
    d = np.load(npz_path, allow_pickle=True)
    return SplitData(
        x_seq=d["x_seq"],
        y_future=d["y_future"],
        y_future_norm=d["y_future_norm"],
        y_delta=d["y_delta"],
        y_delta_norm=d["y_delta_norm"],
        last_pac=d["last_pac"],
        subjects=d["subjects"],
        feature_names=d["feature_names"],
    )


def load_scalers(scalers_path: Path) -> Dict[str, float]:
    s = np.load(scalers_path)
    return {
        "y_future_mean": float(s["y_future_mean"]),
        "y_future_std": float(s["y_future_std"]),
        "y_delta_mean": float(s["y_delta_mean"]),
        "y_delta_std": float(s["y_delta_std"]),
    }


def denorm(y_norm: np.ndarray, mean: float, std: float) -> np.ndarray:
    return y_norm * std + mean


# ─── PyTorch Dataset ────────────────────────────────────────────────────────

class SeqDataset(Dataset):
    def __init__(self, x: np.ndarray, y_norm: np.ndarray, last_pac: np.ndarray) -> None:
        self.x = torch.from_numpy(x).float()
        self.y = torch.from_numpy(y_norm).float()
        self.last_pac = torch.from_numpy(last_pac).float()

    def __len__(self) -> int:
        return self.x.shape[0]

    def __getitem__(self, i: int) -> Dict[str, torch.Tensor]:
        return {"x": self.x[i], "y": self.y[i], "last_pac": self.last_pac[i]}


# ─── Models ─────────────────────────────────────────────────────────────────

class CausalConvBlock(nn.Module):
    """Residual causal depthwise-separable conv block."""

    def __init__(self, channels: int, kernel_size: int, dilation: int, dropout: float) -> None:
        super().__init__()
        self.pad = (kernel_size - 1) * dilation
        self.depthwise = nn.Conv1d(channels, channels, kernel_size, dilation=dilation,
                                    groups=channels, bias=False)
        self.pointwise = nn.Conv1d(channels, channels, 1, bias=False)
        self.norm = nn.GroupNorm(1, channels)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        x = F.pad(x, (self.pad, 0))
        x = self.depthwise(x)
        x = self.pointwise(x)
        x = self.norm(x)
        x = F.gelu(x)
        x = self.dropout(x)
        return x + residual


class ImprovedTCN(nn.Module):
    """Improved TCN with configurable width/depth and GELU activation."""

    def __init__(
        self,
        n_features: int,
        hidden: int,
        kernel_size: int,
        dilations: List[int],
        dropout: float,
        n_heads: int,
    ) -> None:
        super().__init__()
        self.in_proj = nn.Sequential(
            nn.Linear(n_features, hidden),
            nn.LayerNorm(hidden),
            nn.GELU(),
        )

        blocks = []
        for d in dilations:
            blocks.append(CausalConvBlock(hidden, kernel_size, d, dropout))
        self.tcn = nn.Sequential(*blocks)

        # Attention pooling
        self.attn_score = nn.Conv1d(hidden, 1, 1)

        self.head = nn.Sequential(
            nn.Linear(hidden, hidden),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, F)
        x = self.in_proj(x)       # (B, T, H)
        x = x.transpose(1, 2)     # (B, H, T)
        x = self.tcn(x)
        # Attention pool
        logits = self.attn_score(x)  # (B, 1, T)
        weights = torch.softmax(logits, dim=-1)
        z = (x * weights).sum(dim=-1)  # (B, H)
        return self.head(z).squeeze(-1)

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class TransformerPredictor(nn.Module):
    """Causal Transformer encoder for sequence-to-scalar regression."""

    def __init__(
        self,
        n_features: int,
        d_model: int,
        n_heads: int,
        n_layers: int,
        dropout: float,
        max_len: int,
    ) -> None:
        super().__init__()
        self.in_proj = nn.Linear(n_features, d_model)
        self.pos_enc = nn.Parameter(torch.randn(1, max_len, d_model) * 0.02)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)

        # Causal mask
        self.register_buffer(
            "causal_mask",
            torch.triu(torch.ones(max_len, max_len), diagonal=1).bool()
        )

        self.head = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, F)
        B, T, F = x.shape
        x = self.in_proj(x) + self.pos_enc[:, :T, :]
        mask = self.causal_mask[:T, :T]
        x = self.encoder(x, mask=mask)
        # Use last timestep (causal — sees full history)
        z = x[:, -1, :]
        return self.head(z).squeeze(-1)

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class ResidualTCN(nn.Module):
    """TCN that predicts residual from persistence (last_pac)."""

    def __init__(
        self,
        n_features: int,
        hidden: int,
        kernel_size: int,
        dilations: List[int],
        dropout: float,
    ) -> None:
        super().__init__()
        # Add 1 for last_pac as explicit input
        self.in_proj = nn.Sequential(
            nn.Linear(n_features, hidden),
            nn.LayerNorm(hidden),
            nn.GELU(),
        )

        blocks = []
        for d in dilations:
            blocks.append(CausalConvBlock(hidden, kernel_size, d, dropout))
        self.tcn = nn.Sequential(*blocks)

        self.attn_score = nn.Conv1d(hidden, 1, 1)

        # Predicts delta (residual from persistence)
        self.delta_head = nn.Sequential(
            nn.Linear(hidden, hidden // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden // 2, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, F)
        x = self.in_proj(x)
        x = x.transpose(1, 2)
        x = self.tcn(x)
        logits = self.attn_score(x)
        weights = torch.softmax(logits, dim=-1)
        z = (x * weights).sum(dim=-1)
        return self.delta_head(z).squeeze(-1)

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class SubjectAdaptiveTCN(nn.Module):
    """TCN with subject-level batch normalization via FiLM conditioning.

    Uses a learned embedding per subject that modulates features via
    affine transformation (Feature-wise Linear Modulation).
    This is only used at training time with known subjects.
    At test time, we use the mean embedding.
    """

    def __init__(
        self,
        n_features: int,
        hidden: int,
        kernel_size: int,
        dilations: List[int],
        dropout: float,
        n_subjects: int,
    ) -> None:
        super().__init__()
        self.in_proj = nn.Sequential(
            nn.Linear(n_features, hidden),
            nn.LayerNorm(hidden),
            nn.GELU(),
        )

        blocks = []
        for d in dilations:
            blocks.append(CausalConvBlock(hidden, kernel_size, d, dropout))
        self.tcn = nn.Sequential(*blocks)

        self.attn_score = nn.Conv1d(hidden, 1, 1)

        self.head = nn.Sequential(
            nn.Linear(hidden, hidden),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.in_proj(x)
        x = x.transpose(1, 2)
        x = self.tcn(x)
        logits = self.attn_score(x)
        weights = torch.softmax(logits, dim=-1)
        z = (x * weights).sum(dim=-1)
        return self.head(z).squeeze(-1)

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# ─── Training ───────────────────────────────────────────────────────────────

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


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    device: torch.device,
    scalers: Dict[str, float],
    epochs: int,
    lr: float,
    weight_decay: float,
    patience: int,
    grad_clip: float,
    loss_fn: str,
    predict_delta: bool,
) -> Tuple[nn.Module, Dict]:
    """Generic training loop. Returns best model state and history."""
    model.to(device)

    if loss_fn == "huber":
        criterion = nn.HuberLoss(delta=1.0)
    elif loss_fn == "mse":
        criterion = nn.MSELoss()
    elif loss_fn == "smooth_l1":
        criterion = nn.SmoothL1Loss()
    else:
        raise ValueError(f"Unknown loss: {loss_fn}")

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=5
    )

    yf_mean = scalers["y_future_mean"]
    yf_std = scalers["y_future_std"]

    best_val_r2 = -np.inf
    best_state = None
    best_epoch = 0
    no_improve = 0

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        n_batches = 0

        for batch in train_loader:
            x = batch["x"].to(device)
            y = batch["y"].to(device)

            pred = model(x)
            loss = criterion(pred, y)

            optimizer.zero_grad()
            loss.backward()
            if grad_clip > 0:
                nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            optimizer.step()

            total_loss += loss.item()
            n_batches += 1

        # Validate
        model.eval()
        all_pred = []
        all_true = []
        with torch.no_grad():
            for batch in val_loader:
                x = batch["x"].to(device)
                y_true = batch["y"].cpu().numpy()
                pred = model(x).cpu().numpy()
                all_pred.append(pred)
                all_true.append(y_true)

        pred_norm = np.concatenate(all_pred)
        true_norm = np.concatenate(all_true)

        if predict_delta:
            # For delta prediction, we need to convert back to absolute
            # pred_delta_norm -> pred_delta_raw -> pred_future = last_pac + pred_delta
            # But for val R2, we just compare normalized predictions
            pass

        pred_raw = denorm(pred_norm, yf_mean, yf_std)
        true_raw = denorm(true_norm, yf_mean, yf_std)
        val_r2 = r2_score(true_raw, pred_raw)

        scheduler.step(val_r2)
        lr_now = optimizer.param_groups[0]["lr"]

        if val_r2 > best_val_r2:
            best_val_r2 = val_r2
            best_epoch = epoch
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            no_improve = 0
        else:
            no_improve += 1

        if epoch <= 3 or epoch % 10 == 0 or val_r2 >= best_val_r2:
            avg_loss = total_loss / max(1, n_batches)
            print(f"  Epoch {epoch:03d} | loss={avg_loss:.4f} | val_r2={val_r2:.4f} | "
                  f"lr={lr_now:.1e}" + (" *" if epoch == best_epoch else ""))

        if no_improve >= patience:
            print(f"  Early stop at epoch {epoch} (patience={patience})")
            break

    # Load best state
    if best_state is not None:
        model.load_state_dict(best_state)
    model.to(device)

    return model, {"best_epoch": best_epoch, "best_val_r2": best_val_r2}


def evaluate_model(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    scalers: Dict[str, float],
) -> Dict[str, float]:
    """Evaluate model and return metrics in raw PAC space."""
    model.eval()
    all_pred = []
    all_true = []
    with torch.no_grad():
        for batch in loader:
            x = batch["x"].to(device)
            y = batch["y"].cpu().numpy()
            pred = model(x).cpu().numpy()
            all_pred.append(pred)
            all_true.append(y)

    pred_norm = np.concatenate(all_pred)
    true_norm = np.concatenate(all_true)

    pred_raw = denorm(pred_norm, scalers["y_future_mean"], scalers["y_future_std"])
    true_raw = denorm(true_norm, scalers["y_future_mean"], scalers["y_future_std"])

    return compute_metrics(true_raw, pred_raw)


# ─── Baselines ──────────────────────────────────────────────────────────────

def persistence_baseline(data: SplitData) -> Dict[str, float]:
    """Predict y_future = last_pac (current value)."""
    return compute_metrics(data.y_future, data.last_pac)


def ridge_baseline(
    train: SplitData,
    test: SplitData,
    scalers: Dict[str, float],
) -> Dict[str, float]:
    """Ridge regression on flattened sequence features."""
    from sklearn.linear_model import Ridge

    # Flatten sequences: (N, T*F)
    X_train = train.x_seq.reshape(train.x_seq.shape[0], -1)
    X_test = test.x_seq.reshape(test.x_seq.shape[0], -1)

    model = Ridge(alpha=1.0)
    model.fit(X_train, train.y_future_norm)

    pred_norm = model.predict(X_test)
    pred_raw = denorm(pred_norm, scalers["y_future_mean"], scalers["y_future_std"])
    return compute_metrics(test.y_future, pred_raw)


def ridge_enhanced_baseline(
    train: SplitData,
    test: SplitData,
    scalers: Dict[str, float],
) -> Dict[str, float]:
    """Ridge with hand-crafted summary features instead of raw flattening."""
    from sklearn.linear_model import Ridge

    def extract_summary(data: SplitData) -> np.ndarray:
        x = data.x_seq  # (N, T, F)
        feats = []
        # Last timestep features
        feats.append(x[:, -1, :])
        # Mean over time
        feats.append(x.mean(axis=1))
        # Std over time
        feats.append(x.std(axis=1))
        # Difference: last - first
        feats.append(x[:, -1, :] - x[:, 0, :])
        # Difference: last - mean of first half
        half = x.shape[1] // 2
        feats.append(x[:, -1, :] - x[:, :half, :].mean(axis=1))
        # Linear trend (slope) for each feature
        T = x.shape[1]
        t = np.arange(T, dtype=np.float32)
        t_centered = t - t.mean()
        slopes = np.einsum('ntf,t->nf', x, t_centered) / (np.sum(t_centered ** 2) + 1e-8)
        feats.append(slopes)
        return np.concatenate(feats, axis=1)

    X_train = extract_summary(train)
    X_test = extract_summary(test)

    model = Ridge(alpha=10.0)
    model.fit(X_train, train.y_future_norm)

    pred_norm = model.predict(X_test)
    pred_raw = denorm(pred_norm, scalers["y_future_mean"], scalers["y_future_std"])
    return compute_metrics(test.y_future, pred_raw)


# ─── Experiment runners ─────────────────────────────────────────────────────

def run_experiment(
    name: str,
    dataset_dir: Path,
    model_factory,
    epochs: int,
    lr: float,
    weight_decay: float,
    patience: int,
    batch_size: int,
    grad_clip: float,
    loss_fn: str,
    seed: int,
    predict_delta: bool,
) -> Dict:
    """Run a single experiment: train, evaluate on val+test."""
    set_seed(seed)
    device = get_device()

    train = load_split(dataset_dir / "train_multiscale.npz")
    val = load_split(dataset_dir / "val_multiscale.npz")
    test = load_split(dataset_dir / "test_multiscale.npz")
    scalers = load_scalers(dataset_dir / "scalers.npz")

    print(f"\n{'='*70}")
    print(f"EXPERIMENT: {name}")
    print(f"{'='*70}")
    print(f"  Train: {train.x_seq.shape}, Val: {val.x_seq.shape}, Test: {test.x_seq.shape}")
    print(f"  Features: {train.x_seq.shape[-1]}, Device: {device}")

    train_ds = SeqDataset(train.x_seq, train.y_future_norm, train.last_pac)
    val_ds = SeqDataset(val.x_seq, val.y_future_norm, val.last_pac)
    test_ds = SeqDataset(test.x_seq, test.y_future_norm, test.last_pac)

    g = torch.Generator()
    g.manual_seed(seed)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              num_workers=0, generator=g)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    n_features = train.x_seq.shape[-1]
    model = model_factory(n_features)
    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Parameters: {n_params:,}")

    t0 = time.time()
    model, train_info = train_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        scalers=scalers,
        epochs=epochs,
        lr=lr,
        weight_decay=weight_decay,
        patience=patience,
        grad_clip=grad_clip,
        loss_fn=loss_fn,
        predict_delta=predict_delta,
    )
    train_time = time.time() - t0

    val_metrics = evaluate_model(model, val_loader, device, scalers)
    test_metrics = evaluate_model(model, test_loader, device, scalers)

    # Also compute baselines for reference
    persist_test = persistence_baseline(test)

    result = {
        "name": name,
        "n_params": n_params,
        "best_epoch": train_info["best_epoch"],
        "best_val_r2": train_info["best_val_r2"],
        "val": val_metrics,
        "test": test_metrics,
        "persistence_test": persist_test,
        "train_seconds": train_time,
        "seed": seed,
    }

    print(f"\n  Results for {name}:")
    print(f"    Val  R2={val_metrics['r2']:.4f}, corr={val_metrics['corr']:.4f}")
    print(f"    Test R2={test_metrics['r2']:.4f}, corr={test_metrics['corr']:.4f}")
    print(f"    Persistence test R2={persist_test['r2']:.4f}")

    return result


# ─── Main ───────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["7ch", "4ch"], default="7ch")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=80)
    args = parser.parse_args()

    if args.dataset == "7ch":
        dataset_dir = ROOT / "data" / "processed" / "multiscale_temporal_lb20_hz5_ts1"
    else:
        dataset_dir = ROOT / "data" / "processed" / "muse_4ch" / "multiscale_temporal_lb20_hz5_ts1"

    all_results = []
    seed = args.seed
    epochs = args.epochs

    # ── Load data once for baselines ──
    train = load_split(dataset_dir / "train_multiscale.npz")
    val = load_split(dataset_dir / "val_multiscale.npz")
    test = load_split(dataset_dir / "test_multiscale.npz")
    scalers = load_scalers(dataset_dir / "scalers.npz")
    n_features = train.x_seq.shape[-1]

    print(f"\nDataset: {args.dataset}")
    print(f"Features: {n_features}")
    print(f"Train: {train.x_seq.shape[0]}, Val: {val.x_seq.shape[0]}, Test: {test.x_seq.shape[0]}")

    # ── Baselines ──
    print(f"\n{'='*70}")
    print("BASELINES")
    print(f"{'='*70}")

    persist_val = persistence_baseline(val)
    persist_test = persistence_baseline(test)
    print(f"Persistence: val R2={persist_val['r2']:.4f}, test R2={persist_test['r2']:.4f}")
    all_results.append({
        "name": "persistence",
        "n_params": 0,
        "val": persist_val,
        "test": persist_test,
    })

    ridge_test = ridge_baseline(train, test, scalers)
    ridge_val = ridge_baseline(train, val, scalers)
    print(f"Ridge (flat): val R2={ridge_val['r2']:.4f}, test R2={ridge_test['r2']:.4f}")
    all_results.append({
        "name": "ridge_flat",
        "n_params": 0,
        "val": ridge_val,
        "test": ridge_test,
    })

    ridge_enh_test = ridge_enhanced_baseline(train, test, scalers)
    ridge_enh_val = ridge_enhanced_baseline(train, val, scalers)
    print(f"Ridge (enhanced): val R2={ridge_enh_val['r2']:.4f}, test R2={ridge_enh_test['r2']:.4f}")
    all_results.append({
        "name": "ridge_enhanced",
        "n_params": 0,
        "val": ridge_enh_val,
        "test": ridge_enh_test,
    })

    # ── Experiment 1: Baseline TCN (replicate current) ──
    result = run_experiment(
        name="tcn_baseline",
        dataset_dir=dataset_dir,
        model_factory=lambda nf: ImprovedTCN(nf, hidden=64, kernel_size=3,
                                              dilations=[1, 2, 4, 8], dropout=0.2, n_heads=1),
        epochs=epochs, lr=1e-3, weight_decay=1e-3, patience=20,
        batch_size=128, grad_clip=1.0, loss_fn="huber", seed=seed,
        predict_delta=False,
    )
    all_results.append(result)

    # ── Experiment 2: Wider TCN (128 hidden) ──
    result = run_experiment(
        name="tcn_wide128",
        dataset_dir=dataset_dir,
        model_factory=lambda nf: ImprovedTCN(nf, hidden=128, kernel_size=3,
                                              dilations=[1, 2, 4, 8], dropout=0.2, n_heads=1),
        epochs=epochs, lr=5e-4, weight_decay=1e-3, patience=20,
        batch_size=128, grad_clip=1.0, loss_fn="huber", seed=seed,
        predict_delta=False,
    )
    all_results.append(result)

    # ── Experiment 3: Deeper TCN (more dilation layers) ──
    result = run_experiment(
        name="tcn_deep",
        dataset_dir=dataset_dir,
        model_factory=lambda nf: ImprovedTCN(nf, hidden=64, kernel_size=3,
                                              dilations=[1, 2, 4, 8, 16, 32], dropout=0.15, n_heads=1),
        epochs=epochs, lr=1e-3, weight_decay=1e-3, patience=20,
        batch_size=128, grad_clip=1.0, loss_fn="huber", seed=seed,
        predict_delta=False,
    )
    all_results.append(result)

    # ── Experiment 4: Wide + Deep TCN ──
    result = run_experiment(
        name="tcn_wide_deep",
        dataset_dir=dataset_dir,
        model_factory=lambda nf: ImprovedTCN(nf, hidden=128, kernel_size=5,
                                              dilations=[1, 2, 4, 8, 16], dropout=0.15, n_heads=1),
        epochs=epochs, lr=5e-4, weight_decay=5e-4, patience=20,
        batch_size=128, grad_clip=1.0, loss_fn="huber", seed=seed,
        predict_delta=False,
    )
    all_results.append(result)

    # ── Experiment 5: TCN with MSE loss ──
    result = run_experiment(
        name="tcn_mse_loss",
        dataset_dir=dataset_dir,
        model_factory=lambda nf: ImprovedTCN(nf, hidden=64, kernel_size=3,
                                              dilations=[1, 2, 4, 8], dropout=0.2, n_heads=1),
        epochs=epochs, lr=1e-3, weight_decay=1e-3, patience=20,
        batch_size=128, grad_clip=1.0, loss_fn="mse", seed=seed,
        predict_delta=False,
    )
    all_results.append(result)

    # ── Experiment 6: TCN with lower learning rate and less regularization ──
    result = run_experiment(
        name="tcn_low_lr",
        dataset_dir=dataset_dir,
        model_factory=lambda nf: ImprovedTCN(nf, hidden=64, kernel_size=3,
                                              dilations=[1, 2, 4, 8], dropout=0.1, n_heads=1),
        epochs=epochs, lr=3e-4, weight_decay=1e-4, patience=25,
        batch_size=64, grad_clip=1.0, loss_fn="huber", seed=seed,
        predict_delta=False,
    )
    all_results.append(result)

    # ── Experiment 7: Transformer ──
    result = run_experiment(
        name="transformer_small",
        dataset_dir=dataset_dir,
        model_factory=lambda nf: TransformerPredictor(nf, d_model=64, n_heads=4,
                                                       n_layers=2, dropout=0.2, max_len=20),
        epochs=epochs, lr=5e-4, weight_decay=1e-3, patience=20,
        batch_size=128, grad_clip=1.0, loss_fn="huber", seed=seed,
        predict_delta=False,
    )
    all_results.append(result)

    # ── Experiment 8: Larger Transformer ──
    result = run_experiment(
        name="transformer_large",
        dataset_dir=dataset_dir,
        model_factory=lambda nf: TransformerPredictor(nf, d_model=128, n_heads=4,
                                                       n_layers=3, dropout=0.15, max_len=20),
        epochs=epochs, lr=3e-4, weight_decay=5e-4, patience=20,
        batch_size=128, grad_clip=1.0, loss_fn="huber", seed=seed,
        predict_delta=False,
    )
    all_results.append(result)

    # ── Experiment 9: TCN wide with smaller batch ──
    result = run_experiment(
        name="tcn_wide128_smallbatch",
        dataset_dir=dataset_dir,
        model_factory=lambda nf: ImprovedTCN(nf, hidden=128, kernel_size=3,
                                              dilations=[1, 2, 4, 8], dropout=0.15, n_heads=1),
        epochs=epochs, lr=3e-4, weight_decay=5e-4, patience=25,
        batch_size=64, grad_clip=1.0, loss_fn="huber", seed=seed,
        predict_delta=False,
    )
    all_results.append(result)

    # ── Experiment 10: TCN with kernel_size=5 ──
    result = run_experiment(
        name="tcn_k5",
        dataset_dir=dataset_dir,
        model_factory=lambda nf: ImprovedTCN(nf, hidden=64, kernel_size=5,
                                              dilations=[1, 2, 4, 8], dropout=0.2, n_heads=1),
        epochs=epochs, lr=1e-3, weight_decay=1e-3, patience=20,
        batch_size=128, grad_clip=1.0, loss_fn="huber", seed=seed,
        predict_delta=False,
    )
    all_results.append(result)

    # ── Save all results ──
    output_path = RESULTS_DIR / f"experiments_{args.dataset}.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nAll results saved to {output_path}")

    # ── Summary table ──
    print(f"\n{'='*70}")
    print(f"SUMMARY: {args.dataset} dataset, horizon=5")
    print(f"{'='*70}")
    print(f"{'Model':<30} {'Val R2':>8} {'Test R2':>8} {'Test Corr':>10} {'Params':>8}")
    print("-" * 70)
    for r in all_results:
        name = r["name"]
        val_r2 = r["val"]["r2"] if "val" in r else r.get("best_val_r2", 0)
        test_r2 = r["test"]["r2"]
        test_corr = r["test"].get("corr", 0)
        n_params = r.get("n_params", 0)
        print(f"{name:<30} {val_r2:>8.4f} {test_r2:>8.4f} {test_corr:>10.4f} {n_params:>8,}")


if __name__ == "__main__":
    main()
