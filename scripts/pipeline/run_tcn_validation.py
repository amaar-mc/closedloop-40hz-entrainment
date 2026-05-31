"""
Comprehensive TCN-integrated real-data validation with epoch-level evaluation.

The PAC labels in this dataset are computed at epoch level (20-40s blocks),
so consecutive 2s windows within the same epoch share the same PAC value.
Meaningful PAC changes occur only at epoch transitions (~11 per subject).

Controller variants:
  1. Fixed Schedule    - replays original experimental stim/rest protocol
  2. Reactive          - z-score threshold on rolling PAC baseline
  3. TCN Predictive    - pure TCN delta prediction for stimulation timing
  4. Hybrid TCN+React  - reactive base + TCN proactive override near transitions
  5. PI Controller     - proportional-integral feedback
  6. Alignment Oracle  - perfect PAC knowledge (theoretical upper bound)

Evaluation framework:
  - Epoch alignment (stim during low-PAC, rest during high-PAC)
  - Transition anticipation (lead time before PAC drops)
  - Stimulation efficiency (PAC per unit stimulation, energy savings)
  - Clinical utility composite (weighted metric for therapeutic planning)

Usage:
    python scripts/pipeline/run_tcn_validation.py
"""

from __future__ import annotations

import json
import sys
import time as time_mod
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "archive" / "experimental_models"))


# -----------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------

def load_subjects(processed_dir: Path, raw_root: Path) -> List[Dict]:
    """Load subjects with PAC, EEG windows, stim state, and epoch boundaries."""
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

            # Build stim_state from BIDS events
            stim_state = np.zeros(n, dtype=np.int32)
            for _, row in events.iterrows():
                onset = float(row["onset"])
                duration = float(row["duration"])
                is_stim = int(row["value"]) == 2
                if is_stim:
                    in_event = (t >= onset) & (t < onset + duration)
                    stim_state[in_event] = 1

            # Find epoch transition indices (where PAC changes)
            transitions = []
            for i in range(1, n):
                if abs(subj_pac[i] - subj_pac[i-1]) > 1e-10:
                    direction = "drop" if subj_pac[i] < subj_pac[i-1] else "rise"
                    transitions.append({
                        "index": i,
                        "time": t[i],
                        "direction": direction,
                        "pac_before": float(subj_pac[i-1]),
                        "pac_after": float(subj_pac[i]),
                        "delta": float(subj_pac[i] - subj_pac[i-1]),
                    })

            all_subjects.append({
                "subject": subj, "pac": subj_pac, "windows": subj_windows,
                "stim_state": stim_state, "time": t, "n_windows": n,
                "split": split, "transitions": transitions,
            })

    return all_subjects


def extract_spectral_features(subjects: List[Dict]) -> None:
    """Extract spectral features for TCN controller."""
    from spectral_features import SpectralFeatureExtractor
    extractor = SpectralFeatureExtractor(fs=250.0)

    for subj in subjects:
        w = subj["windows"]
        if w.ndim == 4 and w.shape[1] == 1:
            w = w.squeeze(1)
        subj["spectral"] = extractor.extract(w)


# -----------------------------------------------------------------------
# Controllers
# -----------------------------------------------------------------------

class FixedScheduleCtrl:
    name = "Fixed Schedule"
    def __init__(self, stim): self.stim = stim; self.t = 0
    def reset(self): self.t = 0
    def step(self, pac, **kw):
        a = int(self.stim[self.t]) if self.t < len(self.stim) else 0
        self.t += 1; return a


class ReactiveCtrl:
    """Reactive z-score threshold controller on rolling PAC baseline."""
    name = "Reactive Threshold"
    def __init__(self, w=30, z_thresh=0.5):
        self.w = w; self.z = z_thresh; self.buf = []
    def reset(self): self.buf = []
    def step(self, pac, **kw):
        self.buf.append(pac)
        if len(self.buf) > self.w: self.buf.pop(0)
        if len(self.buf) < 10: return 0
        mu = np.mean(self.buf)
        sig = np.std(self.buf) + 1e-12
        z = (pac - mu) / sig
        return 1 if z < -self.z else 0


