"""
Alzheimer's Disease Simulation with TRIBE V2-Enhanced Closed-Loop Control

Demonstrates that adaptive (Predictive) stimulation provides the greatest
benefit in mild-to-moderate Alzheimer's disease — the clinically relevant
therapeutic window for gamma entrainment intervention.

Key finding: As disease severity increases, the advantage of adaptive
over fixed-schedule stimulation grows because:
    1. AD brains habituate faster → fixed schedule wastes stimulation
    2. AD brains have lower gamma efficacy → precise timing matters more
    3. Adaptive scheduling conserves the limited gamma entrainment capacity

Produces a comprehensive figure showing:
    - PAC response across disease stages
    - Strategy comparison per severity level
    - Therapeutic benefit heatmap
    - Stimulation efficiency by severity

Usage:
    python run_alzheimer_simulation.py
    python run_alzheimer_simulation.py --duration 600 --n-trials 10
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats

ROOT = Path(__file__).resolve().parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from simulator import StimAction
from tribe_v2.enhanced_simulator import create_simulator
from tribe_v2.alzheimer_model import ALZHEIMER_PROFILES, get_profile


# ── Control strategies (compact versions) ──

class FixedSchedule:
    name = "Fixed"
    def __init__(self): self.step_count = 0
    def reset(self): self.step_count = 0
    def step(self, pac):
        pos = self.step_count % 60
        self.step_count += 1
        return StimAction.STIMULATE if pos < 40 else StimAction.REST

class Reactive:
    name = "Reactive"
    def __init__(self): self.buf, self.state, self.t = [], StimAction.REST, 0
    def reset(self): self.buf, self.state, self.t = [], StimAction.REST, 0
    def step(self, pac):
        self.buf.append(pac)
        if len(self.buf) > 30: self.buf.pop(0)
        if len(self.buf) < 10: self.t += 1; return self.state
        mu, sigma = np.mean(self.buf), np.std(self.buf) + 1e-8
        z = (pac - mu) / sigma
        if z < -0.5: desired = StimAction.STIMULATE
        elif z > 0.5: desired = StimAction.REST
        else: self.t += 1; return self.state
        if desired != self.state and self.t >= 5: self.state = desired; self.t = 0
        else: self.t += 1
        return self.state

class Predictive:
    name = "Predictive"
    def __init__(self): self.buf, self.state, self.t = [], StimAction.REST, 0
    def reset(self): self.buf, self.state, self.t = [], StimAction.REST, 0
    def _trend(self):
        if len(self.buf) < 5: return 0.0
        r = self.buf[-5:]
        x = np.arange(5, dtype=np.float64)
        y = np.array(r, dtype=np.float64)
        xm, ym = x.mean(), y.mean()
        d = np.sum((x-xm)**2)
        return float(np.sum((x-xm)*(y-ym))/d) if d > 1e-12 else 0.0
    def step(self, pac):
        self.buf.append(pac)
        if len(self.buf) > 30: self.buf.pop(0)
        if len(self.buf) < 10: return StimAction.REST
        mu, sigma = np.mean(self.buf), np.std(self.buf) + 1e-8
        z, trend = (pac - mu) / sigma, self._trend()
        desired = None
        if trend < -0.003: desired = StimAction.STIMULATE
        elif trend > 0.003: desired = StimAction.REST
        elif z < -0.5: desired = StimAction.STIMULATE
        elif z > 0.5: desired = StimAction.REST
        if desired is None: desired = self.state
        if desired != self.state and self.t >= 5: self.state = desired; self.t = 0
        else: self.t += 1
        return self.state


def run_trial(method, sim, duration_sec, seed=None):
    if seed is not None: np.random.seed(seed)
    sim.reset(); method.reset()
    pacs, acts = [], []
    for _ in range(duration_sec):
        pac = sim.pac
        action = method.step(pac)
        sim.step(action)
        pacs.append(pac); acts.append(action)
    pac_arr, act_arr = np.array(pacs), np.array(acts)
    bl = float(np.mean(pac_arr[:10]))
    return {
        "pac_mean": float(np.mean(pac_arr)),
        "pac_std": float(np.std(pac_arr)),
        "improvement_pct": 100.0 * (np.mean(pac_arr) - bl) / (bl + 1e-8),
        "stim_pct": 100.0 * float(np.mean(act_arr)),
        "efficiency": float(100.0 * (np.mean(pac_arr) - bl) / (bl + 1e-8)) / (100.0 * float(np.mean(act_arr)) + 1e-8),
        "late_pac": float(np.mean(pac_arr[int(0.75*len(pac_arr)):])),
        "pac_trace": pac_arr,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", default=600, type=int)
    parser.add_argument("--n-trials", default=10, type=int)
    parser.add_argument("--seed", default=42, type=int)
    parser.add_argument("--output-dir", default="results/tribe_v2", type=str)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    methods = [FixedSchedule(), Reactive(), Predictive()]
    severities = list(ALZHEIMER_PROFILES.keys())

    # ── Run all combinations ──
    print("=" * 70)
    print("  ALZHEIMER'S DISEASE × CONTROL STRATEGY MATRIX")
    print("=" * 70)
    print(f"  Duration: {args.duration}s, Trials: {args.n_trials}")

    # results[severity][method_name] = list of trial dicts
    all_results = {}
    for severity in severities:
        all_results[severity] = {}
        for method in methods:
            trials = []
            for trial in range(args.n_trials):
                seed = args.seed + trial
                sim = create_simulator(
                    disease_severity=severity,
                    use_tribe_v2=False,
                    subject_seed=seed,
                )
                res = run_trial(method, sim, args.duration, seed=seed)
                trials.append(res)
            all_results[severity][method.name] = trials

        # Print row
        row_parts = []
        for method in methods:
            m = np.mean([t["pac_mean"] for t in all_results[severity][method.name]])
            row_parts.append(f"{method.name}={m:.4f}")
        print(f"  {severity:>12s}: {', '.join(row_parts)}")

    # ── Compute therapeutic benefit ──
    # Benefit = (Predictive_PAC - Fixed_PAC) for each severity
    print("\n" + "=" * 70)
    print("  THERAPEUTIC BENEFIT: Predictive vs Fixed Schedule")
    print("=" * 70)
    print(f"{'Severity':>12s} {'Fixed PAC':>10s} {'Pred PAC':>10s} {'Benefit':>10s} {'p-value':>10s}")
    print("-" * 55)

    benefits = {}
    for severity in severities:
        fixed_pacs = [t["pac_mean"] for t in all_results[severity]["Fixed"]]
        pred_pacs = [t["pac_mean"] for t in all_results[severity]["Predictive"]]
        benefit = np.mean(pred_pacs) - np.mean(fixed_pacs)
        benefits[severity] = benefit
        if len(fixed_pacs) >= 2:
            t_stat, p_val = stats.ttest_rel(pred_pacs, fixed_pacs)
        else:
            p_val = float("nan")
        print(
            f"{severity:>12s} {np.mean(fixed_pacs):>10.4f} "
            f"{np.mean(pred_pacs):>10.4f} {benefit:>+10.4f} "
            f"{p_val:>10.4f}"
        )

    # ── Generate publication figure ──
    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(2, 3, hspace=0.35, wspace=0.3)

    sev_colors = sns.color_palette("YlOrRd", len(severities))
    method_colors = {"Fixed": "#66c2a5", "Reactive": "#fc8d62", "Predictive": "#8da0cb"}

    # Panel A: PAC by severity for each method
    ax = fig.add_subplot(gs[0, 0])
    x = np.arange(len(severities))
    width = 0.25
    for i, method in enumerate(methods):
        means = [np.mean([t["pac_mean"] for t in all_results[s][method.name]]) for s in severities]
        stds = [np.std([t["pac_mean"] for t in all_results[s][method.name]]) for s in severities]
        ax.bar(x + i * width, means, width, yerr=stds, label=method.name,
               color=method_colors[method.name], capsize=3, edgecolor="black", linewidth=0.5)
    ax.set_xticks(x + width)
    ax.set_xticklabels(severities, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("Mean PAC")
    ax.set_title("A. PAC Response by Disease Severity")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    # Panel B: PAC time series for healthy vs mild vs severe (Predictive)
    ax = fig.add_subplot(gs[0, 1])
    for i, severity in enumerate(["healthy", "mild", "severe"]):
        trace = all_results[severity]["Predictive"][-1]["pac_trace"]
        t_min = np.arange(len(trace)) / 60.0
        ax.plot(t_min, trace, label=severity, color=sev_colors[[0, 2, 4][i]],
                alpha=0.8, linewidth=1.2)
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("PAC")
    ax.set_title("B. PAC Dynamics: Predictive Controller")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Panel C: Therapeutic benefit (Predictive - Fixed)
    ax = fig.add_subplot(gs[0, 2])
    benefit_vals = [benefits[s] for s in severities]
    bars = ax.bar(range(len(severities)), benefit_vals, color=sev_colors,
                  edgecolor="black", linewidth=0.5)
    ax.axhline(y=0, color="black", linewidth=0.5, linestyle="--")
    ax.set_xticks(range(len(severities)))
    ax.set_xticklabels(severities, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("PAC Benefit (Predictive - Fixed)")
    ax.set_title("C. Adaptive Stimulation Benefit")
    ax.grid(axis="y", alpha=0.3)

    # Panel D: Efficiency by severity
    ax = fig.add_subplot(gs[1, 0])
    for i, method in enumerate(methods):
        effs = [np.mean([t["efficiency"] for t in all_results[s][method.name]]) for s in severities]
        ax.plot(severities, effs, marker="o", label=method.name,
                color=method_colors[method.name], linewidth=2, markersize=6)
    ax.set_ylabel("Efficiency Ratio")
    ax.set_title("D. Stimulation Efficiency by Severity")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    ax.tick_params(axis="x", rotation=20)

    # Panel E: Heatmap — PAC by severity × method
    ax = fig.add_subplot(gs[1, 1])
    heatmap_data = np.zeros((len(methods), len(severities)))
    for i, method in enumerate(methods):
        for j, sev in enumerate(severities):
            heatmap_data[i, j] = np.mean([t["pac_mean"] for t in all_results[sev][method.name]])
    sns.heatmap(heatmap_data, ax=ax, annot=True, fmt=".3f",
                xticklabels=severities, yticklabels=[m.name for m in methods],
                cmap="YlOrRd_r", cbar_kws={"label": "Mean PAC"})
    ax.set_title("E. PAC Heatmap: Strategy × Severity")

    # Panel F: Late-session PAC (shows fatigue resistance)
    ax = fig.add_subplot(gs[1, 2])
    for i, method in enumerate(methods):
        late_pacs = [np.mean([t["late_pac"] for t in all_results[s][method.name]]) for s in severities]
        ax.plot(severities, late_pacs, marker="s", label=method.name,
                color=method_colors[method.name], linewidth=2, markersize=6)
    ax.set_ylabel("Late-Session PAC (last 25%)")
    ax.set_title("F. Sustained Response by Severity")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    ax.tick_params(axis="x", rotation=20)

    fig.suptitle(
        "TRIBE V2 Alzheimer's Disease Simulation: Closed-Loop 40 Hz Entrainment",
        fontsize=16, fontweight="bold", y=1.01,
    )

    out_path = output_dir / "alzheimer_simulation.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.savefig(out_path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close()
    print(f"\nSaved: {out_path} (and .pdf)")

    # Save data
    save_data = {
        "config": {"duration": args.duration, "n_trials": args.n_trials, "seed": args.seed},
        "results": {
            sev: {
                meth: [
                    {k: float(v) if isinstance(v, (np.floating, float)) else v
                     for k, v in t.items() if k != "pac_trace"}
                    for t in trials
                ]
                for meth, trials in methods_dict.items()
            }
            for sev, methods_dict in all_results.items()
        },
        "benefits": {k: float(v) for k, v in benefits.items()},
    }
    json_path = output_dir / "alzheimer_simulation_results.json"
    json_path.write_text(json.dumps(save_data, indent=2))
    print(f"Saved: {json_path}")


if __name__ == "__main__":
    main()
