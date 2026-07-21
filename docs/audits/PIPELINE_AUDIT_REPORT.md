# Pipeline Audit Report: Multiscale Causal TCN (ts5_clean)

**Date:** 2026-02-18
**Auditor:** Claude ML Auditor (Opus 4.6)
**Scope:** Full audit of `temporal_multiscale/` pipeline, trained model `best_multiscale_tcn_lb20_hz1_ts5_audit.pth`

---

## Executive Summary

The pipeline is **technically clean** -- no data leakage, no subject contamination, no normalization bugs. The code is well-structured and the audit scripts are thorough. However, the headline R^2 = 0.74 is **misleading without context**, and the model **does not outperform the trivial persistence baseline** (R^2 = 0.76). The high R^2 reflects PAC autocorrelation amplified by target smoothing, not learned EEG intelligence.

---

## Category 1: Data Leakage

### 1.1 Subject Leakage — PASS

- `data_loader.py:565-631`: Splits by subject with `np.unique(subject_ids)`, shuffled with seed 42.
- `comprehensive_audit_multiscale_ts5_clean.json`: Subject overlap = `[]` across all split pairs.
- 24 train / 5 val / 6 test subjects, zero intersection.
- Subject IDs are stored in metadata only, never passed as model features.

### 1.2 Temporal Leakage (Future Information) — PASS

- `build_multiscale_dataset.py:233`: Loop `for t in range(lookback - 1, len(subj_pac) - horizon)` guarantees `target_idx = t + horizon > end_idx = t`.
- Verified: `audit_multiscale_pipeline.py` confirms `target_idx > end_idx` for all 16,583 samples across all splits.
- Moving averages (`_causal_moving_average`): trailing windows only, `lo = max(0, i - window + 1)`.
- Stimulation context: uses `t >= onset` (past/present events only), `time_since_switch` is backward-looking.
- PAC diff features: `diff1[1:] = pac[1:] - pac[:-1]`, `diff4[4:] = pac[4:] - pac[:-4]` — strictly causal.

### 1.3 Normalization Leakage — PASS

- `build_multiscale_dataset.py:268-301` (`_normalize_with_train_stats`): Scalers computed from `train_split` only.
- Feature mean/std, y_future mean/std, y_delta mean/std all derived from train arrays.
- `apply()` function applies these scalers to all three splits identically.
- Grep for `.fit_transform(` on combined data: none found in `temporal_multiscale/`. All `.fit()` calls in the active codebase are on train data only.
- Val/test normalized feature means are 0.2088/0.2719 (correctly nonzero, confirming train-only scalers).

### 1.4 Feature Leakage — PASS (with major caveat)

- Spectral caches are computed per-split from each split's own windows (`temporal/temporal_dataset.py:260-264`). No cross-split feature extraction.
- PAC history features are causal: the model sees `pac_current` at time `t` and predicts `pac_future` at `t+1`.
- **CAVEAT**: This is technically clean but functionally equivalent to giving the model the answer. PAC autocorrelation at lag=1 (1-second horizon with 5-step smoothing) is extremely high. See Category 3.

### 1.5 Augmentation Leakage — PASS (N/A)

- No augmentation applied in the multiscale TCN pipeline. Data is loaded directly from pre-built `.npz` files.

---

## Category 2: Results Integrity

### 2.1 Are Reported Metrics Real? — PASS

- R^2 formula in `train_multiscale_tcn.py:51-54`: `1.0 - ss_res / (ss_tot + 1e-12)` — standard and correct.
- Evaluation function (`evaluate`, lines 129-172): denormalizes predictions via `y_norm * std + mean` before computing metrics. R^2 is computed in raw PAC space.
- `summary_multiscale_tcn_lb20_hz1_ts5_audit.json` reports test R^2 = 0.7423, matching console output.
- `deployment_audit_multiscale_ts5_clean.json` independently reproduces the same R^2 = 0.7423.

### 2.2 Are Metrics Computed Correctly? — PASS

- R^2 formula is correct (not clamped, allows negative values — confirmed by `pac_zeroed` R^2 = 0.046 and shuffle R^2 = -0.33).
- Correlation is computed separately via `np.corrcoef` — not confused with R^2.
- Metrics are computed on **denormalized** targets, which is the correct practice.

### 2.3 Baseline Comparisons — FAIL (CRITICAL)

