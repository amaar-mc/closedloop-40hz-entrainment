# Project P10 Research Log Notebook

### Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize

### Theta-Gamma Phase Amplitude Coupling in Alzheimer's Disease

### Amaar Chughtai

### Valley Christian High School

### Synopsys Science and Engineering Fair 2026

### Notebook Timeline: January 15, 2026 - March 1, 2026

## January 15, 2026

**Goal:** Following project approval, I started with my literature review.

Iaccarino et al. (2016) showed that 40 Hz γ entrainment reduced amyloid-β cluster load in Alzheimer's
mouse models by activating microglia, and Martorell et al. (2019) extended that to multi-sensory
stimulation reducing tau pathology. Lahijanian et al. (2024) then showed that auditory entrainment
enhanced default mode network connectivity in human dementia patients and published a 35-subject
EEG dataset on OpenNeuro (ds005048).

Current trials use a rigid fixed schedule (40 seconds of 40 Hz auditory stimulation followed by 20 seconds
of silence), cycling for one hour regardless of how the patient's brain responds. Some patients maintain
strong coupling throughout; others lose it within seconds. Neural habituation (Thompson & Spencer,
1966) means the brain progressively tunes out a repeated identical stimulus, so coupling degrades over
time. The fixed schedule wastes stimulation during periods of strong coupling and misses opportunities
during periods of fading coupling.

Question: can we predict when a patient's brain will lose entrainment and deliver stimulation proactively,
before the decline occurs?

The biomarker I chose is Phase-Amplitude Coupling (PAC), specifically, how strongly γ amplitude (38-
42 Hz) locks to θ phase (4-8 Hz), measured via the Modulation Index (Tort et al., 2010). High PAC means
entrained; low PAC means lost synchronization.

Software stages: data loading, preprocessing, PAC computation, model training, controller logic, and
validation. Must use subject level splits (no patient can appear in both training and test data), and causal
features for any temporal model (so no future information is leaking into predictions).

Dataset Specifics OpenNeuro page: 35 elderly dementia patients, 19 EEG channels at 250 Hz, alternating
stimulus (40 Hz AM auditory) and rest epochs of 20-40 seconds each. I planned to focus on the 7 frontal
channels (Fp1, Fp2, F3, F4, F7, F8, Fz) where the 40 Hz response is strongest, and to extract 2-second
analysis windows.

**Gap note (January 16 – February 5, 2026):** During this stretch I was reading papers, refining the PAC
method choice on paper, and dealing with school workload. I also did some preliminary coding on the
data loader.

## February 6, 2026

I built the entire pipeline from raw data loading through to a first trained model.

OpenNeuro .set files use MATLAB v7.3 HDF5 format with companion .fdt binary data files. Standard
MNE-Python readers failed completely.
I spent hours debugging before realizing the issue was file format incompatibility. The solution was to
use h5py to read .set metadata (channel count, sample rate, epoch boundaries) and numpy.fromfile()
to read the .fdt binary data. MATLAB stores matrices in column-major (Fortran) order, while Python
defaults to row-major:

```
with h5py.File(set_path, 'r') as f:
n_channels = int(f['nbchan'][0, 0])
n_samples = int(f['pnts'][0, 0])
```

```
data = np.fromfile(fdt_path, dtype=np.float32) data =
data.reshape((n_channels, n_samples), order='F')
```

Without order='F', the channels appeared transposed and PAC values were ridiculous. With it, the EEG
signals had proper amplitude ranges.

I selected 7 frontal channels and extracted 17,283 two-second windows (500 samples each at 250 Hz)
with 50% overlap across all 35 subjects. Subject-level splits: 24 train (11,736 windows), 5 validation
(2,725 windows), 6 test (2,822 windows).

Next I implemented Phase-Amplitude Coupling using the Tort Modulation Index method. The method
bandpass filters for θ (4- 8 Hz) phase and γ (38- 42 Hz) amplitude, applies the Hilbert transform to extract
instantaneous phase and amplitude, bins γ amplitude by θ phase (18 bins of 20 degrees each), normalizes
to a probability distribution, and computes the KL divergence from uniform. I computed PAC at epoch
level (full 20-40 second stimulation blocks), then assigned the value uniformly to constituent 2-second
windows. This creates label sharing within epochs but ensures reliable MI estimates. PAC values ranged
from about 6*10^-6 to 7*10^-4, with a mean around 4.4x10^-5.

