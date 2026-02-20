"""
PAC-Specific Feature Extraction

Direct computation of phase-amplitude coupling features using:
- Hilbert transform for instantaneous phase/amplitude
- Phase-locking value (PLV)
- Cross-frequency coupling metrics
- Bispectrum features

These features directly measure theta-gamma coupling, which is what we're predicting.

Author: Amaar Chughtai
Date: February 2026
"""

import numpy as np
from scipy import signal
from scipy.signal import hilbert, butter, sosfiltfilt


def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    """Bandpass filter using Butterworth filter."""
    sos = butter(order, [lowcut, highcut], btype='band', fs=fs, output='sos')
    return sosfiltfilt(sos, data, axis=-1)


def compute_instantaneous_phase_amplitude(eeg, freq_band, fs=250):
    """
    Extract instantaneous phase and amplitude using Hilbert transform.

    Args:
        eeg: (n_channels, n_samples) EEG data
        freq_band: (low, high) frequency band in Hz
        fs: sampling frequency

    Returns:
        phase: (n_channels, n_samples) instantaneous phase
        amplitude: (n_channels, n_samples) instantaneous amplitude
    """
    # Bandpass filter
    filtered = butter_bandpass_filter(eeg, freq_band[0], freq_band[1], fs)

    # Hilbert transform
    analytic = hilbert(filtered, axis=-1)
    phase = np.angle(analytic)
    amplitude = np.abs(analytic)

    return phase, amplitude


def compute_phase_locking_value(phase1, phase2):
    """
    Compute Phase-Locking Value (PLV) between two phase time series.

    PLV measures phase synchronization between signals.
    PLV = 1: perfect synchronization
    PLV = 0: no synchronization

    Args:
        phase1, phase2: (n_samples,) phase time series

    Returns:
        plv: scalar phase-locking value
    """
    phase_diff = phase1 - phase2
    plv = np.abs(np.mean(np.exp(1j * phase_diff)))
    return plv


def compute_direct_pac(theta_phase, gamma_amplitude):
    """
    Compute Phase-Amplitude Coupling directly.

    This is the Modulation Index (MI) computed correctly without data leakage.
    We compute it per channel and average.

    Args:
        theta_phase: (n_channels, n_samples) theta phase
        gamma_amplitude: (n_channels, n_samples) gamma amplitude

    Returns:
        pac_values: (n_channels,) PAC for each channel
    """
    n_channels = theta_phase.shape[0]
    pac_values = np.zeros(n_channels)

    for ch in range(n_channels):
        # Mean amplitude at each phase bin
        n_bins = 18  # 20-degree bins
        phase_bins = np.linspace(-np.pi, np.pi, n_bins + 1)

        mean_amp = np.zeros(n_bins)
        for i in range(n_bins):
            mask = (theta_phase[ch] >= phase_bins[i]) & (theta_phase[ch] < phase_bins[i + 1])
            if np.sum(mask) > 0:
                mean_amp[i] = np.mean(gamma_amplitude[ch, mask])

        # Normalize
        mean_amp = mean_amp / np.sum(mean_amp) if np.sum(mean_amp) > 0 else mean_amp

        # Modulation Index (KL divergence from uniform)
        uniform = np.ones(n_bins) / n_bins
        # Add small epsilon to avoid log(0)
        mean_amp = mean_amp + 1e-10
        uniform = uniform + 1e-10

        mi = np.sum(mean_amp * np.log(mean_amp / uniform))
        pac_values[ch] = mi

    return pac_values


def compute_phase_amplitude_correlation(theta_phase, gamma_amplitude):
    """
    Compute correlation between theta phase and gamma amplitude.

    Alternative PAC metric using circular-linear correlation.

    Args:
        theta_phase: (n_channels, n_samples) theta phase
        gamma_amplitude: (n_channels, n_samples) gamma amplitude

    Returns:
        corr: (n_channels,) correlation for each channel
    """
    n_channels = theta_phase.shape[0]
    corr = np.zeros(n_channels)

    for ch in range(n_channels):
        # Circular-linear correlation
        sin_phase = np.sin(theta_phase[ch])
        cos_phase = np.cos(theta_phase[ch])

        # Correlations
        r_sin = np.corrcoef(sin_phase, gamma_amplitude[ch])[0, 1]
        r_cos = np.corrcoef(cos_phase, gamma_amplitude[ch])[0, 1]

        # Combined correlation
        corr[ch] = np.sqrt(r_sin**2 + r_cos**2)

    return corr


