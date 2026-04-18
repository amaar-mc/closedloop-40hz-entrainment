"""
Synthetic Benchmark for TCN Architecture Variants.

Generates synthetic temporal data that mimics the structure of the real
multiscale PAC dataset and trains each architecture variant for a short
run to validate:
    1. All architectures forward-pass without errors.
    2. All architectures can learn a nonlinear temporal mapping.
    3. Relative parameter counts and training speeds.
    4. Gradient flow (no NaN/Inf losses).

The synthetic data has a known ground-truth function, so convergence to
low loss confirms correct implementation rather than predictive skill on
real EEG data.

Synthetic data specification:
    - 1000 training sequences, 200 validation, 200 test
    - Each sequence: (20, 73) = (lookback, features)
    - Features 0-6 are "PAC-derived" with autoregressive structure
    - Features 7-62 are "spectral" (random with temporal correlation)
    - Features 63-72 are "stimulation context" (binary + smooth)
    - Target: nonlinear function of PAC history + stim context + noise
    - Delta target: future_pac - current_pac

Usage:
    python rigor/experiments/synthetic_benchmark.py

Outputs:
    rigor/experiments/synthetic_benchmark_results.json

Author: Amaar Chughtai
Date: February 2026
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
from torch.utils.data import DataLoader, Dataset

# Ensure repository root is importable
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rigor.experiments.tcn_variants import (
    VARIANT_REGISTRY,
    ModelConfig,
    TransformerConfig,
    build_variant,
)
from temporal_multiscale.multiscale_tcn import (
    ModelConfig as BaselineModelConfig,
    MultiscaleCausalTCN,
)

# ---------------------------------------------------------------------------
# Constants matching the real dataset structure
# ---------------------------------------------------------------------------

LOOKBACK: int = 20
N_FEATURES: int = 73
N_PAC_FEATURES: int = 7      # indices 0-6
N_SPECTRAL_FEATURES: int = 56  # indices 7-62
N_STIM_FEATURES: int = 10    # indices 63-72

N_TRAIN: int = 1000
N_VAL: int = 200
N_TEST: int = 200

SEED: int = 42
N_EPOCHS: int = 30
BATCH_SIZE: int = 64
LR: float = 1e-3
WEIGHT_DECAY: float = 1e-3


# ---------------------------------------------------------------------------
# Synthetic data generation
# ---------------------------------------------------------------------------


def _generate_pac_features(n_samples: int, lookback: int, rng: np.random.Generator) -> np.ndarray:
    """Generate PAC-like features with autoregressive structure.

    Mimics the real PAC features: current PAC, moving averages (ma2, ma4,
    ma8, ma16), and differences (diff1, diff4). The underlying PAC signal
    is an AR(1) process with drift, producing realistic temporal correlation.

    Args:
        n_samples: Number of sequences to generate.
        lookback: Sequence length.
        rng: NumPy random generator for reproducibility.

    Returns:
        Array of shape (n_samples, lookback, 7).
    """
    # Generate long AR(1) PAC series, then extract windows
    total_len = n_samples + lookback + 20  # extra for warmup
    ar_coeff = 0.95  # strong autocorrelation, mimics real PAC

    pac_series = np.zeros(total_len)
    pac_series[0] = rng.normal(0.003, 0.001)  # realistic PAC range
    for t in range(1, total_len):
        pac_series[t] = ar_coeff * pac_series[t - 1] + rng.normal(0.0, 0.0003)
    pac_series = np.abs(pac_series)  # PAC is non-negative

    features = np.zeros((n_samples, lookback, N_PAC_FEATURES))
    for i in range(n_samples):
        start = i + 20  # skip warmup
        window = pac_series[start : start + lookback]

        # Feature 0: current PAC
        features[i, :, 0] = window

        # Features 1-4: causal moving averages
        for t in range(lookback):
            for j, w in enumerate([2, 4, 8, 16], start=1):
                lo = max(0, t - w + 1)
                features[i, t, j] = np.mean(window[lo : t + 1])

        # Feature 5: diff1
        features[i, 1:, 5] = window[1:] - window[:-1]

        # Feature 6: diff4
        features[i, 4:, 6] = window[4:] - window[:-4]

    return features


def _generate_spectral_features(
    n_samples: int, lookback: int, rng: np.random.Generator
) -> np.ndarray:
    """Generate spectral-like features with temporal smoothness.

    Real spectral features have moderate temporal correlation and
    cross-feature correlation. We simulate this with smoothed Gaussian
    noise with a random covariance structure.

    Args:
        n_samples: Number of sequences.
        lookback: Sequence length.
        rng: NumPy random generator.

    Returns:
        Array of shape (n_samples, lookback, 56).
    """
    features = np.zeros((n_samples, lookback, N_SPECTRAL_FEATURES))
    # Temporal smoothing kernel
    kernel = np.array([0.1, 0.2, 0.4, 0.2, 0.1])

    for i in range(n_samples):
        raw = rng.normal(0, 1, size=(lookback + len(kernel), N_SPECTRAL_FEATURES))
        for f in range(N_SPECTRAL_FEATURES):
            smoothed = np.convolve(raw[:, f], kernel, mode="valid")[:lookback]
            features[i, :, f] = smoothed

    return features


def _generate_stim_features(
    n_samples: int, lookback: int, rng: np.random.Generator
) -> np.ndarray:
    """Generate stimulation-context features.

    Mimics the real features: binary stim state, time since switch,
    stimulation fraction, cycle phase (sin/cos), and additional context.

    Args:
        n_samples: Number of sequences.
        lookback: Sequence length.
        rng: NumPy random generator.

    Returns:
        Array of shape (n_samples, lookback, 10).
    """
    features = np.zeros((n_samples, lookback, N_STIM_FEATURES))

    for i in range(n_samples):
        # Binary stim state with block structure (40s on / 20s off)
        cycle_pos = rng.uniform(0, 60)
        for t in range(lookback):
            pos = (cycle_pos + t * 2.0) % 60.0  # 2s per window
            stim_on = 1.0 if pos < 40.0 else 0.0
            features[i, t, 0] = stim_on

            # Time since switch (normalized)
            if pos < 40.0:
                features[i, t, 1] = min(pos / 60.0, 1.0)
            else:
                features[i, t, 1] = min((pos - 40.0) / 60.0, 1.0)

            # Stim fraction (trailing average)
            features[i, t, 2] = np.mean(features[i, max(0, t - 9) : t + 1, 0])

            # Cycle phase sin/cos
            phase = pos / 60.0
            features[i, t, 3] = np.sin(2.0 * np.pi * phase)
            features[i, t, 4] = np.cos(2.0 * np.pi * phase)

        # Fill remaining 5 features with correlated noise
        features[i, :, 5:] = rng.normal(0, 0.5, size=(lookback, 5))

    return features


def _target_function(
    pac_features: np.ndarray, stim_features: np.ndarray, rng: np.random.Generator
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute synthetic targets from a known nonlinear function.

    The target mimics future PAC: it depends nonlinearly on recent PAC
    history and stimulation context, with additive noise representing
    the irreducible prediction error.

    Target function:
        future_pac = 0.6 * pac_ma8 + 0.2 * pac_diff1^2
                   + 0.15 * stim_state * pac_current
                   + 0.05 * sin(pac_ma16 * 100)
                   + noise

    Args:
        pac_features: Shape (N, lookback, 7).
        stim_features: Shape (N, lookback, 10).
        rng: NumPy random generator.

    Returns:
        Tuple of (future_pac, delta_pac), each shape (N,).
    """
    n_samples = pac_features.shape[0]

    # Use the last timestep of each sequence (causal)
    pac_current = pac_features[:, -1, 0]  # current PAC
    pac_ma8 = pac_features[:, -1, 3]       # ma8
    pac_ma16 = pac_features[:, -1, 4]      # ma16
    pac_diff1 = pac_features[:, -1, 5]     # diff1
    stim_state = stim_features[:, -1, 0]   # stim on/off

    # Nonlinear target with known structure
    future_pac = (
        0.6 * pac_ma8
        + 0.2 * pac_diff1 ** 2
        + 0.15 * stim_state * pac_current
        + 0.05 * np.sin(pac_ma16 * 1000.0)
        + rng.normal(0, 0.0002, size=n_samples)
    )
    future_pac = np.abs(future_pac)  # PAC is non-negative

    delta_pac = future_pac - pac_current
    return future_pac.astype(np.float32), delta_pac.astype(np.float32)


