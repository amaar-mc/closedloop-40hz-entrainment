# Codebase Structure

**Analysis Date:** 2026-02-26

## Directory Layout

```
closedloop-40hz-entrainment/
├── src/                          # Static PAC prediction (Phase 1) and control logic (Phase 3)
├── temporal_multiscale/          # Temporal PAC forecasting (Phase 2) — active pipeline
├── temporal/                     # LSTM-based temporal prediction (Phase 2, superseded) — validation only
├── archive/                      # Historical experiments and failed approaches
├── data/
│   ├── raw/ds005048/            # BIDS dataset (OpenNeuro) — input to pipeline
│   └── processed/               # Preprocessed windows and features — intermediate outputs
├── models/                       # Saved model checkpoints (.pth files)
├── logs/                         # Training and execution logs
├── results/                      # Simulation outputs and figures
├── docs/                         # Documentation and analysis reports
├── notebooks/                    # Jupyter notebooks for analysis and visualization
├── perwindow_pac/               # PAC feature visualization utilities
├── rigor/                        # Pre-submission checklist and compliance materials
├── .planning/codebase/          # GSD codebase mapping documents (this directory)
├── config.yaml                  # Central configuration file (runtime parameters)
├── CLAUDE.md                    # Project instructions for Claude
└── run_*.py                     # Entry point scripts for demos and analysis
```

## Directory Purposes

**src/:**
- Purpose: Core ML pipeline (Phase 1: static PAC prediction, Phase 3: closed-loop control)
- Contains: Data loading, preprocessing, PAC computation, EEGNet model, training, personalization, controller, simulator, validation framework
- Key files: `data_loader.py`, `eegnet.py`, `training.py`, `controller.py`, `personalization.py`, `simulator.py`, `validation.py`, `preprocessing.py`, `pac_computation.py`, `utils.py`

**temporal_multiscale/:**
- Purpose: Active temporal prediction pipeline (Phase 2) — predict future PAC at 1–10s horizons
- Contains: Multiscale temporal dataset builder, causal TCN model, training loop, real-time inference wrapper, analysis scripts (fatigue sensitivity, per-subject adaptation, direction classifier, transition analysis)
- Key files: `build_multiscale_dataset.py`, `multiscale_tcn.py`, `train_multiscale_tcn.py`, `realtime_inference.py`, `sweep_horizons.py`, `fatigue_analysis.py`, `per_subject_adaptation.py`
- Note: This is the recommended temporal pipeline; `temporal/` is superseded

**temporal/:**
- Purpose: Phase 2 archive — LSTM-based temporal prediction (no longer used for training)
- Contains: Older temporal dataset builder, LSTM model, sklearn baselines
- Key files: `validate_code.py` (still active as pre-training gate)
- Status: Maintained only for `validate_code.py` leakage audit; training moved to `temporal_multiscale/`

**archive/:**
- Purpose: Historical experiments, diagnostic scripts, and failed model architectures
- Contains: v1–v8 training attempts, diagnostic leakage analysis, wavelet features, data augmentation experiments, alternative EEG models (ViT, SpecTempNet)
- Subdirs:
  - `v1_v8_attempts/`: Sequential model training attempts (v1–v8)
  - `diagnostics/`: Leakage detection, debugging scripts (`audit_leakage.py` identifies PAC feature leakage)
  - `experimental_models/`: Alternative architectures and feature engineering
  - `docs_v1_v8/`: Documentation for historical approaches

**data/raw/ds005048/:**
- Purpose: Input BIDS dataset (OpenNeuro)
- Contains: 35 subjects, each with BIDS-structured EEG (.set + .fdt files), events.tsv stimulus markers
- Generated: No (external dataset, do not commit)
- Accessed by: `src/data_loader.py`

**data/processed/:**
- Purpose: Intermediate training data
- Contains:
  - `train_data.npz`, `val_data.npz`, `test_data.npz`: Windowed EEG (n, 1, 7, 500) + PAC labels + subject/session IDs
  - `train_spectral_cache.npy`, etc.: Precomputed spectral features (61 frequency bins)
  - `multiscale_temporal_*/`: Multiscale temporal dataset directories (one per config: `multiscale_temporal_lb20_hz1_ts5_clean/`)
    - `train_multiscale.npz`, `val_multiscale.npz`, `test_multiscale.npz`: Sequences (lookback, 73 features) + targets
    - `scalers.npz`: Feature normalization (mean/std per feature)
    - `metadata.json`: Config snapshot (lookback, horizon, smoothing, etc.)