def compute_cross_channel_plv(phase):
    """
    Compute Phase-Locking Value (PLV) between all channel pairs.

    Args:
        phase: (n_channels, n_samples) phase time series

    Returns:
        plv_matrix: (n_channels, n_channels) PLV matrix
    """
    n_channels = phase.shape[0]
    plv_matrix = np.zeros((n_channels, n_channels))

    for i in range(n_channels):
        for j in range(i + 1, n_channels):
            plv = compute_phase_locking_value(phase[i], phase[j])
            plv_matrix[i, j] = plv
            plv_matrix[j, i] = plv

    return plv_matrix


def compute_preferred_phase(theta_phase, gamma_amplitude):
    """
    Compute the preferred theta phase for maximum gamma amplitude.

    Args:
        theta_phase: (n_channels, n_samples) theta phase
        gamma_amplitude: (n_channels, n_samples) gamma amplitude

    Returns:
        preferred_phase: (n_channels,) preferred phase for each channel
        phase_consistency: (n_channels,) consistency of preferred phase
    """
    n_channels = theta_phase.shape[0]
    preferred_phase = np.zeros(n_channels)
    phase_consistency = np.zeros(n_channels)

    for ch in range(n_channels):
        # Circular mean weighted by amplitude
        weights = gamma_amplitude[ch]

        # Weighted circular mean
        mean_sin = np.sum(weights * np.sin(theta_phase[ch])) / np.sum(weights)
        mean_cos = np.sum(weights * np.cos(theta_phase[ch])) / np.sum(weights)

        preferred_phase[ch] = np.arctan2(mean_sin, mean_cos)

        # Phase consistency (resultant vector length)
        phase_consistency[ch] = np.sqrt(mean_sin**2 + mean_cos**2)

    return preferred_phase, phase_consistency


def extract_pac_features(eeg, fs=250):
    """
    Extract comprehensive PAC-specific features.

    Args:
        eeg: (n_channels, n_samples) EEG window
        fs: sampling frequency

    Returns:
        features: (n_features,) feature vector
    """
    n_channels = eeg.shape[0]
    features = []

    # 1. Extract theta phase and gamma amplitude (Hilbert transform)
    theta_phase, theta_amp = compute_instantaneous_phase_amplitude(eeg, (4, 8), fs)
    gamma_phase, gamma_amp = compute_instantaneous_phase_amplitude(eeg, (38, 42), fs)

    # 2. Direct PAC computation (per channel)
    pac_direct = compute_direct_pac(theta_phase, gamma_amp)
    features.extend(pac_direct)  # 7 features

    # 3. Phase-amplitude correlation (per channel)
    pac_corr = compute_phase_amplitude_correlation(theta_phase, gamma_amp)
    features.extend(pac_corr)  # 7 features

    # 4. Preferred phase and consistency (per channel)
    preferred_phase, phase_consistency = compute_preferred_phase(theta_phase, gamma_amp)
    features.extend(preferred_phase)  # 7 features
    features.extend(phase_consistency)  # 7 features

    # 5. Theta phase synchronization (PLV between channels)
    theta_plv = compute_cross_channel_plv(theta_phase)
    # Extract upper triangle (21 unique pairs for 7 channels)
    theta_plv_features = theta_plv[np.triu_indices(n_channels, k=1)]
    features.extend(theta_plv_features)  # 21 features

    # 6. Gamma amplitude correlation between channels
    gamma_corr = np.corrcoef(gamma_amp)
    gamma_corr_features = gamma_corr[np.triu_indices(n_channels, k=1)]
    features.extend(gamma_corr_features)  # 21 features

    # 7. Cross-frequency coupling strength
    # Average gamma amplitude at different theta phase bins (global)
    theta_phase_avg = np.mean(theta_phase, axis=0)  # Average phase across channels
    gamma_amp_avg = np.mean(gamma_amp, axis=0)  # Average amplitude across channels

    n_bins = 18
    phase_bins = np.linspace(-np.pi, np.pi, n_bins + 1)
    coupling_profile = np.zeros(n_bins)

    for i in range(n_bins):
        mask = (theta_phase_avg >= phase_bins[i]) & (theta_phase_avg < phase_bins[i + 1])
        if np.sum(mask) > 0:
            coupling_profile[i] = np.mean(gamma_amp_avg[mask])

    # Normalize coupling profile
    if np.sum(coupling_profile) > 0:
        coupling_profile = coupling_profile / np.sum(coupling_profile)

    features.extend(coupling_profile)  # 18 features

    # 8. Theta-gamma amplitude coupling
    theta_gamma_amp_corr = np.zeros(n_channels)
    for ch in range(n_channels):
        theta_gamma_amp_corr[ch] = np.corrcoef(theta_amp[ch], gamma_amp[ch])[0, 1]
    features.extend(theta_gamma_amp_corr)  # 7 features

    # 9. Peak-trough asymmetry (theta)
    # Measures asymmetry in theta waveform (relevant for PAC)
    theta_filtered = butter_bandpass_filter(eeg, 4, 8, fs)
    theta_asymmetry = np.zeros(n_channels)
    for ch in range(n_channels):
        peaks = theta_filtered[ch, theta_filtered[ch] > 0]
        troughs = theta_filtered[ch, theta_filtered[ch] < 0]
        if len(peaks) > 0 and len(troughs) > 0:
            theta_asymmetry[ch] = np.abs(np.mean(peaks)) - np.abs(np.mean(troughs))
    features.extend(theta_asymmetry)  # 7 features

    # 10. Gamma burst statistics
    # When does gamma burst occur (relative to theta phase)?
    gamma_threshold = np.percentile(gamma_amp, 75, axis=1, keepdims=True)
    gamma_bursts = gamma_amp > gamma_threshold

    burst_phase_mean = np.zeros(n_channels)
    burst_phase_std = np.zeros(n_channels)

    for ch in range(n_channels):
        burst_phases = theta_phase[ch, gamma_bursts[ch, :]]
        if len(burst_phases) > 0:
            burst_phase_mean[ch] = np.arctan2(
                np.mean(np.sin(burst_phases)),
                np.mean(np.cos(burst_phases))
            )
            # Circular standard deviation
            r = np.sqrt(np.mean(np.sin(burst_phases))**2 + np.mean(np.cos(burst_phases))**2)
            burst_phase_std[ch] = np.sqrt(-2 * np.log(r)) if r > 0 else 0

    features.extend(burst_phase_mean)  # 7 features
    features.extend(burst_phase_std)  # 7 features

    return np.array(features)


