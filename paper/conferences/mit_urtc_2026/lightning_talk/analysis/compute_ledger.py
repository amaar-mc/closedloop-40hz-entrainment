"""Compute the canonical claims ledger for the URTC 2026 Lightning Talk (ID-1269).

Read-only with respect to the repo. Writes computed.json next to this script.
Run with: .venv-reliability/bin/python compute_ledger.py
"""
import csv
import hashlib
import json
import os
from pathlib import Path

import numpy as np
from scipy import stats

REPO = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
MAIN = REPO / "results/metrics/early_late_connectivity_analysis.json"
ONE = REPO / "results/metrics/early_late_connectivity_one_cycle_analysis.json"
GATE = REPO / "results/metrics/early_response_gate.json"
FIG = REPO / "results/metrics/urtc_response_figure.json"
PTSV = REPO / "data/raw/ds005048/participants.tsv"
SEED = 20260809
B = 50000


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rvec(x, y):
    xm = x - x.mean(-1, keepdims=True)
    ym = y - y.mean(-1, keepdims=True)
    return (xm * ym).sum(-1) / np.sqrt((xm ** 2).sum(-1) * (ym ** 2).sum(-1))


def boot_idx(n, seed=SEED, reps=B):
    return np.random.default_rng(seed).integers(0, n, (reps, n))


def pct(a, lo=2.5, hi=97.5):
    return [float(v) for v in np.percentile(a, [lo, hi])]


def corr_summary(x, y):
    r, p = stats.pearsonr(x, y)
    rho, sp = stats.spearmanr(x, y)
    return {"n": int(len(x)), "pearson_r": float(r), "pearson_p": float(p),
            "spearman_rho": float(rho), "spearman_p": float(sp)}


main = json.load(open(MAIN))
one = json.load(open(ONE))
gate = json.load(open(GATE))
fig = json.load(open(FIG))
out = {"inputs": {str(p.relative_to(REPO)): sha(p) for p in [MAIN, ONE, GATE, FIG, PTSV]},
       "bootstrap_method": ("numpy.random.default_rng(seed).integers(0, n, (50000, n)) participant resampling; "
                            "Pearson r per replicate; np.percentile 2.5/97.5. This exact method reproduces "
                            "urtc_response_figure.json frequency_bootstrap_ci95 bit-for-bit with seed 20260812 "
                            "(shared resample indices across frequencies)."),
       "seed": SEED, "reps": B}

# ---------- verify figure-JSON reproduction (validates bootstrap method) ----------
cpf = main["common_position_frequency_specificity_plv"]
freqs = cpf["values"]["frequencies_hz"]
E = np.array(cpf["values"]["early_by_frequency"])
L = np.array(cpf["values"]["late_by_frequency"])
subj = cpf["values"]["subjects"]
idx_fig = boot_idx(35, 20260812)
fig_repro = [pct(rvec(E[idx_fig, j], L[idx_fig, j])) for j in range(7)]
out["figure_ci_reproduction"] = {
    "seed": 20260812,
    "reproduced": fig_repro,
    "stored": fig["frequency_bootstrap_ci95"],
    "max_abs_diff": float(np.max(np.abs(np.array(fig_repro) - np.array(fig["frequency_bootstrap_ci95"])))),
}

# ---------- primary endpoint arrays ----------
t45 = main["target_position_sensitivity_plv"]["cycles_4_to_5"]
e = np.array(t45["values"]["early"])
l = np.array(t45["values"]["late"])
subs = t45["values"]["subject"]
assert subs == subj and np.allclose(e, E[:, 3]) and np.allclose(l, L[:, 3])

# Monte Carlo variability of the primary CI across seeds (stored CI not bit-reproducible: script lost)
mc = {}
for s in [20260809, 20260810, 20260811, 20260812, 20260813, 20260814, 20269809]:
    idx = boot_idx(35, s)
    mc[str(s)] = pct(rvec(e[idx], l[idx]))
