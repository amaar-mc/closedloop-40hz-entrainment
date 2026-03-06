"""
Replay real PAC data through controllers — no simulator, no fake dynamics.

For each subject, we have the actual PAC time series under the fixed schedule
(40s stim + 20s rest). We replay these through each controller and evaluate:

1. DECISION ALIGNMENT: When the controller says STIMULATE, does PAC actually
   rise in the next few steps? When it says REST, was PAC already high?

2. WASTED STIMULATION: In the fixed schedule, how many stim timesteps had
   PAC flat or declining? (= wasted energy, the brain wasn't responding)

3. STIMULATION SAVINGS: The predictive controller would have skipped some
   stim periods. Were those indeed low-value periods?

4. RESPONSE QUALITY: Average PAC change after stim vs rest decisions,
   compared across controllers.

This uses ONLY real data — no synthetic brain model.

Controllers (8 total):
  - Fixed Schedule (actual): Replays BIDS fixed schedule
  - Reactive Threshold: z-score on rolling PAC window
  - Predictive Look-Ahead: trend-based + z-score with hysteresis
  - Oracle (future-aware): Knows future PAC (upper bound)
  - CUSUM Change Detection: Detects sustained PAC drops (Page 1954)
  - Multi-Biomarker Reactive: PAC + gamma + theta weighted z-scores
  - Phase-Aware Reactive: Threshold modulated by phase coherence
  - PI Controller: Proportional-integral control on PAC error

Usage:
    python run_replay_analysis.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import time as time_mod
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy import signal as sig
from scipy import stats

ROOT = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Controllers — original 4
# ---------------------------------------------------------------------------

class FixedScheduleControl:
    """Replays the actual fixed schedule from BIDS events."""
    name = "Fixed Schedule (actual)"

    def __init__(self, stim_state: np.ndarray):
        self.stim_state = stim_state
        self.t = 0

    def reset(self):
        self.t = 0

    def step(self, pac: float) -> int:
        action = int(self.stim_state[self.t]) if self.t < len(self.stim_state) else 0
        self.t += 1
        return action


class ReactiveThresholdControl:
    name = "Reactive Threshold"

    def __init__(self, window: int = 30, z_thresh: float = 0.5):
        self.window = window
        self.z_thresh = z_thresh
        self.buf: list = []

    def reset(self):
        self.buf = []

    def step(self, pac: float) -> int:
        self.buf.append(pac)
        if len(self.buf) > self.window:
            self.buf.pop(0)
        if len(self.buf) < 10:
            return 0
        mu = np.mean(self.buf)
        sigma = np.std(self.buf) + 1e-12
        z = (pac - mu) / sigma
        return 1 if z < -self.z_thresh else 0


class PredictiveLookAheadControl:
    name = "Predictive Look-Ahead"

    def __init__(self, window: int = 30, z_thresh: float = 0.5,
                 trend_k: int = 5, hold_time: int = 5):
        self.window = window
        self.z_thresh = z_thresh
        self.trend_k = trend_k
        self.hold_time = hold_time
        self.buf: list = []
        self.state = 0
        self.t_in_state = 0

    def reset(self):
        self.buf = []
        self.state = 0
        self.t_in_state = 0

    def _trend(self) -> float:
        if len(self.buf) < self.trend_k:
            return 0.0
        recent = self.buf[-self.trend_k:]
        x = np.arange(self.trend_k, dtype=np.float64)
        y = np.array(recent, dtype=np.float64)
        xm, ym = x.mean(), y.mean()
        denom = np.sum((x - xm) ** 2)
        if denom < 1e-12:
            return 0.0
        return float(np.sum((x - xm) * (y - ym)) / denom)

    def step(self, pac: float) -> int:
        self.buf.append(pac)
        if len(self.buf) > self.window:
            self.buf.pop(0)
        if len(self.buf) < 10:
            return 0
        mu = np.mean(self.buf)
        sigma = np.std(self.buf) + 1e-12
        z = (pac - mu) / sigma
        trend = self._trend()

        desired = None
        if trend < -0.3 * sigma:
            desired = 1  # declining -> stimulate
        elif trend > 0.3 * sigma:
            desired = 0  # rising -> rest
        elif z < -self.z_thresh:
            desired = 1
        elif z > self.z_thresh:
            desired = 0
        if desired is None:
            desired = self.state
        if desired != self.state:
            if self.t_in_state >= self.hold_time:
                self.state = desired
                self.t_in_state = 0
        else:
            self.t_in_state += 1
        return self.state


class OracleControl:
    """Knows future PAC — stimulates only when PAC is about to drop."""
    name = "Oracle (future-aware)"

    def __init__(self, pac_series: np.ndarray, lookahead: int = 5):
        self.pac_series = pac_series
        self.lookahead = lookahead
        self.t = 0

    def reset(self):
        self.t = 0

    def step(self, pac: float) -> int:
        # Look ahead: if PAC will drop, stimulate now
        future_idx = min(self.t + self.lookahead, len(self.pac_series) - 1)
        future_pac = self.pac_series[future_idx]
        self.t += 1
        return 1 if future_pac < pac else 0


# ---------------------------------------------------------------------------
# Controllers — 4 new advanced controllers
# ---------------------------------------------------------------------------

class CUSUMControl:
    """CUSUM change-detection controller (Page 1954).

    Detects *sustained* PAC drops rather than instantaneous threshold crossings.
    S(t) = max(0, S(t-1) + (mu - PAC(t) - k)); alarm when S(t) > h.
    On alarm: stimulate for `stim_dur` steps, reset CUSUM, cooldown.
    """
    name = "CUSUM Change Detection"

    def __init__(self, window: int = 30, warmup: int = 10,
                 slack_factor: float = 0.25, threshold_factor: float = 2.0,
                 stim_dur: int = 8, cooldown: int = 5):
        self.window = window
        self.warmup = warmup
        self.slack_factor = slack_factor
        self.threshold_factor = threshold_factor
        self.stim_dur = stim_dur
        self.cooldown = cooldown
        self.buf: list = []
        self.S = 0.0
        self.stim_remaining = 0
        self.cool_remaining = 0

    def reset(self):
        self.buf = []
        self.S = 0.0
        self.stim_remaining = 0
        self.cool_remaining = 0

    def step(self, pac: float) -> int:
        self.buf.append(pac)
        if len(self.buf) > self.window:
            self.buf.pop(0)

        # During active stimulation burst
        if self.stim_remaining > 0:
            self.stim_remaining -= 1
            return 1

        # During cooldown after stimulation
        if self.cool_remaining > 0:
            self.cool_remaining -= 1
            return 0

        # Need warmup samples for statistics
        if len(self.buf) < self.warmup:
            return 0

        mu = np.mean(self.buf)
        sigma = np.std(self.buf) + 1e-12
        k = self.slack_factor * sigma
        h = self.threshold_factor * sigma

        # CUSUM update: accumulate evidence of downward shift
        self.S = max(0.0, self.S + (mu - pac - k))

        if self.S > h:
            # Alarm: sustained drop detected
            self.S = 0.0
            self.stim_remaining = self.stim_dur - 1  # -1 because this step counts
            self.cool_remaining = self.cooldown
            return 1

        return 0


class MultiBiomarkerReactiveControl:
    """Multi-biomarker reactive controller.

    Uses PAC + gamma power + theta power, each with its own rolling z-score.
    Weighted combination: z_combined = 0.5*z_pac + 0.3*z_gamma + 0.2*z_theta.
    Stimulate when z_combined < -0.5.
    """
    name = "Multi-Biomarker Reactive"
    needs_biomarkers = True

    def __init__(self, window: int = 30, warmup: int = 10, z_thresh: float = 0.5):
        self.window = window
        self.warmup = warmup
        self.z_thresh = z_thresh
        self.pac_buf: list = []
        self.gamma_buf: list = []
        self.theta_buf: list = []

    def reset(self):
        self.pac_buf = []
        self.gamma_buf = []
        self.theta_buf = []

    def step(self, pac: float, gamma_power: float = 0.0,
             theta_power: float = 0.0) -> int:
        self.pac_buf.append(pac)
        self.gamma_buf.append(gamma_power)
        self.theta_buf.append(theta_power)
        for buf in (self.pac_buf, self.gamma_buf, self.theta_buf):
            if len(buf) > self.window:
                buf.pop(0)

        if len(self.pac_buf) < self.warmup:
            return 0

        def _z(buf, val):
            mu = np.mean(buf)
            sigma = np.std(buf) + 1e-12
            return (val - mu) / sigma

        z_pac = _z(self.pac_buf, pac)
        z_gamma = _z(self.gamma_buf, gamma_power)
        z_theta = _z(self.theta_buf, theta_power)

        z_combined = 0.5 * z_pac + 0.3 * z_gamma + 0.2 * z_theta
        return 1 if z_combined < -self.z_thresh else 0


class PhaseAwareReactiveControl:
    """Phase-aware reactive controller.

    Reactive z-score with threshold modulated by theta-gamma phase coherence.
    Low coherence (brain disorganized) -> lower threshold -> easier to trigger.
    High coherence (brain organized) -> higher threshold -> less aggressive.
    adaptive_thresh = 0.5 + 0.3 * z_coherence, clamped to [0.1, 1.0].
    """
    name = "Phase-Aware Reactive"
    needs_phase_coherence = True

    def __init__(self, window: int = 30, warmup: int = 10,
                 base_thresh: float = 0.5, coh_weight: float = 0.3):
        self.window = window
        self.warmup = warmup
        self.base_thresh = base_thresh
        self.coh_weight = coh_weight
        self.pac_buf: list = []
        self.coh_buf: list = []

    def reset(self):
        self.pac_buf = []
        self.coh_buf = []

    def step(self, pac: float, phase_coherence: float = 0.0) -> int:
        self.pac_buf.append(pac)
        self.coh_buf.append(phase_coherence)
        for buf in (self.pac_buf, self.coh_buf):
            if len(buf) > self.window:
                buf.pop(0)

        if len(self.pac_buf) < self.warmup:
            return 0

        mu_pac = np.mean(self.pac_buf)
        sigma_pac = np.std(self.pac_buf) + 1e-12
        z_pac = (pac - mu_pac) / sigma_pac

        mu_coh = np.mean(self.coh_buf)
        sigma_coh = np.std(self.coh_buf) + 1e-12
        z_coh = (phase_coherence - mu_coh) / sigma_coh

        adaptive_thresh = np.clip(
            self.base_thresh + self.coh_weight * z_coh, 0.1, 1.0
        )
        return 1 if z_pac < -adaptive_thresh else 0


class PIControl:
    """Proportional-Integral (PI) controller for PAC maintenance.

    Error: e(t) = rolling_mean_PAC - current_PAC
    Integral: I(t) = clamp(I(t-1) + e(t), -5, +5) (anti-windup)
    Control signal: u(t) = Kp * e(t) + Ki * I(t)
    Stimulate when u(t) > 0.
    """
    name = "PI Controller"

    def __init__(self, window: int = 30, warmup: int = 10,
                 kp: float = 1.0, ki: float = 0.2,
                 integral_clamp: float = 5.0):
        self.window = window
        self.warmup = warmup
        self.kp = kp
        self.ki = ki
        self.integral_clamp = integral_clamp
        self.buf: list = []
        self.integral = 0.0

    def reset(self):
        self.buf = []
        self.integral = 0.0

    def step(self, pac: float) -> int:
        self.buf.append(pac)
        if len(self.buf) > self.window:
            self.buf.pop(0)

        if len(self.buf) < self.warmup:
            return 0

        mu = np.mean(self.buf)
        error = mu - pac  # positive when PAC is below average

        # Integral with anti-windup clamp
        self.integral = np.clip(
            self.integral + error, -self.integral_clamp, self.integral_clamp
        )

        u = self.kp * error + self.ki * self.integral
        return 1 if u > 0 else 0


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_subjects() -> List[Dict]:
    """Load all subjects with PAC time series, raw EEG windows, + stim/rest labels."""
    processed_dir = Path("data/processed")
    raw_root = Path("data/raw/ds005048")

    all_subjects = []

    for split in ["train", "val", "test"]:
        d = np.load(processed_dir / f"{split}_data.npz", allow_pickle=True)
        pac = d["pac"].astype(np.float64)
        subjects = d["subjects"]
        windows = d["windows"]  # (N, 1, 7, 500)

        for subj in np.unique(subjects):
            mask = subjects == subj
            subj_pac = pac[mask]
            subj_windows = windows[mask]  # (n, 1, 7, 500)

            # Load events
            tsv = raw_root / subj / "eeg" / f"{subj}_task-40HzAuditoryEntrainment_events.tsv"
            if not tsv.exists():
                continue
            events = pd.read_csv(tsv, sep="\t").sort_values("onset").reset_index(drop=True)

            n = len(subj_pac)
            # Window centers: each 2s window at hop=1s, center at t=1,2,3...
            t = np.arange(n, dtype=np.float64) * 1.0 + 1.0

            # Build stim_state array: 1=stimulating, 0=rest
            stim_state = np.zeros(n, dtype=np.int32)
            for _, row in events.iterrows():
                onset = float(row["onset"])
                duration = float(row["duration"])
                is_stim = int(row["value"]) == 2
                if is_stim:
                    in_event = (t >= onset) & (t < onset + duration)
                    stim_state[in_event] = 1

            all_subjects.append({
                "subject": subj,
                "pac": subj_pac,
                "windows": subj_windows,
                "stim_state": stim_state,
                "time": t,
                "n_windows": n,
                "split": split,
            })

    return all_subjects


# ---------------------------------------------------------------------------
# Biomarker feature extraction with caching
# ---------------------------------------------------------------------------

def _extract_biomarkers_single(eeg: np.ndarray, fs: float = 250.0) -> dict:
    """Extract theta power, gamma power, and phase coherence from one window.

    Args:
        eeg: (n_channels, n_samples) raw EEG in uV
        fs: sampling rate

    Returns:
        dict with theta_power, gamma_power, phase_coherence (scalars, averaged
        across channels)
    """
    n_ch, n_samp = eeg.shape
    nperseg = min(256, n_samp)

    # --- Band powers via Welch PSD ---
    freqs, psd = sig.welch(eeg, fs=fs, nperseg=nperseg, axis=1)
    theta_idx = (freqs >= 4) & (freqs <= 8)
    gamma_idx = (freqs >= 38) & (freqs <= 42)
    theta_power = float(np.mean(np.trapz(psd[:, theta_idx], freqs[theta_idx], axis=1)))
    gamma_power = float(np.mean(np.trapz(psd[:, gamma_idx], freqs[gamma_idx], axis=1)))

    # --- Phase coherence: mean resultant length of gamma-amplitude-weighted
    #     theta phase vectors, per channel then averaged ---
    nyq = fs / 2.0
    b_theta, a_theta = sig.butter(3, [4.0 / nyq, 8.0 / nyq], btype='band')
    b_gamma, a_gamma = sig.butter(3, [38.0 / nyq, 42.0 / nyq], btype='band')

    coherences = np.zeros(n_ch)
    for ch in range(n_ch):
        theta_filt = sig.filtfilt(b_theta, a_theta, eeg[ch])
        gamma_filt = sig.filtfilt(b_gamma, a_gamma, eeg[ch])
        theta_phase = np.angle(sig.hilbert(theta_filt))
        gamma_amp = np.abs(sig.hilbert(gamma_filt))
        # Weighted mean resultant length
        weighted = gamma_amp * np.exp(1j * theta_phase)
        coherences[ch] = np.abs(np.mean(weighted)) / (np.mean(gamma_amp) + 1e-12)

    phase_coherence = float(np.mean(coherences))

    return {
        "theta_power": theta_power,
        "gamma_power": gamma_power,
        "phase_coherence": phase_coherence,
    }


def precompute_biomarker_features(subjects: List[Dict]) -> Dict[str, Dict[str, np.ndarray]]:
    """Compute biomarker features for all subjects, with disk caching.

    Returns:
        dict mapping subject_id -> {
            "theta_power": (n_windows,),
            "gamma_power": (n_windows,),
            "phase_coherence": (n_windows,),
        }
    """
    cache_dir = Path("data/processed/biomarker_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)

    features = {}
    n_cached = 0
    n_computed = 0

    for subj_data in subjects:
        subj_id = subj_data["subject"]
        n = subj_data["n_windows"]

        # Cache key: subject id + number of windows
        cache_key = f"{subj_id}_n{n}"
        cache_file = cache_dir / f"{cache_key}.npz"

        if cache_file.exists():
            cached = np.load(cache_file)
            features[subj_id] = {
                "theta_power": cached["theta_power"],
                "gamma_power": cached["gamma_power"],
                "phase_coherence": cached["phase_coherence"],
            }
            n_cached += 1
            continue

        # Compute features from raw EEG windows
        windows = subj_data["windows"]  # (n, 1, 7, 500)
        theta_arr = np.zeros(n)
        gamma_arr = np.zeros(n)
        coherence_arr = np.zeros(n)

        for i in range(n):
            eeg = windows[i, 0]  # (7, 500) — drop the singleton dim
            bio = _extract_biomarkers_single(eeg, fs=250.0)
            theta_arr[i] = bio["theta_power"]
            gamma_arr[i] = bio["gamma_power"]
            coherence_arr[i] = bio["phase_coherence"]

        features[subj_id] = {
            "theta_power": theta_arr,
            "gamma_power": gamma_arr,
            "phase_coherence": coherence_arr,
        }

        # Save to cache
        np.savez_compressed(
            cache_file,
            theta_power=theta_arr,
            gamma_power=gamma_arr,
            phase_coherence=coherence_arr,
        )
        n_computed += 1

    print(f"  Biomarkers: {n_cached} cached, {n_computed} computed")
    return features


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def evaluate_decisions(pac: np.ndarray, decisions: np.ndarray,
                       lookahead: int = 3) -> Dict:
    """
    Evaluate how good a controller's decisions were given what actually happened.

    For each timestep t where the controller said STIMULATE:
      - Was PAC(t+1..t+k) > PAC(t)? (good call)
      - Was PAC(t+1..t+k) <= PAC(t)? (wasted stimulation)

    For each timestep t where the controller said REST:
      - Was PAC(t) above the session median? (good call — no need to stimulate)
      - Was PAC(t) below median? (missed opportunity)
    """
    n = len(pac)
    stim_mask = decisions == 1
    rest_mask = decisions == 0

    stim_pct = 100.0 * np.mean(stim_mask)

    # PAC change after each decision
    pac_delta = np.zeros(n)
    for i in range(n):
        end = min(i + lookahead, n - 1)
        pac_delta[i] = pac[end] - pac[i]

    # Stim decisions: how often did PAC actually rise?
    if stim_mask.sum() > 0:
        stim_deltas = pac_delta[stim_mask]
        stim_hit_rate = float(np.mean(stim_deltas > 0))
        stim_mean_delta = float(np.mean(stim_deltas))
    else:
        stim_hit_rate = 0.0
        stim_mean_delta = 0.0

    # Rest decisions: was PAC already above median?
    median_pac = np.median(pac)
    if rest_mask.sum() > 0:
        rest_above_median = float(np.mean(pac[rest_mask] > median_pac))
        rest_mean_pac = float(np.mean(pac[rest_mask]))
    else:
        rest_above_median = 0.0
        rest_mean_pac = 0.0

    # Wasted stimulation: controller said STIM but PAC didn't rise
    if stim_mask.sum() > 0:
        wasted = float(np.mean(pac_delta[stim_mask] <= 0))
    else:
        wasted = 0.0

    # Overall PAC during stim decisions vs rest decisions
    mean_pac_during_stim = float(np.mean(pac[stim_mask])) if stim_mask.sum() > 0 else 0.0
    mean_pac_during_rest = float(np.mean(pac[rest_mask])) if rest_mask.sum() > 0 else 0.0

    return {
        "stim_pct": stim_pct,
        "stim_hit_rate": stim_hit_rate,
        "stim_mean_delta": stim_mean_delta,
        "wasted_stim_pct": 100.0 * wasted,
        "rest_above_median_pct": 100.0 * rest_above_median,
        "mean_pac_during_stim": mean_pac_during_stim,
        "mean_pac_during_rest": mean_pac_during_rest,
        "overall_mean_pac": float(np.mean(pac)),
    }


def replay_subject(subj_data: Dict, biomarkers: Dict[str, np.ndarray] | None) -> Dict:
    """Replay all controllers on one subject's real PAC data."""
    pac = subj_data["pac"]
    stim_state = subj_data["stim_state"]
    n = len(pac)

    # Original 4 controllers
    controllers = [
        FixedScheduleControl(stim_state),
        ReactiveThresholdControl(),
        PredictiveLookAheadControl(),
        OracleControl(pac, lookahead=5),
        # New 4 controllers
        CUSUMControl(),
        MultiBiomarkerReactiveControl(),
        PhaseAwareReactiveControl(),
        PIControl(),
    ]

    # Biomarker arrays (None if not precomputed)
    theta_power = biomarkers["theta_power"] if biomarkers else None
    gamma_power = biomarkers["gamma_power"] if biomarkers else None
    phase_coherence = biomarkers["phase_coherence"] if biomarkers else None

    results = {}
    for ctrl in controllers:
        ctrl.reset()
        decisions = np.zeros(n, dtype=np.int32)
        for t in range(n):
            if isinstance(ctrl, MultiBiomarkerReactiveControl) and biomarkers:
                decisions[t] = ctrl.step(
                    pac[t],
                    gamma_power=gamma_power[t],
                    theta_power=theta_power[t],
                )
            elif isinstance(ctrl, PhaseAwareReactiveControl) and biomarkers:
                decisions[t] = ctrl.step(
                    pac[t],
                    phase_coherence=phase_coherence[t],
                )
            else:
                decisions[t] = ctrl.step(pac[t])
        metrics = evaluate_decisions(pac, decisions, lookahead=3)
        results[ctrl.name] = metrics

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time_mod.time()
    print("Loading real subject data...")
    subjects = load_subjects()
    print(f"Loaded {len(subjects)} subjects")

    print("Extracting biomarker features...")
    all_biomarkers = precompute_biomarker_features(subjects)

    # Free raw EEG windows from memory — only needed for feature extraction
    for subj_data in subjects:
        subj_data.pop("windows", None)

    print(f"Setup complete in {time_mod.time() - t0:.1f}s\n")

    all_results: Dict[str, List[Dict]] = {}

    for subj_data in subjects:
        bio = all_biomarkers.get(subj_data["subject"])
        subj_results = replay_subject(subj_data, bio)
        for ctrl_name, metrics in subj_results.items():
            if ctrl_name not in all_results:
                all_results[ctrl_name] = []
            all_results[ctrl_name].append({
                "subject": subj_data["subject"],
                **metrics,
            })

    # ------------------------------------------------------------------
    # Print per-controller summary table
    # ------------------------------------------------------------------
    print("=" * 90)
    print("REPLAY ANALYSIS: Real PAC Data Through Each Controller")
    print("=" * 90)
    print(
        f"{'Controller':<28s} "
        f"{'Stim%':>6s} "
        f"{'Hit Rate':>9s} "
        f"{'Wasted%':>8s} "
        f"{'Stim dPAC':>10s} "
        f"{'Rest>Med%':>9s} "
    )
    print("-" * 75)

    summary = {}
    ctrl_order = [
        "Fixed Schedule (actual)",
        "Reactive Threshold",
        "Predictive Look-Ahead",
        "Oracle (future-aware)",
        "CUSUM Change Detection",
        "Multi-Biomarker Reactive",
        "Phase-Aware Reactive",
        "PI Controller",
    ]

    for name in ctrl_order:
        trials = all_results.get(name)
        if not trials:
            continue
        stim_pct = np.mean([t["stim_pct"] for t in trials])
        hit_rate = np.mean([t["stim_hit_rate"] for t in trials])
        wasted = np.mean([t["wasted_stim_pct"] for t in trials])
        stim_delta = np.mean([t["stim_mean_delta"] for t in trials])
        rest_above = np.mean([t["rest_above_median_pct"] for t in trials])

        print(
            f"{name:<28s} "
            f"{stim_pct:>5.1f}% "
            f"{100*hit_rate:>8.1f}% "
            f"{wasted:>7.1f}% "
            f"{stim_delta:>+10.6f} "
            f"{rest_above:>8.1f}% "
        )

        summary[name] = {
            "stim_pct": round(stim_pct, 1),
            "stim_hit_rate_pct": round(100 * hit_rate, 1),
            "wasted_stim_pct": round(wasted, 1),
            "stim_mean_delta_pac": float(stim_delta),
            "rest_above_median_pct": round(rest_above, 1),
        }

    # ------------------------------------------------------------------
    # Key findings: Fixed vs best reactive
    # ------------------------------------------------------------------
    fixed = summary.get("Fixed Schedule (actual)", {})
    reactive = summary.get("Reactive Threshold", {})

    print(f"\n{'='*90}")
    print("KEY FINDINGS")
    print(f"{'='*90}")

    if fixed and reactive:
        print(f"\nFixed Schedule:")
        print(f"  - Stimulates {fixed['stim_pct']:.1f}% of the time")
        print(f"  - {fixed['wasted_stim_pct']:.1f}% of stimulation is wasted (PAC doesn't rise)")
        print(f"  - Stim hit rate: {fixed['stim_hit_rate_pct']:.1f}%")

        print(f"\nReactive Threshold (baseline best):")
        print(f"  - Stimulates {reactive['stim_pct']:.1f}% of the time")
        print(f"  - {reactive['wasted_stim_pct']:.1f}% of stimulation is wasted")
        print(f"  - Stim hit rate: {reactive['stim_hit_rate_pct']:.1f}%")

    # Compare new controllers vs reactive threshold
    new_controllers = [
        "CUSUM Change Detection",
        "Multi-Biomarker Reactive",
        "Phase-Aware Reactive",
        "PI Controller",
    ]
    print(f"\nNew controllers vs Reactive Threshold ({reactive.get('stim_hit_rate_pct', '?')}% hit rate):")
    for name in new_controllers:
        s = summary.get(name, {})
        if not s:
            continue
        delta_hit = s["stim_hit_rate_pct"] - reactive.get("stim_hit_rate_pct", 0)
        delta_waste = s["wasted_stim_pct"] - reactive.get("wasted_stim_pct", 0)
        print(f"  {name}:")
        print(f"    Hit rate: {s['stim_hit_rate_pct']:.1f}% ({delta_hit:+.1f}pp)")
        print(f"    Wasted:   {s['wasted_stim_pct']:.1f}% ({delta_waste:+.1f}pp)")
        print(f"    Stim%:    {s['stim_pct']:.1f}%")

    # ------------------------------------------------------------------
    # Statistical tests: Wilcoxon signed-rank (paired across subjects)
    # ------------------------------------------------------------------
    print(f"\n{'='*90}")
    print("STATISTICAL TESTS (Wilcoxon signed-rank, paired across subjects)")
    print(f"{'='*90}")

    baselines = ["Fixed Schedule (actual)", "Reactive Threshold"]
    test_controllers = new_controllers

    for baseline_name in baselines:
        baseline_trials = all_results.get(baseline_name, [])
        if len(baseline_trials) < 5:
            continue
        baseline_by_subj = {t["subject"]: t for t in baseline_trials}

        for test_name in test_controllers:
            test_trials = all_results.get(test_name, [])
            if len(test_trials) < 5:
                continue
            test_by_subj = {t["subject"]: t for t in test_trials}
            common = sorted(set(baseline_by_subj) & set(test_by_subj))
            if len(common) < 5:
                continue

            print(f"\n  {test_name} vs {baseline_name} (n={len(common)} subjects):")

            for metric, label in [
                ("stim_hit_rate", "Hit rate"),
                ("wasted_stim_pct", "Wasted stim%"),
                ("stim_pct", "Stim%"),
            ]:
                base_vals = np.array([baseline_by_subj[s][metric] for s in common])
                test_vals = np.array([test_by_subj[s][metric] for s in common])
                diff = test_vals - base_vals

                # Wilcoxon requires non-zero differences
                nonzero = np.abs(diff) > 1e-10
                if nonzero.sum() < 5:
                    print(f"    {label}: insufficient non-zero differences")
                    continue

                stat, p_val = stats.wilcoxon(diff[nonzero])
                direction = "higher" if np.median(diff) > 0 else "lower"
                scale = 100.0 if metric == "stim_hit_rate" else 1.0
                print(
                    f"    {label}: "
                    f"base={scale*np.mean(base_vals):.1f}{'%' if scale > 1 else ''}, "
                    f"test={scale*np.mean(test_vals):.1f}{'%' if scale > 1 else ''}, "
                    f"median diff={scale*np.median(diff):+.2f}, "
                    f"W={stat:.0f}, p={p_val:.4f} ({direction})"
                )

    # ------------------------------------------------------------------
    # Save results
    # ------------------------------------------------------------------
    out_path = Path("results/replay_analysis.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "n_subjects": len(subjects),
        "n_controllers": len(summary),
        "summary": summary,
        "per_subject": {name: trials for name, trials in all_results.items()},
    }
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nSaved: {out_path}")
    print(f"Total runtime: {time_mod.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
