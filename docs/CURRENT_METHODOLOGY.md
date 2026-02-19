# Current Methodology: Closed-Loop 40Hz Entrainment via Temporal PAC Forecasting

**Last Updated:** 2026-02-18
**Status:** Implemented and audited. Results audited for leakage and correctness.

This document describes the methodology **as actually implemented and tested**, not the originally proposed approach. For the original proposal, see `archive_pre_multiscale/`.

---

## 1. Research Objective

Develop a personalized closed-loop system that predicts theta-gamma phase-amplitude coupling (PAC) in real-time to optimize 40 Hz auditory stimulation timing for Alzheimer's disease patients, moving from reactive to predictive control.

**Core hypothesis:** If future PAC can be predicted ahead of time, stimulation decisions can be made proactively rather than reactively, reducing unnecessary stimulation while maintaining efficacy.

---

## 2. Dataset

**Source:** OpenNeuro ds005048 v1.0.1 — "40Hz Auditory Entrainment" (Lahijanian et al., 2024)

| Property | Value |
|----------|-------|
| Subjects | 35 (dementia patients from memory clinic in Tehran) |
| EEG channels | 19 monopolar (10/20 system) |
| Sampling rate | 250 Hz |
| File format | BIDS-compliant; .set files are MATLAB v7.3 (HDF5); actual data in companion .fdt files (float32, Fortran/column-major order) |
| Protocol | 40 Hz pulse train: 40s stimulation + 20s rest per trial (6 short-session, 10 long-session) |
| Preprocessing | Already applied by Makoto's pipeline: 1 Hz HP, 50 Hz notch, ICA, CAR |

**Important data facts:**
- The .set HDF5 files have fields at the **top level** (no `EEG` wrapper group).
- The `data` field contains a filename reference (uint16 chars), not actual EEG.
- Actual data is read from .fdt files with `np.fromfile(dtype=float32)` and reshaped with `order='F'`.

---

## 3. Data Processing Pipeline

### 3.1 Raw Data Loading (`src/data_loader.py`)