out["primary_ci_seed_variability"] = {
    "stored": t45["bootstrap"]["raw_correlation_ci95"],
    "recomputed_by_seed": mc,
    "lower_range": [min(v[0] for v in mc.values()), max(v[0] for v in mc.values())],
    "upper_range": [min(v[1] for v in mc.values()), max(v[1] for v in mc.values())],
}

# ---------- item 3: derived per-participant ----------
d3 = {}
d3["n"] = len(e)
d3["early_positive"] = int((e > 0).sum())
d3["late_positive"] = int((l > 0).sum())
d3["both_positive"] = int(((e > 0) & (l > 0)).sum())
d3["both_nonpositive"] = int(((e <= 0) & (l <= 0)).sum())
d3["early_pos_late_nonpos"] = int(((e > 0) & (l <= 0)).sum())
d3["early_nonpos_late_pos"] = int(((e <= 0) & (l > 0)).sum())
d3["sign_agreement"] = d3["both_positive"] + d3["both_nonpositive"]
d3["early_positive_subjects_nonpos_late"] = [s for s, a, b in zip(subs, e, l) if a > 0 and b <= 0]
d3["early_nonpos_subjects_late_pos"] = [s for s, a, b in zip(subs, e, l) if a <= 0 and b > 0]
d3["early_nonpos_subjects"] = [s for s, a in zip(subs, e) if a <= 0]
d3["late_nonpos_subjects"] = [s for s, b in zip(subs, l) if b <= 0]
for name, arr in [("early", e), ("late", l)]:
    d3[name + "_summary"] = {"min": float(arr.min()), "min_subject": subs[int(arr.argmin())],
                             "max": float(arr.max()), "max_subject": subs[int(arr.argmax())],
                             "median": float(np.median(arr)), "mean": float(arr.mean()),
                             "sd": float(arr.std(ddof=1))}
# regression diagnostics late ~ early
n = len(e)
X = np.column_stack([np.ones(n), e])
beta, *_ = np.linalg.lstsq(X, l, rcond=None)
H = X @ np.linalg.inv(X.T @ X) @ X.T
h = np.diag(H)
resid = l - X @ beta
mse = (resid ** 2).sum() / (n - 2)
cook = resid ** 2 / (2 * mse) * h / (1 - h) ** 2
stud = resid / np.sqrt(mse * (1 - h))
order_h = np.argsort(-h)
order_c = np.argsort(-cook)
d3["ols_late_on_early"] = {"intercept": float(beta[0]), "slope": float(beta[1])}
d3["leverage_rank"] = [{"subject": subs[i], "early": float(e[i]), "late": float(l[i]), "hat": float(h[i]),
                        "cooks_d": float(cook[i]), "studentized_resid": float(stud[i])} for i in order_h[:6]]
d3["cooks_rank"] = [{"subject": subs[i], "early": float(e[i]), "late": float(l[i]), "hat": float(h[i]),
                     "cooks_d": float(cook[i])} for i in order_c[:6]]
d3["hat_threshold_2p_over_n"] = 4 / n
d3["cooks_threshold_4_over_n"] = 4 / n
d3["full"] = corr_summary(e, l)


def drop(names):
    m = np.array([s not in names for s in subs])
    res = corr_summary(e[m], l[m])
    idx = boot_idx(int(m.sum()))
    res["bootstrap_ci95_seed20260809"] = pct(rvec(e[m][idx], l[m][idx]))
    res["dropped"] = names
    return res


top1 = [subs[order_h[0]]]
top2 = [subs[order_h[0]], subs[order_h[1]]]
ctop1 = [subs[order_c[0]]]
ctop2 = [subs[order_c[0]], subs[order_c[1]]]
d3["drop_top1_leverage"] = drop(top1)
d3["drop_top2_leverage"] = drop(top2)
d3["drop_top1_cooks"] = drop(ctop1)
d3["drop_top2_cooks"] = drop(ctop2)
d3["drop_sub01_sub05"] = drop(["sub-01", "sub-05"])
d3["drop_unlabeled_sub06_sub13"] = drop(["sub-06", "sub-13"])
out["item3_derived"] = d3

