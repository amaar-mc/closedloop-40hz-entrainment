"""
TCN multi-seed reproducibility study.

Trains MultiscaleCausalTCN across multiple random seeds on the 4-channel
and 7-channel datasets. The same pre-built NPZ files are reused for every
seed — only the model initialization, DataLoader shuffle ordering, and
training stochasticity change.

Purpose: Demonstrate that reported TCN R2 is not an artifact of a lucky
random seed, satisfying CSEF Scientific Thought rubric requirements for
rigorous reproducibility.

Usage:
    python temporal_multiscale/run_multiseed_study.py \
        --datasets 4ch,7ch \
        --seeds 42,123,456,789,1337 \
        --output results/multiseed_summary.json \
        --epochs 80 --patience 20
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

# Repository root on sys.path so relative imports work when run as a script.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN
from temporal_multiscale.train_multiscale_tcn import (
    SequenceDataset,
    train_one_epoch,
    evaluate,
)


# ---------------------------------------------------------------------------
# Dataset path resolution
# ---------------------------------------------------------------------------

DATASET_DIRS: Dict[str, str] = {
    "4ch": "data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1",
    "7ch": "data/processed/multiscale_temporal_lb20_hz5_ts1",
}


def resolve_dataset_dir(key: str, root: Path) -> Path:
    if key not in DATASET_DIRS:
        raise ValueError(
            f"Unknown dataset key '{key}'. Valid keys: {list(DATASET_DIRS.keys())}"
        )
    path = Path(DATASET_DIRS[key])
    if not path.is_absolute():
        path = root / path
    return path


# ---------------------------------------------------------------------------
# Single-seed training run
# ---------------------------------------------------------------------------

def train_one_seed(
    seed: int,
    dataset_dir: Path,
    device: torch.device,
    epochs: int,
    patience: int,
    batch_size: int,
    lr: float,
    weight_decay: float,
    grad_clip: float,
    yf_mean: float,
    yf_std: float,
    yd_mean: float,
    yd_std: float,
    n_features: int,
) -> Dict:
    """Train Full TCN for one seed and return per-seed metrics.

    CRITICAL: Datasets are NOT rebuilt between seeds. This function loads
    the pre-built NPZ files directly. Seeds control model init, DataLoader
    shuffle order, and training stochasticity only.
    """
    # Deterministic seeding for model init and DataLoader shuffle
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    # Re-load datasets for each seed call (cheap, shares underlying NPZ data)
    train_ds = SequenceDataset(dataset_dir / "train_multiscale.npz")
    val_ds = SequenceDataset(dataset_dir / "val_multiscale.npz")
    test_ds = SequenceDataset(dataset_dir / "test_multiscale.npz")

    g = torch.Generator()
    g.manual_seed(seed)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              num_workers=0, generator=g)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False,
                            num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False,
                             num_workers=0)

    cfg = ModelConfig(
        n_features=n_features,
        hidden=64,
        kernel_size=3,
        dilations=[1, 2, 4, 8],
        dropout=0.1,
        pool_type="attention",
    )
    model = MultiscaleCausalTCN(cfg).to(device)

    huber = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr,
                                  weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=5
    )

    best_val_r2 = -np.inf
    best_epoch = 0
    no_improve = 0
    best_state: Dict = {}
    t0 = time.time()

    for epoch in range(1, epochs + 1):
        train_one_epoch(
            model=model,
            loader=train_loader,
            optimizer=optimizer,
            huber=huber,
            device=device,
            yf_mean=yf_mean,
            yf_std=yf_std,
            yd_mean=yd_mean,
            yd_std=yd_std,
            lambda_delta=0.0,
            lambda_consistency=0.0,
            grad_clip=grad_clip,
        )
        val = evaluate(model, val_loader, device, yf_mean, yf_std, yd_mean, yd_std)
        val_r2 = val["future"]["r2"]
        scheduler.step(val_r2)

        if val_r2 > best_val_r2:
            best_val_r2 = val_r2
            best_epoch = epoch
            no_improve = 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            no_improve += 1

        if no_improve >= patience:
            break

    # Restore best weights for test evaluation
    model.load_state_dict(best_state)
    test = evaluate(model, test_loader, device, yf_mean, yf_std, yd_mean, yd_std)
    train_seconds = float(time.time() - t0)

    return {
        "seed": seed,
        "test_r2": float(test["future"]["r2"]),
        "test_rmse": float(test["future"]["rmse"]),
        "val_r2": float(best_val_r2),
        "best_epoch": best_epoch,
        "train_seconds": round(train_seconds, 1),
    }


# ---------------------------------------------------------------------------
# Per-dataset summary statistics
# ---------------------------------------------------------------------------

def compute_summary(per_seed: List[Dict]) -> Dict:
    r2_values = [r["test_r2"] for r in per_seed]
    rmse_values = [r["test_rmse"] for r in per_seed]
    return {
        "mean_r2": round(float(np.mean(r2_values)), 6),
        "std_r2": round(float(np.std(r2_values, ddof=1)), 6),
        "min_r2": round(float(np.min(r2_values)), 6),
        "max_r2": round(float(np.max(r2_values)), 6),
        "mean_rmse": round(float(np.mean(rmse_values)), 8),
        "std_rmse": round(float(np.std(rmse_values, ddof=1)), 8),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="TCN multi-seed reproducibility study — 5 seeds x 2 datasets."
    )
    p.add_argument(
        "--datasets",
        default="4ch,7ch",
        type=str,
        help="Comma-separated dataset keys. Supported: 4ch, 7ch.",
    )
    p.add_argument(
        "--seeds",
        default="42,123,456,789,1337",
        type=str,
        help="Comma-separated random seeds.",
    )
    p.add_argument("--output", default="results/multiseed_summary.json", type=str)
    p.add_argument("--epochs", default=80, type=int)
    p.add_argument("--patience", default=20, type=int)
    p.add_argument("--batch-size", default=128, type=int)
    p.add_argument("--lr", default=1e-3, type=float)
    p.add_argument("--weight-decay", default=1e-3, type=float)
    p.add_argument("--grad-clip", default=1.0, type=float)
    return p.parse_args()


def main() -> None:
    args = parse_args()

    dataset_keys = [k.strip() for k in args.datasets.split(",") if k.strip()]
    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    # Device selection
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    print("=" * 72)
    print("TCN MULTI-SEED REPRODUCIBILITY STUDY")
    print(f"  Device: {device}")
    print(f"  Datasets: {dataset_keys}")
    print(f"  Seeds: {seeds}")
    print(f"  Epochs: {args.epochs}, Patience: {args.patience}")
    total_runs = len(dataset_keys) * len(seeds)
    print(f"  Total training runs: {total_runs}")
    print("=" * 72)

    datasets_results: Dict = {}

    for ds_key in dataset_keys:
        dataset_dir = resolve_dataset_dir(ds_key, ROOT)

        if not (dataset_dir / "metadata.json").exists():
            raise FileNotFoundError(
                f"Dataset not found at {dataset_dir}. "
                "Run build_multiscale_dataset.py first."
            )

        meta = json.loads((dataset_dir / "metadata.json").read_text())
        n_features = int(meta["n_features"])

        scalers = np.load(dataset_dir / "scalers.npz")
        yf_mean = float(scalers["y_future_mean"])
        yf_std = float(scalers["y_future_std"])
        yd_mean = float(scalers["y_delta_mean"])
        yd_std = float(scalers["y_delta_std"])

        print(f"\n--- Dataset: {ds_key} (n_features={n_features}) ---")
        per_seed: List[Dict] = []

        for i, seed in enumerate(seeds, 1):
            print(f"  [{i}/{len(seeds)}] seed={seed} ...", end="", flush=True)
            result = train_one_seed(
                seed=seed,
                dataset_dir=dataset_dir,
                device=device,
                epochs=args.epochs,
                patience=args.patience,
                batch_size=args.batch_size,
                lr=args.lr,
                weight_decay=args.weight_decay,
                grad_clip=args.grad_clip,
                yf_mean=yf_mean,
                yf_std=yf_std,
                yd_mean=yd_mean,
                yd_std=yd_std,
                n_features=n_features,
            )
            per_seed.append(result)
            print(
                f" test_r2={result['test_r2']:.4f}, "
                f"val_r2={result['val_r2']:.4f}, "
                f"best_epoch={result['best_epoch']}, "
                f"time={result['train_seconds']:.0f}s"
            )

        datasets_results[ds_key] = {
            "n_features": n_features,
            "per_seed": per_seed,
            "summary": compute_summary(per_seed),
        }

    # Compose final JSON output
    output = {
        "model": "MultiscaleCausalTCN",
        "config": {
            "dilations": [1, 2, 4, 8],
            "pool_type": "attention",
            "hidden": 64,
            "kernel_size": 3,
            "dropout": 0.1,
            "lambda_delta": 0.0,
            "lambda_consistency": 0.0,
            "epochs": args.epochs,
            "patience": args.patience,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "weight_decay": args.weight_decay,
        },
        "seeds": seeds,
        "datasets": datasets_results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nMulti-seed summary saved to {output_path}")

    # Summary table
    print("\nTCN Multi-Seed Results (%d seeds)" % len(seeds))
    print(f"{'Dataset':<10} {'Mean R2':>8}  {'Std R2':>7}  {'Min R2':>8}  {'Max R2':>8}")
    print("-" * 52)
    for ds_key in dataset_keys:
        s = datasets_results[ds_key]["summary"]
        print(
            f"{ds_key:<10} {s['mean_r2']:>8.4f}  {s['std_r2']:>7.4f}  "
            f"{s['min_r2']:>8.4f}  {s['max_r2']:>8.4f}"
        )


if __name__ == "__main__":
    main()
