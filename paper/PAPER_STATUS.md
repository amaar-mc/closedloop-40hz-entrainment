---
status: drafting
target_conference: MIT URTC 2026 paper presentation
submission_deadline: TBD - official Fall 2026 cycle not yet posted
last_updated: 2026-05-31
---

# Research Paper — Status

## Paper

**Title (working):** Feature-Selected Temporal Forecasting for Retrospective Closed-Loop 40 Hz Auditory Entrainment

**One-line:** A causal TCN using 12 PAC-trajectory and stimulation-context features predicts future coupling on held-out participants; retrospective replay reveals a controller targeting-specificity tradeoff that must be calibrated before live testing.

## Target Conference

Selected planning target: MIT URTC 2026 paper presentation.

See `conferences/targets.md` and `conferences/mit_urtc_2026/README.md`.

## Progress

| Section      | Draft | Reviewed | Final |
| ------------ | ----- | -------- | ----- |
| Abstract     | draft | —        | —     |
| Introduction | draft | —        | —     |
| Related Work | draft | —        | —     |
| Methods      | draft | —        | —     |
| Results      | draft | —        | —     |
| Discussion   | draft | —        | —     |
| Conclusion   | draft | —        | —     |

## Figures

| Figure                  | Status | File                                            |
| ----------------------- | ------ | ----------------------------------------------- |
| System pipeline diagram | exists | `results/figures/system_block_diagram.pdf`      |
| Horizon sweep           | exists | `results/figures/horizon_sweep.pdf`             |
| Controller comparison   | exists | `results/figures/controller_comparison_v2.pdf`  |
| PAC targeting gap       | exists | `results/figures/pac_targeting_gap.pdf`         |
| Per-subject utility     | exists | `results/figures/per_subject_utility.pdf`       |
| Timeline example        | exists | `submission/paper/figures/timeline_example.pdf` |
| Feature ablation table  | —      | needs standalone figure                         |
| Threshold sensitivity   | exists | `results/figures/threshold_sensitivity.pdf`     |

## Key Numbers (claim-generation aware)

- EEGNet: 1,457 params, test R² = 0.287 (ceiling — not model capacity limit)
- Feature-ablation TCN: 73 features R² = −0.025; 12 PAC+Stim features R² = 0.558
- Five-seed 12-feature forecasting experiment: mean R² = 0.606, range 0.558–0.647
- Current integrated 12-feature replay checkpoint: 27,139 params, test R² = 0.5844
- Current replay: 73.8% low-PAC targeting vs 51.7% reactive
- Current replay: 62.2% balanced alignment vs 64.5% reactive

The older 73-feature replay headline (72.1% alignment, 82.6% low-PAC targeting) is historical and
must not be attributed to the current 12-feature checkpoint.
