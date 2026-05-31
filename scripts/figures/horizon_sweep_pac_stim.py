"""Publication-quality horizon sweep figure — PAC+Stim TCN results.
Data verified against experimental/results/horizon_sweep_pac_stim.json."""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

OUTPUT = REPO / "results" / "figures" / "horizon_sweep_pac_stim.png"

# Verified data (matches table AND JSON exactly)
horizons = [1, 3, 5, 8, 10]
persist  = [0.726, 0.178, 0.104, -0.007, -0.081]
tcn_7ch  = [0.725, 0.607, 0.577,  0.370,  0.669]
tcn_4ch  = [0.642, 0.391, 0.398,  0.419,  0.387]

# Style
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 11,
    "axes.linewidth": 0.7,
    "xtick.direction": "in",
    "ytick.direction": "in",
})

fig, ax = plt.subplots(figsize=(8, 4.8), dpi=300)

# Colors
C_PERSIST = "#2C3E50"
C_TCN7    = "#0E7C6B"
C_TCN4    = "#C76B3A"

# ── Shaded regions ──
# Left: persistence-competitive zone (1s)
ax.axvspan(0.4, 2.0, alpha=0.08, color="#FFD6A5", zorder=0)
ax.text(1.0, -0.22, "Persistence\ncompetitive",
        ha="center", va="center", fontsize=7.5, color="#8B6914",
        fontstyle="italic", alpha=0.8)

# Right: operationally useful zone (3-10s)
ax.axvspan(2.0, 10.6, alpha=0.08, color="#A8DADC", zorder=0)
ax.text(5.5, 0.83, "TCN advantage zone (3\u201310 s)",
        ha="center", va="center", fontsize=8.5, color="#1A6B5E",
        fontstyle="italic")

# Zero reference
ax.axhline(y=0, color="#BBBBBB", linewidth=0.5, zorder=1)

# ── Lines ──
ax.plot(horizons, persist, color=C_PERSIST, linewidth=2.0,
        marker="o", markersize=5, markerfacecolor="white",
        markeredgewidth=1.4, markeredgecolor=C_PERSIST,
        label="Persistence baseline", zorder=3)

ax.plot(horizons, tcn_7ch, color=C_TCN7, linewidth=2.5,
        marker="o", markersize=5.5, markerfacecolor=C_TCN7,
        markeredgewidth=0,
        label="PAC+Stim TCN  (7-channel)", zorder=4)

ax.plot(horizons, tcn_4ch, color=C_TCN4, linewidth=1.8,
        marker="o", markersize=4.5, markerfacecolor="white",
        markeredgewidth=1.4, markeredgecolor=C_TCN4,
        linestyle="--",
        label="PAC+Stim TCN  (4-channel)", zorder=3)

# ── Margin annotation at 5 s ──
ax.annotate("",
            xy=(5.15, 0.577), xytext=(5.15, 0.104),
            arrowprops=dict(arrowstyle="<->", color="#555555",
                            lw=1.0, shrinkA=3, shrinkB=3))
ax.text(5.55, 0.34, "\u0394 = +0.473",
        fontsize=8.5, color="#444444", va="center")

# ── Axes ──
ax.set_xlabel("Prediction Horizon (seconds)", fontsize=12, labelpad=8)
ax.set_ylabel("Test R\u00b2", fontsize=12, labelpad=8)
ax.set_xticks(horizons)
ax.set_xticklabels(["1", "3", "5", "8", "10"])
ax.set_xlim(0.4, 10.6)
ax.set_ylim(-0.32, 0.95)
ax.yaxis.set_major_locator(mticker.MultipleLocator(0.2))

# Grid — y only, subtle
ax.grid(True, axis="y", linewidth=0.25, color="#DDDDDD", zorder=0)
ax.set_axisbelow(True)

# Spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Legend
legend = ax.legend(loc="upper right", frameon=True, framealpha=0.95,
                   edgecolor="#CCCCCC", fontsize=9, handlelength=2.5,
                   borderpad=0.6)
legend.get_frame().set_linewidth(0.4)

plt.tight_layout(pad=1.0)
fig.savefig(OUTPUT, bbox_inches="tight", facecolor="white")
print(f"Saved: {OUTPUT}")
print(f"Size:  {OUTPUT.stat().st_size // 1024} KB")
