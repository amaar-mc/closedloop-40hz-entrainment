# Codebase Structure

**Analysis Date:** 2026-03-05

## Directory Layout

```
closedloop-40hz-entrainment/
├── src/                              # Core ML pipeline: static PAC prediction + closed-loop control
│   ├── data_loader.py                #   BIDS data loading, HDF5 parsing, windowing, PyTorch Dataset
│   ├── preprocessing.py              #   Signal conditioning (bandpass, notch, artifact, CAR)
│   ├── pac_computation.py            #   Modulation Index PAC computation (Tort 2010)
│   ├── eegnet.py                     #   EEGNet CNN architecture (~1,457 params)
│   ├── training.py                   #   Training loop (MSE, Adam, early stopping, augmentation)
│   ├── controller.py                 #   ClosedLoopController + PredictiveLookAheadController
│   ├── personalization.py            #   Rolling baseline z-score adaptation
│   ├── simulator.py                  #   Brain dynamics simulator (exponential + fatigue)
│   ├── validation.py                 #   Multi-method comparison framework
│   └── utils.py                      #   Logging, metrics, plotting, file I/O helpers
│
├── temporal_multiscale/              # Active temporal prediction pipeline (causal TCN)
│   ├── __init__.py                   #   Package init
│   ├── build_multiscale_dataset.py   #   Causal sequence builder (73 features, leakage-safe)
│   ├── multiscale_tcn.py             #   MultiscaleCausalTCN model (~31K params, dual-head)
│   ├── train_multiscale_tcn.py       #   TCN training (Huber loss, AdamW, early stopping)
│   ├── realtime_inference.py         #   RealtimePACForecaster (rolling causal buffer)
│   ├── sweep_horizons.py             #   Horizon sweep: train + eval at horizons 1-10s
│   ├── sweep_multiscale_configs.py   #   Hyperparameter config sweeper
│   ├── fatigue_analysis.py           #   Real-data habituation analysis
│   ├── per_subject_adaptation.py     #   Per-subject fine-tuning evaluation
│   ├── transition_analysis.py        #   Stim/rest transition accuracy
│   ├── direction_classifier.py       #   3-class PAC direction prediction
│   ├── audit_multiscale_pipeline.py  #   Dataset integrity verification
│   ├── comprehensive_submission_audit.py  # Ablation + baseline comparison
│   ├── checkpoint_deployment_audit.py     # Checkpoint robustness to noise
│   └── README.md                     #   Pipeline documentation
│
├── temporal/                         # Superseded LSTM approach (Phase 2 archive)
│   ├── __init__.py                   #   Package init
│   ├── validate_code.py              #   ** STILL ACTIVE ** Pre-training leakage audit gate
│   ├── temporal_dataset.py           #   Old temporal dataset builder (not used)
│   ├── temporal_model.py             #   LSTM model (not used)
│   ├── train_temporal.py             #   Old training script (not used)
│   ├── train_temporal_long_windows.py #  Long-window variant (not used)
│   ├── train_sklearn_temporal.py     #   sklearn baselines (not used)
│   └── reprocess_long_windows.py     #   Data reprocessor (not used)
│
├── archive/                          # Historical experiments and failed approaches
│   ├── v1_v8_attempts/               #   8 sequential model architecture attempts
│   ├── diagnostics/                  #   Leakage detection scripts (audit_leakage.py)
│   ├── experimental_models/          #   Alternative architectures (ViT, SpecTempNet, etc.)
│   └── docs_v1_v8/                   #   Documentation for historical approaches
│
├── rigor/                            # Pre-submission validation and compliance
│   ├── rigorous_validation.py        #   Multi-seed training validation
│   ├── multi_seed_training.py        #   Seed sweep for reproducibility
│   ├── eegnet_enhanced.py            #   Enhanced EEGNet variant (validation)
│   ├── AUDIT_REPORT.md               #   Audit findings
│   └── experiments/                  #   Experiment scripts for validation
│
├── data/
│   ├── raw/ds005048/                 # OpenNeuro BIDS dataset (35 subjects, NOT committed)
│   │   └── sub-*/eeg/               #   .set + .fdt + events.tsv per subject
│   └── processed/                    # Preprocessed data (NOT committed)
│       ├── {train,val,test}_data.npz #   Windowed EEG (n,1,7,500) + PAC labels
│       ├── {split}_spectral_cache.npy #  FFT spectral features (61 bins)
│       └── multiscale_temporal_*/    #   Temporal sequence datasets per config
│           ├── {split}_multiscale.npz #  Sequences (lookback, 73) + targets
│           ├── scalers.npz            #  Feature normalization params
│           └── metadata.json          #  Config snapshot (lookback, horizon, etc.)
│
├── models/                           # Trained model checkpoints (NOT committed)
│   ├── best_eegnet.pth               #   Static PAC predictor
│   ├── best_multiscale_tcn_lb20_hz5_ts1.pth  # Primary TCN checkpoint
│   ├── summary_*.json                #   Training summaries per run
│   └── history_*.json                #   Epoch-by-epoch training histories
│
├── results/                          # Experiment outputs (partially committed)
│   ├── figures/                      #   Publication-quality PNG+PDF plots
│   ├── metrics/                      #   JSON metric files
│   ├── RESULTS_REPORT.md             #   Comprehensive results narrative
│   └── *.json                        #   Per-experiment result files
│
├── docs/                             # Documentation (committed)
│   ├── ABSTRACT.md                   #   247-word abstract for PDF submission
│   ├── POSTER_BOARD*.md              #   Poster iterations (V2-V5)
│   ├── CURRENT_METHODOLOGY.md        #   Detailed methodology writeup
│   ├── CODE_MAP.md                   #   Technical code walkthrough
│   ├── LOG_NOTEBOOK.md               #   Experiment log notebook
│   ├── LAB_NOTEBOOK.md               #   Lab notebook for submission
│   ├── INDEX.md                      #   Documentation index
│   ├── SYNOPSYS_REFERENCE.md         #   Q&A reference for Synopsys
│   ├── PROJECT_DEEP_DIVE.md          #   Deep project analysis
│   ├── archive/                      #   Historical docs
│   ├── audits/                       #   Audit reports
│   ├── reports/                      #   Pre-submission reports
│   └── research/                     #   Research notes
│
├── synopsys_submission/              # Synopsys science fair submission materials
│   ├── abstracts/                    #   Abstract iterations (round1-3)
│   ├── audit/                        #   Submission audits
│   └── reports/                      #   Submission reports
│
├── logs/                             # Execution logs (NOT committed)
├── notebooks/                        # Jupyter notebooks (empty currently)
├── perwindow_pac/                    # PAC visualization utilities
│
├── config.yaml                       # Central configuration (341 lines, all hyperparams)
├── CLAUDE.md                         # Project instructions for Claude Code
├── AGENTS.md                         # Agent configuration
├── README.md                         # Project readme
├── FINDINGS.md                       # Key findings summary
├── PRESENTATION.md                   # Presentation notes
├── requirements.txt                  # Python dependencies
├── .gitignore                        # Git ignore rules
│
├── run_tcn_validation.py             # ** PRIMARY ** Real-data TCN validation (6 controllers)
├── run_closed_loop_demo.py           # Simulation comparison (all strategies +/- fatigue)
├── run_fatigue_sensitivity.py        # Fatigue severity sweep
├── run_replay_analysis.py            # Replay controller on real EEG
├── run_threshold_sweep.py            # Z-score threshold sensitivity
├── run_full_pipeline.py              # End-to-end pipeline runner
├── generate_figures.py               # Publication figure generation
├── generate_timeline_figure.py       # Timeline visualization
└── generate_abstract_pdf.py          # Abstract PDF generator
```

