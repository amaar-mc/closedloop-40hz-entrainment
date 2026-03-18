#!/usr/bin/env python3
"""Generate publication-quality system architecture diagram v4."""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

matplotlib.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 12,
})

# Colors
NAVY = "#1B2A4A"
NAVY_LIGHT = "#2C3E5A"
TEAL = "#2A7F8E"
TEAL_DARK = "#1E6B78"
AMBER = "#D4943A"
CORAL = "#C05746"
WHITE = "#FFFFFF"
LIGHT_GRAY = "#F5F5F5"
DARK_GRAY = "#333333"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(PROJECT_ROOT, "results", "figures", "ai_generated", "system_architecture_v4.png")

fig, ax = plt.subplots(figsize=(14, 6))
ax.set_xlim(-0.5, 14.5)
ax.set_ylim(-2.5, 5.5)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("white")

# Stage definitions: x_center, color, title, subtitle_lines
stages = [
    (1.0,  NAVY,      "Patient\nEEG",          ["7 frontal channels", "250 Hz"]),
    (3.0,  NAVY_LIGHT,"Signal\nProcessing",    ["BP 0.5–80 Hz", "Notch 50 Hz, CAR"]),
    (5.0,  TEAL_DARK, "EEGNet",                ["1,457 params", "R² = 0.287"]),
    (7.0,  TEAL,      "Feature\nEngineering",  ["73 causal features", "(61+7+5)"]),
    (9.0,  TEAL,      "Causal\nTCN",           ["31K params", "20 s lookback", "5 s forecast"]),
    (11.0, AMBER,     "Adaptive\nController",  ["z-score ±0.5", "5 s hysteresis"]),
    (13.0, CORAL,     "40 Hz Audio\nStimulation", ["STIM / REST", "/ MAINTAIN"]),
]

box_w = 1.6
box_h = 2.6

for x, color, title, subs in stages:
    # Main box
    rect = FancyBboxPatch(
        (x - box_w/2, 1.0 - box_h/2),
        box_w, box_h,
        boxstyle="round,pad=0.12",
        facecolor=color, edgecolor="none",
        zorder=3
    )
    ax.add_patch(rect)

    # Title text (white, bold) - upper portion of box
    ax.text(x, 1.5, title, ha="center", va="center",
            fontsize=11, fontweight="bold", color=WHITE, zorder=4,
            linespacing=1.2)

    # Thin separator line
    ax.plot([x - box_w/2 + 0.15, x + box_w/2 - 0.15], [0.85, 0.85],
            color="#FFFFFF", alpha=0.3, lw=0.5, zorder=4)

    # Subtitle text (lighter, inside box below separator)
    sub_text = "\n".join(subs)
    ax.text(x, 0.35, sub_text, ha="center", va="center",
            fontsize=8.5, color="#D0D8E0", zorder=4,
            linespacing=1.4)

# Arrows between stages
for i in range(len(stages) - 1):
    x1 = stages[i][0] + box_w/2 + 0.05
    x2 = stages[i+1][0] - box_w/2 - 0.05
    ax.annotate("", xy=(x2, 1.0), xytext=(x1, 1.0),
                arrowprops=dict(arrowstyle="-|>", color=DARK_GRAY,
                               lw=1.8, mutation_scale=15),
                zorder=5)

# Feedback arrow (curved, from last stage back to first)
from matplotlib.patches import FancyArrowPatch
import matplotlib.path as mpath

# Draw curved feedback arrow underneath
feedback_y = -1.6
pts = [
    (13.0, 1.0 - box_h/2 - 0.1),   # start: bottom of last box
    (13.0, feedback_y),               # go down
    (7.0, feedback_y - 0.3),          # curve through center
    (1.0, feedback_y),                # go to first box
    (1.0, 1.0 - box_h/2 - 0.1),     # up to bottom of first box
]

# Use a smooth curve
from scipy.interpolate import make_interp_spline
xs = [p[0] for p in pts]
ys = [p[1] for p in pts]
t = np.linspace(0, 1, len(pts))
t_smooth = np.linspace(0, 1, 100)

try:
    spl_x = make_interp_spline(t, xs, k=3)
    spl_y = make_interp_spline(t, ys, k=3)
    xs_smooth = spl_x(t_smooth)
    ys_smooth = spl_y(t_smooth)
except:
    xs_smooth = np.interp(t_smooth, t, xs)
    ys_smooth = np.interp(t_smooth, t, ys)

ax.plot(xs_smooth, ys_smooth, color=DARK_GRAY, lw=1.5, ls="--", zorder=2)
# Arrowhead at the end
ax.annotate("", xy=(1.0, 1.0 - box_h/2 - 0.1),
            xytext=(1.3, feedback_y + 0.15),
            arrowprops=dict(arrowstyle="-|>", color=DARK_GRAY, lw=1.5),
            zorder=5)

# Feedback label
ax.text(7.0, feedback_y - 0.55, "Closed-Loop Feedback (EEG monitors entrainment response)",
        ha="center", va="top", fontsize=9.5, color=DARK_GRAY, fontstyle="italic")

# Title
ax.text(7.0, 4.2, "Closed-Loop 40 Hz Entrainment System Architecture",
        ha="center", va="center", fontsize=15, fontweight="bold", color=DARK_GRAY)

# Color legend
legend_y = 3.4
legend_items = [
    (3.5, NAVY, "Signal / Data"),
    (7.0, TEAL, "ML Model"),
    (10.5, AMBER, "Decision / Control"),
]
for lx, lcolor, llabel in legend_items:
    rect = FancyBboxPatch((lx - 0.25, legend_y - 0.15), 0.5, 0.3,
                          boxstyle="round,pad=0.05",
                          facecolor=lcolor, edgecolor="none", zorder=3)
    ax.add_patch(rect)
    ax.text(lx + 0.45, legend_y, llabel, ha="left", va="center",
            fontsize=9.5, color=DARK_GRAY)

# EEG wave icon in first box
wave_x = np.linspace(0.4, 1.6, 60)
wave_y = -0.05 + 0.12 * np.sin(wave_x * 15) * np.exp(-((wave_x - 1.0)**2) / 0.15)
ax.plot(wave_x, wave_y, color="#AABBCC", lw=1.2, zorder=4)

# Speaker icon in last box (drawn with matplotlib)
# Simple speaker shape using lines
spk_x, spk_y = 13.0, -0.05
ax.plot([spk_x-0.15, spk_x+0.05, spk_x+0.2, spk_x+0.2, spk_x+0.05, spk_x-0.15, spk_x-0.15],
        [spk_y-0.08, spk_y-0.08, spk_y-0.18, spk_y+0.18, spk_y+0.08, spk_y+0.08, spk_y-0.08],
        color="#D0D8E0", lw=1.5, zorder=4)
# Sound waves
for r in [0.25, 0.35]:
    theta = np.linspace(-0.5, 0.5, 20)
    ax.plot(spk_x + 0.2 + r * np.cos(theta), spk_y + r * np.sin(theta),
            color="#D0D8E0", lw=1.0, alpha=0.7, zorder=4)

fig.tight_layout(pad=0.5)
fig.savefig(OUTPUT, dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved: {OUTPUT}")
print(f"Size: {os.path.getsize(OUTPUT) // 1024} KB")
