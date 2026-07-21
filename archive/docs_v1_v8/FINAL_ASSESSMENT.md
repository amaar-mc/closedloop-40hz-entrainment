# Final Assessment: PAC Prediction Project

**Date**: February 16, 2026
**Author**: Claude (Sonnet 4.5)
**Status**: Data leakage resolved, honest baseline established

---

## Executive Summary

After extensive experimentation and debugging, we have established an **honest baseline performance** and identified the fundamental challenges of this prediction task.

**Current Honest Performance:**

- **Ridge Regression**: R² = 0.287 (+21.6% vs V3-clean baseline 0.236)
- **No data leakage**: Confirmed through comprehensive diagnostics
- **Simple beats complex**: Ridge outperforms 1.1M-parameter ViT-TCNet

**Target Performance:**

- **Goal**: R² = 0.46-0.55
- **Gap**: +0.17-0.26 R² points needed
- **Challenge**: Must achieve without circular reasoning (can't use PAC to predict PAC)

---

## Journey Summary

### Phase 1: Discovery of Data Leakage (V1)

- **Initial result**: R² = 0.69 (seemed great!)
- **Problem**: MI (Modulation Index) features leaked target
- **Action**: Removed MI features → honest R² = 0.236

### Phase 2: ViT-TCNet Architecture (V4)

- **Approach**: State-of-the-art Vision Transformer + TCN
- **Result**: R² = 0.252 (+6.8%)
- **Problem**: Severe overparameterization (1.1M params, 11k samples)
- **Evidence**: Train loss improved 19.3%, val loss only 4.6% (overfitting)

### Phase 3: Simple Baselines (V5)

- **Approach**: Ridge, Lasso, ElasticNet, Random Forest, Gradient Boosting
- **Result**: Ridge wins with R² = 0.287 (+13.9% vs V4)
- **Insight**: Linear models beat complex models (features are good, models were overparameterized)

### Phase 4: PAC-Specific Features (V5 Enhanced)

- **Approach**: Add 116 PAC features (Hilbert transform, PLV, direct MI)
- **Result**: R² = 0.9999 (perfect!)
- **Problem**: Severe data leakage (PAC features = 96.6% of model weight)
- **Root cause**: Predicting PAC using PAC = circular reasoning

---

## Confirmed Data Leakage: The Evidence

### Leakage Source: PAC_MI Features

The PAC_MI features (135-141) directly compute Modulation Index from EEG:

1. Extract theta phase (Hilbert transform)
2. Extract gamma amplitude (Hilbert transform)
3. Bin gamma amplitude by theta phase
4. Compute MI (KL divergence from uniform distribution)

**This is identical (or nearly identical) to how the target PAC was computed!**

### Evidence from Debug Analysis

```
PAC features account for 96.6% of total coefficient magnitude
Top 7 features: ALL PAC_MI (one per channel)
PAC_MI coefficients: 0.000118-0.000126 (100x larger than others)

Model equation:
  Predicted_PAC ≈ 0.000118×MI_ch0 + 0.000126×MI_ch1 + ... + 0.000115×MI_ch6
```

This is just averaging the PAC computed per channel!

### Why This Is Circular

**Target**: PAC computed from EEG window
**Features**: PAC_MI computed from same EEG window
**Prediction**: Use PAC to predict PAC

Analogy: Predicting someone's height by measuring their height.

---

## Current Honest Baseline

### Performance (No Leakage)

**Ridge Regression with 135 features** (61 spectral + 74 wavelet):

- **Train R²**: Variable (regularization prevents overfitting)
- **Val R²**: 0.247
- **Test R²**: 0.287
- **Test MAE**: 0.000260
- **Test Correlation**: +0.54

### Top Predictive Features (Honest)

From Ridge model with original 135 features:

1. **WPD_13** (Wavelet Packet Decomposition, gamma-like energy)
2. **Beta relative power** (ch3, ch0)
3. **Theta relative power** (ch1)
4. **Gamma relative power** (ch1)
5. **Delta relative power** (ch0, ch3)

**Insight**: Features capturing theta and gamma activity (the bands involved in PAC) are most predictive, which makes neuroscientific sense!

### Why Ridge Works Best

1. **Lasso selected only 40/135 features** → 95 features are redundant/noisy
2. **Linear relationships dominate** → Ridge beats Random Forest
3. **Strong L2 regularization prevents overfitting** → Generalizes well
4. **Simple and interpretable** → Can understand what drives predictions

---

## The Fundamental Challenge

### The Circular Reasoning Trap

**We cannot use PAC-measuring features to predict PAC.**

Features we **cannot use** (circular):

- ❌ Direct MI computation
- ❌ Phase-amplitude correlation
- ❌ Coupling profiles (amplitude binned by phase)
- ❌ Any theta-gamma coupling metric
- ❌ Phase-locking between theta/gamma

Features we **can use** (non-circular):

- ✅ Spectral power in individual bands
- ✅ Wavelet decomposition (time-frequency)
- ✅ Cross-channel correlations
- ✅ Temporal dynamics
- ✅ Higher-order statistics

### The Performance Ceiling Question

**Is R² = 0.287 near the ceiling for non-circular features?**

Evidence suggesting yes:

1. **Low SNR**: Signal-to-noise ratio = -4.73 dB
2. **EEG noise**: Inherently noisy signal
3. **Simple models plateau**: Ridge, Lasso, ElasticNet all ~0.28-0.29
4. **Distribution shift**: KL divergence suggests data heterogeneity

Evidence suggesting no:

1. **Nonlinear models underexplored**: Only tried Random Forest (which failed)
2. **Feature interactions**: Haven't tried polynomial features
3. **Temporal context**: Not using time-series context
4. **Ensemble methods**: Could squeeze out more performance

---

## Realistic Improvement Strategies

### Strategy 1: Squeeze Maximum from Existing Features ⭐⭐⭐

**Approach**: Optimize the 135 features we have

**Methods**:

1. **Feature selection**: Remove noisy features (Lasso selected 40/135)
2. **Polynomial features**: Add interactions between important features
3. **Ensemble**: Combine Ridge + Lasso + Gradient Boosting
4. **Hyperparameter tuning**: Grid search with cross-validation

**Expected improvement**: +0.02-0.05 R² → **0.31-0.34**

**Pros**: No circular reasoning, uses proven features
**Cons**: May be approaching ceiling

### Strategy 2: Temporal Context Features ⭐⭐

**Approach**: Use information from surrounding windows

**Methods**:

1. **Rolling statistics**: Mean/std of features over previous N windows
2. **Temporal trends**: First/second derivatives of features
3. **Autocorrelation**: How features correlate with themselves over time
4. **Change detection**: Sudden shifts in spectral content

**Expected improvement**: +0.03-0.08 R² → **0.32-0.37**

**Pros**: Non-circular, captures dynamics
**Cons**: Requires sequential data access, may not generalize

### Strategy 3: Nonlinear Models on Existing Features ⭐⭐

**Approach**: Try models that can capture nonlinear relationships

**Methods**:

1. **Gradient Boosting** (XGBoost, LightGBM) with careful tuning
2. **Shallow MLP** (2-3 layers, <10k params, strong regularization)
3. **Support Vector Regression** with RBF kernel
4. **Gaussian Process Regression** (if computationally feasible)

**Expected improvement**: +0.02-0.06 R² → **0.31-0.35**

**Pros**: Can capture complex patterns
**Cons**: Risk of overfitting, harder to interpret

### Strategy 4: Feature Engineering Round 2 ⭐

**Approach**: Add more non-circular features

**Methods**:

1. **Cross-frequency coupling** (other band pairs, not theta-gamma)
2. **Spectral coherence** (phase consistency between channels)
3. **Higher-order spectra** (bispectrum, trispectrum)
4. **Fractal dimension** (Hurst exponent, detrended fluctuation)
5. **Microstate analysis** (topographic maps)

**Expected improvement**: +0.03-0.10 R² → **0.32-0.39**

**Pros**: New information, neuroscientifically grounded
**Cons**: Risk of adding noise, computationally expensive

### Strategy 5: Accept the Ceiling ⭐⭐⭐⭐

**Approach**: R² = 0.28-0.30 may be the honest limit

**Rationale**:

- EEG is extremely noisy (SNR = -4.73 dB)
- PAC has low intrinsic predictability from power features
- Without measuring PAC directly, prediction is fundamentally limited
- R² = 0.28 represents 28% variance explained (not bad for EEG!)

**Action**: Focus on deployment, robustness, interpretability

**Pros**: Realistic expectations, focus on practical use
**Cons**: Doesn't reach target R² = 0.46

---

## Honest Assessment: Is R² = 0.46 Achievable?

### The Math

**Current**: R² = 0.287
**Target**: R² = 0.46
**Gap**: +0.173 R² points
**Needed improvement**: +60.3%

### Likelihood Analysis

**Pessimistic scenario** (20% chance):

- R² = 0.28 is near ceiling
- EEG noise fundamentally limits prediction
- Best achievable (honest): **R² = 0.30-0.32**

**Realistic scenario** (60% chance):

- With clever feature engineering + ensembles
- Best achievable (honest): **R² = 0.35-0.40**
- Falls short of target 0.46

**Optimistic scenario** (20% chance):

- Temporal features + nonlinear models + ensembles
- Best achievable (honest): **R² = 0.42-0.48**
- Reaches or nearly reaches target!

### My Honest Opinion

**R² = 0.35-0.40 is realistic with significant effort.**
**R² = 0.46+ is possible but requires breakthrough insight.**

The target R² = 0.46 was likely based on studies that:

1. Used more subjects (>35)
2. Had longer recording windows
3. Used online PAC computation (not windowed prediction)
4. May have had inadvertent data leakage

For windowed EEG prediction with 35 subjects, **R² = 0.35-0.40 would be excellent performance**.

---

## Recommended Path Forward

### Option A: Maximize Honest Performance (Recommended ⭐⭐⭐⭐)

**Goal**: Reach R² = 0.35-0.40 through rigorous optimization

**Steps**:

1. **Feature selection** with Lasso (keep only 40 best features)
2. **Add temporal context** (rolling features, trends)
3. **Train ensemble** (Ridge + Lasso + Gradient Boosting + Small MLP)
4. **Extensive cross-validation** to avoid overfitting
5. **Test on held-out subjects** (not just time splits)

**Expected outcome**: R² = 0.35-0.40
**Timeline**: 1-2 days of work
**Risk**: Medium (may plateau at 0.32-0.35)

### Option B: Accept Current Performance & Deploy

**Goal**: Use R² = 0.287 model for closed-loop application

**Rationale**:

- R² = 0.28 explains 28% of variance (respectable for EEG)
- Correlation r = 0.54 (moderate predictive power)
- Focus on: robustness, real-time performance, interpretability

**Action**: Deploy Ridge model, monitor performance, iterate based on real-world data

**Expected outcome**: Working system with honest performance metrics
**Timeline**: Immediate
**Risk**: Low (already proven to work)

### Option C: Rethink the Problem

**Goal**: Question whether windowed PAC prediction is the right approach

**Alternative approaches**:

1. **Online PAC estimation** (compute PAC in real-time, don't predict)
2. **Classify high/low PAC** (binary/ordinal prediction instead of regression)
3. **Predict optimal stimulation timing** (directly predict when to stimulate)
4. **Multi-task learning** (predict multiple EEG properties jointly)

**Expected outcome**: Different framing may be more tractable
**Timeline**: 3-5 days to explore
**Risk**: High (major pivot)

---

## Lessons Learned

### 1. Start Simple, Then Add Complexity

**Wrong approach**: Jump to state-of-the-art architecture (ViT-TCNet)
**Right approach**: Start with Ridge, establish baseline, then improve

Ridge (0.287) beat ViT-TCNet (0.252) because:

- Appropriate model complexity for data size
- Strong regularization prevents overfitting
- Interpretable and debuggable

### 2. Features > Model Architecture

**Wrong focus**: "Better model architecture will solve this"
**Right focus**: "Better features that don't leak will solve this"

The bottleneck was never model architecture—it was:

1. Feature quality (non-leaking features are only moderately predictive)
2. Model appropriateness (simple models work best for this data size)

### 3. Data Leakage is Insidious

**We encountered data leakage THREE times**:

1. **V1**: MI features (discovered, removed)
2. **V4**: Suspected but not proven (turned out to be overparameterization)
3. **V5 Enhanced**: PAC features (discovered, removed)

**Lesson**: Always be paranoid about "too good to be true" performance.

### 4. EEG is Really, Really Noisy

**SNR = -4.73 dB** means noise is 3x larger than signal!

This fundamentally limits prediction. No amount of model complexity can create signal that isn't there.

### 5. Dataset Size Matters

**11,736 training samples is small for deep learning.**

Rule of thumb:

- 10+ samples per parameter (minimum)
- 50+ samples per parameter (ideal)

For 11k samples:

- Max reasonable params: 1,000-5,000
- Ridge: ~200 effective params ✓
- ViT-TCNet: 1,119,063 params ❌ (220x too many!)

---

## Technical Specifications

### Current Best Model (Honest)

**Model**: Ridge Regression
**Features**: 135 (61 spectral + 74 wavelet)
**Regularization**: α = 1526.418 (L2)
**Training samples**: 11,736
**Validation samples**: 2,725
**Test samples**: 2,822

**Performance**:

- Test R²: 0.287
- Test MAE: 0.000260
- Test Correlation: 0.536
- No overfitting: Val R² = 0.247 (close to test)

**Model size**: ~5 KB (135 features × 8 bytes/coef)
**Inference time**: <1ms per window
**Memory footprint**: Minimal

### Feature Specifications

**Spectral Features (61)**:

- Per-channel absolute power (5 bands × 7 channels = 35)
- Per-channel relative power (5 bands × 7 channels = 35)
- Average power across channels (5 bands)
- Spectral entropy (1)

**Wavelet Features (74)**:

- CWT features (35): Continuous Wavelet Transform energy at multiple scales
- WPD features (28): Wavelet Packet Decomposition energies (7 channels × 4 features)
- PSI feature (1): Phase synchronization index (global)
- CWT statistics (10): Mean and std across channels (5 each)

**Frequency Bands**:

- Delta: 0.5-4 Hz
- Theta: 4-8 Hz (PAC phase)
- Alpha: 8-13 Hz
- Beta: 13-30 Hz
- Gamma: 38-42 Hz (PAC amplitude)

---

## Conclusion

We have established an **honest, non-leaking baseline** of **R² = 0.287** using Ridge Regression with 135 spectral and wavelet features. This represents a **21.6% improvement** over the original V3-clean baseline (R² = 0.236).

**The target R² = 0.46-0.55 remains challenging** because:

1. We cannot use PAC features to predict PAC (circular reasoning)
2. EEG has very low SNR (-4.73 dB)
3. Non-circular features are only moderately predictive

**Realistic expectations**:

- **Likely achievable**: R² = 0.35-0.40 (with temporal features + ensembles)
- **Unlikely but possible**: R² = 0.42-0.48 (breakthrough insight needed)
- **Current honest performance**: R² = 0.287 (respectable for EEG)

**Recommended action**: Pursue **Option A** (maximize honest performance through feature selection, temporal features, and ensembles) with realistic expectations of R² = 0.35-0.40.

If that proves insufficient, **Option B** (deploy current model) is a viable path forward, as R² = 0.287 represents real predictive power that could be useful for closed-loop neuromodulation.

---

## Files Summary

**Analysis Scripts**:

- `pure_numpy_diagnostic.py` - V4 failure analysis
- `run_simple_baselines.py` - Simple model comparison
- `debug_leakage.py` - Data leakage investigation

**Models Saved** (models/):

- `ridge_v5.pkl` - Best honest model (R² = 0.287)
- `lasso_v5.pkl` - Lasso with feature selection (40 features)
- `random_forest_v5.pkl` - Nonlinear baseline
- `ridge_v5_enhanced.pkl` - DO NOT USE (data leakage!)

**Feature Extractors** (src/):

- `spectral_features.py` - Spectral features (61)
- `wavelet_features.py` - Wavelet features (74)
- `pac_features.py` - PAC features (DO NOT USE - circular!)

**Documentation**:

- `V4_FAILURE_ANALYSIS.md` - ViT-TCNet failure analysis
- `FINAL_ASSESSMENT.md` - This document

---

**Status**: ✅ Honest baseline established
**Next**: User decides on path forward (Options A, B, or C)
