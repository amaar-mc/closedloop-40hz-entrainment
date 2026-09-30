# AI-assisted code (Claude Code, 2026-10); reviewed and run by the student. See sts2026/AI_DISCLOSURE_LOG.md
"""EXPLORATORY (post-registration) E6: recording-noise check in the discovery cohort ds005048."""
import json, numpy as np, pandas as pd
from scipy import stats
from scipy.signal import welch
import statsmodels.formula.api as smf
from ds005048_io import load, subjects, FS
import confirmatory as CF

rows = []
for sub in subjects():
    x, ch, ev = load(sub); roi = x[[ch.index(c) for c in CF.ROI]].mean(0)
    rs = ev[(~ev.is_stim) & (ev.stop - ev.start >= 20 * FS)]
    P = np.mean([welch(roi[int(e.start) + int(2 * FS):int(e.stop)], fs=FS, nperseg=int(2 * FS))[1] for _, e in rs.iterrows()], 0)
    f = welch(roi[:1000], fs=FS, nperseg=int(2 * FS))[0]
    m = ((f >= 35) & (f <= 45)) & ~((f >= 39) & (f <= 41))
    rows.append(dict(sid=sub, noise=float(np.log10(P[m].mean()))))
N = pd.DataFrame(rows)
D = pd.read_csv(CF.OUT / 'ds005048_subjects_primary.csv').merge(N, on='sid')
out = dict(spearman_noise_vs_R40=float(stats.spearmanr(D.noise, D.R40)[0]), p=float(stats.spearmanr(D.noise, D.R40)[1]),
           noise_median_by_group=D.groupby('Group').noise.median().to_dict())
d = D[D.Group.isin(['Normal', 'Mild AD'])].copy(); d['AD'] = (d.Group == 'Mild AD').astype(int)
for fml in ['R40 ~ AD', 'R40 ~ AD + noise']:
    mm = smf.ols(fml, data=d).fit(); out[fml] = {k: [round(float(mm.params[k]), 4), round(float(mm.pvalues[k]), 4)] for k in mm.params.index}


def partial(x, y, z):
    ex = x - np.polyval(np.polyfit(z, x, 1), z); ey = y - np.polyval(np.polyfit(z, y, 1), z)
    return float(stats.spearmanr(ex, ey)[0])


out['split_half_partial_noise'] = partial(D.R40_odd.values, D.R40_even.values, D.noise.values)
OUT = CF.OUT.parent / 'exploratory_post'
N.to_csv(OUT / 'ds005048_gamma_noise_silence.csv', index=False)
r = json.load(open(OUT / 'results.json')); r['E6_ds005048_noise'] = out
json.dump(r, open(OUT / 'results.json', 'w'), indent=1, default=float)
print(json.dumps(out, indent=1))
