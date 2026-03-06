# Codebase Concerns

**Analysis Date:** 2026-03-05

## Tech Debt

**Pervasive sys.path Hacks:**
- Issue: Nearly every script manipulates `sys.path` at import time with `sys.path.insert(0, ...)` to resolve cross-module imports. There are 40+ occurrences across the codebase.
- Files: `src/training.py` (line 27), `run_tcn_validation.py` (lines 41-43), `run_full_pipeline.py` (lines 26-27, 66, 361), `run_closed_loop_demo.py` (line 31), `run_fatigue_sensitivity.py` (line 25), `run_threshold_sweep.py` (lines 11-13), `temporal_multiscale/train_multiscale_tcn.py` (line 26), and many more.
- Impact: Fragile import resolution that depends on working directory. Scripts break if run from unexpected locations. Makes the project uninstallable as a proper Python package.
- Fix approach: Convert the project into an installable package with `pyproject.toml` and proper `src/` layout. Use `pip install -e .` for development. Remove all `sys.path` manipulation.

**Hardcoded Absolute Path in Archive:**
- Issue: Two archived files contain a hardcoded session path from a remote environment.
- Files: `archive/experimental_models/data_loader_v2.py` (line 19: `/sessions/inspiring-exciting-feynman/mnt/...`), `archive/experimental_models/training_v2.py` (line 26: same path)
- Impact: These files are archived and not actively used, but indicate fragile import patterns that propagated into active code.
- Fix approach: Low priority (in `archive/`). Ensure no active code references these paths.

**Superseded `temporal/` Directory Still Active as Gate:**
- Issue: The `temporal/` directory is documented as superseded by `temporal_multiscale/`, but `temporal/validate_code.py` is still used as a mandatory pre-training gate (step 3 in CLAUDE.md pipeline). This script audits the superseded LSTM code -- it checks for `SpatialEncoder`, `use_gru`, `bidirectional`, `CosineAnnealing` -- none of which exist in the current TCN pipeline.
- Files: `temporal/validate_code.py`, `temporal/temporal_dataset.py`, `temporal/temporal_model.py`, `temporal/train_temporal.py`
- Impact: Running `temporal/validate_code.py` validates obsolete code, not the current `temporal_multiscale/` pipeline. This gives a false sense of validation. The audit checks are entirely irrelevant to the active codebase.
- Fix approach: Either (a) write a new validation gate for `temporal_multiscale/` that checks the actual TCN pipeline for leakage/integrity, or (b) retire the gate entirely since `temporal_multiscale/audit_multiscale_pipeline.py` already exists for this purpose.

**config.yaml Mostly Unused:**
- Issue: A comprehensive `config.yaml` (340 lines) documents all parameters, but source code hardcodes values rather than loading from it. The `load_config()` utility exists in `src/utils.py` (line 71) but is never imported by any active script. No script in `src/`, `temporal_multiscale/`, or `run_*.py` calls `load_config()`.
- Files: `config.yaml`, `src/utils.py` (lines 71-82)
- Impact: config.yaml is effectively documentation, not configuration. Changing values there has no effect on runtime behavior. Parameters are scattered across CLI argument defaults and constructor signatures.
- Fix approach: Either (a) wire config.yaml loading into entry points and use it as the single source of truth, or (b) demote it to `config.reference.yaml` to prevent confusion.

**config.yaml Contains Stale Values:**
- Issue: Several values in `config.yaml` do not match actual code behavior.
- Files: `config.yaml`
- Specific mismatches:
  - `targets.prediction_r2: 0.80` -- actual static model achieves R2 ~0.287; temporal TCN achieves ~0.25 at 5-10s horizons
  - `model.total_parameters: 2000` -- actual EEGNet has ~1,457 params (per CLAUDE.md)
  - `resources.device: "cuda"` -- development environment is Apple Silicon (MPS)
  - `validation.statistics.effect_size: "cohens_d"` -- actual validation uses Hedges' g (per CURRENT_METHODOLOGY.md)
  - `training.num_workers: 4` -- most scripts use `num_workers=0`