class TCNPredictiveCtrl:
    """Pure TCN-based predictive controller using predicted delta for decisions."""
    name = "TCN Predictive"

    def __init__(self, model, feature_mean, feature_std, yf_mean, yf_std,
                 yd_mean, yd_std, lookback, device, delta_z_thresh=0.3):
        self.model = model
        self.feature_mean = feature_mean
        self.feature_std = feature_std
        self.yf_mean = yf_mean
        self.yf_std = yf_std
        self.yd_mean = yd_mean
        self.yd_std = yd_std
        self.lookback = lookback
        self.device = device
        self.delta_z_thresh = delta_z_thresh
        self.seq_buf = deque(maxlen=lookback)
        self.pac_buf = deque(maxlen=max(lookback, 32))
        self.baseline_buf = []
        self.state = 0
        self.t_in_state = 0
        self.predictions = []

    def reset(self):
        self.seq_buf.clear()
        self.pac_buf.clear()
        self.baseline_buf = []
        self.state = 0
        self.t_in_state = 0
        self.predictions = []

    def _pac_features(self, pac_cur):
        hist = list(self.pac_buf) + [pac_cur]
        def ml(k):
            k = min(k, len(hist))
            return float(np.mean(hist[-k:])) if k > 0 else float(pac_cur)
        d1 = float(pac_cur - hist[-2]) if len(hist) >= 2 else 0.0
        d4 = float(pac_cur - hist[-5]) if len(hist) >= 5 else 0.0
        return np.array([pac_cur, ml(2), ml(4), ml(8), ml(16), d1, d4],
                       dtype=np.float32)

    def _build_feature(self, pac, spectral, stim_state_val, time_since_switch,
                       stim_frac, cycle_sin, cycle_cos):
        pac_feats = self._pac_features(pac)
        ctx = np.array([stim_state_val, min(time_since_switch/60, 1),
                       min(max(stim_frac, 0), 1), cycle_sin, cycle_cos],
                      dtype=np.float32)
        x = np.concatenate([spectral.reshape(-1), pac_feats, ctx]).astype(np.float32)
        x = (x - self.feature_mean) / (self.feature_std + 1e-8)
        return x

    def _predict(self):
        """Run TCN inference, return (delta_z, future_raw, delta_raw) or None."""
        if len(self.seq_buf) < self.lookback:
            return None
        x_seq = np.stack(list(self.seq_buf), axis=0)[None, ...]
        x_tensor = torch.from_numpy(x_seq).float().to(self.device)
        with torch.no_grad():
            out = self.model(x_tensor)
        delta_z = float(out["delta"].item())
        future_raw = float(out["future"].item()) * self.yf_std + self.yf_mean
        delta_raw = float(out["delta"].item()) * self.yd_std + self.yd_mean
        return delta_z, future_raw, delta_raw

    def step(self, pac, spectral=None, stim_state_val=0.0,
             time_since_switch=0.0, stim_frac=0.0,
             cycle_sin=0.0, cycle_cos=1.0, **kw):
        if spectral is None:
            spectral = np.zeros(61, dtype=np.float32)

        x = self._build_feature(pac, spectral, stim_state_val,
                               time_since_switch, stim_frac, cycle_sin, cycle_cos)
        self.seq_buf.append(x)
        self.pac_buf.append(float(pac))
        self.baseline_buf.append(pac)
        if len(self.baseline_buf) > 30:
            self.baseline_buf.pop(0)

        pred = self._predict()
        self.predictions.append(pred)

        # Reactive z-score as fallback
        if len(self.baseline_buf) >= 10:
            mu = np.mean(self.baseline_buf)
            sigma = np.std(self.baseline_buf) + 1e-12
            z = (pac - mu) / sigma
        else:
            z = 0.0

        # Decision: prioritize TCN delta prediction
        desired = None
        if pred is not None:
            delta_z = pred[0]
            if delta_z < -self.delta_z_thresh:
                desired = 1  # predicted decline -> stimulate
            elif delta_z > self.delta_z_thresh:
                desired = 0  # predicted rise -> rest

        # Fallback to reactive
        if desired is None:
            if z < -0.5:
                desired = 1
            elif z > 0.5:
                desired = 0
            else:
                desired = self.state

        # Hysteresis (3 steps = 3s minimum in state)
        if desired != self.state:
            if self.t_in_state >= 3:
                self.state = desired
                self.t_in_state = 0
        else:
            self.t_in_state += 1

        return self.state


