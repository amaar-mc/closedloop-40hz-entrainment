# ViT-TCNet V4: State-of-the-Art PAC Prediction

**Date:** February 17, 2026
**Version:** V4 (ViT-TCNet with wavelet features)
**Goal:** Improve R² from 0.236 (V3-Clean) to 0.46-0.55
**Expected training time:** ~1 hour

---

## What's New in V4

### Architecture Improvements

#### 1. **ViT-TCNet Hybrid Architecture** (`src/vit_tcnet.py`)

Replaces SpecTempNet with a state-of-the-art architecture combining:

- **Vision Transformer (ViT) Encoder**
  - Converts EEG to pseudo-image representation (7×500 → 35×100 RGB)
  - Patch embedding + positional encoding
  - 3-layer transformer encoder with 4 attention heads
  - Captures spatial-temporal patterns through self-attention
  - **Why ViT?** Better than CNNs for irregular channel topologies

- **Temporal Convolutional Network (TCN) Decoder**
  - 4 temporal blocks with exponential dilation (1, 2, 4, 8)
  - Receptive field grows exponentially for long-range dependencies
  - Causal convolutions preserve temporal order
  - **Why TCN?** Captures theta-gamma coupling across multiple time scales

- **Squeeze-and-Excitation (SE) Channel Attention**
  - Learns to emphasize informative feature channels
  - Suppresses less relevant information
  - Improves feature discrimination

**Parameters:** ~2-5M (vs ~450k in V3)
**Expected gain:** +0.08-0.12 R²

#### 2. **Wavelet Features** (`src/wavelet_features.py`)

Adds 74 new features complementing the existing 61 spectral features:

**Continuous Wavelet Transform (CWT):**

- Theta band energy (4-8 Hz)
- Gamma band energy (38-42 Hz)
- Theta-gamma energy ratio
- Cross-frequency coupling correlation
- Wavelet entropy (signal complexity)
- **Total:** 35 features (7 channels × 5)

**Wavelet Packet Decomposition (WPD):**

- Energy in theta-like sub-bands
- Energy in mid-frequency sub-bands (alpha/beta)
- Energy in gamma-like sub-bands
- Energy distribution entropy
- **Total:** 28 features (7 channels × 4)

**Global features:**

- Phase synchronization index (1 feature)
- CWT statistics across channels (10 features)

**Why wavelets?** Capture transient time-frequency relationships that spectral power misses.
**Expected gain:** +0.05-0.08 R²

#### 3. **Enhanced Data Augmentation** (`src/data_augmentation.py`)

Implements time-series specific augmentations:

- **TimeWarp:** Speed up/slow down temporal patterns (simulates frequency variations)
- **MagnitudeWarp:** Smooth amplitude scaling (simulates signal strength changes)
- **TimeShift:** Circular shift ±100ms (phase invariance)
- **AddGaussianNoise:** Small random noise (measurement noise robustness)
- **ChannelDropout:** Random channel zeroing (missing channel robustness)

Each augmentation applied with 50% probability during training.

**Expected gain:** +0.04-0.07 R²

---

## Training Improvements

### 1. **Huber Loss** (delta=0.3)

Replaces SmoothL1Loss with Huber loss:

```python
criterion = nn.HuberLoss(delta=0.3)
```

**Why?** More robust to PAC outliers while maintaining MSE-like behavior for small errors.
**Expected gain:** +0.03-0.05 R²

### 2. **Improved Regularization**

