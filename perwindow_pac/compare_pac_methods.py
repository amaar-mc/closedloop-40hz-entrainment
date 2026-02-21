"""
Diagnostic: compare epoch-level PAC vs per-window PAC.

For each subject, computes:
  - Pearson correlation between epoch-level and per-window PAC
  - Within-epoch variance of per-window PAC (new temporal information)
  - Lag-1 autocorrelation (smoothness of the new signal)
  - Mean absolute deviation from epoch-level value

This validates that per-window PAC is a real signal (correlated with epoch-level)
but contains genuine new information (non-zero within-epoch variance).

Usage:
    venv/Scripts/python.exe perwindow_pac/compare_pac_methods.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent


def lag1_autocorrelation(x: np.ndarray) -> float:
    """Compute lag-1 autocorrelation of a 1D signal."""
    if len(x) < 3:
        return float("nan")
    x_centered = x - np.mean(x)
    var = np.sum(x_centered ** 2)
    if var < 1e-20:
        return float("nan")
    return float(np.sum(x_centered[:-1] * x_centered[1:]) / var)


def compute_within_epoch_variance(
    epoch_pac: np.ndarray, window_pac: np.ndarray
) -> float:
    """Compute mean within-epoch variance of per-window PAC.

    Windows sharing the same epoch-level PAC value belong to the same epoch.
    We compute variance of per-window PAC within each epoch, then average.
    """
    unique_epoch_vals = np.unique(epoch_pac)
    variances = []
    for val in unique_epoch_vals:
        mask = epoch_pac == val
        if mask.sum() < 2:
            continue
        variances.append(float(np.var(window_pac[mask])))
    return float(np.mean(variances)) if variances else 0.0


def analyze_subject(
    subj_id: str,
    epoch_pac: np.ndarray,
    window_pac: np.ndarray,
) -> Dict:
    """Compute diagnostics for one subject."""
    n = len(epoch_pac)

    # Pearson correlation
    if np.std(epoch_pac) < 1e-12 or np.std(window_pac) < 1e-12:
        r, p_val = 0.0, 1.0
    else:
        r, p_val = stats.pearsonr(epoch_pac, window_pac)

    # Within-epoch variance of per-window PAC
    within_var = compute_within_epoch_variance(epoch_pac, window_pac)

    # Lag-1 autocorrelation
    ac_epoch = lag1_autocorrelation(epoch_pac)
    ac_window = lag1_autocorrelation(window_pac)

    # Mean absolute deviation from epoch-level value
    mad = float(np.mean(np.abs(window_pac - epoch_pac)))

    # Unique values
    n_unique_epoch = len(np.unique(epoch_pac))
    n_unique_window = len(np.unique(window_pac))

    return {
        "subject": subj_id,
        "n_windows": n,
        "pearson_r": round(float(r), 4),
        "pearson_p": float(p_val),
        "within_epoch_variance": float(within_var),
        "lag1_autocorr_epoch": round(float(ac_epoch), 4),
        "lag1_autocorr_window": round(float(ac_window), 4),
        "mean_abs_deviation": float(mad),
        "n_unique_epoch": n_unique_epoch,
        "n_unique_window": n_unique_window,
        "epoch_pac_mean": float(np.mean(epoch_pac)),
        "epoch_pac_std": float(np.std(epoch_pac)),
        "window_pac_mean": float(np.mean(window_pac)),
        "window_pac_std": float(np.std(window_pac)),
    }


def main():
    epoch_dir = ROOT / "data" / "processed"
    window_dir = ROOT / "data" / "processed" / "perwindow_pac"

    if not window_dir.exists():
        print("ERROR: Per-window PAC data not found. Run recompute_pac.py first.")
        return

    print("=" * 75)
    print("Diagnostic: Epoch-Level PAC vs Per-Window PAC")
    print("=" * 75)

    all_diagnostics: List[Dict] = []

    for split in ["train", "val", "test"]:
        epoch_path = epoch_dir / f"{split}_data.npz"
        window_path = window_dir / f"{split}_data.npz"

        if not epoch_path.exists() or not window_path.exists():
            print(f"  Skipping {split}: file not found")
            continue

        d_epoch = np.load(epoch_path, allow_pickle=True)
        d_window = np.load(window_path, allow_pickle=True)

        epoch_pac = d_epoch["pac"].astype(np.float64)
        window_pac = d_window["pac"].astype(np.float64)
        subjects = d_epoch["subjects"]

        for subj_id in np.unique(subjects):
            mask = subjects == subj_id
            diag = analyze_subject(
                subj_id, epoch_pac[mask], window_pac[mask]
            )
            diag["split"] = split
            all_diagnostics.append(diag)

    # Print summary table
    print(f"\n{'Subject':<12s} {'Split':<6s} {'N':>5s} {'r':>6s} "
          f"{'WithinVar':>10s} {'AC(epoch)':>10s} {'AC(window)':>10s} "
          f"{'MAD':>10s} {'#Uniq(E)':>8s} {'#Uniq(W)':>8s}")
    print("-" * 95)

    for d in all_diagnostics:
        print(
            f"{d['subject']:<12s} {d['split']:<6s} {d['n_windows']:>5d} "
            f"{d['pearson_r']:>6.3f} "
            f"{d['within_epoch_variance']:>10.2e} "
            f"{d['lag1_autocorr_epoch']:>10.4f} "
            f"{d['lag1_autocorr_window']:>10.4f} "
            f"{d['mean_abs_deviation']:>10.2e} "
            f"{d['n_unique_epoch']:>8d} "
            f"{d['n_unique_window']:>8d}"
        )

    # Aggregate summary
    print(f"\n{'='*75}")
    print("AGGREGATE SUMMARY")
    print(f"{'='*75}")

    n_subjects = len(all_diagnostics)
    metrics = {
        "pearson_r": [d["pearson_r"] for d in all_diagnostics],
        "within_epoch_variance": [d["within_epoch_variance"] for d in all_diagnostics],
        "lag1_autocorr_epoch": [d["lag1_autocorr_epoch"] for d in all_diagnostics],
        "lag1_autocorr_window": [d["lag1_autocorr_window"] for d in all_diagnostics],
        "mean_abs_deviation": [d["mean_abs_deviation"] for d in all_diagnostics],
        "n_unique_epoch": [d["n_unique_epoch"] for d in all_diagnostics],
        "n_unique_window": [d["n_unique_window"] for d in all_diagnostics],
    }

    print(f"  Subjects: {n_subjects}")
    print(f"  Pearson r (epoch vs window): "
          f"mean={np.mean(metrics['pearson_r']):.3f}, "
          f"range=[{np.min(metrics['pearson_r']):.3f}, {np.max(metrics['pearson_r']):.3f}]")
    print(f"  Within-epoch variance:       "
          f"mean={np.mean(metrics['within_epoch_variance']):.2e}, "
          f"range=[{np.min(metrics['within_epoch_variance']):.2e}, "
          f"{np.max(metrics['within_epoch_variance']):.2e}]")
    print(f"  Lag-1 autocorr (epoch):      "
          f"mean={np.nanmean(metrics['lag1_autocorr_epoch']):.4f}")
    print(f"  Lag-1 autocorr (window):     "
          f"mean={np.nanmean(metrics['lag1_autocorr_window']):.4f}")
    print(f"  Mean abs deviation:          "
          f"mean={np.mean(metrics['mean_abs_deviation']):.2e}")
    print(f"  Unique PAC values (epoch):   "
          f"mean={np.mean(metrics['n_unique_epoch']):.0f}")
    print(f"  Unique PAC values (window):  "
          f"mean={np.mean(metrics['n_unique_window']):.0f}")

    # Interpretation
    mean_r = np.mean(metrics["pearson_r"])
    mean_var = np.mean(metrics["within_epoch_variance"])
    print(f"\nINTERPRETATION:")
    if mean_r > 0.5:
        print(f"  - Epoch and per-window PAC are well correlated (r={mean_r:.3f})")
        print(f"    → Per-window PAC captures the same macro trends")
    elif mean_r > 0.2:
        print(f"  - Moderate correlation (r={mean_r:.3f})")
        print(f"    → Per-window PAC captures some epoch structure but adds noise")
    else:
        print(f"  - Weak correlation (r={mean_r:.3f})")
        print(f"    → Per-window PAC is largely independent of epoch labels")

    if mean_var > 0:
        print(f"  - Non-zero within-epoch variance ({mean_var:.2e})")
        print(f"    → Per-window PAC reveals genuine temporal variation within epochs")
    else:
        print(f"  - Zero within-epoch variance → no new temporal information")

    # Save JSON
    results_dir = ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / "perwindow_pac_diagnostics.json"

    output = {
        "n_subjects": n_subjects,
        "aggregate": {
            "pearson_r_mean": round(float(np.mean(metrics["pearson_r"])), 4),
            "pearson_r_std": round(float(np.std(metrics["pearson_r"])), 4),
            "within_epoch_variance_mean": float(np.mean(metrics["within_epoch_variance"])),
            "lag1_autocorr_epoch_mean": round(float(np.nanmean(metrics["lag1_autocorr_epoch"])), 4),
            "lag1_autocorr_window_mean": round(float(np.nanmean(metrics["lag1_autocorr_window"])), 4),
            "mean_abs_deviation_mean": float(np.mean(metrics["mean_abs_deviation"])),
        },
        "per_subject": all_diagnostics,
    }
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
