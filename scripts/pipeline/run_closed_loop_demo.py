"""
End-to-end closed-loop demo: compare control strategies with and without fatigue.

Runs TWO simulation scenarios:
  A. No fatigue (original model): continuous stimulation always works equally well.
  B. With fatigue (habituation model): continuous stimulation effectiveness
     degrades over time, rest periods allow recovery.

The fatigue-aware scenario demonstrates why adaptive scheduling outperforms
fixed-schedule stimulation — the key scientific claim.

Usage:
    python run_closed_loop_demo.py
    python run_closed_loop_demo.py --duration 600 --n-trials 10
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

from simulator import EntrainmentSimulator, FatigueAwareSimulator, StimAction

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Control strategies
# ---------------------------------------------------------------------------

class FixedScheduleControl:
    """40s ON + 20s OFF (standard clinical protocol)."""
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
    """Z-score reactive controller — stimulates when PAC drops below threshold."""
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
    sim,
    duration_sec: int = 360,
    seed: int | None = None,
) -> Dict:
    """Run one simulation trial for a control method on a given simulator."""
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

    # Late-session PAC (last 25% of trial) — shows fatigue effects
    late_start = int(0.75 * len(pac_arr))
    late_pac = float(np.mean(pac_arr[late_start:]))

    result = {
        "pac_mean": mean_pac,
        "pac_std": float(np.std(pac_arr)),
        "pac_improvement_pct": improvement,
        "stimulation_pct": stim_pct,
        "efficiency_ratio": efficiency,
        "late_session_pac": late_pac,
    }

    # Include fatigue info if available
    if hasattr(sim, 'fatigue_history'):
        result["final_fatigue"] = float(sim.fatigue_history[-1])
        result["mean_fatigue"] = float(np.mean(sim.fatigue_history))

    return result


def run_scenario(
    scenario_name: str,
    sim_factory,
    methods: list,
    n_trials: int,
    duration_sec: int,
    base_seed: int,
) -> Dict[str, List[Dict]]:
    """Run all methods for a scenario and print results."""
    print(f"\n{'#'*70}")
    print(f"  SCENARIO: {scenario_name}")
    print(f"{'#'*70}")

    all_results: Dict[str, List[Dict]] = {}

    for method in methods:
        print(f"\n{'='*60}")
        print(f"  {method.name}")
        print(f"{'='*60}")

        trials = []
        for trial in range(n_trials):
            seed = base_seed + trial
            sim = sim_factory()
            res = run_trial(method, sim, duration_sec=duration_sec, seed=seed)
            trials.append(res)

            fatigue_str = ""
            if "final_fatigue" in res:
                fatigue_str = f", fatigue={res['final_fatigue']:.2f}"

            print(
                f"  Trial {trial+1}: "
                f"PAC={res['pac_mean']:.4f}, "
                f"late_PAC={res['late_session_pac']:.4f}, "
                f"improv={res['pac_improvement_pct']:+.1f}%, "
                f"stim={res['stimulation_pct']:.1f}%, "
                f"eff={res['efficiency_ratio']:.3f}"
                f"{fatigue_str}"
            )

        all_results[method.name] = trials

    return all_results


def print_summary(scenario_name: str, all_results: Dict[str, List[Dict]]) -> Dict:
    """Print comparison summary table and return summary dict."""
    print(f"\n{'='*70}")
    print(f"  {scenario_name} — COMPARISON SUMMARY (mean +/- std)")
    print(f"{'='*70}")
    print(
        f"{'Method':<24s} "
        f"{'PAC Mean':>10s} {'Late PAC':>10s} {'Improv%':>9s} {'Stim%':>7s} {'Effic':>8s}"
    )
    print("-" * 72)

    summary = {}
    for name, trials in all_results.items():
        pac_means = [t["pac_mean"] for t in trials]
        late_pacs = [t["late_session_pac"] for t in trials]
        improvements = [t["pac_improvement_pct"] for t in trials]
        stim_pcts = [t["stimulation_pct"] for t in trials]
        effs = [t["efficiency_ratio"] for t in trials]

        row = {
            "pac_mean": f"{np.mean(pac_means):.4f}",
            "pac_mean_std": f"{np.std(pac_means):.4f}",
            "late_session_pac": f"{np.mean(late_pacs):.4f}",
            "late_session_pac_std": f"{np.std(late_pacs):.4f}",
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
            f"{np.mean(late_pacs):>8.4f} "
            f"{np.mean(improvements):>+7.1f}% "
            f"{np.mean(stim_pcts):>5.1f}% "
            f"{np.mean(effs):>8.3f}"
        )

    # Wilcoxon test: Predictive vs Fixed
    from scipy import stats

    pred_trials = all_results.get("Predictive Look-Ahead", [])
    fixed_trials = all_results.get("Fixed Schedule", [])
    if len(pred_trials) >= 3 and len(fixed_trials) >= 3:
        pred_eff = [t["efficiency_ratio"] for t in pred_trials]
        fixed_eff = [t["efficiency_ratio"] for t in fixed_trials]
        try:
            stat, p_val = stats.wilcoxon(pred_eff, fixed_eff)
            print(f"\n  Wilcoxon efficiency (Predictive vs Fixed): stat={stat:.4f}, p={p_val:.4f}")
            summary["wilcoxon_pred_vs_fixed_efficiency"] = {
                "statistic": float(stat), "p_value": float(p_val)
            }
        except Exception:
            pass

    # Wilcoxon test: Predictive vs Fixed on late-session PAC
    if len(pred_trials) >= 3 and len(fixed_trials) >= 3:
        pred_late = [t["late_session_pac"] for t in pred_trials]
        fixed_late = [t["late_session_pac"] for t in fixed_trials]
        try:
            stat, p_val = stats.wilcoxon(pred_late, fixed_late)
            print(f"  Wilcoxon late PAC (Predictive vs Fixed):   stat={stat:.4f}, p={p_val:.4f}")
            summary["wilcoxon_pred_vs_fixed_late_pac"] = {
                "statistic": float(stat), "p_value": float(p_val)
            }
        except Exception:
            pass

    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Closed-loop demo with fatigue comparison.")
    p.add_argument("--duration", default=600, type=int,
                   help="Simulation duration in seconds per trial (default: 600 = 10 min)")
    p.add_argument("--n-trials", default=10, type=int,
                   help="Number of independent trials per method")
    p.add_argument("--seed", default=42, type=int)
    p.add_argument("--output-dir", default="results", type=str)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    methods = [
        FixedScheduleControl(),
        ReactiveThresholdControl(),
        PredictiveLookAheadControl(),
        OracleControl(),
    ]

    # --- Scenario A: No fatigue (baseline) ---
    results_no_fatigue = run_scenario(
        scenario_name="NO FATIGUE (baseline simulator)",
        sim_factory=lambda: EntrainmentSimulator(
            tau_rise=0.15, tau_decay=0.10,
            pac_max=0.3, pac_min=0.05, noise_std=0.02,
        ),
        methods=methods,
        n_trials=args.n_trials,
        duration_sec=args.duration,
        base_seed=args.seed,
    )
    summary_no_fatigue = print_summary("NO FATIGUE", results_no_fatigue)

    # --- Scenario B: With fatigue ---
    results_fatigue = run_scenario(
        scenario_name="WITH FATIGUE (habituation model)",
        sim_factory=lambda: FatigueAwareSimulator(
            tau_rise=0.15, tau_decay=0.10,
            pac_max=0.3, pac_min=0.05, noise_std=0.02,
            fatigue_rate=0.008, recovery_rate=0.03, max_fatigue=0.7,
        ),
        methods=methods,
        n_trials=args.n_trials,
        duration_sec=args.duration,
        base_seed=args.seed,
    )
    summary_fatigue = print_summary("WITH FATIGUE", results_fatigue)

    # --- Cross-scenario comparison ---
    print(f"\n{'#'*70}")
    print("  FATIGUE IMPACT: How much does each strategy degrade?")
    print(f"{'#'*70}")
    print(
        f"{'Method':<24s} "
        f"{'No-fatigue':>10s} {'Fatigue':>10s} {'Degradation':>12s} "
        f"{'Late PAC':>10s} {'Late Fatigue':>12s}"
    )
    print("-" * 80)

    for name in ["Fixed Schedule", "Reactive Threshold", "Predictive Look-Ahead", "Oracle"]:
        nf_pac = float(summary_no_fatigue[name]["pac_mean"])
        f_pac = float(summary_fatigue[name]["pac_mean"])
        degradation = 100.0 * (f_pac - nf_pac) / (nf_pac + 1e-8)

        nf_late = float(summary_no_fatigue[name]["late_session_pac"])
        f_late = float(summary_fatigue[name]["late_session_pac"])
        late_degrad = 100.0 * (f_late - nf_late) / (nf_late + 1e-8)

        print(
            f"{name:<24s} "
            f"{nf_pac:>10.4f} {f_pac:>10.4f} {degradation:>+10.1f}% "
            f"{nf_late:>10.4f}->{f_late:.4f} {late_degrad:>+10.1f}%"
        )

    # Verdict
    fixed_f = float(summary_fatigue["Fixed Schedule"]["pac_mean"])
    pred_f = float(summary_fatigue["Predictive Look-Ahead"]["pac_mean"])
    fixed_f_eff = float(summary_fatigue["Fixed Schedule"]["efficiency"])
    pred_f_eff = float(summary_fatigue["Predictive Look-Ahead"]["efficiency"])
    fixed_f_stim = float(summary_fatigue["Fixed Schedule"]["stim_pct"])
    pred_f_stim = float(summary_fatigue["Predictive Look-Ahead"]["stim_pct"])

    print(f"\n{'='*70}")
    print("VERDICT")
    print(f"{'='*70}")

    if pred_f_eff > fixed_f_eff:
        eff_gain = 100.0 * (pred_f_eff - fixed_f_eff) / (fixed_f_eff + 1e-8)
        stim_saving = fixed_f_stim - pred_f_stim
        print(f"With fatigue, Predictive Look-Ahead achieves:")
        print(f"  - {eff_gain:+.1f}% higher efficiency than Fixed Schedule")
        print(f"  - {stim_saving:.1f} percentage points less stimulation time")
        if pred_f > fixed_f:
            print(f"  - {pred_f:.4f} vs {fixed_f:.4f} mean PAC (HIGHER despite less stimulation)")
        else:
            pac_cost = 100.0 * (pred_f - fixed_f) / (fixed_f + 1e-8)
            print(f"  - {pac_cost:+.1f}% PAC trade-off for {stim_saving:.1f}% less stimulation")
        print()
        print("CONCLUSION: Adaptive scheduling outperforms fixed schedule")
        print("when neural habituation is present. The predictive controller")
        print("achieves comparable or better PAC with significantly less")
        print("stimulation by timing interventions to avoid fatigue buildup.")
    else:
        print("Predictive does not beat Fixed Schedule on efficiency.")
        print("Further tuning of controller parameters may be needed.")

    # Save results
    output = {
        "config": {
            "duration_sec": args.duration,
            "n_trials": args.n_trials,
            "seed": args.seed,
        },
        "no_fatigue": {
            "summary": summary_no_fatigue,
            "raw_trials": results_no_fatigue,
        },
        "with_fatigue": {
            "summary": summary_fatigue,
            "raw_trials": results_fatigue,
        },
    }
    out_path = output_dir / "closed_loop_demo_results.json"
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
