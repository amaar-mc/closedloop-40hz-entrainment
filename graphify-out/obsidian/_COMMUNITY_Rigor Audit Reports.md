---
type: community
members: 46
---

# Rigor Audit Reports

**Members:** 46 nodes

## Members
- [[73-Feature vs 12-Feature Pipeline Distinction Clarification]] - document - results/rigor_audit/08_reproducibility.md
- [[Architecture Exploration Comparison (10 models, 5-seed)]] - document - results/rigor_audit/10_architecture_exploration.md
- [[CSEF Compliance Phase (Phase 1)]] - document - results/rigor_audit/STATUS.md
- [[CSEF Font Requirements (14pt min, sans-serif recommended)]] - document - results/rigor_audit/02_font_audit.md
- [[CSEF Presentation Compliance Checklist (1818 PASS)]] - document - results/rigor_audit/01_compliance_checklist.md
- [[Content Accuracy Phase (Phase 2)]] - document - results/rigor_audit/STATUS.md
- [[Cross-Document Consistency Audit (1212 core values consistent)]] - document - results/rigor_audit/06_cross_doc_consistency.md
- [[Data Leakage Audit (77 checks pass, no leakage)]] - document - results/rigor_audit/07_leakage_audit.md
- [[Default Hyperparameters Are Conservative, Not Cherry-Picked]] - document - results/rigor_audit/11_hyperparam_sensitivity.md
- [[EEGNet Not in Validation Loop Disclosure]] - document - results/rigor_audit/05_defensibility.md
- [[Epoch-Level PAC Granularity Caveat (82% same-epoch pairs)]] - document - results/rigor_audit/07_leakage_audit.md
- [[Feature Ablation Validation (pac_stim  pac  all  spectral confirmed)]] - document - results/rigor_audit/09_feature_validation.md
- [[Feature Selection Impact 5x Larger Than Hyperparameter Sensitivity Range]] - document - results/rigor_audit/11_hyperparam_sensitivity.md
- [[Figure and Visual Compliance Audit]] - document - results/rigor_audit/03_figure_audit.md
- [[Font Compliance Audit]] - document - results/rigor_audit/02_font_audit.md
- [[GRU Model (test R2=0.633, high variance)]] - document - results/rigor_audit/10_architecture_exploration.md
- [[Hidden Size Sweep (h=16-128, R2=0.341-0.610, all beat persistence)]] - document - results/rigor_audit/11_hyperparam_sensitivity.md
- [[Hyperparameter Sensitivity Audit (ROBUST verdict)]] - document - results/rigor_audit/11_hyperparam_sensitivity.md
- [[Hysteresis Value Discrepancy (5s in codepresentation vs 3s in paper)]] - document - results/rigor_audit/04_content_accuracy.md
- [[LightTransformer Model (test R2=0.651, best performer)]] - document - results/rigor_audit/10_architecture_exploration.md
- [[Model Architecture Deep Dive Phase (Phase 3)]] - document - results/rigor_audit/STATUS.md
- [[MultiscaleCausalTCN Architecture Baseline (R2=0.606, deployment advantages)]] - document - results/rigor_audit/10_architecture_exploration.md
- [[MultiscaleCausalTCN Reproducibility Audit (3 new seeds)]] - document - results/rigor_audit/08_reproducibility.md
- [[Must Fix Update System Architecture Figure Before CSEF]] - document - results/rigor_audit/SYNTHESIS.md
- [[Number-by-Number Content Accuracy Verification (6667 pass)]] - document - results/rigor_audit/04_content_accuracy.md
- [[Offline Counterfactual Replay Limitation Disclosure]] - document - results/rigor_audit/05_defensibility.md
- [[PAC Feature Circular Leakage Check (pac_current R2=0.104, matches persistence)]] - document - results/rigor_audit/07_leakage_audit.md
- [[PAC+Stim 12-Feature Subset (test R2=0.568, validated match)]] - document - results/rigor_audit/09_feature_validation.md
- [[Page Count and Section Structure Requirements (12 pages, 8 sections)]] - document - results/rigor_audit/01_compliance_checklist.md
- [[Permutation Test (shuffled R2=-0.004 vs real R2=0.734, genuine signal confirmed)]] - document - results/rigor_audit/07_leakage_audit.md
- [[Project Summary Word Count Check (142 words, under 150 limit)]] - document - results/rigor_audit/01_compliance_checklist.md
- [[RESULTS_REPORT.md Still Describes 73-Feature Model Issue]] - document - results/rigor_audit/06_cross_doc_consistency.md
- [[Rigor Audit Status Overview]] - document - results/rigor_audit/STATUS.md
- [[Rigor Audit Synthesis (HIGH overall confidence, results genuine and reproducible)]] - document - results/rigor_audit/SYNTHESIS.md
- [[Scientific Defensibility Audit (STRONG rating)]] - document - results/rigor_audit/05_defensibility.md
- [[Should Fix Hysteresis Value in Research Paper (3s → 5s)]] - document - results/rigor_audit/SYNTHESIS.md
- [[Spectral Features Uninformative for PAC Forecasting (test R2=-0.510)]] - document - results/rigor_audit/09_feature_validation.md
- [[Stimulation Context Boosts PAC Prediction (+0.230 R2 from pac to pac_stim)]] - document - results/rigor_audit/09_feature_validation.md
- [[Subject-Level Split Disjointness Check (0 overlap across trainvaltest)]] - document - results/rigor_audit/07_leakage_audit.md
- [[System Architecture Figure Outdated Specs Warning (73-feat31K shown vs 12-feat22914)]] - document - results/rigor_audit/03_figure_audit.md
- [[TCN Deployment Rationale (causal architecture, parallel inference, fixed receptive field)]] - document - results/rigor_audit/10_architecture_exploration.md
- [[Temporal Causality Check (target_idx - end_idx == 5, 0 violations)]] - document - results/rigor_audit/07_leakage_audit.md
- [[Tier 1 Architecture Equivalence (TransformerGRUTCN all R2~0.61-0.65, feature selection dominates)]] - document - results/rigor_audit/10_architecture_exploration.md
- [[Times New Roman Font Warning]] - document - results/rigor_audit/02_font_audit.md
- [[XGBoost Subject-Specific Overfitting (val-test gap=0.323, trees fail to generalize)]] - document - results/rigor_audit/10_architecture_exploration.md
- [[Z-Score Scalers Fit on Train Only Verification]] - document - results/rigor_audit/07_leakage_audit.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Rigor_Audit_Reports
SORT file.name ASC
```
