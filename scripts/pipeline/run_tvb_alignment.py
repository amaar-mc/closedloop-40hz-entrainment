"""
TVB Jansen-Rit Alignment Evaluation: Closed-Loop Controller Comparison

Runs Fixed Schedule / Reactive / Trend-Predictive / Oracle controllers
on the TVB Alzheimer's simulator across disease severities.

Each TVB step() takes ~0.5s, so we use reduced trial parameters:
    - 10 subjects per severity (different seeds)
    - 120 seconds per trial
    - 4 severities × 4 controllers = 160 trials total
    - Estimated runtime: ~25 minutes

Usage:
    PYTHONPATH=src python3 run_tvb_alignment.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from tribe_v2.tvb_simulator import TVBAlzheimerSimulator


# ─── Controllers ──────────────────────────────────────────────────────


class FixedScheduleCtrl:
    name = "Fixed Schedule"
    def __init__(self): self.t = 0
    def reset(self): self.t = 0
    def step(self, pac):
        self.t += 1
        return 1 if (self.t % 60) < 40 else 0


class ReactiveCtrl:
    name = "Reactive Threshold"
    def __init__(self, window: int = 30, z_thresh: float = 0.5):
        self.window = window
        self.z_thresh = z_thresh
        self.buf: list[float] = []
    def reset(self): self.buf = []
    def step(self, pac):
        self.buf.append(pac)
        if len(self.buf) > self.window:
            self.buf.pop(0)
        if len(self.buf) < 5:
            return 0
        mu = np.mean(self.buf)
        sig = np.std(self.buf) + 1e-12
        z = (pac - mu) / sig
        return 1 if z < -self.z_thresh else 0


class TrendPredictiveCtrl:
    name = "Trend Predictive"
    def __init__(self, window: int = 30, z_thresh: float = 0.5,
                 trend_k: int = 5, hold: int = 3):
        self.window = window
        self.z_thresh = z_thresh
        self.trend_k = trend_k
        self.hold = hold
        self.buf: list[float] = []
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
    def step(self, pac):
        self.buf.append(pac)
        if len(self.buf) > self.window:
            self.buf.pop(0)
        if len(self.buf) < 5:
            return 0
        mu = np.mean(self.buf)
        sig = np.std(self.buf) + 1e-12
        z = (pac - mu) / sig
        trend = self._trend()
        desired = None
        if trend < -0.003:
            desired = 1
        elif trend > 0.003:
            desired = 0
        elif z < -self.z_thresh:
            desired = 1
        elif z > self.z_thresh:
            desired = 0
        if desired is None:
            desired = self.state
        if desired != self.state and self.t_in_state >= self.hold:
            self.state = desired
            self.t_in_state = 0
        else:
            self.t_in_state += 1
        return self.state


# ─── Metrics ──────────────────────────────────────────────────────────


def evaluate_alignment(pac: np.ndarray, decisions: np.ndarray) -> dict:
    median_pac = np.median(pac)
    low_mask = pac < median_pac
    high_mask = pac >= median_pac
    stim_mask = decisions == 1
    rest_mask = decisions == 0

    low_stim = float(np.mean(stim_mask[low_mask])) if low_mask.sum() > 0 else 0.0
    high_rest = float(np.mean(rest_mask[high_mask])) if high_mask.sum() > 0 else 0.0
    alignment = (low_stim + high_rest) / 2.0

    mean_stim = float(np.mean(pac[stim_mask])) if stim_mask.sum() > 0 else 0.0
    mean_rest = float(np.mean(pac[rest_mask])) if rest_mask.sum() > 0 else 0.0
    pac_gap = mean_rest - mean_stim

    return {
        "alignment": round(alignment, 4),
        "low_pac_stim_rate": round(low_stim, 4),
        "high_pac_rest_rate": round(high_rest, 4),
        "stim_pct": round(100.0 * float(np.mean(stim_mask)), 1),
        "pac_gap": round(pac_gap, 6),
    }


def hedges_g(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return 0.0
    pooled = np.sqrt(
        ((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1))
        / (na + nb - 2)
    )
    if pooled < 1e-12:
        return 0.0
    d = (np.mean(a) - np.mean(b)) / pooled
    return float(d * (1 - 3 / (4 * (na + nb) - 9)))


# ─── Trial Runners ────────────────────────────────────────────────────


def run_trial(ctrl, severity: str, duration_steps: int, seed: int) -> dict:
    sim = TVBAlzheimerSimulator(severity=severity, seed=seed)
    ctrl.reset()
    pac_values = []
    decisions = []
    for _ in range(duration_steps):
        pac = sim.pac
        action = ctrl.step(pac)
        sim.step(action)
        pac_values.append(pac)
        decisions.append(action)
    return evaluate_alignment(np.array(pac_values), np.array(decisions))


def run_oracle_trial(severity: str, duration_steps: int, seed: int) -> dict:
    sim = TVBAlzheimerSimulator(severity=severity, seed=seed)
    pac_values = []
    for step in range(duration_steps):
        pac_values.append(sim.pac)
        action = 1 if (step % 60) < 40 else 0
        sim.step(action)
    pac_arr = np.array(pac_values)
    median_pac = np.median(pac_arr)
    dec_arr = np.array([1 if p < median_pac else 0 for p in pac_arr])
    return evaluate_alignment(pac_arr, dec_arr)


# ─── Main ─────────────────────────────────────────────────────────────


def main():
    n_subjects = 10
    duration_steps = 120
    base_seed = 42
    severities = ["healthy", "mild", "moderate", "severe"]

    controllers = [
        FixedScheduleCtrl(),
        ReactiveCtrl(),
        TrendPredictiveCtrl(),
    ]

    print("=" * 75)
    print("  TVB Jansen-Rit Alzheimer Simulator: Alignment Evaluation")
    print(f"  N={n_subjects} subjects, {duration_steps} steps/trial, ~0.5s/step")
    print("=" * 75)

    t_start = time.time()
    results = {}

    for severity in severities:
        print(f"\n{'─' * 65}")
        print(f"  Severity: {severity.upper()}")
        print(f"{'─' * 65}")

        sev_results = {}

        for ctrl in controllers:
            trial_metrics = []
            t0 = time.time()
            for subj in range(n_subjects):
                seed = base_seed + subj * 137
                m = run_trial(ctrl, severity, duration_steps, seed)
                trial_metrics.append(m)
            elapsed = time.time() - t0

            alignments = np.array([t["alignment"] for t in trial_metrics])
            low_pac = np.array([t["low_pac_stim_rate"] for t in trial_metrics])
            pac_gaps = np.array([t["pac_gap"] for t in trial_metrics])

            sev_results[ctrl.name] = {
                "alignment_mean": round(float(np.mean(alignments)), 4),
                "alignment_std": round(float(np.std(alignments)), 4),
                "low_pac_stim_mean": round(float(np.mean(low_pac)), 4),
                "pac_gap_mean": round(float(np.mean(pac_gaps)), 6),
                "alignments": alignments.tolist(),
            }

            print(
                f"    {ctrl.name:22s}: align={np.mean(alignments):.3f}"
                f"±{np.std(alignments):.3f}"
                f"  low_pac={np.mean(low_pac):.3f}"
                f"  gap={np.mean(pac_gaps):+.5f}"
                f"  ({elapsed:.0f}s)"
            )

        # Oracle
        t0 = time.time()
        oracle_trials = []
        for subj in range(n_subjects):
            seed = base_seed + subj * 137
            m = run_oracle_trial(severity, duration_steps, seed)
            oracle_trials.append(m)
        elapsed = time.time() - t0

        o_align = np.array([t["alignment"] for t in oracle_trials])
        sev_results["Oracle"] = {
            "alignment_mean": round(float(np.mean(o_align)), 4),
            "alignment_std": round(float(np.std(o_align)), 4),
        }
        print(
            f"    {'Oracle':22s}: align={np.mean(o_align):.3f}"
            f"±{np.std(o_align):.3f}  ({elapsed:.0f}s)"
        )

        # Effect sizes
        trend_align = np.array(sev_results["Trend Predictive"]["alignments"])
        react_align = np.array(sev_results["Reactive Threshold"]["alignments"])
        g = hedges_g(trend_align, react_align)

        try:
            _, p = wilcoxon(trend_align, react_align)
        except ValueError:
            p = 1.0

        oracle_mean = float(np.mean(o_align))
        trend_mean = float(np.mean(trend_align))
        react_mean = float(np.mean(react_align))
        pct_oracle_trend = 100.0 * trend_mean / oracle_mean if oracle_mean > 0 else 0
        pct_oracle_react = 100.0 * react_mean / oracle_mean if oracle_mean > 0 else 0

        print(f"\n    Trend vs Reactive:  g={g:+.3f}, p={p:.4f}")
        print(f"    Trend Predictive = {pct_oracle_trend:.1f}% of Oracle")
        print(f"    Reactive         = {pct_oracle_react:.1f}% of Oracle")

        sev_results["trend_vs_reactive_g"] = round(g, 4)
        sev_results["trend_vs_reactive_p"] = round(float(p), 6)
        sev_results["trend_pct_oracle"] = round(pct_oracle_trend, 1)
        sev_results["reactive_pct_oracle"] = round(pct_oracle_react, 1)

        results[severity] = sev_results

    total_time = time.time() - t_start

    # Save results
    out_dir = ROOT / "results" / "tribe_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "tvb_alignment_results.json"

    save_data = {}
    for sev, sev_data in results.items():
        save_data[sev] = {
            k: v for k, v in sev_data.items()
            if not isinstance(v, dict) or "alignments" not in v
        }
        for ctrl_name, ctrl_data in sev_data.items():
            if isinstance(ctrl_data, dict) and "alignment_mean" in ctrl_data:
                save_data[sev][ctrl_name] = {
                    k: v for k, v in ctrl_data.items() if k != "alignments"
                }

    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2)

    print(f"\n{'=' * 75}")
    print(f"  Total time: {total_time:.0f}s ({total_time/60:.1f} min)")
    print(f"  Results saved to {out_path}")
    print(f"{'=' * 75}")


if __name__ == "__main__":
    main()
