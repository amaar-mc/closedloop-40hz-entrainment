# Code Map: Repository Organization & Approach History

**Last Updated:** 2026-02-18

This document catalogs every code file in the repository, organized by module and approach. It explains what each file does, whether it's actively used, and how the different approaches relate to each other.

---

## Timeline of Approaches

```
Phase 1: Static PAC Prediction (V1-V8)     Feb 5-16, 2026
  V1  EEGNet baseline                      R² = 0.69 (LEAKED - MI features)
  V2  EEGNetV2 + ΔPAC                      R² = 0.06 (failed)
  V3  SpecTempNet (spectral-temporal)       R² = 0.69 → 0.236 (clean)
  V4  ViT-TCNet (1.1M params)              R² = 0.252 (overfit)
  V5  Ridge/Lasso/Ensemble baselines        R² = 0.287 ← BEST STATIC
  V6  Optimized ensemble + temporal feats   R² = 0.287 (no gain)
  V7  Raw EEG deep learning (CNN/Attn)      R² = 0.28
  V8  EEGNet/ATCNet/TransformEEG            R² = 0.22

Phase 2: Temporal PAC Prediction            Feb 16-17, 2026
  Temporal LSTM (2s windows, 5s ahead)      R² = -0.05 (failed)
  8s windows reprocessing                   autocorr r=0.45
  Temporal MLP (8s windows, 8s ahead)       R² = 0.125
  Temporal Ridge (8s windows)               R² = -0.21

Phase 3: Multiscale Causal TCN              Feb 17, 2026
  Causal TCN (smoothed targets, ts=5)       R² = 0.7423 (test)
  BUT: Persistence baseline                 R² = 0.7600 (beats TCN)
  AND: Ridge on same features               R² = 0.8120 (beats both)
  Raw targets (ts=1)                        R² = ~0.07
```

---

## Active Code (Currently Used)

### `src/` — Core Pipeline

| File                   | Purpose                                                            | Status     | Key Class/Function                                        |
| ---------------------- | ------------------------------------------------------------------ | ---------- | --------------------------------------------------------- |
| `data_loader.py`       | BIDS data loading, HDF5/FDT parsing, windowing, subject splits     | **ACTIVE** | `EEGWindowDataset`, `create_splits()`, `_load_hdf5_set()` |
| `preprocessing.py`     | Light filtering (0.5-80Hz BP, 50Hz notch, CAR, artifact rejection) | **ACTIVE** | `EEGPreprocessor.preprocess()`                            |
| `pac_computation.py`   | Modulation Index (Tort 2010): theta phase x gamma amplitude        | **ACTIVE** | `PACComputer.compute_pac()`                               |
| `eegnet.py`            | EEGNet CNN for static PAC prediction (1,457 params)                | **ACTIVE** | `EEGNet` — input (B,1,7,500) → output (B,1)               |
| `training.py`          | Training loop for EEGNet (MSE, Adam, ReduceLROnPlateau)            | **ACTIVE** | `ModelTrainer.train()`                                    |
| `controller.py`        | Closed-loop decision engine (z-score thresholds + hysteresis)      | **ACTIVE** | `ClosedLoopController.step()`                             |
| `personalization.py`   | Rolling 30s baseline, z-score normalization                        | **ACTIVE** | `PersonalizationModule.compute_zscore()`                  |
| `simulator.py`         | Brain dynamics simulation (exponential PAC approach)               | **ACTIVE** | `EntrainmentSimulator.step()`                             |
| `validation.py`        | Compare 4 strategies: Fixed/Reactive/Predictive/Oracle             | **ACTIVE** | `ValidationFramework`                                     |
| `utils.py`             | Logging, config, metrics (`compute_regression_metrics`), plotting  | **ACTIVE** | Various utilities                                         |
| `spectral_features.py` | 61 spectral features (band power, phase-amplitude, cross-channel)  | **ACTIVE** | `SpectralFeatureExtractor.extract()`                      |

### `temporal_multiscale/` — Latest Temporal Pipeline

