# Status Report: Closed-Loop 40Hz Entrainment for Alzheimer's Disease

**To:** Amaar Chughtai (Principal Investigator)
**From:** Claude (Technical Implementation Lead)
**Date:** February 5, 2026
**Re:** Complete Project Status, Gap Analysis, and Synopsys Action Plan

---

## 1. EXECUTIVE SUMMARY

Your research project — a personalized deep learning model for closed-loop 40Hz entrainment to optimize theta-gamma coupling in Alzheimer's disease — is at **approximately 45% completion toward a Synopsys-ready submission**. The intellectual foundation (methodology, literature, architecture design) is excellent and fully mature. The code implementation has a solid base but was missing 6 of 10 critical source modules. I have now created a complete `code_drafts_v2/` directory containing all 10 modules (4,159 lines of Python), a centralized `config.yaml`, and updated documentation. **No existing code was modified** — the originals remain untouched in `code_drafts/`.

**Bottom line:** You now have all the code you need. What remains is: (1) downloading the dataset, (2) running the pipeline end-to-end on your RTX 3080, (3) evaluating results, (4) iterating if targets aren't met, and (5) writing the final Synopsys report.

---

## 2. WHAT HAS BEEN COMPLETED

### 2.1 Research Foundation (100% Complete)

All 7 research documents are thorough and publication-quality:

- **01_Foundational_Concepts**: Gamma oscillations, PING mechanism, theta-gamma PAC biology, AD pathophysiology
- **02_Literature_Review**: 50+ papers, Iaccarino 2016 landmark study, Chan 2025 clinical trials, 30% non-responder problem identified
- **03_Technical_Methods**: Signal processing pipeline, EEGNet architecture, PAC computation methods
- **04_Research_Methodology**: GAT-Transformer proposal (later simplified to EEGNet), MPC formulation
- **05_Annotated_Bibliography**: Complete source annotations
- **Comprehensive_Methodology**: The definitive 7-phase implementation plan — this is your ground truth
- **AD_40Hz_IEEE_Paper**: Draft research paper in IEEE format

### 2.2 Code Implementation (Now 100% of Modules Written)

#### Previously Existing (code_drafts/src/) — 4 files, ~1,490 lines:

| Module | Lines | Status | Methodology Compliance |
|--------|-------|--------|----------------------|
| `pac_computation.py` | 349 | COMPLETE, validated with synthetic signals | 100% — Tort MI method, theta 4-8Hz, gamma 38-42Hz, 18 bins, Hilbert transform, KL divergence |
| `eegnet.py` | 296 | COMPLETE, forward pass tested | 100% — 7 channels, 500 samples, F1=8, D=2, F2=16, dropout=0.5, ~2000 params, regression head |
| `personalization.py` | 327 | COMPLETE, unit tested | 100% — 30s rolling window, z-score normalization, circular buffer, min_samples=10 |
| `utils.py` | 447 | COMPLETE | 100% — Plotting, metrics (R², RMSE, MAE, correlation), logging, config management |

#### Newly Created (code_drafts_v2/src/) — 6 files, ~2,669 lines:

| Module | Lines | Status | Methodology Compliance |
|--------|-------|--------|----------------------|
| `data_loader.py` | 576 | NEW — needs dataset to test | Implements BIDSPath loading, 7-channel selection, 2s windows, 50% overlap, PAC labels, 70/15/15 subject-level splits |
| `preprocessing.py` | 440 | NEW — needs dataset to test | Bandpass 0.5-80Hz, notch 50/60Hz, ±100µV artifact rejection, CAR, SNR estimation, bad channel detection |
| `training.py` | 507 | NEW — needs dataset to run | MSE loss, Adam (lr=0.001, wd=1e-4), ReduceLROnPlateau, early stopping (patience=15), data augmentation (time shift, amplitude scale, noise) |
| `controller.py` | 364 | NEW — needs trained model | StimState enum, z-score thresholds (-0.5/+0.5), 5s hysteresis, EEGNet + PersonalizationModule integration |
| `simulator.py` | 308 | NEW — can test with synthetic data | Exponential dynamics, tau_rise=0.15, tau_decay=0.10, PAC range [0.05, 0.3], noise σ=0.02, empirical tau extraction |
| `validation.py` | 549 | NEW — needs trained model + simulator | 4-way comparison (fixed/reactive/predictive/oracle), ANOVA, Tukey HSD, Cohen's d, cross-subject CV |