| Method                                 | Test R^2   | Test Correlation |
| -------------------------------------- | ---------- | ---------------- |
| **Persistence (y_future = y_current)** | **0.7600** | **0.8799**       |
| **Ridge on all features (linear)**     | **0.8120** | **0.9056**       |
| Ridge on PAC features only             | 0.8589     | 0.9270           |
| **MultiscaleCausalTCN (31K params)**   | **0.7423** | **0.8751**       |
| Ridge on spectral features only        | 0.0551     | 0.5201           |
| Ridge on non-PAC features              | 0.0446     | 0.5196           |

**The neural network (R^2 = 0.7423) DOES NOT BEAT the persistence baseline (R^2 = 0.7600).**
A simple linear Ridge model on the same features (R^2 = 0.8120) outperforms both.

The 31,043-parameter TCN adds no value over "predict that future PAC equals current PAC." The nonlinear capacity of the network is not being utilized — in fact it slightly hurts performance compared to the linear model, likely due to overfitting on the 11,256 training samples.

### 2.4 Overfitting Detection — PASS (marginal)

- Best val R^2 = 0.7635, test R^2 = 0.7423. Gap of 0.02 is small.
- Model is selected on val_future_r2 (line 320), not test. No test set contamination.
- Early stopping triggered at epoch 24 (patience=10). Best epoch was 14.
- Train loss continues declining (0.47 → 0.16) while val R^2 plateaus — mild overfitting.

---

## Category 3: Suspicious Patterns

### 3.1 Too-Good-To-Be-True — CONFIRMED SUSPICIOUS

The headline R^2 = 0.74 is misleading for three reasons:

1. **Target smoothing inflates predictability.** `target_smooth_window=5` applies a 5-step causal moving average to PAC before defining targets. This removes high-frequency noise, making future values more similar to current values. Without smoothing (`ts=1`), test R^2 drops to **~0.07**.

2. **The prediction horizon is trivially short.** `horizon=1` means predicting 1 second ahead (1 hop). With 5-step smoothing, the target at t+1 shares 4 of 5 data points with the current smoothed value. This is near-trivial temporal persistence, not meaningful forecasting.

3. **PAC autocorrelation does all the work.** The persistence baseline (R^2 = 0.76) demonstrates that simply predicting "PAC won't change" is already highly accurate under these conditions.

### 3.2 Performance Cliff Under Ablation — CONFIRMED

- PAC-zeroed: R^2 drops from 0.74 to **0.05** (93% collapse)
- Without PAC history, the model learns almost nothing from spectral/context features.
- The model is a **fancy autoregressive wrapper around PAC autocorrelation**.
- It adds NEGATIVE value vs. the persistence baseline.

### 3.3 Subject-Level Variance — NOT AUDITED

- No per-subject R^2 breakdown is available in the outputs.
- The aggregate R^2 = 0.74 could mask wide subject-level variation.

### 3.4 Distribution Mismatch — LOW RISK

- Val/test feature means are shifted from zero (0.21/0.27) — expected with train-only normalization.
- No anomalous values detected in the finite checks.

---

## Category 4: Code Integrity

### 4.1 Silent Failures — SUSPECT (minor)

- `src/utils.py:424`: Bare `except:` in `print_model_summary` (wraps `torchsummary` — cosmetic only).
- `src/data_loader.py:224,237,328`: Bare `except Exception:` in data loading fallbacks. These log at debug level but could silently skip corrupted subjects.
- The `temporal_multiscale/` code has no bare excepts — clean.

### 4.2 Randomness and Reproducibility — FAIL

- **No random seeds set in `temporal_multiscale/train_multiscale_tcn.py`.** No calls to `np.random.seed`, `torch.manual_seed`, or `torch.cuda.manual_seed`.
- `DataLoader(shuffle=True)` without a worker seed.
- Results will vary across runs. The reported R^2 = 0.7423 is one draw from a distribution of possible outcomes.
- This is a **reproducibility failure** for a research submission.

### 4.3 Numerical Precision — PASS

- PAC values (0.0002–0.0046) are z-score normalized before entering the loss function.
- After normalization, targets are in standard N(0,1) range — numerically stable for float32.
- The `1e-8` added to std in normalization prevents division by zero.
- The `1e-12` in R^2 denominator prevents pathological cases.

### 4.4 Dead Code — NOTE

- Multiple unused model architectures: `eegnet_v2.py`, `spectempnet.py`, `vit_tcnet.py`, `training_v2.py`.
- Large `archive/` directory with v1–v8 experiment attempts.
- These don't affect correctness but add confusion about which code is "real."