- Generated: Yes (from `data_loader.py` and `build_multiscale_dataset.py`)
- Committed: No

**models/:**
- Purpose: Model checkpoints and weights
- Contains: `.pth` files (PyTorch checkpoint format)
  - `best_eegnet.pth`: Static PAC predictor (EEGNet)
  - `best_multiscale_tcn.pth`: Temporal PAC forecaster (MultiscaleCausalTCN)
  - Horizon-specific models: `best_multiscale_tcn_h5s.pth`, `best_multiscale_tcn_h10s.pth`, etc. (from `sweep_horizons.py`)
- Format: Python dict with keys: `model_state_dict`, `config`, `metadata`, `feature_scalers`, `target_scalers`
- Committed: No (generated during training)

**logs/:**
- Purpose: Execution logs
- Contains: Training logs (epoch metrics, loss curves), validation logs, simulation logs
- Generated: Yes (from training scripts and demos)
- Committed: No

**results/:**
- Purpose: Simulation outputs and analysis figures
- Subdirs:
  - `metrics/`: JSON files with performance metrics (PAC improvement, efficiency ratio, statistical tests)
  - `figures/`: PNG plots (PAC trajectories, control comparisons, sensitivity analysis)
- Generated: Yes (from `run_closed_loop_demo.py`, `run_fatigue_sensitivity.py`, analysis scripts)
- Committed: No

**docs/:**
- Purpose: Documentation and research reports
- Subdirs:
  - `research/`: Technical analysis documents (CODE_MAP.md, METHODOLOGY.md)
  - `audits/`: Audit reports (leakage detection, ablation studies, submission compliance)
  - `reports/`: Pre-submission checklist, literature review, interview prep
  - `archive/`: Historical documentation
- Committed: Yes

**notebooks/:**
- Purpose: Jupyter notebooks for exploratory analysis and visualization
- Contains: Subject-level analysis, PAC distribution, model comparison notebooks
- Generated: Yes (user-created)
- Committed: Selectively (exclude outputs)

**perwindow_pac/:**
- Purpose: Utilities for PAC visualization and feature inspection
- Contains: Scripts to compute and plot per-window PAC statistics
- Committed: Yes

**rigor/:**
- Purpose: Pre-submission compliance and integrity materials
- Contains: Pre-submission checklist, interview prep questions, fatigue sensitivity data
- Committed: Yes

**.planning/codebase/:**
- Purpose: GSD (Codebase Mapping) document storage
- Contains: ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, STACK.md, INTEGRATIONS.md, CONCERNS.md
- Generated: Yes (by codebase mapper agent)
- Committed: Yes

**config.yaml (project root):**
- Purpose: Central runtime configuration
- Contains: All hyperparameters (channel selection, filter bands, PAC frequency bins, model architecture, training hyperparameters, controller thresholds, simulator dynamics)
- Committed: Yes
- How to edit: Modify `config.yaml` rather than hardcoding parameters in source files

## Key File Locations

**Entry Points:**
- `src/data_loader.py`: Phase 1 data preprocessing
- `src/training.py`: Phase 1 model training
- `temporal_multiscale/build_multiscale_dataset.py`: Phase 2 dataset construction
- `temporal_multiscale/train_multiscale_tcn.py`: Phase 2 model training
- `run_closed_loop_demo.py`: Phase 3 closed-loop simulation
- `run_fatigue_sensitivity.py`: Phase 3 fatigue analysis
- `run_replay_analysis.py`: Phase 3 real-data evaluation

**Configuration:**
- `config.yaml`: All runtime parameters

**Core Logic:**
- `src/eegnet.py`: Static PAC prediction model
- `src/controller.py`: Closed-loop decision logic
- `src/personalization.py`: Subject-specific baseline adaptation
- `src/simulator.py`: Brain dynamics simulator with optional fatigue
- `temporal_multiscale/multiscale_tcn.py`: Temporal PAC forecasting model
- `temporal_multiscale/realtime_inference.py`: Real-time causal inference wrapper

**Preprocessing & Features:**
- `src/data_loader.py`: BIDS dataset loading, window creation
- `src/preprocessing.py`: Signal filtering, artifact rejection, CAR
- `src/pac_computation.py`: Modulation Index PAC computation
- `temporal_multiscale/build_multiscale_dataset.py`: Spectral feature extraction, multiscale context

**Testing & Auditing:**
- `src/validation.py`: Comparison framework for control strategies
- `temporal/validate_code.py`: Pre-training leakage audit gate
- `temporal_multiscale/audit_multiscale_pipeline.py`: Dataset integrity verification
- `temporal_multiscale/comprehensive_submission_audit.py`: Ablation and baseline comparison
- `temporal_multiscale/checkpoint_deployment_audit.py`: Noise robustness testing

