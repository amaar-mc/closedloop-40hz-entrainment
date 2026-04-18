"""
Experiments targeting the val-test generalization gap.

The core problem: models achieve val R2=0.3-0.6 but test R2 near 0 on 7ch horizon=5.
This suggests overfitting to subject-specific patterns in train/val that don't
transfer to unseen test subjects.

Approaches:
1. Subject-wise analysis (where does prediction fail?)
2. Heavy regularization (high dropout, weight decay, smaller model)
3. Mixup augmentation
4. Gradient penalty for smoother predictions
5. Feature ablation (which features help generalization?)
6. Per-subject z-scored targets
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

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
    RESULTS_DIR,
    SplitData,
)


# ─── Per-subject analysis ───────────────────────────────────────────────────

def per_subject_persistence(data: SplitData) -> Dict[str, Dict[str, float]]:
    """Compute persistence R2 per subject."""
    results = {}
    for subj in np.unique(data.subjects):
        mask = data.subjects == subj
        y_true = data.y_future[mask]
        y_pred = data.last_pac[mask]
        results[subj] = compute_metrics(y_true, y_pred)
    return results


def per_subject_evaluate(
    model: nn.Module,
    data: SplitData,
    device: torch.device,
    scalers: Dict[str, float],
    batch_size: int,
) -> Dict[str, Dict[str, float]]:
    """Evaluate model per subject."""
    model.eval()
    results = {}
    for subj in np.unique(data.subjects):
        mask = data.subjects == subj
        x = torch.from_numpy(data.x_seq[mask]).float()
        y_true = data.y_future[mask]

        all_pred = []
        with torch.no_grad():
            for i in range(0, len(x), batch_size):
                batch_x = x[i:i+batch_size].to(device)
                pred = model(batch_x).cpu().numpy()
                all_pred.append(pred)

        pred_norm = np.concatenate(all_pred)
        pred_raw = denorm(pred_norm, scalers["y_future_mean"], scalers["y_future_std"])
        results[subj] = compute_metrics(y_true, pred_raw)
    return results


# ─── Mixup dataset ──────────────────────────────────────────────────────────

class MixupSeqDataset(Dataset):
    """Sequence dataset with mixup augmentation applied at getitem time."""

    def __init__(self, x: np.ndarray, y_norm: np.ndarray, last_pac: np.ndarray,
                 alpha: float) -> None:
        self.x = torch.from_numpy(x).float()
        self.y = torch.from_numpy(y_norm).float()
        self.last_pac = torch.from_numpy(last_pac).float()
        self.alpha = alpha
        self.n = self.x.shape[0]

    def __len__(self) -> int:
        return self.n

    def __getitem__(self, i: int) -> Dict[str, torch.Tensor]:
        if self.alpha > 0:
            lam = np.random.beta(self.alpha, self.alpha)
        else:
            lam = 1.0

        j = np.random.randint(0, self.n)
        x_mixed = lam * self.x[i] + (1 - lam) * self.x[j]
        y_mixed = lam * self.y[i] + (1 - lam) * self.y[j]
        lp_mixed = lam * self.last_pac[i] + (1 - lam) * self.last_pac[j]

        return {"x": x_mixed, "y": y_mixed, "last_pac": lp_mixed}


# ─── Tiny regularized TCN ──────────────────────────────────────────────────

class TinyTCN(nn.Module):
    """Minimalist TCN to test if smaller = better generalization."""

    def __init__(self, n_features: int, hidden: int, dropout: float) -> None:
        super().__init__()
        self.in_proj = nn.Sequential(
            nn.Linear(n_features, hidden),
            nn.LayerNorm(hidden),
            nn.GELU(),
        )
        # Just 2 conv blocks
        self.block1 = CausalConvBlock(hidden, 3, 1, dropout)
        self.block2 = CausalConvBlock(hidden, 3, 2, dropout)
        self.attn = nn.Conv1d(hidden, 1, 1)
        self.head = nn.Sequential(
            nn.Linear(hidden, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.in_proj(x).transpose(1, 2)
        x = self.block1(x)
        x = self.block2(x)
        w = torch.softmax(self.attn(x), dim=-1)
        z = (x * w).sum(dim=-1)
        return self.head(z).squeeze(-1)

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# ─── Feature-subset experiments ─────────────────────────────────────────────

def make_feature_subsets(n_features: int) -> Dict[str, np.ndarray]:
    """Define feature subsets to test which features help generalization."""
    # Based on the dataset: 61 spectral + 7 PAC + 5 stim context = 73
    subsets = {}
    # All features
    subsets["all"] = np.arange(n_features)
    # PAC features only (indices 61-67)
    subsets["pac_only"] = np.arange(61, 68)
    # PAC + stim context (indices 61-72)
    subsets["pac_stim"] = np.arange(61, 73)
    # Spectral only (indices 0-60)
    subsets["spectral_only"] = np.arange(0, 61)
    # Spectral + PAC (no stim context)
    subsets["spectral_pac"] = np.arange(0, 68)
    # PAC + stim + first 10 spectral
    subsets["pac_stim_spec10"] = np.concatenate([np.arange(0, 10), np.arange(61, 73)])
    return subsets


def train_with_feature_subset(
    train_data: SplitData,
    val_data: SplitData,
    test_data: SplitData,
    scalers: Dict[str, float],
    feature_idx: np.ndarray,
    hidden: int,
    dropout: float,
    lr: float,
    weight_decay: float,
    epochs: int,
    patience: int,
    seed: int,
) -> Dict:
    """Train a TCN on a subset of features."""
    set_seed(seed)
    device = get_device()

    x_train = train_data.x_seq[:, :, feature_idx]
    x_val = val_data.x_seq[:, :, feature_idx]
    x_test = test_data.x_seq[:, :, feature_idx]
    n_feat = len(feature_idx)

    train_ds = SeqDataset(x_train, train_data.y_future_norm, train_data.last_pac)
    val_ds = SeqDataset(x_val, val_data.y_future_norm, val_data.last_pac)
    test_ds = SeqDataset(x_test, test_data.y_future_norm, test_data.last_pac)

    g = torch.Generator()
    g.manual_seed(seed)
    train_loader = DataLoader(train_ds, batch_size=128, shuffle=True, num_workers=0, generator=g)
    val_loader = DataLoader(val_ds, batch_size=128, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=128, shuffle=False, num_workers=0)

    model = ImprovedTCN(n_feat, hidden=hidden, kernel_size=3,
                         dilations=[1, 2, 4, 8], dropout=dropout, n_heads=1)
    model.to(device)

    criterion = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max",
                                                            factor=0.5, patience=5)

    yf_mean = scalers["y_future_mean"]
    yf_std = scalers["y_future_std"]

    best_val_r2 = -np.inf
    best_state = None
    best_epoch = 0
    no_improve = 0

    for epoch in range(1, epochs + 1):
        model.train()
        for batch in train_loader:
            x = batch["x"].to(device)
            y = batch["y"].to(device)
            pred = model(x)
            loss = criterion(pred, y)
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

        model.eval()
        all_pred, all_true = [], []
        with torch.no_grad():
            for batch in val_loader:
                x = batch["x"].to(device)
                pred = model(x).cpu().numpy()
                all_pred.append(pred)
                all_true.append(batch["y"].numpy())

        pred_raw = denorm(np.concatenate(all_pred), yf_mean, yf_std)
        true_raw = denorm(np.concatenate(all_true), yf_mean, yf_std)
        val_r2 = r2_score(true_raw, pred_raw)
        scheduler.step(val_r2)

        if val_r2 > best_val_r2:
            best_val_r2 = val_r2
            best_epoch = epoch
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            no_improve = 0
        else:
            no_improve += 1

        if no_improve >= patience:
            break

    if best_state is not None:
        model.load_state_dict(best_state)
    model.to(device)

    # Evaluate on test
    all_pred, all_true = [], []
    with torch.no_grad():
        for batch in test_loader:
            x = batch["x"].to(device)
            pred = model(x).cpu().numpy()
            all_pred.append(pred)
            all_true.append(batch["y"].numpy())

    pred_raw = denorm(np.concatenate(all_pred), yf_mean, yf_std)
    true_raw = denorm(np.concatenate(all_true), yf_mean, yf_std)
    test_metrics = compute_metrics(true_raw, pred_raw)

    # Also evaluate on val
    all_pred, all_true = [], []
    with torch.no_grad():
        for batch in val_loader:
            x = batch["x"].to(device)
            pred = model(x).cpu().numpy()
            all_pred.append(pred)
            all_true.append(batch["y"].numpy())
    pred_raw = denorm(np.concatenate(all_pred), yf_mean, yf_std)
    true_raw = denorm(np.concatenate(all_true), yf_mean, yf_std)
    val_metrics = compute_metrics(true_raw, pred_raw)

    return {
        "n_features": n_feat,
        "n_params": model.count_parameters(),
        "best_epoch": best_epoch,
        "val": val_metrics,
        "test": test_metrics,
    }


# ─── Training with mixup ───────────────────────────────────────────────────

def train_with_mixup(
    train_data: SplitData,
    val_data: SplitData,
    test_data: SplitData,
    scalers: Dict[str, float],
    alpha: float,
    hidden: int,
    dilations: List[int],
    dropout: float,
    lr: float,
    weight_decay: float,
    epochs: int,
    patience: int,
    seed: int,
) -> Dict:
    set_seed(seed)
    device = get_device()
    n_feat = train_data.x_seq.shape[-1]

    train_ds = MixupSeqDataset(train_data.x_seq, train_data.y_future_norm,
                                train_data.last_pac, alpha=alpha)
    val_ds = SeqDataset(val_data.x_seq, val_data.y_future_norm, val_data.last_pac)
    test_ds = SeqDataset(test_data.x_seq, test_data.y_future_norm, test_data.last_pac)

    g = torch.Generator()
    g.manual_seed(seed)
    train_loader = DataLoader(train_ds, batch_size=128, shuffle=True, num_workers=0, generator=g)
    val_loader = DataLoader(val_ds, batch_size=128, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=128, shuffle=False, num_workers=0)

    model = ImprovedTCN(n_feat, hidden=hidden, kernel_size=3,
                         dilations=dilations, dropout=dropout, n_heads=1)
    model.to(device)

    criterion = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max",
                                                            factor=0.5, patience=5)

    yf_mean = scalers["y_future_mean"]
    yf_std = scalers["y_future_std"]

    best_val_r2 = -np.inf
    best_state = None
    best_epoch = 0
    no_improve = 0

    for epoch in range(1, epochs + 1):
        model.train()
        for batch in train_loader:
            x = batch["x"].to(device)
            y = batch["y"].to(device)
            pred = model(x)
            loss = criterion(pred, y)
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

        model.eval()
        all_pred, all_true = [], []
        with torch.no_grad():
            for batch in val_loader:
                x = batch["x"].to(device)
                pred = model(x).cpu().numpy()
                all_pred.append(pred)
                all_true.append(batch["y"].numpy())

        pred_raw = denorm(np.concatenate(all_pred), yf_mean, yf_std)
        true_raw = denorm(np.concatenate(all_true), yf_mean, yf_std)
        val_r2 = r2_score(true_raw, pred_raw)
        scheduler.step(val_r2)

        if val_r2 > best_val_r2:
            best_val_r2 = val_r2
            best_epoch = epoch
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            no_improve = 0
        else:
            no_improve += 1

        if no_improve >= patience:
            break

    if best_state is not None:
        model.load_state_dict(best_state)
    model.to(device)

    # Evaluate
    from experimental.run_experiments import evaluate_model
    val_metrics = evaluate_model(model, val_loader, device, scalers)
    test_metrics = evaluate_model(model, test_loader, device, scalers)

    return {
        "alpha": alpha,
        "n_params": model.count_parameters(),
        "best_epoch": best_epoch,
        "val": val_metrics,
        "test": test_metrics,
    }


# ─── Training with heavy regularization ────────────────────────────────────

def train_heavily_regularized(
    train_data: SplitData,
    val_data: SplitData,
    test_data: SplitData,
    scalers: Dict[str, float],
    name: str,
    hidden: int,
    dilations: List[int],
    dropout: float,
    lr: float,
    weight_decay: float,
    epochs: int,
    patience: int,
    seed: int,
) -> Dict:
    set_seed(seed)
    device = get_device()
    n_feat = train_data.x_seq.shape[-1]

    train_ds = SeqDataset(train_data.x_seq, train_data.y_future_norm, train_data.last_pac)
    val_ds = SeqDataset(val_data.x_seq, val_data.y_future_norm, val_data.last_pac)
    test_ds = SeqDataset(test_data.x_seq, test_data.y_future_norm, test_data.last_pac)

    g = torch.Generator()
    g.manual_seed(seed)
    train_loader = DataLoader(train_ds, batch_size=128, shuffle=True, num_workers=0, generator=g)
    val_loader = DataLoader(val_ds, batch_size=128, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=128, shuffle=False, num_workers=0)

    if hidden <= 24:
        model = TinyTCN(n_feat, hidden=hidden, dropout=dropout)
    else:
        model = ImprovedTCN(n_feat, hidden=hidden, kernel_size=3,
                             dilations=dilations, dropout=dropout, n_heads=1)
    model.to(device)

    criterion = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max",
                                                            factor=0.5, patience=5)

    yf_mean = scalers["y_future_mean"]
    yf_std = scalers["y_future_std"]

    best_val_r2 = -np.inf
    best_state = None
    best_epoch = 0
    no_improve = 0

    for epoch in range(1, epochs + 1):
        model.train()
        for batch in train_loader:
            x = batch["x"].to(device)
            y = batch["y"].to(device)
            pred = model(x)
            loss = criterion(pred, y)
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

        model.eval()
        all_pred, all_true = [], []
        with torch.no_grad():
            for batch in val_loader:
                x = batch["x"].to(device)
                pred = model(x).cpu().numpy()
                all_pred.append(pred)
                all_true.append(batch["y"].numpy())

        pred_raw = denorm(np.concatenate(all_pred), yf_mean, yf_std)
        true_raw = denorm(np.concatenate(all_true), yf_mean, yf_std)
        val_r2 = r2_score(true_raw, pred_raw)
        scheduler.step(val_r2)

        if val_r2 > best_val_r2:
            best_val_r2 = val_r2
            best_epoch = epoch
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            no_improve = 0
        else:
            no_improve += 1

        if epoch <= 3 or epoch % 10 == 0 or val_r2 >= best_val_r2:
            print(f"  [{name}] Epoch {epoch:03d} | val_r2={val_r2:.4f}" +
                  (" *" if epoch == best_epoch else ""))

        if no_improve >= patience:
            print(f"  [{name}] Early stop at epoch {epoch}")
            break

    if best_state is not None:
        model.load_state_dict(best_state)
    model.to(device)

    from experimental.run_experiments import evaluate_model
    val_metrics = evaluate_model(model, val_loader, device, scalers)
    test_metrics = evaluate_model(model, test_loader, device, scalers)

    return {
        "name": name,
        "n_params": model.count_parameters(),
        "best_epoch": best_epoch,
        "val": val_metrics,
        "test": test_metrics,
    }


# ─── Main ───────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["7ch", "4ch"], default="7ch")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=80)
    args = parser.parse_args()

    if args.dataset == "7ch":
        dataset_dir = ROOT / "data" / "processed" / "multiscale_temporal_lb20_hz5_ts1"
    else:
        dataset_dir = ROOT / "data" / "processed" / "muse_4ch" / "multiscale_temporal_lb20_hz5_ts1"

    train = load_split(dataset_dir / "train_multiscale.npz")
    val = load_split(dataset_dir / "val_multiscale.npz")
    test = load_split(dataset_dir / "test_multiscale.npz")
    scalers = load_scalers(dataset_dir / "scalers.npz")

    all_results = []

    # ── 1. Per-subject analysis with persistence ──
    print(f"\n{'='*70}")
    print("PER-SUBJECT PERSISTENCE ANALYSIS")
    print(f"{'='*70}")
    persist_test = per_subject_persistence(test)
    for subj, m in sorted(persist_test.items()):
        print(f"  {subj}: R2={m['r2']:.4f}, corr={m['corr']:.4f}")

    persist_val = per_subject_persistence(val)
    for subj, m in sorted(persist_val.items()):
        print(f"  {subj}: R2={m['r2']:.4f}, corr={m['corr']:.4f}")

    all_results.append({"section": "per_subject_persistence",
                         "test": persist_test, "val": persist_val})

    # ── 2. Feature ablation ──
    print(f"\n{'='*70}")
    print("FEATURE ABLATION")
    print(f"{'='*70}")
    subsets = make_feature_subsets(train.x_seq.shape[-1])
    feat_results = {}
    for subset_name, idx in subsets.items():
        print(f"\n  Testing subset: {subset_name} ({len(idx)} features)")
        r = train_with_feature_subset(
            train, val, test, scalers,
            feature_idx=idx,
            hidden=64, dropout=0.2,
            lr=1e-3, weight_decay=1e-3,
            epochs=args.epochs, patience=20, seed=args.seed,
        )
        feat_results[subset_name] = r
        print(f"    Val R2={r['val']['r2']:.4f}, Test R2={r['test']['r2']:.4f} "
              f"(n_feat={r['n_features']}, params={r['n_params']:,})")

    all_results.append({"section": "feature_ablation", "results": feat_results})

    # ── 3. Mixup augmentation ──
    print(f"\n{'='*70}")
    print("MIXUP AUGMENTATION")
    print(f"{'='*70}")
    mixup_results = {}
    for alpha in [0.1, 0.2, 0.5, 1.0]:
        print(f"\n  Mixup alpha={alpha}")
        r = train_with_mixup(
            train, val, test, scalers,
            alpha=alpha, hidden=64, dilations=[1, 2, 4, 8],
            dropout=0.2, lr=1e-3, weight_decay=1e-3,
            epochs=args.epochs, patience=20, seed=args.seed,
        )
        mixup_results[str(alpha)] = r
        print(f"    Val R2={r['val']['r2']:.4f}, Test R2={r['test']['r2']:.4f}")

    all_results.append({"section": "mixup", "results": mixup_results})

    # ── 4. Heavy regularization ──
    print(f"\n{'='*70}")
    print("REGULARIZATION EXPERIMENTS")
    print(f"{'='*70}")
    reg_results = {}

    configs = [
        ("tiny_h16", 16, [1, 2], 0.3, 1e-3, 5e-3),
        ("tiny_h24", 24, [1, 2], 0.3, 1e-3, 5e-3),
        ("small_h32_highdrop", 32, [1, 2, 4], 0.4, 1e-3, 1e-2),
        ("medium_h64_highdrop", 64, [1, 2, 4, 8], 0.4, 1e-3, 5e-3),
        ("medium_h64_veryhighdrop", 64, [1, 2, 4, 8], 0.5, 1e-3, 1e-2),
        ("deep_h64_highdrop", 64, [1, 2, 4, 8, 16, 32], 0.3, 1e-3, 5e-3),
    ]

    for name, hidden, dilations, dropout, lr, wd in configs:
        print(f"\n  Config: {name}")
        r = train_heavily_regularized(
            train, val, test, scalers,
            name=name, hidden=hidden, dilations=dilations,
            dropout=dropout, lr=lr, weight_decay=wd,
            epochs=args.epochs, patience=20, seed=args.seed,
        )
        reg_results[name] = r
        print(f"    Val R2={r['val']['r2']:.4f}, Test R2={r['test']['r2']:.4f}")

    all_results.append({"section": "regularization", "results": reg_results})

    # ── Save results ──
    out_path = RESULTS_DIR / f"generalization_{args.dataset}.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    # ── Summary ──
    print(f"\n{'='*70}")
    print(f"GENERALIZATION EXPERIMENTS SUMMARY: {args.dataset}")
    print(f"{'='*70}")

    print("\nFeature Ablation:")
    print(f"  {'Subset':<20} {'Val R2':>8} {'Test R2':>8} {'Features':>8}")
    print("  " + "-" * 50)
    for name, r in feat_results.items():
        print(f"  {name:<20} {r['val']['r2']:>8.4f} {r['test']['r2']:>8.4f} {r['n_features']:>8}")

    print("\nMixup:")
    print(f"  {'Alpha':<10} {'Val R2':>8} {'Test R2':>8}")
    print("  " + "-" * 30)
    for alpha, r in mixup_results.items():
        print(f"  {alpha:<10} {r['val']['r2']:>8.4f} {r['test']['r2']:>8.4f}")

    print("\nRegularization:")
    print(f"  {'Config':<30} {'Val R2':>8} {'Test R2':>8} {'Params':>8}")
    print("  " + "-" * 60)
    for name, r in reg_results.items():
        print(f"  {name:<30} {r['val']['r2']:>8.4f} {r['test']['r2']:>8.4f} "
              f"{r['n_params']:>8,}")


if __name__ == "__main__":
    main()
