# AI-assisted code (Claude Code, 2026-10); reviewed and run by the student. See sts2026/AI_DISCLOSURE_LOG.md
"""Key figures for the STS report. Every value is read from the results files (nothing typed in).
Output: sts2026/figures/fig*.png (+ figure_data.json). Palette: validated reference categorical slots 1-3
(blue/orange/aqua; all-pairs safe for scatter), light surface, text in ink tokens (never series colours)."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

H = Path(__file__).resolve().parent
RES = H.parent / "results"
FIG = H.parent / "figures"
FIG.mkdir(exist_ok=True)
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
S1, S2, S3, NEUTRAL = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"
GROUPS = [("young_CN", "Young CN", S1, "o"), ("older_CN", "Older CN", S2, "s"), ("AD", "Mild AD", S3, "^")]
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
                     "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "text.color": INK, "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
                     "legend.frameon": False})
C = RES / "confirmatory"
E = RES / "exploratory_post"
data = {}


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / f"{name}.png", dpi=300)
    plt.close(fig)


def pivot(B, col, label, visit="P1"):
    s = B[(B.label == label) & (B.visit == visit) & (B.occurrence == 1)]
    return s.set_index("sid")[col]


B = pd.read_csv(C / "dv56_blocks_primary.csv")
grp = B.drop_duplicates("sid").set_index("sid").group
D48 = pd.read_csv(C / "ds005048_subjects_primary.csv")
R = json.load(open(C / "results.json"))
X = json.load(open(E / "results.json"))
H5 = json.load(open(C / "results_h5_S2_no_rejection.json"))
H5p = json.load(open(C / "results_h5_primary.json"))

# ---------------- Fig 1: audit - the old forecast skill is label construction + schedule
a1 = json.load(open(RES / "audit_block_label_artifact.json"))
a2 = json.load(open(RES / "audit_pac_forecast.json"))["Q3_pooled_R2"]
hb = [1, 3, 5, 10]
fig, ax = plt.subplots(figsize=(6.2, 3.6))
ax.plot(hb, [a1[f"h{h}s"]["persistence"] for h in hb], "-o", color=S1, lw=2, ms=8, label="Persistence on block labels")
ax.plot(hb, [a1[f"h{h}s"]["schedule_lookup"] for h in hb], "-s", color=S2, lw=2, ms=8,
        label="Zero-parameter schedule lookup on block labels")
hw = [2, 4, 6, 8, 10]
ax.plot(hw, [a2[f"h{i}_{2*i}s"]["running_subject_mean"] for i in range(1, 6)], "-^", color=S3, lw=2, ms=8,
        label="Best honest predictor, per-window PAC")
ax.axhline(0, color=INK2, lw=0.8)
ax.set_xlabel("Forecast horizon (s)"); ax.set_ylabel("Pooled R² (35 participants)")
ax.set_title("Original PAC 'forecast' skill is reproduced without any EEG model", fontsize=10, loc="left")
ax.legend(fontsize=8, loc="upper right")
save(fig, "fig1_audit_forecast_artifact")
data["fig1"] = dict(block=a1, per_window=a2)

# ---------------- Fig 2: the individual response is stable within a session (two cohorts)
fig, axs = plt.subplots(1, 2, figsize=(9, 4))
ax = axs[0]
ax.scatter(D48.R40_odd, D48.R40_even, s=40, color=S1, edgecolor=SURF, linewidth=1.5)
lim = [min(D48.R40_odd.min(), D48.R40_even.min()) - .05, max(D48.R40_odd.max(), D48.R40_even.max()) + .05]
ax.plot(lim, lim, color=NEUTRAL, lw=1, ls="--")
r = R["ds005048_discovery_reliability"]["split_half_odd_even"]
ax.set_title(f"A  Discovery (ds005048, n={r['n']})\nodd vs even blocks: ρ = {r['rho']:.2f} [{r['ci95'][0]:.2f}, {r['ci95'][1]:.2f}]",
             fontsize=9, loc="left")
ax.set_xlabel("R40, odd stimulation blocks"); ax.set_ylabel("R40, even stimulation blocks")
ax = axs[1]
A, AV = pivot(B, "R40", "periodic_A"), pivot(B, "R40", "periodic_AV")
for g, lab, col, mk in GROUPS:
    ids = [i for i in A.index if grp.get(i) == g and i in AV.index]
    ax.scatter(A[ids], AV[ids], s=44, color=col, marker=mk, edgecolor=SURF, linewidth=1.5, label=f"{lab} (n={len(ids)})")
lim = [-0.1, 1.0]
ax.plot(lim, lim, color=NEUTRAL, lw=1, ls="--")
p, u = R["primary"]["H1_primary_A_vs_AV_groupcentred"], R["primary"]["H1_uncentred"]
ax.set_title(f"B  Held-out (Chan et al. 2022 data, n={p['n']})\nρ = {u['rho']:.2f}; within-group ρ = {p['rho']:.2f} "
             f"[{p['ci95'][0]:.2f}, {p['ci95'][1]:.2f}]", fontsize=9, loc="left")
ax.set_xlabel("R40, 40 Hz clicks alone"); ax.set_ylabel("R40, 40 Hz clicks + light (separate block)")
ax.legend(fontsize=8, loc="lower right")
save(fig, "fig2_within_session_trait")

# ---------------- Fig 3: specificity - rhythm (periodic vs jittered) and frequency (40 vs 33 Hz control)
fig, axs = plt.subplots(1, 2, figsize=(9, 3.8), gridspec_kw={"width_ratios": [1, 1.3]})
ax = axs[0]
P, J = pivot(B, "R40", "periodic_A"), pivot(B, "R40", "random_A")
ids = [i for i in P.index if i in J.index and np.isfinite(P[i]) and np.isfinite(J[i])]
for i in ids:
    ax.plot([0, 1], [J[i], P[i]], color=NEUTRAL, lw=0.8, alpha=.7)
ax.scatter(np.zeros(len(ids)), J[ids], color=S2, s=30, zorder=3, edgecolor=SURF)
ax.scatter(np.ones(len(ids)), P[ids], color=S1, s=30, zorder=3, edgecolor=SURF)
ax.set_xticks([0, 1], ["Jittered clicks\n(±5 ms)", "Periodic\n40 Hz clicks"]); ax.set_xlim(-.4, 1.4)
h2c = R["primary"]["H2c_periodic_vs_random_CN"]
ax.set_ylabel("R40"); ax.set_title(f"A  Rhythm-specific (CN, n={h2c['n']}): d_z = {h2c['dz']:.1f}", fontsize=9, loc="left")
ax = axs[1]
labels = ["ds005048\n(discovery)", "Chan 2022\n(held-out)", "EESM19\n(held-out, S2)"]
v40 = [R["ds005048_discovery_reliability"]["first_vs_second_block"]["rho"], R["primary"]["H1_uncentred"]["rho"],
       H5["ICC_R40"]["icc3_1"]]
c40 = [R["ds005048_discovery_reliability"]["first_vs_second_block"]["ci95"], R["primary"]["H1_uncentred"]["ci95"],
       H5["ICC_R40"]["ci95"]]
v33 = [R["ds005048_discovery_reliability"]["NC_R33_odd_even"]["rho"], R["primary"]["NC1_R33_A_vs_AV"]["rho"],
       H5["ICC_R33"]["icc3_1"]]
c33 = [R["ds005048_discovery_reliability"]["NC_R33_odd_even"]["ci95"], R["primary"]["NC1_R33_A_vs_AV"]["ci95"],
       H5["ICC_R33"]["ci95"]]
x = np.arange(3)
for off, v, c, col, lab in [(-.17, v40, c40, S1, "40 Hz (stimulus)"), (.17, v33, c33, NEUTRAL, "33 Hz (no stimulus; control)")]:
    ax.bar(x + off, v, width=.3, color=col, label=lab)
    ax.errorbar(x + off, v, yerr=[[vv - cc[0] for vv, cc in zip(v, c)], [cc[1] - vv for vv, cc in zip(v, c)]],
                fmt="none", ecolor=INK2, lw=1, capsize=3)
ax.axhline(0, color=INK2, lw=.8)
ax.set_xticks(x, labels, fontsize=8); ax.set_ylabel("Reliability (ρ or ICC)")
ax.set_title("B  Reliability is specific to the stimulated frequency", fontsize=9, loc="left")
ax.set_ylim(-.45, 1.2)
ax.legend(fontsize=8, loc="upper center", ncol=2)
save(fig, "fig3_specificity")

# ---------------- Fig 4: stability across sessions (forest)
rows = [("AD, 0–4 months, before treatment (n=14)", R["primary"]["H3a_P1_to_P2Abaseline"]["icc3_1"], R["primary"]["H3a_P1_to_P2Abaseline"]["ci95"]),
        ("AD, 3 months, active or sham (n=14)", R["primary"]["H3b_P2Abaseline_to_3mo"]["icc3_1"], R["primary"]["H3b_P2Abaseline_to_3mo"]["ci95"]),
        ("Young, 2 nights (n=20; registered rule)", H5p["ICC_R40_first_two_nights"]["icc3_1"], H5p["ICC_R40_first_two_nights"]["ci95"]),
        ("Young, 4 nights (n=16; sensitivity S2)", H5["ICC_R40"]["icc3_1"], H5["ICC_R40"]["ci95"])]
fig, ax = plt.subplots(figsize=(7.6, 3.4))
for i, (lab, v, c) in enumerate(rows[::-1]):
    ax.plot(c, [i, i], color=INK2, lw=1.2)
    ax.plot(v, i, "o", color=S1, ms=8)
ax.axvline(0, color=INK2, lw=.8); ax.axvline(0.5, color=NEUTRAL, lw=1, ls="--")
ax.text(0.52, -0.45, "pre-registered bar (ICC 0.5)", color=INK2, fontsize=8, ha="left", va="center")
ax.set_yticks(range(len(rows)), [r[0] for r in rows[::-1]], fontsize=8)
ax.set_xlabel("ICC(3,1) of R40 across sessions, with 95% bootstrap CI"); ax.set_xlim(-.4, 1)
ax.set_ylim(-.8, len(rows) - .5)
ax.set_title("Across sessions: moderate, imprecise stability", fontsize=10, loc="left")
save(fig, "fig4_across_session_stability")

# ---------------- Fig 5: recording noise lowers the measured response (3 cohorts) + H4 is a noise proxy
N56 = pd.read_csv(E / "gamma_noise_silence.csv").set_index("sid")
N48 = pd.read_csv(E / "ds005048_gamma_noise_silence.csv").set_index("sid")
S185 = pd.read_csv(C / "ds005185_sessions_S2_no_rejection.csv").dropna(subset=["R40"])
fig, axs = plt.subplots(1, 3, figsize=(11, 3.6), sharey=False)
d = D48.set_index("sid").join(N48)
axs[0].scatter(d.noise, d.R40, color=S1, s=36, edgecolor=SURF)
axs[0].set_title(f"A  ds005048: ρ = {stats.spearmanr(d.noise, d.R40)[0]:.2f}", fontsize=9, loc="left")
t = pd.concat([A, N56.gamma_noise_silence, grp], axis=1, keys=["R40", "noise", "g"]).dropna()
for g, lab, col, mk in GROUPS:
    s = t[t.g == g]
    axs[1].scatter(s.noise, s.R40, color=col, marker=mk, s=40, edgecolor=SURF, label=lab)
axs[1].legend(fontsize=7, loc="upper right")
axs[1].set_title(f"B  Chan 2022: ρ = {stats.spearmanr(t.noise, t.R40)[0]:.2f}", fontsize=9, loc="left")
axs[2].scatter(S185.noise, S185.R40, color=S1, s=26, edgecolor=SURF)
axs[2].set_title(f"C  EESM19 (sessions): ρ = {stats.spearmanr(S185.noise, S185.R40)[0]:.2f}", fontsize=9, loc="left")
axs[0].set_xlabel("noise in silence")
axs[1].set_xlabel("noise in silence")
axs[2].set_xlabel("noise during sound (35–38, 42–45 Hz)")
fig.supxlabel("log10 gamma-band noise power (35–45 Hz, excluding 39–41 Hz)", fontsize=9, color=INK2)
axs[0].set_ylabel("R40")
fig.suptitle("Noisier recordings show weaker measured 40 Hz responses in all three cohorts", x=.01, ha="left", fontsize=10)
save(fig, "fig5_noise_confound")

# ---------------- Fig 6: group comparisons vs published 'enhanced in AD' claims (forest)
e3 = X["E3_pooled_AD_effect"]
rows = [("Older vs young CN (Chan 2022)", R["primary"]["H2a_older_vs_young"]["hedges_g"], R["primary"]["H2a_older_vs_young"]["g_ci95"]),
        ("Mild AD vs older CN (Chan 2022)", R["primary"]["H2b_AD_vs_older"]["hedges_g"], R["primary"]["H2b_AD_vs_older"]["g_ci95"]),
        ("Mild AD vs normal (ds005048)", e3["ds005048_mildAD_vs_normal"]["g"],
         [e3["ds005048_mildAD_vs_normal"]["g"] - 1.96 * e3["ds005048_mildAD_vs_normal"]["se"],
          e3["ds005048_mildAD_vs_normal"]["g"] + 1.96 * e3["ds005048_mildAD_vs_normal"]["se"]]),
        ("AD vs controls, pooled (2 cohorts)", e3["fixed_effect_pooled"]["g"], e3["fixed_effect_pooled"]["ci95"])]
fig, ax = plt.subplots(figsize=(7, 3.0))
for i, (lab, v, c) in enumerate(rows[::-1]):
    ax.plot(c, [i, i], color=INK2, lw=1.2)
    ax.plot(v, i, "D" if "pooled" in lab else "o", color=S2 if "pooled" in lab else S1, ms=8)
ax.axvline(0, color=INK2, lw=.8)
ax.set_yticks(range(len(rows)), [r[0] for r in rows[::-1]], fontsize=8)
ax.set_xlabel("Hedges g (negative = weaker 40 Hz response), 95% CI")
ax.set_title("No support for an enhanced 40 Hz response in AD or aging", fontsize=10, loc="left")
save(fig, "fig6_group_claims")

json.dump(data, open(FIG / "figure_data.json", "w"), indent=1, default=float)
print("figures:", sorted(p.name for p in FIG.glob("*.png")))
