"""
Architecture comparison study: train and evaluate all models across horizons.

Runs persistence, Ridge, SimpleLSTM, XGBoost, SimpleTransformer, and
MultiscaleCausalTCN on the pre-built 4ch and 7ch multiscale temporal datasets
at prediction horizons 1, 3, 5, 8, 10 seconds.

Outputs one JSON comparison table per dataset to --output-dir.

Usage:
    python temporal_multiscale/run_comparison_study.py \\
      --horizons 1,3,5,8,10 \\
      --models persistence,ridge,lstm,xgboost,transformer,tcn \\
      --datasets 4ch,7ch \\
      --seed 42 \\
      --epochs 80 \\
      --patience 20 \\
      --output-dir results

    # Dry run (checks datasets exist, prints what would be run)
    python temporal_multiscale/run_comparison_study.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import torch

from temporal_multiscale.comparison_models import (
    SimpleLSTM,
    SimpleTransformer,
    set_seed,
    train_pytorch_model,
    train_xgboost_model,
)
from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN
from temporal_multiscale.sweep_horizons import persistence_baseline, ridge_baseline
from temporal_multiscale.train_multiscale_tcn import SequenceDataset


# ---------------------------------------------------------------------------
# Dataset path helpers
# ---------------------------------------------------------------------------

def _dataset_base_4ch() -> Path:
    return ROOT / "data" / "processed" / "muse_4ch"


def _dataset_base_7ch() -> Path:
    return ROOT / "data" / "processed"


def _dataset_dir(dataset: str, horizon: int) -> Path:
    """Return the pre-built or to-be-built dataset directory for a given config."""
    lb = 20
    ts = 1
    suffix = f"multiscale_temporal_lb{lb}_hz{horizon}_ts{ts}"
    if dataset == "4ch":
        return _dataset_base_4ch() / suffix
    elif dataset == "7ch":
        return _dataset_base_7ch() / suffix
    else:
        raise ValueError(f"Unknown dataset: {dataset!r}. Expected '4ch' or '7ch'.")


def _ensure_dataset(dataset: str, horizon: int) -> Path:
    """
    Return dataset_dir, building it if it does not exist.

    For horizon==5 the datasets are pre-built on disk; for other horizons
    we call build_multiscale_dataset on-the-fly (ts1, lb20).
    """
    d = _dataset_dir(dataset, horizon)
    meta_path = d / "metadata.json"
    if meta_path.exists():
        return d

    print(f"  [BUILD] Dataset not found, building {d.name} ...")
    from temporal_multiscale.build_multiscale_dataset import build_multiscale_dataset

    if dataset == "4ch":
        processed_dir = _dataset_base_4ch()
        # 4ch dataset uses data/processed/muse_4ch as processed_dir but that
        # dir does not contain raw BIDS events.  The stim-context features come
        # from data/raw/ds005048; the spectral cache is in muse_4ch/.
        raw_root = ROOT / "data" / "raw" / "ds005048"
    else:
        processed_dir = _dataset_base_7ch()
        raw_root = ROOT / "data" / "raw" / "ds005048"

    build_multiscale_dataset(
        processed_dir=processed_dir,
        raw_root=raw_root,
        output_dir=d,
        lookback=20,
        horizon=horizon,
        target_smooth_window=1,
    )
    return d


def _n_features(dataset_dir: Path) -> int:
    meta = json.loads((dataset_dir / "metadata.json").read_text())
    return int(meta["n_features"])


# ---------------------------------------------------------------------------
# Device selection
# ---------------------------------------------------------------------------

def _device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


# ---------------------------------------------------------------------------
# Per-model runners
# ---------------------------------------------------------------------------

def _run_persistence(dataset_dir: Path) -> Dict[str, Any]:
    t0 = time.time()
    r = persistence_baseline(dataset_dir)
    return {
        "model": "persistence",
        "test_r2": r["r2"],
        "test_rmse": r["rmse"],
        "n_params": 0,
        "best_epoch": 0,
        "val_r2": float("nan"),
        "test_corr": float("nan"),
        "train_seconds": float(time.time() - t0),
    }


def _run_ridge(dataset_dir: Path) -> Dict[str, Any]:
    """
    Ridge with alpha auto-scaled to input dimensionality.

    alpha=1.0 overflows when T*F is large (e.g. 20*73=1460 dims). We set
    alpha=n_dims to keep the regularization-to-signal ratio consistent across
    different feature counts. This prevents the ill-conditioning that causes
    NaN/overflow in the normal-equation solver at high dimensionality.
    """
    from sklearn.linear_model import Ridge

    t0 = time.time()
    train_npz = np.load(dataset_dir / "train_multiscale.npz", allow_pickle=True)
    test_npz = np.load(dataset_dir / "test_multiscale.npz", allow_pickle=True)

    x_train = train_npz["x_seq"].astype(np.float64).reshape(train_npz["x_seq"].shape[0], -1)
    x_test = test_npz["x_seq"].astype(np.float64).reshape(test_npz["x_seq"].shape[0], -1)
    y_train = train_npz["y_future"].astype(np.float64)
    y_test = test_npz["y_future"].astype(np.float64)

    # Scale alpha with input dimension to prevent ill-conditioning.
    # solver='lsqr' avoids the normal-equation Cholesky that overflows at
    # high dimensionality (T*F=1460 for 7ch), using a conjugate-gradient
    # iterative solver instead.
    alpha = float(x_train.shape[1])
    ridge = Ridge(alpha=alpha, solver="lsqr")
    ridge.fit(x_train, y_train)
    y_pred = ridge.predict(x_test)

    ss_res = np.sum((y_test - y_pred) ** 2)
    ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
    r2 = float(1.0 - ss_res / (ss_tot + 1e-12))
    rmse = float(np.sqrt(np.mean((y_test - y_pred) ** 2)))

    return {
        "model": "ridge",
        "test_r2": r2,
        "test_rmse": rmse,
        "n_params": 0,
        "best_epoch": 0,
        "val_r2": float("nan"),
        "test_corr": float("nan"),
        "train_seconds": float(time.time() - t0),
    }


def _run_lstm(
    dataset_dir: Path,
    n_features: int,
    device: torch.device,
    epochs: int,
    patience: int,
    seed: int,
) -> Dict[str, Any]:
    set_seed(seed)
    scalers = np.load(dataset_dir / "scalers.npz")
    train_ds = SequenceDataset(dataset_dir / "train_multiscale.npz")
    val_ds = SequenceDataset(dataset_dir / "val_multiscale.npz")
    test_ds = SequenceDataset(dataset_dir / "test_multiscale.npz")
    model = SimpleLSTM(n_features=n_features)
    result = train_pytorch_model(
        model=model,
        train_ds=train_ds,
        val_ds=val_ds,
        test_ds=test_ds,
        scalers=scalers,
        device=device,
        epochs=epochs,
        patience=patience,
        seed=seed,
    )
    result["model"] = "lstm"
    return result


def _run_xgboost(dataset_dir: Path, seed: int) -> Dict[str, Any]:
    result = train_xgboost_model(dataset_dir=dataset_dir, seed=seed)
    result["model"] = "xgboost"
    return result


def _run_transformer(
    dataset_dir: Path,
    n_features: int,
    device: torch.device,
    epochs: int,
    patience: int,
    seed: int,
) -> Dict[str, Any]:
    set_seed(seed)
    scalers = np.load(dataset_dir / "scalers.npz")
    train_ds = SequenceDataset(dataset_dir / "train_multiscale.npz")
    val_ds = SequenceDataset(dataset_dir / "val_multiscale.npz")
    test_ds = SequenceDataset(dataset_dir / "test_multiscale.npz")
    model = SimpleTransformer(n_features=n_features)
    # Lower LR for Transformer stability — research note in PLAN.md
    result = train_pytorch_model(
        model=model,
        train_ds=train_ds,
        val_ds=val_ds,
        test_ds=test_ds,
        scalers=scalers,
        device=device,
        epochs=epochs,
        patience=patience,
        lr=1e-4,
        seed=seed,
    )
    result["model"] = "transformer"
    return result


def _run_tcn(
    dataset_dir: Path,
    n_features: int,
    device: torch.device,
    epochs: int,
    patience: int,
    seed: int,
) -> Dict[str, Any]:
    set_seed(seed)
    scalers = np.load(dataset_dir / "scalers.npz")
    train_ds = SequenceDataset(dataset_dir / "train_multiscale.npz")
    val_ds = SequenceDataset(dataset_dir / "val_multiscale.npz")
    test_ds = SequenceDataset(dataset_dir / "test_multiscale.npz")
    cfg = ModelConfig(n_features=n_features)
    model = MultiscaleCausalTCN(cfg)
    result = train_pytorch_model(
        model=model,
        train_ds=train_ds,
        val_ds=val_ds,
        test_ds=test_ds,
        scalers=scalers,
        device=device,
        epochs=epochs,
        patience=patience,
        seed=seed,
    )
    result["model"] = "tcn"
    # Use MultiscaleCausalTCN's own param counter (includes requires_grad only)
    result["n_params"] = model.count_parameters()
    return result


# ---------------------------------------------------------------------------
# ASCII table printer
# ---------------------------------------------------------------------------

def _print_table(rows: List[Dict[str, Any]], dataset: str, horizon: int) -> None:
    print(f"\n  {'Model':<14}  {'Test R2':>9}  {'RMSE':>12}  {'Params':>8}  {'Time(s)':>8}")
    print(f"  {'-'*14}  {'-'*9}  {'-'*12}  {'-'*8}  {'-'*8}")
    for r in rows:
        model = r.get("model", "?")
        r2 = r.get("test_r2", float("nan"))
        rmse = r.get("test_rmse", float("nan"))
        params = r.get("n_params", 0)
        secs = r.get("train_seconds", float("nan"))
        r2_s = f"{r2:.4f}" if not (r2 != r2) else "  N/A"
        rmse_s = f"{rmse:.6f}" if not (rmse != rmse) else "    N/A"
        params_s = f"{params:,}" if params else "     -"
        secs_s = f"{secs:.1f}" if not (secs != secs) else "  N/A"
        print(f"  {model:<14}  {r2_s:>9}  {rmse_s:>12}  {params_s:>8}  {secs_s:>8}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Architecture comparison study.")
    p.add_argument(
        "--horizons", default="1,3,5,8,10", type=str,
        help="Comma-separated prediction horizons in seconds",
    )
    p.add_argument(
        "--models",
        default="persistence,ridge,lstm,xgboost,transformer,tcn",
        type=str,
        help="Comma-separated model names to run",
    )
    p.add_argument(
        "--datasets", default="4ch,7ch", type=str,
        help="Comma-separated dataset configs: 4ch and/or 7ch",
    )
    p.add_argument("--seed", default=42, type=int)
    p.add_argument("--epochs", default=80, type=int)
    p.add_argument("--patience", default=20, type=int)
    p.add_argument(
        "--output-dir", default="results", type=str,
        help="Directory to write JSON comparison tables",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Only check datasets and print the run plan; do not train",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    horizons = [int(h.strip()) for h in args.horizons.split(",") if h.strip()]
    models = [m.strip().lower() for m in args.models.split(",") if m.strip()]
    datasets = [d.strip().lower() for d in args.datasets.split(",") if d.strip()]
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    device = _device()
    print("=" * 70)
    print("ARCHITECTURE COMPARISON STUDY")
    print("=" * 70)
    print(f"  Horizons:  {horizons}")
    print(f"  Models:    {models}")
    print(f"  Datasets:  {datasets}")
    print(f"  Device:    {device}")
    print(f"  Epochs:    {args.epochs}  Patience: {args.patience}  Seed: {args.seed}")
    print(f"  Output:    {output_dir}")
    print()

    if args.dry_run:
        print("[DRY RUN] Checking dataset existence ...")
        for ds in datasets:
            for hz in horizons:
                d = _dataset_dir(ds, hz)
                exists = (d / "metadata.json").exists()
                status = "[OK]" if exists else "[MISSING — will build]"
                print(f"  {status} {d}")
        print("\n[DRY RUN] Would run:")
        for ds in datasets:
            for hz in horizons:
                for m in models:
                    print(f"  dataset={ds}  horizon={hz:2d}  model={m}")
        return

    # Accumulate results per dataset
    all_results: Dict[str, List[Dict[str, Any]]] = {ds: [] for ds in datasets}

    for ds in datasets:
        print(f"\n{'='*70}")
        print(f"DATASET: {ds}")
        print(f"{'='*70}")

        for hz in horizons:
            print(f"\n  --- Horizon = {hz}s ---")
            try:
                dataset_dir = _ensure_dataset(ds, hz)
            except Exception as e:
                print(f"  [ERROR] Could not prepare dataset for hz={hz}: {e}")
                continue

            nf = _n_features(dataset_dir)
            print(f"  Dataset: {dataset_dir.name}  n_features={nf}")

            for model_name in models:
                print(f"  Running {model_name} ...", end=" ", flush=True)
                try:
                    if model_name == "persistence":
                        result = _run_persistence(dataset_dir)
                    elif model_name == "ridge":
                        result = _run_ridge(dataset_dir)
                    elif model_name == "lstm":
                        result = _run_lstm(dataset_dir, nf, device, args.epochs, args.patience, args.seed)
                    elif model_name == "xgboost":
                        result = _run_xgboost(dataset_dir, args.seed)
                    elif model_name == "transformer":
                        result = _run_transformer(dataset_dir, nf, device, args.epochs, args.patience, args.seed)
                    elif model_name == "tcn":
                        result = _run_tcn(dataset_dir, nf, device, args.epochs, args.patience, args.seed)
                    else:
                        raise ValueError(f"Unknown model: {model_name!r}")

                    result["horizon"] = hz
                    result["dataset"] = ds
                    r2 = result.get("test_r2", float("nan"))
                    rmse = result.get("test_rmse", float("nan"))
                    secs = result.get("train_seconds", float("nan"))
                    print(f"R2={r2:.4f}  RMSE={rmse:.6f}  ({secs:.1f}s)")
                    all_results[ds].append(result)

                except Exception as e:
                    print(f"[ERROR] {e}")
                    all_results[ds].append({
                        "model": model_name,
                        "horizon": hz,
                        "dataset": ds,
                        "test_r2": float("nan"),
                        "test_rmse": float("nan"),
                        "n_params": 0,
                        "error": str(e),
                    })

            _print_table(
                [r for r in all_results[ds] if r.get("horizon") == hz],
                dataset=ds,
                horizon=hz,
            )

    # Write JSON output tables
    for ds in datasets:
        out_path = output_dir / f"comparison_table_{ds}.json"
        out_path.write_text(json.dumps(all_results[ds], indent=2))
        print(f"\nSaved: {out_path}  ({len(all_results[ds])} rows)")

    # Final summary across all datasets
    print(f"\n{'='*70}")
    print("STUDY COMPLETE")
    print(f"{'='*70}")
    for ds in datasets:
        rows = all_results[ds]
        total = len(rows)
        ok = sum(1 for r in rows if not (r.get("test_r2", float("nan")) != r.get("test_r2", float("nan"))))
        print(f"  {ds}: {ok}/{total} runs succeeded")


if __name__ == "__main__":
    main()
