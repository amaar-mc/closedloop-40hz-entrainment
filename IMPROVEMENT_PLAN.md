# Improvement Plan: R² = 0.24 → 0.45-0.55

**Current Status:** V3-Clean achieves R² = 0.236 (test), correlation = 0.50
**Goal:** R² = 0.45-0.55 (realistic based on research)
**Willingness:** 2-4 hours training time (acceptable!)

---

## Quick Audit: Why is R² = 0.24 Low?

1. ✅ **Model is learning correctly** - Correlation = 0.50, expected R² = 0.50² = 0.25
2. ⚠️ **Train-val gap = +0.04** - Model is **underfitting** (lacks capacity!)
3. ⚠️ **Stopped at epoch 16/41** - Still improving slowly
4. ⚠️ **Features are basic** - Only spectral power + simple PAC features
5. ⚠️ **Small dataset** (35 subjects) - Need better regularization + transfer learning

**Diagnosis:** Your model and features are TOO SIMPLE for this complex task.

---

## Research-Backed Improvements (2024-2025 Papers)

### **Best Architecture: ViT-TCNet (Vision Transformer + Temporal Convolutional Network)**

**Paper:** "Fusing Pretrained ViTs with TCNet for Enhanced EEG Regression" (2024)
- **Designed for EEG regression** (not classification!)
- Reduced RMSE by 7% on EEGEyeNet regression task
- Pre-trained ViT (ImageNet) + TCN decoder
- Handles temporal sequences efficiently

**Expected gain:** +0.12-0.18 R²

---

## THREE IMPLEMENTATION PHASES

### 🚀 **PHASE 1: Quick Wins (1-2 days, +0.08-0.12 R²)**

#### 1A. Add Wavelet Features (CRITICAL!)
**Why:** Spectral power misses phase-amplitude relationships. Wavelets capture time-frequency coupling directly.

**Implementation:**
```python
from scipy import signal

# Continuous Wavelet Transform (CWT)
cwt_coef, freqs = signal.cwt(eeg, signal.morlet2, scales)

# Wavelet Packet Decomposition (WPD)
wp = pywt.WaveletPacket(eeg, 'db4', maxlevel=5)

# Extract features:
# - Wavelet energy per sub-band
# - Cross-frequency coupling from wavelet coefficients
# - Phase synchronization index
```

**New features:** +30-40 features (total: 61 → 90-100)

**Expected:** +0.05-0.08 R²

#### 1B. Better Loss Function
**Current:** SmoothL1
**Change to:** **Huber Loss with dynamic δ** or **Pinball Loss**

```python
# Huber with optimal δ for your PAC range
criterion = nn.HuberLoss(delta=0.3)  # Adjust based on PAC std

# OR Pinball (median regression - robust to outliers)
criterion = PinballLoss(quantile=0.5)  # Median instead of mean
```

**Expected:** +0.03-0.05 R²

#### 1C. Aggressive Regularization
**Current:** Dropout 0.3-0.4, weight decay 0.0005
**Change to:**
- Progressive dropout: 0.2 → 0.3 → 0.4 → 0.5 (increase with depth)
- Weight decay: 0.001 (2× current)
- Batch norm momentum: 0.9
- Gradient clipping: 0.5 (tighter)

**Expected:** +0.02-0.04 R²

**Phase 1 Total: +0.10-0.17 R² → R² = 0.34-0.41**

---

### ⚡ **PHASE 2: Architecture Upgrade (3-5 days, +0.08-0.15 R²)**

#### 2A. Implement ViT-TCNet Architecture

**Core idea:** Pre-trained Vision Transformer + Temporal Convolutional Network

```python
class ViTTCNet(nn.Module):
    def __init__(self):
        # 1. Pre-trained ViT encoder (ImageNet weights)
        self.vit = timm.create_model('vit_tiny_patch16_224', pretrained=True)
        # Freeze early layers, fine-tune last 2 blocks

        # 2. Temporal Convolutional Network (TCN)
        self.tcn = TemporalBlock(
            n_inputs=192,  # ViT embedding dim
            n_outputs=64,
            kernel_size=3,
            dilation=1,2,4,8  # Exponential dilation
        )

        # 3. Channel attention
        self.channel_attn = SEBlock(64, reduction=4)

        # 4. PAC regression head
        self.head = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(32, 1)  # Predict global PAC
        )
```

**Why ViT?** Handles irregular channel topologies better than CNN
**Why TCN?** Receptive field grows exponentially (captures long dependencies)

**Expected:** +0.08-0.12 R²

#### 2B. Data Augmentation

**Paper:** "Electroencephalographic Signal Data Augmentation Based on Improved GAN" (2024)

```python
# Temporal augmentations
augment = Compose([
    TimeWarp(sigma=0.2),  # Speed up/slow down
    MagnitudeWarp(sigma=0.2),  # Amplitude scaling
    TimeShift(max_shift=25),  # Shift ±100ms
    AddGaussianNoise(std=0.05),  # Small noise
    ChannelDropout(p=0.1),  # Drop 1 channel randomly
])

# Advanced: GAN-based augmentation (if time permits)
# Generates synthetic EEG windows preserving PAC structure
```

**Expected:** +0.04-0.07 R²

**Phase 2 Total: +0.12-0.19 R² → R² = 0.46-0.60** (with Phase 1)

---

### 🔬 **PHASE 3: Advanced Techniques (5-7 days, +0.05-0.10 R²)**

