# Technology Stack

**Analysis Date:** 2026-03-05

## Languages

**Primary:**
- Python 3.10+ (specified in `requirements.txt`; system runtime is 3.13.3) - All source code, scripts, analysis, and figure generation

**Secondary:**
- YAML - Configuration (`config.yaml`)
- JSON - Metadata, training histories, validation results (`models/*.json`, `data/processed/multiscale_temporal_lb20_hz5_ts1/metadata.json`)
- Batch/Shell - Windows install script (`install.cmd`)

## Runtime

**Environment:**
- CPython 3.13.3 (system), targeting 3.10+
- Virtual environment via `venv/` (standard library venv)
- Apple Silicon (MPS) for local dev; CUDA 11.8 for GPU training

**Package Manager:**
- pip
- Lockfile: Not present (only `requirements.txt` with minimum version pins `>=`)

## Frameworks

**Core Deep Learning:**
- PyTorch >= 2.0.0 - Neural network training, inference, GPU acceleration
  - `torch` - Core framework used in `src/eegnet.py`, `temporal_multiscale/multiscale_tcn.py`, all training loops
  - `torchvision` >= 0.15.0 - Listed dependency, not directly imported in main pipeline
  - `torchaudio` >= 2.0.0 - Listed dependency, not directly imported in main pipeline

**EEG Processing:**
- MNE >= 1.5.0 - EEG data structures, channel info (`src/data_loader.py`)
- MNE-BIDS >= 0.14.0 - BIDS dataset loading (`src/data_loader.py`)