## Directory Purposes

**src/:**
- Purpose: Core ML pipeline -- static PAC prediction (EEGNet) and closed-loop control logic
- Contains: 10 Python modules covering data loading, preprocessing, PAC computation, model definition, training, controller, personalization, simulation, validation, utilities
- Key files: `eegnet.py` (model), `controller.py` (decision logic), `training.py` (training loop), `data_loader.py` (BIDS ingestion)
- Import pattern: Modules import each other directly (no package `__init__.py`). `sys.path.insert(0, ...)` used in `training.py` for script-mode imports.

**temporal_multiscale/:**
- Purpose: Active temporal prediction pipeline -- predict future PAC 5-10s ahead using causal TCN
- Contains: Dataset builder, TCN model, training script, real-time inference wrapper, horizon sweep, analysis scripts, audit scripts
- Key files: `multiscale_tcn.py` (model), `build_multiscale_dataset.py` (data), `train_multiscale_tcn.py` (training), `realtime_inference.py` (inference)
- Has `__init__.py` -- importable as Python package

**temporal/:**
- Purpose: Superseded LSTM-based temporal prediction (Phase 2 archive)
- Status: Only `validate_code.py` is still actively used as a required pre-training audit gate
- Has `__init__.py` -- importable as Python package

**archive/:**
- Purpose: Historical experiments documenting 8 model architectures (V1-V8) that all converged to R^2 ~ 0.287 ceiling, plus diagnostic scripts that identified PAC feature leakage
- Key: `diagnostics/audit_leakage.py` -- original detection of MI feature leakage (R^2 inflated to 0.999)

