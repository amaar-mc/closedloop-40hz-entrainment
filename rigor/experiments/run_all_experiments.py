"""
Run All TCN Architecture Experiments on Real Data.

Trains all TCN variants (baseline + 4 experimental) on the real multiscale
temporal PAC dataset and produces a comparative evaluation.

Requirements:
    - Real data must exist at --data-dir (default: data/processed/multiscale_temporal)
    - This directory must contain: train_multiscale.npz, val_multiscale.npz,
      test_multiscale.npz, scalers.npz, metadata.json

Usage:
    python rigor/experiments/run_all_experiments.py \\
        --data-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean

    # With custom horizon sweep:
    python rigor/experiments/run_all_experiments.py \\
        --data-dir data/processed/multiscale_temporal \\
        --epochs 80 --patience 20

Outputs:
    rigor/experiments/experiment_results.json
    rigor/experiments/experiment_history_{variant}.json  (per-variant training curves)

Author: Amaar Chughtai
Date: February 2026
"""

from __future__ import annotations

import argparse
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

# Ensure repository root is importable
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rigor.experiments.tcn_variants import (
    VARIANT_REGISTRY,
    ModelConfig,
    MultiTaskTCN,
    TransformerConfig,
    build_variant,
)
from temporal_multiscale.multiscale_tcn import (
    ModelConfig as BaselineModelConfig,
    MultiscaleCausalTCN,
)


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------


class SequenceDataset(Dataset):
    """Loads a multiscale temporal dataset from disk."""

    def __init__(self, npz_path: Path) -> None:
        d = np.load(npz_path, allow_pickle=True)
        self.x = torch.from_numpy(d["x_seq"]).float()
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


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute R-squared."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / (ss_tot + 1e-12))


def _corr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute Pearson correlation."""
    if np.std(y_true) < 1e-12 or np.std(y_pred) < 1e-12:
        return 0.0
    return float(np.corrcoef(y_true, y_pred)[0, 1])


def _metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Compute regression metrics."""
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    return {
        "r2": _r2(y_true, y_pred),
        "corr": _corr(y_true, y_pred),
        "mae": mae,
        "rmse": rmse,
    }


def _denorm(y_norm: np.ndarray, mean: float, std: float) -> np.ndarray:
    """Denormalize z-scored predictions."""
    return y_norm * std + mean


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    huber: nn.Module,
    device: torch.device,
    yf_mean: float,
    yf_std: float,
    yd_mean: float,
    yd_std: float,
    lambda_delta: float,
    lambda_consistency: float,
    grad_clip: float,
) -> Dict[str, float]:
    """Train for one epoch.

    Args:
        model: Model to train.
        loader: Training data loader.
        optimizer: Optimizer.
        huber: Huber loss function.
        device: Compute device.
        yf_mean: Future PAC target mean (for denormalization in consistency loss).
        yf_std: Future PAC target std.
        yd_mean: Delta PAC target mean.
        yd_std: Delta PAC target std.
        lambda_delta: Weight for delta loss.
        lambda_consistency: Weight for consistency loss.
        grad_clip: Gradient clipping max norm.

    Returns:
        Dictionary with average training loss.
    """
    model.train()
    total = 0.0
    n = 0

    for batch in loader:
        x = batch["x_seq"].to(device)
        y_future = batch["y_future"].to(device)
        y_delta = batch["y_delta"].to(device)
        last_pac = batch["last_pac"].to(device)

        out = model(x)
        pred_future = out["future"]
        pred_delta = out["delta"]

        loss_future = huber(pred_future, y_future)
        loss_delta = huber(pred_delta, y_delta)

        # Consistency in raw PAC space
        pred_future_raw = pred_future * yf_std + yf_mean
        pred_delta_raw = pred_delta * yd_std + yd_mean
        loss_consistency = torch.mean(
            (pred_future_raw - (last_pac + pred_delta_raw)) ** 2
        )

        loss = (
            loss_future
            + lambda_delta * loss_delta
            + lambda_consistency * loss_consistency
        )

        optimizer.zero_grad()
        loss.backward()
        if grad_clip > 0:
            nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        optimizer.step()

        total += float(loss.item())
        n += 1

    return {"loss": total / max(1, n)}


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    yf_mean: float,
    yf_std: float,
    yd_mean: float,
    yd_std: float,
) -> Dict[str, Dict[str, float]]:
    """Evaluate model on a data split.

    Args:
        model: Trained model.
        loader: Data loader.
        device: Compute device.
        yf_mean: Future target mean.
        yf_std: Future target std.
        yd_mean: Delta target mean.
        yd_std: Delta target std.

    Returns:
        Dictionary with 'future' and 'delta' metric sub-dicts.
    """
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
        pf = out["future"].cpu().numpy()
        pd = out["delta"].cpu().numpy()

        future_pred_norm.append(pf)
        future_true_norm.append(y_future)
        delta_pred_norm.append(pd)
        delta_true_norm.append(y_delta)

    fp_all = np.concatenate(future_pred_norm)
    ft_all = np.concatenate(future_true_norm)
    dp_all = np.concatenate(delta_pred_norm)
    dt_all = np.concatenate(delta_true_norm)

    future_pred = _denorm(fp_all, yf_mean, yf_std)
    future_true = _denorm(ft_all, yf_mean, yf_std)
    delta_pred = _denorm(dp_all, yd_mean, yd_std)
    delta_true = _denorm(dt_all, yd_mean, yd_std)

    return {
        "future": _metrics(future_true, future_pred),
        "delta": _metrics(delta_true, delta_pred),
    }


