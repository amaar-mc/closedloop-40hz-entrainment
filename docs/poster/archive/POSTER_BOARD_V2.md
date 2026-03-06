# POSTER BOARD CONTENT — V2 (Print-Ready)

**Synopsys Championship — Santa Clara County**
**Category:** Biological Science and Engineering, Computational Biology and Bioinformatics
**Author:** Amaar Chughtai
**Date:** March 2026

**Board dimensions:** 48" wide x 56" tall (tri-fold)
**Font minimum:** 24pt body, 48-72pt section headers, 150-200pt title

---

## COMPLIANCE CHECKLIST

- [x] No school name or logo
- [x] No research institution logo
- [x] No postal/email/web/social media/QR codes
- [x] No photos of people (all figures are charts/diagrams)
- [x] No awards or medals from previous fairs
- [x] References on board
- [x] AI disclosure included (in Acknowledgements)
- [x] Proper figure attribution (all author-generated from code)
- [x] Abstract printed separately, placed on table
- [x] Font ≥ 24pt body text
- [ ] Notebook on table
- [ ] Compliance checklist + Forms 1C/7 on table
- [ ] Forms 1B, 3, 4, 6A, 6B, signed Ethics Statement available (not displayed)

---

## BOARD LAYOUT

```
+========================+================================+========================+
|     LEFT PANEL         |        CENTER PANEL             |     RIGHT PANEL        |
|     (~14" wide)        |        (~20" wide)              |     (~14" wide)        |
|                        |                                 |                        |
|                        |  ┌──────────────────────────┐   |                        |
|                        |  │       PROJECT TITLE       │   |                        |
|                        |  │       Author Name         │   |                        |
|  ┌──────────────────┐  |  └──────────────────────────┘   |  ┌──────────────────┐  |
|  │   INTRODUCTION   │  |                                 |  │ RESULTS/FINDINGS │  |
|  │                  │  |  ┌──────────────────────────┐   |  │   (continued)    │  |
|  │                  │  |  │   MATERIALS, METHODS,    │   |  │                  │  |
|  └──────────────────┘  |  │      & PROCEDURES        │   |  │  [FIG 5] Control │  |
|                        |  │                          │   |  │   Comparison Bar │  |
|  ┌──────────────────┐  |  │  [FIG 2] System Arch.    │   |  │                  │  |
|  │   BACKGROUND /   │  |  │                          │   |  │  [FIG 6] Per-Sub │  |
|  │ LITERATURE REVIEW│  |  └──────────────────────────┘   |  │   Scatter Plot   │  |
|  │                  │  |                                 |  │                  │  |
|  │ [FIG 1] Fixed vs │  |  ┌──────────────────────────┐   |  │  [TABLE] Stats   │  |
|  │  Adaptive Concept│  |  │    DATA / CHARTS         │   |  └──────────────────┘  |
|  │                  │  |  │                          │   |                        |
|  └──────────────────┘  |  │  [FIG 3] Horizon Sweep   │   |  ┌──────────────────┐  |
|                        |  │   (central finding)      │   |  │   CONCLUSIONS /  │  |
|  ┌──────────────────┐  |  │                          │   |  │ FURTHER RESEARCH │  |
|  │   HYPOTHESIS /   │  |  │  [FIG 4] Timeline        │   |  │                  │  |
|  │ ENGINEERING GOAL │  |  │   Example (real data)    │   |  └──────────────────┘  |
|  │                  │  |  │                          │   |                        |
|  └──────────────────┘  |  └──────────────────────────┘   |  ┌──────────────────┐  |
|                        |                                 |  │   REFERENCES /   │  |
|                        |                                 |  │ ACKNOWLEDGEMENTS │  |
|                        |                                 |  └──────────────────┘  |
+========================+================================+========================+

TABLE (in front of board, ~15" x 24"):
┌────────────┬────────────┬────────────┬────────────┐
│  Project   │  Abstract  │ Compliance │  Forms     │
│  Notebook  │  (printed) │ Checklist  │  1C, 7     │
└────────────┴────────────┴────────────┴────────────┘
```

