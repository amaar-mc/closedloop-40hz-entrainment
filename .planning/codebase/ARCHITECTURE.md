# Architecture

**Analysis Date:** 2026-03-05

## Pattern Overview

**Overall:** Multi-pipeline research system with three distinct processing stages (data ingestion, model training, closed-loop control) connected through file-based intermediate artifacts (`.npz` data splits, `.pth` checkpoints, `.json` scalers/metadata).

**Key Characteristics:**
- File-based pipeline coupling: each stage writes outputs consumed by the next stage via disk (no in-memory service layer)
- Two parallel model pipelines: static EEGNet for real-time PAC estimation, temporal TCN for future PAC forecasting
- Subject-level data isolation enforced at every stage (no within-subject leakage between train/val/test)
- All runtime parameters centralized in `config.yaml` (signal processing, model hyperparameters, controller thresholds, simulator dynamics)
- Top-level `run_*.py` scripts serve as experiment entry points that compose modules from `src/` and `temporal_multiscale/`
- Configuration is documentation-first: `config.yaml` documents all parameters but each module also has matching defaults; CLI args override at runtime

## Layers

**Data Ingestion Layer:**
- Purpose: Load raw BIDS EEG data, preprocess signals, compute PAC labels, create train/val/test splits
- Location: `src/data_loader.py`, `src/preprocessing.py`, `src/pac_computation.py`
- Contains: `BIDSDataProcessor` (BIDS loading, HDF5 `.set` + `.fdt` parsing, event-based windowing), `EEGPreprocessor` (bandpass 0.5-80 Hz, notch 50 Hz, artifact rejection +-100 uV, CAR), `PACComputer` (Tort Modulation Index: theta 4-8 Hz phase x gamma 38-42 Hz amplitude, 18 phase bins)
- Depends on: Raw data at `data/raw/ds005048/` (OpenNeuro BIDS format with `.set`/`.fdt` pairs + `events.tsv`), MNE, h5py, scipy
- Used by: Training pipeline, temporal dataset builder
- Outputs: `data/processed/{train,val,test}_data.npz` containing windows `(n, 1, 7, 500)` + PAC labels `(n,)` + subject IDs

**Static Model Layer (EEGNet):**
- Purpose: Train and serve a compact CNN that predicts current PAC from raw 2-second EEG windows
- Location: `src/eegnet.py`, `src/training.py`
- Contains: `EEGNet` (~1,457 params): Block 1 (temporal conv 8x1x64 + depthwise spatial 7x1) -> Block 2 (separable conv 16x1x16) -> FC head. `ModelTrainer` (MSE loss, Adam lr=0.001 wd=1e-4, ReduceLROnPlateau factor=0.5 patience=5, early stopping patience=15, gradient clipping max_norm=1.0). `DataAugmentor` (time shift, amplitude scaling, Gaussian noise).
- Depends on: Processed `.npz` splits from data ingestion layer
- Used by: `ClosedLoopController` for real-time PAC inference
- Outputs: `models/best_eegnet.pth` checkpoint (includes `pac_mean`/`pac_std` for z-score denormalization)
- Performance: R^2 ~ 0.287 on held-out test subjects (ceiling for 7 frontal channels after 8 architecture attempts)

**Temporal Model Layer (Multiscale TCN):**
- Purpose: Predict future PAC 5-10 seconds ahead using causal temporal features
- Location: `temporal_multiscale/build_multiscale_dataset.py`, `temporal_multiscale/multiscale_tcn.py`, `temporal_multiscale/train_multiscale_tcn.py`
- Contains:
  - `build_multiscale_dataset()`: Constructs causal sequences from processed windows. Feature vector = 73 dimensions: 61 spectral (from FFT cache) + 7 PAC-derived (current, MA2/4/8/16, diff1/4) + 5 stim context (state, time_since_switch, stim_frac, cycle_phase_sin/cos). Sequence format: `X[t-lookback+1:t]` -> `y[t+horizon]`.
  - `MultiscaleCausalTCN` (~31K params): Input projection (Linear + LayerNorm + SiLU) -> 4 `CausalDSConvBlock` layers (depthwise-separable conv, dilations [1,2,4,8], GroupNorm, SiLU, residual connections) -> `AttentionPool1D` (or `LastStepPool`) -> dual regression heads (future PAC + delta PAC, each: Linear->SiLU->Dropout->Linear)
  - Training: HuberLoss (delta=1.0) + optional multi-task delta loss + consistency penalty in raw PAC space. AdamW (lr=1e-3, wd=1e-3). ReduceLROnPlateau (mode="max" on val R^2, factor=0.5, patience=5). Early stopping patience=20.