With data loaded and labeled, I built the first model EEGNet (Lawhern et al., 2018), for regression.
EEGNet uses temporal convolutions followed by depth wise spatial convolutions that capture channel
relationships, which makes it well-suited for EEG. My adaptation replaced the classification head with a
single linear output neuron for continuous PAC prediction:
Input: (batch, 1, 7, 500) -> 7 channels x 500 samples
Temporal Convolution: 8 filters, kernel=(1,64)
Depthwise Spatial: 16 filters, kernel=(7,1), groups=
ELU + AvgPool + Dropout(0.5)
Separable Convolution
ELU + AvgPool + Dropout(0.5)
Flatten + Linear(240 -> 1)
Total Parameters: 1,

Training used MSE loss, Adam optimizer (lr=0.001, weight_decay=0.0001), gradient clipping
(max_norm=1.0), ReduceLROnPlateau scheduler, and early stopping with patience of 15 epochs. The
result: test R² = 0.287, with inference time under 1 ms on Apple Silicon MPS.

That R² seems low, but architectural improvements could push it higher.

## February 16, 2026

I tested multiple architectures with different parameter counts. Used EEGNet variants, spectral-temporal
hybrids, transformer-based approaches, and simple baselines for comparison.

**EEGNet (baseline, V1)** - 1,457 parameters. Test R² = 0.287.

**EEGNetV2 (delta PAC prediction)** - ~3,200 parameters. Predicted PAC change instead of absolute
PAC. Test R² = 0.06. Delta prediction failed because temporal changes at 2-second resolution are
probably too noisy.

**SpecTempNet (spectral-temporal hybrid, V3)** - 180,000 parameters. Initial result: R² = 0.69!! But I
found that PAC-derived features in the input directly encoded the target. Ridge analysis confirmed that
the PAC features carried 96.6% of the total model weight. After removing the circular features: R² =
0.236. Data leakage.

**ViT-TCNet (Vision Transformer + TCN, V4)** - ~2,000,000 parameters. Treated EEG as image patches
plus temporal convolution. Test R² = 0.252. Severe overfitting with a samples-to-parameters ratio of
0.006 on only 11K training samples.

**Ridge Regression (V5)** - 135 coefficients. Spectral power features, no PAC features. Test R² = 0.287.
It’s the exact same as EEGNet?

**ATCNet (attention-based TCN, V6)** - ~25,000 parameters. Test R² = 0.075.

**EEGNetLarge (scaled EEGNet)** - 141,000 parameters. Test R² = 0.287. Same ceiling, 100x more
parameters.

```
Architecture Parameters Test R² Notes
```

```
EEGNet 1,457 0.
```

```
Optimal parameter
efficiency
```

```
SpecTempNet 180,000 0.236 After leak fix
```

```
ViT-TCNet ~2,000,000 0.252 Overfitting
```

```
Ridge Regression 135 coefs 0.287 Matches deep learning
```

```
ATCNet 25,000 0.075 Underperformed
```

```
EEGNetLarge 141,000 0.287 Same ceiling
```

The simplest models (EEGNet with 1,457 parameters, Ridge with 135 coefficients) matched the
performance of models with 1,000x more parameters. R² = 0.287 is a data ceiling? The signal-to-noise
ratio was approximately -4.73 dB (signal weaker than noise), and epoch-level PAC labels assigned to 2-
second windows inherently limit single-window accuracy. The question should probably change.

## February 17, 2026

Pivoting the idea of the architecture. The 0.287 is a data ceiling. Instead of asking "how accurately can
we estimate current PAC?" the question should be "how far ahead can we predict future PAC?" If the
system can forecast PAC 5-10 seconds into the future, a controller can intervene proactively before
coupling declines, rather than reacting after the fact. Enabling auditory stimulus takes time too.

Part 1: design temporal feature representation. I built 73-dimensional feature vectors per timestep:

**Spectral features (61 dimensions):** Band power in delta (0.5-4 Hz), θ (4- 8 Hz), alpha (8-12 Hz), beta
(12-30 Hz), and γ (30- 42 Hz) for each of 7 channels (35 features), plus 26 cross-channel features.