---

## TITLE (Center panel, top — 150-200pt font)

**Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease**

Amaar Chughtai

---

## ============================
## LEFT PANEL: WHY
## ============================

---

### INTRODUCTION (48-72pt header, 24pt+ body)

Alzheimer's disease affects over 55 million people worldwide, with no cure and limited treatment options. Recent neuroscience research has revealed a promising approach: 40 Hz auditory stimulation can synchronize brain gamma oscillations, reducing amyloid-beta plaques and tau tangles in animal models and showing early cognitive benefits in human clinical trials.

Current clinical protocols deliver stimulation on a rigid fixed schedule: 40 seconds of 40 Hz auditory stimulation followed by 20 seconds of silence, cycling continuously for one hour regardless of how the patient's brain is responding. During the "on" periods, the brain may already be well-entrained and not need stimulation; during the "off" periods, entrainment may be fading and the brain could benefit from continued stimulation. The schedule treats every moment the same.

This one-size-fits-all approach ignores two critical realities. First, **between patients**: some patients maintain strong theta-gamma coupling throughout a session, while others lose coupling within seconds of stimulus onset and never fully synchronize. Second, **within a session**: even in patients who initially entrain well, prolonged repetitive stimulation causes neural habituation. Gamma oscillation amplitude progressively weakens, theta-gamma coupling degrades, and the brain effectively "tunes out" the stimulus. The result is wasted stimulation during periods of strong coupling and missed opportunities during periods of fading coupling.

This project asks: **can we predict when a patient's brain will lose entrainment and deliver stimulation proactively, before the decline occurs?**

---

### BACKGROUND / LITERATURE REVIEW (48-72pt header, 24pt+ body)

**40 Hz Gamma Entrainment:**
Iaccarino et al. (2016) first demonstrated that 40 Hz light flickering reduces amyloid load in Alzheimer's mouse models by activating microglia. Martorell et al. (2019) extended this to multi-sensory (auditory + visual) stimulation, showing reduced amyloid and tau pathology with improved cognition. Lahijanian et al. (2024) confirmed that auditory gamma entrainment enhances default mode network connectivity in human dementia patients.

**Phase-Amplitude Coupling (PAC):**
PAC measures how strongly high-frequency gamma amplitude (38-42 Hz) is modulated by lower-frequency theta phase (4-8 Hz). Tort et al. (2010) established the Modulation Index as the standard quantitative measure. High PAC indicates successful entrainment; low PAC indicates the brain has lost synchronization with the stimulus.

**Neural Habituation:**
Thompson & Spencer (1966) established that repeated identical stimuli produce progressively weaker neural responses. In 40 Hz entrainment, this means fixed schedules become less effective over time because the brain "tunes out" the repetitive stimulus, producing diminishing PAC.

**The Gap:**
No existing system predicts future entrainment state to enable proactive control. Current approaches either use fixed schedules (no adaptation) or reactive thresholds (respond after decline has already occurred, introducing delay).

**[FIGURE 1: Fixed vs. Adaptive Scheduling Concept — CREATE]**

*Two-panel schematic diagram.*

*Left panel — "Fixed Schedule (Current)":*
- *Top: flat line labeled "Stimulation" showing uniform 40s ON / 20s OFF blocks*
- *Bottom: fluctuating PAC signal showing periods where stimulation continues during high PAC (wasted) and stops during low PAC (missed)*
- *Red X marks on misaligned regions*

*Right panel — "Adaptive Schedule (This Project)":*
- *Top: variable-length ON/OFF blocks that track the PAC signal*
- *Bottom: same PAC signal, but stimulation aligns with low-PAC periods*
- *Green checkmarks on aligned regions*
- *Arrow from PAC signal to controller decision labeled "TCN predicts 5-10s ahead"*

*Attribution: Author-generated diagram.*

---

### HYPOTHESIS / ENGINEERING GOAL (48-72pt header, 24pt+ body)

