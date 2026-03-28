"""
Compute sliding-window PAC labels for all processed EEG windows.

Instead of the current epoch-level PAC (one value per 20-40s epoch, shared
by all ~20-40 constituent 2s windows), this computes PAC on a backward-looking
sliding context window (5s or 8s) ending at each 2s window.

Approach:
    1. Load processed windows from data/processed/{split}_data.npz
    2. Identify contiguous segments (windows within same epoch overlap by 1s)
    3. Stitch windows to reconstruct continuous signal per segment
    4. For each window position, extract the backward context (e.g. 5s ending
       at the window's end) from the stitched signal
    5. Compute Tort MI (theta 4-8 Hz, gamma 38-42 Hz) on that context
    6. Save new PAC labels alongside originals

All PAC computation is strictly causal: the context window looks backward only.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy.signal import butter, filtfilt, hilbert


# -- PAC computation (self-contained, mirrors src/pac_computation.py) --------

def _bandpass_filter(
    signal: np.ndarray,
    low: float,
    high: float,
    fs: float,
    order: int,
) -> np.ndarray:
    """Zero-phase bandpass filter."""
    b, a = butter(order, [low, high], btype="band", fs=fs)
    return filtfilt(b, a, signal)


def compute_tort_mi(
    signal: np.ndarray,
    fs: float,
    theta_band: Tuple[float, float],
    gamma_band: Tuple[float, float],
    n_bins: int,
    filter_order: int,
) -> float:
    """
    Compute Tort Modulation Index on a single-channel signal.

    Args:
        signal: 1-D array of EEG samples.
        fs: Sampling rate in Hz.
        theta_band: (low, high) for phase extraction.
        gamma_band: (low, high) for amplitude extraction.
        n_bins: Number of phase bins.
        filter_order: Butterworth filter order.

    Returns:
        Modulation Index (float).
    """
    theta_sig = _bandpass_filter(signal, theta_band[0], theta_band[1], fs, filter_order)
    gamma_sig = _bandpass_filter(signal, gamma_band[0], gamma_band[1], fs, filter_order)

    theta_phase = np.angle(hilbert(theta_sig))
    gamma_amp = np.abs(hilbert(gamma_sig))

    phase_bins = np.linspace(-np.pi, np.pi, n_bins + 1)
    mean_amp = np.zeros(n_bins)
    for i in range(n_bins):
        mask = (theta_phase >= phase_bins[i]) & (theta_phase < phase_bins[i + 1])
        if np.sum(mask) > 0:
            mean_amp[i] = np.mean(gamma_amp[mask])

    total = np.sum(mean_amp) + 1e-10
    mean_amp_norm = mean_amp / total

    uniform = np.ones(n_bins) / n_bins
    kl_div = np.sum(mean_amp_norm * np.log((mean_amp_norm + 1e-10) / uniform))
    mi = kl_div / np.log(n_bins)
    return float(mi)


def compute_multichannel_pac(
    signals: np.ndarray,
    fs: float,
    theta_band: Tuple[float, float],
    gamma_band: Tuple[float, float],
    n_bins: int,
    filter_order: int,
) -> float:
    """Average PAC across channels. signals: (n_channels, n_samples)."""
    pac_vals = []
    for ch in range(signals.shape[0]):
        pac_vals.append(
            compute_tort_mi(signals[ch], fs, theta_band, gamma_band, n_bins, filter_order)
        )
    return float(np.mean(pac_vals))


# -- Segment identification and stitching ------------------------------------

def find_contiguous_segments(
    windows: np.ndarray,
    hop_samples: int,
) -> List[Tuple[int, int]]:
    """
    Find contiguous segments in a subject's windows.

    Two consecutive windows are contiguous if the last `hop_samples` of window[i]
    match the first `hop_samples` of window[i+1].

    Args:
        windows: (N, 1, n_channels, window_samples) array for one subject.
        hop_samples: Number of overlapping samples between consecutive windows.

    Returns:
        List of (start_idx, end_idx) tuples (end exclusive).
    """
    n = windows.shape[0]
    if n == 0:
        return []

    segments: List[Tuple[int, int]] = []
    seg_start = 0

    for i in range(n - 1):
        # Compare last hop_samples of window i with first hop_samples of window i+1
        w_curr_tail = windows[i, 0, 0, hop_samples:]  # channel 0 only for speed
        w_next_head = windows[i + 1, 0, 0, :hop_samples]
        if not np.allclose(w_curr_tail, w_next_head, atol=1e-6):
            segments.append((seg_start, i + 1))
            seg_start = i + 1

    segments.append((seg_start, n))
    return segments


def stitch_segment(
    windows: np.ndarray,
    seg_start: int,
    seg_end: int,
    hop_samples: int,
) -> np.ndarray:
    """
    Stitch contiguous windows into continuous multi-channel signal.

    Args:
        windows: (N, 1, n_channels, window_samples) full subject windows.
        seg_start: First window index in segment.
        seg_end: One past last window index.
        hop_samples: Hop size in samples.

    Returns:
        signal: (n_channels, total_samples) stitched signal.
    """
    seg_windows = windows[seg_start:seg_end, 0, :, :]  # (seg_len, n_ch, win_samples)
    n_windows = seg_windows.shape[0]
    n_channels = seg_windows.shape[1]
    win_samples = seg_windows.shape[2]

    total_samples = win_samples + (n_windows - 1) * hop_samples
    signal = np.zeros((n_channels, total_samples), dtype=np.float64)

    for i in range(n_windows):
        start = i * hop_samples
        signal[:, start:start + win_samples] = seg_windows[i]

    return signal


# -- Sliding window PAC computation -----------------------------------------

def compute_sliding_pac_for_segment(
    signal: np.ndarray,
    n_windows: int,
    window_samples: int,
    hop_samples: int,
    context_sec: float,
    fs: float,
    theta_band: Tuple[float, float],
    gamma_band: Tuple[float, float],
    n_bins_full: int,
    n_bins_short: int,
    filter_order: int,
    min_samples_for_pac: int,
) -> np.ndarray:
    """
    Compute backward-looking sliding-window PAC for each window in a segment.

    For window i, the analysis window spans from
        max(0, window_end - context_samples) to window_end
    where window_end = i * hop_samples + window_samples.

    Args:
        signal: Stitched continuous signal (n_channels, total_samples).
        n_windows: Number of 2s windows in this segment.
        window_samples: Samples per window (500 at 250 Hz).
        hop_samples: Hop between windows (250 at 250 Hz).
        context_sec: Total backward context in seconds.
        fs: Sampling rate.
        theta_band: Phase frequency band.
        gamma_band: Amplitude frequency band.
        n_bins_full: Phase bins for full-length contexts.
        n_bins_short: Phase bins for short contexts (fallback).
        filter_order: Butterworth filter order.
        min_samples_for_pac: Minimum signal length for PAC computation.

    Returns:
        pac_values: (n_windows,) array of PAC values.
    """
    context_samples = int(context_sec * fs)
    pac_values = np.zeros(n_windows, dtype=np.float64)

    for i in range(n_windows):
        window_end = i * hop_samples + window_samples
        context_start = max(0, window_end - context_samples)
        context_signal = signal[:, context_start:window_end]

        actual_samples = context_signal.shape[1]
        if actual_samples < min_samples_for_pac:
            # Too short for reliable PAC -- use raw 2s window with reduced bins
            win_start = i * hop_samples
            context_signal = signal[:, win_start:window_end]
            actual_samples = context_signal.shape[1]

        # Choose bin count based on context length
        # With 5s context at 250 Hz = 1250 samples, theta at 4 Hz gives ~20 cycles
        # With <3s context, reduce bins for stability
        actual_sec = actual_samples / fs
        if actual_sec >= 3.0:
            n_bins = n_bins_full
        else:
            n_bins = n_bins_short

        pac_values[i] = compute_multichannel_pac(
            context_signal, fs, theta_band, gamma_band, n_bins, filter_order
        )

    return pac_values


# -- Main pipeline -----------------------------------------------------------

def compute_sliding_pac_for_split(
    windows: np.ndarray,
    subjects: np.ndarray,
    original_pac: np.ndarray,
    context_sec: float,
    fs: float,
    theta_band: Tuple[float, float],
    gamma_band: Tuple[float, float],
    n_bins_full: int,
    n_bins_short: int,
    filter_order: int,
    window_sec: float,
    hop_sec: float,
) -> np.ndarray:
    """
    Compute sliding-window PAC for an entire split.

    Args:
        windows: (N, 1, n_channels, window_samples) EEG data.
        subjects: (N,) subject labels.
        original_pac: (N,) epoch-level PAC for reference.
        context_sec: Backward context window in seconds.
        fs, theta_band, gamma_band, etc.: PAC computation parameters.
        window_sec: Window duration.
        hop_sec: Hop duration.

    Returns:
        sliding_pac: (N,) new PAC values.
    """
    window_samples = int(window_sec * fs)
    hop_samples = int(hop_sec * fs)
    min_samples_for_pac = int(1.5 * fs)  # 1.5 seconds minimum

    n_total = len(windows)
    sliding_pac = np.zeros(n_total, dtype=np.float64)

    unique_subjects = np.unique(subjects)
    processed = 0

    for subj in unique_subjects:
        subj_mask = subjects == subj
        subj_indices = np.where(subj_mask)[0]
        subj_windows = windows[subj_indices]

        # Find contiguous segments
        segments = find_contiguous_segments(subj_windows, hop_samples)

        for seg_start, seg_end in segments:
            n_seg_windows = seg_end - seg_start
            signal = stitch_segment(subj_windows, seg_start, seg_end, hop_samples)

            seg_pac = compute_sliding_pac_for_segment(
                signal=signal,
                n_windows=n_seg_windows,
                window_samples=window_samples,
                hop_samples=hop_samples,
                context_sec=context_sec,
                fs=fs,
                theta_band=theta_band,
                gamma_band=gamma_band,
                n_bins_full=n_bins_full,
                n_bins_short=n_bins_short,
                filter_order=filter_order,
                min_samples_for_pac=min_samples_for_pac,
            )

            # Map back to global indices
            global_indices = subj_indices[seg_start:seg_end]
            sliding_pac[global_indices] = seg_pac

        processed += len(subj_indices)
        print(f"  {subj}: {len(subj_indices)} windows, "
              f"{len(segments)} segments done")

    assert processed == n_total, f"Processed {processed} != total {n_total}"
    return sliding_pac


def report_statistics(
    name: str,
    original_pac: np.ndarray,
    sliding_pac: np.ndarray,
) -> Dict:
    """Print and return comparison statistics."""
    stats = {
        "n_windows": len(original_pac),
        "original_unique": int(len(np.unique(original_pac))),
        "sliding_unique": int(len(np.unique(sliding_pac))),
        "original_mean": float(np.mean(original_pac)),
        "original_std": float(np.std(original_pac)),
        "original_min": float(np.min(original_pac)),
        "original_max": float(np.max(original_pac)),
        "sliding_mean": float(np.mean(sliding_pac)),
        "sliding_std": float(np.std(sliding_pac)),
        "sliding_min": float(np.min(sliding_pac)),
        "sliding_max": float(np.max(sliding_pac)),
        "correlation": float(np.corrcoef(original_pac, sliding_pac)[0, 1]),
    }

    # Adjacent-same ratio
    orig_same = np.sum(np.abs(np.diff(original_pac)) < 1e-12)
    slide_same = np.sum(np.abs(np.diff(sliding_pac)) < 1e-12)
    n_adj = len(original_pac) - 1
    stats["original_adjacent_same_pct"] = float(100 * orig_same / max(1, n_adj))
    stats["sliding_adjacent_same_pct"] = float(100 * slide_same / max(1, n_adj))

    print(f"\n  {name} statistics:")
    print(f"    Windows:       {stats['n_windows']}")
    print(f"    Unique values: {stats['original_unique']} (epoch) -> "
          f"{stats['sliding_unique']} (sliding)")
    print(f"    Mean:          {stats['original_mean']:.8f} -> {stats['sliding_mean']:.8f}")
    print(f"    Std:           {stats['original_std']:.8f} -> {stats['sliding_std']:.8f}")
    print(f"    Range:         [{stats['original_min']:.8f}, {stats['original_max']:.8f}] -> "
          f"[{stats['sliding_min']:.8f}, {stats['sliding_max']:.8f}]")
    print(f"    Correlation:   {stats['correlation']:.4f}")
    print(f"    Adjacent same: {stats['original_adjacent_same_pct']:.1f}% -> "
          f"{stats['sliding_adjacent_same_pct']:.1f}%")

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute sliding-window PAC labels."
    )
    parser.add_argument(
        "--processed-dir", type=str,
        default="data/processed",
        help="Directory with {train,val,test}_data.npz",
    )
    parser.add_argument(
        "--output-dir", type=str,
        default="experimental/sliding_pac/pac_labels",
        help="Output directory for new PAC labels",
    )
    parser.add_argument(
        "--context-sec", type=float, default=5.0,
        help="Backward context window in seconds (default 5.0)",
    )
    parser.add_argument(
        "--fs", type=float, default=250.0,
        help="Sampling rate in Hz",
    )
    parser.add_argument(
        "--n-bins", type=int, default=18,
        help="Number of phase bins for full context (default 18)",
    )
    parser.add_argument(
        "--n-bins-short", type=int, default=9,
        help="Number of phase bins for short context fallback (default 9)",
    )
    args = parser.parse_args()

    processed_dir = Path(args.processed_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    theta_band = (4.0, 8.0)
    gamma_band = (38.0, 42.0)
    filter_order = 4
    window_sec = 2.0
    hop_sec = 1.0

    print("=" * 70)
    print("COMPUTE SLIDING-WINDOW PAC LABELS")
    print("=" * 70)
    print(f"  Context:     {args.context_sec}s backward-looking")
    print(f"  Phase bins:  {args.n_bins} (full) / {args.n_bins_short} (short)")
    print(f"  Theta:       {theta_band} Hz")
    print(f"  Gamma:       {gamma_band} Hz")
    print()

    all_stats = {}
    t0 = time.time()

    for split in ["train", "val", "test"]:
        print(f"\n--- {split.upper()} ---")
        data = np.load(processed_dir / f"{split}_data.npz", allow_pickle=True)
        windows = data["windows"]
        subjects = data["subjects"]
        original_pac = data["pac"].astype(np.float64)

        # Windows are stored in microvolts -- PAC computation works on any
        # scale since MI is normalized by total amplitude. But keep consistent
        # with original pipeline that operates on V-scale data. Actually,
        # data_loader.py saves windows already scaled to microvolts (line 525),
        # and pac_computation works on whatever scale (MI is scale-invariant).

        sliding_pac = compute_sliding_pac_for_split(
            windows=windows,
            subjects=subjects,
            original_pac=original_pac,
            context_sec=args.context_sec,
            fs=args.fs,
            theta_band=theta_band,
            gamma_band=gamma_band,
            n_bins_full=args.n_bins,
            n_bins_short=args.n_bins_short,
            filter_order=filter_order,
            window_sec=window_sec,
            hop_sec=hop_sec,
        )

        stats = report_statistics(split, original_pac, sliding_pac)
        all_stats[split] = stats

        np.savez_compressed(
            output_dir / f"{split}_sliding_pac.npz",
            sliding_pac=sliding_pac,
            original_pac=original_pac,
            subjects=subjects,
            context_sec=args.context_sec,
        )
        print(f"  Saved: {output_dir / f'{split}_sliding_pac.npz'}")

    elapsed = time.time() - t0

    # Save summary
    summary = {
        "context_sec": args.context_sec,
        "n_bins_full": args.n_bins,
        "n_bins_short": args.n_bins_short,
        "theta_band": list(theta_band),
        "gamma_band": list(gamma_band),
        "filter_order": filter_order,
        "elapsed_sec": elapsed,
        "stats": all_stats,
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    print(f"\n{'=' * 70}")
    print(f"DONE in {elapsed:.1f}s")
    print(f"Summary: {summary_path}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
