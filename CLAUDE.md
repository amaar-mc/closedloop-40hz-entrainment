# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

Always use the project's virtual environment:
```bash
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

Install dependencies:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

## Common Commands

### Full Pipeline (order matters)

```bash
# 1. Preprocess raw BIDS data → processed windows + PAC labels
python src/data_loader.py --bids_root data/raw/ds005048 --output data/processed

# 2. Train static PAC predictor (EEGNet)
python src/training.py --data_dir data/processed --output_dir models --epochs 100 --batch_size 64 --device cuda

# 3. Pre-training leakage/integrity audit (REQUIRED gate before temporal training)
python temporal/validate_code.py

# 4. Build leakage-safe multiscale temporal dataset (requires step 1)
python temporal_multiscale/build_multiscale_dataset.py \
  --data-dir data/processed \
  --output-dir data/processed/multiscale_temporal_lb20_hz5_ts1

# 5. Train multiscale causal TCN (requires step 4)
python temporal_multiscale/train_multiscale_tcn.py \
  --data-dir data/processed/multiscale_temporal_lb20_hz5_ts1 \
  --output-dir models

# 6. Sweep prediction horizons 1–10s (trains separate model per horizon)
python temporal_multiscale/sweep_horizons.py \
  --data-dir data/processed --output-dir models

# 7. Closed-loop simulation with fatigue comparison
python run_closed_loop_demo.py --duration 600 --n-trials 10

# 8. Fatigue sensitivity sweep
python run_fatigue_sensitivity.py
```

### Audits

```bash
python temporal_multiscale/audit_multiscale_pipeline.py         # dataset integrity
python temporal_multiscale/comprehensive_submission_audit.py     # ablation + baselines
python temporal_multiscale/checkpoint_deployment_audit.py        # robustness to noise
```

### Analysis Scripts

```bash
python temporal_multiscale/fatigue_analysis.py                  # real-data habituation
python temporal_multiscale/per_subject_adaptation.py             # fine-tuning evaluation
python temporal_multiscale/transition_analysis.py                # stim/rest transition accuracy
python temporal_multiscale/direction_classifier.py               # 3-class PAC direction
```

### Testing

There is no dedicated `tests/` package. For `src/` changes, run an end-to-end smoke path (data loading → training → validation) with a reduced `--epochs` count. Always run `temporal/validate_code.py` before any temporal training.

There is no `pytest`, `tests/`, or configured CI test suite. Testing is a mix of module self-tests, audit scripts, reduced-epoch smoke runs, and full validation scripts.

Most `src/` modules expose a bottom-of-file self-test and can be run directly:

```bash
python src/eegnet.py
python src/controller.py
python src/preprocessing.py
python src/personalization.py
python src/simulator.py
python src/pac_computation.py
```

Run one specific audit function from `temporal/validate_code.py` with `python -c`:

```bash
python -c "from temporal.validate_code import load_data, test_no_subject_leakage; splits = load_data('data/processed'); raise SystemExit(0 if test_no_subject_leakage(splits) else 1)"
python -c "from temporal.validate_code import load_data, test_temporal_sequence_logic; splits = load_data('data/processed'); raise SystemExit(0 if test_temporal_sequence_logic(splits, lookback=10, horizon=5) else 1)"
```

## Architecture Overview

### Data Flow

```
data/raw/ds005048/          OpenNeuro BIDS dataset (35 subjects, .set/.fdt pairs)
        ↓
src/data_loader.py          Loads HDF5-format .set files (MATLAB v7.3), reads
                            actual EEG from .fdt (float32, Fortran order), applies
                            BIDS events.tsv for Stimulus/Rest segmentation
        ↓
src/preprocessing.py        Bandpass (0.5–80 Hz), notch (50 Hz), artifact zeroing
                            (±100 µV threshold, samples set to 0.0), common average reference
        ↓
src/pac_computation.py      Modulation Index (Tort 2010): theta (4–8 Hz) phase ×
                            gamma (38–42 Hz) amplitude → scalar PAC per window
        ↓
data/processed/             train/val/test_data.npz — subject-level split
                            Windows: (n, 1, 7, 500) — 7 frontal channels, 2s @ 250Hz
                            PAC labels: range [0.000006, 0.000701], mean ~0.000044
