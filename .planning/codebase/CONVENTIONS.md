# Coding Conventions

**Analysis Date:** 2026-03-05

## Naming Patterns

**Files:**
- snake_case for all Python modules: `data_loader.py`, `pac_computation.py`, `realtime_inference.py`
- Top-level run scripts use `run_` prefix: `run_closed_loop_demo.py`, `run_tcn_validation.py`, `run_fatigue_sensitivity.py`
- Audit/analysis scripts are descriptive: `audit_multiscale_pipeline.py`, `comprehensive_submission_audit.py`
- Model checkpoints: `best_{model_name}.pth` (e.g., `best_eegnet.pth`, `best_multiscale_tcn_lb20_hz5_ts1.pth`)
- Training artifacts: `summary_{run_name}.json`, `history_{run_name}.json`

**Classes:**
- PascalCase: `EEGNet`, `ClosedLoopController`, `MultiscaleCausalTCN`, `PersonalizationModule`
- Enum classes use PascalCase with UPPER_CASE members: `StimState.STIMULATE`, `StimAction.REST`
- Dataclasses for structured containers: `ValidationMetrics`, `ModelConfig`

**Functions:**
- snake_case: `compute_zscore()`, `train_one_epoch()`, `bandpass_filter()`
- Private/internal functions prefixed with underscore: `_make_decision()`, `_save_checkpoint()`, `_load_npz()`, `_corr()`, `_r2()`
- Test/demo functions: `test_eegnet()`, `test_controller()`, `test_preprocessing()`, `validate_simulator_dynamics()`

**Variables:**
- snake_case: `pac_values`, `train_losses`, `best_val_loss`
- Constants in UPPER_CASE: `BOOTSTRAP_N_RESAMPLES`, `BOOTSTRAP_CI_LEVEL`, `FATIGUE_RATES_SWEEP`, `TENSORPAC_AVAILABLE`
- Short math variables acceptable in local scope: `x`, `y`, `z`, `n`, `t`, `lr`, `fs`
- Abbreviations preserved from domain: `pac` (phase-amplitude coupling), `snr` (signal-to-noise ratio), `car` (common average reference)

**Types:**
- Type hints on all public method signatures
- `from typing import Dict, Tuple, Optional, List` (legacy style) in `src/` modules
- `from __future__ import annotations` used in `temporal_multiscale/` modules (newer style)
- Return type hints on all public functions

## Code Style

**Formatting:**
- No automated formatter configured (no `.prettierrc`, `pyproject.toml`, `.flake8`, `.pylintrc`)
- Manual 4-space indentation throughout
- Line length: soft 100 characters, hard break around 120
- Trailing commas used inconsistently

**Linting:**
- No linting configuration present
- Manual `# noqa: E402` used for path-manipulation imports in `rigor/rigorous_validation.py`

**String Quotes:**
- Single quotes for short strings: `'cuda'`, `'train'`, `'r2'`
- Double quotes for longer strings and docstrings
- f-strings for interpolation: `f"Epoch {epoch}/{epochs}"`

## Docstrings

**Module-Level:**
Every Python file has a comprehensive module docstring with:
1. What the module does
2. Key features or pipeline steps
3. Author and date
4. References where applicable

Pattern from `src/training.py`:
```python
"""
Training Pipeline for EEGNet PAC Prediction Model

Implements model training with:
- MSE loss and Adam optimizer (lr=0.001, weight_decay=1e-4)
- ReduceLROnPlateau scheduler (factor=0.5, patience=5)
...

Author: Amaar Chughtai
Date: February 2026
"""
```

Pattern from `temporal_multiscale/multiscale_tcn.py` (concise variant):
```python
"""
Lightweight multiscale causal TCN for future PAC and delta-PAC prediction.

Design constraints:
- Causal temporal modeling (real-time safe).
- Low parameter count for fast closed-loop inference.
- Multi-head regression: predict future PAC and delta PAC jointly.
"""
```

