"""
Horizon sweep: evaluate persistence, Ridge and TCN baselines at multiple
prediction horizons.

Usage:
    python temporal_multiscale/sweep_horizons.py
    python temporal_multiscale/sweep_horizons.py --horizons 1,2,3,5,8,10
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Dict, List

import numpy as np
from sklearn.linear_model import Ridge


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / (ss_tot + 1e-12))


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


# ---------------------------------------------------------------------------
# Baseline evaluators (work on pre-built multiscale NPZ files)
# ---------------------------------------------------------------------------

def persistence_baseline(dataset_dir: Path) -> Dict[str, float]:
    """Persistence baseline: predict future PAC = current PAC (last_pac)."""
    test = np.load(dataset_dir / "test_multiscale.npz", allow_pickle=True)
    y_true = test["y_future"].astype(np.float64)
    y_pred = test["last_pac"].astype(np.float64)
    return {"r2": _r2(y_true, y_pred), "rmse": _rmse(y_true, y_pred)}


def ridge_baseline(dataset_dir: Path, alpha: float = 1.0) -> Dict[str, float]:
    """Ridge regression on flattened feature sequences."""
    train = np.load(dataset_dir / "train_multiscale.npz", allow_pickle=True)
    test = np.load(dataset_dir / "test_multiscale.npz", allow_pickle=True)

    x_train = train["x_seq"].astype(np.float64)
    x_test = test["x_seq"].astype(np.float64)
    y_train = train["y_future"].astype(np.float64)
    y_test = test["y_future"].astype(np.float64)

    # Flatten sequences: (N, T, F) -> (N, T*F)
    x_train_flat = x_train.reshape(x_train.shape[0], -1)
    x_test_flat = x_test.reshape(x_test.shape[0], -1)

    ridge = Ridge(alpha=alpha)
    ridge.fit(x_train_flat, y_train)
    y_pred = ridge.predict(x_test_flat)

    return {"r2": _r2(y_test, y_pred), "rmse": _rmse(y_test, y_pred)}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sweep prediction horizons.")
    p.add_argument("--python", default=".\\venv\\Scripts\\python.exe", type=str)
    p.add_argument("--horizons", default="1,2,3,5,8,10", type=str,
                   help="Comma-separated horizon values")
    p.add_argument("--lookback", default=20, type=int)
    p.add_argument("--target-smooth-window", default=5, type=int)
    p.add_argument("--epochs", default=80, type=int)
    p.add_argument("--patience", default=20, type=int)
    p.add_argument("--batch-size", default=256, type=int)
    p.add_argument("--hidden", default=64, type=int)
    p.add_argument("--dropout", default=0.2, type=float)
    p.add_argument("--weight-decay", default=1e-3, type=float)
    p.add_argument("--pool-type", default="attention", type=str)
    p.add_argument("--seed", default=42, type=int)
    p.add_argument("--models-dir", default="models", type=str)
    p.add_argument("--skip-tcn", action="store_true",
                   help="Only compute persistence and Ridge baselines")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    models_dir = Path(args.models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)

    horizons = [int(h.strip()) for h in args.horizons.split(",") if h.strip()]
    results: List[Dict] = []

    for hz in horizons:
        print(f"\n{'='*70}")
        print(f"HORIZON = {hz}")
        print(f"{'='*70}")

        dataset_dir = Path(
            f"data/processed/multiscale_temporal_lb{args.lookback}_hz{hz}"
            f"_ts{args.target_smooth_window}_clean"
        )
        run_name = (
            f"multiscale_tcn_lb{args.lookback}_hz{hz}"
            f"_ts{args.target_smooth_window}"
        )

        # Build dataset (always rebuild for each horizon)
        build_cmd = (
            f'{args.python} temporal_multiscale/build_multiscale_dataset.py '
            f'--output-dir "{dataset_dir}" '
            f'--lookback {args.lookback} --horizon {hz} '
            f'--target-smooth-window {args.target_smooth_window}'
        )
        print(f"\n[BUILD] {build_cmd}")
        rc = subprocess.call(build_cmd, shell=True)
        if rc != 0:
            print(f"[WARN] Dataset build failed for hz={hz} (exit={rc})")
            continue

        # Persistence baseline
        try:
            persist = persistence_baseline(dataset_dir)
            print(f"  Persistence: R2={persist['r2']:.4f}, RMSE={persist['rmse']:.6f}")
        except Exception as e:
            print(f"  Persistence failed: {e}")
            persist = {"r2": float("nan"), "rmse": float("nan")}

        # Ridge baseline
        try:
            ridge = ridge_baseline(dataset_dir)
            print(f"  Ridge:       R2={ridge['r2']:.4f}, RMSE={ridge['rmse']:.6f}")
        except Exception as e:
            print(f"  Ridge failed: {e}")
            ridge = {"r2": float("nan"), "rmse": float("nan")}

        # TCN training
        tcn_r2 = float("nan")
        tcn_rmse = float("nan")
        if not args.skip_tcn:
            train_cmd = (
                f'{args.python} temporal_multiscale/train_multiscale_tcn.py '
                f'--dataset-dir "{dataset_dir}" '
                f'--models-dir "{args.models_dir}" '
                f'--run-name "{run_name}" '
                f'--lookback {args.lookback} --horizon {hz} '
                f'--target-smooth-window {args.target_smooth_window} '
                f'--epochs {args.epochs} --patience {args.patience} '
                f'--batch-size {args.batch_size} --hidden {args.hidden} '
                f'--dropout {args.dropout} --weight-decay {args.weight_decay} '
                f'--pool-type {args.pool_type} --seed {args.seed} '
                f'--lambda-delta 0.0 --lambda-consistency 0.0 '
                f'--allow-metadata-mismatch'
            )
            print(f"\n[TRAIN] {train_cmd}")
            rc = subprocess.call(train_cmd, shell=True)
            if rc == 0:
                summary_path = models_dir / f"summary_{run_name}.json"
                if summary_path.exists():
                    s = json.loads(summary_path.read_text())
                    tcn_r2 = s["test_future_metrics"]["r2"]
                    tcn_rmse = s["test_future_metrics"]["rmse"]
            else:
                print(f"[WARN] TCN training failed for hz={hz} (exit={rc})")

        row = {
            "horizon": hz,
            "lookback": args.lookback,
            "target_smooth_window": args.target_smooth_window,
            "persistence_r2": persist["r2"],
            "persistence_rmse": persist["rmse"],
            "ridge_r2": ridge["r2"],
            "ridge_rmse": ridge["rmse"],
            "tcn_r2": tcn_r2,
            "tcn_rmse": tcn_rmse,
            "tcn_margin_over_persistence": tcn_r2 - persist["r2"]
            if not (np.isnan(tcn_r2) or np.isnan(persist["r2"]))
            else float("nan"),
        }
        results.append(row)

    # Save and print summary
    out_path = models_dir / "sweep_horizons_results.json"
    out_path.write_text(json.dumps(results, indent=2))

    print(f"\n{'='*70}")
    print("HORIZON SWEEP RESULTS")
    print(f"{'='*70}")
    print(f"{'Hz':>4s}  {'Persist R2':>11s}  {'Ridge R2':>9s}  {'TCN R2':>7s}  {'Margin':>7s}")
    print("-" * 50)
    for r in results:
        margin = r["tcn_margin_over_persistence"]
        margin_s = f"{margin:+.4f}" if not np.isnan(margin) else "   N/A"
        persist_s = f"{r['persistence_r2']:.4f}" if not np.isnan(r["persistence_r2"]) else "  N/A"
        ridge_s = f"{r['ridge_r2']:.4f}" if not np.isnan(r["ridge_r2"]) else "  N/A"
        tcn_s = f"{r['tcn_r2']:.4f}" if not np.isnan(r["tcn_r2"]) else "  N/A"
        print(f"{r['horizon']:>4d}  {persist_s:>11s}  {ridge_s:>9s}  {tcn_s:>7s}  {margin_s:>7s}")

    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
