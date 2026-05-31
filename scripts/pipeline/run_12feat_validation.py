"""
Train 12-feature TCN (PAC+context only) and run 35-subject controller replay.

Drops spectral features (indices 0-60) that encode subject anatomy.
Keeps only PAC trajectory + stimulation context (indices 61-72).

Reproduces the headline controller comparison with the improved model:
  - Trains from existing normalized dataset (no rebuild needed)
  - Runs same replay logic as scripts/pipeline/run_tcn_validation.py
  - Prints comparison vs original 73-feature results

Usage:
    python scripts/pipeline/run_12feat_validation.py [--no-train]  # --no-train to skip training if ckpt exists
"""

from __future__ import annotations

import argparse
import json
import sys
import time as time_mod
from collections import deque
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from scipy import stats
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN

# Feature slice: PAC + context only
FEAT_START = 61
FEAT_END = 73  # exclusive
N_FEATURES = FEAT_END - FEAT_START  # 12

DATASET_DIR = ROOT / "data/processed/multiscale_temporal_lb20_hz5_ts1"
PROCESSED_DIR = ROOT / "data/processed"
RAW_ROOT = ROOT / "data/raw/ds005048"
CKPT_PATH = ROOT / "models/best_12feat_tcn_lb20_hz5_ts1.pth"
RESULT_PATH = ROOT / "results/metrics/controller_comparison_12feat.json"

# -----------------------------------------------------------------------
# Training
# -----------------------------------------------------------------------

class FeatureMaskedDataset(Dataset):
    """Load multiscale npz, slice features to PAC+context only."""
    def __init__(self, npz_path: Path) -> None:
        d = np.load(npz_path, allow_pickle=True)
        x_full = d["x_seq"]  # (N, T, 73)
        x_masked = x_full[:, :, FEAT_START:FEAT_END]  # (N, T, 12)
        self.x = torch.from_numpy(x_masked).float()
        self.y_future = torch.from_numpy(d["y_future_norm"]).float()
        self.y_delta = torch.from_numpy(d["y_delta_norm"]).float()
        self.last_pac = torch.from_numpy(d["last_pac"]).float()

    def __len__(self) -> int:
        return self.x.shape[0]

    def __getitem__(self, i: int) -> Dict[str, torch.Tensor]:
        return {
            "x_seq": self.x[i],
            "y_future": self.y_future[i],
            "y_delta": self.y_delta[i],
            "last_pac": self.last_pac[i],
        }


def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / (ss_tot + 1e-12))


def _corr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if np.std(y_true) < 1e-12 or np.std(y_pred) < 1e-12:
        return 0.0
    return float(np.corrcoef(y_true, y_pred)[0, 1])


