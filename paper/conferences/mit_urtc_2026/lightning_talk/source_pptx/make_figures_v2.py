"""Figures for the editable PowerPoint deck (URTC 2026 lightning talk, ID-1269).

Same data as source/make_figures.py (every value read from results/metrics/ and analysis/), drawn
in Arial with the author's poster palette (teal = 40-Hz sound, dark blue = electrodes), direct labels
instead of captions, and 300-dpi PNGs for PowerPoint.

From paper/conferences/mit_urtc_2026/lightning_talk/:
  <python> source_pptx/make_figures_v2.py --repo ../../../.. --recon analysis --out source_pptx/fig
"""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

# Vermilion always means 40-Hz sound. Teal is the EEG signal. Grays are silence and controls.
INK = "#222222"
INK_2 = "#444444"
MUTED = "#666666"
HAIR = "#E4E6E8"
AXIS = "#9A9A9A"
SOUND = "#1482A5"       # the author's poster teal = 40-Hz sound / the main result
SOUND_SOFT = "#B8DCE8"
SIGNAL = "#235078"      # the author's poster dark blue = EEG electrodes
SILENCE = "#9AA3AD"     # always direct-labelled (contrast 2.6:1)
SILENCE_SOFT = "#DDE1E5"
CONTROL = "#9AA3AD"
SILENCE_LINE = "#5F6975"

FONT = "Arial"

plt.rcParams.update(
    {
        "font.family": FONT,
        "font.size": 15,
        "svg.fonttype": "path",  # outline text so math glyphs need no installed fonts
        "mathtext.fontset": "custom",  # math letters in Arial italic, like the inline math on the slides
        "mathtext.rm": "Arial",
        "mathtext.it": "Arial:italic",
        "mathtext.bf": "Arial:bold",
        "axes.edgecolor": AXIS,
        "axes.labelcolor": INK_2,
        "axes.linewidth": 1.0,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "xtick.major.size": 4,
        "ytick.major.size": 4,
        "xtick.major.width": 1.0,
        "ytick.major.width": 1.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "none",
        "axes.facecolor": "none",
        "savefig.facecolor": "none",
        "legend.frameon": False,
    }
)

MINUS = "−"


def tick_labels(values, fmt="{:g}"):
    return [fmt.format(v).replace("-", MINUS) if v != 0 else "0" for v in values]


def save(fig, out, name):
    fig.savefig(out / f"{name}.svg", transparent=True)
    fig.savefig(out / f"{name}.png", dpi=300, transparent=False, facecolor="white")
    plt.close(fig)


# ----------------------------------------------------------------------------------------------
# Slide 5: early vs later contrast
# ----------------------------------------------------------------------------------------------
def fig_scatter(primary, out):
    node = primary["target_position_sensitivity_plv"]["cycles_4_to_5"]
    early = np.array(node["values"]["early"])
    late = np.array(node["values"]["late"])
    r = node["raw_association"]["pearson_r"]
    assert abs(r - np.corrcoef(early, late)[0, 1]) < 1e-12

    fig, ax = plt.subplots(figsize=(7.0, 5.3))
    fig.subplots_adjust(left=0.15, right=0.975, bottom=0.15, top=0.975)
    lo, hi = -0.13, 0.47
    ax.axhline(0, color=HAIR, lw=1.2, zorder=0)
    ax.axvline(0, color=HAIR, lw=1.2, zorder=0)
    ax.plot([lo, hi], [lo, hi], ls=(0, (4, 4)), color=CONTROL, lw=1.6, zorder=1)

    slope, intercept = np.polyfit(early, late, 1)
    xs = np.array([early.min() - 0.01, early.max() + 0.01])
    ax.plot(xs, slope * xs + intercept, color=INK, lw=1.8, zorder=2)
    ax.scatter(early, late, s=78, color=SOUND, edgecolor="white", linewidth=1.3, zorder=3)
    ci = node["bootstrap"]["raw_correlation_ci95"]
    ax.text(0.035, 0.965, rf"$r$ = {r:.3f}", transform=ax.transAxes, ha="left", va="top", fontsize=24,
            color=INK, fontweight="bold")
    ax.text(0.035, 0.865, f"95% CI [{ci[0]:.3f}, {ci[1]:.3f}]\n" + rf"$n$ = {len(early)} people",
            transform=ax.transAxes, ha="left", va="top", fontsize=15, color=INK_2, linespacing=1.35)
    ax.text(0.352, 0.366, "later = early", ha="right", va="bottom", fontsize=13, color=MUTED, rotation=0)
    ax.text(0.228, 0.112, "best-fit line", ha="left", va="center", fontsize=13, color=INK)

    ax.set_xlim(lo, 0.37)
    ax.set_ylim(lo, hi)
    xt = [-0.1, 0, 0.1, 0.2, 0.3]
    yt = [-0.1, 0, 0.1, 0.2, 0.3, 0.4]
    ax.set_xticks(xt)
    ax.set_xticklabels(tick_labels(xt))
    ax.set_yticks(yt)
    ax.set_yticklabels(tick_labels(yt))
    ax.set_xlabel("Early contrast, cycles 1-2", fontsize=17, labelpad=8)
    ax.set_ylabel("Later contrast, cycles 4-5", fontsize=17, labelpad=8)
    ax.tick_params(labelsize=15)
    save(fig, out, "fig_scatter")
    return {"slope": float(slope), "intercept": float(intercept), "n": int(len(early)), "r": float(r)}