**Class Docstrings:**
- Describe purpose, attributes, and usage patterns
- Include `Args:` section in `__init__`
- List architectural details for model classes (input/output shapes, parameter counts)

**Function Docstrings:**
- Google-style format with `Args:`, `Returns:`, and sometimes `Note:` sections
- Include shape annotations for tensor/array parameters: `(batch, 1, n_channels, n_samples)`
- Internal functions (`_r2`, `_corr`) use one-liners or omit docstrings

## Import Organization

**Order:**
1. Standard library (`os`, `sys`, `argparse`, `json`, `logging`, `time`, `pathlib`)
2. Third-party packages (`numpy`, `scipy`, `torch`, `sklearn`, `matplotlib`, `pandas`)
3. Project-local imports (`from eegnet import EEGNet`, `from utils import setup_logging`)

**Standard Aliases:**
- `import numpy as np`
- `import pandas as pd`
- `import matplotlib.pyplot as plt`
- `import seaborn as sns`
- No other `as` aliases

**Path Manipulation:**
- `src/` modules: `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`
- `temporal_multiscale/` and `rigor/`: `ROOT = Path(__file__).resolve().parents[1]`
- Top-level scripts: `sys.path.insert(0, str(ROOT / "src"))`

**Optional Imports:**
- Wrapped in try/except with fallback flags:
```python
try:
    from tensorpac import Pac
    TENSORPAC_AVAILABLE = True
except ImportError:
    TENSORPAC_AVAILABLE = False
```
```python
try:
    from temporal_multiscale.realtime_inference import RealtimePACForecaster
except ImportError:
    RealtimePACForecaster = None
```

**No Path Aliases:** No `pyproject.toml` or `setup.cfg` with path aliases. All imports resolve via manually-inserted sys.path entries.

## Configuration Management

**Central Config:**
- All hyperparameters in `config.yaml` at project root
- Loaded via `src/utils.py:load_config()` using `yaml.safe_load()`
- Sections: `dataset`, `channels`, `preprocessing`, `pac`, `model`, `training`, `controller`, `simulator`, `validation`, `plotting`, `logging`, `resources`, `paths`, `metadata`

**Override Pattern:**
- `argparse` CLI arguments override config defaults
- Example from `temporal_multiscale/train_multiscale_tcn.py`: `--lr`, `--epochs`, `--hidden`, `--dropout`
- Defaults in argparse match `config.yaml` values

**Metadata Enforcement:**
- `build_multiscale_dataset.py` writes `metadata.json` alongside data files
- `train_multiscale_tcn.py` validates CLI args against `metadata.json`; raises `ValueError` on mismatch
- `--allow-metadata-mismatch` flag available as explicit override
- `--rebuild-dataset` flag triggers fresh dataset build

## Normalization Conventions

**PAC Target Normalization (EEGNet pipeline in `src/training.py`):**
```python
pac_mean = float(pac_train_raw.mean())
pac_std = float(pac_train_raw.std())
pac_train_norm = (pac_train_raw - pac_mean) / pac_std
pac_val_norm = (val_data['pac'] - pac_mean) / pac_std
```
- Store `pac_mean` and `pac_std` in model checkpoint via `checkpoint_extra`
- Denormalize at inference: `pac_raw = pac_norm * pac_std + pac_mean`

**Feature Normalization (TCN pipeline in `temporal_multiscale/`):**
- `StandardScaler` fit on training features only
- Saved to `scalers.npz` with keys: `feature_mean`, `feature_std`, `y_future_mean`, `y_future_std`, `y_delta_mean`, `y_delta_std`
- Applied in realtime inference (`realtime_inference.py`): `x = (x - self.feature_mean) / (self.feature_std + 1e-8)`

**Critical Rule:** Never fit scalers on val/test data. Always use train-only statistics.

## Error Handling