**rigor/:**
- Purpose: Pre-submission reproducibility validation
- Contains: Multi-seed training, enhanced EEGNet variant testing, rigorous validation framework
- Generated: `rigorous_validation_results.json` (679KB of validation data)

## Key File Locations

**Entry Points (ordered by pipeline stage):**
- `src/data_loader.py`: Stage 1 -- BIDS data loading and window creation
- `src/training.py`: Stage 2 -- EEGNet training
- `temporal/validate_code.py`: Gate -- pre-training leakage audit (REQUIRED)
- `temporal_multiscale/build_multiscale_dataset.py`: Stage 3 -- temporal dataset construction
- `temporal_multiscale/train_multiscale_tcn.py`: Stage 4 -- TCN training
- `run_tcn_validation.py`: Stage 5 -- primary real-data evaluation
- `run_closed_loop_demo.py`: Stage 5 alt -- simulation-based evaluation

**Configuration:**
- `config.yaml`: All runtime parameters (dataset, channels, preprocessing, windowing, PAC, model, training, controller, stimulation, simulator, validation, plotting, logging, resources, paths)

**Core Logic (models + control):**
- `src/eegnet.py`: EEGNet CNN (~1,457 params, static PAC from 2s window)
- `temporal_multiscale/multiscale_tcn.py`: MultiscaleCausalTCN (~31K params, future PAC + delta)
- `src/controller.py`: `ClosedLoopController` (reactive) + `PredictiveLookAheadController` (proactive)
- `src/personalization.py`: `PersonalizationModule` (rolling baseline z-scores)
- `temporal_multiscale/realtime_inference.py`: `RealtimePACForecaster` (online TCN wrapper)
- `src/simulator.py`: `EntrainmentSimulator` + `FatigueAwareSimulator`
- `src/validation.py`: `SimulationValidator` + 4 control strategy classes

**Preprocessing & Features:**
- `src/preprocessing.py`: `EEGPreprocessor` (bandpass, notch, artifact, CAR)
- `src/pac_computation.py`: `PACComputer` (Tort MI method, theta-gamma)
- `temporal_multiscale/build_multiscale_dataset.py`: Spectral + PAC + stim context features

**Audits:**
- `temporal/validate_code.py`: Pre-training leakage check (REQUIRED gate)
- `temporal_multiscale/audit_multiscale_pipeline.py`: Dataset integrity
- `temporal_multiscale/comprehensive_submission_audit.py`: Ablation + baselines
- `temporal_multiscale/checkpoint_deployment_audit.py`: Noise robustness

**Analysis Scripts:**
- `temporal_multiscale/sweep_horizons.py`: Train models at horizons 1-10s
- `temporal_multiscale/fatigue_analysis.py`: Real-data habituation patterns
- `temporal_multiscale/per_subject_adaptation.py`: Fine-tuning evaluation
- `temporal_multiscale/transition_analysis.py`: Transition accuracy
- `temporal_multiscale/direction_classifier.py`: 3-class PAC direction

**Utilities:**
- `src/utils.py`: `setup_logging()`, `ensure_dir()`, `count_parameters()`, `compute_regression_metrics()`, YAML loading, plotting helpers

## Naming Conventions

**Files:**
- `data_loader.py`, `preprocessing.py`, `pac_computation.py`: Noun phrases describing purpose
- `eegnet.py`, `multiscale_tcn.py`: Model architecture names in lowercase
- `training.py`, `train_multiscale_tcn.py`: Verb prefix for training entry points
- `controller.py`, `personalization.py`, `simulator.py`, `validation.py`: Noun (main abstraction)
- `realtime_inference.py`: Adjective + noun compound
- `run_*.py`: Top-level experiment scripts, always prefixed with `run_`
- `*_analysis.py`: Analysis/diagnostic scripts
- `*_audit.py`: Validation/integrity audit scripts
- `generate_*.py`: Figure/document generation scripts

**Directories:**
- `src/`: Core source (no `__init__.py`, not a package)
- `temporal_multiscale/`: Multi-word descriptive with underscores (is a package)
- `temporal/`: Short name (is a package, mostly superseded)
- `data/raw/`, `data/processed/`: Hierarchical data stages
- `models/`, `logs/`, `results/`: Output staging areas
- `archive/`: Historical code preserved for documentation
- `docs/`: Documentation and reports

