# Personalized Deep Learning Model for Closed-Loop 40 Hz

# Entrainment to Optimize Theta-Gamma Phase Amplitude

# Coupling in Alzheimer’s Disease

## Amaar M. Chughtai

```
Alzheimer's disease affects over 55 million people worldwide, with no
cure and limited treatment options. Recent neuroscience research has
revealed how 40 Hz auditory stimulation can synchronize brain gamma
oscillations, reducing amyloid-beta plaques and tau tangles in animal
models and showing early cognitive benefits in human clinical trials.
```

```
Current clinical protocols deliver this stimulation on a rigid fixed schedule
— 40 seconds of 40 Hz auditory stimulation followed by 20 seconds of
silence, cycling continuously for one hour regardless of how the patient's
brain is responding. This one-size-fits-all approach ignores how some
patients maintain strong theta-gamma coupling throughout a session, while
others lose coupling within seconds and never fully synchronize.
Prolonged repetitive stimulation causes neural habituation, where the brain
progressively "tunes out" the stimulus, and coupling degrades over time.
The result is wasted stimulation during periods of strong coupling and
missed opportunities during periods of fading coupling.
```

```
This project asks: can we predict when a patient's brain will lose
entrainment and deliver stimulation proactively, before the decline occurs?
```

## Introduction Results & Findings

## Conclusions

## Background

## Materials

- 40 Hz gamma entrainment reduces amyloid load in Alzheimer's mouse
  models by activating microglia (Iaccarino 2016); multi-sensory
  stimulation reduces tau pathology and improves cognition (Martorell
  2019); auditory entrainment enhances default mode network
  connectivity in human dementia patients (Lahijanian 2024)
- **Phase-Amplitude Coupling (PAC)** quantifies entrainment success —
  how strongly gamma amplitude (38-42 Hz) locks to theta phase (4- 8
  Hz), measured via the Modulation Index (Tort 2010). High PAC =
  entrained; low PAC = lost synchronization.
- Neural habituation causes repeated identical stimuli to produce
  progressively weaker neural responses (Thompson & Spencer 1966),
  making fixed schedules less effective over time

```
No existing system predicts future entrainment state for proactive
control. Current approaches either use fixed schedules (no adaptation) or
reactive thresholds (respond after PAC decline has already occurred).
```

## Hypothesis

```
Dataset:
```

- 35 dementia patients, OpenNeuro ds 005048 (Lahijanian 2024 )
- 7 frontal EEG channels (Fp 1 , Fp 2 , F 3 , F 4 , F 7 , F 8 , Fz), 250 Hz
- Alternating Stimulus ( 40 Hz AM auditory) and Rest epochs, 20 - 40 s each
- 17 , 283 two-second windows; subject-level splits ( 24 train / 5 val / 6 test)

```
Compute: Python 3. 13 , PyTorch, Apple Silicon (MPS), no cloud GPU required
```

## Procedures

```
Training:
```

- EEGNet: MSE loss, Adam optimizer, gradient clipping (max_norm=1.0),
  early stopping
- Causal TCN: Huber loss (robust to PAC outliers), learning rate reduction on
  plateau, early stopping (patience=20)
- All hyperparameters tuned on validation set (5 subjects); test set (6 subjects)
  used only for final evaluation

```
Validation (two independent protocols):
```

- Primary (real data): Replayed TCN controller on all 35 subjects' actual EEG
  recordings — offline counterfactual decisions on real brain data. For
  validation, ground-truth PAC labels were used as TCN input, isolating the
  TCN's predictive contribution from EEGNet estimation error.
- Secondary (simulation): Closed-loop simulation with neural fatigue modeling
  - 6 severity levels × 50 trials × 600 seconds per trial

```
Statistical validation:
```

- Wilcoxon signed-rank tests (non-parametric, paired)
- Bootstrap 95% confidence intervals
- Hedges' g effect sizes
- Compared against: Fixed Schedule, Reactive Threshold, PI Controller,
  Alignment Oracle (theoretical upper bound)

## Data, Charts, & Models