| File                                | Purpose                                                                       | Status     | Key Class/Function                 |
| ----------------------------------- | ----------------------------------------------------------------------------- | ---------- | ---------------------------------- |
| `build_multiscale_dataset.py`       | Causal sequence construction (12 PAC+Stim features, lookback=20, horizon=1-5) | **ACTIVE** | `build_multiscale_dataset()`       |
| `multiscale_tcn.py`                 | Causal TCN: depthwise-sep conv, dilation [1,2,4,8], attention pool            | **ACTIVE** | `MultiscaleCausalTCN` (31K params) |
| `train_multiscale_tcn.py`           | Training: Huber + multi-task (future+delta+consistency), early stop           | **ACTIVE** | `train_one_epoch()`, `evaluate()`  |
| `audit_multiscale_pipeline.py`      | Dataset integrity: subject overlap, temporal causality, normalization         | **ACTIVE** | `run_audit()`                      |
| `comprehensive_submission_audit.py` | Ablation tests: Ridge baselines, persistence, shuffle-label sanity            | **ACTIVE** | `run_audit()`                      |
| `checkpoint_deployment_audit.py`    | Robustness: PAC-zeroed, PAC-noisy at sigma [0.1, 0.25, 0.5, 1.0]              | **ACTIVE** | `run_audit()`                      |
| `realtime_inference.py`             | Rolling inference wrapper with causal buffers for closed-loop                 | **ACTIVE** | `RealtimePACForecaster.step()`     |
| `sweep_multiscale_configs.py`       | Hyperparameter sweep over lookback:horizon pairs                              | **ACTIVE** | CLI orchestrator                   |
| `README.md`                         | Quick-start guide and hyperparameter recommendations                          | **ACTIVE** | Documentation                      |

---

## Experimental Code (Implemented but Not in Main Pipeline)

### `src/` — Alternative Architectures

| File                   | Purpose                                                                    | Status           | Params | Best R²       |
| ---------------------- | -------------------------------------------------------------------------- | ---------------- | ------ | ------------- |
| `eegnet_v2.py`         | Enhanced EEGNet for ΔPAC prediction (F1=12, F2=24, hidden FC)              | **EXPERIMENTAL** | ~3,200 | 0.06          |
| `spectempnet.py`       | Multi-scale temporal CNN + spectral branch + 4-head attention              | **ABANDONED**    | ~180K  | 0.236 (clean) |
| `vit_tcnet.py`         | ViT encoder (EEG→pseudo-image) + TCN decoder + SE attention                | **ABANDONED**    | ~1.1M  | 0.252         |
| `training_v2.py`       | Enhanced trainer (Huber loss, cosine annealing, R²-based early stop)       | **EXPERIMENTAL** | —      | —             |
| `data_loader_v2.py`    | Paired-window loader for ΔPAC with built-in augmentation                   | **EXPERIMENTAL** | —      | —             |
| `data_augmentation.py` | EEG augmentation: time warp, magnitude warp, shift, noise, channel dropout | **OPTIONAL**     | —      | —             |
| `wavelet_features.py`  | 74 CWT + WPD features (used by ViT-TCNet)                                  | **IMPLEMENTED**  | —      | —             |
| `pac_features.py`      | 116 direct PAC features (MI, PLV, coupling profile)                        | **UNUSED**       | —      | —             |

### `temporal/` — Earlier Temporal Approaches

| File                             | Purpose                                                       | Status         | Best R² |
| -------------------------------- | ------------------------------------------------------------- | -------------- | ------- |
| `temporal_dataset.py`            | Sequence construction for LSTM (lookback=10, horizon=5)       | **SUPERSEDED** | —       |
| `temporal_model.py`              | SpatialEncoder + Bidirectional LSTM/GRU + multi-horizon heads | **SUPERSEDED** | -0.05   |
| `train_temporal.py`              | LSTM training: HuberLoss, CosineAnnealing, gradient clip      | **SUPERSEDED** | -0.05   |
| `reprocess_long_windows.py`      | Reprocess ds005048 with 8s windows (2000 samples, 4s hop)     | **SUPERSEDED** | —       |
| `train_temporal_long_windows.py` | Train on 8s windows (lookback=5, horizon=2)                   | **SUPERSEDED** | —       |
| `train_sklearn_temporal.py`      | Ridge + MLP baselines on 8s temporal sequences                | **SUPERSEDED** | 0.125   |
| `validate_code.py`               | Pre-training audit: leakage, autocorrelation, Ridge baseline  | **USEFUL**     | —       |

