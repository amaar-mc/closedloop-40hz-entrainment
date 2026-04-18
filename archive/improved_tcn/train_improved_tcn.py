"""
Train ImprovedTCN on enhanced multiscale datasets.

Key differences from train_multiscale_tcn.py:
- Loads ImprovedTCN instead of MultiscaleCausalTCN.
- EnhancedSequenceDataset computes per-subject causal smoothed targets for auxiliary head.
- Multi-task loss: Huber(future) + lambda_smooth*Huber(smooth) + lambda_delta*Huber(delta)
  + lambda_consistency*consistency_penalty.
- Evaluation uses only the future head (apples-to-apples vs baseline).
- Saves results/improved_tcn_{dataset}.json with delta_r2 vs baseline.

Usage:
    python improved_tcn/train_improved_tcn.py \\
      --dataset-dir data/processed/enhanced_multiscale_7ch \\
      --models-dir models/improved_tcn \\
      --run-name improved_tcn_7ch_hz5 \\
      --horizon 5 --lookback 20 --target-smooth-window 1 \\
      --lambda-smooth 0.3 --lambda-delta 0.3 --lambda-consistency 0.1 \\
      --n-attn-heads 4 --attn-layers 1 \\
      --epochs 80 --patience 20 --batch-size 128 --lr 1e-3 \\
      --seed 42 --allow-metadata-mismatch \\
      --compare-baseline results/comparison_table_7ch.json
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from improved_tcn.improved_tcn_model import ImprovedModelConfig, ImprovedTCN


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class EnhancedSequenceDataset(Dataset):
    """Loads enhanced multiscale NPZ and computes per-subject causal smoothed targets.

    The smoothed target is a causal moving average of y_future_norm computed
    within each subject's contiguous block to avoid cross-subject contamination.
    This provides a cleaner training signal: the shared backbone learns to
    represent the underlying PAC trend rather than instantaneous noise.
    """

    def __init__(self, npz_path: Path, smooth_window: int = 5) -> None:
        d = np.load(npz_path, allow_pickle=True)
        self.x = torch.from_numpy(d["x_seq"]).float()
        self.y_future = torch.from_numpy(d["y_future_norm"]).float()
        self.y_delta = torch.from_numpy(d["y_delta_norm"]).float()
        self.last_pac = torch.from_numpy(d["last_pac"]).float()
        subjects = d["subjects"]

        y_smooth = self._compute_per_subject_smooth(d["y_future_norm"], subjects, smooth_window)
        self.y_smooth = torch.from_numpy(y_smooth).float()

    @staticmethod
    def _compute_per_subject_smooth(
        y_future: np.ndarray,
        subjects: np.ndarray,
        window: int,
    ) -> np.ndarray:
        """Apply causal trailing mean within each subject block.

        Causal (trailing) average: position i uses y[max(0, i-window+1) : i+1].
        This preserves temporal causality and prevents cross-subject bleed.
        """
        y_smooth = np.empty_like(y_future, dtype=np.float64)
        unique_subjects = np.unique(subjects)
        for subj in unique_subjects:
            mask = subjects == subj
            indices = np.where(mask)[0]
            y_subj = y_future[indices].astype(np.float64)
            y_s = np.empty_like(y_subj)
            for i in range(len(y_subj)):
                start = max(0, i - window + 1)
                y_s[i] = y_subj[start : i + 1].mean()
            y_smooth[indices] = y_s
        return y_smooth.astype(np.float32)

    def __len__(self) -> int:
        return self.x.shape[0]

    def __getitem__(self, i: int) -> Dict[str, torch.Tensor]:
        return {
            "x_seq": self.x[i],
            "y_future": self.y_future[i],
            "y_delta": self.y_delta[i],
            "last_pac": self.last_pac[i],
            "y_smooth": self.y_smooth[i],
        }


# ---------------------------------------------------------------------------
# Metrics helpers
# ---------------------------------------------------------------------------

def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / (ss_tot + 1e-12))


def _corr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if np.std(y_true) < 1e-12 or np.std(y_pred) < 1e-12:
        return 0.0
    return float(np.corrcoef(y_true, y_pred)[0, 1])


def _metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    return {
        "r2": _r2(y_true, y_pred),
        "corr": _corr(y_true, y_pred),
        "mae": float(np.mean(np.abs(y_true - y_pred))),
        "rmse": float(np.sqrt(np.mean((y_true - y_pred) ** 2))),
    }


def _denorm(y_norm: np.ndarray, mean: float, std: float) -> np.ndarray:
    return y_norm * std + mean


# ---------------------------------------------------------------------------
# Train / eval loops
# ---------------------------------------------------------------------------

def train_one_epoch(
    model: ImprovedTCN,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    huber: nn.Module,
    device: torch.device,
    yf_mean: float,
    yf_std: float,
    yd_mean: float,
    yd_std: float,
    lambda_smooth: float,
    lambda_delta: float,
    lambda_consistency: float,
    grad_clip: float,
) -> Dict[str, float]:
    model.train()
    total_loss = 0.0
    n_batches = 0

    for batch in loader:
        x = batch["x_seq"].to(device)
        y_future = batch["y_future"].to(device)
        y_delta = batch["y_delta"].to(device)
        last_pac = batch["last_pac"].to(device)
        y_smooth = batch["y_smooth"].to(device)

        out = model(x)
        pred_future = out["future"]
        pred_delta = out["delta"]
        pred_smooth = out["smooth"]

        loss_future = huber(pred_future, y_future)
        loss_delta = huber(pred_delta, y_delta)
        # Auxiliary smoothed-target loss: drives backbone toward trend-capturing representations.
        loss_smooth = huber(pred_smooth, y_smooth)

        # Consistency in raw PAC space: future_raw ≈ current_raw + delta_raw
        pred_future_raw = pred_future * yf_std + yf_mean
        pred_delta_raw = pred_delta * yd_std + yd_mean
        loss_consistency = torch.mean((pred_future_raw - (last_pac + pred_delta_raw)) ** 2)

        loss = (
            loss_future
            + lambda_smooth * loss_smooth
            + lambda_delta * loss_delta
            + lambda_consistency * loss_consistency
        )

        optimizer.zero_grad()
        loss.backward()
        if grad_clip > 0:
            nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        optimizer.step()

        total_loss += float(loss.item())
        n_batches += 1

    return {"loss": total_loss / max(1, n_batches)}


@torch.no_grad()
def evaluate(
    model: ImprovedTCN,
    loader: DataLoader,
    device: torch.device,
    yf_mean: float,
    yf_std: float,
    yd_mean: float,
    yd_std: float,
) -> Dict[str, Dict[str, float]]:
    """Evaluate on future and delta heads only. smooth head is auxiliary / training-only."""
    model.eval()
    future_pred_norm: List[np.ndarray] = []
    future_true_norm: List[np.ndarray] = []
    delta_pred_norm: List[np.ndarray] = []
    delta_true_norm: List[np.ndarray] = []

    for batch in loader:
        x = batch["x_seq"].to(device)
        y_future = batch["y_future"].cpu().numpy()
        y_delta = batch["y_delta"].cpu().numpy()

        out = model(x)
        future_pred_norm.append(out["future"].cpu().numpy())
        future_true_norm.append(y_future)
        delta_pred_norm.append(out["delta"].cpu().numpy())
        delta_true_norm.append(y_delta)

    fp = np.concatenate(future_pred_norm)
    ft = np.concatenate(future_true_norm)
    dp = np.concatenate(delta_pred_norm)
    dt = np.concatenate(delta_true_norm)

    return {
        "future": _metrics(_denorm(ft, yf_mean, yf_std), _denorm(fp, yf_mean, yf_std)),
        "delta": _metrics(_denorm(dt, yd_mean, yd_std), _denorm(dp, yd_mean, yd_std)),
    }


# ---------------------------------------------------------------------------
# Baseline extraction
# ---------------------------------------------------------------------------

def get_baseline_tcn_r2(comparison_json: Path, horizon: int) -> Optional[float]:
    """Extract TCN test_r2 at a given horizon from a comparison table JSON.

    Returns None if the entry is not found.
    """
    if not comparison_json.exists():
        return None
    data = json.loads(comparison_json.read_text())
    for entry in data:
        model_id = entry.get("model", "") or entry.get("model_name", "")
        entry_horizon = int(entry.get("horizon", -1))
        if "tcn" in str(model_id).lower() and entry_horizon == horizon:
            return float(entry.get("test_r2", entry.get("test_future_r2", 0.0)))
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train ImprovedTCN with multi-task smoothing.")
    p.add_argument("--dataset-dir", default="data/processed/enhanced_multiscale_7ch", type=str)
    p.add_argument("--models-dir", default="models/improved_tcn", type=str)
    p.add_argument("--results-dir", default="results", type=str)
    p.add_argument("--run-name", default="", type=str)
    p.add_argument("--allow-metadata-mismatch", action="store_true")
    p.add_argument("--compare-baseline", default="results/comparison_table_7ch.json", type=str,
                   help="Path to comparison table JSON for baseline TCN R2 delta computation.")
    p.add_argument("--dataset-tag", default="", type=str,
                   help="Short label for the output JSON filename (e.g. '7ch' or '4ch'). "
                        "Inferred from --run-name if empty.")

    # Dataset args
    p.add_argument("--lookback", default=20, type=int)
    p.add_argument("--horizon", default=5, type=int)
    p.add_argument("--target-smooth-window", default=1, type=int,
                   help="Dataset target smoothing (metadata check).")
    p.add_argument("--smooth-window", default=5, type=int,
                   help="Window size for per-subject auxiliary smoothed target computation.")

    # Architecture args
    p.add_argument("--hidden", default=64, type=int)
    p.add_argument("--dropout", default=0.2, type=float)
    p.add_argument("--kernel-size", default=3, type=int)
    p.add_argument("--dilations", default="1,2,4,8", type=str)
    p.add_argument("--pool-type", default="attention", type=str,
                   choices=["attention", "last_step"])
    p.add_argument("--n-attn-heads", default=4, type=int)
    p.add_argument("--attn-layers", default=1, type=int)
    p.add_argument("--no-self-attention", action="store_true",
                   help="Disable temporal self-attention (ablation mode).")

    # Training args
    p.add_argument("--epochs", default=80, type=int)
    p.add_argument("--batch-size", default=128, type=int)
    p.add_argument("--lr", default=1e-3, type=float)
    p.add_argument("--weight-decay", default=1e-3, type=float)
    p.add_argument("--patience", default=20, type=int)
    p.add_argument("--grad-clip", default=1.0, type=float)
    p.add_argument("--lambda-smooth", default=0.3, type=float)
    p.add_argument("--lambda-delta", default=0.3, type=float)
    p.add_argument("--lambda-consistency", default=0.1, type=float)
    p.add_argument("--seed", default=42, type=int)

    return p.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    dataset_dir = Path(args.dataset_dir)
    models_dir = Path(args.models_dir)
    results_dir = Path(args.results_dir)
    models_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    if not (dataset_dir / "metadata.json").exists():
        raise FileNotFoundError(
            f"Dataset metadata not found at {dataset_dir / 'metadata.json'}. "
            "Build the enhanced dataset with improved_tcn/build_enhanced_dataset.py first."
        )

    meta = json.loads((dataset_dir / "metadata.json").read_text())
    if not args.allow_metadata_mismatch:
        mismatches = []
        if int(meta.get("lookback", args.lookback)) != int(args.lookback):
            mismatches.append(f"lookback(meta={meta.get('lookback')}, arg={args.lookback})")
        if int(meta.get("horizon", args.horizon)) != int(args.horizon):
            mismatches.append(f"horizon(meta={meta.get('horizon')}, arg={args.horizon})")
        meta_smooth = int(meta.get("target_smooth_window", 1))
        if meta_smooth != int(args.target_smooth_window):
            mismatches.append(
                f"target_smooth_window(meta={meta_smooth}, arg={args.target_smooth_window})"
            )
        if mismatches:
            raise ValueError(
                "Dataset metadata does not match requested args. "
                "Pass --allow-metadata-mismatch to skip this check. "
                f"Mismatches: {', '.join(mismatches)}"
            )

    print("Loading datasets...")
    train_ds = EnhancedSequenceDataset(dataset_dir / "train_multiscale.npz", args.smooth_window)
    val_ds = EnhancedSequenceDataset(dataset_dir / "val_multiscale.npz", args.smooth_window)
    test_ds = EnhancedSequenceDataset(dataset_dir / "test_multiscale.npz", args.smooth_window)
    print("Datasets loaded.")

    g = torch.Generator()
    g.manual_seed(args.seed)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              num_workers=0, generator=g)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False, num_workers=0)

    scalers = np.load(dataset_dir / "scalers.npz")
    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])
    yd_mean = float(scalers["y_delta_mean"])
    yd_std = float(scalers["y_delta_std"])

    dilations = [int(x.strip()) for x in args.dilations.split(",") if x.strip()]

    if args.run_name.strip():
        run_name = args.run_name.strip()
    else:
        run_name = f"improved_tcn_lb{args.lookback}_hz{args.horizon}"

    cfg = ImprovedModelConfig(
        n_features=int(meta["n_features"]),
        hidden=args.hidden,
        kernel_size=args.kernel_size,
        dilations=dilations,
        dropout=args.dropout,
        pool_type=args.pool_type,
        n_attn_heads=args.n_attn_heads,
        attn_layers=args.attn_layers,
        use_self_attention=not args.no_self_attention,
    )
    model = ImprovedTCN(cfg)

    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    model.to(device)

    print("=" * 80)
    print("TRAIN IMPROVED TCN")
    print("=" * 80)
    print(f"Device:               {device}")
    if device.type == "cuda":
        print(f"GPU:                  {torch.cuda.get_device_name(0)}")
    print(f"Parameters:           {model.count_parameters():,}")
    print(f"Train/Val/Test:       {len(train_ds):,} / {len(val_ds):,} / {len(test_ds):,}")
    print(f"Features:             {meta['n_features']}")
    print(f"Lookback/Horizon:     {meta['lookback']} / {meta['horizon']}")
    print(f"Smooth window (aux):  {args.smooth_window}")
    print(f"Self-attention:       {cfg.use_self_attention} ({cfg.n_attn_heads}h, {cfg.attn_layers}L)")
    print(f"Lambda smooth/delta/consistency: {args.lambda_smooth}/{args.lambda_delta}/{args.lambda_consistency}")
    print()

    huber = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=args.lr, weight_decay=args.weight_decay
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=5
    )

    best_val_r2 = -np.inf
    best_epoch = 0
    no_improve = 0
    history = []
    t0 = time.time()
    best_ckpt = models_dir / f"best_{run_name}.pth"

    for epoch in range(1, args.epochs + 1):
        tr = train_one_epoch(
            model=model,
            loader=train_loader,
            optimizer=optimizer,
            huber=huber,
            device=device,
            yf_mean=yf_mean,
            yf_std=yf_std,
            yd_mean=yd_mean,
            yd_std=yd_std,
            lambda_smooth=args.lambda_smooth,
            lambda_delta=args.lambda_delta,
            lambda_consistency=args.lambda_consistency,
            grad_clip=args.grad_clip,
        )
        val = evaluate(model, val_loader, device, yf_mean, yf_std, yd_mean, yd_std)
        val_r2 = val["future"]["r2"]
        scheduler.step(val_r2)
        lr_now = optimizer.param_groups[0]["lr"]

        improved = val_r2 > best_val_r2
        if improved:
            best_val_r2 = val_r2
            best_epoch = epoch
            no_improve = 0
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "cfg": cfg.__dict__,
                    "metadata": meta,
                    "scalers": {
                        "y_future_mean": yf_mean,
                        "y_future_std": yf_std,
                        "y_delta_mean": yd_mean,
                        "y_delta_std": yd_std,
                    },
                    "epoch": epoch,
                    "val_future_r2": best_val_r2,
                },
                best_ckpt,
            )
        else:
            no_improve += 1

        row = {
            "epoch": epoch,
            "train_loss": tr["loss"],
            "val_future_r2": val["future"]["r2"],
            "val_future_corr": val["future"]["corr"],
            "val_future_mae": val["future"]["mae"],
            "val_delta_r2": val["delta"]["r2"],
            "lr": lr_now,
        }
        history.append(row)

        mark = " *best" if improved else ""
        if epoch <= 5 or epoch % 10 == 0 or improved:
            print(
                f"Epoch {epoch:03d} | "
                f"train_loss={row['train_loss']:.4f} | "
                f"val_future_r2={row['val_future_r2']:.4f} | "
                f"val_delta_r2={row['val_delta_r2']:.4f} | "
                f"lr={lr_now:.2e}{mark}"
            )

        if no_improve >= args.patience:
            print(f"Early stopping at epoch {epoch} (patience={args.patience}).")
            break

    # Final test evaluation — future head only (apples-to-apples vs baseline)
    ckpt = torch.load(best_ckpt, map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    test = evaluate(model, test_loader, device, yf_mean, yf_std, yd_mean, yd_std)

    # Compute delta vs baseline TCN
    compare_path = Path(args.compare_baseline)
    baseline_r2 = get_baseline_tcn_r2(compare_path, args.horizon)
    if baseline_r2 is None:
        print(f"WARNING: Could not find baseline TCN R2 for horizon={args.horizon} in {compare_path}")
        baseline_r2 = float("nan")
    improved_r2 = test["future"]["r2"]
    delta_r2 = improved_r2 - baseline_r2 if not np.isnan(baseline_r2) else float("nan")

    train_secs = float(time.time() - t0)
    result = {
        "model": "ImprovedTCN",
        "improvements": ["enhanced_features", "multi_task_smoothing", "self_attention"],
        "n_params": model.count_parameters(),
        "n_features": int(meta["n_features"]),
        "best_epoch": best_epoch,
        "best_val_r2": float(best_val_r2),
        "test_future_metrics": test["future"],
        "test_delta_metrics": test["delta"],
        "baseline_tcn_r2": float(baseline_r2),
        "delta_r2": float(delta_r2),
        "train_seconds": train_secs,
        "config": {
            "lookback": args.lookback,
            "horizon": args.horizon,
            "target_smooth_window": args.target_smooth_window,
            "smooth_window": args.smooth_window,
            "hidden": args.hidden,
            "kernel_size": args.kernel_size,
            "dilations": dilations,
            "dropout": args.dropout,
            "pool_type": args.pool_type,
            "n_attn_heads": cfg.n_attn_heads,
            "attn_layers": cfg.attn_layers,
            "use_self_attention": cfg.use_self_attention,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "weight_decay": args.weight_decay,
            "lambda_smooth": args.lambda_smooth,
            "lambda_delta": args.lambda_delta,
            "lambda_consistency": args.lambda_consistency,
            "seed": args.seed,
        },
    }

    # Determine output filename tag
    tag = args.dataset_tag.strip()
    if not tag:
        # Infer from run_name: look for "7ch" or "4ch"
        for candidate in ("7ch", "4ch"):
            if candidate in run_name:
                tag = candidate
                break
        if not tag:
            tag = run_name

    out_path = results_dir / f"improved_tcn_{tag}.json"
    out_path.write_text(json.dumps(result, indent=2))

    history_path = models_dir / f"history_{run_name}.json"
    history_path.write_text(json.dumps(history, indent=2))

    print("\n" + "=" * 80)
    print("TRAINING COMPLETE")
    print("=" * 80)
    print(f"Best checkpoint:  {best_ckpt}")
    print(f"Results:          {out_path}")
    print(
        f"Test future: R2={improved_r2:.4f}, "
        f"corr={test['future']['corr']:.4f}, "
        f"RMSE={test['future']['rmse']:.6f}"
    )
    print(
        f"Test delta:  R2={test['delta']['r2']:.4f}, "
        f"corr={test['delta']['corr']:.4f}"
    )
    print(f"Baseline TCN R2:  {baseline_r2:.4f}")
    print(f"Delta R2:         {delta_r2:+.4f}")


if __name__ == "__main__":
    main()
