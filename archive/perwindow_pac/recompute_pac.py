"""
Recompute PAC per 2-second window instead of per epoch.

The original pipeline computes PAC once per epoch (20-40s event block) and assigns
that same value to every 2-second window within the epoch. This script recomputes
PAC individually for each 2-second window using 9 phase bins (40 degrees each) instead
of 18, which is more robust with the ~12 theta cycles available in a 2s window.

Usage:
    venv/Scripts/python.exe perwindow_pac/recompute_pac.py
"""

from __future__ import annotations

import sys
import time as time_mod
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from pac_computation import PACComputer  # noqa: E402


def recompute_pac_for_split(
    input_path: Path,
    output_path: Path,
    pac_computer: PACComputer,
) -> None:
    """Recompute PAC per window for one split file.

    Args:
        input_path: Path to original {split}_data.npz
        output_path: Path to save recomputed {split}_data.npz
        pac_computer: PACComputer instance (configured with n_bins=9)
    """
    d = np.load(input_path, allow_pickle=True)
    windows = d["windows"]   # (N, 1, 7, 500)
    subjects = d["subjects"]
    old_pac = d["pac"]

    n_windows = len(windows)
    new_pac = np.zeros(n_windows, dtype=np.float64)

    print(f"  Processing {n_windows} windows from {input_path.name}...")
    t0 = time_mod.time()

    for i in range(n_windows):
        eeg = windows[i, 0]  # (7, 500) — 7 channels, 500 samples
        # compute_pac_multichannel returns (7,) PAC values; average across channels
        pac_values = pac_computer.compute_pac_multichannel(eeg)
        new_pac[i] = float(np.mean(pac_values))

        if (i + 1) % 500 == 0:
            elapsed = time_mod.time() - t0
            rate = (i + 1) / elapsed
            eta = (n_windows - i - 1) / rate
            print(f"    {i+1}/{n_windows} windows ({rate:.0f}/s, ETA {eta:.0f}s)")

    elapsed = time_mod.time() - t0
    print(f"  Done: {n_windows} windows in {elapsed:.1f}s ({n_windows/elapsed:.0f}/s)")

    # Summary statistics
    print(f"  Old PAC: mean={np.mean(old_pac):.6f}, std={np.std(old_pac):.6f}, "
          f"unique={len(np.unique(old_pac))}")
    print(f"  New PAC: mean={np.mean(new_pac):.6f}, std={np.std(new_pac):.6f}, "
          f"unique={len(np.unique(new_pac))}")

    # Save with same keys, replacing pac
    np.savez_compressed(
        output_path,
        windows=windows,
        pac=new_pac,
        subjects=subjects,
    )
    print(f"  Saved: {output_path}")


def main():
    input_dir = ROOT / "data" / "processed"
    output_dir = ROOT / "data" / "processed" / "perwindow_pac"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 9 phase bins (40 degrees each) — more robust with ~12 theta cycles per 2s window
    pac_computer = PACComputer(
        theta_band=(4.0, 8.0),
        gamma_band=(38.0, 42.0),
        fs=250.0,
        n_bins=9,
    )

    print("=" * 70)
    print("Per-Window PAC Recomputation (9 phase bins)")
    print("=" * 70)
    print(f"Input:  {input_dir}")
    print(f"Output: {output_dir}")
    print()

    t_total = time_mod.time()

    for split in ["train", "val", "test"]:
        input_path = input_dir / f"{split}_data.npz"
        output_path = output_dir / f"{split}_data.npz"

        if not input_path.exists():
            print(f"  WARNING: {input_path} not found, skipping")
            continue

        recompute_pac_for_split(input_path, output_path, pac_computer)
        print()

    print(f"Total runtime: {time_mod.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
