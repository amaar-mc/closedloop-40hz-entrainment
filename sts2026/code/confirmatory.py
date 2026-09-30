# AI-assisted code (Claude Code, 2026-10); reviewed and run by the student. See sts2026/AI_DISCLOSURE_LOG.md
"""PRE-REGISTERED confirmatory analysis (see sts2026/05_PREREGISTRATION.md). Frozen before the held-out
dataset (Harvard Dataverse 56XZ3F) was analysed; its sha256 is recorded in the pre-registration.

Stage 1  extract : per-block response measures for every recording (56XZ3F) and per-participant measures
                   for the discovery set (ds005048) -> results/confirmatory/*.csv
Stage 2  test    : quality gate K1, H1 (cross-block trait reliability), H2 (group claims), H3 (stability over
                   months), H4 (cross-cohort prediction), negative controls, sensitivity analyses
                   -> results/confirmatory/results.json

Usage:  python confirmatory.py extract [--variant NAME]  ;  python confirmatory.py test
"""
import sys, json, glob, os, re
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import welch

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "results" / "confirmatory"
OUT.mkdir(parents=True, exist_ok=True)
SEED = 20261001
ROI = ["Fz", "F3", "F4", "Cz", "C3", "C4"]            # identical in both datasets
ROI_ALT = ["Fz", "FC1", "FC2", "Cz"]                  # sensitivity S1 (56XZ3F only)
NEIGH40 = [37.0, 38.0, 42.0, 43.0]
NEIGH33 = [30.0, 31.0, 35.0, 36.0]   # control frequency >=4 Hz from 40 (no Hann leakage)
PTP_UV = 200.0                                        # epoch rejection threshold (peak-to-peak, any ROI channel)
MIN_EPOCHS = 20

VARIANTS = {  # name -> dict of options (primary first)
    "primary": dict(roi=ROI, reject=True, ref="average"),
    "S1_roi_frontocentral": dict(roi=ROI_ALT, reject=True, ref="average"),
    "S2_no_rejection": dict(roi=ROI, reject=False, ref="average"),
    "S3_mastoid_ref": dict(roi=ROI, reject=True, ref="mastoid"),
}


# ----------------------------------------------------------------------------------------- measures
def itc(epochs, fs, f):
    """epochs: (n, L) ROI-mean signal. Hann-windowed DFT at f; ITC = |mean unit phasor|."""
    L = epochs.shape[1]
    k = np.exp(-2j * np.pi * f * np.arange(L) / fs) * np.hanning(L)
    z = epochs @ k
    return float(np.abs(np.mean(z / np.abs(z))))


