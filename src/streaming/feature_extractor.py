"""
Streaming spectral feature extractor for closed-loop EEG inference.

Computes the same 61-feature (7-channel) or 37-feature (4-channel) vector as
the offline ``extract_spectral_features()`` in
``archive/experimental_models/spectral_features.py``, but using causal
``sosfilt`` with persistent filter state instead of the non-causal two-pass filter.

This causality property is required for scientifically valid real-time
closed-loop control: a filter must not use future samples.

Feature layout (identical to offline):
  theta_power(n_ch)  + gamma_power(n_ch) + alpha_power(n_ch) + beta_power(n_ch)
  + theta_gamma_ratio(n_ch) + pac_features(3*n_ch) + cross_channel_stats(5)
  Total: 8*n_ch + 5  →  37 for 4-ch, 61 for 7-ch.

Author: Amaar Chughtai
Date: March 2026
"""

from __future__ import annotations

import numpy as np
from scipy import signal
from typing import Tuple


class StreamingFeatureExtractor:
    """
    Compute spectral features from sequential 2-second EEG windows.

    Uses causal ``sosfilt`` with persistent state so phase and amplitude
    estimates are continuous across windows — required for real-time
    closed-loop operation.

    Args:
        n_channels: Number of EEG channels (4 for Muse 2, 7 for full frontal).
        fs: Sampling frequency in Hz (must match the data source).
        n_pac_bins: Number of phase bins for PAC-structure features.
    """

    _THETA_BAND: Tuple[float, float] = (4.0, 8.0)
    _GAMMA_BAND: Tuple[float, float] = (38.0, 42.0)
    _ALPHA_BAND: Tuple[float, float] = (8.0, 13.0)
    _BETA_BAND: Tuple[float, float] = (13.0, 30.0)
    _FILTER_ORDER: int = 3
    _N_SAMPLES: int = 500  # 2 s at 250 Hz

    def __init__(self, n_channels: int, fs: float = 250.0, n_pac_bins: int = 18) -> None:
        self.n_channels = n_channels
        self.fs = fs
        self.n_pac_bins = n_pac_bins

        nyq = fs / 2.0

        # Build SOS-format Butterworth bandpass filters
        self._sos_theta = signal.butter(
            self._FILTER_ORDER,
            [self._THETA_BAND[0] / nyq, self._THETA_BAND[1] / nyq],
            btype="band",
            output="sos",
        )
        self._sos_gamma = signal.butter(
            self._FILTER_ORDER,
            [self._GAMMA_BAND[0] / nyq, self._GAMMA_BAND[1] / nyq],
            btype="band",
            output="sos",
        )

        # Initialise per-channel filter state: shape (n_channels, n_sos_stages, 2)
        self._zi_theta: np.ndarray = np.zeros(
            (n_channels, self._sos_theta.shape[0], 2)
        )
        self._zi_gamma: np.ndarray = np.zeros(
            (n_channels, self._sos_gamma.shape[0], 2)
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def n_features(self) -> int:
        """Total number of output features: 8 * n_channels + 5."""
        return 8 * self.n_channels + 5

    def process_window(self, eeg: np.ndarray) -> np.ndarray:
        """
        Compute the feature vector for a single 2-second EEG window.

        The filter state is updated in place so consecutive calls produce
        a continuous filtered signal across windows.

        Args:
            eeg: Raw EEG window, shape (n_channels, 500).

        Returns:
            features: Feature vector of length ``n_features`` (37 or 61).

        Raises:
            AssertionError: If ``eeg.shape`` does not equal
                ``(self.n_channels, 500)``.
        """
        assert eeg.shape == (self.n_channels, self._N_SAMPLES), (
            f"Expected shape ({self.n_channels}, {self._N_SAMPLES}), "
            f"got {eeg.shape}"
        )

        # ---- 1. Band powers via Welch (identical to offline) ----
        theta_power = self._welch_band(eeg, self._THETA_BAND)
        alpha_power = self._welch_band(eeg, self._ALPHA_BAND)
        beta_power = self._welch_band(eeg, self._BETA_BAND)
        gamma_power = self._welch_band(eeg, self._GAMMA_BAND)

        # ---- 2. Theta-gamma ratios ----
        theta_gamma_ratio = theta_power / (gamma_power + 1e-10)

        # ---- 3. Phase/amplitude via causal sosfilt + Hilbert ----
        phase, amplitude = self._causal_phase_amplitude(eeg)

        # ---- 4. PAC-structure features (3 per channel) ----
        pac_features = self._compute_pac_features(phase, amplitude)
        pac_features_flat = pac_features.flatten()

        # ---- 5. Cross-channel stats (5 scalars) ----
        cross = np.array([
            theta_power.mean(),
            theta_power.std(),
            gamma_power.mean(),
            gamma_power.std(),
            theta_gamma_ratio.mean(),
        ])

        # ---- Concatenate in same order as offline pipeline ----
        return np.concatenate([
            theta_power,        # n_ch
            gamma_power,        # n_ch
            alpha_power,        # n_ch
            beta_power,         # n_ch
            theta_gamma_ratio,  # n_ch
            pac_features_flat,  # 3 * n_ch
            cross,              # 5
        ])

    def reset(self) -> None:
        """Zero all filter states (restart as if no prior windows seen)."""
        self._zi_theta[:] = 0.0
        self._zi_gamma[:] = 0.0

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _welch_band(self, eeg: np.ndarray, band: Tuple[float, float]) -> np.ndarray:
        """
        Compute band power per channel using Welch's method.

        This is Welch-based (not filter-based) so it is identical to the
        offline pipeline — no causal vs non-causal difference here.

        Args:
            eeg: (n_channels, n_samples)
            band: (low_hz, high_hz)

        Returns:
            band_power: (n_channels,) integrated PSD in band.
        """
        nperseg = min(256, eeg.shape[1])
        freqs, psd = signal.welch(eeg, fs=self.fs, nperseg=nperseg, axis=1)
        idx = np.logical_and(freqs >= band[0], freqs <= band[1])
        return np.trapz(psd[:, idx], freqs[idx], axis=1)

    def _causal_phase_amplitude(
        self, eeg: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract theta instantaneous phase and gamma amplitude envelope
        using causal sosfilt with persistent state.

        State arrays ``_zi_theta`` and ``_zi_gamma`` are updated in-place
        so filtering is continuous across consecutive process_window() calls.

        Args:
            eeg: (n_channels, n_samples)

        Returns:
            phase: (n_channels, n_samples) instantaneous theta phase [rad]
            amplitude: (n_channels, n_samples) gamma amplitude envelope
        """
        n_channels, n_samples = eeg.shape
        phase = np.zeros((n_channels, n_samples))
        amplitude = np.zeros((n_channels, n_samples))

        for ch in range(n_channels):
            # Theta: causal bandpass → Hilbert for instantaneous phase
            theta_filtered, self._zi_theta[ch] = signal.sosfilt(
                self._sos_theta, eeg[ch], zi=self._zi_theta[ch]
            )
            analytic_theta = signal.hilbert(theta_filtered)
            phase[ch] = np.angle(analytic_theta)

            # Gamma: causal bandpass → Hilbert for amplitude envelope
            gamma_filtered, self._zi_gamma[ch] = signal.sosfilt(
                self._sos_gamma, eeg[ch], zi=self._zi_gamma[ch]
            )
            analytic_gamma = signal.hilbert(gamma_filtered)
            amplitude[ch] = np.abs(analytic_gamma)

        return phase, amplitude

    def _compute_pac_features(
        self, phase: np.ndarray, amplitude: np.ndarray
    ) -> np.ndarray:
        """
        Compute PAC-structure features identical to offline compute_pac_features().

        Features per channel: [resultant_length, amp_var, max_bin_idx].
        The modulation index (MI) term is intentionally omitted — it directly
        encodes the prediction target and causes leakage (see archive/diagnostics/).

        Args:
            phase: (n_channels, n_samples) theta instantaneous phase.
            amplitude: (n_channels, n_samples) gamma amplitude envelope.

        Returns:
            features: (n_channels, 3)
        """
        n_channels = phase.shape[0]
        features = np.empty((n_channels, 3))
        phase_bins = np.linspace(-np.pi, np.pi, self.n_pac_bins + 1)

        for ch in range(n_channels):
            # Mean amplitude per phase bin
            amp_per_bin = np.zeros(self.n_pac_bins)
            for i in range(self.n_pac_bins):
                mask = (phase[ch] >= phase_bins[i]) & (phase[ch] < phase_bins[i + 1])
                if mask.sum() > 0:
                    amp_per_bin[i] = amplitude[ch, mask].mean()

            # Circular mean resultant length (phase consistency)
            mean_phase = np.angle(np.mean(np.exp(1j * phase[ch])))
            resultant_length = np.abs(
                np.mean(np.exp(1j * (phase[ch] - mean_phase)))
            )

            # Amplitude variance
            amp_var = amplitude[ch].var()

            # Preferred phase bin index (normalised to [0, 1])
            max_bin_idx = float(np.argmax(amp_per_bin)) / self.n_pac_bins

            features[ch] = [resultant_length, amp_var, max_bin_idx]

        return features