def train_12feat_tcn(seed: int = 42) -> Path:
    """Train MultiscaleCausalTCN with 12 features, save checkpoint, return path."""
    torch.manual_seed(seed)
    np.random.seed(seed)

    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    train_ds = FeatureMaskedDataset(DATASET_DIR / "train_multiscale.npz")
    val_ds = FeatureMaskedDataset(DATASET_DIR / "val_multiscale.npz")
    test_ds = FeatureMaskedDataset(DATASET_DIR / "test_multiscale.npz")

    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=256, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=256, shuffle=False, num_workers=0)

    meta = json.loads((DATASET_DIR / "metadata.json").read_text())
    s = np.load(DATASET_DIR / "scalers.npz")
    yf_mean = float(s["y_future_mean"])
    yf_std = float(s["y_future_std"])
    yd_mean = float(s["y_delta_mean"])
    yd_std = float(s["y_delta_std"])

    cfg = ModelConfig(
        n_features=N_FEATURES,
        hidden=64,
        kernel_size=3,
        dilations=[1, 2, 4, 8],
        dropout=0.2,
        pool_type="attention",
    )
    model = MultiscaleCausalTCN(cfg).to(device)
    print(f"Device: {device}  |  Params: {model.count_parameters():,}  |  Features: {N_FEATURES}")
    print(f"Train/Val/Test: {len(train_ds)}/{len(val_ds)}/{len(test_ds)}")

    huber = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=5
    )

    best_val_r2 = -np.inf
    no_improve = 0
    patience = 20
    epochs = 150

    print(f"\n{'Epoch':>6s} {'TrainLoss':>10s} {'ValR2':>8s} {'TestR2':>8s} {'Best':>6s}")
    print("-" * 45)

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for batch in train_loader:
            x = batch["x_seq"].to(device)
            y_f = batch["y_future"].to(device)
            y_d = batch["y_delta"].to(device)
            optimizer.zero_grad()
            out = model(x)
            loss = huber(out["future"].squeeze(-1), y_f) + 0.3 * huber(out["delta"].squeeze(-1), y_d)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item() * len(x)
        train_loss = total_loss / len(train_ds)

        model.eval()
        with torch.no_grad():
            y_true_val, y_pred_val = [], []
            for batch in val_loader:
                x = batch["x_seq"].to(device)
                out = model(x)
                y_pred_val.append(out["future"].squeeze(-1).cpu().numpy())
                y_true_val.append(batch["y_future"].numpy())
            y_true_val = np.concatenate(y_true_val)
            y_pred_val = np.concatenate(y_pred_val)
            val_r2 = _r2(y_true_val, y_pred_val)

            y_true_te, y_pred_te = [], []
            for batch in test_loader:
                x = batch["x_seq"].to(device)
                out = model(x)
                y_pred_te.append(out["future"].squeeze(-1).cpu().numpy())
                y_true_te.append(batch["y_future"].numpy())
            y_true_te = np.concatenate(y_true_te)
            y_pred_te = np.concatenate(y_pred_te)
            test_r2 = _r2(y_true_te, y_pred_te)

        scheduler.step(val_r2)

        is_best = val_r2 > best_val_r2
        if is_best:
            best_val_r2 = val_r2
            no_improve = 0
            torch.save({
                "cfg": {
                    "n_features": N_FEATURES,
                    "hidden": 64,
                    "kernel_size": 3,
                    "dilations": [1, 2, 4, 8],
                    "dropout": 0.2,
                    "pool_type": "attention",
                },
                "model_state_dict": model.state_dict(),
                "metadata": {
                    "lookback": meta["lookback"],
                    "horizon": meta["horizon"],
                    "n_features": N_FEATURES,
                    "feat_start": FEAT_START,
                    "feat_end": FEAT_END,
                    "val_r2": round(val_r2, 4),
                    "test_r2": round(test_r2, 4),
                    "seed": seed,
                },
                "scalers": {
                    "feature_mean": s["feature_mean"][FEAT_START:FEAT_END],
                    "feature_std": s["feature_std"][FEAT_START:FEAT_END],
                    "y_future_mean": yf_mean,
                    "y_future_std": yf_std,
                    "y_delta_mean": yd_mean,
                    "y_delta_std": yd_std,
                },
            }, CKPT_PATH)
        else:
            no_improve += 1

        if epoch % 10 == 0 or epoch <= 5 or is_best:
            mark = " *" if is_best else ""
            print(f"{epoch:>6d} {train_loss:>10.4f} {val_r2:>8.4f} {test_r2:>8.4f}{mark}")

        if no_improve >= patience:
            print(f"\nEarly stopping at epoch {epoch}")
            break

    print(f"\nBest val R2: {best_val_r2:.4f}")
    print(f"Saved: {CKPT_PATH}")
    return CKPT_PATH


# -----------------------------------------------------------------------
# Controller replay (same logic as run_tcn_validation.py)
# -----------------------------------------------------------------------

class FixedScheduleCtrl:
    name = "Fixed Schedule"
    def __init__(self, stim): self.stim = stim; self.t = 0
    def reset(self): self.t = 0
    def step(self, pac, **kw):
        a = int(self.stim[self.t]) if self.t < len(self.stim) else 0
        self.t += 1; return a


class ReactiveCtrl:
    name = "Reactive Threshold"
    def __init__(self, w=30, z_thresh=0.5): self.w = w; self.z = z_thresh; self.buf = []
    def reset(self): self.buf = []
    def step(self, pac, **kw):
        self.buf.append(pac)
        if len(self.buf) > self.w: self.buf.pop(0)
        if len(self.buf) < 10: return 0
        mu = np.mean(self.buf); sig = np.std(self.buf) + 1e-12
        return 1 if (pac - mu) / sig < -self.z else 0