---

## Archived Code (`archive/`)

### `archive/v1_v8_attempts/` — Static PAC Training Scripts

| File                        | Version | Approach                                 | Result          | Why Archived                                |
| --------------------------- | ------- | ---------------------------------------- | --------------- | ------------------------------------------- |
| `run_training_v2.py`        | V2      | EEGNetV2 + ΔPAC training launcher        | R² = 0.06       | ΔPAC prediction failed (predicting noise)   |
| `run_training_v3.py`        | V3      | SpecTempNet with spectral features       | R² = 0.69/0.236 | MI leakage inflated results                 |
| `run_training_v4.py`        | V4      | ViT-TCNet training with wavelet features | R² = 0.252      | 1.1M params overfit on 11K samples          |
| `run_v6_optimized.py`       | V6      | Optimized ensemble + temporal context    | R² = 0.287      | No improvement over Ridge alone             |
| `run_v7_raw_eeg_models.py`  | V7      | 1D CNN + Attention + Hybrid on raw EEG   | R² = 0.28       | No advantage over handcrafted features      |
| `run_v8_specialized_eeg.py` | V8      | EEGNet/ATCNet/TransformEEG               | R² = 0.22       | All underperformed Ridge                    |
| `run_enhanced_features.py`  | V5+     | Ridge with PAC features (leakage test)   | R² = 0.9999     | Confirmed PAC features = circular reasoning |
| `run_simple_baselines.py`   | V5      | Ridge/Lasso/ElasticNet/RF/GBM            | R² = 0.287      | Winner! Moved to production                 |

### `archive/diagnostics/` — Debugging & Leakage Detection

| File                       | Purpose                                                     |
| -------------------------- | ----------------------------------------------------------- |
| `audit_leakage.py`         | Detected MI features leaking target PAC (correlation > 0.7) |
| `debug_leakage.py`         | Coefficient analysis: PAC features = 96.6% of Ridge weight  |
| `diagnostic_analysis.py`   | Feature quality checks: correlation, variance, NaN/Inf      |
| `pure_numpy_diagnostic.py` | V4 failure analysis: overparameterization, SNR = -4.73 dB   |
| `simple_diagnostic.py`     | Basic feature correlation and model complexity analysis     |

### `archive/docs_v1_v8/` — Historical Documentation