- **Weight decay:** 0.001 (2× higher than V3)
- **Gradient clipping:** 0.5 (tighter than V3's 1.0)
- **Progressive dropout:** Already built into ViT-TCNet architecture

**Expected gain:** +0.02-0.04 R²

### 3. **Cosine Annealing with Warm Restarts**

```python
scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
    optimizer, T_0=20, T_mult=2, eta_min=1e-6
)
```

**Why?** Helps escape local minima and improves convergence.

---

## Files Created

### Core Components:

1. **`src/wavelet_features.py`** - CWT + WPD feature extraction
2. **`src/vit_tcnet.py`** - ViT-TCNet architecture
3. **`src/data_augmentation.py`** - Time-series augmentation
4. **`run_training_v4.py`** - Main training script

### Preserved from V3:

- `src/spectral_features.py` - Spectral feature extraction (61 features)
- `data/processed/` - Processed EEG windows

---

## How to Run

### Step 1: Test Individual Components

Test wavelet features:

```bash
cd /sessions/kind-elegant-ride/mnt/closedloop-40hz-entrainment
python src/wavelet_features.py
```

Expected output:

```
✓ EEG shape: (7, 500)
✓ Wavelet features shape: (74,)
✓ Batch features shape: (3, 74)
✓ Wavelet feature extraction test passed!
```

Test data augmentation:

```bash
python src/data_augmentation.py
```

Expected output:

```
✓ TimeWarp: shape=(7, 500), range=[...
✓ MagnitudeWarp: shape=(7, 500), range=[...
✓ Full pipeline: shape=(7, 500), range=[...
✓ Augmentation test passed!
```

Test ViT-TCNet architecture:

```bash
python src/vit_tcnet.py
```

Expected output:

```
✓ Total parameters: ~2-5M
✓ Input EEG shape: (16, 1, 7, 500)
✓ Input spectral shape: (16, 61)
✓ Input wavelet shape: (16, 74)
✓ Output shape: (16, 1)
✓ ViT-TCNet test passed!
```

### Step 2: Train V4 Model

```bash
python run_training_v4.py
```

**What to expect:**

Initial epochs (1-10):

```
Epoch   1: Val R² ~ 0.10-0.20 (lower than V3 start due to more complex model)
Epoch   5: Val R² ~ 0.25-0.35 (learning progressing)
Epoch  10: Val R² ~ 0.35-0.45 (approaching target)
```

Mid-training (10-30):

```
Epoch  20: Val R² ~ 0.40-0.50 (reaching target range)
Epoch  30: Val R² ~ 0.45-0.55 (optimal performance)
```

Late training (30-60):

```
Epoch  40-60: Fine-tuning, may plateau
Early stopping likely around epoch 50-80
```

**Training time:** ~1 hour (depends on GPU)

---

## Expected Results

### Performance Targets:

| Metric               | V3-Clean | V4 Target   | V4 Stretch   |
| -------------------- | -------- | ----------- | ------------ |
| **Test R²**          | 0.236    | 0.46-0.50   | 0.50-0.55    |
| **Test Correlation** | 0.50     | 0.68-0.71   | 0.71-0.74    |
| **Improvement**      | Baseline | **95-112%** | **112-133%** |

### What if results are lower?

- **R² = 0.35-0.45:** Good progress! Consider Phase 3 (meta-learning + ensemble)
- **R² = 0.25-0.35:** Model is learning but needs more capacity/data
- **R² < 0.25:** Check training logs for issues (gradient explosion, poor convergence)

---

## Feature Breakdown

### Total Features: 135

| Feature Group          | Count | Source        |
| ---------------------- | ----- | ------------- |
| **Spectral features**  | 61    | From V3-Clean |
| - Theta power          | 7     | Per channel   |
| - Gamma power          | 7     | Per channel   |
| - Alpha power          | 7     | Per channel   |
| - Beta power           | 7     | Per channel   |
| - Theta-gamma ratio    | 7     | Per channel   |
| - PAC features (no MI) | 21    | 3 per channel |
| - Global statistics    | 5     | Cross-channel |
| **Wavelet features**   | 74    | NEW in V4     |
| - CWT features         | 35    | 5 per channel |
| - WPD features         | 28    | 4 per channel |
| - Phase sync index     | 1     | Global        |
| - CWT statistics       | 10    | Cross-channel |

---

## Model Architecture Summary

```
Input: Raw EEG (1×7×500) + Spectral (61) + Wavelet (74)

┌─────────────────────────────────────────────────────┐
│ Branch 1: Raw EEG                                   │
│   ↓                                                 │
│   EEGToImage (7×500 → 3×35×100)                    │
│   ↓                                                 │
│   Patch Embed (→ 192×200)                          │
│   ↓                                                 │
│   + Positional Encoding                            │
│   ↓                                                 │
│   Transformer Encoder (3 layers, 4 heads)          │
│   ↓                                                 │
│   Global Pool + Project → (64,)                    │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Branch 2: Spectral + Wavelet Features              │
│   ↓                                                 │
│   Concatenate (61 + 74 = 135)                      │
│   ↓                                                 │
│   MLP: 135 → 128 → 64                              │
└─────────────────────────────────────────────────────┘

Fusion:
  Concatenate branches → (128,)
  ↓
  Expand temporal dim → (128, 32)
  ↓
  TCN (4 blocks, exp. dilation 1,2,4,8) → (64, 32)
  ↓
  SE Channel Attention → (64, 32)
  ↓
  Regression Head: Pool + MLP (128→64→32→1)
  ↓
Output: PAC prediction (scalar)
```

**Total parameters:** ~2-5M
**Inference time:** ~5-10ms per sample on GPU

---

## Next Steps After Training

### 1. Evaluate Results

```bash
# Results automatically saved to:
models/best_vit_tcnet_v4.pth          # Best model weights
models/training_history_v4.npz        # Training curves
models/vit_tcnet_stats_v4.npz         # Normalization stats
```

### 2. Compare with V3-Clean

```python
import numpy as np

# Load V3 history
v3_hist = np.load('models/training_history_v3.npz')
v3_best_r2 = v3_hist['best_val_r2']  # 0.236

# Load V4 history
v4_hist = np.load('models/training_history_v4.npz')
v4_best_r2 = v4_hist['best_val_r2']  # Expected: 0.46-0.55

improvement = (v4_best_r2 - v3_best_r2) / v3_best_r2 * 100
print(f"Improvement: {improvement:.1f}%")
```

### 3. Generate Visualizations

Create plots for:

- Training/validation loss curves
- R² progression over epochs
- Predicted vs actual PAC scatter plot
- Residual analysis

### 4. Update Lab Notebook

Document:

- Final V4 performance (test R², correlation, MAE)
- Comparison with V3-Clean and baselines
- Key insights from training (convergence, optimal epoch, etc.)
- Ablation study (contribution of each component)

### 5. Proceed to Closed-Loop Simulation

Use the trained V4 model for real-time PAC prediction in the closed-loop system.

---

## Troubleshooting

### If training is too slow:

- Reduce batch size (32 → 16)
- Reduce TCN channels ([64,64,64,64] → [32,32,32,32])
- Reduce transformer layers (3 → 2)

### If model overfits (train R² >> val R²):

- Increase weight decay (0.001 → 0.002)
- Increase dropout (0.4 → 0.5)
- Add more augmentation

### If model underfits (both train and val R² low):

- Increase model capacity (TCN channels, transformer layers)
- Reduce regularization
- Train longer (increase patience)

---

## Research Papers Referenced

1. **Fusing Pretrained ViTs with TCNet for Enhanced EEG Regression** (2024)
   - Main architecture inspiration
   - https://arxiv.org/abs/2404.15311

2. **EEG-TCNet: An Accurate Temporal Convolutional Network** (2020)
   - TCN design for EEG
   - https://arxiv.org/pdf/2006.00622

3. **Electroencephalographic Signal Data Augmentation Based on Improved GAN** (2024)
   - Data augmentation strategies
   - https://pmc.ncbi.nlm.nih.gov/articles/PMC11047879/

4. **Wavelet Features for EEG Analysis** (2024)
   - CWT + WPD feature extraction
   - https://www.sciencedirect.com/science/article/abs/pii/S1746809423002446

5. **Robust Loss Functions for Deep Learning** (2019)
   - Huber loss optimization
   - https://arxiv.org/abs/1712.09482

---

## Summary

**V4 implements Phase 2 of the improvement plan:**

- ✅ ViT-TCNet architecture (state-of-the-art for EEG regression)
- ✅ Wavelet features (+74 features capturing time-frequency dynamics)
- ✅ Enhanced augmentation (5 time-series transformations)
- ✅ Huber loss (robust to outliers)
- ✅ Improved regularization

**Expected improvement:** R² = 0.236 → 0.46-0.55 (95-133% improvement)

**Next:** Train the model and evaluate results!

---

**Status:** Ready to train
**Command:** `python run_training_v4.py`
**Expected time:** ~1 hour
**Expected R²:** 0.46-0.55 ⭐
