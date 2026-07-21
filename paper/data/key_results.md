# Key Results - Claim-Aware Reference

This file separates current results from historical model generations. Use machine-readable artifacts
for submission claims and do not combine controller metrics across checkpoints.

## Dataset

- OpenNeuro `ds005048` version `1.0.1` (Lahijanian et al. 2024)
- 35 participants in the local BIDS release
- 19 recorded EEG channels; 7 frontal channels selected for this pipeline:
  `Fp1`, `Fp2`, `F7`, `F3`, `Fz`, `F4`, `F8`
- 250 Hz sampling rate
- Two-second windows with one-second hop
- Subject-level temporal split: 24 train / 5 validation / 6 test participants
- Temporal samples: 11,160 train / 2,605 validation / 2,678 test

Sources:

- `data/raw/ds005048/dataset_description.json`
- `data/raw/ds005048/participants.tsv`
- `data/processed/multiscale_temporal_lb20_hz5_ts1/metadata.json`

## Selected Temporal Representation

The selected representation uses 12 temporally ordered inputs:

- 7 PAC trajectory features: current PAC, trailing means over 2/4/8/16 steps, and differences over
  1 and 4 steps
- 5 stimulation-context features: on/off state, normalized time since switch, recent stimulation
  fraction, protocol-cycle sine, and protocol-cycle cosine

Source: `temporal_multiscale/build_multiscale_dataset.py`

## Generation A: Feature-Selection Experiments

### Single-Seed Feature Ablation

| Feature subset                       | Features |  Test R^2 |
| ------------------------------------ | -------: | --------: |
| Spectral only                        |       61 |    -0.420 |
| All candidate features               |       73 |    -0.025 |
| PAC trajectory only                  |        7 |     0.344 |
| PAC trajectory + stimulation context |       12 | **0.558** |

Source: `archive/experimental/results/generalization_7ch.json`

### Five-Seed Forecasting Experiment

|     Seed |  Test R^2 |
| -------: | --------: |
|       42 |     0.558 |
|      123 |     0.620 |
|      456 |     0.597 |
|      789 |     0.608 |
|     2024 |     0.647 |
| **Mean** | **0.606** |

Range: `0.558-0.647`.

The raw test values produce population SD `0.0291` and sample SD `0.0326`. State the convention if
reporting an SD. Prefer the exact rounded mean and range in submission prose.

Source: `archive/experimental/results/pac_stim_focused.json`

### Single-Seed Horizon Sweep

| Horizon | TCN Test R^2 | Persistence R^2 |
| ------: | -----------: | --------------: |
|     1 s |        0.725 |           0.726 |
|     3 s |        0.607 |           0.178 |
|     5 s |        0.577 |           0.104 |
|     8 s |        0.370 |          -0.007 |
|    10 s |        0.669 |          -0.081 |

The 10-second value is a single-seed result and should be replicated before it is treated as a
stable estimate.

Source: `archive/experimental/results/horizon_sweep_pac_stim.json`

## Generation B: Current 12-Feature Controller Integration

Current checkpoint: `models/best_12feat_tcn_lb20_hz5_ts1.pth`

- Inputs: 12 PAC+Stim features
- Lookback: 20 steps
- Horizon: 5 steps
- Trainable parameters: 27,139

The manuscript reports the architecture parameter count here but keeps forecasting-study,
target-definition stress-test, and controller-replay metrics separate because they come from
different generation paths. The validation command prints checkpoint metadata `test_r2=0.5844`, but
that value is not used as a standalone manuscript result.

### Retrospective Replay on 35 Recorded PAC Trajectories

| Strategy                    | Alignment | Low-PAC Stim | High-PAC Rest |           PAC Gap |
| --------------------------- | --------: | -----------: | ------------: | ----------------: |
| Fixed schedule              |     45.0% |        61.4% |         28.6% |     -6.55 x 10^-6 |
| Reactive threshold          | **64.5%** |        51.7% |     **77.3%** | **21.09 x 10^-6** |
| TCN predictive (12-feature) |     62.2% |    **73.8%** |         50.7% |     21.02 x 10^-6 |
| Alignment oracle            |    100.0% |       100.0% |        100.0% |     33.36 x 10^-6 |

The current TCN improves low-PAC targeting but reduces high-PAC rest specificity. Its balanced
alignment is lower than reactive thresholding. This is a mixed offline result, not evidence of
therapeutic efficacy.

Sources:

- `scripts/pipeline/run_12feat_validation.py`
- `results/metrics/controller_comparison_12feat.json`

## Generation C: Historical 73-Feature Replay

The older `models/best_multiscale_tcn_lb20_hz5_ts1.pth` replay reports:

- TCN predictive alignment: 72.1%
- Low-PAC stimulation targeting: 82.6%
- PAC gap: 30.5 x 10^-6

These are historical results for a different checkpoint. Do not attribute them to the current
12-feature controller.

Source: `results/metrics/tcn_validation_results.json`

## Submission Boundaries

- Use **retrospective controller replay** or **offline replay**.
- Do not claim clinical efficacy, prospective deployment, patient outcomes, or reduced disease
  progression.
- State that event-level PAC labels limit transition resolution.
- State that PAC values are complete-event summaries assigned back to constituent windows. The
  stored-series forecast is not yet an end-to-end streaming prediction.
- State that replay does not model physiological responses to counterfactual decisions.
- Treat spectral-feature anatomy explanations as hypotheses consistent with ablation, not proven
  mechanisms.