**Hypothesis:** A causal temporal convolutional network can predict future PAC at 5-10 second horizons where simpler methods fail, enabling adaptive stimulation scheduling that targets periods of genuine therapeutic need.

**Engineering Goals:**

1. **Prediction:** Build a deep learning model that predicts brain entrainment state 5-10 seconds into the future, the minimum lead time required for a controller to act proactively

2. **Control:** Integrate predictions into a closed-loop controller that decides when to stimulate, rest, or maintain current state

3. **Validation:** Demonstrate on real patient EEG data (not just simulation) that predictive control outperforms both fixed schedules and reactive approaches

4. **Robustness:** Show the advantage is consistent across patients and robust to modeling assumptions about neural fatigue

---

## ============================
## CENTER PANEL: WHAT / HOW
## ============================

---

### MATERIALS (48-72pt header, 24pt+ body)

**Dataset:**
- 35 dementia patients, OpenNeuro ds005048 (Lahijanian et al., 2024)
- 19-channel EEG at 250 Hz sampling rate; 7 frontal channels selected (Fp1, Fp2, F3, F4, F7, F8, Fz)
- Alternating Stimulus (40 Hz AM auditory) and Rest epochs, 20-40 seconds each
- 17,283 two-second analysis windows extracted
- Subject-level train/validation/test splits (24/5/6 subjects) to prevent within-subject data leakage

**Software & Compute:**
- Python 3.13, PyTorch (deep learning framework)
- All training and inference run on Apple Silicon (MPS), no cloud GPU required
- Full pipeline: preprocessing, PAC computation, model training, closed-loop simulation, statistical analysis

**Two Neural Networks (sized for dataset to prevent overfitting):**

| | EEGNet | Causal TCN |
|---|---|---|
| **Purpose** | Estimate current PAC from raw EEG | Predict future PAC from history |
| **Parameters** | 1,457 (12 samples/param) | 31,043 |
| **Input** | Raw EEG (7 ch x 500 samples) | 73 features x 20 timesteps |
| **Architecture** | Temporal + depthwise spatial conv | Dilated causal conv (d=1,2,4,8) |
| **Output** | Current PAC estimate | Future PAC (5s horizon) |
| **Key feature** | Real-time inference | 44-second receptive field, causal (no future leakage) |

- 8 architectures tested (1,457 to 1.1M parameters); all converge near same R², confirming a data ceiling rather than model limitation

---

### METHODS (48-72pt header, 24pt+ body)

**PAC Computation.** To quantify how well a patient's brain is entrained to the 40 Hz stimulus, I computed phase-amplitude coupling (PAC) using the Modulation Index method (Tort et al., 2010). PAC measures how strongly high-frequency gamma amplitude (38-42 Hz) is modulated by lower-frequency theta phase (4-8 Hz). When the brain is successfully entrained, gamma oscillations lock to the theta rhythm, producing a high Modulation Index. When entrainment is lost, gamma and theta decouple and the index drops. I computed PAC at the epoch level (full 20-40 second stimulus or rest blocks) and assigned the value to each constituent 2-second window within that epoch.

**Causal Temporal Dataset Construction.** To predict future PAC, I constructed temporal sequences from the processed EEG windows. Each timestep contains 73 input features: 61 spectral power features capturing band power across frequency ranges, 7 PAC-derived features reflecting current coupling strength and recent trends, and 5 stimulation context features encoding whether the patient is currently receiving stimulation or resting, and for how long. The model receives 20 timesteps of history (20 seconds) and predicts PAC 5 seconds into the future. Crucially, the dataset is strictly causal: no input feature at time *t* contains any information from time *t+1* or beyond. I verified this with a dedicated leakage audit. All features and targets were z-score normalized using statistics computed only from the training set, so no information from validation or test subjects could leak into the model.