- Depends on: Processed `.npz` splits + `{split}_spectral_cache.npy` + BIDS `events.tsv` for stim context
- Used by: `RealtimePACForecaster`, `PredictiveLookAheadController`
- Outputs: `models/best_multiscale_tcn_lb20_hz5_ts1.pth` (dict with `model_state_dict`, `cfg`, `metadata`, `scalers`), `data/processed/multiscale_temporal/scalers.npz`, `metadata.json`
- Performance: R^2 ~ 0.25 at 5-10s horizons where persistence/Ridge baselines collapse to negative R^2

**Realtime Inference Layer:**
- Purpose: Wrap trained TCN for online causal prediction with rolling buffer
- Location: `temporal_multiscale/realtime_inference.py`
- Contains: `RealtimePACForecaster` -- maintains `deque(maxlen=lookback)` for feature sequences and `deque(maxlen=32)` for PAC history. Per-step: assembles 73-feature vector from spectral_features(61) + PAC history features(7) + stim context(5), z-score normalizes using saved scalers, runs TCN forward pass, denormalizes predictions back to raw PAC scale.
- Depends on: Trained TCN checkpoint + `scalers.npz`
- Used by: `PredictiveLookAheadController` in `src/controller.py`, `PredictiveLookAheadControl` in `src/validation.py`

**Closed-Loop Control Layer:**
- Purpose: Make real-time stimulation decisions (STIMULATE/REST) based on brain state
- Location: `src/controller.py`, `src/personalization.py`
- Contains:
  - `ClosedLoopController`: Reactive controller. Loads EEGNet checkpoint. Per step: EEG window -> EEGNet PAC prediction -> z-score via `PersonalizationModule` -> threshold decision -> hysteresis enforcement.
  - `PredictiveLookAheadController`: Proactive controller. Takes `RealtimePACForecaster` instance. Per step: spectral features + PAC + stim context -> TCN prediction -> proactive decision based on predicted delta_pac -> reactive z-score fallback -> hysteresis.
  - `PersonalizationModule`: `deque(maxlen=30)` circular buffer. Compute-before-update pattern (z-score computed on current value before it enters buffer). Lazy-cached mean/std with cache invalidation on update.
  - `MultiChannelPersonalization`: Independent per-channel baselines (not used in current pipeline).
  - `StimState` enum: STIMULATE=1, REST=0.
- Depends on: EEGNet checkpoint (reactive) or TCN forecaster (predictive)
- Used by: Validation framework, demo scripts

**Simulation & Validation Layer:**
- Purpose: Simulate brain dynamics and compare control strategies
- Location: `src/simulator.py`, `src/validation.py`
- Contains:
  - `EntrainmentSimulator`: Exponential approach model: `PAC(t+1) = PAC(t) + tau * (target - PAC(t)) + noise`. Params: tau_rise=0.15, tau_decay=0.10, pac_max=0.3, pac_min=0.05, noise_std=0.02.
  - `FatigueAwareSimulator`: Extends above with habituation dynamics: effectiveness(t) = 1 - fatigue(t), fatigue accumulates during stim (rate=0.008), recovers during rest (rate=0.03), max_fatigue=0.7.
  - `extract_tau_parameters_from_data()`: Empirical tau estimation from observed PAC transitions.
  - `SimulationValidator`: Multi-method comparison framework. Runs each `ControlMethodBase` through identical simulation, collects `ValidationMetrics` (PAC mean/std/improvement, stim time, efficiency, R^2), ANOVA + Cohen's d.
  - Control strategies: `FixedScheduleControl` (40s ON / 20s OFF), `ReactiveThresholdControl` (z-score on rolling baseline), `PredictiveLookAheadControl` (TCN or trend-based heuristic), `OracleControl` (perfect information).
- Depends on: Controller layer, simulator
- Used by: Top-level demo/validation scripts

