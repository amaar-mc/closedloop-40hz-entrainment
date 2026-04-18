#!/usr/bin/env python3
"""Generate publication-quality system architecture diagram v5.
Redesigned for readability: lighter box fills, dark text, clear borders."""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

matplotlib.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 12,
})

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(PROJECT_ROOT, "results", "figures", "ai_generated", "system_architecture_v5.png")

# ── Color scheme: light fills with dark borders for readability ──
# Category colors (border/accent) and their light fills
BLUE_BORDER  = "#1B2A4A"
BLUE_FILL    = "#D6DEE8"
TEAL_BORDER  = "#1A6B6D"
TEAL_FILL    = "#CCE5E6"
AMBER_BORDER = "#B07A20"
AMBER_FILL   = "#FAE8C8"
CORAL_BORDER = "#A04030"
CORAL_FILL   = "#F5D0CA"
TEXT_DARK    = "#1A1A1A"
TEXT_MID     = "#444444"
ARROW_COLOR  = "#555555"

fig, ax = plt.subplots(figsize=(15, 5.5))
ax.set_xlim(-0.3, 14.8)
ax.set_ylim(-2.2, 4.8)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("white")

# ── Stage definitions ──
stages = [
    (1.0,  BLUE_FILL,  BLUE_BORDER,  "Patient\nEEG",          "7 frontal ch.\n250 Hz"),
    (3.0,  BLUE_FILL,  BLUE_BORDER,  "Signal\nProcessing",    "BP 0.5\u201380 Hz\nNotch, CAR"),
    (5.0,  TEAL_FILL,  TEAL_BORDER,  "EEGNet",                "1,457 params\nR\u00b2 = 0.287"),
    (7.0,  TEAL_FILL,  TEAL_BORDER,  "Feature\nEngineering",  "73 features\n(61+7+5)"),
    (9.0,  TEAL_FILL,  TEAL_BORDER,  "Causal\nTCN",           "31K params\n5 s forecast"),
    (11.0, AMBER_FILL, AMBER_BORDER, "Adaptive\nController",  "z-score \u00b10.5\n5 s hysteresis"),
    (13.0, CORAL_FILL, CORAL_BORDER, "40 Hz Audio\nStimulation", "STIM / REST\n/ MAINTAIN"),
]

box_w = 1.65
box_h = 2.4
box_y_center = 1.0

for x, fill, border, title, subtitle in stages:
    # Box with colored border
    rect = FancyBboxPatch(
        (x - box_w/2, box_y_center - box_h/2),
        box_w, box_h,
        boxstyle="round,pad=0.1",
        facecolor=fill, edgecolor=border, linewidth=2.0,
        zorder=3
    )
    ax.add_patch(rect)

    # Colored header bar at top of box
    header_h = 0.85
    header_rect = FancyBboxPatch(
        (x - box_w/2 + 0.01, box_y_center + box_h/2 - header_h - 0.01),
        box_w - 0.02, header_h,
        boxstyle="round,pad=0.08",
        facecolor=border, edgecolor="none",
        zorder=4
    )
    ax.add_patch(header_rect)

    # Title text (white on dark header)
    ax.text(x, box_y_center + box_h/2 - header_h/2 - 0.01,
            title, ha="center", va="center",
            fontsize=11.5, fontweight="bold", color="white", zorder=5,
            linespacing=1.15)

    # Subtitle text (dark on light body)
    ax.text(x, box_y_center - 0.35,
            subtitle, ha="center", va="center",
            fontsize=9.5, color=TEXT_MID, zorder=5,
            linespacing=1.35)

# ── Arrows between stages ──
for i in range(len(stages) - 1):
    x1 = stages[i][0] + box_w/2 + 0.05
    x2 = stages[i+1][0] - box_w/2 - 0.05
    ax.annotate("", xy=(x2, box_y_center + 0.3), xytext=(x1, box_y_center + 0.3),
                arrowprops=dict(arrowstyle="-|>", color=ARROW_COLOR,
                               lw=2.0, mutation_scale=16),
                zorder=6)

# ── Feedback arrow ──
from scipy.interpolate import make_interp_spline

fb_y = -1.3
pts = [
    (13.0, box_y_center - box_h/2 - 0.08),
    (13.0, fb_y),
    (7.0, fb_y - 0.25),
    (1.0, fb_y),
    (1.0, box_y_center - box_h/2 - 0.08),
]
xs = [p[0] for p in pts]
ys = [p[1] for p in pts]
t = np.linspace(0, 1, len(pts))
t_s = np.linspace(0, 1, 100)
try:
    sx = make_interp_spline(t, xs, k=3)
    sy = make_interp_spline(t, ys, k=3)
    xc, yc = sx(t_s), sy(t_s)
except:
    xc = np.interp(t_s, t, xs)
    yc = np.interp(t_s, t, ys)

ax.plot(xc, yc, color=ARROW_COLOR, lw=1.8, ls="--", zorder=2)
ax.annotate("", xy=(1.0, box_y_center - box_h/2 - 0.08),
            xytext=(1.3, fb_y + 0.12),
            arrowprops=dict(arrowstyle="-|>", color=ARROW_COLOR, lw=1.8),
            zorder=6)

ax.text(7.0, fb_y - 0.45,
        "Closed-Loop Feedback (EEG monitors entrainment response)",
        ha="center", va="top", fontsize=10, color=TEXT_MID, fontstyle="italic")

# ── Title ──
ax.text(7.0, 4.2, "Closed-Loop 40 Hz Entrainment System Architecture",
        ha="center", va="center", fontsize=16, fontweight="bold", color=TEXT_DARK)

# ── Legend ──
leg_y = 3.55
for lx, fill, border, label in [
    (3.0, BLUE_FILL, BLUE_BORDER, "Signal / Data"),
    (7.0, TEAL_FILL, TEAL_BORDER, "ML Model"),
    (11.0, AMBER_FILL, AMBER_BORDER, "Decision / Control"),
]:
    r = FancyBboxPatch((lx - 0.3, leg_y - 0.18), 0.6, 0.36,
                       boxstyle="round,pad=0.05",
                       facecolor=fill, edgecolor=border, linewidth=1.2, zorder=3)
    ax.add_patch(r)
    ax.text(lx + 0.5, leg_y, label, ha="left", va="center",
            fontsize=10, color=TEXT_DARK)

# ── EEG wave icon ──
wave_x = np.linspace(0.45, 1.55, 80)
wave_y = (box_y_center - 0.85) + 0.1 * np.sin(wave_x * 18) * np.exp(-((wave_x - 1.0)**2) / 0.12)
ax.plot(wave_x, wave_y, color=BLUE_BORDER, lw=1.0, alpha=0.5, zorder=5)

# ── Speaker icon ──
sx, sy = 13.0, box_y_center - 0.85
# Speaker body
ax.fill([sx-0.12, sx+0.05, sx+0.18, sx+0.18, sx+0.05, sx-0.12],
        [sy-0.06, sy-0.06, sy-0.14, sy+0.14, sy+0.06, sy+0.06],
        color=CORAL_BORDER, alpha=0.5, zorder=5)
for r in [0.2, 0.3]:
    th = np.linspace(-0.5, 0.5, 20)
    ax.plot(sx + 0.18 + r * np.cos(th), sy + r * np.sin(th),
            color=CORAL_BORDER, lw=1.0, alpha=0.4, zorder=5)

fig.tight_layout(pad=0.3)
fig.savefig(OUTPUT, dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved: {OUTPUT}")
print(f"Size: {os.path.getsize(OUTPUT) // 1024} KB")
