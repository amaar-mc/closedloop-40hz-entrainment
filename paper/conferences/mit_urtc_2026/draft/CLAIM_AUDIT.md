# MIT URTC Draft Claim Audit

This file records which result generation supports each manuscript claim. It exists because older
project documents combine metrics from different checkpoints.

## Generation A: Feature-Selection Experiments

Primary artifacts:

- `archive/experimental/results/generalization_7ch.json`
- `archive/experimental/results/pac_stim_focused.json`
- `archive/experimental/results/horizon_sweep_pac_stim.json`

Use this generation for:

- The single-seed feature ablation: 73 features `R^2 = -0.025`; 12 PAC+Stim features
  `R^2 = 0.558`.
- The five-seed 12-feature forecasting result: mean `R^2 = 0.606`, range `0.558-0.647`.
- The single-seed horizon sweep and persistence comparison.

The archived experiment reports `22,914` parameters for its hidden-64 TCN implementation.
Its prose summary reports `+/- 0.032`, but the raw five values produce population SD `0.0291` and
sample SD `0.0326`. The manuscript reports the exact rounded mean and range to avoid an unstated SD
convention.

## Generation B: Current 12-Feature Controller Integration

Primary artifacts:

- `models/best_12feat_tcn_lb20_hz5_ts1.pth`
- `scripts/pipeline/run_12feat_validation.py`
- `results/metrics/controller_comparison_12feat.json`

Verified locally on 2026-05-31 with:

```bash
python3 scripts/pipeline/run_12feat_validation.py --no-train
```

The replay was refreshed again after the final editorial revision. The checkpoint metadata and
35-trajectory controller table remained unchanged.

The current integrated checkpoint has:

- 12 PAC+Stim inputs
- 20-step lookback
- 5-step forecast horizon
- `27,139` trainable parameters
- checkpoint metadata test `R^2 = 0.5844`

Its retrospective replay summary is:

| Strategy | Alignment | Low-PAC Stim | High-PAC Rest | PAC Gap |
|---|---:|---:|---:|---:|
| Fixed schedule | 45.01% | 61.43% | 28.59% | -6.55 x 10^-6 |
| Reactive threshold | 64.49% | 51.67% | 77.30% | 21.09 x 10^-6 |
| TCN predictive (12-feat) | 62.23% | 73.77% | 50.68% | 21.02 x 10^-6 |
| Alignment oracle | 100.00% | 100.00% | 100.00% | 33.36 x 10^-6 |

The TCN improves low-PAC targeting but reduces high-PAC rest specificity. Its balanced alignment is
lower than the reactive controller's alignment. This is a mixed result and must be stated as such.
The replay includes trajectories from all 35 participants across the training, validation, and test
splits. It is a full-cohort integration diagnostic, not an additional held-out forecasting test.

## Generation C: Historical 73-Feature Replay

Primary artifact:

- `results/metrics/tcn_validation_results.json`

This older replay reports `72.1%` alignment and `82.6%` low-PAC targeting for an older
`31,043`-parameter checkpoint. These values may be discussed only as historical model-generation
context. They must not be attributed to the final 12-feature checkpoint.

## Required Wording

- Use **retrospective controller replay** or **offline replay**, not clinical validation.
- State that replay decisions are evaluated against recorded PAC trajectories.
- State that the replay does not estimate the physiological effect of counterfactual decisions.
- State the epoch-level PAC-label granularity limitation.
- State that complete-event PAC summaries are assigned back to constituent windows. Future-index
  ordering within the stored series does not establish online availability of the PAC inputs.
- Do not claim that spectral features are proven to encode anatomy. The ablation only shows that the
  larger spectral feature set generalizes poorly across held-out participants.