def fig_scatter_small(primary, out):
    node = primary["target_position_sensitivity_plv"]["cycles_4_to_5"]
    early = np.array(node["values"]["early"])
    late = np.array(node["values"]["late"])
    r = node["raw_association"]["pearson_r"]
    fig, ax = plt.subplots(figsize=(4.1, 3.2))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.2, top=0.97)
    lo, hi = -0.13, 0.47
    ax.axhline(0, color=HAIR, lw=1.0, zorder=0)
    ax.axvline(0, color=HAIR, lw=1.0, zorder=0)
    ax.plot([lo, hi], [lo, hi], ls=(0, (4, 4)), color=CONTROL, lw=1.3, zorder=1)
    slope, intercept = np.polyfit(early, late, 1)
    xs = np.array([early.min() - 0.01, early.max() + 0.01])
    ax.plot(xs, slope * xs + intercept, color=INK, lw=1.6, zorder=2)
    ax.scatter(early, late, s=42, color=SOUND, edgecolor="white", linewidth=1.0, zorder=3)
    ax.text(0.05, 0.95, rf"$r$ = {r:.2f}", transform=ax.transAxes, ha="left", va="top", fontsize=17,
            color=INK, fontweight="bold")
    ax.set_xlim(lo, 0.37)
    ax.set_ylim(lo, hi)
    ax.set_xticks([0, 0.2])
    ax.set_yticks([0, 0.2, 0.4])
    ax.set_xticklabels(["0", "0.2"])
    ax.set_yticklabels(["0", "0.2", "0.4"])
    ax.set_xlabel("Early contrast", fontsize=14, labelpad=4)
    ax.set_ylabel("Later contrast", fontsize=14, labelpad=4)
    ax.tick_params(labelsize=13)
    save(fig, out, "fig_scatter_small")


# ----------------------------------------------------------------------------------------------
# Slide 6: three checks, drawn as small multiples on one r axis
# ----------------------------------------------------------------------------------------------
PANEL = (3.7, 3.7)


def _r_axis(ax, ylabel=True):
    ax.axhline(0, color=AXIS, lw=1.0, zorder=0)
    ax.set_ylim(-0.5, 1.0)
    yt = [-0.5, 0, 0.5, 1.0]
    ax.set_yticks(yt)
    ax.set_yticklabels(tick_labels(yt, "{:.1f}"))
    if ylabel:
        ax.set_ylabel("Early vs. later r", fontsize=16, labelpad=4)
    ax.tick_params(labelsize=14.5)


def _dot(ax, x, r, a, b, primary):
    c = SOUND if primary else CONTROL
    ax.plot([x, x], [a, b], color=c, lw=2.2 if primary else 1.7, solid_capstyle="round", zorder=2)
    ax.scatter([x], [r], s=100 if primary else 62, color=c, edgecolor="white", linewidth=1.3, zorder=3)