| File                            | Purpose                                                  |
| ------------------------------- | -------------------------------------------------------- |
| `ARCHITECTURE_V3_DESIGN.md`     | SpecTempNet design rationale                             |
| `AUDIT_REPORT.md`               | V3 audit revealing MI leakage                            |
| `FINAL_ASSESSMENT.md`           | Honest evaluation: R² = 0.287 is the ceiling             |
| `FINAL_VERDICT_MASTER_MODEL.md` | Why "one master model" won't work                        |
| `IMPROVEMENT_PLAN.md`           | Phase-based plan (targets never achieved)                |
| `IMPROVEMENTS_V2_SUMMARY.md`    | V2 ΔPAC improvements (didn't work)                       |
| `V3_CLEAN_NO_MI.md`             | Guide to removing MI features                            |
| `V3_IMPLEMENTATION_SUMMARY.md`  | SpecTempNet implementation details                       |
| `V4_FAILURE_ANALYSIS.md`        | Post-mortem: overparameterization + no transfer learning |
| `V4_VIT_TCNET.md`               | V4 design document                                       |

---

## Top-Level Documentation

| File                                     | Purpose                                                  | Status           |
| ---------------------------------------- | -------------------------------------------------------- | ---------------- |
| `CLAUDE.md`                              | Project instructions for Claude Code                     | **CURRENT**      |
| `AGENTS.md`                              | Repository guidelines, structure, commit style           | **CURRENT**      |
| `README.md`                              | Main project documentation (some metrics outdated)       | **NEEDS UPDATE** |
| `config.yaml`                            | Centralized runtime parameters                           | **CURRENT**      |
| `COMPREHENSIVE_ANALYSIS_ALL_ATTEMPTS.md` | Retrospective of V1-V8 (static R² = 0.287 ceiling)       | **HISTORICAL**   |
| `LAB_NOTEBOOK_MASTER_COMPLETE.txt`       | Master lab notebook Dec 2025 - Feb 2026                  | **HISTORICAL**   |
| `SUMMARY_FOR_USER.md`                    | Executive summary of 8s window investigation             | **HISTORICAL**   |
| `TEMPORAL_PREDICTION_FINAL_REPORT.md`    | Why temporal prediction failed with 2s/8s windows        | **HISTORICAL**   |
| `TEMPORAL_PREDICTION_REPORT.md`          | Initial LSTM investigation, zero autocorrelation finding | **HISTORICAL**   |

---

## Feature Engineering Summary

| Feature Set                   | Dimensions                                | Source File                   | Used By                                |
| ----------------------------- | ----------------------------------------- | ----------------------------- | -------------------------------------- |
| Raw EEG windows               | (1, 7, 500)                               | `data_loader.py`              | EEGNet, V7/V8 models                   |
| Spectral features             | 61                                        | `spectral_features.py`        | SpecTempNet, Ridge, TCN                |
| Wavelet features              | 74                                        | `wavelet_features.py`         | ViT-TCNet only                         |
| PAC features                  | 116                                       | `pac_features.py`             | Never used (circular)                  |
| Multiscale temporal (current) | 12 (7 PAC-derived + 5 stim context)       | `build_multiscale_dataset.py` | MultiscaleCausalTCN                    |
| Multiscale temporal (initial) | 73 (61 spectral + 7 PAC-derived + 5 stim) | `build_multiscale_dataset.py` | Deprecated — spectral features overfit |

---

## Model Zoo

| Model               | File                                    | Params | Input                  | Best R²  | Notes                            |
| ------------------- | --------------------------------------- | ------ | ---------------------- | -------- | -------------------------------- |
| EEGNet              | `src/eegnet.py`                         | 1,457  | (B,1,7,500)            | 0.287    | Active; static PAC               |
| EEGNetV2            | `src/eegnet_v2.py`                      | 3,200  | (B,1,7,500)            | 0.06     | ΔPAC; failed                     |
| SpecTempNet         | `src/spectempnet.py`                    | 180K   | EEG + 61 spectral      | 0.236    | Clean; abandoned                 |
| ViT-TCNet           | `src/vit_tcnet.py`                      | 1.1M   | EEG + 61 spec + 74 wav | 0.252    | Overfit; abandoned               |
| SpatialEncoder+LSTM | `temporal/temporal_model.py`            | 85K    | Sequence of (7,500)    | -0.05    | Failed                           |
| MultiscaleCausalTCN | `temporal_multiscale/multiscale_tcn.py` | 31K    | (B,20,73)              | 0.7423\* | \*ts=5, doesn't beat persistence |
| Ridge Regression    | sklearn (various scripts)               | ~200   | 61 spectral            | 0.287    | Best static model                |
| Ridge (temporal)    | `comprehensive_submission_audit.py`     | ~73    | 73 multiscale          | 0.8120\* | \*ts=5, beats TCN                |

---

## What Each R² Actually Means

| Claim                         | Context                                            | Honest Interpretation                                       |
| ----------------------------- | -------------------------------------------------- | ----------------------------------------------------------- |
| R² = 0.287 (EEGNet/Ridge)     | Static: current EEG → current PAC                  | Genuine prediction from spectral features                   |
| R² = 0.7423 (TCN, ts=5)       | Temporal: 20s history → 1s ahead, smoothed targets | Mostly PAC autocorrelation; doesn't beat persistence (0.76) |
| R² = 0.8120 (Ridge, ts=5)     | Linear model on same 73 features                   | Same autocorrelation, linear is enough                      |
| R² = ~0.07 (TCN, ts=1)        | Raw targets, no smoothing                          | True temporal prediction ability                            |
| R² = 0.125 (MLP, 8s windows)  | 8s windows, 8s ahead                               | Modest; still below static baseline                         |
| R² = -0.05 (LSTM, 2s windows) | 2s windows, 5s ahead                               | Failed; zero autocorrelation at 2s scale                    |
