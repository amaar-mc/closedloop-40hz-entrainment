"""
TCN Interpretability Analysis for Multiscale Causal TCN.

Performs three interpretability analyses on the trained TCN model:

    1. Attention Weight Analysis: Captures AttentionPool1D attention weights
       across the test set to reveal which past timesteps the model weights
       most heavily when forming predictions.

    2. Feature Group Ablation: Zeros out feature groups (PAC, Spectral,
       Stimulation Context) and measures R-squared drop to quantify each
       group's contribution to prediction performance.

    3. Stimulation-Conditional Performance: Splits the test set by
       stimulation context (stim_on vs stim_off, transition vs steady)
       and computes R-squared for each condition, revealing whether the
       model performs better in certain brain states.

Usage:
    python rigor/experiments/tcn_interpretability.py \\
        --checkpoint-path models/best_multiscale_tcn_lb20_hz1.pth \\
        --data-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean \\
        --output-dir rigor/experiments/interpretability_results

Outputs:
    attention_weights.json        -- Per-position mean attention weights
    feature_ablation.json         -- R-squared drop per feature group
    stimulation_conditional.json  -- R-squared by stimulation condition
    interpretability_summary.json -- Combined summary of all analyses

Author: Amaar Chughtai
Date: February 2026
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from temporal_multiscale.multiscale_tcn import (
    AttentionPool1D,
    ModelConfig,
    MultiscaleCausalTCN,
)

# ---------------------------------------------------------------------------
# Feature group definitions
# ---------------------------------------------------------------------------
# Default multiscale dataset layout (73 features):
#   [0:61)   = spectral features (56 band powers + 5 ratios = 61 dims)
#   [61:68)  = PAC multiscale features (pac_current, ma2, ma4, ma8, ma16, diff1, diff4)
#   [68:73)  = stimulation context (stim_state, time_since_switch, stim_frac, phase_sin, phase_cos)
#
# The actual feature layout is determined at dataset build time and recorded
# in metadata.json.  We define groups by name prefixes for robustness.

FEATURE_GROUP_PREFIXES: Dict[str, List[str]] = {
    "PAC History": ["pac_"],
    "Spectral": ["spectral_"],
    "Stim Context": ["stim_", "time_since_switch", "cycle_phase"],
}


def _resolve_feature_groups(
    feature_names: List[str],
) -> Dict[str, List[int]]:
    """Map feature group names to column indices using prefix matching.

    Args:
        feature_names: Ordered list of feature names from the dataset.

    Returns:
        Dictionary mapping group name to list of feature indices.
    """
    groups: Dict[str, List[int]] = {}
    for group_name, prefixes in FEATURE_GROUP_PREFIXES.items():
        indices = []
        for i, fname in enumerate(feature_names):
            if any(fname.startswith(p) for p in prefixes):
                indices.append(i)
        groups[group_name] = indices

    # Catch any features not assigned to a group
    assigned = set()
    for idx_list in groups.values():
        assigned.update(idx_list)
    unassigned = [i for i in range(len(feature_names)) if i not in assigned]
    if unassigned:
        groups["Other"] = unassigned

    return groups


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------


class InterpretabilityDataset(Dataset):
    """Loads multiscale temporal dataset with metadata for interpretability.

    Extends the standard SequenceDataset to also expose raw targets, subjects,
    and feature names needed for conditional analysis.
    """

    def __init__(self, npz_path: Path) -> None:
        d = np.load(npz_path, allow_pickle=True)
        self.x = torch.from_numpy(d["x_seq"]).float()
        self.y_future = torch.from_numpy(d["y_future_norm"]).float()
        self.y_delta = torch.from_numpy(d["y_delta_norm"]).float()
        self.last_pac = torch.from_numpy(d["last_pac"]).float()
        self.subjects = d["subjects"] if "subjects" in d else None
        self.feature_names = (
            d["feature_names"].tolist() if "feature_names" in d else None
        )

        # Raw x (un-normalized) is not stored separately in the npz, but we
        # need the stim_state column from the *normalized* features to split
        # by condition.  The stim_state feature is binary (0/1) before
        # normalization, so after z-scoring it will be bimodal.  We recover
        # the approximate original by checking which value is closer to the
        # mean of the two modes.  A cleaner approach uses the raw feature
        # names to find the stim_state index.
        self.x_raw = d["x_seq"]  # keep numpy copy for condition analysis

    def __len__(self) -> int:
        return self.x.shape[0]

    def __getitem__(self, i: int) -> Dict[str, torch.Tensor]:
        return {
            "x_seq": self.x[i],
            "y_future": self.y_future[i],
            "y_delta": self.y_delta[i],
            "last_pac": self.last_pac[i],
        }


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute R-squared, returning 0.0 when variance is near zero."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    if ss_tot < 1e-12:
        return 0.0
    return float(1.0 - ss_res / ss_tot)


def _metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Compute standard regression metrics."""
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    return {
        "r2": _r2(y_true, y_pred),
        "mae": mae,
        "rmse": rmse,
        "n_samples": len(y_true),
    }


