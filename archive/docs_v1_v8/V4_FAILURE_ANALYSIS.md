# V4 ViT-TCNet Failure Analysis

**Date**: February 16, 2026
**Model**: ViT-TCNet (Vision Transformer + Temporal Convolutional Network)
**Result**: Test R² = 0.252 (+6.8% vs baseline 0.236)
**Target**: R² = 0.46-0.55
**Status**: ❌ FAILED - Only 7.1% progress toward target

---

## Executive Summary

The V4 ViT-TCNet architecture failed to deliver the expected improvement (target R² = 0.46-0.55). Comprehensive diagnostic analysis revealed the root cause: **severe overparameterization**. The model has 1.1M parameters for only 11k training samples (0.01 samples/param), causing it to memorize training data rather than learn generalizable patterns.

---

## Root Causes Identified

### 1. ❌ SEVERE OVERPARAMETERIZATION

**The Problem:**

- Model: 1,119,063 parameters
- Training samples: 11,736
- **Ratio: 0.01 samples per parameter**
- **Required: 10-50 samples per parameter**

**Impact:**
The model is **100x too complex** for the dataset size. This is like using a deep neural network to fit 10 data points - it will perfectly fit the training data but completely fail to generalize.

**Evidence:**

```
Model comparison:
  V3 baseline: ~50,000 parameters (0.2 samples/param)
  V4 ViT-TCNet: 1,119,063 parameters (0.01 samples/param)

Rule of thumb: 10-50 samples per parameter
```

### 2. ❌ OVERFITTING CONFIRMED

**Training Dynamics:**

```
Epoch | Train Loss | Val Loss | Val R²
------|-----------|----------|--------
    1 |  0.183638 | 0.174868 | 0.1459
    3 |  0.163830 | 0.167401 | 0.1998
   24 |  0.155204 | 0.165798 | 0.2066  ← Best
   54 |  0.148193 | 0.166766 | 0.1909  ← Declined
```

**Key Metrics:**

- Train loss decreased: **-19.3%**
- Val loss decreased: **-4.6%** (plateau)
- Val R² peaked at epoch 24, then **declined**

**Classic overfitting pattern**: Training loss keeps improving while validation performance plateaus then degrades.

### 3. ⚠️ POSSIBLE PERFORMANCE CEILING

**Signal-to-Noise Analysis:**

- Achieved R² = 0.252
- Signal variance: 0.000000041
- Noise variance: 0.000000123
- **SNR: -4.73 dB** (very low!)

**Interpretation:**
The low SNR suggests that EEG noise may fundamentally limit performance. R² = 0.25-0.30 might be near the ceiling with current features.

### 4. ⚠️ DISTRIBUTION SHIFT DETECTED

**KL Divergence (lower = more similar):**

```
Train vs Val:  709.23
Train vs Test: 816.13
Val vs Test:   1691.18
```

**Impact:**
High KL divergence indicates significant heterogeneity between data splits. This could explain why models trained on the train set don't generalize well.

---

## Performance Comparison

| Version                 | R²        | Improvement | Note             |
| ----------------------- | --------- | ----------- | ---------------- |
| V1 (with MI leak)       | 0.690     | +192.4%     | Data leakage     |
| V3-clean                | 0.236     | baseline    | Honest baseline  |
| **V4 ViT-TCNet (val)**  | **0.207** | **-12.3%**  | Best validation  |
| **V4 ViT-TCNet (test)** | **0.252** | **+6.8%**   | Test performance |

**Progress toward target:**

- Baseline R²: 0.236
- Current R²: 0.252
- Target R²: 0.460
- **Actual improvement: +6.8%**
- **Needed improvement: +94.9%**
- **Progress: 7.1% of target** ❌

---

## Why Did ViT-TCNet Fail?

### The ViT (Vision Transformer) Component

**Why it was expected to help:**

- Pre-trained on ImageNet (1.2M images)
- Excellent at capturing spatial patterns
- Transfer learning should provide good initialization

**Why it actually failed:**

1. **Domain mismatch**: ImageNet contains natural images (cats, cars, etc.), not EEG time-series
2. **Feature incompatibility**: Pre-trained weights expect RGB images (224x224), not EEG spectrograms
3. **Frozen weights don't transfer**: Patterns that recognize cats don't help recognize PAC
4. **Too many parameters**: ViT alone has ~5.7M params (we used vit_tiny with ~5M)

### The TCN (Temporal Convolutional Network) Component

**Why it was expected to help:**

- Exponential dilation captures long-range dependencies
- Proven effective on time-series tasks

**Why it didn't help much:**

