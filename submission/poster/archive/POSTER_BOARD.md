# POSTER BOARD CONTENT

**Synopsys Championship -- Santa Clara County**
**Category:** Biological Science and Engineering, Computational Biology and Bioinformatics
**Author:** Amaar Chughtai
**Date:** February 2026

---

## ABSTRACT (Printed separately, placed on table. Max 250 words.)

40 Hz auditory stimulation synchronizes brain gamma oscillations, reducing amyloid pathology in Alzheimer's disease models. Current clinical protocols use fixed schedules (40 seconds on, 20 seconds off), ignoring individual brain responses. This project developed a deep learning system that predicts when a patient's brain will lose entrainment and times stimulation accordingly.

Using EEG recordings from 35 dementia patients (OpenNeuro ds005048), I computed theta-gamma phase-amplitude coupling (PAC) as a real-time entrainment biomarker. I built a causal Temporal Convolutional Network (31,000 parameters) with dilated convolutions to predict future PAC, integrated into a closed-loop controller validated on real patient data.

The central prediction finding is a horizon sweep: at 1-2 second horizons, simple baselines suffice. At 5-10 seconds — the operationally relevant range for proactive control — all baselines collapse to negative R-squared while the TCN maintains R-squared of 0.24-0.28 (+0.5 margin).

When integrated into a closed-loop controller and replayed on all 35 subjects' real EEG, the TCN achieved 72.1% epoch alignment versus 64.5% for reactive control (Hedges' g = 1.31, p < 0.001, Wilcoxon signed-rank). It targeted 82.6% of low-PAC windows for stimulation versus 51.7% reactive (g = 4.47, p < 0.001), reaching 91% of the theoretical oracle bound. All 35 subjects benefited (binomial p < 0.001). In simulation, adaptive scheduling efficiency increased with fatigue severity (+9.0% to +11.2%, all p < 0.001), and the advantage held across four different fatigue model assumptions (+6.9% to +19.0%, all p < 10^-13). Half of subjects habituate while half do not, validating the need for personalized control.

_Word count: 247_

---

## BOARD LAYOUT

```
+------------------+--------------------+------------------+
|                  |                    |                  |
|   LEFT PANEL     |   CENTER PANEL     |   RIGHT PANEL    |
|   (WHY)          |   (WHAT / HOW)     |   (WHAT LEARNED) |
|                  |                    |                  |
| INTRODUCTION     |      TITLE         | RESULTS          |
|                  |                    |   (continued)    |
| BACKGROUND       | HYPOTHESIS /       |                  |
|                  |  ENGINEERING GOAL  | CONCLUSIONS      |
| RESEARCH         |                    |                  |
|  QUESTION        | METHODS            | BROADER IMPACT   |
|                  |                    |                  |
|                  | RESULTS            | FURTHER RESEARCH |
|                  |                    |                  |
|                  |                    | REFERENCES       |
+------------------+--------------------+------------------+
```

---

## TITLE (Center panel, top. 150-200pt font.)

**Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease**

Amaar Chughtai

---

## LEFT PANEL: WHY

---

### INTRODUCTION / BACKGROUND (48-72pt header, 24pt+ body)

- 40 Hz sensory stimulation synchronizes brain gamma waves, reducing amyloid pathology in Alzheimer's models (Iaccarino et al., 2016; Martorell et al., 2019)
- Clinical trials use fixed schedules: 40 seconds stimulation, 20 seconds rest, repeated for one hour
- Fixed timing ignores individual brain responses and neural habituation to repetitive stimulation
- Phase-amplitude coupling (PAC) between theta (4-8 Hz) and gamma (38-42 Hz) rhythms quantifies entrainment strength (Tort et al., 2010)
- Dataset: 35 dementia patients, 19-channel EEG at 250 Hz, 17,283 two-second windows from 7 frontal channels (OpenNeuro ds005048)

**[FIGURE 1: Diagram showing PAC concept]**
Suggested visual: Two-panel schematic. Left side shows a fixed schedule waveform (uniform on/off blocks). Right side shows an adaptive schedule waveform (variable-length blocks responding to a fluctuating PAC signal plotted above it). Label the PAC signal with "High PAC = Entrained" and "Low PAC = Lost Entrainment." Use arrows to show the adaptive system delivering stimulation only when PAC drops.

---

### RESEARCH QUESTION