def _denorm(y_norm: np.ndarray, mean: float, std: float) -> np.ndarray:
    """Denormalize z-scored predictions."""
    return y_norm * std + mean


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------


def load_model_and_scalers(
    checkpoint_path: Path,
    device: torch.device,
) -> Tuple[MultiscaleCausalTCN, Dict[str, float], Dict[str, Any]]:
    """Load the trained TCN checkpoint.

    Args:
        checkpoint_path: Path to the .pth checkpoint file.
        device: Torch device for the model.

    Returns:
        Tuple of (model, scalers_dict, metadata_dict).

    Raises:
        FileNotFoundError: If checkpoint file does not exist.
    """
    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Checkpoint not found: {checkpoint_path}\n"
            "Train the model first with temporal_multiscale/train_multiscale_tcn.py"
        )

    ckpt = torch.load(checkpoint_path, map_location=device, weights_only=False)
    cfg = ModelConfig(**ckpt["cfg"])
    model = MultiscaleCausalTCN(cfg)
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(device)
    model.eval()

    scalers = ckpt.get("scalers", {})
    metadata = ckpt.get("metadata", {})

    return model, scalers, metadata


# ---------------------------------------------------------------------------
# Analysis 1: Attention Weight Analysis
# ---------------------------------------------------------------------------


class AttentionWeightCapture:
    """Hook-based capture of AttentionPool1D attention weights.

    Registers a forward hook on the AttentionPool1D.score Conv1d layer
    to intercept logits before softmax, then computes and stores the
    resulting attention weights for each batch.
    """

    def __init__(self, model: MultiscaleCausalTCN) -> None:
        self.weights_list: List[np.ndarray] = []
        self._hook_handle = None

        # Find the AttentionPool1D module
        if not isinstance(model.pool, AttentionPool1D):
            raise ValueError(
                f"Model pool type is {type(model.pool).__name__}, "
                "not AttentionPool1D. Cannot capture attention weights."
            )

        # Hook into the full AttentionPool1D forward to capture weights
        self._hook_handle = model.pool.register_forward_hook(self._hook_fn)

    def _hook_fn(
        self,
        module: nn.Module,
        input: Tuple[torch.Tensor, ...],
        output: torch.Tensor,
    ) -> None:
        """Forward hook that computes and stores attention weights.

        The AttentionPool1D forward does:
            logits = self.score(x)        # (B, 1, T)
            weights = softmax(logits, -1) # (B, 1, T)
            pooled = (x * weights).sum(-1)

        We recompute weights from the input to avoid modifying the module.
        """
        x = input[0]  # (B, C, T)
        with torch.no_grad():
            logits = module.score(x)  # (B, 1, T)
            weights = torch.softmax(logits, dim=-1)  # (B, 1, T)
            self.weights_list.append(weights.squeeze(1).cpu().numpy())

    def remove(self) -> None:
        """Remove the forward hook."""
        if self._hook_handle is not None:
            self._hook_handle.remove()
            self._hook_handle = None

    def get_all_weights(self) -> np.ndarray:
        """Concatenate all captured weights into (N, T) array."""
        if not self.weights_list:
            return np.array([])
        return np.concatenate(self.weights_list, axis=0)


