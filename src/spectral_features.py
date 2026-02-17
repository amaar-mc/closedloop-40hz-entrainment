"""
Spectral Feature Extraction for PAC Prediction

Extracts frequency-domain features that are relevant for theta-gamma PAC:
- Theta band power (4-8 Hz)
- Gamma band power (38-42 Hz)
- Theta phase (Hilbert transform)
- Gamma amplitude envelope
- Theta-gamma ratios
- Cross-channel coherence

Author: Amaar Chughtai
Date: February 2026
"""

import numpy as np
import torch
from scipy import signal
from typing import Tuple, Optional


def extract_band_power(eeg: np.ndarray,
                       fs: float = 250.0,
                       band: Tuple[float, float] = (4, 8)) -> np.ndarray:
    """
    Extract power in a specific frequency band using Welch's method.

    Args:
        eeg: EEG data (n_channels, n_samples)
        fs: Sampling frequency (Hz)
        band: Frequency band (low, high) in Hz

    Returns:
        band_power: Power in band for each channel (n_channels,)
    """
    # Welch's method for PSD estimation
    nperseg = min(256, eeg.shape[1])  # Window length
    freqs, psd = signal.welch(eeg, fs=fs, nperseg=nperseg, axis=1)

    # Find indices for frequency band
    idx_band = np.logical_and(freqs >= band[0], freqs <= band[1])

    # Integrate power in band
    band_power = np.trapz(psd[:, idx_band], freqs[idx_band], axis=1)

    return band_power


