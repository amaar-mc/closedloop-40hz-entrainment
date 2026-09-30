# AI-assisted code (Claude Code, 2026-10); reviewed and run by the student. See sts2026/AI_DISCLOSURE_LOG.md
"""EXPLORATORY (post-registration) E5: do recording-noise differences explain the group trend (AD < CN) or the
H4 prediction? Uses outputs of confirmatory.py and explore_post_registration.e4()."""
import json, numpy as np, pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from sklearn.linear_model import Ridge
import confirmatory as CF, explore_post_registration as E

N = pd.read_csv(E.OUT / 'gamma_noise_silence.csv').set_index('sid')
B = pd.read_csv(CF.OUT / 'dv56_blocks_primary.csv'); grp = B.drop_duplicates('sid').set_index('sid').group
A1 = CF.pivot(B, 'R40_1min', 'periodic_A'); A = CF.pivot(B, 'R40', 'periodic_A')
T = pd.concat([A1, A, N.gamma_noise_silence, grp], axis=1, keys=['A1', 'A', 'noise', 'g']).dropna()
out = {'noise_median_by_group': T.groupby('g').noise.median().to_dict()}
T['g'] = pd.Categorical(T.g, categories=['older_CN', 'young_CN', 'AD'])
for name, f in [('with_noise', 'A1 ~ C(g) + noise'), ('without_noise', 'A1 ~ C(g)')]:
    m = smf.ols(f, data=T).fit()
    out[f'H2_ols_{name}'] = {k: [round(float(m.params[k]), 4), round(float(m.pvalues[k]), 4)] for k in m.params.index}
D = pd.read_csv(CF.OUT / 'ds005048_subjects_primary.csv').rename(columns={'Age': 'age'})
F = (pd.read_csv(CF.OUT / 'dv56_prestim_features.csv').set_index('sid').join(A.rename('R40'))
     .join(pd.read_csv(CF.OUT / 'dv56_ages.csv').set_index('sid')).join(N).dropna(subset=['R40']))
feats = ['aper_exp', 'aper_off', 'iaf', 'rel40', 'age']; z = lambda s: (s - s.mean()) / s.std()
Xtr = D[feats].apply(pd.to_numeric, errors='coerce'); Xtr = Xtr.fillna(Xtr.mean()).apply(z).values
mm = Ridge(alpha=1).fit(Xtr, z(D.R40).values)
Xte = F[feats].apply(pd.to_numeric, errors='coerce'); Xte = Xte.fillna(Xte.mean()).apply(z).values
F['pred'] = mm.predict(Xte)
for c in ['pred', 'R40', 'gamma_noise_silence']:
    F[c + '_c'] = F[c] - F.groupby('group')[c].transform('mean')


def partial(x, y, zz):
    ex = x - np.polyval(np.polyfit(zz, x, 1), zz); ey = y - np.polyval(np.polyfit(zz, y, 1), zz)
    return float(stats.pearsonr(ex, ey)[0])


out['H4_r_partial_noise'] = partial(F.pred.values, F.R40.values, F.gamma_noise_silence.values)
out['H4_r_groupcentred_partial_noise'] = partial(F.pred_c.values, F.R40_c.values, F.gamma_noise_silence_c.values)
out['pred_vs_noise_r'] = float(stats.pearsonr(F.pred, F.gamma_noise_silence)[0])
r = json.load(open(E.OUT / 'results.json')); r['E5_noise_vs_groups_and_H4'] = out
json.dump(r, open(E.OUT / 'results.json', 'w'), indent=1, default=float)
print(json.dumps(out, indent=1))