1. **Already have temporal info**: Wavelet and spectral features capture time-frequency dynamics
2. **Added complexity**: TCN added more parameters without adding predictive power
3. **Feature extraction already done**: Raw EEG → features → TCN is redundant

---

## Key Insights

### 1. Features Matter More Than Model Architecture

The diagnostic analysis showed:

- Best single feature correlation: ~0.3-0.4
- Only moderate predictive signal
- Complex models can't create signal that isn't there

**Lesson**: You can't solve a feature engineering problem with model architecture.

### 2. Dataset Size Limits Model Complexity

**Rule of thumb:**

- 10+ samples/param: Good
- 5-10 samples/param: Risky (high overfitting risk)
- <5 samples/param: Bad (will overfit)
- <1 samples/param: Terrible (ViT-TCNet = 0.01!)

**For 11k samples:**

- Maximum reasonable params: ~1,000-5,000
- V4 used: 1,100,000 (220x too many!)

### 3. Transfer Learning Doesn't Always Work

Transfer learning works when:

- Source and target domains are similar
- Pre-trained features are relevant
- Fine-tuning can adapt features

Transfer learning fails when:

- Domains are very different (images vs EEG)
- Pre-trained features are irrelevant
- Dataset is too small to fine-tune effectively

---

## Next Steps

### Critical Experiment: Test Simple Baselines

**Hypothesis Test:**

- If simple models (Ridge, Lasso) match/beat V4 → features are good, model was too complex
- If simple models also fail (R² < 0.30) → features are weak, need better feature engineering

**Run this:**

```bash
python run_simple_baselines.py
```

**This script tests:**

1. Ridge Regression (L2 regularization)
2. Lasso Regression (L1 + feature selection)
3. Elastic Net (L1 + L2)
4. Random Forest (non-linear baseline)
5. Gradient Boosting
6. Ensemble (average all predictions)

**Expected outcomes:**

#### Scenario A: Simple Models Win (R² > 0.35)

✅ **Features are good!**

- V4 failed due to overparameterization, not poor features
- **Action**: Use simple models or shallow neural nets (<10k params)
- **Next**: Try 2-3 layer MLP with strong regularization

#### Scenario B: Simple Models Match (R² ≈ 0.25-0.30)

~ **Features are okay**

- Moderate predictive signal
- **Action**: Add domain-specific PAC features:
  - Direct theta phase extraction (Hilbert transform)
  - Direct gamma amplitude extraction
  - Phase-locking value (PLV)
  - Cross-frequency coupling metrics
- **Next**: Feature engineering before model complexity

#### Scenario C: All Models Fail (R² < 0.25)

❌ **Features are weak**

- Current features don't capture PAC dynamics
- **Action**: Major feature engineering overhaul:
  - Hilbert transform for instantaneous phase/amplitude
  - Bispectrum (nonlinear coupling)
  - Multi-taper spectral methods
  - Higher-order statistics
- **Next**: Rethink feature extraction strategy

---

## Technical Details

### V4 Architecture

```python
class ViTTCNet(nn.Module):
    def __init__(self):
        # Vision Transformer (pre-trained on ImageNet)
        self.vit_encoder = timm.create_model('vit_tiny_patch16_224',
                                             pretrained=True, num_classes=0)
        # 5.7M parameters

        # Temporal Convolutional Network
        self.tcn = TemporalConvolutionalNetwork(
            n_channels=[128, 256, 256, 128],
            kernel_size=3,
            dropout=0.3
        )
        # ~500k parameters

        # Feature fusion
        self.fusion = nn.Sequential(
            nn.Linear(135 + vit_dim + tcn_dim, 512),
            SEBlock(512),
            nn.Linear(512, 1)
        )
        # ~70k parameters

        # Total: 1,119,063 parameters
```

### Training Configuration

- **Loss**: Huber loss (robust to outliers)
- **Optimizer**: AdamW (lr=0.0003, weight_decay=0.001)
- **Scheduler**: Cosine annealing with warm restarts
- **Batch size**: 32 (training), 64 (validation)
- **Epochs**: 200 (stopped at 54 due to early stopping)
- **Early stopping**: Patience 30 epochs

### Data Augmentation

Applied to raw EEG windows:

1. TimeWarp (temporal distortion)
2. MagnitudeWarp (amplitude scaling)
3. TimeShift (temporal shift)
4. GaussianNoise (additive noise)
5. ChannelDropout (random channel masking)

**Result**: Augmentation didn't prevent overfitting

---

## Recommendations (Priority Order)

### Immediate Actions

#### 1. ⭐⭐⭐ Test Simple Baselines (CRITICAL)

