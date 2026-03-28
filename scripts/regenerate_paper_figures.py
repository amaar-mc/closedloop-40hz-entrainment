#!/usr/bin/env python3
"""
Regenerate ALL matplotlib data figures with unified publication style.
- Times New Roman font
- Muted professional color palette (navy, teal, slate, amber)
- Consistent sizing, line weights, and legend styling
- No neon/hot pink/bright green
"""

import json
import os
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "results" / "figures"
DATA = REPO / "results"

# ── Unified Publication Style ──────────────────────────────────────────────

# Color palette: muted, professional, colorblind-friendly
NAVY    = "#1B2A4A"
TEAL    = "#2A7F8E"
AMBER   = "#D4943A"
SLATE   = "#6B7B8D"
CORAL   = "#C05746"
SAGE    = "#5B8C5A"
LIGHT_TEAL = "#D0ECF0"
LIGHT_AMBER = "#FBE8C8"
LIGHT_SAGE = "#D4E8D4"

matplotlib.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.5,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "legend.fontsize": 9,
    "legend.framealpha": 0.9,
    "legend.edgecolor": "#CCCCCC",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "lines.linewidth": 2.0,
    "lines.markersize": 7,
})


def save(fig, name):
    for ext in ("png", "pdf"):
        p = OUT / f"{name}.{ext}"
        fig.savefig(p)
        print(f"  {p.name} ({p.stat().st_size // 1024} KB)")
    plt.close(fig)


# ── Figure 1: Horizon Sweep ───────────────────────────────────────────────

def fig_horizon_sweep():
    print("\n[1] Horizon Sweep")
    with open(REPO / "models" / "sweep_horizons_results.json") as f:
        records = json.load(f)

    h = [r["horizon"] for r in records]
    pers = [r["persistence_r2"] for r in records]
    ridge = [r["ridge_r2"] for r in records]
    tcn = [r["tcn_r2"] for r in records]

    fig, ax = plt.subplots(figsize=(7, 4.5))

    # Shaded operational zone
    ax.axvspan(4.5, 10.5, color=LIGHT_TEAL, alpha=0.4, zorder=0,
               label="Operationally useful (5\u201310 s)")

    # Zero line
    ax.axhline(0, color=SLATE, ls="--", lw=1, zorder=1, label="R\u00b2 = 0")

    # Lines
    ax.plot(h, pers, color=NAVY, marker="o", label="Persistence", zorder=3)
    ax.plot(h, ridge, color=AMBER, marker="s", label="Ridge Regression", zorder=3)
    ax.plot(h, tcn, color=TEAL, marker="^", ms=9, lw=2.5,
            label="Causal TCN (ours)", zorder=4)

    ax.set_xlabel("Prediction Horizon (seconds)")
    ax.set_ylabel("R\u00b2")
    ax.set_title("PAC Forecasting Performance vs. Prediction Horizon")
    ax.set_xticks(h)
    ax.set_xlim(0.5, 10.5)
    ax.legend(loc="upper right")
    fig.tight_layout()
    save(fig, "horizon_sweep")


# ── Figure 2: Controller Comparison Bar Chart ─────────────────────────────

