# Architecture V3: Hybrid Spectral-Temporal Network for PAC Prediction

## Why Previous Approaches Failed

**EEGNet V1/V2 Issues:**
- Too simple (1.4k-25k params) for complex PAC dynamics
- Only uses raw EEG → misses explicit frequency relationships
- PAC has low temporal autocorrelation (0.137) → need richer features
- Predicting tiny values (~0.001) → need better normalization

## Core Problems to Solve

1. **PAC is frequency coupling** - Need explicit theta (4-8Hz) and gamma (38-42Hz) representation
2. **Low temporal correlation** - Need spatial + spectral features, not just temporal
3. **Small signal** - Need robust feature extraction before regression
4. **Individual variability** - Need subject-specific adaptation

## Proposed Architecture: SpecTempNet (Spectral-Temporal Network)

### Architecture Overview

```
INPUT: EEG (7 channels × 500 samples) → 2 seconds @ 250Hz

BRANCH 1: Raw EEG Path (Temporal Features)
  ↓ Multi-scale temporal CNN (kernel sizes: 16, 32, 64, 128)
  ↓ Extract oscillatory patterns at different scales
  ↓ → Feature vector (128 dims)

BRANCH 2: Spectral Path (Frequency Features)
  ↓ Compute power spectral density (Welch's method)
  ↓ Extract theta power (4-8 Hz) per channel
  ↓ Extract gamma power (38-42 Hz) per channel
  ↓ Compute theta-gamma ratios
  ↓ Extract band-specific features
  ↓ → Feature vector (64 dims)

BRANCH 3: Phase-Amplitude Path (PAC-specific)
  ↓ Extract theta phase (Hilbert transform)
  ↓ Extract gamma amplitude envelope
  ↓ Compute instantaneous coupling features
  ↓ → Feature vector (32 dims)

FUSION LAYER:
  ↓ Concatenate all features → (128 + 64 + 32 = 224 dims)
  ↓ Multi-head self-attention (focus on relevant features)
  ↓ → Attended features (224 dims)

PREDICTION HEAD:
  ↓ Dense layers: 224 → 128 → 64 → 32 → 1
  ↓ Dropout (0.4) + LayerNorm
  ↓ → PAC prediction (scalar)
```

### Key Improvements

1. **Explicit Spectral Features** ✅
   - Directly compute theta/gamma power
   - Model has access to the frequency bands that define PAC
   - Reduces reliance on learning frequency decomposition

2. **Multi-Scale Temporal Convolutions** ✅
   - Different kernel sizes capture different oscillatory timescales
   - More expressive than single-scale EEGNet

3. **Phase-Amplitude Features** ✅
   - Pre-compute coupling-relevant features
   - Helps model focus on PAC-specific patterns

4. **Attention Mechanism** ✅
   - Learn which features matter most for each prediction
   - Handles feature importance dynamically

5. **Deeper Network** ✅
   - ~150k-200k parameters (vs 1.4k-25k)
   - More capacity for complex patterns
   - Still small enough to train on 35 subjects with regularization

### Model Size & Regularization

**Parameters:** ~180k total
- Multi-scale CNN: ~60k params
- Spectral/Phase branches: ~40k params
- Attention: ~30k params
- Prediction head: ~50k params

**Regularization Strategy:**
- Dropout: 0.4 (aggressive)
- Weight decay: 0.0005
- Batch normalization after each conv
- Layer normalization in attention
- Early stopping (patience=25)
- Data augmentation (as before)

**With 11,735 training samples:**
- Samples per parameter: ~65 (healthy ratio)
- Should avoid overfitting with proper regularization

## Training Configuration

```python
Model: SpecTempNet (~180k params)
Loss: Smooth L1 Loss (less sensitive to outliers than MSE)
Optimizer: AdamW (lr=0.0003, weight_decay=0.0005)
Schedule: ReduceLROnPlateau (patience=7, factor=0.5)
Batch size: 32 (smaller for better gradient estimates)
Epochs: 200 (patience=25 for early stopping)
Augmentation: Time jitter, amplitude scaling, channel dropout, Gaussian noise
```

## Expected Performance

**Conservative Estimate:** R² = 0.20-0.35
**Optimistic Estimate:** R² = 0.35-0.50
**Realistic Target:** R² > 0.30

**Why this should work better:**
1. Explicit frequency features reduce learning difficulty
2. Multi-scale temporal features capture oscillations better
3. More parameters = more capacity for complex patterns
4. Attention helps model focus on predictive features
5. Better regularization prevents overfitting

## Training Time Estimate

- Batch size: 32
- Batches per epoch: 11,735 / 32 = ~367
- Time per batch: ~15-25ms (model is larger)
- Time per epoch: 367 × 20ms = ~7-8 seconds
- Expected epochs: 60-100 (with early stopping)
- **Total training time: 7-15 minutes**

Still quite fast! Larger model but still reasonable on RTX 3080.

## Implementation Priority

1. ✅ Create SpecTempNet architecture (`spectempnet.py`)
2. ✅ Create spectral feature extractor (`spectral_features.py`)
3. ✅ Create new data loader with spectral features (`data_loader_v3.py`)
4. ✅ Create training script (`training_v3.py`)
5. ✅ Run training and evaluate

## Fallback Options if This Fails

If R² < 0.25 after this:

**Option A: Subject-Specific Fine-Tuning**
- Train global model on all subjects
- Fine-tune last 2 layers per-subject on their data
- Test with leave-one-subject-out cross-validation

**Option B: Multi-Task Learning**
- Predict PAC + theta power + gamma power simultaneously
- Auxiliary tasks provide additional signal

**Option C: Ensemble Model**
- Train 5 models with different random seeds
- Average predictions
- Reduces variance

**Option D: Accept Lower R² & Focus on Closed-Loop**
- Use current best model (R² ~0.15-0.25)
- Demonstrate closed-loop control concept
- Discuss limitations honestly in paper