**Can a deep learning model predict future brain entrainment state 5-10 seconds ahead, enabling adaptive stimulation scheduling that is more efficient than fixed protocols?**

---

## CENTER PANEL: WHAT / HOW

---

### HYPOTHESIS / ENGINEERING GOAL (48-72pt header)

- A causal temporal convolutional network can predict future PAC at 5-10 second horizons where simpler methods fail
- Adaptive stimulation scheduling using these predictions will achieve comparable entrainment with less total stimulation time
- The efficiency advantage will increase as neural habituation increases

---

### METHODS / EXPERIMENTAL DESIGN (48-72pt header)

**Data Pipeline:**

- Extracted 17,283 EEG windows (2 seconds each) from 35 subjects across 7 frontal channels
- Subject-level train/validation/test splits (24/5/6 subjects) to prevent data leakage
- Computed PAC using the Modulation Index method (theta phase crossed with gamma amplitude)

**Two Neural Networks (sized for 17,283-sample dataset to avoid overfitting):**

- EEGNet: 1,457 parameters (12 samples/param), estimates PAC from raw EEG in real time (Lawhern et al., 2018)
- Causal TCN: 31,000 parameters, predicts future PAC from 20-step history with dilated causal convolutions and 44-second receptive field
- Larger models (120K-1.1M params) tested; all overfit or converged at same R-squared, confirming data ceiling

**Closed-Loop Simulation:**

- Compared four control strategies: Fixed Schedule, Reactive, Predictive (trend-based), and Oracle (perfect knowledge)
- Modeled neural fatigue at six severity levels to test robustness
- 50 trials per condition, 600 seconds each, Wilcoxon signed-rank tests, bootstrap 95% CIs, Hedges' g effect sizes

**[FIGURE 2: System architecture diagram]**
Suggested visual: Flowchart showing the closed-loop pipeline. Raw EEG (7 channels) feeds into EEGNet, which outputs current PAC. PAC history feeds into the causal TCN, which outputs predicted future PAC. The prediction feeds into the controller, which decides STIMULATE / REST / MAINTAIN. An arrow loops back to the patient, closing the loop. Label each component with its parameter count and inference time.

---

### RESULTS / DATA (48-72pt header)

**Result 1 -- Horizon Sweep (Central Finding):**

**[FIGURE 3: Line graph -- most important figure on the board]**
Suggested visual: Line graph with prediction horizon (1, 2, 3, 5, 8, 10 seconds) on the x-axis and R-squared on the y-axis (range: -0.4 to 0.8). Plot three lines: Persistence baseline (blue, declines from 0.76 to -0.26), Ridge regression (orange, declines from 0.81 to -0.21), and TCN (green, declines from 0.74 to 0.28). Shade the region below R-squared = 0 in light red and label it "Worse than mean prediction." Shade the 5-10 second region in light green and label it "Controller-relevant horizon." Add a double-headed arrow in the 5-10s zone showing the "+0.5 R-squared margin." Data points:

- Persistence: 0.760, 0.488, 0.234, -0.267, -0.276, -0.256
- Ridge: 0.812, 0.542, 0.254, -0.393, -0.211, -0.212
- TCN: 0.735, 0.470, 0.277, 0.254, 0.240, 0.278

**Interpretation:** At 1-2 seconds, simple baselines suffice. At 5-10 seconds, only the TCN provides useful predictions (+0.5 R-squared over baselines). This is the operationally relevant range for proactive control.

---

## RIGHT PANEL: WHAT LEARNED

---

### RESULTS (continued)

**Result 2 -- Adaptive Scheduling Efficiency:**

**[FIGURE 4: Bar chart with error bars]**
Suggested visual: Grouped bar chart. X-axis: fatigue severity (None, Mild, Moderate, Mod-High, High, Severe). Two bars per group: Fixed Schedule efficiency (blue) and Adaptive efficiency (green). Y-axis: stimulation efficiency (PAC mean / stimulation fraction). Add asterisks for significance. Data (n = 50 trials each, rigorous validation):

- None (rate=0.000): Fixed 0.343, Adaptive 0.375 (+9.5%, p < 0.001\*\*)
- Mild (rate=0.004): Fixed 0.341, Adaptive 0.375 (+10.0%, p < 0.001\*\*)
- Moderate (rate=0.008): Fixed 0.335, Adaptive 0.366 (+9.0%, p < 0.001\*\*)
- Mod-High (rate=0.015): Fixed 0.329, Adaptive 0.361 (+9.7%, p < 0.001\*\*)
- High (rate=0.025): Fixed 0.319, Adaptive 0.354 (+10.8%, p < 0.001\*\*)
- Severe (rate=0.040): Fixed 0.316, Adaptive 0.352 (+11.2%, p < 0.001\*\*)

