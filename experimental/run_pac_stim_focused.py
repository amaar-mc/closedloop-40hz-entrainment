"""
Focused experiments on PAC+stim features.

Key finding: pac_stim (12 features) alone achieves test R2=0.558 on 7ch,
far exceeding any model using all 73 features. Spectral features cause
subject-specific overfitting that destroys generalization.

This script systematically explores:
1. pac_stim with different model sizes
2. pac_stim with target smoothing
3. pac_stim on 4ch data
4. Small subsets of spectral features that might help
5. Multi-seed robustness
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
    CausalConvBlock,
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
    SplitData,
)
from experimental.run_generalization import MixupSeqDataset


def extract_pac_stim(data: SplitData) -> np.ndarray:
    """Extract PAC + stim context features (indices 61-72)."""
    return data.x_seq[:, :, 61:73]


def extract_pac_only(data: SplitData) -> np.ndarray:
    """Extract PAC features only (indices 61-67)."""
    return data.x_seq[:, :, 61:68]


def extract_pac_stim_topspec(data: SplitData, n_spec: int) -> np.ndarray:
    """Extract PAC + stim + top N spectral features."""
    pac_stim = data.x_seq[:, :, 61:73]
    spec = data.x_seq[:, :, :n_spec]
    return np.concatenate([spec, pac_stim], axis=2)


def train_eval_subset(
    name: str,
    x_train: np.ndarray,
    y_train_norm: np.ndarray,
    lp_train: np.ndarray,
    x_val: np.ndarray,
    y_val_norm: np.ndarray,
    lp_val: np.ndarray,
    x_test: np.ndarray,
    y_test_norm: np.ndarray,
    lp_test: np.ndarray,
    y_test_raw: np.ndarray,
    y_val_raw: np.ndarray,
    scalers: Dict[str, float],
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
    set_seed(seed)
    device = get_device()
    n_feat = x_train.shape[-1]

    if mixup_alpha > 0:
        train_ds = MixupSeqDataset(x_train, y_train_norm, lp_train, alpha=mixup_alpha)
    else:
        train_ds = SeqDataset(x_train, y_train_norm, lp_train)
    val_ds = SeqDataset(x_val, y_val_norm, lp_val)
    test_ds = SeqDataset(x_test, y_test_norm, lp_test)

    g = torch.Generator()
    g.manual_seed(seed)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              num_workers=0, generator=g)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    model = ImprovedTCN(n_feat, hidden=hidden, kernel_size=kernel_size,
                         dilations=dilations, dropout=dropout, n_heads=1)
    n_params = model.count_parameters()

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

    return {
        "name": name,
        "n_features": n_feat,
        "n_params": n_params,
        "best_epoch": info["best_epoch"],
        "val": val_metrics,
        "test": test_metrics,
        "train_seconds": train_time,
        "seed": seed,
    }


def ridge_on_subset(
    x_train: np.ndarray,
    y_train_norm: np.ndarray,
    x_test: np.ndarray,
    y_test_raw: np.ndarray,
    scalers: Dict[str, float],
    alpha: float,
) -> Dict[str, float]:
    """Ridge regression on feature subset."""
    from sklearn.linear_model import Ridge

    X_tr = x_train.reshape(x_train.shape[0], -1)
    X_te = x_test.reshape(x_test.shape[0], -1)

    model = Ridge(alpha=alpha)
    model.fit(X_tr, y_train_norm)

    pred_norm = model.predict(X_te)
    pred_raw = denorm(pred_norm, scalers["y_future_mean"], scalers["y_future_std"])
    return compute_metrics(y_test_raw, pred_raw)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=80)
    args = parser.parse_args()

    all_results = []

    # ═══════════════════════════════════════════════════════
    # 7ch experiments with pac_stim features (ts=1)
    # ═══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("7CH PAC+STIM FEATURES (ts=1, raw target)")
    print(f"{'='*70}")

    dataset_dir = ROOT / "data" / "processed" / "multiscale_temporal_lb20_hz5_ts1"
    train = load_split(dataset_dir / "train_multiscale.npz")
    val = load_split(dataset_dir / "val_multiscale.npz")
    test = load_split(dataset_dir / "test_multiscale.npz")
    scalers = load_scalers(dataset_dir / "scalers.npz")

    x_train_ps = extract_pac_stim(train)
    x_val_ps = extract_pac_stim(val)
    x_test_ps = extract_pac_stim(test)

    # Persistence baseline
    persist_test = persistence_baseline(test)
    print(f"  Persistence test R2={persist_test['r2']:.4f}")
    all_results.append({"name": "persistence_7ch", "test": persist_test})

    # Ridge on pac_stim
    ridge_ps_test = ridge_on_subset(x_train_ps, train.y_future_norm, x_test_ps,
                                     test.y_future, scalers, alpha=1.0)
    ridge_ps_val = ridge_on_subset(x_train_ps, train.y_future_norm, x_val_ps,
                                    val.y_future, scalers, alpha=1.0)
    print(f"  Ridge pac_stim: val R2={ridge_ps_val['r2']:.4f}, test R2={ridge_ps_test['r2']:.4f}")
    all_results.append({"name": "ridge_pac_stim_7ch", "val": ridge_ps_val, "test": ridge_ps_test})

    # Ridge on pac_stim with different alpha
    for alpha in [0.1, 10.0, 100.0]:
        r_t = ridge_on_subset(x_train_ps, train.y_future_norm, x_test_ps,
                               test.y_future, scalers, alpha=alpha)
        r_v = ridge_on_subset(x_train_ps, train.y_future_norm, x_val_ps,
                               val.y_future, scalers, alpha=alpha)
        print(f"  Ridge(a={alpha}) pac_stim: val R2={r_v['r2']:.4f}, test R2={r_t['r2']:.4f}")

    # ── Various architectures on pac_stim ──
    configs = [
        # (name, hidden, dilations, ks, dropout, lr, wd, batch)
        ("tcn_h32_pac_stim", 32, [1, 2, 4], 3, 0.2, 1e-3, 1e-3, 128),
        ("tcn_h64_pac_stim", 64, [1, 2, 4, 8], 3, 0.2, 1e-3, 1e-3, 128),
        ("tcn_h64_deep_pac_stim", 64, [1, 2, 4, 8, 16, 32], 3, 0.2, 1e-3, 1e-3, 128),
        ("tcn_h32_highreg_pac_stim", 32, [1, 2, 4], 3, 0.3, 1e-3, 5e-3, 128),
        ("tcn_h64_highreg_pac_stim", 64, [1, 2, 4, 8], 3, 0.3, 1e-3, 5e-3, 128),
        ("tcn_h64_deep_highreg_pac_stim", 64, [1, 2, 4, 8, 16, 32], 3, 0.3, 1e-3, 5e-3, 128),
        ("tcn_h128_pac_stim", 128, [1, 2, 4, 8], 3, 0.2, 5e-4, 1e-3, 128),
        ("tcn_h32_lowlr_pac_stim", 32, [1, 2, 4], 3, 0.15, 3e-4, 5e-4, 64),
    ]

    for name, hidden, dil, ks, drop, lr, wd, bs in configs:
        print(f"\n  --- {name} ---")
        r = train_eval_subset(
            name=name,
            x_train=x_train_ps, y_train_norm=train.y_future_norm, lp_train=train.last_pac,
            x_val=x_val_ps, y_val_norm=val.y_future_norm, lp_val=val.last_pac,
            x_test=x_test_ps, y_test_norm=test.y_future_norm, lp_test=test.last_pac,
            y_test_raw=test.y_future, y_val_raw=val.y_future,
            scalers=scalers,
            hidden=hidden, dilations=dil, kernel_size=ks,
            dropout=drop, lr=lr, weight_decay=wd,
            batch_size=bs, epochs=args.epochs, patience=20,
            seed=args.seed, loss_fn="huber", mixup_alpha=0.0,
        )
        print(f"  Val R2={r['val']['r2']:.4f}, Test R2={r['test']['r2']:.4f} "
              f"(params={r['n_params']:,})")
        all_results.append(r)

    # ── Mixup on pac_stim ──
    print(f"\n{'='*70}")
    print("PAC+STIM + MIXUP")
    print(f"{'='*70}")
    for alpha in [0.1, 0.2, 0.5]:
        name = f"tcn_h64_pac_stim_mixup{alpha}"
        print(f"\n  --- {name} ---")
        r = train_eval_subset(
            name=name,
            x_train=x_train_ps, y_train_norm=train.y_future_norm, lp_train=train.last_pac,
            x_val=x_val_ps, y_val_norm=val.y_future_norm, lp_val=val.last_pac,
            x_test=x_test_ps, y_test_norm=test.y_future_norm, lp_test=test.last_pac,
            y_test_raw=test.y_future, y_val_raw=val.y_future,
            scalers=scalers,
            hidden=64, dilations=[1, 2, 4, 8], kernel_size=3,
            dropout=0.2, lr=1e-3, weight_decay=1e-3,
            batch_size=128, epochs=args.epochs, patience=20,
            seed=args.seed, loss_fn="huber", mixup_alpha=alpha,
        )
        print(f"  Val R2={r['val']['r2']:.4f}, Test R2={r['test']['r2']:.4f}")
        all_results.append(r)

    # ── Multi-seed robustness on best pac_stim config ──
    print(f"\n{'='*70}")
    print("MULTI-SEED ROBUSTNESS (pac_stim, h64, ts=1)")
    print(f"{'='*70}")
    seed_results = []
    for s in [42, 123, 456, 789, 2024]:
        r = train_eval_subset(
            name=f"tcn_h64_pac_stim_seed{s}",
            x_train=x_train_ps, y_train_norm=train.y_future_norm, lp_train=train.last_pac,
            x_val=x_val_ps, y_val_norm=val.y_future_norm, lp_val=val.last_pac,
            x_test=x_test_ps, y_test_norm=test.y_future_norm, lp_test=test.last_pac,
            y_test_raw=test.y_future, y_val_raw=val.y_future,
            scalers=scalers,
            hidden=64, dilations=[1, 2, 4, 8], kernel_size=3,
            dropout=0.2, lr=1e-3, weight_decay=1e-3,
            batch_size=128, epochs=args.epochs, patience=20,
            seed=s, loss_fn="huber", mixup_alpha=0.0,
        )
        seed_results.append(r)
        all_results.append(r)
        print(f"  Seed {s}: Val R2={r['val']['r2']:.4f}, Test R2={r['test']['r2']:.4f}")

    test_r2s = [r["test"]["r2"] for r in seed_results]
    print(f"\n  Multi-seed test R2: mean={np.mean(test_r2s):.4f}, "
          f"std={np.std(test_r2s):.4f}, "
          f"range=[{np.min(test_r2s):.4f}, {np.max(test_r2s):.4f}]")

    # ═══════════════════════════════════════════════════════
    # PAC+STIM with target smoothing ts=5
    # ═══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("7CH PAC+STIM FEATURES (ts=5)")
    print(f"{'='*70}")

    dataset_ts5 = ROOT / "data" / "processed" / "exp_ts5_7ch"
    train_ts5 = load_split(dataset_ts5 / "train_multiscale.npz")
    val_ts5 = load_split(dataset_ts5 / "val_multiscale.npz")
    test_ts5 = load_split(dataset_ts5 / "test_multiscale.npz")
    scalers_ts5 = load_scalers(dataset_ts5 / "scalers.npz")

    x_train_ps5 = extract_pac_stim(train_ts5)
    x_val_ps5 = extract_pac_stim(val_ts5)
    x_test_ps5 = extract_pac_stim(test_ts5)

    persist_ts5 = persistence_baseline(test_ts5)
    print(f"  Persistence test R2={persist_ts5['r2']:.4f}")
    all_results.append({"name": "persistence_7ch_ts5", "test": persist_ts5})

    for name, hidden, dil, drop, lr, wd in [
        ("tcn_h64_pac_stim_ts5", 64, [1, 2, 4, 8], 0.2, 1e-3, 1e-3),
        ("tcn_h64_deep_pac_stim_ts5", 64, [1, 2, 4, 8, 16, 32], 0.2, 1e-3, 1e-3),
        ("tcn_h32_pac_stim_ts5", 32, [1, 2, 4], 0.2, 1e-3, 1e-3),
        ("tcn_h64_highreg_pac_stim_ts5", 64, [1, 2, 4, 8], 0.3, 1e-3, 5e-3),
    ]:
        print(f"\n  --- {name} ---")
        r = train_eval_subset(
            name=name,
            x_train=x_train_ps5, y_train_norm=train_ts5.y_future_norm, lp_train=train_ts5.last_pac,
            x_val=x_val_ps5, y_val_norm=val_ts5.y_future_norm, lp_val=val_ts5.last_pac,
            x_test=x_test_ps5, y_test_norm=test_ts5.y_future_norm, lp_test=test_ts5.last_pac,
            y_test_raw=test_ts5.y_future, y_val_raw=val_ts5.y_future,
            scalers=scalers_ts5,
            hidden=hidden, dilations=dil, kernel_size=3,
            dropout=drop, lr=lr, weight_decay=wd,
            batch_size=128, epochs=args.epochs, patience=20,
            seed=args.seed, loss_fn="huber", mixup_alpha=0.0,
        )
        print(f"  Val R2={r['val']['r2']:.4f}, Test R2={r['test']['r2']:.4f}")
        all_results.append(r)

    # ═══════════════════════════════════════════════════════
    # 4CH PAC+STIM experiments
    # ═══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("4CH PAC+STIM FEATURES (ts=1)")
    print(f"{'='*70}")

    dataset_4ch = ROOT / "data" / "processed" / "muse_4ch" / "multiscale_temporal_lb20_hz5_ts1"
    train_4ch = load_split(dataset_4ch / "train_multiscale.npz")
    val_4ch = load_split(dataset_4ch / "val_multiscale.npz")
    test_4ch = load_split(dataset_4ch / "test_multiscale.npz")
    scalers_4ch = load_scalers(dataset_4ch / "scalers.npz")

    # 4ch has 49 features: 37 spectral + 7 PAC + 5 stim = 49
    # PAC indices: 37-43, stim indices: 44-48
    x_train_4ch_ps = train_4ch.x_seq[:, :, 37:49]
    x_val_4ch_ps = val_4ch.x_seq[:, :, 37:49]
    x_test_4ch_ps = test_4ch.x_seq[:, :, 37:49]

    persist_4ch = persistence_baseline(test_4ch)
    print(f"  Persistence test R2={persist_4ch['r2']:.4f}")
    all_results.append({"name": "persistence_4ch", "test": persist_4ch})

    for name, hidden, dil, drop, lr, wd in [
        ("tcn_h64_pac_stim_4ch", 64, [1, 2, 4, 8], 0.2, 1e-3, 1e-3),
        ("tcn_h32_pac_stim_4ch", 32, [1, 2, 4], 0.2, 1e-3, 1e-3),
        ("tcn_h64_highreg_pac_stim_4ch", 64, [1, 2, 4, 8], 0.3, 1e-3, 5e-3),
        ("tcn_h64_deep_pac_stim_4ch", 64, [1, 2, 4, 8, 16, 32], 0.2, 1e-3, 1e-3),
    ]:
        print(f"\n  --- {name} ---")
        r = train_eval_subset(
            name=name,
            x_train=x_train_4ch_ps, y_train_norm=train_4ch.y_future_norm,
            lp_train=train_4ch.last_pac,
            x_val=x_val_4ch_ps, y_val_norm=val_4ch.y_future_norm,
            lp_val=val_4ch.last_pac,
            x_test=x_test_4ch_ps, y_test_norm=test_4ch.y_future_norm,
            lp_test=test_4ch.last_pac,
            y_test_raw=test_4ch.y_future, y_val_raw=val_4ch.y_future,
            scalers=scalers_4ch,
            hidden=hidden, dilations=dil, kernel_size=3,
            dropout=drop, lr=lr, weight_decay=wd,
            batch_size=128, epochs=args.epochs, patience=20,
            seed=args.seed, loss_fn="huber", mixup_alpha=0.0,
        )
        print(f"  Val R2={r['val']['r2']:.4f}, Test R2={r['test']['r2']:.4f}")
        all_results.append(r)

    # ═══════════════════════════════════════════════════════
    # Ridge with hand-crafted PAC+stim summary features
    # ═══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("RIDGE ON PAC+STIM SUMMARY FEATURES")
    print(f"{'='*70}")

    def extract_summary(x: np.ndarray) -> np.ndarray:
        """Hand-crafted summary features from pac+stim sequences."""
        feats = []
        feats.append(x[:, -1, :])          # Last timestep
        feats.append(x.mean(axis=1))        # Mean over time
        feats.append(x.std(axis=1))         # Std over time
        feats.append(x[:, -1, :] - x[:, 0, :])  # Trend
        half = x.shape[1] // 2
        feats.append(x[:, -1, :] - x[:, :half, :].mean(axis=1))  # Recent change
        # Min, max
        feats.append(x.min(axis=1))
        feats.append(x.max(axis=1))
        return np.concatenate(feats, axis=1)

    from sklearn.linear_model import Ridge

    for ds_name, xtr, ytr, xval, yval, xte, yte, sc in [
        ("7ch_ts1", x_train_ps, train.y_future_norm, x_val_ps, val.y_future,
         x_test_ps, test.y_future, scalers),
        ("4ch_ts1", x_train_4ch_ps, train_4ch.y_future_norm, x_val_4ch_ps,
         val_4ch.y_future, x_test_4ch_ps, test_4ch.y_future, scalers_4ch),
    ]:
        X_tr = extract_summary(xtr)
        X_val = extract_summary(xval)
        X_te = extract_summary(xte)

        for alpha in [0.1, 1.0, 10.0]:
            model = Ridge(alpha=alpha)
            model.fit(X_tr, ytr)

            pred_val = denorm(model.predict(X_val), sc["y_future_mean"], sc["y_future_std"])
            pred_test = denorm(model.predict(X_te), sc["y_future_mean"], sc["y_future_std"])
            val_m = compute_metrics(yval, pred_val)
            test_m = compute_metrics(yte, pred_test)

            name = f"ridge_pac_stim_summary_{ds_name}_a{alpha}"
            print(f"  {name}: val R2={val_m['r2']:.4f}, test R2={test_m['r2']:.4f}")
            all_results.append({"name": name, "val": val_m, "test": test_m})

    # ── Save ──
    out_path = RESULTS_DIR / "pac_stim_focused.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    # ── Summary ──
    print(f"\n{'='*70}")
    print("PAC+STIM FOCUSED SUMMARY")
    print(f"{'='*70}")
    print(f"{'Name':<45} {'Val R2':>8} {'Test R2':>8} {'Params':>8}")
    print("-" * 75)
    for r in all_results:
        name = r.get("name", "?")
        val_r2 = r.get("val", {}).get("r2", float("nan"))
        test_r2 = r.get("test", {}).get("r2", float("nan"))
        n_params = r.get("n_params", 0)
        print(f"{name:<45} {val_r2:>8.4f} {test_r2:>8.4f} {n_params:>8,}")


if __name__ == "__main__":
    main()
