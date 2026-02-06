"""
EEG Preprocessing Pipeline for Closed-Loop 40Hz Entrainment

Implements signal conditioning steps for OpenNeuro ds005048 dataset:
- Bandpass filtering (0.5-80 Hz, 4th-order Butterworth)
- Notch filtering (50/60 Hz powerline interference, Q=30)
- Amplitude thresholding for artifact rejection (±100 µV)
- Common average reference (CAR)
- Signal quality assessment

Note: ICA and ASR already applied by Makoto's pipeline in raw dataset.

References:
    - Makoto's EEG preprocessing pipeline
    - Butterworth filters: Oppenheim & Schafer (1989)

Author: Amaar Chughtai
Date: February 2026
"""

import numpy as np
import logging
from typing import Tuple, Optional, List
from scipy.signal import butter, filtfilt, iirnotch, freqz
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class EEGPreprocessor:
    """
    Implements EEG signal preprocessing pipeline.

    Pipeline stages:
        1. Bandpass filter (0.5-80 Hz, 4th-order Butterworth)
        2. Notch filter (50 Hz or 60 Hz for powerline, Q=30)
        3. Amplitude thresholding (artifact rejection at ±100 µV)
        4. Common average reference (CAR)
        5. Quality assessment (SNR estimation)

    Parameters:
        fs: Sampling frequency in Hz (default 250)
        hp_freq: High-pass cutoff in Hz (default 0.5)
        lp_freq: Low-pass cutoff in Hz (default 80)
        notch_freq: Notch filter frequency in Hz (50 or 60, default 50)
        notch_q: Notch filter quality factor (default 30)
        artifact_threshold: Amplitude threshold in µV for artifact rejection (default 100)
    """

    def __init__(self,
                 fs: float = 250.0,
                 hp_freq: float = 0.5,
                 lp_freq: float = 80.0,
                 notch_freq: float = 50.0,
                 notch_q: float = 30.0,
                 artifact_threshold: float = 100.0):
        """
        Initialize EEG preprocessor.

        Args:
            fs: Sampling frequency in Hz
            hp_freq: High-pass cutoff frequency (Hz)
            lp_freq: Low-pass cutoff frequency (Hz)
            notch_freq: Notch filter frequency (50 or 60 Hz)
            notch_q: Quality factor for notch filter
            artifact_threshold: Amplitude threshold in µV
        """
        self.fs = fs
        self.hp_freq = hp_freq
        self.lp_freq = lp_freq
        self.notch_freq = notch_freq
        self.notch_q = notch_q
        self.artifact_threshold = artifact_threshold

        # Precompute filter coefficients
        self._compute_filter_coefficients()

        logger.info(f"EEGPreprocessor initialized:")
        logger.info(f"  Sampling rate: {fs} Hz")
        logger.info(f"  Bandpass: {hp_freq}-{lp_freq} Hz (4th-order Butterworth)")
        logger.info(f"  Notch: {notch_freq} Hz (Q={notch_q})")
        logger.info(f"  Artifact threshold: ±{artifact_threshold} µV")

    def _compute_filter_coefficients(self):
        """Precompute filter coefficients for efficiency."""
        # Bandpass filter: 0.5-80 Hz, 4th order Butterworth
        self.b_bandpass, self.a_bandpass = butter(
            N=4,
            Wn=[self.hp_freq, self.lp_freq],
            btype='band',
            fs=self.fs
        )

        # Notch filter: 50/60 Hz
        self.b_notch, self.a_notch = iirnotch(
            w0=self.notch_freq,
            Q=self.notch_q,
            fs=self.fs
        )

        logger.debug("Filter coefficients computed and cached")

    def bandpass_filter(self, signal: np.ndarray) -> np.ndarray:
        """
        Apply bandpass filter (0.5-80 Hz, 4th-order Butterworth).

        Uses zero-phase filtering (filtfilt) for no phase distortion.

        Args:
            signal: Input signal (n_samples,) or (n_channels, n_samples)

        Returns:
            filtered: Bandpass filtered signal
        """
        if signal.ndim == 1:
            # Single channel
            filtered = filtfilt(self.b_bandpass, self.a_bandpass, signal)
        else:
            # Multi-channel
            filtered = np.zeros_like(signal)
            for ch in range(signal.shape[0]):
                filtered[ch, :] = filtfilt(self.b_bandpass, self.a_bandpass, signal[ch, :])

        return filtered

    def notch_filter(self, signal: np.ndarray) -> np.ndarray:
        """
        Apply notch filter to remove powerline interference.

        Removes 50 Hz (Europe/Asia) or 60 Hz (North America) with Q=30.

        Args:
            signal: Input signal (n_samples,) or (n_channels, n_samples)

        Returns:
            filtered: Notch filtered signal
        """
        if signal.ndim == 1:
            filtered = filtfilt(self.b_notch, self.a_notch, signal)
        else:
            filtered = np.zeros_like(signal)
            for ch in range(signal.shape[0]):
                filtered[ch, :] = filtfilt(self.b_notch, self.a_notch, signal[ch, :])

        return filtered

    def artifact_rejection(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect and mark artifact samples using amplitude thresholding.

        Marks samples exceeding ±100 µV as artifacts.

        Args:
            signal: Input signal (n_channels, n_samples)

        Returns:
            signal_clean: Signal with artifacts set to 0
            artifact_mask: Boolean mask (True = artifact)
        """
        # Compute amplitude per channel
        amplitude = np.abs(signal)

        # Create artifact mask
        artifact_mask = (amplitude > self.artifact_threshold)

        # Count artifacts
        n_artifacts = np.sum(artifact_mask)
        pct_artifacts = 100.0 * n_artifacts / signal.size
        logger.debug(f"Artifact rejection: {n_artifacts} samples ({pct_artifacts:.2f}%)")

        # Zero out artifacts
        signal_clean = signal.copy()
        signal_clean[artifact_mask] = 0.0

        return signal_clean, artifact_mask

    def common_average_reference(self, signal: np.ndarray) -> np.ndarray:
        """
        Apply common average reference (CAR).

        Subtracts the mean of all channels from each channel.
        Reduces common noise across all electrodes.

        Args:
            signal: Multi-channel signal (n_channels, n_samples)

        Returns:
            signal_car: CAR-referenced signal
        """
        if signal.ndim == 1:
            logger.warning("CAR requires multi-channel signal. Returning original.")
            return signal

        # Compute mean across channels
        mean_signal = np.mean(signal, axis=0, keepdims=True)  # (1, n_samples)

        # Subtract from each channel
        signal_car = signal - mean_signal

        return signal_car

    def estimate_snr(self, signal: np.ndarray,
                     noise_band: Tuple[float, float] = (0.5, 2.0),
                     signal_band: Tuple[float, float] = (38.0, 42.0)) -> float:
        """
        Estimate signal-to-noise ratio.

        Uses gamma band (38-42 Hz) as signal and low frequency (0.5-2 Hz) as noise.

        Args:
            signal: Input signal (n_channels, n_samples)
            noise_band: Frequency band for noise estimation (Hz)
            signal_band: Frequency band for signal estimation (Hz)

        Returns:
            snr_db: SNR in dB
        """
        from scipy.signal import welch

        # Compute power spectral density per channel
        if signal.ndim == 1:
            signal_2d = signal[np.newaxis, :]
        else:
            signal_2d = signal

        snr_values = []

        for ch in range(signal_2d.shape[0]):
            freqs, pxx = welch(signal_2d[ch, :], fs=self.fs, nperseg=self.fs*4)

            # Power in noise band
            noise_mask = (freqs >= noise_band[0]) & (freqs <= noise_band[1])
            noise_power = np.mean(pxx[noise_mask])

            # Power in signal band
            signal_mask = (freqs >= signal_band[0]) & (freqs <= signal_band[1])
            signal_power = np.mean(pxx[signal_mask])

            # SNR in dB
            snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
            snr_values.append(snr)

        snr_mean = np.mean(snr_values)
        logger.debug(f"SNR estimation: {snr_mean:.2f} dB")

        return snr_mean

    def detect_bad_channels(self, signal: np.ndarray,
                           threshold_std: float = 5.0) -> List[int]:
        """
        Detect bad/noisy channels using standard deviation criterion.

        Channels with std >> mean std are marked as bad.

        Args:
            signal: Multi-channel signal (n_channels, n_samples)
            threshold_std: Number of stds above mean for bad channel detection

        Returns:
            bad_channels: List of bad channel indices
        """
        if signal.ndim == 1:
            return []

        # Compute standard deviation per channel
        stds = np.std(signal, axis=1)
        mean_std = np.mean(stds)
        std_of_stds = np.std(stds)

        # Identify outliers
        threshold = mean_std + threshold_std * std_of_stds
        bad_channels = np.where(stds > threshold)[0].tolist()

        if bad_channels:
            logger.warning(f"Detected {len(bad_channels)} bad channels: {bad_channels}")

        return bad_channels

    def preprocess(self, signal: np.ndarray) -> Tuple[np.ndarray, dict]:
        """
        Full preprocessing pipeline.

        Pipeline:
            1. Bandpass filter (0.5-80 Hz)
            2. Notch filter (50/60 Hz)
            3. Common average reference
            4. Artifact rejection
            5. Quality assessment

        Args:
            signal: Raw EEG signal (n_channels, n_samples)

        Returns:
            signal_processed: Preprocessed signal
            qc_report: Dictionary with quality metrics
        """
        qc_report = {}

        logger.info("Starting preprocessing pipeline...")

        # 1. Bandpass filter
        logger.debug("Applying bandpass filter...")
        signal = self.bandpass_filter(signal)

        # 2. Notch filter
        logger.debug("Applying notch filter...")
        signal = self.notch_filter(signal)

        # 3. Common average reference
        logger.debug("Applying common average reference...")
        signal = self.common_average_reference(signal)

        # 4. Artifact rejection
        logger.debug("Applying artifact rejection...")
        signal, artifact_mask = self.artifact_rejection(signal)
        qc_report['n_artifacts'] = int(np.sum(artifact_mask))
        qc_report['pct_artifacts'] = float(100.0 * np.sum(artifact_mask) / artifact_mask.size)

        # 5. Quality assessment
        logger.debug("Estimating SNR...")
        snr = self.estimate_snr(signal)
        qc_report['snr_db'] = float(snr)

        # Detect bad channels
        logger.debug("Detecting bad channels...")
        bad_channels = self.detect_bad_channels(signal)
        qc_report['bad_channels'] = bad_channels

        logger.info("Preprocessing complete!")
        logger.info(f"  Artifacts: {qc_report['n_artifacts']} ({qc_report['pct_artifacts']:.2f}%)")
        logger.info(f"  SNR: {snr:.2f} dB")
        logger.info(f"  Bad channels: {len(bad_channels)}")

        return signal, qc_report

    def plot_filter_response(self, save_path: Optional[str] = None):
        """
        Plot frequency response of bandpass and notch filters.

        Args:
            save_path: Path to save figure (if None, display only)
        """
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))

        # Frequency response
        freqs = np.linspace(0, self.fs/2, 1000)

        # Bandpass filter
        w_bandpass, h_bandpass = freqz(self.b_bandpass, self.a_bandpass, 2*np.pi*freqs/self.fs)
        axes[0].plot(freqs, 20*np.log10(np.abs(h_bandpass)), 'b-', lw=2)
        axes[0].axvline(self.hp_freq, color='r', linestyle='--', label=f'HPF: {self.hp_freq} Hz')
        axes[0].axvline(self.lp_freq, color='r', linestyle='--', label=f'LPF: {self.lp_freq} Hz')
        axes[0].set_ylabel('Magnitude (dB)')
        axes[0].set_title('Bandpass Filter Response (0.5-80 Hz, 4th-order)')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()
        axes[0].set_xlim([0, self.fs/2])

        # Notch filter
        w_notch, h_notch = freqz(self.b_notch, self.a_notch, 2*np.pi*freqs/self.fs)
        axes[1].plot(freqs, 20*np.log10(np.abs(h_notch)), 'g-', lw=2)
        axes[1].axvline(self.notch_freq, color='r', linestyle='--', label=f'Notch: {self.notch_freq} Hz')
        axes[1].set_xlabel('Frequency (Hz)')
        axes[1].set_ylabel('Magnitude (dB)')
        axes[1].set_title(f'Notch Filter Response ({self.notch_freq} Hz, Q={self.notch_q})')
        axes[1].grid(True, alpha=0.3)
        axes[1].legend()
        axes[1].set_xlim([0, 100])

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved filter response plot to {save_path}")
        else:
            plt.show()

        plt.close()


def test_preprocessing():
    """Test preprocessing pipeline with synthetic signal."""
    logger.info("="*60)
    logger.info("Preprocessing Test")
    logger.info("="*60)

    # Create synthetic signal
    fs = 250.0
    duration = 10.0
    n_samples = int(fs * duration)
    time = np.arange(n_samples) / fs

    # Create multi-channel data (7 frontal channels)
    n_channels = 7
    signal = np.zeros((n_channels, n_samples))

    # Add theta (4-8 Hz)
    theta = 0.5 * np.sin(2*np.pi*6*time)

    # Add gamma (38-42 Hz)
    gamma = 0.3 * np.sin(2*np.pi*40*time)

    # Add noise
    noise = 0.1 * np.random.randn(n_channels, n_samples)

    # Add artifacts (large amplitude spikes)
    artifact_indices = np.random.randint(0, n_samples, size=100)
    noise[0, artifact_indices] += 5.0

    # Combine
    for ch in range(n_channels):
        signal[ch, :] = theta + gamma + noise[ch, :]

    logger.info(f"Synthetic signal shape: {signal.shape}")
    logger.info(f"  Theta (6 Hz) + Gamma (40 Hz) + Noise + Artifacts")

    # Initialize preprocessor
    preprocessor = EEGPreprocessor(fs=fs)

    # Run preprocessing
    signal_clean, qc_report = preprocessor.preprocess(signal)

    logger.info("\nPreprocessing Quality Report:")
    for key, value in qc_report.items():
        logger.info(f"  {key}: {value}")

    # Plot filter response
    preprocessor.plot_filter_response()

    logger.info("\n" + "="*60)
    logger.info("Preprocessing test completed!")
    logger.info("="*60)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    test_preprocessing()
