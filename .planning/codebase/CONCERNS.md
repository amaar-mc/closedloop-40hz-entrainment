# Codebase Concerns

**Analysis Date:** 2026-02-26

## Tech Debt

### Static PAC Prediction Ceiling at R² ≈ 0.287

**Issue:** EEGNet model performance has plateaued despite 8 architectural iterations (V1-V8). Current R² = 0.287 on held-out test subjects represents a hard ceiling for predicting PAC from 7 frontal EEG channels.

**Files:** `src/eegnet.py`, `src/training.py`, `archive/v1_v8_attempts/` (all 8 variants)

**Impact:** Any future enhancements to the static PAC predictor (better architectures, additional preprocessing, data augmentation) are unlikely to yield significant improvements. The limitation is fundamental to the input signal's information content rather than model capacity. All deep learning variants (SpecTempNet 0.236, ViT-TCNet 0.252, ATCNet 0.22) converged below or equal to simple Ridge baseline (0.287).

**Fix approach:** Accept 0.287 as operationally unavoidable and focus on temporal prediction (5–10s ahead, where TCN shows +0.5 R² advantage) or alternative input modalities (e.g., subcortical LFP). Do not spend engineering effort on static model improvements.

---

### Multiscale TCN Temporal Advantage Requires Target Smoothing

**Issue:** The MultiscaleCausalTCN achieves R² = 0.7423 at 1s horizon with smoothed targets (`target_smooth_window=5`), but this performance is driven by PAC autocorrelation, not true predictive capability. When evaluated on raw targets (`target_smooth_window=1`), R² drops to ~0.07. Worse: Ridge regression on identical features achieves R² = 0.8120 (beats TCN by 0.07 R²).

**Files:** `temporal_multiscale/build_multiscale_dataset.py` (line 158–179: target smoothing logic), `temporal_multiscale/train_multiscale_tcn.py` (line 75–76: denormalization), `temporal_multiscale/comprehensive_submission_audit.py` (Ridge baseline comparison)

**Impact:** TCN's claimed advantage at 5–10s horizons (used in closed-loop demos) is meaningful (+0.5 R² over baselines). However, all reported results conflate two confounding factors: (1) architectural advantage and (2) target smoothing acting as implicit label smoothing. The honest R² range is 0.07–0.25 depending on smoothing window. This limits applicability to real-time scenarios requiring unsmoothed, causal predictions.

**Fix approach:**
- Document target smoothing window as a critical hyperparameter in config.yaml (currently at line 158 but under-emphasized).
- Always report both `ts=1` (raw, causal) and `ts=5` (smoothed, autocorrelation-heavy) results side-by-side in future papers/results.
- For closed-loop deployment, test with `ts=1` to validate real-time performance.
- Consider online adaptive smoothing (exponential moving average) instead of lookback smoothing to reduce lag.

---

### Spectral Feature Leakage (Resolved but Design Risk Remains)

**Issue:** Early PAC feature engineering (`pac_features.py`) directly computed Modulation Index from EEG, creating circular input-output dependencies. Ridge on PAC features inflated R² to 0.9999. This was detected and removed, but the codebase still has no mechanism to prevent reintroduction of leakage if features are regenerated.

**Files:** `archive/experimental_models/pac_features.py` (never used now), `archive/diagnostics/audit_leakage.py` (detection), `src/spectral_features.py` (safe features, but no validation)

**Impact:** Low risk currently because leakage was caught and `pac_features.py` is archived. However, future feature engineering could accidentally reintroduce MI-derived features. The validation in `temporal/validate_code.py` checks temporal leakage but not feature-target correlation.

**Fix approach:**
- Add correlation check in `src/spectral_features.py` to fail loudly if any feature has r > 0.7 with PAC labels.
- Update `temporal/validate_code.py` to compute feature-target correlation matrix on train split and warn if thresholds are exceeded.
- Document in CLAUDE.md the "safe features" list (theta power, gamma power, cross-frequency coupling where phase is theta but amplitude is not gamma).

---

### Limited Subject Count in Test Set (6 Subjects / 2,822 Windows)

**Issue:** Dataset has 35 subjects total, split 70/15/15 = 24 train, 5 val, 6 test. Test set is only 6 subjects (2,822 windows). This is a very small held-out population for statistical generalization claims. High variance in per-subject R² may mask true model quality.