@torch.no_grad()
def analyze_attention_weights(
    model: MultiscaleCausalTCN,
    loader: DataLoader,
    device: torch.device,
) -> Dict[str, Any]:
    """Run the test set through the model and capture attention weights.

    Args:
        model: Trained TCN model with AttentionPool1D.
        loader: Test data loader.
        device: Compute device.

    Returns:
        Dictionary with per-position attention statistics.
    """
    model.eval()

    if not isinstance(model.pool, AttentionPool1D):
        return {
            "error": (
                f"Model uses {type(model.pool).__name__} pooling, "
                "not AttentionPool1D. Skipping attention analysis."
            ),
        }

    capture = AttentionWeightCapture(model)

    try:
        for batch in loader:
            x = batch["x_seq"].to(device)
            _ = model(x)
    finally:
        capture.remove()

    all_weights = capture.get_all_weights()  # (N, T)
    if all_weights.size == 0:
        return {"error": "No attention weights captured."}

    n_samples, seq_len = all_weights.shape

    # Compute per-position statistics
    mean_weights = all_weights.mean(axis=0).tolist()
    std_weights = all_weights.std(axis=0).tolist()
    median_weights = np.median(all_weights, axis=0).tolist()
    p25_weights = np.percentile(all_weights, 25, axis=0).tolist()
    p75_weights = np.percentile(all_weights, 75, axis=0).tolist()

    # Identify the most-attended positions
    mean_arr = np.array(mean_weights)
    top_k = min(5, seq_len)
    top_positions = np.argsort(mean_arr)[::-1][:top_k].tolist()

    # Compute entropy of attention distribution (higher = more uniform)
    # H = -sum(w * log(w + eps))
    eps = 1e-10
    entropy_per_sample = -np.sum(
        all_weights * np.log(all_weights + eps), axis=1
    )
    max_entropy = float(np.log(seq_len))

    result = {
        "n_samples": n_samples,
        "sequence_length": seq_len,
        "mean_attention_per_position": mean_weights,
        "std_attention_per_position": std_weights,
        "median_attention_per_position": median_weights,
        "p25_attention_per_position": p25_weights,
        "p75_attention_per_position": p75_weights,
        "top_attended_positions": top_positions,
        "top_attended_weights": [float(mean_arr[i]) for i in top_positions],
        "attention_entropy_mean": float(np.mean(entropy_per_sample)),
        "attention_entropy_std": float(np.std(entropy_per_sample)),
        "max_possible_entropy": max_entropy,
        "normalized_entropy": float(np.mean(entropy_per_sample) / max_entropy),
        "interpretation": {
            "position_0": "Oldest timestep in lookback window",
            f"position_{seq_len - 1}": "Most recent timestep (current)",
            "high_entropy": "Attention is spread uniformly across time",
            "low_entropy": "Attention concentrates on specific positions",
        },
    }

    return result


# ---------------------------------------------------------------------------
# Analysis 2: Feature Group Ablation
# ---------------------------------------------------------------------------


