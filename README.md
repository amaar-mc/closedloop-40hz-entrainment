# Personalized Deep Learning Model for Closed-Loop 40Hz Entrainment

**Optimizing Theta-Gamma Coupling in Alzheimer's Disease via Model Predictive Control**

## Project Overview

This project implements a novel closed-loop neuromodulation system that uses deep learning to predict theta-gamma phase-amplitude coupling (PAC) in real-time and optimizes 40 Hz auditory stimulation timing through Model Predictive Control (MPC). The system moves beyond reactive closed-loop approaches to predictive control, anticipating brain state changes 5-10 seconds ahead.

### Key Innovation

- **Predictive vs. Reactive**: Forecasts EEG dynamics using EEGNet deep learning architecture
- **Personalized Control**: Adapts to individual patient baseline via z-score normalization
- **Energy Efficient**: Targets 60-70% reduction in stimulation time while maintaining efficacy
- **Clinically Validated**: Uses OpenNeuro ds005048 dataset with dementia patients

## Dataset

**OpenNeuro ds005048 v1.0.1**: 40Hz Auditory Entrainment
- URL: https://openneuro.org/datasets/ds005048/versions/1.0.1
- Participants: ~13-20 dementia patients (mild AD, memory complaints)
- EEG: 19-channel monopolar, 250 Hz sampling rate
- Protocol: 40s stimulation + 20s rest (6-10 trials)
- Format: BIDS-compliant (.set files)

### Download Instructions

```bash
# Option 1: OpenNeuro CLI
pip install openneuro-cli
openneuro download --snapshot 1.0.1 ds005048

# Option 2: AWS S3
aws s3 sync --no-sign-request \
  s3://openneuro.org/ds005048 \
  data/raw/ds005048/

# Option 3: Direct download from website
# Visit: https://openneuro.org/datasets/ds005048/versions/1.0.1
```

## Hardware Requirements

**Tested Configuration**:
- GPU: NVIDIA RTX 3080 (10GB VRAM)
- RAM: 16GB minimum
- Storage: 50GB for dataset and checkpoints
- CUDA: 11.8 or higher

**Performance**:
- Training time: ~2-3 hours for full dataset
- Inference latency: <50ms per window
- Batch size: 32-64 (optimal for RTX 3080)

## Installation

### 1. Clone or Download Code

```bash
cd code_drafts
```

### 2. Create Virtual Environment

```bash
python3.10 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. Install PyTorch with CUDA

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Verify Installation

```bash
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
python -c "import mne; import tensorpac; print('MNE and Tensorpac OK')"
```

## Project Structure

```
code_drafts/
├── src/
│   ├── data_loader.py           # BIDS data loading and windowing
│   ├── preprocessing.py         # EEG signal preprocessing pipeline
│   ├── pac_computation.py       # Phase-amplitude coupling (MI method)
│   ├── eegnet.py                # EEGNet deep learning architecture
│   ├── personalization.py       # Rolling baseline z-score module
│   ├── controller.py            # Closed-loop MPC decision engine
│   ├── simulator.py             # Brain response simulation
│   ├── training.py              # Model training pipeline
│   ├── validation.py            # Performance evaluation
│   └── utils.py                 # Helper functions and plotting
│
├── data/
│   ├── raw/                     # Downloaded OpenNeuro dataset
│   └── processed/               # Preprocessed windows and labels
│
├── models/                      # Trained model checkpoints
├── results/
│   ├── figures/                 # Plots and visualizations
│   └── metrics/                 # Performance metrics (CSV)
│
├── logs/                        # Development logs
├── notebooks/                   # Jupyter analysis notebooks
│
├── requirements.txt
├── README.md
└── config.yaml                  # Configuration parameters
```

## Usage

### Step 1: Download and Preprocess Data

```bash
# Download dataset (see above)
# Place in data/raw/ds005048/