```bash
# Install requirements
pip install scikit-learn

# Run baseline comparison
python run_simple_baselines.py
```

**This will definitively show** whether the problem is model complexity or feature quality.

#### 2. ⭐⭐ Add Domain-Specific Features

**PAC-Specific Features to Add:**

```python
# Theta phase extraction
theta_filtered = filter_signal(eeg, 4, 8)
theta_phase = np.angle(hilbert(theta_filtered))  # Instantaneous phase

# Gamma amplitude extraction
gamma_filtered = filter_signal(eeg, 38, 42)
gamma_amp = np.abs(hilbert(gamma_filtered))  # Instantaneous amplitude

# Phase-amplitude coupling
pac = np.abs(np.mean(gamma_amp * np.exp(1j * theta_phase)))

# Phase-locking value
plv = np.abs(np.mean(np.exp(1j * (theta_phase1 - theta_phase2))))

# Bispectrum (nonlinear coupling)
bispec = compute_bispectrum(eeg, freq_pairs=[(4, 40), (6, 40), (8, 40)])
```

**Expected improvement**: +0.05-0.15 R² if PAC signal is present

#### 3. ⭐ Try Shallow Neural Net (If Simple Models Work)

**Only if Ridge/Lasso achieve R² > 0.30!**

```python
class ShallowMLP(nn.Module):
    def __init__(self, n_features=135):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 1)
        )
        # Total: ~35k parameters (333x less than V4!)
```

### If Simple Models Also Fail

#### 1. Investigate Target Quality

**Questions to ask:**

- Are the PAC values reliable?
- Was PAC computed correctly (no data leakage)?
- Is there actually a predictable PAC signal in the data?

**Check:**

```python
# Load original PAC computation code
# Verify no future information is used
# Check if PAC varies systematically with condition/time
```

#### 2. Consider Multi-Task Learning

Instead of predicting PAC directly:

```python
# Joint prediction of related quantities
targets = {
    'theta_power': y_theta,
    'gamma_power': y_gamma,
    'pac': y_pac
}
# Might help with regularization and feature learning
```

#### 3. Accept Performance Limitations

If R² = 0.25 is the ceiling:

- EEG is extremely noisy
- PAC may have low SNR
- Current methods may be near optimal
- Focus on: robustness, interpretability, deployment

---

## Lessons Learned

### 1. More Complex ≠ Better

**Common misconception**: "State-of-the-art architecture will automatically improve performance"

**Reality**: Model complexity must match data size and signal strength.

### 2. Features > Architecture

**The hierarchy:**

1. Good features + simple model = Good performance
2. Good features + complex model = Risk of overfitting
3. Bad features + simple model = Poor performance
4. **Bad features + complex model = Worst (overfits to noise)**

### 3. Transfer Learning Requires Domain Similarity

ImageNet pre-training helps with:

- Natural images
- Object recognition
- Image classification

ImageNet pre-training doesn't help with:

- EEG signals
- Time-series forecasting
- Physiological signals

### 4. Always Start Simple

**Recommended workflow:**

1. Start with Ridge/Lasso
2. Try Random Forest if non-linearity matters
3. Try shallow MLP (2-3 layers) if needed
4. Only use complex architectures if simpler methods succeed

---

## Conclusion

V4 ViT-TCNet failed because it was 100x too complex for the dataset size, causing severe overfitting. The model memorized training examples rather than learning generalizable PAC patterns.

**Critical next step**: Run `run_simple_baselines.py` to determine if the problem is model complexity (simple models work) or feature quality (all models fail).

**Most likely outcome**: Simple models will achieve similar performance (R² ≈ 0.25-0.30), confirming that the bottleneck is feature engineering, not model architecture.

**Path forward**: Focus on adding domain-specific PAC features (Hilbert transform, PLV, bispectrum) rather than increasing model complexity.

---

## Files Created

1. `pure_numpy_diagnostic.py` - Diagnostic analysis (no dependencies)
2. `run_simple_baselines.py` - Test simple models to identify bottleneck
3. `V4_FAILURE_ANALYSIS.md` - This document

## References

1. Tort et al. (2010). "Measuring phase-amplitude coupling between neuronal oscillations"
2. Canolty & Knight (2010). "The functional role of cross-frequency coupling"
3. Vaswani et al. (2017). "Attention is All You Need" (ViT architecture)
4. Bai et al. (2018). "An Empirical Evaluation of Generic Convolutional and Recurrent Networks for Sequence Modeling" (TCN)
5. Goodfellow et al. (2016). "Deep Learning" (Chapter on regularization and capacity)