**Files:** `src/data_loader.py` (lines 450–475: split logic), `config.yaml` (lines 162–167: split ratios)

**Impact:** Reported R² = 0.287 has unknown confidence interval. If one "difficult" test subject drops R² by 0.1 or one "easy" subject inflates it by 0.1, the 6-subject test set cannot detect this. Per-subject R² metrics should be reported alongside aggregate metrics.

**Fix approach:**
- Implement per-subject cross-validation (leave-one-subject-out, LOSO) if computational budget allows (35 folds).
- Report R² with 95% CI or use bootstrap resampling across subjects to estimate uncertainty.
- In `validation.py`, add per-subject breakdown in figure 2 (heatmap of test R² by subject).
- See `temporal_multiscale/per_subject_adaptation.py` for existing per-subject analysis framework.

---

## Known Bugs

### Personalization Module Insufficient Initialization

**Issue:** `PersonalizationModule` in `src/personalization.py` (lines 108–130) requires 10 samples (10 seconds at 1 Hz) before computing z-scores. During early trial, z-score returns None. Controller handles this (line 181: fallback to PAC thresholds), but silent None propagation could mask initialization issues in custom controllers.

**Files:** `src/personalization.py` (lines 83, 121: return None/None), `src/controller.py` (line 181: None check)

**Trigger:** Run any closed-loop demo with fewer than 10 seconds initial data.

**Workaround:** Always initialize EntrainmentSimulator with pre-run period ≥ 10 seconds, or pre-populate baseline in checkpoints.

**Fix approach:**
- Initialize baseline with dataset statistics on first load (mean/std from train split).
- Replace None returns with error raises if z-score computation fails after baseline stabilization (after 30 seconds).

---

### Hardcoded Hysteresis Time Constant

**Issue:** Controller hysteresis is hardcoded to 5 seconds (hold_time_sec) in `src/controller.py` (line 78). While configurable via config.yaml, there is no validation that hold_time is ≥ 1 decision window (1 second at 1 Hz decision rate). If hold_time < 1, state can oscillate within a single decision cycle.

**Files:** `src/controller.py` (line 81: hold_time_sec parameter), `config.yaml` (line 181: hold_time_sec = 5.0)

**Impact:** Minimal in practice (5s is sensible), but silent violation of assumption in docstring. Simulators with `decision_rate_hz > 1.0` could see instability.

**Fix approach:**
- Add assertion in `ClosedLoopController.__init__` (after line 79): `assert hold_time_sec >= 1.0 / decision_rate_hz`.
- Raise ValueError if violated.

---

### Dataset Metadata Mismatch Detection Incomplete

**Issue:** `build_multiscale_dataset.py` enforces metadata consistency (lines 158–180), but only checks if lookback/horizon/smoothing match existing metadata. If someone changes `stim_history_sec` or `n_phase_bins` in config, the script will silently use stale cached spectral features instead of rebuilding.

**Files:** `temporal_multiscale/build_multiscale_dataset.py` (lines 158–180: metadata checking), `config.yaml` (lines 83–84: phase binning config)

**Trigger:** Modify `config.yaml` PAC.n_phase_bins → run `build_multiscale_dataset.py` on existing dataset dir → uses old spectral cache.

**Fix approach:**
- Hash config PAC/windowing settings and include in metadata.json.
- Compare config hash in `_load_spectral_cache()` and error if mismatch (rather than --allow-metadata-mismatch flag).

---

## Security Considerations

### No Input Validation on EEG Data Ranges

**Issue:** EEG data is loaded and preprocessed without explicit range checks beyond artifact rejection (±100 µV threshold). Pathological values (Inf, NaN, extreme values > ±1000 µV) could propagate silently or cause numerical instability in spectral features.

**Files:** `src/data_loader.py` (lines 150–200: loading), `src/preprocessing.py` (lines 263: artifact rejection)

**Current mitigation:** Artifact rejection threshold limits most outliers. PAC computation normalizes by mean amplitude, which could saturate if extreme values present.

**Recommendations:**
- Validate input ranges in `data_loader.py` before windowing: `assert np.all(np.abs(eeg) <= 1000), f"EEG values exceed ±1000 µV"`.
- Add NaN/Inf checks in preprocessing output.
- Log histogram of max absolute values per subject to catch outlier subjects.

---

### Model Checkpoint Serialization Lacks Validation