### 2.3 Configuration and Documentation

| Item | Status |
|------|--------|
| `config.yaml` | NEW — centralized parameter management for all modules |
| `requirements.txt` | Complete — PyTorch 2.0+, MNE, scipy, tensorpac, etc. |
| `README.md` | Complete — setup, usage, citations |
| `GAP_ANALYSIS.md` | Complete — identified all gaps (now resolved in v2) |
| `IMPLEMENTATION_SUMMARY.md` | Complete — technical overview |
| `DEVELOPMENT_LOG.md` | Complete — design decisions documented |

---

## 3. WHAT HAS NOT BEEN COMPLETED

These are the operational steps — not code, but execution:

| Step | Status | Dependency | Estimated Time |
|------|--------|------------|----------------|
| Download OpenNeuro ds005048 dataset | NOT DONE | Internet + ~10GB storage | 30-60 min |
| Run preprocessing on raw data | NOT DONE | Downloaded dataset | 1-2 hours |
| Generate PAC labels for all windows | NOT DONE | Preprocessed data | 2-3 hours |
| Train EEGNet model | NOT DONE | PAC labels + RTX 3080 | 2-3 hours |
| Evaluate model accuracy (R² > 0.80 target) | NOT DONE | Trained model | 30 min |
| Extract empirical tau parameters | NOT DONE | Preprocessed data + PAC values | 1 hour |
| Run closed-loop simulation | NOT DONE | Trained model + simulator | 1-2 hours |
| Statistical analysis (ANOVA, effect sizes) | NOT DONE | Simulation results | 1-2 hours |
| Generate publication figures | NOT DONE | All results | 2-3 hours |
| Write final Synopsys report | NOT DONE | All results | 4-8 hours |

**Total remaining effort: ~15-25 hours (~3-4 days of focused work)**

---

## 4. STEP-BY-STEP ACTION PLAN FOR SYNOPSYS

Here is exactly what you need to do, in order:

### STEP 1: Environment Setup (Day 1, ~1 hour)

```bash
cd code_drafts_v2
python3.10 -m venv venv
source venv/bin/activate
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, GPU: {torch.cuda.get_device_name(0)}')"
```

### STEP 2: Clone/Download the Dataset (Day 1, ~30-60 min)

Yes, you need to download the data. You have three options:

```bash
# Option A: OpenNeuro CLI (recommended)
pip install openneuro-cli
openneuro download --snapshot 1.0.1 ds005048 -o data/raw/ds005048

# Option B: AWS S3 (faster, no sign-in required)
aws s3 sync --no-sign-request s3://openneuro.org/ds005048 data/raw/ds005048/

# Option C: Manual download from https://openneuro.org/datasets/ds005048/versions/1.0.1
```

After download, verify the structure:
```bash
ls data/raw/ds005048/sub-*/ses-*/eeg/*.set
# Should show .set files for each subject
```

### STEP 3: Preprocess and Generate Training Data (Day 1-2, ~3-4 hours)

```bash
python src/data_loader.py \
  --bids_root data/raw/ds005048 \
  --output data/processed \
  --window_sec 2.0 \
  --hop_sec 1.0
```

This will:
- Load each subject's EEG from BIDS .set files
- Select 7 frontal channels (Fp1, Fp2, F7, F3, Fz, F4, F8)
- Apply preprocessing (bandpass, notch, artifact rejection)
- Extract 2-second sliding windows with 50% overlap
- Compute PAC labels (Modulation Index) for every window
- Split subjects into train (70%), validation (15%), test (15%)
- Save everything to `data/processed/`