**Experiment Entry Layer:**
- Purpose: Compose modules into runnable experiments
- Location: Top-level `run_*.py` scripts
- Key scripts:
  - `run_tcn_validation.py`: Primary validation. Runs 6 controller variants (Fixed, Reactive, TCN Predictive, Hybrid TCN+Reactive, PI Controller, Alignment Oracle) on real EEG data with epoch-level evaluation. Computes alignment, transition anticipation, efficiency, clinical utility. Wilcoxon signed-rank + Hedges' g statistics. **This is the definitive evaluation script.**
  - `run_closed_loop_demo.py`: Simulation-based comparison (all strategies with/without fatigue, N trials)
  - `run_fatigue_sensitivity.py`: Fatigue severity sweep
  - `run_replay_analysis.py`: Replay controller decisions on real recorded EEG
  - `run_threshold_sweep.py`: Threshold sensitivity analysis (z-score thresholds 0.2-1.0)
  - `run_full_pipeline.py`: End-to-end pipeline runner
- Depends on: All layers above
- Outputs: `results/*.json`, `results/figures/*.png`

## Data Flow

**Raw BIDS to Processed Windows:**

1. `src/data_loader.py` (`BIDSDataProcessor.process_dataset()`) scans `data/raw/ds005048/sub-*/eeg/` for `.set` + `.fdt` file pairs
2. `.set` files are MATLAB v7.3 HDF5; actual EEG is in `.fdt` (float32, Fortran order) -- loaded via `_load_hdf5_set()` which reads `root['data']` as filename reference, then `np.fromfile(fdt, dtype=float32).reshape(n_channels, n_points, order='F')`
3. 7 frontal channels selected: Fp1, Fp2, F7, F3, Fz, F4, F8
4. `src/preprocessing.py` (`EEGPreprocessor.preprocess()`) applies bandpass (0.5-80 Hz Butterworth 4th-order), notch (50 Hz Q=30), artifact rejection (+-100 uV), CAR. Note: raw data already preprocessed by Makoto's pipeline (1Hz HP, 50Hz notch, ICA, CAR).
5. `extract_stimulus_windows()` segments by BIDS `events.tsv` into Stimulus/Rest blocks
6. PAC computed at epoch level (full 20-40s blocks) via `PACComputer.compute_pac_multichannel()`, then assigned to ALL constituent 2s windows within that epoch (windows from same epoch share same PAC label)
7. 2s sliding windows extracted with 50% overlap (hop=1s, 500 samples @ 250 Hz)
8. Subject-level splits (seed=42): 70/15/15 -> 24 train / 5 val / 6 test subjects. Written to `data/processed/{train,val,test}_data.npz`
9. Total: 17,283 windows (Train 11,736, Val 2,725, Test 2,822)

**Processed Windows to Temporal Sequences:**

1. `temporal_multiscale/build_multiscale_dataset.py` loads existing `.npz` splits via `_load_split()`
2. Loads pre-computed spectral cache (`{split}_spectral_cache.npy`, 61 features from FFT)
3. For each subject within each split:
   - Reads `events.tsv` via `_subject_events()` to get stim/rest state per window
   - Computes 5 stim context features via `_stim_context_from_events()`: state, time_since_switch (normalized /60), stim_frac (causal MA over 20s), cycle_phase_sin/cos
   - Computes 7 PAC-derived features via `_pac_multiscale_features()`: current, MA2/4/8/16, diff1, diff4 (all causal)
   - Concatenates: [61 spectral | 7 PAC | 5 context] = 73 features per timestep
4. Builds causal sequences: for each valid t, sequence = features[t-lookback+1 : t+1], target = PAC[t+horizon]
5. Z-score normalizes ALL features using train-only statistics; saves `scalers.npz`
6. Optional causal target smoothing (`_causal_target_smooth()`) with configurable window (ts=1 means raw targets)
7. Outputs: `data/processed/multiscale_temporal_{config}/{train,val,test}_multiscale.npz` + `scalers.npz` + `metadata.json`

**Closed-Loop Decision Flow (Reactive -- ClosedLoopController):**

1. `step(eeg_window)` receives raw EEG `(7, 500)` or `(1, 7, 500)`
2. Reshape to `(1, 1, 7, 500)` tensor, move to device
3. EEGNet forward pass -> PAC scalar prediction, clipped to [0, 1]
4. `PersonalizationModule.compute_zscore(pac)` -- computes BEFORE update to prevent self-contamination
5. `PersonalizationModule.update(pac)` -- adds to rolling buffer
6. `_make_decision(z_score)`: z < -0.5 -> STIMULATE, z > +0.5 -> REST, else MAINTAIN
7. Hysteresis: desired != current AND time_in_state >= hold_samples (5s) -> transition; else stay

**Closed-Loop Decision Flow (Predictive -- PredictiveLookAheadController):**

