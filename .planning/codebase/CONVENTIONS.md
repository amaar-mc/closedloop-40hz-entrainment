# Coding Conventions

**Analysis Date:** 2026-02-26

## Naming Patterns

**Files:**
- Lowercase with underscores: `eegnet.py`, `data_loader.py`, `pac_computation.py`
- Core logic: `src/` (eegnet, training, controller, etc.)
- Temporal/time-series logic: `temporal_multiscale/` (build, train, audit, analysis)
- Main entry points: root level (run_*.py scripts)
- Archive: `archive/` for obsolete/experimental versions

**Functions:**
- Lowercase with underscores: `compute_regression_metrics()`, `ensure_dir()`, `count_parameters()`
- Private helpers: prefix with single underscore: `_make_decision()`, `_save_checkpoint()`, `_causal_moving_average()`
- Public methods: no prefix

**Variables:**
- Lowercase with underscores: `tau_rise`, `pac_max`, `model_state_dict`, `train_losses`
- Class attributes: match function naming (underscored)
- Loop variables: short (`i`, `j`, `step`, `epoch`), but descriptive in data contexts (`subj`, `window`, `seq`)
- Constants: UPPERCASE: `TENSORPAC_AVAILABLE`, `StimState.STIMULATE`

**Types and Classes:**
- PascalCase: `EEGNet`, `ModelTrainer`, `ClosedLoopController`, `PersonalizationModule`
- Enums with IntEnum: `class StimState(IntEnum)` — members are UPPERCASE
- Dataclasses: PascalCase with concise names: `ModelConfig`, `ValidationMetrics`

**PyTorch Modules:**
- Tensor variables: suffix with `_tensor`, `_t`, or plain (context-dependent)
  - `eeg_tensor`, `output`, `pac_pred` (model outputs)
  - `x`, `y` (generic in functions)
- Shapes documented inline: `# (batch, channels, samples)`

## Code Style

**Formatting:**
- No explicit linter config (no `.eslintrc`, `.prettierrc`, `pyproject.toml`)
- Follows PEP 8 implicitly (4-space indents, lowercase module names)
- Line length: soft 100 characters; hard break at 120

**Linting:**
- No automated linter mentioned in build
- Manual code review practices evident in docstrings and assertions

**Import Organization:**

Order (as seen in `src/training.py`, `src/eegnet.py`):
1. Standard library (os, sys, argparse, pathlib, typing, logging, json, yaml)
2. Third-party imports grouped by domain:
   - Numeric: numpy, scipy
   - ML/DL: torch, sklearn
   - Visualization: matplotlib, seaborn
   - CLI: argparse
   - Data: pandas, h5py, mne
3. Local imports: project modules (eegnet, utils, preprocessing)

Example from `src/training.py`:
```python
import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau

from tqdm import tqdm

from eegnet import EEGNet
from utils import setup_logging, ensure_dir, count_parameters, compute_regression_metrics
```

**Path Aliases:**
- No alias imports (no `as` renames) except for standard library (e.g., `from pathlib import Path`)
- Full module paths preferred (e.g., `torch.nn`, not `from torch import nn`)
- Exception: `import numpy as np` and `import pandas as pd` (standard industry convention)

## Error Handling

**Patterns:**
- Assertions for invariants and programming errors:
  ```python
  assert len(self.windows) == len(self.pac_labels), \
      f"Mismatch: {len(self.windows)} windows vs {len(self.pac_labels)} labels"
  assert 0 <= tau_rise <= 1, f"tau_rise must be in [0, 1], got {tau_rise}"
  ```

- Exceptions for runtime failures (user input, file I/O, data validation):
  ```python
  if not path.exists():
      raise FileNotFoundError(path)
  if not np.all(np.isfinite(arr)):
      raise ValueError("Non-finite values in array")
  raise ValueError(f"Invalid action: {action}")
  ```

- Logging for warnings and informational messages:
  ```python
  logger.info(f"Model loaded and set to eval mode")
  logger.warning(f"Subject {subj} not contiguous in {split_name}")
  ```

- Try-except for optional dependencies:
  ```python
  try:
      from tensorpac import Pac
      TENSORPAC_AVAILABLE = True
  except ImportError:
      TENSORPAC_AVAILABLE = False
      warnings.warn("Tensorpac not available...")
  ```

- Graceful degradation (fallback to CPU if GPU unavailable):
  ```python
  device = args.device if torch.cuda.is_available() else 'cpu'
  ```

**No Silent Failures:**
- Audit scripts return bool and raise SystemExit(1) on failure: `if not ok: raise SystemExit(1)`
- Data validation checks are explicit (finite check, shape check, leakage checks)

## Logging

**Framework:** Python standard `logging` module

**Logger setup:**
- Global logger per module: `logger = logging.getLogger(__name__)` or `logger = logging.getLogger('closed_loop_entrainment')`
- Centralized setup in `utils.setup_logging()` for console + file logging
- Default level: INFO