**What to check after this step:**
- How many total windows were generated? (expect ~5,000-15,000)
- What is the PAC distribution? (expect range ~0.001 to ~0.3)
- Are there any subjects with no valid windows? (if so, check data quality)

### STEP 4: Train the EEGNet Model (Day 2, ~2-3 hours)

```bash
python src/training.py \
  --data_dir data/processed \
  --output_dir models \
  --epochs 100 \
  --batch_size 64 \
  --lr 0.001 \
  --device cuda
```

**What you're looking for:**
- Training loss should decrease smoothly
- Validation loss should track training loss (no large gap = no overfitting)
- Early stopping should trigger around epoch 40-80
- Best model saved to `models/best_eegnet.pth`

### STEP 5: Evaluate Model — THE CRITICAL GATE (Day 2, ~30 min)

**This is the moment of truth.** Your target is R² > 0.80.

Run the model on the test set and check:
- **R² score** (coefficient of determination)
- **RMSE** (root mean squared error)
- **Correlation** (Pearson r)

**IF R² > 0.80:** Proceed to Step 6. You're on track.

**IF R² = 0.60-0.80:** Acceptable for a research project. You can still demonstrate the closed-loop concept works. Adjust your paper's claims to report the actual R² and discuss limitations. Try these improvements:
- Enable data augmentation (time shifting, amplitude scaling)
- Increase epochs to 150
- Try batch size 32 (sometimes helps)
- Try learning rate 0.0005

**IF R² < 0.60:** More work needed. Try:
- Check PAC label quality — are labels noisy? Try averaging PAC across channels differently
- Add L2 regularization (increase weight_decay to 1e-3)
- Try subject-specific fine-tuning: train on all subjects, then fine-tune final layer on each test subject
- Consider if the prediction horizon is too ambitious — try predicting current PAC (0s ahead) instead of 5-10s ahead
- Use ensemble of 3-5 EEGNet models with different random seeds

### STEP 6: Run Closed-Loop Simulation (Day 3, ~2 hours)

```bash
python src/validation.py \
  --model_path models/best_eegnet.pth \
  --data_dir data/processed \
  --output_dir results \
  --duration 360
```

This runs 4 control strategies head-to-head:
1. **Fixed Schedule** (control): 40s ON / 20s OFF
2. **Reactive Threshold**: Decisions based on current PAC (no prediction)
3. **Predictive MPC** (your system): EEGNet prediction + z-score + hysteresis
4. **Oracle**: Perfect PAC knowledge (theoretical upper bound)

**Target results:**
- Predictive MPC achieves ≥15% PAC improvement over Fixed Schedule
- Predictive MPC uses 30-40% stimulation time (vs. 67% for Fixed Schedule)
- Predictive MPC outperforms Reactive by 10-20%
- Statistical significance: p < 0.05 (ANOVA)

### STEP 7: Analyze and Iterate (Day 3-4, ~2-3 hours)

If targets are not met, iterate:
- Tune z-score thresholds (-0.5/+0.5 are starting points)
- Adjust hysteresis hold time (try 3s or 7s instead of 5s)
- Adjust simulator tau parameters using empirical extraction from your data
- Try different test subjects

Generate all publication figures:
- PAC prediction scatter plot (predicted vs. actual)
- Training curves (loss over epochs)
- Closed-loop vs. open-loop PAC time series
- Bar chart comparing all 4 strategies
- Z-score distribution histogram

### STEP 8: Write Synopsys Report (Day 4-5, ~4-8 hours)

