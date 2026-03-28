"""
Extract 12 PAC+Stim features from the existing 73-feature multiscale dataset
to create a fair comparison baseline for the sliding-window PAC experiment.

Features extracted (indices 61-72 of the 73-feature dataset):
    61-67: pac_current, pac_ma2, pac_ma4, pac_ma8, pac_ma16, pac_diff1, pac_diff4
    68-72: stim_state, time_since_switch_60s, stim_frac_20s, cycle_phase_sin, cycle_phase_cos

The targets (y_future, y_delta) and their normalization are recomputed
from the 12-feature subset to match how the sliding dataset is built.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


PAC_STIM_START = 61
PAC_STIM_END = 73  # exclusive, 12 features


def build_original_12feat(
    source_dir: Path,
    output_dir: Path,
) -> None:
    """
    Extract 12 PAC+Stim features and re-normalize from scratch.

    This ensures the comparison is fair: both datasets use the same
    12 features, same lookback/horizon, same subjects, same normalization
    approach (fit on train, apply to all).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    splits_data = {}

    for split in ["train", "val", "test"]:
        d = np.load(source_dir / f"{split}_multiscale.npz", allow_pickle=True)

        # Extract 12 PAC+Stim features from the normalized 73-feature sequences
        # BUT we need to re-normalize from raw, so we need to denormalize first.
        # Easier: go back to raw values using the existing scalers
        x_full = d["x_seq"]  # (N, T, 73) -- already normalized

        # Denormalize features
        scalers_orig = np.load(source_dir / "scalers.npz")
        feat_mean = scalers_orig["feature_mean"]
        feat_std = scalers_orig["feature_std"]

        # Denorm: x_raw = x_norm * std + mean
        x_raw = x_full.astype(np.float64) * feat_std + feat_mean

        # Extract PAC+Stim columns
        x_12_raw = x_raw[:, :, PAC_STIM_START:PAC_STIM_END]

        # Raw targets (denorm)
        yf_mean_orig = float(scalers_orig["y_future_mean"])
        yf_std_orig = float(scalers_orig["y_future_std"])
        yd_mean_orig = float(scalers_orig["y_delta_mean"])
        yd_std_orig = float(scalers_orig["y_delta_std"])

        y_future_raw = d["y_future_norm"].astype(np.float64) * yf_std_orig + yf_mean_orig
        y_delta_raw = d["y_delta_norm"].astype(np.float64) * yd_std_orig + yd_mean_orig
        last_pac_raw = d["last_pac"].astype(np.float64)

        splits_data[split] = {
            "x_12_raw": x_12_raw,
            "y_future": y_future_raw.astype(np.float32),
            "y_delta": y_delta_raw.astype(np.float32),
            "last_pac": last_pac_raw.astype(np.float32),
            "subjects": d["subjects"],
        }

    # Re-normalize with train stats on the 12 features
    x_train = splits_data["train"]["x_12_raw"]
    feat_mean_12 = x_train.reshape(-1, 12).mean(axis=0)
    feat_std_12 = x_train.reshape(-1, 12).std(axis=0) + 1e-8

    yf_mean = float(splits_data["train"]["y_future"].mean())
    yf_std = float(splits_data["train"]["y_future"].std()) + 1e-8
    yd_mean = float(splits_data["train"]["y_delta"].mean())
    yd_std = float(splits_data["train"]["y_delta"].std()) + 1e-8

    scalers = {
        "feature_mean": feat_mean_12.astype(np.float64),
        "feature_std": feat_std_12.astype(np.float64),
        "y_future_mean": np.float64(yf_mean),
        "y_future_std": np.float64(yf_std),
        "y_delta_mean": np.float64(yd_mean),
        "y_delta_std": np.float64(yd_std),
    }

    feature_names = [
        "pac_current", "pac_ma2", "pac_ma4", "pac_ma8", "pac_ma16",
        "pac_diff1", "pac_diff4",
        "stim_state", "time_since_switch_60s", "stim_frac_20s",
        "cycle_phase_sin", "cycle_phase_cos",
    ]

    for split in ["train", "val", "test"]:
        d = splits_data[split]
        x_norm = ((d["x_12_raw"] - feat_mean_12) / feat_std_12).astype(np.float32)
        y_future_norm = ((d["y_future"] - yf_mean) / yf_std).astype(np.float32)
        y_delta_norm = ((d["y_delta"] - yd_mean) / yd_std).astype(np.float32)

        np.savez_compressed(
            output_dir / f"{split}_multiscale.npz",
            x_seq=x_norm,
            y_future=d["y_future"],
            y_delta=d["y_delta"],
            y_future_norm=y_future_norm,
            y_delta_norm=y_delta_norm,
            last_pac=d["last_pac"],
            subjects=d["subjects"],
            feature_names=np.array(feature_names),
        )

    np.savez_compressed(output_dir / "scalers.npz", **scalers)

    # Read source metadata for subject lists
    source_meta = json.loads((source_dir / "metadata.json").read_text())

    metadata = {
        "lookback": source_meta["lookback"],
        "horizon": source_meta["horizon"],
        "window_sec": source_meta["window_sec"],
        "hop_sec": source_meta["hop_sec"],
        "stim_history_sec": source_meta["stim_history_sec"],
        "target_smooth_window": source_meta.get("target_smooth_window", 1),
        "n_features": 12,
        "n_train": int(splits_data["train"]["x_12_raw"].shape[0]),
        "n_val": int(splits_data["val"]["x_12_raw"].shape[0]),
        "n_test": int(splits_data["test"]["x_12_raw"].shape[0]),
        "feature_names": feature_names,
        "pac_type": "epoch_level",
        "train_subjects": source_meta["train_subjects"],
        "val_subjects": source_meta["val_subjects"],
        "test_subjects": source_meta["test_subjects"],
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print(f"Built original 12-feature dataset at {output_dir}")
    for split in ["train", "val", "test"]:
        n = splits_data[split]["x_12_raw"].shape[0]
        print(f"  {split}: {n} samples, 12 features")


if __name__ == "__main__":
    source = Path("data/processed/multiscale_temporal_lb20_hz5_ts1")
    output = Path("experimental/sliding_pac/dataset_original")
    build_original_12feat(source, output)