**Closed-Loop Controller.** The controller takes the TCN's predicted future PAC and turns it into a stimulation decision. It maintains a rolling 30-second baseline of each patient's recent PAC values and converts the prediction into a personalized z-score. If the z-score falls below -0.5, meaning coupling is predicted to decline, the controller triggers STIMULATE. If it rises above +0.5, meaning coupling is predicted to remain strong, the controller signals REST. Otherwise it holds the current state (MAINTAIN). A 5-second hysteresis window prevents rapid switching between states. Because the TCN predicts 5 seconds ahead, the controller begins stimulating before the patient's coupling actually drops, rather than waiting to react after the decline has already occurred.

**[FIGURE 2: System Architecture Flowchart — CREATE]**

*Flowchart showing the closed-loop pipeline:*
1. *Patient icon with EEG headset →*
2. *"Raw EEG (7 frontal channels)" box →*
3. *"EEGNet (1,457 params)" box → "Current PAC Estimate" →*
4. *"Feature Extraction (73 features)" box →*
5. *"Causal TCN (31K params)" box → "Predicted PAC (5s ahead)" →*
6. *"Closed-Loop Controller" decision diamond → three outputs: STIMULATE / REST / MAINTAIN*
7. *Arrow loops back from controller output to patient (audio speaker icon)*
8. *Label inference time: "<50ms total"*

*Attribution: Author-generated diagram.*

---

### PROCEDURES (48-72pt header, 24pt+ body)

**Model Training.** I trained the EEGNet on raw EEG windows to estimate current PAC, using mean squared error (MSE) loss, the Adam optimizer, and gradient clipping at max_norm=1.0 to stabilize training. Early stopping halted training when validation performance stopped improving, preventing the model from memorizing the training data. I trained the Causal TCN on temporal sequences to predict future PAC using a combined loss function: Huber loss on the primary PAC prediction plus a multi-task penalty that encourages the model to correctly predict the *direction* of PAC change, not just the absolute value. The learning rate was reduced automatically when validation loss plateaued, and training stopped if 20 consecutive epochs passed without improvement (early stopping patience of 20). All hyperparameter decisions were made using the validation set (5 subjects). The test set (6 subjects) was used only for the final reported evaluation and was never seen during model development.

**Validation Protocol.** For the primary validation, I replayed the TCN controller on all 35 subjects' actual EEG recordings. The controller processed each subject's data as if running in real time, making stimulation decisions at every 2-second window based on the model's predictions. This tests the controller on real brain data, though because the recordings are historical, the controller cannot observe how the brain would respond to its decisions (offline counterfactual replay). For a secondary validation, I ran closed-loop simulations that model neural fatigue, where the brain's response to stimulation progressively weakens over time. I tested across 6 fatigue severity levels (none through severe), running 50 independent 600-second trials per condition. All statistical comparisons used Wilcoxon signed-rank tests (non-parametric, paired), bootstrap 95% confidence intervals, and Hedges' g effect sizes. I compared four control strategies: Fixed Schedule (the current clinical standard of 40s on / 20s off), Reactive Threshold (responds to current PAC after decline has already occurred), PI Controller (proportional-integral feedback), and Alignment Oracle (perfect future knowledge, serving as the theoretical upper bound on what any controller could achieve).

---

### DATA / CHARTS / MODELS (48-72pt header)

**[FIGURE 3: Prediction Horizon Sweep — CENTRAL FINDING]**

*Source: Generate from data points below (line graph).*

*X-axis: Prediction Horizon (1, 2, 3, 5, 8, 10 seconds)*
*Y-axis: R² (-0.4 to 0.9)*
*Three lines:*
- *Persistence baseline (blue): 0.760, 0.488, 0.234, -0.267, -0.276, -0.256*
- *Ridge regression (orange): 0.812, 0.542, 0.254, -0.393, -0.211, -0.212*
- *Causal TCN (green): 0.735, 0.470, 0.277, 0.254, 0.240, 0.278*

*Shading: light red below R²=0 ("Worse than mean prediction"), light green for 5-10s zone ("Controller-relevant horizon"). Double-headed arrow showing "+0.5 R² margin" in the 5-10s zone.*

