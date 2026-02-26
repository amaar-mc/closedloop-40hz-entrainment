# Technology Stack

**Analysis Date:** 2026-02-26

## Languages

**Primary:**
- Python 3.10+ - All application logic, data processing, model training, and simulations

**Secondary:**
- Batch/Shell - Installation scripts (`install.cmd` for Windows)

## Runtime

**Environment:**
- CPython 3.10+ (specified in `requirements.txt` header)
- Virtual environment via `venv` module

**Package Manager:**
- pip - Package installation
- Lockfile: Not present (uses direct version pinning in `requirements.txt`)

## Frameworks

**Core (Deep Learning):**
- PyTorch 2.0.0+ - Neural network training, inference, GPU acceleration (CUDA 11.8)
  - `torch` - Core framework
  - `torchvision` 0.15.0+ - Image processing utilities
  - `torchaudio` 2.0.0+ - Audio processing

**EEG Processing:**
- MNE (1.5.0+) - EEG signal processing, filtering, artifact detection
- MNE-BIDS (0.14.0+) - BIDS dataset integration (loads OpenNeuro ds005048)

**Signal Processing:**
- SciPy (1.11.0+) - Signal filtering, FFT, statistical functions
  - `scipy.signal` - Butterworth filters, Hilbert transform, notch filtering
  - `scipy.stats` - Statistical tests (ANOVA, Tukey HSD)

**Phase-Amplitude Coupling:**
- TensorPAC (0.6.5) - Optional library for PAC computation validation; graceful fallback if unavailable
  - Manual Modulation Index implementation in `src/pac_computation.py` as primary

**Machine Learning:**
- scikit-learn (1.3.0+) - Ridge regression baselines, classifiers, metrics
  - `sklearn.linear_model` - Ridge, RidgeClassifier for baseline models
  - `sklearn.metrics` - R² score, MSE, MAE, classification metrics

**Data Handling:**
- NumPy (1.24.0+) - Array operations, signal manipulation
- Pandas (2.0.0+) - Event metadata handling, dataframe operations
- h5py (3.8.0+) - Reading MATLAB v7.3 HDF5 `.set` files

**Visualization:**
- Matplotlib (3.7.0+) - Figure generation, EEG plots
- Seaborn (0.12.0+) - Statistical plots, styling

**Training & Optimization:**
- Optuna (3.1.0) - Optional hyperparameter optimization
- Captum (0.6.0+) - Optional model interpretability and feature attribution

**Utilities:**
- YAML (PyYAML 6.0+) - Configuration loading from `config.yaml`
- tqdm (4.65.0+) - Progress bars for training loops

**Development & Notebooks:**
- Jupyter (1.0.0+) - Interactive analysis notebooks
- IPython kernel (6.22.0+) - Jupyter backend

## Key Dependencies

**Critical for Pipeline:**
- `torch` 2.0.0+ - Model training and inference; GPU acceleration via CUDA 11.8
- `mne` 1.5.0+ - BIDS dataset loading, EEG preprocessing (bandpass, notch, CAR)
- `mne-bids` 0.14.0+ - OpenNeuro ds005048 dataset integration
- `numpy` 1.24.0+ - Signal processing, array operations

**Infrastructure:**
- `h5py` 3.8.0+ - Reading companion `.fdt` float32 data files (Fortran order)
- `scipy` 1.11.0+ - Signal filtering (butter, filtfilt, hilbert), statistical tests
- `tensorpac` 0.6.5 - PAC computation validation (optional with fallback)

**Evaluation & Visualization:**
- `scikit-learn` 1.3.0+ - Baseline models (Ridge), metrics computation
- `pandas` 2.0.0+ - Event metadata, trial data organization
- `matplotlib` 3.7.0+ - Figure export for results
- `seaborn` 0.12.0+ - Statistical visualization

## Configuration

**Environment:**
- Configured via `config.yaml` (central runtime parameters)
  - Channel selection (7 frontal: Fp1, Fp2, F7, F3, Fz, F4, F8)
  - Filter bands (bandpass 0.5-80 Hz, notch 50 Hz)
  - PAC computation (Modulation Index, theta 4-8 Hz, gamma 38-42 Hz)
  - Model architecture (EEGNet hyperparameters)
  - Training (optimizer, LR scheduling, batch size, early stopping)
  - Controller thresholds and hysteresis
  - Simulator dynamics (rise/decay time constants, fatigue parameters)
  - Logging level (INFO default, file: `logs/experiment.log`)

**GPU/Resource Configuration:**
- Device selection: `cuda` or `cpu`
- GPU memory cap: 8000 MB default
- Mixed precision: Enabled by default (PyTorch 2.0+)
- CPU workers: 4 default for DataLoader

**Build:**
- No build system (pure Python, scripts run directly)
- Checkpoints saved as PyTorch `.pth` files to `models/` directory
- Training metadata saved as `.json` to same directory

## Platform Requirements

**Development:**
- Python 3.10+
- NVIDIA CUDA 11.8+ (optional but recommended for GPU acceleration)
- 8+ GB system RAM
- ~50 GB disk for OpenNeuro ds005048 dataset + processed windows

**Production/Deployment:**
- Python 3.10+
- GPU optional (CPU fallback available)
- Inference latency target: 50 ms per window (configured in `config.yaml`)
- Model inference runs on real-time EEG streams via `temporal_multiscale/realtime_inference.py`

---

*Stack analysis: 2026-02-26*
