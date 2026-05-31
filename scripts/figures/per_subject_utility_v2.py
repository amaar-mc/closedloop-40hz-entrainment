"""Publication-quality per-subject alignment scatter plot.
Data verified: all 35/35 subjects have TCN > Reactive alignment."""
from __future__ import annotations

import json
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
DATA = REPO / "results" / "metrics" / "tcn_validation_results.json"
OUTPUT = REPO / "results" / "figures" / "per_subject_utility.png"

# Load verified data
with open(DATA) as f:
    d = json.load(f)

reactive = d["per_subject"]["Reactive Threshold"]
tcn = d["per_subject"]["TCN Predictive"]

# Extract alignment scores by split
train_rx = [reactive[i]["alignment_score"] for i in range(24)]
train_tx = [tcn[i]["alignment_score"] for i in range(24)]
val_rx   = [reactive[i]["alignment_score"] for i in range(24, 29)]
val_tx   = [tcn[i]["alignment_score"] for i in range(24, 29)]
test_rx  = [reactive[i]["alignment_score"] for i in range(29, 35)]
test_tx  = [tcn[i]["alignment_score"] for i in range(29, 35)]

# Style
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 11,
    "axes.linewidth": 0.7,
    "xtick.direction": "in",
    "ytick.direction": "in",
})

# Colors
C_TRAIN = "#1B2A4A"   # navy
C_VAL   = "#D4943A"   # amber
C_TEST  = "#C05746"   # coral
C_TCN_ZONE  = "#D0ECF0"  # light teal
C_REACT_ZONE = "#FBE8C8"  # light amber

fig, ax = plt.subplots(figsize=(6, 6), dpi=300)

# Diagonal and shaded regions
diag = [0.30, 0.90]
ax.plot(diag, diag, ls="-", color="#AAAAAA", lw=0.8, zorder=1)
ax.fill_between(diag, diag, [0.90, 0.90],
                color=C_TCN_ZONE, alpha=0.35, zorder=0)
ax.fill_between(diag, [0.30, 0.30], diag,
                color=C_REACT_ZONE, alpha=0.25, zorder=0)

# Zone labels
ax.text(0.44, 0.82, "TCN better", fontsize=9.5, color="#1A6B5E",
        fontstyle="italic", alpha=0.8)
ax.text(0.72, 0.62, "Reactive better", fontsize=9.5, color="#B8860B",
        fontstyle="italic", alpha=0.6)

# Scatter — consistent marker size, clean edges
scatter_kw = dict(s=55, zorder=3, edgecolors="white", linewidths=0.6)

ax.scatter(train_rx, train_tx, marker="o", c=C_TRAIN,
           label=f"Train (n = {len(train_rx)})", **scatter_kw)
ax.scatter(val_rx, val_tx, marker="s", c=C_VAL,
           label=f"Val (n = {len(val_rx)})", **scatter_kw)
ax.scatter(test_rx, test_tx, marker="D", c=C_TEST,
           label=f"Test (n = {len(test_rx)})", **scatter_kw)

# Axes
ax.set_xlabel("Reactive Threshold Alignment", fontsize=12, labelpad=8)
ax.set_ylabel("TCN Predictive Alignment", fontsize=12, labelpad=8)
ax.set_xlim(0.43, 0.80)
ax.set_ylim(0.58, 0.90)
ax.xaxis.set_major_locator(mticker.MultipleLocator(0.05))
ax.yaxis.set_major_locator(mticker.MultipleLocator(0.05))
ax.set_aspect("equal")

# Grid
ax.grid(True, linewidth=0.2, color="#DDDDDD", zorder=0)
ax.set_axisbelow(True)

# Spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Title
ax.set_title("Per-Subject Alignment (35/35 favor TCN)",
             fontsize=13, pad=12)

# Legend
legend = ax.legend(loc="lower right", frameon=True, framealpha=0.95,
                   edgecolor="#CCCCCC", fontsize=9.5, handlelength=1.5,
                   borderpad=0.5)
legend.get_frame().set_linewidth(0.4)

plt.tight_layout(pad=1.0)
fig.savefig(OUTPUT, bbox_inches="tight", facecolor="white")
print(f"Saved: {OUTPUT}")
print(f"Size:  {OUTPUT.stat().st_size // 1024} KB")