def _persistence_baseline(
    loader: DataLoader,
    yf_mean: float,
    yf_std: float,
) -> Dict[str, float]:
    """Compute persistence baseline (predict last PAC as future PAC).

    Args:
        loader: Data loader.
        yf_mean: Future target mean.
        yf_std: Future target std.

    Returns:
        Metrics for the persistence baseline.
    """
    all_last_pac: List[np.ndarray] = []
    all_y_future_norm: List[np.ndarray] = []

    for batch in loader:
        all_last_pac.append(batch["last_pac"].numpy())
        all_y_future_norm.append(batch["y_future"].numpy())

    last_pac = np.concatenate(all_last_pac)
    y_future_true = _denorm(np.concatenate(all_y_future_norm), yf_mean, yf_std)

    # Persistence: predict current PAC as future PAC
    return _metrics(y_future_true, last_pac)


# ---------------------------------------------------------------------------
# Experiment runner
# ---------------------------------------------------------------------------


def run_single_experiment(
    variant_name: str,
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    test_loader: DataLoader,
    scalers: Dict[str, float],
    args: argparse.Namespace,
    device: torch.device,
    output_dir: Path,
) -> Dict[str, object]:
    """Train and evaluate a single model variant.

    Args:
        variant_name: Name for logging and output.
        model: Model instance.
        train_loader: Training data.
        val_loader: Validation data.
        test_loader: Test data.
        scalers: Dictionary with y_future_mean/std and y_delta_mean/std.
        args: Command-line arguments with training hyperparameters.
        device: Compute device.
        output_dir: Directory for saving history and checkpoints.

    Returns:
        Summary dictionary with metrics and metadata.
    """
    model = model.to(device)
    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    yf_mean = scalers["y_future_mean"]
    yf_std = scalers["y_future_std"]
    yd_mean = scalers["y_delta_mean"]
    yd_std = scalers["y_delta_std"]

    # Determine lambda values
    if variant_name == "multitask":
        lambda_delta = MultiTaskTCN.RECOMMENDED_LAMBDA_DELTA
        lambda_consistency = MultiTaskTCN.RECOMMENDED_LAMBDA_CONSISTENCY
    else:
        lambda_delta = args.lambda_delta
        lambda_consistency = args.lambda_consistency

    print(f"\n{'=' * 60}")
    print(f"Experiment: {variant_name}")
    print(f"{'=' * 60}")
    print(f"Parameters:       {n_params:,}")
    print(f"lambda_delta:     {lambda_delta}")
    print(f"lambda_consistency: {lambda_consistency}")

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
    history: List[Dict[str, float]] = []
    t0 = time.time()
    best_state: Dict[str, torch.Tensor] | None = None

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
            lambda_delta=lambda_delta,
            lambda_consistency=lambda_consistency,
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
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
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
                f"  Epoch {epoch:03d} | "
                f"train_loss={row['train_loss']:.4f} | "
                f"val_R2={row['val_future_r2']:.4f} | "
                f"val_delta_R2={row['val_delta_r2']:.4f} | "
                f"lr={lr_now:.2e}{mark}"
            )

        if no_improve >= args.patience:
            print(f"  Early stopping at epoch {epoch} (patience={args.patience}).")
            break

    train_time = time.time() - t0

    # Load best checkpoint and evaluate on test set
    if best_state is not None:
        model.load_state_dict(best_state)
    model = model.to(device)

    test = evaluate(model, test_loader, device, yf_mean, yf_std, yd_mean, yd_std)

    # Save training history
    history_path = output_dir / f"experiment_history_{variant_name}.json"
    history_path.write_text(json.dumps(history, indent=2))

    summary = {
        "variant": variant_name,
        "n_params": n_params,
        "best_epoch": best_epoch,
        "best_val_future_r2": float(best_val_r2),
        "test_future": test["future"],
        "test_delta": test["delta"],
        "train_time_sec": train_time,
        "lambda_delta": lambda_delta,
        "lambda_consistency": lambda_consistency,
    }

    print(
        f"  RESULT: test_R2={test['future']['r2']:.4f}, "
        f"test_corr={test['future']['corr']:.4f}, "
        f"test_MAE={test['future']['mae']:.6f}"
    )
    print(
        f"          delta_R2={test['delta']['r2']:.4f}, "
        f"time={train_time:.1f}s, best_epoch={best_epoch}"
    )

    return summary


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(
        description="Run all TCN architecture experiments."
    )
    p.add_argument(
        "--data-dir",
        type=str,
        default="data/processed/multiscale_temporal",
        help="Path to the multiscale temporal dataset directory.",
    )
    p.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).resolve().parent),
        help="Directory for experiment output files.",
    )
    p.add_argument("--epochs", type=int, default=80)
    p.add_argument("--batch-size", type=int, default=128)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--weight-decay", type=float, default=1e-3)
    p.add_argument("--patience", type=int, default=20)
    p.add_argument("--grad-clip", type=float, default=1.0)
    p.add_argument("--lambda-delta", type=float, default=0.0)
    p.add_argument("--lambda-consistency", type=float, default=0.0)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--variants",
        type=str,
        default="all",
        help=(
            "Comma-separated list of variants to run, or 'all'. "
            f"Available: baseline,{','.join(VARIANT_REGISTRY.keys())}"
        ),
    )
    return p.parse_args()