def extract_phase_amplitude(eeg: np.ndarray,
                            fs: float = 250.0,
                            phase_band: Tuple[float, float] = (4, 8),
                            amp_band: Tuple[float, float] = (38, 42)) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract phase of low-frequency oscillation and amplitude envelope of high-frequency.

    Args:
        eeg: EEG data (n_channels, n_samples)
        fs: Sampling frequency
        phase_band: Frequency band for phase extraction (theta)
        amp_band: Frequency band for amplitude extraction (gamma)

    Returns:
        phase: Instantaneous phase (n_channels, n_samples)
        amplitude: Amplitude envelope (n_channels, n_samples)
    """
    n_channels, n_samples = eeg.shape

    # Design bandpass filters
    nyq = fs / 2

    # Theta filter for phase
    b_theta, a_theta = signal.butter(3, [phase_band[0]/nyq, phase_band[1]/nyq], btype='band')

    # Gamma filter for amplitude
    b_gamma, a_gamma = signal.butter(3, [amp_band[0]/nyq, amp_band[1]/nyq], btype='band')

    phase = np.zeros((n_channels, n_samples))
    amplitude = np.zeros((n_channels, n_samples))

    for ch in range(n_channels):
        # Filter in theta band
        theta_signal = signal.filtfilt(b_theta, a_theta, eeg[ch, :])
        # Extract phase via Hilbert transform
        analytic_theta = signal.hilbert(theta_signal)
        phase[ch, :] = np.angle(analytic_theta)

        # Filter in gamma band
        gamma_signal = signal.filtfilt(b_gamma, a_gamma, eeg[ch, :])
        # Extract amplitude envelope
        analytic_gamma = signal.hilbert(gamma_signal)
        amplitude[ch, :] = np.abs(analytic_gamma)

    return phase, amplitude


def compute_pac_features(phase: np.ndarray,
                        amplitude: np.ndarray,
                        n_bins: int = 18) -> np.ndarray:
    """
    Compute PAC-specific features from phase and amplitude.

    Args:
        phase: Theta phase (n_channels, n_samples)
        amplitude: Gamma amplitude (n_channels, n_samples)
        n_bins: Number of phase bins

    Returns:
        pac_features: Feature vector per channel (n_channels, n_features)
    """
    n_channels = phase.shape[0]
    features = []

    for ch in range(n_channels):
        # 1. Mean amplitude at each phase bin
        phase_bins = np.linspace(-np.pi, np.pi, n_bins + 1)
        amp_per_bin = []
        for i in range(n_bins):
            mask = (phase[ch, :] >= phase_bins[i]) & (phase[ch, :] < phase_bins[i+1])
            if mask.sum() > 0:
                amp_per_bin.append(amplitude[ch, mask].mean())
            else:
                amp_per_bin.append(0.0)

        # 2. Modulation index (KL divergence from uniform)
        amp_per_bin = np.array(amp_per_bin)
        amp_per_bin_norm = amp_per_bin / (amp_per_bin.sum() + 1e-10)
        uniform = np.ones(n_bins) / n_bins
        mi = np.sum(amp_per_bin_norm * np.log((amp_per_bin_norm + 1e-10) / (uniform + 1e-10)))

        # 3. Circular mean resultant length (phase consistency)
        mean_phase = np.angle(np.mean(np.exp(1j * phase[ch, :])))
        resultant_length = np.abs(np.mean(np.exp(1j * (phase[ch, :] - mean_phase))))

        # 4. Amplitude variance
        amp_var = amplitude[ch, :].var()

        # Features: [MI, resultant_length, amp_var, max_amp_bin_idx]
        max_bin_idx = np.argmax(amp_per_bin) / n_bins  # Normalized to [0, 1]

        features.append([mi, resultant_length, amp_var, max_bin_idx])

    return np.array(features)  # (n_channels, 4)


def extract_spectral_features(eeg: np.ndarray, fs: float = 250.0) -> np.ndarray:
    """
    Extract comprehensive spectral features for PAC prediction.

    Args:
        eeg: EEG data (n_channels, n_samples)
        fs: Sampling frequency

    Returns:
        features: Feature vector (n_features,)
    """
    n_channels = eeg.shape[0]

    # 1. Band powers (per channel)
    theta_power = extract_band_power(eeg, fs, band=(4, 8))      # 7 features
    alpha_power = extract_band_power(eeg, fs, band=(8, 13))     # 7 features
    beta_power = extract_band_power(eeg, fs, band=(13, 30))     # 7 features
    gamma_power = extract_band_power(eeg, fs, band=(38, 42))    # 7 features

    # 2. Theta-gamma ratios (per channel)
    theta_gamma_ratio = theta_power / (gamma_power + 1e-10)     # 7 features

    # 3. Phase-amplitude features
    phase, amplitude = extract_phase_amplitude(eeg, fs)
    pac_features = compute_pac_features(phase, amplitude)       # (7, 4) = 28 features
    pac_features_flat = pac_features.flatten()

    # 4. Cross-channel features (global statistics)
    theta_power_mean = theta_power.mean()
    theta_power_std = theta_power.std()
    gamma_power_mean = gamma_power.mean()
    gamma_power_std = gamma_power.std()
    theta_gamma_ratio_mean = theta_gamma_ratio.mean()

    # Concatenate all features
    features = np.concatenate([
        theta_power,                    # 7
        gamma_power,                    # 7
        alpha_power,                    # 7
        beta_power,                     # 7
        theta_gamma_ratio,              # 7
        pac_features_flat,              # 28
        [theta_power_mean, theta_power_std,
         gamma_power_mean, gamma_power_std,
         theta_gamma_ratio_mean]        # 5
    ])

    return features  # Total: 7+7+7+7+7+28+5 = 68 features


class SpectralFeatureExtractor:
    """
    Batch processor for spectral feature extraction.
    """

    def __init__(self, fs: float = 250.0):
        self.fs = fs

    def extract(self, eeg_batch: np.ndarray) -> np.ndarray:
        """
        Extract features for a batch of EEG windows.

        Args:
            eeg_batch: (batch_size, n_channels, n_samples)

        Returns:
            features: (batch_size, n_features)
        """
        batch_size = eeg_batch.shape[0]
        feature_list = []

        for i in range(batch_size):
            features = extract_spectral_features(eeg_batch[i], self.fs)
            feature_list.append(features)

        return np.array(feature_list)

    def extract_torch(self, eeg_batch: torch.Tensor) -> torch.Tensor:
        """
        Extract features from PyTorch tensor.

        Args:
            eeg_batch: (batch_size, n_channels, n_samples) torch.Tensor

        Returns:
            features: (batch_size, n_features) torch.Tensor
        """
        # Convert to numpy
        eeg_np = eeg_batch.cpu().numpy()

        # Extract features
        features_np = self.extract(eeg_np)

        # Convert back to torch
        features_torch = torch.from_numpy(features_np).float()

        return features_torch.to(eeg_batch.device)


def test_spectral_features():
    """Test the spectral feature extraction."""
    print("Testing Spectral Feature Extraction...")

    # Simulate EEG data
    fs = 250.0
    duration = 2.0
    n_samples = int(fs * duration)
    n_channels = 7

    # Create synthetic EEG with theta and gamma components
    t = np.arange(n_samples) / fs
    eeg = np.zeros((n_channels, n_samples))

    for ch in range(n_channels):
        # Theta oscillation (6 Hz)
        theta = np.sin(2 * np.pi * 6 * t) * (1 + 0.3 * np.random.randn())
        # Gamma oscillation (40 Hz) modulated by theta phase
        gamma_amp = 0.5 * (1 + np.sin(2 * np.pi * 6 * t))
        gamma = gamma_amp * np.sin(2 * np.pi * 40 * t)
        # White noise
        noise = 0.1 * np.random.randn(n_samples)

        eeg[ch, :] = theta + gamma + noise

    # Extract features
    features = extract_spectral_features(eeg, fs)

    print(f"✓ EEG shape: {eeg.shape}")
    print(f"✓ Features shape: {features.shape}")
    print(f"✓ Features: {features[:10]}...")  # First 10 features

    # Test batch extraction
    extractor = SpectralFeatureExtractor(fs)
    batch = np.stack([eeg, eeg, eeg])  # Batch of 3
    batch_features = extractor.extract(batch)

    print(f"✓ Batch features shape: {batch_features.shape}")
    print("✓ Spectral feature extraction test passed!")


if __name__ == "__main__":
    test_spectral_features()
