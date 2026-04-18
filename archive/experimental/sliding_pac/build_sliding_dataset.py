"""
Build temporal dataset using sliding-window PAC labels.

Constructs 20-step lookback sequences with 12 PAC+Stim features,
using sliding-window PAC values (from compute_sliding_pac.py) instead
of epoch-level PAC. Maintains the same subject-level train/val/test splits
(24/5/6 subjects) as the original pipeline.

Features (12 total, matching indices 61-72 of the 73-feature original):
    0-6:  PAC multiscale features (pac_current, pac_ma2, pac_ma4, pac_ma8,
          pac_ma16, pac_diff1, pac_diff4)  -- computed from sliding PAC
    7-11: Stim context (stim_state, time_since_switch_60s, stim_frac_20s,
          cycle_phase_sin, cycle_phase_cos)

Targets: y_future = sliding PAC at position t + horizon
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


# -- Causal feature computation (mirrors build_multiscale_dataset.py) --------

def _causal_moving_average(x: np.ndarray, window: int) -> np.ndarray:
    """Causal trailing average including the current sample."""
    x = x.astype(np.float64, copy=False)
    csum = np.cumsum(x)
    out = np.empty_like(x)
    for i in range(len(x)):
        lo = max(0, i - window + 1)
        total = csum[i] - (csum[lo - 1] if lo > 0 else 0.0)
        out[i] = total / (i - lo + 1)
    return out


def _pac_multiscale_features(pac: np.ndarray) -> Tuple[np.ndarray, List[str]]:
    """Causal PAC-derived features from past/current values only."""
    pac = pac.astype(np.float64, copy=False)
    ma2 = _causal_moving_average(pac, 2)
    ma4 = _causal_moving_average(pac, 4)
    ma8 = _causal_moving_average(pac, 8)
    ma16 = _causal_moving_average(pac, 16)

    diff1 = np.zeros_like(pac)
    diff4 = np.zeros_like(pac)
    diff1[1:] = pac[1:] - pac[:-1]
    diff4[4:] = pac[4:] - pac[:-4]

    x = np.stack([pac, ma2, ma4, ma8, ma16, diff1, diff4], axis=1)
    names = [
        "pac_current",
        "pac_ma2",
        "pac_ma4",
        "pac_ma8",
        "pac_ma16",
        "pac_diff1",
        "pac_diff4",
    ]
    return x, names


def _subject_events(raw_root: Path, subject: str) -> pd.DataFrame:
    """Load BIDS events TSV for a subject."""
    tsv = raw_root / subject / "eeg" / f"{subject}_task-40HzAuditoryEntrainment_events.tsv"
    if not tsv.exists():
        raise FileNotFoundError(f"Missing events file for {subject}: {tsv}")

    events = pd.read_csv(tsv, sep="\t")
    required = {"onset", "duration", "value"}
    missing = required - set(events.columns)
    if missing:
        raise ValueError(f"{tsv} missing columns: {sorted(missing)}")

    events = events.sort_values("onset").reset_index(drop=True)
    events["state"] = (events["value"].astype(int) == 2).astype(np.float64)
    return events


def _stim_context_from_events(
    events: pd.DataFrame,
    n_windows: int,
    window_sec: float,
    hop_sec: float,
    stim_history_sec: int,
) -> Tuple[np.ndarray, List[str]]:
    """Build causal stimulation-context features for each window."""
    t = np.arange(n_windows, dtype=np.float64) * hop_sec + window_sec / 2.0
    state = np.zeros(n_windows, dtype=np.float64)

    for _, row in events.iterrows():
        onset = float(row["onset"])
        duration = float(row["duration"])
        stim_state = float(row["state"])
        in_event = (t >= onset) & (t < onset + duration)
        state[in_event] = stim_state

    switch_onsets = np.unique(
        np.concatenate([[0.0], events["onset"].to_numpy(dtype=np.float64)])
    )
    idx = np.searchsorted(switch_onsets, t, side="right") - 1
    idx = np.clip(idx, 0, len(switch_onsets) - 1)
    last_switch = switch_onsets[idx]
    time_since_switch = np.maximum(0.0, t - last_switch)

    history_n = max(1, int(round(stim_history_sec / hop_sec)))
    stim_frac_recent = _causal_moving_average(state, history_n)

    cycle = 60.0
    phase = (t % cycle) / cycle
    phase_sin = np.sin(2.0 * np.pi * phase)
    phase_cos = np.cos(2.0 * np.pi * phase)

    ctx = np.stack(
        [
            state,
            np.minimum(time_since_switch / 60.0, 1.0),
            stim_frac_recent,
            phase_sin,
            phase_cos,
        ],
        axis=1,
    )
    names = [
        "stim_state",
        "time_since_switch_60s",
        f"stim_frac_{stim_history_sec}s",
        "cycle_phase_sin",
        "cycle_phase_cos",
    ]
    return ctx, names


# -- Dataset builder ---------------------------------------------------------

def build_sliding_dataset(
    pac_labels_dir: Path,
    raw_root: Path,
    processed_dir: Path,
    output_dir: Path,
    lookback: int,
    horizon: int,
    window_sec: float,
    hop_sec: float,
    stim_history_sec: int,
) -> Dict[str, int]:
    """
    Build temporal dataset with sliding-window PAC targets and features.

    Returns:
        Dictionary with sample counts per split.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("BUILD SLIDING-PAC TEMPORAL DATASET")
    print("=" * 70)
    print(f"  PAC labels:     {pac_labels_dir}")
    print(f"  Raw root:       {raw_root}")
    print(f"  Output:         {output_dir}")
    print(f"  Lookback:       {lookback}")
    print(f"  Horizon:        {horizon}")
    print()

    splits_data: Dict[str, Dict[str, np.ndarray]] = {}

    for split in ["train", "val", "test"]:
        # Load sliding PAC labels
        pac_data = np.load(
            pac_labels_dir / f"{split}_sliding_pac.npz", allow_pickle=True
        )
        sliding_pac = pac_data["sliding_pac"].astype(np.float64)
        subjects = pac_data["subjects"]

        # Load original processed data for subject info
        orig = np.load(processed_dir / f"{split}_data.npz", allow_pickle=True)
        orig_subjects = orig["subjects"]

        # Verify subjects match
        assert np.array_equal(subjects, orig_subjects), (
            f"{split}: subject arrays do not match between PAC labels and processed data"
        )

        # Build sequences per subject
        seq_list: List[np.ndarray] = []
        y_future_list: List[float] = []
        y_delta_list: List[float] = []
        last_pac_list: List[float] = []
        out_subjects: List[str] = []
        feature_names: List[str] | None = None

        unique_subjects = np.unique(subjects)

        for subject in unique_subjects:
            idx = np.where(subjects == subject)[0]
            if len(idx) < (lookback + horizon):
                continue
            if not np.all(np.diff(idx) == 1):
                raise ValueError(
                    f"{split}: non-contiguous rows for {subject}"
                )

            s0, s1 = int(idx[0]), int(idx[-1]) + 1
            subj_pac = sliding_pac[s0:s1]

            # Build stim context features
            events = _subject_events(raw_root, subject)
            ctx, ctx_names = _stim_context_from_events(
                events=events,
                n_windows=len(subj_pac),
                window_sec=window_sec,
                hop_sec=hop_sec,
                stim_history_sec=stim_history_sec,
            )

            # Build PAC multiscale features from sliding PAC
            pac_feats, pac_names = _pac_multiscale_features(subj_pac)

            # Concatenate: 7 PAC features + 5 stim features = 12
            step_feat = np.concatenate([pac_feats, ctx], axis=1)
            if feature_names is None:
                feature_names = pac_names + ctx_names

            # Build causal sequence samples
            for t in range(lookback - 1, len(subj_pac) - horizon):
                local_start = t - lookback + 1
                local_end = t
                local_target = t + horizon

                seq = step_feat[local_start:local_end + 1]
                seq_list.append(seq.astype(np.float32))

                yf = float(subj_pac[local_target])
                yc = float(subj_pac[local_end])
                y_future_list.append(yf)
                y_delta_list.append(yf - yc)
                last_pac_list.append(yc)
                out_subjects.append(subject)

        if feature_names is None:
            raise RuntimeError(f"No samples created for split={split}")

        splits_data[split] = {
            "x_seq": np.asarray(seq_list, dtype=np.float32),
            "y_future": np.asarray(y_future_list, dtype=np.float32),
            "y_delta": np.asarray(y_delta_list, dtype=np.float32),
            "last_pac": np.asarray(last_pac_list, dtype=np.float32),
            "subjects": np.asarray(out_subjects),
            "feature_names": np.asarray(feature_names),
        }

        print(f"  {split}: x={splits_data[split]['x_seq'].shape}, "
              f"y_future unique={len(np.unique(splits_data[split]['y_future']))}")

    # Normalize with train stats
    x_train = splits_data["train"]["x_seq"].astype(np.float64)
    feat_mean = x_train.reshape(-1, x_train.shape[-1]).mean(axis=0)
    feat_std = x_train.reshape(-1, x_train.shape[-1]).std(axis=0) + 1e-8

    yf_mean = float(splits_data["train"]["y_future"].mean())
    yf_std = float(splits_data["train"]["y_future"].std()) + 1e-8
    yd_mean = float(splits_data["train"]["y_delta"].mean())
    yd_std = float(splits_data["train"]["y_delta"].std()) + 1e-8

    scalers = {
        "feature_mean": feat_mean.astype(np.float64),
        "feature_std": feat_std.astype(np.float64),
        "y_future_mean": np.float64(yf_mean),
        "y_future_std": np.float64(yf_std),
        "y_delta_mean": np.float64(yd_mean),
        "y_delta_std": np.float64(yd_std),
    }

    counts = {}
    for split in ["train", "val", "test"]:
        d = splits_data[split]
        d["x_seq"] = ((d["x_seq"] - feat_mean) / feat_std).astype(np.float32)
        d["y_future_norm"] = ((d["y_future"] - yf_mean) / yf_std).astype(np.float32)
        d["y_delta_norm"] = ((d["y_delta"] - yd_mean) / yd_std).astype(np.float32)

        np.savez_compressed(output_dir / f"{split}_multiscale.npz", **d)
        counts[split] = int(d["x_seq"].shape[0])

    np.savez_compressed(output_dir / "scalers.npz", **scalers)

    metadata = {
        "lookback": lookback,
        "horizon": horizon,
        "window_sec": window_sec,
        "hop_sec": hop_sec,
        "stim_history_sec": stim_history_sec,
        "target_smooth_window": 1,
        "n_features": int(splits_data["train"]["x_seq"].shape[-1]),
        "n_train": counts["train"],
        "n_val": counts["val"],
        "n_test": counts["test"],
        "feature_names": list(splits_data["train"]["feature_names"]),
        "pac_type": "sliding_window",
        "train_subjects": sorted(np.unique(splits_data["train"]["subjects"]).tolist()),
        "val_subjects": sorted(np.unique(splits_data["val"]["subjects"]).tolist()),
        "test_subjects": sorted(np.unique(splits_data["test"]["subjects"]).tolist()),
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print(f"\n  Saved to {output_dir}")
    print(f"  Features: {metadata['n_features']}")
    print(f"  Train/Val/Test: {counts['train']}/{counts['val']}/{counts['test']}")

    return counts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build temporal dataset with sliding-window PAC."
    )
    parser.add_argument(
        "--pac-labels-dir", type=str,
        default="experimental/sliding_pac/pac_labels",
    )
    parser.add_argument("--raw-root", type=str, default="data/raw/ds005048")
    parser.add_argument("--processed-dir", type=str, default="data/processed")
    parser.add_argument(
        "--output-dir", type=str,
        default="experimental/sliding_pac/dataset",
    )
    parser.add_argument("--lookback", type=int, default=20)
    parser.add_argument("--horizon", type=int, default=5)
    parser.add_argument("--stim-history-sec", type=int, default=20)
    args = parser.parse_args()

    build_sliding_dataset(
        pac_labels_dir=Path(args.pac_labels_dir),
        raw_root=Path(args.raw_root),
        processed_dir=Path(args.processed_dir),
        output_dir=Path(args.output_dir),
        lookback=args.lookback,
        horizon=args.horizon,
        window_sec=2.0,
        hop_sec=1.0,
        stim_history_sec=args.stim_history_sec,
    )


if __name__ == "__main__":
    main()
