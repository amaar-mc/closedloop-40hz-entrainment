# Architecture

**Analysis Date:** 2026-02-26

## Pattern Overview

**Overall:** Layered pipeline with feature extraction → prediction → control decision flow, organized as three independent subsystems: Static PAC Prediction (Phase 1), Temporal PAC Forecasting (Phase 2), and Closed-Loop Control (Phase 3). Each subsystem follows a clear separation of concerns: data processing, model training, and inference.

**Key Characteristics:**
- Data flows unidirectionally from raw BIDS dataset → preprocessing → feature extraction → model prediction → controller decision
- Modular design allows independent training and validation of each stage
- Interfaces defined through NumPy arrays and checkpoint files (no tight coupling)
- Real-time inference path separate from training path to ensure causal ordering (no future leakage)
- Configuration-driven hyperparameters (all parameters in `config.yaml`)

## Layers

**Data Ingestion Layer:**
- Purpose: Load BIDS-compliant EEG dataset and create aligned labels
- Location: `src/data_loader.py`
- Contains: BIDS dataset reader, event-based segmentation, window generation, PyTorch DataLoader factory
- Depends on: OpenNeuro ds005048 (MATLAB v7.3 HDF5 .set files + .fdt float32 arrays), events.tsv stimulus markers
- Used by: Preprocessing layer, feature extraction layer

**Preprocessing Layer:**
- Purpose: Signal conditioning and artifact rejection
- Location: `src/preprocessing.py`
- Contains: Bandpass filter (0.5–80 Hz, Butterworth 4th-order), notch filter (50 Hz, Q=30), amplitude thresholding (±100 µV), common average reference (CAR)
- Depends on: Data ingestion layer
- Used by: Feature extraction layer
- Note: Input data already preprocessed by Makoto's pipeline; this applies light additional filtering only

**Feature Extraction Layer:**
- Purpose: Compute PAC labels and spectral features from preprocessed EEG
- Location: `src/pac_computation.py` (PAC), `temporal_multiscale/build_multiscale_dataset.py` (spectral features + context)
- Contains:
  - PAC computation via Modulation Index (theta 4–8 Hz phase × gamma 38–42 Hz amplitude)
  - Spectral binning (61 frequency bins for 1–40 Hz)
  - Multiscale PAC history features (moving averages at 2, 4, 8, 16 timestep windows)
  - Stimulation context features (current state, time since last switch, 5-minute rolling stim fraction)
- Depends on: Preprocessing layer
- Used by: Model training layer (static and temporal paths)

**Static PAC Prediction Model:**
- Purpose: Predict PAC from a single 2-second EEG window
- Location: `src/eegnet.py`, `src/training.py`
- Contains: EEGNet CNN (1,457 parameters): Block 1 (temporal conv 8×1×64 + depthwise spatial) → Block 2 (separable conv) → FC head
- Depends on: Feature extraction (raw EEG windows + PAC labels)
- Used by: Controller for real-time inference
- Performance: R² ≈ 0.287 on held-out test subjects (ceiling for 7 frontal channels)

**Temporal PAC Forecasting Model:**
- Purpose: Predict future PAC at horizons 1–10 seconds ahead
- Location: `temporal_multiscale/multiscale_tcn.py`, `temporal_multiscale/train_multiscale_tcn.py`
- Contains: MultiscaleCausalTCN (31K parameters): 4 causal depthwise-separable conv blocks (dilations [1,2,4,8]) with GroupNorm + attention pooling, dual-head regression (future PAC + delta-PAC)
- Depends on: Multiscale temporal dataset from `build_multiscale_dataset.py`
- Used by: Closed-loop controller for proactive decisions at 5–10s horizons
- Performance: R² ≈ 0.25 at 5–10s horizons (maintains prediction where baselines collapse)

**Closed-Loop Control Layer:**
- Purpose: Real-time stimulation decisions based on personalized PAC thresholds
- Location: `src/controller.py`, `src/personalization.py`
- Contains:
  - `ClosedLoopController`: Integrates EEGNet inference + personalization module + decision logic
  - `PersonalizationModule`: Rolling 30-second baseline with z-score normalization
  - State machine: STIMULATE / REST states with 5-second hysteresis
  - Thresholds: z < −0.5 → stimulate; z > +0.5 → rest
- Depends on: Trained EEGNet checkpoint + real-time EEG stream
- Used by: Simulation/validation framework

