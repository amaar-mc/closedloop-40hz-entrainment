"""
TRIBE V2-Enhanced Closed-Loop Validation

Compares control strategies across two simulation backends:
    A. Original exponential simulator (EntrainmentSimulator)
    B. TRIBE V2-enhanced simulator (biophysically grounded cortical model)

And across Alzheimer's disease severity levels:
    - Healthy, Preclinical, Mild, Moderate, Severe

Generates comprehensive comparison figures and statistics.

Usage:
    python run_tribe_validation.py
    python run_tribe_validation.py --duration 600 --n-trials 10
    python run_tribe_validation.py --disease-sweep --output-dir results/tribe_v2
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats

# Ensure src/ is importable
ROOT = Path(__file__).resolve().parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from simulator import EntrainmentSimulator, FatigueAwareSimulator, StimAction
from tribe_v2.enhanced_simulator import (
    TribeEnhancedSimulator,
    TribeSimulatorConfig,
    create_simulator,
)
from tribe_v2.alzheimer_model import ALZHEIMER_PROFILES

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────
# Control strategies (matching existing pipeline)
# ─────────────────────────────────────────────────────────────────────

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
    """Z-score reactive with hysteresis."""
    name = "Reactive"

    def __init__(self, window: int = 30, z_thresh: float = 0.5, hold_time: int = 5):
        self.window = window
        self.z_thresh = z_thresh
        self.hold_time = hold_time
        self.buf: list = []
        self.state = StimAction.REST
        self.t_in_state = 0

    def reset(self):
        self.buf = []
        self.state = StimAction.REST
        self.t_in_state = 0

    def step(self, pac: float) -> int:
        self.buf.append(pac)
        if len(self.buf) > self.window:
            self.buf.pop(0)
        if len(self.buf) < 10:
            self.t_in_state += 1
            return self.state
        mu = np.mean(self.buf)
        sigma = np.std(self.buf) + 1e-8
        z = (pac - mu) / sigma
        if z < -self.z_thresh:
            desired = StimAction.STIMULATE
        elif z > self.z_thresh:
            desired = StimAction.REST
        else:
            self.t_in_state += 1
            return self.state
        if desired != self.state and self.t_in_state >= self.hold_time:
            self.state = desired
            self.t_in_state = 0
        else:
            self.t_in_state += 1
        return self.state


class PredictiveLookAheadControl:
    """Trend-based look-ahead with hysteresis."""
    name = "Predictive"

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
        if trend < -0.003:
            desired = StimAction.STIMULATE
        elif trend > 0.003:
            desired = StimAction.REST
        elif z < -self.z_thresh:
            desired = StimAction.STIMULATE
        elif z > self.z_thresh:
            desired = StimAction.REST
        if desired is None:
            desired = self.state
        if desired != self.state and self.t_in_state >= self.hold_time:
            self.state = desired
            self.t_in_state = 0
        else:
            self.t_in_state += 1
        return self.state


class OracleControl:
    """Perfect knowledge oracle."""
    name = "Oracle"

    def __init__(self, target: float = 0.2):
        self.target = target

    def reset(self):
        pass

    def step(self, pac: float) -> int:
        return StimAction.STIMULATE if pac < self.target else StimAction.REST


# ─────────────────────────────────────────────────────────────────────
# Simulation runner
# ─────────────────────────────────────────────────────────────────────

def run_trial(method, sim, duration_sec: int, seed: int | None = None) -> Dict:
    """Run one simulation trial."""
    if seed is not None:
        np.random.seed(seed)
    sim.reset()
    method.reset()

    pac_values, actions = [], []
    for _ in range(duration_sec):
        pac = sim.pac
        action = method.step(pac)
        sim.step(action)
        pac_values.append(pac)
        actions.append(action)

    pac_arr = np.array(pac_values)
    act_arr = np.array(actions)
    n_baseline = min(10, len(pac_arr))
    baseline = float(np.mean(pac_arr[:n_baseline]))
    mean_pac = float(np.mean(pac_arr))
    improvement = 100.0 * (mean_pac - baseline) / (baseline + 1e-8)
    stim_pct = 100.0 * float(np.mean(act_arr))
    efficiency = improvement / (stim_pct + 1e-8) if stim_pct > 0 else 0.0
    late_start = int(0.75 * len(pac_arr))
    late_pac = float(np.mean(pac_arr[late_start:]))

    return {
        "pac_mean": mean_pac,
        "pac_std": float(np.std(pac_arr)),
        "pac_improvement_pct": improvement,
        "stimulation_pct": stim_pct,
        "efficiency_ratio": efficiency,
        "late_session_pac": late_pac,
        "pac_trace": pac_arr.tolist(),
        "action_trace": act_arr.tolist(),
    }


def run_comparison(
    methods: list,
    sim_factory_original,
    sim_factory_tribe,
    n_trials: int,
    duration_sec: int,
    base_seed: int,
) -> Dict[str, Dict[str, List[Dict]]]:
    """Run methods on both simulation backends."""
    results = {"original": {}, "tribe_v2": {}}

    for backend_name, factory in [("original", sim_factory_original), ("tribe_v2", sim_factory_tribe)]:
        for method in methods:
            trials = []
            for trial in range(n_trials):
                seed = base_seed + trial
                sim = factory()
                res = run_trial(method, sim, duration_sec, seed=seed)
                trials.append(res)
            results[backend_name][method.name] = trials
            mean_pac = np.mean([t["pac_mean"] for t in trials])
            mean_eff = np.mean([t["efficiency_ratio"] for t in trials])
            print(f"  [{backend_name:>8s}] {method.name:<18s}: PAC={mean_pac:.4f}, eff={mean_eff:.3f}")

    return results


def run_disease_sweep(
    n_trials: int,
    duration_sec: int,
    base_seed: int,
) -> Dict[str, Dict[str, List[Dict]]]:
    """Run Predictive controller across all disease severities."""
    method = PredictiveLookAheadControl()
    results = {}

    for severity in ALZHEIMER_PROFILES:
        trials = []
        for trial in range(n_trials):
            seed = base_seed + trial
            sim = create_simulator(
                disease_severity=severity,
                use_tribe_v2=False,
                subject_seed=seed,
            )
            res = run_trial(method, sim, duration_sec, seed=seed)
            trials.append(res)
        results[severity] = trials
        mean_pac = np.mean([t["pac_mean"] for t in trials])
        mean_late = np.mean([t["late_session_pac"] for t in trials])
        print(f"  {severity:>12s}: PAC={mean_pac:.4f}, late={mean_late:.4f}")

    return results


# ─────────────────────────────────────────────────────────────────────
# Plotting
# ─────────────────────────────────────────────────────────────────────

def plot_backend_comparison(results: Dict, output_dir: Path) -> None:
    """Plot original vs TRIBE V2-enhanced simulation comparison."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "Simulation Backend Comparison: Original vs TRIBE V2-Enhanced",
        fontsize=14, fontweight="bold",
    )

    backends = ["original", "tribe_v2"]
    backend_labels = ["Original (Exponential)", "TRIBE V2-Enhanced"]
    methods = list(results["original"].keys())
    colors = sns.color_palette("Set2", len(methods))

    # 1. PAC mean comparison
    ax = axes[0, 0]
    x = np.arange(len(methods))
    width = 0.35
    for i, (backend, label) in enumerate(zip(backends, backend_labels)):
        means = [np.mean([t["pac_mean"] for t in results[backend][m]]) for m in methods]
        stds = [np.std([t["pac_mean"] for t in results[backend][m]]) for m in methods]
        ax.bar(x + i * width, means, width, yerr=stds, label=label,
               color=colors[i] if i < len(colors) else "gray",
               capsize=3, edgecolor="black", linewidth=0.5)
    ax.set_ylabel("Mean PAC")
    ax.set_title("PAC by Strategy and Backend")
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(methods, rotation=15, ha="right", fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)

    # 2. Efficiency comparison
    ax = axes[0, 1]
    for i, (backend, label) in enumerate(zip(backends, backend_labels)):
        effs = [np.mean([t["efficiency_ratio"] for t in results[backend][m]]) for m in methods]
        ax.bar(x + i * width, effs, width, label=label,
               color=colors[i] if i < len(colors) else "gray",
               edgecolor="black", linewidth=0.5)
    ax.set_ylabel("Efficiency Ratio")
    ax.set_title("PAC Improvement per Unit Stimulation")
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(methods, rotation=15, ha="right", fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)

    # 3. PAC time series (last trial, Predictive method)
    ax = axes[1, 0]
    for i, (backend, label) in enumerate(zip(backends, backend_labels)):
        if "Predictive" in results[backend]:
            trace = results[backend]["Predictive"][-1]["pac_trace"]
            time_min = np.arange(len(trace)) / 60.0
            ax.plot(time_min, trace, label=label, alpha=0.8, linewidth=1.2)
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("PAC")
    ax.set_title("Predictive Controller: PAC Dynamics")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # 4. Stimulation percentage
    ax = axes[1, 1]
    for i, (backend, label) in enumerate(zip(backends, backend_labels)):
        stims = [np.mean([t["stimulation_pct"] for t in results[backend][m]]) for m in methods]
        ax.bar(x + i * width, stims, width, label=label,
               color=colors[i] if i < len(colors) else "gray",
               edgecolor="black", linewidth=0.5)
    ax.set_ylabel("Stimulation Time (%)")
    ax.set_title("Energy Efficiency")
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(methods, rotation=15, ha="right", fontsize=9)
    ax.set_ylim([0, 100])
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out_path = output_dir / "tribe_v2_backend_comparison.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"\nSaved: {out_path}")