**Interpretation:** At all fatigue levels (6/6), adaptive scheduling is significantly more efficient (all p < 0.001, Wilcoxon signed-rank, large effect sizes with Hedges' g = 1.7-2.4). The advantage generally increases from +9.0% to +11.2% with fatigue severity.

**Result 3 -- Individual Habituation Variability:**

**[FIGURE 5: Histogram or dot plot]**
Suggested visual: Horizontal dot plot or lollipop chart showing PAC change (%) for each of the 35 subjects, sorted from most negative to most positive. Color dots red for subjects showing decline and blue for subjects showing increase. Label extreme cases: sub-35 at -66.8%, sub-19 at -57.0%, sub-20 at +93.0%, sub-27 at +149.1%. Draw a vertical dashed line at 0%. Note that population-level p = 0.542 (not significant), but 49% decline and 51% increase. This variability is the core argument for adaptive scheduling.

**Result 4 -- Fatigue Model Robustness:**
Adaptive advantage tested under 4 different fatigue model assumptions (n = 50 trials each):

- Exponential Decay: +9.0%, p = 1.8e-15, Hedges' g = 2.31
- Step Function (threshold-based): +6.9%, p = 4.4e-14, Hedges' g = 1.21
- Heterogeneous Population (50/50 split): +8.9%, p = 2.5e-14, Hedges' g = 1.71
- Saturation Model (synaptic depletion): +19.0%, p = 1.8e-15, Hedges' g = 3.66

**Interpretation:** The adaptive scheduling advantage is robust across all fatigue model types, not an artifact of one particular simulation assumption. Gains range from +6.9% to +19.0% with large effect sizes.

**Result 5 -- TCN-Based Predictive Control on Real EEG (Primary Result):**

**[FIGURE 6: Controller comparison bar chart -- see results/figures/controller_comparison.png]**

TCN predictive controller replayed on all 35 subjects' real EEG data (no simulation):

| Controller         | Alignment | Low-PAC Targeting | PAC Gap (µV²)          |
| ------------------ | --------- | ----------------- | ---------------------- |
| Fixed Schedule     | 45.0%     | 61.4%             | −6.6 (wrong direction) |
| Reactive           | 64.5%     | 51.7%             | +21.1                  |
| **TCN Predictive** | **72.1%** | **82.6%**         | **+30.5**              |
| Oracle             | 100.0%    | 100.0%            | +33.3                  |

TCN vs Reactive (n=35): Alignment g=+1.31, Low-PAC targeting g=+4.47, PAC gap g=+1.57 (all p<0.001). TCN reaches 91% of oracle bound. 35/35 subjects benefit (binomial p<0.001). Robust across thresholds 0.2-1.0.

**Data Integrity and Model Validation:**

- Subject-level splits: 6 held-out test subjects never seen during training or model selection (generalizability)
- Shuffle-label test: R-squared = -0.332 (model learns real signal, not artifacts)
- Causal dataset construction verified (no future information leakage)
- Feature ablation: PAC features account for R-squared = 0.859; spectral-only features give R-squared = 0.045 (interpretability)
- 8 architectures tested (1.5K to 1.1M parameters); all converge near R-squared = 0.287, confirming data ceiling not model limitation

---

### CONCLUSIONS / DISCUSSION (48-72pt header)

- At 5-10 second horizons, the causal TCN maintains R-squared = 0.24-0.28 while all baselines collapse below zero
- This +0.5 R-squared margin exists at the operationally relevant range for proactive control
- Adaptive scheduling achieves 80% entrainment using 49% stimulation time (+9-11% efficiency, all p < 0.001)
- The adaptive advantage is robust across 4 different fatigue model assumptions (+6.9% to +19.0%, all p < 10^-13)
- Half of patients habituate to stimulation; the other half do not, validating the need for personalized scheduling
- Lightweight models (1,457 and 31,000 parameters) enable real-time embedded deployment

**Limitation:** Real-data validation uses offline replay (counterfactual decisions on recorded EEG), not live streaming. Live closed-loop EEG validation is future work.

---

### BROADER IMPACT / APPLICATIONS (48-72pt header)

- Personalized neurostimulation devices for Alzheimer's, reducing patient burden through shorter, targeted sessions
- Adaptive scheduling principle applicable to any repetitive neural stimulation therapy (tDCS, TMS, light/sound entrainment)
- Framework extensible to other therapeutic frequencies and multi-biomarker control

---

### FURTHER RESEARCH (48-72pt header)

- Deploy with live EEG streaming to validate adaptive scheduling in a real-time crossover experiment
- Record 30-60 minute sessions to capture the full habituation curve
- Replace the heuristic controller with a reinforcement learning policy for long-term optimization

---

### REFERENCES (48-72pt header, 24pt body)

1. Iaccarino, H. F., et al. (2016). Gamma frequency entrainment attenuates amyloid load and modifies microglia. _Nature_, 540(7632), 230-235.
2. Martorell, A. J., et al. (2019). Multi-sensory gamma stimulation ameliorates Alzheimer's-associated pathology and improves cognition. _Cell_, 177(2), 256-271.
3. Tort, A. B., et al. (2010). Measuring phase-amplitude coupling between neuronal oscillations of different frequencies. _Journal of Neurophysiology_, 104(2), 1195-1210.
4. Lawhern, V. J., et al. (2018). EEGNet: A compact convolutional neural network for EEG-based brain-computer interfaces. _Journal of Neural Engineering_, 15(5), 056013.
5. Lahijanian, M., et al. (2024). Auditory gamma-band entrainment enhances default mode network connectivity in dementia patients. _Scientific Reports_, 14, 13153.
6. Thompson, R. F., & Spencer, W. A. (1966). Habituation: A model phenomenon for the study of neuronal substrates of behavior. _Psychological Review_, 73(1), 16-43.

**AI Disclosure:** AI coding assistant (Claude Code) used for code development. All experimental design, data analysis, and scientific interpretation are the student's own work.

---

## WORD COUNT ESTIMATE (body text only, excluding abstract and figure descriptions)

- Introduction / Background: ~75 words
- Research Question: ~25 words
- Hypothesis / Engineering Goal: ~45 words
- Methods: ~115 words
- Results text: ~120 words
- Conclusions: ~105 words
- Broader Impact: ~35 words
- Further Research: ~30 words
- Data Integrity: ~50 words
- **Total: ~600 words**

Within acceptable range. If further trimming needed, reduce Methods data pipeline to 2 bullets or compress Result 4 into a single bullet.

---

## FIGURE PRODUCTION CHECKLIST

| Figure                           | Type                 | Status                                                 | Placement                          |
| -------------------------------- | -------------------- | ------------------------------------------------------ | ---------------------------------- |
| Fig 1: Fixed vs Adaptive Concept | Schematic diagram    | TO CREATE (manual/design tool)                         | Left panel, below Introduction     |
| Fig 2: System Architecture       | Flowchart            | TO CREATE (manual/design tool)                         | Center panel, below Methods        |
| Fig 3: Horizon Sweep             | Line graph (3 lines) | DATA READY (see data points in Results text)           | Center panel, below Results header |
| Fig 4: Fatigue Sensitivity       | Grouped bar chart    | DATA READY                                             | Right panel, Result 2              |
| Fig 5: Individual Habituation    | Dot/lollipop chart   | DATA READY                                             | Right panel, Result 3              |
| Fig 6: Controller Comparison     | Grouped bar chart    | GENERATED: `results/figures/controller_comparison.png` | Right panel, Result 5              |
| Fig 7: Timeline Example          | 3-panel timeline     | GENERATED: `results/figures/timeline_example.png`      | Center panel or Right panel        |
| Fig 8: Threshold Sensitivity     | Line+bar dual axis   | GENERATED: `results/figures/threshold_sensitivity.png` | Right panel, robustness            |

**Generated figures** (in `results/figures/`, 300 DPI PNG + vector PDF):

- `controller_comparison.png` — 6 controllers, 3 metrics
- `pac_targeting_gap.png` — PAC during stim vs rest by controller
- `per_subject_utility.png` — 35-subject scatter (TCN vs Reactive)
- `stim_vs_alignment.png` — Stimulation rate vs alignment trade-off
- `timeline_example.png` — Real PAC trajectory with TCN vs Reactive decisions
- `threshold_sensitivity.png` — TCN robustness across delta-z thresholds

All figures use clean white background, large axis labels (minimum 18pt), colorblind-safe palette.
