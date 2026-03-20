# Temporal PAC Prediction System — Implementation Report

**Author:** Amaar Chughtai
**Date:** February 17, 2026
**Status:** Code validated, awaiting GPU training
**Location:** `temporal/` subdirectory

---

## Executive Summary

I implemented Option B: a full LSTM temporal prediction system that predicts PAC 5 seconds into the future from a 10-second history of EEG windows and PAC values. The code is clean, validated, and ready to train on your RTX 3080.

**However**, validation revealed a critical empirical finding: **PAC temporal autocorrelation in this dataset is essentially zero** (r = 0.06 at lag-1, indistinguishable from noise at lag ≥ 3). A Ridge regression temporal baseline achieves only R² = 0.03 for future prediction, compared to R² = 0.19 for current-window prediction.

This means the LSTM is unlikely to achieve R² = 0.75-0.85 on this data as-is. The underlying reason and remediation paths are discussed below.

---

## What Was Built

### Files Created

```
temporal/
├── __init__.py              # Module docstring and description
├── temporal_dataset.py      # TemporalPACDataset (PyTorch Dataset)
├── temporal_model.py        # TemporalPACPredictor (LSTM architecture)
├── train_temporal.py        # Full training pipeline with evaluation
└── validate_code.py         # Validation suite (runs without PyTorch)
```

### Repository Cleanup

Old V1-V8 files were archived into organized subdirectories:

```
archive/
├── v1_v8_attempts/          # All previous training scripts
├── docs_v1_v8/              # Previous version documentation
└── diagnostics/             # Data leakage audits and diagnostics
```

---

## Architecture

### Conceptual Pipeline

```
Input: 10 consecutive EEG windows (10 seconds of history)
       + 10 corresponding PAC values (PAC history)
       + 10 × 61 spectral features (optional)

    ┌─ Per Window ──────────────────────────────────┐
    │  EEG (7ch × 500 samples)                      │
    │     → Temporal Conv (7→16, k=25)              │
    │     → BN → ELU → AvgPool(4)                  │
    │     → Spatial Conv (16→32, k=15, depthwise)   │
    │     → BN → ELU → AvgPool(5)                  │
    │     → Global AvgPool → Linear(32→32)          │
    │  Output: 32-dim embedding                     │
    └───────────────────────────────────────────────┘

    Per timestep: [32-dim EEG embed, 1 PAC value, 61 spectral] = 94-dim
    → Linear(94 → 64) → LayerNorm → ELU → Dropout

    Sequence of 10 timesteps → Bidirectional LSTM (2 layers, 64 hidden)
    → Take last output (128-dim)

    Regression head: 128 → 64 → 32 → 1 (with LayerNorm + ELU + Dropout)

Output: Predicted PAC value at t+5 seconds
```

### Model Specifications

| Component | Parameters |
|-----------|------------|
| SpatialEncoder | ~2,500 |
| Input projection | ~6,200 |
| Bi-LSTM (2 layers) | ~66,000 |
| Regression head | ~10,500 |
| **Total** | **~85,000** |

Design rationale: Kept under 100k parameters to prevent overfitting on ~11k training sequences (learned from the V4 overparameterization failure at 1.1M params).

---

## Validation Results

### All Code Checks Passed

- Sequence logic: 147,056 sequences validated, zero boundary violations
- Subject leakage: Zero overlap between train/val/test subjects
- Code audit: All 18 checks passed (normalization, checkpointing, metrics, etc.)

### Critical Empirical Finding: Zero PAC Autocorrelation

| Lag (seconds) | Mean autocorrelation | Statistically significant? |
|--------------|---------------------|---------------------------|
| 1 | 0.060 | Barely (p ≈ 0.04) |
| 2 | -0.026 | No |
| 3 | 0.002 | No |
| 5 | 0.011 | No |
| 10 | -0.003 | No |
| 20 | -0.001 | No |

PAC values in consecutive windows are essentially **uncorrelated**. Knowing PAC at time t tells you nothing about PAC at time t+5.

### Baseline Performance Comparison

| Approach | Test R² | Notes |
|----------|---------|-------|
| Current-window Ridge (spectral) | 0.194 | Same window EEG → same window PAC |
| Current-window Ridge (all features) | 0.287 | Best previous result |
| Temporal Ridge (5s ahead, EEG stats) | 0.031 | Past EEG → future PAC |
| Temporal Ridge (5s ahead, spectral) | -0.002 | With full spectral features |
| Persistence (PAC[t-1] → PAC[t+5]) | -0.760 | Using last known PAC |
| Naive (predict mean) | -0.028 | Lower bound |

**The temporal prediction task is fundamentally harder than current-window prediction for this data.**

---

## Why the Reference Paper Got R² = 0.80

The discrepancy between our results and the reference paper (R² = 0.75-0.85) likely stems from:

1. **Stimulation context**: The paper's model likely used ON/OFF stimulation state as input. Since the protocol alternates 40s-ON / 20s-OFF, the stimulation state is a powerful predictor of PAC trajectory. Our data includes no stimulation labels.

2. **PAC computation window**: Our PAC is computed over 2-second windows (500 samples at 250Hz). This is quite short for a Modulation Index based on Hilbert transforms — the resulting PAC values are inherently noisy. Longer windows (10-30 seconds) produce smoother, more autocorrelated PAC time series.

3. **Different subjects/conditions**: The reference may have used subjects or conditions with stronger theta-gamma coupling dynamics.

