# AI-assisted code (Claude Code, 2026-10); reviewed and run by the student. See sts2026/AI_DISCLOSURE_LOG.md
"""PRE-REGISTERED AMENDMENT H5 (see 05_PREREGISTRATION.md section 9): across-night stability of the individual
40 Hz response in an independent third dataset, OpenNeuro ds005185 (EESM19; 20 young adults x 4 nights;
~4 min continuous 40 Hz amplitude-modulated noise before sleep; PSG scalp channels F3 F4 C3 C4 O1 O2 M1 M2, 500 Hz).

Measure (same definition as the main study): R40 = ITC(40 Hz) - mean ITC(37, 38, 42, 43 Hz) over 1-s epochs.
Epochs are locked to the 1-s stimulus triggers (rising edges of row 36 of the sample-aligned sourcedata .mat).
ROI signal: mean(F3, F4, C3, C4) - mean(O1, O2) (fronto-central vs occipital; the recording reference is
unspecified, so a fixed bipolar derivation is used). NaN (bad) channels are dropped from each mean.
1 Hz FIR high-pass; epochs with any ROI channel > 200 uV peak-to-peak rejected; >= 20 epochs required.
Control: R33 (33 Hz vs 30, 31, 35, 36 Hz). Noise covariate: log power 35-38 & 42-45 Hz during stimulation.
"""
import glob, json, re, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import welch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import confirmatory as CF

ROOT = HERE.parents[1] / "data" / "raw" / "ds005185"
OUT = CF.OUT
FRONT, OCC = ["F3", "F4", "C3", "C4"], ["O1", "O2"]


def triggers(mat_path):
    import h5py
    try:
        with h5py.File(mat_path, "r") as f:
            D = np.array(f["data"])
    except OSError:  # older MATLAB v5 file
        import scipy.io as sio
        D = np.asarray(sio.loadmat(mat_path)["data"])
    D = D.T if D.shape[0] > D.shape[1] else D
    t = D[35]
    return np.flatnonzero((t[1:] > 0) & (t[:-1] == 0)) + 1, D.shape[1]


def session_measure(set_path, mat_path):
    import mne
    mne.set_log_level("ERROR")
    raw = mne.io.read_raw_eeglab(set_path, preload=True)
    fs = raw.info["sfreq"]
    x = raw.get_data() * 1e6
    tr, n_mat = triggers(mat_path)
    if len(tr) < 200:
        return dict(n_trig=len(tr), error="fewer than 200 stimulus triggers (pre-registered exclusion)")
    if n_mat != x.shape[1]:
        return dict(error=f"length mismatch {n_mat} vs {x.shape[1]}")
    ok = lambda c: c in raw.ch_names and np.all(np.isfinite(x[raw.ch_names.index(c)]))
    fr = [c for c in FRONT if ok(c)]
    oc = [c for c in OCC if ok(c)]
    if not fr or not oc:
        return dict(error="missing ROI channels")
    from scipy.signal import butter, sosfiltfilt
    import mne.filter as mf
    chans = fr + oc
    xx = mf.filter_data(x[[raw.ch_names.index(c) for c in chans]], fs, 1.0, None, verbose=False)
    sig = xx[:len(fr)].mean(0) - xx[len(fr):].mean(0)
    L = int(round(fs))
    ep = []
    for s in tr:
        if s + L > xx.shape[1]:
            continue
        seg = xx[:, s:s + L]
        if np.max(np.ptp(seg, axis=1)) > CF.PTP_UV:
            continue
        ep.append(sig[s:s + L])
    if len(ep) < CF.MIN_EPOCHS:
        return dict(n_ep=len(ep), error="too few epochs")
    ep = np.asarray(ep)
    R40 = CF.itc(ep, fs, 40.0) - np.mean([CF.itc(ep, fs, f) for f in CF.NEIGH40])
    R33 = CF.itc(ep, fs, 33.0) - np.mean([CF.itc(ep, fs, f) for f in CF.NEIGH33])
    f, P = welch(np.concatenate(ep), fs=fs, nperseg=L)
    m = ((f >= 35) & (f <= 38)) | ((f >= 42) & (f <= 45))
    return dict(R40=R40, R33=R33, itc40=CF.itc(ep, fs, 40.0), n_ep=len(ep), n_trig=len(tr),
                noise=float(np.log10(P[m].mean())), front=",".join(fr), occ=",".join(oc))


