"""Generate system architecture figure v7 with correct specs using matplotlib."""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[2] / "results" / "figures" / "ai_generated" / "system_architecture_v7.png"

# Colors
C_SIGNAL = "#B0C4DE"   # light steel blue
C_ML     = "#4682B4"   # steel blue
C_ML2    = "#2E6E8E"   # darker teal
C_CTRL   = "#DAA520"   # goldenrod
C_STIM   = "#CD5C5C"   # indian red
C_TEXT   = "#1A1A1A"
C_WHITE  = "#FFFFFF"
C_FEED   = "#888888"

BOXES = [
    {"label": "Patient\nEEG",         "sub": "7 frontal ch.\n250 Hz",          "color": C_SIGNAL, "text": C_TEXT},
    {"label": "Signal\nProcessing",   "sub": "BP 0.5\u201380 Hz\nNotch, CAR",  "color": C_SIGNAL, "text": C_TEXT},
    {"label": "EEGNet",               "sub": "1,457 params\nR\u00b2 = 0.287",  "color": C_ML,     "text": C_WHITE},
    {"label": "Feature\nEngineering", "sub": "73 \u2192 12 Features\n(PAC+Stim selected)", "color": "#3A9E8E", "text": C_WHITE},
    {"label": "Causal\nTCN",          "sub": "22,914 params\n5 s forecast",    "color": C_ML2,    "text": C_WHITE},
    {"label": "Adaptive\nController", "sub": "z-score \u00b10.5\n5 s hysteresis", "color": C_CTRL, "text": C_TEXT},
    {"label": "40 Hz Audio\nStimulation", "sub": "STIM / REST\n/ MAINTAIN",    "color": C_STIM,   "text": C_WHITE},
]

fig, ax = plt.subplots(figsize=(14, 4.2), dpi=200)
ax.set_xlim(-0.5, 15)
ax.set_ylim(-1.8, 3.2)
ax.axis("off")
fig.patch.set_facecolor("white")

# Title
ax.text(7.25, 2.85, "Closed-Loop 40 Hz Entrainment System Architecture",
        ha="center", va="center", fontsize=13, fontweight="bold", color=C_TEXT)

# Legend
legend_y = 2.45
for lx, lc, lt in [(3.5, C_SIGNAL, "Signal / Data"), (6.0, C_ML, "ML Model"), (8.8, C_CTRL, "Decision / Control")]:
    ax.add_patch(mpatches.FancyBboxPatch((lx, legend_y - 0.12), 0.35, 0.24,
                 boxstyle="round,pad=0.03", facecolor=lc, edgecolor="gray", linewidth=0.5))
    ax.text(lx + 0.5, legend_y, lt, ha="left", va="center", fontsize=7.5, color=C_TEXT)

# Draw boxes
bw, bh = 1.7, 1.4
x_start = 0.0
gap = 0.35
positions = []
for i, box in enumerate(BOXES):
    x = x_start + i * (bw + gap)
    y = 0.0
    positions.append((x, y))

    rect = mpatches.FancyBboxPatch((x, y), bw, bh,
           boxstyle="round,pad=0.08", facecolor=box["color"],
           edgecolor="#555555", linewidth=1.0)
    ax.add_patch(rect)

    ax.text(x + bw / 2, y + bh * 0.68, box["label"],
            ha="center", va="center", fontsize=9, fontweight="bold",
            color=box["text"], linespacing=1.1)

    ax.text(x + bw / 2, y + bh * 0.25, box["sub"],
            ha="center", va="center", fontsize=6.5,
            color=box["text"], linespacing=1.15, style="italic")

# Draw arrows between boxes
for i in range(len(BOXES) - 1):
    x1 = positions[i][0] + bw
    x2 = positions[i + 1][0]
    y_mid = bh / 2
    ax.annotate("", xy=(x2, y_mid), xytext=(x1, y_mid),
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.5))

# Feedback arrow (dashed curve from last box back to first)
x_last = positions[-1][0] + bw / 2
x_first = positions[0][0] + bw / 2
from matplotlib.patches import FancyArrowPatch
import matplotlib.path as mpath

# Create curved path below boxes
verts = [
    (x_last, 0.0),
    (x_last, -1.0),
    (x_first, -1.0),
    (x_first, 0.0),
]
codes = [mpath.Path.MOVETO, mpath.Path.CURVE4, mpath.Path.CURVE4, mpath.Path.CURVE4]
path = mpath.Path(verts, codes)
patch = FancyArrowPatch(path=path, arrowstyle="-|>", color=C_FEED,
                         lw=1.5, linestyle="dashed", mutation_scale=15)
ax.add_patch(patch)

ax.text((x_first + x_last) / 2, -1.2,
        "Closed-Loop Feedback (EEG monitors entrainment response)",
        ha="center", va="center", fontsize=7, color=C_FEED, style="italic")

plt.tight_layout(pad=0.3)
fig.savefig(OUTPUT, bbox_inches="tight", facecolor="white")
print(f"Saved: {OUTPUT}")
print(f"Size:  {OUTPUT.stat().st_size // 1024} KB")
