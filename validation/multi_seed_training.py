"""
Multi-Seed Training for Robustness Evaluation

Trains EEGNet variants (original, enhanced, large) across multiple random seeds
with independent subject-level re-splits to address the "no cross-validation"
audit finding and quantify variance in reported R^2 metrics.

For each seed:
    1. Shuffle subjects with the new seed
    2. Split into 70/15/15 train/val/test by subject (no data leakage)
    3. Z-score normalize PAC targets using training-set statistics
    4. Train with Huber loss, Adam, ReduceLROnPlateau, early stopping
    5. Evaluate on the held-out test set

Reports:
    - Per-seed: R^2, RMSE, MAE, correlation, best epoch
    - Aggregate: mean, std, 95% CI, min, max for all metrics
    - Saved to rigor/multi_seed_results_{model}.json

Usage:
    python rigor/multi_seed_training.py --model original --seeds "42,123,456,789,2026"
    python rigor/multi_seed_training.py --model enhanced --epochs 120
    python rigor/multi_seed_training.py --model large --device cpu

Author: Amaar Chughtai
Date: February 2026
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from torch.optim.lr_scheduler import ReduceLROnPlateau
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# ---------------------------------------------------------------------------
# Path setup: allow imports from src/ and rigor/
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
RIGOR_DIR = PROJECT_ROOT / "rigor"
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(RIGOR_DIR))

from eegnet import EEGNet
from eegnet_enhanced import EEGNetEnhanced, EEGNetLarge, count_parameters

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("multi_seed_training")


# ===================================================================
# Data helpers
# ===================================================================

def load_all_data(data_dir: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load and concatenate train/val/test npz splits into a single pool.

    The original splits used seed=42. To evaluate with different seeds we
    need the full pool of windows with their subject IDs so we can re-split.

    Args:
        data_dir: Path to directory containing {train,val,test}_data.npz.

    Returns:
        windows: All EEG windows (N, 1, 7, 500).
        pac: All PAC labels (N,).
        subjects: Subject ID per window (N,), string array.
    """
    all_windows: List[np.ndarray] = []
    all_pac: List[np.ndarray] = []
    all_subjects: List[np.ndarray] = []

    for split_name in ("train", "val", "test"):
        npz_path = data_dir / f"{split_name}_data.npz"
        if not npz_path.exists():
            raise FileNotFoundError(
                f"Missing {npz_path}. Run data preprocessing first:\n"
                f"  python src/data_loader.py --bids_root data/raw/ds005048 "
                f"--output data/processed"
            )
        data = np.load(npz_path, allow_pickle=True)
        all_windows.append(data["windows"])
        all_pac.append(data["pac"])
        all_subjects.append(data["subjects"])

    windows = np.concatenate(all_windows, axis=0)
    pac = np.concatenate(all_pac, axis=0)
    subjects = np.concatenate(all_subjects, axis=0)

    logger.info(
        f"Loaded {len(windows)} total windows from {len(np.unique(subjects))} subjects"
    )
    return windows, pac, subjects


def split_by_subject(
    windows: np.ndarray,
    pac: np.ndarray,
    subjects: np.ndarray,
    seed: int,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
) -> Dict[str, Dict[str, np.ndarray]]:
    """
    Create train/val/test splits by subject with a given random seed.

    Ensures no data leakage: each subject appears in exactly one split.

    Args:
        windows: All EEG windows (N, 1, 7, 500).
        pac: All PAC labels (N,).
        subjects: Subject ID per window (N,).
        seed: Random seed for subject shuffling.
        train_ratio: Fraction of subjects for training.
        val_ratio: Fraction of subjects for validation.

    Returns:
        Dictionary with 'train', 'val', 'test' keys, each containing
        {'windows': ndarray, 'pac': ndarray}.
    """
    rng = np.random.RandomState(seed)
    unique_subjects = np.unique(subjects)
    n_subjects = len(unique_subjects)

    shuffled = rng.permutation(unique_subjects)

    n_train = int(n_subjects * train_ratio)
    n_val = int(n_subjects * val_ratio)

    train_subjects = set(shuffled[:n_train])
    val_subjects = set(shuffled[n_train : n_train + n_val])
    test_subjects = set(shuffled[n_train + n_val :])

    splits: Dict[str, Dict[str, np.ndarray]] = {}
    for name, subj_set in [
        ("train", train_subjects),
        ("val", val_subjects),
        ("test", test_subjects),
    ]:
        mask = np.array([s in subj_set for s in subjects])
        splits[name] = {
            "windows": windows[mask],
            "pac": pac[mask],
        }

    logger.info(
        f"  Seed {seed}: "
        f"train={len(splits['train']['pac'])} "
        f"({len(train_subjects)} subj), "
        f"val={len(splits['val']['pac'])} "
        f"({len(val_subjects)} subj), "
        f"test={len(splits['test']['pac'])} "
        f"({len(test_subjects)} subj)"
    )

    return splits


