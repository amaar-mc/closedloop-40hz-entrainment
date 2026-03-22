"""
Best combination experiments:
1. Target smoothing (ts=5) + deep TCN architecture + regularization
2. Target smoothing (ts=5) + mixup
3. Multi-seed evaluation for the best config (robustness check)
4. Ensemble of multiple models
5. 4ch experiments with the best config
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

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
    ridge_baseline,
    ridge_enhanced_baseline,
    RESULTS_DIR,
    SplitData,
)
from experimental.run_generalization import MixupSeqDataset


def train_and_eval(
    name: str,
    dataset_dir: Path,
    hidden: int,
    dilations: List[int],
    kernel_size: int,
    dropout: float,
    lr: float,
    weight_decay: float,
    batch_size: int,
    epochs: int,
    patience: int,
    seed: int,
    loss_fn: str,
    mixup_alpha: float,
) -> Dict:
    """Train model and evaluate."""
    set_seed(seed)
    device = get_device()

    train = load_split(dataset_dir / "train_multiscale.npz")
    val = load_split(dataset_dir / "val_multiscale.npz")
    test = load_split(dataset_dir / "test_multiscale.npz")
    scalers = load_scalers(dataset_dir / "scalers.npz")

    n_feat = train.x_seq.shape[-1]

    if mixup_alpha > 0:
        train_ds = MixupSeqDataset(train.x_seq, train.y_future_norm,
                                    train.last_pac, alpha=mixup_alpha)
    else:
        train_ds = SeqDataset(train.x_seq, train.y_future_norm, train.last_pac)
    val_ds = SeqDataset(val.x_seq, val.y_future_norm, val.last_pac)
    test_ds = SeqDataset(test.x_seq, test.y_future_norm, test.last_pac)

    g = torch.Generator()
    g.manual_seed(seed)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              num_workers=0, generator=g)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    model = ImprovedTCN(n_feat, hidden=hidden, kernel_size=kernel_size,
                         dilations=dilations, dropout=dropout, n_heads=1)
    n_params = model.count_parameters()
    print(f"  [{name}] Params: {n_params:,}, Features: {n_feat}")

    t0 = time.time()
    model, info = train_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        scalers=scalers,
        epochs=epochs,
        lr=lr,
        weight_decay=weight_decay,
        patience=patience,
        grad_clip=1.0,
        loss_fn=loss_fn,
        predict_delta=False,
    )
    train_time = time.time() - t0

    val_metrics = evaluate_model(model, val_loader, device, scalers)
    test_metrics = evaluate_model(model, test_loader, device, scalers)
    persist_test = persistence_baseline(test)

    print(f"  [{name}] Val R2={val_metrics['r2']:.4f}, Test R2={test_metrics['r2']:.4f}, "
          f"Persist={persist_test['r2']:.4f}")

    return {
        "name": name,
        "n_params": n_params,
        "best_epoch": info["best_epoch"],
        "val": val_metrics,
        "test": test_metrics,
        "persistence_test": persist_test,
        "train_seconds": train_time,
        "seed": seed,
    }


def ensemble_evaluate(
    models_info: List[Dict],
    dataset_dir: Path,
) -> Dict:
    """Evaluate ensemble of models by averaging predictions."""
    device = get_device()
    test = load_split(dataset_dir / "test_multiscale.npz")
    val = load_split(dataset_dir / "val_multiscale.npz")
    scalers = load_scalers(dataset_dir / "scalers.npz")

    yf_mean = scalers["y_future_mean"]
    yf_std = scalers["y_future_std"]

    test_ds = SeqDataset(test.x_seq, test.y_future_norm, test.last_pac)
    val_ds = SeqDataset(val.x_seq, val.y_future_norm, val.last_pac)
    test_loader = DataLoader(test_ds, batch_size=256, shuffle=False, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=256, shuffle=False, num_workers=0)

    n_feat = test.x_seq.shape[-1]

    def get_predictions(loader: DataLoader, model_configs: List[Dict]) -> np.ndarray:
        all_model_preds = []
        for minfo in model_configs:
            model = ImprovedTCN(n_feat, hidden=minfo["hidden"],
                                 kernel_size=minfo.get("kernel_size", 3),
                                 dilations=minfo["dilations"],
                                 dropout=minfo["dropout"], n_heads=1)
            model.load_state_dict(minfo["state_dict"])
            model.to(device)
            model.eval()

            preds = []
            with torch.no_grad():
                for batch in loader:
                    x = batch["x"].to(device)
                    pred = model(x).cpu().numpy()
                    preds.append(pred)
            all_model_preds.append(np.concatenate(preds))

        # Average predictions
        return np.mean(all_model_preds, axis=0)

    # For simplicity, we just average the raw norm predictions
    # We need the trained models though, so this function would need them
    # Instead, we'll collect predictions during training

    return {"note": "ensemble requires model states - see multi-seed section"}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=80)
    args = parser.parse_args()

    all_results = []

    # ── Best combos on ts=1 (raw target, apples-to-apples with existing) ──
    print(f"\n{'='*70}")
    print("BEST COMBOS ON ts=1 (7ch, raw target)")
    print(f"{'='*70}")

    dataset_7ch_ts1 = ROOT / "data" / "processed" / "multiscale_temporal_lb20_hz5_ts1"

    # Deep TCN with high regularization (best architecture from exp 1)
    r = train_and_eval(
        "deep_tcn_highreg_ts1",
        dataset_7ch_ts1,
        hidden=64, dilations=[1, 2, 4, 8, 16, 32], kernel_size=3,
        dropout=0.3, lr=1e-3, weight_decay=5e-3,
        batch_size=128, epochs=args.epochs, patience=20,
        seed=args.seed, loss_fn="huber", mixup_alpha=0.0,
    )
    all_results.append(r)

    # Deep TCN + mixup
    r = train_and_eval(
        "deep_tcn_mixup02_ts1",
        dataset_7ch_ts1,
        hidden=64, dilations=[1, 2, 4, 8, 16, 32], kernel_size=3,
        dropout=0.2, lr=1e-3, weight_decay=1e-3,
        batch_size=128, epochs=args.epochs, patience=20,
        seed=args.seed, loss_fn="huber", mixup_alpha=0.2,
    )
    all_results.append(r)

    # Deep TCN + mixup + high regularization
    r = train_and_eval(
        "deep_tcn_mixup_highreg_ts1",
        dataset_7ch_ts1,
        hidden=64, dilations=[1, 2, 4, 8, 16, 32], kernel_size=3,
        dropout=0.3, lr=1e-3, weight_decay=5e-3,
        batch_size=128, epochs=args.epochs, patience=20,
        seed=args.seed, loss_fn="huber", mixup_alpha=0.2,
    )
    all_results.append(r)

    # Wider deep TCN with regularization
    r = train_and_eval(
        "wide_deep_tcn_highreg_ts1",
        dataset_7ch_ts1,
        hidden=96, dilations=[1, 2, 4, 8, 16], kernel_size=3,
        dropout=0.3, lr=5e-4, weight_decay=5e-3,
        batch_size=128, epochs=args.epochs, patience=20,
        seed=args.seed, loss_fn="huber", mixup_alpha=0.0,
    )
    all_results.append(r)

    # ── Best combos on ts=5 ──
    print(f"\n{'='*70}")
    print("BEST COMBOS ON ts=5 (7ch)")
    print(f"{'='*70}")

    dataset_7ch_ts5 = ROOT / "data" / "processed" / "exp_ts5_7ch"

    # Deep TCN with regularization
    r = train_and_eval(
        "deep_tcn_highreg_ts5",
        dataset_7ch_ts5,
        hidden=64, dilations=[1, 2, 4, 8, 16, 32], kernel_size=3,
        dropout=0.3, lr=1e-3, weight_decay=5e-3,
        batch_size=128, epochs=args.epochs, patience=20,
        seed=args.seed, loss_fn="huber", mixup_alpha=0.0,
    )
    all_results.append(r)

    # Deep TCN + mixup
    r = train_and_eval(
        "deep_tcn_mixup02_ts5",
        dataset_7ch_ts5,
        hidden=64, dilations=[1, 2, 4, 8, 16, 32], kernel_size=3,
        dropout=0.2, lr=1e-3, weight_decay=1e-3,
        batch_size=128, epochs=args.epochs, patience=20,
        seed=args.seed, loss_fn="huber", mixup_alpha=0.2,
    )
    all_results.append(r)

    # Standard TCN on ts=5 (reference)
    r = train_and_eval(
        "tcn_standard_ts5",
        dataset_7ch_ts5,
        hidden=64, dilations=[1, 2, 4, 8], kernel_size=3,
        dropout=0.2, lr=1e-3, weight_decay=1e-3,
        batch_size=128, epochs=args.epochs, patience=20,
        seed=args.seed, loss_fn="huber", mixup_alpha=0.0,
    )
    all_results.append(r)

    # ── Best combos on ts=3 ──
    print(f"\n{'='*70}")
    print("BEST COMBOS ON ts=3 (7ch)")
    print(f"{'='*70}")

    dataset_7ch_ts3 = ROOT / "data" / "processed" / "exp_ts3_7ch"

    r = train_and_eval(
        "deep_tcn_highreg_ts3",
        dataset_7ch_ts3,
        hidden=64, dilations=[1, 2, 4, 8, 16, 32], kernel_size=3,
        dropout=0.3, lr=1e-3, weight_decay=5e-3,
        batch_size=128, epochs=args.epochs, patience=20,
        seed=args.seed, loss_fn="huber", mixup_alpha=0.0,
    )
    all_results.append(r)

    r = train_and_eval(
        "deep_tcn_mixup02_ts3",
        dataset_7ch_ts3,
        hidden=64, dilations=[1, 2, 4, 8, 16, 32], kernel_size=3,
        dropout=0.2, lr=1e-3, weight_decay=1e-3,
        batch_size=128, epochs=args.epochs, patience=20,
        seed=args.seed, loss_fn="huber", mixup_alpha=0.2,
    )
    all_results.append(r)

    # ── Multi-seed robustness for best ts=1 config ──
    print(f"\n{'='*70}")
    print("MULTI-SEED ROBUSTNESS (deep_tcn + high reg, ts=1)")
    print(f"{'='*70}")

    seed_results = []
    for s in [42, 123, 456, 789, 2024]:
        r = train_and_eval(
            f"deep_tcn_highreg_ts1_seed{s}",
            dataset_7ch_ts1,
            hidden=64, dilations=[1, 2, 4, 8, 16, 32], kernel_size=3,
            dropout=0.3, lr=1e-3, weight_decay=5e-3,
            batch_size=128, epochs=args.epochs, patience=20,
            seed=s, loss_fn="huber", mixup_alpha=0.0,
        )
        seed_results.append(r)
        all_results.append(r)

    test_r2s = [r["test"]["r2"] for r in seed_results]
    print(f"\n  Multi-seed test R2: mean={np.mean(test_r2s):.4f}, "
          f"std={np.std(test_r2s):.4f}, range=[{np.min(test_r2s):.4f}, {np.max(test_r2s):.4f}]")

    # ── 4ch experiments with best config ──
    print(f"\n{'='*70}")
    print("4CH EXPERIMENTS")
    print(f"{'='*70}")

    dataset_4ch_ts1 = ROOT / "data" / "processed" / "muse_4ch" / "multiscale_temporal_lb20_hz5_ts1"

    # Baselines
    train_4ch = load_split(dataset_4ch_ts1 / "train_multiscale.npz")
    val_4ch = load_split(dataset_4ch_ts1 / "val_multiscale.npz")
    test_4ch = load_split(dataset_4ch_ts1 / "test_multiscale.npz")
    scalers_4ch = load_scalers(dataset_4ch_ts1 / "scalers.npz")

    persist_4ch = persistence_baseline(test_4ch)
    ridge_4ch = ridge_baseline(train_4ch, test_4ch, scalers_4ch)
    print(f"  4ch Persistence test R2={persist_4ch['r2']:.4f}")
    print(f"  4ch Ridge test R2={ridge_4ch['r2']:.4f}")

    all_results.append({"name": "persistence_4ch", "test": persist_4ch})
    all_results.append({"name": "ridge_4ch", "test": ridge_4ch})

    # Deep TCN with high reg on 4ch
    r = train_and_eval(
        "deep_tcn_highreg_4ch_ts1",
        dataset_4ch_ts1,
        hidden=64, dilations=[1, 2, 4, 8, 16, 32], kernel_size=3,
        dropout=0.3, lr=1e-3, weight_decay=5e-3,
        batch_size=128, epochs=args.epochs, patience=20,
        seed=args.seed, loss_fn="huber", mixup_alpha=0.0,
    )
    all_results.append(r)

    # Standard TCN on 4ch
    r = train_and_eval(
        "tcn_standard_4ch_ts1",
        dataset_4ch_ts1,
        hidden=64, dilations=[1, 2, 4, 8], kernel_size=3,
        dropout=0.2, lr=1e-3, weight_decay=1e-3,
        batch_size=128, epochs=args.epochs, patience=20,
        seed=args.seed, loss_fn="huber", mixup_alpha=0.0,
    )
    all_results.append(r)

    # Deep TCN + mixup on 4ch
    r = train_and_eval(
        "deep_tcn_mixup02_4ch_ts1",
        dataset_4ch_ts1,
        hidden=64, dilations=[1, 2, 4, 8, 16, 32], kernel_size=3,
        dropout=0.2, lr=1e-3, weight_decay=1e-3,
        batch_size=128, epochs=args.epochs, patience=20,
        seed=args.seed, loss_fn="huber", mixup_alpha=0.2,
    )
    all_results.append(r)

    # ── 4ch with target smoothing ts=5 ──
    from temporal_multiscale.build_multiscale_dataset import build_multiscale_dataset

    dataset_4ch_ts5 = ROOT / "data" / "processed" / "muse_4ch" / "exp_ts5_4ch"
    if not (dataset_4ch_ts5 / "metadata.json").exists():
        print("\n  Building 4ch ts=5 dataset...")
        build_multiscale_dataset(
            processed_dir=ROOT / "data" / "processed" / "muse_4ch",
            raw_root=ROOT / "data" / "raw" / "ds005048",
            output_dir=dataset_4ch_ts5,
            lookback=20, horizon=5, window_sec=2.0, hop_sec=1.0,
            stim_history_sec=20, target_smooth_window=5,
        )

    # Persistence on 4ch ts=5
    test_4ch_ts5 = load_split(dataset_4ch_ts5 / "test_multiscale.npz")
    persist_4ch_ts5 = persistence_baseline(test_4ch_ts5)
    print(f"  4ch ts=5 Persistence test R2={persist_4ch_ts5['r2']:.4f}")
    all_results.append({"name": "persistence_4ch_ts5", "test": persist_4ch_ts5})

    r = train_and_eval(
        "deep_tcn_highreg_4ch_ts5",
        dataset_4ch_ts5,
        hidden=64, dilations=[1, 2, 4, 8, 16, 32], kernel_size=3,
        dropout=0.3, lr=1e-3, weight_decay=5e-3,
        batch_size=128, epochs=args.epochs, patience=20,
        seed=args.seed, loss_fn="huber", mixup_alpha=0.0,
    )
    all_results.append(r)

    r = train_and_eval(
        "tcn_standard_4ch_ts5",
        dataset_4ch_ts5,
        hidden=64, dilations=[1, 2, 4, 8], kernel_size=3,
        dropout=0.2, lr=1e-3, weight_decay=1e-3,
        batch_size=128, epochs=args.epochs, patience=20,
        seed=args.seed, loss_fn="huber", mixup_alpha=0.0,
    )
    all_results.append(r)

    # ── Save ──
    out_path = RESULTS_DIR / "best_combos.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    # ── Final summary ──
    print(f"\n{'='*70}")
    print("BEST COMBOS SUMMARY")
    print(f"{'='*70}")
    print(f"{'Name':<35} {'Val R2':>8} {'Test R2':>8} {'Test Corr':>10}")
    print("-" * 70)
    for r in all_results:
        name = r.get("name", "?")
        val_r2 = r.get("val", {}).get("r2", float("nan"))
        test_r2 = r.get("test", {}).get("r2", float("nan"))
        test_corr = r.get("test", {}).get("corr", float("nan"))
        print(f"{name:<35} {val_r2:>8.4f} {test_r2:>8.4f} {test_corr:>10.4f}")


if __name__ == "__main__":
    main()
