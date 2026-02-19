"""
Transition analysis: compare model accuracy at stim/rest state transitions
vs steady-state windows.

Hypothesis: the model adds the most value at transitions — exactly where the
closed-loop controller makes its timing decisions.

Usage:
    python temporal_multiscale/transition_analysis.py \
        --checkpoint models/best_multiscale_tcn_lb20_hz1_ts5.pth \
        --dataset-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import Ridge

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 2:
        return float("nan")
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / (ss_tot + 1e-12))


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def _mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


# ---------------------------------------------------------------------------
# Transition identification
# ---------------------------------------------------------------------------

def identify_transitions(
    dataset_dir: Path,
    raw_root: Path,
    split: str = "test",
    margin: int = 5,
) -> Tuple[np.ndarray, np.ndarray]:
    """Identify transition vs steady-state windows in a split.

    A window is "transition" if its target index falls within ±margin
    windows of a stim_state change.

    Returns:
        transition_mask: boolean array (n_samples,)
        steady_mask: boolean array (n_samples,)
    """
    d = np.load(dataset_dir / f"{split}_multiscale.npz", allow_pickle=True)
    subjects = d["subjects"]
    x_seq = d["x_seq"]
    n_samples = x_seq.shape[0]

    # feature_names are stored to identify stim_state column
    feature_names = d.get("feature_names", None)
    if feature_names is not None:
        feature_names = list(feature_names)
        stim_col = feature_names.index("stim_state") if "stim_state" in feature_names else None
    else:
        stim_col = None

    transition_mask = np.zeros(n_samples, dtype=bool)

    unique_subjects = np.unique(subjects)
    for subj in unique_subjects:
        subj_mask = subjects == subj
        subj_indices = np.where(subj_mask)[0]

        if stim_col is not None:
            # Extract stim_state from the last timestep of each sequence
            stim_states = x_seq[subj_indices, -1, stim_col]
        else:
            # Fallback: try to load from events.tsv
            stim_states = _stim_states_from_events(raw_root, subj, len(subj_indices))

        # Find state change points
        changes = np.where(np.abs(np.diff(stim_states)) > 0.3)[0]

        # Mark windows within ±margin of each change
        for ch_idx in changes:
            lo = max(0, ch_idx - margin)
            hi = min(len(subj_indices), ch_idx + margin + 1)
            global_indices = subj_indices[lo:hi]
            transition_mask[global_indices] = True

    steady_mask = ~transition_mask
    return transition_mask, steady_mask


def _stim_states_from_events(
    raw_root: Path, subject: str, n_windows: int
) -> np.ndarray:
    """Fallback: reconstruct stim states from BIDS events.tsv."""
    tsv = raw_root / subject / "eeg" / f"{subject}_task-40HzAuditoryEntrainment_events.tsv"
    if not tsv.exists():
        return np.zeros(n_windows)

    events = pd.read_csv(tsv, sep="\t")
    events = events.sort_values("onset").reset_index(drop=True)

    hop_sec = 1.0
    window_sec = 2.0
    t = np.arange(n_windows, dtype=np.float64) * hop_sec + window_sec / 2.0
    state = np.zeros(n_windows, dtype=np.float64)

    for _, row in events.iterrows():
        onset = float(row["onset"])
        duration = float(row["duration"])
        is_stim = float(int(row["value"]) == 2)
        in_event = (t >= onset) & (t < onset + duration)
        state[in_event] = is_stim

    return state


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_subset(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    mask: np.ndarray,
    label: str,
) -> Dict[str, float]:
    yt = y_true[mask]
    yp = y_pred[mask]
    return {
        "label": label,
        "n": int(mask.sum()),
        "r2": _r2(yt, yp),
        "rmse": _rmse(yt, yp),
        "mae": _mae(yt, yp),
    }


def get_predictions(
    checkpoint_path: str,
    dataset_dir: Path,
    split: str = "test",
    device_str: str = "cpu",
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Get TCN, Ridge, and persistence predictions on a split.

    Returns:
        y_true, y_persist, y_ridge, y_tcn  (all in raw PAC space)
    """
    device = torch.device(device_str)
    d = np.load(dataset_dir / f"{split}_multiscale.npz", allow_pickle=True)
    scalers = np.load(dataset_dir / "scalers.npz")
    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])

    y_true = d["y_future"].astype(np.float64)
    y_persist = d["last_pac"].astype(np.float64)

    # Ridge
    train = np.load(dataset_dir / "train_multiscale.npz", allow_pickle=True)
    x_train_flat = train["x_seq"].reshape(train["x_seq"].shape[0], -1).astype(np.float64)
    y_train = train["y_future"].astype(np.float64)
    ridge = Ridge(alpha=1.0)
    ridge.fit(x_train_flat, y_train)
    x_test_flat = d["x_seq"].reshape(d["x_seq"].shape[0], -1).astype(np.float64)
    y_ridge = ridge.predict(x_test_flat)

    # TCN
    ckpt = torch.load(checkpoint_path, map_location=device)
    cfg = ModelConfig(**ckpt["cfg"])
    model = MultiscaleCausalTCN(cfg)
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(device)
    model.eval()

    x_tensor = torch.from_numpy(d["x_seq"]).float().to(device)
    batch_size = 512
    preds = []
    with torch.no_grad():
        for i in range(0, len(x_tensor), batch_size):
            batch = x_tensor[i : i + batch_size]
            out = model(batch)["future"].cpu().numpy()
            preds.append(out)
    y_tcn_norm = np.concatenate(preds)
    y_tcn = y_tcn_norm * yf_std + yf_mean

    return y_true, y_persist, y_ridge, y_tcn


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Transition analysis.")
    p.add_argument("--checkpoint", type=str, required=True)
    p.add_argument("--dataset-dir", type=str, required=True)
    p.add_argument("--raw-root", default="data/raw/ds005048", type=str)
    p.add_argument("--output-json", default="", type=str)
    p.add_argument("--margin", default=5, type=int,
                   help="±N windows around each state change")
    p.add_argument("--device", default="cpu", type=str)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    dataset_dir = Path(args.dataset_dir)
    raw_root = Path(args.raw_root)

    print("=" * 60)
    print("TRANSITION ANALYSIS")
    print("=" * 60)

    # Identify transitions
    trans_mask, steady_mask = identify_transitions(
        dataset_dir, raw_root, split="test", margin=args.margin,
    )
    print(f"Transition windows: {trans_mask.sum()}")
    print(f"Steady-state windows: {steady_mask.sum()}")

    if trans_mask.sum() == 0:
        print("No transitions found — cannot proceed.")
        return

    # Get all predictions
    y_true, y_persist, y_ridge, y_tcn = get_predictions(
        args.checkpoint, dataset_dir, split="test", device_str=args.device,
    )

    # Evaluate each model on each subset
    results: List[Dict] = []
    for model_name, y_pred in [
        ("persistence", y_persist),
        ("ridge", y_ridge),
        ("tcn", y_tcn),
    ]:
        for mask, label in [
            (np.ones(len(y_true), dtype=bool), "all"),
            (trans_mask, "transition"),
            (steady_mask, "steady_state"),
        ]:
            res = evaluate_subset(y_true, y_pred, mask, label)
            res["model"] = model_name
            results.append(res)

    # Print results table
    print(f"\n{'Model':<14s} {'Subset':<14s} {'N':>6s} {'R2':>8s} {'RMSE':>10s} {'MAE':>10s}")
    print("-" * 64)
    for r in results:
        r2_s = f"{r['r2']:.4f}" if not np.isnan(r["r2"]) else "  N/A"
        print(
            f"{r['model']:<14s} {r['label']:<14s} "
            f"{r['n']:>6d} {r2_s:>8s} "
            f"{r['rmse']:>10.6f} {r['mae']:>10.6f}"
        )

    # Compute model margin over persistence
    print(f"\n{'='*60}")
    print("MODEL MARGIN OVER PERSISTENCE")
    print(f"{'='*60}")
    for label in ["all", "transition", "steady_state"]:
        persist_r2 = [r["r2"] for r in results
                      if r["model"] == "persistence" and r["label"] == label][0]
        for model_name in ["ridge", "tcn"]:
            model_r2 = [r["r2"] for r in results
                        if r["model"] == model_name and r["label"] == label][0]
            margin = model_r2 - persist_r2
            print(f"  {model_name:<8s} @ {label:<14s}: "
                  f"R2={model_r2:.4f} vs persist={persist_r2:.4f} "
                  f"margin={margin:+.4f}")

    # Save
    output_path = args.output_json or str(
        Path(args.checkpoint).parent / "transition_analysis_results.json"
    )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