class TCN12FeatCtrl:
    """TCN predictive controller using only PAC+context features (no spectral)."""
    name = "TCN Predictive (12-feat)"

    def __init__(self, model, feat_mean, feat_std, yf_mean, yf_std,
                 yd_mean, yd_std, lookback, device, delta_z_thresh=0.3):
        self.model = model
        self.feat_mean = feat_mean
        self.feat_std = feat_std
        self.yf_mean = yf_mean; self.yf_std = yf_std
        self.yd_mean = yd_mean; self.yd_std = yd_std
        self.lookback = lookback; self.device = device
        self.delta_z_thresh = delta_z_thresh
        self.seq_buf = deque(maxlen=lookback)
        self.pac_buf = deque(maxlen=max(lookback, 32))
        self.baseline_buf = []
        self.state = 0; self.t_in_state = 0

    def reset(self):
        self.seq_buf.clear(); self.pac_buf.clear()
        self.baseline_buf = []; self.state = 0; self.t_in_state = 0

    def _pac_features(self, pac_cur):
        hist = list(self.pac_buf) + [pac_cur]
        def ml(k):
            k = min(k, len(hist))
            return float(np.mean(hist[-k:])) if k > 0 else float(pac_cur)
        d1 = float(pac_cur - hist[-2]) if len(hist) >= 2 else 0.0
        d4 = float(pac_cur - hist[-5]) if len(hist) >= 5 else 0.0
        return np.array([pac_cur, ml(2), ml(4), ml(8), ml(16), d1, d4], dtype=np.float32)

    def _build_feature(self, pac, stim_state_val, time_since_switch, stim_frac, c_sin, c_cos):
        pac_feats = self._pac_features(pac)  # 7
        ctx = np.array([stim_state_val, min(time_since_switch/60, 1),
                        min(max(stim_frac, 0), 1), c_sin, c_cos], dtype=np.float32)  # 5
        x = np.concatenate([pac_feats, ctx])  # 12 features
        return ((x - self.feat_mean) / (self.feat_std + 1e-8)).astype(np.float32)

    def _predict(self):
        if len(self.seq_buf) < self.lookback:
            return None
        x_seq = np.stack(list(self.seq_buf), axis=0)[None, ...]
        x_t = torch.from_numpy(x_seq).float().to(self.device)
        with torch.no_grad():
            out = self.model(x_t)
        return float(out["delta"].item()), float(out["future"].item()) * self.yf_std + self.yf_mean

    def step(self, pac, stim_state_val=0.0, time_since_switch=0.0,
             stim_frac=0.0, cycle_sin=0.0, cycle_cos=1.0, **kw):
        x = self._build_feature(pac, stim_state_val, time_since_switch, stim_frac, cycle_sin, cycle_cos)
        self.seq_buf.append(x)
        self.pac_buf.append(float(pac))
        self.baseline_buf.append(pac)
        if len(self.baseline_buf) > 30: self.baseline_buf.pop(0)

        pred = self._predict()
        mu = np.mean(self.baseline_buf) if len(self.baseline_buf) >= 10 else pac
        sig = np.std(self.baseline_buf) + 1e-12 if len(self.baseline_buf) >= 10 else 1.0
        z = (pac - mu) / sig

        desired = None
        if pred is not None:
            delta_z = pred[0]
            if delta_z < -self.delta_z_thresh: desired = 1
            elif delta_z > self.delta_z_thresh: desired = 0

        if desired is None:
            if z < -0.5: desired = 1
            elif z > 0.5: desired = 0
            else: desired = self.state

        if desired != self.state:
            if self.t_in_state >= 3: self.state = desired; self.t_in_state = 0
        else:
            self.t_in_state += 1
        return self.state


class AlignmentOracleCtrl:
    name = "Alignment Oracle"
    def __init__(self, pac): self.median = np.median(pac); self.pac = pac; self.t = 0
    def reset(self): self.t = 0
    def step(self, pac, **kw): self.t += 1; return 1 if pac < self.median else 0


