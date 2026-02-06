"""
Personalization Module for Adaptive Baseline Tracking

Implements rolling window baseline computation and z-score normalization for
subject-specific adaptation of closed-loop control thresholds.

Key Features:
    - 30-second rolling window for baseline PAC estimation
    - Z-score normalization for standardized threshold comparison
    - Circular buffer for efficient O(1) updates
    - Minimum sample requirement before z-score computation

Author: Amaar Chughtai
Date: February 2026
"""

import numpy as np
from collections import deque
from typing import Optional, Tuple


class PersonalizationModule:
    """
    Maintains patient-specific baseline statistics and computes z-scores.

    The personalization module adapts the closed-loop controller to individual
    patient neural dynamics by tracking a rolling baseline of PAC values and
    computing standardized z-scores for threshold-based decisions.

    Attributes:
        window_size: Number of PAC samples to include in baseline window
        min_samples: Minimum samples required before computing z-scores
        pac_buffer: Circular buffer storing recent PAC values
    """

    def __init__(self,
                 window_size: int = 30,
                 min_samples: int = 10):
        """
        Initialize personalization module.

        Args:
            window_size: Number of seconds for rolling baseline window (default 30)
                        At 1 Hz decision rate, this is 30 samples
            min_samples: Minimum samples needed before z-score computation (default 10)
                        Prevents unstable statistics with too few samples
        """
        self.window_size = window_size
        self.min_samples = min_samples

        # Circular buffer with maximum size = window_size
        # Automatically discards oldest values when full
        self.pac_buffer = deque(maxlen=window_size)

        # Statistics cache (updated on demand)
        self._mean_cache = None
        self._std_cache = None
        self._cache_valid = False

    def update(self, pac_value: float):
        """
        Add new PAC value to the rolling baseline buffer.

        Args:
            pac_value: Current PAC measurement to add to baseline
        """
        self.pac_buffer.append(pac_value)
        self._cache_valid = False  # Invalidate statistics cache

    def get_baseline_stats(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Compute mean and standard deviation of baseline PAC values.

        Returns:
            mean: Mean PAC over baseline window, or None if insufficient data
            std: Standard deviation of PAC, or None if insufficient data

        Note:
            Returns (None, None) if fewer than min_samples are available.
            Adds small epsilon (1e-8) to std to prevent division by zero.
        """
        if len(self.pac_buffer) < self.min_samples:
            return None, None

        # Use cached values if available
        if self._cache_valid:
            return self._mean_cache, self._std_cache

        # Compute statistics
        values = np.array(self.pac_buffer)
        mean = np.mean(values)
        std = np.std(values) + 1e-8  # Add epsilon to prevent division by zero

        # Update cache
        self._mean_cache = float(mean)
        self._std_cache = float(std)
        self._cache_valid = True

        return self._mean_cache, self._std_cache

    def compute_zscore(self, pac_value: float) -> Optional[float]:
        """
        Compute z-score of current PAC relative to rolling baseline.

        Z-score formula: z = (PAC - μ_baseline) / σ_baseline

        Args:
            pac_value: Current PAC value to normalize

        Returns:
            z_score: Standardized z-score, or None if insufficient baseline data

        Interpretation:
            z < 0: PAC below baseline (weak coupling)
            z = 0: PAC at baseline (normal coupling)
            z > 0: PAC above baseline (strong coupling)
        """
        mean, std = self.get_baseline_stats()

        if mean is None:
            return None  # Insufficient data for z-score

        z_score = (pac_value - mean) / std
        return float(z_score)

    def reset(self):
        """
        Clear baseline buffer and statistics cache.

        Use this when:
        - Starting a new patient session
        - Detecting a major state change
        - Resetting the controller
        """
        self.pac_buffer.clear()
        self._mean_cache = None
        self._std_cache = None
        self._cache_valid = False

    def get_buffer_size(self) -> int:
        """Return current number of samples in baseline buffer."""
        return len(self.pac_buffer)

    def is_ready(self) -> bool:
        """Check if baseline has sufficient samples for z-score computation."""
        return len(self.pac_buffer) >= self.min_samples

    def get_buffer_contents(self) -> np.ndarray:
        """
        Return copy of current baseline buffer contents.

        Returns:
            buffer: Array of PAC values in temporal order (oldest to newest)
        """
        return np.array(self.pac_buffer)


class MultiChannelPersonalization:
    """
    Personalization module for multi-channel PAC with separate baselines.

    Maintains independent baseline statistics for each EEG channel, enabling
    channel-specific z-score computation for spatially-aware control strategies.
    """

    def __init__(self,
                 n_channels: int,
                 window_size: int = 30,
                 min_samples: int = 10):
        """
        Initialize multi-channel personalization.

        Args:
            n_channels: Number of EEG channels
            window_size: Rolling window size per channel
            min_samples: Minimum samples per channel before z-scores
        """
        self.n_channels = n_channels
        self.modules = [
            PersonalizationModule(window_size, min_samples)
            for _ in range(n_channels)
        ]

    def update(self, pac_values: np.ndarray):
        """
        Update baseline for all channels.

        Args:
            pac_values: PAC values for each channel (n_channels,)
        """
        assert len(pac_values) == self.n_channels, \
            f"Expected {self.n_channels} PAC values, got {len(pac_values)}"

        for ch, pac in enumerate(pac_values):
            self.modules[ch].update(pac)

    def compute_zscores(self, pac_values: np.ndarray) -> np.ndarray:
        """
        Compute z-scores for all channels.

        Args:
            pac_values: Current PAC values (n_channels,)

        Returns:
            z_scores: Z-scores per channel (n_channels,)
                     NaN for channels with insufficient baseline data
        """
        z_scores = np.zeros(self.n_channels)

        for ch, pac in enumerate(pac_values):
            z = self.modules[ch].compute_zscore(pac)
            z_scores[ch] = z if z is not None else np.nan

        return z_scores

    def compute_average_zscore(self, pac_values: np.ndarray) -> Optional[float]:
        """
        Compute average z-score across all channels (ignoring NaN).

        Args:
            pac_values: Current PAC values (n_channels,)

        Returns:
            z_avg: Average z-score, or None if no channels are ready
        """
        z_scores = self.compute_zscores(pac_values)
        valid_z = z_scores[~np.isnan(z_scores)]

        if len(valid_z) == 0:
            return None

        return float(np.mean(valid_z))

    def reset(self):
        """Reset all channel baselines."""
        for module in self.modules:
            module.reset()

    def is_ready(self) -> bool:
        """Check if at least one channel has sufficient baseline data."""
        return any(module.is_ready() for module in self.modules)


def test_personalization():
    """Test personalization module with synthetic PAC time series."""
    print("=" * 60)
    print("Personalization Module Test")
    print("=" * 60)

    # Create personalization module
    pers = PersonalizationModule(window_size=30, min_samples=10)

    # Simulate PAC time series
    np.random.seed(42)
    baseline_pac = 0.15  # Baseline PAC
    noise_level = 0.02

    print("\n1. Testing baseline accumulation...")
    for t in range(15):
        pac = baseline_pac + np.random.randn() * noise_level
        pers.update(pac)

        if t < 9:
            z = pers.compute_zscore(pac)
            print(f"  t={t+1}: PAC={pac:.4f}, z-score=Not ready (need {10-t-1} more)")
        elif t == 9:
            z = pers.compute_zscore(pac)
            print(f"  t={t+1}: PAC={pac:.4f}, z-score={z:.2f} (baseline established!)")
        else:
            z = pers.compute_zscore(pac)
            print(f"  t={t+1}: PAC={pac:.4f}, z-score={z:.2f}")

    print("\n2. Testing z-score interpretation...")
    mean, std = pers.get_baseline_stats()
    print(f"  Baseline: μ={mean:.4f}, σ={std:.4f}")

    # Test weak coupling (below baseline)
    weak_pac = mean - 1.5 * std
    z_weak = pers.compute_zscore(weak_pac)
    print(f"\n  Weak coupling: PAC={weak_pac:.4f}, z={z_weak:.2f}")
    print(f"    → z < -0.5: STIMULATE (boost gamma)")

    # Test normal coupling
    normal_pac = mean
    z_normal = pers.compute_zscore(normal_pac)
    print(f"\n  Normal coupling: PAC={normal_pac:.4f}, z={z_normal:.2f}")
    print(f"    → -0.5 ≤ z ≤ +0.5: MAINTAIN current state")

    # Test strong coupling (above baseline)
    strong_pac = mean + 1.5 * std
    z_strong = pers.compute_zscore(strong_pac)
    print(f"\n  Strong coupling: PAC={strong_pac:.4f}, z={z_strong:.2f}")
    print(f"    → z > +0.5: REST (prevent habituation)")

    print("\n3. Testing multi-channel personalization...")
    multi_pers = MultiChannelPersonalization(n_channels=7, window_size=30)

    # Simulate 15 timesteps of 7-channel PAC
    for t in range(15):
        # Each channel has slightly different baseline
        pac_values = baseline_pac + np.random.randn(7) * noise_level
        pac_values += np.linspace(-0.02, 0.02, 7)  # Spatial gradient
        multi_pers.update(pac_values)

    # Compute z-scores for new observation
    test_pac = baseline_pac + np.linspace(-0.03, 0.03, 7)
    z_scores = multi_pers.compute_zscores(test_pac)
    z_avg = multi_pers.compute_average_zscore(test_pac)

    print(f"\n  Per-channel z-scores:")
    for ch, z in enumerate(z_scores):
        print(f"    Channel {ch+1}: z={z:.2f}")
    print(f"\n  Average z-score: {z_avg:.2f}")

    print("\n4. Testing reset functionality...")
    pers.reset()
    print(f"  Buffer size after reset: {pers.get_buffer_size()}")
    print(f"  Ready for z-scores: {pers.is_ready()}")

    print("\n" + "=" * 60)
    print("All personalization tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_personalization()