1. Load .set/.fdt pairs via custom HDF5 reader (MNE's `read_raw_eeglab` fails on v7.3 format).
2. Select 7 frontal channels: Fp1, Fp2, F7, F3, Fz, F4, F8.
3. Apply light preprocessing: bandpass 0.5-80 Hz, 50 Hz notch, artifact rejection (+-100 uV threshold), CAR.
4. Segment by BIDS events.tsv: extract Stimulus and Rest epochs.
5. Compute epoch-level PAC (Modulation Index, Tort 2010) from full 20-40s epochs for stable labels.
6. Extract 2-second sliding windows (500 samples) with 1-second hop (50% overlap).
7. Assign epoch-level PAC to all constituent windows.

**Output:** `data/processed/{train,val,test}_data.npz`
- Windows: `(n, 1, 7, 500)` in microvolts
- PAC labels: scalar per window, range [0.0002, 0.0046], mean ~0.001
- Subject-level splits: 24 train / 5 val / 6 test (seed=42, no subject leakage)
- Total: 17,283 windows (train 11,736, val 2,725, test 2,822)

### 3.2 Spectral Feature Extraction (`temporal/temporal_dataset.py`)

Per-window spectral features (61 dimensions) computed independently per split:
- Band power in 5 frequency bands (delta, theta, alpha, beta, gamma) across 7 channels
- Cross-channel spectral coherence
- Saved as `{split}_spectral_cache.npy`

### 3.3 Multiscale Temporal Dataset (`temporal_multiscale/build_multiscale_dataset.py`)

Constructs causal temporal sequences for forecasting:

**Features per timestep (73 total):**
- 61 spectral features (per-window, from cache)
- 7 PAC-derived features: `pac_current`, `pac_ma2`, `pac_ma4`, `pac_ma8`, `pac_ma16`, `pac_diff1`, `pac_diff4`
- 5 stimulation context features: `stim_state`, `time_since_switch`, `stim_frac_20s`, `cycle_phase_sin`, `cycle_phase_cos`

**Sequence construction:**
- Lookback = 20 steps (20 seconds of history)
- Horizon = 1 step (1 second ahead)
- Target smoothing: 5-step causal trailing mean applied to PAC targets before defining y_future
- Per-subject sequence building (no cross-subject sequences)
- y_delta = y_future - y_current (change prediction)

**Normalization:** Z-score normalization with **train-only** statistics:
- Feature-wise mean/std computed from flattened train sequences
- y_future and y_delta mean/std from train targets
- Applied to all splits

---

## 4. Model Architecture

### 4.1 Static PAC Prediction: EEGNet (`src/eegnet.py`)

- Input: `(batch, 1, 7, 500)` → Output: `(batch, 1)`
- Block 1: Temporal conv (1→8 filters, kernel=64) + depthwise spatial (D=2) + BN + ELU + AvgPool
- Block 2: Separable pointwise (8→16 filters) + BN + ELU + AvgPool
- FC head: regression to scalar PAC
- Parameters: ~1,457
- **Performance: R^2 = 0.287** on held-out test subjects

### 4.2 Temporal PAC Forecasting: MultiscaleCausalTCN (`temporal_multiscale/multiscale_tcn.py`)

- Input: `(batch, T=20, F=73)` → Output: future PAC + delta PAC
- Input projection: Linear(73→64) + LayerNorm + SiLU
- 4x CausalDSConvBlock: depthwise separable conv (kernel=3, dilation=[1,2,4,8]), BatchNorm, SiLU, residual connections
- Causal padding: `F.pad(x, (pad, 0))` ensures no future information
- AttentionPool1D: learned attention weights over time axis
- Two regression heads: future_head and delta_head (each: Linear→SiLU→Dropout→Linear)
- Parameters: 31,043
- **Performance: R^2 = 0.7423 on test** (but see audit caveats below)

### 4.3 Training Configuration

| Parameter | Value |
|-----------|-------|
| Loss | Huber (delta=1.0) + 0.5 * Huber(delta) + 0.1 * consistency |
| Optimizer | AdamW (lr=1e-3, weight_decay=1e-4) |
| Scheduler | ReduceLROnPlateau (mode=max, factor=0.5, patience=5) |
| Gradient clipping | max_norm=1.0 |
| Early stopping | patience=10 on val_future_r^2 |
| Batch size | 128 |
| Best epoch | 14 of 24 (early stopped) |

---

## 5. Closed-Loop Control System

### 5.1 Controller (`src/controller.py`)

Threshold-based decision engine with hysteresis:

| Condition | Action | Rationale |
|-----------|--------|-----------|
| z < -0.5 | STIMULATE | PAC below baseline, boost gamma |
| z > +0.5 | REST | PAC above baseline, prevent habituation |
| else | MAINTAIN | Stable coupling |

Hysteresis: 5-second minimum hold time prevents oscillation.

### 5.2 Personalization (`src/personalization.py`)

Rolling 30-second circular buffer for subject-specific baseline:
- z-score: `z = (PAC_current - mean) / std`
- Minimum 10 samples before computing z-scores

### 5.3 Simulation (`src/simulator.py`)

Brain response model (exponential approach):
- Stimulation: `PAC(t+1) = PAC(t) + 0.15 * (0.3 - PAC(t)) + noise`
- Rest: `PAC(t+1) = PAC(t) + 0.10 * (0.05 - PAC(t)) + noise`
- Gaussian noise sigma = 0.02

### 5.4 Validation (`src/validation.py`)

Compares 4 strategies: Fixed Schedule, Reactive Threshold, Predictive MPC, Oracle.
Statistical analysis: repeated measures ANOVA, Tukey HSD, Cohen's d.

---

## 6. Results and Audit Findings

### 6.1 Verified Results (as of 2026-02-18)

| Metric | Value | Source |
|--------|-------|--------|
| Static EEGNet test R^2 | 0.287 | `src/training.py` |
| TCN test future R^2 (ts=5, hz=1) | 0.7423 | `summary_multiscale_tcn_lb20_hz1_ts5_audit.json` |
| TCN test delta R^2 | 0.2219 | Same |
| Persistence baseline R^2 | 0.7600 | `comprehensive_audit_multiscale_ts5_clean.json` |
| Ridge (all features) R^2 | 0.8120 | Same |
| Ridge (PAC only) R^2 | 0.8589 | Same |
| TCN with PAC zeroed R^2 | 0.0464 | `deployment_audit_multiscale_ts5_clean.json` |
| Raw target (ts=1) test R^2 | ~0.07 | `TEMPORAL_PREDICTION_DEEP_DIVE.md` |

### 6.2 Audit Integrity Checks (all PASS)

- No subject overlap between train/val/test
- Temporal causality verified for all samples
- Normalization scalers fit on training data only
- Shuffle-label sanity: R^2 = -0.33 (correct — labels matter)
- No future information leakage in feature construction

### 6.3 Critical Audit Findings

**Finding 1: TCN does not beat persistence.**
The persistence baseline (R^2 = 0.76) outperforms the TCN (R^2 = 0.74). The neural network adds negative marginal value over simply predicting "future PAC = current PAC."

**Finding 2: Target smoothing inflates R^2.**
With unsmoothed targets (ts=1), prediction R^2 drops to ~0.07 — essentially random. The smoothing window of 5 shares 4/5 data points between adjacent smoothed values, making prediction trivially autocorrelated.

**Finding 3: Complete PAC oracle dependency.**
Zeroing PAC features collapses R^2 from 0.74 to 0.05. The model learns nothing from spectral or context features — it is entirely a PAC autoregressive model.

**Finding 4: Linear model outperforms neural network.**
Ridge regression on the same features achieves R^2 = 0.81, beating both the TCN and persistence. The nonlinear capacity of the TCN is not utilized.

**Finding 5: No random seed set.**
`temporal_multiscale/train_multiscale_tcn.py` does not set numpy/torch seeds, so results are not reproducible across runs.

---

## 7. Interpretation

The fundamental finding is that **PAC temporal prediction from this dataset is hard** (raw R^2 ~0.07) due to:

1. **Target noise**: 2-second window PAC estimates are noisy; only epoch-level (20-40s) estimates are stable.
2. **Missing exogenous drivers**: The model cannot observe the stimulation device state in deployment.
3. **Cross-subject heterogeneity**: Individual differences in brain anatomy and pathology.
4. **Autocorrelation ceiling**: PAC changes slowly, so persistence is a strong baseline that is hard to beat.

Target smoothing creates a tractable regression problem (R^2 ~0.75) but this reflects **latent coupling state predictability**, not raw PAC forecasting ability. This distinction must be clearly communicated in any publication.

The practical recommendation: for closed-loop control, use the smoothed PAC state as a denoised biomarker of coupling strength, with the understanding that the "prediction" is primarily temporal persistence of the latent state.

---

## 8. File Map

| File | Purpose |
|------|---------|
| `src/data_loader.py` | BIDS loading, windowing, subject-level splitting |
| `src/preprocessing.py` | Bandpass, notch, artifact rejection, CAR |
| `src/pac_computation.py` | Modulation Index (Tort 2010) |
| `src/eegnet.py` | Static PAC prediction model |
| `src/training.py` | EEGNet training loop |
| `src/controller.py` | Threshold-based closed-loop controller |
| `src/personalization.py` | Rolling baseline z-score |
| `src/simulator.py` | Brain response simulation |
| `src/validation.py` | Strategy comparison framework |
| `temporal_multiscale/build_multiscale_dataset.py` | Causal sequence construction |
| `temporal_multiscale/multiscale_tcn.py` | Causal TCN architecture |
| `temporal_multiscale/train_multiscale_tcn.py` | TCN training loop |
| `temporal_multiscale/audit_multiscale_pipeline.py` | Dataset integrity audit |
| `temporal_multiscale/comprehensive_submission_audit.py` | Submission-grade audit |
| `temporal_multiscale/checkpoint_deployment_audit.py` | Deployment realism audit |
| `config.yaml` | Centralized runtime parameters |
