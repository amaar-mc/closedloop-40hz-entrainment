#!/usr/bin/env python3
"""
Generate publication-quality figures from TCN validation results.

Produces four figures in results/figures/:
  1. controller_comparison.png  -- Grouped bar chart of key metrics
  2. pac_targeting_gap.png      -- PAC rest-stim gap per controller
  3. per_subject_utility.png    -- Scatter: Reactive vs TCN clinical utility
  4. stim_vs_alignment.png      -- Stim % vs Alignment trade-off
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OUT_DIR = "results/figures"
JSON_PATH = "results/metrics/tcn_validation_results.json"
FIG_SIZE = (8, 6)
DPI = 300
FONT_SIZE = 12

# Colorblind-friendly palette (IBM Design / Wong 2011)
COLORS = {
    "Fixed Schedule":      "#648FFF",   # blue
    "Reactive Threshold":  "#FE6100",   # orange
    "TCN Predictive":      "#DC267F",   # magenta
    "Hybrid TCN+Reactive": "#785EF0",   # violet
    "PI Controller":       "#FFB000",   # amber
    "Alignment Oracle":    "#22A884",   # teal
}

# Short display names for tight axis labels
SHORT = {
    "Fixed Schedule":      "Fixed",
    "Reactive Threshold":  "Reactive",
    "TCN Predictive":      "TCN",
    "Hybrid TCN+Reactive": "Hybrid",
    "PI Controller":       "PI",
    "Alignment Oracle":    "Oracle",
}

# Subject-level split boundaries (24 train / 5 val / 6 test)
TRAIN_N, VAL_N, TEST_N = 24, 5, 6

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _significance_stars(p):
    """Return significance stars based on p-value."""
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    return "n.s."


def _sem(values):
    """Standard error of the mean."""
    a = np.array(values, dtype=float)
    return np.std(a, ddof=1) / np.sqrt(len(a))


def _controller_order():
    """Canonical display order for controllers."""
    return [
        "Fixed Schedule",
        "PI Controller",
        "Reactive Threshold",
        "TCN Predictive",
        "Hybrid TCN+Reactive",
        "Alignment Oracle",
    ]


# ---------------------------------------------------------------------------
# Figure 1 -- Controller Comparison Bar Chart
# ---------------------------------------------------------------------------

def fig_controller_comparison(data):
    """Grouped bar chart: Alignment, Low-PAC Stim Rate, High-PAC Rest Rate."""
    controllers = _controller_order()
    metrics = ["alignment_score", "low_epoch_stim_rate", "high_epoch_rest_rate"]
    metric_labels = ["Alignment Score (%)", "Low-PAC Stim Rate (%)", "High-PAC Rest Rate (%)"]

    # Gather means and SEMs from per-subject data
    means = {m: [] for m in metrics}
    sems = {m: [] for m in metrics}
    for ctrl in controllers:
        subjects = data["per_subject"][ctrl]
        for m in metrics:
            vals = [s[m] * 100 for s in subjects]   # stored as fractions
            means[m].append(np.mean(vals))
            sems[m].append(_sem(vals))

    # TCN vs Reactive stats
    tcn_vs_reactive = data["comparisons"]["TCN_Predictive_vs_Reactive_Threshold"]["metrics"]

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    n_ctrl = len(controllers)
    n_met = len(metrics)
    x = np.arange(n_ctrl)
    bar_w = 0.22
    offsets = np.array([-bar_w, 0, bar_w])

    metric_colors = ["#648FFF", "#DC267F", "#22A884"]

    for j, m in enumerate(metrics):
        bars = ax.bar(
            x + offsets[j], means[m], bar_w,
            yerr=sems[m], capsize=3, color=metric_colors[j],
            edgecolor="white", linewidth=0.5, label=metric_labels[j],
            error_kw=dict(lw=1, capthick=1),
        )

    # Significance annotations for TCN (index=3) vs Reactive (index=2)
    tcn_idx = controllers.index("TCN Predictive")
    react_idx = controllers.index("Reactive Threshold")
    metric_keys_in_comparison = {
        "alignment_score": "alignment_score",
        "low_epoch_stim_rate": "low_epoch_stim_rate",
        "high_epoch_rest_rate": "high_epoch_rest_rate",
    }

    y_max = max(max(means[m]) + max(sems[m]) for m in metrics)
    annot_y = y_max + 3

    for j, m in enumerate(metrics):
        comp = tcn_vs_reactive[metric_keys_in_comparison[m]]
        p = comp["wilcoxon_p"]
        g = comp["hedges_g"]
        stars = _significance_stars(p)

        # Draw bracket between Reactive and TCN bars for this metric
        x_left = react_idx + offsets[j]
        x_right = tcn_idx + offsets[j]
        bracket_y = annot_y + j * 5

        ax.plot([x_left, x_left, x_right, x_right],
                [bracket_y - 1, bracket_y, bracket_y, bracket_y - 1],
                lw=1, color="0.3")
        ax.text(
            (x_left + x_right) / 2, bracket_y + 0.3,
            f"{stars}\ng = {g:.2f}",
            ha="center", va="bottom", fontsize=8, color="0.2", linespacing=1.1,
        )

    ax.set_xticks(x)
    ax.set_xticklabels([SHORT[c] for c in controllers], fontsize=FONT_SIZE - 1)
    ax.set_ylabel("Percentage (%)", fontsize=FONT_SIZE)
    ax.set_title("Controller Performance Comparison", fontsize=FONT_SIZE + 2, fontweight="bold", pad=12)
    ax.legend(fontsize=FONT_SIZE - 2, loc="upper left", frameon=False)
    ax.set_ylim(0, annot_y + n_met * 5 + 8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

    fig.tight_layout()
    for ext in ("png", "pdf"):
        path = os.path.join(OUT_DIR, f"controller_comparison.{ext}")
        fig.savefig(path, dpi=DPI, bbox_inches="tight")
        print(f"  Saved {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 2 -- PAC Targeting Gap
# ---------------------------------------------------------------------------

def fig_pac_targeting_gap(data):
    """Bar chart of (mean PAC during rest - mean PAC during stim) per controller."""
    controllers = _controller_order()

    gaps_mean = []
    gaps_sem = []
    for ctrl in controllers:
        subjects = data["per_subject"][ctrl]
        gaps = [s["pac_stim_rest_gap"] * 1e6 for s in subjects]  # convert to micro-units for readability
        gaps_mean.append(np.mean(gaps))
        gaps_sem.append(_sem(gaps))

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    x = np.arange(len(controllers))
    colors = [COLORS[c] for c in controllers]

    bars = ax.bar(
        x, gaps_mean, 0.6,
        yerr=gaps_sem, capsize=4,
        color=colors, edgecolor="white", linewidth=0.5,
        error_kw=dict(lw=1.2, capthick=1.2),
    )

    ax.axhline(0, color="0.5", lw=0.8, ls="--", zorder=0)
    ax.set_xticks(x)
    ax.set_xticklabels([SHORT[c] for c in controllers], fontsize=FONT_SIZE - 1)
    ax.set_ylabel(r"PAC Gap (rest $-$ stim)  [$\times 10^{-6}$]", fontsize=FONT_SIZE)
    ax.set_title("PAC Targeting Gap by Controller", fontsize=FONT_SIZE + 2, fontweight="bold", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

    # Annotate Hedges' g for TCN vs Reactive
    comp = data["comparisons"]["TCN_Predictive_vs_Reactive_Threshold"]["metrics"]["pac_stim_rest_gap"]
    g = comp["hedges_g"]
    p = comp["wilcoxon_p"]
    stars = _significance_stars(p)
    tcn_idx = controllers.index("TCN Predictive")
    react_idx = controllers.index("Reactive Threshold")
    y_top = max(gaps_mean) + max(gaps_sem) + 2
    ax.plot(
        [react_idx, react_idx, tcn_idx, tcn_idx],
        [y_top - 0.5, y_top, y_top, y_top - 0.5],
        lw=1, color="0.3",
    )
    ax.text(
        (react_idx + tcn_idx) / 2, y_top + 0.3,
        f"{stars}  g = {g:.2f}",
        ha="center", va="bottom", fontsize=10, color="0.2",
    )

    fig.tight_layout()
    for ext in ("png", "pdf"):
        path = os.path.join(OUT_DIR, f"pac_targeting_gap.{ext}")
        fig.savefig(path, dpi=DPI, bbox_inches="tight")
        print(f"  Saved {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3 -- Per-Subject Utility Scatter
# ---------------------------------------------------------------------------

def fig_per_subject_utility(data):
    """Scatter: Reactive utility (x) vs TCN utility (y), colored by split."""
    reactive_subjects = data["per_subject"]["Reactive Threshold"]
    tcn_subjects = data["per_subject"]["TCN Predictive"]

    # Build lookup by subject id
    react_by_sub = {s["subject"]: s["clinical_utility"] for s in reactive_subjects}
    tcn_by_sub = {s["subject"]: s["clinical_utility"] for s in tcn_subjects}

    # Assign splits based on ordering (24 train / 5 val / 6 test)
    all_subjects = [s["subject"] for s in tcn_subjects]
    train_subs = set(all_subjects[:TRAIN_N])
    val_subs = set(all_subjects[TRAIN_N:TRAIN_N + VAL_N])
    test_subs = set(all_subjects[TRAIN_N + VAL_N:])

    split_colors = {"Train": "#648FFF", "Val": "#FFB000", "Test": "#DC267F"}
    split_markers = {"Train": "o", "Val": "s", "Test": "D"}

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    # Diagonal y=x
    lims = [0.35, 0.75]
    ax.plot(lims, lims, ls="--", lw=1.2, color="0.55", zorder=0, label="y = x")
    ax.fill_between(lims, lims, [lims[1], lims[1]], alpha=0.06, color="#DC267F", zorder=0)
    ax.fill_between(lims, [lims[0], lims[0]], lims, alpha=0.06, color="#648FFF", zorder=0)

    # Text annotations for regions
    ax.text(0.42, 0.70, "TCN better", fontsize=10, color="#DC267F", alpha=0.6, style="italic")
    ax.text(0.60, 0.42, "Reactive better", fontsize=10, color="#648FFF", alpha=0.6, style="italic")

    n_above = 0
    for sub in all_subjects:
        if sub in train_subs:
            split = "Train"
        elif sub in val_subs:
            split = "Val"
        else:
            split = "Test"
        rx = react_by_sub[sub]
        ty = tcn_by_sub[sub]
        if ty > rx:
            n_above += 1
        ax.scatter(
            rx, ty, c=split_colors[split], marker=split_markers[split],
            s=60, edgecolors="white", linewidths=0.5, zorder=3,
            label=split,
        )

    # Deduplicate legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), fontsize=FONT_SIZE - 2,
              loc="lower right", frameon=True, framealpha=0.9, edgecolor="0.8")

    ax.set_xlabel("Reactive Clinical Utility", fontsize=FONT_SIZE)
    ax.set_ylabel("TCN Predictive Clinical Utility", fontsize=FONT_SIZE)
    ax.set_title(
        f"Per-Subject Clinical Utility  ({n_above}/{len(all_subjects)} subjects favour TCN)",
        fontsize=FONT_SIZE + 1, fontweight="bold", pad=12,
    )
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_aspect("equal")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

    fig.tight_layout()
    for ext in ("png", "pdf"):
        path = os.path.join(OUT_DIR, f"per_subject_utility.{ext}")
        fig.savefig(path, dpi=DPI, bbox_inches="tight")
        print(f"  Saved {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 4 -- Stimulation Rate vs Alignment Trade-off
# ---------------------------------------------------------------------------

def fig_stim_vs_alignment(data):
    """Labeled scatter: x = Stim %, y = Alignment %, one point per controller."""
    controllers = _controller_order()
    summary = data["summary"]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    xs, ys = [], []
    for ctrl in controllers:
        s = summary[ctrl]
        x = s["stim_pct"]
        y = s["alignment_score"]
        xs.append(x)
        ys.append(y)
        ax.scatter(
            x, y,
            c=COLORS[ctrl], s=180, edgecolors="white", linewidths=1.2, zorder=3,
        )

    # Label each point, with manual nudge to avoid overlap
    nudges = {
        "Fixed Schedule":      (8, -2),
        "PI Controller":       (8, 2),
        "Reactive Threshold":  (8, 2),
        "TCN Predictive":      (8, -4),
        "Hybrid TCN+Reactive": (-10, 4),
        "Alignment Oracle":    (8, -5),
    }
    for ctrl in controllers:
        s = summary[ctrl]
        dx, dy = nudges.get(ctrl, (2, 2))
        ax.annotate(
            SHORT[ctrl],
            (s["stim_pct"], s["alignment_score"]),
            xytext=(dx, dy), textcoords="offset points",
            fontsize=FONT_SIZE - 1, fontweight="bold", color=COLORS[ctrl],
        )

    # Draw Pareto frontier (upper-left is better: high alignment, low stim)
    # Sort by stim_pct ascending, keep Pareto-optimal
    pairs = sorted(zip(xs, ys, controllers), key=lambda t: t[0])
    pareto_x, pareto_y = [], []
    best_align = -1
    for px, py, _ in pairs:
        if py > best_align:
            pareto_x.append(px)
            pareto_y.append(py)
            best_align = py
    if len(pareto_x) > 1:
        ax.plot(pareto_x, pareto_y, ls="--", lw=1.2, color="0.6", zorder=1, alpha=0.7)
        ax.text(
            pareto_x[-1] + 1, pareto_y[-1] - 2,
            "Pareto frontier", fontsize=9, color="0.5", style="italic",
        )

    # Ideal corner annotation
    ax.annotate(
        "Ideal\n(low stim, high align)",
        xy=(15, 95), fontsize=9, color="0.45", ha="center", style="italic",
    )

    ax.set_xlabel("Stimulation Rate (%)", fontsize=FONT_SIZE)
    ax.set_ylabel("Alignment Score (%)", fontsize=FONT_SIZE)
    ax.set_title("Stimulation Efficiency vs Alignment Trade-off",
                  fontsize=FONT_SIZE + 2, fontweight="bold", pad=12)
    ax.set_xlim(10, 75)
    ax.set_ylim(35, 108)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

    fig.tight_layout()
    for ext in ("png", "pdf"):
        path = os.path.join(OUT_DIR, f"stim_vs_alignment.{ext}")
        fig.savefig(path, dpi=DPI, bbox_inches="tight")
        print(f"  Saved {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update({
        "font.size": FONT_SIZE,
        "axes.labelsize": FONT_SIZE,
        "axes.titlesize": FONT_SIZE + 2,
        "xtick.labelsize": FONT_SIZE - 1,
        "ytick.labelsize": FONT_SIZE - 1,
        "legend.fontsize": FONT_SIZE - 2,
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        "savefig.bbox": "tight",
        "font.family": "sans-serif",
    })

    os.makedirs(OUT_DIR, exist_ok=True)

    with open(JSON_PATH) as f:
        data = json.load(f)

    print(f"Loaded validation results: {data['n_subjects']} subjects\n")

    print("[1/4] Controller comparison bar chart ...")
    fig_controller_comparison(data)

    print("[2/4] PAC targeting gap ...")
    fig_pac_targeting_gap(data)

    print("[3/4] Per-subject utility scatter ...")
    fig_per_subject_utility(data)

    print("[4/4] Stimulation vs alignment trade-off ...")
    fig_stim_vs_alignment(data)

    print("\nAll figures saved to", OUT_DIR)


if __name__ == "__main__":
    main()