def generate_synthetic_dataset(
    n_samples: int, seed: int
) -> Dict[str, np.ndarray]:
    """Generate a complete synthetic dataset split (unnormalized).

    Args:
        n_samples: Number of sequences.
        seed: Random seed for reproducibility.

    Returns:
        Dictionary with keys: x_seq, y_future, y_delta, last_pac.
    """
    rng = np.random.default_rng(seed)

    pac_feats = _generate_pac_features(n_samples, LOOKBACK, rng)
    spectral_feats = _generate_spectral_features(n_samples, LOOKBACK, rng)
    stim_feats = _generate_stim_features(n_samples, LOOKBACK, rng)

    x_seq = np.concatenate([pac_feats, spectral_feats, stim_feats], axis=2)
    assert x_seq.shape == (n_samples, LOOKBACK, N_FEATURES), (
        f"Expected ({n_samples}, {LOOKBACK}, {N_FEATURES}), got {x_seq.shape}"
    )

    y_future, y_delta = _target_function(pac_feats, stim_feats, rng)
    last_pac = pac_feats[:, -1, 0].astype(np.float32)

    return {
        "x_seq": x_seq.astype(np.float32),
        "y_future": y_future,
        "y_delta": y_delta,
        "last_pac": last_pac,
    }


def normalize_datasets(
    train_data: Dict[str, np.ndarray],
    val_data: Dict[str, np.ndarray],
    test_data: Dict[str, np.ndarray],
) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    """Z-score normalize features and targets using train statistics.

    Mirrors the normalization in build_multiscale_dataset.py: fit scalers
    on train split only, apply to all splits. This is critical for the
    models to converge since raw PAC values are ~0.003 (very small scale).

    Args:
        train_data: Training split dictionary.
        val_data: Validation split dictionary.
        test_data: Test split dictionary.

    Returns:
        Tuple of normalized (train, val, test) dictionaries.
    """
    x_train = train_data["x_seq"]
    feat_mean = x_train.reshape(-1, x_train.shape[-1]).mean(axis=0)
    feat_std = x_train.reshape(-1, x_train.shape[-1]).std(axis=0) + 1e-8

    yf_mean = train_data["y_future"].mean()
    yf_std = train_data["y_future"].std() + 1e-8
    yd_mean = train_data["y_delta"].mean()
    yd_std = train_data["y_delta"].std() + 1e-8

    def _apply(data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        return {
            "x_seq": ((data["x_seq"] - feat_mean) / feat_std).astype(np.float32),
            "y_future": ((data["y_future"] - yf_mean) / yf_std).astype(np.float32),
            "y_delta": ((data["y_delta"] - yd_mean) / yd_std).astype(np.float32),
            "last_pac": data["last_pac"],
        }

    return _apply(train_data), _apply(val_data), _apply(test_data)


# ---------------------------------------------------------------------------
# Dataset and training utilities
# ---------------------------------------------------------------------------


class SyntheticDataset(Dataset):
    """PyTorch Dataset wrapper for synthetic data arrays."""

    def __init__(self, data: Dict[str, np.ndarray]) -> None:
        self.x = torch.from_numpy(data["x_seq"]).float()
        self.y_future = torch.from_numpy(data["y_future"]).float()
        self.y_delta = torch.from_numpy(data["y_delta"]).float()
        self.last_pac = torch.from_numpy(data["last_pac"]).float()

    def __len__(self) -> int:
        return self.x.shape[0]

    def __getitem__(self, i: int) -> Dict[str, torch.Tensor]:
        return {
            "x_seq": self.x[i],
            "y_future": self.y_future[i],
            "y_delta": self.y_delta[i],
            "last_pac": self.last_pac[i],
        }


def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute R-squared (coefficient of determination)."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / (ss_tot + 1e-12))


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute root mean squared error."""
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def _corr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute Pearson correlation coefficient."""
    if np.std(y_true) < 1e-12 or np.std(y_pred) < 1e-12:
        return 0.0
    return float(np.corrcoef(y_true, y_pred)[0, 1])


def train_and_evaluate(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    test_loader: DataLoader,
    n_epochs: int,
    lr: float,
    weight_decay: float,
    lambda_delta: float,
    lambda_consistency: float,
    device: torch.device,
) -> Dict[str, object]:
    """Train a model variant and return evaluation metrics.

    Args:
        model: Model to train.
        train_loader: Training data loader.
        val_loader: Validation data loader.
        test_loader: Test data loader.
        n_epochs: Number of training epochs.
        lr: Learning rate.
        weight_decay: AdamW weight decay.
        lambda_delta: Weight for delta loss term.
        lambda_consistency: Weight for consistency loss term.
        device: Compute device.

    Returns:
        Dictionary with training history, test metrics, timing, and
        convergence status.
    """
    model = model.to(device)
    huber = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=lr, weight_decay=weight_decay
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=5
    )

    history: List[Dict[str, float]] = []
    best_val_loss = float("inf")
    nan_detected = False
    t0 = time.time()

    for epoch in range(1, n_epochs + 1):
        # --- Training ---
        model.train()
        train_loss_sum = 0.0
        train_n = 0

        for batch in train_loader:
            x = batch["x_seq"].to(device)
            y_future = batch["y_future"].to(device)
            y_delta = batch["y_delta"].to(device)
            last_pac = batch["last_pac"].to(device)

            out = model(x)
            loss_future = huber(out["future"], y_future)
            loss_delta = huber(out["delta"], y_delta)

            # Consistency: future ~= current + delta
            loss_consistency = torch.mean(
                (out["future"] - (last_pac + out["delta"])) ** 2
            )

            loss = (
                loss_future
                + lambda_delta * loss_delta
                + lambda_consistency * loss_consistency
            )

            if torch.isnan(loss) or torch.isinf(loss):
                nan_detected = True
                break

            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            train_loss_sum += loss.item()
            train_n += 1

        if nan_detected:
            break

        avg_train_loss = train_loss_sum / max(1, train_n)

        # --- Validation ---
        model.eval()
        val_preds: List[np.ndarray] = []
        val_trues: List[np.ndarray] = []
        val_loss_sum = 0.0
        val_n = 0

        with torch.no_grad():
            for batch in val_loader:
                x = batch["x_seq"].to(device)
                y_future = batch["y_future"].to(device)

                out = model(x)
                val_loss = huber(out["future"], y_future)
                val_loss_sum += val_loss.item()
                val_n += 1

                val_preds.append(out["future"].cpu().numpy())
                val_trues.append(y_future.cpu().numpy())

        avg_val_loss = val_loss_sum / max(1, val_n)
        scheduler.step(avg_val_loss)

        val_pred_all = np.concatenate(val_preds)
        val_true_all = np.concatenate(val_trues)
        val_r2 = _r2(val_true_all, val_pred_all)

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

        history.append({
            "epoch": epoch,
            "train_loss": avg_train_loss,
            "val_loss": avg_val_loss,
            "val_r2": val_r2,
        })

    train_time = time.time() - t0

    # --- Test evaluation with best model ---
    if not nan_detected:
        model.load_state_dict(best_state)

    model.eval()
    test_future_preds: List[np.ndarray] = []
    test_future_trues: List[np.ndarray] = []
    test_delta_preds: List[np.ndarray] = []
    test_delta_trues: List[np.ndarray] = []

    with torch.no_grad():
        for batch in test_loader:
            x = batch["x_seq"].to(device)
            out = model(x)

            test_future_preds.append(out["future"].cpu().numpy())
            test_future_trues.append(batch["y_future"].numpy())
            test_delta_preds.append(out["delta"].cpu().numpy())
            test_delta_trues.append(batch["y_delta"].numpy())

    test_fp = np.concatenate(test_future_preds)
    test_ft = np.concatenate(test_future_trues)
    test_dp = np.concatenate(test_delta_preds)
    test_dt = np.concatenate(test_delta_trues)

    return {
        "test_future_r2": _r2(test_ft, test_fp),
        "test_future_rmse": _rmse(test_ft, test_fp),
        "test_future_corr": _corr(test_ft, test_fp),
        "test_delta_r2": _r2(test_dt, test_dp),
        "test_delta_rmse": _rmse(test_dt, test_dp),
        "train_time_sec": train_time,
        "n_epochs_completed": len(history),
        "final_train_loss": history[-1]["train_loss"] if history else None,
        "final_val_loss": history[-1]["val_loss"] if history else None,
        "final_val_r2": history[-1]["val_r2"] if history else None,
        "nan_detected": nan_detected,
        "converged": (not nan_detected) and len(history) == n_epochs,
    }


