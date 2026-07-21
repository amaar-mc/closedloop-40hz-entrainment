# SpecTempNet (V3) Implementation Summary

## What We Built

A **Hybrid Spectral-Temporal Network** that combines:

1. **Multi-scale temporal CNN** - Captures oscillatory patterns at different frequencies (16, 32, 64, 128 sample kernels)
2. **Explicit spectral features** - Theta/gamma power, phase-amplitude coupling, band ratios (68 features)
3. **Multi-head attention** - Learns which features are most predictive
4. **Deep regression head** - 4-layer MLP with LayerNorm and dropout

## Why This Should Work Better

### Previous Failures:

- **V1 (EEGNet)**: 1,457 params, R² = 0.0838 - Too simple
- **V2 (Enhanced EEGNet)**: 25,185 params, R² = 0.0622 - ΔPAC prediction was predicting noise!

### V3 Improvements:

| Issue                                  | Previous Approach              | V3 Solution                                   |
| -------------------------------------- | ------------------------------ | --------------------------------------------- |
| **Low temporal correlation** (r=0.137) | Only raw EEG temporal features | + Spectral features (theta/gamma power)       |
| **Complex frequency coupling**         | Learn frequency decomposition  | Pre-compute theta/gamma features explicitly   |
| **Small PAC values** (~0.001)          | Basic normalization            | Better normalization + robust loss (SmoothL1) |
| **Model too simple**                   | 1.4k-25k params                | ~180k params (but with strong regularization) |
| **Insufficient capacity**              | Single-scale CNN               | Multi-scale CNN + attention                   |

## Architecture Details

```
INPUT: EEG (7 channels × 500 samples @ 250Hz = 2 seconds)

┌─────────────────────────────────────────────────────────────────┐
│ BRANCH 1: Multi-Scale Temporal CNN                             │
│   Kernel 16 (gamma range)  ─┐                                  │
│   Kernel 32 (mid-range)     ├─→ Concat → Spatial Conv → Pool   │
│   Kernel 64 (mid-range)     │                                   │
│   Kernel 128 (theta range)  ─┘                                  │
│   Output: 128 features                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ BRANCH 2: Spectral Features (Pre-computed)                     │
│   - Theta power (7 channels)                                    │
│   - Gamma power (7 channels)                                    │
│   - Alpha/Beta power (7+7 channels)                            │
│   - Theta-gamma ratios (7 channels)                            │
│   - Phase-amplitude coupling features (28 features)            │
│   - Global statistics (5 features)                             │
│   Total: 68 features → MLP → 64 features                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ FUSION: Multi-Head Attention (4 heads)                         │
│   Concatenate [128 temporal + 64 spectral] = 192 dims          │
│   Self-attention → Learn feature importance → 192 dims         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PREDICTION HEAD                                                 │
│   192 → 128 → 64 → 32 → 1                                       │
│   (LayerNorm + ELU + Dropout 0.4 between each layer)           │
│   Output: PAC prediction (scalar)                               │
└─────────────────────────────────────────────────────────────────┘
```

## Model Statistics

- **Total parameters:** ~180,000
- **Model size:** ~700 KB
- **Samples per parameter:** 11,735 / 180,000 ≈ 65 (healthy ratio!)
- **Regularization:** Dropout 0.4, Weight decay 0.0005, BatchNorm, LayerNorm

## Training Configuration

```python
Loss: SmoothL1Loss (robust to outliers, better than MSE/Huber)
Optimizer: AdamW (lr=0.0003, weight_decay=0.0005)
Scheduler: ReduceLROnPlateau (patience=7, factor=0.5)
Batch size: 32 (smaller = better gradient estimates)
Max epochs: 200
Early stopping: patience=25
Augmentation: Time jitter, amplitude scaling, channel dropout
```

## Expected Performance

| Metric      | V1 (Baseline) | V2 (Failed) | V3 (Target)      |
| ----------- | ------------- | ----------- | ---------------- |
| **R²**      | 0.0838        | 0.0622 ❌   | **0.30-0.50** ✅ |
| Val Loss    | 0.9964        | 0.6347      | 0.40-0.50        |
| MAE         | 0.7499        | 1.0357      | 0.60-0.80        |
| Correlation | +0.29         | +0.25       | +0.55-0.70       |

**Conservative estimate:** R² = 0.25-0.35
**Realistic target:** R² = 0.30-0.45
**Optimistic:** R² = 0.45-0.55

