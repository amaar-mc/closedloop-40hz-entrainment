# Numbers Sheet: Know These Cold

Print this. Review before each interview round.

---

## Dataset
| | Value |
|---|---|
| Source | OpenNeuro ds005048 (Lahijanian 2024) |
| Subjects | 35 (17 AD, 6 MCI, 10 HC, 2 unspec) |
| Channels | 7 frontal (Fp1, Fp2, F7, F3, Fz, F4, F8) |
| Sampling rate | 250 Hz |
| Windows | 17,283 (2-second, 1-second hop) |
| Train / Val / Test | 24 / 5 / 6 subjects |
| Stim protocol | 40s on, 20s off, repeating |

## Stage 1: EEGNet (Static PAC Estimator)
| | Value |
|---|---|
| Parameters | 1,457 |
| Input | (batch, 1, 7, 500) = 7ch x 2s x 250Hz |
| Output | Scalar PAC estimate |
| Test R2 | 0.287 |
| Architectures tested | 8 (1,457 to 1.1M params) |
| Result | ALL converge to 0.287 |

## Stage 2: Causal TCN (Temporal PAC Forecaster)
| | Value |
|---|---|
| Parameters | 22,914 (hidden=64) |
| Features | 12 (7 PAC + 5 stim context) |
| Lookback | 20 steps (20 seconds) |
| Horizon | 5 seconds |
| Dilations | [1, 2, 4, 8] |
| Receptive field | 31 steps |
| Loss | Huber + multi-task delta + consistency |
| Optimizer | AdamW |
| Early stopping | patience = 20 |

## Feature Ablation
| Feature set | # | Test R2 |
|---|---|---|
| All (spectral + PAC + stim) | 73 | -0.025 |
| PAC only | 7 | 0.344 |
| **PAC + Stim (final)** | **12** | **0.558** |
| Spectral only | 61 | -0.420 |

## Multi-Seed Validation (h=5s, 12 features)
| Seed | Val R2 | Test R2 |
|---|---|---|
| 42 | 0.804 | 0.558 |
| 123 | 0.822 | 0.620 |
| 456 | 0.799 | 0.597 |
| 789 | 0.831 | 0.608 |
| 2024 | 0.846 | 0.647 |
| **Mean +/- Std** | **0.820 +/- 0.019** | **0.606 +/- 0.032** |

## Horizon Sweep (PAC+Stim features, seed 42)
| Horizon | Persistence R2 | TCN R2 | Margin |
|---|---|---|---|
| 1s | 0.726 | 0.725 | -0.001 |
| 3s | 0.178 | 0.607 | +0.429 |
| 5s | 0.104 | 0.577 | +0.473 |
| 8s | -0.007 | 0.370 | +0.377 |
| 10s | -0.081 | 0.669 | +0.751 |

## Controller Comparison (N=35, Real EEG Replay)
| Controller | Alignment | Low-PAC Stim | PAC Gap (x10^-6) |
|---|---|---|---|
| Fixed Schedule | 45.0% | 61.4% | -6.6 |
| Reactive | 64.5% | 51.7% | +21.1 |
| **TCN Predictive** | **72.1%** | **82.6%** | **+30.5** |
| Hybrid | 73.8% | 85.3% | +34.0 |
| Oracle | 100% | 100% | +33.3 |

## Statistical Significance (TCN vs Reactive)
| Metric | TCN | Reactive | g [95% CI] | p |
|---|---|---|---|---|
| Alignment | 72.1% | 64.5% | 1.31 [0.75, 1.87] | <0.001 |
| Low-PAC Stim | 82.6% | 51.7% | 4.47 [3.33, 5.62] | <0.001 |
| PAC Gap | 30.5 | 21.1 | 1.57 [0.98, 2.17] | <0.001 |

## Key Single Numbers
| | |
|---|---|
| Subjects benefiting | 35/35 (binomial p < 0.001) |
| Oracle proximity | 91% (30.5 / 33.3) |
| Inference time | < 50 ms |
| Hardware cost | ~ $250 (Muse 2 + headphones) |
| Alzheimer's global | 55 million (WHO) |
| Alzheimer's US | 6.9 million |
| Cognito trial size | 670 patients (Phase 3) |
| Cognito funding | $105 million (March 2026) |
| Iaccarino amyloid reduction | 40-50% in mice |
| Non-responder rate | ~30% (Fortunato) |
| Habituation | ~50% of subjects in dataset |

## The 12 Features (in order)
1. pac_current
2. pac_ma2 (causal moving avg, 2 windows)
3. pac_ma4
4. pac_ma8
5. pac_ma16
6. pac_diff1 (first-order difference)
7. pac_diff4 (4-step difference)
8. stim_state (binary: 0=rest, 1=stim)
9. time_since_switch (normalized to 60s)
10. stim_frac_20s (stimulation fraction, last 20s)
11. cycle_phase_sin
12. cycle_phase_cos
