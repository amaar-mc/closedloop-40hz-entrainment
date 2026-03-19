# 4. Methods

## 4.1 Dataset and Preprocessing

### 4.1.1 Dataset

We used the publicly available OpenNeuro dataset ds005048 v1.0.1 (Lahijanian et al., 2024), originally described in Naeini et al. (2022). The dataset comprises resting-state and stimulation EEG recordings from 35 patients with dementia diagnoses attending a memory clinic in Tehran, Iran. EEG was recorded using a 19-channel monopolar montage following the international 10/20 system at a sampling rate of 250 Hz. The dataset is distributed in BIDS-compliant format; raw EEG is stored in MATLAB v7.3 (HDF5) `.set` files paired with companion `.fdt` files containing the actual voltage data in single-precision floating-point format using Fortran (column-major) memory ordering.

The stimulation protocol consisted of repeated cycles of 40 Hz auditory pulse train stimulation (40 seconds) followed by silent rest (20 seconds), enabling paired within-subject comparisons of neural coupling state across stimulation and rest conditions.

### 4.1.2 Preprocessing

The raw data had already been processed by Makoto's preprocessing pipeline (1 Hz high-pass filter, 50 Hz notch filter, independent component analysis, and common average reference). We applied a light additional preprocessing pass to standardize the data:

1. **Bandpass filtering:** 4th-order Butterworth filter from 0.5 to 80 Hz (zero-phase, forward-backward pass).
2. **Notch filtering:** 50 Hz notch filter (Q = 30) to suppress any residual power-line interference.
3. **Artifact rejection:** Channels and windows containing samples exceeding ±100 µV were rejected. Critically, artifact rejection was applied *before* common average reference (CAR) to prevent corrupted channel voltages from propagating to all electrodes during rereferencing.
4. **Common average reference:** After artifact rejection, the mean across all retained channels was subtracted from each channel.

### 4.1.3 Channel Selection

We selected 7 frontal channels — Fp1, Fp2, F7, F3, Fz, F4, F8 — which span the prefrontal and frontal regions most relevant to theta-gamma phase-amplitude coupling associated with memory and cognitive function. These channels form the feature space for all models described subsequently.

### 4.1.4 Epoch Segmentation and Windowing

Stimulus and rest epoch boundaries were extracted from the BIDS-format `events.tsv` files accompanying each recording. Stimulus epochs (approximately 40 seconds) and rest epochs (approximately 20 seconds) were segmented accordingly.

To generate training windows suitable for convolutional processing, each epoch was divided into 2-second sliding windows of 500 samples at a 1-second hop (50% overlap). This yielded 17,283 total windows: 11,736 from 24 training subjects, 2,725 from 5 validation subjects, and 2,822 from 6 test subjects.

### 4.1.5 Subject-Level Data Splits

Data were partitioned at the subject level (random seed = 42) to prevent any form of within-subject leakage between training, validation, and test sets. The approximately 70/15/15 split assigned 24 subjects to training, 5 to validation, and 6 to testing. No window from a test subject appeared in any training or validation batch.

---

## 4.2 Phase-Amplitude Coupling Computation

Phase-amplitude coupling (PAC) was quantified using the Modulation Index (MI) introduced by Tort et al. (2010, J Neurophysiol). The MI measures the degree to which the amplitude of a high-frequency oscillation is modulated by the phase of a lower-frequency oscillation. We computed coupling between:

- **Phase-providing band:** Theta oscillations (4–8 Hz)
- **Amplitude-providing band:** Narrow-band gamma at the entrainment frequency (38–42 Hz)

The MI is computed by dividing the theta phase into N = 18 bins of 20° each (360°/18), computing the mean gamma amplitude within each phase bin, normalizing to obtain a probability distribution P(φ_j), and evaluating the Kullback-Leibler divergence from the uniform distribution:

$$\text{MI} = \frac{D_{KL}(P, U)}{\log(N)}$$