**Static PAC Prediction Ceiling at R2 ~0.287:**
- Issue: EEGNet performance has plateaued despite 8 architectural iterations (V1-V8 in `archive/v1_v8_attempts/`). All deep learning variants (SpecTempNet, ViT-TCNet, ATCNet) converged at or below Ridge baseline (0.287).
- Files: `src/eegnet.py`, `src/training.py`, `archive/v1_v8_attempts/`
- Impact: The limitation is fundamental to the input signal's information content (7 frontal channels, 2s windows), not model capacity. Do not spend engineering effort on static model improvements.
- Fix approach: Accept as ceiling. The TCN's value is at longer prediction horizons (5-10s), not better static accuracy.

## Known Bugs

**PredictiveLookAheadController z-score Ordering Inconsistency:**
- Symptoms: In `PredictiveLookAheadController.step()` (`src/controller.py` lines 377-379), `self.personalization.update(pac_current)` is called BEFORE `self.personalization.compute_zscore(pac_current)`. In contrast, `ClosedLoopController.step()` (lines 162-166) correctly computes z-score BEFORE updating the baseline. The predictive controller includes the current observation in its own baseline computation.
- Files: `src/controller.py` lines 377-379 vs lines 162-166
- Trigger: Every step of PredictiveLookAheadController
- Workaround: The effect is small (1 sample in a 30-sample window) and the TCN prediction path is the primary decision driver, so z-score is only a fallback. But it is semantically incorrect and inconsistent with the reactive controller.

**ANOVA on Single-Trial Scalars:**
- Symptoms: `SimulationValidator.statistical_comparison()` wraps each method's single scalar metric in a list and passes to `stats.f_oneway()`. ANOVA on groups of size 1 is undefined -- within-group variance is zero, producing NaN F-statistic.
- Files: `src/validation.py` lines 619-622
- Trigger: Running `validator.statistical_comparison()` with `n_trials=1` (the default in `run_simulation`)
- Workaround: Code catches the exception and returns NaN. The real validation in `run_tcn_validation.py` uses per-subject results with Wilcoxon tests, not this path.

**Double SiLU in CausalDSConvBlock:**
- Symptoms: The residual block applies SiLU activation twice: once on `x` after norm+dropout, then again on `x + residual`. Standard residual blocks use a single post-addition activation.
- Files: `temporal_multiscale/multiscale_tcn.py` lines 52-58 (comment on line 54 acknowledges this)
- Trigger: Every forward pass of the TCN
- Workaround: The model was trained and validated with this pattern. The inline comment explicitly warns that changing it requires retraining. Not a correctness bug, but a non-standard design that could confuse contributors.

## Security Considerations

**Unsafe Pickle Deserialization:**
- Risk: All `torch.load()` calls use `weights_only=False`, enabling arbitrary code execution via pickle. 12+ occurrences across the codebase.
- Files: `src/controller.py` (line 102), `src/training.py` (line 412), `temporal_multiscale/realtime_inference.py` (line 39), `temporal_multiscale/train_multiscale_tcn.py` (line 392), `run_tcn_validation.py` (line 641), `run_full_pipeline.py` (lines 279, 343), `run_threshold_sweep.py` (line 26), `generate_timeline_figure.py` (line 32), `rigor/experiments/tcn_interpretability.py` (line 211)
- Current mitigation: Only locally-generated checkpoints are loaded. No checkpoint downloading from untrusted sources.
- Recommendations: For a research project this is acceptable. If distributing checkpoints, switch to `weights_only=True` with explicit safe globals.

**No Input Validation on EEG Data Ranges:**
- Risk: EEG data is loaded without explicit range checks beyond artifact rejection (100 uV threshold). Pathological values (Inf, NaN, extreme values) could propagate silently.
- Files: `src/data_loader.py`, `src/preprocessing.py`
- Current mitigation: Artifact rejection threshold limits most outliers.
- Recommendations: Add NaN/Inf checks in preprocessing output. Log max absolute values per subject.

## Performance Bottlenecks

**Per-Sample Augmentation in Training Loop:**
- Problem: `DataAugmentor.augment()` is called per-sample in a Python for-loop during `ModelTrainer.train_epoch()`.
- Files: `src/training.py` lines 244-248
- Cause: `for i in range(len(batch_x_np)): batch_x_np[i] = augmentor.augment(batch_x_np[i])` iterates over each sample in the batch in pure Python.
- Improvement path: Vectorize augmentation operations to operate on entire batches using NumPy broadcasting, or move to GPU-side augmentation.