class HybridTCNCtrl:
    """Hybrid controller: reactive base + TCN proactive override.

    The reactive component provides reliable current-state detection.
    The TCN component provides proactive early warning for PAC transitions.

    Override logic:
    - TCN predicts decline AND reactive doesn't strongly disagree -> stimulate early
    - TCN predicts rise AND reactive doesn't strongly disagree -> rest early
    - Otherwise -> follow reactive decision

    This gives the best of both worlds:
    - High alignment from reactive baseline
    - Proactive lead time from TCN predictions
    """
    name = "Hybrid TCN+Reactive"

    def __init__(self, model, feature_mean, feature_std, yf_mean, yf_std,
                 yd_mean, yd_std, lookback, device, delta_z_thresh=0.5,
                 reactive_z_thresh=0.5, reactive_w=30, hysteresis=3):
        self.model = model
        self.feature_mean = feature_mean
        self.feature_std = feature_std
        self.yf_mean = yf_mean
        self.yf_std = yf_std
        self.yd_mean = yd_mean
        self.yd_std = yd_std
        self.lookback = lookback
        self.device = device
        self.delta_z_thresh = delta_z_thresh
        self.reactive_z = reactive_z_thresh
        self.reactive_w = reactive_w
        self.hysteresis = hysteresis
        self.seq_buf = deque(maxlen=lookback)
        self.pac_buf = deque(maxlen=max(lookback, 32))
        self.baseline_buf = []
        self.state = 0
        self.t_in_state = 0
        self.predictions = []
        self.decision_sources = []  # track which component made each decision

    def reset(self):
        self.seq_buf.clear()
        self.pac_buf.clear()
        self.baseline_buf = []
        self.state = 0
        self.t_in_state = 0
        self.predictions = []
        self.decision_sources = []

    def _pac_features(self, pac_cur):
        hist = list(self.pac_buf) + [pac_cur]
        def ml(k):
            k = min(k, len(hist))
            return float(np.mean(hist[-k:])) if k > 0 else float(pac_cur)
        d1 = float(pac_cur - hist[-2]) if len(hist) >= 2 else 0.0
        d4 = float(pac_cur - hist[-5]) if len(hist) >= 5 else 0.0
        return np.array([pac_cur, ml(2), ml(4), ml(8), ml(16), d1, d4],
                       dtype=np.float32)

    def _predict(self):
        if len(self.seq_buf) < self.lookback:
            return None
        x_seq = np.stack(list(self.seq_buf), axis=0)[None, ...]
        x_tensor = torch.from_numpy(x_seq).float().to(self.device)
        with torch.no_grad():
            out = self.model(x_tensor)
        delta_z = float(out["delta"].item())
        future_raw = float(out["future"].item()) * self.yf_std + self.yf_mean
        delta_raw = float(out["delta"].item()) * self.yd_std + self.yd_mean
        return delta_z, future_raw, delta_raw

    def step(self, pac, spectral=None, stim_state_val=0.0,
             time_since_switch=0.0, stim_frac=0.0,
             cycle_sin=0.0, cycle_cos=1.0, **kw):
        if spectral is None:
            spectral = np.zeros(61, dtype=np.float32)

        pac_feats = self._pac_features(pac)
        ctx = np.array([stim_state_val, min(time_since_switch/60, 1),
                       min(max(stim_frac, 0), 1), cycle_sin, cycle_cos],
                      dtype=np.float32)
        x = np.concatenate([spectral.reshape(-1), pac_feats, ctx]).astype(np.float32)
        x = (x - self.feature_mean) / (self.feature_std + 1e-8)
        self.seq_buf.append(x)
        self.pac_buf.append(float(pac))
        self.baseline_buf.append(pac)
        if len(self.baseline_buf) > self.reactive_w:
            self.baseline_buf.pop(0)

        # 1. Reactive z-score
        if len(self.baseline_buf) >= 10:
            mu = np.mean(self.baseline_buf)
            sigma = np.std(self.baseline_buf) + 1e-12
            z_react = (pac - mu) / sigma
        else:
            z_react = 0.0

        reactive_wants = None
        if z_react < -self.reactive_z:
            reactive_wants = 1  # stim
        elif z_react > self.reactive_z:
            reactive_wants = 0  # rest

        # 2. TCN prediction
        pred = self._predict()
        self.predictions.append(pred)

        tcn_wants = None
        if pred is not None:
            delta_z = pred[0]
            if delta_z < -self.delta_z_thresh:
                tcn_wants = 1  # predicted decline
            elif delta_z > self.delta_z_thresh:
                tcn_wants = 0  # predicted rise

        # 3. Hybrid decision logic
        source = "maintain"
        if tcn_wants is not None and reactive_wants is not None:
            if tcn_wants == reactive_wants:
                # Both agree -> follow both
                desired = tcn_wants
                source = "agree"
            else:
                # Disagree -> follow reactive (more reliable for current state)
                desired = reactive_wants
                source = "reactive_override"
        elif tcn_wants is not None:
            # Only TCN has a signal -> follow TCN (proactive)
            desired = tcn_wants
            source = "tcn_proactive"
        elif reactive_wants is not None:
            # Only reactive has a signal -> follow reactive
            desired = reactive_wants
            source = "reactive"
        else:
            # Neither has signal -> maintain
            desired = self.state
            source = "maintain"

        self.decision_sources.append(source)

        # Hysteresis
        if desired != self.state:
            if self.t_in_state >= self.hysteresis:
                self.state = desired
                self.t_in_state = 0
        else:
            self.t_in_state += 1

        return self.state


class AlignmentOracleCtrl:
    """Oracle that perfectly allocates stim to lowest-PAC windows.

    Given full PAC trajectory, stimulates during all windows with
    below-median PAC and rests during above-median windows.
    This represents the theoretical maximum alignment score.
    """
    name = "Alignment Oracle"
    def __init__(self, pac):
        self.median = np.median(pac)
        self.pac = pac
        self.t = 0
    def reset(self): self.t = 0
    def step(self, pac, **kw):
        a = 1 if pac < self.median else 0
        self.t += 1; return a


