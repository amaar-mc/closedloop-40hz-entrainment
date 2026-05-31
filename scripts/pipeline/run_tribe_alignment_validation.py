"""
TRIBE V2-Enhanced Simulation: Alignment & Clinical Utility Evaluation

Computes the EXACT same metrics as the real-data validation (run_tcn_validation.py):
    - Alignment score = (Low-PAC Stim Rate + High-PAC Rest Rate) / 2
    - Low-PAC Stim Rate (targeting precision)
    - High-PAC Rest Rate (specificity)
    - PAC Gap = mean_PAC_rest - mean_PAC_stim (positive = correct targeting)
    - Clinical Utility composite
    - Effect sizes (Hedges' g) for all pairwise comparisons

Runs across Alzheimer's disease severities to show how the therapeutic
benefit of predictive control changes with disease progression.

Usage:
    PYTHONPATH=src python scripts/pipeline/run_tribe_alignment_validation.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from simulator import StimAction
from tribe_v2.enhanced_simulator import create_simulator
from tribe_v2.alzheimer_model import ALZHEIMER_PROFILES


# ─── Controllers (same logic as original validation) ───

class FixedScheduleCtrl:
    name = "Fixed Schedule"
    def __init__(self): self.t = 0
    def reset(self): self.t = 0
    def step(self, pac, **kw):
        pos = self.t % 60
        self.t += 1
        return 1 if pos < 40 else 0

class ReactiveCtrl:
    name = "Reactive Threshold"
    def __init__(self, w=30, z_thresh=0.5):
        self.w = w; self.z = z_thresh; self.buf = []
    def reset(self): self.buf = []
    def step(self, pac, **kw):
        self.buf.append(pac)
        if len(self.buf) > self.w: self.buf.pop(0)
        if len(self.buf) < 10: return 0
        mu, sig = np.mean(self.buf), np.std(self.buf) + 1e-12
        return 1 if (pac - mu) / sig < -self.z else 0

class PredictiveCtrl:
    name = "TCN Predictive"
    def __init__(self, w=30, z_thresh=0.5, trend_k=5, hold=3):
        self.w = w; self.z = z_thresh; self.trend_k = trend_k
        self.hold = hold; self.buf = []; self.state = 0; self.t_in_state = 0
    def reset(self):
        self.buf = []; self.state = 0; self.t_in_state = 0
    def _trend(self):
        if len(self.buf) < self.trend_k: return 0.0
        r = self.buf[-self.trend_k:]
        x = np.arange(self.trend_k, dtype=np.float64)
        y = np.array(r, dtype=np.float64)
        xm, ym = x.mean(), y.mean()
        d = np.sum((x - xm)**2)
        return float(np.sum((x - xm)*(y - ym))/d) if d > 1e-12 else 0.0
    def step(self, pac, **kw):
        self.buf.append(pac)
        if len(self.buf) > self.w: self.buf.pop(0)
        if len(self.buf) < 10: return 0
        mu, sig = np.mean(self.buf), np.std(self.buf) + 1e-12
        z = (pac - mu) / sig
        trend = self._trend()
        desired = None
        if trend < -0.003: desired = 1
        elif trend > 0.003: desired = 0
        elif z < -self.z: desired = 1
        elif z > self.z: desired = 0
        if desired is None: desired = self.state
        if desired != self.state and self.t_in_state >= self.hold:
            self.state = desired; self.t_in_state = 0
        else: self.t_in_state += 1
        return self.state

class OracleCtrl:
    name = "Alignment Oracle"
    def __init__(self): self.pac_all = None; self.median = None; self.t = 0
    def set_pac(self, pac_all):
        self.pac_all = pac_all; self.median = np.median(pac_all)
    def reset(self): self.t = 0
    def step(self, pac, **kw):
        a = 1 if pac < self.median else 0
        self.t += 1; return a


# ─── Evaluation (same as run_tcn_validation.py) ───

def evaluate_alignment(pac: np.ndarray, decisions: np.ndarray) -> dict:
    """Compute alignment metrics — exact same definitions as original study."""
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
    pac_gap = mean_pac_rest - mean_pac_stim

    stim_pct = 100.0 * float(np.mean(stim_mask))
    # Clinical utility (simplified — no lead time in simulation)
    align_norm = min(alignment, 1.0)
    eff_norm = max(0, 1 - stim_pct / 100.0)
    utility = 0.50 * align_norm + 0.30 * eff_norm + 0.20 * max(0, pac_gap / (np.std(pac) + 1e-10))

    return {
        "alignment": alignment,
        "low_pac_stim_rate": low_stim_rate,
        "high_pac_rest_rate": high_rest_rate,
        "stim_pct": stim_pct,
        "pac_gap": pac_gap,
        "mean_pac_stim": mean_pac_stim,
        "mean_pac_rest": mean_pac_rest,
        "clinical_utility": utility,
    }


def hedges_g(a: np.ndarray, b: np.ndarray) -> float:
    """Compute Hedges' g effect size."""
    na, nb = len(a), len(b)
    pooled_std = np.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2))
    if pooled_std < 1e-12:
        return 0.0
    d = (np.mean(a) - np.mean(b)) / pooled_std
    # Correction factor
    cf = 1 - 3 / (4 * (na + nb) - 9)
    return float(d * cf)