def main() -> None:
    """Entry point for the experiment runner."""
    args = parse_args()

    # Deterministic seeding
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Validate data directory
    required_files = [
        "train_multiscale.npz",
        "val_multiscale.npz",
        "test_multiscale.npz",
        "scalers.npz",
        "metadata.json",
    ]
    for fname in required_files:
        if not (data_dir / fname).exists():
            print(f"ERROR: Missing required file: {data_dir / fname}")
            print("Run build_multiscale_dataset.py first to generate the data.")
            sys.exit(1)

    # Load metadata and scalers
    meta = json.loads((data_dir / "metadata.json").read_text())
    scalers_npz = np.load(data_dir / "scalers.npz")
    scalers = {
        "y_future_mean": float(scalers_npz["y_future_mean"]),
        "y_future_std": float(scalers_npz["y_future_std"]),
        "y_delta_mean": float(scalers_npz["y_delta_mean"]),
        "y_delta_std": float(scalers_npz["y_delta_std"]),
    }

    n_features = int(meta["n_features"])

    # Load datasets
    train_ds = SequenceDataset(data_dir / "train_multiscale.npz")
    val_ds = SequenceDataset(data_dir / "val_multiscale.npz")
    test_ds = SequenceDataset(data_dir / "test_multiscale.npz")

    g = torch.Generator()
    g.manual_seed(args.seed)
    train_loader = DataLoader(
        train_ds, batch_size=args.batch_size, shuffle=True, num_workers=0, generator=g
    )
    val_loader = DataLoader(
        val_ds, batch_size=args.batch_size, shuffle=False, num_workers=0
    )
    test_loader = DataLoader(
        test_ds, batch_size=args.batch_size, shuffle=False, num_workers=0
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("=" * 80)
    print("TCN ARCHITECTURE EXPERIMENTS")
    print("=" * 80)
    print(f"Device:          {device}")
    if device.type == "cuda":
        print(f"GPU:             {torch.cuda.get_device_name(0)}")
    print(f"Data dir:        {data_dir}")
    print(f"Features:        {n_features}")
    print(f"Lookback:        {meta['lookback']}")
    print(f"Horizon:         {meta['horizon']}")
    print(f"Train/Val/Test:  {len(train_ds):,} / {len(val_ds):,} / {len(test_ds):,}")
    print(f"Epochs:          {args.epochs}")
    print(f"Batch size:      {args.batch_size}")
    print(f"Seed:            {args.seed}")

    # Determine which variants to run
    if args.variants == "all":
        variant_names = ["baseline"] + list(VARIANT_REGISTRY.keys())
    else:
        variant_names = [v.strip() for v in args.variants.split(",")]

    # --- Persistence baseline ---
    print("\n" + "-" * 60)
    print("Computing persistence baseline...")
    print("-" * 60)
    persistence = _persistence_baseline(
        test_loader, scalers["y_future_mean"], scalers["y_future_std"]
    )
    print(f"  Persistence: R2={persistence['r2']:.4f}, RMSE={persistence['rmse']:.6f}")

    # --- Run experiments ---
    all_results: Dict[str, object] = {
        "metadata": {
            "data_dir": str(data_dir),
            "n_features": n_features,
            "lookback": meta["lookback"],
            "horizon": meta["horizon"],
            "n_train": len(train_ds),
            "n_val": len(val_ds),
            "n_test": len(test_ds),
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "weight_decay": args.weight_decay,
            "seed": args.seed,
        },
        "persistence_baseline": persistence,
        "variants": {},
    }

    for variant_name in variant_names:
        # Reset seed for fair comparison
        torch.manual_seed(args.seed)
        np.random.seed(args.seed)
        random.seed(args.seed)

        if variant_name == "baseline":
            cfg = BaselineModelConfig(
                n_features=n_features,
                hidden=64,
                kernel_size=3,
                dilations=[1, 2, 4, 8],
                dropout=0.1,
                pool_type="attention",
            )
            model = MultiscaleCausalTCN(cfg)
        else:
            model = build_variant(variant_name, n_features)

        result = run_single_experiment(
            variant_name=variant_name,
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            test_loader=test_loader,
            scalers=scalers,
            args=args,
            device=device,
            output_dir=output_dir,
        )
        all_results["variants"][variant_name] = result

    # --- Final comparison table ---
    print("\n" + "=" * 80)
    print("EXPERIMENT COMPARISON")
    print("=" * 80)
    print(
        f"{'Variant':<20} {'Params':>8} {'Test R2':>10} {'Corr':>8} "
        f"{'MAE':>10} {'RMSE':>10} {'Delta R2':>10} {'Time':>8}"
    )
    print("-" * 94)

    # Persistence row
    print(
        f"{'persistence':<20} {'--':>8} {persistence['r2']:>10.4f} "
        f"{persistence['corr']:>8.4f} {persistence['mae']:>10.6f} "
        f"{persistence['rmse']:>10.6f} {'--':>10} {'--':>8}"
    )

    # Model rows
    for name, result in all_results["variants"].items():
        tf = result["test_future"]
        td = result["test_delta"]
        print(
            f"{name:<20} {result['n_params']:>8,} {tf['r2']:>10.4f} "
            f"{tf['corr']:>8.4f} {tf['mae']:>10.6f} {tf['rmse']:>10.6f} "
            f"{td['r2']:>10.4f} {result['train_time_sec']:>7.1f}s"
        )

    # --- Highlight best ---
    if all_results["variants"]:
        best_name = max(
            all_results["variants"],
            key=lambda n: all_results["variants"][n]["test_future"]["r2"],
        )
        best_r2 = all_results["variants"][best_name]["test_future"]["r2"]
        margin = best_r2 - persistence["r2"]
        print(f"\nBest variant: {best_name} (R2={best_r2:.4f}, margin over persistence: {margin:+.4f})")

    # Save results
    results_path = output_dir / "experiment_results.json"
    results_path.write_text(json.dumps(all_results, indent=2))
    print(f"\nResults saved to: {results_path}")


if __name__ == "__main__":
    main()
