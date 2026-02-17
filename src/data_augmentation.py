"""
Time-Series Data Augmentation for EEG

Implements augmentation techniques specifically designed for time-series EEG data
to improve model generalization with small datasets.

Based on:
- "Electroencephalographic Signal Data Augmentation Based on Improved GAN" (2024)
- "Data augmentation for time series classification" (TorchAudio)

Augmentations:
- TimeWarp: Speed up/slow down temporal patterns
- MagnitudeWarp: Scale amplitudes smoothly
- TimeShift: Shift signal in time
- AddGaussianNoise: Add small random noise
- ChannelDropout: Randomly drop channels

Author: Amaar Chughtai
Date: February 2026
"""

import numpy as np
import torch
from scipy.interpolate import CubicSpline


class TimeWarp:
    """
    Warp the time axis by changing the speed of the signal.

    This simulates natural variations in oscillation frequency.
    """

    def __init__(self, sigma: float = 0.2):
        """
        Args:
            sigma: Standard deviation of warping strength
        """
        self.sigma = sigma

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Args:
            x: EEG data (n_channels, n_samples)

        Returns:
            warped: Time-warped EEG (n_channels, n_samples)
        """
        n_channels, n_samples = x.shape

        # Create smooth warping curve
        orig_steps = np.arange(n_samples)

        # Random warping: sample random timesteps and interpolate
        n_knots = 5  # Number of control points
        knot_indices = np.linspace(0, n_samples - 1, n_knots)
        knot_values = knot_indices + np.random.randn(n_knots) * self.sigma * n_samples / n_knots

        # Ensure monotonicity (no time reversals)
        knot_values = np.sort(knot_values)
        knot_values[0] = 0
        knot_values[-1] = n_samples - 1

        # Cubic spline interpolation
        warper = CubicSpline(knot_indices, knot_values)
        warped_steps = warper(orig_steps)

        # Clip to valid range
        warped_steps = np.clip(warped_steps, 0, n_samples - 1)

        # Interpolate each channel
        warped = np.zeros_like(x)
        for ch in range(n_channels):
            warped[ch, :] = np.interp(warped_steps, orig_steps, x[ch, :])

        return warped


class MagnitudeWarp:
    """
    Warp the magnitude (amplitude) of the signal smoothly over time.

    This simulates natural variations in signal strength.
    """

    def __init__(self, sigma: float = 0.2):
        """
        Args:
            sigma: Standard deviation of magnitude changes
        """
        self.sigma = sigma

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Args:
            x: EEG data (n_channels, n_samples)

        Returns:
            warped: Magnitude-warped EEG (n_channels, n_samples)
        """
        n_channels, n_samples = x.shape

        # Create smooth magnitude curve
        n_knots = 5
        knot_indices = np.linspace(0, n_samples - 1, n_knots)
        knot_values = 1.0 + np.random.randn(n_knots) * self.sigma

        # Ensure positive scaling
        knot_values = np.abs(knot_values)

        # Cubic spline interpolation
        warper = CubicSpline(knot_indices, knot_values)
        magnitude_curve = warper(np.arange(n_samples))

        # Apply magnitude warping
        warped = x * magnitude_curve[np.newaxis, :]

        return warped


class TimeShift:
    """
    Shift the signal in time (circular shift).

    This makes the model robust to the exact timing of oscillations.
    """

    def __init__(self, max_shift: int = 25):
        """
        Args:
            max_shift: Maximum shift in samples (±100ms at 250Hz)
        """
        self.max_shift = max_shift

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Args:
            x: EEG data (n_channels, n_samples)

        Returns:
            shifted: Time-shifted EEG (n_channels, n_samples)
        """
        shift = np.random.randint(-self.max_shift, self.max_shift + 1)
        shifted = np.roll(x, shift, axis=1)
        return shifted


class AddGaussianNoise:
    """
    Add Gaussian noise to simulate measurement noise.
    """

    def __init__(self, std: float = 0.05):
        """
        Args:
            std: Standard deviation of noise (relative to signal)
        """
        self.std = std

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Args:
            x: EEG data (n_channels, n_samples)

        Returns:
            noisy: EEG with added noise (n_channels, n_samples)
        """
        noise = np.random.randn(*x.shape) * self.std * x.std()
        noisy = x + noise
        return noisy


