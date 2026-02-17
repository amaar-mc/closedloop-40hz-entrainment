"""
Build leakage-safe multiscale temporal datasets for PAC forecasting.

Core design:
- Uses existing subject-level splits in data/processed/{train,val,test}_data.npz.
- Adds stimulation-context features from BIDS events.tsv (value: 1=rest, 2=stim).
- Builds causal multiscale PAC history features (no future information).
- Creates sequence samples: X[t-lookback+1:t] -> y[t+horizon].

Outputs:
- data/processed/multiscale_temporal/{train,val,test}_multiscale.npz
- data/processed/multiscale_temporal/scalers.npz
- data/processed/multiscale_temporal/metadata.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


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


def _load_split(base_dir: Path, split: str) -> Dict[str, np.ndarray]:
    data = np.load(base_dir / f"{split}_data.npz")
    out = {
        "windows": data["windows"],
        "pac": data["pac"].astype(np.float64),
        "subjects": data["subjects"],
    }
    return out


def _load_spectral_cache(base_dir: Path, split: str, n_rows: int) -> np.ndarray:
    cache_path = base_dir / f"{split}_spectral_cache.npy"
    if not cache_path.exists():
        raise FileNotFoundError(
            f"Missing spectral cache: {cache_path}. "
            "Generate it first with existing temporal pipeline."
        )
    spectral = np.load(cache_path).astype(np.float64)
    if spectral.shape[0] != n_rows:
        raise ValueError(
            f"Spectral rows ({spectral.shape[0]}) do not match split rows ({n_rows}) "
            f"for {split}."
        )
    return spectral


def _subject_events(raw_root: Path, subject: str) -> pd.DataFrame:
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
    """
    Build causal stimulation-context features for each window.

    Time reference for each window is its center:
        t_i = i*hop + window_sec/2
    """
    t = np.arange(n_windows, dtype=np.float64) * hop_sec + window_sec / 2.0
    state = np.zeros(n_windows, dtype=np.float64)

    for _, row in events.iterrows():
        onset = float(row["onset"])
        duration = float(row["duration"])
        stim_state = float(row["state"])
        in_event = (t >= onset) & (t < onset + duration)
        state[in_event] = stim_state

    # Compute time since last nominal state switch onset.
    switch_onsets = np.unique(np.concatenate([[0.0], events["onset"].to_numpy(dtype=np.float64)]))
    idx = np.searchsorted(switch_onsets, t, side="right") - 1
    idx = np.clip(idx, 0, len(switch_onsets) - 1)
    last_switch = switch_onsets[idx]
    time_since_switch = np.maximum(0.0, t - last_switch)

    history_n = max(1, int(round(stim_history_sec / hop_sec)))
    stim_frac_recent = _causal_moving_average(state, history_n)

    # Optional protocol-phase features (40s on / 20s off nominal cycle).
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


def _causal_target_smooth(pac: np.ndarray, window: int) -> np.ndarray:
    """Causal trailing mean target denoiser."""
    if window <= 1:
        return pac.astype(np.float64, copy=True)
    return _causal_moving_average(pac.astype(np.float64), window)


def _build_split_samples(
    split_name: str,
    split: Dict[str, np.ndarray],
    spectral: np.ndarray,
    raw_root: Path,
    lookback: int,
    horizon: int,
    window_sec: float,
    hop_sec: float,
    stim_history_sec: int,
    target_smooth_window: int,
) -> Dict[str, np.ndarray]:
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

        events = _subject_events(raw_root, subject)
        ctx, ctx_names = _stim_context_from_events(
            events=events,
            n_windows=len(subj_pac),
            window_sec=window_sec,
            hop_sec=hop_sec,
            stim_history_sec=stim_history_sec,
        )
        pac_feats, pac_names = _pac_multiscale_features(subj_pac)

        # Per-step feature vector
        step_feat = np.concatenate([subj_spec, pac_feats, ctx], axis=1)
        if feature_names is None:
            feature_names = (
                [f"spectral_{i:02d}" for i in range(subj_spec.shape[1])]
                + pac_names
                + ctx_names
            )

        # Build causal sequence samples
        # Sequence end at local index t. Target is t+horizon.
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


def _normalize_with_train_stats(
    train_split: Dict[str, np.ndarray],
    val_split: Dict[str, np.ndarray],
    test_split: Dict[str, np.ndarray],
) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray], Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    """
    Fit scalers on TRAIN only and apply to all splits.
    """
    x_train = train_split["x_seq"].astype(np.float64)
    # Feature scaling over all train timesteps
    feat_mean = x_train.reshape(-1, x_train.shape[-1]).mean(axis=0)
    feat_std = x_train.reshape(-1, x_train.shape[-1]).std(axis=0) + 1e-8

    yf_mean = train_split["y_future"].mean().item()
    yf_std = train_split["y_future"].std().item() + 1e-8
    yd_mean = train_split["y_delta"].mean().item()
    yd_std = train_split["y_delta"].std().item() + 1e-8

    def apply(split: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        out = dict(split)
        out["x_seq"] = ((split["x_seq"] - feat_mean) / feat_std).astype(np.float32)
        out["y_future_norm"] = ((split["y_future"] - yf_mean) / yf_std).astype(np.float32)
        out["y_delta_norm"] = ((split["y_delta"] - yd_mean) / yd_std).astype(np.float32)
        return out

    scalers = {
        "feature_mean": feat_mean.astype(np.float64),
        "feature_std": feat_std.astype(np.float64),
        "y_future_mean": np.float64(yf_mean),
        "y_future_std": np.float64(yf_std),
        "y_delta_mean": np.float64(yd_mean),
        "y_delta_std": np.float64(yd_std),
    }
    return apply(train_split), apply(val_split), apply(test_split), scalers


def build_multiscale_dataset(
    processed_dir: Path,
    raw_root: Path,
    output_dir: Path,
    lookback: int = 20,
    horizon: int = 5,
    window_sec: float = 2.0,
    hop_sec: float = 1.0,
    stim_history_sec: int = 20,
    target_smooth_window: int = 1,
) -> Dict[str, float]:
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("BUILD MULTISCALE TEMPORAL DATASET")
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
    for split in ["train", "val", "test"]:
        splits[split] = _load_split(processed_dir, split)
        spectral[split] = _load_spectral_cache(
            processed_dir, split, n_rows=len(splits[split]["pac"])
        )

    built = {}
    for split in ["train", "val", "test"]:
        built[split] = _build_split_samples(
            split_name=split,
            split=splits[split],
            spectral=spectral[split],
            raw_root=raw_root,
            lookback=lookback,
            horizon=horizon,
            window_sec=window_sec,
            hop_sec=hop_sec,
            stim_history_sec=stim_history_sec,
            target_smooth_window=target_smooth_window,
        )
        print(
            f"{split}: x={built[split]['x_seq'].shape}, "
            f"y_future={built[split]['y_future'].shape}"
        )

    train_norm, val_norm, test_norm, scalers = _normalize_with_train_stats(
        built["train"], built["val"], built["test"]
    )

    for split_name, split in [
        ("train", train_norm),
        ("val", val_norm),
        ("test", test_norm),
    ]:
        np.savez_compressed(output_dir / f"{split_name}_multiscale.npz", **split)

    np.savez_compressed(output_dir / "scalers.npz", **scalers)

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
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print("\nSaved:")
    print(f"- {output_dir / 'train_multiscale.npz'}")
    print(f"- {output_dir / 'val_multiscale.npz'}")
    print(f"- {output_dir / 'test_multiscale.npz'}")
    print(f"- {output_dir / 'scalers.npz'}")
    print(f"- {output_dir / 'metadata.json'}")

    return {
        "n_features": metadata["n_features"],
        "n_train": metadata["n_train"],
        "n_val": metadata["n_val"],
        "n_test": metadata["n_test"],
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build multiscale temporal dataset.")
    p.add_argument("--processed-dir", default="data/processed", type=str)
    p.add_argument("--raw-root", default="data/raw/ds005048", type=str)
    p.add_argument("--output-dir", default="data/processed/multiscale_temporal", type=str)
    p.add_argument("--lookback", default=20, type=int)
    p.add_argument("--horizon", default=5, type=int)
    p.add_argument("--window-sec", default=2.0, type=float)
    p.add_argument("--hop-sec", default=1.0, type=float)
    p.add_argument("--stim-history-sec", default=20, type=int)
    p.add_argument("--target-smooth-window", default=1, type=int)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    build_multiscale_dataset(
        processed_dir=Path(args.processed_dir),
        raw_root=Path(args.raw_root),
        output_dir=Path(args.output_dir),
        lookback=args.lookback,
        horizon=args.horizon,
        window_sec=args.window_sec,
        hop_sec=args.hop_sec,
        stim_history_sec=args.stim_history_sec,
        target_smooth_window=args.target_smooth_window,
    )


if __name__ == "__main__":
    main()