where U is the uniform distribution over N bins. The MI is dimensionless, with values near zero indicating no coupling and higher values indicating stronger theta-gamma coordination.

**Epoch-level label assignment:** Rather than computing PAC on each 2-second window individually — which would yield noisy, unreliable estimates due to the brevity of the window relative to the frequency resolution requirements of the theta band — we computed PAC over the full duration of each 20–40 second epoch. The resulting epoch-level MI value was then assigned as the label for all 2-second windows extracted from that epoch. Consequently, windows derived from the same epoch share the same PAC label.

This assignment strategy produces stable, reliable PAC labels but introduces a fundamental ceiling on per-window prediction accuracy: the instantaneous 2-second EEG snapshot cannot contain enough information to fully reproduce the PAC computed over the 10–20x longer epoch from which it was drawn. This ceiling motivates the architectural search described in Section 5 and, ultimately, the temporal prediction approach described in Sections 4.4 and 4.5.

Across the full dataset, PAC values ranged from 6×10⁻⁶ to 7×10⁻⁴ (dimensionless MI units) with a mean of approximately 4.4×10⁻⁵, reflecting the low-to-moderate theta-gamma coupling typical in resting and mildly stimulated EEG from this patient population.

---

## 4.3 Static PAC Estimation: EEGNet

### 4.3.1 Architecture

As the primary static PAC estimator, we adapted EEGNet (Lawhern et al., 2018), a compact convolutional neural network originally designed for EEG-based brain-computer interface classification. We repurposed it as a regression model predicting scalar PAC from a 2-second EEG window.

**Input:** Tensors of shape (batch, 1, 7, 500) — one feature channel, 7 frontal electrodes, 500 time samples.

**Block 1 — Temporal and spatial convolution:**
- Temporal convolution: 8 filters (F1 = 8) with a kernel of length 64 samples (256 ms), shared across all channels, to capture oscillatory dynamics in the theta and gamma bands.
- Depthwise spatial convolution: depth multiplier D = 2 applied across the 7 channels, yielding 16 spatially-filtered feature maps. This learns channel-specific weighting without dramatically increasing parameter count.
- Batch normalization, ELU activation, and average pooling (pool size = 4).

**Block 2 — Separable convolution:**
- Depthwise separable convolution with F2 = 16 pointwise filters and kernel length 16 (64 ms), followed by batch normalization, ELU, and average pooling (pool size = 8).

**Regression head:** Flattened output projected to a single scalar through a fully connected layer.

**Total parameters:** 1,457.

The shallow architecture was intentional: with 17,283 training windows spread across 24 subjects, an overparameterized model would overfit to subject-specific features. The EEGNet design's inductive biases — temporal convolution for frequency decomposition, depthwise spatial convolution for channel weighting — align well with the structure of EEG data.

### 4.3.2 Training

PAC targets were z-score normalized using the training set mean and standard deviation; these normalization statistics were saved with the model checkpoint and applied consistently at test time.

- **Loss:** Mean Squared Error (MSE) on normalized targets.
- **Optimizer:** Adam (learning rate = 0.001, weight decay = 1×10⁻⁴).
- **Scheduler:** ReduceLROnPlateau (mode = min, factor = 0.5, patience = 5 epochs).
- **Gradient clipping:** max_norm = 1.0.
- **Early stopping:** Patience = 15 epochs on validation loss.
- **Best checkpoint:** Epoch 53.

### 4.3.3 Performance

On held-out test subjects, EEGNet achieved R² = 0.287. As discussed in Section 5, this value represents a data-imposed ceiling rather than an architectural limitation — a 135-parameter Ridge regression model achieves an identical R² of 0.287 on the same features. The ceiling arises from the epoch-level label assignment described in Section 4.2 and the limited temporal resolution of 2-second windows.

---

## 4.4 Feature Engineering for Temporal Prediction

To enable temporal PAC forecasting, we constructed a 73-dimensional causal feature vector for each 2-second window, designed to capture the current brain state and recent history of PAC dynamics without any access to future information.

