# Methodology and Technical Architecture

## 1. Dataset

**OpenNeuro ds005048 v1.0.1** — "40 Hz Auditory Entrainment in Dementia" (Lahijanian et al., 2024)

- 35 elderly dementia patients from a memory clinic in Tehran, Iran
- 19 monopolar EEG channels (10/20 international system), 250 Hz sampling rate
- Stimulation protocol: 40 Hz amplitude-modulated auditory pulses (5 kHz carrier, 4% duty cycle)
- Design: alternating 40-second stimulation / 20-second rest epochs
- File format: BIDS-compliant .set files (MATLAB v7.3 HDF5) with companion .fdt files (float32, Fortran/column-major order)
- Data already preprocessed upstream by Makoto's EEGLAB pipeline (1 Hz highpass, 50 Hz notch, ICA artifact removal, common average reference)

## 2. Data Loading and Preprocessing

### Raw Data Ingestion

Standard Python EEG readers (MNE-Python) cannot load MATLAB v7.3 HDF5 .set files. A custom loader was developed:

1. Read `.set` HDF5 metadata with h5py (top-level keys — no `EEG` wrapper group)
2. Read actual EEG data from companion `.fdt` files via `numpy.fromfile(dtype=float32)`
3. Reshape with `order='F'` (Fortran/column-major) — critical due to MATLAB storage convention
4. Extract stimulus/rest epoch boundaries from BIDS `events.tsv`

### Channel Selection

7 frontal channels selected: Fp1, Fp2, F7, F3, Fz, F4, F8. Rationale: frontal regions show the strongest 40 Hz entrainment response and are most accessible in clinical EEG setups.

### Light Secondary Preprocessing

Applied on top of upstream Makoto pipeline:

1. **Bandpass filter:** 0.5–80 Hz, 4th-order Butterworth, zero-phase (scipy.signal.filtfilt)
2. **Notch filter:** 50 Hz, quality factor Q = 30 (powerline interference)
3. **Artifact rejection:** Samples exceeding ±100 µV amplitude threshold rejected
4. **Common average reference (CAR):** Applied after artifact rejection to prevent corrupted channels from propagating

### Windowing

- 2-second sliding windows (500 samples at 250 Hz)
- 1-second hop (50% overlap, 250-sample stride)
- PAC computed at the epoch level (full 20–40 second blocks) for stability, then assigned uniformly to all constituent 2-second windows within that epoch

### Subject-Level Data Split

Random seed 42, subject-level (no within-subject leakage):

| Split      | Subjects | Windows    |
| ---------- | -------- | ---------- |
| Train      | 24       | 11,736     |
| Validation | 5        | 2,725      |
| Test       | 6        | 2,822      |
| **Total**  | **35**   | **17,283** |

Output: `{train,val,test}_data.npz` with `windows` shape (n, 1, 7, 500) and `pac` shape (n,)

PAC label range: [0.000006, 0.000701], mean approximately 0.000044.

## 3. Phase-Amplitude Coupling (PAC) Computation

### Method: Modulation Index (Tort et al., 2010)

**Frequency bands:**

- Phase signal: theta, 4–8 Hz
- Amplitude signal: gamma, 38–42 Hz (centered on 40 Hz entrainment frequency)

**Algorithm:**

1. Bandpass filter the EEG into theta (4–8 Hz) and gamma (38–42 Hz) using 4th-order Butterworth filters (zero-phase)
2. Apply the Hilbert transform to extract:
   - Instantaneous phase from the theta-filtered signal: `angle(hilbert(theta))` in [−π, π]
   - Instantaneous amplitude envelope from the gamma-filtered signal: `|hilbert(gamma)|`
3. Divide the phase space [−π, π] into 18 bins (20° each)
4. Compute the mean gamma amplitude within each phase bin
5. Normalize mean amplitudes to a probability distribution: P_i = A_i / sum(A)
6. Compute the Kullback-Leibler divergence from a uniform distribution: KL = sum(P_i × log(P_i × n_bins))
7. Normalize by maximum possible KL: MI = KL / log(n_bins)

Result: MI in [0, 1]. Higher values indicate stronger theta-gamma coupling.

## 4. Static PAC Prediction — EEGNet

### Architecture

Based on Lawhern et al. (2018), adapted for regression.