def response(x_roi, fs, a, b, reject=True, max_epochs=None):
    """x_roi: (n_roi, n) in uV. 1-s epochs from a+1 s to b-0.5 s. Returns dict(R40, R33, n)."""
    L = int(round(fs))
    starts = list(range(a + L, b - L // 2 - L + 1, L))
    ep = []
    for s in starts:
        seg = x_roi[:, s:s + L]
        if reject and np.max(np.ptp(seg, axis=1)) > PTP_UV:
            continue
        ep.append(seg.mean(0))
    if max_epochs:
        ep = ep[:max_epochs]
    if len(ep) < MIN_EPOCHS:
        return dict(R40=np.nan, R33=np.nan, n=len(ep), itc40=np.nan)
    ep = np.asarray(ep)
    i40 = itc(ep, fs, 40.0)
    return dict(R40=i40 - np.mean([itc(ep, fs, f) for f in NEIGH40]),
                R33=itc(ep, fs, 33.0) - np.mean([itc(ep, fs, f) for f in NEIGH33]),
                n=len(ep), itc40=i40)


def rest_features(segments, fs):
    """segments: list of (n_roi, n) arrays of non-stimulation EEG (uV). FOOOF 2-35 Hz on mean spectrum."""
    from fooof import FOOOF
    nper = int(2 * fs)
    P, f = None, None
    for s in segments:
        f, p = welch(s, fs=fs, nperseg=nper)
        P = p.mean(0) if P is None else P + p.mean(0)
    P = P / len(segments)
    fm = FOOOF(peak_width_limits=(1, 8), max_n_peaks=4, aperiodic_mode="fixed", verbose=False)
    fm.fit(f, P, [2, 35])
    off, expo = fm.aperiodic_params_
    pk = np.atleast_2d(fm.get_params("peak_params"))
    al = pk[(pk[:, 0] >= 7) & (pk[:, 0] <= 13)] if pk.size and not np.all(np.isnan(pk)) else np.empty((0, 3))
    iaf = float(al[np.argmax(al[:, 1]), 0]) if len(al) else np.nan
    rel40 = float(np.log10(P[(f >= 38) & (f <= 42)].mean() / P[(f >= 30) & (f <= 50)].mean()))
    return dict(aper_exp=float(expo), aper_off=float(off), iaf=iaf, rel40=rel40, fit_r2=float(fm.r_squared_))


# ----------------------------------------------------------------------------------------- 56XZ3F
def _subject_group(path):
    rel = path.split("dv56XZ3F/")[1]
    sid = re.search(r"/(Y\d+|E\d+|HG\d+)_EEG/", "/" + rel).group(1)
    if rel.startswith("Phase1_CNControls"):
        grp = "young_CN" if sid.startswith("Y") else "older_CN"
        visit = "P1"
    elif rel.startswith("Phase1_AD"):
        grp, visit = "AD", "P1"
    else:
        grp = "AD"
        visit = "P2A_base" if "baseline.bdf" in rel else "P2A_3mo"
    return sid, grp, visit, rel


def extract_dv56(variant="primary"):
    sys.path.insert(0, str(HERE))
    from dv56_io import schedule, ROOT
    import mne
    mne.set_log_level("ERROR")
    opt = VARIANTS[variant]
    rows, feats = [], []
    only = os.environ.get("DV56_ONLY")  # test hook: restrict to one file (used only on the excluded HG204 3-month file)
    for bdf in sorted(glob.glob(str(ROOT / "*/*/*.bdf"))):
        base = os.path.basename(bdf)
        if only and only not in bdf:
            continue
        if any(k in base for k in ("constant_light", "hour", "duty_cycle", "baseline_eyes", "baseline_stim")):
            continue
        d = os.path.dirname(bdf)
        notes = glob.glob(d + "/*Notes.txt")
        if "baseline.bdf" in base:
            notes = [n for n in notes if "baseline_Notes" in n]
        elif "3months" in base:
            notes = [n for n in notes if "3months" in n]
        sid, grp, visit, rel = _subject_group(bdf)
        if sid == "HG222" and visit == "P2A_base":
            continue  # byte-identical copy of HG221's baseline file (md5 3e056d07...) -> excluded
        raw = mne.io.read_raw_bdf(bdf, preload=True)
        sch, _ = schedule(bdf, notes[0], raw=raw)
        if sch is None:
            continue
        from dv56_io import BIOSEMI32
        fs = raw.info["sfreq"]
        if opt["ref"] == "mastoid":
            mast = raw.copy().pick(["LM", "RM"]).get_data().mean(0)
        raw.pick([f"A{i}" for i in range(1, 33)])
        raw.rename_channels({f"A{i}": BIOSEMI32[i - 1] for i in range(1, 33)})
        raw.filter(1.0, None, fir_design="firwin")
        x = raw.get_data() * 1e6
        if opt["ref"] == "average":
            x = x - x.mean(0, keepdims=True)
        else:
            from scipy.signal import butter, sosfiltfilt
            m = sosfiltfilt(butter(4, 1.0, "high", fs=fs, output="sos"), mast) * 1e6
            x = x - m
        xr = x[[raw.ch_names.index(c) for c in opt["roi"]]]
        seen = {}
        for b in sch:
            lab = b["label"]
            if "tablet" in b["desc"].lower():
                continue  # block with extra stimulation noted by experimenters
            seen[lab] = seen.get(lab, 0) + 1
            r_full = response(xr, fs, b["start"], b["stop"], reject=opt["reject"])
            r_1min = response(xr, fs, b["start"], b["stop"], reject=opt["reject"], max_epochs=58)
            rows.append(dict(sid=sid, group=grp, visit=visit, file=rel, label=lab, occurrence=seen[lab],
                             start_s=b["start"] / fs, stop_s=b["stop"] / fs, source=b["source"],
                             R40=r_full["R40"], R33=r_full["R33"], itc40=r_full["itc40"], n_ep=r_full["n"],
                             R40_1min=r_1min["R40"], n_ep_1min=r_1min["n"]))
        # pre-stimulation features: first block of Phase-1 recordings (silent baseline, stimulus covered)
        if visit == "P1" and sch[0]["label"] == "baseline" and "_2.bdf" not in base:
            a, bb = sch[0]["start"] + int(2 * fs), sch[0]["stop"] - int(fs)
            feats.append(dict(sid=sid, group=grp, **rest_features([xr[:, a:bb]], fs)))
    pd.DataFrame(rows).to_csv(OUT / f"dv56_blocks_{variant}.csv", index=False)
    if variant == "primary":
        pd.DataFrame(feats).to_csv(OUT / "dv56_prestim_features.csv", index=False)


# ----------------------------------------------------------------------------------------- ds005048
def extract_ds005048(variant="primary"):
    sys.path.insert(0, str(HERE))
    from ds005048_io import load, subjects, participants, FS
    opt = VARIANTS[variant]
    roi = opt["roi"] if all(c in ["Fz", "F3", "F4", "Cz", "C3", "C4"] for c in opt["roi"]) else ROI
    rows = []
    for sub in subjects():
        x, ch, ev = load(sub)
        xr = x[[ch.index(c) for c in roi]]
        st = ev[ev.is_stim].reset_index(drop=True)
        per_block = [response(xr, FS, int(e.start), int(e.stop), reject=opt["reject"]) for _, e in st.iterrows()]

        def pooled(sel):
            L = int(FS)
            ep = []
            for _, e in st.iloc[sel].iterrows():
                for s in range(int(e.start) + L, int(e.stop) - L // 2 - L + 1, L):
                    seg = xr[:, s:s + L]
                    if opt["reject"] and np.max(np.ptp(seg, axis=1)) > PTP_UV:
                        continue
                    ep.append(seg.mean(0))
            ep = np.asarray(ep)
            return itc(ep, FS, 40.0) - np.mean([itc(ep, FS, f) for f in NEIGH40])

        # block-wise (within-block ITC) averaged, as in discovery, plus odd/even halves
        R = np.array([p["R40"] for p in per_block])
        R33 = np.array([p["R33"] for p in per_block])
        rs = ev[(~ev.is_stim) & (ev.stop - ev.start >= 20 * FS)]
        segs = [xr[:, int(e.start) + int(2 * FS):int(e.stop)] for _, e in rs.iterrows()]
        f = rest_features(segs, FS) if variant == "primary" else {}
        rows.append(dict(sid=sub, R40=np.nanmean(R), R40_odd=np.nanmean(R[0::2]), R40_even=np.nanmean(R[1::2]),
                         R33=np.nanmean(R33), R33_odd=np.nanmean(R33[0::2]), R33_even=np.nanmean(R33[1::2]),
                         R40_first=R[0], R40_second=R[1], n_blocks=len(R), **f))
    df = pd.DataFrame(rows).merge(participants().rename(columns={"participant_id": "sid"}), on="sid")
    df.to_csv(OUT / f"ds005048_subjects_{variant}.csv", index=False)


# ----------------------------------------------------------------------------------------- statistics
rng = np.random.default_rng(SEED)


def boot_ci(fn, *arrays, n=10000):
    idx = np.arange(len(arrays[0]))
    vals = []
    for _ in range(n):
        s = rng.choice(idx, len(idx), replace=True)
        v = fn(*[a[s] for a in arrays])
        if np.isfinite(v):
            vals.append(v)
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def spearman_test(x, y, n_perm=10000):
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    rho = stats.spearmanr(x, y)[0]
    perm = np.array([stats.spearmanr(x, rng.permutation(y))[0] for _ in range(n_perm)])
    p = (1 + np.sum(np.abs(perm) >= abs(rho))) / (n_perm + 1)
    ci = boot_ci(lambda a, b: stats.spearmanr(a, b)[0], x, y)
    return dict(rho=float(rho), ci95=ci, p_perm=float(p), n=int(len(x)),
                pearson_r=float(stats.pearsonr(x, y)[0]))


def icc_3_1(a, b):
    X = np.c_[a, b]
    n, k = X.shape
    gm = X.mean()
    ms_r = k * np.sum((X.mean(1) - gm) ** 2) / (n - 1)
    ms_e = np.sum((X - X.mean(1, keepdims=True) - X.mean(0, keepdims=True) + gm) ** 2) / ((n - 1) * (k - 1))
    return (ms_r - ms_e) / (ms_r + (k - 1) * ms_e)


def icc_test(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    a, b = a[m], b[m]
    return dict(icc3_1=float(icc_3_1(a, b)), ci95=boot_ci(icc_3_1, a, b), n=int(len(a)),
                spearman=float(stats.spearmanr(a, b)[0]))


def hedges_g(a, b):
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2))
    return (np.mean(a) - np.mean(b)) / sp * (1 - 3 / (4 * (na + nb) - 9))


def group_test(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    u = stats.mannwhitneyu(a, b, alternative="two-sided")
    cliff = 2 * u.statistic / (len(a) * len(b)) - 1
    gs = []
    for _ in range(10000):
        gs.append(hedges_g(rng.choice(a, len(a)), rng.choice(b, len(b))))
    return dict(median_a=float(np.median(a)), median_b=float(np.median(b)), n_a=len(a), n_b=len(b),
                p_mwu=float(u.pvalue), cliffs_delta=float(cliff), hedges_g=float(hedges_g(a, b)),
                g_ci95=[float(np.percentile(gs, 2.5)), float(np.percentile(gs, 97.5))])


def holm(pdict):
    keys = sorted(pdict, key=pdict.get)
    m, out, prev = len(keys), {}, 0
    for i, k in enumerate(keys):
        adj = min(1.0, max(prev, (m - i) * pdict[k]))
        out[k] = adj
        prev = adj
    return out


def pivot(blocks, col, label, visit="P1", occurrence=1):
    s = blocks[(blocks.label == label) & (blocks.visit == visit) & (blocks.occurrence == occurrence)]
    return s.set_index("sid")[col]


def run_tests(variant="primary"):
    B = pd.read_csv(OUT / f"dv56_blocks_{variant}.csv")
    grp = B.drop_duplicates("sid").set_index("sid").group
    R = {}
    A = pivot(B, "R40", "periodic_A")
    AV = pivot(B, "R40", "periodic_AV")
    base1 = B[(B.visit == "P1") & (B.label == "baseline")].groupby("sid").R40.first()  # first silent block
    # K1 quality gate: periodic audio vs first silent baseline block (all Phase-1 participants)
    k = pd.concat([A, base1], axis=1, keys=["A", "base"]).dropna()
    w = stats.wilcoxon(k.A - k.base, alternative="greater")
    R["K1_gate_audio_vs_silence"] = dict(median_diff=float(np.median(k.A - k.base)), p_one_sided=float(w.pvalue),
                                         n=len(k), n_pos=int((k.A > k.base).sum()), passed=bool(w.pvalue < 0.05))
    kav = pd.concat([AV, base1], axis=1, keys=["AV", "base"]).dropna()
    R["K1b_gate_AV_vs_silence"] = dict(median_diff=float(np.median(kav.AV - kav.base)),
                                       p_one_sided=float(stats.wilcoxon(kav.AV - kav.base, alternative="greater").pvalue),
                                       n=len(kav))
    # H1 primary: cross-block reliability periodic_A vs periodic_AV, group-median-centred, Spearman
    h = pd.concat([A, AV], axis=1, keys=["A", "AV"]).dropna()
    h["g"] = grp.reindex(h.index)
    hc = h.copy()
    for c in ["A", "AV"]:
        hc[c] = h[c] - h.groupby("g")[c].transform("median")
    R["H1_primary_A_vs_AV_groupcentred"] = spearman_test(hc.A, hc.AV)
    R["H1_primary_A_vs_AV_groupcentred"]["success"] = bool(
        R["H1_primary_A_vs_AV_groupcentred"]["rho"] >= 0.5 and R["H1_primary_A_vs_AV_groupcentred"]["ci95"][0] > 0.2)
    R["H1_uncentred"] = spearman_test(h.A, h.AV)
    for g in ["young_CN", "older_CN", "AD"]:
        s = h[h.g == g]
        R[f"H1_by_group_{g}"] = spearman_test(s.A, s.AV) if len(s) >= 6 else dict(n=len(s))
    # NC1: 37-Hz control reliability (should be ~0)
    A33, AV33 = pivot(B, "R33", "periodic_A"), pivot(B, "R33", "periodic_AV")
    n1 = pd.concat([A33, AV33], axis=1, keys=["A", "AV"]).dropna()
    R["NC1_R33_A_vs_AV"] = spearman_test(n1.A, n1.AV)
    # NC2: R40 in non-rhythmic sound blocks (random_A in CN, constant_A in AD) ~ 0 and < periodic
    nr = pd.concat([pivot(B, "R40", "random_A"), pivot(B, "R40", "constant_A")]).groupby(level=0).first()
    R["NC2_nonrhythmic_audio_R40"] = dict(median=float(nr.median()), n=int(nr.notna().sum()),
                                           p_wilcoxon_vs0=float(stats.wilcoxon(nr.dropna()).pvalue))
    # NC3: reliability of R40 between the first two silent baseline blocks (should be ~0)
    bl = B[(B.visit == "P1") & (B.label == "baseline")].sort_values(["sid", "file", "start_s"])
    b1 = bl.groupby("sid").R40.apply(lambda s: s.iloc[0] if len(s) > 0 else np.nan)
    b2 = bl.groupby("sid").R40.apply(lambda s: s.iloc[1] if len(s) > 1 else np.nan)
    n3 = pd.concat([b1, b2], axis=1, keys=["b1", "b2"]).dropna()
    R["NC3_silence_R40_b1_vs_b2"] = spearman_test(n3.b1, n3.b2)
    # H2 group claims on the first minute of periodic audio
    A1 = pivot(B, "R40_1min", "periodic_A")
    gA = pd.concat([A1, grp.reindex(A1.index)], axis=1, keys=["r", "g"]).dropna()
    H2 = {}
    H2["H2a_older_vs_young"] = group_test(gA[gA.g == "older_CN"].r, gA[gA.g == "young_CN"].r)
    H2["H2b_AD_vs_older"] = group_test(gA[gA.g == "AD"].r, gA[gA.g == "older_CN"].r)
    pr = pd.concat([pivot(B, "R40", "periodic_A"), pivot(B, "R40", "random_A")], axis=1, keys=["p", "r"]).dropna()
    wz = stats.wilcoxon(pr.p - pr.r)
    H2["H2c_periodic_vs_random_CN"] = dict(median_diff=float(np.median(pr.p - pr.r)), n=len(pr), p=float(wz.pvalue),
                                            dz=float((pr.p - pr.r).mean() / (pr.p - pr.r).std(ddof=1)),
                                            ci95_mean_diff=boot_ci(np.mean, (pr.p - pr.r).values))
    adj = holm({k: v.get("p_mwu", v.get("p")) for k, v in H2.items()})
    for k in H2:
        H2[k]["p_holm"] = adj[k]
    R.update(H2)
    # H3 stability over months in AD (periodic AV)
    P1 = pivot(B, "R40", "periodic_AV", "P1")
    PB = pivot(B, "R40", "periodic_AV", "P2A_base")
    P3 = pivot(B, "R40", "periodic_AV", "P2A_3mo")
    d_a = pd.concat([P1, PB], axis=1).dropna()
    d_b = pd.concat([PB, P3], axis=1).dropna()
    H3 = {"H3a_P1_to_P2Abaseline": icc_test(d_a.iloc[:, 0].values, d_a.iloc[:, 1].values),
          "H3b_P2Abaseline_to_3mo": icc_test(d_b.iloc[:, 0].values, d_b.iloc[:, 1].values)}
    for k, v in H3.items():
        a, b = (P1, PB) if "P1" in k else (PB, P3)
        d = pd.concat([a, b], axis=1).dropna()
        v["spearman_perm"] = spearman_test(d.iloc[:, 0], d.iloc[:, 1])
        v["success"] = bool(v["icc3_1"] >= 0.5 and v["ci95"][0] > 0)
    adj = holm({k: v["spearman_perm"]["p_perm"] for k, v in H3.items()})
    for k in H3:
        H3[k]["p_holm"] = adj[k]
    R.update(H3)
    # H3 sensitivity: without HG204 (3-month file opened during the census)
    d = pd.concat([PB, P3], axis=1).dropna().drop(index="HG204", errors="ignore")
    R["H3b_sens_without_HG204"] = icc_test(d.iloc[:, 0].values, d.iloc[:, 1].values)
    return R


def run_h4():
    D = pd.read_csv(OUT / "ds005048_subjects_primary.csv")
    F = pd.read_csv(OUT / "dv56_prestim_features.csv")
    B = pd.read_csv(OUT / "dv56_blocks_primary.csv")
    y56 = pivot(B, "R40", "periodic_A")
    F = F.set_index("sid").join(y56.rename("R40")).dropna(subset=["R40"])
    demo = pd.read_csv(OUT / "dv56_ages.csv").set_index("sid") if (OUT / "dv56_ages.csv").exists() else None
    feats = ["aper_exp", "aper_off", "iaf", "rel40", "age"]
    D = D.rename(columns={"Age": "age"})
    if demo is None:
        return dict(error="dv56_ages.csv missing")
    F = F.join(demo)
    z = lambda s: (s - s.mean()) / s.std()
    Xtr = D[feats].apply(pd.to_numeric, errors="coerce")
    Xtr = Xtr.fillna(Xtr.mean()).apply(z).values
    ytr = z(D.R40).values
    Xte = F[feats].apply(pd.to_numeric, errors="coerce")
    Xte = Xte.fillna(Xte.mean()).apply(z).values
    yte = z(F.R40).values
    from sklearn.linear_model import Ridge
    m = Ridge(alpha=1.0).fit(Xtr, ytr)
    pred = m.predict(Xte)
    r = stats.pearsonr(pred, yte)[0]
    perm = np.array([stats.pearsonr(pred, rng.permutation(yte))[0] for _ in range(10000)])
    p = (1 + np.sum(perm >= r)) / 10001
    return dict(r=float(r), p_perm_one_sided=float(p), n_test=int(len(yte)), n_train=int(len(ytr)),
                coefs=dict(zip(feats, map(float, m.coef_))), success=bool(r >= 0.3 and p < 0.05))


def run_ds005048():
    D = pd.read_csv(OUT / "ds005048_subjects_primary.csv")
    return dict(split_half_odd_even=spearman_test(D.R40_odd, D.R40_even),
                first_vs_second_block=spearman_test(D.R40_first, D.R40_second),
                NC_R33_odd_even=spearman_test(D.R33_odd, D.R33_even),
                group_medians=D.groupby("Group").R40.median().to_dict())


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "extract":
        v = sys.argv[2] if len(sys.argv) > 2 else "primary"
        if v == "primary" and not os.environ.get("DV56_ONLY"):
            extract_ds005048(v)
        extract_dv56(v)
    elif cmd == "test":
        res = {"ds005048_discovery_reliability": run_ds005048(), "primary": run_tests("primary"), "H4": run_h4()}
        for v in VARIANTS:
            if v != "primary" and (OUT / f"dv56_blocks_{v}.csv").exists():
                res[v] = run_tests(v)
        json.dump(res, open(OUT / "results.json", "w"), indent=1, default=float)
        print(json.dumps(res, indent=1, default=float))
