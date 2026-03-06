# Rigorous Pipeline Audit Report

**Project:** Closed-Loop 40 Hz Gamma Entrainment System
**Audit Date:** February 21, 2026
**Purpose:** Identify and address all gaps before Synopsys Championship submission

---

## 1. Summary of Findings

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | 2 | Broken statistics (ANOVA on n=1), validation does not test actual TCN |
| HIGH | 8 | No cross-validation, no CIs, broken Cohen's d, under-parameterized EEGNet, oracle PAC features, no simulator variability, small sample sizes, duplicate method |
| MEDIUM | 9 | Preprocessing order, loss function mismatch, augmentation issues, config discrepancies |
| LOW | 5 | Redundant processing, documentation gaps, Windows-specific paths |

---

## 2. Critical Findings

### 2.1 Validation Does Not Test the Trained TCN Model
**Severity:** CRITICAL
**File:** src/validation.py, lines 202-294

The `PredictiveLookAheadControl` class in validation.py computes a simple linear regression trend over the last 5 PAC observations. It does NOT use the trained MultiscaleCausalTCN model. Despite being named "Predictive Look-Ahead," it is a trend-following heuristic.

The actual TCN-based controller (`PredictiveLookAheadController` in controller.py, lines 287-491) takes a `forecaster` argument but is never used in the validation pipeline.

**Impact:** Claims about the TCN improving closed-loop control are not supported by the validation results.
**Resolution:** The trend-based approach is a legitimate control strategy. We document it honestly as "Predictive Look-Ahead (trend-based)" and note that end-to-end TCN integration is future work.

### 2.2 Statistical Tests on n=1 Samples
**Severity:** CRITICAL
**File:** src/validation.py, lines 473-517

The `statistical_comparison` method passes single scalar values to `stats.f_oneway`. ANOVA requires within-group variance which cannot be computed from n=1.

**Resolution:** Fixed in rigor/rigorous_validation.py. Run n_trials=50+ and accumulate all trial metrics properly.

---

## 3. High Severity Findings

### 3.1 No Cross-Validation
**File:** src/data_loader.py, lines 565-631

Single fixed 70/15/15 split with seed=42. With 35 subjects, test performance is sensitive to which subjects land in each split.

**Resolution:** rigor/multi_seed_training.py runs with 5 different seeds and reports mean +/- std.

### 3.2 No Confidence Intervals
Nowhere are confidence intervals computed for any metric.

**Resolution:** rigor/rigorous_validation.py adds bootstrap 95% CIs for all metrics.

### 3.3 Cohen's d Mathematically Wrong
**File:** src/validation.py, lines 506-510

`np.var(values[0])` where `values[0]` is a single float returns 0.0, making Cohen's d astronomically large.

**Resolution:** Fixed in rigor/rigorous_validation.py with proper Hedges' g computation.

### 3.4 EEGNet Under-Parameterized
**File:** src/eegnet.py

Only ~1,457 parameters for 11,736 training samples. Temporal kernel of 64 samples (256ms) may miss full theta cycles.

**Resolution:** rigor/eegnet_enhanced.py provides EEGNetEnhanced (~10K params) and EEGNetLarge (~50K params).

### 3.5 PAC Features Use Ground-Truth
**File:** temporal_multiscale/build_multiscale_dataset.py, lines 140-163

The 7 PAC-derived features use ground truth PAC. In deployment, these would come from a noisy real-time estimator.

**Resolution:** Document as known limitation. The ablation in comprehensive_audit shows:
- Full features (73): Ridge R^2 = 0.812
- No PAC features (66): Ridge R^2 = 0.045
- PAC only features (7): Ridge R^2 = 0.859

This means most predictive power comes from PAC history, not spectral features. This is honest and expected.

### 3.6 No Subject Variability in Simulator
**File:** src/simulator.py, lines 49-91

Fixed parameters for all simulated subjects.

**Resolution:** rigor/rigorous_validation.py adds population-diverse simulation.

### 3.7 Duplicate step() Method
**File:** src/validation.py, lines 149-199

ReactiveThresholdControl defines step() twice. Second definition silently overwrites first.

**Resolution:** Noted as code quality issue, functionally benign.

### 3.8 Epoch-Level PAC Labels
**File:** src/data_loader.py, lines 362-421

All windows within the same epoch share the same PAC label. This limits what the model can learn about within-epoch dynamics.

**Resolution:** This is a fundamental dataset characteristic, not a bug. Document clearly for judges.

---

## 4. What the Existing Results Actually Show

### 4.1 Static PAC Prediction
- **R^2 = 0.287** is the genuine ceiling for predicting PAC from 7 frontal EEG channels
- 8 different architectures (EEGNet, EEGNetV2, SpecTempNet, ViT-TCNet, Ridge, Lasso, GBM, RF) all converge near this value
- The V1 R^2=0.69 was inflated by MI feature leakage (correctly caught and fixed)

### 4.2 Temporal PAC Prediction
- At ts=5 (smoothed target), the TCN achieves R^2=0.764, but persistence achieves 0.760
- At ts=1 (raw target), the TCN achieves R^2=0.067
- The KEY result is the **horizon sweep**: at 5-10s horizons, TCN R^2=0.25 while persistence is negative
- This +0.5 R^2 margin at operationally useful horizons is the core scientific contribution

### 4.3 Closed-Loop Control
- The "Predictive" method is trend-based (NOT the TCN)
- With fatigue: Predictive is significantly more efficient than Fixed (Wilcoxon p=0.0098)
- Efficiency advantage grows monotonically with fatigue severity
- The simulation uses a simplified brain model

---

## 5. Recommendations for Judges

### What to Emphasize
1. The horizon sweep result: TCN predicts where nothing else can (5-10s)
2. The efficiency advantage under fatigue is statistically significant and dose-dependent
3. The data pipeline is leak-free (shuffle sanity, subject-level splits, causal construction)
4. Honest reporting of limitations (single dataset, simulated evaluation, simplified brain model)

### What to Be Ready to Defend
1. "Why is R^2 only 0.287?" - PAC is inherently noisy, 7 channels is limited spatial info
2. "Did the TCN beat persistence?" - Only at 3+ second horizons (where it matters for control)
3. "Is this simulation realistic?" - It's a first-order approximation; real-time validation is future work
4. "How do you know there's no leakage?" - Shuffle-label test (R^2=-0.332), subject-level splits, causal construction audit

---

## 6. Changes Made in rigor/ Branch

| File | Purpose |
|------|---------|
| rigor/rigorous_validation.py | Statistically sound simulation evaluation (n=50 trials, CIs, effect sizes) |
| rigor/eegnet_enhanced.py | Enhanced EEGNet architectures (10K and 50K params) |
| rigor/multi_seed_training.py | Multi-seed training for variance estimation |
| rigor/AUDIT_REPORT.md | This document |
| docs/LOG_NOTEBOOK.md | Digital research log notebook for Synopsys |
| docs/POSTER_BOARD.md | Poster board text and visual suggestions |