class ChannelDropout:
    """
    Randomly drop (zero out) one or more channels.

    This makes the model robust to missing channels or artifacts.
    """

    def __init__(self, p: float = 0.1):
        """
        Args:
            p: Probability of dropping each channel
        """
        self.p = p

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Args:
            x: EEG data (n_channels, n_samples)

        Returns:
            dropped: EEG with channels dropped (n_channels, n_samples)
        """
        n_channels = x.shape[0]
        dropped = x.copy()

        for ch in range(n_channels):
            if np.random.rand() < self.p:
                dropped[ch, :] = 0.0

        return dropped


class Compose:
    """
    Compose multiple augmentations together.
    """

    def __init__(self, transforms: list):
        self.transforms = transforms

    def __call__(self, x: np.ndarray) -> np.ndarray:
        for transform in self.transforms:
            if np.random.rand() < 0.5:  # Apply each with 50% probability
                x = transform(x)
        return x


class EEGAugmentation:
    """
    Complete augmentation pipeline for EEG data.
    """

    def __init__(self,
                 time_warp: bool = True,
                 magnitude_warp: bool = True,
                 time_shift: bool = True,
                 gaussian_noise: bool = True,
                 channel_dropout: bool = True):
        """
        Args:
            time_warp: Enable time warping
            magnitude_warp: Enable magnitude warping
            time_shift: Enable time shifting
            gaussian_noise: Enable Gaussian noise
            channel_dropout: Enable channel dropout
        """
        transforms = []

        if time_warp:
            transforms.append(TimeWarp(sigma=0.2))
        if magnitude_warp:
            transforms.append(MagnitudeWarp(sigma=0.2))
        if time_shift:
            transforms.append(TimeShift(max_shift=25))
        if gaussian_noise:
            transforms.append(AddGaussianNoise(std=0.05))
        if channel_dropout:
            transforms.append(ChannelDropout(p=0.1))

        self.augment = Compose(transforms)

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Args:
            x: EEG data (n_channels, n_samples)

        Returns:
            augmented: Augmented EEG (n_channels, n_samples)
        """
        return self.augment(x)


def test_augmentation():
    """Test the augmentation pipeline."""
    print("Testing EEG Augmentation...")

    # Create synthetic EEG
    fs = 250.0
    duration = 2.0
    n_samples = int(fs * duration)
    n_channels = 7

    t = np.arange(n_samples) / fs
    eeg = np.zeros((n_channels, n_samples))

    for ch in range(n_channels):
        # Theta + gamma + noise
        theta = np.sin(2 * np.pi * 6 * t)
        gamma = 0.5 * (1 + np.sin(2 * np.pi * 6 * t)) * np.sin(2 * np.pi * 40 * t)
        noise = 0.1 * np.random.randn(n_samples)
        eeg[ch, :] = theta + gamma + noise

    print(f"✓ Original EEG shape: {eeg.shape}")
    print(f"✓ Original EEG range: [{eeg.min():.4f}, {eeg.max():.4f}]")

    # Test individual augmentations
    augmentations = {
        'TimeWarp': TimeWarp(sigma=0.2),
        'MagnitudeWarp': MagnitudeWarp(sigma=0.2),
        'TimeShift': TimeShift(max_shift=25),
        'AddGaussianNoise': AddGaussianNoise(std=0.05),
        'ChannelDropout': ChannelDropout(p=0.1)
    }

    for name, aug in augmentations.items():
        augmented = aug(eeg)
        print(f"✓ {name}: shape={augmented.shape}, range=[{augmented.min():.4f}, {augmented.max():.4f}]")

    # Test full pipeline
    pipeline = EEGAugmentation()
    augmented = pipeline(eeg)

    print(f"✓ Full pipeline: shape={augmented.shape}, range=[{augmented.min():.4f}, {augmented.max():.4f}]")

    # Test multiple augmentations
    print("\nTesting variability across 10 augmentations:")
    aug_std = []
    for i in range(10):
        aug = pipeline(eeg)
        aug_std.append(aug.std())

    print(f"✓ Mean std across augmentations: {np.mean(aug_std):.4f} ± {np.std(aug_std):.4f}")
    print("✓ Augmentation test passed!")


if __name__ == "__main__":
    test_augmentation()