# ─── Simulation runner ───

def run_subject_trial(ctrl, severity, duration_sec, seed):
    """Run one simulated subject trial and return alignment metrics."""
    # Oracle needs a two-pass approach: first collect PAC, then decide
    if isinstance(ctrl, OracleCtrl):
        sim = create_simulator(
            disease_severity=severity, use_tribe_v2=False,
            subject_seed=seed, step_duration_sec=1.0,
        )
        # Pass 1: collect PAC under fixed schedule to get natural dynamics
        pac_values = []
        for step in range(duration_sec):
            pac_values.append(sim.pac)
            action = 1 if (step % 60) < 40 else 0
            sim.step(action)
        pac_arr = np.array(pac_values)
        # Pass 2: oracle uses full PAC knowledge
        median_pac = np.median(pac_arr)
        dec_arr = np.array([1 if p < median_pac else 0 for p in pac_arr])
        return evaluate_alignment(pac_arr, dec_arr)

    sim = create_simulator(
        disease_severity=severity, use_tribe_v2=False,
        subject_seed=seed, step_duration_sec=1.0,
    )
    ctrl.reset()

    pac_values, decisions = [], []
    for _ in range(duration_sec):
        pac = sim.pac
        action = ctrl.step(pac)
        sim.step(action)
        pac_values.append(pac)
        decisions.append(action)

    pac_arr = np.array(pac_values)
    dec_arr = np.array(decisions)
    return evaluate_alignment(pac_arr, dec_arr)


