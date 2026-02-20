"""
Fatigue sensitivity sweep: how does the advantage of adaptive scheduling
grow as habituation severity increases?

Sweeps fatigue_rate from 0 (no habituation) to 0.04 (severe habituation)
and shows that the efficiency gap between Predictive Look-Ahead and
Fixed Schedule widens with stronger fatigue.

Usage:
    python run_fatigue_sensitivity.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from simulator import FatigueAwareSimulator, StimAction


# --- Controllers (inline for self-containment) ---

class FixedScheduleControl:
    name = "Fixed Schedule"
    def __init__(self):
        self.step_count = 0
    def reset(self):
        self.step_count = 0
    def step(self, pac: float) -> int:
        pos = self.step_count % 60
        self.step_count += 1
        return StimAction.STIMULATE if pos < 40 else StimAction.REST


class PredictiveLookAheadControl:
    name = "Predictive Look-Ahead"
    def __init__(self, window=30, z_thresh=0.5, trend_k=5, hold_time=5):
        self.window = window
        self.z_thresh = z_thresh
        self.trend_k = trend_k
        self.hold_time = hold_time
        self.buf: list = []
        self.state = StimAction.REST
        self.t_in_state = 0

    def reset(self):
        self.buf = []
        self.state = StimAction.REST
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
            return StimAction.REST
        mu = np.mean(self.buf)
        sigma = np.std(self.buf) + 1e-8
        z = (pac - mu) / sigma
        trend = self._trend()
        desired = None
        if trend < -0.3 * sigma:
            desired = StimAction.STIMULATE
        elif trend > 0.3 * sigma:
            desired = StimAction.REST
        elif z < -self.z_thresh:
            desired = StimAction.STIMULATE
        elif z > self.z_thresh:
            desired = StimAction.REST
        if desired is None:
            desired = self.state
        if desired != self.state:
            if self.t_in_state >= self.hold_time:
                self.state = desired
                self.t_in_state = 0
        else:
            self.t_in_state += 1
        return self.state


def run_trial(method, sim, duration_sec=600, seed=None):
    if seed is not None:
        np.random.seed(seed)
    sim.reset()
    method.reset()
    pac_values = []
    actions = []
    for _ in range(duration_sec):
        pac = sim.pac
        action = method.step(pac)
        sim.step(action)
        pac_values.append(pac)
        actions.append(action)

    pac_arr = np.array(pac_values)
    act_arr = np.array(actions)
    baseline = pac_arr[0]
    mean_pac = float(np.mean(pac_arr))
    improvement = 100.0 * (mean_pac - baseline) / (baseline + 1e-8)
    stim_pct = 100.0 * float(np.mean(act_arr))
    efficiency = improvement / (stim_pct + 1e-8) if stim_pct > 0 else 0.0

    # Late session (last 25%)
    late_start = int(0.75 * len(pac_arr))
    late_pac = float(np.mean(pac_arr[late_start:]))

    return {
        "pac_mean": mean_pac,
        "pac_improvement_pct": improvement,
        "stimulation_pct": stim_pct,
        "efficiency_ratio": efficiency,
        "late_session_pac": late_pac,
        "final_fatigue": float(sim.fatigue_history[-1]),
    }


def main():
    n_trials = 10
    duration = 600
    base_seed = 42

    fatigue_rates = [0.0, 0.004, 0.008, 0.015, 0.025, 0.04]

    print("=" * 80)
    print("FATIGUE SENSITIVITY ANALYSIS")
    print("How does adaptive scheduling advantage grow with habituation severity?")
    print("=" * 80)
    print(f"Config: {n_trials} trials, {duration}s each, recovery_rate=0.03, max_fatigue=0.7\n")

    print(
        f"{'Fatigue Rate':>12s} | "
        f"{'Fixed PAC':>10s} {'Fixed Eff':>10s} | "
        f"{'Pred PAC':>10s} {'Pred Eff':>10s} | "
        f"{'Eff Gain%':>10s} {'Stim Save':>10s} {'p-value':>8s}"
    )
    print("-" * 95)

    results = []

    for fr in fatigue_rates:
        fixed_trials = []
        pred_trials = []

        for trial in range(n_trials):
            seed = base_seed + trial

            sim = FatigueAwareSimulator(
                tau_rise=0.15, tau_decay=0.10,
                pac_max=0.3, pac_min=0.05, noise_std=0.02,
                fatigue_rate=fr, recovery_rate=0.03, max_fatigue=0.7,
            )
            method = FixedScheduleControl()
            fixed_trials.append(run_trial(method, sim, duration, seed))

            sim = FatigueAwareSimulator(
                tau_rise=0.15, tau_decay=0.10,
                pac_max=0.3, pac_min=0.05, noise_std=0.02,
                fatigue_rate=fr, recovery_rate=0.03, max_fatigue=0.7,
            )
            method = PredictiveLookAheadControl()
            pred_trials.append(run_trial(method, sim, duration, seed))

        fixed_pac = np.mean([t["pac_mean"] for t in fixed_trials])
        fixed_eff = np.mean([t["efficiency_ratio"] for t in fixed_trials])
        pred_pac = np.mean([t["pac_mean"] for t in pred_trials])
        pred_eff = np.mean([t["efficiency_ratio"] for t in pred_trials])

        eff_gain = 100.0 * (pred_eff - fixed_eff) / (fixed_eff + 1e-8)
        stim_save = np.mean([t["stimulation_pct"] for t in fixed_trials]) - \
                    np.mean([t["stimulation_pct"] for t in pred_trials])

        # Wilcoxon on efficiency
        try:
            _, p_val = stats.wilcoxon(
                [t["efficiency_ratio"] for t in pred_trials],
                [t["efficiency_ratio"] for t in fixed_trials],
            )
        except Exception:
            p_val = 1.0

        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""

        print(
            f"{fr:>12.3f} | "
            f"{fixed_pac:>10.4f} {fixed_eff:>10.3f} | "
            f"{pred_pac:>10.4f} {pred_eff:>10.3f} | "
            f"{eff_gain:>+9.1f}% {stim_save:>9.1f}pp {p_val:>7.4f} {sig}"
        )

        results.append({
            "fatigue_rate": fr,
            "fixed_pac_mean": fixed_pac,
            "fixed_efficiency": fixed_eff,
            "pred_pac_mean": pred_pac,
            "pred_efficiency": pred_eff,
            "efficiency_gain_pct": eff_gain,
            "stim_saving_pp": stim_save,
            "wilcoxon_p": p_val,
        })

    # Summary
    print(f"\n{'='*80}")
    print("INTERPRETATION")
    print(f"{'='*80}")

    gains = [r["efficiency_gain_pct"] for r in results if r["fatigue_rate"] > 0]
    if all(g > 0 for g in gains):
        print("At ALL non-zero fatigue levels, adaptive scheduling is more efficient.")
        print(f"Efficiency advantage ranges from {min(gains):+.1f}% to {max(gains):+.1f}%.")
    sig_count = sum(1 for r in results if r["wilcoxon_p"] < 0.05 and r["fatigue_rate"] > 0)
    total_non_zero = sum(1 for r in results if r["fatigue_rate"] > 0)
    print(f"Statistically significant (p<0.05) at {sig_count}/{total_non_zero} non-zero fatigue levels.")

    out_path = Path("results/fatigue_sensitivity.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