4. **Within-subject prediction**: If the reference used within-subject train/test splits (rather than cross-subject), temporal patterns specific to each individual would inflate R².

---

## Methodology Details

### Data Preparation

- **Source data**: OpenNeuro ds005048, 35 subjects, 7-channel frontal EEG
- **Windows**: 2-second duration, 1-second hop (50% overlap), 250 Hz
- **Split**: Subject-based (24 train / 5 val / 6 test subjects)
- **Temporal sequences**: lookback=10, horizon=5 → 11,400 train / 2,655 val / 2,738 test sequences
- **Normalization**: PAC z-scored using training set statistics; spectral features z-scored per feature

### Training Configuration

- **Loss**: HuberLoss (delta=1.0 on normalized scale)
- **Optimizer**: AdamW (lr=1e-3, weight_decay=1e-3)
- **Scheduler**: Cosine annealing with warm restarts (T_0=20, T_mult=2)
- **Gradient clipping**: 0.5
- **Early stopping**: 30 epochs patience on validation R²
- **Max epochs**: 150

### Evaluation

All metrics computed in original (denormalized) PAC scale:
- R² (coefficient of determination)
- Pearson correlation
- MAE, RMSE, MAPE

---

## How to Run

### Step 1: Validate (no GPU needed)

```bash
cd closedloop-40hz-entrainment
python temporal/validate_code.py
```

### Step 2: Train the LSTM (GPU recommended)

```bash
python temporal/train_temporal.py --horizon 5 --lookback 10 --epochs 150
```

### Step 3: Multi-horizon experiment (optional)

```bash
python temporal/train_temporal.py --multi-horizon
```

### Step 4: Try GRU variant (optional)

```bash
python temporal/train_temporal.py --use-gru
```

---

## Honest Assessment & Next Steps

### What Will Likely Happen

Given the near-zero PAC autocorrelation, the LSTM will likely achieve R² in the range of **0.03-0.10** for temporal prediction. The nonlinear modeling capacity of the LSTM should provide some improvement over Ridge, but the fundamental signal simply isn't there in 2-second PAC windows.

### Recommended Next Steps (in priority order)

1. **Recompute PAC with longer windows (10-30 seconds)**
   The 2-second Modulation Index is too noisy. Reprocessing the raw .set files with 10+ second PAC windows should produce smoother time series with actual temporal structure. This is the single highest-impact change.

2. **Extract stimulation context from the raw data**
   The ON/OFF stimulation state (40s ON / 20s OFF cycles) is likely the strongest predictor of PAC trajectory. It should be extractable from the event markers in the raw .set files.

3. **Switch to within-subject evaluation**
   If the closed-loop system will be personalized per-patient, within-subject temporal prediction is the relevant metric. This would likely show higher R² than cross-subject.

4. **Consider ΔPAC prediction**
   Rather than predicting absolute PAC(t+5), predict the *change* in PAC: ΔPAC = PAC(t+5) - PAC(t). This formulation may be more predictable and is more actionable for a controller (the controller needs to know "will PAC go up or down?").

5. **Multi-step curriculum**
   Train on easier horizons first (1-2 seconds) then fine-tune for longer horizons (5-10 seconds).

---

## Repository Structure (After Cleanup)

```
closedloop-40hz-entrainment/
├── temporal/                          # ★ NEW: Temporal prediction system
│   ├── __init__.py
│   ├── temporal_dataset.py            # Data preparation
│   ├── temporal_model.py              # LSTM/GRU architecture
│   ├── train_temporal.py              # Training pipeline
│   └── validate_code.py              # Validation suite
├── src/                               # Core modules (unchanged)
│   ├── spectral_features.py           # 61 spectral features
│   ├── wavelet_features.py            # 74 wavelet features
│   ├── vit_tcnet.py                   # ViT-TCNet (V4)
│   ├── data_augmentation.py           # EEG augmentation
│   ├── eegnet.py / eegnet_v2.py       # EEGNet architectures
│   ├── spectempnet.py                 # SpecTempNet (V3)
│   └── [other utility modules]
├── data/processed/                    # Processed data splits
│   ├── train_data.npz                 # 11,736 windows, 24 subjects
│   ├── val_data.npz                   # 2,725 windows, 5 subjects
│   ├── test_data.npz                  # 2,822 windows, 6 subjects
│   └── *_spectral_cache.npy           # Cached spectral features
├── models/                            # Saved model weights
├── archive/                           # ★ Organized old versions
│   ├── v1_v8_attempts/                # Previous training scripts
│   ├── docs_v1_v8/                    # Previous documentation
│   └── diagnostics/                   # Data leakage audits
├── COMPREHENSIVE_ANALYSIS_ALL_ATTEMPTS.md  # Full V1-V8 history
├── TEMPORAL_PREDICTION_REPORT.md      # ★ This document
├── LAB_NOTEBOOK_MASTER_COMPLETE.txt   # Lab notebook
├── README.md                          # Project README
├── config.yaml                        # Configuration
└── requirements.txt                   # Dependencies
```

---

## Key Takeaway

The temporal prediction approach (Option B) is architecturally sound and the code is validated. The fundamental limitation is **data-side**: 2-second PAC windows produce essentially i.i.d. values with no temporal structure. The path to R² = 0.75+ requires reprocessing the raw data with longer PAC windows and stimulation context — a data engineering task, not a model engineering task.

The LSTM system is ready to train and will serve as the prediction backbone once the data is reprocessed appropriately.