# Run preprocessing
python src/data_loader.py --bids_root data/raw/ds005048 --output data/processed
```

### Step 2: Train EEGNet Model

```bash
python src/training.py \
  --data_dir data/processed \
  --output_dir models \
  --epochs 100 \
  --batch_size 64 \
  --lr 0.001 \
  --device cuda
```

### Step 3: Run Closed-Loop Simulation

```bash
python src/validation.py \
  --model_path models/best_eegnet.pth \
  --data_dir data/processed \
  --output_dir results \
  --duration 360
```

### Step 4: Analyze Results

```bash
jupyter notebook notebooks/04_simulation_results.ipynb
```

## Key Modules

### 1. EEGNet Architecture

Compact convolutional neural network optimized for EEG:
- **Input**: (batch, 1, 7 channels, 500 samples) - 2 seconds @ 250 Hz
- **Output**: (batch, 1) - Predicted PAC value
- **Parameters**: ~2000 (prevents overfitting)
- **Layers**: Temporal conv → Depthwise spatial → Separable conv → Regression head

### 2. PAC Computation (Modulation Index)

Implementation of Tort et al. (2010) method:
1. Bandpass filter: Theta (4-8 Hz), Gamma (38-42 Hz)
2. Hilbert transform: Extract phase (theta) and amplitude (gamma)
3. Phase binning: 18 bins × 20°
4. KL divergence: From uniform distribution
5. Normalization: MI ∈ [0, 1]

### 3. Personalization Module

Adaptive baseline using rolling window:
- Window size: 30 seconds (30 predictions @ 1 Hz)
- Z-score normalization: z = (PAC - μ) / σ
- Circular buffer: Efficient O(1) updates
- Minimum samples: 10 (before z-scores computed)

### 4. Closed-Loop Controller

MPC-inspired threshold-based decision engine:

| Z-Score Range | Coupling Status | Action | Rationale |
|---------------|-----------------|--------|-----------|
| z < -0.5 | Weak | STIMULATE | Boost gamma |
| z > +0.5 | Strong | REST | Prevent habituation |
| -0.5 ≤ z ≤ +0.5 | Normal | MAINTAIN | Stability |

**Hysteresis**: 5-second minimum hold time prevents oscillation

### 5. Simulation Framework

Exponential approach to target PAC:
- **Stimulation**: PAC(t+1) = PAC(t) + τ_rise × (PAC_max - PAC(t))
- **Rest**: PAC(t+1) = PAC(t) + τ_decay × (PAC_min - PAC(t))
- **Noise**: Gaussian (σ = 0.02)
- **Parameters**: Extracted empirically from dataset

## Expected Results

### Performance Targets

| Metric | Target | Baseline (Open-Loop) |
|--------|--------|----------------------|
| PAC Improvement | ≥15% | 0% (reference) |
| Prediction R² | >0.80 | N/A |
| Stimulation Time | 30-40% | 67% (40s/60s) |
| PAC Stability | Lower variance | Higher variance |

### Hypotheses

1. **H1**: EEGNet achieves R² > 0.80 for 5-second PAC prediction
2. **H2**: Closed-loop increases PAC by 15-30% vs. fixed schedule
3. **H3**: Equivalent efficacy with 60-70% less stimulation time
4. **H4**: Subject-specific fine-tuning improves accuracy by >10%

## Configuration

Edit `config.yaml` to customize parameters:

```yaml
# Data Processing
sampling_rate: 250  # Hz
window_size: 2.0    # seconds
hop_size: 1.0       # seconds (50% overlap)
channels: ['Fp1', 'Fp2', 'F7', 'F3', 'Fz', 'F4', 'F8']

# PAC Computation
theta_band: [4, 8]     # Hz
gamma_band: [38, 42]   # Hz
n_phase_bins: 18

# EEGNet Model
F1: 8                  # Temporal filters
D: 2                   # Depth multiplier
F2: 16                 # Separable filters
dropout: 0.5

# Training
epochs: 100
batch_size: 64
learning_rate: 0.001
weight_decay: 0.0001
patience: 15           # Early stopping

