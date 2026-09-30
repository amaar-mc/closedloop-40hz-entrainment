# AI-assisted code (Claude Code, 2026-10); reviewed and run by the student. See sts2026/AI_DISCLOSURE_LOG.md
"""EXPLORATORY (post-registration; NOT confirmatory). Validity checks prompted by the confirmatory results.

E1  H4 moonshot: does the cross-cohort prediction hold WITHIN groups (i.e., beyond young-vs-old separation)?
    Group-centred r; AD-only and CN-only r; a negative-control target (R33).
E2  Artifact checks for 56XZ3F: the covered strobe ran at 40 Hz during some 'silent' baselines and during
    audio-only blocks. (a) R40 in silent baselines with covered strobe at 40 Hz vs 0 Hz (from the notes);
    (b) R40 on the unconnected EXG5-8 inputs during periodic audio; (c) topography of R40 in periodic audio.
E3  Pooled AD-vs-control effect across both cohorts (ds005048 mild AD vs Normal; 56XZ3F AD vs older CN).
"""
import json, glob, os, re, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import confirmatory as C
from dv56_io import schedule, ROOT, BIOSEMI32

OUT = HERE.parent / "results" / "exploratory_post"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(7)


def e1():
    D = pd.read_csv(C.OUT / "ds005048_subjects_primary.csv").rename(columns={"Age": "age"})
    F = pd.read_csv(C.OUT / "dv56_prestim_features.csv").set_index("sid")
    B = pd.read_csv(C.OUT / "dv56_blocks_primary.csv")
    A = C.pivot(B, "R40", "periodic_A")
    A33 = C.pivot(B, "R33", "periodic_A")
    F = F.join(A.rename("R40")).join(A33.rename("R33")).join(pd.read_csv(C.OUT / "dv56_ages.csv").set_index("sid"))
    F = F.dropna(subset=["R40"])
    feats = ["aper_exp", "aper_off", "iaf", "rel40", "age"]
    z = lambda s: (s - s.mean()) / s.std()
    Xtr = D[feats].apply(pd.to_numeric, errors="coerce"); Xtr = Xtr.fillna(Xtr.mean()).apply(z).values
    from sklearn.linear_model import Ridge
    m = Ridge(alpha=1.0).fit(Xtr, z(D.R40).values)
    Xte = F[feats].apply(pd.to_numeric, errors="coerce"); Xte = Xte.fillna(Xte.mean()).apply(z).values
    F["pred"] = m.predict(Xte)
    out = {}
    for g in ["young_CN", "older_CN", "AD"]:
        s = F[F.group == g]
        out[f"r_within_{g}"] = dict(r=float(stats.pearsonr(s.pred, s.R40)[0]), n=len(s),
                                    p=float(stats.pearsonr(s.pred, s.R40)[1]))
    Fc = F.copy()
    for c in ["pred", "R40"]:
        Fc[c] = F[c] - F.groupby("group")[c].transform("mean")
    r = stats.pearsonr(Fc.pred, Fc.R40)[0]
    perm = [stats.pearsonr(Fc.pred, rng.permutation(Fc.R40.values))[0] for _ in range(10000)]
    out["r_group_centred"] = dict(r=float(r), p_perm_one_sided=float((1 + np.sum(np.array(perm) >= r)) / 10001),
                                  n=len(Fc))
    out["r_pred_vs_R33_negative_control"] = float(stats.pearsonr(F.pred, F.R33)[0])
    out["univariate_spearman_all"] = {c: float(stats.spearmanr(F[c], F.R40, nan_policy="omit")[0]) for c in feats}
    out["univariate_spearman_groupcentred"] = {
        c: float(stats.spearmanr(F[c] - F.groupby("group")[c].transform("mean"), Fc.R40, nan_policy="omit")[0])
        for c in feats[:4]}
    out["group_means_R40"] = F.groupby("group").R40.mean().to_dict()
    out["group_means_aper_exp"] = F.groupby("group").aper_exp.mean().to_dict()
    return out