@torch.no_grad()
def run_ablation_experiment(
    model: MultiscaleCausalTCN,
    loader: DataLoader,
    device: torch.device,
    feature_groups: Dict[str, List[int]],
    yf_mean: float,
    yf_std: float,
) -> Dict[str, Any]:
    """Zero-ablation experiment: zero out each feature group and measure R2 drop.

    For each feature group, the corresponding columns in x_seq are set to
    zero (which in normalized space corresponds to the mean value). This
    measures the marginal importance of each group by observing how much
    performance degrades when it is removed.

    Args:
        model: Trained TCN model.
        loader: Test data loader.
        device: Compute device.
        feature_groups: Mapping from group name to list of feature indices.
        yf_mean: Future PAC target mean for denormalization.
        yf_std: Future PAC target std for denormalization.

    Returns:
        Dictionary with baseline R2 and per-group ablation results.
    """
    model.eval()

    # First pass: collect baseline (unablated) predictions
    all_pred_norm: List[np.ndarray] = []
    all_true_norm: List[np.ndarray] = []
    all_x: List[torch.Tensor] = []

    for batch in loader:
        x = batch["x_seq"].to(device)
        y_future = batch["y_future"].cpu().numpy()
        all_x.append(x.cpu())

        out = model(x)
        all_pred_norm.append(out["future"].cpu().numpy())
        all_true_norm.append(y_future)

    pred_baseline = _denorm(np.concatenate(all_pred_norm), yf_mean, yf_std)
    true_values = _denorm(np.concatenate(all_true_norm), yf_mean, yf_std)
    baseline_r2 = _r2(true_values, pred_baseline)
    baseline_metrics = _metrics(true_values, pred_baseline)

    # Concatenate all inputs for ablation passes
    x_all = torch.cat(all_x, dim=0)  # (N, T, F)

    # For each feature group, zero out those columns and re-run inference
    ablation_results: Dict[str, Any] = {}

    for group_name, indices in feature_groups.items():
        if not indices:
            ablation_results[group_name] = {
                "indices": indices,
                "n_features": 0,
                "note": "No features in this group",
            }
            continue

        # Create ablated copy
        x_ablated = x_all.clone()
        x_ablated[:, :, indices] = 0.0  # Zero in normalized space = feature mean

        # Run inference in batches to avoid memory issues
        ablated_preds: List[np.ndarray] = []
        batch_size = loader.batch_size or 128
        for start in range(0, len(x_ablated), batch_size):
            end = min(start + batch_size, len(x_ablated))
            x_batch = x_ablated[start:end].to(device)
            out = model(x_batch)
            ablated_preds.append(out["future"].cpu().numpy())

        pred_ablated = _denorm(np.concatenate(ablated_preds), yf_mean, yf_std)
        ablated_r2 = _r2(true_values, pred_ablated)
        ablated_metrics = _metrics(true_values, pred_ablated)

        r2_drop = baseline_r2 - ablated_r2
        r2_drop_pct = (
            100.0 * r2_drop / abs(baseline_r2) if abs(baseline_r2) > 1e-12 else 0.0
        )

        ablation_results[group_name] = {
            "indices": indices,
            "n_features": len(indices),
            "ablated_r2": ablated_r2,
            "ablated_mae": ablated_metrics["mae"],
            "ablated_rmse": ablated_metrics["rmse"],
            "r2_drop": r2_drop,
            "r2_drop_pct": r2_drop_pct,
        }

    result = {
        "baseline_r2": baseline_r2,
        "baseline_metrics": baseline_metrics,
        "feature_groups": ablation_results,
        "total_features": int(x_all.shape[-1]),
        "interpretation": {
            "positive_r2_drop": "Removing this group HURTS performance (group is useful)",
            "negative_r2_drop": "Removing this group HELPS performance (group may add noise)",
            "zero_in_normalized_space": "Ablated features are set to their training mean",
        },
    }

    return result


# ---------------------------------------------------------------------------
# Analysis 3: Stimulation-Conditional Performance
# ---------------------------------------------------------------------------


def _find_stim_state_index(feature_names: List[str]) -> Optional[int]:
    """Find the index of the stim_state feature.

    Args:
        feature_names: List of feature names from the dataset.

    Returns:
        Index of the stim_state feature, or None if not found.
    """
    for i, name in enumerate(feature_names):
        if name == "stim_state":
            return i
    return None


def _find_time_since_switch_index(feature_names: List[str]) -> Optional[int]:
    """Find the index of the time_since_switch feature.

    Args:
        feature_names: List of feature names from the dataset.

    Returns:
        Index of the time_since_switch feature, or None if not found.
    """
    for i, name in enumerate(feature_names):
        if name.startswith("time_since_switch"):
            return i
    return None