**Input:** (batch, 1, 7, 500) — 1 feature map, 7 channels, 500 timepoints

| Block       | Layer                      | Details                                               | Output Shape    |
| ----------- | -------------------------- | ----------------------------------------------------- | --------------- |
| **Block 1** | Conv2d (temporal)          | 8 filters, kernel (1, 64), padding (0, 32)            | (B, 8, 7, 500)  |
|             | BatchNorm2d                | 8 features                                            | (B, 8, 7, 500)  |
|             | Conv2d (depthwise spatial) | 16 filters (D=2), kernel (7, 1), groups=8             | (B, 16, 1, 500) |
|             | BatchNorm2d                | 16 features                                           | (B, 16, 1, 500) |
|             | ELU activation             |                                                       | (B, 16, 1, 500) |
|             | AvgPool2d                  | kernel (1, 4)                                         | (B, 16, 1, 125) |
|             | Dropout                    | p = 0.5                                               | (B, 16, 1, 125) |
| **Block 2** | Conv2d (depthwise)         | 16 filters, kernel (1, 16), padding (0, 8), groups=16 | (B, 16, 1, 125) |
|             | Conv2d (pointwise)         | 16 filters, kernel (1, 1)                             | (B, 16, 1, 125) |
|             | BatchNorm2d                | 16 features                                           | (B, 16, 1, 125) |
|             | ELU activation             |                                                       | (B, 16, 1, 125) |
|             | AvgPool2d                  | kernel (1, 8)                                         | (B, 16, 1, 15)  |
|             | Dropout                    | p = 0.5                                               | (B, 16, 1, 15)  |
| **Head**    | Flatten                    |                                                       | (B, 240)        |
|             | Linear                     | 240 → 1                                               | (B, 1)          |

**Total parameters:** ~1,457

**Training:**

- Loss: Mean Squared Error (MSE) on z-scored PAC targets (mean/std computed from training set, saved in checkpoint)
- Optimizer: Adam (lr = 1e-3, weight_decay = 1e-4)
- Scheduler: ReduceLROnPlateau (factor = 0.5, patience = 5, monitoring val_loss)
- Gradient clipping: max_norm = 1.0
- Early stopping: patience = 15 epochs on validation loss
- Batch size: 64

**Performance:** Test R² = 0.287. This represents the ceiling for static PAC prediction from 7 frontal channels — 8 different architectures (EEGNet, Delta-PAC, SpecTempNet, ViT-TCNet, Ridge, EEGNet-LSTM, and two others) all converged near this value, indicating a fundamental data limitation rather than an architectural one.

## 5. Feature Engineering for Temporal Prediction

Each 2-second window produces a 73-dimensional feature vector:

### Spectral Features (61 dimensions)

- Band power in 5 frequency bands: delta (0.5–4 Hz), theta (4–8 Hz), alpha (8–12 Hz), beta (12–30 Hz), gamma (30–42 Hz)
- Computed independently for each of 7 channels: 5 × 7 = 35 features
- Cross-channel spectral coherence measures: 26 additional features
- Extracted via FFT-based power spectral density estimation

### PAC-Derived Features (7 dimensions)

- `pac_current`: Current epoch-level PAC value
- `pac_ma2`, `pac_ma4`, `pac_ma8`, `pac_ma16`: Causal moving averages over 2, 4, 8, and 16 timesteps
- `pac_diff1`: PAC difference from t-1 to t (first derivative)
- `pac_diff4`: PAC difference from t-4 to t (longer-range trend)

All moving averages are strictly causal (use only past and current values).

### Stimulation Context Features (5 dimensions)

- `stim_state`: Binary indicator (0 = rest, 1 = stimulation), from BIDS events.tsv
- `time_since_switch_60s`: Seconds since last stimulation/rest transition, capped at 60s
- `stim_frac_20s`: Fraction of time spent in stimulation over the preceding 20 seconds
- `cycle_phase_sin`: sin(2πt/60) encoding position within the 60-second stim/rest cycle
- `cycle_phase_cos`: cos(2πt/60) (complementary sinusoidal encoding)

### Sequence Construction

Sequences are built per-subject to prevent cross-subject contamination:

- Lookback window: T = 20 timesteps (20 seconds of history)
- Prediction horizon: h = 5 timesteps (5 seconds ahead)
- Target: raw PAC at t+h (no smoothing; target_smooth_window = 1)
- Delta target: y_future − y_current