### 4.4.1 Spectral Features (61 dimensions)

Spectral power was estimated in five canonical frequency bands across all 7 frontal channels:

| Band | Frequency Range |
|------|----------------|
| Delta | 0.5–4 Hz |
| Theta | 4–8 Hz |
| Alpha | 8–13 Hz |
| Beta | 13–30 Hz |
| Gamma | 30–45 Hz |

Band power was computed for each of 7 channels, yielding 35 band-power features. An additional 26 features captured cross-channel spectral coherence computed pairwise across selected channel pairs. All 61 spectral features were computed per-window from only the current 2-second epoch using a Welch periodogram estimate.

### 4.4.2 PAC-Derived Features (7 dimensions)

Seven features summarized the temporal dynamics of PAC history:

- `pac_current`: PAC value of the current window.
- `pac_ma2`, `pac_ma4`, `pac_ma8`, `pac_ma16`: Causal moving averages over the preceding 2, 4, 8, and 16 windows (2, 4, 8, and 16 seconds).
- `pac_diff1`: First-order finite difference (current PAC minus previous PAC), capturing trend direction.
- `pac_diff4`: Change in PAC over the preceding 4 windows, capturing medium-term momentum.

All moving averages are computed causally — only past values are used — to prevent future information leakage.

### 4.4.3 Stimulation Context Features (5 dimensions)

Five features encoded the current stimulation context:

- `stim_state`: Binary indicator of whether stimulation was active (1) or inactive (0) at the current window.
- `time_since_switch_60s`: Time elapsed since the last stimulation state change, normalized to a 60-second window.
- `stim_frac_20s`: Fraction of the preceding 20 seconds during which stimulation was active.
- `cycle_phase_sin`, `cycle_phase_cos`: Sine and cosine encodings of the position within the 60-second stimulation cycle (40s on + 20s off), enabling the model to learn phase-dependent PAC dynamics.

### 4.4.4 Normalization

All 73 features were z-score normalized using feature-wise mean and standard deviation computed exclusively from the training split. These statistics were saved and applied identically to validation and test splits. Target PAC values (y_future and y_delta) were similarly normalized using training-set statistics.

This train-only normalization prevents any information from the validation or test distributions from influencing the model during training, satisfying the strict causality requirements of a prospective closed-loop system.

---

## 4.5 Temporal PAC Forecasting: MultiscaleCausalTCN

### 4.5.1 Architecture

We developed the MultiscaleCausalTCN, a causal temporal convolutional network designed to predict future PAC 5 seconds ahead from a 20-second history of the 73-dimensional feature vectors described in Section 4.4.

**Input:** Tensors of shape (batch, T=20, F=73) — 20 sequential 2-second windows, each with 73 features.

**Input projection:** A linear layer projects the 73-dimensional input to 64-dimensional internal representations, followed by LayerNorm and SiLU activation.

**Causal depthwise-separable convolutional blocks (×4):** Each block applies a causal depthwise separable convolution with kernel size 3 and a dilation factor from the set [1, 2, 4, 8]. Causal padding (`F.pad(x, (pad, 0))`) is applied to ensure that the convolution at each time step attends only to the current and past positions, with no access to future values. Each block uses GroupNorm (instead of BatchNorm) for normalization, providing stable batch statistics across variable subject distributions, followed by SiLU activation and a residual connection.

The four dilation factors [1, 2, 4, 8] yield a theoretical receptive field of (1 + 2 + 4 + 8) × (3 − 1) + 1 = 31 time steps, covering the full 20-step lookback window with margin.

**Attention pooling:** A learned attention mechanism (AttentionPool1D) aggregates the temporal sequence into a single fixed-dimensional vector by computing scalar attention weights over the time axis and taking their weighted sum.

**Dual regression heads:** Two identical regression heads (Linear → SiLU → Dropout → Linear) produce:
- `y_future`: predicted PAC 5 seconds ahead.
- `y_delta`: predicted change in PAC from the current value to the 5-second-ahead value.