1. `step()` receives spectral_features(61), pac_current, stim_state, time_since_switch, stim_frac, cycle_phase
2. Updates personalization baseline, computes z-score
3. `RealtimePACForecaster.step()`:
   - Assembles 73-feature vector via `_build_step_feature()`
   - Appends to `seq_buffer` deque
   - If `len(seq_buffer) < lookback` -> returns None (not ready)
   - Stacks buffer into `(1, T, 73)` tensor, runs TCN forward
   - Denormalizes outputs: `future_raw = future_norm * yf_std + yf_mean`
   - Returns `{future_pac, delta_pac, current_pac, implied_future_from_delta}`
4. Decision priority: (a) delta_pac < -0.3 -> preemptive STIMULATE, (b) delta_pac > +0.3 -> REST, (c) reactive z-score fallback, (d) maintain
5. Same 5s hysteresis as reactive controller

**State Management:**
- No global state store. Each controller/simulator maintains its own history arrays (lists/numpy arrays).
- `PersonalizationModule`: `deque(maxlen=30)` with lazy-cached mean/std (invalidated on every `update()`)
- `RealtimePACForecaster`: `deque(maxlen=lookback)` for feature sequences, `deque(maxlen=32)` for PAC history used in MA features
- `EntrainmentSimulator`: Append-only lists for pac_history and action_history
- All stateful components have `reset()` methods for trial-by-trial isolation
- Results serialized to JSON (metrics/config) and NPZ (arrays) in `results/` and `models/`

## Key Abstractions

**EEGWindowDataset (`src/data_loader.py` line 50):**
- Purpose: PyTorch Dataset wrapping pre-computed EEG windows + PAC labels
- Pattern: Standard `__getitem__()` returning `(window_tensor, pac_scalar)`. Windows stored as float tensors `(1, 7, 500)`.

**SequenceDataset (`temporal_multiscale/train_multiscale_tcn.py` line 32):**
- Purpose: PyTorch Dataset for temporal TCN training
- Pattern: `__getitem__()` returns dict `{x_seq, y_future, y_delta, last_pac}`. Loaded from pre-built `.npz` files.

**ControlMethodBase (`src/validation.py` line 84):**
- Purpose: Abstract interface for control strategies
- Pattern: Strategy pattern. Defines `step(pac_current) -> action` and `reset()`. `SimulationValidator` runs any `ControlMethodBase` through identical simulation.
- Subclasses: `FixedScheduleControl`, `ReactiveThresholdControl`, `PredictiveLookAheadControl`, `OracleControl`

**ModelConfig (`temporal_multiscale/multiscale_tcn.py` line 89):**
- Purpose: Immutable dataclass configuration for `MultiscaleCausalTCN` architecture
- Pattern: Serialized as `cfg.__dict__` into checkpoint so model can be reconstructed from saved `.pth` file without knowing original CLI args.

**PersonalizationModule (`src/personalization.py` line 22):**
- Purpose: Subject-specific adaptive baseline via rolling window z-scores
- Pattern: Compute-before-update (z-score computed on current value before it enters the buffer, preventing self-contamination). Lazy-cached statistics invalidated on each `update()`.

**RealtimePACForecaster (`temporal_multiscale/realtime_inference.py` line 20):**
- Purpose: Wrap trained TCN for online causal inference with rolling buffer
- Pattern: Feature assembly + buffer management + model inference + denormalization in a single `step()` call. Returns None until lookback buffer is full.

## Entry Points

**Data Processing:**
- Location: `src/data_loader.py` -- `python src/data_loader.py --bids_root data/raw/ds005048 --output data/processed`
- Triggers: Manual; first pipeline step
- Responsibilities: Full BIDS -> preprocessed windows + PAC labels pipeline

**Static Model Training:**
- Location: `src/training.py` -- `python src/training.py --data_dir data/processed --output_dir models --epochs 100 --batch_size 64`
- Triggers: After data processing
- Responsibilities: Z-score normalize PAC targets, train EEGNet, save checkpoint with normalization params

**Temporal Dataset Build:**
- Location: `temporal_multiscale/build_multiscale_dataset.py` -- `python temporal_multiscale/build_multiscale_dataset.py --data-dir data/processed --output-dir data/processed/multiscale_temporal_lb20_hz5_ts1`
- Triggers: After data processing + spectral cache creation
- Responsibilities: Build causal sequences with 73 features, z-score normalize, save splits + scalers + metadata