Feature normalization: z-score computed from training data only, applied to all splits. Feature and target scalers saved separately in `scalers.npz`.

**Output:** X shape (n_sequences, 20, 73), y_future shape (n_sequences,), y_delta shape (n_sequences,)

## 6. Temporal PAC Forecasting — MultiscaleCausalTCN

### Architecture

**Input:** (batch, 20, 73) — 20 timesteps, 73 features per step

| Component             | Layer                              | Details                                      | Parameters |
| --------------------- | ---------------------------------- | -------------------------------------------- | ---------- |
| **Input projection**  | Linear                             | 73 → 64                                      | 4,736      |
|                       | LayerNorm                          | 64                                           | 128        |
|                       | SiLU activation                    |                                              | 0          |
| **TCN Block 1**       | Causal Conv1d (depthwise)          | 64 channels, kernel 3, dilation 1, groups=64 | 192        |
|                       | Conv1d (pointwise)                 | 64 → 64, kernel 1                            | 4,096      |
|                       | GroupNorm(1, 64)                   |                                              | 128        |
|                       | SiLU + residual + Dropout(0.1)     |                                              | 0          |
| **TCN Block 2**       | Causal Conv1d (depthwise)          | kernel 3, dilation 2                         | 192        |
|                       | Conv1d (pointwise)                 | 64 → 64                                      | 4,096      |
|                       | GroupNorm(1, 64) + SiLU + residual |                                              | 128        |
| **TCN Block 3**       | Causal Conv1d (depthwise)          | kernel 3, dilation 4                         | 192        |
|                       | Conv1d (pointwise)                 | 64 → 64                                      | 4,096      |
|                       | GroupNorm(1, 64) + SiLU + residual |                                              | 128        |
| **TCN Block 4**       | Causal Conv1d (depthwise)          | kernel 3, dilation 8                         | 192        |
|                       | Conv1d (pointwise)                 | 64 → 64                                      | 4,096      |
|                       | GroupNorm(1, 64) + SiLU + residual |                                              | 128        |
| **Attention pooling** | Conv1d                             | 64 → 1, kernel 1                             | 65         |
|                       | Softmax over time → weighted sum   |                                              | 0          |
| **Future head**       | Linear → SiLU → Dropout → Linear   | 64 → 64 → 1                                  | 4,225      |
| **Delta head**        | Linear → SiLU → Dropout → Linear   | 64 → 64 → 1                                  | 4,225      |

**Total parameters:** 31,043

**Key design decisions:**

- **Causal padding:** Each depthwise convolution pads only on the left: `F.pad(x, ((kernel_size-1)*dilation, 0))`. This ensures the model cannot see future timesteps — essential for a real-time prediction system.
- **Dilation pattern [1, 2, 4, 8]:** Receptive field = (1+2+4+8) × (3-1) + 1 = 31 timesteps, covering the full 20-step input with margin.
- **GroupNorm(1, C) instead of BatchNorm:** Equivalent to instance normalization. Chosen for stability with small batch sizes and cross-subject distribution shifts (different patients have different PAC baselines).
- **Depthwise-separable convolutions:** Factorize spatial and channel mixing for parameter efficiency (31K vs hundreds of thousands for standard convolutions).
- **Attention pooling:** Learned softmax weights over the time axis, allowing the model to focus on the most informative timesteps rather than using only the last timestep.
- **Dual-head output:** Future PAC prediction (primary) and delta-PAC prediction (auxiliary). The delta head provides a multi-task learning signal during training.

### Training

- Loss: Huber loss (delta = 1.0) on future PAC prediction — less sensitive to outliers than MSE
- Multi-task: delta head and consistency penalty available but disabled (lambda = 0.0) in best checkpoint
- Optimizer: AdamW (lr = 1e-3, weight_decay = 1e-3)
- Scheduler: ReduceLROnPlateau (factor = 0.5, patience = 5, monitoring val_future_r², mode = max)
- Gradient clipping: max_norm = 1.0
- Early stopping: patience = 20 epochs on validation R²
- Batch size: 128
- Best epoch: 53

### Performance

| Metric         | Value      |
| -------------- | ---------- |
| Validation R²  | 0.411      |
| Test R²        | 0.170      |
| Test RMSE      | 3.3 × 10⁻⁵ |
| Test Pearson r | 0.433      |