def make_dataloader(
    windows: np.ndarray,
    pac: np.ndarray,
    batch_size: int,
    shuffle: bool,
    device_is_cuda: bool,
) -> DataLoader:
    """
    Create a DataLoader from numpy arrays.

    Args:
        windows: EEG windows (N, 1, 7, 500).
        pac: PAC labels (N,).
        batch_size: Batch size.
        shuffle: Whether to shuffle.
        device_is_cuda: Whether CUDA is used (for pin_memory).

    Returns:
        PyTorch DataLoader.
    """
    x_tensor = torch.from_numpy(windows).float()
    y_tensor = torch.from_numpy(pac).float()
    dataset = TensorDataset(x_tensor, y_tensor)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=0,
        pin_memory=device_is_cuda,
    )


# ===================================================================
# Model factory
# ===================================================================

MODEL_REGISTRY = {
    "original": {
        "cls": EEGNet,
        "kwargs": {
            "n_channels": 7,
            "n_samples": 500,
            "F1": 8,
            "D": 2,
            "F2": 16,
            "dropout": 0.5,
            "kernel_length": 64,
        },
    },
    "enhanced": {
        "cls": EEGNetEnhanced,
        "kwargs": {
            "n_channels": 7,
            "n_samples": 500,
            "F1": 16,
            "D": 2,
            "F2": 32,
            "dropout": 0.5,
            "kernel_length": 125,
        },
    },
    "large": {
        "cls": EEGNetLarge,
        "kwargs": {
            "n_channels": 7,
            "n_samples": 500,
            "F1": 32,
            "D": 2,
            "F2": 64,
            "dropout": 0.5,
            "kernel_length": 125,
        },
    },
}


def create_model(model_name: str, device: str) -> nn.Module:
    """
    Instantiate a model by name and move to device.

    Args:
        model_name: One of 'original', 'enhanced', 'large'.
        device: 'cuda' or 'cpu'.

    Returns:
        Initialized model on the specified device.
    """
    if model_name not in MODEL_REGISTRY:
        raise ValueError(
            f"Unknown model '{model_name}'. "
            f"Choose from: {list(MODEL_REGISTRY.keys())}"
        )
    spec = MODEL_REGISTRY[model_name]
    model = spec["cls"](**spec["kwargs"])
    return model.to(device)


# ===================================================================
# Training loop for a single seed
# ===================================================================