# ---------- item 4: cohort ----------
rows = list(csv.DictReader(open(PTSV), delimiter="\t"))
groups = {}
for r in rows:
    groups.setdefault(r["Group"], []).append(r)
ages = np.array([float(r["Age"]) for r in rows])
coh = {"n_rows": len(rows),
       "group_counts": {g: len(v) for g, v in groups.items()},
       "group_subjects": {g: [r["participant_id"] for r in v] for g, v in groups.items()},
       "sex_counts": {s: sum(r["Gender"] == s for r in rows) for s in sorted({r["Gender"] for r in rows})},
       "age": {"mean": float(ages.mean()), "sd_ddof1": float(ages.std(ddof=1)), "min": float(ages.min()),
               "max": float(ages.max()), "median": float(np.median(ages))},
       "per_group": {}}
for g, v in groups.items():
    a = np.array([float(r["Age"]) for r in v])
    mm = [float(r["MMSE"]) for r in v if r["MMSE"] not in ("-", "", "n/a")]
    coh["per_group"][g] = {"n": len(v),
                           "female": sum(r["Gender"] == "Female" for r in v),
                           "male": sum(r["Gender"] == "Male" for r in v),
                           "age_mean": float(a.mean()), "age_min": float(a.min()), "age_max": float(a.max()),
                           "mmse_min": min(mm) if mm else None, "mmse_max": max(mm) if mm else None,
                           "mmse_mean": float(np.mean(mm)) if mm else None}
mm_all = [float(r["MMSE"]) for r in rows if r["MMSE"] not in ("-", "")]
coh["mmse_all_labeled"] = {"n": len(mm_all), "min": min(mm_all), "max": max(mm_all), "mean": float(np.mean(mm_all)),
                           "sd_ddof1": float(np.std(mm_all, ddof=1))}
# protocol cohorts from events.tsv
proto = {}
for s in subs:
    ev = list(csv.DictReader(open(REPO / f"data/raw/ds005048/{s}/eeg/{s}_task-40HzAuditoryEntrainment_events.tsv"),
                             delimiter="\t"))
    stim = [x for x in ev if x["trial_type"] == "Stimulus"]
    rest = [x for x in ev if x["trial_type"] == "Rest"]
    complete_rest = [x for x in rest if float(x["duration"]) >= 20]
    proto[s] = {"n_stim": len(stim), "n_rest": len(rest), "n_complete_rest": len(complete_rest),
                "stim_durations": sorted({float(x["duration"]) for x in stim}),
                "last_rest_duration": float(rest[-1]["duration"]) if rest else None}
coh["protocol_from_events"] = proto
six = [s for s in subs if proto[s]["n_stim"] == 6]
ten = [s for s in subs if proto[s]["n_stim"] == 10]
coh["six_block_subjects"] = six
coh["ten_block_subjects"] = ten
coh["other_block_counts"] = sorted({proto[s]["n_stim"] for s in subs} - {6, 10})
coh["cycles_5_to_6_subjects_equal_ten_block"] = sorted(
    main["target_position_sensitivity_plv"]["cycles_5_to_6"]["values"]["subject"]) == sorted(ten)
lab = {r["participant_id"]: r for r in rows}
coh["six_block_groups"] = {s: lab[s]["Group"] for s in six}
coh["n_complete_cycles_min"] = min(p["n_complete_rest"] for p in proto.values())
coh["n_complete_cycles_six_block"] = sorted({proto[s]["n_complete_rest"] for s in six})
coh["n_complete_cycles_ten_block"] = sorted({proto[s]["n_complete_rest"] for s in ten})
out["item4_cohort"] = coh

# labeled-only primary r and per-group
grp_of = {s: lab[s]["Group"] for s in subs}
pg = {}
for g in ["Normal", "MCI", "Mild AD", "Moderate AD", "-"]:
    m = np.array([grp_of[s] == g for s in subs])
    if m.sum() >= 3:
        pg[g] = corr_summary(e[m], l[m])
    else:
        pg[g] = {"n": int(m.sum()), "note": "too few for correlation"}