**Classes:**
- PascalCase: `EEGNet`, `ClosedLoopController`, `PredictiveLookAheadController`, `PersonalizationModule`, `MultiscaleCausalTCN`, `RealtimePACForecaster`, `EntrainmentSimulator`, `FatigueAwareSimulator`, `SimulationValidator`
- Enums: `StimState` (IntEnum), `StimAction` (IntEnum)
- Dataclasses: `ModelConfig`, `ValidationMetrics`

**Functions:**
- snake_case: `setup_logging()`, `compute_regression_metrics()`, `extract_tau_parameters_from_data()`
- Private with underscore: `_load_split()`, `_causal_moving_average()`, `_pac_multiscale_features()`, `_make_decision()`, `_save_checkpoint()`

**Constants:**
- UPPER_CASE: `FRONTAL_CHANNELS` (list in `BIDSDataProcessor`), `TENSORPAC_AVAILABLE`

## Where to Add New Code

**New EEG processing step:**
- Add to `src/preprocessing.py` as a new method on `EEGPreprocessor`, or create a new module in `src/`
- Update `src/data_loader.py` to call it in the per-subject processing loop

**New model architecture:**
- Create `src/new_model.py` (for static prediction) or `temporal_multiscale/new_model.py` (for temporal prediction)
- Follow pattern: define `nn.Module` class with `forward()`, optional `freeze_backbone()`/`unfreeze_all()` for fine-tuning
- Use `ModelConfig` dataclass pattern for serializable architecture config

**New control strategy:**
- Subclass `ControlMethodBase` in `src/validation.py` (for simulation evaluation) or create new controller class in `src/controller.py` (for real-time use)
- Implement `step(pac_current) -> action` and `reset()`
- Add to `SimulationValidator.add_method()` calls in demo scripts

**New temporal feature:**
- Add computation in `temporal_multiscale/build_multiscale_dataset.py` inside `_build_split_samples()`, append to feature vector and update feature_names list
- Ensure feature is causal (uses only past/current data, no future leakage)
- Rebuild dataset: `python temporal_multiscale/build_multiscale_dataset.py --output-dir data/processed/multiscale_temporal_new`

**New analysis script:**
- Create in `temporal_multiscale/` with `*_analysis.py` suffix
- Make executable with `if __name__ == "__main__"` block and `argparse`
- Output results to `results/` as JSON

**New top-level experiment:**
- Create `run_*.py` at project root
- Import from `src/` and `temporal_multiscale/` as needed
- Serialize results to `results/*.json`

**New utility function:**
- Add to `src/utils.py` for shared helpers (metrics, plotting, file I/O)

**New configuration parameter:**
- Add to appropriate section of `config.yaml` with YAML comment
- Add matching default in the relevant module's constructor/function signature

**New documentation:**
- Add to `docs/` directory
- Update `docs/INDEX.md` with link

## Special Directories

**data/raw/ds005048/:**
- Purpose: OpenNeuro BIDS dataset (35 subjects, .set/.fdt pairs)
- Generated: No (external download)
- Committed: No (too large)
- Access: `src/data_loader.py`, `temporal_multiscale/build_multiscale_dataset.py`

**data/processed/:**
- Purpose: All intermediate datasets (windows, features, sequences)
- Generated: Yes (from pipeline scripts)
- Committed: No
- Rebuild: `python src/data_loader.py --bids_root data/raw/ds005048 --output data/processed`

**models/:**
- Purpose: All trained model checkpoints + training metadata
- Generated: Yes (from training scripts)
- Committed: No (large binary files)
- Key checkpoint: `best_multiscale_tcn_lb20_hz5_ts1.pth` (primary TCN model)

**archive/:**
- Purpose: Historical experiments preserved for documentation of why approaches were rejected (8 static architectures, PAC feature leakage discovery, alternative models)
- Generated: No (manually archived)
- Committed: Yes
- Do NOT modify: these files document the research journey

**logs/:**
- Purpose: Execution logs
- Generated: Yes
- Committed: No

**results/:**
- Purpose: Experiment outputs (metrics JSON, publication figures)
- Generated: Yes (from `run_*.py` scripts and `generate_*.py` scripts)
- Committed: Partially (figures and RESULTS_REPORT.md committed, raw JSON may not be)

**.planning/codebase/:**
- Purpose: GSD codebase mapping documents
- Generated: Yes (by codebase mapper agent)
- Committed: Yes

---

*Structure analysis: 2026-03-05*
