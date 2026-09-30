# AI-assisted code (Claude Code, 2026-09/10); reviewed and run by the student. See sts2026/AI_DISCLOSURE_LOG.md
"""Audit: reproduce how block-level ('epoch') PAC labels inflate forecast R^2.

Original pipeline (src/data_loader.py::extract_stimulus_windows): each 2-s window (1-s hop) inside a
20-40 s Stimulus/Rest block receives the MI of the WHOLE block (future samples included).
Here we rebuild those labels and score two predictors that contain no learned EEG dynamics:
  persistence          y(t+h) := y(t)
  schedule_lookup      if t+h is in the same block as t -> y(t) (label already encodes the whole block),
                       else -> causal mean of the subject's previous blocks of the upcoming type.
Pooled R^2 over all 35 subjects. Output: sts2026/results/audit_block_label_artifact.json
"""
import json
import numpy as np
from scipy.signal import butter, sosfiltfilt, hilbert
from ds005048_io import load, subjects, FS
from audit_pac_forecast import mi_tort, FRONTAL, OUT

W, HOP = int(2 * FS), int(1 * FS)


def subject_rows(sub):
    x, ch, ev = load(sub)
    xs = x[[ch.index(c) for c in FRONTAL]]
    th = sosfiltfilt(butter(4, [4, 8], "band", fs=FS, output="sos"), xs, axis=1)
    ga = sosfiltfilt(butter(4, [38, 42], "band", fs=FS, output="sos"), xs, axis=1)
    ph, am = np.angle(hilbert(th, axis=1)), np.abs(hilbert(ga, axis=1))
    rows = []
    for b, e in ev.reset_index(drop=True).iterrows():
        if e.stop - e.start < W:
            continue
        lab = np.mean([mi_tort(ph[c, e.start:e.stop], am[c, e.start:e.stop]) for c in range(xs.shape[0])])
        for s in range(e.start, e.stop - W, HOP):
            rows.append((b, int(e.is_stim), lab))
    return np.array(rows)


def r2(y, yh):
    y, yh = np.asarray(y), np.asarray(yh)
    return float(1 - np.sum((y - yh) ** 2) / np.sum((y - y.mean()) ** 2))


def main():
    D = {s: subject_rows(s) for s in subjects()}
    out = {}
    for h in [1, 3, 5, 10]:
        Y, P, S = [], [], []
        for d in D.values():
            for t in range(20, len(d) - h):
                y_now, y_fut = d[t, 2], d[t + h, 2]
                Y.append(y_fut); P.append(y_now)
                if d[t + h, 0] == d[t, 0]:
                    S.append(y_now)
                else:
                    prev = d[:t + 1]
                    same_type = prev[prev[:, 1] == d[t + h, 1]]
                    S.append(same_type[:, 2].mean() if len(same_type) else prev[:, 2].mean())
        out[f"h{h}s"] = dict(persistence=r2(Y, P), schedule_lookup=r2(Y, S), n=len(Y))
    json.dump(out, open(OUT / "audit_block_label_artifact.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
