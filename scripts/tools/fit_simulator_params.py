"""Fit simulator tau parameters from real PAC transition data.

Extracts tau_rise and tau_decay from the processed multiscale temporal
dataset by fitting exponential approach dynamics to observed PAC
transitions during stimulation and rest periods.

Model: PAC(t+1) = PAC(t) + tau * (target - PAC(t))
  => tau = (PAC(t+1) - PAC(t)) / (target - PAC(t))

For stimulation (rise): target = per-subject 90th percentile PAC
For rest (decay): target = per-subject 10th percentile PAC

Because PAC is computed at the epoch level (full 20-40s blocks) and
assigned to all 2s windows within each epoch, consecutive windows
within one epoch share the same PAC value. This script collapses to
epoch-level PAC before fitting, then measures inter-epoch transitions.

Addresses RSRCH-04: simulator tau values must be either fit from real
data or documented with literature citations. This script provides the
empirical extraction, complementing the literature citations already
present in src/simulator.py (Galambos 1981, Picton 2003).

See .planning/phases/10-scope-lock-foundation/SIMULATOR_DEFENSE.md for
the full analysis motivating this script.
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

# Feature index for stim_state in the 73-feature multiscale vector
STIM_STATE_FEATURE_IDX = 68

# Minimum valid tau candidates per subject to include in population
# estimate. Set to 3 because the ds005048 block structure (alternating
# 40s stim / 20s rest) yields only ~8-10 epochs per subject, and not
# all inter-epoch transitions produce valid tau candidates.
MIN_VALID_CANDIDATES = 3

# Heuristic defaults from src/simulator.py for comparison
HEURISTIC_TAU_RISE = 0.15
HEURISTIC_TAU_DECAY = 0.10

# Numerical stability guard
EPSILON = 1e-8


def load_all_splits(data_dir: Path) -> dict[str, np.ndarray]:
    """Load and concatenate train/val/test multiscale splits.

    Returns dict with keys: last_pac, stim_state, subjects, end_idx.
    All arrays are concatenated across splits in order.
    """
    all_last_pac = []
    all_stim_state = []
    all_subjects = []
    all_end_idx = []

    for split in ["train", "val", "test"]:
        path = data_dir / f"{split}_multiscale.npz"
        if not path.exists():
            raise FileNotFoundError(f"Missing split file: {path}")

        d = np.load(path, allow_pickle=True)

        # Verify feature_names has stim_state at expected index
        feature_names = list(d["feature_names"])
        if feature_names[STIM_STATE_FEATURE_IDX] != "stim_state":
            raise ValueError(
                f"Expected stim_state at index {STIM_STATE_FEATURE_IDX}, "
                f"got {feature_names[STIM_STATE_FEATURE_IDX]}"
            )

        all_last_pac.append(d["last_pac"])
        # stim_state is z-scored; positive = stim, negative = rest
        all_stim_state.append(d["x_seq"][:, -1, STIM_STATE_FEATURE_IDX])
        all_subjects.append(d["subjects"])
        all_end_idx.append(d["end_idx"])

    return {
        "last_pac": np.concatenate(all_last_pac),
        "stim_state": np.concatenate(all_stim_state),
        "subjects": np.concatenate(all_subjects),
        "end_idx": np.concatenate(all_end_idx),
    }


def collapse_to_epochs(
    pac_sorted: np.ndarray,
    stim_binary: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Collapse window-level data to epoch-level.

    PAC is computed at the epoch level (20-40s blocks) and shared across
    all 2s windows in each epoch. This function detects epoch boundaries
    where PAC value changes and returns one PAC value and one stim state
    per epoch.

    The stim state for each epoch is the majority vote of window-level
    stim states within that epoch run.
    """
    # Find indices where PAC changes (epoch boundaries)
    change_idx = np.concatenate(
        [[0], np.where(pac_sorted[1:] != pac_sorted[:-1])[0] + 1]
    )
    epoch_pac = pac_sorted[change_idx]

    # Majority-vote stim state per epoch
    epoch_stim = np.empty(len(change_idx), dtype=int)
    for j in range(len(change_idx)):
        start = change_idx[j]
        end = change_idx[j + 1] if j + 1 < len(change_idx) else len(pac_sorted)
        epoch_stim[j] = int(np.mean(stim_binary[start:end]) >= 0.5)

    return epoch_pac, epoch_stim