**Signal Processing:**
- SciPy >= 1.11.0 - Core signal processing and statistics
  - `scipy.signal` - Butterworth filters (`butter`, `filtfilt`), Hilbert transform (`hilbert`), notch filter (`iirnotch`) in `src/preprocessing.py`, `src/pac_computation.py`
  - `scipy.stats` - Statistical tests (Wilcoxon, Hedges' g) in `src/validation.py`, `run_tcn_validation.py`

**Phase-Amplitude Coupling:**
- TensorPAC >= 0.6.5 - Optional validation library with graceful fallback
  - Primary PAC uses manual Tort (2010) Modulation Index in `src/pac_computation.py`
  - TensorPAC imported conditionally: `try: from tensorpac import Pac` with `TENSORPAC_AVAILABLE` flag

**Machine Learning:**
- scikit-learn >= 1.3.0 - Baseline models and metrics
  - `sklearn.linear_model` - Ridge, Lasso, ElasticNet baselines (`models/*.pkl`)
  - `sklearn.metrics` - `r2_score`, `mean_squared_error`, `mean_absolute_error` in `src/utils.py`
  - `sklearn.ensemble` - GradientBoosting, RandomForest baselines

**Data Handling:**
- NumPy >= 1.24.0 - Array operations throughout; data stored as `.npz`/`.npy` files
- Pandas >= 2.0.0 - Events TSV reading, tabular data handling
- h5py >= 3.8.0 - Reading MATLAB v7.3 HDF5 `.set` files in `src/data_loader.py`

**Visualization:**
- Matplotlib >= 3.7.0 - All figure generation (`generate_figures.py`, `generate_timeline_figure.py`, `src/utils.py`, `src/validation.py`)
  - Uses `Agg` backend for headless rendering in figure scripts
  - 300 DPI, PNG+PDF output format
- Seaborn >= 0.12.0 - Statistical plots, `whitegrid` style default (`src/utils.py`)

**Configuration & Utilities:**
- PyYAML >= 6.0 - `config.yaml` loading in `src/utils.py`
- tqdm >= 4.65.0 - Progress bars in training loops (`src/training.py`)

**Optional (listed in requirements, not in main pipeline):**
- Optuna >= 3.1.0 - Hyperparameter optimization
- Captum >= 0.6.0 - Model interpretability / feature attribution

**Development:**
- Jupyter >= 1.0.0 + ipykernel >= 6.22.0 - Notebook support (notebooks in `notebooks/`, gitignored)

**Testing:**
- No test framework installed. Validation via end-to-end runs and `temporal/validate_code.py` audit gate.

## Key Dependencies

**Critical (model training and inference):**
- `torch` >= 2.0.0 - EEGNet (~1,457 params, `src/eegnet.py`), MultiscaleCausalTCN (~31K params, `temporal_multiscale/multiscale_tcn.py`), all training loops, checkpoint save/load
- `numpy` >= 1.24.0 - Array operations throughout; all data stored as `.npz` files
- `scipy` >= 1.11.0 - Signal filtering pipeline (`src/preprocessing.py`), PAC computation (`src/pac_computation.py`), statistical validation
- `h5py` >= 3.8.0 - Reading MATLAB v7.3 HDF5 `.set` files; critical for data loading

**Infrastructure:**
- `mne` >= 1.5.0 + `mne-bids` >= 0.14.0 - BIDS dataset integration
- `pyyaml` >= 6.0 - Central config loading
- `scikit-learn` >= 1.3.0 - Baseline models (Ridge, GBM, RF) and standard metrics

## Configuration

**Central Configuration:**
- All runtime parameters in `config.yaml` (340 lines, 17 sections)
- Loaded via `yaml.safe_load()` in `src/utils.py`

**Key Configuration Sections:**
| Section | Key Parameters | File |
|---------|---------------|------|
| `model.eegnet` | F1=8, D=2, F2=16, dropout=0.5, kernel_length=64 | `config.yaml` |
| `training` | Adam lr=0.001, wd=1e-4, ReduceLROnPlateau, early_stop patience=15 | `config.yaml` |
| `preprocessing` | Bandpass 0.5-80 Hz, notch 50 Hz, artifact 100 uV | `config.yaml` |
| `controller` | z_low=-0.5, z_high=0.5, hold_time=5s, baseline_window=30s | `config.yaml` |
| `simulator` | tau_rise=0.15, tau_decay=0.10, pac_max=0.3, pac_min=0.05 | `config.yaml` |
| `channels` | 7 frontal: Fp1, Fp2, F7, F3, Fz, F4, F8 | `config.yaml` |
| `paths` | raw=`data/raw/ds005048`, processed=`data/processed`, models=`models` | `config.yaml` |
| `resources` | device=cuda, gpu_id=0, mixed_precision=true, n_cpus=4 | `config.yaml` |

**TCN-specific config** is not in `config.yaml` but embedded in code:
- `temporal_multiscale/multiscale_tcn.py` - `ModelConfig` dataclass (in_features=73, hidden=64, n_blocks=4, dilations=[1,2,4,8], kernel_size=3, dropout=0.1)
- `temporal_multiscale/train_multiscale_tcn.py` - Training args (Huber loss, patience=20, lr via CLI)
- `temporal_multiscale/build_multiscale_dataset.py` - Dataset args (lookback=20, horizon=5, target_smooth=1)

**Environment Variables:**
- None required. No `.env` files. All configuration via `config.yaml` and CLI arguments.

## Data Formats

**Input (Raw BIDS):**
- `.set` files - MATLAB v7.3 HDF5 (channel metadata), read via `h5py`
- `.fdt` files - Float32 EEG data, **Fortran/column-major order** (use `order='F'`)
- `events.tsv` - Tab-separated event markers (onset, duration, value)
- `channels.tsv`, `*_eeg.json` - BIDS metadata per subject

**Intermediate (Processed):**
- `{train,val,test}_data.npz` - Keys: `windows` (n,1,7,500), `pac` (n,), `subjects` (n,)
- `{split}_spectral_cache.npy` - 61-dim spectral features per window
- `{split}_multiscale.npz` - Keys: `x_seq`, `y_future_norm`, `y_delta_norm`, `last_pac`
- `scalers.npz` - Z-score normalization parameters
- `metadata.json` - Build config (lookback, horizon, target_smooth, subject splits)

**Output (Models & Results):**
- `.pth` - PyTorch checkpoints (model state dict + config + stats)
- `.pkl` - scikit-learn model pickles (Ridge, GBM, RF, Lasso, ElasticNet)
- `.json` - Training histories, audit results, validation metrics
- `.png` / `.pdf` - Publication figures at 300 DPI

## Model Artifacts

**Production checkpoint:**
- `models/best_multiscale_tcn_lb20_hz5_ts1.pth` - MultiscaleCausalTCN (~31K params), lookback=20, horizon=5s, target_smooth=1

**Baseline models (sklearn pickles):**
- `models/ridge_v5.pkl`, `models/ridge_v5_enhanced.pkl`
- `models/gradient_boosting_v5.pkl`, `models/gradient_boosting_v6.pkl`
- `models/random_forest_v5.pkl`
- `models/lasso_v5.pkl`, `models/lasso_v6.pkl`
- `models/elasticnet_v5.pkl`
- `models/mlp_v6.pkl`

**Training metadata:**
- `models/summary_multiscale_tcn_*.json` - Per-config training summaries
- `models/history_multiscale_tcn_*.json` - Epoch-level training histories
- `models/sweep_horizons_results.json` - Horizon 1-10s sweep results

## Platform Requirements

**Development:**
- Python 3.10+
- macOS (Apple Silicon with MPS) or Linux with NVIDIA GPU (CUDA 11.8)
- 8+ GB system RAM
- Raw dataset: ~2 GB (OpenNeuro ds005048, 35 subjects)
- Processed data: ~500 MB

**GPU Support:**
- CUDA 11.8 (primary target per `requirements.txt`)
- MPS (Apple Silicon, used in current dev environment)
- CPU fallback supported throughout all scripts

**No containerization, CI/CD, or automated deployment.**

---

*Stack analysis: 2026-03-05*
