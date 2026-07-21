# Model Improvements V2 - Summary

**Date:** February 17, 2026
**Objective:** Improve PAC prediction from R² = 0.084 → R² > 0.30

---

## 🎯 GOAL

Achieve a prediction accuracy (R²) of **at least 0.30** for theta-gamma PAC prediction, enabling a credible closed-loop control system for 40Hz entrainment optimization in Alzheimer's disease.

**Current Baseline:** R² = 0.084 (validation), trained on February 5-6, 2026
**Realistic Target:** R² = 0.30-0.50
**Stretch Goal:** R² > 0.50

---

## 📊 ARCHITECTURE CHANGES

### **BEFORE (Baseline - R² = 0.084)**

**Prediction Target:**

- Absolute PAC at t+1 second
- Input: EEG[t-2s, t] → Output: PAC[t+1s, t+3s]
- Problem: Low autocorrelation at 1s lag (r=0.43)

**Model: EEGNet**

```
F1 = 8  (temporal filters)
D  = 2  (depth multiplier)
F2 = 16 (separable filters)
Parameters: 1,457
Dropout: 0.5
```

**Training:**

- Loss: MSE (Mean Squared Error)
- Optimizer: Adam (lr=0.001, wd=0.0001)
- Scheduler: ReduceLROnPlateau
- Batch size: 64
- Epochs: 100 (early stop patience=15)
- **No data augmentation**

**Results:**

- Train Loss: 0.866
- Val Loss: 0.996
- Val R²: **0.0838**
- Val MAE: 0.745

---

### **AFTER (Improved - Target R² > 0.30)**

**Prediction Target:** ⭐ **KEY CHANGE**

- **ΔPAC (change)** at t+0.5 seconds
- Input: EEG[t-2s, t] → Output: ΔPAC = PAC[t+0.5s] - PAC[t]
- Advantage: Removes subject-specific baseline shifts, higher autocorrelation

**Model: EEGNetV2** ⭐ **ENHANCED**

```
F1 = 12  (50% more temporal filters)
D  = 2   (unchanged)
F2 = 24  (50% more separable filters)
Parameters: ~3,200 (2.2× larger, still small)
Dropout: 0.5
+ Additional FC hidden layer (64 units)
```

**Training:** ⭐ **IMPROVED**

- Loss: **Huber Loss** (robust to outliers, delta=1.0)
- Optimizer: AdamW (lr=0.001, wd=0.0001)
- Scheduler: **CosineAnnealingWarmRestarts** (T0=10, Tmult=2)
- **Gradient clipping**: max_norm=1.0
- Batch size: 64
- Epochs: **150** (patience=**20**)
- **Data augmentation:** ⭐ **NEW**
  - Time jittering: ±25 samples (±0.1s)
  - Amplitude scaling: 0.95-1.05×
  - Gaussian noise: σ=0.03 × signal_std
  - Channel dropout: Randomly zero 1 channel (20% prob)
  - Applied with 50% probability during training

---

## 📈 EXPECTED IMPROVEMENTS

Based on error analysis (documented in lab notebook Page 56-59):

| Change                        | Expected ΔR²   | Rationale                                        |
| ----------------------------- | -------------- | ------------------------------------------------ |
| **ΔPAC prediction**           | +0.07 to +0.12 | Removes baseline variability, higher signal      |
| **Shorter horizon (1s→0.5s)** | +0.04 to +0.10 | Higher autocorrelation at 0.5s lag               |
| **Data augmentation**         | +0.03 to +0.07 | Reduces overfitting, increases effective samples |
| **Enhanced model**            | +0.02 to +0.04 | Slightly more capacity without overfitting       |
| **Huber loss**                | +0.01 to +0.03 | Robust to outlier PAC values                     |

**Total Expected Improvement:** +0.17 to +0.36
**Predicted R²:** 0.084 + 0.17 to 0.36 = **0.25 to 0.44**

**Realistic Target:** R² = 0.30 (midpoint)

---

## 📁 NEW FILES CREATED

1. **`src/eegnet_v2.py`** - Enhanced model architecture
2. **`src/data_loader_v2.py`** - ΔPAC computation + augmentation
3. **`src/training_v2.py`** - Improved training loop
4. **`run_training_v2.py`** - Simple runner script

---

## 🚀 HOW TO RUN

### Prerequisites:

```bash
# Ensure you're in the project directory
cd /path/to/closedloop-40hz-entrainment

# Activate environment (if using venv)
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Verify CUDA is available (optional but recommended)
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### Run Training:

```bash
python run_training_v2.py
```

**Expected Output:**

```
================================================================================
IMPROVED TRAINING PIPELINE (Version 2)
================================================================================