**Simulator & Validation Layer:**
- Purpose: Test control strategies without live subjects
- Location: `src/simulator.py`, `src/validation.py`
- Contains:
  - `EntrainmentSimulator`: Exponential PAC dynamics (τ_rise=0.15, τ_decay=0.10) with optional fatigue model
  - `ValidationFramework`: Compares Fixed Schedule / Reactive / Predictive / Oracle strategies
  - Fatigue model: Recovery curves modeled as exponential with duty-cycle threshold
- Depends on: Trained models, controller
- Used by: Analysis scripts (`run_closed_loop_demo.py`, `run_fatigue_sensitivity.py`)

## Data Flow

**Static Prediction Path (Phase 1):**

1. Load raw BIDS EEG from `data/raw/ds005048`
2. `data_loader.py`: Parse MATLAB v7.3 .set files, read float32 .fdt arrays, segment by events.tsv
3. `preprocessing.py`: Apply bandpass (0.5–80 Hz) + notch (50 Hz) + artifact thresholding (±100 µV) + CAR
4. `pac_computation.py`: Compute Modulation Index PAC per epoch (20–40s blocks)
5. Create 2-second sliding windows (50% overlap) with epoch-level PAC labels
6. Export to `data/processed/{train,val,test}_data.npz` (Windows: (n, 1, 7, 500), PAC: (n,))
7. Train EEGNet via `training.py`: Adam (lr=0.001) + Huber loss + ReduceLROnPlateau + early stopping (patience=15)
8. Save checkpoint to `models/best_eegnet.pth` (includes z-score normalization stats)

**Temporal Prediction Path (Phase 2):**

1. Load preprocessed windows from `data/processed/{train,val,test}_data.npz` (output of Phase 1)
2. Extract spectral features via FFT (61 bins) and compute moving averages (2, 4, 8, 16 timesteps)
3. Read events.tsv for stimulation context (current state, time-since-switch, stim fraction)
4. Build causal sequences (no future leakage): X[t-lookback+1:t] → y[t+horizon]
5. Normalize features with z-score (saved in scalers.npz)
6. Export to `data/processed/multiscale_temporal/{train,val,test}_multiscale.npz`
7. Train MultiscaleCausalTCN via `train_multiscale_tcn.py`: Huber loss + multi-task (future + delta) + ReduceLROnPlateau
8. Save checkpoint to `models/best_multiscale_tcn.pth` (includes config, metadata, scalers)

**Closed-Loop Inference Path:**

1. Receive 2-second EEG window (1, 7, 500) at 1 Hz decision rate
2. `controller.py`: EEGNet inference → PAC estimate
3. `personalization.py`: Update 30-second rolling baseline → compute z-score
4. Decision logic: threshold-based + hysteresis (5-second hold)
5. Optional: Use `realtime_inference.py` (causal rolling buffer) for temporal TCN prediction at 5–10s horizon
6. Output: STIMULATE / REST action + diagnostics (PAC, z-score, confidence)

**State Management:**
- Static predictions: Stateless (single window → single PAC estimate)
- Temporal predictions: Stateful (maintains causal rolling buffer of 20–80 timesteps)
- Controller: Stateful (maintains current state, time-in-state, personalization buffer, hysteresis counter)
- Simulator: Stateful (maintains PAC, fatigue level, action history)

## Key Abstractions

**EEGWindowDataset:**
- Purpose: Abstracts batch loading of windowed EEG and labels
- Examples: `src/data_loader.py` (defines EEGWindowDataset), used by training scripts
- Pattern: PyTorch Dataset subclass with `__len__` and `__getitem__`

**PACComputer:**
- Purpose: Encapsulates Modulation Index computation with configurable band selection
- Examples: `src/pac_computation.py`, instantiated in `data_loader.py`
- Pattern: Stateless class with precomputed Butterworth filter coefficients

**EEGNet:**
- Purpose: Trainable CNN for static PAC regression
- Examples: `src/eegnet.py`, instantiated by `src/training.py` and `src/controller.py`
- Pattern: PyTorch nn.Module with fixed architecture (Block 1 → Block 2 → FC head)

**MultiscaleCausalTCN:**
- Purpose: Trainable temporal model for multi-step PAC forecasting
- Examples: `temporal_multiscale/multiscale_tcn.py`, instantiated by `temporal_multiscale/train_multiscale_tcn.py`
- Pattern: PyTorch nn.Module with dataclass config; causal (left-padded) convolutions

**PersonalizationModule:**
- Purpose: Maintains subject-specific rolling baseline for z-score adaptation
- Examples: `src/personalization.py`, instantiated by `src/controller.py`
- Pattern: Stateful circular buffer (deque) with on-demand statistics caching

**EntrainmentSimulator:**
- Purpose: Simulates brain PAC dynamics in response to stimulation actions
- Examples: `src/simulator.py`, instantiated by validation/analysis scripts
- Pattern: Stateful simulator with exponential approach model, optional fatigue layer