**Issue:** EEGNet checkpoints are saved via `torch.save()` with no integrity checks. Corrupted checkpoints could load silently with invalid weights. Testing code at `src/eegnet.py` (line 257) is minimal.

**Files:** `src/training.py` (lines 290–310: checkpoint save), `src/controller.py` (lines 90–110: checkpoint load)

**Fix approach:**
- After loading checkpoint, validate model output shape and range on dummy input.
- Use torch.jit.script() or onnx export for production deployment to enforce schema.

---

## Performance Bottlenecks

### Data Loading Inefficiency for Large Datasets

**Issue:** `build_multiscale_dataset.py` loads entire train split into memory (line 39–46), computes spectral features in a loop (lines 204–255). For 11,736 training windows, this creates multiple 11K × 61 arrays in memory and CPU-bound feature computation. No caching of spectral features between runs.

**Files:** `temporal_multiscale/build_multiscale_dataset.py` (lines 39–300: no batch processing)

**Impact:** Dataset building takes ~5–10 minutes on typical hardware. Repeated hyperparameter sweeps (see `sweep_multiscale_configs.py`) require repeated feature computation.

**Improvement path:**
- Cache spectral features to disk (already partially done: `{split}_spectral_cache.npy`).
- Use numpy's memmap for large feature matrices to avoid loading entire arrays.
- Parallelize spectral computation across windows using `multiprocessing.Pool` or `joblib.Parallel`.

---

### Closed-Loop Real-Time Inference Unoptimized

**Issue:** `realtime_inference.py` (`RealtimePACForecaster.step()`) loads EEGNet model on every inference (no lazy loading). At 1 Hz decision rate over 10-minute trial, model is loaded 600 times, each incurring CUDA kernel overhead.

**Files:** `temporal_multiscale/realtime_inference.py` (lines 50–100: step function), `run_closed_loop_demo.py` (line 200–300: demo loop)

**Impact:** Inference latency for closed-loop is ~50 ms per window (acceptable), but could be 10–20 ms with proper batching/caching.

**Improvement path:**
- Pre-load model once in `__init__`, not per-step.
- Consider model quantization (torch.quantization) for 2–3x speedup.
- Add jit.trace() for TorchScript compilation.

---

### No Batch Inference in ValidationFramework

**Issue:** `ValidationFramework` in `src/validation.py` (lines 300–400) runs model inference one window at a time in a tight loop. No batching even though PyTorch can batch 64 samples efficiently.

**Files:** `src/validation.py` (lines 350–380: inference loop)

**Impact:** Validation takes ~2 minutes for 1-hour simulation. Could be 10 seconds with batch inference.

**Improvement path:**
- Buffer 64 consecutive EEG windows, batch infer all 64, unbuffer results.
- Trade 64-window latency (64 seconds of data) for 20x throughput gain on validation.

---

## Fragile Areas

### Temporal Dataset Causality Enforcement Relies on Manual Inspection

**Issue:** `audit_multiscale_pipeline.py` checks no future leakage, but the check is post-hoc auditing. If someone refactors `_stim_context_from_events()` or `_pac_multiscale_features()` without understanding causality, leakage could be reintroduced. No automated gate prevents committing broken code.

**Files:** `temporal_multiscale/build_multiscale_dataset.py` (lines 140–200: feature construction), `temporal_multiscale/audit_multiscale_pipeline.py` (lines 50–150: validation)

**Why fragile:** Dataset logic is low-level numpy (cumulative sums, searchsorted, masking). Easy to introduce off-by-one errors. Test coverage in audit is descriptive (print statements), not assertion-based.

**Safe modification:**
- Always test with `--allow-metadata-mismatch` flag when changing feature construction.
- Run `audit_multiscale_pipeline.py` before training on new dataset.
- Add unit tests in `temporal_multiscale/test_dataset_causality.py` (currently missing).
- Test coverage gaps: no test for PAC leakage into future context features.

---

### Fatigue Model Parameters Empirically Extracted, Not Validated

**Issue:** `simulator.py` fatigue model (tau_rise, tau_decay, pac_max, pac_min) are empirically extracted from Lahijanian et al. dataset (line 10–14). No ablation on fatigue severity or sensitivity analysis. If real brain fatigue has different time constants, simulation results are invalid.

**Files:** `src/simulator.py` (lines 49–91: parameter initialization), `run_fatigue_sensitivity.py` (lines 50–100: sensitivity sweep)