Key Improvements:
  ✓ ΔPAC prediction (change vs absolute)
  ✓ Shorter prediction horizon (0.5s vs 1s)
  ✓ Data augmentation (time jitter, scaling, noise)
  ✓ Enhanced EEGNet (F1=12, F2=24, ~3200 params)
  ✓ Huber loss (robust to outliers)
  ✓ Cosine annealing learning rate
  ✓ Gradient clipping
  ✓ Longer training (150 epochs, patience=20)

Target: R² > 0.30 (currently 0.084)
================================================================================

Press Enter to start training (or Ctrl+C to cancel)...

[Training begins...]
```

### Training Duration:

- **Per epoch:** ~2-3 minutes (on RTX 3080)
- **Total (150 epochs max):** ~5-7 hours
- **With early stopping (expected ~60-80 epochs):** ~2-4 hours

### Outputs:

- **Best model:** `models/best_eegnet_v2.pth`
- **Training history:** `models/training_history_v2.npz`
- **PAC statistics:** `models/pac_stats_v2.npz`
- **Console log:** Printed to terminal (can redirect to file)

---

## 📊 WHAT TO EXPECT

### Good Outcome (Target):

```
Best epoch: 65
Best val loss: 0.723
Best val R²: 0.314
```

→ **R² = 0.31** (3.7× improvement!) ✓ Proceed to closed-loop simulation

### Moderate Outcome:

```
Best val R²: 0.20-0.29
```

→ **2.4-3.5× improvement** - Still useful, acknowledge limitations in paper

### Poor Outcome:

```
Best val R²: <0.15
```

→ **<2× improvement** - Need further iteration, but can still demonstrate proof-of-concept

---

## 🔍 MONITORING TRAINING

Watch for these indicators:

**✓ Good signs:**

- Val R² steadily increasing
- Train/val loss gap small (<0.15)
- Learning rate smoothly annealing
- Early stopping around epoch 60-80

**⚠ Warning signs:**

- Val R² plateaus below 0.15 early
- Large train/val gap (>0.3) = overfitting
- Val R² decreasing after initial increase

**If training fails:**

1. Check CUDA is working: `nvidia-smi`
2. Check data loaded: Look for "Training pairs: X" message
3. Check for NaN loss: Usually data normalization issue

---

## 📝 FOR LAB NOTEBOOK

Document this experiment as:

**Entry: February 17, 2026 - Experiment V2: Improved Model Training**

**Hypothesis:** Predicting ΔPAC with data augmentation and enhanced architecture will achieve R² > 0.30

**Method:**

- Changed prediction target from absolute PAC to ΔPAC
- Reduced prediction horizon from 1s to 0.5s
- Enhanced model: F1=8→12, F2=16→24 (~3200 params)
- Added data augmentation (time jitter, amplitude scale, noise, channel dropout)
- Switched to Huber loss (robust to outliers)
- Improved training: cosine annealing, gradient clipping, longer epochs

**Expected Result:** R² = 0.25-0.44 (realistic target 0.30)

**Actual Result:** [FILL IN AFTER TRAINING]

- Val R²: **\_\_**
- Val MAE: **\_\_**
- Val Correlation: **\_\_**

**Analysis:** [FILL IN AFTER TRAINING]

- Did improvements work as expected?
- Which changes contributed most?
- What to try next if target not met?

**Conclusion:** [FILL IN AFTER TRAINING]

---

## 🎓 SYNOPSYS PRESENTATION

If R² > 0.30:

- **"Achieved 3.6× improvement in PAC prediction accuracy through systematic optimization"**
- "Implemented ΔPAC prediction reducing subject-specific variability"
- "Data augmentation and regularization enabled better generalization"

If R² = 0.20-0.29:

- **"Achieved 2.4-3.5× improvement through architectural enhancements"**
- "Identified key challenges in EEG-based brain state prediction"
- "Demonstrated feasibility of closed-loop control despite prediction limitations"

Either way:

- **Document the PROCESS:** "Systematic error analysis → targeted improvements"
- **Show rigor:** "Tested 5 hypotheses, implemented 8 improvements"
- **Demonstrate understanding:** "PAC prediction fundamentally challenging due to neural dynamics complexity"

---

## 📚 REFERENCES FOR LAB NOTEBOOK

Improvements based on:

1. Lawhern et al. (2018) - EEGNet architecture principles
2. Ioffe & Szegedy (2015) - Batch normalization for deep learning
3. Zhang et al. (2018) - Data augmentation for time series
4. Huber (1964) - Robust loss functions
5. Loshchilov & Hutter (2019) - Cosine annealing with restarts

---

**Good luck, Amaar! Let's get those results! 🚀**