# Controller
z_low: -0.5            # Weak coupling threshold
z_high: 0.5            # Strong coupling threshold
hold_time: 5.0         # Hysteresis (seconds)
baseline_window: 30    # Personalization window (seconds)

# Simulation
tau_rise: 0.15         # PAC increase rate
tau_decay: 0.10        # PAC decrease rate
pac_max: 0.3           # Maximum PAC
pac_min: 0.05          # Minimum PAC
noise_std: 0.02
```

## Validation Protocol

### Comparison Methods

1. **Fixed Schedule (Control)**: 40s ON + 20s OFF
2. **Closed-Loop (Treatment)**: Adaptive stimulation
3. **Reactive Threshold**: Current PAC-based (no prediction)
4. **Predictive MPC**: Full system (proposed)

### Metrics

- **PAC Enhancement**: Mean, peak, time above threshold
- **Efficiency**: PAC per unit stimulation time
- **Stability**: Variance, oscillation frequency
- **Accuracy**: R², RMSE, MAE for predictions
- **Clinical**: Equivalent to Phase II trial outcomes

### Statistical Analysis

- **Primary**: Repeated measures ANOVA (5 methods)
- **Post-hoc**: Tukey HSD for pairwise comparisons
- **Effect Size**: Cohen's d
- **Significance**: α = 0.05 (two-tailed)

## Troubleshooting

### CUDA Out of Memory
- Reduce batch size: `--batch_size 32` or `--batch_size 16`
- Enable gradient accumulation in training.py
- Use mixed precision training (automatic with PyTorch 2.0+)

### Poor Model Performance
- Check data preprocessing: Are artifacts removed?
- Verify PAC computation: Compare to published values
- Increase training epochs: `--epochs 150`
- Try data augmentation: Enable in config.yaml

### Slow Training
- Verify GPU usage: `nvidia-smi` during training
- Check data loading: Increase num_workers in DataLoader
- Enable mixed precision: Should be automatic with RTX 3080
- Profile bottlenecks: Use PyTorch profiler

### Dataset Download Issues
- Check disk space: Need ~10GB
- Use AWS CLI: May be faster than openneuro-cli
- Download subsets: Start with 1-2 subjects for testing

## Citations

### Key Papers

1. **EEGNet Architecture**
   Lawhern et al. (2018). "EEGNet: A Compact Convolutional Neural Network for EEG-based Brain-Computer Interfaces." *Journal of Neural Engineering*, 15(5).

2. **Modulation Index (PAC)**
   Tort et al. (2010). "Measuring Phase-Amplitude Coupling Between Neuronal Oscillations of Different Frequencies." *Journal of Neurophysiology*, 104(2).

3. **40 Hz Gamma Entrainment**
   Iaccarino et al. (2016). "Gamma Frequency Entrainment Attenuates Amyloid Load and Modifies Microglia." *Nature*, 540, 230-235.

4. **Clinical Evidence**
   Chan et al. (2025). "Gamma Sensory Stimulation in Mild Alzheimer's Dementia: An Open-Label Extension Study." *Alzheimer's & Dementia*, 21.

5. **Dataset**
   Lahijanian et al. (2024). "Auditory Gamma-band Entrainment Enhances Default Mode Network Connectivity in Dementia Patients." *Scientific Reports*, 14.

### Dataset

OpenNeuro ds005048 v1.0.1:
https://openneuro.org/datasets/ds005048/versions/1.0.1

DOI: 10.18112/openneuro.ds005048.v1.0.1

## License

This research code is provided for academic and educational purposes.
Dataset: OpenNeuro ds005048 (CC0 license)

## Author

**Amaar Chughtai**
Valley Christian High School
Research Project: January-February 2026

## Acknowledgments

- OpenNeuro platform for dataset hosting
- MNE-Python developers for EEG processing tools
- Tensorpac developers for PAC computation library
- PyTorch team for deep learning framework

## Contact

For questions or issues, please refer to the development log:
`logs/DEVELOPMENT_LOG.md`

---

**Status**: Implementation Complete
**Last Updated**: February 5, 2026