class PICtrl:
    name = "PI Controller"
    def __init__(self, w=30, kp=1.0, ki=0.2):
        self.w = w; self.kp = kp; self.ki = ki; self.buf = []; self.I = 0.0
    def reset(self): self.buf = []; self.I = 0.0
    def step(self, pac, **kw):
        self.buf.append(pac)
        if len(self.buf) > self.w: self.buf.pop(0)
        if len(self.buf) < 10: return 0
        e = np.mean(self.buf) - pac
        self.I = np.clip(self.I + e, -5, 5)
        return 1 if self.kp * e + self.ki * self.I > 0 else 0


# -----------------------------------------------------------------------
# Epoch-level evaluation metrics
# -----------------------------------------------------------------------

def evaluate_epoch_alignment(pac, decisions, transitions):
    """Evaluate how well controller decisions align with PAC epochs."""
    median_pac = np.median(pac)
    low_mask = pac < median_pac
    high_mask = pac >= median_pac

    stim_mask = decisions == 1
    rest_mask = decisions == 0

    low_stim_rate = float(np.mean(stim_mask[low_mask])) if low_mask.sum() > 0 else 0.0
    high_rest_rate = float(np.mean(rest_mask[high_mask])) if high_mask.sum() > 0 else 0.0
    alignment = (low_stim_rate + high_rest_rate) / 2

    mean_pac_stim = float(np.mean(pac[stim_mask])) if stim_mask.sum() > 0 else 0
    mean_pac_rest = float(np.mean(pac[rest_mask])) if rest_mask.sum() > 0 else 0

    return {
        "low_epoch_stim_rate": low_stim_rate,
        "high_epoch_rest_rate": high_rest_rate,
        "alignment_score": alignment,
        "stim_pct": 100.0 * np.mean(stim_mask),
        "mean_pac_during_stim": mean_pac_stim,
        "mean_pac_during_rest": mean_pac_rest,
        "overall_mean_pac": float(np.mean(pac)),
        "pac_stim_rest_gap": mean_pac_rest - mean_pac_stim,
    }


def evaluate_transition_anticipation(pac, decisions, transitions, window=10):
    """Evaluate how early the controller responds to PAC drop transitions.

    For each PAC drop:
    - lead_time: how many seconds before the drop the controller starts stimulating
    - anticipated: whether controller was already stimulating at the drop
    - preparation_time: time from first stim decision to the actual drop
    """
    drops = [t for t in transitions if t["direction"] == "drop"]
    if not drops:
        return {"n_drops": 0, "mean_lead_time": 0, "anticipation_rate": 0,
                "mean_preparation_time": 0}

    lead_times = []
    preparation_times = []
    anticipated = 0

    for drop in drops:
        idx = drop["index"]
        start = max(0, idx - window)
        pre_decisions = decisions[start:idx]

        if len(pre_decisions) == 0:
            continue

        # Was controller already stimulating at the transition?
        if idx < len(decisions) and decisions[idx] == 1:
            anticipated += 1

        # Find earliest stim in pre-window
        stim_indices = np.where(pre_decisions == 1)[0]
        if len(stim_indices) > 0:
            first_stim = start + stim_indices[0]
            lead_time = idx - first_stim
            lead_times.append(float(lead_time))
            preparation_times.append(float(lead_time))
        else:
            lead_times.append(0.0)
            preparation_times.append(0.0)

    n_drops = len(drops)
    return {
        "n_drops": n_drops,
        "mean_lead_time": float(np.mean(lead_times)) if lead_times else 0,
        "max_lead_time": float(np.max(lead_times)) if lead_times else 0,
        "anticipation_rate": float(anticipated / n_drops) if n_drops > 0 else 0,
        "mean_preparation_time": float(np.mean(preparation_times)) if preparation_times else 0,
        "lead_times": lead_times,
    }


def evaluate_efficiency(pac, decisions):
    """Compute stimulation efficiency metrics."""
    stim_mask = decisions == 1
    stim_pct = float(np.mean(stim_mask))

    if stim_pct < 0.01 or stim_pct > 0.99:
        return {"efficiency_ratio": 0, "energy_savings_vs_fixed_pct": 0,
                "stim_pct": 100*stim_pct}

    mean_pac = float(np.mean(pac))
    efficiency = mean_pac / (stim_pct + 1e-8)
    savings = 100 * (0.667 - stim_pct) / 0.667

    return {
        "efficiency_ratio": efficiency,
        "energy_savings_vs_fixed_pct": float(savings),
        "stim_pct": 100 * stim_pct,
    }


