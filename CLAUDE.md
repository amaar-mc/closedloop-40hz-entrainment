# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

Always use the project's virtual environment:
```bash
venv/Scripts/python.exe   # Windows (this repo)
source venv/bin/activate  # Linux/Mac
```

Install dependencies:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

## Common Commands

```bash
# Preprocess raw BIDS data → processed windows + PAC labels
python src/data_loader.py --bids_root data/raw/ds005048 --output data/processed

# Train static PAC predictor (EEGNet)
python src/training.py --data_dir data/processed --output_dir models --epochs 100 --batch_size 64 --device cuda

# Run closed-loop simulation and compare control strategies
python src/validation.py --output_dir results --duration 360 --n_trials 3

# Pre-training leakage/integrity audit (required gate before temporal training)
python temporal/validate_code.py

# Build leakage-safe multiscale temporal dataset
python temporal_multiscale/build_multiscale_dataset.py \
  --data-dir data/processed \
  --output-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean

# Train multiscale causal TCN for future PAC prediction
python temporal_multiscale/train_multiscale_tcn.py \
  --data-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean \
  --output-dir models

# Run submission-grade audits
python temporal_multiscale/audit_multiscale_pipeline.py
python temporal_multiscale/comprehensive_submission_audit.py
```

There is no dedicated `tests/` package. For `src/` changes, run an end-to-end smoke path (data loading → training → validation) with a reduced `--epochs` count. Run `temporal/validate_code.py` before any temporal training.

## Architecture Overview

### Data Flow

```
data/raw/ds005048/          OpenNeuro BIDS dataset (35 subjects, .set/.fdt pairs)
        ↓
src/data_loader.py          Loads HDF5-format .set files (MATLAB v7.3), reads
                            actual EEG from .fdt (float32, Fortran order), applies
                            BIDS events.tsv for Stimulus/Rest segmentation
        ↓
src/preprocessing.py        Bandpass (0.5–80 Hz), notch (50 Hz), artifact rejection
                            (±100 µV threshold), common average reference
        ↓
src/pac_computation.py      Modulation Index (Tort 2010): theta (4–8 Hz) phase ×
                            gamma (38–42 Hz) amplitude → scalar PAC per window
        ↓
data/processed/             train/val/test_data.npz — subject-level split
                            Windows: (n, 1, 7, 500) — 7 frontal channels, 2s @ 250Hz
                            PAC labels: µV range [0.0002, 0.0046]
```

### Static PAC Prediction (`src/`)

`eegnet.py` — EEGNet regression model (~1,457 params):
- Input: `(batch, 1, 7, 500)` → Output: `(batch, 1)` predicted PAC
- Block 1: temporal conv + depthwise spatial; Block 2: separable conv; FC head

`training.py` — Training loop with z-score normalization of PAC targets (mean/std saved in checkpoint), Huber/MSE loss, Adam, ReduceLROnPlateau, gradient clipping (max_norm=1.0), early stopping.

Current performance: **R² ≈ 0.287** on held-out test subjects.

### Temporal PAC Prediction (`temporal_multiscale/`)

The latest pipeline for predicting *future* PAC (5–10 s ahead):

- `build_multiscale_dataset.py` — Constructs causal sequences from processed windows; adds stimulation-context features from BIDS events.tsv; no future leakage. Outputs `multiscale_temporal/` splits with z-score scalers.
- `multiscale_tcn.py` — `MultiscaleCausalTCN`: causal depthwise-separable conv blocks with dilation [1,2,4,8], residual connections, attention pooling; multi-head output (future PAC + delta-PAC).
- `train_multiscale_tcn.py` — Huber loss + multi-task delta/consistency penalty, ReduceLROnPlateau, early stopping (patience=20).

Current performance: **R² ≈ 0.125** for 8-second-ahead prediction (fundamental data limitation, not a code bug).

### Closed-Loop Control (`src/`)

`controller.py` → `personalization.py` → `simulator.py` → `validation.py`

1. `ClosedLoopController` runs EEGNet inference on each 2-second window.
2. `PersonalizationModule` maintains a 30-second rolling baseline; outputs z-score.
3. Decision: z < −0.5 → STIMULATE, z > +0.5 → REST, else MAINTAIN. 5-second hysteresis.
4. `EntrainmentSimulator` models brain response (exponential PAC dynamics).
5. `ValidationFramework` compares Fixed Schedule / Reactive / Predictive MPC / Oracle.

### Configuration

All runtime parameters live in `config.yaml` — channel selection, filter bands, PAC bins, model hyperparameters, controller thresholds, simulator dynamics. Edit there rather than in source files.

### Key Data Facts

- `.set` files are MATLAB v7.3 HDF5 (top-level keys, no `EEG` wrapper group); actual data is in companion `.fdt` files (float32, **Fortran/column-major order** — use `order='F'` when reshaping).
- Data is already preprocessed (1 Hz HP, 50 Hz notch, ICA, CAR) by Makoto's pipeline; `preprocessing.py` applies only light additional filtering.
- 17,283 total windows: Train 11,736 (24 subjects), Val 2,725 (5), Test 2,822 (6).

## Commit Style

Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`. Imperative subject line (e.g., `fix: prevent subject leakage in temporal split builder`). PRs must include before/after R²/RMSE metrics when model behavior changes.
