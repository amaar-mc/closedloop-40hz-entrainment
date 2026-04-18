#!/usr/bin/env python3
"""
Generate Figure: Fixed Schedule vs Predictive Closed-Loop comparison diagram.

Saves to: results/figures/ai_generated/closedloop_vs_fixed_v3.png
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyArrowPatch
from pathlib import Path

# ---------------------------------------------------------------------------
# Colour palette (matches paper style)
# ---------------------------------------------------------------------------
NAVY       = "#1B2A4A"
TEAL       = "#2A7F8E"
LIGHT_TEAL = "#D0ECF0"
CORAL      = "#C05746"
SAGE       = "#5B8C5A"
SLATE      = "#6B7B8D"
WHITE      = "#FFFFFF"

# ---------------------------------------------------------------------------
# Font setup — Times New Roman (serif fallback)
# ---------------------------------------------------------------------------
try:
    fm.findfont("Times New Roman", fallback_to_default=False)
    FONT_FAMILY = "Times New Roman"
except Exception:
    FONT_FAMILY = "serif"

plt.rcParams.update({
    "font.family": FONT_FAMILY,
    "axes.unicode_minus": False,
    "mathtext.fontset": "dejavuserif",
})

# ---------------------------------------------------------------------------
# Synthetic PAC signal (~4 full cycles over 240 s)
# ---------------------------------------------------------------------------
t = np.linspace(0, 250, 2000)
pac = 0.5 + 0.35 * np.sin(2 * np.pi * t / 60)          # period = 60 s, ~4 cycles
pac += 0.07 * np.sin(2 * np.pi * t / 23 + 0.8)          # slight irregularity
pac += 0.04 * np.sin(2 * np.pi * t / 13 + 2.1)          # more texture

# Detect peaks and troughs
from scipy.signal import argrelextrema

peak_idx = argrelextrema(pac, np.greater, order=120)[0]
trough_idx = argrelextrema(pac, np.less, order=120)[0]

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(12, 5), dpi=300,
                                  sharey=True, facecolor=WHITE)
fig.subplots_adjust(wspace=0.10, left=0.07, right=0.96, top=0.84, bottom=0.14)

y_lo, y_hi = -0.02, 1.12

# ===== Helper: draw stim bar =====
def draw_stim_bar(ax, t_start, t_end, alpha=0.35):
    ax.axvspan(t_start, t_end, color=LIGHT_TEAL, alpha=alpha, zorder=0)
    ax.plot([t_start, t_start], [y_lo, y_hi], color=TEAL, lw=0.5, alpha=0.25)
    ax.plot([t_end, t_end], [y_lo, y_hi], color=TEAL, lw=0.5, alpha=0.25)

# ===== PANEL A — Fixed Schedule (Open-Loop) =====
ax = ax_a

# Fixed stim bars: 35 s ON / 25 s OFF (gives clearer misses)
stim_on = 35
stim_off = 25
period = stim_on + stim_off
cursor = 0
fixed_intervals = []
while cursor < t[-1]:
    on_start = cursor
    on_end = min(cursor + stim_on, t[-1])
    fixed_intervals.append((on_start, on_end))
    draw_stim_bar(ax, on_start, on_end)
    cursor += period

# PAC line
ax.plot(t, pac, color=NAVY, lw=2.2, zorder=3)

# Red X at peaks that fall inside a stim window (wasted stimulation)
for pi in peak_idx:
    in_stim = any(s <= t[pi] <= e for s, e in fixed_intervals)
    if in_stim:
        ax.plot(t[pi], pac[pi], marker='x', color=CORAL, markersize=13,
                markeredgewidth=3.0, zorder=5)

# Red circles at troughs outside stim windows (missed opportunity)
missed_troughs = []
for ti in trough_idx:
    in_stim = any(s <= t[ti] <= e for s, e in fixed_intervals)
    if not in_stim:
        missed_troughs.append(ti)
        ax.scatter(t[ti], pac[ti], s=160, facecolors='none', edgecolors=CORAL,
                   linewidths=2.5, zorder=5)

# Annotation: alignment %
ax.text(0.95, 0.93, "45% alignment", transform=ax.transAxes,
        ha="right", va="top", fontsize=14, fontweight="bold", color=CORAL)

# Annotation arrows for X and circle
if len(peak_idx) >= 2:
    ax.annotate("wasted\nstimulation", xy=(t[peak_idx[1]], pac[peak_idx[1]]),
                xytext=(t[peak_idx[1]] + 16, pac[peak_idx[1]] + 0.04),
                fontsize=8.5, color=CORAL, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="->", color=CORAL, lw=1.0,
                                connectionstyle="arc3,rad=0.15"))

if missed_troughs:
    mi = missed_troughs[0]
    ax.annotate("missed\nopportunity", xy=(t[mi], pac[mi]),
                xytext=(t[mi] + 16, pac[mi] - 0.04),
                fontsize=8.5, color=CORAL, ha="left", va="top",
                arrowprops=dict(arrowstyle="->", color=CORAL, lw=1.0,
                                connectionstyle="arc3,rad=-0.15"))

# Stim ON legend swatch (small rectangle + text) — positioned in upper-left
rect_x = 0.03
rect_y = 0.82
ax.add_patch(plt.Rectangle((rect_x, rect_y), 0.08, 0.06, transform=ax.transAxes,
             facecolor=LIGHT_TEAL, edgecolor=TEAL, lw=0.8, zorder=6, clip_on=False))
ax.text(rect_x + 0.10, rect_y + 0.03, "Stim ON", transform=ax.transAxes,
        ha="left", va="center", fontsize=8.5, color=TEAL, fontstyle="italic")

# Panel label & titles
ax.text(-0.10, 1.08, "A", transform=ax.transAxes, fontsize=20,
        fontweight="bold", va="top", ha="right")
ax.set_title("Fixed Schedule (Open-Loop)", fontsize=14, fontweight="bold", pad=12)
ax.set_ylabel("PAC Strength", fontsize=12, labelpad=6)
ax.set_xlabel("Time", fontsize=12)
ax.set_ylim(y_lo, y_hi)
ax.set_xlim(t[0], t[-1])
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xticks([])
ax.set_yticks([])

# ===== PANEL B — Predictive Closed-Loop (Ours) =====
ax = ax_b

# Stim bars centred on troughs (± 12 s)
closed_intervals = []
for ti in trough_idx:
    t_centre = t[ti]
    on_start = max(t_centre - 12, t[0])
    on_end = min(t_centre + 12, t[-1])
    closed_intervals.append((on_start, on_end))
    draw_stim_bar(ax, on_start, on_end, alpha=0.50)

# PAC line
ax.plot(t, pac, color=NAVY, lw=2.2, zorder=3)

# Green checkmarks at troughs
for ti in trough_idx:
    ax.plot(t[ti], pac[ti] - 0.07, marker=r'$\checkmark$', color=SAGE,
            markersize=18, zorder=5, markeredgewidth=0.5)

# Arrow bracket: "TCN forecasts 5-10 s ahead"
# Place above the second trough region
if len(trough_idx) >= 2:
    bracket_centre = t[trough_idx[1]]
    half_span = 28
    bracket_left = bracket_centre - half_span
    bracket_right = bracket_centre + half_span
    bracket_y = 1.01

    # Horizontal double-ended arrow
    ax.annotate("", xy=(bracket_left, bracket_y), xytext=(bracket_right, bracket_y),
                arrowprops=dict(arrowstyle="<->", color=SLATE, lw=1.8),
                zorder=4)
    ax.text(bracket_centre, bracket_y + 0.045,
            "TCN forecasts 5\u201310 s ahead", ha="center", va="bottom",
            fontsize=10, color=SLATE, fontstyle="italic", fontweight="bold")

# Annotation: alignment %
ax.text(0.95, 0.93, "72% alignment", transform=ax.transAxes,
        ha="right", va="top", fontsize=14, fontweight="bold", color=SAGE)

# Stim ON legend swatch — upper-left to match Panel A
rect_x = 0.03
rect_y = 0.82
ax.add_patch(plt.Rectangle((rect_x, rect_y), 0.08, 0.06, transform=ax.transAxes,
             facecolor=LIGHT_TEAL, edgecolor=TEAL, lw=0.8, zorder=6, clip_on=False))
ax.text(rect_x + 0.10, rect_y + 0.03, "Stim ON", transform=ax.transAxes,
        ha="left", va="center", fontsize=8.5, color=TEAL, fontstyle="italic")

# Panel label & titles
ax.text(-0.04, 1.08, "B", transform=ax.transAxes, fontsize=20,
        fontweight="bold", va="top", ha="right")
ax.set_title("Predictive Closed-Loop (Ours)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Time", fontsize=12)
ax.set_xlim(t[0], t[-1])
ax.set_ylim(y_lo, y_hi)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xticks([])
ax.set_yticks([])

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
out_path = Path("results/figures/ai_generated/closedloop_vs_fixed_v3.png")
out_path.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor=WHITE)
plt.close(fig)
print(f"Saved -> {out_path.resolve()}")
