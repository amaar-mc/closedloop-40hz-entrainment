"""
End-to-end closed-loop demo: compare all control strategies in simulation.

This is the "one command to reproduce everything" script.  It:
  1. Loads a trained TCN checkpoint and dataset scalers.
  2. Runs N simulated sessions per control strategy:
       - Fixed Schedule (40s ON / 20s OFF)
       - Reactive Threshold (current PAC z-score)
       - Predictive Look-Ahead (PAC trend + z-score)
       - Oracle (perfect PAC knowledge)
  3. Outputs a comparison table and summary JSON.

Usage:
    python run_closed_loop_demo.py
    python run_closed_loop_demo.py --duration 600 --n-trials 5
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np

# Ensure src/ is importable
ROOT = Path(__file__).resolve().parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from simulator import EntrainmentSimulator, StimAction

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Control strategies (self-contained, no external model dependency)
# ---------------------------------------------------------------------------

class FixedScheduleControl:
    """40s ON + 20s OFF."""
    name = "Fixed Schedule"

    def __init__(self, stim_dur: int = 40, rest_dur: int = 20):
        self.cycle = stim_dur + rest_dur
        self.stim_dur = stim_dur
        self.step_count = 0

    def reset(self):
        self.step_count = 0

    def step(self, pac: float) -> int:
        pos = self.step_count % self.cycle
        self.step_count += 1
        return StimAction.STIMULATE if pos < self.stim_dur else StimAction.REST


class ReactiveThresholdControl:
    """Z-score reactive controller."""
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
            return StimAction.REST
        mu = np.mean(self.buf)
        sigma = np.std(self.buf) + 1e-8
        z = (pac - mu) / sigma
        if z < -self.z_thresh:
            return StimAction.STIMULATE
        return StimAction.REST


class PredictiveLookAheadControl:
    """Trend-based look-ahead controller with hysteresis."""
    name = "Predictive Look-Ahead"

    def __init__(self, window: int = 30, z_thresh: float = 0.5,
                 trend_k: int = 5, hold_time: int = 5):
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
        # Proactive: declining trend -> stimulate
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


class OracleControl:
    """Perfect knowledge — stimulate when below target."""
    name = "Oracle"

    def __init__(self, target: float = 0.2):
        self.target = target

    def reset(self):
        pass

    def step(self, pac: float) -> int:
        return StimAction.STIMULATE if pac < self.target else StimAction.REST


# ---------------------------------------------------------------------------
# Simulation runner
# ---------------------------------------------------------------------------

def run_trial(
    method,
    duration_sec: int = 360,
    tau_rise: float = 0.15,
    tau_decay: float = 0.10,
    seed: int | None = None,
) -> Dict:
    """Run one simulation trial for a control method."""
    if seed is not None:
        np.random.seed(seed)

    sim = EntrainmentSimulator(
        tau_rise=tau_rise, tau_decay=tau_decay,
        pac_max=0.3, pac_min=0.05, noise_std=0.02,
    )
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

    return {
        "pac_mean": mean_pac,
        "pac_std": float(np.std(pac_arr)),
        "pac_improvement_pct": improvement,
        "stimulation_pct": stim_pct,
        "efficiency_ratio": efficiency,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Closed-loop demo simulation.")
    p.add_argument("--duration", default=360, type=int,
                   help="Simulation duration in seconds per trial")
    p.add_argument("--n-trials", default=5, type=int,
                   help="Number of independent trials per method")
    p.add_argument("--seed", default=42, type=int)
    p.add_argument("--output-dir", default="results", type=str)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    methods = [
        FixedScheduleControl(),
        ReactiveThresholdControl(),
        PredictiveLookAheadControl(),
        OracleControl(),
    ]

    all_results: Dict[str, List[Dict]] = {}

    for method in methods:
        print(f"\n{'='*60}")
        print(f"  {method.name}")
        print(f"{'='*60}")

        trials = []
        for trial in range(args.n_trials):
            seed = args.seed + trial
            res = run_trial(method, duration_sec=args.duration, seed=seed)
            trials.append(res)
            print(
                f"  Trial {trial+1}: "
                f"PAC={res['pac_mean']:.4f}, "
                f"improv={res['pac_improvement_pct']:+.1f}%, "
                f"stim={res['stimulation_pct']:.1f}%, "
                f"eff={res['efficiency_ratio']:.3f}"
            )

        all_results[method.name] = trials

    # Aggregate
    print(f"\n{'='*70}")
    print("COMPARISON SUMMARY (mean +/- std across trials)")
    print(f"{'='*70}")
    print(
        f"{'Method':<24s} "
        f"{'PAC Mean':>10s} {'Improv%':>9s} {'Stim%':>7s} {'Effic':>8s}"
    )
    print("-" * 62)

    summary = {}
    for name, trials in all_results.items():
        pac_means = [t["pac_mean"] for t in trials]
        improvements = [t["pac_improvement_pct"] for t in trials]
        stim_pcts = [t["stimulation_pct"] for t in trials]
        effs = [t["efficiency_ratio"] for t in trials]

        row = {
            "pac_mean": f"{np.mean(pac_means):.4f}",
            "pac_mean_std": f"{np.std(pac_means):.4f}",
            "improvement_pct": f"{np.mean(improvements):.1f}",
            "improvement_std": f"{np.std(improvements):.1f}",
            "stim_pct": f"{np.mean(stim_pcts):.1f}",
            "stim_std": f"{np.std(stim_pcts):.1f}",
            "efficiency": f"{np.mean(effs):.3f}",
            "efficiency_std": f"{np.std(effs):.3f}",
        }
        summary[name] = row

        print(
            f"{name:<24s} "
            f"{np.mean(pac_means):>8.4f}+-{np.std(pac_means):.4f} "
            f"{np.mean(improvements):>+7.1f}% "
            f"{np.mean(stim_pcts):>5.1f}% "
            f"{np.mean(effs):>8.3f}"
        )

    # Statistical test (Wilcoxon signed-rank) between Predictive and Reactive
    from scipy import stats

    pred_trials = all_results.get("Predictive Look-Ahead", [])
    react_trials = all_results.get("Reactive Threshold", [])
    if len(pred_trials) >= 3 and len(react_trials) >= 3:
        pred_pac = [t["pac_mean"] for t in pred_trials]
        react_pac = [t["pac_mean"] for t in react_trials]
        try:
            stat, p_val = stats.wilcoxon(pred_pac, react_pac)
            print(f"\nWilcoxon test (Predictive vs Reactive): stat={stat:.4f}, p={p_val:.4f}")
            summary["wilcoxon_pred_vs_reactive"] = {"statistic": float(stat), "p_value": float(p_val)}
        except Exception:
            pass

    # Save
    output = {
        "config": {
            "duration_sec": args.duration,
            "n_trials": args.n_trials,
            "seed": args.seed,
        },
        "summary": summary,
        "raw_trials": {k: v for k, v in all_results.items()},
    }
    out_path = output_dir / "closed_loop_demo_results.json"
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
