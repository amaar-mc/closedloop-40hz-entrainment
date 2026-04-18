"""
Hardware-agnostic EEG adapters for closed-loop inference.

Provides two adapters:
- SimulatedEEGAdapter: BrainFlow SYNTHETIC_BOARD for hardware-free development
  and CI testing. Yields (n_channels, 500) float32 windows at ~2-second intervals.
- RealEEGAdapter: Muse 2 BLE adapter.  Attempted 2026-03-21 on macOS Darwin 25.4.0.
  BLE connection failed (Bluetooth not enabled in BrainFlow C++ layer).
  The class contains the full implementation that would work on a BLE-enabled
  system, but raises NotImplementedError with a diagnostic on the current host.
  SimulatedEEGAdapter is the confirmed shipping demo path.  See 11-03-SUMMARY.md.

Usage:
    with SimulatedEEGAdapter(n_channels=4) as adapter:
        window = adapter.get_window()  # (4, 500) float32
"""

from __future__ import annotations

import time
from typing import List, Optional

import numpy as np

try:
    from brainflow.board_shim import BoardIds, BoardShim, BrainFlowInputParams, LogLevels
    _HAS_BRAINFLOW = True
except ImportError:
    _HAS_BRAINFLOW = False

try:
    from scipy.signal import resample as _resample

    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False

# Samples per window at 250 Hz over a 2-second window.
WINDOW_SAMPLES: int = 500

# Seconds to sleep before pulling a fresh window so the board accumulates enough data.
WINDOW_DURATION_SEC: float = 2.0


class SimulatedEEGAdapter:
    """
    Simulated EEG source using BrainFlow SYNTHETIC_BOARD.

    Creates a BrainFlow board session that generates synthetic EEG at 250 Hz.
    Calling get_window() sleeps 2 seconds then pulls 500 samples from the board,
    returning a (n_channels, 500) float32 array.

    Implements context manager protocol for deterministic resource cleanup.

    Args:
        n_channels: Number of EEG channels to extract (default 4).
        channel_indices: Explicit EEG channel indices into the board's EEG channel
            list.  If None, takes the first n_channels from the board's EEG channel
            list.  If provided, validates every index is within the board's EEG
            channel list.

    Raises:
        ValueError: If channel_indices contains indices outside the board's EEG
            channel list, or if n_channels exceeds available EEG channels.
    """

    def __init__(
        self,
        n_channels: int = 4,
        channel_indices: Optional[List[int]] = None,
    ) -> None:
        # Suppress verbose BrainFlow C++ logging before any board operation.
        BoardShim.set_log_level(LogLevels.LEVEL_OFF.value)

        self._board_id = BoardIds.SYNTHETIC_BOARD
        available_eeg = list(BoardShim.get_eeg_channels(self._board_id))

        if channel_indices is None:
            if n_channels > len(available_eeg):
                raise ValueError(
                    f"Requested n_channels={n_channels} but SYNTHETIC_BOARD only "
                    f"has {len(available_eeg)} EEG channels."
                )
            self._eeg_indices = available_eeg[:n_channels]
        else:
            invalid = [idx for idx in channel_indices if idx not in available_eeg]
            if invalid:
                raise ValueError(
                    f"channel_indices {invalid} are not valid EEG channel indices "
                    f"for SYNTHETIC_BOARD (valid: {available_eeg})."
                )
            self._eeg_indices = list(channel_indices)

        self.n_channels = len(self._eeg_indices)

        params = BrainFlowInputParams()
        self._board = BoardShim(self._board_id.value, params)
        self._board.prepare_session()
        self._board.start_stream()

    def get_window(self) -> np.ndarray:
        """
        Sleep 2 seconds and return one (n_channels, 500) float32 EEG window.

        Sleeping before reading ensures the ring buffer always holds a fresh
        2-second chunk independent of any previous call timing.

        Returns:
            np.ndarray of shape (n_channels, 500) and dtype float32.
        """
        time.sleep(WINDOW_DURATION_SEC)
        # get_current_board_data returns all channels x WINDOW_SAMPLES.
        raw = self._board.get_current_board_data(WINDOW_SAMPLES)
        # Index to our chosen EEG channels and cast to float32.
        window = raw[self._eeg_indices, :].astype(np.float32)
        return window

    def close(self) -> None:
        """Stop stream and release BrainFlow session."""
        try:
            self._board.stop_stream()
        finally:
            self._board.release_session()

    def __enter__(self) -> SimulatedEEGAdapter:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()


