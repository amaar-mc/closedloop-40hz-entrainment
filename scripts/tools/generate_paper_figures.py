"""
Generate publication-quality figures for the research paper.

Figures produced:
  1. horizon_sweep.{png,pdf}  — PAC forecasting R² vs. prediction horizon for
     Persistence, Ridge, and MultiscaleCausalTCN baselines.
  2. system_block_diagram.{png,pdf} — Full closed-loop EEG-to-stimulation
     pipeline block diagram.

Caption note (horizon sweep):
  Evaluated with 5-window causal target smoothing (ts=5).  Deployed checkpoint
  uses raw targets (ts=1); see Supplementary Table S1 for absolute performance
  under that condition.

Usage:
    python scripts/generate_paper_figures.py
"""

import json
import os
import sys
from pathlib import Path

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = REPO_ROOT / "results" / "figures"
SWEEP_JSON = REPO_ROOT / "models" / "sweep_horizons_results.json"

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
BLUE = "#2196F3"
ORANGE = "#FF9800"
GREEN = "#4CAF50"
GREEN_SHADE = "#C8E6C9"   # light green for shaded region

matplotlib.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.4,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    }
)


# ---------------------------------------------------------------------------
# Figure 1: Horizon sweep
# ---------------------------------------------------------------------------
def generate_horizon_sweep(output_dir: Path = FIGURES_DIR) -> None:
    """
    Line graph showing R² vs. prediction horizon for three models:
    - Persistence baseline (circles, blue)
    - Ridge regression (squares, orange)
    - Causal TCN (triangles, green, thicker line)

    Data are read directly from models/sweep_horizons_results.json so that the
    figure always reflects the exact numbers from the sweep run.

    Caption note:
        Evaluated with 5-window causal target smoothing (ts=5).
        Deployed checkpoint uses raw targets (ts=1); see Supplementary Table S1
        for absolute performance under that condition.
    """
    # Load exact sweep data
    with open(SWEEP_JSON, "r") as fh:
        records = json.load(fh)

    horizons = [r["horizon"] for r in records]
    persistence_r2 = [r["persistence_r2"] for r in records]
    ridge_r2 = [r["ridge_r2"] for r in records]
    tcn_r2 = [r["tcn_r2"] for r in records]

    fig, ax = plt.subplots(figsize=(8, 5))

    # Shaded "operationally useful" region (5-10s)
    ax.axvspan(4.5, 10.5, color=GREEN_SHADE, alpha=0.5,
               label="Operationally useful range (5–10 s)", zorder=1)

    # Horizontal zero line
    ax.axhline(y=0, color="black", linestyle="--", linewidth=1.0,
               zorder=2, label="R² = 0")

    # Three model lines
    ax.plot(horizons, persistence_r2,
            color=BLUE, marker="o", markersize=7, linewidth=1.8,
            label="Persistence", zorder=3)
    ax.plot(horizons, ridge_r2,
            color=ORANGE, marker="s", markersize=7, linewidth=1.8,
            label="Ridge Regression", zorder=3)
    ax.plot(horizons, tcn_r2,
            color=GREEN, marker="^", markersize=8, linewidth=2.5,
            label="Causal TCN (ours)", zorder=4)

    ax.set_xlabel("Prediction Horizon (seconds)")
    ax.set_ylabel("R²")
    ax.set_title("PAC Forecasting Performance vs. Prediction Horizon")
    ax.set_xticks(horizons)
    ax.set_xlim(0.5, 10.5)

    # Legend — place outside the shaded region, upper-right area
    ax.legend(loc="upper right", framealpha=0.9)

    fig.tight_layout()

    for ext in ("png", "pdf"):
        out_path = output_dir / f"horizon_sweep.{ext}"
        dpi = 300 if ext == "png" else None
        fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
        print(f"  Saved: {out_path}")

    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 2: System block diagram
