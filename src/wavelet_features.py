"""
Wavelet Feature Extraction for Enhanced PAC Prediction

Extracts time-frequency features using wavelets to capture phase-amplitude coupling
more effectively than traditional spectral features.

Features include:
- Continuous Wavelet Transform (CWT) energy in theta/gamma bands
- Wavelet Packet Decomposition (WPD) sub-band energies
- Cross-frequency coupling from wavelet coefficients
- Phase synchronization index
- Wavelet entropy

These features complement spectral features by capturing transient time-frequency
relationships that are critical for PAC dynamics.

Author: Amaar Chughtai
Date: February 2026
"""

import numpy as np
import pywt
from scipy import signal
from typing import Tuple, List


def compute_cwt_features(eeg: np.ndarray,
                         fs: float = 250.0,
                         scales: np.ndarray = None) -> np.ndarray:
    """
    Compute Continuous Wavelet Transform features for theta-gamma PAC.

    Args:
        eeg: EEG data (n_channels, n_samples)
        fs: Sampling frequency
        scales: CWT scales (default: covers 4-50 Hz)

    Returns:
        cwt_features: (n_channels, n_features)
    """
    n_channels = eeg.shape[0]

    # Define scales to cover theta (4-8 Hz) and gamma (38-42 Hz)
    if scales is None:
        # Morlet wavelet: f = fc / (scale * dt), where fc ≈ 1.0 for Morlet
        dt = 1.0 / fs
        freqs_of_interest = np.concatenate([
            np.linspace(4, 8, 5),    # Theta: 5 frequencies
            np.linspace(38, 42, 5)   # Gamma: 5 frequencies
        ])
        fc = 1.0  # Center frequency for Morlet wavelet
        scales = fc / (freqs_of_interest * dt)

    features = []

    for ch in range(n_channels):
        # Compute CWT using Morlet wavelet
        coef, _ = pywt.cwt(eeg[ch, :], scales, 'morl', sampling_period=1.0/fs)

        # Split into theta and gamma bands
        theta_coef = coef[:5, :]   # First 5 scales (theta)
        gamma_coef = coef[5:, :]   # Last 5 scales (gamma)

        # Feature 1: Mean theta energy
        theta_energy = np.mean(np.abs(theta_coef) ** 2)

        # Feature 2: Mean gamma energy
        gamma_energy = np.mean(np.abs(gamma_coef) ** 2)

        # Feature 3: Theta-gamma energy ratio
        tg_ratio = theta_energy / (gamma_energy + 1e-10)

        # Feature 4: Cross-frequency coupling strength
        # Compute correlation between theta envelope and gamma power
        theta_envelope = np.mean(np.abs(theta_coef), axis=0)
        gamma_power = np.mean(np.abs(gamma_coef) ** 2, axis=0)
        cfc_corr = np.corrcoef(theta_envelope, gamma_power)[0, 1]

        # Feature 5: Wavelet entropy (measure of signal complexity)
        # Normalized Shannon entropy of squared coefficients
        coef_energy = np.abs(coef) ** 2
        coef_prob = coef_energy / (coef_energy.sum() + 1e-10)
        wavelet_entropy = -np.sum(coef_prob * np.log(coef_prob + 1e-10))
        wavelet_entropy_norm = wavelet_entropy / np.log(coef_prob.size)

        features.append([
            theta_energy,
            gamma_energy,
            tg_ratio,
            cfc_corr if not np.isnan(cfc_corr) else 0.0,
            wavelet_entropy_norm
        ])

    return np.array(features)  # (n_channels, 5)


