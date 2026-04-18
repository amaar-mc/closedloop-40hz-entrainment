"""
Build enhanced multiscale temporal datasets for PAC forecasting.

Extends the base spectral dataset (build_multiscale_dataset.py) by appending
time-domain enhanced features (Hjorth parameters, sample entropy, zero-crossing
rate) per channel to each feature vector.

Feature composition (7ch):
    61 spectral + 35 enhanced (5 feats × 7ch) + 7 PAC-derived + 5 stim context = 108

Feature composition (4ch):
    37 spectral + 20 enhanced (5 feats × 4ch) + 7 PAC-derived + 5 stim context = 69

Outputs mirror the original multiscale dataset format so existing SequenceDataset
and training code loads them without modification.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

# Path discovery — supports running as script or as module
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from temporal_multiscale.build_multiscale_dataset import (
    _build_split_samples,
    _causal_moving_average,
    _causal_target_smooth,
    _load_spectral_cache,
    _load_split,
    _normalize_with_train_stats,
    _pac_multiscale_features,
    _stim_context_from_events,
    _subject_events,
)

from improved_tcn.enhanced_features import extract_enhanced_features_batch


def _build_split_samples_enhanced(
    split_name: str,
    split: Dict[str, np.ndarray],
    spectral: np.ndarray,
    enhanced: np.ndarray,
    raw_root: Path,
    lookback: int,
    horizon: int,
    window_sec: float,
    hop_sec: float,
    stim_history_sec: int,
    target_smooth_window: int,
) -> Dict[str, np.ndarray]:
    """
    Build sequence samples with enhanced features concatenated after spectral.

    Feature vector per step:
        [spectral (F_spec)] + [enhanced (5*C)] + [pac_feats (7)] + [stim_ctx (5)]
    """
    subjects = split["subjects"]
    pac = split["pac"]

    seq_list: List[np.ndarray] = []
    y_future: List[float] = []
    y_delta: List[float] = []
    last_pac: List[float] = []
    out_subjects: List[str] = []
    start_idx: List[int] = []
    end_idx: List[int] = []
    target_idx: List[int] = []

    unique_subjects = np.unique(subjects)
    feature_names: List[str] | None = None

    n_spectral = spectral.shape[1]
    n_enhanced = enhanced.shape[1]

    for subject in unique_subjects:
        idx = np.where(subjects == subject)[0]
        if len(idx) < (lookback + horizon):
            continue
        if not np.all(np.diff(idx) == 1):
            raise ValueError(f"{split_name}: non-contiguous rows for {subject}")

        s0, s1 = int(idx[0]), int(idx[-1]) + 1
        subj_pac_raw = pac[s0:s1]
        subj_pac = _causal_target_smooth(subj_pac_raw, target_smooth_window)
        subj_spec = spectral[s0:s1]
        subj_enh = enhanced[s0:s1]

        events = _subject_events(raw_root, subject)
        ctx, ctx_names = _stim_context_from_events(
            events=events,
            n_windows=len(subj_pac),
            window_sec=window_sec,
            hop_sec=hop_sec,
            stim_history_sec=stim_history_sec,
        )
        pac_feats, pac_names = _pac_multiscale_features(subj_pac)

        # Per-step feature vector: spectral + enhanced + pac + stim_ctx
        step_feat = np.concatenate([subj_spec, subj_enh, pac_feats, ctx], axis=1)

        if feature_names is None:
            n_ch = n_enhanced // 5
            enh_names: List[str] = []
            for ch in range(n_ch):
                for feat in [
                    "hjorth_activity",
                    "hjorth_mobility",
                    "hjorth_complexity",
                    "sample_entropy",
                    "zcr",
                ]:
                    enh_names.append(f"{feat}_{ch}")

            feature_names = (
                [f"spectral_{i:02d}" for i in range(n_spectral)]
                + enh_names
                + pac_names
                + ctx_names
            )

        # Build causal sequence samples
        for t in range(lookback - 1, len(subj_pac) - horizon):
            local_start = t - lookback + 1
            local_end = t
            local_target = t + horizon

            seq = step_feat[local_start : local_end + 1]
            seq_list.append(seq.astype(np.float32))

            yf = float(subj_pac[local_target])
            yc = float(subj_pac[local_end])
            y_future.append(yf)
            y_delta.append(yf - yc)
            last_pac.append(yc)

            out_subjects.append(subject)
            start_idx.append(local_start)
            end_idx.append(local_end)
            target_idx.append(local_target)

    if feature_names is None:
        raise RuntimeError(f"No samples created for split={split_name}.")

    return {
        "x_seq": np.asarray(seq_list, dtype=np.float32),
        "y_future": np.asarray(y_future, dtype=np.float32),
        "y_delta": np.asarray(y_delta, dtype=np.float32),
        "last_pac": np.asarray(last_pac, dtype=np.float32),
        "subjects": np.asarray(out_subjects),
        "start_idx": np.asarray(start_idx, dtype=np.int32),
        "end_idx": np.asarray(end_idx, dtype=np.int32),
        "target_idx": np.asarray(target_idx, dtype=np.int32),
        "feature_names": np.asarray(feature_names),
    }


def build_enhanced_dataset(
    processed_dir: Path,
    raw_root: Path,
    output_dir: Path,
    lookback: int = 20,
    horizon: int = 5,
    window_sec: float = 2.0,
    hop_sec: float = 1.0,
    stim_history_sec: int = 20,
    target_smooth_window: int = 1,
) -> Dict[str, int]:
    """
    Build an enhanced multiscale temporal dataset.

    Loads existing spectral cache, computes enhanced time-domain features from
    raw EEG windows, concatenates them, and saves the combined dataset.

    Returns:
        Dict with n_features, n_train, n_val, n_test counts.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("BUILD ENHANCED MULTISCALE TEMPORAL DATASET")
    print("=" * 80)
    print(f"processed_dir: {processed_dir}")
    print(f"raw_root:      {raw_root}")
    print(f"output_dir:    {output_dir}")
    print(f"lookback:      {lookback}")
    print(f"horizon:       {horizon}")
    print(f"window_sec:    {window_sec}")
    print(f"hop_sec:       {hop_sec}")
    print(f"stim_history:  {stim_history_sec}s")
    print(f"target_smooth_window: {target_smooth_window}")
    print()

    splits: Dict[str, Dict[str, np.ndarray]] = {}
    spectral: Dict[str, np.ndarray] = {}
    enhanced: Dict[str, np.ndarray] = {}

    for split in ["train", "val", "test"]:
        print(f"Loading {split} split...")
        splits[split] = _load_split(processed_dir, split)
        spectral[split] = _load_spectral_cache(
            processed_dir, split, n_rows=len(splits[split]["pac"])
        )

        print(f"  Computing enhanced features for {split} ({len(splits[split]['pac'])} windows)...")
        enhanced[split] = extract_enhanced_features_batch(splits[split]["windows"])
        n_enh = enhanced[split].shape[1]
        n_ch = n_enh // 5
        print(f"  Enhanced features: {enhanced[split].shape} ({n_ch} channels × 5 feats)")

    built = {}
    for split in ["train", "val", "test"]:
        print(f"\nBuilding sequence samples for {split}...")
        built[split] = _build_split_samples_enhanced(
            split_name=split,
            split=splits[split],
            spectral=spectral[split],
            enhanced=enhanced[split],
            raw_root=raw_root,
            lookback=lookback,
            horizon=horizon,
            window_sec=window_sec,
            hop_sec=hop_sec,
            stim_history_sec=stim_history_sec,
            target_smooth_window=target_smooth_window,
        )
        print(
            f"  {split}: x_seq={built[split]['x_seq'].shape}, "
            f"y_future={built[split]['y_future'].shape}"
        )

    print("\nNormalising with train statistics...")
    train_norm, val_norm, test_norm, scalers = _normalize_with_train_stats(
        built["train"], built["val"], built["test"]
    )

    print("Saving datasets...")
    for split_name, split_data in [
        ("train", train_norm),
        ("val", val_norm),
        ("test", test_norm),
    ]:
        out_path = output_dir / f"{split_name}_multiscale.npz"
        np.savez_compressed(out_path, **split_data)
        print(f"  Saved {out_path}")

    scalers_path = output_dir / "scalers.npz"
    np.savez_compressed(scalers_path, **scalers)
    print(f"  Saved {scalers_path}")

    metadata = {
        "lookback": lookback,
        "horizon": horizon,
        "window_sec": window_sec,
        "hop_sec": hop_sec,
        "stim_history_sec": stim_history_sec,
        "target_smooth_window": target_smooth_window,
        "n_features": int(train_norm["x_seq"].shape[-1]),
        "n_train": int(train_norm["x_seq"].shape[0]),
        "n_val": int(val_norm["x_seq"].shape[0]),
        "n_test": int(test_norm["x_seq"].shape[0]),
        "train_subjects": sorted(np.unique(train_norm["subjects"]).tolist()),
        "val_subjects": sorted(np.unique(val_norm["subjects"]).tolist()),
        "test_subjects": sorted(np.unique(test_norm["subjects"]).tolist()),
        "feature_source": "spectral + enhanced_time_domain + pac_derived + stim_context",
    }
    meta_path = output_dir / "metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2))
    print(f"  Saved {meta_path}")

    print(f"\n[DONE] n_features={metadata['n_features']}, "
          f"train={metadata['n_train']}, "
          f"val={metadata['n_val']}, "
          f"test={metadata['n_test']}")

    return {
        "n_features": metadata["n_features"],
        "n_train": metadata["n_train"],
        "n_val": metadata["n_val"],
        "n_test": metadata["n_test"],
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build enhanced multiscale temporal dataset with time-domain features."
    )
    p.add_argument(
        "--processed-dir",
        default="data/processed",
        type=str,
        help="Directory containing {split}_data.npz and {split}_spectral_cache.npy files.",
    )
    p.add_argument(
        "--raw-root",
        default="data/raw/ds005048",
        type=str,
        help="BIDS raw data root (for events.tsv files).",
    )
    p.add_argument(
        "--output-dir",
        default="data/processed/enhanced_multiscale_7ch",
        type=str,
        help="Output directory for enhanced dataset.",
    )
    p.add_argument("--lookback", default=20, type=int)
    p.add_argument("--horizon", default=5, type=int)
    p.add_argument("--window-sec", default=2.0, type=float)
    p.add_argument("--hop-sec", default=1.0, type=float)
    p.add_argument("--stim-history-sec", default=20, type=int)
    p.add_argument("--target-smooth-window", default=1, type=int)
    p.add_argument(
        "--muse-4ch",
        action="store_true",
        help=(
            "When set, overrides --processed-dir to data/processed/muse_4ch "
            "and --output-dir to data/processed/muse_4ch/enhanced_multiscale "
            "(unless those are already explicitly provided)."
        ),
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    processed_dir = args.processed_dir
    output_dir = args.output_dir

    # Apply muse-4ch defaults only if the user did not explicitly override them
    if args.muse_4ch:
        if processed_dir == "data/processed":
            processed_dir = "data/processed/muse_4ch"
        if output_dir == "data/processed/enhanced_multiscale_7ch":
            output_dir = "data/processed/muse_4ch/enhanced_multiscale"

    build_enhanced_dataset(
        processed_dir=Path(processed_dir),
        raw_root=Path(args.raw_root),
        output_dir=Path(output_dir),
        lookback=args.lookback,
        horizon=args.horizon,
        window_sec=args.window_sec,
        hop_sec=args.hop_sec,
        stim_history_sec=args.stim_history_sec,
        target_smooth_window=args.target_smooth_window,
    )


if __name__ == "__main__":
    main()