Your Synopsys submission needs:
- Abstract (250 words)
- Introduction and background
- Methods (reference your Comprehensive Methodology)
- Results (with figures and statistical tests)
- Discussion (what worked, what didn't, limitations)
- Conclusion and future work
- References

---

## 5. MODEL ARCHITECTURE — DETAILED SPECIFICATION

### EEGNet for PAC Regression

```
INPUT: (batch, 1, 7, 500) — 7 frontal EEG channels, 2 seconds @ 250 Hz

┌─────────────────────────────────────────────────────────────┐
│  BLOCK 1: Temporal + Spatial Feature Extraction              │
│                                                              │
│  Conv2D(1→8, kernel=(1,64), padding=(0,32))   [TEMPORAL]     │
│  BatchNorm2d(8)                                              │
│  DepthwiseConv2D(8→16, kernel=(7,1), groups=8) [SPATIAL]     │
│  BatchNorm2d(16)                                             │
│  ELU activation                                              │
│  AvgPool2d(1,4)                                              │
│  Dropout(0.5)                                                │
│                                                              │
│  Output: (batch, 16, 1, 125)                                 │
├─────────────────────────────────────────────────────────────┤
│  BLOCK 2: Separable Convolution                             │
│                                                              │
│  DepthwiseConv2D(16→16, kernel=(1,16), groups=16)            │
│  PointwiseConv2D(16→16, kernel=(1,1))                        │
│  BatchNorm2d(16)                                             │
│  ELU activation                                              │
│  AvgPool2d(1,8)                                              │
│  Dropout(0.5)                                                │
│                                                              │
│  Output: (batch, 16, 1, 15)                                  │
├─────────────────────────────────────────────────────────────┤
│  REGRESSION HEAD                                             │
│                                                              │
│  Flatten → (batch, 240)                                      │
│  Linear(240, 1)                                              │
│                                                              │
│  Output: (batch, 1) — Predicted PAC value                    │
└─────────────────────────────────────────────────────────────┘

Total trainable parameters: ~2,000
```

### Why EEGNet (not GAT-Transformer)

Your original methodology (Document 04) proposed a Graph Attention Network + Transformer. The Comprehensive Methodology wisely simplified this to EEGNet. The reasons are:

1. **Parameter count**: EEGNet has ~2,000 params vs. ~50,000+ for GAT-Transformer. With only ~20 subjects, you'd massively overfit with the larger model.
2. **Training time**: 2-3 hours on RTX 3080 vs. potentially days.
3. **Proven track record**: EEGNet is validated across dozens of EEG-BCI papers.
4. **Sufficient for the task**: PAC prediction from 7 channels is a relatively constrained regression task.

### Closed-Loop Control Architecture

```
                    ┌──────────────────┐
   EEG Window ──────┤   EEGNet Model   ├──── PAC Prediction
   (7 × 500)        │   (~2000 params) │         │
                    └──────────────────┘         │
                                                  ▼
                                        ┌──────────────────┐
                                        │ Personalization   │
                                        │ Module            │
                                        │ (30s rolling      │
                                        │  baseline)        │
                                        └────────┬─────────┘
                                                  │
                                              z-score
                                                  │
                                                  ▼
                                        ┌──────────────────┐
                                        │ Decision Engine   │
                                        │                   │
                                        │ z < -0.5 → STIM  │
                                        │ z > +0.5 → REST  │
                                        │ else   → HOLD    │
                                        │                   │
                                        │ (5s hysteresis)   │
                                        └────────┬─────────┘
                                                  │
                                          STIMULATE / REST
                                                  │
                                                  ▼
                                        ┌──────────────────┐
                                        │ 40 Hz Auditory    │
                                        │ Stimulation       │
                                        │ (ON / OFF)        │
                                        └──────────────────┘
```

---

## 6. GOAL SUMMARY — WHAT SUCCESS LOOKS LIKE

### Primary Metrics (Must Achieve)

| Metric | Target | What It Proves |
|--------|--------|---------------|
| Prediction R² | > 0.80 | EEGNet can forecast near-future PAC from EEG |
| PAC Improvement | ≥ 15% over fixed schedule | Closed-loop is better than open-loop |
| p-value | < 0.05 | Results are statistically significant |

### Secondary Metrics (Strengthen the Paper)

| Metric | Target | What It Proves |
|--------|--------|---------------|
| Stimulation reduction | 60-70% less than fixed schedule | Energy efficiency / reduced exposure |
| PAC stability | Lower variance than fixed schedule | More consistent therapeutic state |
| Cohen's d | > 0.5 (medium effect) | Clinically meaningful effect size |

### The Synopsys Narrative

Your paper tells this story:
1. **Problem**: AD disrupts gamma oscillations and theta-gamma coupling. Current 40Hz entrainment is static (one-size-fits-all).
2. **Gap**: 30% of patients don't respond. Individual variability is not addressed.
3. **Solution**: A personalized closed-loop system that predicts brain state and adapts stimulation in real-time.
4. **Method**: EEGNet (deep learning) + z-score personalization + MPC control policy.
5. **Result**: X% PAC improvement, Y% stimulation reduction, p < 0.05.
6. **Significance**: First application of predictive closed-loop control to gamma entrainment for AD.

---

## 7. RISK REGISTER

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| R² < 0.80 | Medium | HIGH | Data augmentation, ensemble, fine-tuning, lower prediction horizon |
| Dataset download fails | Low | HIGH | 3 download methods available, can start with 2-3 subjects |
| PAC improvement < 15% | Medium | HIGH | Tune thresholds, adjust hysteresis, try different tau parameters |
| Overfitting (small dataset) | Medium | MEDIUM | ~2000 params, dropout 0.5, L2, early stopping, LOSO-CV |
| RTX 3080 memory issues | Low | LOW | Reduce batch size to 16-32, gradient accumulation |
| Simulation doesn't match real brain dynamics | Medium | MEDIUM | Extract empirical tau from data, sensitivity analysis, acknowledge limitation |

---

## 8. FILE INVENTORY

### code_drafts/ (Original — Untouched)
```
src/eegnet.py             296 lines  ✅ Complete
src/pac_computation.py     349 lines  ✅ Complete
src/personalization.py     327 lines  ✅ Complete
src/utils.py               447 lines  ✅ Complete
```

### code_drafts_v2/ (New — Complete Pipeline)
```
src/eegnet.py              295 lines  ✅ (copied from v1)
src/pac_computation.py     348 lines  ✅ (copied from v1)
src/personalization.py     326 lines  ✅ (copied from v1)
src/utils.py               446 lines  ✅ (copied from v1)
src/data_loader.py         576 lines  ✅ NEW
src/preprocessing.py       440 lines  ✅ NEW
src/training.py            507 lines  ✅ NEW
src/controller.py          364 lines  ✅ NEW
src/simulator.py           308 lines  ✅ NEW
src/validation.py          549 lines  ✅ NEW
config.yaml                           ✅ NEW
requirements.txt                      ✅ Complete
README.md                             ✅ Complete
                          ─────────
TOTAL:                    4,159 lines of Python
```

### Research Documents
```
01_Foundational_Concepts_40Hz_Entrainment_AD.docx       ✅
02_Literature_Review_40Hz_Entrainment_AD.docx            ✅
03_Technical_Methods_Signal_Processing.docx               ✅
04_Research_Methodology_Proposed_Approach.docx            ✅
05_Annotated_Bibliography_Sources.docx                    ✅
AD_40Hz_Entrainment_Research_Paper_IEEE.docx              ✅
Comprehensive_Methodology_Closed_Loop_40Hz_Entrainment.docx  ✅
```

---

## 9. TIMELINE TO SYNOPSYS SUBMISSION

| Day | Task | Deliverable |
|-----|------|-------------|
| Day 1 | Setup environment, download dataset | Working environment, raw data on disk |
| Day 1-2 | Preprocess data, generate PAC labels | `data/processed/` with all windows and labels |
| Day 2 | Train EEGNet | `models/best_eegnet.pth`, training curves |
| Day 2 | Evaluate model accuracy | R² score, prediction scatter plot |
| Day 3 | Run closed-loop simulation | Comparison metrics for 4 strategies |
| Day 3 | Statistical analysis | ANOVA, Tukey HSD, effect sizes |
| Day 3-4 | Generate all figures | Publication-quality plots in `results/figures/` |
| Day 4-5 | Write Synopsys report | Final paper with abstract, methods, results, discussion |

**Estimated total: 4-5 focused days from today.**

---

*Report generated February 5, 2026. All code files are in `code_drafts_v2/`. Original drafts preserved in `code_drafts/`.*