**Interpretation:** At 1-2 second horizons, simple baselines (just repeating the last value) work fine. But at 5-10 seconds, the lead time a controller needs to act proactively, all baselines collapse below zero while the TCN maintains R² ≈ 0.25. This +0.5 margin is what makes predictive control possible.

**[FIGURE 4: Real-Data Controller Timeline — `results/figures/timeline_example.png`]**

*Existing figure. Shows a real test subject (sub-15) with:*
- *Top panel: actual PAC signal with low-PAC (orange) and high-PAC (blue) epochs marked*
- *Middle panel: Reactive controller decisions (green = stimulate, gray = rest)*
- *Bottom panel: TCN controller decisions (orange = stimulate, gray = rest)*
- *Visual comparison: TCN stimulates during more low-PAC periods than Reactive*

*Attribution: Author-generated from OpenNeuro ds005048 data.*

---

## ============================
## RIGHT PANEL: WHAT LEARNED
## ============================

---

### RESULTS / FINDINGS (48-72pt header, 24pt+ body)

**Result 1: TCN Predictive Control Outperforms All Alternatives (Primary Result)**

Controller performance replayed on all 35 subjects' real EEG:

| Controller | Alignment | Low-PAC Targeting | PAC Gap (µV²) |
|---|---|---|---|
| Fixed Schedule | 45.0% | 61.4% | -6.6 (wrong direction) |
| Reactive | 64.5% | 51.7% | +21.1 |
| **TCN Predictive** | **72.1%** | **82.6%** | **+30.5** |
| Oracle (upper bound) | 100.0% | 100.0% | +33.3 |

TCN vs Reactive: Alignment g = +1.31, Low-PAC targeting g = +4.47, PAC gap g = +1.57 (all p < 0.001, Wilcoxon signed-rank). TCN reaches **91% of the theoretical oracle bound**.

**[FIGURE 5: Controller Comparison — `results/figures/controller_comparison.png`]**

*Existing figure. Grouped bar chart showing 6 controllers x 3 metrics (Alignment, Low-PAC Stim Rate, High-PAC Rest Rate) with error bars and significance brackets (g = 1.31, g = 4.47).*

*Attribution: Author-generated from OpenNeuro ds005048 data.*

**Result 2: Every Patient Benefits**

**[FIGURE 6: Per-Subject Clinical Utility — `results/figures/per_subject_utility.png`]**

*Existing figure. Scatter plot of TCN utility (y-axis) vs Reactive utility (x-axis) for all 35 subjects. Every point falls above the y = x diagonal, indicating every subject benefits from TCN control. Points colored by split (Train/Val/Test) to show generalization.*

*Attribution: Author-generated from OpenNeuro ds005048 data.*

35/35 subjects (100%) show higher clinical utility with TCN vs Reactive (binomial p < 0.001). The advantage holds across train (24), validation (5), and test (6) subject splits, including 6 subjects the model never saw during training.

**Result 3: Adaptive Advantage Increases with Fatigue**

Simulation results across 6 fatigue severity levels (n = 50 trials each):

| Fatigue Level | Fixed Efficiency | Adaptive Efficiency | Improvement |
|---|---|---|---|
| None | 0.343 | 0.375 | +9.5%*** |
| Mild | 0.341 | 0.375 | +10.0%*** |
| Moderate | 0.335 | 0.366 | +9.0%*** |
| High | 0.319 | 0.354 | +10.8%*** |
| Severe | 0.316 | 0.352 | +11.2%*** |

***p < 0.001, Wilcoxon signed-rank, Hedges' g = 1.7-2.4 (large-very large effects)

The adaptive advantage generally grows from +9.0% to +11.2% as fatigue worsens, exactly when personalization matters most.

**Result 4: Robust Across Fatigue Model Assumptions**

Tested under 4 different mathematical models of neural fatigue (n = 50 trials each):

