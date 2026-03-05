"""
Train multiscale causal TCN for PAC forecasting.

Usage:
    python temporal_multiscale/train_multiscale_tcn.py --rebuild-dataset
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path
from typing import Dict, Tuple
import sys

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

# Ensure repository root is importable when run as a script path.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from temporal_multiscale.build_multiscale_dataset import build_multiscale_dataset
from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN


class SequenceDataset(Dataset):
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


def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / (ss_tot + 1e-12))


def _corr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if np.std(y_true) < 1e-12 or np.std(y_pred) < 1e-12:
        return 0.0
    return float(np.corrcoef(y_true, y_pred)[0, 1])


def _metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    return {
        "r2": _r2(y_true, y_pred),
        "corr": _corr(y_true, y_pred),
        "mae": mae,
        "rmse": rmse,
    }


def _denorm(y_norm: np.ndarray, mean: float, std: float) -> np.ndarray:
    return y_norm * std + mean


def train_one_epoch(
    model: MultiscaleCausalTCN,
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

        # Consistency in raw PAC space:
        # future_raw ~= current_raw + delta_raw
        pred_future_raw = pred_future * yf_std + yf_mean
        pred_delta_raw = pred_delta * yd_std + yd_mean
        loss_consistency = torch.mean((pred_future_raw - (last_pac + pred_delta_raw)) ** 2)

        loss = loss_future + lambda_delta * loss_delta + lambda_consistency * loss_consistency

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
    model: MultiscaleCausalTCN,
    loader: DataLoader,
    device: torch.device,
    yf_mean: float,
    yf_std: float,
    yd_mean: float,
    yd_std: float,
) -> Dict[str, Dict[str, float]]:
    model.eval()
    future_pred_norm = []
    future_true_norm = []
    delta_pred_norm = []
    delta_true_norm = []

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

    future_pred_norm = np.concatenate(future_pred_norm)
    future_true_norm = np.concatenate(future_true_norm)
    delta_pred_norm = np.concatenate(delta_pred_norm)
    delta_true_norm = np.concatenate(delta_true_norm)

    future_pred = _denorm(future_pred_norm, yf_mean, yf_std)
    future_true = _denorm(future_true_norm, yf_mean, yf_std)
    delta_pred = _denorm(delta_pred_norm, yd_mean, yd_std)
    delta_true = _denorm(delta_true_norm, yd_mean, yd_std)

    return {
        "future": _metrics(future_true, future_pred),
        "delta": _metrics(delta_true, delta_pred),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train multiscale causal TCN.")
    p.add_argument("--processed-dir", default="data/processed", type=str)
    p.add_argument("--raw-root", default="data/raw/ds005048", type=str)
    p.add_argument("--dataset-dir", default="data/processed/multiscale_temporal", type=str)
    p.add_argument("--models-dir", default="models", type=str)
    p.add_argument("--run-name", default="", type=str)
    p.add_argument("--allow-metadata-mismatch", action="store_true")

    p.add_argument("--rebuild-dataset", action="store_true")
    p.add_argument("--lookback", default=20, type=int)
    p.add_argument("--horizon", default=5, type=int)
    p.add_argument("--stim-history-sec", default=20, type=int)
    p.add_argument("--target-smooth-window", default=1, type=int)

    p.add_argument("--hidden", default=64, type=int)
    p.add_argument("--dropout", default=0.2, type=float)
    p.add_argument("--kernel-size", default=3, type=int)
    p.add_argument("--dilations", default="1,2,4,8", type=str)
    p.add_argument("--pool-type", default="attention", type=str,
                   choices=["attention", "last_step"])

    p.add_argument("--epochs", default=80, type=int)
    p.add_argument("--batch-size", default=128, type=int)
    p.add_argument("--lr", default=1e-3, type=float)
    p.add_argument("--weight-decay", default=1e-3, type=float)
    p.add_argument("--patience", default=20, type=int)
    p.add_argument("--grad-clip", default=1.0, type=float)
    p.add_argument("--lambda-delta", default=0.0, type=float)
    p.add_argument("--lambda-consistency", default=0.0, type=float)
    p.add_argument("--seed", default=42, type=int)
    return p.parse_args()


def main() -> None:
    args = parse_args()

    # Deterministic seeding for reproducibility
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    dataset_dir = Path(args.dataset_dir)
    models_dir = Path(args.models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)

    if args.rebuild_dataset or not (dataset_dir / "metadata.json").exists():
        build_multiscale_dataset(
            processed_dir=Path(args.processed_dir),
            raw_root=Path(args.raw_root),
            output_dir=dataset_dir,
            lookback=args.lookback,
            horizon=args.horizon,
            stim_history_sec=args.stim_history_sec,
            target_smooth_window=args.target_smooth_window,
        )

    train_ds = SequenceDataset(dataset_dir / "train_multiscale.npz")
    val_ds = SequenceDataset(dataset_dir / "val_multiscale.npz")
    test_ds = SequenceDataset(dataset_dir / "test_multiscale.npz")

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
                "Use --rebuild-dataset or pass --allow-metadata-mismatch explicitly. "
                f"Mismatches: {', '.join(mismatches)}"
            )

    dilations = [int(x.strip()) for x in args.dilations.split(",") if x.strip()]
    run_name = args.run_name.strip() or f"multiscale_tcn_lb{args.lookback}_hz{args.horizon}"

    cfg = ModelConfig(
        n_features=int(meta["n_features"]),
        hidden=args.hidden,
        kernel_size=args.kernel_size,
        dilations=dilations,
        dropout=args.dropout,
        pool_type=args.pool_type,
    )
    model = MultiscaleCausalTCN(cfg)
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    model.to(device)

    print("=" * 80)
    print("TRAIN MULTISCALE CAUSAL TCN")
    print("=" * 80)
    print(f"Device:          {device}")
    if device.type == "cuda":
        print(f"GPU:             {torch.cuda.get_device_name(0)}")
    print(f"Parameters:      {model.count_parameters():,}")
    print(f"Train/Val/Test:  {len(train_ds):,} / {len(val_ds):,} / {len(test_ds):,}")
    print(f"Features:        {meta['n_features']}")
    print(f"Lookback/Horizon:{meta['lookback']} / {meta['horizon']}")
    print(f"Target smooth:   {meta.get('target_smooth_window', 1)}")
    print()

    huber = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.lr,
        weight_decay=args.weight_decay,
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
        if epoch <= 5 or epoch % 5 == 0 or improved:
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

    # Final test evaluation with best checkpoint
    ckpt = torch.load(best_ckpt, map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    test = evaluate(model, test_loader, device, yf_mean, yf_std, yd_mean, yd_std)

    summary = {
        "model": "MultiscaleCausalTCN",
        "run_name": run_name,
        "n_params": model.count_parameters(),
        "best_epoch": best_epoch,
        "best_val_future_r2": float(best_val_r2),
        "test_future_metrics": test["future"],
        "test_delta_metrics": test["delta"],
        "train_seconds": float(time.time() - t0),
        "config": {
            "lookback": args.lookback,
            "horizon": args.horizon,
            "stim_history_sec": args.stim_history_sec,
            "target_smooth_window": args.target_smooth_window,
            "hidden": args.hidden,
            "kernel_size": args.kernel_size,
            "dilations": dilations,
            "dropout": args.dropout,
            "pool_type": args.pool_type,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "weight_decay": args.weight_decay,
            "lambda_delta": args.lambda_delta,
            "lambda_consistency": args.lambda_consistency,
            "seed": args.seed,
        },
    }

    summary_path = models_dir / f"summary_{run_name}.json"
    history_path = models_dir / f"history_{run_name}.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    history_path.write_text(json.dumps(history, indent=2))

    print("\n" + "=" * 80)
    print("TRAINING COMPLETE")
    print("=" * 80)
    print(f"Best checkpoint: {best_ckpt}")
    print(f"Summary:         {summary_path}")
    print(f"History:         {history_path}")
    print(
        "Test future: "
        f"R2={summary['test_future_metrics']['r2']:.4f}, "
        f"corr={summary['test_future_metrics']['corr']:.4f}, "
        f"MAE={summary['test_future_metrics']['mae']:.6f}"
    )
    print(
        "Test delta:  "
        f"R2={summary['test_delta_metrics']['r2']:.4f}, "
        f"corr={summary['test_delta_metrics']['corr']:.4f}, "
        f"MAE={summary['test_delta_metrics']['mae']:.6f}"
    )


if __name__ == "__main__":
    main()