def fig_frequency(fig_json, primary, out):
    freqs = fig_json["frequencies_hz"]
    rs = fig_json["frequency_correlations"]
    cis = [list(c) for c in fig_json["frequency_bootstrap_ci95"]]
    prim = primary["target_position_sensitivity_plv"]["cycles_4_to_5"]
    i40 = freqs.index(40.0)
    assert abs(rs[i40] - prim["raw_association"]["pearson_r"]) < 1e-12
    # The 40-Hz whisker is the primary analysis CI (the one quoted in the abstract).
    cis[i40] = prim["bootstrap"]["raw_correlation_ci95"]
    cs = primary["common_position_frequency_specificity_plv"]["statistics"]
    assert abs(cs["primary_correlation"] - rs[i40]) < 1e-12

    fig, ax = plt.subplots(figsize=(5.0, 3.7))
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.19, top=0.96)
    _r_axis(ax)
    for f, r, (a, b) in zip(freqs, rs, cis):
        _dot(ax, f, r, a, b, f == 40.0)
    ax.text(40.6, rs[i40], f"{rs[i40]:.2f}", color=INK, fontsize=14, va="center", ha="left", fontweight="bold")
    ax.set_xticks(freqs)
    ax.set_xticklabels([f"{int(f)}" for f in freqs])
    lab = ax.get_xticklabels()[i40]
    lab.set_color(SOUND)
    lab.set_fontweight("bold")
    # 39 and 41 sit one unit from 40; shift their labels outward so the three do not touch
    from matplotlib.transforms import ScaledTranslation
    for j, dx in ((freqs.index(39.0), -5), (freqs.index(41.0), 5)):
        lbl = ax.get_xticklabels()[j]
        lbl.set_transform(lbl.get_transform() + ScaledTranslation(dx / 72, 0, fig.dpi_scale_trans))
    ax.set_xlim(34, 46)
    ax.set_xlabel("Frequency analyzed (Hz)", fontsize=15, labelpad=5)
    save(fig, out, "fig_frequency")
    return {"freqs": freqs, "r": rs, "ci": cis}


def bootstrap_r(x, y, reps=50000, seed=20260809):
    rng = np.random.default_rng(seed)
    n = len(x)
    idx = rng.integers(0, n, size=(reps, n))
    X, Y = x[idx], y[idx]
    Xc = X - X.mean(1, keepdims=True)
    Yc = Y - Y.mean(1, keepdims=True)
    r = (Xc * Yc).sum(1) / np.sqrt((Xc**2).sum(1) * (Yc**2).sum(1))
    return [float(v) for v in np.percentile(r, [2.5, 97.5])]


def fig_measures(primary, out):
    meas = primary["common_position_measure_convergence"]["measures"]
    rows = []
    for key, label in [("plv", "PLV"), ("pli", "PLI"), ("wpli", "wPLI")]:
        m = meas[key]
        r = m["raw_association"]["pearson_r"]
        ci = m["bootstrap"]["raw_correlation_ci95"]
        rows.append((label, float(r), list(ci)))

    fig, ax = plt.subplots(figsize=PANEL)
    fig.subplots_adjust(left=0.21, right=0.97, bottom=0.19, top=0.96)
    _r_axis(ax, ylabel=False)
    for i, (label, r, (a, b)) in enumerate(rows):
        _dot(ax, i, r, a, b, i == 0)
        ax.text(i + 0.14, r, f"{r:.2f}", color=INK if i == 0 else INK_2, fontsize=14, va="center", ha="left",
                fontweight="bold" if i == 0 else "normal")
    ax.set_xticks(range(3))
    ax.set_xticklabels([r[0] for r in rows], fontsize=15, color=INK)
    ax.set_xlim(-0.55, 2.75)
    ax.set_xlabel("Phase measure", fontsize=15, labelpad=5)
    save(fig, out, "fig_measures")
    return rows