```
A causal temporal convolutional network can predict future PAC at 5 - 10
second horizons where simpler methods fail, enabling adaptive stimulation
that targets periods of genuine therapeutic need.
Goals:
```

- Predict brain entrainment 5 - 10 s into the future (the minimum lead time
  for proactive control)
- Closed control loop pipeline — integrate predictions into a closed-loop
  stimulation controller
- Validate on real patient EEG that predictive control outperforms fixed
  and reactive approaches

```
Result 1 : TCN Predictive Control Outperforms All Alternatives
Controller performance replayed on all 35 subjects' real EEG:
```

```
Controller Alignment Low-PAC
Targeting
```

```
PAC Gap (×10⁻⁶) Stim %
```

```
Fixed Schedule 45.0% 61.4% -6.6 (wrong
direction)
```

```
66.6%
```

```
Reactive 64.5% 51.7% +21.1 36.7%
```

```
TCN Predictive 72.1% 82.6% +30.5 59.7%
```

```
Oracle (upper
bound)
```

```
100.0% 100.0% +33.3 48.3%
```

- TCN vs Reactive: Alignment g = + 1. 31 , Low-PAC targeting g = + 4. 47 ,
  PAC gap g = + 1. 57 (all p < 0. 001 )
- TCN PAC targeting gap reaches 92 % of the theoretical oracle
- TCN uses less stimulation than Fixed Schedule ( 59. 7 % vs 66. 6 %)
- Reactive misses 48 % of low-PAC windows that need treatment

```
Result 2 : Every Patient Benefits
```

- 35/35 subjects (100%) show higher utility with TCN vs Reactive
  (binomial p < 0.001)
- Advantage holds for 6 held-out test subjects never seen during training

```
Result 3 : Advantage Increases with Fatigue
Simulation results across 6 fatigue severity levels (n = 50 trials each):
Fatigue Level Fixed Efficiency Adaptive Efficiency Improvement
```

```
None 0.343 0.375 +9.5%***
```

```
Mild 0.341 0.375 +10.0%***
```

```
Moderate 0.335 0.366 +9.0%***
```

```
High 0.319 0.354 +10.8%***
```

```
Severe 0.316 0.352 +11.2%***
```

```
***p < 0. 001 , Hedges' g = 1. 7 – 2. 4 (large to very large effects). Advantage
grows as fatigue worsens; exactly when personalization matters most.
```

```
Result 4 : Robust Across Fatigue Model Assumptions
Tested under 4 different mathematical models of neural fatigue (n = 50
trials each):
Fatigue Model Advantage P-value Hedges’ g
```

```
Exponential Decay +9.0% 1.8 × 10⁻¹⁵ 2.
```

```
Step Function +6.9% 4.4 × 10⁻¹⁴ 1.
```

```
Heterogeneous
(50/50)
```

```
+8.9% 2.5 × 10⁻¹⁴ 1.
```

```
Saturation (synaptic) +19.0% 1.8 × 10⁻¹⁵ 3.
```

1. At 5 - 10 s horizons, the TCN maintains R² ≈ 0. 25 while all baselines
   collapse below zero; a + 0. 5 R² margin at the operationally relevant
   range for proactive control
2. On real patient EEG: 72. 1 % alignment vs 64. 5 % reactive (p < 0. 001 ),
   targeting 82. 6 % of low-PAC windows vs 51. 7 % = 60 % improvement
   in therapeutic targeting
3. All 35 patients benefited, including 6 held-out test subjects —
   generalizes across individual EEG patterns
4. Adaptive advantage increases with fatigue (+ 9. 0 % to + 11. 2 %) and
   holds across four fatigue model assumptions
5. Half of patients habituate while half do not, validating the need for
   personalized, not fixed scheduling

```
Limitation: Real-data validation uses offline replay on recorded EEG, not
live closed-loop streaming. The system makes decisions on real brain data
but cannot observe the brain's response to those decisions.
```

## Model Approach

```
To control stimulation proactively, the system needs to predict PAC 5 - 10
seconds into the future. The approach consists of two phases:
```