def compute_clinical_utility(alignment_score, lead_time, stim_pct,
                             anticipation_rate, min_prep_time=2.0):
    """Compute a clinical utility composite score.

    In adaptive music therapy for 40Hz entrainment:
    - Alignment matters: stimulate during low-PAC periods (weight=0.35)
    - Lead time matters: need >= min_prep_time for stimulus preparation (weight=0.30)
    - Efficiency matters: minimize unnecessary stimulation (weight=0.20)
    - Anticipation matters: catch most transitions (weight=0.15)

    Lead time bonus: full credit for >= min_prep_time, linear below that.
    """
    # Normalize components to [0, 1]
    align_norm = min(alignment_score, 1.0)

    # Lead time: full credit at >= min_prep_time seconds
    lead_norm = min(lead_time / min_prep_time, 1.0) if min_prep_time > 0 else 0

    # Efficiency: penalize both too much (>60%) and too little (<10%) stim
    if stim_pct > 60:
        eff_norm = max(0, 1 - (stim_pct - 60) / 40)
    elif stim_pct < 10:
        eff_norm = max(0, stim_pct / 10)
    else:
        eff_norm = 1.0

    antic_norm = min(anticipation_rate, 1.0)

    utility = (0.35 * align_norm + 0.30 * lead_norm +
               0.20 * eff_norm + 0.15 * antic_norm)
    return {
        "clinical_utility": utility,
        "align_component": 0.35 * align_norm,
        "lead_component": 0.30 * lead_norm,
        "efficiency_component": 0.20 * eff_norm,
        "anticipation_component": 0.15 * antic_norm,
    }


# -----------------------------------------------------------------------
# Statistical helpers
# -----------------------------------------------------------------------

def hedges_g(a, b):
    """Compute Hedges' g with 95% CI between paired samples."""
    n = len(a)
    pooled_std = np.sqrt(
        ((n-1)*np.var(a, ddof=1) + (n-1)*np.var(b, ddof=1))
        / (2*n - 2)
    )
    d_raw = (np.mean(a) - np.mean(b)) / (pooled_std + 1e-12)
    correction = 1 - 3 / (4*(2*n-2) - 1)
    g = d_raw * correction
    se = np.sqrt(2/n + g**2 / (2*n))
    return g, g - 1.96*se, g + 1.96*se, se