**Impact:** Closed-loop validation is based on simulator, not real data. If fatigue dynamics differ in actual patients, controller tuning could fail.

**Fix approach:**
- Run `run_fatigue_sensitivity.py` (already exists) with wider parameter ranges in config.yaml.
- Compare fixed-schedule and reactive-threshold strategies across 5x tau_rise, tau_decay to quantify sensitivity.
- Document in results that all closed-loop metrics are **simulator-based** and should be validated on real EEG in future work.

---

### Depthwise-Separable Conv Implementation Not Verified Against Standard

**Issue:** `CausalDSConvBlock` in `multiscale_tcn.py` (lines 20–54) implements custom depthwise-separable convolution with GroupNorm. No unit test compares output to torch.nn.Conv2d + pointwise decomposition to verify correctness.

**Files:** `temporal_multiscale/multiscale_tcn.py` (lines 20–54: CausalDSConvBlock)

**Why fragile:** Custom NN modules are easy to get wrong (padding, group sizes, residual connections). If bug is subtle (e.g., pad order), it will silently degrade performance.

**Safe modification:**
- Add unit test: `test_multiscale_tcn.py` with reference implementation comparison.
- Verify output shape and gradient flow on dummy input.

---

## Scaling Limits

### Memory Usage Unbounded by Dataset Size

**Issue:** `build_multiscale_dataset.py` loads all split data into memory at once (lines 39–46: `np.load()` entire splits). For future larger datasets (e.g., 100 subjects instead of 35), this could exceed 16 GB RAM.

**Current capacity:** 17,283 windows × 73 features × 8 bytes (float64) = ~10 MB per split. Scales linearly with subject count.

**Scaling path:**
- Use HDF5 (h5py) for lazy loading: read windows in chunks during training.
- Implement DataLoader prefetch to overlap I/O and computation.
- At 1000 subjects (100 hours data), expected memory = ~30 GB. Need chunking.

---

### No Distributed Training Support

**Issue:** Training loop in `train_multiscale_tcn.py` (lines 150–220) runs on single GPU. No DataParallel or DistributedDataParallel wrapper. For multi-GPU hardware, code would need significant refactoring.

**Impact:** With current dataset (11.7K windows, ~4 minutes per epoch), adding more subjects would hit GPU memory limit quickly.

**Scaling path:**
- Wrap DataLoader and model with DistributedDataParallel.
- Add command-line flag `--num_gpus` (default=1).
- For now, document single-GPU requirement in CLAUDE.md.

---

## Test Coverage Gaps

### No Unit Tests for Core Modules

