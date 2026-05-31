"""
TCN ablation study: quantify contribution of each architectural component.

Trains 5 variants of MultiscaleCausalTCN on the 4-channel dataset and
reports the R2 impact of removing GroupNorm, attention pooling, multi-scale
dilation, or reducing to a single block.

Usage:
    python temporal_multiscale/run_ablation_study.py \
        --dataset-dir data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1 \
        --output results/metrics/ablation_table.json \
        --epochs 80 --patience 20 --seed 42

    # Dry run (no training):
    python temporal_multiscale/run_ablation_study.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import tempfile
import time
from dataclasses import dataclass
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

from temporal_multiscale.multiscale_tcn import (
    CausalDSConvBlock,
    AttentionPool1D,
    LastStepPool,
    ModelConfig,
    MultiscaleCausalTCN,
)
from temporal_multiscale.train_multiscale_tcn import (
    SequenceDataset,
    train_one_epoch,
    evaluate,
)


# ---------------------------------------------------------------------------
# No-GroupNorm variant
# ---------------------------------------------------------------------------

class CausalDSConvBlockNoNorm(CausalDSConvBlock):
    """CausalDSConvBlock with GroupNorm replaced by Identity (ablation)."""

    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dilation: int = 1,
        dropout: float = 0.1,
    ) -> None:
        super().__init__(channels=channels, kernel_size=kernel_size,
                         dilation=dilation, dropout=dropout)
        # Override the norm set by parent __init__
        self.norm = nn.Identity()


class MultiscaleCausalTCNNoNorm(MultiscaleCausalTCN):
    """MultiscaleCausalTCN using CausalDSConvBlockNoNorm in all blocks."""

    def __init__(self, cfg: ModelConfig) -> None:
        # Call nn.Module.__init__ directly to avoid MultiscaleCausalTCN building
        # its own blocks — we rebuild them below with the no-norm variant.
        nn.Module.__init__(self)
        self.cfg = cfg

        self.in_proj = nn.Sequential(
            nn.Linear(cfg.n_features, cfg.hidden),
            nn.LayerNorm(cfg.hidden),
            nn.SiLU(),
        )

        blocks = []
        for d in cfg.dilations:
            blocks.append(
                CausalDSConvBlockNoNorm(
                    channels=cfg.hidden,
                    kernel_size=cfg.kernel_size,
                    dilation=d,
                    dropout=cfg.dropout,
                )
            )
        self.tcn = nn.Sequential(*blocks)

        if cfg.pool_type == "last_step":
            self.pool = LastStepPool()
        else:
            self.pool = AttentionPool1D(cfg.hidden)

        self.future_head = nn.Sequential(
            nn.Linear(cfg.hidden, cfg.hidden),
            nn.SiLU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.hidden, 1),
        )
        self.delta_head = nn.Sequential(
            nn.Linear(cfg.hidden, cfg.hidden),
            nn.SiLU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.hidden, 1),
        )


# ---------------------------------------------------------------------------
# Variant definitions
# ---------------------------------------------------------------------------

@dataclass
class AblationVariant:
    name: str
    config_overrides: Dict  # overrides applied on top of the base ModelConfig
    no_norm: bool = False   # use MultiscaleCausalTCNNoNorm instead of default
    config_label: Dict = None  # human-readable config for JSON output

    def __post_init__(self) -> None:
        if self.config_label is None:
            self.config_label = {}


def build_variants(n_features: int) -> List[AblationVariant]:
    return [
        AblationVariant(
            name="Full TCN",
            config_overrides=dict(dilations=[1, 2, 4, 8], pool_type="attention"),
            no_norm=False,
            config_label={"dilations": [1, 2, 4, 8], "pool_type": "attention",
                          "norm": "GroupNorm"},
        ),
        AblationVariant(
            name="No attention (last step)",
            config_overrides=dict(dilations=[1, 2, 4, 8], pool_type="last_step"),
            no_norm=False,
            config_label={"dilations": [1, 2, 4, 8], "pool_type": "last_step",
                          "norm": "GroupNorm"},
        ),
        AblationVariant(
            name="Single dilation (no multi-scale)",
            config_overrides=dict(dilations=[1, 1, 1, 1], pool_type="attention"),
            no_norm=False,
            config_label={"dilations": [1, 1, 1, 1], "pool_type": "attention",
                          "norm": "GroupNorm"},
        ),
        AblationVariant(
            name="Single block",
            config_overrides=dict(dilations=[1], pool_type="attention"),
            no_norm=False,
            config_label={"dilations": [1], "pool_type": "attention",
                          "norm": "GroupNorm"},
        ),
        AblationVariant(
            name="No GroupNorm",
            config_overrides=dict(dilations=[1, 2, 4, 8], pool_type="attention"),
            no_norm=True,
            config_label={"dilations": [1, 2, 4, 8], "pool_type": "attention",
                          "norm": "Identity"},
        ),
    ]


def build_model(variant: AblationVariant, n_features: int) -> MultiscaleCausalTCN:
    cfg = ModelConfig(
        n_features=n_features,
        hidden=64,
        kernel_size=3,
        dilations=variant.config_overrides["dilations"],
        dropout=0.1,
        pool_type=variant.config_overrides["pool_type"],
    )
    if variant.no_norm:
        return MultiscaleCausalTCNNoNorm(cfg)
    return MultiscaleCausalTCN(cfg)


# ---------------------------------------------------------------------------
# Training one variant
# ---------------------------------------------------------------------------

def train_variant(
    variant: AblationVariant,
    dataset_dir: Path,
    device: torch.device,
    epochs: int,
    patience: int,
    batch_size: int,
    lr: float,
    weight_decay: float,
    grad_clip: float,
    seed: int,
    yf_mean: float,
    yf_std: float,
    yd_mean: float,
    yd_std: float,
    n_features: int,
    train_loader: DataLoader,
    val_loader: DataLoader,
    test_loader: DataLoader,
) -> Dict:
    """Train a single variant and return its result dict."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    model = build_model(variant, n_features)
    model.to(device)

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
            # Store state dict in memory — no checkpoint file needed
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            no_improve += 1

        if epoch <= 3 or epoch % 10 == 0:
            print(f"  Epoch {epoch:03d} | val_r2={val_r2:.4f} (best={best_val_r2:.4f})")

        if no_improve >= patience:
            print(f"  Early stopping at epoch {epoch}.")
            break

    # Restore best weights and evaluate on test
    model.load_state_dict(best_state)
    test = evaluate(model, test_loader, device, yf_mean, yf_std, yd_mean, yd_std)
    train_seconds = float(time.time() - t0)

    return {
        "variant": variant.name,
        "config": variant.config_label,
        "n_params": model.count_parameters(),
        "best_epoch": best_epoch,
        "val_r2": float(best_val_r2),
        "test_r2": float(test["future"]["r2"]),
        "test_rmse": float(test["future"]["rmse"]),
        "delta_r2_vs_full": 0.0,  # filled in after all variants run
        "train_seconds": round(train_seconds, 1),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="TCN ablation study — 5 variants, single seed."
    )
    p.add_argument(
        "--dataset-dir",
        default="data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1",
        type=str,
    )
    p.add_argument("--output", default="results/metrics/ablation_table.json", type=str)
    p.add_argument("--epochs", default=80, type=int)
    p.add_argument("--patience", default=20, type=int)
    p.add_argument("--batch-size", default=128, type=int)
    p.add_argument("--lr", default=1e-3, type=float)
    p.add_argument("--weight-decay", default=1e-3, type=float)
    p.add_argument("--grad-clip", default=1.0, type=float)
    p.add_argument("--seed", default=42, type=int)
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print variant configs and param counts without training.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    dataset_dir = Path(ROOT / args.dataset_dir) if not Path(args.dataset_dir).is_absolute() \
        else Path(args.dataset_dir)
    output_path = Path(ROOT / args.output) if not Path(args.output).is_absolute() \
        else Path(args.output)

    if not (dataset_dir / "metadata.json").exists():
        raise FileNotFoundError(
            f"Dataset metadata not found at {dataset_dir}/metadata.json. "
            "Run build_multiscale_dataset.py first."
        )

    meta = json.loads((dataset_dir / "metadata.json").read_text())
    n_features = int(meta["n_features"])
    variants = build_variants(n_features)

    # Dry-run: print configs and exit
    if args.dry_run:
        print("=" * 70)
        print("DRY RUN — ablation variant configs (no training)")
        print("=" * 70)
        print(f"{'Variant':<35} {'Params':>8}  Config")
        print("-" * 70)
        for v in variants:
            m = build_model(v, n_features)
            print(f"{v.name:<35} {m.count_parameters():>8,}  {v.config_label}")
        return

    # Device selection
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"Device: {device}")

    # Deterministic seeding for DataLoader generator
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    # Load datasets (shared across all variants)
    train_ds = SequenceDataset(dataset_dir / "train_multiscale.npz")
    val_ds = SequenceDataset(dataset_dir / "val_multiscale.npz")
    test_ds = SequenceDataset(dataset_dir / "test_multiscale.npz")

    g = torch.Generator()
    g.manual_seed(args.seed)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              num_workers=0, generator=g)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                            num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False,
                             num_workers=0)

    scalers = np.load(dataset_dir / "scalers.npz")
    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])
    yd_mean = float(scalers["y_delta_mean"])
    yd_std = float(scalers["y_delta_std"])

    print("=" * 70)
    print("TCN ABLATION STUDY")
    print(f"  Dataset: {dataset_dir}")
    print(f"  n_features={n_features}, train={len(train_ds):,}, "
          f"val={len(val_ds):,}, test={len(test_ds):,}")
    print(f"  epochs={args.epochs}, patience={args.patience}, seed={args.seed}")
    print("=" * 70)

    results = []
    for i, variant in enumerate(variants, 1):
        print(f"\n[{i}/{len(variants)}] Variant: {variant.name}")
        result = train_variant(
            variant=variant,
            dataset_dir=dataset_dir,
            device=device,
            epochs=args.epochs,
            patience=args.patience,
            batch_size=args.batch_size,
            lr=args.lr,
            weight_decay=args.weight_decay,
            grad_clip=args.grad_clip,
            seed=args.seed,
            yf_mean=yf_mean,
            yf_std=yf_std,
            yd_mean=yd_mean,
            yd_std=yd_std,
            n_features=n_features,
            train_loader=train_loader,
            val_loader=val_loader,
            test_loader=test_loader,
        )
        print(f"  => test_r2={result['test_r2']:.4f}, "
              f"test_rmse={result['test_rmse']:.2e}, "
              f"n_params={result['n_params']:,}, "
              f"best_epoch={result['best_epoch']}, "
              f"time={result['train_seconds']:.0f}s")
        results.append(result)

    # Compute delta_r2_vs_full
    full_r2 = next(r["test_r2"] for r in results if r["variant"] == "Full TCN")
    for r in results:
        r["delta_r2_vs_full"] = round(r["test_r2"] - full_r2, 6)

    # Save JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2))
    print(f"\nAblation table saved to {output_path}")

    # ASCII table
    print("\n" + "=" * 80)
    print("ABLATION RESULTS")
    print("=" * 80)
    print(f"{'Variant':<35} {'Params':>8}  {'Val R2':>7}  {'Test R2':>8}  {'Delta R2':>9}")
    print("-" * 80)
    for r in results:
        sign = "+" if r["delta_r2_vs_full"] >= 0 else ""
        print(
            f"{r['variant']:<35} {r['n_params']:>8,}  "
            f"{r['val_r2']:>7.4f}  {r['test_r2']:>8.4f}  "
            f"{sign}{r['delta_r2_vs_full']:>8.4f}"
        )
    print("-" * 80)
    print(f"Full TCN test R2 = {full_r2:.4f}")


if __name__ == "__main__":
    main()
