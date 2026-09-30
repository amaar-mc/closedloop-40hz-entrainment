# AI-assisted code (Claude Code, 2026-09/10); reviewed and run by the student. See sts2026/AI_DISCLOSURE_LOG.md
"""EXPLORATORY feasibility (discovery set ds005048 only): can we resolve the build-up and decay of the
stimulus-locked 40-Hz response at block onset/offset in older adults?

Phase reference trick (removes event-marker jitter): for each stimulation block, the complex 40-Hz
Fourier coefficient of the block's steady-state middle (5..35 s) defines the block's stimulus phase.
Around onset/offset we compute the complex 40-Hz coefficient in short sliding windows (100 ms = 4 cycles,
step 12 ms) using a phase clock continuous with that steady state, and project it onto the steady-state
phase: A(t) = Re(c(t) * conj(c_ss)/|c_ss|) / |c_ss|  (1 = steady state, 0 = no locked response).
Linear-time-invariant (LTI) superposition predicts onset A_on(t) + offset A_off(t) = 1 (complementarity).
A synthetic LTI control is analysed identically (steady-state waveform switched on/off), which gives the
curve expected from the analysis window alone.
"""
import json
import numpy as np
from ds005048_io import load, subjects, FS
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "results"
CH = ["Fz", "F3", "F4", "Cz", "C3", "C4", "FC1"]
F0 = 40.0
WIN = int(0.1 * FS)          # 100 ms analysis window
STEP = 3                     # 12 ms
PRE, POST = int(0.5 * FS), int(1.0 * FS)


def coef(seg):
    t = np.arange(seg.shape[-1]) / FS
    return seg @ np.exp(-2j * np.pi * F0 * t)


def curve(sig, t0, clock0, ref):
    """sig: 1-D; t0 = event sample; clock0 = sample whose phase defines the 40-Hz clock."""
    out = []
    for c in range(t0 - PRE, t0 + POST - WIN, STEP):
        seg = sig[c:c + WIN]
        z = coef(seg) * np.exp(-2j * np.pi * F0 * (c - clock0) / FS)
        out.append(np.real(z * np.conj(ref)) / np.abs(ref) ** 2)
    return np.array(out)


def main():
    on_all, off_all, on_syn, off_syn = [], [], [], []
    for sub in subjects():
        x, ch, ev = load(sub)
        sig = x[[ch.index(c) for c in CH if c in ch]].mean(0)
        for _, e in ev[ev.is_stim].iterrows():
            if e.stop + POST > sig.size or e.start - PRE < 0:
                continue
            a, b = e.start + int(5 * FS), e.start + int(35 * FS)
            n = (b - a) // WIN * WIN
            # steady-state reference in WIN-length pieces with the same clock
            ref = np.mean([coef(sig[k:k + WIN]) * np.exp(-2j * np.pi * F0 * (k - e.start) / FS)
                           for k in range(a, a + n, WIN)])
            on_all.append(curve(sig, e.start, e.start, ref))
            off_all.append(curve(sig, e.stop, e.start, ref))
            # synthetic LTI control: pure steady-state sinusoid gated on/off at the markers
            tt = np.arange(sig.size)
            syn = np.real(2 * ref / WIN * np.exp(2j * np.pi * F0 * (tt - e.start) / FS))
            gate = ((tt >= e.start) & (tt < e.stop)).astype(float)
            on_syn.append(curve(syn * gate, e.start, e.start, ref))
            off_syn.append(curve(syn * gate, e.stop, e.start, ref))
    t = (np.arange(-PRE, POST - WIN, STEP) + WIN / 2) / FS
    on, off = np.mean(on_all, 0), np.mean(off_all, 0)
    res = dict(n_blocks=len(on_all), t=t.round(3).tolist(),
               onset=on.round(3).tolist(), offset=off.round(3).tolist(),
               complementarity=(on + off).round(3).tolist(),
               onset_synthetic=np.mean(on_syn, 0).round(3).tolist(),
               offset_synthetic=np.mean(off_syn, 0).round(3).tolist(),
               sem_onset=(np.std(on_all, 0) / np.sqrt(len(on_all))).round(3).tolist())
    json.dump(res, open(OUT / "explore_onset_offset_ds005048.json", "w"), indent=1)
    for k in range(0, len(t), 6):
        print(f"t={t[k]:+.3f}  on={on[k]:+.2f}  off={off[k]:+.2f}  sum={on[k]+off[k]:+.2f}  "
              f"syn_on={res['onset_synthetic'][k]:+.2f} syn_off={res['offset_synthetic'][k]:+.2f} sem={res['sem_onset'][k]:.2f}")


if __name__ == "__main__":
    main()