def compute_wpd_features(eeg: np.ndarray,
                        wavelet: str = 'db4',
                        level: int = 5) -> np.ndarray:
    """
    Compute Wavelet Packet Decomposition features.

    WPD provides a complete decomposition of the signal into sub-bands,
    allowing capture of energy distribution across multiple frequency scales.

    Args:
        eeg: EEG data (n_channels, n_samples)
        wavelet: Wavelet type (default: Daubechies 4)
        level: Decomposition level

    Returns:
        wpd_features: (n_channels, n_features)
    """
    n_channels = eeg.shape[0]
    features = []

    for ch in range(n_channels):
        # Perform WPD
        wp = pywt.WaveletPacket(data=eeg[ch, :], wavelet=wavelet, maxlevel=level)

        # Extract nodes at the maximum level
        nodes = [node.path for node in wp.get_level(level, 'freq')]

        # Compute energy in each sub-band
        energies = []
        for node_path in nodes:
            node = wp[node_path]
            energy = np.sum(node.data ** 2)
            energies.append(energy)

        energies = np.array(energies)
        total_energy = energies.sum() + 1e-10

        # Feature 1-4: Energy in specific sub-bands (normalized)
        # At level 5, we have 32 sub-bands. Select bands of interest:
        # Low freq (theta-like): nodes 0-4
        # Mid freq (alpha/beta): nodes 5-15
        # High freq (gamma-like): nodes 16-31

        theta_like_energy = energies[:5].sum() / total_energy
        mid_freq_energy = energies[5:16].sum() / total_energy
        gamma_like_energy = energies[16:].sum() / total_energy

        # Feature 4: Energy distribution entropy
        energy_prob = energies / total_energy
        energy_entropy = -np.sum(energy_prob * np.log(energy_prob + 1e-10))
        energy_entropy_norm = energy_entropy / np.log(len(energies))

        features.append([
            theta_like_energy,
            mid_freq_energy,
            gamma_like_energy,
            energy_entropy_norm
        ])

    return np.array(features)  # (n_channels, 4)


def compute_phase_sync_index(eeg: np.ndarray,
                             fs: float = 250.0,
                             theta_band: Tuple[float, float] = (4, 8),
                             gamma_band: Tuple[float, float] = (38, 42)) -> float:
    """
    Compute phase synchronization index between theta and gamma bands.

    Measures how consistently gamma amplitude is coupled to theta phase
    across channels.

    Args:
        eeg: EEG data (n_channels, n_samples)
        fs: Sampling frequency
        theta_band: Theta frequency band
        gamma_band: Gamma frequency band

    Returns:
        psi: Phase synchronization index (scalar)
    """
    n_channels = eeg.shape[0]

    # Design filters
    nyq = fs / 2
    b_theta, a_theta = signal.butter(3, [theta_band[0]/nyq, theta_band[1]/nyq], btype='band')
    b_gamma, a_gamma = signal.butter(3, [gamma_band[0]/nyq, gamma_band[1]/nyq], btype='band')

    # Extract phase and amplitude for each channel
    theta_phases = []
    gamma_amps = []

    for ch in range(n_channels):
        # Theta phase
        theta_sig = signal.filtfilt(b_theta, a_theta, eeg[ch, :])
        analytic_theta = signal.hilbert(theta_sig)
        theta_phase = np.angle(analytic_theta)
        theta_phases.append(theta_phase)

        # Gamma amplitude
        gamma_sig = signal.filtfilt(b_gamma, a_gamma, eeg[ch, :])
        analytic_gamma = signal.hilbert(gamma_sig)
        gamma_amp = np.abs(analytic_gamma)
        gamma_amps.append(gamma_amp)

    theta_phases = np.array(theta_phases)  # (n_channels, n_samples)
    gamma_amps = np.array(gamma_amps)

    # Compute mean phase and amplitude across channels
    mean_theta_phase = np.angle(np.mean(np.exp(1j * theta_phases), axis=0))
    mean_gamma_amp = np.mean(gamma_amps, axis=0)

    # Compute phase-amplitude coupling strength
    # Using circular correlation
    n_bins = 18
    phase_bins = np.linspace(-np.pi, np.pi, n_bins + 1)
    amp_per_bin = []

    for i in range(n_bins):
        mask = (mean_theta_phase >= phase_bins[i]) & (mean_theta_phase < phase_bins[i+1])
        if mask.sum() > 0:
            amp_per_bin.append(mean_gamma_amp[mask].mean())
        else:
            amp_per_bin.append(0.0)

    amp_per_bin = np.array(amp_per_bin)

    # Phase synchronization index: circular variance of amplitude distribution
    psi = np.std(amp_per_bin) / (np.mean(amp_per_bin) + 1e-10)

    return float(psi)