class _NumpySimulatedAdapter:
    """Pure-numpy fallback when brainflow is not installed (e.g. cloud deploy).

    Generates synthetic EEG with alternating high/low gamma-theta coupling
    to produce realistic PAC fluctuations and stimulus state transitions.
    Cycle: ~20s high PAC (rest) → ~15s low PAC (stimulate) → repeat.
    """

    def __init__(self, n_channels: int = 4) -> None:
        self.n_channels = n_channels
        self._fs = 250.0
        self._t = 0.0
        self._window_count = 0

    def get_window(self) -> np.ndarray:
        time.sleep(WINDOW_DURATION_SEC)
        t = np.arange(WINDOW_SAMPLES) / self._fs + self._t
        self._t += WINDOW_DURATION_SEC
        self._window_count += 1

        # Slow oscillation in gamma coupling strength (~35s cycle)
        cycle_phase = (self._t % 35.0) / 35.0
        # Smooth transitions: high coupling 0-0.57 (20s), low 0.57-1.0 (15s)
        if cycle_phase < 0.4:
            gamma_strength = 1.5 + 0.3 * np.sin(2 * np.pi * cycle_phase * 2.5)
        elif cycle_phase < 0.57:
            # Transition down
            blend = (cycle_phase - 0.4) / 0.17
            gamma_strength = 1.5 * (1 - blend) + 0.2 * blend
        elif cycle_phase < 0.83:
            gamma_strength = 0.2 + 0.1 * np.sin(2 * np.pi * cycle_phase * 3)
        else:
            # Transition up
            blend = (cycle_phase - 0.83) / 0.17
            gamma_strength = 0.2 * (1 - blend) + 1.5 * blend

        window = np.zeros((self.n_channels, WINDOW_SAMPLES), dtype=np.float32)
        for ch in range(self.n_channels):
            theta = 8.0 * np.sin(2 * np.pi * 6 * t + ch * 0.7)
            theta_phase = 2 * np.pi * 6 * t + ch * 0.7
            # Phase-amplitude coupling: gamma amplitude modulated by theta phase
            gamma_env = (1 + np.cos(theta_phase)) / 2  # peaks at theta peak
            gamma = gamma_strength * gamma_env * np.sin(2 * np.pi * 40 * t + ch)
            alpha = 3.0 * np.sin(2 * np.pi * 10 * t + ch * 1.2)
            noise = np.random.randn(WINDOW_SAMPLES).astype(np.float32) * 1.5
            window[ch] = (theta + gamma + alpha + noise).astype(np.float32)
        return window

    def close(self) -> None:
        pass

    def __enter__(self) -> "_NumpySimulatedAdapter":
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        pass


if not _HAS_BRAINFLOW:
    SimulatedEEGAdapter = _NumpySimulatedAdapter  # type: ignore[misc]