def fig_controller_comparison():
    print("\n[2] Controller Comparison")
    with open(DATA / "tcn_validation_results.json") as f:
        d = json.load(f)

    controllers = ["Fixed", "PI", "Reactive", "TCN", "Hybrid", "Oracle"]
    keys = ["Fixed Schedule", "PI Controller", "Reactive Threshold",
            "TCN Predictive", "Hybrid TCN+Reactive", "Alignment Oracle"]

    # Summary values are already percentages (e.g., 45.0 not 0.45)
    alignment = [d["summary"][k]["alignment_score"] for k in keys]
    low_pac = [d["summary"][k]["low_epoch_stim_rate"] for k in keys]
    high_pac = [d["summary"][k]["high_epoch_rest_rate"] for k in keys]

    x = np.arange(len(controllers))
    w = 0.25

    fig, ax = plt.subplots(figsize=(9, 5.5))
    b1 = ax.bar(x - w, alignment, w, label="Alignment (%)", color=NAVY, zorder=3)
    b2 = ax.bar(x, low_pac, w, label="Low-PAC Stim Rate (%)", color=TEAL, zorder=3)
    b3 = ax.bar(x + w, high_pac, w, label="High-PAC Rest Rate (%)", color=AMBER, zorder=3)

    # Error bars from per-subject data
    metrics_map = {"alignment_score": b1, "low_epoch_stim_rate": b2, "high_epoch_rest_rate": b3}
    for metric_key, bars in metrics_map.items():
        for j, ctrl in enumerate(keys):
            subj_list = d["per_subject"][ctrl]
            vals = [s[metric_key] * 100 for s in subj_list]  # convert to %
            sem = np.std(vals) / np.sqrt(len(vals))
            ax.errorbar(bars[j].get_x() + bars[j].get_width()/2,
                       bars[j].get_height(), yerr=sem,
                       fmt="none", ecolor="#333", capsize=3, lw=1, zorder=5)

    # Significance brackets for TCN vs Reactive
    def bracket(x1, x2, y, text):
        ax.plot([x1, x1, x2, x2], [y, y+1.5, y+1.5, y], color="#333", lw=0.8)
        ax.text((x1+x2)/2, y+2, text, ha="center", va="bottom", fontsize=7.5)

    rx = x[2]  # Reactive
    tx = x[3]  # TCN
    bracket(rx - w, tx - w, 78, "g = 1.31  (alignment)")
    bracket(rx, tx, 90, "g = 4.47  (low-PAC targeting)")
    ax.text((rx + tx)/2, 97, "*** p < 0.001", ha="center", fontsize=8,
            fontweight="bold")

    ax.set_ylabel("Percentage (%)")
    ax.set_title("Controller Performance Comparison (N=35)")
    ax.set_xticks(x)
    ax.set_xticklabels(controllers)
    ax.set_ylim(0, 112)
    ax.legend(loc="upper left", framealpha=0.9)
    fig.tight_layout()
    save(fig, "controller_comparison")


# ── Figure 3: Per-Subject Utility Scatter ─────────────────────────────────

def fig_per_subject():
    print("\n[3] Per-Subject Utility")
    with open(DATA / "tcn_validation_results.json") as f:
        d = json.load(f)

    fig, ax = plt.subplots(figsize=(5.5, 5.5))

    # Diagonal
    ax.plot([0.3, 0.8], [0.3, 0.8], ls="--", color=SLATE, lw=1, zorder=1, label="y = x")
    ax.fill_between([0.3, 0.8], [0.3, 0.8], [0.8, 0.8],
                    color=LIGHT_TEAL, alpha=0.3, zorder=0)
    ax.fill_between([0.3, 0.8], [0.3, 0.3], [0.3, 0.8],
                    color=LIGHT_AMBER, alpha=0.2, zorder=0)

    # Annotations
    ax.text(0.38, 0.72, "TCN better", fontsize=9, color=TEAL, fontstyle="italic")
    ax.text(0.62, 0.38, "Reactive better", fontsize=9, color=AMBER, fontstyle="italic")

    # Get per-subject alignment for reactive vs TCN
    reactive_subs = d["per_subject"]["Reactive Threshold"]
    tcn_subs = d["per_subject"]["TCN Predictive"]

    # Match by subject ID
    for idx in range(len(reactive_subs)):
        rx = reactive_subs[idx]["alignment_score"]
        tx = tcn_subs[idx]["alignment_score"]
        if idx < 24:
            marker, color, label = "o", NAVY, "Train" if idx == 0 else None
        elif idx < 29:
            marker, color, label = "s", AMBER, "Val" if idx == 24 else None
        else:
            marker, color, label = "D", CORAL, "Test" if idx == 29 else None
        ax.scatter(rx, tx, marker=marker, c=color, s=50, zorder=3,
                  label=label, edgecolors="white", linewidths=0.5)

    ax.set_xlabel("Reactive Clinical Utility")
    ax.set_ylabel("TCN Predictive Clinical Utility")
    ax.set_title("Per-Subject Alignment (35/35 favor TCN)")
    ax.set_xlim(0.35, 0.75)
    ax.set_ylim(0.35, 0.75)
    ax.set_aspect("equal")
    ax.legend(loc="lower right", framealpha=0.9)
    fig.tight_layout()
    save(fig, "per_subject_utility")


# ── Figure 4: Timeline Example ────────────────────────────────────────────