@torch.no_grad()
def analyze_stimulation_conditional(
    model: MultiscaleCausalTCN,
    dataset: InterpretabilityDataset,
    device: torch.device,
    yf_mean: float,
    yf_std: float,
    feature_names: List[str],
    scalers_npz_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Compute prediction performance conditioned on stimulation state.

    Splits the test set into conditions:
    - stim_on:   Last timestep in sequence has stim_state = 1
    - stim_off:  Last timestep in sequence has stim_state = 0
    - transition: time_since_switch is small (< 10s normalized)
    - steady:     time_since_switch is large (>= 10s normalized)

    For reliable condition splitting, we use the *raw* (un-normalized)
    feature values when available via scalers, or fall back to thresholding
    the normalized values.

    Args:
        model: Trained TCN model.
        dataset: Test dataset with raw x values.
        device: Compute device.
        yf_mean: Future PAC target mean.
        yf_std: Future PAC target std.
        feature_names: Feature name list.
        scalers_npz_path: Path to scalers.npz for de-normalizing features.

    Returns:
        Dictionary with per-condition metrics.
    """
    model.eval()

    stim_idx = _find_stim_state_index(feature_names)
    tss_idx = _find_time_since_switch_index(feature_names)

    if stim_idx is None:
        return {
            "error": "Could not find 'stim_state' feature in feature names. "
            "Cannot perform stimulation-conditional analysis."
        }

    # Load feature-level scalers to de-normalize stim features
    feat_mean = None
    feat_std = None
    if scalers_npz_path is not None and scalers_npz_path.exists():
        s = np.load(scalers_npz_path)
        if "feature_mean" in s and "feature_std" in s:
            feat_mean = s["feature_mean"]
            feat_std = s["feature_std"]

    # Collect predictions and conditions
    x_raw = dataset.x_raw  # (N, T, F) numpy, normalized
    n_samples = len(dataset)
    seq_len = x_raw.shape[1]

    # Use last timestep for condition labeling (most recent state)
    last_step_features = x_raw[:, -1, :]  # (N, F)

    # De-normalize stim_state to recover binary values
    if feat_mean is not None and feat_std is not None:
        stim_raw = (
            last_step_features[:, stim_idx] * feat_std[stim_idx]
            + feat_mean[stim_idx]
        )
    else:
        # Fall back: stim_state is binary, so in normalized space the two
        # modes are at (-mean/std) and ((1-mean)/std). Threshold at 0.5
        # in raw space is (0.5 - mean) / std in normalized space.
        stim_raw = last_step_features[:, stim_idx]

    # Binary classification: stim_on if raw value > 0.5
    is_stim_on = stim_raw > 0.5

    # Transition vs steady (if time_since_switch is available)
    is_transition = np.zeros(n_samples, dtype=bool)
    transition_threshold_sec = 10.0  # Seconds
    if tss_idx is not None:
        if feat_mean is not None and feat_std is not None:
            tss_raw = (
                last_step_features[:, tss_idx] * feat_std[tss_idx]
                + feat_mean[tss_idx]
            )
            # time_since_switch is stored as min(t/60, 1.0), so threshold
            # 10s corresponds to 10/60 = 0.167
            is_transition = tss_raw < (transition_threshold_sec / 60.0)
        else:
            # Without scalers, use normalized value threshold
            tss_norm = last_step_features[:, tss_idx]
            is_transition = tss_norm < np.median(tss_norm)

    # Run full inference
    loader = DataLoader(dataset, batch_size=256, shuffle=False, num_workers=0)
    all_pred_norm: List[np.ndarray] = []
    all_true_norm: List[np.ndarray] = []

    for batch in loader:
        x = batch["x_seq"].to(device)
        out = model(x)
        all_pred_norm.append(out["future"].cpu().numpy())
        all_true_norm.append(batch["y_future"].cpu().numpy())

    pred_all = _denorm(np.concatenate(all_pred_norm), yf_mean, yf_std)
    true_all = _denorm(np.concatenate(all_true_norm), yf_mean, yf_std)

    # Compute overall metrics
    overall_metrics = _metrics(true_all, pred_all)

    # Define conditions
    conditions: Dict[str, np.ndarray] = {
        "stim_on": is_stim_on,
        "stim_off": ~is_stim_on,
        "transition": is_transition,
        "steady": ~is_transition,
        "stim_on_transition": is_stim_on & is_transition,
        "stim_on_steady": is_stim_on & ~is_transition,
        "stim_off_transition": ~is_stim_on & is_transition,
        "stim_off_steady": ~is_stim_on & ~is_transition,
    }

    condition_results: Dict[str, Any] = {}
    for cond_name, mask in conditions.items():
        n_cond = int(np.sum(mask))
        if n_cond < 10:
            condition_results[cond_name] = {
                "n_samples": n_cond,
                "note": f"Too few samples ({n_cond}) for reliable metrics",
            }
            continue

        cond_metrics = _metrics(true_all[mask], pred_all[mask])
        cond_metrics["n_samples"] = n_cond
        cond_metrics["fraction_of_total"] = round(n_cond / n_samples, 4)
        condition_results[cond_name] = cond_metrics

    result = {
        "overall": overall_metrics,
        "conditions": condition_results,
        "n_total": n_samples,
        "stim_state_feature_index": stim_idx,
        "time_since_switch_feature_index": tss_idx,
        "transition_threshold_sec": transition_threshold_sec,
        "interpretation": {
            "stim_on": "Stimulation was active at the last timestep in the input window",
            "stim_off": "Rest period at the last timestep in the input window",
            "transition": f"Within {transition_threshold_sec}s of a state switch",
            "steady": f"More than {transition_threshold_sec}s since last state switch",
        },
    }

    return result


# ---------------------------------------------------------------------------
# Pretty printing
# ---------------------------------------------------------------------------


def print_attention_summary(results: Dict[str, Any]) -> None:
    """Print attention weight analysis summary."""
    print("\n" + "=" * 72)
    print("ATTENTION WEIGHT ANALYSIS")
    print("=" * 72)

    if "error" in results:
        print(f"  {results['error']}")
        return

    seq_len = results["sequence_length"]
    mean_weights = results["mean_attention_per_position"]

    print(f"  Sequence length:     {seq_len}")
    print(f"  Number of samples:   {results['n_samples']}")
    print(f"  Normalized entropy:  {results['normalized_entropy']:.4f}")
    print(f"    (1.0 = perfectly uniform, 0.0 = fully concentrated)")
    print()

    # Print top-5 most attended positions
    print("  Top-5 Most Attended Positions:")
    print(f"    {'Position':<12} {'Rel. to End':<14} {'Mean Weight':<14} {'Description'}")
    print("    " + "-" * 55)
    for pos, w in zip(
        results["top_attended_positions"], results["top_attended_weights"]
    ):
        rel = pos - (seq_len - 1)
        desc = "most recent" if pos == seq_len - 1 else f"{abs(rel)} steps ago"
        print(f"    {pos:<12} {rel:<14} {w:<14.6f} {desc}")

    # Print weight distribution across time (binned for readability)
    print()
    n_bins = min(10, seq_len)
    bin_size = seq_len // n_bins
    print(f"  Attention Distribution (binned into {n_bins} groups):")
    print(f"    {'Positions':<18} {'Mean Weight Sum':<18} {'Bar'}")
    print("    " + "-" * 55)
    max_bin_sum = 0.0
    bins = []
    for b in range(n_bins):
        start = b * bin_size
        end = start + bin_size if b < n_bins - 1 else seq_len
        bin_sum = sum(mean_weights[start:end])
        bins.append((start, end, bin_sum))
        max_bin_sum = max(max_bin_sum, bin_sum)

    for start, end, bin_sum in bins:
        bar_len = int(40 * bin_sum / (max_bin_sum + 1e-10))
        bar = "#" * bar_len
        label = f"[{start:3d}-{end - 1:3d}]"
        print(f"    {label:<18} {bin_sum:<18.6f} {bar}")


def print_ablation_summary(results: Dict[str, Any]) -> None:
    """Print feature group ablation summary."""
    print("\n" + "=" * 72)
    print("FEATURE GROUP ABLATION")
    print("=" * 72)

    baseline_r2 = results["baseline_r2"]
    print(f"  Baseline R2:       {baseline_r2:.4f}")
    print(f"  Total features:    {results['total_features']}")
    print()

    print(
        f"  {'Group':<20} {'N Features':>10} {'Ablated R2':>12} "
        f"{'R2 Drop':>10} {'Drop %':>10}"
    )
    print("  " + "-" * 66)

    groups = results["feature_groups"]
    # Sort by R2 drop (most important first)
    sorted_groups = sorted(
        groups.items(),
        key=lambda kv: kv[1].get("r2_drop", 0.0),
        reverse=True,
    )
    for group_name, gdata in sorted_groups:
        if "note" in gdata:
            print(f"  {group_name:<20} {gdata['n_features']:>10} {'--':>12} {'--':>10} {gdata['note']}")
            continue
        print(
            f"  {group_name:<20} {gdata['n_features']:>10} "
            f"{gdata['ablated_r2']:>12.4f} {gdata['r2_drop']:>10.4f} "
            f"{gdata['r2_drop_pct']:>9.1f}%"
        )


def print_conditional_summary(results: Dict[str, Any]) -> None:
    """Print stimulation-conditional performance summary."""
    print("\n" + "=" * 72)
    print("STIMULATION-CONDITIONAL PERFORMANCE")
    print("=" * 72)

    if "error" in results:
        print(f"  {results['error']}")
        return

    overall = results["overall"]
    print(f"  Overall R2:        {overall['r2']:.4f}")
    print(f"  Overall MAE:       {overall['mae']:.6f}")
    print(f"  Total samples:     {results['n_total']}")
    print()

    print(
        f"  {'Condition':<25} {'N Samples':>10} {'Fraction':>10} "
        f"{'R2':>10} {'MAE':>12} {'RMSE':>12}"
    )
    print("  " + "-" * 82)

    conditions = results["conditions"]
    for cond_name, cdata in conditions.items():
        if "note" in cdata:
            print(f"  {cond_name:<25} {cdata['n_samples']:>10} {'':>10} {cdata['note']}")
            continue
        print(
            f"  {cond_name:<25} {cdata['n_samples']:>10} "
            f"{cdata['fraction_of_total']:>10.4f} "
            f"{cdata['r2']:>10.4f} {cdata['mae']:>12.6f} {cdata['rmse']:>12.6f}"
        )


# ---------------------------------------------------------------------------
# JSON serialization
# ---------------------------------------------------------------------------


def _make_serializable(obj: Any) -> Any:
    """Recursively convert numpy types for JSON serialization."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {str(k): _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_serializable(v) for v in obj]
    if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    return obj


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(
        description="TCN Interpretability Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python rigor/experiments/tcn_interpretability.py \\\n"
            "    --checkpoint-path models/best_multiscale_tcn_lb20_hz1.pth \\\n"
            "    --data-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean\n"
        ),
    )
    p.add_argument(
        "--checkpoint-path",
        type=str,
        required=True,
        help="Path to trained TCN checkpoint (.pth file).",
    )
    p.add_argument(
        "--data-dir",
        type=str,
        required=True,
        help="Path to multiscale temporal dataset directory.",
    )
    p.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).resolve().parent / "interpretability_results"),
        help="Directory for output JSON files.",
    )
    p.add_argument(
        "--batch-size",
        type=int,
        default=256,
        help="Batch size for inference (default: 256).",
    )
    return p.parse_args()