def evaluate_epoch_alignment(pac, decisions):
    median_pac = np.median(pac)
    low_mask = pac < median_pac; high_mask = ~low_mask
    stim_mask = decisions == 1; rest_mask = decisions == 0
    low_stim = float(np.mean(stim_mask[low_mask])) if low_mask.sum() > 0 else 0.0
    high_rest = float(np.mean(rest_mask[high_mask])) if high_mask.sum() > 0 else 0.0
    alignment = (low_stim + high_rest) / 2
    mean_pac_stim = float(np.mean(pac[stim_mask])) if stim_mask.sum() > 0 else 0
    mean_pac_rest = float(np.mean(pac[rest_mask])) if rest_mask.sum() > 0 else 0
    return {
        "alignment_score": alignment,
        "low_stim_rate": low_stim,
        "high_rest_rate": high_rest,
        "stim_pct": 100.0 * float(np.mean(stim_mask)),
        "mean_pac_stim": mean_pac_stim,
        "mean_pac_rest": mean_pac_rest,
        "pac_gap": mean_pac_rest - mean_pac_stim,
    }


def hedges_g(a: np.ndarray, b: np.ndarray):
    n = len(a)
    pooled = np.sqrt(((n-1)*np.var(a, ddof=1) + (n-1)*np.var(b, ddof=1)) / (2*n - 2))
    d = (np.mean(a) - np.mean(b)) / (pooled + 1e-12)
    c = 1 - 3 / (4*(2*n-2) - 1)
    g = d * c
    se = np.sqrt(2/n + g**2 / (2*n))
    return g, g - 1.96*se, g + 1.96*se


def load_subjects(processed_dir: Path, raw_root: Path) -> List[Dict]:
    subjects = []
    for split in ("train", "val", "test"):
        d = np.load(processed_dir / f"{split}_data.npz", allow_pickle=True)
        pac = d["pac"].astype(np.float64)
        subj_ids = d["subjects"]
        for subj in np.unique(subj_ids):
            mask = subj_ids == subj
            subj_pac = pac[mask]
            tsv = raw_root / subj / "eeg" / f"{subj}_task-40HzAuditoryEntrainment_events.tsv"
            if not tsv.exists():
                continue
            events = pd.read_csv(tsv, sep="\t").sort_values("onset").reset_index(drop=True)
            n = len(subj_pac)
            t = np.arange(n, dtype=np.float64) * 1.0 + 1.0
            stim_state = np.zeros(n, dtype=np.int32)
            for _, row in events.iterrows():
                onset, duration = float(row["onset"]), float(row["duration"])
                if int(row["value"]) == 2:
                    stim_state[(t >= onset) & (t < onset + duration)] = 1
            subjects.append({
                "subject": subj, "pac": subj_pac,
                "stim_state": stim_state, "time": t, "split": split,
            })
    return subjects