def extract_wavelet_features(eeg: np.ndarray, fs: float = 250.0) -> np.ndarray:
    """
    Extract comprehensive wavelet-based features for PAC prediction.

    Args:
        eeg: EEG data (n_channels, n_samples)
        fs: Sampling frequency

    Returns:
        features: Feature vector (n_features,)
    """
    n_channels = eeg.shape[0]

    # 1. CWT features (per channel)
    cwt_features = compute_cwt_features(eeg, fs)  # (7, 5) = 35 features
    cwt_features_flat = cwt_features.flatten()

    # 2. WPD features (per channel)
    wpd_features = compute_wpd_features(eeg)  # (7, 4) = 28 features
    wpd_features_flat = wpd_features.flatten()

    # 3. Global phase synchronization index
    psi = compute_phase_sync_index(eeg, fs)  # 1 feature

    # 4. Cross-channel statistics
    cwt_mean = cwt_features.mean(axis=0)  # 5 features (mean across channels)
    cwt_std = cwt_features.std(axis=0)    # 5 features (std across channels)

    # Concatenate all features
    features = np.concatenate([
        cwt_features_flat,      # 35
        wpd_features_flat,      # 28
        [psi],                  # 1
        cwt_mean,               # 5
        cwt_std                 # 5
    ])

    return features  # Total: 35 + 28 + 1 + 5 + 5 = 74 features


class WaveletFeatureExtractor:
    """
    Batch processor for wavelet feature extraction.
    """

    def __init__(self, fs: float = 250.0):
        self.fs = fs

    def extract(self, eeg_batch: np.ndarray) -> np.ndarray:
        """
        Extract wavelet features for a batch of EEG windows.

        Args:
            eeg_batch: (batch_size, n_channels, n_samples)

        Returns:
            features: (batch_size, n_features)
        """
        batch_size = eeg_batch.shape[0]
        feature_list = []

        for i in range(batch_size):
            features = extract_wavelet_features(eeg_batch[i], self.fs)
            feature_list.append(features)

        return np.array(feature_list)


def test_wavelet_features():
    """Test the wavelet feature extraction."""
    print("Testing Wavelet Feature Extraction...")

    # Simulate EEG data
    fs = 250.0
    duration = 2.0
    n_samples = int(fs * duration)
    n_channels = 7

    # Create synthetic EEG with theta-gamma PAC
    t = np.arange(n_samples) / fs
    eeg = np.zeros((n_channels, n_samples))

    for ch in range(n_channels):
        # Theta oscillation (6 Hz)
        theta = np.sin(2 * np.pi * 6 * t)
        # Gamma oscillation (40 Hz) modulated by theta phase
        gamma_amp = 0.5 * (1 + np.sin(2 * np.pi * 6 * t))
        gamma = gamma_amp * np.sin(2 * np.pi * 40 * t)
        # White noise
        noise = 0.1 * np.random.randn(n_samples)

        eeg[ch, :] = theta + gamma + noise

    # Extract features
    features = extract_wavelet_features(eeg, fs)

    print(f"✓ EEG shape: {eeg.shape}")
    print(f"✓ Wavelet features shape: {features.shape}")
    print(f"✓ Feature breakdown:")
    print(f"  - CWT features: 35 (7 channels × 5)")
    print(f"  - WPD features: 28 (7 channels × 4)")
    print(f"  - Phase sync index: 1")
    print(f"  - CWT statistics: 10 (mean + std)")
    print(f"  - Total: {features.shape[0]} features")

    # Test batch extraction
    extractor = WaveletFeatureExtractor(fs)
    batch = np.stack([eeg, eeg, eeg])
    batch_features = extractor.extract(batch)

    print(f"✓ Batch features shape: {batch_features.shape}")
    print("✓ Wavelet feature extraction test passed!")


if __name__ == "__main__":
    test_wavelet_features()