def fig_positions(primary, out):
    tps = primary["target_position_sensitivity_plv"]
    mult = primary["target_position_multiplicity_plv"]["positions"]
    order = ["cycles_3_to_4", "cycles_4_to_5", "cycles_5_to_6", "cycles_6_to_7", "cycles_7_to_8", "cycles_8_to_9"]
    fig, ax = plt.subplots(figsize=PANEL)
    fig.subplots_adjust(left=0.21, right=0.97, bottom=0.19, top=0.96)
    _r_axis(ax, ylabel=False)
    rows = []
    for i, k in enumerate(order):
        node = tps[k]
        r = node["raw_association"]["pearson_r"]
        a, b = node["bootstrap"]["raw_correlation_ci95"]
        _dot(ax, i, r, a, b, k == "cycles_4_to_5")
        rows.append({"position": k, "n": node["n_participants"], "r": r, "ci": [a, b],
                     "bonferroni_p": mult[k]["bonferroni_p_two_sided"]})
    ns = [r["n"] for r in rows]
    split = ns.index(27)
    ax.axvline(split - 0.5, color=HAIR, lw=1.2, zorder=0)
    ax.text((split - 1) / 2, -0.38, rf"$n$ = {ns[0]}", ha="center", va="center", fontsize=15, color=INK_2)
    ax.text((split + len(order) - 1) / 2, -0.38, rf"$n$ = {ns[split]}", ha="center", va="center", fontsize=15,
            color=INK_2)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([k.replace("cycles_", "").replace("_to_", "-") for k in order])
    ax.get_xticklabels()[order.index("cycles_4_to_5")].set_color(SOUND)
    ax.get_xticklabels()[order.index("cycles_4_to_5")].set_fontweight("bold")
    ax.set_xlim(-0.6, len(order) - 0.4)
    ax.set_xlabel("Later cycles used", fontsize=15, labelpad=5)
    save(fig, out, "fig_positions")
    return rows


# ----------------------------------------------------------------------------------------------
# Slide 3: protocol + group PLV in every 20-s window (cycles 1-5, shared by all 35)
# ----------------------------------------------------------------------------------------------
def load_windows(recon):
    rows = list(csv.DictReader(open(recon / "reconstructed_window_table.csv")))
    for r in rows:
        r["block"] = int(r["block"])
        r["half"] = int(r["half"])
        r["t0"] = int(r["start"]) / 250.0
        r["t1"] = int(r["end"]) / 250.0
        r["cycle_complete"] = r["cycle_complete"] == "True"
    return rows


def window_grand_average(rows, col="plv_40", cycles=range(1, 6)):
    groups = defaultdict(list)
    for r in rows:
        if r["block"] in cycles and r["cycle_complete"]:
            groups[(r["block"], r["condition"], r["half"], r["t0"], r["t1"])].append(float(r[col]))
    out = []
    for (blk, cond, half, t0, t1), vals in sorted(groups.items(), key=lambda kv: kv[0][3]):
        v = np.array(vals)
        out.append({"cycle": blk, "condition": cond, "half": half, "t0": t0, "t1": t1, "n": len(v),
                    "mean": float(v.mean()), "sem": float(v.std(ddof=1) / np.sqrt(len(v)))})
    return out


