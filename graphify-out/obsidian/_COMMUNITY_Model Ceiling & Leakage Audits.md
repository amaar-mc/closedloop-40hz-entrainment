---
type: community
members: 38
---

# Model Ceiling & Leakage Audits

**Members:** 38 nodes

## Members
- [[135 Total Features (61 Spectral + 74 Wavelet) for V4]] - document - archive/docs_v1_v8/V4_VIT_TCNET.md
- [[61-Feature Breakdown (7 Theta + 7 Gamma + 7 Alpha + 7 Beta + 7 Ratio + 21 PAC + 5 Global)]] - document - archive/docs_v1_v8/V3_CLEAN_NO_MI.md
- [[Circular Reasoning Constraint Cannot Use PAC to Predict PAC]] - document - archive/docs_v1_v8/FINAL_VERDICT_MASTER_MODEL.md
- [[Data Split Audit Passed 24 Train  5 Val  6 Test Subjects (No Overlap)]] - document - archive/docs_v1_v8/AUDIT_REPORT.md
- [[Distribution Shift Between TrainValTest (KL Divergence 709-1691)]] - document - archive/docs_v1_v8/V4_FAILURE_ANALYSIS.md
- [[Domain Mismatch ImageNet Pre-training Does Not Transfer to EEG]] - document - archive/docs_v1_v8/V4_FAILURE_ANALYSIS.md
- [[EEGNetV2 Architecture (F1=12, F2=24, ~3200 params)]] - document - archive/docs_v1_v8/IMPROVEMENTS_V2_SUMMARY.md
- [[Honest Baseline Ridge Regression R²=0.287 (135 spectral+wavelet features)]] - document - archive/docs_v1_v8/FINAL_ASSESSMENT.md
- [[Improvement Plan V3 R²=0.236 → Target R²=0.45-0.55]] - document - archive/docs_v1_v8/IMPROVEMENT_PLAN.md
- [[Information-Theoretic Limit Shannon Mutual Information Confirms R² ≈ 0.29]] - document - archive/docs_v1_v8/FINAL_VERDICT_MASTER_MODEL.md
- [[MI Formula in Features Identical to Target PAC Formula (KL Divergence)]] - document - archive/docs_v1_v8/AUDIT_REPORT.md
- [[MI Leakage Fix Modulation Index Removed from Spectral Features]] - document - archive/docs_v1_v8/V3_CLEAN_NO_MI.md
- [[Master Model Verdict R² ≈ 0.29 Ceiling]] - document - archive/docs_v1_v8/FINAL_VERDICT_MASTER_MODEL.md
- [[Meta-Learning Plan (MAML for Subject-Independent Transfer)]] - document - archive/docs_v1_v8/IMPROVEMENT_PLAN.md
- [[Multi-Head Attention Fusion (4 Heads, 192 dims)]] - document - archive/docs_v1_v8/V3_IMPLEMENTATION_SUMMARY.md
- [[Multi-Scale Temporal CNN (Kernel Sizes 163264128)]] - document - archive/docs_v1_v8/V3_IMPLEMENTATION_SUMMARY.md
- [[Multi-Task Learning Plan (PAC + Theta + Gamma Joint Prediction)]] - document - archive/docs_v1_v8/IMPROVEMENT_PLAN.md
- [[Overparameterization Failure Pattern (ViT-TCNet 1.1M params vs 11k samples)]] - document - archive/docs_v1_v8/FINAL_VERDICT_MASTER_MODEL.md
- [[PAC Features (pac_features.py) Flagged as Circular — Do Not Use]] - document - archive/docs_v1_v8/FINAL_ASSESSMENT.md
- [[Rationale Features  Architecture for Small EEG Datasets]] - document - archive/docs_v1_v8/FINAL_ASSESSMENT.md
- [[Rationale PAC is Theta-Gamma Frequency Coupling — Explicit Features Required]] - document - archive/docs_v1_v8/ARCHITECTURE_V3_DESIGN.md
- [[Ridge Regression Best Model (R²=0.287, ~200 params)]] - document - archive/docs_v1_v8/FINAL_VERDICT_MASTER_MODEL.md
- [[SNR Ceiling -4.73 dB Limits R² to ~0.30]] - document - archive/docs_v1_v8/FINAL_VERDICT_MASTER_MODEL.md
- [[SpecTempNet Architecture Design (3-Branch Raw EEG + Spectral + Phase-Amplitude)]] - document - archive/docs_v1_v8/ARCHITECTURE_V3_DESIGN.md
- [[SpecTempNet V3 Hybrid Spectral-Temporal Network (~180k params)]] - document - archive/docs_v1_v8/V3_IMPLEMENTATION_SUMMARY.md
- [[Subject-Specific Adaptation as V3 Fallback Option]] - document - archive/docs_v1_v8/ARCHITECTURE_V3_DESIGN.md
- [[Task Distinction Future PAC Prediction (R²=0.80 target) vs Static Window PAC (R²=0.29)]] - document - archive/docs_v1_v8/FINAL_VERDICT_MASTER_MODEL.md
- [[Three Data Leakage Encounters (V1 MI, V4 Suspected, V5 PAC Features)]] - document - archive/docs_v1_v8/FINAL_ASSESSMENT.md
- [[V2 Data Augmentation (Time Jitter, Amplitude Scaling, Gaussian Noise, Channel Dropout)]] - document - archive/docs_v1_v8/IMPROVEMENTS_V2_SUMMARY.md
- [[V2 Improvements ΔPAC Target + Data Augmentation + EEGNetV2]] - document - archive/docs_v1_v8/IMPROVEMENTS_V2_SUMMARY.md
- [[V3 Audit MI Feature Leakage Identified (R²=0.69 Inflated)]] - document - archive/docs_v1_v8/AUDIT_REPORT.md
- [[V3-Clean Model 61 Spectral Features (MI Removed)]] - document - archive/docs_v1_v8/V3_CLEAN_NO_MI.md
- [[V4 Wavelet Features 74 Features (35 CWT + 28 WPD + 11 Global)]] - document - archive/docs_v1_v8/V4_VIT_TCNET.md
- [[ViT-TCNet Architecture Plan (Pre-trained ViT + TCN Decoder)]] - document - archive/docs_v1_v8/IMPROVEMENT_PLAN.md
- [[ViT-TCNet V4 Design (Pre-trained ViT + TCN + SE Attention)]] - document - archive/docs_v1_v8/V4_VIT_TCNET.md
- [[ViT-TCNet V4 Failure Analysis (Test R²=0.252, Expected 0.46-0.55)]] - document - archive/docs_v1_v8/V4_FAILURE_ANALYSIS.md
- [[Wavelet Features Plan (CWT + WPD, +30-40 features)]] - document - archive/docs_v1_v8/IMPROVEMENT_PLAN.md
- [[ΔPAC Prediction Target (Change vs Absolute PAC)]] - document - archive/docs_v1_v8/IMPROVEMENTS_V2_SUMMARY.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Model_Ceiling_&_Leakage_Audits
SORT file.name ASC
```