def e2():
    import mne
    mne.set_log_level("ERROR")
    rows, topo = [], []
    for bdf in sorted(glob.glob(str(ROOT / "Phase1_*/*/*stim_on*.bdf"))):
        if "hour" in bdf:
            continue
        d = os.path.dirname(bdf)
        notes = glob.glob(d + "/*Notes.txt")[0]
        sid = re.search(r"(Y\d+|E\d+|HG\d+)_EEG", bdf).group(1)
        raw = mne.io.read_raw_bdf(bdf, preload=True)
        sch, _ = schedule(bdf, notes, raw=raw)
        if sch is None:
            continue
        fs = raw.info["sfreq"]
        exg = raw.copy().pick(["EXG5", "EXG6", "EXG7", "EXG8"]).get_data() * 1e6
        raw.pick([f"A{i}" for i in range(1, 33)])
        raw.rename_channels({f"A{i}": BIOSEMI32[i - 1] for i in range(1, 33)})
        raw.filter(1.0, None, fir_design="firwin")
        x = raw.get_data() * 1e6
        x = x - x.mean(0, keepdims=True)
        roi = x[[raw.ch_names.index(c) for c in C.ROI]]
        for b in sch:
            desc = b["desc"].lower()
            if b["label"] == "baseline":
                strobe = "40" if "strobe frequency 40hz" in desc else "0" if "strobe frequency 0hz" in desc else "na"
                r = C.response(roi, fs, b["start"], b["stop"])
                rows.append(dict(sid=sid, kind=f"baseline_strobe{strobe}", R40=r["R40"]))
            if b["label"] == "periodic_A":
                r = C.response(roi, fs, b["start"], b["stop"])
                re_ = C.response(exg, fs, b["start"], b["stop"], reject=False)
                rows.append(dict(sid=sid, kind="periodic_A_scalpROI", R40=r["R40"]))
                rows.append(dict(sid=sid, kind="periodic_A_EXG5-8_unconnected", R40=re_["R40"]))
                t = {}
                for ch in raw.ch_names:
                    t[ch] = C.response(x[[raw.ch_names.index(ch)]], fs, b["start"], b["stop"])["R40"]
                topo.append(dict(sid=sid, **t))
                break
    R = pd.DataFrame(rows)
    T = pd.DataFrame(topo)
    T.to_csv(OUT / "topography_periodic_audio_R40.csv", index=False)
    out = {"median_R40_by_kind": R.groupby("kind").R40.median().to_dict(),
           "n_by_kind": R.groupby("kind").R40.count().to_dict()}
    p = R.pivot_table(index="sid", columns="kind", values="R40", aggfunc="mean")
    if {"baseline_strobe40", "baseline_strobe0"} <= set(p.columns):
        q = p[["baseline_strobe40", "baseline_strobe0"]].dropna()
        out["strobe40_vs_strobe0_baseline"] = dict(median_diff=float((q.iloc[:, 0] - q.iloc[:, 1]).median()), n=len(q),
                                                   p=float(stats.wilcoxon(q.iloc[:, 0] - q.iloc[:, 1]).pvalue))
    out["topography_median_R40"] = T.drop(columns="sid").median().sort_values(ascending=False).round(3).to_dict()
    return out


def e3():
    D = pd.read_csv(C.OUT / "ds005048_subjects_primary.csv")
    B = pd.read_csv(C.OUT / "dv56_blocks_primary.csv")
    A1 = C.pivot(B, "R40_1min", "periodic_A")
    grp = B.drop_duplicates("sid").set_index("sid").group
    res = {}
    effs = []
    for name, a, b in [("ds005048_mildAD_vs_normal", D[D.Group == "Mild AD"].R40.values, D[D.Group == "Normal"].R40.values),
                       ("dv56_AD_vs_olderCN", A1[grp.reindex(A1.index) == "AD"].dropna().values,
                        A1[grp.reindex(A1.index) == "older_CN"].dropna().values)]:
        g = C.hedges_g(a, b)
        na, nb = len(a), len(b)
        v = (na + nb) / (na * nb) + g ** 2 / (2 * (na + nb))
        effs.append((g, v))
        res[name] = dict(g=float(g), se=float(np.sqrt(v)), n_AD=na, n_ctrl=nb,
                         p_mwu=float(stats.mannwhitneyu(a, b).pvalue))
    w = np.array([1 / v for _, v in effs]); gs = np.array([g for g, _ in effs])
    gp = float(np.sum(w * gs) / np.sum(w)); se = float(np.sqrt(1 / np.sum(w)))
    Q = float(np.sum(w * (gs - gp) ** 2))
    res["fixed_effect_pooled"] = dict(g=gp, ci95=[gp - 1.96 * se, gp + 1.96 * se], z_p=float(2 * stats.norm.sf(abs(gp / se))),
                                      Q=Q, note="2 studies; fixed effect; ds005048 grouping was seen during discovery")
    return res