**Causal Moving Average Uses Python Loop:**
- Problem: `_causal_moving_average()` in `temporal_multiscale/build_multiscale_dataset.py` uses an explicit Python for-loop over all timesteps.
- Files: `temporal_multiscale/build_multiscale_dataset.py` lines 27-36
- Cause: Handles edge cases for initial ramp-up where the window is not yet full.
- Improvement path: Use `np.convolve` or `scipy.ndimage.uniform_filter1d`. Only matters if dataset rebuilds become frequent.

## Fragile Areas

**Import Resolution:**
- Files: All `run_*.py` scripts, all `temporal_multiscale/*.py` scripts
- Why fragile: Scripts depend on specific working directory and `sys.path` manipulations to resolve imports. Running from project root works; running from `src/` or any other directory fails with confusing ImportErrors.
- Safe modification: Always run scripts from the project root directory.
- Test coverage: None.

**PAC Label Semantics (Epoch-Level Assignment):**
- Files: `src/data_loader.py`, `temporal_multiscale/build_multiscale_dataset.py`
- Why fragile: PAC is computed at the epoch level (20-40s blocks) and assigned identically to all constituent 2s windows within that epoch. Windows from the same epoch share the same PAC label. Any code that assumes per-window PAC variability will see artificial plateaus.
- Safe modification: Document this assumption in any new analysis code. The `temporal_multiscale/` pipeline handles this correctly via causal smoothing.
- Test coverage: None.

**Checkpoint Format Coupling:**
- Files: `src/controller.py` (lines 102-104), `temporal_multiscale/realtime_inference.py` (lines 39-62), `temporal_multiscale/train_multiscale_tcn.py` (lines 347-362)
- Why fragile: Different checkpoints store different key structures. EEGNet checkpoints have `model_state_dict`, `pac_mean`, `pac_std`. TCN checkpoints have `model_state_dict`, `cfg`, `metadata`, `scalers`. RealtimePACForecaster requires both a checkpoint AND a separate `scalers.npz` file. No schema validation on load.
- Safe modification: When changing checkpoint format, update both the save path and ALL consumers.
- Test coverage: None.

**Dual Normalization Schemes:**
- Files: `src/training.py` (lines 466-475), `temporal_multiscale/build_multiscale_dataset.py` (lines 268-301)
- Why fragile: EEGNet uses z-score normalization of PAC targets (mean/std stored in checkpoint). TCN uses separate z-score normalization (mean/std stored in `scalers.npz`). The two schemes are independent. Using one's denormalization stats with the other produces garbage.
- Safe modification: Always denormalize with the same stats used for normalization.
- Test coverage: None.

**Target Smoothing Changes Evaluation Semantics:**
- Files: `temporal_multiscale/build_multiscale_dataset.py` (line 166-170), `temporal_multiscale/train_multiscale_tcn.py` (line 189)
- Why fragile: `target_smooth_window=5` predicts a causal denoised PAC state (R2 ~0.74). `target_smooth_window=1` predicts raw PAC (R2 ~0.07). These are fundamentally different prediction tasks. Comparing models trained with different smoothing windows is meaningless, but the metadata check only warns -- it does not prevent loading mismatched results.
- Safe modification: Never compare R2 values across different `target_smooth_window` settings. Always report the smoothing window alongside any R2 claim.

## Scaling Limits

**In-Memory Dataset Loading:**
- Current capacity: 17,283 windows x 7 channels x 500 samples x float32 = ~242 MB. Fits comfortably in RAM.
- Limit: At 100+ subjects or higher sampling rates, full `np.load()` into memory becomes problematic.
- Scaling path: Switch to memory-mapped files or HDF5 with lazy loading. Not urgent for current 35-subject dataset.

## Dependencies at Risk

**Unpinned Dependency Versions:**
- Risk: `requirements.txt` uses `>=` minimum versions (e.g., `torch>=2.0.0`, `numpy>=1.24.0`) without upper bounds. Future major releases could break compatibility.
- Impact: Reproducibility risk. A fresh `pip install` in 2027 could install incompatible versions.
- Migration plan: Pin exact versions in a `requirements.lock` from a known-working environment.

