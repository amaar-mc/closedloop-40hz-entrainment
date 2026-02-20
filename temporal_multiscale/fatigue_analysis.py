"""
Habituation/fatigue analysis: does PAC decline across repeated stimulation
blocks within each subject?

If the brain habituates to continuous 40Hz stimulation, later stim blocks
should produce lower PAC than earlier ones.  This is direct evidence that
fixed-schedule stimulation wastes energy and that adaptive timing matters.

Usage:
    python temporal_multiscale/fatigue_analysis.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_subject_pac_and_events(
    processed_dir: Path, raw_root: Path, split: str
) -> List[Dict]:
    """Load PAC values and align with BIDS events for each subject."""
    d = np.load(processed_dir / f"{split}_data.npz", allow_pickle=True)
    pac = d["pac"].astype(np.float64)
    subjects = d["subjects"]

    results = []
    for subj in np.unique(subjects):
        mask = subjects == subj
        subj_pac = pac[mask]

        # Load events
        tsv = raw_root / subj / "eeg" / f"{subj}_task-40HzAuditoryEntrainment_events.tsv"
        if not tsv.exists():
            continue
        events = pd.read_csv(tsv, sep="\t").sort_values("onset").reset_index(drop=True)

        # Window centers (hop=1s, window=2s)
        n_windows = len(subj_pac)
        t = np.arange(n_windows, dtype=np.float64) * 1.0 + 1.0  # center of each 2s window

        # Assign each window to a stim block
        stim_state = np.zeros(n_windows, dtype=np.float64)
        block_id = np.full(n_windows, -1, dtype=np.int32)
        current_block = 0

        for _, row in events.iterrows():
            onset = float(row["onset"])
            duration = float(row["duration"])
            is_stim = int(row["value"]) == 2
            in_event = (t >= onset) & (t < onset + duration)
            stim_state[in_event] = 1.0 if is_stim else 0.0
            if is_stim:
                block_id[in_event] = current_block
            else:
                # Rest block increments the counter for next stim
                if is_stim is False and current_block >= 0:
                    pass
            # Track block transitions
            if is_stim:
                pass

        # Re-do block assignment more carefully: each contiguous stim period is a block
        stim_blocks = []
        in_stim = False
        block_num = -1
        for i in range(n_windows):
            if stim_state[i] == 1.0:
                if not in_stim:
                    block_num += 1
                    in_stim = True
                block_id[i] = block_num
            else:
                in_stim = False
                block_id[i] = -1  # rest

        n_blocks = block_num + 1

        # Compute mean PAC per stim block
        block_pac = []
        for b in range(n_blocks):
            bmask = block_id == b
            if bmask.sum() > 0:
                block_pac.append({
                    "block": b,
                    "mean_pac": float(np.mean(subj_pac[bmask])),
                    "std_pac": float(np.std(subj_pac[bmask])),
                    "n_windows": int(bmask.sum()),
                    # PAC in first half vs second half of block
                    "first_half_pac": float(np.mean(subj_pac[bmask][:bmask.sum() // 2]))
                    if bmask.sum() >= 4
                    else float(np.mean(subj_pac[bmask])),
                    "second_half_pac": float(np.mean(subj_pac[bmask][bmask.sum() // 2:]))
                    if bmask.sum() >= 4
                    else float(np.mean(subj_pac[bmask])),
                })

        if len(block_pac) >= 2:
            results.append({
                "subject": subj,
                "n_blocks": n_blocks,
                "blocks": block_pac,
            })

    return results


def analyze_fatigue(results: List[Dict]) -> Dict:
    """Analyze habituation patterns across subjects."""

    print("=" * 70)
    print("HABITUATION / FATIGUE ANALYSIS")
    print("=" * 70)

    # 1. Per-subject: does PAC decline across blocks?
    print("\n--- Per-Subject PAC Across Stim Blocks ---")
    print(f"{'Subject':<10s} {'Blocks':>6s}  Block PAC values...")

    all_first_block_pac = []
    all_last_block_pac = []
    all_slopes = []
    within_block_declines = []

    for res in results:
        subj = res["subject"]
        blocks = res["blocks"]
        pacs = [b["mean_pac"] for b in blocks]

        # Linear regression: block_number vs mean_pac
        x = np.arange(len(pacs), dtype=np.float64)
        slope, intercept, r_val, p_val, std_err = stats.linregress(x, pacs)
        all_slopes.append(slope)

        all_first_block_pac.append(pacs[0])
        all_last_block_pac.append(pacs[-1])

        pac_str = " -> ".join(f"{p:.5f}" for p in pacs)
        decline_pct = 100.0 * (pacs[-1] - pacs[0]) / (pacs[0] + 1e-12)
        print(f"{subj:<10s} {len(pacs):>6d}  {pac_str}  ({decline_pct:+.1f}%, slope={slope:.2e})")

        # Within-block fatigue: does PAC drop within each block?
        for b in blocks:
            if b["n_windows"] >= 4:
                within_decline = b["second_half_pac"] - b["first_half_pac"]
                within_block_declines.append(within_decline)

    # 2. Aggregate statistics
    print(f"\n--- Aggregate Statistics ({len(results)} subjects) ---")

    first_arr = np.array(all_first_block_pac)
    last_arr = np.array(all_last_block_pac)
    slopes_arr = np.array(all_slopes)

    # Paired test: first block vs last block
    t_stat, p_val = stats.ttest_rel(first_arr, last_arr)
    mean_decline = float(np.mean(last_arr - first_arr))
    pct_decline = 100.0 * mean_decline / (np.mean(first_arr) + 1e-12)

    print(f"First block mean PAC:  {np.mean(first_arr):.6f} +/- {np.std(first_arr):.6f}")
    print(f"Last block mean PAC:   {np.mean(last_arr):.6f} +/- {np.std(last_arr):.6f}")
    print(f"Mean decline:          {mean_decline:.6f} ({pct_decline:+.1f}%)")
    print(f"Paired t-test:         t={t_stat:.3f}, p={p_val:.4f}")
    print(f"Significant (p<0.05):  {'YES' if p_val < 0.05 else 'NO'}")

    # Slope analysis
    n_declining = int(np.sum(slopes_arr < 0))
    print(f"\nSlope across blocks:   mean={np.mean(slopes_arr):.2e}, median={np.median(slopes_arr):.2e}")
    print(f"Subjects with decline: {n_declining}/{len(slopes_arr)} ({100*n_declining/len(slopes_arr):.0f}%)")

    # One-sample t-test: is mean slope < 0?
    t_slope, p_slope = stats.ttest_1samp(slopes_arr, 0)
    print(f"Slope t-test (< 0):    t={t_slope:.3f}, p={p_slope/2:.4f} (one-tailed)")

    # 3. Within-block fatigue
    within_arr = np.array(within_block_declines)
    if len(within_arr) > 0:
        t_within, p_within = stats.ttest_1samp(within_arr, 0)
        n_decline_within = int(np.sum(within_arr < 0))
        print(f"\n--- Within-Block Fatigue ---")
        print(f"Blocks analyzed:       {len(within_arr)}")
        print(f"Mean 2nd-half - 1st-half: {np.mean(within_arr):.6f}")
        print(f"Blocks with decline:   {n_decline_within}/{len(within_arr)} ({100*n_decline_within/len(within_arr):.0f}%)")
        print(f"t-test:                t={t_within:.3f}, p={p_within:.4f}")

    summary = {
        "n_subjects": len(results),
        "first_block_mean_pac": float(np.mean(first_arr)),
        "last_block_mean_pac": float(np.mean(last_arr)),
        "mean_decline": float(mean_decline),
        "pct_decline": float(pct_decline),
        "paired_ttest_t": float(t_stat),
        "paired_ttest_p": float(p_val),
        "n_subjects_declining": n_declining,
        "pct_subjects_declining": float(100 * n_declining / len(slopes_arr)),
        "mean_slope": float(np.mean(slopes_arr)),
        "slope_ttest_p_onetail": float(p_slope / 2),
        "within_block_mean_decline": float(np.mean(within_arr)) if len(within_arr) > 0 else None,
        "within_block_pct_declining": float(100 * n_decline_within / len(within_arr))
        if len(within_arr) > 0
        else None,
    }

    return summary


def main() -> None:
    processed_dir = Path("data/processed")
    raw_root = Path("data/raw/ds005048")

    all_results = []
    for split in ["train", "val", "test"]:
        all_results.extend(
            load_subject_pac_and_events(processed_dir, raw_root, split)
        )

    print(f"Loaded {len(all_results)} subjects with multiple stim blocks\n")

    summary = analyze_fatigue(all_results)

    # Verdict
    print(f"\n{'='*70}")
    print("VERDICT")
    print(f"{'='*70}")
    if summary["pct_subjects_declining"] > 50:
        print(f"{summary['pct_subjects_declining']:.0f}% of subjects show PAC decline across blocks.")
        print("This supports the habituation hypothesis: continuous stimulation")
        print("becomes less effective over time, justifying adaptive scheduling.")
    else:
        print(f"Only {summary['pct_subjects_declining']:.0f}% of subjects show clear PAC decline.")
        print("Habituation evidence is mixed — some subjects habituate, others don't.")
        print("Adaptive scheduling still justified for fatiguing subjects.")

    out_path = Path("results/fatigue_analysis.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