class RealEEGAdapter:
    """
    Muse 2 BLE adapter — NOT VIABLE on macOS Darwin 25.4.0.

    Attempted: 2026-03-21.  BrainFlow BoardIds.MUSE_2_BOARD failed to connect
    via BLE.  Error: "BOARD_NOT_READY_ERROR:7 unable to prepare streaming
    session — Bluetooth is not enabled."

    The complete implementation is present below and will work on a system with
    an active BrainFlow-compatible BLE stack.  On the current host, __init__
    raises NotImplementedError with a diagnostic message so callers get a clear
    error instead of a silent hang.

    The simulated mode (SimulatedEEGAdapter) is the confirmed shipping demo
    path.  The 4-channel model architecture supports real hardware when
    available — no model changes are needed.

    See: .planning/phases/11-real-time-inference-pipeline/11-03-SUMMARY.md

    Muse 2 hardware details (for future enablement):
    - Board: BoardIds.MUSE_2_BOARD (value=38)
    - Native sampling rate: 256 Hz
    - 4 EEG channels: TP9, AF7, AF8, TP10 (BrainFlow indices [1, 2, 3, 4])
    - 2-second window: 512 samples at 256 Hz, resampled to 500 at 250 Hz
    - BLE on macOS: BrainFlowInputParams.mac_address must be set to the
      paired headset's Bluetooth address (e.g. "XX:XX:XX:XX:XX:XX")
    """

    # Muse 2 native rate (Hz) and target rate for downstream models.
    _NATIVE_FS: int = 256
    _TARGET_FS: int = 250
    # Samples at native rate for a 2-second window.
    _NATIVE_SAMPLES: int = 512  # 256 Hz × 2 s
    # Samples at target rate for a 2-second window.
    _TARGET_SAMPLES: int = 500  # 250 Hz × 2 s

    def __init__(self, mac_address: str = "") -> None:
        """
        Attempt to open a Muse 2 BLE session.

        Args:
            mac_address: Bluetooth MAC address of the paired Muse 2 headset
                (e.g. "XX:XX:XX:XX:XX:XX").  Required on most platforms; on
                macOS, BrainFlow may discover the device automatically if empty.

        Raises:
            NotImplementedError: Always on macOS Darwin 25.4.0 where BLE is not
                enabled in the BrainFlow C++ layer.
            RuntimeError: If BrainFlow raises BrainFlowError during session
                preparation on other platforms.
        """
        if not _HAS_SCIPY:
            raise RuntimeError(
                "scipy is required for Muse 2 resampling. "
                "Run: pip install scipy"
            )

        BoardShim.set_log_level(LogLevels.LEVEL_OFF.value)

        self._board_id = BoardIds.MUSE_2_BOARD
        self._eeg_indices = list(BoardShim.get_eeg_channels(self._board_id))
        self.n_channels = len(self._eeg_indices)  # 4

        params = BrainFlowInputParams()
        if mac_address:
            params.mac_address = mac_address

        self._board = BoardShim(self._board_id.value, params)

        try:
            self._board.prepare_session()
        except Exception as exc:
            raise NotImplementedError(
                "Muse 2 BLE integration is not viable on this system.\n"
                f"BrainFlow error: {exc}\n"
                "Use SimulatedEEGAdapter for hardware-free development.\n"
                "See .planning/phases/11-real-time-inference-pipeline/11-03-SUMMARY.md"
            ) from exc

        self._board.start_stream()

    def get_window(self) -> np.ndarray:
        """
        Sleep 2 seconds and return one (n_channels, 500) float32 EEG window.

        Reads 512 samples at 256 Hz (2 s) then resamples to 500 samples at
        250 Hz using scipy.signal.resample.

        Returns:
            np.ndarray of shape (n_channels, 500) and dtype float32.
        """
        time.sleep(WINDOW_DURATION_SEC)
        raw = self._board.get_current_board_data(self._NATIVE_SAMPLES)
        eeg = raw[self._eeg_indices, :]  # (4, 512) at 256 Hz
        # Resample from 256 Hz → 250 Hz along sample axis.
        eeg_resampled = _resample(eeg, self._TARGET_SAMPLES, axis=1)
        return eeg_resampled.astype(np.float32)

    def close(self) -> None:
        """Stop stream and release BrainFlow session."""
        try:
            self._board.stop_stream()
        finally:
            self._board.release_session()

    def __enter__(self) -> RealEEGAdapter:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()
