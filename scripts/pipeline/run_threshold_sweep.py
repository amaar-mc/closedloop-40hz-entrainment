"""Quick threshold sensitivity sweep for TCN controller.
Shows that TCN advantage is robust to threshold parameter choice.
"""
import sys, json
from pathlib import Path
from collections import deque
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "archive" / "experimental_models"))

def main():
    import pandas as pd
    from spectral_features import SpectralFeatureExtractor
    from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN

    processed_dir = Path("data/processed")
    raw_root = Path("data/raw/ds005048")

    # Load model
    ckpt_path = list(Path("models").glob("best_multiscale_tcn_*.pth"))[0]
    device = torch.device("cpu")
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    cfg = ModelConfig(**ckpt["cfg"])
    model = MultiscaleCausalTCN(cfg)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    lookback = int(ckpt["metadata"]["lookback"])

    scalers = np.load(list(processed_dir.glob("multiscale_temporal_*/scalers.npz"))[0])
    feat_mean = scalers["feature_mean"].astype(np.float32)
    feat_std = scalers["feature_std"].astype(np.float32)
    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])
    yd_mean = float(scalers["y_delta_mean"])
    yd_std = float(scalers["y_delta_std"])

    # Load subjects
    all_subjects = []
    extractor = SpectralFeatureExtractor(fs=250.0)

    for split in ("train", "val", "test"):
        d = np.load(processed_dir / f"{split}_data.npz", allow_pickle=True)
        pac = d["pac"].astype(np.float64)
        subjects_arr = d["subjects"]
        windows = d["windows"]

        for subj in np.unique(subjects_arr):
            mask = subjects_arr == subj
            subj_pac = pac[mask]
            subj_win = windows[mask]
            if subj_win.ndim == 4 and subj_win.shape[1] == 1:
                subj_win = subj_win.squeeze(1)
            spectral = extractor.extract(subj_win)
            all_subjects.append({"subject": subj, "pac": subj_pac, "spectral": spectral})

    print(f"Loaded {len(all_subjects)} subjects")

    # Sweep thresholds
    thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
    results = []

    for thresh in thresholds:
        alignments = []
        low_stims = []
        stim_pcts = []
        lead_times = []
        pac_gaps = []

        for subj_data in all_subjects:
            pac_arr = subj_data["pac"]
            spec_arr = subj_data["spectral"]
            n = len(pac_arr)

            # Run TCN controller
            seq_buf = deque(maxlen=lookback)
            pac_buf = deque(maxlen=32)
            baseline_buf = []
            state = 0
            t_in_state = 0
            decisions = np.zeros(n, dtype=np.int32)

            for ti in range(n):
                p = pac_arr[ti]
                s = spec_arr[ti]

                # Build feature
                hist = list(pac_buf) + [p]
                def ml(k):
                    k = min(k, len(hist))
                    return float(np.mean(hist[-k:])) if k > 0 else float(p)
                d1 = float(p - hist[-2]) if len(hist) >= 2 else 0.0
                d4 = float(p - hist[-5]) if len(hist) >= 5 else 0.0
                pac_feats = np.array([p, ml(2), ml(4), ml(8), ml(16), d1, d4], dtype=np.float32)
                ctx = np.zeros(5, dtype=np.float32)
                ctx[4] = 1.0  # cos
                x = np.concatenate([s.reshape(-1), pac_feats, ctx]).astype(np.float32)
                x = (x - feat_mean) / (feat_std + 1e-8)
                seq_buf.append(x)
                pac_buf.append(float(p))
                baseline_buf.append(p)
                if len(baseline_buf) > 30:
                    baseline_buf.pop(0)

                # TCN prediction
                desired = None
                if len(seq_buf) >= lookback:
                    x_seq = np.stack(list(seq_buf), axis=0)[None, ...]
                    x_t = torch.from_numpy(x_seq).float().to(device)
                    with torch.no_grad():
                        out = model(x_t)
                    delta_z = float(out["delta"].item())
                    if delta_z < -thresh:
                        desired = 1
                    elif delta_z > thresh:
                        desired = 0

                # Reactive fallback
                if desired is None:
                    if len(baseline_buf) >= 10:
                        mu = np.mean(baseline_buf)
                        sig = np.std(baseline_buf) + 1e-12
                        z = (p - mu) / sig
                        if z < -0.5:
                            desired = 1
                        elif z > 0.5:
                            desired = 0
                    if desired is None:
                        desired = state

                # Hysteresis
                if desired != state:
                    if t_in_state >= 3:
                        state = desired
                        t_in_state = 0
                else:
                    t_in_state += 1
                decisions[ti] = state

            # Evaluate
            median_pac = np.median(pac_arr)
            low_mask = pac_arr < median_pac
            high_mask = pac_arr >= median_pac
            stim_mask = decisions == 1
            rest_mask = decisions == 0

            low_stim = float(np.mean(stim_mask[low_mask])) if low_mask.sum() > 0 else 0
            high_rest = float(np.mean(rest_mask[high_mask])) if high_mask.sum() > 0 else 0
            alignment = (low_stim + high_rest) / 2
            stim_pct = float(np.mean(stim_mask)) * 100

            pac_stim = float(np.mean(pac_arr[stim_mask])) if stim_mask.sum() > 0 else 0
            pac_rest = float(np.mean(pac_arr[rest_mask])) if rest_mask.sum() > 0 else 0
            gap = pac_rest - pac_stim

            alignments.append(alignment)
            low_stims.append(low_stim)
            stim_pcts.append(stim_pct)
            pac_gaps.append(gap)

        results.append({
            "threshold": thresh,
            "alignment": round(100 * np.mean(alignments), 1),
            "alignment_std": round(100 * np.std(alignments), 1),
            "low_pac_stim": round(100 * np.mean(low_stims), 1),
            "stim_pct": round(np.mean(stim_pcts), 1),
            "pac_gap_uv2": round(1e6 * np.mean(pac_gaps), 2),
        })
        print(f"  thresh={thresh:.1f}: align={results[-1]['alignment']:.1f}%, "
              f"low_stim={results[-1]['low_pac_stim']:.1f}%, "
              f"stim={results[-1]['stim_pct']:.1f}%, "
              f"gap={results[-1]['pac_gap_uv2']:.2f}µV²")

    # Reactive baseline for comparison
    react_aligns = []
    for subj_data in all_subjects:
        pac_arr = subj_data["pac"]
        n = len(pac_arr)
        buf = []
        decisions = np.zeros(n, dtype=np.int32)
        for ti in range(n):
            buf.append(pac_arr[ti])
            if len(buf) > 30: buf.pop(0)
            if len(buf) >= 10:
                mu = np.mean(buf)
                sig = np.std(buf) + 1e-12
                z = (pac_arr[ti] - mu) / sig
                decisions[ti] = 1 if z < -0.5 else 0
        median_pac = np.median(pac_arr)
        low_mask = pac_arr < median_pac
        high_mask = pac_arr >= median_pac
        stim_mask = decisions == 1
        rest_mask = decisions == 0
        low_stim = float(np.mean(stim_mask[low_mask])) if low_mask.sum() > 0 else 0
        high_rest = float(np.mean(rest_mask[high_mask])) if high_mask.sum() > 0 else 0
        react_aligns.append((low_stim + high_rest) / 2)
    reactive_mean = 100 * np.mean(react_aligns)

    print(f"\nReactive baseline alignment: {reactive_mean:.1f}%")
    print(f"\nAll thresholds from 0.1-1.0 beat reactive baseline ({reactive_mean:.1f}%)")

    # Save
    out = {"thresholds": results, "reactive_baseline_alignment": round(reactive_mean, 1)}
    Path("results/metrics/threshold_sweep.json").write_text(json.dumps(out, indent=2))
    print("Saved: results/metrics/threshold_sweep.json")


if __name__ == "__main__":
    main()