---

## Category 5: Deployment Realism

### 5.1 Closed-Loop Feasibility — PASS (simulation only)

- Inference latency ~1ms is well within the 1 Hz decision budget.
- The threshold controller (`controller.py`) is simple and fast.
- However, the brain response model in `simulator.py` is a first-order exponential approach to a fixed point — far from realistic neurobiology.

### 5.2 Oracle Dependency — FAIL (CRITICAL)

The model requires **accurate PAC history** as input features. In a real closed-loop:

1. Raw EEG is acquired in real-time.
2. PAC must be estimated from raw EEG (which requires ~20-40 seconds of data for stable Modulation Index — see `extract_stimulus_windows` in `data_loader.py:399-405`, which uses the full epoch).
3. The estimated PAC is fed as input to the TCN.
4. The TCN predicts future PAC.

**Problem:** Step 2 produces noisy PAC estimates from short windows. The deployment audit shows:

- sigma=0.5 noise → R^2 drops from 0.74 to 0.68
- sigma=1.0 noise → R^2 drops to 0.52

Real-time PAC estimation noise is likely sigma > 1.0 in normalized space, given that 2-second window PAC estimates are extremely noisy (the codebase itself acknowledges this by computing PAC from 20-40 second epochs, not 2-second windows). This means **deployed performance would likely collapse below the persistence baseline**.

### 5.3 The Hard Question — SUSPECT

The model does not beat persistence (R^2 = 0.76 > 0.74). A fixed-schedule controller (40s on, 20s off) requires zero ML infrastructure. The question becomes: **does the entire ML pipeline add value over just continuing whatever you're currently doing?**

The answer from this data is: **no, not yet.** The TCN adds negative marginal value over persistence, and the Ridge model (which does beat persistence) requires the same PAC oracle dependency.

---

## Summary Table

| Category               | Verdict     | Critical Issues                                                   |
| ---------------------- | ----------- | ----------------------------------------------------------------- |
| 1. Data Leakage        | **PASS**    | No leakage detected across all vectors                            |
| 2. Results Integrity   | **FAIL**    | TCN (R^2=0.74) does NOT beat persistence (R^2=0.76)               |
| 3. Suspicious Patterns | **FAIL**    | R^2 inflated by target smoothing; model is autoregressive wrapper |
| 4. Code Integrity      | **SUSPECT** | No random seeds → not reproducible                                |
| 5. Deployment Realism  | **FAIL**    | PAC oracle dependency makes real-time deployment unrealistic      |

---

## CRITICAL FAILURES

1. **The TCN does not beat the persistence baseline.** Persistence R^2 = 0.7600 vs. TCN R^2 = 0.7423. The 31,043-parameter neural network adds NEGATIVE value over "predict that nothing changes." A simple Ridge regression (R^2 = 0.81) does beat persistence, but the TCN does not.

2. **The headline R^2 = 0.74 is meaningless without disclosing that (a) the target is smoothed (ts=5), (b) the horizon is 1 second, and (c) persistence alone gets 0.76.** Reporting "R^2 = 0.74" without this context would be misleading in any research submission.

3. **PAC oracle dependency.** The model collapses to R^2 = 0.05 without PAC input features. In real deployment, PAC must be estimated online with significant noise, likely degrading performance below usefulness.

4. **No random seed set.** Results are not reproducible. Different runs will produce different R^2 values.

## WARNINGS

1. **Target smoothing creates false confidence.** Unsmoothed R^2 is ~0.07 (essentially random). The smoothing window of 5 shares 4/5 data points between adjacent targets, making prediction artificially easy.

2. **No per-subject metrics.** The aggregate hides potential per-subject failures.

3. **Ridge outperforms the neural network.** If a linear model on the same features gets R^2 = 0.81 and the TCN gets 0.74, the nonlinear model is overfitting or undersized. The complexity is not justified.

4. **The ill-conditioned matrix warnings** in Ridge indicate multicollinearity among the 73 features — some features are redundant.

## NOTES

- The audit infrastructure is well-designed. The shuffle-label sanity test, temporal causality checks, and PAC-zeroed ablation are exactly the right things to check.
- The codebase is clean, well-documented, and modular.
- The honest finding is that **PAC temporal prediction from this dataset is fundamentally hard** (R^2 ~0.07 for raw targets), and target smoothing creates an illusion of predictability. This is a data limitation, not a code bug — but it must be clearly communicated.
