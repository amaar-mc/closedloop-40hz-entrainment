"""
Enhanced time-domain feature extraction from raw EEG windows.

Adds Hjorth parameters (activity, mobility, complexity), sample entropy,
and zero-crossing rate per channel to complement the existing spectral
(Welch PSD) features.

These features capture signal irregularity, morphological complexity, and
transition rates that PSD misses — well-established in EEG BCI literature.

All features are computed within-window only (no future information leakage).
"""

from __future__ import annotations

import math
from typing import List, Tuple

import numpy as np
from scipy.spatial.distance import cdist


def compute_hjorth_params(signal: np.ndarray) -> Tuple[float, float, float]:
    """
    Compute Hjorth activity, mobility, and complexity for a 1D signal.

    Args:
        signal: 1D array of shape (n_samples,)

    Returns:
        (activity, mobility, complexity) — all scalar floats
    """
    activity = float(np.var(signal))

    dx = np.diff(signal)
    mobility = float(np.std(dx) / (np.std(signal) + 1e-12))

    ddx = np.diff(dx)
    dx_mobility = float(np.std(ddx) / (np.std(dx) + 1e-12))
    complexity = dx_mobility / (mobility + 1e-12)

    return activity, mobility, complexity


def compute_sample_entropy(signal: np.ndarray, m: int, r: float) -> float:
    """
    Compute sample entropy (SampEn) for a 1D signal.

    Uses embedding dimension m and tolerance r. Template matches are counted
    using Chebyshev distance with vectorized pairwise computation via cdist.

    Args:
        signal: 1D array of shape (n_samples,)
        m: embedding dimension (typically 2)
        r: tolerance (typically 0.2 * std(signal))

    Returns:
        SampEn value — 0.0 for flat or degenerate signals
    """
    sig_std = np.std(signal)
    if sig_std < 1e-12:
        return 0.0

    n = len(signal)

    # Build template matrices for length m and m+1
    # Templates: rows are consecutive sub-sequences of length m
    # Shape: (n - m, m)
    templates_m = np.array([signal[i : i + m] for i in range(n - m)])
    templates_m1 = np.array([signal[i : i + m + 1] for i in range(n - m - 1)])

    # Count matches at length m (Chebyshev = max of abs diffs)
    # Exclude self-matches on the diagonal
    dist_m = cdist(templates_m[:-1], templates_m[:-1], metric="chebyshev")
    np.fill_diagonal(dist_m, np.inf)
    count_b = float(np.sum(dist_m < r))

    # Count matches at length m+1
    dist_m1 = cdist(templates_m1, templates_m1, metric="chebyshev")
    np.fill_diagonal(dist_m1, np.inf)
    count_a = float(np.sum(dist_m1 < r))

    # Normalise by number of template pairs
    n_pairs_b = float((n - m - 1) * (n - m - 2))
    n_pairs_a = float((n - m - 1) * (n - m - 2))

    if n_pairs_b <= 0 or n_pairs_a <= 0:
        return 0.0

    b = count_b / n_pairs_b
    a = count_a / n_pairs_a

    if b <= 0 or a <= 0:
        return 0.0

    return float(-math.log(a / b))


def compute_zero_crossing_rate(signal: np.ndarray) -> float:
    """
    Compute zero-crossing rate: fraction of samples where sign changes.

    Args:
        signal: 1D array of shape (n_samples,)

    Returns:
        Zero-crossing rate in [0, 1]
    """
    return float(np.sum(np.diff(np.sign(signal)) != 0) / len(signal))


def extract_enhanced_features(eeg_window: np.ndarray, fs: float) -> np.ndarray:
    """
    Extract enhanced time-domain features from a single EEG window.

    For each channel computes: Hjorth activity, Hjorth mobility, Hjorth
    complexity, sample entropy, and zero-crossing rate.

    Args:
        eeg_window: shape (n_channels, n_samples) — squeezed from (1, C, 500)
        fs: sampling frequency in Hz (used for future extensions; not used
            in current feature set which is sample-count-based)

    Returns:
        Flat feature array of shape (5 * n_channels,), ordered channel-by-channel.
        Feature order per channel: hjorth_activity, hjorth_mobility,
        hjorth_complexity, sample_entropy, zcr
    """
    n_channels, n_samples = eeg_window.shape
    features: List[float] = []

    for ch in range(n_channels):
        sig = eeg_window[ch].astype(np.float64)
        sig_std = float(np.std(sig))
        r = 0.2 * sig_std

        activity, mobility, complexity = compute_hjorth_params(sig)
        samp_ent = compute_sample_entropy(sig, m=2, r=r)
        zcr = compute_zero_crossing_rate(sig)

        features.extend([activity, mobility, complexity, samp_ent, zcr])

    return np.array(features, dtype=np.float64)


def get_enhanced_feature_names(n_channels: int) -> List[str]:
    """Return ordered feature names for n_channels."""
    feat_types = [
        "hjorth_activity",
        "hjorth_mobility",
        "hjorth_complexity",
        "sample_entropy",
        "zcr",
    ]
    return [f"{feat}_{ch}" for ch in range(n_channels) for feat in feat_types]


def extract_enhanced_features_batch(windows: np.ndarray) -> np.ndarray:
    """
    Extract enhanced features for a batch of EEG windows.

    Args:
        windows: shape (N, 1, C, 500)

    Returns:
        Feature array of shape (N, 5 * C)
    """
    n_samples, _, n_channels, n_timepoints = windows.shape
    n_feats = 5 * n_channels
    out = np.zeros((n_samples, n_feats), dtype=np.float64)

    for i in range(n_samples):
        if i > 0 and i % 1000 == 0:
            print(f"  Enhanced features: {i}/{n_samples}")
        eeg = windows[i, 0]  # shape (C, 500)
        out[i] = extract_enhanced_features(eeg, fs=250.0)

    return out


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    np.random.seed(42)
    fs = 250.0
    n_ch = 7
    n_t = 500
    t = np.linspace(0, 2.0, n_t)

    # Synthetic EEG: theta (6Hz) + gamma (40Hz) + broadband noise
    synthetic = np.stack(
        [
            np.sin(2 * np.pi * 6 * t) + 0.3 * np.sin(2 * np.pi * 40 * t)
            + 0.1 * np.random.randn(n_t)
            for _ in range(n_ch)
        ]
    )  # (7, 500)

    feats = extract_enhanced_features(synthetic, fs=fs)

    assert feats.shape == (35,), f"Shape mismatch: {feats.shape} != (35,)"
    assert np.all(np.isfinite(feats)), "NaN or inf in features"

    # Hjorth activity per channel = variance; must be > 0 for non-zero signal
    for ch in range(n_ch):
        activity = feats[ch * 5]  # first feature per channel
        assert activity > 0, f"Channel {ch} activity should be > 0, got {activity}"

    # Batch interface
    batch = synthetic[np.newaxis, np.newaxis, :, :]  # (1, 1, 7, 500)
    batch_feats = extract_enhanced_features_batch(batch)
    assert batch_feats.shape == (1, 35), f"Batch shape mismatch: {batch_feats.shape}"
    assert np.allclose(batch_feats[0], feats), "Batch != single mismatch"

    print("[PASS] enhanced_features self-test")
    sys.exit(0)
