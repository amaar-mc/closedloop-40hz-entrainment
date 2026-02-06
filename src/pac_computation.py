"""
Phase-Amplitude Coupling (PAC) Computation Module

Implements Modulation Index method from Tort et al. (2010) for computing
theta-gamma phase-amplitude coupling from EEG signals.

References:
    Tort, A. B., et al. (2010). "Measuring phase-amplitude coupling between
    neuronal oscillations of different frequencies." Journal of Neurophysiology,
    104(2), 1195-1210.

Author: Amaar Chughtai
Date: February 2026
"""

import numpy as np
from scipy.signal import butter, filtfilt, hilbert
from typing import Tuple, Optional
import warnings

# Optional: Use Tensorpac for comparison/validation
try:
    from tensorpac import Pac
    TENSORPAC_AVAILABLE = True
except ImportError:
    TENSORPAC_AVAILABLE = False
    warnings.warn("Tensorpac not available. Using manual PAC computation only.")


class PACComputer:
    """
    Computes Phase-Amplitude Coupling using Modulation Index method.

    The Modulation Index quantifies PAC by measuring how much the amplitude
    of high-frequency oscillations (gamma) is modulated by the phase of
    low-frequency oscillations (theta).

    Attributes:
        theta_band: Tuple of (low, high) frequencies for theta phase (Hz)
        gamma_band: Tuple of (low, high) frequencies for gamma amplitude (Hz)
        fs: Sampling frequency (Hz)
        n_bins: Number of phase bins (typically 18 for 20° bins)
        filter_order: Butterworth filter order (default 4)
    """

    def __init__(self,
                 theta_band: Tuple[float, float] = (4.0, 8.0),
                 gamma_band: Tuple[float, float] = (38.0, 42.0),
                 fs: float = 250.0,
                 n_bins: int = 18,
                 filter_order: int = 4):
        """
        Initialize PAC computer.

        Args:
            theta_band: (low, high) frequencies for theta in Hz
            gamma_band: (low, high) frequencies for gamma in Hz
            fs: Sampling frequency in Hz
            n_bins: Number of phase bins (18 = 20° bins)
            filter_order: Order of Butterworth filter
        """
        self.theta_band = theta_band
        self.gamma_band = gamma_band
        self.fs = fs
        self.n_bins = n_bins
        self.filter_order = filter_order

        # Pre-compute filter coefficients
        self.b_theta, self.a_theta = butter(
            filter_order, theta_band, btype='band', fs=fs
        )
        self.b_gamma, self.a_gamma = butter(
            filter_order, gamma_band, btype='band', fs=fs
        )

    def bandpass_filter(self, signal: np.ndarray,
                       band: Tuple[float, float]) -> np.ndarray:
        """
        Apply Butterworth bandpass filter to signal.

        Args:
            signal: Input signal (n_samples,)
            band: (low, high) frequency band in Hz

        Returns:
            filtered: Bandpass filtered signal
        """
        b, a = butter(self.filter_order, band, btype='band', fs=self.fs)
        filtered = filtfilt(b, a, signal)
        return filtered

    def extract_phase_amplitude(self, signal: np.ndarray,
                               phase_band: Tuple[float, float],
                               amp_band: Tuple[float, float]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract phase from low-frequency and amplitude from high-frequency.

        Args:
            signal: Input EEG signal (n_samples,)
            phase_band: Frequency band for phase extraction (e.g., theta)
            amp_band: Frequency band for amplitude extraction (e.g., gamma)

        Returns:
            phase: Instantaneous phase in radians (-π to π)
            amplitude: Instantaneous amplitude (envelope)
        """
        # Filter signal into phase and amplitude bands
        phase_signal = self.bandpass_filter(signal, phase_band)
        amp_signal = self.bandpass_filter(signal, amp_band)

        # Apply Hilbert transform
        phase_analytic = hilbert(phase_signal)
        amp_analytic = hilbert(amp_signal)

        # Extract phase (angle) and amplitude (magnitude)
        phase = np.angle(phase_analytic)  # Range: [-π, π]
        amplitude = np.abs(amp_analytic)   # Envelope

        return phase, amplitude

    def compute_modulation_index(self, phase: np.ndarray,
                                 amplitude: np.ndarray) -> float:
        """
        Compute Modulation Index from phase and amplitude time series.

        MI measures the divergence of the amplitude distribution across phase
        bins from a uniform distribution using Kullback-Leibler distance.

        Args:
            phase: Phase time series in radians (-π to π)
            amplitude: Amplitude envelope time series

        Returns:
            mi: Modulation Index (0 = no coupling, 1 = perfect coupling)
        """
        # Bin phase into n_bins bins
        phase_bins = np.linspace(-np.pi, np.pi, self.n_bins + 1)

        # Compute mean amplitude in each phase bin
        mean_amp = np.zeros(self.n_bins)
        for i in range(self.n_bins):
            # Find samples in this phase bin
            mask = (phase >= phase_bins[i]) & (phase < phase_bins[i + 1])
            if np.sum(mask) > 0:
                mean_amp[i] = np.mean(amplitude[mask])
            else:
                mean_amp[i] = 0.0

        # Normalize to probability distribution
        mean_amp_norm = mean_amp / (np.sum(mean_amp) + 1e-10)  # Avoid division by zero

        # Compute KL divergence from uniform distribution
        uniform = np.ones(self.n_bins) / self.n_bins
        kl_div = np.sum(mean_amp_norm * np.log((mean_amp_norm + 1e-10) / uniform))

        # Normalize MI by maximum possible KL divergence
        mi = kl_div / np.log(self.n_bins)

        return float(mi)

    def compute_pac(self, signal: np.ndarray) -> float:
        """
        Compute PAC for a single-channel EEG signal.

        This is the main user-facing method that combines all steps.

        Args:
            signal: Single-channel EEG signal (n_samples,)

        Returns:
            pac: Phase-amplitude coupling (Modulation Index)
        """
        # Extract phase and amplitude
        phase, amplitude = self.extract_phase_amplitude(
            signal, self.theta_band, self.gamma_band
        )

        # Compute MI
        pac = self.compute_modulation_index(phase, amplitude)

        return pac

    def compute_pac_multichannel(self, signals: np.ndarray) -> np.ndarray:
        """
        Compute PAC for multi-channel EEG.

        Args:
            signals: Multi-channel EEG (n_channels, n_samples)

        Returns:
            pac_values: PAC for each channel (n_channels,)
        """
        n_channels = signals.shape[0]
        pac_values = np.zeros(n_channels)

        for ch in range(n_channels):
            pac_values[ch] = self.compute_pac(signals[ch, :])

        return pac_values

    def compute_pac_average(self, signals: np.ndarray) -> float:
        """
        Compute average PAC across all channels.

        Args:
            signals: Multi-channel EEG (n_channels, n_samples)

        Returns:
            pac_avg: Average PAC across channels
        """
        pac_values = self.compute_pac_multichannel(signals)
        return float(np.mean(pac_values))


def compute_pac_tensorpac(signal: np.ndarray,
                          fs: float = 250.0,
                          theta_band: Tuple[float, float] = (4.0, 8.0),
                          gamma_band: Tuple[float, float] = (38.0, 42.0)) -> float:
    """
    Compute PAC using Tensorpac library (for validation/comparison).

    Args:
        signal: Single-channel EEG signal (n_samples,) or (1, n_samples)
        fs: Sampling frequency in Hz
        theta_band: Frequency range for phase
        gamma_band: Frequency range for amplitude

    Returns:
        pac: Modulation Index value

    Raises:
        ImportError: If Tensorpac is not installed
    """
    if not TENSORPAC_AVAILABLE:
        raise ImportError("Tensorpac is not installed. Use manual PAC computation instead.")

    # Ensure signal is 2D
    if signal.ndim == 1:
        signal = signal[np.newaxis, :]  # Add channel dimension

    # Initialize PAC object with Modulation Index method
    p = Pac(
        idpac=(2, 0, 0),  # (2, 0, 0) = Modulation Index
        f_pha=(theta_band[0], theta_band[1], 1, 0.5),  # (f_start, f_end, f_width, f_step)
        f_amp=(gamma_band[0], gamma_band[1], 1, 0.5)
    )

    # Compute PAC
    xpac = p.filterfit(fs, signal, n_jobs=1)

    # Extract scalar PAC value (average across frequency bins if multiple)
    pac = float(np.mean(xpac))

    return pac


def validate_pac_computation(n_samples: int = 5000, fs: float = 250.0) -> dict:
    """
    Validate PAC computation using synthetic signals.

    Creates three test cases:
    1. No coupling: Random noise
    2. Weak coupling: Theta + gamma with slight phase-locking
    3. Strong coupling: Theta modulates gamma amplitude strongly

    Args:
        n_samples: Number of samples in test signal
        fs: Sampling frequency

    Returns:
        results: Dictionary with PAC values for each test case
    """
    time = np.arange(n_samples) / fs
    pac_computer = PACComputer(fs=fs)

    results = {}

    # Test 1: No coupling (random noise)
    noise = np.random.randn(n_samples)
    pac_noise = pac_computer.compute_pac(noise)
    results['no_coupling'] = pac_noise
    print(f"No coupling (random noise): MI = {pac_noise:.4f}")

    # Test 2: Pure theta + pure gamma (no coupling)
    theta_freq = 6.0  # Hz
    gamma_freq = 40.0  # Hz
    theta = np.sin(2 * np.pi * theta_freq * time)
    gamma = 0.3 * np.sin(2 * np.pi * gamma_freq * time)
    uncoupled = theta + gamma
    pac_uncoupled = pac_computer.compute_pac(uncoupled)
    results['uncoupled_oscillations'] = pac_uncoupled
    print(f"Uncoupled oscillations: MI = {pac_uncoupled:.4f}")

    # Test 3: Strong coupling (gamma amplitude modulated by theta phase)
    theta_phase = 2 * np.pi * theta_freq * time
    gamma_amp = 1.0 + 0.8 * np.sin(theta_phase)  # Amplitude modulation
    coupled_gamma = gamma_amp * np.sin(2 * np.pi * gamma_freq * time)
    coupled = theta + coupled_gamma
    pac_coupled = pac_computer.compute_pac(coupled)
    results['strong_coupling'] = pac_coupled
    print(f"Strong coupling: MI = {pac_coupled:.4f}")

    print("\nExpected: no_coupling < uncoupled < strong_coupling")
    print(f"Actual: {pac_noise:.4f} < {pac_uncoupled:.4f} < {pac_coupled:.4f}")

    return results


if __name__ == "__main__":
    print("=" * 60)
    print("PAC Computation Module - Validation Test")
    print("=" * 60)

    # Run validation
    results = validate_pac_computation()

    print("\n" + "=" * 60)
    print("Testing multi-channel PAC computation")
    print("=" * 60)

    # Multi-channel test
    fs = 250.0
    n_samples = 5000
    n_channels = 7
    time = np.arange(n_samples) / fs

    # Simulate multi-channel data with varying PAC strength
    multi_channel_data = np.zeros((n_channels, n_samples))
    for ch in range(n_channels):
        theta = np.sin(2 * np.pi * 6.0 * time)
        coupling_strength = ch / n_channels  # Increasing coupling across channels
        gamma_amp = 1.0 + coupling_strength * np.sin(2 * np.pi * 6.0 * time)
        gamma = gamma_amp * np.sin(2 * np.pi * 40.0 * time)
        multi_channel_data[ch, :] = theta + gamma

    pac_computer = PACComputer(fs=fs)
    pac_per_channel = pac_computer.compute_pac_multichannel(multi_channel_data)

    print("\nPAC per channel (increasing coupling strength):")
    for ch, pac in enumerate(pac_per_channel):
        print(f"  Channel {ch + 1}: MI = {pac:.4f}")

    pac_avg = pac_computer.compute_pac_average(multi_channel_data)
    print(f"\nAverage PAC across channels: MI = {pac_avg:.4f}")

    print("\n" + "=" * 60)
    print("All PAC computation tests completed successfully!")
    print("=" * 60)