| Fatigue Model | Advantage | p-value | Hedges' g |
|---|---|---|---|
| Exponential Decay | +9.0% | 1.8 × 10⁻¹⁵ | 2.31 |
| Step Function | +6.9% | 4.4 × 10⁻¹⁴ | 1.21 |
| Heterogeneous (50/50) | +8.9% | 2.5 × 10⁻¹⁴ | 1.71 |
| Saturation (synaptic) | +19.0% | 1.8 × 10⁻¹⁵ | 3.66 |

The adaptive scheduling advantage is not an artifact of one fatigue assumption. It holds under all four models with large effect sizes.

**Data Integrity:**
- Subject-level splits prevent data leakage (6 held-out test subjects never seen during training)
- Shuffle-label test: R² = -0.332 (model learns real signal, not artifacts)
- Causal dataset construction verified (no future information in input features)
- Feature ablation confirms interpretability: PAC-derived features drive prediction, spectral features provide independent signal

---

### CONCLUSIONS / FURTHER RESEARCH (48-72pt header, 24pt+ body)

**Conclusions:**

1. At 5-10 second prediction horizons, the causal TCN maintains R² ≈ 0.25 while all baselines collapse below zero, a +0.5 R² margin at the operationally relevant range for proactive neural stimulation control

2. When integrated into a closed-loop controller and validated on real patient EEG, the TCN achieved 72.1% alignment versus 64.5% reactive (p < 0.001), targeting 82.6% of low-PAC windows compared to 51.7%, a 60% improvement in therapeutic targeting

3. All 35 patients benefited from TCN-based control, including 6 held-out test subjects, demonstrating generalization across individual EEG patterns

4. The adaptive advantage increases with fatigue severity (+9.0% to +11.2%) and holds across four different fatigue model assumptions, confirming robustness

5. Half of patients habituate to stimulation while half do not, validating the fundamental need for personalized rather than fixed scheduling

**Limitation:** Real-data validation uses offline replay (counterfactual decisions on recorded EEG), not live closed-loop streaming. The system makes decisions on real brain data but cannot observe the brain's response to those decisions.

**Further Research:**

- Deploy with live EEG streaming for real-time crossover validation (adaptive vs fixed within same session)
- Record 30-60 minute sessions to capture the full habituation time course
- Replace the heuristic controller with reinforcement learning for long-horizon optimization
- Extend to multi-biomarker control (PAC + spectral power + connectivity)

**Broader Impact:**

- Personalized neurostimulation could reduce patient burden through shorter, targeted therapy sessions
- The adaptive scheduling principle applies to any repetitive neural stimulation therapy (tDCS, TMS, light/sound entrainment)
- Lightweight models (1,457 + 31,000 parameters) enable deployment on embedded/wearable devices

---

### REFERENCES (48-72pt header, 24pt body)

1. Iaccarino, H. F., et al. (2016). Gamma frequency entrainment attenuates amyloid load and modifies microglia. *Nature*, 540(7632), 230-235.

2. Martorell, A. J., et al. (2019). Multi-sensory gamma stimulation ameliorates Alzheimer's-associated pathology and improves cognition. *Cell*, 177(2), 256-271.

3. Tort, A. B., et al. (2010). Measuring phase-amplitude coupling between neuronal oscillations of different frequencies. *Journal of Neurophysiology*, 104(2), 1195-1210.

4. Lawhern, V. J., et al. (2018). EEGNet: A compact convolutional neural network for EEG-based brain-computer interfaces. *Journal of Neural Engineering*, 15(5), 056013.

5. Lahijanian, M., et al. (2024). Auditory gamma-band entrainment enhances default mode network connectivity in dementia patients. *Scientific Reports*, 14, 13153.

6. Thompson, R. F., & Spencer, W. A. (1966). Habituation: A model phenomenon for the study of neuronal substrates of behavior. *Psychological Review*, 73(1), 16-43.

### ACKNOWLEDGEMENTS

**Data Source:** OpenNeuro dataset ds005048 (Lahijanian et al., 2024). All EEG data used under open access license.