**Analysis Scripts:**
- `temporal_multiscale/sweep_horizons.py`: Train and evaluate models at multiple prediction horizons
- `temporal_multiscale/fatigue_analysis.py`: Real-data habituation analysis
- `temporal_multiscale/per_subject_adaptation.py`: Fine-tuning evaluation
- `temporal_multiscale/transition_analysis.py`: Stim/rest transition accuracy
- `temporal_multiscale/direction_classifier.py`: 3-way PAC direction classification

**Utilities:**
- `src/utils.py`: Logging, plotting, metrics computation, file I/O

## Naming Conventions

**Files:**
- `data_loader.py`: Noun-describing-function (purpose is clear from name)
- `preprocessing.py`: Noun (conceptual stage)
- `eegnet.py`: Model class name in lowercase
- `training.py`: Verb-ing (training loop entry point)
- `controller.py`: Noun (main abstraction)
- `multiscale_tcn.py`: Model architecture name
- `run_*.py`: Top-level scripts prefixed with `run_`
- `*_analysis.py`: Analysis/diagnostic scripts
- `*_audit.py`: Validation/audit scripts
- `validate_*.py`: Pre-flight validation

**Directories:**
- `src/`: Core source code
- `temporal_multiscale/`: Multi-word descriptive (underscores)
- `data/raw/`, `data/processed/`: Hierarchical data stages
- `models/`: Trained weights storage
- `docs/`, `logs/`, `results/`: Output staging areas
- `archive/`: Historical code

**Modules within src/:**
- Classes: PascalCase (`EEGNet`, `ClosedLoopController`, `PersonalizationModule`)
- Functions: snake_case (`setup_logging`, `compute_regression_metrics`)
- Constants: UPPER_CASE (`DEVICE`, `SAMPLE_RATE`)

## Where to Add New Code

**New Feature:**
- Primary code: `src/` (if part of Phase 1 static prediction or Phase 3 control), or `temporal_multiscale/` (if Phase 2 temporal)
- Tests: No dedicated `tests/` directory; run end-to-end smoke tests with reduced `--epochs`
- Run leakage audit before temporal training: `python temporal/validate_code.py`

**New Component/Module:**
- Implementation: `src/` or `temporal_multiscale/` depending on pipeline stage
- If reusable across phases: `src/utils.py` (if utilities) or create new module in `src/`
- If specific to temporal: Create in `temporal_multiscale/` alongside related code

**Utilities:**
- Shared helpers: `src/utils.py`
- Plotting utilities: Add to `src/utils.py` or create `src/plotting.py`
- Metrics computation: Add to `src/utils.py`

**Analysis Scripts:**
- One-off analysis: Create in `temporal_multiscale/` (if Phase 2) or root (if full-pipeline)
- Name with `*_analysis.py` or `*_audit.py` suffix
- Keep analysis scripts executable as top-level Python scripts

**Configuration:**
- Add new hyperparameters to `config.yaml` under appropriate section
- Load in code via: `config = yaml.safe_load(open('config.yaml'))` (see `training.py` for pattern)
- Document parameter purpose in YAML comments

**Data Artifacts:**
- Intermediate data: `data/processed/{split}_*.npz` or `data/processed/multiscale_temporal_*/`
- Models: `models/*.pth`
- Results: `results/metrics/` (JSON) or `results/figures/` (PNG)
- DO NOT commit generated files; add to `.gitignore`

## Special Directories

**data/raw/ds005048/:**
- Purpose: OpenNeuro BIDS dataset (external, not generated)
- Generated: No
- Committed: No (too large, external source)

**archive/:**
- Purpose: Failed experiments and historical attempts (keep for documentation of why approaches were rejected)
- Generated: No (manually archived)
- Committed: Yes (for historical reference)

**models/:**
- Purpose: Trained model checkpoints
- Generated: Yes (from training scripts)
- Committed: No (large binary files)

**data/processed/:**
- Purpose: Intermediate datasets
- Generated: Yes (from `data_loader.py` and `build_multiscale_dataset.py`)
- Committed: No

**logs/ and results/:**
- Purpose: Execution outputs
- Generated: Yes
- Committed: No

**.planning/codebase/:**
- Purpose: GSD documentation
- Generated: Yes (by codebase mapper)
- Committed: Yes

---

*Structure analysis: 2026-02-26*