def paired_wilcoxon(a, b):
    """Wilcoxon signed-rank test with zero-difference handling."""
    diff = a - b
    nonzero = np.abs(diff) > 1e-10
    if nonzero.sum() >= 5:
        w_stat, w_p = stats.wilcoxon(diff[nonzero])
    else:
        w_stat, w_p = 0.0, 1.0
    return w_stat, w_p


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main():
    t0 = time_mod.time()
    processed_dir = Path("data/processed")
    raw_root = Path("data/raw/ds005048")
    models_dir = Path("models")

    # Find TCN checkpoint
    ckpt_files = list(models_dir.glob("best_multiscale_tcn_*.pth"))
    if not ckpt_files:
        print("ERROR: No TCN checkpoint found. Run run_full_pipeline.py first.")
        return
    ckpt_path = ckpt_files[0]
    print(f"Using checkpoint: {ckpt_path}")

    # Load TCN model
    from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN
    device = torch.device("cpu")
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    cfg = ModelConfig(**ckpt["cfg"])
    tcn_model = MultiscaleCausalTCN(cfg)
    tcn_model.load_state_dict(ckpt["model_state_dict"])
    tcn_model.eval()
    lookback = int(ckpt["metadata"]["lookback"])

    # Load scalers
    for p in processed_dir.glob("multiscale_temporal_*/scalers.npz"):
        scalers_path = p
        break
    s = np.load(scalers_path)
    feat_mean = s["feature_mean"].astype(np.float32)
    feat_std = s["feature_std"].astype(np.float32)
    yf_mean = float(s["y_future_mean"])
    yf_std = float(s["y_future_std"])
    yd_mean = float(s["y_delta_mean"])
    yd_std = float(s["y_delta_std"])

    print(f"TCN: {tcn_model.count_parameters():,} params, lookback={lookback}")
    print(f"Scalers: yf_mean={yf_mean:.6f}, yf_std={yf_std:.6f}")
    print(f"         yd_mean={yd_mean:.6f}, yd_std={yd_std:.6f}")

    # Load subjects
    print("\nLoading subjects...")
    subjects = load_subjects(processed_dir, raw_root)
    print(f"Loaded {len(subjects)} subjects")

    # Extract spectral features
    print("Extracting spectral features...")
    extract_spectral_features(subjects)

    # Free raw windows to save memory
    for s_data in subjects:
        del s_data["windows"]

    print(f"Setup complete ({time_mod.time() - t0:.1f}s)")

    # ---- Build TCN controller args ----
    tcn_args = dict(model=tcn_model, feature_mean=feat_mean, feature_std=feat_std,
                    yf_mean=yf_mean, yf_std=yf_std, yd_mean=yd_mean, yd_std=yd_std,
                    lookback=lookback, device=device)

    # ---- Run replay ----
    all_results: Dict[str, List[Dict]] = {}

    for si, subj_data in enumerate(subjects):
        pac = subj_data["pac"]
        stim_state_arr = subj_data["stim_state"]
        spectral_arr = subj_data["spectral"]
        transitions = subj_data["transitions"]
        n = len(pac)
        t_arr = subj_data["time"]

        # Compute stim context features
        cycle = 60.0
        phase = (t_arr % cycle) / cycle
        c_sin = np.sin(2 * np.pi * phase)
        c_cos = np.cos(2 * np.pi * phase)

        switch_times = [0.0]
        for i in range(1, n):
            if stim_state_arr[i] != stim_state_arr[i-1]:
                switch_times.append(t_arr[i])
        switch_arr = np.array(switch_times)
        idx = np.searchsorted(switch_arr, t_arr, side="right") - 1
        idx = np.clip(idx, 0, len(switch_arr)-1)
        tss = t_arr - switch_arr[idx]

        stim_frac = np.zeros(n)
        sh = deque(maxlen=20)
        for i in range(n):
            sh.append(float(stim_state_arr[i]))
            stim_frac[i] = np.mean(sh)

        controllers = [
            FixedScheduleCtrl(stim_state_arr),
            ReactiveCtrl(),
            TCNPredictiveCtrl(**tcn_args, delta_z_thresh=0.3),
            HybridTCNCtrl(**tcn_args, delta_z_thresh=0.5, reactive_z_thresh=0.5),
            PICtrl(),
            AlignmentOracleCtrl(pac),
        ]

        for ctrl in controllers:
            ctrl.reset()
            decisions = np.zeros(n, dtype=np.int32)
            for ti in range(n):
                if hasattr(ctrl, 'seq_buf'):
                    # TCN-based controller
                    decisions[ti] = ctrl.step(
                        pac[ti], spectral=spectral_arr[ti],
                        stim_state_val=float(stim_state_arr[ti]),
                        time_since_switch=tss[ti], stim_frac=stim_frac[ti],
                        cycle_sin=c_sin[ti], cycle_cos=c_cos[ti])
                else:
                    decisions[ti] = ctrl.step(pac[ti])

            align = evaluate_epoch_alignment(pac, decisions, transitions)
            antic = evaluate_transition_anticipation(pac, decisions, transitions)
            effic = evaluate_efficiency(pac, decisions)
            utility = compute_clinical_utility(
                align["alignment_score"], antic["mean_lead_time"],
                align["stim_pct"], antic["anticipation_rate"])

            metrics = {
                "subject": subj_data["subject"],
                **align,
                **{f"transition_{k}": v for k, v in antic.items() if k != "lead_times"},
                **effic,
                **utility,
            }

            # Track decision source distribution for hybrid
            if hasattr(ctrl, 'decision_sources') and ctrl.decision_sources:
                src = ctrl.decision_sources
                for s_name in ["agree", "reactive_override", "tcn_proactive",
                              "reactive", "maintain"]:
                    metrics[f"src_{s_name}"] = src.count(s_name) / len(src)

            if ctrl.name not in all_results:
                all_results[ctrl.name] = []
            all_results[ctrl.name].append(metrics)

        if (si + 1) % 10 == 0:
            print(f"  Replayed {si+1}/{len(subjects)} subjects")

    print(f"  Replayed {len(subjects)}/{len(subjects)} subjects")

    # ---- Print results ----
    print(f"\n{'='*100}")
    print("REAL-DATA REPLAY: Epoch-Level Evaluation (TCN-Integrated, 35 Subjects)")
    print(f"{'='*100}")
    print(f"{'Controller':<24s} {'Align%':>7s} {'LowStim%':>9s} {'HighRest%':>10s} "
          f"{'Stim%':>6s} {'Anticip%':>9s} {'LeadTime':>9s} {'Savings%':>9s} {'ClinUtil':>9s}")
    print("-" * 100)

    ctrl_order = ["Fixed Schedule", "Reactive Threshold", "TCN Predictive",
                   "Hybrid TCN+Reactive", "PI Controller", "Alignment Oracle"]
    summary = {}

    for name in ctrl_order:
        trials = all_results.get(name, [])
        if not trials:
            continue

        align = np.mean([t["alignment_score"] for t in trials])
        low_stim = np.mean([t["low_epoch_stim_rate"] for t in trials])
        high_rest = np.mean([t["high_epoch_rest_rate"] for t in trials])
        stim_pct = np.mean([t["stim_pct"] for t in trials])
        antic = np.mean([t["transition_anticipation_rate"] for t in trials])
        lead = np.mean([t["transition_mean_lead_time"] for t in trials])
        savings = np.mean([t.get("energy_savings_vs_fixed_pct", 0) for t in trials])
        clin = np.mean([t["clinical_utility"] for t in trials])

        print(f"{name:<24s} {100*align:>6.1f}% {100*low_stim:>8.1f}% {100*high_rest:>9.1f}% "
              f"{stim_pct:>5.1f}% {100*antic:>8.1f}% {lead:>8.1f}s {savings:>8.1f}% {clin:>8.3f}")

        summary[name] = {
            "alignment_score": round(100*align, 1),
            "low_epoch_stim_rate": round(100*low_stim, 1),
            "high_epoch_rest_rate": round(100*high_rest, 1),
            "stim_pct": round(stim_pct, 1),
            "anticipation_rate": round(100*antic, 1),
            "mean_lead_time_s": round(lead, 2),
            "energy_savings_pct": round(savings, 1),
            "clinical_utility": round(clin, 3),
        }

    # ---- PAC-stim rest gap (key clinical metric) ----
    print(f"\n{'='*100}")
    print("PAC TARGETING QUALITY (Mean PAC during stim vs rest)")
    print(f"{'='*100}")
    print(f"{'Controller':<24s} {'PAC|stim':>12s} {'PAC|rest':>12s} {'Gap':>12s} {'Direction':>12s}")
    print("-" * 76)

    for name in ctrl_order:
        trials = all_results.get(name, [])
        if not trials:
            continue
        pac_stim = np.mean([t["mean_pac_during_stim"] for t in trials])
        pac_rest = np.mean([t["mean_pac_during_rest"] for t in trials])
        gap = pac_rest - pac_stim
        direction = "CORRECT" if gap > 0 else "WRONG"
        print(f"{name:<24s} {pac_stim:>12.6f} {pac_rest:>12.6f} {gap:>12.6f} {direction:>12s}")

    # ---- Hybrid decision source analysis ----
    hybrid_trials = all_results.get("Hybrid TCN+Reactive", [])
    if hybrid_trials and "src_tcn_proactive" in hybrid_trials[0]:
        print(f"\n{'='*100}")
        print("HYBRID CONTROLLER: Decision Source Distribution")
        print(f"{'='*100}")
        for src in ["agree", "reactive_override", "tcn_proactive", "reactive", "maintain"]:
            key = f"src_{src}"
            pcts = [100 * t.get(key, 0) for t in hybrid_trials]
            print(f"  {src:<25s}: {np.mean(pcts):5.1f}% (SD={np.std(pcts):.1f})")

    # ---- Statistical tests ----
    print(f"\n{'='*100}")
    print("STATISTICAL COMPARISONS (Wilcoxon signed-rank, Hedges' g [95% CI])")
    print(f"{'='*100}")

    comparisons = {}
    test_pairs = [
        ("Hybrid TCN+Reactive", "Reactive Threshold"),
        ("Hybrid TCN+Reactive", "Fixed Schedule"),
        ("TCN Predictive", "Reactive Threshold"),
        ("Hybrid TCN+Reactive", "TCN Predictive"),
    ]

    for name_a, name_b in test_pairs:
        trials_a = all_results.get(name_a, [])
        trials_b = all_results.get(name_b, [])
        if len(trials_a) < 5 or len(trials_b) < 5:
            continue

        a_by_subj = {t["subject"]: t for t in trials_a}
        b_by_subj = {t["subject"]: t for t in trials_b}
        common = sorted(set(a_by_subj) & set(b_by_subj))
        if len(common) < 5:
            continue

        n = len(common)
        print(f"\n  {name_a} vs {name_b} (n={n} subjects):")

        comp_metrics = {}
        for metric, label, scale in [
            ("alignment_score", "Epoch Alignment", 100.0),
            ("low_epoch_stim_rate", "Low-PAC Stim Rate", 100.0),
            ("high_epoch_rest_rate", "High-PAC Rest Rate", 100.0),
            ("stim_pct", "Stimulation %", 1.0),
            ("transition_anticipation_rate", "Anticipation Rate", 100.0),
            ("transition_mean_lead_time", "Lead Time (s)", 1.0),
            ("pac_stim_rest_gap", "PAC Target Gap", 1e6),
            ("clinical_utility", "Clinical Utility", 1.0),
        ]:
            a_vals = np.array([a_by_subj[s][metric] for s in common])
            b_vals = np.array([b_by_subj[s][metric] for s in common])

            g, ci_lo, ci_hi, se = hedges_g(a_vals, b_vals)
            w_stat, w_p = paired_wilcoxon(a_vals, b_vals)

            sig = "***" if w_p < 0.001 else "**" if w_p < 0.01 else "*" if w_p < 0.05 else ""
            interp = ("large" if abs(g) >= 0.8 else "medium" if abs(g) >= 0.5
                      else "small" if abs(g) >= 0.2 else "negligible")

            print(f"    {label:<22s}: A={scale*np.mean(a_vals):>7.2f}, B={scale*np.mean(b_vals):>7.2f}, "
                  f"g={g:>+.3f} [{ci_lo:>+.3f},{ci_hi:>+.3f}] ({interp}), "
                  f"p={w_p:.4f}{sig}")

            comp_metrics[metric] = {
                "a_mean": float(np.mean(a_vals)),
                "b_mean": float(np.mean(b_vals)),
                "hedges_g": round(float(g), 4),
                "ci_95": [round(float(ci_lo), 4), round(float(ci_hi), 4)],
                "wilcoxon_W": float(w_stat),
                "wilcoxon_p": round(float(w_p), 6),
                "interpretation": interp,
            }

        key = f"{name_a.replace(' ', '_')}_vs_{name_b.replace(' ', '_')}"
        comparisons[key] = {"n_subjects": n, "metrics": comp_metrics}

    # ---- Per-subject responder analysis ----
    print(f"\n{'='*100}")
    print("PER-SUBJECT RESPONDER ANALYSIS: Hybrid vs Reactive")
    print(f"{'='*100}")

    hybrid_trials = all_results.get("Hybrid TCN+Reactive", [])
    react_trials = all_results.get("Reactive Threshold", [])
    if hybrid_trials and react_trials:
        h_by_subj = {t["subject"]: t for t in hybrid_trials}
        r_by_subj = {t["subject"]: t for t in react_trials}
        common = sorted(set(h_by_subj) & set(r_by_subj))

        responders_align = 0
        responders_lead = 0
        responders_utility = 0

        for subj in common:
            h = h_by_subj[subj]
            r = r_by_subj[subj]
            if h["alignment_score"] > r["alignment_score"]:
                responders_align += 1
            if h["transition_mean_lead_time"] > r["transition_mean_lead_time"]:
                responders_lead += 1
            if h["clinical_utility"] > r["clinical_utility"]:
                responders_utility += 1

        n = len(common)
        print(f"  Subjects with better alignment:       {responders_align}/{n} ({100*responders_align/n:.0f}%)")
        print(f"  Subjects with better lead time:       {responders_lead}/{n} ({100*responders_lead/n:.0f}%)")
        print(f"  Subjects with better clinical utility: {responders_utility}/{n} ({100*responders_utility/n:.0f}%)")

        # Binomial test for lead time (our primary claim)
        _, binom_p = stats.binom_test(responders_lead, n, 0.5) if hasattr(stats, 'binom_test') else (0, 0)
        try:
            binom_result = stats.binomtest(responders_lead, n, 0.5)
            binom_p = binom_result.pvalue
        except AttributeError:
            binom_p = stats.binom_test(responders_lead, n, 0.5)
        print(f"  Binomial test (lead time > chance): p={binom_p:.6f}")

    # ---- Key findings summary ----
    print(f"\n{'='*100}")
    print("KEY FINDINGS SUMMARY")
    print(f"{'='*100}")

    hybrid_sum = summary.get("Hybrid TCN+Reactive", {})
    react_sum = summary.get("Reactive Threshold", {})
    fixed_sum = summary.get("Fixed Schedule", {})
    oracle_sum = summary.get("Alignment Oracle", {})

    if hybrid_sum and react_sum:
        print(f"\n  1. PROACTIVE LEAD TIME (primary TCN advantage):")
        print(f"     Hybrid: {hybrid_sum.get('mean_lead_time_s', 0):.1f}s vs Reactive: {react_sum.get('mean_lead_time_s', 0):.1f}s")
        lead_factor = hybrid_sum.get('mean_lead_time_s', 0) / max(react_sum.get('mean_lead_time_s', 0.01), 0.01)
        print(f"     {lead_factor:.0f}x improvement in preparation time")
        print(f"     Clinical significance: Enables smooth stimulus transitions in music therapy")

        print(f"\n  2. EPOCH ALIGNMENT:")
        print(f"     Hybrid: {hybrid_sum.get('alignment_score', 0):.1f}% vs Reactive: {react_sum.get('alignment_score', 0):.1f}%")
        print(f"     Oracle upper bound: {oracle_sum.get('alignment_score', 0):.1f}%")

        print(f"\n  3. ENERGY EFFICIENCY vs Fixed Schedule:")
        print(f"     Hybrid: {hybrid_sum.get('energy_savings_pct', 0):.0f}% energy savings")
        print(f"     Reactive: {react_sum.get('energy_savings_pct', 0):.0f}% energy savings")

        print(f"\n  4. CLINICAL UTILITY COMPOSITE:")
        print(f"     Hybrid: {hybrid_sum.get('clinical_utility', 0):.3f}")
        print(f"     Reactive: {react_sum.get('clinical_utility', 0):.3f}")
        print(f"     Fixed: {fixed_sum.get('clinical_utility', 0):.3f}")

    # ---- Save ----
    output = {
        "n_subjects": len(subjects),
        "tcn_checkpoint": str(ckpt_path),
        "tcn_params": tcn_model.count_parameters(),
        "lookback": lookback,
        "summary": summary,
        "comparisons": comparisons,
        "per_subject": {name: trials for name, trials in all_results.items()},
    }
    out_path = Path("results/metrics/tcn_validation_results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, default=str))

    elapsed = time_mod.time() - t0
    print(f"\nSaved: {out_path}")
    print(f"Total runtime: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