**PAC-derived features (7 dimensions):** Current epoch-level PAC value, causal moving averages at
windows of 2, 4, 8, and 16 timesteps, plus first-difference and 4-step difference for trend information.

**Stimulation context (5 dimensions):** Binary ON/OFF state, time since last transition, fraction stimulated
over a 20-second window, and sine/cosine encoding of cycle phase position.

Every feature was causal so there could be no data leakage like there was before.

Sequence setup: 20 timesteps of lookback (20 seconds of history) feeding into a prediction of PAC at 5
seconds ahead. Raw PAC targets, no smoothing, for realism.

Part 2: build it. I designed a MultiscaleCausalTCN with four temporal convolution blocks at increasing
dilations:
dilations = [1, 2, 4, 8
F.pad(x, ((kernel_size-1)*dilation, 0)) -> left-only, so no future leakage

RF calculation: kernel size 3, dilations [1, 2, 4, 8], RF = 1 + (3-1) x (1+2+4+8) = 31 timesteps. That
covers the full 20-step input with margin. Output goes through learned attention pooling over the time
dimension, then to a future PAC prediction head. Total parameters: 31,043.

Choices:

- GroupNorm instead of BatchNorm: Different patients have different PAC baselines; GroupNorm
  normalizes per-sample rather than per-batch, which stabilizes cross-subject training.
- Depthwise separable convolutions: Parameter efficiency by factorizing spatial and channel mixing.
- AdamW with lr=0.001, weight_decay=0.001.
- Early stopping: patience=20, monitoring validation R².
  **Component EEGNet Causal TCN**
  Purpose Estimate current PAC from raw
  EEG

```
Predict future PAC from history
```

```
Parameters 1,457 31,
Input Raw EEG (7 ch x 500 samples) 73 features x 20 timesteps
Architecture Temporal + depthwise spatial conv Dilated causal conv (d=1,2,4,8)
Output Current PAC estimate Future PAC (5s horizon)
Key feature Real-time inference 31 - step receptive field, causal
```

```
First training results: validation R² = 0.411 versus test R² = 0.170. Probably because PAC dynamics vary
across patients. It also reinforced why personalized control matters.
```

## February 18, 2026

The temporal model could easily be over stated because smoothed targets make some metrics look much
better than raw target forecasting, and PAC history features have obvious predictive control.

I documented assumptions, wrote out methodology choices, and checked the temporal pipeline for the
failure modes that had already hurt the static phase: data leakage, split mistakes, and overly flattering
interpretations.

Data integrity checklist:

- No leakage: Verified training, validation, and test subjects completely distinct.
- All feature timestamps strictly precede target timestamps.
- Scalers fit only on training data, applied to all splits.
- No input features exceed r = 0.5 with target (after PAC leak removal from the SpecTempNet lesson).
- Shuffle-label - R² = -0.332 on permuted labels, which is good

Checked the habituation patterns in the real EEG data by looking at PAC history per patient:

```
First Block Mean PAC: 0.
Last Block Mean PAC: 0.
Population Change: +4.5% (not significant, p = 0.542)
```

No population trend but the individual variability was the issue:

```
Response Pattern Count Percentage Range
```

```
Habituators (PAC decline) 17/35 48.6% - 66.8% to -5%
```

```
Facilitators (PAC increase) 18/35 51.4% +5% to +149.1%
```

The subjects split nearly equally between habituators and facilitators, which is why there is no population
trend (it cancels). Half of patients habituate while half do not, so fixed scheduling cannot serve both
groups. One patient showed -66.8% decline (strong fatigue), another showed +149.1% increase
(enhanced entrainment over time), and about 46.7% of individual stimulation blocks showed within-
block PAC decline.

## February 19, 2026

The horizon sweep that proved where the TCN adds value; + I made the controller integration that acts
based on the prediction

For the horizon sweep, I trained separate TCN models for prediction horizons of 1, 2, 3, 5, 8, and 10
seconds, comparing each against persistence (assume PAC stays the same) and Ridge regression (linear
model on the same 73 features).
**Horizon Persistence R² Ridge R² TCN R²**

1 s 0.760 0.812 0. (^)
2 s 0.488 0.542 0. (^)
3 s 0.234 0.253 0. (^)
5 s - 0.267 - 0.393 0. (^)
8 s - 0.276 - 0.211 0. (^)
10 s - 0.256 - 0.212 0. (^)
At 1-2 second horizons, PAC changes slowly enough that simple baselines outperform the TCN. But at
the 3-second crossover point, the TCN starts winning. At 5-10 seconds, both baselines collapse to
negative R² (worse than predicting the mean) while the TCN maintains R² around 0.25. Thus the value
prop of the TCN is the +0.5 R² margin.
Baselines fail because PAC autocorrelation decays to near zero beyond ~3 seconds, so persistence
becomes random. The TCN succeeds because multi-scale dilated convolutions capture the patterns at
timescales of 1, 2, 4, and 8 seconds, and it can model nonlinearity of the PAC.
5 - 10 seconds is the relevant range for proactive control. At 1-2 seconds there is not enough lead time for
meaningful intervention. At 5-10 seconds there is enough time for decision processing and stimulation
transitions.

With the horizon sweep validating the TCN at 5 seconds, I built the full two-stage controller pipeline:

```
Raw EEG --> EEGNet (1,457 params) --> Current PAC Estimate
--> Feature Extraction (73 dimensions)
--> TCN (31,043 params) --> Future PAC (5s ahead)
--> Personalization Module --> Control Decision
```

The PersonalizationModule maintains a 30-second rolling buffer to compute a per-patient z-score
baseline. The controller logic combines reactive z-score decisions with TCN-predicted PAC trends. If
the TCN predicts PAC will decline, stimulate proactively; if it predicts PAC will rise, let the brain
maintain naturally; otherwise fall back to reactive control based on the current z-score. A 5-second
hysteresis prevents rapid changes of states.

LATENCY!: under 5 ms (EEGNet + TCN + control logic). Memory: under 100 MB. Decision rate: 1
Hz. Light enough for embedded devices and wearable tech in the future.

## February 21, 2026

Built the validation protocol needed to test the controller on real subject trajectories. Built replay analysis
framework (offline counterfactual analysis on recorded EEG), the validation scripts, and other tools.

Sub-question: does the adaptive advantage depend on specific mathematical assumptions about how
neural fatigue works? I built an EntrainmentSimulator with four different fatigue mechanisms and tested
across six severity levels.
Fatigue severity results (n = 50 trials each, 600-second sessions):
**Fatigue Level Fixed Efficiency Adaptive Efficiency Improvement**

```
None 0.343 0.375 +9.5% *
```

```
Mild 0.341 0.375 +10.0% *
```

```
Moderate 0.335 0.366 +9.0% *
```

```
High 0.319 0.354 +10.8% *
```

```
Severe 0.316 0.352 +11.2% *
```

_*_ p < 0.001, Hedges' g = 1.7-2.4 (large to very large effects). As fatigue worsens the advantage grows!
With no fatigue at all, adaptive control helps by +9.5%, suggesting benefits beyond fatigue mitigation
(targeting natural PAC fluctuations).
Fatigue model (4 different mathematical models, n = 50 trials each):

```
Fatigue Model Advantage p-value Hedges' g
```

Exponential Decay +9.0% 1.8 x 10^- 15 2. (^)
Step Function +6.9% 4.4 x 10^- 14 1. (^)
Heterogeneous (50/50) +8.9% 2.5 x 10^- 14 1. (^)
Saturation (synaptic) +19.0% 1.8 x 10^- 15 3. (^)
All models showed significant advantage. The saturation model (probably most biologically realistic,
based on Michaelis-Menten receptor kinetics) showed the largest benefit at +19.0% with g = 3.66. The
advantage across four different mathematical formulations means for the real fatigue model my pipeline
still provides benefit.
I also ran threshold sensitivity analysis on the TCN controller, testing delta-z thresholds from 0.1 to 1.0:
**Delta-z Threshold Alignment Low-PAC Stim PAC Gap (x10^-6)**
0.1 59.6% 51.2% 12.
0.2 68.5% 72.9% 26.
0.3 73.7% 84.9% 32.

#### 0.4 73.9% 85.3% 33.

#### 0.5 73.7% 85.3% 33.

#### 1.0 73.8% 85.3% 34.

Performance plateaus at delta-z >= 0.3 and consistently exceeds the reactive baseline across all thresholds

> = 0.2. The results are not dependent on precise threshold tuning.

**Gap note (February 22-25, 2026):** Continued cleanup, figure generation, and validation. The final
controller replay result was not locked until February 26.

## February 26, 2026

This was the day the final controller comparison on real patient EEG was finished. The method: replay
each subject's full EEG recording, have the controller make stimulate/rest decisions at each 2-second
window, and compare those decisions against ground-truth PAC to compute alignment metrics. For this
validation, I used ground-truth PAC labels as TCN input to isolate the TCN's predictive contribution from
EEGNet estimation error.

Four controllers tested: Fixed Schedule (40s ON / 20s OFF), Reactive Threshold (z-score on current
PAC), TCN Predictive (z-score + 5-second lookahead), and Oracle (theoretical upper bound).
**Controller performance replayed on all 35 subjects' real EEG:**

```
Controller Alignment
```

```
Low-PAC
Targeting PAC Gap (x10^-6)^ Stim %^
```

```
Fixed Schedule 45.0% 61.4%
```

- 6.6 (wrong
  direction) 66.6%^

```
Reactive 64.5% 51.7% +21.1 36.7%
```

```
TCN Predictive 72.1% 82.6% +30.5 59.7%
```

```
Oracle (upper bound) 100.0% 100.0% +33.3 48.3%
```

Alignment = (Low-PAC Stim Rate + High-PAC Rest Rate) / 2, balanced accuracy of therapeutic
targeting. Low-PAC Targeting = percentage of below-median PAC windows where the controller
stimulates ("did we treat when the brain needed it?"). PAC Gap = mean PAC during rest minus mean
PAC during stim (positive means the controller correctly targets low-PAC periods).
TCN vs Reactive:

- Alignment: Hedges' g = +1.31, p < 0.
- Low-PAC targeting: Hedges' g = +4.47, p < 0.
- PAC gap: Hedges' g = +1.57, p < 0.
- All Wilcoxon signed-rank tests, bootstrap 95% confidence intervals
  **Key findings:**

The fixed schedule went in the wrong direction (-6.6), meaning it stimulated more during high-PAC than
low-PAC periods. Timing was uncorrelated with brain state.

The TCN achieved 92% of oracle performance: PAC gap 30.5 versus 33.3 theoretical maximum
(30.5/33.3 = 92%). It targeted 82.6% of low-PAC windows versus Reactive's 51.7%, a 60% improvement
in timing. And it used less stimulation than Fixed Schedule (59.7% vs 66.6%), meaning better outcomes
with less total stimulation.

The reactive controller missed 48% of low-PAC windows that needed treatment. Its conservatism (36.7%
total stim) means high specificity but terrible sensitivity.

All 35 of 35 subjects showed higher clinical utility with TCN versus Reactive (binomial p < 0.001). This
held for the 6 held-out test subjects never seen during training, demonstrating cross-subject
generalization.

_Controller comparison on all 35 subjects' real EEG recordings. TCN Predictive outperforms all
alternatives on alignment, low-PAC targeting, and PAC gap._

_Every patient benefits: 35/35 subjects show higher utility with TCN vs Reactive._

_Example controller timeline for one subject, showing how the TCN-driven controller aligns stimulation
with periods of low PAC._

## March 1, 2026

I compiled all results into the poster, abstract, and this notebook for the Synopsys Science Fair
submission.
**Summary of the complete pipeline:**

The system works in two stages. EEGNet (1,457 parameters) estimates current PAC from a 2-second raw
EEG window. The Causal TCN (31,043 parameters) then ingests 20 seconds of 73-feature history and
forecasts PAC 5 seconds ahead. A personalization module adapts to each patient's individual PAC
baseline using a rolling z-score, and the controller uses the TCN's prediction to make proactive
stimulation decisions with a 5-second hysteresis.
**Conclusions, verified against the poster and validated results:**

1. At 5-10 second horizons, the TCN maintains R² around 0.25 while all baselines collapse below
   zero (+0.5 R² margin at the relevant range for proactive control).
2. On real patient EEG: 72.1% alignment versus 64.5% reactive (p < 0.001), targeting 82.6% of
   low-PAC windows versus 51.7% (60% improvement in therapeutic targeting).
3. All 35 patients benefited, including 6 held-out test subjects. Generalizes across individual EEG
   patterns.
4. Adaptive advantage increases with fatigue (+9.0% to +11.2%) and holds across four fatigue
   model assumptions (Hedges' g = 1.21-3.66, all p < 0.001).
5. Half of patients habituate while half do not, validating the need for personalized rather than fixed
   scheduling.

Limitation: The system makes decisions on real brain data but cannot observe the brain's response to
those decisions.
**Further research directions:**

- Deploy with live EEG streaming for real time crossover validation (adaptive vs fixed within same
  session)
- Record 30-60 minute sessions to capture the full habituation time course
- Replace the heuristic controller with RL for long horizon optimization
- Extend to multi-biomarker control (PAC + spectral power + connectivity)

## CSEF Preparation Update — March 2026

---

## March 3–5, 2026

Something about the February 17 val-test gap kept bothering me. Val R² = 0.411 but test R² = 0.170. The model was learning something real on validation subjects but failing on test subjects. What if the 61 spectral features are the problem? They encode things like baseline power in each band per channel, which is basically a fingerprint of each person's skull and electrode placement. The model might just be memorizing which subject is which.

I designed an ablation study to test this. Same TCN architecture, same training protocol, same test split — only change is which features go in:

| Feature Subset | # Features |
|---|---|
| All features (baseline) | 73 |
| PAC + Stim context | 12 |
| PAC only | 7 |
| PAC + Stim + 10 spectral | 22 |
| Spectral + PAC | 68 |
| Spectral only | 61 |

No smoothing (ts=1) so the numbers are honest. All feature indices double-checked for causality.

---

## March 6–8, 2026

The ablation results came back and I stared at the table for a while:

| Feature Subset | Val R² | Test R² | Val-Test Gap |
|---|---|---|---|
| All features (73) | 0.333 | -0.025 | 0.358 |
| PAC + Stim (12) | 0.804 | 0.558 | 0.246 |
| PAC only (7) | 0.422 | 0.344 | 0.078 |
| PAC + Stim + 10 spectral (22) | 0.859 | 0.496 | 0.363 |
| Spectral + PAC (68) | 0.387 | 0.222 | 0.165 |
| Spectral only (61) | -0.044 | -0.420 | 0.376 |

The spectral-only model gets test R² = -0.420. That is *worse than predicting the mean*. These features aren't just unhelpful — they're actively poisoning generalization. And the full 73-feature model that I spent all of February building? Test R² = -0.025. Basically zero.

But 12 features — just the PAC trajectory and stim context — hit 0.558 on the test set. That's a 5x improvement over the 73-feature version, using 83% fewer inputs.

I keep coming back to the same thought: the bottleneck was never the model. It was the features. Eight architectures, three orders of magnitude in parameter count, and they all hit the same ceiling because the input features were wrong. The spectral features let the model memorize individual subjects instead of learning temporal dynamics.

---

## March 10–12, 2026

Before I get too excited I need to check that this isn't a fluke. Neural network results can depend heavily on random initialization — maybe seed 42 just got lucky. Trained the same h=64 TCN with PAC+Stim features under 5 different seeds:

| Seed | Val R² | Test R² |
|---|---|---|
| 42 | 0.804 | 0.558 |
| 123 | 0.822 | 0.620 |
| 456 | 0.799 | 0.597 |
| 789 | 0.831 | 0.608 |
| 2024 | 0.846 | 0.647 |
| Mean ± Std | 0.820 ± 0.019 | 0.606 ± 0.032 |

Not a fluke. The worst seed (0.558) still beats the old 73-feature model by 4.6x. Mean test R² = 0.606 ± 0.032. This is the number I'll report.

---

## March 13–14, 2026

Now that I know the features matter more than the model, how small can the model go? Tested hidden sizes 32, 64, and 128 with different regularization strengths on the 12-feature set:

| Model | Params | Val R² | Test R² |
|---|---|---|---|
| TCN h=32 high-reg | 5,154 | 0.844 | 0.613 |
| TCN h=64 | 22,914 | 0.804 | 0.558 |
| TCN h=64 high-reg | 22,914 | 0.814 | 0.598 |
| TCN h=128 | 86,786 | 0.853 | 0.645 |

The h=32 model with strong regularization (dropout 0.3, weight decay 5e-3) gets R² = 0.613 with only 5,154 parameters. h=128 is 17x bigger and only gains 0.032. Same story again — the signal is in the features, not the model capacity. The small model is better for deployment anyway.

---

## March 15–17, 2026

Two experiments this week.

First, I tested the 12-feature TCN on 4-channel data (Fp1, Fp2, Fz, F3 — the channels a Muse 2 consumer headset would give you). The old 73-feature 4ch model got test R² = 0.112, barely above persistence at 0.117. With PAC+Stim features: test R² = 0.430. The temporal context compensates for having fewer electrodes because the PAC trajectory patterns don't depend much on spatial coverage.

Second, I reran the horizon sweep with the 12-feature model:

| Horizon | Persistence R² | Ridge R² | TCN R² |
|---|---|---|---|
| 1 s | 0.760 | 0.812 | 0.725 |
| 3 s | 0.234 | 0.253 | 0.607 |
| 5 s | -0.267 | -0.393 | 0.577 |
| 8 s | -0.276 | -0.211 | 0.370 |
| 10 s | -0.256 | -0.212 | 0.669 |

Same shape as the February sweep but with much higher TCN numbers. At 1s the TCN is slightly below persistence, which makes sense — PAC barely changes in one second so just guessing "same as now" works fine. At 3s and beyond the baselines fall apart and the TCN pulls away. The 10s result (0.669) is surprisingly strong, probably because the protocol timing features help the model predict stim/rest transitions that far out.

---

## March 18–20, 2026

Built two demo apps this week. The caregiver monitoring app is live on Hugging Face Spaces at `huggingface.co/spaces/amaarc/neurocare-40hz` — it shows real-time PAC tracking, stimulation decisions, and patient status.

The more interesting one is `neurocare_live.py`, a mission control dashboard that does real-time PAC computation and actually synthesizes the 40 Hz audio stimulation. It has a live PAC waveform, the TCN prediction trace (5s look-ahead), a stim ON/OFF toggle with hysteresis, and a patient profile panel.

I wanted to demo this with real Muse 2 hardware but hit a wall: BLE doesn't work on macOS 25.x (BOARD_NOT_READY_ERROR:7 — BLE not enabled at kernel level). Spent a couple hours trying workarounds before giving up. The code has a RealEEGAdapter that would work on a BLE-enabled system, but for CSEF judging day I'll use SimulatedEEGAdapter. It runs the same pipeline on synthetic EEG, which is honest enough for a demo.

---

## March 21–22, 2026

Updated all CSEF submission materials to put the feature ablation discovery front and center. Revised the poster (V6), all five interview scripts, the elevator pitch (~130 words, 60 seconds), research paper (v4 with new ablation section), and abstract. Every number cross-checked against the source data files. Searched all documents for any leftover references to "73 features" or "R² = 0.25" that should say "12 features" and "R² = 0.606" — found and fixed several.

---

## Equipment and Materials

- Compute: MacBook Pro (Apple M1 Pro, 16 GB RAM). All computation on local hardware.
- **Software:** Python 3.13, PyTorch, NumPy, SciPy, scikit-learn, h5py, MNE-Python. Git
- **Dataset:** OpenNeuro ds005048 (Lahijanian et al., 2024). 35 dementia patients, 7 frontal EEG
  channels, 250 Hz. Alternating stimulus (40 Hz AM auditory) and rest epochs. 17,283 two-second
  windows. Subject-level splits: 24 train / 5 val / 6 test. All data used under open access license.

## References

Iaccarino, H. F., et al. (2016). Gamma frequency entrainment attenuates amyloid load and modifies
microglia. _Nature_ , 540(7632), 230-235.

Martorell, A. J., et al. (2019). Multi-sensory γ stimulation ameliorates Alzheimer's-associated pathology
and improves cognition. _Cell_ , 177(2), 256-271.

Tort, A. B., et al. (2010). Measuring phase-amplitude coupling between neuronal oscillations of different
frequencies. _Journal of Neurophysiology_ , 104(2), 1195-1210.

Lawhern, V. J., et al. (2018). EEGNet: A compact convolutional neural network for EEG-based brain-
computer interfaces. _Journal of Neural Engineering_ , 15(5), 056013.

Lahijanian, M., et al. (2024). Auditory γ-band entrainment enhances default mode network connectivity
in dementia patients. _Scientific Reports_ , 14, 13153.

Thompson, R. F., & Spencer, W. A. (1966). Habituation: A model phenomenon for the study of neuronal