def main() -> None:
    """Run all interpretability analyses."""
    args = parse_args()

    checkpoint_path = Path(args.checkpoint_path)
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("TCN INTERPRETABILITY ANALYSIS")
    print("=" * 72)
    print(f"  Checkpoint:  {checkpoint_path}")
    print(f"  Data dir:    {data_dir}")
    print(f"  Output dir:  {output_dir}")

    # ------------------------------------------------------------------
    # Validate inputs
    # ------------------------------------------------------------------
    missing_files: List[str] = []
    if not checkpoint_path.exists():
        missing_files.append(f"Checkpoint: {checkpoint_path}")
    for fname in ["test_multiscale.npz", "scalers.npz", "metadata.json"]:
        if not (data_dir / fname).exists():
            missing_files.append(f"Data file: {data_dir / fname}")

    if missing_files:
        print("\nERROR: The following required files are missing:")
        for f in missing_files:
            print(f"  - {f}")
        print(
            "\nTo generate these files:\n"
            "  1. Build dataset: python temporal_multiscale/build_multiscale_dataset.py\n"
            "  2. Train model:   python temporal_multiscale/train_multiscale_tcn.py"
        )
        sys.exit(1)

    # ------------------------------------------------------------------
    # Load model and data
    # ------------------------------------------------------------------
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  Device:      {device}")

    model, scalers, metadata = load_model_and_scalers(checkpoint_path, device)
    print(f"  Parameters:  {model.count_parameters():,}")
    print(f"  Pool type:   {model.cfg.pool_type}")

    yf_mean = scalers.get("y_future_mean", 0.0)
    yf_std = scalers.get("y_future_std", 1.0)

    test_ds = InterpretabilityDataset(data_dir / "test_multiscale.npz")
    test_loader = DataLoader(
        test_ds, batch_size=args.batch_size, shuffle=False, num_workers=0
    )
    print(f"  Test samples: {len(test_ds):,}")

    # Resolve feature names
    feature_names: List[str] = []
    if test_ds.feature_names is not None:
        feature_names = test_ds.feature_names
    else:
        # Fall back to metadata or generic names
        n_features = int(metadata.get("n_features", test_ds.x.shape[-1]))
        feature_names = [f"feature_{i}" for i in range(n_features)]

    print(f"  Features:    {len(feature_names)}")

    # ------------------------------------------------------------------
    # Analysis 1: Attention Weights
    # ------------------------------------------------------------------
    print("\n[1/3] Analyzing attention weights...")
    attention_results = analyze_attention_weights(model, test_loader, device)
    print_attention_summary(attention_results)

    attention_path = output_dir / "attention_weights.json"
    attention_path.write_text(
        json.dumps(_make_serializable(attention_results), indent=2)
    )
    print(f"\n  Saved: {attention_path}")

    # ------------------------------------------------------------------
    # Analysis 2: Feature Group Ablation
    # ------------------------------------------------------------------
    print("\n[2/3] Running feature group ablation...")
    feature_groups = _resolve_feature_groups(feature_names)

    # Print discovered feature groups
    for group_name, indices in feature_groups.items():
        print(f"    {group_name}: {len(indices)} features (indices {indices[0]}-{indices[-1] if indices else 'N/A'})")

    ablation_results = run_ablation_experiment(
        model=model,
        loader=test_loader,
        device=device,
        feature_groups=feature_groups,
        yf_mean=yf_mean,
        yf_std=yf_std,
    )
    print_ablation_summary(ablation_results)

    ablation_path = output_dir / "feature_ablation.json"
    ablation_path.write_text(
        json.dumps(_make_serializable(ablation_results), indent=2)
    )
    print(f"\n  Saved: {ablation_path}")

    # ------------------------------------------------------------------
    # Analysis 3: Stimulation-Conditional Performance
    # ------------------------------------------------------------------
    print("\n[3/3] Analyzing stimulation-conditional performance...")
    scalers_npz_path = data_dir / "scalers.npz"
    conditional_results = analyze_stimulation_conditional(
        model=model,
        dataset=test_ds,
        device=device,
        yf_mean=yf_mean,
        yf_std=yf_std,
        feature_names=feature_names,
        scalers_npz_path=scalers_npz_path,
    )
    print_conditional_summary(conditional_results)

    conditional_path = output_dir / "stimulation_conditional.json"
    conditional_path.write_text(
        json.dumps(_make_serializable(conditional_results), indent=2)
    )
    print(f"\n  Saved: {conditional_path}")

    # ------------------------------------------------------------------
    # Combined summary
    # ------------------------------------------------------------------
    combined = {
        "checkpoint": str(checkpoint_path),
        "data_dir": str(data_dir),
        "model_params": model.count_parameters(),
        "pool_type": model.cfg.pool_type,
        "n_test_samples": len(test_ds),
        "n_features": len(feature_names),
        "feature_names": feature_names,
        "attention_analysis": attention_results,
        "feature_ablation": ablation_results,
        "stimulation_conditional": conditional_results,
    }

    summary_path = output_dir / "interpretability_summary.json"
    summary_path.write_text(json.dumps(_make_serializable(combined), indent=2))

    print("\n" + "=" * 72)
    print("INTERPRETABILITY ANALYSIS COMPLETE")
    print("=" * 72)
    print(f"  Output directory: {output_dir}")
    print(f"  Files:")
    print(f"    - {attention_path.name}")
    print(f"    - {ablation_path.name}")
    print(f"    - {conditional_path.name}")
    print(f"    - {summary_path.name}")
    print("=" * 72)


if __name__ == "__main__":
    main()