```

**PAC label assignment:** PAC is computed at the epoch level (full 20–40s blocks), then assigned to all constituent 2s windows within that epoch. This means windows from the same epoch share the same PAC label.

### Static PAC Prediction (`src/`)

`eegnet.py` — EEGNet regression model (~1,457 params):
- Input: `(batch, 1, 7, 500)` → Output: `(batch, 1)` predicted PAC
- Block 1: temporal conv + depthwise spatial; Block 2: separable conv; FC head

`training.py` — Training loop with z-score normalization of PAC targets (mean/std saved in checkpoint), MSE loss, Adam, ReduceLROnPlateau, gradient clipping (max_norm=1.0), early stopping.

Current performance: **R² ≈ 0.287** on held-out test subjects (this is the ceiling for static prediction from 7 frontal channels — see docs/CODE_MAP.md for the full history of 8 model architectures that all converge here).

### Temporal PAC Prediction (`temporal_multiscale/`)

The latest pipeline for predicting *future* PAC (5–10 s ahead):

- `build_multiscale_dataset.py` — Constructs causal sequences (73 features: 61 spectral + 7 PAC-derived + 5 stim context) from processed windows; no future leakage. Outputs splits with z-score scalers.
- `multiscale_tcn.py` — `MultiscaleCausalTCN` (~31K params): causal depthwise-separable conv blocks with dilation [1,2,4,8], GroupNorm (cross-subject stable), attention pooling; dual-head output (future PAC + delta-PAC).
- `train_multiscale_tcn.py` — Huber loss + multi-task delta/consistency penalty, ReduceLROnPlateau, early stopping (patience=20).
- `realtime_inference.py` — `RealtimePACForecaster`: rolling causal inference wrapper for closed-loop integration.
- `sweep_horizons.py` — Trains and evaluates at horizons 1–10s; demonstrates TCN advantage at 5–10s where baselines fail.

**Key result:** At 1–2s horizons, persistence and Ridge beat the TCN. At 5–10s horizons, both collapse to negative R² while the TCN maintains R² ≈ 0.25 — a +0.5 R² margin. This is the operationally useful range for proactive control.

### Closed-Loop Control (`src/`)

`controller.py` → `personalization.py` → `simulator.py` → `validation.py`

1. `ClosedLoopController` runs EEGNet inference on each 2-second window.
2. `PersonalizationModule` maintains a 30-second rolling baseline; outputs z-score.
3. Decision: z < −0.5 → STIMULATE, z > +0.5 → REST, else MAINTAIN. 3-second hysteresis.
4. `EntrainmentSimulator` models brain response (exponential PAC dynamics, optional fatigue model).
5. `ValidationFramework` compares Fixed Schedule / Reactive / Predictive Look-Ahead / Oracle.

Top-level demo scripts: `run_closed_loop_demo.py` (all strategies ± fatigue), `run_fatigue_sensitivity.py` (fatigue severity sweep), `run_replay_analysis.py` (replay on real data).

### Superseded: `temporal/`

LSTM-based temporal prediction (Phase 2). Superseded by `temporal_multiscale/`. Only `temporal/validate_code.py` is still actively used as a pre-training audit gate.

### Additional Directories

- `rigor/`: Extended robustness, multi-seed, and statistical validation scripts.
- `scripts/pipeline/`: Orchestration scripts; some entry points have fragile import-path assumptions — use carefully.

### Configuration

All runtime parameters live in `config.yaml` — channel selection, filter bands, PAC bins, model hyperparameters, controller thresholds, simulator dynamics. Edit there rather than in source files.

### Key Data Facts

- `.set` files are MATLAB v7.3 HDF5 (top-level keys, no `EEG` wrapper group); actual data is in companion `.fdt` files (float32, **Fortran/column-major order** — use `order='F'` when reshaping).
- Data is already preprocessed (1 Hz HP, 50 Hz notch, ICA, CAR) by Makoto's pipeline; `preprocessing.py` applies only light additional filtering.
- 17,283 total windows: Train 11,736 (24 subjects), Val 2,725 (5), Test 2,822 (6).
- Splits are **subject-level** (no within-subject leakage between train/val/test).

## Critical Gotchas

- **MI feature leakage:** PAC features (from `archive/experimental_models/pac_features.py`) are circular — they directly encode the target. Using them as model inputs inflates R² to 0.999. Only spectral features are safe for PAC prediction. See `archive/diagnostics/audit_leakage.py` for the original detection.
- **Target smoothing changes evaluation:** `target_smooth_window=5` predicts a causal denoised PAC state (R² ≈ 0.74); `target_smooth_window=1` predicts raw PAC (R² ≈ 0.07). Never compare models across different target definitions.
- **Persistence is a strong baseline at short horizons.** Always report persistence and Ridge alongside any TCN result. The TCN's value is exclusively at 3+ second horizons.
- **Dataset rebuild required if args change.** `build_multiscale_dataset.py` enforces metadata consistency. If reusing a dataset dir with different lookback/horizon/smoothing args, rebuild or pass `--allow-metadata-mismatch`.
- **Do not extend `archive/` unless explicitly asked.**

## Commit Style

Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`. Imperative subject line (e.g., `fix: prevent subject leakage in temporal split builder`). PRs must include before/after R²/RMSE metrics when model behavior changes. Include before/after metrics such as R², RMSE, alignment, or stimulation efficiency when model behavior changes. Record the exact validation commands you ran.