def fit_subject_tau(
    epoch_pac: np.ndarray,
    epoch_stim: np.ndarray,
    target_stim: float,
    target_rest: float,
) -> dict:
    """Fit tau_rise and tau_decay for a single subject at epoch level.

    For consecutive epoch pairs (pac_t, pac_{t+1}):
      - During stimulation: tau = delta_pac / (target_stim - pac_t)
      - During rest: tau = delta_pac / (target_rest - pac_t)

    Only keeps candidates where 0 < tau <= 1 (physically meaningful).

    Returns dict with tau_rise, tau_decay (medians), transition counts,
    and raw candidate lists for population-level pooling.
    """
    rise_candidates: list[float] = []
    decay_candidates: list[float] = []

    for i in range(len(epoch_pac) - 1):
        pac_t = float(epoch_pac[i])
        pac_t1 = float(epoch_pac[i + 1])
        delta = pac_t1 - pac_t

        if epoch_stim[i] == 1:
            # Stimulation epoch: PAC should approach target_stim
            denominator = target_stim - pac_t
            if abs(denominator) > EPSILON:
                tau_candidate = delta / denominator
                if 0 < tau_candidate <= 1:
                    rise_candidates.append(tau_candidate)
        else:
            # Rest epoch: PAC should approach target_rest
            denominator = target_rest - pac_t
            if abs(denominator) > EPSILON:
                tau_candidate = delta / denominator
                if 0 < tau_candidate <= 1:
                    decay_candidates.append(tau_candidate)

    result: dict = {
        "tau_rise": None,
        "tau_decay": None,
        "n_rise_transitions": len(rise_candidates),
        "n_decay_transitions": len(decay_candidates),
        "n_epochs": int(len(epoch_pac)),
        "rise_candidates": rise_candidates,
        "decay_candidates": decay_candidates,
    }

    if len(rise_candidates) >= MIN_VALID_CANDIDATES:
        result["tau_rise"] = float(np.median(rise_candidates))

    # Per-subject decay: report if at least 1 valid candidate
    if len(decay_candidates) >= 1:
        result["tau_decay"] = float(np.median(decay_candidates))

    return result


def fit_population_tau(
    data: dict[str, np.ndarray],
    verbose: bool,
) -> dict:
    """Fit tau parameters across all subjects.

    Groups sequences by subject, reconstructs temporal order via end_idx,
    collapses to epoch-level PAC, and fits per-subject tau values.
    Aggregates with population median and IQR.
    """
    subjects = data["subjects"]
    unique_subjects = np.unique(subjects)
    logger.info("Fitting tau for %d subjects", len(unique_subjects))

    per_subject_results = []
    all_tau_rise = []
    all_tau_decay = []
    # Pool all valid decay candidates across subjects for robust
    # population estimate. Rest epochs are fewer than stim epochs in
    # ds005048 (20s rest vs 40s stim blocks), so per-subject decay
    # counts are often 0-2 valid candidates. Pooling gives a reliable
    # population median.
    pooled_decay_candidates: list[float] = []

    for subj in sorted(unique_subjects):
        mask = subjects == subj
        end_idx = data["end_idx"][mask]
        last_pac = data["last_pac"][mask]
        stim_raw = data["stim_state"][mask]

        # Sort by end_idx to reconstruct temporal order
        sort_order = np.argsort(end_idx)
        pac_sorted = last_pac[sort_order]
        stim_sorted = stim_raw[sort_order]

        # Convert z-scored stim_state to binary (positive = stim = 1)
        stim_binary = (stim_sorted > 0).astype(int)

        # Collapse to epoch-level (PAC is constant within epochs)
        epoch_pac, epoch_stim = collapse_to_epochs(pac_sorted, stim_binary)

        # Per-subject targets: robust max/min via percentiles
        target_stim = float(np.percentile(epoch_pac, 90))
        target_rest = float(np.percentile(epoch_pac, 10))

        result = fit_subject_tau(
            epoch_pac, epoch_stim, target_stim, target_rest
        )
        result["subject"] = str(subj)

        # Collect pooled decay candidates before removing raw lists
        pooled_decay_candidates.extend(result["decay_candidates"])

        # Remove raw candidate lists before storing in per_subject output
        del result["rise_candidates"]
        del result["decay_candidates"]

        per_subject_results.append(result)

        if result["tau_rise"] is not None:
            all_tau_rise.append(result["tau_rise"])
        if result["tau_decay"] is not None:
            all_tau_decay.append(result["tau_decay"])

        if verbose:
            rise_str = (
                f"{result['tau_rise']:.4f}" if result["tau_rise"] else "N/A"
            )
            decay_str = (
                f"{result['tau_decay']:.4f}" if result["tau_decay"] else "N/A"
            )
            print(
                f"  {subj}: tau_rise={rise_str} "
                f"(n={result['n_rise_transitions']}), "
                f"tau_decay={decay_str} "
                f"(n={result['n_decay_transitions']}), "
                f"epochs={result['n_epochs']}"
            )

    # Population aggregation
    population = {}

    # tau_rise: per-subject medians aggregated
    if all_tau_rise:
        arr = np.array(all_tau_rise)
        population["tau_rise_median"] = float(np.median(arr))
        population["tau_rise_q25"] = float(np.percentile(arr, 25))
        population["tau_rise_q75"] = float(np.percentile(arr, 75))
        population["tau_rise_n_subjects"] = len(arr)
    else:
        raise ValueError("No subjects had sufficient rise transitions")

    # tau_decay: pooled across subjects because rest epochs are sparse
    # (0-2 valid candidates per subject). The pooled approach is more
    # robust than per-subject medians when individual counts are low.
    n_decay_subjects = len(all_tau_decay)
    if pooled_decay_candidates:
        arr = np.array(pooled_decay_candidates)
        population["tau_decay_median"] = float(np.median(arr))
        population["tau_decay_q25"] = float(np.percentile(arr, 25))
        population["tau_decay_q75"] = float(np.percentile(arr, 75))
        population["tau_decay_n_subjects"] = n_decay_subjects
        population["tau_decay_n_pooled"] = len(arr)
        population["tau_decay_method"] = "pooled_across_subjects"
    else:
        raise ValueError("No valid decay transitions found across any subject")

    population["heuristic_tau_rise"] = HEURISTIC_TAU_RISE
    population["heuristic_tau_decay"] = HEURISTIC_TAU_DECAY
    population["per_subject"] = per_subject_results
    population["fit_method"] = "exponential_approach_median_per_subject"
    population["data_source"] = "multiscale_temporal_lb20_hz5_ts1"

    return population


