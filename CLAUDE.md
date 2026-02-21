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
  --output-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean

# 5. Train multiscale causal TCN (requires step 4)
python temporal_multiscale/train_multiscale_tcn.py \
  --data-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean \
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

**PAC label assignment:** PAC is computed at the epoch level (full 20–40s blocks), then assigned to all constituent 2s windows within that epoch. This means windows from the same epoch share the same PAC label.

### Static PAC Prediction (`src/`)

`eegnet.py` — EEGNet regression model (~1,457 params):
- Input: `(batch, 1, 7, 500)` → Output: `(batch, 1)` predicted PAC
- Block 1: temporal conv + depthwise spatial; Block 2: separable conv; FC head

`training.py` — Training loop with z-score normalization of PAC targets (mean/std saved in checkpoint), Huber/MSE loss, Adam, ReduceLROnPlateau, gradient clipping (max_norm=1.0), early stopping.

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
3. Decision: z < −0.5 → STIMULATE, z > +0.5 → REST, else MAINTAIN. 5-second hysteresis.
4. `EntrainmentSimulator` models brain response (exponential PAC dynamics, optional fatigue model).
5. `ValidationFramework` compares Fixed Schedule / Reactive / Predictive MPC / Oracle.

Top-level demo scripts: `run_closed_loop_demo.py` (all strategies ± fatigue), `run_fatigue_sensitivity.py` (fatigue severity sweep), `run_replay_analysis.py` (replay on real data).

### Superseded: `temporal/`

LSTM-based temporal prediction (Phase 2). Superseded by `temporal_multiscale/`. Only `temporal/validate_code.py` is still actively used as a pre-training audit gate.

### Configuration

All runtime parameters live in `config.yaml` — channel selection, filter bands, PAC bins, model hyperparameters, controller thresholds, simulator dynamics. Edit there rather than in source files.

### Key Data Facts

- `.set` files are MATLAB v7.3 HDF5 (top-level keys, no `EEG` wrapper group); actual data is in companion `.fdt` files (float32, **Fortran/column-major order** — use `order='F'` when reshaping).
- Data is already preprocessed (1 Hz HP, 50 Hz notch, ICA, CAR) by Makoto's pipeline; `preprocessing.py` applies only light additional filtering.
- 17,283 total windows: Train 11,736 (24 subjects), Val 2,725 (5), Test 2,822 (6).
- Splits are **subject-level** (no within-subject leakage between train/val/test).

## Critical Gotchas

- **MI feature leakage:** PAC features (from `pac_features.py`) are circular — they directly encode the target. Using them as model inputs inflates R² to 0.999. Only spectral features are safe for PAC prediction. See `archive/diagnostics/audit_leakage.py` for the original detection.
- **Target smoothing changes evaluation:** `target_smooth_window=5` predicts a causal denoised PAC state (R² ≈ 0.74); `target_smooth_window=1` predicts raw PAC (R² ≈ 0.07). Never compare models across different target definitions.
- **Persistence is a strong baseline at short horizons.** Always report persistence and Ridge alongside any TCN result. The TCN's value is exclusively at 3+ second horizons.
- **Dataset rebuild required if args change.** `build_multiscale_dataset.py` enforces metadata consistency. If reusing a dataset dir with different lookback/horizon/smoothing args, rebuild or pass `--allow-metadata-mismatch`.

## Commit Style

Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`. Imperative subject line (e.g., `fix: prevent subject leakage in temporal split builder`). PRs must include before/after R²/RMSE metrics when model behavior changes.