def fig_protocol(rows, out):
    ga = window_grand_average(rows)
    assert all(w["n"] == 35 for w in ga), "cycles 1-5 must be complete for every participant"
    t_first = min(w["t0"] for w in ga)

    fig = plt.figure(figsize=(9.0, 4.0))
    ax_t = fig.add_axes([0.1, 0.64, 0.88, 0.33])  # timeline
    ax_p = fig.add_axes([0.1, 0.165, 0.88, 0.42], sharex=ax_t)  # group PLV
    tmax = max(w["t1"] for w in ga)

    # --- timeline blocks (seconds from first sound onset) -------------------------------------
    ax_t.set_xlim(-6, tmax - t_first + 6)
    ax_t.set_ylim(0, 1)
    ax_t.axis("off")
    for w in ga:
        x0, x1 = w["t0"] - t_first, w["t1"] - t_first
        stim = w["condition"] == "stim"
        # the two 20-s halves of a sound block touch; a thin white rule marks the analysis split
        left = x0 + (0.0 if stim and w["half"] == 2 else 0.6)
        right = x1 - (0.0 if stim and w["half"] == 1 else 0.6)
        ax_t.add_patch(Rectangle((left, 0.06), right - left, 0.26, color=SOUND if stim else SILENCE, lw=0))
        if stim and w["half"] == 2 and w["cycle"] > 1:  # cycle 1 carries the "sound" label instead
            ax_t.plot([x0, x0], [0.06, 0.32], color="white", lw=0.9, ls=(0, (2, 2)))
    ax_t.text(20, 0.19, "sound", ha="center", va="center", fontsize=13, color="white", fontweight="bold")
    ax_t.text(50, 0.19, "silence", ha="center", va="center", fontsize=10.5, color="white", fontweight="bold")
    for c in range(1, 6):
        mid = (c - 1) * 60 + 30
        ax_t.text(mid, 0.45, f"cycle {c}", ha="center", va="center", fontsize=15, color=INK_2)

    def bracket(x0, x1, y, label, color):
        ax_t.plot([x0 + 1, x0 + 1, x1 - 1, x1 - 1], [y - 0.07, y, y, y - 0.07], color=color, lw=1.6,
                  solid_capstyle="butt")
        ax_t.text((x0 + x1) / 2, y + 0.1, label, ha="center", va="bottom", fontsize=15, color=color,
                  fontweight="bold")

    bracket(0, 120, 0.66, "Early: cycles 1-2", INK)
    bracket(180, 300, 0.66, "Later: cycles 4-5", INK)
    ax_t.text(150, 0.76, "gap", ha="center", va="bottom", fontsize=14.5, color=MUTED, style="italic")

    # --- group PLV per window ------------------------------------------------------------------
    for w in ga:
        x0, x1 = w["t0"] - t_first, w["t1"] - t_first
        stim = w["condition"] == "stim"
        color = SOUND if stim else SILENCE_LINE
        soft = SOUND_SOFT if stim else SILENCE_SOFT
        ax_p.add_patch(Rectangle((x0 + 1.2, w["mean"] - w["sem"]), x1 - x0 - 2.4, 2 * w["sem"], color=soft,
                                 lw=0, zorder=1))
        ax_p.plot([x0 + 1.2, x1 - 1.2], [w["mean"], w["mean"]], color=color, lw=2.6, solid_capstyle="butt",
                  zorder=2)
    ax_p.set_ylim(0.43, 0.63)
    yt = [0.45, 0.50, 0.55, 0.60]
    ax_p.set_yticks(yt)
    ax_p.set_yticklabels([f"{v:.2f}" for v in yt])
    ax_p.set_ylabel("40-Hz PLV (mean of 35)", fontsize=14, labelpad=6)
    xt = [0, 60, 120, 180, 240, 300]
    ax_p.set_xticks(xt)
    ax_p.set_xticklabels([str(v) for v in xt])
    ax_p.set_xlabel("Seconds from first sound onset", fontsize=15, labelpad=5)
    ax_p.tick_params(labelsize=14.5)
    save(fig, out, "fig_protocol")
    return ga


