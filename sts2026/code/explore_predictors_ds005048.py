# AI-assisted code (Claude Code, 2026-09/10); reviewed and run by the student. See sts2026/AI_DISCLOSURE_LOG.md
"""EXPLORATORY feasibility (discovery ds005048 only): is individual 40-Hz responsiveness
(a) reliable (split-half across blocks), and (b) related to non-stimulation EEG features?

Response  R40  = within-block ITC at 40 Hz minus mean ITC at 38,39,41,42 Hz... (1-s epochs, stim blocks)
Negative control response R37 = same at 37 Hz (no stimulus there) minus its neighbours.
Non-stimulation features from SILENCE windows (skipping the first 2 s after offset):
  aperiodic exponent & offset (FOOOF, 2-35 Hz, fronto-central mean spectrum), alpha peak frequency,
  relative 40-Hz power, plus age & MMSE.
Nothing here is confirmatory; it only sizes effects for the pre-registration.
"""
import json
import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import welch
from fooof import FOOOF
from ds005048_io import load, subjects, participants, FS
from explore_subharmonic import block_itc
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "results"
CH = ["Fz", "F3", "F4", "Cz", "C3", "C4"]


def resp(sig, blocks, f, nb):
    v = lambda g: np.mean([block_itc(sig, e.start + int(FS), e.start + int(39 * FS), g)[0] for _, e in blocks.iterrows()])
    return v(f) - np.mean([v(g) for g in nb])


def main():
    rows = []
    for sub in subjects():
        x, ch, ev = load(sub)
        sig = x[[ch.index(c) for c in CH]].mean(0)
        st = ev[ev.is_stim].reset_index(drop=True)
        r40 = resp(sig, st, 40, [38, 42, 37, 43])
        r40_odd = resp(sig, st.iloc[0::2], 40, [38, 42, 37, 43])
        r40_even = resp(sig, st.iloc[1::2], 40, [38, 42, 37, 43])
        r37 = resp(sig, st, 37, [35, 36, 38, 39])
        # silence spectra
        rs = ev[(~ev.is_stim) & (ev.stop - ev.start >= 20 * FS)]
        segs = [x[[ch.index(c) for c in CH], e.start + int(2 * FS):e.stop] for _, e in rs.iterrows()]
        P = np.mean([welch(s, fs=FS, nperseg=int(2 * FS))[1].mean(0) for s in segs], 0)
        f = welch(segs[0], fs=FS, nperseg=int(2 * FS))[0]
        fm = FOOOF(peak_width_limits=(1, 8), max_n_peaks=4, aperiodic_mode="fixed", verbose=False)
        fm.fit(f, P, [2, 35])
        off, expo = fm.aperiodic_params_
        pk = fm.get_params("peak_params")
        pk = np.atleast_2d(pk)
        alpha = pk[(pk[:, 0] >= 7) & (pk[:, 0] <= 13)] if pk.size else np.empty((0, 3))
        iaf = float(alpha[np.argmax(alpha[:, 1]), 0]) if len(alpha) else np.nan
        rel40 = float(np.log10(P[(f >= 38) & (f <= 42)].mean() / P[(f >= 30) & (f <= 50)].mean()))
        rows.append(dict(sub=sub, R40=r40, R40_odd=r40_odd, R40_even=r40_even, R37=r37,
                         aper_exp=expo, aper_off=off, iaf=iaf, rel40_rest=rel40, fit_r2=fm.r_squared_))
    df = pd.DataFrame(rows).merge(participants().rename(columns={"participant_id": "sub"}), on="sub")
    for c in ["Age", "MMSE"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df.to_csv(OUT / "explore_predictors_ds005048.csv", index=False)
    res = {}
    r = stats.pearsonr(df.R40_odd, df.R40_even)[0]
    res["split_half_r"] = float(r); res["spearman_brown"] = float(2 * r / (1 + r))
    for y in ["R40", "R37"]:
        for xcol in ["aper_exp", "aper_off", "iaf", "rel40_rest", "Age", "MMSE"]:
            m = df[[xcol, y]].dropna()
            rho, p = stats.spearmanr(m[xcol], m[y])
            res[f"{y}~{xcol}"] = dict(rho=round(float(rho), 3), p=round(float(p), 4), n=len(m))
    res["group_R40_median"] = df.groupby("Group").R40.median().round(3).to_dict()
    res["group_n"] = df.Group.value_counts().to_dict()
    json.dump(res, open(OUT / "explore_predictors_ds005048.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