def run_replay(ckpt_path: Path) -> Dict:
    device = torch.device("cpu")
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    cfg = ModelConfig(**ckpt["cfg"])
    model = MultiscaleCausalTCN(cfg)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    lookback = int(ckpt["metadata"]["lookback"])
    scalers = ckpt["scalers"]

    feat_mean = scalers["feature_mean"].astype(np.float32)
    feat_std = scalers["feature_std"].astype(np.float32)
    yf_mean = float(scalers["y_future_mean"])
    yf_std = float(scalers["y_future_std"])
    yd_mean = float(scalers["y_delta_mean"])
    yd_std = float(scalers["y_delta_std"])

    print(f"\nCheckpoint: val_r2={ckpt['metadata']['val_r2']}, test_r2={ckpt['metadata']['test_r2']}")
    print(f"Model: {model.count_parameters():,} params, {N_FEATURES} features, lookback={lookback}")

    subjects = load_subjects(PROCESSED_DIR, RAW_ROOT)
    print(f"Loaded {len(subjects)} subjects\n")

    tcn_args = dict(model=model, feat_mean=feat_mean, feat_std=feat_std,
                    yf_mean=yf_mean, yf_std=yf_std, yd_mean=yd_mean, yd_std=yd_std,
                    lookback=lookback, device=device, delta_z_thresh=0.3)

    all_results: Dict[str, List[Dict]] = {}

    for si, subj_data in enumerate(subjects):
        pac = subj_data["pac"]
        stim_state_arr = subj_data["stim_state"]
        n = len(pac)
        t_arr = subj_data["time"]

        cycle = 60.0
        phase = (t_arr % cycle) / cycle
        c_sin = np.sin(2 * np.pi * phase)
        c_cos = np.cos(2 * np.pi * phase)

        switch_times = [0.0]
        for i in range(1, n):
            if stim_state_arr[i] != stim_state_arr[i-1]:
                switch_times.append(t_arr[i])
        sw = np.array(switch_times)
        idx = np.clip(np.searchsorted(sw, t_arr, side="right") - 1, 0, len(sw)-1)
        tss = t_arr - sw[idx]

        stim_frac = np.zeros(n)
        sh = deque(maxlen=20)
        for i in range(n):
            sh.append(float(stim_state_arr[i]))
            stim_frac[i] = np.mean(sh)

        controllers = [
            FixedScheduleCtrl(stim_state_arr),
            ReactiveCtrl(),
            TCN12FeatCtrl(**tcn_args),
            AlignmentOracleCtrl(pac),
        ]

        for ctrl in controllers:
            ctrl.reset()
            decisions = np.zeros(n, dtype=np.int32)
            for ti in range(n):
                if isinstance(ctrl, TCN12FeatCtrl):
                    decisions[ti] = ctrl.step(
                        pac[ti], stim_state_val=float(stim_state_arr[ti]),
                        time_since_switch=tss[ti], stim_frac=stim_frac[ti],
                        cycle_sin=c_sin[ti], cycle_cos=c_cos[ti])
                else:
                    decisions[ti] = ctrl.step(pac[ti])

            metrics = evaluate_epoch_alignment(pac, decisions)
            metrics["subject"] = subj_data["subject"]
            if ctrl.name not in all_results:
                all_results[ctrl.name] = []
            all_results[ctrl.name].append(metrics)

    return all_results