# ----------------------------------------------------------------------------------------------
# Title slide: one participant's whole session, window by window
# ----------------------------------------------------------------------------------------------
def fig_title_strip(rows, out, subject="sub-32"):
    ws = [r for r in rows if r["subject"] == subject and r["cycle_complete"]]
    ws.sort(key=lambda r: r["t0"])
    t_first = ws[0]["t0"]
    fig, ax = plt.subplots(figsize=(8.4, 2.35))
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.26, top=0.84)
    for r in ws:
        x0, x1 = (r["t0"] - t_first) / 60, (r["t1"] - t_first) / 60
        color = SOUND if r["condition"] == "stim" else SILENCE
        ax.add_patch(Rectangle((x0 + 0.015, 0), x1 - x0 - 0.03, float(r["plv_40"]), color=color, lw=0))
    handles = [Rectangle((0, 0), 1, 1, color=SOUND), Rectangle((0, 0), 1, 1, color=SILENCE)]
    ax.legend(handles, ["sound", "silence"], loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=2,
              fontsize=12, handlelength=1.0, handleheight=1.0, borderaxespad=0.2, columnspacing=1.2)
    ax.set_xlim(0, (ws[-1]["t1"] - t_first) / 60)
    ax.set_ylim(0, 0.85)
    ax.set_yticks([0, 0.4, 0.8])
    ax.set_yticklabels(["0", "0.4", "0.8"])
    ax.set_xticks(range(0, 10))
    ax.set_xlabel("Minutes", fontsize=13, labelpad=3)
    ax.set_ylabel("40-Hz PLV", fontsize=13, labelpad=4)
    ax.tick_params(labelsize=12)
    save(fig, out, "fig_title_strip")
    return {"subject": subject, "n_windows": len(ws),
            "plv": [(r["condition"], r["block"], round(float(r["plv_40"]), 4)) for r in ws]}


# ----------------------------------------------------------------------------------------------
# Slide 4: what PLV measures, shown on one real electrode-pair from sub-01, cycle 1
# ----------------------------------------------------------------------------------------------
def fig_phase(fd, out):
    """Two unit circles for one example pair. Bars outside the circle show how often the phase
    difference fell at each angle over the 20-s window (length 1 = what a uniform spread gives);
    the arrow inside is the mean phasor, whose length is that pair's PLV."""
    snip = fd["b_snippet"]
    fig = plt.figure(figsize=(5.2, 3.0))
    rows = [("stimulation", "Sound on", SOUND), ("silence", "Silence", SILENCE_LINE)]
    result = {"site_a": snip["site_a"], "site_b": snip["site_b"]}
    for i, (key, label, color) in enumerate(rows):
        s_ = snip[key]
        raw = np.array(s_["full_window_phase_difference_rad_decimated_50hz"])
        mean_vec = np.exp(1j * raw).mean()
        # the stored per-pair PLV uses every sample; the 50-Hz series drawn here must agree
        assert abs(abs(mean_vec) - s_["pair_plv_full_window"]) < 0.01
        edges = np.array(s_["phase_difference_histogram_36bins"]["bin_edges_rad"])
        counts = np.array(s_["phase_difference_histogram_36bins"]["counts"], dtype=float)
        share = counts / counts.sum() * len(counts)

        ax = fig.add_axes([0.02 + i * 0.5, 0.15, 0.46, 0.72])
        ax.set_aspect("equal")
        ax.axis("off")
        ax.add_patch(Circle((0, 0), 1.0, fill=False, ec=AXIS, lw=1.3))
        ax.plot([-1.0, 1.0], [0, 0], color=HAIR, lw=0.9, zorder=0)
        ax.plot([0, 0], [-1.0, 1.0], color=HAIR, lw=0.9, zorder=0)
        r0, scale = 1.06, 0.2
        for a0, a1, h in zip(edges[:-1], edges[1:], share):
            th = np.linspace(a0 + 0.012, a1 - 0.012, 8)
            r1 = r0 + scale * h
            xs = np.concatenate([r0 * np.cos(th), r1 * np.cos(th[::-1])])
            ys = np.concatenate([r0 * np.sin(th), r1 * np.sin(th[::-1])])
            ax.fill(xs, ys, color=color, alpha=0.55, lw=0)
        ax.annotate("", xy=(mean_vec.real, mean_vec.imag), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=3.0, mutation_scale=18,
                                    shrinkA=0, shrinkB=0))
        lim = max(r0 + scale * share.max() + 0.05, 1.75)
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        fig.text(0.25 + i * 0.5, 0.92, label, ha="center", va="bottom", fontsize=16, fontweight="bold",
                 color=INK)
        fig.text(0.25 + i * 0.5, 0.05, f"PLV = {abs(mean_vec):.2f}", ha="center",
                 va="center", fontsize=18, color=INK)
        if i == 0:
            ax.text(0.0, -0.55, "arrow length\n= PLV", ha="center", va="center", fontsize=11, color=MUTED,
                    linespacing=1.15)
        result[key] = {"pair_plv": s_["pair_plv_full_window"], "decimated_resultant": float(abs(mean_vec)),
                       "max_bin_share": float(share.max()),
                       "subject_mean_plv_200_pairs": s_["subject_window_plv_mean_200_pairs"]}
    save(fig, out, "fig_phase")
    return result