# ---------------------------------------------------------------------------
def generate_system_block_diagram(output_dir: Path = FIGURES_DIR) -> None:
    """
    Horizontal left-to-right block diagram showing the full closed-loop
    EEG-to-stimulation pipeline with a feedback arrow from the stimulation
    decision back to the patient.

    Colour coding:
        Blue   (#2196F3) — data / signal processing blocks
        Green  (#4CAF50) — ML model blocks
        Orange (#FF9800) — decision / controller blocks
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------
    BOX_H = 1.0          # box height
    BOX_W = 1.55         # box width (most blocks)
    Y_TOP = 3.7          # top row Y centre
    Y_MID = 2.35         # not used as a separate row — kept for reference
    FONT_MAIN = 8.5
    FONT_SUB = 7.0

    def draw_box(cx, cy, label, sublabel, color, width=BOX_W, height=BOX_H):
        """Draw a rounded rectangle centred at (cx, cy)."""
        x0 = cx - width / 2
        y0 = cy - height / 2
        box = FancyBboxPatch(
            (x0, y0), width, height,
            boxstyle="round,pad=0.07",
            facecolor=color, edgecolor="white",
            linewidth=1.5, zorder=3,
        )
        ax.add_patch(box)
        ax.text(cx, cy + 0.15, label, ha="center", va="center",
                fontsize=FONT_MAIN, fontweight="bold", color="white",
                zorder=4, wrap=True)
        ax.text(cx, cy - 0.21, sublabel, ha="center", va="center",
                fontsize=FONT_SUB, color="white", zorder=4,
                style="italic")

    def arrow(x0, y0, x1, y1, annotation=None, ann_above=True):
        """Draw a simple right-pointing arrow with optional label."""
        ax.annotate(
            "",
            xy=(x1, y1), xytext=(x0, y0),
            arrowprops=dict(arrowstyle="-|>", color="#555555",
                            lw=1.3),
            zorder=2,
        )
        if annotation:
            mx = (x0 + x1) / 2
            my = (y0 + y1) / 2
            dy = 0.22 if ann_above else -0.22
            ax.text(mx, my + dy, annotation, ha="center", va="center",
                    fontsize=6.5, color="#444444", zorder=5)

    # ------------------------------------------------------------------
    # Block centres (left → right in top row)
    # ------------------------------------------------------------------
    ALPHA = 0.82          # colour alpha not applicable — use hex directly

    LIGHT_BLUE = "#64B5F6"
    MID_BLUE   = "#2196F3"
    DARK_BLUE  = "#1565C0"
    MID_GREEN  = "#4CAF50"
    DARK_GREEN = "#388E3C"
    MID_ORANGE = "#FF9800"
    DARK_ORANGE = "#E65100"

    Y = Y_TOP

    # x positions for top row
    xs = [1.1, 3.0, 4.9, 6.8, 8.7, 10.6, 12.5]

    blocks = [
        # (cx, label, sublabel, color)
        (xs[0], "Patient EEG",        "7 frontal ch.\n250 Hz",         LIGHT_BLUE),
        (xs[1], "Preprocessing",      "BP 0.5–80 Hz\nnotch, CAR",      MID_BLUE),
        (xs[2], "EEGNet",             "1,457 params\nMSE trained",      MID_GREEN),
        (xs[3], "Feature\nExtraction","73 features\n61+7+5",            DARK_BLUE),
        (xs[4], "Causal TCN",         "31 K params\n20 s lookback",     DARK_GREEN),
        (xs[5], "Closed-Loop\nController", "z-score ±0.5\n5 s hysteresis", MID_ORANGE),
        (xs[6], "40 Hz\nAudio Stim.", "STIMULATE /\nREST / MAINTAIN",   DARK_ORANGE),
    ]

    for cx, label, sublabel, color in blocks:
        draw_box(cx, Y, label, sublabel, color)

    # ------------------------------------------------------------------
    # Arrows between consecutive blocks (top row, left → right)
    # ------------------------------------------------------------------
    arrow_labels = [
        "2 s windows",
        "EEG tensor\n(1,7,500)",
        "PAC estimate",
        "causal\nsequence",
        "Pred. PAC\n(5 s ahead)",
        "decision",
    ]
    for i in range(len(xs) - 1):
        x0 = xs[i] + BOX_W / 2
        x1 = xs[i + 1] - BOX_W / 2
        ann = arrow_labels[i]
        arrow(x0, Y, x1, Y, annotation=ann, ann_above=True)

    # ------------------------------------------------------------------
    # Inference latency annotation below EEGNet
    # ------------------------------------------------------------------
    ax.text(xs[2], Y - 0.82, "<50 ms\ninference",
            ha="center", va="center", fontsize=6.5, color="#555555",
            fontstyle="italic")

    # ------------------------------------------------------------------
    # Feedback arrow: from Stimulation block back to Patient EEG
    # Curves below the main row
    # ------------------------------------------------------------------
    fb_y = Y - 1.65     # vertical drop for the feedback curve

    # Downward segment from stim block
    ax.annotate("", xy=(xs[6], fb_y), xytext=(xs[6], Y - BOX_H / 2),
                arrowprops=dict(arrowstyle="-", color="#E65100", lw=1.4,
                                connectionstyle="arc3,rad=0.0"),
                zorder=2)

    # Horizontal return segment (right to left, below blocks)
    ax.annotate("", xy=(xs[0], fb_y), xytext=(xs[6], fb_y),
                arrowprops=dict(arrowstyle="-|>", color="#E65100", lw=1.4),
                zorder=2)

    # Upward segment to Patient EEG block
    ax.annotate("", xy=(xs[0], Y - BOX_H / 2), xytext=(xs[0], fb_y),
                arrowprops=dict(arrowstyle="-", color="#E65100", lw=1.4),
                zorder=2)

    # Label on feedback loop
    ax.text((xs[0] + xs[6]) / 2, fb_y - 0.22,
            "Entrainment feedback (40 Hz gamma–theta coupling)",
            ha="center", va="center", fontsize=7.0, color="#E65100",
            fontstyle="italic")

    # ------------------------------------------------------------------
    # Title / legend patches
    # ------------------------------------------------------------------
    ax.set_title(
        "Closed-Loop 40 Hz Entrainment System Architecture",
        fontsize=13, fontweight="bold", pad=12,
    )

    legend_patches = [
        mpatches.Patch(color=MID_BLUE,   label="Signal / Data"),
        mpatches.Patch(color=MID_GREEN,  label="ML Model"),
        mpatches.Patch(color=MID_ORANGE, label="Decision / Control"),
    ]
    ax.legend(handles=legend_patches, loc="lower center",
              bbox_to_anchor=(0.5, -0.04), ncol=3,
              framealpha=0.85, fontsize=9)

    fig.tight_layout()

    for ext in ("png", "pdf"):
        out_path = output_dir / f"system_block_diagram.{ext}"
        dpi = 300 if ext == "png" else None
        fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
        print(f"  Saved: {out_path}")

    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating Figure 1: PAC Horizon Sweep ...")
    generate_horizon_sweep(FIGURES_DIR)

    print("Generating Figure 2: System Block Diagram ...")
    generate_system_block_diagram(FIGURES_DIR)

    print("\nDone. Files written:")
    for name in (
        "horizon_sweep.png",
        "horizon_sweep.pdf",
        "system_block_diagram.png",
        "system_block_diagram.pdf",
    ):
        p = FIGURES_DIR / name
        size_kb = p.stat().st_size // 1024 if p.exists() else 0
        status = "OK" if p.exists() else "MISSING"
        print(f"  [{status}] {p}  ({size_kb} KB)")
