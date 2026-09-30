# AI-assisted code (Claude Code, 2026-09/10); reviewed and run by the student. See sts2026/AI_DISCLOSURE_LOG.md
"""EXPLORATORY (discovery ds005048): stimulus-locked spectrum of the response to 40-Hz clicks.

A linear time-invariant system driven by a 40-Hz periodic input can only respond at 40 Hz and its
harmonics (80, 120 ...). A phase-locked response at the 20-Hz SUBharmonic (or 60 Hz = 3/2) would
indicate nonlinear (e.g. period-doubling oscillator) dynamics (cf. Metzner & Steuber 2021 model).
Measure: within each stimulation block, 1-s epochs (integer number of 40- and 20-Hz cycles) -> ITC per
block at frequency f; average over blocks (phase ambiguity of a period-doubled response between blocks
is therefore allowed). Bias floor: same measure at neighbouring non-harmonic frequencies and in silence.
"""
import json
import numpy as np
from scipy import stats
from ds005048_io import load, subjects, FS
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "results"
CH = ["Fz", "F3", "F4", "Cz", "C3", "C4"]
FREQS = [18, 19, 20, 21, 22, 38, 39, 40, 41, 42, 58, 59, 60, 61, 62]


def block_itc(sig, a, b, f):
    L = int(FS)
    t = np.arange(L) / FS
    k = np.exp(-2j * np.pi * f * t) * np.hanning(L)
    z = np.array([sig[s:s + L] @ k for s in range(a, b - L + 1, L)])
    return np.abs(np.mean(z / np.abs(z))), len(z)


def main():
    rows = []
    for sub in subjects():
        x, ch, ev = load(sub)
        sig = x[[ch.index(c) for c in CH]].mean(0)
        r = {"sub": sub}
        for cond, flag, skip in [("stim", True, 1), ("rest", False, 2)]:
            blocks = ev[(ev.is_stim == flag) & (ev.stop - ev.start >= 20 * FS)]
            for f in FREQS:
                vals = [block_itc(sig, e.start + int(skip * FS), e.start + int(19 * FS) + int(skip * FS), f)[0]
                        for _, e in blocks.iterrows()]  # 18-19 epochs per block, equal n across conditions
                r[f"{cond}_{f}"] = float(np.mean(vals))
        rows.append(r)
    res = {}
    for f in [20, 40, 60]:
        nb = [f - 2, f - 1, f + 1, f + 2]
        for cond in ["stim", "rest"]:
            d = np.array([r[f"{cond}_{f}"] - np.mean([r[f"{cond}_{g}"] for g in nb]) for r in rows])
            res[f"{cond}_{f}Hz_minus_neighbours"] = dict(mean=float(d.mean()), dz=float(d.mean() / d.std(ddof=1)),
                                                         p_wilcoxon=float(stats.wilcoxon(d).pvalue),
                                                         n_pos=int((d > 0).sum()))
        d = np.array([r[f"stim_{f}"] - r[f"rest_{f}"] for r in rows])
        res[f"stim_minus_rest_{f}Hz"] = dict(mean=float(d.mean()), dz=float(d.mean() / d.std(ddof=1)),
                                             p_wilcoxon=float(stats.wilcoxon(d).pvalue), n_pos=int((d > 0).sum()))
    res["grand_means"] = {k: float(np.mean([r[k] for r in rows])) for k in rows[0] if k != "sub"}
    json.dump(res, open(OUT / "explore_subharmonic_ds005048.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "grand_means"}, indent=1))
    print({k: round(v, 3) for k, v in res["grand_means"].items()})


if __name__ == "__main__":
    main()