def icc_multi(M):
    """ICC(3,1), two-way mixed, consistency, single measure; M: subjects x sessions (complete rows)."""
    n, k = M.shape
    gm = M.mean()
    ms_r = k * np.sum((M.mean(1) - gm) ** 2) / (n - 1)
    ms_e = np.sum((M - M.mean(1, keepdims=True) - M.mean(0, keepdims=True) + gm) ** 2) / ((n - 1) * (k - 1))
    return (ms_r - ms_e) / (ms_r + (k - 1) * ms_e)


def extract():
    rows = []
    for s in sorted(glob.glob(str(ROOT / "sub-*/ses-00[1-4]/eeg/*task-ASSR_acq-PSG_eeg.set"))):
        sub, ses = re.search(r"(sub-\d+)/(ses-\d+)", s).groups()
        mats = glob.glob(str(ROOT / "sourcedata" / sub / ses / "ASSR" / "*.mat"))
        if len(mats) != 1:
            rows.append(dict(sub=sub, ses=ses, error=f"{len(mats)} mat files"))
            continue
        rows.append(dict(sub=sub, ses=ses, **session_measure(s, mats[0])))
    pd.DataFrame(rows).to_csv(OUT / "ds005185_sessions.csv", index=False)


def test():
    D = pd.read_csv(OUT / "ds005185_sessions.csv")
    res = {"n_sessions_valid": int(D.R40.notna().sum()), "n_sessions_total": len(D),
           "errors": D[D.R40.isna()][["sub", "ses"] + (["error"] if "error" in D else [])].astype(str).values.tolist(),
           "group_median_R40": float(D.R40.median()), "group_median_itc40": float(D.itc40.median())}
    rng = np.random.default_rng(CF.SEED)
    for col in ["R40", "R33"]:
        W = D.pivot(index="sub", columns="ses", values=col).dropna()
        M = W.values
        icc = icc_multi(M)
        boots = [icc_multi(M[rng.choice(len(M), len(M))]) for _ in range(10000)]
        res[f"ICC_{col}"] = dict(icc3_1=float(icc), ci95=[float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                                 n_subjects=int(len(M)), n_sessions=int(M.shape[1]))
    # secondary: first two valid nights per subject (uses all subjects)
    d2 = D.dropna(subset=["R40"]).sort_values(["sub", "ses"]).groupby("sub").head(2)
    W2 = d2.assign(k=d2.groupby("sub").cumcount()).pivot(index="sub", columns="k", values="R40").dropna().values
    boots = [icc_multi(W2[rng.choice(len(W2), len(W2))]) for _ in range(10000)]
    res["ICC_R40_first_two_nights"] = dict(icc3_1=float(icc_multi(W2)), ci95=[float(np.percentile(boots, 2.5)),
                                           float(np.percentile(boots, 97.5))], n_subjects=int(len(W2)),
                                           spearman=float(stats.spearmanr(W2[:, 0], W2[:, 1])[0]))
    # noise-controlled: residualize R40 on session noise (pooled regression), then ICC
    d = D.dropna(subset=["R40", "noise"]).copy()
    b = np.polyfit(d.noise, d.R40, 1)
    d["R40_resid"] = d.R40 - np.polyval(b, d.noise)
    W = d.pivot(index="sub", columns="ses", values="R40_resid").dropna().values
    boots = [icc_multi(W[rng.choice(len(W), len(W))]) for _ in range(10000)]
    res["ICC_R40_noise_residualized"] = dict(icc3_1=float(icc_multi(W)), ci95=[float(np.percentile(boots, 2.5)),
                                             float(np.percentile(boots, 97.5))], n_subjects=int(len(W)))
    res["noise_vs_R40_spearman_pooled"] = float(stats.spearmanr(d.noise, d.R40)[0])
    r = res["ICC_R40"]
    res["H5_success"] = bool(r["icc3_1"] >= 0.5 and r["ci95"][0] > 0.2)
    res["NC_R33_null"] = bool(abs(res["ICC_R33"]["icc3_1"]) < 0.3)
    json.dump(res, open(OUT / "results_h5.json", "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    {"extract": extract, "test": test}[sys.argv[1]]()
