# Closed-Loop 40 Hz Gamma Entrainment System

**Adaptive scheduling of 40 Hz auditory stimulation using EEG-based PAC prediction**

## What This Is

A machine learning system that predicts when a person's brain will lose gamma entrainment during 40 Hz auditory stimulation, enabling adaptive scheduling that achieves comparable neural effects with significantly less stimulation than fixed-schedule protocols.

Built on the OpenNeuro ds005048 dataset (35 dementia patients, 19-channel EEG, 250 Hz).

**Key results:**
- **Horizon sweep:** The causal TCN maintains R^2 = 0.24-0.28 at 5-10 second prediction horizons where all baselines collapse to negative R^2 — a +0.5 R^2 margin over persistence and Ridge regression.
- **Real-data closed-loop validation (N=35 subjects):** The TCN predictive controller achieves 72.1% epoch alignment vs 64.5% for reactive control (Hedges' g = 1.31, p < 0.001). It targets 82.6% of low-PAC windows for stimulation vs 51.7% reactive (g = 4.47, p < 0.001). PAC targeting gap reaches 91% of the theoretical oracle bound. All 35/35 subjects benefit (binomial p < 0.001).
- **Fatigue robustness:** Adaptive scheduling advantage grows with habituation severity (+9.0% to +11.2%, all p < 0.001) and holds across 4 different fatigue model assumptions (+6.9% to +19.0%, all p < 10^-13).

See [`FINDINGS.md`](FINDINGS.md) for the complete results and [`results/RESULTS_REPORT.md`](results/RESULTS_REPORT.md) for all statistics.

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
|   |-- per_subject_adaptation.py    Per-subject fine-tuning evaluation
|   |-- transition_analysis.py       Stim/rest transition accuracy
|   |-- direction_classifier.py      3-class PAC direction prediction
|   |-- fatigue_analysis.py          Real-data habituation analysis
|   |-- realtime_inference.py        Streaming inference module
|   +-- [audits: audit_multiscale_pipeline, comprehensive_submission_audit]
|
|-- temporal/                      Earlier temporal models (v1, superseded)
|   |-- temporal_model.py            LSTM-based temporal model
|   |-- validate_code.py             Pre-training leakage validation
|   +-- [training scripts, dataset builders]
|
|-- run_full_pipeline.py            End-to-end pipeline (preprocess → train → validate)
|-- run_tcn_validation.py           Real-data TCN closed-loop validation (6 controllers)
|-- run_threshold_sweep.py          TCN threshold sensitivity analysis
|-- run_replay_analysis.py          Replay analysis on real EEG data
|-- run_closed_loop_demo.py         Simulation demo: all strategies +/- fatigue
|-- run_fatigue_sensitivity.py      Fatigue severity sweep (6 levels x 4 models)
|-- generate_figures.py             Publication figures (controller comparison, etc.)
|-- generate_timeline_figure.py     Timeline visualization (TCN vs reactive decisions)
|
|-- docs/                          Documentation
|   |-- INDEX.md                     Documentation navigation
|   |-- CURRENT_METHODOLOGY.md       Pipeline methodology
|   |-- CODE_MAP.md                  Architecture reference
|   |-- research/                    Background literature (.docx/.txt)
|   |-- reports/                     Technical analysis reports
|   |-- audits/                      Pipeline integrity audit reports
|   +-- archive/                     Outdated pre-multiscale docs
|
|-- results/                       Output data and reports
|   |-- RESULTS_REPORT.md            Comprehensive results with all statistics
|   |-- tcn_validation_results.json  TCN closed-loop validation output
|   |-- threshold_sweep.json         Threshold sensitivity data
|   |-- closed_loop_demo_results.json
|   |-- fatigue_analysis.json
|   |-- fatigue_sensitivity.json
|   +-- figures/                     Publication-quality figures (PNG + PDF)
|       |-- controller_comparison.png
|       |-- pac_targeting_gap.png
|       |-- per_subject_utility.png
|       |-- stim_vs_alignment.png
|       |-- timeline_example.png
|       +-- threshold_sensitivity.png
|
|-- models/                        Checkpoints (.pth) + training histories (.json)
|-- logs/                          Training logs and output captures
|-- archive/                       Old code: v1-v8 attempts, diagnostics
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
python run_full_pipeline.py

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
python run_tcn_validation.py

# 7. Threshold sensitivity analysis
python run_threshold_sweep.py

# 8. Closed-loop simulation with fatigue comparison
python run_closed_loop_demo.py --duration 600 --n-trials 50

# 9. Fatigue sensitivity analysis
python run_fatigue_sensitivity.py

# 10. Generate publication figures
python generate_figures.py
python generate_timeline_figure.py
```

### Run Audits

```bash
python temporal/validate_code.py                          # Pre-training leakage check
python temporal_multiscale/audit_multiscale_pipeline.py    # Pipeline audit
python temporal_multiscale/comprehensive_submission_audit.py  # Submission audit
```

## Models

### EEGNet (Static PAC Prediction)

Predicts PAC from a single 2-second EEG window.

- Input: `(batch, 1, 7, 500)` -- 7 frontal channels, 2s @ 250 Hz
- Output: `(batch, 1)` -- predicted PAC
- Parameters: ~1,457
- Test R^2: 0.287

### Multiscale Causal TCN (Temporal PAC Prediction)

Predicts future PAC from a sequence of past observations. Main contribution.

- Input: `(batch, seq_len, n_features)` -- PAC + stimulation context
- Causal depthwise-separable convolutions, dilations [1, 2, 4, 8]
- GroupNorm (cross-subject stable), attention pooling, dual regression heads
- R^2 at horizon=1: 0.74 | R^2 at horizon=5-10: 0.24-0.28 (baselines: negative)

## Results Summary

### Horizon Sweep (TCN Prediction)

| Horizon | Persistence R^2 | Ridge R^2 | TCN R^2 |
|---------|-----------------|-----------|---------|
| 1 sec | 0.76 | **0.81** | 0.74 |
| 5 sec | -0.27 | -0.39 | **0.25** |
| 10 sec | -0.26 | -0.21 | **0.28** |

At 5-10 seconds — the operationally relevant range for proactive control — only the TCN provides useful predictions (+0.5 R^2 margin over all baselines).

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

Amaar Chughtai | February 2026

## License

Research code for academic and educational purposes. Dataset: OpenNeuro ds005048 (CC0).