**Patterns:**
- `assert` for shape validation and parameter bounds:
  ```python
  assert 0 <= tau_rise <= 1, f"tau_rise must be in [0, 1], got {tau_rise}"
  assert len(self.windows) == len(self.pac_labels)
  ```
- `ValueError` for invalid function arguments: `raise ValueError(f"Invalid window shape: {eeg_window.shape}")`
- `FileNotFoundError` for missing data files: `raise FileNotFoundError(path)`
- `SystemExit(1)` in audit scripts when validation fails
- No custom exception classes

**Guard Patterns:**
- `None` returns for insufficient data: `PersonalizationModule.compute_zscore()` returns `None` before `min_samples` reached
- Epsilon guards for division by zero: `baseline_std + 1e-8`, `ss_tot + 1e-12`
- `np.clip()` for range enforcement: `pac_pred = np.clip(pac_pred, 0.0, 1.0)`

**Graceful Degradation:**
- CPU fallback when GPU unavailable
- Trend-based heuristic fallback when TCN forecaster is None (in `PredictiveLookAheadControl`)

## Logging

**Framework:** Python `logging` module

**Logger Naming:**
- Module-level: `logger = logging.getLogger(__name__)` (most modules)
- Named logger: `logging.getLogger('closed_loop_entrainment')` in `src/training.py`

**Setup:**
- `src/utils.py:setup_logging()` configures console + optional file handler
- Format: `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'`

**Patterns:**
- `logger.info()` for pipeline progress, metrics, configuration
- `logger.debug()` for per-step processing (filter application, per-channel stats)
- `logger.warning()` for degraded conditions (bad channels, single-channel CAR)
- Direct `print()` used in `temporal_multiscale/` scripts for simpler CLI output

**Section Headers:**
```python
logger.info("=" * 60)
logger.info("Starting training for {epochs} epochs")
logger.info("=" * 60)
```

**Metric Logging:**
```python
logger.info(f"Epoch {epoch}/{epochs}")
logger.info(f"  Train Loss: {train_loss:.6f}")
logger.info(f"  Val Loss:   {val_loss:.6f}")
logger.info(f"  Val R2:     {metrics['r2']:.4f}")
```

## Model Checkpoint Conventions

**EEGNet Checkpoints (`src/training.py`):**
```python
{
    'epoch': int,
    'model_state_dict': OrderedDict,
    'optimizer_state_dict': OrderedDict,
    'val_loss': float,
    'train_losses': List[float],
    'val_losses': List[float],
    'pac_mean': float,        # normalization params
    'pac_std': float,
}
```
- Saved to: `models/best_eegnet.pth`
- Loaded with: `torch.load(path, map_location=device, weights_only=False)`

**TCN Checkpoints (`temporal_multiscale/train_multiscale_tcn.py`):**
```python
{
    'model_state_dict': OrderedDict,
    'cfg': dict,               # ModelConfig.__dict__ for reconstruction
    'metadata': dict,          # dataset metadata (lookback, horizon, etc.)
    'scalers': {
        'y_future_mean': float,
        'y_future_std': float,
        'y_delta_mean': float,
        'y_delta_std': float,
    },
    'epoch': int,
    'val_future_r2': float,
}
```
- Saved to: `models/best_{run_name}.pth`
- Self-contained: includes config and scalers for standalone inference
- Training summary/history saved separately as JSON: `models/summary_{run_name}.json`, `models/history_{run_name}.json`

## Device Selection Pattern

Use this pattern for all new scripts:
```python
if torch.cuda.is_available():
    device = torch.device("cuda")
elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
```

## Data Split Conventions

- **Subject-level splits only.** No within-subject leakage between train/val/test.
- Split ratio: 70/15/15 (24 train, 5 val, 6 test subjects)
- Random seed: 42
- Saved as `{train,val,test}_data.npz` with keys: `windows`, `pac`, `subjects`
- Temporal datasets: `{train,val,test}_multiscale.npz` with keys: `x_seq`, `y_future`, `y_delta`, `y_future_norm`, `y_delta_norm`, `subjects`, `start_idx`, `end_idx`, `target_idx`, `last_pac`, `feature_names`