## Code Style

- Follow PEP 8 with 4-space indentation.
- Aim for readable line lengths; existing code is usually under 100 chars and occasionally near 120.
- Prefer simple, explicit NumPy/PyTorch code over abstraction-heavy frameworks.
- Keep functions focused and pipeline stages obvious.
- Match the surrounding file instead of forcing a repo-wide rewrite.

## Imports

- Order imports as: standard library, third-party, project-local.
- Use standard aliases: `numpy as np`, `pandas as pd`, `matplotlib.pyplot as plt`, `seaborn as sns`.
- Legacy `src/` modules often use `sys.path.insert(...)` when run as scripts; preserve that pattern if extending them.
- Newer `temporal_multiscale/`, `rigor/`, and some `scripts/` files prefer `Path(__file__).resolve()`-based root discovery.
- Use local imports only to avoid heavy optional dependencies or circular imports.

## Typing

- Add type hints to public functions, methods, and important helpers.
- In `src/`, matching existing `typing` imports like `Dict`, `List`, `Optional`, and `Tuple` is fine.
- In newer temporal and rigor modules, `from __future__ import annotations` plus built-in generics is the local preference.
- Use type hints to clarify array/tensor shapes and returns, not to add noise.

## Naming and Docstrings

- Use `snake_case` for modules, functions, variables, and CLI flags.
- Use `PascalCase` for classes and `UPPER_CASE` for constants.
- Preserve common repo abbreviations such as `pac`, `eeg`, `snr`, `fs`, and `r2`.
- Keep checkpoint and run names descriptive, e.g. `best_multiscale_tcn_lb20_hz5_ts1.pth`.
- Most modules begin with a multi-line module docstring; keep that style when modifying substantial files.
- Prefer good names and docstrings over inline comments; add comments only for non-obvious signal-processing or leakage-safety logic.

## Error Handling and Logging

- Use `assert` for internal invariants and shape checks in hot paths.
- Raise `ValueError` for invalid inputs or unsupported states.
- Raise `FileNotFoundError` for missing datasets, checkpoints, or artifacts.
- Audit scripts should return `bool` and raise `SystemExit(1)` from `main()` on failure.
- Use small epsilon guards for numerical stability instead of silent failures.
- In reusable modules, prefer `logging.getLogger(__name__)` or the existing `closed_loop_entrainment` logger.
- In one-shot audits and CLI scripts, `print()` output is normal.
- Preserve the repo's `[PASS]` / `[FAIL]` output style for audits.
- New CLI entry points should use `argparse` and keep defaults aligned with `config.yaml` or nearby scripts.

## ML Guardrails

- Never allow subject overlap across train, val, and test splits.
- Preserve causal indexing: future targets must occur strictly after the sequence end.
- Fit normalization statistics on train only, then reuse them for val, test, and inference.
- Keep checkpoints self-describing when possible by storing config, metadata, and scaler values.
- Use deterministic seeding for temporal experiments when touching training logic.
- Report persistence and Ridge baselines honestly; they are expected reference points in this repo.

## Data and Artifact Hygiene

- Never commit raw data, private data, credentials, or large generated artifacts.
- Write checkpoints to `models/`, reports to `results/`, and logs to `logs/`.
- Do not mix generated outputs into `src/`, `temporal/`, or `temporal_multiscale/`.
- If a change affects defaults or interfaces, update `README.md`, `config.yaml`, or the relevant docs.

## When Adding New Code

- Put active implementation in `src/`, `temporal_multiscale/`, `rigor/`, or `scripts/` as appropriate.
- Add a small self-test or audit hook when practical, especially for new `src/` modules.
- Reuse existing utilities and conventions before inventing new framework layers.
- Optimize for correctness, leakage safety, and reproducibility before novelty or speed.

## Lint and Syntax Checks

No canonical formatter, linter, or type checker is configured. Default to syntax checks unless the user explicitly asks for a formatter/linter pass.

```bash
python -m py_compile src/training.py
python -m compileall src temporal temporal_multiscale rigor scripts
```

If you use `ruff`, `black`, or `mypy`, keep scope narrow and avoid repo-wide churn.

## Validation Matrix

- Changed `src/eegnet.py`: run `python src/eegnet.py` and a reduced-epoch `src/training.py` smoke run.
- Changed `src/controller.py`: run `python src/controller.py` and, if relevant, a closed-loop validation script.
- Changed preprocessing or PAC logic: rebuild or at least spot-check processed data before retraining.
- Changed `temporal/` or `temporal_multiscale/`: run `python temporal/validate_code.py` and the relevant multiscale audit.
- Changed split logic: explicitly verify subject disjointness and temporal causality.