if __name__ == "__main__":
    res = {"E1_H4_within_group": e1(), "E3_pooled_AD_effect": e3(), "E2_artifact_checks": e2()}
    json.dump(res, open(OUT / "results.json", "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


def e4():
    """Noise confound: gamma-band noise floor in silence vs R40; noise-controlled trait reliability and H4."""
    import mne
    from scipy.signal import welch
    mne.set_log_level("ERROR")
    rows = []
    for bdf in sorted(glob.glob(str(ROOT / "Phase1_*/*/*stim_on*.bdf"))):
        if "hour" in bdf or "_2.bdf" in bdf:
            continue
        d = os.path.dirname(bdf)
        notes = glob.glob(d + "/*Notes.txt")[0]
        sid = re.search(r"(Y\d+|E\d+|HG\d+)_EEG", bdf).group(1)
        raw = mne.io.read_raw_bdf(bdf, preload=True)
        sch, _ = schedule(bdf, notes, raw=raw)
        if sch is None or sch[0]["label"] != "baseline":
            continue
        fs = raw.info["sfreq"]
        raw.pick([f"A{i}" for i in range(1, 33)])
        raw.rename_channels({f"A{i}": BIOSEMI32[i - 1] for i in range(1, 33)})
        raw.filter(1.0, None, fir_design="firwin")
        x = raw.get_data() * 1e6
        x = x - x.mean(0, keepdims=True)
        roi = x[[raw.ch_names.index(c) for c in C.ROI]].mean(0)
        a, b = sch[0]["start"] + int(2 * fs), sch[0]["stop"] - int(fs)
        f, P = welch(roi[a:b], fs=fs, nperseg=int(2 * fs))
        m = ((f >= 35) & (f <= 45)) & ~((f >= 39) & (f <= 41))
        noise = float(np.log10(P[m].mean()))
        rows.append(dict(sid=sid, gamma_noise_silence=noise))
    N = pd.DataFrame(rows).set_index("sid")
    B = pd.read_csv(C.OUT / "dv56_blocks_primary.csv")
    grp = B.drop_duplicates("sid").set_index("sid").group
    A = C.pivot(B, "R40", "periodic_A"); AV = C.pivot(B, "R40", "periodic_AV")
    T = pd.concat([A, AV, N.gamma_noise_silence, grp], axis=1, keys=["A", "AV", "noise", "g"]).dropna()
    for c in ["A", "AV", "noise"]:
        T[c + "_c"] = T[c] - T.groupby("g")[c].transform("median")

    def partial_spearman(x, y, z):
        rx = stats.rankdata(x); ry = stats.rankdata(y); rz = stats.rankdata(z)
        ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz); ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
        return float(stats.pearsonr(ex, ey)[0])

    out = dict(n=len(T),
               spearman_noise_vs_R40A=float(stats.spearmanr(T.noise, T.A)[0]),
               spearman_noise_vs_R40A_groupcentred=float(stats.spearmanr(T.noise_c, T.A_c)[0]),
               H1_groupcentred_rho=float(stats.spearmanr(T.A_c, T.AV_c)[0]),
               H1_groupcentred_partial_on_noise=partial_spearman(T.A_c.values, T.AV_c.values, T.noise_c.values),
               H1_uncentred_partial_on_noise=partial_spearman(T.A.values, T.AV.values, T.noise.values))
    boots = []
    idx = np.arange(len(T))
    for _ in range(5000):
        s = rng.choice(idx, len(idx))
        boots.append(partial_spearman(T.A_c.values[s], T.AV_c.values[s], T.noise_c.values[s]))
    out["H1_groupcentred_partial_on_noise_ci95"] = [float(np.nanpercentile(boots, 2.5)), float(np.nanpercentile(boots, 97.5))]
    N.to_csv(OUT / "gamma_noise_silence.csv")
    return out