out["item3_by_group_descriptive"] = pg
# protocol cohort r check
for nm, lst in [("six", six), ("ten", ten)]:
    m = np.array([s in lst for s in subs])
    out.setdefault("protocol_cohort_recheck", {})[nm] = corr_summary(e[m], l[m])

# ---------- item 5: frequency specificity ----------
idx = boot_idx(35, SEED)
Rb = np.stack([rvec(E[idx, j], L[idx, j]) for j in range(7)], axis=1)  # (B,7)
r_point = [float(stats.pearsonr(E[:, j], L[:, j])[0]) for j in range(7)]
ctrl = [j for j in range(7) if freqs[j] != 40.0]
diffs = Rb[:, [3]] - Rb[:, ctrl]
k = len(ctrl)
fam_lo, fam_hi = 100 * 0.025 / k, 100 * (1 - 0.025 / k)
f5 = {"frequencies_hz": freqs,
      "r_point": r_point,
      "spearman_point": [float(stats.spearmanr(E[:, j], L[:, j])[0]) for j in range(7)],
      "pearson_p_point": [float(stats.pearsonr(E[:, j], L[:, j])[1]) for j in range(7)],
      "boot_ci95_seed20260809": [pct(Rb[:, j]) for j in range(7)],
      "boot_ci95_stored_fig_seed20260812": fig["frequency_bootstrap_ci95"],
      "pairwise": {}}
for c, j in enumerate(ctrl):
    key = f"{int(freqs[j])}_hz"
    st = cpf["statistics"]["pairwise_participant_bootstrap"][key]
    f5["pairwise"][key] = {
        "control_r": r_point[j],
        "diff_point": r_point[3] - r_point[j],
        "boot_ci95_recomputed": pct(diffs[:, c]),
        "bonferroni_ci_recomputed": pct(diffs[:, c], fam_lo, fam_hi),
        "boot_ci95_stored": st["bootstrap_ci95"],
        "bonferroni_ci_stored": st["bonferroni_familywise_ci95"],
        "boot_prop_diff_le_0": float((diffs[:, c] <= 0).mean()),
    }
mind = diffs.min(axis=1)
f5["min_diff_point"] = float(min(r_point[3] - r_point[j] for j in ctrl))
f5["min_diff_point_vs"] = f"{int(freqs[ctrl[int(np.argmin([r_point[3]-r_point[j] for j in ctrl]))]])} Hz"
f5["min_diff_boot_ci95_recomputed"] = pct(mind)
f5["min_diff_boot_ci95_stored"] = cpf["statistics"]["bootstrap_minimum_difference_ci95"]
f5["prop_boot_40_is_max"] = float((Rb[:, 3] > Rb[:, ctrl].max(axis=1)).mean())
f5["bonferroni_percentiles"] = [fam_lo, fam_hi]
out["item5_frequency"] = f5

# ---------- item 6: alt measures ----------
f6 = {}
for m_ in ["plv", "pli", "wpli"]:
    blk = main["common_position_measure_convergence"]["measures"][m_]
    x = np.array(blk["values"]["early"]); y = np.array(blk["values"]["late"])
    assert blk["values"]["subject"] == subs
    idx = boot_idx(35, SEED)
    f6[m_] = {"recomputed": corr_summary(x, y), "stored_raw_association": blk["raw_association"],
              "boot_ci95_seed20260809": pct(rvec(x[idx], y[idx])),
              "boot_ci95_stored": blk["bootstrap"]["raw_correlation_ci95"],
              "early_positive": int((x > 0).sum()), "late_positive": int((y > 0).sum())}
out["item6_measures"] = f6

# ---------- item 7 recheck ----------
f7 = {}
for pos, t in main["target_position_sensitivity_plv"].items():
    x = np.array(t["values"]["early"]); y = np.array(t["values"]["late"])
    f7[pos] = corr_summary(x, y)
out["item7_recheck"] = f7

json.dump(out, open(OUT / "computed.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str)[:200])
