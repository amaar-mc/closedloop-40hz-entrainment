"""
Train XGBoost on flattened features for PAC forecasting (architecture exploration).

Non-neural baseline: flattens (20, 12) PAC+Stim features into a 240-dim vector
and trains gradient-boosted trees. Uses 5-seed averaging for fair comparison.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import r2_score
from xgboost import XGBRegressor

# --- Constants ---
DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "processed" / "multiscale_temporal_lb20_hz5_ts1"
PAC_STIM_INDICES = list(range(61, 73))  # 12 features
SEEDS = [42, 123, 456, 789, 1024]


def load_data() -> tuple:
    """Load, subset PAC+Stim features, and flatten for XGBoost.

    Trains on normalized targets for numerical stability, then
    denormalizes predictions for R2 evaluation in raw PAC space.
    """
    splits = {}
    for split in ["train", "val", "test"]:
        d = np.load(DATA_DIR / f"{split}_multiscale.npz", allow_pickle=True)
        x = d["x_seq"][:, :, PAC_STIM_INDICES]  # (N, 20, 12)
        x_flat = x.reshape(x.shape[0], -1)       # (N, 240)
        y_norm = d["y_future_norm"]               # (N,) z-scored
        y_raw = d["y_future"]                     # (N,) unnormalized
        splits[split] = {"x": x_flat, "y_norm": y_norm, "y_raw": y_raw}

    scalers = np.load(DATA_DIR / "scalers.npz")
    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])
    return splits, yf_mean, yf_std


def denorm(y_norm: np.ndarray, mean: float, std: float) -> np.ndarray:
    return y_norm * std + mean


def train_single_run(splits: dict, yf_mean: float, yf_std: float, seed: int) -> dict:
    """Train a single XGBoost model on normalized targets."""
    model = XGBRegressor(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=seed,
        n_jobs=-1,
        tree_method="hist",
        early_stopping_rounds=30,
    )

    model.fit(
        splits["train"]["x"],
        splits["train"]["y_norm"],
        eval_set=[(splits["val"]["x"], splits["val"]["y_norm"])],
        verbose=False,
    )

    # Predict in normalized space, denormalize for R2 in raw PAC space
    val_pred_norm = model.predict(splits["val"]["x"])
    test_pred_norm = model.predict(splits["test"]["x"])

    val_pred = denorm(val_pred_norm, yf_mean, yf_std)
    test_pred = denorm(test_pred_norm, yf_mean, yf_std)

    val_r2 = r2_score(splits["val"]["y_raw"], val_pred)
    test_r2 = r2_score(splits["test"]["y_raw"], test_pred)

    return {
        "seed": seed,
        "n_estimators_used": int(model.best_iteration) if model.best_iteration else int(model.n_estimators),
        "best_val_r2": float(val_r2),
        "test_r2": float(test_r2),
    }


def main() -> None:
    print("=" * 70)
    print("ARCHITECTURE EXPLORATION: XGBoost (Flattened Features)")
    print("=" * 70)

    splits, yf_mean, yf_std = load_data()
    print(f"Train: {splits['train']['x'].shape}, Val: {splits['val']['x'].shape}, Test: {splits['test']['x'].shape}")

    seed_results = []
    for seed in SEEDS:
        t0 = time.time()
        r = train_single_run(splits, yf_mean, yf_std, seed)
        elapsed = time.time() - t0
        print(f"  seed={seed}: val_R2={r['best_val_r2']:.4f}, test_R2={r['test_r2']:.4f} "
              f"(n_trees={r['n_estimators_used']}, {elapsed:.1f}s)")
        seed_results.append(r)

    val_r2s = [r["best_val_r2"] for r in seed_results]
    test_r2s = [r["test_r2"] for r in seed_results]

    results = {
        "model": "XGBoost",
        "input_dim": 240,
        "seeds": SEEDS,
        "val_r2_mean": float(np.mean(val_r2s)),
        "val_r2_std": float(np.std(val_r2s)),
        "test_r2_mean": float(np.mean(test_r2s)),
        "test_r2_std": float(np.std(test_r2s)),
        "per_seed": seed_results,
    }

    print(f"\nXGBoost 5-seed: val_R2={results['val_r2_mean']:.4f}+/-{results['val_r2_std']:.4f}, "
          f"test_R2={results['test_r2_mean']:.4f}+/-{results['test_r2_std']:.4f}")

    out_path = Path(__file__).resolve().parent / "results_xgboost.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