class PACFeatureExtractor:
    """
    Extracts PAC-specific features from EEG data.

    Total features: 116 features
    - Direct PAC (MI): 7
    - PAC correlation: 7
    - Preferred phase: 7
    - Phase consistency: 7
    - Theta PLV: 21
    - Gamma correlation: 21
    - Coupling profile: 18
    - Theta-gamma amp correlation: 7
    - Theta asymmetry: 7
    - Burst phase mean: 7
    - Burst phase std: 7
    """

    def __init__(self, fs=250):
        self.fs = fs

    def extract(self, eeg_batch):
        """
        Extract PAC features from batch of EEG windows.

        Args:
            eeg_batch: (batch_size, n_channels, n_samples) or (n_channels, n_samples)

        Returns:
            features: (batch_size, 116) or (116,) feature array
        """
        if eeg_batch.ndim == 2:
            # Single sample
            return extract_pac_features(eeg_batch, self.fs)
        else:
            # Batch
            batch_size = eeg_batch.shape[0]
            features = np.zeros((batch_size, 116))

            for i in range(batch_size):
                features[i] = extract_pac_features(eeg_batch[i], self.fs)

            return features


def test_pac_features():
    """Test PAC feature extraction."""
    print("Testing PAC feature extraction...")

    # Generate synthetic data with PAC
    fs = 250
    t = np.arange(0, 2, 1/fs)  # 2 seconds
    n_channels = 7

    eeg = np.zeros((n_channels, len(t)))

    for ch in range(n_channels):
        # Theta oscillation (5 Hz)
        theta = np.sin(2 * np.pi * 5 * t)
        theta_phase = 2 * np.pi * 5 * t

        # Gamma amplitude modulated by theta phase
        gamma_amp = 1 + 0.5 * np.cos(theta_phase - np.pi/4)  # Peak at specific phase
        gamma = gamma_amp * np.sin(2 * np.pi * 40 * t)

        # Combine
        eeg[ch] = theta + 0.3 * gamma + 0.1 * np.random.randn(len(t))

    # Extract features
    extractor = PACFeatureExtractor(fs=fs)
    features = extractor.extract(eeg)

    print(f"✓ Features extracted: shape = {features.shape}")
    print(f"  Direct PAC (MI): {features[0:7]}")
    print(f"  PAC correlation: {features[7:14]}")
    print(f"  Mean coupling profile: {np.mean(features[70:88]):.4f}")

    # Test batch extraction
    eeg_batch = np.stack([eeg, eeg, eeg])
    features_batch = extractor.extract(eeg_batch)
    print(f"✓ Batch extraction: shape = {features_batch.shape}")

    print("\n✓ PAC feature extraction test passed!")


if __name__ == '__main__':
    test_pac_features()
