"""
Hardware-agnostic EEG adapters for closed-loop inference.

Provides two adapters:
- SimulatedEEGAdapter: BrainFlow SYNTHETIC_BOARD for hardware-free development
  and CI testing. Yields (n_channels, 500) float32 windows at ~2-second intervals.
- RealEEGAdapter: Stub for Muse 2 hardware integration (implemented in Plan 03).

Usage:
    with SimulatedEEGAdapter(n_channels=4) as adapter:
        window = adapter.get_window()  # (4, 500) float32
"""

from __future__ import annotations

import time
from typing import List, Optional

import numpy as np

from brainflow.board_shim import BoardIds, BoardShim, BrainFlowInputParams, LogLevels

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


class RealEEGAdapter:
    """
    Real EEG adapter stub for Muse 2 hardware integration.

    Full implementation is deferred to Plan 03 (RTINF-03).

    Muse 2 hardware notes (for Plan 03):
    - Board: BoardIds.MUSE_2_BOARD
    - Native sample rate: 256 Hz — must resample to 250 Hz for downstream
      feature extraction and model inference.
    - BLE connection on macOS: pass mac_address via BrainFlowInputParams.
    - Channel map: EEG channels [1, 2, 3, 4] (TP9, AF7, AF8, TP10).
    """

    def __init__(self) -> None:
        raise NotImplementedError(
            "Muse 2 integration is implemented in Plan 03. "
            "Use SimulatedEEGAdapter for hardware-free development."
        )

    def get_window(self) -> np.ndarray:
        """Return one (n_channels, 500) float32 EEG window from Muse 2."""
        raise NotImplementedError("Implemented in Plan 03.")

    def close(self) -> None:
        """Stop stream and release hardware session."""
        raise NotImplementedError("Implemented in Plan 03.")
