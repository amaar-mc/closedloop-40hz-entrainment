---
type: community
members: 41
---

# Generalization-Gap Experiments

**Members:** 41 nodes

## Members

- [[12 PAC+Stim Features (indices 61-72)]] - code - archive/experimental/sliding_pac/build_original_12feat.py
- [[Approaches That Did NOT Work (architecture, mixup, heavy-reg on all 73)]] - document - archive/experimental/FINDINGS.md
- [[Architecture Search on PAC+Stim Features (8 configs)]] - code - archive/experimental/run_pac_stim_focused.py
- [[Best Combination Experiments (run_best_combo.py)]] - code - archive/experimental/run_best_combo.py
- [[Build Original 12-Feature Dataset (build_original_12feat.py)]] - code - archive/experimental/sliding_pac/build_original_12feat.py
- [[Build Sliding-PAC Temporal Dataset (build_sliding_dataset.py)]] - code - archive/experimental/sliding_pac/build_sliding_dataset.py
- [[Causal PAC Multiscale Feature Extractor (MA24816, diff14)]] - code - archive/experimental/sliding_pac/build_sliding_dataset.py
- [[CausalConvBlock (residual depthwise-separable causal conv)]] - code - archive/experimental/run_experiments.py
- [[Contiguous Window Stitching for Continuous EEG Signal]] - code - archive/experimental/sliding_pac/compute_sliding_pac.py
- [[Cross-Epoch Transition Analysis (hard prediction samples)]] - code - archive/experimental/sliding_pac/train_and_compare.py
- [[Dataset Rebuild with Target Smooth Windows (ts=1358)]] - code - archive/experimental/run_target_smoothing.py
- [[Epoch-Level PAC Caveat 82.2% Same-Epoch Samples]] - document - archive/experimental/AUDIT_AND_REPORT.md
- [[Epoch-Level vs Sliding-PAC TCN Comparison (train_and_compare.py)]] - code - archive/experimental/sliding_pac/train_and_compare.py
- [[FINDINGS Spectral Features Cause Catastrophic Generalization Failure]] - document - archive/experimental/FINDINGS.md
- [[Feature Ablation Table (6 subsets all→-0.025, pac_stim→0.558)]] - document - archive/experimental/FINDINGS.md
- [[Feature Subset Ablation Study]] - code - archive/experimental/run_generalization.py
- [[Finding Epoch-Level TCN R²=0.554, Sliding-PAC TCN R²=0.212]] - document - archive/experimental/sliding_pac/RESULTS.md
- [[Finding Persistence R²=-0.897 on Sliding PAC (vs 0.104 epoch PAC)]] - document - archive/experimental/sliding_pac/RESULTS.md
- [[Generalization Gap Experiments (run_generalization.py)]] - code - archive/experimental/run_generalization.py
- [[ImprovedTCN Architecture (6338 params, 12-feature input)]] - document - archive/experimental/AUDIT_AND_REPORT.md
- [[ImprovedTCN Model (configurable dilated causal TCN with attention pooling)]] - code - archive/experimental/run_experiments.py
- [[Known Bug Stim Context hop_sec Mismatch (1s vs 2s window)]] - document - archive/experimental/AUDIT_AND_REPORT.md
- [[ML Experiment Framework (run_experiments.py)]] - code - archive/experimental/run_experiments.py
- [[MixupSeqDataset (mixup augmentation for EEG sequences)]] - code - archive/experimental/run_generalization.py
- [[Multi-Seed Robustness Evaluation (5 seeds on best TCN config)]] - code - archive/experimental/run_best_combo.py
- [[PAC+Stim Feature Discovery Audit Report]] - document - archive/experimental/AUDIT_AND_REPORT.md
- [[PAC+Stim Focused Experiments (run_pac_stim_focused.py)]] - code - archive/experimental/run_pac_stim_focused.py
- [[Per-Subject Persistence and Model Analysis]] - code - archive/experimental/run_generalization.py
- [[Persistence Baseline (predict future PAC = current PAC)]] - code - archive/experimental/run_experiments.py
- [[Rationale Spectral Features Cause Subject-Specific Overfitting]] - document - archive/experimental/AUDIT_AND_REPORT.md
- [[Ridge Baseline (flat and enhanced summary features)]] - code - archive/experimental/run_experiments.py
- [[Sliding-Window PAC Computation (compute_sliding_pac.py)]] - code - archive/experimental/sliding_pac/compute_sliding_pac.py
- [[Sliding-Window PAC Experiment Results (RESULTS.md)]] - document - archive/experimental/sliding_pac/RESULTS.md
- [[SplitData Dataclass (x_seq, y_future, y_delta, last_pac, subjects)]] - code - archive/experimental/run_experiments.py
- [[Stim Context Feature Builder from BIDS Events]] - code - archive/experimental/sliding_pac/build_sliding_dataset.py
- [[Target Smoothing + PAC+Stim Best R²=0.793 (ts=5, h=64)]] - document - archive/experimental/FINDINGS.md
- [[Target Smoothing Experiment (run_target_smoothing.py)]] - code - archive/experimental/run_target_smoothing.py
- [[TinyTCN (minimalist 2-block causal TCN)]] - code - archive/experimental/run_generalization.py
- [[Tort Modulation Index (Causal Sliding Window)]] - code - archive/experimental/sliding_pac/compute_sliding_pac.py
- [[Train-Only Re-normalization of 12-Feature Subset]] - code - archive/experimental/sliding_pac/build_original_12feat.py
- [[TransformerPredictor (causal encoder, sequence-to-scalar)]] - code - archive/experimental/run_experiments.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Generalization-Gap_Experiments
SORT file.name ASC
```
