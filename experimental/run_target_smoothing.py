"""
Experiment: Target smoothing effect on PAC prediction.

The current pipeline uses target_smooth_window=1 (raw PAC).
Since PAC labels are assigned at epoch level (20-40s blocks) to constituent
2s windows, all windows in an epoch share the same PAC. This creates
high-frequency noise in the target when viewed as a time series.

Smoothing the target with a causal trailing average (ts=3, ts=5) reduces
this noise and should improve R2 significantly, since the model is then
predicting a denoised trend rather than raw noisy labels.

This script rebuilds datasets with different smoothing windows and trains
on each.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experimental.run_experiments import (
    ImprovedTCN,
    SeqDataset,
    compute_metrics,
    denorm,
    get_device,
    load_scalers,
    load_split,
    persistence_baseline,
    r2_score,
    set_seed,
    train_model,
    evaluate_model,
    RESULTS_DIR,
)
from temporal_multiscale.build_multiscale_dataset import build_multiscale_dataset
from torch.utils.data import DataLoader


def run_smoothed_experiment(
    dataset_label: str,
    target_smooth_window: int,
    n_features: int,
    seed: int,
    epochs: int,
    base_processed_dir: Path,
    raw_root: Path,
) -> dict:
    """Build dataset with given smoothing, train TCN, evaluate."""
    set_seed(seed)
    device = get_device()

    # Build dataset with target smoothing
    output_dir = ROOT / "data" / "processed" / f"exp_ts{target_smooth_window}_{dataset_label}"
    if not (output_dir / "metadata.json").exists():
        print(f"\nBuilding dataset with target_smooth_window={target_smooth_window}...")
        build_multiscale_dataset(
            processed_dir=base_processed_dir,
            raw_root=raw_root,
            output_dir=output_dir,
            lookback=20,
            horizon=5,
            window_sec=2.0,
            hop_sec=1.0,
            stim_history_sec=20,
            target_smooth_window=target_smooth_window,
        )
    else:
        print(f"\nUsing cached dataset at {output_dir}")

    train = load_split(output_dir / "train_multiscale.npz")
    val = load_split(output_dir / "val_multiscale.npz")
    test = load_split(output_dir / "test_multiscale.npz")
    scalers = load_scalers(output_dir / "scalers.npz")

    n_feat = train.x_seq.shape[-1]
    print(f"  Features: {n_feat}, Smoothing window: {target_smooth_window}")

    # Persistence baseline for this smoothing level
    persist_test = persistence_baseline(test)
    persist_val = persistence_baseline(val)
    print(f"  Persistence: val R2={persist_val['r2']:.4f}, test R2={persist_test['r2']:.4f}")

    # Train TCN
    train_ds = SeqDataset(train.x_seq, train.y_future_norm, train.last_pac)
    val_ds = SeqDataset(val.x_seq, val.y_future_norm, val.last_pac)
    test_ds = SeqDataset(test.x_seq, test.y_future_norm, test.last_pac)

    g = torch.Generator()
    g.manual_seed(seed)
    train_loader = DataLoader(train_ds, batch_size=128, shuffle=True, num_workers=0, generator=g)
    val_loader = DataLoader(val_ds, batch_size=128, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=128, shuffle=False, num_workers=0)

    model = ImprovedTCN(n_feat, hidden=64, kernel_size=3,
                         dilations=[1, 2, 4, 8], dropout=0.2, n_heads=1)
    n_params = model.count_parameters()
    print(f"  TCN params: {n_params:,}")

    t0 = time.time()
    model, info = train_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        scalers=scalers,
        epochs=epochs,
        lr=1e-3,
        weight_decay=1e-3,
        patience=20,
        grad_clip=1.0,
        loss_fn="huber",
        predict_delta=False,
    )
    train_time = time.time() - t0

    val_metrics = evaluate_model(model, val_loader, device, scalers)
    test_metrics = evaluate_model(model, test_loader, device, scalers)

    # Also try wider TCN
    set_seed(seed)
    model_wide = ImprovedTCN(n_feat, hidden=128, kernel_size=3,
                              dilations=[1, 2, 4, 8], dropout=0.15, n_heads=1)
    print(f"\n  Training wide TCN (128 hidden)...")
    g2 = torch.Generator()
    g2.manual_seed(seed)
    train_loader2 = DataLoader(train_ds, batch_size=128, shuffle=True, num_workers=0, generator=g2)
    model_wide, info_wide = train_model(
        model=model_wide,
        train_loader=train_loader2,
        val_loader=val_loader,
        device=device,
        scalers=scalers,
        epochs=epochs,
        lr=5e-4,
        weight_decay=1e-3,
        patience=20,
        grad_clip=1.0,
        loss_fn="huber",
        predict_delta=False,
    )
    val_wide = evaluate_model(model_wide, val_loader, device, scalers)
    test_wide = evaluate_model(model_wide, test_loader, device, scalers)

    return {
        "target_smooth_window": target_smooth_window,
        "dataset_label": dataset_label,
        "persistence_val": persist_val,
        "persistence_test": persist_test,
        "tcn_64": {
            "n_params": n_params,
            "val": val_metrics,
            "test": test_metrics,
            "best_epoch": info["best_epoch"],
            "train_seconds": train_time,
        },
        "tcn_128": {
            "n_params": model_wide.count_parameters(),
            "val": val_wide,
            "test": test_wide,
            "best_epoch": info_wide["best_epoch"],
        },
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["7ch", "4ch"], default="7ch")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=80)
    args = parser.parse_args()

    if args.dataset == "7ch":
        base_dir = ROOT / "data" / "processed"
    else:
        base_dir = ROOT / "data" / "processed" / "muse_4ch"

    raw_root = ROOT / "data" / "raw" / "ds005048"

    results = []
    for ts in [1, 3, 5, 8]:
        print(f"\n{'='*70}")
        print(f"TARGET SMOOTH WINDOW = {ts}")
        print(f"{'='*70}")

        r = run_smoothed_experiment(
            dataset_label=args.dataset,
            target_smooth_window=ts,
            n_features=73 if args.dataset == "7ch" else 49,
            seed=args.seed,
            epochs=args.epochs,
            base_processed_dir=base_dir,
            raw_root=raw_root,
        )
        results.append(r)

    # Save
    out_path = RESULTS_DIR / f"target_smoothing_{args.dataset}.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    # Summary
    print(f"\n{'='*70}")
    print(f"TARGET SMOOTHING SUMMARY: {args.dataset}")
    print(f"{'='*70}")
    print(f"{'TS':>4} {'Persist Val':>12} {'Persist Test':>13} {'TCN64 Val':>10} "
          f"{'TCN64 Test':>11} {'TCN128 Val':>11} {'TCN128 Test':>12}")
    print("-" * 80)
    for r in results:
        ts = r["target_smooth_window"]
        pv = r["persistence_val"]["r2"]
        pt = r["persistence_test"]["r2"]
        tv = r["tcn_64"]["val"]["r2"]
        tt = r["tcn_64"]["test"]["r2"]
        wv = r["tcn_128"]["val"]["r2"]
        wt = r["tcn_128"]["test"]["r2"]
        print(f"{ts:>4} {pv:>12.4f} {pt:>13.4f} {tv:>10.4f} {tt:>11.4f} {wv:>11.4f} {wt:>12.4f}")


if __name__ == "__main__":
    main()
