# AI-assisted code (Claude Code, 2026-09/10); reviewed and run by the student. See sts2026/AI_DISCLOSURE_LOG.md
"""Audit: what does the theta-gamma PAC 'forecast' actually capture?

Independent recomputation on ds005048 (all 35 subjects):
  * per-window (2 s, non-overlapping) Tort MI, theta 4-8 Hz phase x 38-42 Hz amplitude,
    mean over 7 frontal channels (same bands/channels as the original pipeline);
  * 40 Hz evoked SNR per window for comparison (a direct stimulus-response measure).
Questions:
  Q1  Is window PAC temporally predictable from its own past (lag-1 autocorrelation)?
  Q2  Does 40 Hz sound change PAC at all (stim vs rest, paired over subjects)?
  Q3  How much 'forecast R^2' is obtainable with NO EEG dynamics: subject running mean + known
      future stimulation state (the schedule), vs persistence and AR baselines?
Outputs: sts2026/results/audit_pac_forecast.json
"""
import json
import numpy as np
from scipy.signal import butter, sosfiltfilt, hilbert
from scipy import stats
from ds005048_io import load, subjects, FS
from pathlib import Path

FRONTAL = ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8"]
WIN = int(2 * FS)
OUT = Path(__file__).resolve().parents[1] / "results"


def mi_tort(phase, amp, nb=18):
    bins = np.linspace(-np.pi, np.pi, nb + 1)
    idx = np.clip(np.digitize(phase, bins) - 1, 0, nb - 1)
    m = np.bincount(idx, weights=amp, minlength=nb) / np.maximum(np.bincount(idx, minlength=nb), 1)
    p = m / m.sum()
    p = np.where(p > 0, p, 1e-12)
    return (np.log(nb) + np.sum(p * np.log(p))) / np.log(nb)


def per_subject(sub):
    x, ch, ev = load(sub)
    sel = [ch.index(c) for c in FRONTAL]
    xs = x[sel]
    th = sosfiltfilt(butter(4, [4, 8], "band", fs=FS, output="sos"), xs, axis=1)
    ga = sosfiltfilt(butter(4, [38, 42], "band", fs=FS, output="sos"), xs, axis=1)
    ph, am = np.angle(hilbert(th, axis=1)), np.abs(hilbert(ga, axis=1))
    rows = []
    for _, e in ev.iterrows():
        for s in range(e.start, e.stop - WIN + 1, WIN):
            mi = np.mean([mi_tort(ph[c, s:s + WIN], am[c, s:s + WIN]) for c in range(len(sel))])
            seg = xs[:, s:s + WIN]
            F = np.abs(np.fft.rfft(seg * np.hanning(WIN), axis=1)) ** 2
            f = np.fft.rfftfreq(WIN, 1 / FS)
            k40 = np.argmin(np.abs(f - 40))
            nb = np.r_[k40 - 6:k40 - 2, k40 + 3:k40 + 7]  # neighbours 37-38.5, 41.5-43 Hz
            snr = np.mean(10 * np.log10(F[:, k40] / F[:, nb].mean(1)))
            rows.append((s / FS, int(e.is_stim), mi, snr))
    r = np.array(rows)
    return r[np.argsort(r[:, 0])]


def r2(y, yh):
    return 1 - np.sum((y - yh) ** 2) / np.sum((y - y.mean()) ** 2)


def main():
    subs = subjects()
    D = {s: per_subject(s) for s in subs}
    res = {"n_subjects": len(subs)}
    # Q1 autocorrelation (within stim blocks and overall)
    ac = [stats.pearsonr(d[:-1, 2], d[1:, 2])[0] for d in D.values()]
    res["Q1_lag1_autocorr_PAC_mean"] = float(np.mean(ac))
    ac_snr = [stats.pearsonr(d[:-1, 3], d[1:, 3])[0] for d in D.values()]
    res["Q1_lag1_autocorr_SNR40_mean"] = float(np.mean(ac_snr))
    # Q2 stim vs rest
    for j, name in [(2, "PAC_MI"), (3, "SNR40_dB")]:
        st = np.array([d[d[:, 1] == 1, j].mean() for d in D.values()])
        rs = np.array([d[d[:, 1] == 0, j].mean() for d in D.values()])
        diff = st - rs
        dz = diff.mean() / diff.std(ddof=1)
        res[f"Q2_{name}_stim_minus_rest"] = dict(mean_stim=float(st.mean()), mean_rest=float(rs.mean()),
                                                 cohen_dz=float(dz), wilcoxon_p=float(stats.wilcoxon(diff).pvalue),
                                                 n_pos=int((diff > 0).sum()))
    # Q3 forecasting at horizons h windows (2 s each), pooled over all subjects (leave-one-subject-out for
    # the stim offset), causal running subject mean.
    out = {}
    for h in [1, 2, 3, 4, 5]:
        ys, yp, ysch, yar = [], [], [], []
        for s in subs:
            d = D[s]
            others = np.concatenate([D[o] for o in subs if o != s])
            # stim offset relative to each other-subject mean (learned out-of-subject)
            off = np.mean([D[o][D[o][:, 1] == 1, 2].mean() - D[o][:, 2].mean() for o in subs if o != s])
            frac_st = np.mean([np.mean(D[o][:, 1]) for o in subs if o != s])
            y = d[:, 2]
            for t in range(10, len(d) - h):
                rm = y[:t + 1].mean()  # causal running mean of the subject
                ys.append(y[t + h]); yp.append(y[t])
                ysch.append(rm + off * (d[t + h, 1] - frac_st))  # schedule known in advance
                yar.append(rm)
        ys, yp, ysch, yar = map(np.array, (ys, yp, ysch, yar))
        out[f"h{h}_{2*h}s"] = dict(persistence=r2(ys, yp), running_subject_mean=r2(ys, yar),
                                   subject_mean_plus_schedule=r2(ys, ysch))
    res["Q3_pooled_R2"] = out
    OUT.mkdir(exist_ok=True, parents=True)
    json.dump(res, open(OUT / "audit_pac_forecast.json", "w"), indent=1)
    np.savez(OUT / "audit_window_table.npz", **{s: D[s] for s in subs})
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
