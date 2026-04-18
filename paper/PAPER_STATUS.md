---
status: drafting
target_conference: TBD
submission_deadline: TBD
last_updated: 2026-04-18
---

# Research Paper — Status

## Paper

**Title (working):** Personalized Deep Learning for Closed-Loop 40 Hz Gamma Entrainment: Feature Ablation Reveals Generalizable Temporal Prediction of Phase-Amplitude Coupling

**One-line:** A causal TCN using 12 PAC+stimulation context features (not spectral anatomy) predicts future entrainment 5-10 seconds ahead, enabling closed-loop adaptive scheduling that outperforms fixed and reactive protocols on real patient EEG.

## Target Conference

See `conferences/targets.md`

## Progress

| Section | Draft | Reviewed | Final |
|---|---|---|---|
| Abstract | — | — | — |
| Introduction | — | — | — |
| Related Work | — | — | — |
| Methods | — | — | — |
| Architecture Search | — | — | — |
| Results | — | — | — |
| Discussion | — | — | — |
| Conclusion | — | — | — |

## Figures

| Figure | Status | File |
|---|---|---|
| System pipeline diagram | exists | `results/figures/system_block_diagram.pdf` |
| Horizon sweep | exists | `results/figures/horizon_sweep.pdf` |
| Controller comparison | exists | `results/figures/controller_comparison_v2.pdf` |
| PAC targeting gap | exists | `results/figures/pac_targeting_gap.pdf` |
| Per-subject utility | exists | `results/figures/per_subject_utility.pdf` |
| Timeline example | exists | `submission/paper/figures/timeline_example.pdf` |
| Feature ablation table | — | needs standalone figure |
| Threshold sensitivity | exists | `results/figures/threshold_sensitivity.pdf` |

## Key Numbers (from ground truth)

- EEGNet: 1,457 params, test R² = 0.287 (ceiling — not model capacity limit)
- 12-feat TCN: 5,154 params, test R² = 0.606 ± 0.032 (5-seed mean)
- 73-feat TCN: test R² = −0.025 (spectral features cause generalization failure)
- Horizon 3-10s: TCN R² = 0.577–0.669 vs persistence collapse to negative
- Alignment: 72.1% TCN vs 64.5% reactive (g=1.31, p<0.001)
- Low-PAC targeting: 82.6% vs 51.7% (g=4.47, p<0.001)
- PAC gap: 91% of oracle bound
- 35/35 subjects benefit (binomial p<0.001)
- Fatigue: +9.0% to +11.2%, all p<0.001 across 5 severity levels