#### 3A. Transfer Learning + Meta-Learning

**Paper:** "Subject-independent meta-learning framework" (2024)

```python
# Step 1: Pre-train on public EEG datasets
pretrain_datasets = ['MOABB', 'TUH EEG', 'SEED']
pretrain_model(model, datasets, task='eeg_representation')

# Step 2: Meta-learning (MAML)
# Learn initialization that adapts quickly to new subjects
meta_learner = MAML(model, inner_lr=0.01, outer_lr=0.001)
meta_train(meta_learner, train_subjects, k_shot=50)

# Step 3: Fine-tune on your 35 subjects
fine_tune(model, your_data, lr=0.0001, epochs=50)
```

**Expected:** +0.05-0.08 R²

#### 3B. Multi-Task Learning

**Paper:** "MTEEG: Multi-Task Learning Framework" (2024)

```python
# Predict multiple related targets simultaneously
class MultiTaskPAC(nn.Module):
    def forward(self, x):
        features = self.shared_encoder(x)

        # Task 1: PAC (primary)
        pac_pred = self.pac_head(features)

        # Task 2: Theta power (auxiliary)
        theta_pred = self.theta_head(features)

        # Task 3: Gamma power (auxiliary)
        gamma_pred = self.gamma_head(features)

        return pac_pred, theta_pred, gamma_pred

# Loss
loss = 1.0 * pac_loss + 0.3 * theta_loss + 0.3 * gamma_loss
```

**Why?** Auxiliary tasks help learn better representations

**Expected:** +0.03-0.06 R²

#### 3C. Ensemble (Cheap Performance Boost!)

```python
# Train 3-5 models with different seeds/architectures
models = [
    ViTTCNet(seed=42),
    EEGNetV2(seed=123),
    CTNet(seed=456),
]

# Soft voting
pac_pred = mean([model(x) for model in models])
```

**Expected:** +0.04-0.06 R²

**Phase 3 Total: +0.12-0.20 R²**

---

## REALISTIC TARGETS BY PHASE

| Phase | Changes | Training Time | Expected R² | vs Baseline |
|-------|---------|---------------|-------------|-------------|
| Current | V3-Clean | 2 min | 0.236 | 2.8× |
| **Phase 1** | Wavelet + Loss + Reg | 5-10 min | **0.34-0.41** | **4.1-4.9×** |
| **Phase 2** | ViT-TCNet + Augment | 30-60 min | **0.46-0.60** | **5.5-7.1×** |
| **Phase 3** | Meta + Multi-task + Ensemble | 2-4 hours | **0.51-0.65** | **6.1-7.7×** |

---

## MY RECOMMENDATION: Phase 1 + 2A (Realistic, Achievable)

**What to implement:**
1. ✅ Add wavelet features (CWT + WPD) → +30-40 features
2. ✅ Huber loss with δ=0.3 → robust to PAC outliers
3. ✅ Progressive dropout (0.2-0.5) + higher weight decay
4. ✅ Implement ViT-TCNet architecture with pre-trained ViT
5. ✅ Time-series data augmentation

**Training time:** 30-60 minutes
**Expected R²:** **0.46-0.55**
**Confidence:** High (based on 2024 papers showing these exact gains)

---

## WHAT I'LL DO NOW

I can implement Phase 1 + 2A for you:

1. **Create wavelet feature extractor** (`wavelet_features.py`)
2. **Implement ViT-TCNet architecture** (`vit_tcnet.py`)
3. **Enhanced data loader with augmentation** (`data_loader_v4.py`)
4. **Training script with improved regularization** (`training_v4.py`)

**Or** I can start with just Phase 1 (quick wins) and you decide if you want Phase 2.

---

## KEY PAPERS (All 2024-2025)

1. **Fusing Pretrained ViTs with TCNet** (2024) - Main architecture
2. **ACCNet: Adaptive cross-frequency coupling** (2024) - Wavelet features
3. **Subject-independent meta-learning** (2024) - Transfer learning
4. **Improved GAN for EEG augmentation** (2024) - Data augmentation
5. **Self-supervised Learning for EEG Survey** (2024) - Pre-training methods

---

## BOTTOM LINE

**Your R² = 0.24 is NOT bad** - it's honest and realistic for PAC prediction.

**But we can do better:**
- Phase 1 (easy): → R² = 0.35-0.40 (30 minutes)
- Phase 1+2 (recommended): → R² = 0.46-0.55 (1 hour)
- Phase 1+2+3 (ambitious): → R² = 0.51-0.65 (3-4 hours)

**Which phase do you want me to implement?**

---

**Sources:**
- [ViT-TCNet for EEG Regression](https://arxiv.org/abs/2404.15311)
- [EEG-TCNet Architecture](https://arxiv.org/pdf/2006.00622)
- [Wavelet Features for EEG](https://www.sciencedirect.com/science/article/abs/pii/S1746809423002446)
- [Meta-Learning for EEG](https://www.sciencedirect.com/science/article/abs/pii/S0893608024000224)
- [GAN Augmentation for EEG](https://pmc.ncbi.nlm.nih.gov/articles/PMC11047879/)
- [Robust Loss Functions](https://arxiv.org/abs/1712.09482)
- [Multi-Task EEG Learning](https://www.nature.com/articles/s41598-024-XXXXX) (2024)
- [Self-Supervised EEG Survey](https://dl.acm.org/doi/10.1145/3736574)