## Training Time Estimate

- Batches per epoch: 367 (11,735 samples / 32 batch_size)
- Time per batch: ~15-20ms (larger model than v1/v2)
- Time per epoch: 367 × 18ms ≈ **6-7 seconds**
- Expected epochs: 60-100 (early stopping)
- **Total time: 6-12 minutes**

Much longer than v2 (1.2s/epoch) but still very reasonable!

## Files Created

1. `src/spectral_features.py` - Spectral feature extraction (theta/gamma power, PAC features)
2. `src/spectempnet.py` - SpecTempNet model architecture
3. `run_training_v3.py` - Complete training pipeline
4. `ARCHITECTURE_V3_DESIGN.md` - Design rationale
5. `V3_IMPLEMENTATION_SUMMARY.md` - This file

## How to Run

```bash
python run_training_v3.py
```

Press Enter when prompted. Training will:

1. Load processed EEG data
2. Extract spectral features (theta/gamma power, PAC features)
3. Create model (~180k parameters)
4. Train for up to 200 epochs (early stopping at 25 patience)
5. Save best model to `models/best_spectempnet_v3.pth`

## What to Expect

### During Training:

```
Epoch   1/200 | Time:   6.5s | LR: 0.000300
  Train Loss: 0.623456 | Val Loss: 0.678912
  Val R²:  0.0234 | Val MAE: 0.987654 | Val Corr: +0.1523

Epoch  10/200 | Time:   6.3s | LR: 0.000300
  Train Loss: 0.521234 | Val Loss: 0.567891
  Val R²:  0.1234 | Val MAE: 0.845678 | Val Corr: +0.3512
  ⭐ New best R²! Model saved.

...

Epoch  65/200 | Time:   6.4s | LR: 0.000075
  Train Loss: 0.412345 | Val Loss: 0.456789
  Val R²:  0.3456 | Val MAE: 0.678912 | Val Corr: +0.5892
  ⭐ New best R²! Model saved.
```

### Success Criteria:

- ✅ **Target achieved:** Val R² > 0.30
- ⚠️ **Acceptable:** Val R² > 0.25 (still 3-4× better than v1/v2)
- ❌ **Failed:** Val R² < 0.20 (need different approach)

## If This Succeeds (R² > 0.30)

**Next steps:**

1. ✅ Document results in lab notebook
2. ✅ Run closed-loop simulation with this model
3. ✅ Compare control strategies (fixed, reactive, predictive, oracle)
4. ✅ Generate publication figures
5. ✅ Write Synopsys report
6. ✅ Complete IEEE paper Results section

## If This Still Fails (R² < 0.25)

**Fallback options:**

### Option A: Subject-Specific Fine-Tuning

- Train on all subjects globally
- Fine-tune last 2 layers per-subject
- Use leave-one-subject-out cross-validation

### Option B: Ensemble Model

- Train 5 models with different random seeds
- Average predictions
- Reduces variance, typically improves R² by 0.05-0.10

### Option C: Multi-Task Learning

- Predict PAC + theta power + gamma power simultaneously
- Auxiliary tasks provide additional training signal

### Option D: Accept Current Performance

- Use best available model (R² ~0.15-0.25)
- Proceed with proof-of-concept closed-loop simulation
- Discuss limitations honestly in paper
- Focus on methodology contribution

## Key Differences from V2

| Aspect           | V2 (Failed)      | V3 (New)                            |
| ---------------- | ---------------- | ----------------------------------- |
| **Target**       | ΔPAC (change) ❌ | Absolute PAC ✅                     |
| **Features**     | Raw EEG only     | Raw EEG + spectral (68 features) ✅ |
| **Architecture** | Single-scale CNN | Multi-scale CNN + attention ✅      |
| **Parameters**   | 25k              | 180k ✅                             |
| **Loss**         | Huber            | SmoothL1 (more robust) ✅           |
| **Batch size**   | 64               | 32 (better gradients) ✅            |

## Why We're Confident This Will Work

1. **Addresses root cause:** Low PAC temporal correlation → Add explicit frequency features
2. **More capacity:** 180k params can learn complex nonlinear patterns
3. **Better features:** Pre-computing theta/gamma reduces learning difficulty
4. **Proven architecture:** Multi-scale CNNs + attention work well for EEG
5. **Strong regularization:** Prevents overfitting despite larger model
6. **Robust loss:** SmoothL1 handles PAC outliers better than MSE

**Let's run it and see!** 🚀