**ClosedLoopController:**
- Purpose: Integrates inference, personalization, and decision logic for real-time control
- Examples: `src/controller.py`, instantiated by `validation.py` and demo scripts
- Pattern: Stateful controller with state machine (STIMULATE/REST) and hysteresis

**RealtimePACForecaster:**
- Purpose: Wraps MultiscaleCausalTCN for low-latency causal rolling inference
- Examples: `temporal_multiscale/realtime_inference.py`
- Pattern: Stateful wrapper maintaining rolling buffer of (lookback) timesteps

## Entry Points

**Data Preparation (Phase 1):**
- Location: `src/data_loader.py` (direct script execution or import)
- Triggers: Manual invocation with `--bids_root` and `--output` arguments
- Responsibilities: Load BIDS dataset, create windows, compute PAC, export train/val/test splits

**Training Static Model (Phase 1):**
- Location: `src/training.py` (direct script execution)
- Triggers: Manual invocation with `--data_dir`, `--output_dir`, `--epochs` arguments
- Responsibilities: Load train/val splits, train EEGNet, checkpoint best model

**Building Temporal Dataset (Phase 2):**
- Location: `temporal_multiscale/build_multiscale_dataset.py` (direct script execution)
- Triggers: Manual invocation with `--data-dir`, `--output-dir`, optional `--lookback`, `--horizon`, `--smooth` arguments
- Responsibilities: Load static splits, compute multiscale features, build causal sequences, export normalized dataset

**Training Temporal Model (Phase 2):**
- Location: `temporal_multiscale/train_multiscale_tcn.py` (direct script execution)
- Triggers: Manual invocation with `--data-dir`, `--output-dir` arguments
- Responsibilities: Load multiscale dataset, train MultiscaleCausalTCN, checkpoint best model

**Closed-Loop Simulation (Phase 3):**
- Location: `run_closed_loop_demo.py` (direct script execution)
- Triggers: Manual invocation with optional `--duration`, `--n-trials`, `--enable-fatigue` arguments
- Responsibilities: Compare control strategies (Fixed / Reactive / Predictive / Oracle) with/without fatigue

**Fatigue Sensitivity Analysis (Phase 3):**
- Location: `run_fatigue_sensitivity.py` (direct script execution)
- Triggers: Manual invocation with optional `--severity-range` argument
- Responsibilities: Sweep fatigue parameters and measure performance degradation

**Real-Time Replay Analysis:**
- Location: `run_replay_analysis.py` (direct script execution)
- Triggers: Manual invocation with optional `--subject-id`, `--session-id` arguments
- Responsibilities: Replay controller on real EEG data (from test split) and evaluate performance

**Audit Scripts:**
- `temporal_multiscale/validate_code.py`: Pre-training gate; checks for temporal leakage
- `temporal_multiscale/audit_multiscale_pipeline.py`: Dataset integrity check
- `temporal_multiscale/comprehensive_submission_audit.py`: Ablation study + baseline comparison
- `temporal_multiscale/checkpoint_deployment_audit.py`: Robustness to noise

## Error Handling

**Strategy:** Exceptions bubble up with descriptive logging; validation gates enforce data contracts.

**Patterns:**
- Data validation in `data_loader.py`: Check file existence, shape consistency, subject-level split integrity
- Temporal leakage detection in `temporal/validate_code.py`: Assert no future information in sequences
- Metadata consistency in `build_multiscale_dataset.py`: Enforce args match on reuse (or require `--allow-metadata-mismatch`)
- Model checkpoint validation: Load config, verify architecture matches saved metadata
- Graceful fallback: If temporal model unavailable, controller falls back to static EEGNet only

## Cross-Cutting Concerns

**Logging:** Via Python `logging` module, configured in `src/utils.py`. Logger named `'closed_loop_entrainment'` used throughout. Levels: DEBUG (detailed debug output), INFO (progress), WARNING (data quality issues), ERROR (exceptions).

**Validation:**
- Input shapes checked in EEGNet `forward()` and MultiscaleCausalTCN `forward()`
- PAC labels range-checked in training loss computation
- Z-scores computed only if personalization buffer has ≥ min_samples

**Authentication:** Not applicable (offline research pipeline).

**Personalization:** Via PersonalizationModule: rolling baseline + z-score normalization, subject-specific thresholds in ClosedLoopController.

**State Reset:** All stateful components (controller, simulator, forecaster, personalization) have `reset()` method for trial-by-trial isolation.

---

*Architecture analysis: 2026-02-26*