**AI Disclosure:** AI coding assistant (Claude Code, Anthropic) used for software development. All experimental design, data analysis, scientific interpretation, and conclusions are the student's own work.

---

## ============================
## FIGURE SUMMARY & PRODUCTION
## ============================

| # | Figure | Source | Status | Placement | Size Estimate |
|---|--------|--------|--------|-----------|---------------|
| 1 | Fixed vs Adaptive Concept | CREATE (schematic) | TO CREATE | Left panel, below Background | ~12" x 6" |
| 2 | System Architecture Flowchart | CREATE (diagram) | TO CREATE | Center panel, Methods section | ~16" x 6" |
| 3 | Horizon Sweep (line graph) | CREATE from data points | TO CREATE | Center panel, Data section | ~16" x 8" (LARGEST) |
| 4 | Real-Data Timeline | `results/figures/timeline_example.png` | DONE | Center panel, below Fig 3 | ~16" x 5" |
| 5 | Controller Comparison | `results/figures/controller_comparison.png` | DONE | Right panel, Result 1 | ~12" x 7" |
| 6 | Per-Subject Utility | `results/figures/per_subject_utility.png` | DONE | Right panel, Result 2 | ~10" x 7" |

**Total figures: 6** (4 data figures + 2 conceptual diagrams)

**Figures NOT used on board** (available in notebook or as backup):
- `pac_targeting_gap.png` — supports Result 1 but controller_comparison covers it
- `stim_vs_alignment.png` — interesting but not essential; keep in notebook
- `threshold_sensitivity.png` — supports robustness claim; reference verbally or keep in notebook

**Figure production notes:**
- All generated figures are 300 DPI PNG + vector PDF (print-ready)
- For printing: use PDF versions for figures 4-6, scale to target size
- Figures 1-3 need to be created; use consistent style (white background, large axis labels ≥ 18pt, colorblind-safe palette)
- Figure 3 (Horizon Sweep) is the most important figure on the board — give it the most space and place it at eye level in the center panel

---

## ============================
## WORD COUNT ESTIMATE
## ============================

| Section | Words (approx) |
|---------|---------------|
| Introduction | ~95 |
| Background / Literature Review | ~190 |
| Hypothesis / Engineering Goal | ~100 |
| Materials, Methods, & Procedures | ~250 |
| Results text (all 4 results) | ~250 |
| Data Integrity | ~45 |
| Conclusions | ~135 |
| Further Research | ~50 |
| Broader Impact | ~45 |
| **Total body text** | **~1,160** |

This is appropriate for a 48" x 56" board at 24pt font. The existing V1 had ~600 words for a standard board; this version nearly doubles the content to fill the larger format. Tables and figures will occupy approximately 50% of the board area.

---

## ============================
## DESIGN & PRINTING NOTES
## ============================

**Color scheme suggestion:**
- Header backgrounds: dark blue or dark teal (professional, medical/neuro feel)
- Body text: black on white
- Accent color: green (for TCN/adaptive results — matches figure palette)
- Alert color: red (for baselines failing / wrong direction)

**Typography suggestion:**
- Title: 150-200pt, bold sans-serif (e.g., Helvetica, Arial, Calibri)
- Section headers: 48-72pt, bold
- Body text: 24-28pt, regular
- Table text: 24pt
- Figure captions: 20-24pt, italic
- References: 20-24pt

**Layout priority (eye-level placement for judges):**
- Figure 3 (Horizon Sweep) — center panel, middle — this is the "hero" finding
- Figure 5 (Controller Comparison) — right panel, upper — the primary real-data result
- Results table — right panel, alongside Figure 5
- Conclusions — right panel, slightly below eye level

**Panel construction:**
- Standard tri-fold foam board OR printed vinyl banner mounted on foam core
- If tri-fold: left/right panels fold inward (~14" each), center panel ~20"
- If flat banner: single 48" x 56" print, mounted on foam board with fold lines

---

*Version 2 — refined from POSTER_BOARD.md with expanded content for 48" x 56" format, Synopsys compliance verified, figure placement specified.*
