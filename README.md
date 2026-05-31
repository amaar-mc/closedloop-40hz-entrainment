# Closed-Loop 40 Hz Gamma Entrainment System

**Adaptive scheduling of 40 Hz auditory stimulation using EEG-based PAC prediction**

> **Status:** CSEF 2026 submission complete (April 2026). Codebase is research-complete and archived.

## What This Is

A two-stage machine learning system that predicts when a patient's brain will lose gamma entrainment during 40 Hz auditory stimulation, enabling proactive adaptive scheduling that outperforms fixed and reactive protocols.

Built on OpenNeuro ds005048 (35 dementia patients, 7 frontal EEG channels, 250 Hz). Validated on real patient EEG across all 35 subjects.

**Key findings:**

- **Feature selection breakthrough (main scientific contribution):** Removing 61 spectral EEG features — which encode subject-specific brain anatomy and do not generalize — raised temporal prediction test R² from −0.025 to 0.606 ± 0.032 (5-seed mean). Using only 12 PAC trajectory + stimulation context features was more impactful than any architectural change across 8 models tested.
- **Horizon sweep:** Causal TCN maintains R² = 0.577–0.669 at 3–10 second prediction horizons where persistence collapses to negative R² — a +0.47 R² margin at the operationally relevant range for proactive control.
- **Real-data closed-loop validation (N=35):** TCN predictive controller achieves 72.1% epoch alignment vs 64.5% reactive (Hedges' g = 1.31, p < 0.001). Targets 82.6% of low-PAC windows vs 51.7% reactive (g = 4.47, p < 0.001). PAC targeting gap = 91% of theoretical oracle. All 35/35 subjects benefit (binomial p < 0.001).
- **Fatigue robustness:** Adaptive advantage grows with habituation severity (+9.0% to +11.2%, all p < 0.001) and holds across 4 fatigue model assumptions (+6.9% to +19.0%, all p < 10⁻¹³).
- **Architecture exploration:** 8 static PAC estimators tested (1,457 to ~1.1M params) — all converge to R² = 0.287 ceiling set by epoch-level label resolution, not model capacity.

See [`FINDINGS.md`](FINDINGS.md) for complete results and [`results/RESULTS_REPORT.md`](results/RESULTS_REPORT.md) for all statistics.

## Repository Structure

```
closedloop-40hz-entrainment/
|
|-- FINDINGS.md                    Consolidated results & analysis (start here)
|-- CLAUDE.md                      Development instructions for Claude Code
|-- config.yaml                    Runtime configuration (all hyperparameters)
|-- requirements.txt               Python dependencies
|
|-- src/                           Core pipeline: data loading, models, control
|   |-- data_loader.py               BIDS data loading (.set/.fdt HDF5 pairs)
|   |-- preprocessing.py             Bandpass, notch, artifact rejection, CAR
|   |-- pac_computation.py           Modulation Index (Tort 2010)
|   |-- eegnet.py                    EEGNet regression (~1,457 params)
|   |-- training.py                  Training loop (z-score targets, Huber loss)
|   |-- controller.py                Closed-loop controllers (reactive + predictive)
|   |-- personalization.py           Rolling baseline z-score module
|   |-- simulator.py                 Brain dynamics simulator (+ fatigue model)
|   |-- validation.py                Multi-strategy comparison framework
|   +-- [supporting: utils, features, augmentation, v2 variants]
|
|-- temporal_multiscale/           Temporal PAC prediction (main contribution)
|   |-- multiscale_tcn.py            MultiscaleCausalTCN architecture
|   |-- build_multiscale_dataset.py  Causal sequence construction (no leakage)
|   |-- train_multiscale_tcn.py      Training with deterministic seeding
|   |-- sweep_horizons.py            Horizon sweep: 1-10 second predictions
|   |-- realtime_inference.py        Streaming inference module
|   +-- [analysis, audits, per-subject adaptation, fatigue, transitions]
|
|-- scripts/                       Runnable scripts (moved from root)
|   |-- pipeline/                    End-to-end pipeline orchestrators
|   |   |-- run_full_pipeline.py       Preprocess → train → validate
|   |   |-- run_tcn_validation.py      Real-data TCN closed-loop (6 controllers)
|   |   |-- run_threshold_sweep.py     Threshold sensitivity analysis
|   |   |-- run_replay_analysis.py     Replay analysis on real EEG
|   |   |-- run_closed_loop_demo.py    Simulation demo: all strategies +/- fatigue
|   |   +-- run_fatigue_sensitivity.py Fatigue severity sweep
|   |-- figures/                     Publication figure generators
|   |   |-- generate_figures.py        Controller comparison, PAC targeting, etc.
|   |   |-- generate_timeline_figure.py  TCN vs reactive decision timeline
|   |   +-- generate_controller_comparison.py  Bar chart comparison
|   |-- audit/                       Leakage and pipeline integrity checks
|   |-- tools/                       Supporting PDF, QR, and figure utilities
|   +-- notebook/                    Research notebook generator (Node.js/docx)
|
|-- docs/                          Current documentation and historical research notes
|   |-- INDEX.md                     Documentation navigation
|   |-- methodology/                 CURRENT_METHODOLOGY.md, CODE_MAP.md
|   |-- audits/                      Pipeline integrity audit reports
|   |-- research/                    Background literature
|   +-- archive/                     Superseded reports and methodology notes
|
|-- results/                       Output data and reports
|   |-- RESULTS_REPORT.md            Comprehensive results with all statistics
|   |-- metrics/                     Machine-readable JSON metrics
|   |-- figures/                     Publication-quality figures (PNG + PDF)
|   +-- reports/                     Focused technical reports
|
|-- apps/                          Streamlit demonstration interfaces
|-- validation/                    Robustness validation and extended experiments
|-- models/                        Checkpoints (.pth) + training histories (.json)
|-- logs/                          Training logs and output captures
|-- paper/                         Active conference-paper planning and drafting
|-- submission/                    Completed CSEF 2026 submission archive
|-- archive/                       Superseded code, diagnostics, and notebooks
|-- data/                          Raw BIDS dataset + processed windows (not in git)
+-- venv/                          Python virtual environment (not in git)
```

## Quick Start

### Prerequisites

- Python 3.10+ with venv
- NVIDIA GPU with CUDA 11.8+ (optional but recommended)
- OpenNeuro ds005048 dataset downloaded to `data/raw/ds005048/`

### Setup

```bash
python -m venv venv
venv/Scripts/activate               # Windows
# source venv/bin/activate          # Linux/Mac

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

### Run the Full Pipeline

```bash
# Option A: Automated end-to-end pipeline
python scripts/pipeline/run_full_pipeline.py

# Option B: Step-by-step

# 1. Preprocess raw BIDS data -> windows + PAC labels
python src/data_loader.py --bids_root data/raw/ds005048 --output data/processed

# 2. Train static PAC predictor (EEGNet)
python src/training.py --data_dir data/processed --output_dir models --epochs 100

# 3. Build temporal sequences (causal, no leakage, raw targets)
python temporal_multiscale/build_multiscale_dataset.py \
  --data-dir data/processed \
  --output-dir data/processed/multiscale_temporal_lb20_hz5_ts1

# 4. Train temporal TCN
python temporal_multiscale/train_multiscale_tcn.py \
  --data-dir data/processed/multiscale_temporal_lb20_hz5_ts1 \
  --output-dir models

# 5. Sweep prediction horizons (1-10 seconds)
python temporal_multiscale/sweep_horizons.py \
  --data-dir data/processed --output-dir models

# 6. Real-data TCN closed-loop validation (primary result)
python scripts/pipeline/run_tcn_validation.py

# 7. Threshold sensitivity analysis
python scripts/pipeline/run_threshold_sweep.py

# 8. Closed-loop simulation with fatigue comparison
python scripts/pipeline/run_closed_loop_demo.py --duration 600 --n-trials 50

# 9. Fatigue sensitivity analysis
python scripts/pipeline/run_fatigue_sensitivity.py

# 10. Generate publication figures
python scripts/figures/generate_figures.py
python scripts/figures/generate_timeline_figure.py
```

### Run Audits

```bash
python scripts/audit/validate_leakage.py                  # Pre-training leakage check
python temporal_multiscale/audit_multiscale_pipeline.py    # Pipeline audit
python temporal_multiscale/comprehensive_submission_audit.py  # Submission audit
```

## Models

### Stage 1 — EEGNet (Static PAC Estimation)

Estimates current PAC from a single 2-second EEG window. Feeds Stage 2.

- Input: `(batch, 1, 7, 500)` — 7 frontal channels, 2s @ 250 Hz
- Output: `(batch, 1)` — current PAC estimate
- Parameters: ~1,457
- Test R²: 0.287 (ceiling — epoch-level labels on 2s windows, not a model capacity limit)
- 8 architectures explored (EEGNet to 1.1M-param ViT-TCNet); all converge to same R² = 0.287

### Stage 2 — Multiscale Causal TCN (Temporal PAC Prediction)

Predicts future PAC (5s horizon) from a 20-second causal history. Main contribution.

- Input: `(batch, 20, 12)` — 12 PAC+Stim features × 20 timesteps (lookback)
- Features: PAC trajectory (7: current + 4 trailing means + 2 differences) + stimulation context (5: state, time-since-switch, stim fraction, cycle sin/cos)
- Architecture: dilated causal depthwise-separable conv, dilations [1, 2, 4, 8], GroupNorm, attention pooling, dual head (future PAC + delta-PAC)
- Parameters: 5,154 (h=32)
- Test R²: 0.606 ± 0.032 (5-seed mean) | Horizon 3–10s R²: 0.577–0.669
- Checkpoint: `models/best_12feat_tcn_lb20_hz5_ts1.pth`

**Feature ablation (key result):**

| Feature Subset | # Features | Val R² | Test R² |
|---|---|---|---|
| All features (73) | 73 | 0.333 | −0.025 |
| Spectral only (61) | 61 | −0.044 | −0.420 |
| **PAC + Stim context** | **12** | **0.804** | **0.558** |

Spectral features (indices 0–60) encode subject-specific anatomy that does not generalize. Removing them is the core scientific finding.

## Results Summary

### Horizon Sweep (12-feat PAC+Stim TCN)

| Horizon | Persistence R² | Ridge R² | TCN R² |
|---------|----------------|----------|--------|
| 1 sec | ~0.76 | ~0.81 | ~0.74 |
| 3 sec | −0.081 | negative | **0.577** |
| 5 sec | negative | negative | **0.606** |
| 10 sec | negative | negative | **0.669** |

At 3–10 seconds — the operationally relevant range for proactive control — only the TCN provides useful predictions (+0.47 R² margin over persistence at collapse).

### Real-Data Closed-Loop Validation (N=35 subjects)

| Controller | Alignment | Low-PAC Targeting | PAC Gap (uV^2) |
|-----------|-----------|-------------------|----------------|
| Fixed Schedule | 45.0% | 61.4% | -6.6 (wrong direction) |
| Reactive | 64.5% | 51.7% | +21.1 |
| **TCN Predictive** | **72.1%** | **82.6%** | **+30.5** |
| Oracle | 100.0% | 100.0% | +33.3 |

TCN vs Reactive (Wilcoxon signed-rank, all p < 0.001): Alignment g = +1.31, Low-PAC targeting g = +4.47, PAC gap g = +1.57. TCN reaches 91% of oracle bound. 35/35 subjects benefit.

### Adaptive Scheduling Efficiency

| Fatigue Level | Fixed Efficiency | Adaptive Efficiency | Gain | p-value |
|---------------|-----------------|--------------------|----- |---------|
| None | 0.343 | 0.375 | +9.5% | < 0.001 |
| Severe | 0.316 | 0.352 | +11.2% | < 0.001 |

Advantage holds across all 6 fatigue levels and 4 different fatigue model assumptions (+6.9% to +19.0%, all p < 10^-13).

Full results: [`FINDINGS.md`](FINDINGS.md) | [`results/RESULTS_REPORT.md`](results/RESULTS_REPORT.md)

## Dataset

**OpenNeuro ds005048 v1.0.1** -- 40 Hz Auditory Entrainment in Dementia

- 35 subjects, 19-channel EEG (10/20), 250 Hz
- Alternating 40s stimulation / 20s rest blocks
- BIDS-compliant, HDF5 .set files + float32 .fdt companion files
- Download: https://openneuro.org/datasets/ds005048/versions/1.0.1

## Citations

1. Iaccarino et al. (2016). Gamma frequency entrainment attenuates amyloid load. *Nature*, 540, 230-235.
2. Tort et al. (2010). Measuring phase-amplitude coupling. *J Neurophysiology*, 104(2), 1195-1210.
3. Lawhern et al. (2018). EEGNet: compact CNN for EEG-based BCIs. *J Neural Engineering*, 15(5), 056013.
4. Lahijanian et al. (2024). Auditory gamma-band entrainment enhances default mode network connectivity in dementia patients. *Scientific Reports*, 14, 13153.

## Author

Amaar Chughtai | CSEF 2026 — submitted April 2026

## License

Research code for academic and educational purposes. Dataset: OpenNeuro ds005048 (CC0).