def fig_timeline():
    print("\n[4] Timeline Example")
    with open(DATA / "tcn_validation_results.json") as f:
        d = json.load(f)

    # Use the first test subject's data if available
    # Reconstruct from per-subject summary
    # Since we don't have raw timeline data in JSON, we'll use the replay analysis
    replay_path = DATA / "perwindow_replay_analysis.json"
    if not replay_path.exists():
        print("  SKIP: perwindow_replay_analysis.json not found")
        return

    with open(replay_path) as f:
        replay = json.load(f)

    # Find a test subject
    subjects = list(replay.keys())
    if not subjects:
        print("  SKIP: no subjects in replay data")
        return

    # Pick sub-15 if available (test set subject used in original figure)
    subj_key = None
    for sk in subjects:
        if "15" in sk:
            subj_key = sk
            break
    if not subj_key:
        subj_key = subjects[0]

    sd = replay[subj_key]
    pac = np.array(sd["pac_values"])
    reactive_actions = np.array(sd["reactive_threshold_actions"])
    tcn_actions = np.array(sd["tcn_predictive_actions"])
    t = np.arange(len(pac)) * 2  # 2s windows

    # Determine PAC median for background shading
    pac_med = np.median(pac)

    fig, axes = plt.subplots(3, 1, figsize=(10, 5), height_ratios=[2.5, 1, 1],
                            sharex=True, gridspec_kw={"hspace": 0.08})

    # Top: PAC trace
    ax0 = axes[0]
    # Background: low-PAC regions (need stim) vs high-PAC (can rest)
    for i in range(len(pac)):
        color = LIGHT_AMBER if pac[i] < pac_med else LIGHT_TEAL
        ax0.axvspan(t[i], t[i]+2, color=color, alpha=0.3, zorder=0)
    ax0.plot(t, pac, color=NAVY, lw=1.2, zorder=2)
    ax0.axhline(pac_med, color=SLATE, ls=":", lw=0.8, zorder=1)
    ax0.set_ylabel("PAC (\u00d710\u207b\u2076)", fontsize=9)
    ax0.set_title(f"Controller Timeline \u2014 {subj_key} (test set)", fontsize=11)
    ax0.legend(["PAC", "Median"], loc="upper right", fontsize=8)

    # Middle: Reactive controller
    ax1 = axes[1]
    for i in range(len(reactive_actions)):
        if reactive_actions[i] == 1:
            ax1.axvspan(t[i], t[i]+2, color=TEAL, alpha=0.7, zorder=2)
        else:
            ax1.axvspan(t[i], t[i]+2, color="#E8E8E8", alpha=0.7, zorder=2)
        if pac[i] < pac_med:
            ax1.axvspan(t[i], t[i]+2, ymin=0, ymax=0.1, color=AMBER, zorder=3)
    ax1.set_ylabel("Reactive", fontsize=9)
    ax1.set_yticks([])

    # Bottom: TCN controller
    ax2 = axes[2]
    for i in range(len(tcn_actions)):
        if tcn_actions[i] == 1:
            ax2.axvspan(t[i], t[i]+2, color=AMBER, alpha=0.7, zorder=2)
        else:
            ax2.axvspan(t[i], t[i]+2, color="#E8E8E8", alpha=0.7, zorder=2)
        if pac[i] < pac_med:
            ax2.axvspan(t[i], t[i]+2, ymin=0, ymax=0.1, color=TEAL, zorder=3)
    ax2.set_ylabel("TCN", fontsize=9)
    ax2.set_yticks([])
    ax2.set_xlabel("Time (seconds)")

    # Legends
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=TEAL, alpha=0.7, label="Stimulate"),
                      Patch(facecolor="#E8E8E8", label="Rest"),
                      Patch(facecolor=AMBER, alpha=0.4, label="Low-PAC (need stim)")]
    ax1.legend(handles=legend_elements, loc="upper right", fontsize=7, ncol=3)
    ax2.legend(handles=legend_elements, loc="upper right", fontsize=7, ncol=3)

    fig.tight_layout()
    save(fig, "timeline_example")


# ── Main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    print("Regenerating figures with unified publication style...")

    fig_horizon_sweep()
    fig_controller_comparison()
    fig_per_subject()
    # fig_timeline()  # Requires raw per-window data not in JSON; keep existing figure
    print("\n[4] Timeline: SKIPPED (using existing figure)")
    print("  The timeline requires raw per-window data from run_tcn_validation.py")
    print("  Existing timeline_example.png is retained.")

    print("\nDone. All figures saved to results/figures/")