## Reproducibility

**Seeds:**
Full deterministic seeding in TCN training (`temporal_multiscale/train_multiscale_tcn.py`):
```python
random.seed(args.seed)
np.random.seed(args.seed)
torch.manual_seed(args.seed)
torch.cuda.manual_seed_all(args.seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```
Default seed: 42 everywhere.

**DataLoader:** Uses `torch.Generator` with manual seed for shuffle reproducibility.

**Audit Trail:**
- Training summaries saved as JSON with full config, metrics, timing
- Dataset metadata preserved in `metadata.json` alongside data files
- Audit scripts write JSON reports (e.g., `models/comprehensive_audit_multiscale_ts5.json`)

## Module Design

**Exports:** No `__all__` definitions. Import by name.

**Barrel Files:** `temporal_multiscale/__init__.py` and `temporal/__init__.py` exist but are empty.

**Entry Points:** All scripts runnable via `if __name__ == "__main__":` with `argparse`. Most define a `main()` function.

**Self-Test Pattern:** Many modules include a `test_*()` function at bottom, run when executed directly:
- `src/eegnet.py` -> `test_eegnet()`: forward pass with dummy input, shape validation
- `src/controller.py` -> `test_controller()`: synthetic 60-step closed-loop simulation
- `src/preprocessing.py` -> `test_preprocessing()`: synthetic signal through full pipeline
- `src/personalization.py` -> `test_personalization()`: z-score computation validation
- `src/simulator.py` -> `validate_simulator_dynamics()`: step response and recovery tests

## Statistical Reporting

**Required Metrics for Regression:**
- R^2, RMSE, MAE, Pearson correlation
- Computed via `src/utils.py:compute_regression_metrics()` or inline `_r2()`, `_corr()`, `_metrics()`

**Required Metrics for Controller Comparisons:**
- ANOVA, Wilcoxon signed-rank, Hedges' g effect size
- Bootstrap 95% confidence intervals (1000 resamples)
- Per-subject results (not just aggregate)

**Baseline Requirements:**
- Always report persistence baseline and Ridge baseline alongside model results
- At short horizons (1-2s), persistence beats the TCN -- this is expected and must be disclosed

**Commit Requirement:** PRs must include before/after R^2/RMSE metrics when model behavior changes.

## Training Loop Conventions

**EEGNet (static, `src/training.py`):**
- Loss: `nn.MSELoss()`
- Optimizer: `Adam(lr=0.001, weight_decay=1e-4)`
- Scheduler: `ReduceLROnPlateau(mode='min', factor=0.5, patience=5)` on val_loss
- Gradient clipping: `clip_grad_norm_(max_norm=1.0)`
- Early stopping: patience=15 on val_loss
- Data augmentation: time shift, amplitude scaling, Gaussian noise (p=0.5 each)

**TCN (temporal, `temporal_multiscale/train_multiscale_tcn.py`):**
- Loss: `nn.HuberLoss(delta=1.0)` + lambda-weighted delta loss + consistency penalty
- Optimizer: `AdamW(lr=1e-3, weight_decay=1e-3)`
- Scheduler: `ReduceLROnPlateau(mode='max', factor=0.5, patience=5)` on val_future_r2
- Gradient clipping: `clip_grad_norm_(max_norm=1.0)`
- Early stopping: patience=20 on val_future_r2
- Batch size: 128

## Activation Functions

- EEGNet: `ELU` (better than ReLU for EEG per literature)
- TCN: `SiLU` (Swish) throughout, including double-SiLU in residual blocks (trained artifact, do not change without retraining)

---

*Convention analysis: 2026-03-05*