**TCN Training:**
- Location: `temporal_multiscale/train_multiscale_tcn.py` -- can auto-rebuild dataset with `--rebuild-dataset`
- Triggers: After temporal dataset build
- Responsibilities: Train MultiscaleCausalTCN, save checkpoint + summary/history JSON

**Pre-Training Audit Gate:**
- Location: `temporal/validate_code.py` -- **REQUIRED** before any temporal training
- Triggers: Manual; integrity check
- Responsibilities: Verify no future information leaks into training sequences

**Real-Data TCN Validation (primary evaluation):**
- Location: `run_tcn_validation.py`
- Triggers: After both models trained
- Responsibilities: 6 controller variants on real EEG, epoch-level alignment/transition/efficiency metrics, Wilcoxon + Hedges' g

**Simulation Demos:**
- `run_closed_loop_demo.py`: All strategies with/without fatigue
- `run_fatigue_sensitivity.py`: Fatigue severity sweep
- `run_replay_analysis.py`: Replay on recorded real EEG

**Audits:**
- `temporal_multiscale/audit_multiscale_pipeline.py`: Dataset integrity
- `temporal_multiscale/comprehensive_submission_audit.py`: Ablation + baselines
- `temporal_multiscale/checkpoint_deployment_audit.py`: Robustness to noise

## Error Handling

**Strategy:** Defensive with graceful degradation. Errors in individual subjects are caught and logged; processing continues with remaining subjects. Validation gates enforce data contracts before training.

**Patterns:**
- `BIDSDataProcessor.process_dataset()` (`src/data_loader.py`): try/except per subject with `traceback.print_exc()` and `continue` -- logs error, skips subject, processes rest. Final check: raises `RuntimeError` if zero windows extracted from all subjects.
- `ClosedLoopController.step()` (`src/controller.py`): validates input ndim, raises `ValueError` for unexpected shapes (must be 2D or 3D)
- `PersonalizationModule.compute_zscore()` (`src/personalization.py`): returns `None` when `len(buffer) < min_samples` (caller must handle None)
- `PredictiveLookAheadControl.step()` (`src/validation.py`): cascading fallback chain: TCN prediction -> trend heuristic -> reactive z-score -> maintain current state. Never crashes on missing prediction.
- `RealtimePACForecaster.step()` (`temporal_multiscale/realtime_inference.py`): returns `None` until lookback buffer is full (safe for controller to receive)
- `build_multiscale_dataset.py`: validates metadata consistency between saved dataset and CLI args. Raises `ValueError` on mismatch unless `--allow-metadata-mismatch` passed. Validates contiguous subject indices.
- `EntrainmentSimulator.__init__()` (`src/simulator.py`): `assert` statements validate tau in [0,1], pac_min < pac_max <= 1
- Training loops: gradient clipping (max_norm=1.0) in both EEGNet and TCN training prevents exploding gradients

## Cross-Cutting Concerns

**Logging:** Python `logging` module throughout `src/` with named loggers per module (`logging.getLogger(__name__)`). Root logger `'closed_loop_entrainment'` configured in `src/utils.py`. `temporal_multiscale/` uses `print()` statements instead (no structured logging). Log file configured at `logs/experiment.log`.

**Validation:** Input shape validation at model boundaries. PAC label range not explicitly checked but z-score normalization handles scale. Z-scores computed only when personalization buffer has >= min_samples. Metadata consistency enforced in dataset builder. Pre-training leakage audit (`temporal/validate_code.py`) is a documented required gate.

**Configuration:** Single `config.yaml` at project root (341 lines). Not auto-loaded by modules -- each module has its own defaults that match config values. Config serves as documentation and reference truth. CLI args override at runtime. Key sections: dataset, channels, preprocessing, windowing, pac, model, training, controller, stimulation, simulator, validation, plotting, logging, resources, paths.

**Reproducibility:** Deterministic seeding in TCN training: `random.seed(42)`, `np.random.seed(42)`, `torch.manual_seed(42)`, `torch.cuda.manual_seed_all(42)`, `cudnn.deterministic=True`, `cudnn.benchmark=False`. Data splits use fixed seed=42. All experiment results serialized to JSON with full config snapshot.

**State Reset:** All stateful components (`ClosedLoopController`, `PredictiveLookAheadController`, `PersonalizationModule`, `EntrainmentSimulator`, `FatigueAwareSimulator`, `RealtimePACForecaster`) implement `reset()` for trial-by-trial isolation.

---

*Architecture analysis: 2026-03-05*
