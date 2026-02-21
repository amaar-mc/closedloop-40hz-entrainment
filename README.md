# Closed-Loop 40 Hz Gamma Entrainment System

**Adaptive scheduling of 40 Hz auditory stimulation using EEG-based PAC prediction**

## What This Is

A machine learning system that predicts when a person's brain will lose gamma entrainment during 40 Hz auditory stimulation, enabling adaptive scheduling that achieves comparable neural effects with significantly less stimulation than fixed-schedule protocols.

Built on the OpenNeuro ds005048 dataset (35 dementia patients, 19-channel EEG, 250 Hz).

**Key result:** The temporal prediction model (causal TCN) maintains R^2 ~ 0.25 at 5-10 second prediction horizons where all baselines fail (persistence R^2 < -0.25). The adaptive controller is statistically more efficient than fixed scheduling (Wilcoxon p < 0.01) and the advantage grows with habituation severity.

See [`FINDINGS.md`](FINDINGS.md) for the complete results and analysis.

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
|-- run_closed_loop_demo.py        End-to-end demo: all strategies +/- fatigue
|-- run_fatigue_sensitivity.py     Fatigue severity sweep
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
|-- results/                       Output data
|   |-- closed_loop_demo_results.json
|   |-- fatigue_analysis.json
|   +-- fatigue_sensitivity.json
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
# 1. Preprocess raw BIDS data -> windows + PAC labels
python src/data_loader.py --bids_root data/raw/ds005048 --output data/processed

# 2. Train static PAC predictor (EEGNet)
python src/training.py --data_dir data/processed --output_dir models --epochs 100

# 3. Build temporal sequences (causal, no leakage)
python temporal_multiscale/build_multiscale_dataset.py \
  --data-dir data/processed \
  --output-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean

# 4. Train temporal TCN
python temporal_multiscale/train_multiscale_tcn.py \
  --data-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean \
  --output-dir models

# 5. Sweep prediction horizons (1-10 seconds)
python temporal_multiscale/sweep_horizons.py \
  --data-dir data/processed --output-dir models

# 6. Run closed-loop simulation with fatigue comparison
python run_closed_loop_demo.py --duration 600 --n-trials 10

# 7. Run fatigue sensitivity analysis
python run_fatigue_sensitivity.py
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
- R^2 at horizon=1: 0.764 | R^2 at horizon=5-10: ~0.25 (baselines: negative)

## Results Summary

| Metric | Value |
|--------|-------|
| TCN test R^2 (1s ahead) | 0.764 |
| TCN R^2 (5-10s ahead) | 0.24 - 0.28 |
| Persistence R^2 (5-10s) | -0.26 to -0.27 |
| Adaptive vs Fixed efficiency | +2.1% to +5.7% (p < 0.01) |
| Stimulation time saved | 14-18 percentage points |

Full results: [`FINDINGS.md`](FINDINGS.md)

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