def print_results(all_results: Dict[str, List[Dict]]) -> None:
    ctrl_order = ["Fixed Schedule", "Reactive Threshold",
                  "TCN Predictive (12-feat)", "Alignment Oracle"]

    print(f"\n{'='*80}")
    print("12-FEATURE TCN CONTROLLER COMPARISON (N=35 subjects, real EEG)")
    print(f"{'='*80}")
    print(f"{'Controller':<30s} {'Align%':>8s} {'LowStim%':>9s} {'HiRest%':>8s} {'Stim%':>6s}")
    print("-" * 65)

    summary = {}
    for name in ctrl_order:
        trials = all_results.get(name, [])
        if not trials:
            continue
        align = np.mean([t["alignment_score"] for t in trials])
        low_stim = np.mean([t["low_stim_rate"] for t in trials])
        high_rest = np.mean([t["high_rest_rate"] for t in trials])
        stim_pct = np.mean([t["stim_pct"] for t in trials])
        print(f"{name:<30s} {100*align:>7.1f}% {100*low_stim:>8.1f}% "
              f"{100*high_rest:>7.1f}% {stim_pct:>5.1f}%")
        summary[name] = {
            "alignment": round(100*align, 1),
            "low_stim": round(100*low_stim, 1),
            "high_rest": round(100*high_rest, 1),
            "stim_pct": round(stim_pct, 1),
        }

    print(f"\n{'='*80}")
    print("PAC TARGETING GAP")
    print(f"{'='*80}")
    print(f"{'Controller':<30s} {'PAC|stim':>12s} {'PAC|rest':>12s} {'Gap×10⁻⁶':>10s}")
    print("-" * 65)
    for name in ctrl_order:
        trials = all_results.get(name, [])
        if not trials:
            continue
        ps = np.mean([t["mean_pac_stim"] for t in trials])
        pr = np.mean([t["mean_pac_rest"] for t in trials])
        gap = pr - ps
        print(f"{name:<30s} {ps:>12.6f} {pr:>12.6f} {gap*1e6:>9.1f}")

    # Stats: 12-feat TCN vs Reactive
    tcn_align = np.array([t["alignment_score"] for t in all_results.get("TCN Predictive (12-feat)", [])])
    rxn_align = np.array([t["alignment_score"] for t in all_results.get("Reactive Threshold", [])])
    tcn_ls = np.array([t["low_stim_rate"] for t in all_results.get("TCN Predictive (12-feat)", [])])
    rxn_ls = np.array([t["low_stim_rate"] for t in all_results.get("Reactive Threshold", [])])

    if len(tcn_align) > 0:
        g_align, lo_a, hi_a = hedges_g(tcn_align, rxn_align)
        g_ls, lo_ls, hi_ls = hedges_g(tcn_ls, rxn_ls)
        _, p_align = stats.wilcoxon(tcn_align - rxn_align)
        _, p_ls = stats.wilcoxon(tcn_ls - rxn_ls)

        print(f"\n{'='*80}")
        print("STATISTICAL COMPARISON: 12-feat TCN vs Reactive")
        print(f"{'='*80}")
        print(f"Alignment:     Hedges' g = {g_align:.2f} [{lo_a:.2f}, {hi_a:.2f}], p = {p_align:.4f}")
        print(f"Low-PAC Stim:  Hedges' g = {g_ls:.2f} [{lo_ls:.2f}, {hi_ls:.2f}], p = {p_ls:.4f}")

    # Comparison vs original 73-feat numbers
    print(f"\n{'='*80}")
    print("COMPARISON vs ORIGINAL 73-FEATURE MODEL")
    print(f"{'='*80}")
    print(f"{'Metric':<30s} {'73-feat (old)':>14s} {'12-feat (new)':>14s} {'Delta':>8s}")
    print("-" * 65)

    orig = {"Alignment (TCN)": 72.1, "Low-PAC Stim (TCN)": 82.6,
            "Alignment (Reactive)": 64.5, "Low-PAC Stim (Reactive)": 51.7}

    if "TCN Predictive (12-feat)" in summary:
        new = {
            "Alignment (TCN)": summary["TCN Predictive (12-feat)"]["alignment"],
            "Low-PAC Stim (TCN)": summary["TCN Predictive (12-feat)"]["low_stim"],
            "Alignment (Reactive)": summary.get("Reactive Threshold", {}).get("alignment", 0),
            "Low-PAC Stim (Reactive)": summary.get("Reactive Threshold", {}).get("low_stim", 0),
        }
        for k in orig:
            delta = new[k] - orig[k]
            sign = "+" if delta >= 0 else ""
            print(f"{k:<30s} {orig[k]:>13.1f}% {new[k]:>13.1f}% {sign}{delta:>6.1f}%")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-train", action="store_true",
                        help="Skip training, load existing checkpoint")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    t0 = time_mod.time()

    if args.no_train and CKPT_PATH.exists():
        print(f"Skipping training — loading {CKPT_PATH}")
    else:
        print("=" * 60)
        print("TRAINING 12-FEATURE TCN")
        print("=" * 60)
        train_12feat_tcn(seed=args.seed)

    print("\n" + "=" * 60)
    print("RUNNING 35-SUBJECT CONTROLLER REPLAY")
    print("=" * 60)
    all_results = run_replay(CKPT_PATH)
    print_results(all_results)

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary_out = {}
    for name, trials in all_results.items():
        summary_out[name] = {
            "alignment_mean": round(float(np.mean([t["alignment_score"] for t in trials])), 4),
            "low_stim_mean": round(float(np.mean([t["low_stim_rate"] for t in trials])), 4),
            "high_rest_mean": round(float(np.mean([t["high_rest_rate"] for t in trials])), 4),
            "pac_gap_mean": round(float(np.mean([t["pac_gap"] for t in trials])), 9),
            "n_subjects": len(trials),
        }
    RESULT_PATH.write_text(json.dumps(summary_out, indent=2))
    print(f"\nResults saved to {RESULT_PATH}")
    print(f"Total time: {time_mod.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