- Estimate current PAC from raw EEG in real time (since live patients don't
  have ground-truth labels)
- Predict future PAC from a history of past estimates — temporal forecasting

```
Stage 1 : Architecture Decision for Static PAC Estimation
```

## Further Research

- Deploy with live EEG streaming for real-time crossover validation (adaptive
  vs fixed within same session)
- Record 30 – 60 - minute sessions to capture the full habituation time course
- Replace the heuristic controller with reinforcement learning for long-horizon
  optimization
- Extend to multi-biomarker control (PAC + spectral power + connectivity)

## References

```
Iaccarino, H. F., et al. ( 2016 ). Gamma frequency entrainment attenuates
amyloid load and modifies microglia. Nature, 540 ( 7632 ), 230 - 235.
```

```
Martorell, A. J., et al. ( 2019 ). Multi-sensory gamma stimulation
ameliorates Alzheimer's-associated pathology and improves cognition.
Cell, 177 ( 2 ), 256 - 271.
```

```
Tort, A. B., et al. ( 2010 ). Measuring phase-amplitude coupling between
neuronal oscillations of different frequencies. Journal of Neurophysiology,
104 ( 2 ), 1195 - 1210.
```

```
Lawhern, V. J., et al. ( 2018 ). EEGNet: A compact convolutional neural
network for EEG-based brain-computer interfaces. Journal of Neural
Engineering, 15 ( 5 ), 056013.
```

```
Lahijanian, M., et al. ( 2024 ). Auditory gamma-band entrainment enhances
default mode network connectivity in dementia patients. Scientific
Reports, 14 , 13153.
```

```
Thompson, R. F., & Spencer, W. A. ( 1966 ). Habituation: A model
phenomenon for the study of neuronal substrates of behavior.
Psychological Review, 73 ( 1 ), 16 - 43.
```

## Acknowledgements

```
Data Source: OpenNeuro dataset ds005048 (Lahijanian et al., 2024). All
EEG data used under open access license.
```

```
Architecture Params Test R²
```

```
EEGNet (V1) 1457 0.
```

```
SpecTempNet (V3) 180K 0.
```

```
ViT-TCNet (V4) ~2M 0.
```

```
Ridge Regression (V5) 135 coefs 0.
```

```
ATCNet (V8) 25K 0.
```

```
EEGNetLarge (rigor) 141K 0.
```

- Simplest models (EEGNet, Ridge,
  EEGNetLarge) converge to R² = 0. 287
- Larger models perform worse due to
  overfitting; the 2 M-parameter ViT-
  TCNet scored lower than the 1 , 457 -
  parameter EEGNet
- Conclusion: R² = 0. 287 is a data ceiling
  (epoch-level PAC labels on 2 s windows)

```
EEGNet matches the best R² ( 0. 287 ) with
only 1 , 457 parameters; It’s the lightest
weight architecture tested, enabling real-
time inference on embedded devices.
provides the current PAC estimate that
feeds into the temporal predictor.
```

```
Stage 2 : Temporal Prediction; Causal TCN
```

```
EEGNet Causal TCN
Purpose Estimate current PAC from raw EEG Predict future PAC from history
```

```
Parameters 1457 (12 samples/param) 31,
Input Raw EEG (7 ch x 500 samples) 73 features x 20 timesteps
Architecture Temporal + depth wise spatial conv. Dilated causal conv (d=1,2,4,8)
Output Current PAC Estimate Future PAC (5s Horizon)
Key Feature Real-time-inference 31 - step receptive field, causal (no
future leakage)
```

```
73 TCN input features: 61 spectral power + 7 PAC-derived (current value from
EEGNet, moving averages, trends) + 5 stimulation context (on/off state,
duration, session phase)
```

```
Since no single-window architecture could exceed R² = 0. 287 , I shifted the
approach: instead of predicting PAC better from one snapshot, predict it further
into the future from a sequence of snapshots. The Causal TCN ingests 20
seconds of history and forecasts PAC 5 seconds ahead.
```