At the 5-second prediction horizon, persistence baseline achieves R² = −0.267 and Ridge regression achieves R² = −0.393. The TCN's R² = 0.254 represents a +0.52 margin — the only model with useful predictions at this timescale.

## 7. Closed-Loop Controller

### Architecture

```
EEG window (2s, 7ch) → EEGNet → PAC estimate → PersonalizationModule → z-score → Decision Logic → STIM / REST
                                                                                         ↑
                                                              TCN forecaster (optional) ──┘
```

### PersonalizationModule

Maintains a rolling circular buffer of the 30 most recent PAC values (30 seconds at 1 Hz decision rate). Computes:

```
z = (PAC_current - mean(buffer)) / (std(buffer) + 1e-8)
```

Requires a minimum of 10 samples before producing z-scores. Statistics recomputed on each update.

### Reactive Threshold Controller

Decision logic per 1-second cycle:

| Condition       | Action                                               |
| --------------- | ---------------------------------------------------- |
| z < −0.5        | **STIMULATE** — PAC below baseline, coupling is weak |
| z > +0.5        | **REST** — PAC above baseline, coupling is strong    |
| −0.5 ≤ z ≤ +0.5 | **MAINTAIN** current state                           |

**Hysteresis:** Minimum 5 seconds in any state before transitioning. Prevents rapid oscillation between stimulate and rest.

### TCN Predictive Controller

Extends the reactive controller with lookahead:

1. Feed 20 timesteps of 73-dimensional features into the TCN
2. Receive predicted future PAC and predicted delta-PAC
3. If predicted delta < −0.3 (PAC declining): **STIMULATE** proactively
4. If predicted delta > +0.3 (PAC rising): **REST** proactively
5. Otherwise: fall back to reactive z-score logic

This enables the controller to initiate stimulation before entrainment degrades, rather than waiting until degradation is detected.

### Validation Methodology

All 35 subjects' EEG recordings are replayed through each controller. At each 2-second window, the controller makes a stimulate/rest decision based on its strategy. The decision is compared against the true PAC state to compute alignment metrics.

**Controllers compared:**

1. Fixed Schedule (clinical standard): 40s ON / 20s OFF
2. Reactive Threshold: z-score decisions on current PAC
3. TCN Predictive: z-score + 5-second lookahead
4. Hybrid (TCN + Reactive): combines both signals
5. PI Controller: proportional-integral control on PAC error
6. Alignment Oracle: perfect hindsight (theoretical upper bound)

## 8. Statistical Analysis

### Primary Comparisons

All controller comparisons use paired (within-subject) designs on N = 35 subjects:

- **Wilcoxon signed-rank test:** Non-parametric paired test, chosen because controller metrics are not guaranteed to be normally distributed. Two-sided, significance threshold p < 0.05.
- **Hedges' g effect size:** Bias-corrected standardized mean difference with 95% confidence intervals. Interpretation: < 0.2 negligible, 0.2–0.5 small, 0.5–0.8 medium, > 0.8 large.
- **Binomial test:** For the proportion of subjects showing improvement (35/35).

### Metrics

| Metric                   | Definition                                                                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| Epoch alignment          | Fraction of epochs where the controller's decision matches the optimal action (stimulate during low-PAC, rest during high-PAC) |
| Low-PAC stimulation rate | Fraction of low-PAC windows that receive stimulation                                                                           |
| High-PAC rest rate       | Fraction of high-PAC windows that receive rest                                                                                 |
| PAC targeting gap        | Mean PAC during rest minus mean PAC during stimulation (positive = correct targeting direction)                                |
| Clinical utility         | Composite score combining alignment, targeting, and efficiency                                                                 |
| Mean lead time           | Average seconds of advance warning before PAC state change                                                                     |

### Robustness Checks

- **Threshold sensitivity:** Controller performance evaluated across delta-z thresholds from 0.1 to 1.0
- **Fatigue model sensitivity:** Four different habituation models tested (linear decay, exponential with tau = 30s and 60s, power law) across six severity levels
- **Shuffle-label sanity check:** TCN trained on randomly permuted PAC labels achieves R² = −0.332, confirming the model learns real signal structure
- **Subject-level cross-validation:** Train/val/test splits at the subject level with no overlap