**Patterns:**
- Entry/exit logging for major operations:
  ```python
  logger.info("="*60)
  logger.info("Starting training for {epochs} epochs")
  logger.info("="*60)
  ```

- Per-epoch metrics:
  ```python
  logger.info(f"Epoch {epoch}/{epochs}")
  logger.info(f"  Train Loss: {train_loss:.6f}")
  logger.info(f"  Val Loss:   {val_loss:.6f}")
  ```

- State changes:
  ```python
  logger.info(f"Model loaded and set to eval mode")
  logger.info(f"Controller reset for new session")
  ```

- Diagnostics:
  ```python
  logger.info(f"PAC normalization: mean={pac_mean:.6f}, std={pac_std:.6f}")
  logger.info(f"ClosedLoopController initialized: Z-score thresholds: [{z_low}, {z_high}]")
  ```

## Comments

**When to Comment:**
- **High-level block comments:** Explain WHY (not WHAT), especially for non-obvious algorithms:
  ```python
  # BLOCK 1: Temporal and Spatial Feature Extraction
  # Temporal conv learns frequency-specific patterns;
  # depthwise spatial filter specializes per temporal feature
  ```

- **Inline comments:** Clarify shape transformations and mathematical operations:
  ```python
  x = self.conv1(x)           # (batch, F1, n_channels, n_samples)
  x = self.depthwise(x)       # (batch, F1*D, 1, n_samples)
  ```

- **Warning comments:** Flag subtle bugs or gotchas:
  ```python
  # MI feature leakage: using PAC features as inputs inflates R² to 0.999
  # Only spectral features are safe for PAC prediction.
  ```

**JSDoc/TSDoc:**
- Not used (Python project)
- Instead: **Google/NumPy docstring style** (used throughout)

## Function Design

**Size:**
- Target: 20-50 lines per function (public methods)
- Complex operations (train loop): up to 100 lines, but well-structured with sub-functions
- Helper functions: 5-15 lines

**Parameters:**
- Named arguments for clarity: `def train(self, train_loader, val_loader, epochs=100, checkpoint_dir='models')`
- Type hints throughout: `def step(self, eeg_window: np.ndarray) -> Tuple[StimState, float, Optional[float]]`
- Default values for optional params: `dropout: float = 0.5`, `device: str = 'cpu'`

**Return Values:**
- Single return is fine: `return epoch_loss`
- Multiple returns use tuples for related values: `return action, pac_pred, z_score`
- Dictionaries for heterogeneous results: `return {'train_losses': [...], 'best_epoch': ...}`
- None for void operations (after side effects like logging/saving): `logger.info(...); return None`

**Documentation (Docstrings):**
All public methods include docstring with Args/Returns:
```python
def step(self, eeg_window: np.ndarray) -> Tuple[StimState, float, Optional[float]]:
    """
    Execute one control step.

    Processes incoming EEG window and makes stimulation decision.

    Args:
        eeg_window: 2-second EEG window (7 channels, 500 samples)
                   Or (1, 7, 500) with feature channel

    Returns:
        action: Stimulation state (StimState.STIMULATE or .REST)
        pac_pred: Predicted PAC value
        z_score: Computed z-score (None if personalization not ready)
    """
```

## Module Design

**Exports:**
- Public: Classes, key functions (e.g., `EEGNet`, `ClosedLoopController`, `compute_regression_metrics`)
- Private: Prefixed with `_` (e.g., `_make_decision`, `_save_checkpoint`)
- No explicit `__all__` list (relying on convention)

**Barrel Files:**
- `__init__.py` files are minimal (mostly empty or single import)
- Direct imports preferred: `from eegnet import EEGNet` rather than `from src import EEGNet`

**Test Entry Points:**
- Standalone `test_*()` functions in modules:
  ```python
  def test_eegnet():
      """Test EEGNet with example input."""
      model = EEGNet(...)
      ...
      return model

  if __name__ == "__main__":
      model = test_eegnet()
  ```

- Audit/validation scripts: standalone top-level scripts (e.g., `temporal/validate_code.py`, `temporal_multiscale/audit_multiscale_pipeline.py`)

**Configuration:**
- Centralized `config.yaml` (not code-based ConfigObj)
- Loaded with `utils.load_config()` where needed
- Parameters passed as function arguments (not global state)

## Convention Deviations

**Accepted variations:**
- Temporal/spectral feature scripts use more scientific notation (e.g., variable names like `MI`, `PAC`, `theta`, `gamma`) for domain clarity
- Dataclass configs use `field(default_factory=...)` for mutable defaults (PEP 557 pattern)
- Type hints may be relaxed in small helper functions and scripts (e.g., audit scripts)

---

*Convention analysis: 2026-02-26*