**CUDA 11.8 Assumption in Documentation:**
- Risk: `requirements.txt` header and installation instructions assume CUDA 11.8 and NVIDIA RTX 3080, but actual development uses Apple Silicon with MPS. The MPS fallback code exists in `src/training.py` (lines 452-457) and `temporal_multiscale/train_multiscale_tcn.py` (lines 284-289) but documentation does not mention MPS.
- Impact: Confusing for new developers on non-NVIDIA platforms.
- Migration plan: Update `requirements.txt` header to document multi-platform support (CUDA, MPS, CPU).

## Missing Critical Features

**No Automated Leakage Detection in Active Pipeline:**
- Problem: The MI feature leakage risk (documented in CLAUDE.md "Critical Gotchas") has no automated guard in the current `temporal_multiscale/` pipeline. The original detection is in `archive/diagnostics/audit_leakage.py`, but this only audits the old `archive/experimental_models/pac_features.py` path. The `temporal_multiscale/build_multiscale_dataset.py` excludes MI features by construction (uses spectral + PAC-derived + context), but there is no runtime assertion that MI features are absent from the feature vector.
- Blocks: Any developer adding new features could inadvertently reintroduce MI leakage without detection.

**No Reproducibility Seeding in EEGNet Training:**
- Problem: While `temporal_multiscale/train_multiscale_tcn.py` seeds NumPy, PyTorch, and CUDA (lines 213-219), the EEGNet training pipeline in `src/training.py` does not set any random seeds. The only seeds in `src/` are in ad-hoc `test_*()` functions (`src/controller.py` line 528, `src/personalization.py` line 254, `src/data_loader.py` line 589).
- Blocks: Exact reproduction of EEGNet training results.

**No Model Registry or Versioning:**
- Problem: Model checkpoints are saved as `best_eegnet.pth` and `best_multiscale_tcn_lb20_hz5_ts1.pth` with no versioning, hash, or associated metadata about the training run environment.
- Blocks: Tracking which checkpoint produced which results. Safe rollback after retraining.

**No Personalization State Persistence:**
- Problem: `PersonalizationModule` state (30-second rolling baseline) is not serializable. When resuming a closed-loop session, the baseline resets, causing 10+ seconds of invalid z-scores.
- Files: `src/personalization.py` (no `state_dict()`/`load_state_dict()` methods), `src/controller.py`
- Blocks: Session resumption in any real deployment scenario.

## Test Coverage Gaps

**Zero Automated Tests:**
- What's not tested: Everything. No `tests/` directory, no pytest configuration, no CI pipeline.
- Files: Entire codebase. Ad-hoc `test_*()` functions exist in `src/eegnet.py`, `src/controller.py`, `src/simulator.py`, `src/personalization.py`, `src/preprocessing.py` but are only runnable via `if __name__ == "__main__"` blocks.
- Risk: Any change to preprocessing, model architecture, data loading, or controller logic could silently break functionality.
- Priority: High

**Controller Decision Logic:**
- What's not tested: Hysteresis boundary conditions (z_score exactly at threshold, hold_time at exact boundary, None z_score handling), state machine transitions, interaction between reactive and predictive controllers.
- Files: `src/controller.py` (`_make_decision` methods)
- Risk: Subtle bugs in stimulation timing produce incorrect validation results.
- Priority: High

**Normalization Round-Trip:**
- What's not tested: That z-score normalization in training and denormalization in inference produce correct PAC values. The EEGNet path clips predictions to [0, 1] (`src/controller.py` line 159) which silently truncates any denormalization error.
- Files: `src/training.py`, `src/controller.py`, `temporal_multiscale/realtime_inference.py`
- Risk: Reported PAC values could be systematically biased without detection.
- Priority: High

**Data Loader Edge Cases:**
- What's not tested: Handling of missing `.fdt` files, corrupt HDF5, subjects with too few windows, non-contiguous subject indices.
- Files: `src/data_loader.py`
- Risk: Pipeline crashes with unhelpful errors on malformed data.
- Priority: Medium

**Temporal Dataset Causality:**
- What's not tested: Automated assertion that no future information leaks into features. The `temporal_multiscale/audit_multiscale_pipeline.py` prints diagnostics but uses print statements, not assertions. It is not wired into any gate.
- Files: `temporal_multiscale/audit_multiscale_pipeline.py`, `temporal_multiscale/build_multiscale_dataset.py`
- Risk: Feature refactoring could reintroduce temporal leakage without detection.
- Priority: High

---

*Concerns audit: 2026-03-05*