def train_single_seed(
    model_name: str,
    splits: Dict[str, Dict[str, np.ndarray]],
    seed: int,
    device: str,
    epochs: int = 100,
    batch_size: int = 64,
    learning_rate: float = 0.001,
    weight_decay: float = 1e-4,
    patience_lr: int = 5,
    patience_early_stop: int = 15,
) -> Dict[str, float]:
    """
    Train a model for one seed and evaluate on the test split.

    Uses Huber loss (matching the TCN pipeline) instead of MSE for robustness
    to outlier PAC values. PAC targets are z-score normalized using
    training-set statistics.

    Args:
        model_name: Model variant to train.
        splits: Dictionary with 'train', 'val', 'test' data arrays.
        seed: Random seed (used for weight initialization reproducibility).
        device: 'cuda' or 'cpu'.
        epochs: Maximum training epochs.
        batch_size: Training batch size.
        learning_rate: Initial learning rate for Adam.
        weight_decay: L2 regularization strength.
        patience_lr: Patience for ReduceLROnPlateau.
        patience_early_stop: Patience for early stopping.

    Returns:
        Dictionary with test metrics: r2, rmse, mae, correlation, best_epoch,
        train_loss_final, val_loss_final.
    """
    # Reproducibility
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    # Z-score normalize PAC using training statistics
    pac_train_raw = splits["train"]["pac"]
    pac_mean = float(pac_train_raw.mean())
    pac_std = float(pac_train_raw.std())
    if pac_std < 1e-12:
        logger.warning(f"  Seed {seed}: PAC std near zero ({pac_std:.2e}), skipping normalization")
        pac_std = 1.0

    pac_train = (pac_train_raw - pac_mean) / pac_std
    pac_val = (splits["val"]["pac"] - pac_mean) / pac_std
    pac_test = (splits["test"]["pac"] - pac_mean) / pac_std

    device_is_cuda = device != "cpu"
    train_loader = make_dataloader(
        splits["train"]["windows"], pac_train, batch_size, shuffle=True,
        device_is_cuda=device_is_cuda,
    )
    val_loader = make_dataloader(
        splits["val"]["windows"], pac_val, batch_size, shuffle=False,
        device_is_cuda=device_is_cuda,
    )
    test_loader = make_dataloader(
        splits["test"]["windows"], pac_test, batch_size, shuffle=False,
        device_is_cuda=device_is_cuda,
    )

    # Create model
    model = create_model(model_name, device)

    # Huber loss (matching the TCN pipeline, robust to PAC outliers)
    criterion = nn.HuberLoss(delta=1.0)
    optimizer = optim.Adam(
        model.parameters(), lr=learning_rate, weight_decay=weight_decay
    )
    scheduler = ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=patience_lr
    )

    best_val_loss = float("inf")
    best_epoch = 0
    best_state_dict = None
    patience_counter = 0

    for epoch in range(1, epochs + 1):
        # --- Train ---
        model.train()
        train_loss_accum = 0.0
        n_train_batches = 0
        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()
            output = model(batch_x).squeeze(-1)
            loss = criterion(output, batch_y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            train_loss_accum += loss.item()
            n_train_batches += 1

        train_loss = train_loss_accum / max(n_train_batches, 1)

        # --- Validate ---
        model.eval()
        val_loss_accum = 0.0
        n_val_batches = 0
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x = batch_x.to(device)
                batch_y = batch_y.to(device)
                output = model(batch_x).squeeze(-1)
                loss = criterion(output, batch_y)
                val_loss_accum += loss.item()
                n_val_batches += 1

        val_loss = val_loss_accum / max(n_val_batches, 1)

        scheduler.step(val_loss)

        # Early stopping + checkpointing (in-memory)
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_epoch = epoch
            patience_counter = 0
            best_state_dict = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            patience_counter += 1
            if patience_counter >= patience_early_stop:
                break

    # --- Evaluate on test set using best model ---
    if best_state_dict is not None:
        model.load_state_dict(best_state_dict)
        model.to(device)

    model.eval()
    all_preds: List[np.ndarray] = []
    all_targets: List[np.ndarray] = []
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            batch_x = batch_x.to(device)
            output = model(batch_x).squeeze(-1)
            all_preds.append(output.cpu().numpy())
            all_targets.append(batch_y.numpy())

    preds = np.concatenate(all_preds)
    targets = np.concatenate(all_targets)

    # Metrics in z-score space (consistent with training loss interpretation)
    r2 = float(r2_score(targets, preds))
    rmse = float(np.sqrt(mean_squared_error(targets, preds)))
    mae = float(mean_absolute_error(targets, preds))
    correlation = float(np.corrcoef(targets, preds)[0, 1])

    logger.info(
        f"  Seed {seed}: R2={r2:.4f}, RMSE={rmse:.4f}, MAE={mae:.4f}, "
        f"Corr={correlation:.4f}, best_epoch={best_epoch}"
    )

    return {
        "seed": seed,
        "r2": r2,
        "rmse": rmse,
        "mae": mae,
        "correlation": correlation,
        "best_epoch": best_epoch,
        "train_loss_final": train_loss,
        "val_loss_best": best_val_loss,
        "pac_mean": pac_mean,
        "pac_std": pac_std,
    }


# ===================================================================
# Aggregate statistics
# ===================================================================

def compute_aggregate_stats(
    seed_results: List[Dict[str, float]],
) -> Dict[str, Dict[str, float]]:
    """
    Compute aggregate statistics across seeds for each metric.

    Computes mean, std, 95% CI (assuming t-distribution for small n),
    min, and max.

    Args:
        seed_results: List of per-seed result dictionaries.

    Returns:
        Dictionary mapping metric name to {mean, std, ci95_low, ci95_high, min, max}.
    """
    from scipy import stats as sp_stats

    metrics_of_interest = ["r2", "rmse", "mae", "correlation", "best_epoch"]
    aggregate: Dict[str, Dict[str, float]] = {}

    n = len(seed_results)

    for metric in metrics_of_interest:
        values = np.array([r[metric] for r in seed_results])
        mean = float(values.mean())
        std = float(values.std(ddof=1)) if n > 1 else 0.0

        # 95% CI using t-distribution
        if n > 1:
            t_crit = float(sp_stats.t.ppf(0.975, df=n - 1))
            margin = t_crit * std / np.sqrt(n)
        else:
            margin = 0.0

        aggregate[metric] = {
            "mean": mean,
            "std": std,
            "ci95_low": mean - margin,
            "ci95_high": mean + margin,
            "min": float(values.min()),
            "max": float(values.max()),
            "n_seeds": n,
        }

    return aggregate


# ===================================================================
# Main
# ===================================================================

def main() -> None:
    """Run multi-seed training experiment."""
    parser = argparse.ArgumentParser(
        description=(
            "Train EEGNet variants across multiple random seeds and report "
            "mean +/- std of test metrics (R^2, RMSE, MAE)."
        )
    )
    parser.add_argument(
        "--model",
        type=str,
        default="original",
        choices=["original", "enhanced", "large"],
        help="Model variant to train (default: original)",
    )
    parser.add_argument(
        "--seeds",
        type=str,
        default="42,123,456,789,2026",
        help="Comma-separated random seeds (default: '42,123,456,789,2026')",
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default=str(PROJECT_ROOT / "data" / "processed"),
        help="Directory with preprocessed data (default: data/processed)",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=str(RIGOR_DIR),
        help="Directory for results JSON (default: rigor/)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Maximum training epochs per seed (default: 100)",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=64,
        help="Training batch size (default: 64)",
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=0.001,
        help="Learning rate (default: 0.001)",
    )
    parser.add_argument(
        "--weight_decay",
        type=float,
        default=1e-4,
        help="L2 regularization (default: 1e-4)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        help="Device: cuda or cpu (default: cuda)",
    )

    args = parser.parse_args()

    # Parse seeds
    seeds = [int(s.strip()) for s in args.seeds.split(",")]
    logger.info(f"Multi-seed training experiment")
    logger.info(f"  Model:  {args.model}")
    logger.info(f"  Seeds:  {seeds}")
    logger.info(f"  Epochs: {args.epochs}")
    logger.info(f"  Device: {args.device}")

    # Resolve device
    device = args.device
    if device == "cuda" and not torch.cuda.is_available():
        logger.warning("CUDA not available, falling back to CPU")
        device = "cpu"
    logger.info(f"  Using device: {device}")

    # Print model info
    tmp_model = create_model(args.model, "cpu")
    n_params = count_parameters(tmp_model)
    logger.info(f"  Model class: {tmp_model.__class__.__name__}")
    logger.info(f"  Parameters:  {n_params:,}")
    del tmp_model

    # Load data
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(
            f"\nERROR: Data directory not found: {data_dir}\n"
            f"Please run data preprocessing first:\n"
            f"  python src/data_loader.py --bids_root data/raw/ds005048 "
            f"--output data/processed\n"
            f"\nAlternatively, specify a different data directory with --data_dir."
        )
        sys.exit(1)

    try:
        windows, pac, subjects = load_all_data(data_dir)
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

    # Run training for each seed
    logger.info(f"\n{'=' * 70}")
    logger.info(f"Starting {len(seeds)}-seed training runs")
    logger.info(f"{'=' * 70}")

    seed_results: List[Dict[str, float]] = []
    total_start = time.time()

    for i, seed in enumerate(seeds):
        logger.info(f"\n--- Seed {seed} ({i + 1}/{len(seeds)}) ---")
        seed_start = time.time()

        # Re-split subjects with this seed
        splits = split_by_subject(windows, pac, subjects, seed=seed)

        # Train and evaluate
        result = train_single_seed(
            model_name=args.model,
            splits=splits,
            seed=seed,
            device=device,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.lr,
            weight_decay=args.weight_decay,
        )

        seed_elapsed = time.time() - seed_start
        result["elapsed_sec"] = seed_elapsed
        seed_results.append(result)
        logger.info(f"  Seed {seed} completed in {seed_elapsed:.1f}s")

    total_elapsed = time.time() - total_start

    # Compute aggregate statistics
    aggregate = compute_aggregate_stats(seed_results)

    # Print summary
    print(f"\n{'=' * 70}")
    print(f"MULTI-SEED RESULTS: {args.model} ({n_params:,} params)")
    print(f"{'=' * 70}")
    print(f"Seeds: {seeds}")
    print(f"Total time: {total_elapsed:.1f}s")
    print()

    print(f"{'Metric':<15s}  {'Mean':>8s}  {'Std':>8s}  {'95% CI':>20s}  {'Min':>8s}  {'Max':>8s}")
    print("-" * 70)
    for metric in ["r2", "rmse", "mae", "correlation"]:
        stats = aggregate[metric]
        ci_str = f"[{stats['ci95_low']:.4f}, {stats['ci95_high']:.4f}]"
        print(
            f"{metric:<15s}  {stats['mean']:>8.4f}  {stats['std']:>8.4f}  "
            f"{ci_str:>20s}  {stats['min']:>8.4f}  {stats['max']:>8.4f}"
        )

    # Best epoch statistics
    be = aggregate["best_epoch"]
    print(
        f"\n{'best_epoch':<15s}  {be['mean']:>8.1f}  {be['std']:>8.1f}  "
        f"{'':>20s}  {be['min']:>8.0f}  {be['max']:>8.0f}"
    )

    print()
    print("Per-seed breakdown:")
    print(f"  {'Seed':<8s}  {'R2':>8s}  {'RMSE':>8s}  {'MAE':>8s}  {'Corr':>8s}  {'Epoch':>6s}")
    print("  " + "-" * 48)
    for r in seed_results:
        print(
            f"  {r['seed']:<8d}  {r['r2']:>8.4f}  {r['rmse']:>8.4f}  "
            f"{r['mae']:>8.4f}  {r['correlation']:>8.4f}  {r['best_epoch']:>6d}"
        )

    # Save results
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"multi_seed_results_{args.model}.json"

    results_json = {
        "experiment": "multi_seed_training",
        "model": args.model,
        "model_class": MODEL_REGISTRY[args.model]["cls"].__name__,
        "n_parameters": n_params,
        "seeds": seeds,
        "config": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.lr,
            "weight_decay": args.weight_decay,
            "loss": "HuberLoss(delta=1.0)",
            "optimizer": "Adam",
            "scheduler": "ReduceLROnPlateau(factor=0.5, patience=5)",
            "early_stopping_patience": 15,
            "gradient_clip_max_norm": 1.0,
        },
        "per_seed_results": seed_results,
        "aggregate": aggregate,
        "total_elapsed_sec": total_elapsed,
        "data_dir": str(data_dir),
        "n_total_windows": int(len(windows)),
        "n_subjects": int(len(np.unique(subjects))),
    }

    with open(output_path, "w") as f:
        json.dump(results_json, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