# ----------------------------------------------------------------------------------------------
# Slide 4: electrodes used
# ----------------------------------------------------------------------------------------------
POS = {
    "Fp1": (-0.31, 0.95), "Fp2": (0.31, 0.95),
    "F7": (-0.81, 0.59), "F3": (-0.41, 0.53), "Fz": (0.0, 0.48), "F4": (0.41, 0.53), "F8": (0.81, 0.59),
    "T7": (-1.0, 0.0), "C3": (-0.5, 0.0), "Cz": (0.0, 0.0), "C4": (0.5, 0.0), "T8": (1.0, 0.0),
    "P7": (-0.81, -0.59), "P3": (-0.41, -0.53), "Pz": (0.0, -0.48), "P4": (0.41, -0.53), "P8": (0.81, -0.59),
    "O1": (-0.31, -0.95), "O2": (0.31, -0.95),
}


def fig_headmap(primary, fd, out):
    prov = primary["provenance"]
    front, post = prov["frontal_channels"], prov["posterior_channels"]
    a1, a2 = fd["b_snippet"]["site_a"].split("-")
    b1, b2 = fd["b_snippet"]["site_b"].split("-")
    fig, ax = plt.subplots(figsize=(3.0, 3.2))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)
    R = 1.17
    ax.add_patch(Circle((0, 0), R, fill=False, ec=AXIS, lw=1.4))
    ax.add_patch(Polygon([[-0.13, R - 0.01], [0, R + 0.17], [0.13, R - 0.01]], closed=False, fill=False,
                         ec=AXIS, lw=1.4))
    for sx in (-1, 1):
        x_left = R + 0.01 if sx > 0 else -R - 0.13
        ax.add_patch(FancyBboxPatch((x_left, -0.2), 0.12, 0.4,
                                    boxstyle="round,pad=0.0,rounding_size=0.06", fill=False, ec=AXIS, lw=1.4))
    pair_electrodes = {a1, a2, b1, b2}
    R_DISC = 0.16
    # A straight F4-O2 line would run under P4 and read as F4-P4, so that signal is drawn as a bow.
    BOW = {("F4", "O2"): (1.25, -0.25)}
    t = np.linspace(0, 1, 400)
    for (p, q) in [(a1, a2), (b1, b2)]:
        e0, e1 = np.array(POS[p]), np.array(POS[q])
        if (p, q) in BOW:
            ctrl = np.array(BOW[(p, q)])
            pts = np.outer((1 - t) ** 2, e0) + np.outer(2 * (1 - t) * t, ctrl) + np.outer(t ** 2, e1)
        else:
            pts = np.outer(1 - t, e0) + np.outer(t, e1)
        for k, v in POS.items():
            if k in (p, q):
                continue
            edge = R_DISC if (k in front or k in post) else 0.065
            assert np.min(np.hypot(*(pts - np.array(v)).T)) > edge + 0.02, f"{p}-{q} line touches {k}"
        ax.plot(*pts.T, color=SIGNAL, lw=2.4, zorder=1, solid_capstyle="round")
    for name, (x, y) in POS.items():
        used = name in front or name in post
        if used and name in pair_electrodes:
            ax.add_patch(Circle((x, y), R_DISC, color=SIGNAL, zorder=2))
            ax.text(x, y, name, ha="center", va="center", fontsize=12, color="white", fontweight="bold",
                    zorder=3)
        elif used:
            ax.add_patch(Circle((x, y), R_DISC, facecolor="#D3E8EF", edgecolor=SIGNAL, lw=1.0, zorder=2))
            ax.text(x, y, name, ha="center", va="center", fontsize=12, color=SIGNAL, fontweight="bold",
                    zorder=3)
        else:
            ax.add_patch(Circle((x, y), 0.065, fill=False, ec=AXIS, lw=1.0, zorder=2))
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.3, 1.45)
    ax.set_aspect("equal")
    ax.axis("off")
    save(fig, out, "fig_headmap")
    return {"frontal": front, "posterior": post, "example_pair": [fd["b_snippet"]["site_a"], fd["b_snippet"]["site_b"]]}