# ---------------------------------------------------------------------------
# Main benchmark
# ---------------------------------------------------------------------------


def run_benchmark() -> Dict[str, object]:
    """Run the full synthetic benchmark across all variants.

    Returns:
        Dictionary mapping variant names to their results.
    """
    print("=" * 80)
    print("SYNTHETIC BENCHMARK: TCN Architecture Variants")
    print("=" * 80)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if device.type == "cuda":
        print(f"GPU:    {torch.cuda.get_device_name(0)}")
    print()

    # Reproducibility
    torch.manual_seed(SEED)
    np.random.seed(SEED)

    # Generate data
    print("Generating synthetic data...")
    train_raw = generate_synthetic_dataset(N_TRAIN, seed=SEED)
    val_raw = generate_synthetic_dataset(N_VAL, seed=SEED + 1)
    test_raw = generate_synthetic_dataset(N_TEST, seed=SEED + 2)

    # Normalize using train statistics (matches real pipeline)
    train_data, val_data, test_data = normalize_datasets(train_raw, val_raw, test_raw)

    train_ds = SyntheticDataset(train_data)
    val_ds = SyntheticDataset(val_data)
    test_ds = SyntheticDataset(test_data)

    g = torch.Generator()
    g.manual_seed(SEED)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, generator=g)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False)

    print(f"Train: {len(train_ds)}, Val: {len(val_ds)}, Test: {len(test_ds)}")
    print(f"Sequence shape: ({LOOKBACK}, {N_FEATURES})")
    print()

    # --- Baseline: MultiscaleCausalTCN ---
    results: Dict[str, object] = {}

    print("-" * 60)
    print("Training: baseline (MultiscaleCausalTCN)")
    print("-" * 60)

    baseline_cfg = BaselineModelConfig(
        n_features=N_FEATURES,
        hidden=64,
        kernel_size=3,
        dilations=[1, 2, 4, 8],
        dropout=0.1,
        pool_type="attention",
    )
    baseline_model = MultiscaleCausalTCN(baseline_cfg)
    n_params = baseline_model.count_parameters()
    print(f"Parameters: {n_params:,}")

    torch.manual_seed(SEED)
    baseline_results = train_and_evaluate(
        model=baseline_model,
        train_loader=train_loader,
        val_loader=val_loader,
        test_loader=test_loader,
        n_epochs=N_EPOCHS,
        lr=LR,
        weight_decay=WEIGHT_DECAY,
        lambda_delta=0.0,       # matches production config
        lambda_consistency=0.0,
        device=device,
    )
    baseline_results["n_params"] = n_params
    results["baseline"] = baseline_results

    print(
        f"  Test future R2: {baseline_results['test_future_r2']:.4f}, "
        f"RMSE: {baseline_results['test_future_rmse']:.6f}, "
        f"Time: {baseline_results['train_time_sec']:.1f}s"
    )
    print(
        f"  Converged: {baseline_results['converged']}, "
        f"NaN: {baseline_results['nan_detected']}"
    )
    print()

    # --- Variant experiments ---
    for variant_name, (cls, config_factory) in VARIANT_REGISTRY.items():
        print("-" * 60)
        print(f"Training: {variant_name}")
        print("-" * 60)

        cfg = config_factory(N_FEATURES)
        model = cls(cfg)
        n_params = model.count_parameters()
        print(f"Parameters: {n_params:,}")

        # Use recommended multi-task lambdas for the multitask variant
        if variant_name == "multitask":
            lambda_delta = MultiTaskTCN.RECOMMENDED_LAMBDA_DELTA
            lambda_consistency = MultiTaskTCN.RECOMMENDED_LAMBDA_CONSISTENCY
            print(f"  lambda_delta={lambda_delta}, lambda_consistency={lambda_consistency}")
        else:
            lambda_delta = 0.0
            lambda_consistency = 0.0

        torch.manual_seed(SEED)
        variant_results = train_and_evaluate(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            test_loader=test_loader,
            n_epochs=N_EPOCHS,
            lr=LR,
            weight_decay=WEIGHT_DECAY,
            lambda_delta=lambda_delta,
            lambda_consistency=lambda_consistency,
            device=device,
        )
        variant_results["n_params"] = n_params

        # Store lambda values used
        variant_results["lambda_delta"] = lambda_delta
        variant_results["lambda_consistency"] = lambda_consistency

        results[variant_name] = variant_results

        print(
            f"  Test future R2: {variant_results['test_future_r2']:.4f}, "
            f"RMSE: {variant_results['test_future_rmse']:.6f}, "
            f"Time: {variant_results['train_time_sec']:.1f}s"
        )
        print(
            f"  Converged: {variant_results['converged']}, "
            f"NaN: {variant_results['nan_detected']}"
        )
        print()

    # --- Summary table ---
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(
        f"{'Variant':<20} {'Params':>8} {'Test R2':>10} {'Test RMSE':>12} "
        f"{'Delta R2':>10} {'Time(s)':>8} {'OK':>4}"
    )
    print("-" * 80)

    for name, res in results.items():
        ok = "Y" if res["converged"] and not res["nan_detected"] else "N"
        print(
            f"{name:<20} {res['n_params']:>8,} {res['test_future_r2']:>10.4f} "
            f"{res['test_future_rmse']:>12.6f} {res['test_delta_r2']:>10.4f} "
            f"{res['train_time_sec']:>8.1f} {ok:>4}"
        )

    print()

    # --- Sanity checks ---
    all_converged = all(
        r["converged"] and not r["nan_detected"] for r in results.values()
    )
    any_learned = any(r["test_future_r2"] > 0.0 for r in results.values())

    if all_converged:
        print("PASS: All variants completed training without NaN/Inf.")
    else:
        failed = [n for n, r in results.items() if not r["converged"] or r["nan_detected"]]
        print(f"WARN: These variants had issues: {failed}")

    if any_learned:
        print("PASS: At least one variant achieved positive R2 (learned the signal).")
    else:
        print("WARN: No variant achieved positive R2 on synthetic data.")

    return results


# Import for multi-task lambda access
from rigor.experiments.tcn_variants import MultiTaskTCN


def main() -> None:
    """Entry point for the synthetic benchmark."""
    results = run_benchmark()

    # Convert numpy types for JSON serialization
    def _serialize(obj: object) -> object:
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    serializable = {}
    for name, res in results.items():
        serializable[name] = {k: _serialize(v) for k, v in res.items()}

    output_path = Path(__file__).resolve().parent / "synthetic_benchmark_results.json"
    output_path.write_text(json.dumps(serializable, indent=2))
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
