# Key Results — Ground Truth Reference

Source of truth: `submission/poster/v6_board.md`, `results/RESULTS_REPORT.md`, `csef/lab_notebook/vfinal_lab_notebook.md`

## Dataset

- OpenNeuro ds005048 (Lahijanian et al. 2024)
- 35 elderly subjects, 7 frontal EEG channels (Fp1, Fp2, F3, F4, F7, F8, Fz), 250 Hz
- Alternating 40 Hz AM auditory stimulus / rest epochs (20-40s each)
- 17,283 two-second windows; subject-level splits: 24 train / 5 val / 6 test

## Stage 1: Static PAC Estimation (Architecture Search)

| Architecture | Parameters | Test R² |
|---|---|---|
| EEGNet (V1) — selected | 1,457 | 0.287 |
| SpecTempNet (V3) | 180K | 0.236 |
| ViT-TCNet (V4) | ~1.1M | 0.252 |
| Ridge Regression (V5) | 135 coefs | 0.287 |
| ATCNet (V8) | 25K | 0.22 |
| EEGNetLarge (rigor) | 141K | 0.287 |

**Key finding:** R²=0.287 is a data ceiling (epoch-level PAC labels on 2s windows). Model capacity irrelevant above ~1.5K params.

## Stage 2: Temporal Prediction — Feature Ablation

| Feature Subset | # Features | Val R² | Test R² |
|---|---|---|---|
| All features | 73 | 0.333 | −0.025 |
| Spectral only | 61 | −0.044 | −0.420 |
| **PAC + Stim context** | **12** | **0.804** | **0.558** (single seed) |
| PAC + Stim (5-seed) | 12 | — | **0.606 ± 0.032** |

**Key finding:** Spectral features (indices 0-60) encode subject anatomy, not generalizable signal. PAC+Stim features (indices 61-72) are portable across subjects.

### The 12 PAC+Stim Features

PAC trajectory (7): current PAC, 4 trailing moving averages (2/4/8/16 steps), 2 differences (1-step, 4-step)
Stimulation context (5): on/off state, time since last switch (normalized), recent stim fraction (20-step window), protocol cycle sin, protocol cycle cos

## Stage 2: Horizon Sweep (12-feat PAC+Stim TCN)

| Horizon | Persistence R² | Ridge R² | TCN R² |
|---|---|---|---|
| 1s | ~0.76 | ~0.81 | ~0.74 |
| 3s | negative | negative | 0.577 |
| 5s | negative | negative | 0.606 |
| 10s | negative | negative | 0.669 |

**Key finding:** At 3-10s (proactive control range), only TCN provides useful predictions. +0.47 R² margin over best baseline.

## Stage 3: Closed-Loop Controller Validation (N=35, real EEG)

| Controller | Alignment | Low-PAC Stim | High-PAC Rest | PAC Gap (×10⁻⁶) | Stim % |
|---|---|---|---|---|---|
| Fixed Schedule | 45.0% | 61.4% | 28.6% | −6.6 (wrong dir.) | 66.6% |
| Reactive | 64.5% | 51.7% | 77.3% | +21.1 | 36.7% |
| **TCN Predictive** | **72.1%** | **82.6%** | **61.6%** | **+30.5** | **59.7%** |
| Oracle (upper bound) | 100.0% | 100.0% | 100.0% | +33.3 | 48.3% |

**Statistics (TCN vs Reactive, Wilcoxon signed-rank):**
- Alignment: Hedges' g = 1.31 [CI: ...], p < 0.001
- Low-PAC Stim: Hedges' g = 4.47, p < 0.001
- PAC gap: Hedges' g = 1.57, p < 0.001
- PAC gap oracle fraction: 30.5 / 33.3 = **91.6% → reported as 91%**
- 35/35 subjects benefit (binomial p < 0.001)

## Fatigue Robustness (Simulation)

| Fatigue Level | Fixed Efficiency | Adaptive Efficiency | Improvement |
|---|---|---|---|
| None | 0.343 | 0.375 | +9.5%*** |
| Mild | 0.341 | 0.375 | +10.0%*** |
| Moderate | 0.335 | 0.366 | +9.0%*** |
| High | 0.319 | 0.354 | +10.8%*** |
| Severe | 0.316 | 0.352 | +11.2%*** |

***p < 0.001, Hedges' g = 1.7–2.4

## Model Architecture

**EEGNet (Stage 1):**
- Input: (batch, 1, 7, 500) — 7 ch × 2s @ 250 Hz
- Temporal conv → depthwise spatial conv → separable conv → FC
- ~1,457 params

**Causal TCN (Stage 2):**
- Input: (batch, 20, 12) — 20-step lookback × 12 features
- Dilated causal depthwise-separable conv, dilations [1,2,4,8]
- GroupNorm, attention pooling, dual head (future PAC + delta-PAC)
- 5,154 params (h=32); 31-step receptive field
- Checkpoint: `models/best_12feat_tcn_lb20_hz5_ts1.pth`

## Reproducibility

- 5 random seeds (h=64 variant): test R² range 0.558–0.647, mean 0.606 ± 0.032
- Shuffle-label R² = −0.332 (confirms real signal, not artifact)
- Causal dataset verified (no future leakage): `scripts/audit/validate_leakage.py`
- Subject-level splits verified: no within-subject overlap across train/val/test