# ----------------------------------------------------------------------------------------------
# Slide 2: the stimulus (40-Hz train of 1-ms, 5-kHz tone pips; Lahijanian et al. 2024)
# ----------------------------------------------------------------------------------------------
def fig_stimulus(out):
    fs = 400_000
    period, on, carrier = 0.025, 0.001, 5000.0
    t = np.arange(0, 0.1, 1 / fs)
    y = (np.mod(t, period) < on) * np.sin(2 * np.pi * carrier * t)

    fig = plt.figure(figsize=(5.7, 2.6))
    ax = fig.add_axes([0.03, 0.3, 0.6, 0.52])
    ax.plot(t * 1000, y, color=SOUND, lw=1.2)
    ax.set_xlim(-1.5, 101)
    ax.set_ylim(-1.3, 1.3)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Time (ms)", fontsize=15, labelpad=3)
    ax.tick_params(labelsize=14.5)
    ax.annotate("", xy=(25, 1.2), xytext=(0, 1.2),
                arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.0, shrinkA=0, shrinkB=0))
    ax.text(12.5, 1.3, "25 ms", ha="center", va="bottom", fontsize=15, color=INK_2)
    ax.add_patch(Rectangle((-1.2, -1.22), 2.8, 2.44, fill=False, ec=INK_2, lw=0.9, ls=(0, (2, 2))))

    tz = np.arange(-0.0003, 0.0014, 1 / fs)
    yz = ((tz >= 0) & (tz < on)) * np.sin(2 * np.pi * carrier * tz)
    axz = fig.add_axes([0.72, 0.3, 0.26, 0.52])
    axz.plot(tz * 1000, yz, color=SOUND, lw=1.5)
    axz.set_xlim(-0.3, 1.4)
    axz.set_ylim(-1.3, 1.3)
    axz.set_yticks([])
    axz.spines["left"].set_visible(False)
    axz.set_xticks([0, 1])
    axz.set_xlabel("Time (ms)", fontsize=15, labelpad=3)
    axz.tick_params(labelsize=14.5)
    axz.text(0.5, 1.3, "one pulse", ha="center", va="bottom", fontsize=15, color=INK_2)
    from matplotlib.patches import ConnectionPatch
    for ya, yb in ((1.22, 1.3), (-1.22, -1.3)):
        fig.add_artist(ConnectionPatch((1.6, ya), (-0.3, yb), "data", "data", axesA=ax, axesB=axz,
                                       color=AXIS, lw=0.9, ls=(0, (2, 2))))
    save(fig, out, "fig_stimulus")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--recon", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    repo, recon, out = Path(args.repo), Path(args.recon), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    primary = json.loads((repo / "results/metrics/early_late_connectivity_analysis.json").read_text())
    fig_json = json.loads((repo / "results/metrics/urtc_response_figure.json").read_text())
    fd = json.loads((recon / "figure_data.json").read_text())
    rows = load_windows(recon)

    info = {
        "scatter": fig_scatter(primary, out),
        "scatter_small": fig_scatter_small(primary, out),
        "frequency": fig_frequency(fig_json, primary, out),
        "measures": fig_measures(primary, out),
        "positions": fig_positions(primary, out),
        "protocol_grand_average": fig_protocol(rows, out),
        "title_strip": fig_title_strip(rows, out),
        "phase": fig_phase(fd, out),
        "headmap": fig_headmap(primary, fd, out),
    }
    fig_stimulus(out)
    (out / "figure_values.json").write_text(json.dumps(info, indent=2, default=float))
    print(json.dumps({k: info[k] for k in ("scatter", "measures", "phase", "headmap")}, indent=1, default=float))


if __name__ == "__main__":
    main()
