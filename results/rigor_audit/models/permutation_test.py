"""
Permutation test for PAC+Stim feature model.

Shuffles target labels, trains for 20 epochs on the 12 PAC+Stim features only,
and confirms R² drops to near zero (expected for a non-leaking model).

If the shuffled model still achieves R² > 0.1, something is wrong.

Usage:
    python results/rigor_audit/models/permutation_test.py
"""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data" / "processed" / "multiscale_temporal_lb20_hz5_ts1"

sys.path.insert(0, str(ROOT))
from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN


def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / (ss_tot + 1e-12))


def load_pac_stim_only(split_name: str) -> dict:
    """Load a split and select only PAC+Stim features (indices 61:73)."""
    d = np.load(DATA_DIR / f"{split_name}_multiscale.npz", allow_pickle=True)
    feature_names = list(d["feature_names"])

    # PAC features: indices 61-67 (pac_current through pac_diff4)
    # Stim features: indices 68-72 (stim_state through cycle_phase_cos)
    pac_stim_indices = [i for i, name in enumerate(feature_names)
                        if name.startswith("pac_") or name.startswith("stim_")
                        or name.startswith("time_since_") or name.startswith("cycle_")]
    pac_stim_names = [feature_names[i] for i in pac_stim_indices]

    x_full = d["x_seq"]  # already normalized
    x_subset = x_full[:, :, pac_stim_indices]

    return {
        "x_seq": x_subset,
        "y_future_norm": d["y_future_norm"],
        "y_future": d["y_future"],
        "last_pac": d["last_pac"],
        "feature_names": pac_stim_names,
        "feature_indices": pac_stim_indices,
    }


def train_model(
    x_train: torch.Tensor,
    y_train: torch.Tensor,
    x_val: torch.Tensor,
    y_val: torch.Tensor,
    n_features: int,
    device: torch.device,
    n_epochs: int,
    seed: int,
    label: str,
) -> dict:
    """Train a small TCN and return val metrics."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    cfg = ModelConfig(
        n_features=n_features,
        hidden=32,
        kernel_size=3,
        dilations=[1, 2, 4, 8],
        dropout=0.1,
    )
    model = MultiscaleCausalTCN(cfg).to(device)

    train_ds = TensorDataset(x_train, y_train)
    val_ds = TensorDataset(x_val, y_val)
    train_loader = DataLoader(train_ds, batch_size=128, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=256, shuffle=False)

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-3)
    huber = nn.HuberLoss(delta=1.0)

    best_val_r2 = -np.inf
    for epoch in range(1, n_epochs + 1):
        model.train()
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            out = model(xb)
            loss = huber(out["future"], yb)
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

        # Evaluate
        model.eval()
        preds = []
        trues = []
        with torch.no_grad():
            for xb, yb in val_loader:
                xb = xb.to(device)
                out = model(xb)
                preds.append(out["future"].cpu().numpy())
                trues.append(yb.numpy())
        preds = np.concatenate(preds)
        trues = np.concatenate(trues)
        r2 = _r2(trues, preds)

        if r2 > best_val_r2:
            best_val_r2 = r2

        if epoch <= 3 or epoch % 5 == 0 or epoch == n_epochs:
            print(f"  [{label}] Epoch {epoch:02d}/{n_epochs}: val_R²={r2:.4f} (best={best_val_r2:.4f})")

    return {"best_val_r2": best_val_r2, "final_val_r2": _r2(trues, preds)}


def main() -> None:
    n_epochs = 20
    n_permutations = 5
    seed = 42

    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    print("=" * 70)
    print("PERMUTATION TEST — PAC+Stim Features Only (12 features)")
    print(f"Device: {device}, Epochs: {n_epochs}, Permutations: {n_permutations}")
    print("=" * 70)
    print()

    train_data = load_pac_stim_only("train")
    val_data = load_pac_stim_only("val")

    n_features = train_data["x_seq"].shape[-1]
    print(f"Features ({n_features}): {train_data['feature_names']}")
    print(f"Train: {train_data['x_seq'].shape}, Val: {val_data['x_seq'].shape}")
    print()

    x_train = torch.from_numpy(train_data["x_seq"]).float()
    y_train = torch.from_numpy(train_data["y_future_norm"]).float()
    x_val = torch.from_numpy(val_data["x_seq"]).float()
    y_val = torch.from_numpy(val_data["y_future_norm"]).float()

    scalers = np.load(DATA_DIR / "scalers.npz")
    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])

    # 1. Train with real labels
    print("-" * 70)
    print("PHASE 1: Train with REAL labels")
    print("-" * 70)
    t0 = time.time()
    real_result = train_model(
        x_train, y_train, x_val, y_val,
        n_features=n_features, device=device,
        n_epochs=n_epochs, seed=seed, label="REAL",
    )
    real_time = time.time() - t0
    print(f"  Real labels: best val R² = {real_result['best_val_r2']:.4f} ({real_time:.1f}s)")
    print()

    # 2. Train with shuffled labels (multiple permutations)
    print("-" * 70)
    print(f"PHASE 2: Train with SHUFFLED labels ({n_permutations} permutations)")
    print("-" * 70)
    perm_r2s = []
    for p in range(n_permutations):
        perm_seed = seed + p + 1
        rng = np.random.RandomState(perm_seed)

        # Shuffle training labels
        y_train_shuf = y_train[torch.from_numpy(rng.permutation(len(y_train)))]
        # Shuffle val labels independently
        y_val_shuf = y_val[torch.from_numpy(rng.permutation(len(y_val)))]

        perm_result = train_model(
            x_train, y_train_shuf, x_val, y_val_shuf,
            n_features=n_features, device=device,
            n_epochs=n_epochs, seed=perm_seed, label=f"PERM-{p+1}",
        )
        perm_r2s.append(perm_result["best_val_r2"])
        print(f"  Permutation {p+1}: best val R² = {perm_result['best_val_r2']:.4f}")
        print()

    # 3. Summary
    mean_perm_r2 = float(np.mean(perm_r2s))
    max_perm_r2 = float(np.max(perm_r2s))
    real_r2 = real_result["best_val_r2"]

    print("=" * 70)
    print("PERMUTATION TEST RESULTS")
    print("=" * 70)
    print(f"  Real labels best val R²:     {real_r2:.4f}")
    print(f"  Shuffled labels mean R²:     {mean_perm_r2:.4f}")
    print(f"  Shuffled labels max R²:      {max_perm_r2:.4f}")
    print(f"  Gap (real - shuffled mean):   {real_r2 - mean_perm_r2:.4f}")
    print()

    # Verdict
    if max_perm_r2 > 0.1:
        print("  [FAIL] Shuffled model R² > 0.1 — possible structural leakage!")
        verdict = False
    elif real_r2 < mean_perm_r2 + 0.02:
        print("  [FAIL] Real model barely better than shuffled — model may not be learning signal!")
        verdict = False
    else:
        print("  [PASS] Shuffled R² near zero, real R² substantially higher.")
        print("         Signal is genuine, not an artifact of data structure.")
        verdict = True

    print()
    sys.exit(0 if verdict else 1)


if __name__ == "__main__":
    main()