def main():
    duration_sec = 600  # 10 minutes per subject
    n_subjects = 35     # Match original N=35
    base_seed = 42

    print("=" * 80)
    print("  TRIBE V2 SIMULATION: Alignment & Clinical Utility")
    print("  (Same metrics as real-data TCN validation, N=35 simulated subjects)")
    print("=" * 80)

    all_results = {}

    for severity in ["healthy", "mild", "moderate", "severe"]:
        print(f"\n{'─' * 70}")
        print(f"  Disease Severity: {severity.upper()}")
        print(f"{'─' * 70}")

        ctrls = [
            FixedScheduleCtrl(),
            ReactiveCtrl(),
            PredictiveCtrl(),
            OracleCtrl(),
        ]

        severity_results = {}
        for ctrl in ctrls:
            subject_metrics = []
            for subj in range(n_subjects):
                seed = base_seed + subj
                metrics = run_subject_trial(ctrl, severity, duration_sec, seed)
                subject_metrics.append(metrics)
            severity_results[ctrl.name] = subject_metrics

        # Print summary table
        print(f"\n  {'Controller':<22s} {'Alignment':>10s} {'Low-PAC Stim':>13s} "
              f"{'High-PAC Rest':>14s} {'Stim %':>7s} {'PAC Gap':>10s} {'Utility':>8s}")
        print("  " + "-" * 88)

        for ctrl in ctrls:
            trials = severity_results[ctrl.name]
            align = 100 * np.mean([t["alignment"] for t in trials])
            low_stim = 100 * np.mean([t["low_pac_stim_rate"] for t in trials])
            high_rest = 100 * np.mean([t["high_pac_rest_rate"] for t in trials])
            stim_pct = np.mean([t["stim_pct"] for t in trials])
            gap = np.mean([t["pac_gap"] for t in trials])
            utility = np.mean([t["clinical_utility"] for t in trials])
            print(f"  {ctrl.name:<22s} {align:>9.1f}% {low_stim:>12.1f}% "
                  f"{high_rest:>13.1f}% {stim_pct:>6.1f}% {gap:>+10.6f} {utility:>8.3f}")

        # Effect sizes: Predictive vs Reactive
        pred_trials = severity_results["TCN Predictive"]
        react_trials = severity_results["Reactive Threshold"]
        oracle_trials = severity_results["Alignment Oracle"]

        print(f"\n  Effect Sizes (TCN Predictive vs Reactive Threshold):")
        print(f"  {'Metric':<22s} {'TCN':>8s} {'Reactive':>10s} {'Hedges g':>10s} {'p-value':>10s}")
        print("  " + "-" * 65)

        for metric, label, scale in [
            ("alignment", "Alignment", 100),
            ("low_pac_stim_rate", "Low-PAC Stim", 100),
            ("high_pac_rest_rate", "High-PAC Rest", 100),
            ("pac_gap", "PAC Gap", 1),
            ("clinical_utility", "Clinical Utility", 1),
        ]:
            a = np.array([t[metric] for t in pred_trials])
            b = np.array([t[metric] for t in react_trials])
            g = hedges_g(a, b)
            t_stat, p_val = stats.ttest_rel(a, b) if len(a) > 1 else (0, 1)
            print(f"  {label:<22s} {scale * np.mean(a):>8.1f} {scale * np.mean(b):>10.1f} "
                  f"{g:>+10.2f} {p_val:>10.4f}")

        # Oracle fraction
        pred_align = np.mean([t["alignment"] for t in pred_trials])
        oracle_align = np.mean([t["alignment"] for t in oracle_trials])
        oracle_frac = pred_align / oracle_align if oracle_align > 0 else 0
        print(f"\n  Oracle fraction: {100 * oracle_frac:.1f}% "
              f"(TCN {100*pred_align:.1f}% / Oracle {100*oracle_align:.1f}%)")

        # Subject consistency
        n_better = sum(
            1 for i in range(n_subjects)
            if pred_trials[i]["alignment"] > react_trials[i]["alignment"]
        )
        print(f"  Subjects where TCN > Reactive: {n_better}/{n_subjects} ({100*n_better/n_subjects:.0f}%)")

        all_results[severity] = {
            ctrl_name: [
                {k: round(float(v), 6) for k, v in t.items()}
                for t in trials
            ]
            for ctrl_name, trials in severity_results.items()
        }

    # ─── Cross-severity summary ───
    print("\n" + "=" * 80)
    print("  CROSS-SEVERITY SUMMARY: TCN Predictive Controller")
    print("=" * 80)
    print(f"  {'Severity':<12s} {'Alignment':>10s} {'Low-PAC Stim':>13s} "
          f"{'PAC Gap':>10s} {'Oracle %':>10s} {'N better':>10s}")
    print("  " + "-" * 70)

    for severity in ["healthy", "mild", "moderate", "severe"]:
        pred = all_results[severity]["TCN Predictive"]
        react = all_results[severity]["Reactive Threshold"]
        oracle = all_results[severity]["Alignment Oracle"]

        align = 100 * np.mean([t["alignment"] for t in pred])
        low_stim = 100 * np.mean([t["low_pac_stim_rate"] for t in pred])
        gap = np.mean([t["pac_gap"] for t in pred])
        oracle_align = np.mean([t["alignment"] for t in oracle])
        pred_align = np.mean([t["alignment"] for t in pred])
        ofrac = 100 * pred_align / oracle_align if oracle_align > 0 else 0
        n_better = sum(
            1 for i in range(n_subjects)
            if pred[i]["alignment"] > react[i]["alignment"]
        )

        print(f"  {severity:<12s} {align:>9.1f}% {low_stim:>12.1f}% "
              f"{gap:>+10.6f} {ofrac:>9.1f}% {n_better:>5d}/{n_subjects}")

    # Save
    out_dir = Path("results/tribe_v2")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "tribe_v2_alignment_results.json"
    out_path.write_text(json.dumps(all_results, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