**Total parameters:** 31,043.

### 4.5.2 Training Configuration

| Parameter | Value |
|-----------|-------|
| Loss function | Huber loss (delta = 1.0) on future PAC prediction |
| Multi-task penalties | Lambda_delta and lambda_consistency architecturally supported; disabled (set to 0.0) for the best checkpoint |
| Optimizer | AdamW (lr = 1×10⁻³, weight_decay = 1×10⁻³) |
| Scheduler | ReduceLROnPlateau (mode = max, factor = 0.5, patience = 5 epochs) |
| Gradient clipping | max_norm = 1.0 |
| Early stopping | Patience = 20 epochs on validation R² |
| Batch size | 128 sequences |
| Best checkpoint | Epoch 53 (validation R² = 0.411) |
| Target smoothing | ts = 1 (raw PAC; no smoothing) |

**Target smoothing note:** Early experiments used a smoothing window of ts = 5, which shared 4 of 5 data points between consecutive target values and inflated R² to 0.74. The final model uses raw (unsmoothed) targets (ts = 1) to produce honest metrics. All reported results are from the ts = 1 configuration.

**Training data:** 11,160 sequences from 24 training subjects.

### 4.5.3 Performance

On held-out test subjects, the MultiscaleCausalTCN achieved:
- Test R² = 0.170 (raw PAC, 5-second horizon)
- Test Pearson r = 0.433

While R² = 0.170 appears modest in isolation, its clinical significance emerges from the horizon sweep (Section 6): at 5–10 second prediction horizons, all baseline models (persistence and Ridge regression) collapse to negative R² (persistence R² = −0.26 to −0.27; Ridge R² = −0.21 to −0.39), while the TCN maintains R² = 0.24–0.28 — a margin of approximately +0.5 R² units. This operationally relevant horizon range is precisely what is needed for proactive stimulation control.

---

## 4.6 Closed-Loop Controller Design

### 4.6.1 Personalization Module

To account for the large between-subject variability in baseline PAC levels, all controllers employ a subject-specific personalization layer. A rolling circular buffer of length 30 seconds (30 windows at 1 Hz) maintains a continuously updated estimate of each subject's current PAC baseline. The z-score of the current PAC value is computed as:

$$z = \frac{\text{PAC}_\text{current} - \mu_\text{baseline}}{\sigma_\text{baseline}}$$

A minimum of 10 samples must accumulate in the buffer before z-scores are computed, preventing unreliable estimates at session onset.

### 4.6.2 Decision Logic

All controllers use a common decision function mapping the z-score (or predicted z-score) to one of three actions:

| Condition | Action | Rationale |
|-----------|--------|-----------|
| z < −0.5 | STIMULATE | PAC below personal baseline; apply 40 Hz entrainment |
| z > +0.5 | REST | PAC above baseline; avoid habituation |
| −0.5 ≤ z ≤ +0.5 | MAINTAIN | PAC near baseline; continue current state |

A 5-second hysteresis hold time prevents rapid oscillation between states, ensuring that each state is maintained for at least 5 seconds before a transition is considered.

### 4.6.3 Controller Variants

We evaluated six controller strategies spanning fixed-schedule, reactive, and predictive approaches:

**1. Fixed Schedule (clinical reference):** Stimulation follows a fixed 40-second ON / 20-second OFF cycle, matching the protocol used to collect the original dataset. This represents the current standard of care and serves as the primary control condition.

**2. Reactive Threshold:** At each 2-second window, the current PAC (estimated by EEGNet) is compared to the personalized baseline using the z-score thresholds above. Stimulation decisions are made based on the current estimated brain state with no lookahead.

**3. TCN Predictive:** The MultiscaleCausalTCN predicts PAC 5 seconds into the future. The predicted future PAC is converted to a predicted z-score, and stimulation decisions are made using this prediction rather than the current state. This enables proactive control — beginning stimulation before PAC declines, rather than waiting for the decline to be detected.

