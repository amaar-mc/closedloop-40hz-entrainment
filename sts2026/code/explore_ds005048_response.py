# AI-assisted code (Claude Code, 2026-09/10); reviewed and run by the student. See sts2026/AI_DISCLOSURE_LOG.md
"""EXPLORATORY (discovery set only, ds005048). Feasibility of candidate response measures.

Per participant:
  * ITC40: inter-trial phase coherence at 40 Hz across 1-s epochs cut from stimulation blocks
    (1 s = 40 cycles, so epochs share stimulus phase if the click train is locked to block onset),
    vs the same computed in silence (null for the stimulus clock).
  * Onset/offset dynamics: 40-Hz band envelope (38-42 Hz, zero-phase) time-locked to block onsets and
    offsets, averaged over blocks, channel = mean over fronto-central set.
  * Links to age / MMSE / diagnosis (exploratory correlations, reported with n and CI, not claims).
Outputs: sts2026/results/explore_ds005048_response.json and per-participant CSV.
"""
import json
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt, hilbert
from scipy import stats
from ds005048_io import load, subjects, participants, FS
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "results"
CH = ["Fz", "F3", "F4", "Cz", "C3", "C4", "Fp1", "Fp2"]


def itc_at(x, starts, L, f):
    """x: (ch, n). ITC at freq f over epochs [s, s+L). Returns mean over channels."""
    t = np.arange(L) / FS
    ker = np.exp(-2j * np.pi * f * t) * np.hanning(L)
    ph = []
    for s in starts:
        seg = x[:, s:s + L]
        c = seg @ ker
        ph.append(c / np.abs(c))
    ph = np.array(ph)
    return float(np.abs(ph.mean(0)).mean()), len(starts)


def main():
    rows, onset_env, offset_env = [], [], []
    for sub in subjects():
        x, ch, ev = load(sub)
        xs = x[[ch.index(c) for c in CH]]
        L = int(FS)
        st_starts, rs_starts, onsets, offsets = [], [], [], []
        for _, e in ev.iterrows():
            if e.is_stim:
                onsets.append(e.start); offsets.append(e.stop)
                st_starts += list(range(e.start + L, e.stop - L, L))  # skip first second (onset transient)
            elif e.stop - e.start >= 20 * FS:
                rs_starts += list(range(e.start + 2 * L, e.stop - L, L))
        itc_s, n_s = itc_at(xs, st_starts, L, 40.0)
        itc_r, n_r = itc_at(xs, rs_starts, L, 40.0)
        # matched-n null: ITC depends on n; subsample stim epochs to rest count
        rng = np.random.default_rng(0)
        itc_s_m = np.mean([itc_at(xs, rng.choice(st_starts, n_r, replace=False), L, 40.0)[0] for _ in range(20)])
        ctrl = {f: itc_at(xs, st_starts, L, f)[0] for f in [37.0, 43.0]}
        env = np.abs(hilbert(sosfiltfilt(butter(4, [38, 42], "band", fs=FS, output="sos"), xs, axis=1), axis=1)).mean(0)
        pre, post = int(2 * FS), int(4 * FS)
        on = np.mean([env[o - pre:o + post] for o in onsets if o - pre >= 0 and o + post <= env.size], 0)
        off = np.mean([env[o - pre:o + post] for o in offsets if o + post <= env.size], 0)
        onset_env.append(on / env.mean()); offset_env.append(off / env.mean())
        rows.append(dict(sub=sub, itc40_stim=itc_s, itc40_stim_matched=itc_s_m, itc40_rest=itc_r,
                         itc37_stim=ctrl[37.0], itc43_stim=ctrl[43.0], n_stim_ep=n_s, n_rest_ep=n_r))
    df = pd.DataFrame(rows)
    p = participants().rename(columns={"participant_id": "sub"})
    df = df.merge(p, on="sub", how="left")
    df.to_csv(OUT / "explore_ds005048_per_participant.csv", index=False)
    res = {}
    d = df.itc40_stim_matched - df.itc40_rest
    res["itc40_stim_matched_minus_rest"] = dict(mean=float(d.mean()), dz=float(d.mean() / d.std()),
                                                p=float(stats.wilcoxon(d).pvalue), n_pos=int((d > 0).sum()))
    res["itc_means"] = df[["itc40_stim", "itc40_stim_matched", "itc40_rest", "itc37_stim", "itc43_stim"]].mean().to_dict()
    for col in ["Age", "MMSE"]:
        if col in df:
            v = pd.to_numeric(df[col], errors="coerce")
            m = v.notna()
            r, pv = stats.spearmanr(v[m], d[m])
            res[f"spearman_itcgain_vs_{col}"] = dict(rho=float(r), p=float(pv), n=int(m.sum()))
    res["columns"] = list(p.columns)
    t = (np.arange(-2 * FS, 4 * FS) / FS)
    res["onset_env_grand"] = np.round(np.mean(onset_env, 0)[::25], 3).tolist()
    res["offset_env_grand"] = np.round(np.mean(offset_env, 0)[::25], 3).tolist()
    res["env_time_s"] = t[::25].round(2).tolist()
    json.dump(res, open(OUT / "explore_ds005048_response.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if "env" not in k}, indent=1))
    print("onset ", res["onset_env_grand"]); print("offset", res["offset_env_grand"])


if __name__ == "__main__":
    main()