def print_results(results: dict) -> None:
    """Print formatted results table to stdout."""
    tau_r = results["tau_rise_median"]
    tau_d = results["tau_decay_median"]
    r_q25 = results["tau_rise_q25"]
    r_q75 = results["tau_rise_q75"]
    d_q25 = results["tau_decay_q25"]
    d_q75 = results["tau_decay_q75"]
    n_rise = results["tau_rise_n_subjects"]
    n_decay = results["tau_decay_n_subjects"]
    n_pooled = results.get("tau_decay_n_pooled", n_decay)

    # Time constants: T = -1/ln(1-tau)
    tc_rise = -1.0 / np.log(1.0 - tau_r)
    tc_decay = -1.0 / np.log(1.0 - tau_d)

    n_total = len(results["per_subject"])

    print()
    print("=== Simulator Tau Parameter Fitting ===")
    print(f"Dataset: multiscale_temporal_lb20_hz5_ts1 (N={n_total} subjects)")
    print()
    print("Population estimates:")
    print(
        f"  tau_rise:  {tau_r:.4f} "
        f"(IQR: {r_q25:.4f}-{r_q75:.4f}, n={n_rise} subjects)"
    )
    print(
        f"  tau_decay: {tau_d:.4f} "
        f"(IQR: {d_q25:.4f}-{d_q75:.4f}, "
        f"n={n_pooled} pooled from {n_decay} subjects)"
    )
    print()
    print("Comparison with heuristic defaults:")
    print(
        f"  tau_rise:  fitted={tau_r:.4f}  vs  "
        f"heuristic={HEURISTIC_TAU_RISE:.2f}  "
        f"(ratio: {tau_r / HEURISTIC_TAU_RISE:.2f}x)"
    )
    print(
        f"  tau_decay: fitted={tau_d:.4f}  vs  "
        f"heuristic={HEURISTIC_TAU_DECAY:.2f}  "
        f"(ratio: {tau_d / HEURISTIC_TAU_DECAY:.2f}x)"
    )
    print()
    print("Time constants (T = -1/ln(1-tau)):")
    print(
        f"  tau_rise  = {tau_r:.4f} -> T={tc_rise:.1f}s  "
        f"(heuristic: 6.2s)"
    )
    print(
        f"  tau_decay = {tau_d:.4f} -> T={tc_decay:.1f}s  "
        f"(heuristic: 9.5s)"
    )
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fit simulator tau_rise/tau_decay from real PAC data"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/processed/multiscale_temporal_lb20_hz5_ts1"),
        help="Path to multiscale temporal dataset directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/metrics/simulator_tau_fit.json"),
        help="Output JSON path for fitted parameters",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-subject breakdown",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    if not args.data_dir.exists():
        raise FileNotFoundError(f"Dataset not found: {args.data_dir}")

    # Load all splits
    data = load_all_splits(args.data_dir)
    logger.info(
        "Loaded %d sequences across %d subjects",
        len(data["last_pac"]),
        len(np.unique(data["subjects"])),
    )

    # Fit tau parameters
    results = fit_population_tau(data, args.verbose)

    # Print summary
    print_results(results)

    # Save JSON
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    logger.info("Saved results to %s", args.output)


if __name__ == "__main__":
    main()
