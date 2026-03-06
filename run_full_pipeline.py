"""
Full end-to-end pipeline: preprocess → spectral cache → temporal dataset → train TCN → validate.

This script orchestrates every stage needed to go from raw BIDS data to
publication-ready results. It checks for intermediate outputs so you can
resume from any point.

Usage:
    python run_full_pipeline.py                    # Run everything
    python run_full_pipeline.py --skip-preprocess  # Skip raw data processing
    python run_full_pipeline.py --horizon 5        # Train at specific horizon
    python run_full_pipeline.py --target-smooth 1  # Raw targets (no smoothing)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def step_preprocess(bids_root: Path, output_dir: Path) -> bool:
    """Step 1: Preprocess raw BIDS data into train/val/test splits."""
    needed = [output_dir / f"{s}_data.npz" for s in ("train", "val", "test")]
    if all(f.exists() for f in needed):
        print("[SKIP] Preprocessed splits already exist")
        return True

    print("=" * 80)
    print("STEP 1: PREPROCESS RAW BIDS DATA")
    print("=" * 80)

    from data_loader import BIDSDataProcessor

    processor = BIDSDataProcessor(
        bids_root=str(bids_root),
        output_dir=str(output_dir),
        window_sec=2.0,
        hop_sec=1.0,
    )
    windows, pac_labels, subject_ids, session_ids = processor.process_dataset()
    splits = processor.create_splits(windows, pac_labels, subject_ids)
    processor.save_splits(splits)
    return True


def step_spectral_cache(processed_dir: Path) -> bool:
    """Step 2: Generate spectral feature caches for each split."""
    needed = [processed_dir / f"{s}_spectral_cache.npy" for s in ("train", "val", "test")]
    if all(f.exists() for f in needed):
        print("[SKIP] Spectral caches already exist")
        return True

    print("=" * 80)
    print("STEP 2: EXTRACT SPECTRAL FEATURES")
    print("=" * 80)

    sys.path.insert(0, str(ROOT / "archive" / "experimental_models"))
    from spectral_features import SpectralFeatureExtractor

    extractor = SpectralFeatureExtractor(fs=250.0)

    for split in ("train", "val", "test"):
        cache_path = processed_dir / f"{split}_spectral_cache.npy"
        if cache_path.exists():
            print(f"  [SKIP] {split} spectral cache exists")
            continue

        print(f"  Extracting spectral features for {split}...")
        data = np.load(processed_dir / f"{split}_data.npz")
        windows = data["windows"]  # (N, 1, 7, 500)
        if windows.ndim == 4 and windows.shape[1] == 1:
            windows = windows.squeeze(1)  # (N, 7, 500)

        spectral = extractor.extract(windows)
        np.save(cache_path, spectral)
        print(f"    Saved {split}: {spectral.shape}")

    return True


def step_build_dataset(
    processed_dir: Path,
    raw_root: Path,
    output_dir: Path,
    lookback: int,
    horizon: int,
    target_smooth: int,
) -> bool:
    """Step 3: Build multiscale temporal dataset."""
    needed = [output_dir / f"{s}_multiscale.npz" for s in ("train", "val", "test")]
    meta_path = output_dir / "metadata.json"

    if all(f.exists() for f in needed) and meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if (
            int(meta.get("lookback", -1)) == lookback
            and int(meta.get("horizon", -1)) == horizon
            and int(meta.get("target_smooth_window", -1)) == target_smooth
        ):
            print("[SKIP] Temporal dataset already exists with matching params")
            return True

    print("=" * 80)
    print("STEP 3: BUILD MULTISCALE TEMPORAL DATASET")
    print("=" * 80)

    from temporal_multiscale.build_multiscale_dataset import build_multiscale_dataset

    build_multiscale_dataset(
        processed_dir=processed_dir,
        raw_root=raw_root,
        output_dir=output_dir,
        lookback=lookback,
        horizon=horizon,
        stim_history_sec=20,
        target_smooth_window=target_smooth,
    )
    return True


def step_train_tcn(
    dataset_dir: Path,
    models_dir: Path,
    lookback: int,
    horizon: int,
    target_smooth: int,
) -> Path:
    """Step 4: Train multiscale causal TCN."""
    run_name = f"multiscale_tcn_lb{lookback}_hz{horizon}_ts{target_smooth}"
    ckpt_path = models_dir / f"best_{run_name}.pth"

    if ckpt_path.exists():
        print(f"[SKIP] TCN checkpoint exists: {ckpt_path}")
        return ckpt_path

    print("=" * 80)
    print("STEP 4: TRAIN MULTISCALE CAUSAL TCN")
    print("=" * 80)

    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, Dataset

    from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN

    class SeqDataset(Dataset):
        def __init__(self, path):
            d = np.load(path, allow_pickle=True)
            self.x = torch.from_numpy(d["x_seq"]).float()
            self.yf = torch.from_numpy(d["y_future_norm"]).float()
            self.yd = torch.from_numpy(d["y_delta_norm"]).float()
            self.lp = torch.from_numpy(d["last_pac"]).float()

        def __len__(self):
            return len(self.x)

        def __getitem__(self, i):
            return {"x_seq": self.x[i], "y_future": self.yf[i],
                    "y_delta": self.yd[i], "last_pac": self.lp[i]}

    train_ds = SeqDataset(dataset_dir / "train_multiscale.npz")
    val_ds = SeqDataset(dataset_dir / "val_multiscale.npz")
    test_ds = SeqDataset(dataset_dir / "test_multiscale.npz")

    scalers = np.load(dataset_dir / "scalers.npz")
    yf_mean, yf_std = float(scalers["y_future_mean"]), float(scalers["y_future_std"])
    yd_mean, yd_std = float(scalers["y_delta_mean"]), float(scalers["y_delta_std"])

    meta = json.loads((dataset_dir / "metadata.json").read_text())

    device = torch.device("mps" if torch.backends.mps.is_available()
                          else "cuda" if torch.cuda.is_available() else "cpu")

    cfg = ModelConfig(
        n_features=int(meta["n_features"]),
        hidden=64,
        kernel_size=3,
        dilations=[1, 2, 4, 8],
        dropout=0.2,
        pool_type="attention",
    )
    model = MultiscaleCausalTCN(cfg).to(device)
    print(f"Device: {device}, Params: {model.count_parameters():,}")
    print(f"Train/Val/Test: {len(train_ds):,}/{len(val_ds):,}/{len(test_ds):,}")

    g = torch.Generator()
    g.manual_seed(42)
    train_loader = DataLoader(train_ds, batch_size=128, shuffle=True, generator=g)
    val_loader = DataLoader(val_ds, batch_size=256, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=256, shuffle=False)

    huber = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-3)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=5
    )

    best_val_r2 = -np.inf
    best_epoch = 0
    patience_counter = 0
    history = []

    for epoch in range(1, 81):
        model.train()
        train_loss = 0.0
        n_batch = 0
        for batch in train_loader:
            x = batch["x_seq"].to(device)
            yf = batch["y_future"].to(device)
            yd = batch["y_delta"].to(device)

            out = model(x)
            loss = huber(out["future"], yf)

            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_loss += loss.item()
            n_batch += 1

        train_loss /= max(1, n_batch)

        # Validation
        model.eval()
        preds, trues = [], []
        with torch.no_grad():
            for batch in val_loader:
                x = batch["x_seq"].to(device)
                out = model(x)
                preds.append(out["future"].cpu().numpy())
                trues.append(batch["y_future"].numpy())

        preds = np.concatenate(preds) * yf_std + yf_mean
        trues = np.concatenate(trues) * yf_std + yf_mean
        ss_res = np.sum((trues - preds) ** 2)
        ss_tot = np.sum((trues - trues.mean()) ** 2)
        val_r2 = 1.0 - ss_res / (ss_tot + 1e-12)

        scheduler.step(val_r2)

        improved = val_r2 > best_val_r2
        if improved:
            best_val_r2 = val_r2
            best_epoch = epoch
            patience_counter = 0
            torch.save({
                "model_state_dict": model.state_dict(),
                "cfg": cfg.__dict__,
                "metadata": meta,
                "scalers": {
                    "y_future_mean": yf_mean, "y_future_std": yf_std,
                    "y_delta_mean": yd_mean, "y_delta_std": yd_std,
                },
                "epoch": epoch,
                "val_future_r2": best_val_r2,
            }, ckpt_path)
        else:
            patience_counter += 1

        if epoch <= 5 or epoch % 10 == 0 or improved:
            mark = " *" if improved else ""
            print(f"  Epoch {epoch:03d} | loss={train_loss:.4f} | val_r2={val_r2:.4f}{mark}")

        if patience_counter >= 20:
            print(f"  Early stopping at epoch {epoch}")
            break

    # Test evaluation
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    preds, trues = [], []
    with torch.no_grad():
        for batch in test_loader:
            x = batch["x_seq"].to(device)
            out = model(x)
            preds.append(out["future"].cpu().numpy())
            trues.append(batch["y_future"].numpy())

    preds = np.concatenate(preds) * yf_std + yf_mean
    trues = np.concatenate(trues) * yf_std + yf_mean
    ss_res = np.sum((trues - preds) ** 2)
    ss_tot = np.sum((trues - trues.mean()) ** 2)
    test_r2 = 1.0 - ss_res / (ss_tot + 1e-12)
    test_rmse = float(np.sqrt(np.mean((trues - preds) ** 2)))
    test_corr = float(np.corrcoef(trues, preds)[0, 1]) if np.std(preds) > 1e-12 else 0.0

    print(f"\n  Best epoch: {best_epoch}, Test R2={test_r2:.4f}, RMSE={test_rmse:.6f}, corr={test_corr:.4f}")

    summary = {
        "model": "MultiscaleCausalTCN",
        "run_name": run_name,
        "n_params": model.count_parameters(),
        "best_epoch": best_epoch,
        "best_val_future_r2": float(best_val_r2),
        "test_future_r2": float(test_r2),
        "test_future_rmse": float(test_rmse),
        "test_future_corr": float(test_corr),
        "config": {
            "lookback": lookback, "horizon": horizon,
            "target_smooth_window": target_smooth,
        },
    }
    (models_dir / f"summary_{run_name}.json").write_text(json.dumps(summary, indent=2))

    return ckpt_path


def step_replay_with_tcn(
    processed_dir: Path,
    raw_root: Path,
    ckpt_path: Path,
    scalers_path: Path,
    output_path: Path,
) -> dict:
    """Step 5: Replay real data through controllers including TCN-based predictive."""
    if output_path.exists():
        print(f"[SKIP] TCN replay results exist: {output_path}")
        return json.loads(output_path.read_text())

    print("=" * 80)
    print("STEP 5: REAL-DATA REPLAY WITH TCN CONTROLLER")
    print("=" * 80)

    import torch
    from scipy import signal as sig, stats

    # Load TCN model
    from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN

    device = torch.device("cpu")  # CPU for replay (sequential anyway)
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    cfg = ModelConfig(**ckpt["cfg"])
    tcn_model = MultiscaleCausalTCN(cfg)
    tcn_model.load_state_dict(ckpt["model_state_dict"])
    tcn_model.eval()

    s = np.load(scalers_path)
    feature_mean = s["feature_mean"].astype(np.float32)
    feature_std = s["feature_std"].astype(np.float32)
    yf_mean = float(s["y_future_mean"])
    yf_std = float(s["y_future_std"])
    yd_mean = float(s["y_delta_mean"])
    yd_std = float(s["y_delta_std"])

    lookback = int(ckpt["metadata"]["lookback"])
    n_features = int(cfg.n_features)

    # Load spectral feature extractor
    sys.path.insert(0, str(ROOT / "archive" / "experimental_models"))
    from spectral_features import SpectralFeatureExtractor
    spec_extractor = SpectralFeatureExtractor(fs=250.0)

    # Load subjects
    import pandas as pd
    all_subjects = []
    for split in ("train", "val", "test"):
        d = np.load(processed_dir / f"{split}_data.npz", allow_pickle=True)
        pac = d["pac"].astype(np.float64)
        subjects = d["subjects"]
        windows = d["windows"]

        for subj in np.unique(subjects):
            mask = subjects == subj
            subj_pac = pac[mask]
            subj_windows = windows[mask]

            tsv = raw_root / subj / "eeg" / f"{subj}_task-40HzAuditoryEntrainment_events.tsv"
            if not tsv.exists():
                continue
            events = pd.read_csv(tsv, sep="\t").sort_values("onset").reset_index(drop=True)

            n = len(subj_pac)
            t = np.arange(n, dtype=np.float64) * 1.0 + 1.0
            stim_state = np.zeros(n, dtype=np.int32)
            for _, row in events.iterrows():
                onset = float(row["onset"])
                duration = float(row["duration"])
                is_stim = int(row["value"]) == 2
                if is_stim:
                    in_event = (t >= onset) & (t < onset + duration)
                    stim_state[in_event] = 1

            all_subjects.append({
                "subject": subj, "pac": subj_pac, "windows": subj_windows,
                "stim_state": stim_state, "time": t, "n_windows": n, "split": split,
            })

    print(f"  Loaded {len(all_subjects)} subjects")

    # Extract spectral features for all windows
    print("  Extracting spectral features...")
    for subj_data in all_subjects:
        w = subj_data["windows"]
        if w.ndim == 4 and w.shape[1] == 1:
            w = w.squeeze(1)
        subj_data["spectral"] = spec_extractor.extract(w)  # (n, 61)

    # ---- Controller implementations ----

    class FixedScheduleCtrl:
        name = "Fixed Schedule"
        def __init__(self, stim): self.stim = stim; self.t = 0
        def reset(self): self.t = 0
        def step(self, pac, **kw):
            a = int(self.stim[self.t]) if self.t < len(self.stim) else 0
            self.t += 1; return a

    class ReactiveCtrl:
        name = "Reactive Threshold"
        def __init__(self, w=30, z=0.5): self.w=w; self.z=z; self.buf=[]
        def reset(self): self.buf=[]
        def step(self, pac, **kw):
            self.buf.append(pac)
            if len(self.buf) > self.w: self.buf.pop(0)
            if len(self.buf) < 10: return 0
            mu=np.mean(self.buf); sig=np.std(self.buf)+1e-12
            return 1 if (pac-mu)/sig < -self.z else 0

    class TCNPredictiveCtrl:
        """Predictive controller using trained TCN for look-ahead."""
        name = "TCN Predictive"
        def __init__(self):
            from collections import deque
            self.seq_buf = deque(maxlen=lookback)
            self.pac_buf = deque(maxlen=max(lookback, 32))
            self.baseline_buf = []
            self.state = 0
            self.t_in_state = 0

        def reset(self):
            self.seq_buf.clear()
            self.pac_buf.clear()
            self.baseline_buf = []
            self.state = 0
            self.t_in_state = 0

        def _pac_features(self, pac_cur):
            hist = list(self.pac_buf) + [pac_cur]
            def ml(k):
                k=min(k,len(hist))
                return float(np.mean(hist[-k:])) if k>0 else float(pac_cur)
            ma2,ma4,ma8,ma16 = ml(2),ml(4),ml(8),ml(16)
            d1 = float(pac_cur-hist[-2]) if len(hist)>=2 else 0.0
            d4 = float(pac_cur-hist[-5]) if len(hist)>=5 else 0.0
            return np.array([pac_cur,ma2,ma4,ma8,ma16,d1,d4], dtype=np.float32)

        def step(self, pac, spectral=None, stim_state_val=0.0,
                 time_since_switch=0.0, stim_frac=0.0,
                 cycle_sin=0.0, cycle_cos=1.0, **kw):
            # Build feature vector
            if spectral is None:
                spectral = np.zeros(61, dtype=np.float32)
            pac_feats = self._pac_features(pac)
            ctx = np.array([stim_state_val, min(time_since_switch/60,1),
                           min(max(stim_frac,0),1), cycle_sin, cycle_cos], dtype=np.float32)
            x = np.concatenate([spectral.reshape(-1), pac_feats, ctx]).astype(np.float32)
            x = (x - feature_mean) / (feature_std + 1e-8)
            self.seq_buf.append(x)
            self.pac_buf.append(float(pac))

            # Baseline tracking
            self.baseline_buf.append(pac)
            if len(self.baseline_buf) > 30:
                self.baseline_buf.pop(0)

            # Not enough history for TCN
            if len(self.seq_buf) < lookback:
                return 0

            # Run TCN inference
            x_seq = np.stack(list(self.seq_buf), axis=0)[None, ...]
            x_tensor = torch.from_numpy(x_seq).float().to(device)
            with torch.no_grad():
                out = tcn_model(x_tensor)
            future_norm = float(out["future"].item())
            delta_norm = float(out["delta"].item())
            future_raw = future_norm * yf_std + yf_mean
            delta_raw = delta_norm * yd_std + yd_mean

            # Decision logic: use predicted delta
            # Also compute z-score for reactive fallback
            if len(self.baseline_buf) >= 10:
                mu = np.mean(self.baseline_buf)
                sigma = np.std(self.baseline_buf) + 1e-12
                z = (pac - mu) / sigma
            else:
                z = 0.0

            desired = None
            # Proactive: predicted decline -> stimulate early
            if delta_raw < -0.3 * (np.std(self.baseline_buf) + 1e-12) if len(self.baseline_buf) >= 10 else delta_raw < -1e-5:
                desired = 1
            # Proactive: predicted rise -> rest
            elif delta_raw > 0.3 * (np.std(self.baseline_buf) + 1e-12) if len(self.baseline_buf) >= 10 else delta_raw > 1e-5:
                desired = 0
            # Reactive fallback
            elif z < -0.5:
                desired = 1
            elif z > 0.5:
                desired = 0

            if desired is None:
                desired = self.state

            # Hysteresis
            if desired != self.state:
                if self.t_in_state >= 5:
                    self.state = desired
                    self.t_in_state = 0
            else:
                self.t_in_state += 1

            return self.state

    class OracleCtrl:
        name = "Oracle"
        def __init__(self, pac, la=5): self.pac=pac; self.la=la; self.t=0
        def reset(self): self.t=0
        def step(self, pac, **kw):
            fi = min(self.t+self.la, len(self.pac)-1)
            fp = self.pac[fi]; self.t+=1
            return 1 if fp < pac else 0

    class PICtrl:
        name = "PI Controller"
        def __init__(self, w=30, kp=1.0, ki=0.2):
            self.w=w; self.kp=kp; self.ki=ki; self.buf=[]; self.I=0.0
        def reset(self): self.buf=[]; self.I=0.0
        def step(self, pac, **kw):
            self.buf.append(pac)
            if len(self.buf)>self.w: self.buf.pop(0)
            if len(self.buf)<10: return 0
            e = np.mean(self.buf)-pac
            self.I = np.clip(self.I+e, -5, 5)
            return 1 if self.kp*e+self.ki*self.I > 0 else 0

    # ---- Evaluate function ----
    def evaluate_decisions(pac, decisions, lookahead=3):
        n = len(pac)
        stim_mask = decisions == 1
        rest_mask = decisions == 0
        stim_pct = 100.0 * np.mean(stim_mask)

        pac_delta = np.zeros(n)
        for i in range(n):
            end = min(i + lookahead, n - 1)
            pac_delta[i] = pac[end] - pac[i]

        if stim_mask.sum() > 0:
            hit_rate = float(np.mean(pac_delta[stim_mask] > 0))
            stim_delta = float(np.mean(pac_delta[stim_mask]))
            wasted = float(np.mean(pac_delta[stim_mask] <= 0))
        else:
            hit_rate = stim_delta = 0.0; wasted = 0.0

        median_pac = np.median(pac)
        rest_above = float(np.mean(pac[rest_mask] > median_pac)) if rest_mask.sum() > 0 else 0.0

        return {
            "stim_pct": stim_pct, "stim_hit_rate": hit_rate,
            "stim_mean_delta": stim_delta, "wasted_stim_pct": 100*wasted,
            "rest_above_median_pct": 100*rest_above,
            "mean_pac_during_stim": float(np.mean(pac[stim_mask])) if stim_mask.sum() > 0 else 0,
            "mean_pac_during_rest": float(np.mean(pac[rest_mask])) if rest_mask.sum() > 0 else 0,
        }

    # ---- Run replay ----
    all_results = {}
    for si, subj_data in enumerate(all_subjects):
        pac = subj_data["pac"]
        stim_state_arr = subj_data["stim_state"]
        spectral_arr = subj_data["spectral"]
        n = len(pac)
        t_arr = subj_data["time"]

        # Compute stim context features
        cycle = 60.0
        phase = (t_arr % cycle) / cycle
        c_sin = np.sin(2 * np.pi * phase)
        c_cos = np.cos(2 * np.pi * phase)

        # Time since last switch
        switch_times = [0.0]
        for i in range(1, n):
            if stim_state_arr[i] != stim_state_arr[i-1]:
                switch_times.append(t_arr[i])
        switch_arr = np.array(switch_times)
        idx = np.searchsorted(switch_arr, t_arr, side="right") - 1
        idx = np.clip(idx, 0, len(switch_arr)-1)
        time_since_switch = t_arr - switch_arr[idx]

        # Stim fraction (trailing 20s)
        from collections import deque
        stim_frac = np.zeros(n)
        stim_hist = deque(maxlen=20)
        for i in range(n):
            stim_hist.append(float(stim_state_arr[i]))
            stim_frac[i] = np.mean(stim_hist)

        controllers = [
            FixedScheduleCtrl(stim_state_arr),
            ReactiveCtrl(),
            TCNPredictiveCtrl(),
            OracleCtrl(pac),
            PICtrl(),
        ]

        for ctrl in controllers:
            ctrl.reset()
            decisions = np.zeros(n, dtype=np.int32)
            for t_i in range(n):
                if isinstance(ctrl, TCNPredictiveCtrl):
                    decisions[t_i] = ctrl.step(
                        pac[t_i],
                        spectral=spectral_arr[t_i],
                        stim_state_val=float(stim_state_arr[t_i]),
                        time_since_switch=time_since_switch[t_i],
                        stim_frac=stim_frac[t_i],
                        cycle_sin=c_sin[t_i],
                        cycle_cos=c_cos[t_i],
                    )
                else:
                    decisions[t_i] = ctrl.step(pac[t_i])

            metrics = evaluate_decisions(pac, decisions)
            if ctrl.name not in all_results:
                all_results[ctrl.name] = []
            all_results[ctrl.name].append({"subject": subj_data["subject"], **metrics})

        if (si + 1) % 5 == 0:
            print(f"  Replayed {si+1}/{len(all_subjects)} subjects")

    # ---- Summarize ----
    print(f"\n{'='*80}")
    print("REPLAY RESULTS (Real PAC Data, TCN Integrated)")
    print(f"{'='*80}")
    print(f"{'Controller':<22s} {'Stim%':>6s} {'HitRate':>8s} {'Wasted%':>8s} {'dPAC':>10s} {'Rest>Med':>9s}")
    print("-" * 70)

    summary = {}
    for name in ["Fixed Schedule", "Reactive Threshold", "TCN Predictive", "Oracle", "PI Controller"]:
        trials = all_results.get(name, [])
        if not trials:
            continue
        sp = np.mean([t["stim_pct"] for t in trials])
        hr = np.mean([t["stim_hit_rate"] for t in trials])
        ws = np.mean([t["wasted_stim_pct"] for t in trials])
        sd = np.mean([t["stim_mean_delta"] for t in trials])
        ra = np.mean([t["rest_above_median_pct"] for t in trials])
        print(f"{name:<22s} {sp:>5.1f}% {100*hr:>7.1f}% {ws:>7.1f}% {sd:>+10.6f} {ra:>8.1f}%")
        summary[name] = {
            "stim_pct": round(sp,1), "stim_hit_rate_pct": round(100*hr,1),
            "wasted_stim_pct": round(ws,1), "stim_mean_delta_pac": float(sd),
            "rest_above_median_pct": round(ra,1),
        }

    # ---- Statistical tests ----
    print(f"\n{'='*80}")
    print("STATISTICAL TESTS")
    print(f"{'='*80}")

    # TCN vs Reactive
    tcn_trials = all_results.get("TCN Predictive", [])
    reactive_trials = all_results.get("Reactive Threshold", [])
    if len(tcn_trials) >= 5 and len(reactive_trials) >= 5:
        tcn_by_subj = {t["subject"]: t for t in tcn_trials}
        react_by_subj = {t["subject"]: t for t in reactive_trials}
        common = sorted(set(tcn_by_subj) & set(react_by_subj))

        if len(common) >= 5:
            print(f"\nTCN Predictive vs Reactive Threshold (n={len(common)} subjects):")
            for metric, label in [
                ("stim_hit_rate", "Hit rate"),
                ("wasted_stim_pct", "Wasted stim%"),
                ("stim_pct", "Stim%"),
                ("stim_mean_delta", "Mean dPAC"),
            ]:
                tcn_vals = np.array([tcn_by_subj[s][metric] for s in common])
                react_vals = np.array([react_by_subj[s][metric] for s in common])
                diff = tcn_vals - react_vals

                nonzero = np.abs(diff) > 1e-10
                if nonzero.sum() < 5:
                    print(f"  {label}: insufficient differences")
                    continue

                stat, p = stats.wilcoxon(diff[nonzero])
                scale = 100.0 if metric == "stim_hit_rate" else 1.0
                # Hedges' g effect size
                n1 = len(tcn_vals)
                pooled_std = np.sqrt(((n1-1)*np.var(tcn_vals,ddof=1) + (n1-1)*np.var(react_vals,ddof=1)) / (2*n1 - 2))
                hedges_g = (np.mean(tcn_vals) - np.mean(react_vals)) / (pooled_std + 1e-12)
                # Correction factor
                correction = 1 - 3 / (4 * (2*n1 - 2) - 1)
                hedges_g *= correction

                print(f"  {label}: TCN={scale*np.mean(tcn_vals):.1f}, React={scale*np.mean(react_vals):.1f}, "
                      f"W={stat:.0f}, p={p:.4f}, Hedges' g={hedges_g:.3f}")

    # Save results
    output = {
        "n_subjects": len(all_subjects),
        "n_controllers": len(summary),
        "tcn_checkpoint": str(ckpt_path),
        "summary": summary,
        "per_subject": {name: trials for name, trials in all_results.items()},
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, default=str))
    print(f"\nSaved: {output_path}")

    return output


def step_compute_statistics(replay_results: dict, output_path: Path) -> dict:
    """Step 6: Compute proper effect sizes and clinical interpretability."""
    print("=" * 80)
    print("STEP 6: EFFECT SIZES AND CLINICAL INTERPRETATION")
    print("=" * 80)

    from scipy import stats as sp_stats

    results = {}
    per_subject = replay_results.get("per_subject", {})

    # Compare TCN Predictive vs each baseline
    tcn_trials = per_subject.get("TCN Predictive", [])
    if not tcn_trials:
        print("  No TCN results available")
        return results

    baselines = ["Fixed Schedule", "Reactive Threshold", "PI Controller"]

    for baseline_name in baselines:
        baseline_trials = per_subject.get(baseline_name, [])
        if len(baseline_trials) < 5:
            continue

        tcn_by_subj = {t["subject"]: t for t in tcn_trials}
        base_by_subj = {t["subject"]: t for t in baseline_trials}
        common = sorted(set(tcn_by_subj) & set(base_by_subj))

        if len(common) < 5:
            continue

        comparison = {"n_subjects": len(common), "metrics": {}}

        for metric, label in [
            ("stim_hit_rate", "Stimulation Hit Rate"),
            ("wasted_stim_pct", "Wasted Stimulation %"),
            ("stim_pct", "Stimulation Time %"),
            ("stim_mean_delta", "Mean PAC Change After Stim"),
        ]:
            tcn_vals = np.array([tcn_by_subj[s][metric] for s in common])
            base_vals = np.array([base_by_subj[s][metric] for s in common])
            diff = tcn_vals - base_vals

            # Wilcoxon signed-rank test (nonparametric paired test)
            nonzero = np.abs(diff) > 1e-10
            if nonzero.sum() >= 5:
                w_stat, w_p = sp_stats.wilcoxon(diff[nonzero])
            else:
                w_stat, w_p = 0.0, 1.0

            # Hedges' g (bias-corrected Cohen's d)
            n = len(common)
            pooled_std = np.sqrt(
                ((n-1)*np.var(tcn_vals, ddof=1) + (n-1)*np.var(base_vals, ddof=1))
                / (2*n - 2)
            )
            d = (np.mean(tcn_vals) - np.mean(base_vals)) / (pooled_std + 1e-12)
            correction = 1 - 3 / (4*(2*n-2) - 1)
            hedges_g = d * correction

            # 95% CI for Hedges' g (approximate)
            se_g = np.sqrt(2/n + hedges_g**2 / (2*n))
            ci_low = hedges_g - 1.96 * se_g
            ci_high = hedges_g + 1.96 * se_g

            # Clinical interpretation
            if abs(hedges_g) < 0.2:
                effect_interp = "negligible"
            elif abs(hedges_g) < 0.5:
                effect_interp = "small"
            elif abs(hedges_g) < 0.8:
                effect_interp = "medium"
            else:
                effect_interp = "large"

            comparison["metrics"][metric] = {
                "label": label,
                "tcn_mean": float(np.mean(tcn_vals)),
                "tcn_std": float(np.std(tcn_vals, ddof=1)),
                "baseline_mean": float(np.mean(base_vals)),
                "baseline_std": float(np.std(base_vals, ddof=1)),
                "mean_diff": float(np.mean(diff)),
                "wilcoxon_W": float(w_stat),
                "wilcoxon_p": float(w_p),
                "hedges_g": float(hedges_g),
                "hedges_g_ci_95": [float(ci_low), float(ci_high)],
                "effect_interpretation": effect_interp,
            }

            sig_str = "*" if w_p < 0.05 else ""
            scale = 100.0 if metric == "stim_hit_rate" else 1.0
            print(f"  {label} (TCN vs {baseline_name}):")
            print(f"    TCN: {scale*np.mean(tcn_vals):.2f} +/- {scale*np.std(tcn_vals,ddof=1):.2f}")
            print(f"    Base: {scale*np.mean(base_vals):.2f} +/- {scale*np.std(base_vals,ddof=1):.2f}")
            print(f"    Hedges' g = {hedges_g:.3f} [{ci_low:.3f}, {ci_high:.3f}] ({effect_interp})")
            print(f"    Wilcoxon W={w_stat:.0f}, p={w_p:.4f}{sig_str}")

        results[f"TCN_vs_{baseline_name.replace(' ', '_')}"] = comparison

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {output_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Full pipeline: preprocess → train → validate")
    parser.add_argument("--bids-root", default="data/raw/ds005048")
    parser.add_argument("--processed-dir", default="data/processed")
    parser.add_argument("--models-dir", default="models")
    parser.add_argument("--horizon", type=int, default=5)
    parser.add_argument("--lookback", type=int, default=20)
    parser.add_argument("--target-smooth", type=int, default=1,
                        help="Target smoothing window (1=raw, 5=smoothed)")
    parser.add_argument("--skip-preprocess", action="store_true")
    args = parser.parse_args()

    bids_root = Path(args.bids_root)
    processed_dir = Path(args.processed_dir)
    models_dir = Path(args.models_dir)
    dataset_dir = processed_dir / f"multiscale_temporal_lb{args.lookback}_hz{args.horizon}_ts{args.target_smooth}"

    t0 = time.time()

    # Step 1: Preprocess
    if not args.skip_preprocess:
        step_preprocess(bids_root, processed_dir)

    # Step 2: Spectral cache
    step_spectral_cache(processed_dir)

    # Step 3: Build temporal dataset
    step_build_dataset(processed_dir, bids_root, dataset_dir,
                       args.lookback, args.horizon, args.target_smooth)

    # Step 4: Train TCN
    ckpt_path = step_train_tcn(dataset_dir, models_dir,
                                args.lookback, args.horizon, args.target_smooth)

    # Step 5: Real-data replay with TCN
    scalers_path = dataset_dir / "scalers.npz"
    replay_output = Path("results") / f"tcn_replay_lb{args.lookback}_hz{args.horizon}_ts{args.target_smooth}.json"
    replay_results = step_replay_with_tcn(
        processed_dir, bids_root, ckpt_path, scalers_path, replay_output
    )

    # Step 6: Statistics
    stats_output = Path("results") / f"effect_sizes_lb{args.lookback}_hz{args.horizon}_ts{args.target_smooth}.json"
    step_compute_statistics(replay_results, stats_output)

    elapsed = time.time() - t0
    print(f"\n{'='*80}")
    print(f"PIPELINE COMPLETE ({elapsed:.0f}s)")
    print(f"{'='*80}")
    print(f"  Checkpoint: {ckpt_path}")
    print(f"  Replay results: {replay_output}")
    print(f"  Effect sizes: {stats_output}")


if __name__ == "__main__":
    main()