**4. Hybrid TCN + Reactive:** Combines both the TCN prediction and the current reactive signal, blending proactive and reactive control into a single policy for robustness.

**5. PI Controller:** A proportional-integral feedback controller modulates stimulation intensity based on the accumulated error between target and measured PAC, providing a continuous (rather than binary) control signal.

**6. Alignment Oracle:** A theoretical upper bound computed with perfect hindsight — decisions are made using the actual future PAC values that the brain will exhibit, as if a perfect predictor existed. Serves as a ceiling reference for assessing how close the TCN-based controller approaches theoretical optimality.

---

## 4.7 Validation Protocol

### 4.7.1 Offline Counterfactual Replay

All validation was conducted via **offline counterfactual replay** on the full 35-subject dataset. Each subject's real EEG recording was replayed in sequence: at each 2-second window, the controller computed a stimulation decision based on the available EEG features, the rolling baseline, and (for the TCN Predictive controller) the TCN's future PAC prediction. The actual PAC labels observed in the data served as the ground truth against which each decision was evaluated.

Critically, for validation of the TCN-based controller, ground-truth PAC labels were used as TCN input features, isolating the TCN's predictive contribution from any additional error introduced by EEGNet's static PAC estimation. This design provides a clean evaluation of the temporal prediction signal.

The counterfactual nature of this evaluation means that the decisions computed by each controller reflect what that controller *would have done* had it been deployed, but the recorded EEG itself reflects only the stimulation actually delivered during data collection — not the controller's hypothetical decisions. We did not deliver novel stimulation during validation, and we do not claim to have altered subjects' brain activity. All results describe computed stimulation decisions and their alignment with the observed PAC ground truth.

### 4.7.2 Validation Metrics

Four metrics were computed for each controller across all 35 subjects:

- **Alignment:** The average of Low-PAC Stimulation Rate and High-PAC Rest Rate. Alignment of 100% means the controller always stimulates when PAC is low and always rests when PAC is high — the theoretically optimal policy.

$$\text{Alignment} = \frac{\text{Low-PAC Stim Rate} + \text{High-PAC Rest Rate}}{2}$$

- **Low-PAC Stimulation Rate:** The fraction of windows with below-median PAC (for that subject) during which the controller prescribed stimulation. Higher values indicate the controller correctly targets low-PAC states for entrainment.

- **High-PAC Rest Rate:** The fraction of windows with above-median PAC during which the controller prescribed rest. Higher values indicate the controller correctly avoids over-stimulation when coupling is already strong.

- **PAC Gap:** The mean PAC during rest windows minus the mean PAC during stimulation windows. A positive gap confirms the controller successfully targets lower-PAC states for stimulation; a negative gap indicates perverse targeting.

---

## 4.8 Statistical Analysis

All comparisons between controllers were conducted as paired, within-subject tests over the 35-subject dataset. Because the per-subject distributions of alignment and PAC metrics were not assumed to be normally distributed, we used the Wilcoxon signed-rank test (two-sided) throughout. No corrections for multiple comparisons were applied within the primary TCN-versus-Reactive contrast; secondary comparisons are noted as exploratory.

Effect sizes were quantified using Hedges' g (bias-corrected Cohen's d appropriate for small-to-moderate samples), reported with 95% confidence intervals obtained via 10,000-iteration bias-corrected and accelerated (BCa) bootstrap over the 35 subjects.

Clinical breadth of benefit was assessed with a binomial test on the count of subjects for whom the TCN Predictive controller outperformed the Reactive Threshold controller on each primary metric.

Threshold sensitivity was evaluated by repeating the primary comparisons across z-score thresholds ranging from 0.2 to 1.0 in steps of 0.1, to confirm that the observed advantages were not artifacts of a specific threshold choice.

All statistical analyses were conducted in Python using SciPy (scipy.stats) for hypothesis tests and custom bootstrap routines for confidence intervals.