**Issue:** Repository has no `tests/` directory. Testing is manual (run CLAUDE.md commands) or via high-level demo scripts (`run_closed_loop_demo.py`). No unit test for:
- PAC computation correctness against reference (scipy.signal.hilbert, PyEEG)
- Personalization module z-score computation
- Controller decision thresholds (boundary cases: exactly z=-0.5, z=0.5)
- Temporal dataset causality (windows don't contain future information)

**Impact:** Medium risk. Bugs in low-level functions (PAC, z-score) would propagate to all downstream analyses.

**Priority: Medium**

**Fix approach:**
- Create `tests/` directory with:
  - `test_pac_computation.py`: Compare PACComputer against PyEEG.
  - `test_personalization.py`: Unit tests for z-score with edge cases.
  - `test_controller.py`: State machine logic, hysteresis, boundary cases.
  - `test_dataset_causality.py`: Verify no future leakage in temporal sequences.
- Run tests in CI/CD before merging (add `.github/workflows/test.yml`).

---

### Missing Integration Tests for Closed-Loop Control

**Issue:** No test that runs full pipeline: load data → train EEGNet → run closed-loop → validate metrics. Current validation (`src/validation.py`) runs on simulator, not real data. No integration test catches API mismatches between controller/simulator/validation.

**Files:** No integration test file; validation is manual (`run_closed_loop_demo.py`)

**Priority: Low** (manual testing catches most issues, but CI would catch regressions)

**Fix approach:**
- Add `tests/test_integration_closed_loop.py`: Load subset of real data, train tiny EEGNet (5 epochs), run 1-minute closed-loop simulation, verify no exceptions and reasonable metrics.
- Add `--smoke-test` flag to `run_closed_loop_demo.py` to run 1-minute trial instead of 10.

---

### Temporal Multiscale Audit Assertions Are Soft (Warnings, Not Errors)

**Issue:** `audit_multiscale_pipeline.py` (lines 80–150) prints warnings but does not raise exceptions. If dataset has issues, user can easily miss them. No pre-training gate enforces audit success.

**Files:** `temporal_multiscale/audit_multiscale_pipeline.py` (lines 100–150: print() instead of assert)

**Trigger:** User runs `build_multiscale_dataset.py` → data has slight subject overlap → audit prints warning → user ignores → trains on contaminated data.

**Fix approach:**
- Convert print() warnings to raise ValueError() if issues are critical.
- Make CLAUDE.md step 3 (`python temporal/validate_code.py`) a required gate that must pass before step 4.

---

## Dependencies at Risk

### Deprecated PyTorch Version Lock

**Issue:** `requirements.txt` pins `torch>=2.0,<2.2` (see install command in CLAUDE.md). PyTorch 2.0 is from October 2023, and 2.1/2.2 introduce new performance features (torch.compile, FlashAttention). Code is not tested on latest PyTorch.

**Impact:** Low. Current code is compatible with PyTorch 2.1+, but no active testing.

**Migration plan:**
- Update `requirements.txt` to `torch>=2.0` (remove upper bound).
- Test locally with PyTorch 2.4+ (current as of Feb 2026).
- Leverage torch.compile() for 1.5–2x speedup in inference if available.

---

### MNE-BIDS Version Compatibility Unknown

**Issue:** `src/data_loader.py` (line 36–37) imports mne and h5py but does not specify versions. MNE-BIDS API changed in v1.0→v1.2 regarding BIDSPath and raw loading. If user has MNE 1.4+, code could fail silently on newer API.

**Files:** `src/data_loader.py` (line 36: `import mne`), `requirements.txt` (no mne version specified)

**Fix approach:**
- Add `mne>=1.2,<2.0` and `mne-bids>=0.12` to requirements.txt.
- Test on target versions.

---

## Missing Critical Features

### No Checkpointing of Personalization Baseline

**Issue:** `PersonalizationModule` state (30-second rolling baseline mean/std) is not saved to checkpoint. When resuming a closed-loop session from checkpoint, baseline is reset, causing z-score artifacts.

**Files:** `src/controller.py` (lines 85–110: checkpoint loading), `src/personalization.py` (line 30: class def, no state serialization)

**Impact:** If closed-loop is interrupted and resumed, first 30 seconds will have invalid z-scores.

**Fix approach:**
- Add `state_dict()` and `load_state_dict()` methods to PersonalizationModule.
- Save in checkpoint alongside EEGNet weights.
- Update `ClosedLoopController.load_checkpoint()` to restore personalization state.

---

### No Uncertainty Quantification on PAC Predictions

**Issue:** EEGNet and TCN output point estimates (mean PAC prediction) with no confidence intervals. Controller thresholds (z = ±0.5) do not account for prediction uncertainty. High-uncertainty predictions could lead to false decisions.

**Files:** `src/eegnet.py` (line 40: single output head), `src/controller.py` (line 150: hard threshold)

**Impact:** Medium. If model is uncertain about PAC state, controller should use conservative decision (stay in current state) rather than switching. Current code makes hard decisions regardless.

**Improvement path:**
- Add uncertainty estimation: ensemble methods, Monte Carlo dropout, or calibration.
- Update controller to use Bayesian decision rule: P(z < -0.5 | uncertainty) > threshold before stimulating.
- See `temporal_multiscale/checkpoint_deployment_audit.py` for noise robustness testing (related but not UQ).

---

### No Online Learning / Adaptation in Closed-Loop

**Issue:** EEGNet weights are frozen after training. If patient demographics or EEG characteristics drift over time (habituation, electrode shift, disease progression), model accuracy will degrade but is never updated.

**Files:** `run_closed_loop_demo.py` (no online learning), `src/controller.py` (no weight updates)

**Impact:** Long-term deployment (weeks/months) likely to see performance drift.

**Improvement path:**
- Implement online meta-learning: small adaptation steps on recent data.
- See `temporal_multiscale/per_subject_adaptation.py` for framework (currently for fine-tuning, not deployment-time).
- Use experience replay + SGD on recent valid predictions to avoid catastrophic forgetting.