def plot_disease_sweep(results: Dict, output_dir: Path) -> None:
    """Plot Alzheimer's disease severity sweep results."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(
        "TRIBE V2 Alzheimer's Disease Simulation: Predictive Controller",
        fontsize=14, fontweight="bold",
    )

    severities = list(results.keys())
    colors = sns.color_palette("YlOrRd", len(severities))

    # 1. PAC mean by severity
    ax = axes[0]
    means = [np.mean([t["pac_mean"] for t in results[s]]) for s in severities]
    stds = [np.std([t["pac_mean"] for t in results[s]]) for s in severities]
    bars = ax.bar(range(len(severities)), means, yerr=stds, color=colors,
                  capsize=4, edgecolor="black", linewidth=0.5)
    ax.set_xticks(range(len(severities)))
    ax.set_xticklabels(severities, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("Mean PAC")
    ax.set_title("PAC Response vs Disease Severity")
    ax.grid(axis="y", alpha=0.3)

    # 2. PAC time series by severity
    ax = axes[1]
    for i, severity in enumerate(severities):
        trace = results[severity][-1]["pac_trace"]
        time_min = np.arange(len(trace)) / 60.0
        ax.plot(time_min, trace, label=severity, color=colors[i],
                alpha=0.8, linewidth=1.2)
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("PAC")
    ax.set_title("PAC Dynamics by Disease Severity")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # 3. Efficiency by severity
    ax = axes[2]
    effs = [np.mean([t["efficiency_ratio"] for t in results[s]]) for s in severities]
    ax.bar(range(len(severities)), effs, color=colors,
           edgecolor="black", linewidth=0.5)
    ax.set_xticks(range(len(severities)))
    ax.set_xticklabels(severities, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("Efficiency Ratio")
    ax.set_title("Stimulation Efficiency vs Severity")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out_path = output_dir / "tribe_v2_alzheimer_sweep.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="TRIBE V2-enhanced closed-loop validation"
    )
    p.add_argument("--duration", default=360, type=int,
                   help="Simulation duration in seconds (default: 360)")
    p.add_argument("--n-trials", default=5, type=int,
                   help="Trials per method (default: 5)")
    p.add_argument("--seed", default=42, type=int)
    p.add_argument("--disease-sweep", action="store_true",
                   help="Run Alzheimer's disease severity sweep")
    p.add_argument("--output-dir", default="results/tribe_v2", type=str)
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

    # ── Backend Comparison ──
    print("=" * 70)
    print("  BACKEND COMPARISON: Original vs TRIBE V2-Enhanced")
    print("=" * 70)

    results = run_comparison(
        methods=methods,
        sim_factory_original=lambda: FatigueAwareSimulator(
            tau_rise=0.15, tau_decay=0.10,
            pac_max=0.3, pac_min=0.05, noise_std=0.02,
            fatigue_rate=0.008, recovery_rate=0.03, max_fatigue=0.7,
        ),
        sim_factory_tribe=lambda: create_simulator(
            disease_severity="healthy",
            use_tribe_v2=False,
            subject_seed=42,
        ),
        n_trials=args.n_trials,
        duration_sec=args.duration,
        base_seed=args.seed,
    )

    plot_backend_comparison(results, output_dir)

    # Print summary table
    print("\n" + "=" * 70)
    print("  SUMMARY: Mean PAC (Original vs TRIBE V2)")
    print("=" * 70)
    print(f"{'Method':<20s} {'Original':>10s} {'TRIBE V2':>10s} {'Delta':>8s}")
    print("-" * 50)
    for method_name in results["original"]:
        orig_pac = np.mean([t["pac_mean"] for t in results["original"][method_name]])
        tribe_pac = np.mean([t["pac_mean"] for t in results["tribe_v2"][method_name]])
        delta = tribe_pac - orig_pac
        print(f"{method_name:<20s} {orig_pac:>10.4f} {tribe_pac:>10.4f} {delta:>+8.4f}")

    # ── Disease Severity Sweep ──
    if args.disease_sweep:
        print("\n" + "=" * 70)
        print("  ALZHEIMER'S DISEASE SEVERITY SWEEP")
        print("=" * 70)

        disease_results = run_disease_sweep(
            n_trials=args.n_trials,
            duration_sec=args.duration,
            base_seed=args.seed,
        )

        plot_disease_sweep(disease_results, output_dir)

        # Statistical comparison: healthy vs each severity
        print("\nStatistical comparison (Predictive controller, healthy vs each):")
        print("-" * 60)
        healthy_pacs = [t["pac_mean"] for t in disease_results["healthy"]]
        for severity in ["mild", "moderate", "severe"]:
            sev_pacs = [t["pac_mean"] for t in disease_results[severity]]
            if len(healthy_pacs) >= 2 and len(sev_pacs) >= 2:
                t_stat, p_val = stats.ttest_ind(healthy_pacs, sev_pacs)
                d_healthy = np.mean(healthy_pacs)
                d_sev = np.mean(sev_pacs)
                reduction_pct = 100.0 * (d_healthy - d_sev) / d_healthy
                print(
                    f"  healthy vs {severity:>8s}: "
                    f"PAC {d_healthy:.4f} → {d_sev:.4f} "
                    f"({reduction_pct:+.1f}%), "
                    f"t={t_stat:.2f}, p={p_val:.4f}"
                )

    # ── Save all results ──
    output_data = {
        "config": {
            "duration_sec": args.duration,
            "n_trials": args.n_trials,
            "seed": args.seed,
        },
        "backend_comparison": {
            backend: {
                method: [
                    {k: v for k, v in t.items() if k not in ("pac_trace", "action_trace")}
                    for t in trials
                ]
                for method, trials in methods_dict.items()
            }
            for backend, methods_dict in results.items()
        },
    }
    if args.disease_sweep:
        output_data["disease_sweep"] = {
            severity: [
                {k: v for k, v in t.items() if k not in ("pac_trace", "action_trace")}
                for t in trials
            ]
            for severity, trials in disease_results.items()
        }

    out_path = output_dir / "tribe_v2_validation_results.json"
    out_path.write_text(json.dumps(output_data, indent=2))
    print(f"\nSaved results: {out_path}")
    print(f"Figures: {output_dir}/")


if __name__ == "__main__":
    main()
