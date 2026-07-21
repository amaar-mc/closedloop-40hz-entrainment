#!/usr/bin/env python3
"""Generate the PAC benchmark stress-test figure for the MIT URTC manuscript."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "paper/conferences/mit_urtc_2026/figures/pac_benchmark_stress_test.png"
SOURCE = ROOT / "archive/experimental/sliding_pac/results/comparison_results.json"

NAVY = "#17365D"
TEAL = "#1F6E73"
GOLD = "#C9972B"
CORAL = "#B9574F"
LIGHT_TEAL = "#E8F3F3"
LIGHT_CORAL = "#F8E8E6"
GRAY = "#6B7280"


def rounded_box(ax, x, y, w, h, *, color, edge, title, lines) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.015,rounding_size=0.02",
            facecolor=color,
            edgecolor=edge,
            linewidth=1.2,
        )
    )
    ax.text(x + 0.03, y + h - 0.07, title, color=edge, fontsize=9, fontweight="bold", va="top")
    ax.text(x + 0.03, y + h - 0.22, "\n".join(lines), color=NAVY, fontsize=8, va="top", linespacing=1.2)


def load_results() -> tuple[list[str], np.ndarray, np.ndarray, int]:
    data = json.loads(SOURCE.read_text())
    models = ["Persistence", "Ridge", "TCN"]
    event = np.array(
        [
            data["epoch"]["persistence"]["r2"],
            data["epoch"]["ridge"]["r2"],
            data["epoch"]["test_metrics"]["r2"],
        ]
    )
    sliding = np.array(
        [
            data["sliding"]["persistence"]["r2"],
            data["sliding"]["ridge"]["r2"],
            data["sliding"]["test_metrics"]["r2"],
        ]
    )
    return models, event, sliding, int(data["epoch"]["n_test"])


def generate() -> None:
    models, event, sliding, n_test = load_results()

    fig = plt.figure(figsize=(3.3, 4.35), dpi=300, facecolor="white")
    gs = fig.add_gridspec(2, 1, height_ratios=[1.42, 1.0], hspace=0.22)

    ax = fig.add_subplot(gs[0])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    rounded_box(
        ax,
        0.01,
        0.59,
        0.98,
        0.39,
        color=LIGHT_CORAL,
        edge=CORAL,
        title="A. Event-summary benchmark",
        lines=[
            "Complete-event PAC is assigned to each 2 s window.",
            "Early inputs include later samples: retrospective only.",
        ],
    )
    rounded_box(
        ax,
        0.01,
        0.04,
        0.98,
        0.39,
        color=LIGHT_TEAL,
        edge=TEAL,
        title="B. Backward-looking PAC stress test",
        lines=[
            "PAC uses a 5 s context ending at forecast time t.",
            "No sample after t enters the PAC context.",
        ],
    )
    ax.add_patch(FancyArrowPatch((0.50, 0.57), (0.50, 0.45), arrowstyle="-|>", mutation_scale=13, color=GOLD, linewidth=1.6))
    ax.text(0.54, 0.51, "stress test", ha="left", va="center", fontsize=8, color=NAVY, fontweight="bold")

    ax2 = fig.add_subplot(gs[1])
    x = np.arange(len(models))
    width = 0.34
    ax2.bar(x - width / 2, event, width, label="Event-summary PAC", color=CORAL)
    ax2.bar(x + width / 2, sliding, width, label="Backward-looking PAC", color=TEAL)
    ax2.axhline(0, color=NAVY, linewidth=0.8)
    ax2.set_ylim(-1.05, 0.70)
    ax2.set_ylabel("Held-out test R-squared", color=NAVY, fontsize=8)
    ax2.set_xticks(x, models, fontsize=8)
    ax2.tick_params(axis="y", labelsize=8)
    ax2.grid(axis="y", color="#D1D5DB", linewidth=0.5, alpha=0.8)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.legend(loc="lower right", frameon=False, fontsize=7)
    for offset, values in [(-width / 2, event), (width / 2, sliding)]:
        for xpos, value in zip(x + offset, values):
            va = "bottom" if value >= 0 else "top"
            y = value + (0.025 if value >= 0 else -0.025)
            ax2.text(xpos, y, f"{value:.3f}", ha="center", va=va, fontsize=7.5, color=NAVY)
    ax2.set_title("Single-seed fixed-split point estimates", fontsize=8, color=NAVY, pad=4)
    ax2.text(
        0.5,
        -0.28,
        f"Held-out test: n={n_test:,}; no confidence intervals",
        transform=ax2.transAxes,
        ha="center",
        va="top",
        fontsize=6.4,
        color=GRAY,
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    generate()
