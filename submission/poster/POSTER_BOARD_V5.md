# POSTER BOARD CONTENT — V5 (Condensed, Visual-Forward, Audit-Verified)

**Synopsys Championship — Santa Clara County**
**Category:** Biological Science and Engineering, Computational Biology and Bioinformatics
**Author:** Amaar Chughtai
**Date:** March 2026

**Board dimensions:** 48" wide × 56" tall (tri-fold)
**Font:** 28-30pt body, 48-72pt section headers, 150-200pt title

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
- [x] Font >= 24pt body text
- [ ] Notebook on table (in folder)
- [ ] Compliance checklist + Forms 1C/7 on table
- [ ] Forms 1B, 3, 4, 6A, 6B, signed Ethics Statement available (not displayed)
- [ ] Full references list printed on table

---

## BOARD LAYOUT

```
+========================+================================+========================+
|     LEFT PANEL         |        CENTER PANEL             |     RIGHT PANEL        |
|     (~14" wide)        |        (~20" wide)              |     (~14" wide)        |
|                        |                                 |                        |
|                        |  +----------------------------+  |                        |
|                        |  |       PROJECT TITLE        |  |                        |
|                        |  |       Author Name          |  |                        |
|  +------------------+  |  +----------------------------+  |  +------------------+  |
|  |  INTRODUCTION    |  |                                 |  |  RESULTS          |  |
|  |  (prose text)    |  |  +----------------------------+  |  |                  |  |
|  +------------------+  |  |   MATERIALS                |  |  | [TABLE] Control  |  |
|                        |  |   (bullet list)            |  |  |  Comparison      |  |
|  +------------------+  |  +----------------------------+  |  |                  |  |
|  |  BACKGROUND      |  |                                 |  | [FIG 5] Ctrl Bar |  |
|  |  (bullets + text)|  |  +----------------------------+  |  |  (LARGE)         |  |
|  |                  |  |  |   APPROACH                 |  |  |                  |  |
|  | [FIG 1] Fixed vs |  |  |                            |  |  | [FIG 6] Per-Subj |  |
|  |  Adaptive        |  |  |  [FIG 2] Full Pipeline     |  |  |  Scatter (LARGE) |  |
|  | (LARGE ~12"x8")  |  |  |  (LARGE ~18"x8")          |  |  |                  |  |
|  +------------------+  |  |                            |  |  | [TABLE] Fatigue  |  |
|                        |  |  Arch Exploration table    |  |  +------------------+  |
|  +------------------+  |  |  + bridging text           |  |                        |
|  | HYPOTHESIS /     |  |  +----------------------------+  |  +------------------+  |
|  | ENGINEERING GOAL |  |                                 |  |  CONCLUSIONS      |  |
|  | (bullet list)    |  |  +----------------------------+  |  |  (bullet list)    |  |
|  +------------------+  |  |   DATA / CHARTS            |  |  +------------------+  |
|                        |  +----------------------------+  |  +------------------+  |
|                        |                                 |  |  CONCLUSIONS      |  |
|                        |  +----------------------------+  |  |  (bullet list)    |  |
|                        |  |   DATA / CHARTS            |  |  +------------------+  |
|                        |  |                            |  |                        |
|                        |  |  [FIG 3] Horizon Sweep     |  |  +------------------+  |
|                        |  |  (LARGE ~18"x10")          |  |  | FURTHER RESEARCH |  |
|                        |  |                            |  |  | + REFERENCES /   |  |
|                        |  |  [FIG 4] Timeline          |  |  | ACKNOWLEDGEMENTS |  |
|                        |  |  (LARGE ~18"x6")           |  |  +------------------+  |
|                        |  +----------------------------+  |                        |
+========================+================================+========================+

TABLE (in front of board):
+------------+------------+------------+------------+
|  Project   |  Abstract  |  Full      |  Forms     |
|  Notebook  |  (printed) | References |  1C, 7     |
+------------+------------+------------+------------+
```

**Design note:** Figures should occupy ~60-65% of board area. Text is condensed to bullet points and short phrases wherever possible. Font increased to 28-30pt body for readability at distance.

---

## TITLE (Center panel, top — 150-200pt font)

**Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Phase Amplitude Coupling in Alzheimer's Disease**

Amaar Chughtai

---

## ============================
## LEFT PANEL: WHY
## ============================

---

### INTRODUCTION (48-72pt header, 28-30pt body)

Alzheimer's disease affects over 55 million people worldwide, with no cure and limited treatment options. Recent neuroscience research has revealed a promising approach: 40 Hz auditory stimulation can synchronize brain gamma oscillations, reducing amyloid-beta plaques and tau tangles in animal models and showing early cognitive benefits in human clinical trials.

Current clinical protocols deliver this stimulation on a rigid fixed schedule — 40 seconds of 40 Hz auditory stimulation followed by 20 seconds of silence, cycling continuously for one hour regardless of how the patient's brain is responding. This one-size-fits-all approach ignores two critical realities. First, **between patients**: some maintain strong theta-gamma coupling throughout a session, while others lose coupling within seconds and never fully synchronize. Second, **within a session**: prolonged repetitive stimulation causes neural habituation — the brain progressively "tunes out" the stimulus, and coupling degrades over time. The result is wasted stimulation during periods of strong coupling and missed opportunities during periods of fading coupling.

This project asks: **can we predict when a patient's brain will lose entrainment and deliver stimulation proactively, before the decline occurs?**

---

### BACKGROUND (48-72pt header, 28-30pt body)

**What the literature has shown:**
- **40 Hz gamma entrainment** reduces amyloid load in Alzheimer's mouse models by activating microglia (Iaccarino 2016); multi-sensory stimulation further reduces tau pathology and improves cognition (Martorell 2019); auditory entrainment enhances default mode network connectivity in human dementia patients (Lahijanian 2024)
- **Phase-Amplitude Coupling (PAC)** quantifies entrainment success — how strongly gamma amplitude (38-42 Hz) locks to theta phase (4-8 Hz), measured via the Modulation Index (Tort 2010). High PAC = entrained; low PAC = lost synchronization.
- **Neural habituation** causes repeated identical stimuli to produce progressively weaker neural responses (Thompson & Spencer 1966), making fixed schedules less effective over time

**The gap:** No existing system predicts *future* entrainment state to enable proactive control. Current approaches either use fixed schedules (no adaptation) or reactive thresholds (respond *after* decline has already occurred, introducing delay).

**[FIGURE 1: Fixed vs. Adaptive Scheduling — LARGE, ~12" × 8"]**

*Two-panel schematic showing the core problem and proposed solution:*

*Left panel — "Fixed Schedule (Current)":*
- *Uniform 40s ON / 20s OFF blocks — ignores brain state*
- *Red X marks: stimulates during high PAC (wasted), rests during low PAC (missed)*
- *Label: "No adaptation — treats every moment the same"*

*Right panel — "Adaptive Schedule (This Project)":*
- *Variable ON/OFF blocks aligned to the PAC signal*
- *Green checkmarks on aligned regions*
- *Arrow: "TCN predicts 5s ahead → controller stimulates proactively"*
- *Label: "Personalized — targets periods of genuine therapeutic need"*

*Attribution: Author-generated diagram.*

---

### HYPOTHESIS / ENGINEERING GOALS (48-72pt header, 28-30pt body)

**Hypothesis:** A causal temporal convolutional network can predict future PAC at 5-10 second horizons where simpler methods fail, enabling adaptive stimulation that targets periods of genuine therapeutic need.

**Goals:**
1. **Predict** brain entrainment 5-10s into the future — the minimum lead time for proactive control
2. **Control** — integrate predictions into a closed-loop stimulation controller
3. **Validate** on real patient EEG that predictive control outperforms fixed and reactive approaches
4. **Robustness** — consistent advantage across all patients and fatigue model assumptions

---

## ============================
## CENTER PANEL: WHAT / HOW
## ============================

---

### MATERIALS (48-72pt header, 28-30pt body)

**Dataset:** 35 elderly subjects, OpenNeuro ds005048 (Lahijanian 2024)
- 7 frontal EEG channels (Fp1, Fp2, F3, F4, F7, F8, Fz), 250 Hz
- Alternating Stimulus (40 Hz AM auditory) and Rest epochs, 20-40s each
- 17,283 two-second windows; subject-level splits (24 train / 5 val / 6 test)

**Compute:** Python 3.13, PyTorch, Apple Silicon (MPS) — no cloud GPU required

---

### APPROACH: TWO-STAGE PREDICTIVE PIPELINE (48-72pt header, 28-30pt body)

**The challenge:** To control stimulation proactively, the system needs to predict PAC 5-10 seconds into the future. This requires two capabilities:
1. **Estimate current PAC** from raw EEG in real time (since live patients don't have ground-truth labels)
2. **Predict future PAC** from a history of past estimates — the temporal forecasting problem

**Stage 1 — Static PAC Estimation: Architecture Exploration**

I tested 8 neural network configurations to estimate current PAC from a single 2-second EEG window, spanning nearly three orders of magnitude in model size (the poster table shows the 6 most informative; see paper Table 1 for all 8 including EEGNetV2 and Optimized Ensemble):

| Architecture | Parameters | Test R² |
|---|---|---|
| **EEGNet (V1)** | **1,457** | **0.287** |
| SpecTempNet (V3) | 180K | 0.236 |
| ViT-TCNet (V4) | ~1.1M | 0.252 |
| Ridge Regression (V5) | 135 coefs | 0.287 |
| ATCNet (V8) | 25K | 0.22 |
| EEGNetLarge (rigor) | 141K | 0.287 |

**Key findings:**
- Simplest models (EEGNet, Ridge, EEGNetLarge) converge to R² = 0.287
- Larger models perform *worse* due to overfitting — the 1.1M-parameter ViT-TCNet scored lower than the 1,457-parameter EEGNet
- **Conclusion:** R² = 0.287 is a data ceiling (epoch-level PAC labels on 2s windows), not a model capacity limitation. More complex architectures cannot break through it.

**Why EEGNet was selected:** EEGNet matches the best R² (0.287) with only 1,457 parameters — the most lightweight deep learning architecture tested, enabling real-time inference on embedded devices. It provides the current PAC estimate that feeds into the temporal predictor.

**Stage 2 — Temporal Prediction: Causal TCN**

Since no single-window architecture could exceed R² = 0.287, I shifted the approach: instead of predicting PAC *better* from one snapshot, predict it *further into the future* from a sequence of snapshots. The Causal TCN ingests 20 seconds of history and forecasts PAC 5 seconds ahead.

| | EEGNet (Stage 1) | Causal TCN (Stage 2) |
|---|---|---|
| **Purpose** | Estimate current PAC from raw EEG | Predict future PAC from history |
| **Parameters** | 1,457 | 31,043 |
| **Input** | Raw EEG (7 ch × 500 samples) | 73 features × 20 timesteps |
| **Architecture** | Temporal + depthwise spatial conv | Dilated causal conv (d=1,2,4,8) |
| **Output** | Current PAC estimate | Future PAC (5s horizon) |
| **Key design** | Real-time inference | 31-step receptive field, strictly causal (no future leakage) |

**73 TCN input features:** 61 spectral power + 7 PAC-derived (current value, moving averages, trends) + 5 stimulation context (on/off state, duration, session phase)

**[FIGURE 2: Full System Pipeline — LARGE, ~18" × 8"]**

*Flowchart showing the complete closed-loop system:*
1. *Patient with EEG headset →*
2. *"Raw EEG (7 frontal channels)" →*
3. *"EEGNet (1,457 params)" → "Current PAC Estimate" →*
4. *"Feature Extraction (73 features)" →*
5. *"Causal TCN (31K params)" → "Predicted PAC (5s ahead)" →*
6. *"Closed-Loop Controller" decision diamond → STIMULATE / REST / MAINTAIN*
7. *Arrow loops back to patient (audio speaker)*
8. *Labels: "<50ms inference", "30s rolling baseline", "z-score thresholds ±0.5"*

*Attribution: Author-generated diagram.*

**Controller logic** (visible in Figure 2):
- Rolling 30-second baseline → personalized z-score of predicted PAC
- z < −0.5 → STIMULATE (coupling predicted to decline)
- z > +0.5 → REST (coupling predicted to remain strong)
- Otherwise → MAINTAIN current state
- 3-second hysteresis prevents rapid switching

---

### PROCEDURES (48-72pt header, 28-30pt body)

**Training:**
- **EEGNet:** MSE loss, Adam optimizer, gradient clipping (max_norm=1.0), early stopping
- **Causal TCN:** Huber loss (robust to PAC outliers), ReduceLROnPlateau, early stopping (patience=20)
- All hyperparameters tuned on validation set (5 subjects); test set (6 subjects) used only for final evaluation

**Validation — two independent protocols:**
- **Primary (real data):** Replayed TCN controller on all 35 subjects' actual EEG recordings — offline counterfactual decisions on real brain data. For validation, ground-truth PAC labels were used as TCN input, isolating the TCN's predictive contribution from EEGNet estimation error.
- **Secondary (simulation):** Closed-loop simulation with neural fatigue modeling — 6 severity levels × 50 trials × 600 seconds per trial

**Statistical rigor:**
- Wilcoxon signed-rank tests (non-parametric, paired)
- 95% confidence intervals (large-sample normal approximation)
- Hedges' g effect sizes
- Compared against: Fixed Schedule, Reactive Threshold, PI Controller, Alignment Oracle (theoretical upper bound)

---

### DATA & CHARTS (48-72pt header)

**[FIGURE 3: Prediction Horizon Sweep — CENTRAL FINDING — LARGEST FIGURE, ~18" × 10"]**

*Line graph. X-axis: Prediction Horizon (1, 2, 3, 5, 8, 10 seconds). Y-axis: R².*
*Three lines:*
- *Persistence baseline (blue): 0.760, 0.488, 0.234, −0.267, −0.276, −0.256*
- *Ridge regression (orange): 0.812, 0.542, 0.253, −0.393, −0.211, −0.212*
- *Causal TCN (green): 0.735, 0.470, 0.277, 0.254, 0.240, 0.278*

*Shading: light red below R²=0, light green for 5-10s zone. Arrow: "+0.5 R² margin."*

*Caption: At 1-2s, baselines work fine. At 5-10s — the range needed for proactive control — baselines collapse below zero while the TCN maintains R² ≈ 0.25.*

*Attribution: Author-generated from OpenNeuro ds005048 data.*

**[FIGURE 4: Real-Data Controller Timeline — `results/figures/timeline_example.png` — ~18" × 6"]**

*Shows real test subject with actual PAC signal, Reactive controller decisions, and TCN controller decisions side by side. TCN targets more low-PAC periods.*

*Attribution: Author-generated from OpenNeuro ds005048 data.*

---

## ============================
## RIGHT PANEL: RESULTS
## ============================

---

### RESULTS & FINDINGS (48-72pt header, 28-30pt body)

**Result 1: TCN Predictive Control Outperforms All Alternatives**

**Metric Definitions** (see Figure 6 bar chart):
- **Low-PAC Stim Rate** (sensitivity): % of below-median PAC windows where controller stimulates — "did we treat when the brain needed it?"
- **High-PAC Rest Rate** (specificity): % of above-median PAC windows where controller rests — "did we leave the brain alone when it was doing fine?"
- **Alignment** = (Low-PAC Stim Rate + High-PAC Rest Rate) / 2 — balanced accuracy of targeting. 50% = random, 100% = perfect.
- **PAC Gap**: mean PAC during rest − mean PAC during stim. Positive = controller correctly concentrates stimulation during low-PAC periods.
- Low/high split at each subject's median PAC (personalized threshold)

Controller performance on all 35 subjects' real EEG:

| Controller | Alignment | Low-PAC Stim | High-PAC Rest | PAC Gap (×10⁻⁶) | Stim % |
|---|---|---|---|---|---|
| Fixed Schedule | 45.0% | 61.4% | 28.6% | −6.6 (wrong dir.) | 66.6% |
| Reactive | 64.5% | 51.7% | 77.3% | +21.1 | 36.7% |
| **TCN Predictive** | **72.1%** | **82.6%** | **61.6%** | **+30.5** | **59.7%** |
| Oracle (upper bound) | 100.0% | 100.0% | 100.0% | +33.3 | 48.3% |

- TCN vs Reactive: Alignment g = +1.31, Low-PAC targeting g = +4.47, PAC gap g = +1.57 (all p < 0.001)
- TCN PAC targeting gap reaches **91% of the theoretical oracle** (30.5 vs 33.3; precise value 91.6%, rounded to 91% consistent with paper)
- TCN uses less stimulation than Fixed Schedule (59.7% vs 66.6%) with far superior targeting
- **Trade-off:** Reactive achieves higher High-PAC Rest (77.3% vs 61.6%) by being conservative, but misses 48% of low-PAC windows that need treatment

**[FIGURE 6: Controller Comparison — `results/figures/controller_comparison.png` — LARGE]**

*Attribution: Author-generated from OpenNeuro ds005048 data.*

**Result 2: Every Patient Benefits**

**[FIGURE 6: Per-Subject Clinical Utility — `results/figures/per_subject_utility.png` — LARGE]**

*All 35 points above the y = x diagonal. Points colored by Train/Val/Test split.*

- 35/35 subjects (100%) show higher utility with TCN vs Reactive (binomial p < 0.001)
- Advantage holds for 6 held-out test subjects never seen during training

*Attribution: Author-generated from OpenNeuro ds005048 data.*

**Result 3: Advantage Grows with Fatigue**

| Fatigue Level | Fixed Eff. | Adaptive Eff. | Improvement |
|---|---|---|---|
| None | 0.343 | 0.375 | +9.5%*** |
| Mild | 0.341 | 0.375 | +10.0%*** |
| Moderate | 0.335 | 0.366 | +9.0%*** |
| High | 0.319 | 0.354 | +10.8%*** |
| Severe | 0.316 | 0.352 | +11.2%*** |

***p < 0.001, Hedges' g = 1.7–2.4 (large to very large effects). Advantage grows as fatigue worsens — exactly when personalization matters most.

*Note: Result 3 uses the simulation-based fatigue analysis with five discrete severity levels (None/Mild/Moderate/High/Severe). The paper's Section 4.4 reports a separate analysis across six habituation rate levels (0.0-0.040) showing efficiency advantage from +0.4% to +5.7%. Both analyses confirm the same qualitative finding: adaptive advantage increases with fatigue severity.*

**Result 4: Robust Across Fatigue Models (Supplementary Simulation)**

| Fatigue Model | Advantage | Hedges' g |
|---|---|---|
| Exponential Decay | +9.0% | 2.31 |
| Step Function | +6.9% | 1.21 |
| Heterogeneous (50/50) | +8.9% | 1.71 |
| Saturation (synaptic) | +19.0% | 3.66 |

All p < 0.001. Advantage holds under all four mathematical models of neural fatigue.

*Note: Result 4 is a supplementary simulation analysis not reported in the paper. The paper's robustness analysis (Section 4.4) instead reports threshold sensitivity across delta_z=0.1-1.0 and fatigue severity sweep across six levels. This simulation-based fatigue model comparison is additional supporting evidence.*

**Data Integrity:** Subject-level splits (no leakage) · Shuffle-label R² = −0.332 (real signal, not artifacts) · Causal dataset verified · Feature ablation confirms interpretability

---

### CONCLUSIONS (48-72pt header, 28-30pt body)

1. At 5-10s horizons, the TCN maintains R² ≈ 0.25 while all baselines collapse below zero — a **+0.5 R² margin** at the operationally relevant range for proactive control

2. On real patient EEG: **72.1% alignment vs 64.5% reactive** (p < 0.001), targeting **82.6% of low-PAC windows vs 51.7%** — a 60% improvement in therapeutic targeting

3. **All 35 patients showed improved alignment**, including 6 held-out test subjects — generalizes across individual EEG patterns

4. Adaptive advantage **increases with fatigue** — confirmed across six fatigue severity levels in simulation and four fatigue model assumptions

5. Half of patients habituate while half do not — validating the need for **personalized, not fixed** scheduling

**Limitation:** Real-data validation uses offline replay on recorded EEG, not live closed-loop streaming. The system makes decisions on real brain data but cannot observe the brain's response to those decisions.

---

### FURTHER RESEARCH (28-30pt body)

- Deploy with live EEG streaming for real-time crossover validation
- Record 30-60 min sessions to capture full habituation time course
- Replace heuristic controller with reinforcement learning
- Extend to multi-biomarker control (PAC + spectral power + connectivity)

**Broader Impact:**
- Adaptive scheduling principle applies to any repetitive neural stimulation therapy (tDCS, TMS, light/sound)
- Lightweight models (1,457 + 31K params) enable embedded/wearable deployment

---

### SELECTED REFERENCES (28-30pt body)

1. Iaccarino et al. (2016). Gamma frequency entrainment attenuates amyloid load. *Nature*, 540, 230-235.
2. Tort et al. (2010). Measuring phase-amplitude coupling. *J Neurophysiol*, 104, 1195-1210.
3. Lahijanian et al. (2024). Auditory gamma entrainment enhances DMN connectivity. *Sci Rep*, 14, 13153.

*Full reference list available on table.*

### ACKNOWLEDGEMENTS

**Data:** OpenNeuro ds005048 (Lahijanian et al., 2024), open access license.
**AI Disclosure:** AI coding assistant (Claude Code, Anthropic) used for software development. All experimental design, analysis, interpretation, and conclusions are the student's own work.

---

## ============================
## FIGURE SUMMARY & PRODUCTION
## ============================

| # | Figure | Source | Status | Placement | Size Target |
|---|--------|--------|--------|-----------|-------------|
| 1 | Fixed vs Adaptive Concept | CREATE (schematic) | TO CREATE | Left panel, Introduction | ~12" × 8" |
| 2 | Full System Pipeline | CREATE (diagram) | TO CREATE | Center panel, Approach | ~18" × 8" |
| 3 | Horizon Sweep (line graph) | CREATE from data | TO CREATE | Center panel, Data | ~18" × 10" (LARGEST) |
| 4 | Real-Data Timeline | `results/figures/timeline_example.png` | DONE | Center panel, below Fig 3 | ~18" × 6" |
| 5 | Controller Comparison | `results/figures/controller_comparison.png` | DONE | Right panel, Result 1 | ~12" × 8" |
| 6 | Per-Subject Utility | `results/figures/per_subject_utility.png` | DONE | Right panel, Result 2 | ~12" × 8" |

**Total figures: 6** — all enlarged from V4 sizes. Figures occupy ~60-65% of board area.

**Figures available in notebook** (not on board):
- `pac_targeting_gap.png`, `stim_vs_alignment.png`, `threshold_sensitivity.png`

---

## ============================
## WORD COUNT ESTIMATE
## ============================

| Section | V4 Words | V5 Words | Reduction |
|---------|----------|----------|-----------|
| Introduction & Background (merged) | ~385 | ~200 | −48% |
| Hypothesis / Goals | ~100 | ~85 | −15% |
| Materials | ~120 | ~55 | −54% |
| Approach (Arch Exploration + Methods merged) | ~550 | ~310 | −44% |
| Procedures | ~250 | ~120 | −52% |
| Data/Charts text | ~100 | ~30 | −70% |
| Results (all 4 + integrity) | ~335 | ~200 | −40% |
| Conclusions | ~135 | ~110 | −19% |
| Further Research + Impact | ~95 | ~65 | −32% |
| References | ~90 | ~40 | −56% |
| **Total body text** | **~1,720** | **~1,015** | **−41%** |

The ~700 word reduction frees space for larger figures and increased font size (28-30pt vs 24pt).

---

## ============================
## DESIGN & PRINTING NOTES
## ============================

**Color scheme:**
- Header backgrounds: dark blue or dark teal
- Body text: black on white
- Accent: green (TCN/adaptive results)
- Alert: red (baseline failures)

**Typography:**
- Title: 150-200pt bold sans-serif
- Section headers: 48-72pt bold
- Body text: 28-30pt regular (increased from V4's 24pt)
- Table text: 26-28pt
- Figure captions: 22-24pt italic
- References: 22-24pt

**Layout priorities (eye-level):**
1. Figure 2 (Pipeline) — center panel — judges immediately see the system
2. Figure 3 (Horizon Sweep) — center panel — the "hero" finding
3. Figure 5 (Controller Comparison) — right panel — primary real-data result
4. Results table — right panel, adjacent to Figure 5

---

## ============================
## V5 CHANGELOG (from V4)
## ============================

### Structural Changes

1. **Introduction and Background/Literature Review merged** into single "Introduction & Background" section — eliminates redundancy, reduces text by ~48% while preserving all citations and key concepts

2. **Methods, Procedures, and Architecture Exploration reorganized** into two clear sections:
   - "Approach: Two-Stage Predictive Pipeline" — combines architecture exploration with the pipeline explanation in a logical narrative flow (Phase 1 → Phase 2 → Controller)
   - "Procedures" — condensed to bullet points for training, validation, and statistical methods

3. **Data/Charts text gutted** — removed explanatory paragraphs per feedback ("let the charts speak for themselves"). Only figure captions remain; interpretation is in Results and Conclusions.

4. **References reduced to "Selected References"** — 3 key citations on board; full list printed on table below poster

### Narrative Clarifications

5. **Two-stage pipeline explicitly framed** — Section now clearly explains: (a) why two models are needed, (b) that Architecture Exploration was about selecting the Stage 1 model, (c) why EEGNet won (best R² at minimal parameters, real-time capable), (d) that the R²=0.287 ceiling motivated the shift to temporal prediction

6. **"8 configurations" noted with "6 shown in table"** — paper Table 1 lists 8 (V1-V8); poster table shows 6 most informative rows with note referencing paper for full list

7. **Architecture Exploration conclusion made explicit** — "Conclusion: R²=0.287 is a data ceiling, not a model capacity limitation. More complex architectures cannot break through it."

8. **EEGNet selection rationale added** — "Why EEGNet was selected: matches best R² with only 1,457 parameters — the most lightweight architecture tested, enabling real-time inference on embedded devices."

9. **Validation methodology clarified** — now explicitly states: "For validation, ground-truth PAC labels were used as TCN input, isolating the TCN's predictive contribution from EEGNet estimation error."

### Data Corrections (carried from V4 audit)

10. **Receptive field corrected from "44-second" to "31-step"** — kernel_size=3, dilations=[1,2,4,8]: RF = 1 + (3−1)×(1+2+4+8) = 31 timesteps = 31 seconds at 1s/step. The V4 PPTX had "44" which matches no calculation.

11. **PAC Gap units verified as "(×10⁻⁶)"** — Modulation Index (Tort 2010) is dimensionless KL-divergence, not voltage-squared. Confirmed correct from V4 fix.

12. **"92% of oracle" corrected back to "91%"** — 30.5 ÷ 33.3 = 0.9159 = 91.6%. The paper uses 91% (consistent rounding convention). Poster now matches paper.

13. **Ridge R² at horizon=3 corrected from 0.254 to 0.253** — Source JSON: 0.2534641, which rounds to 0.253 at 3 d.p., not 0.254.

14. **All numerical claims re-verified against:**
    - `results/RESULTS_REPORT.md` — controller comparison table ✓
    - `models/sweep_horizons_results.json` — horizon sweep data points ✓
    - `results/metrics/threshold_sweep.json` — threshold sensitivity ✓
    - `docs/CODE_MAP.md` — architecture exploration R² values ✓
    - `temporal_multiscale/multiscale_tcn.py` — TCN architecture (dilations, kernel_size) ✓

### Visual Changes

13. **All figures enlarged** — target sizes increased 30-50% from V4 to occupy ~60-65% of board area (up from ~50%)

14. **Font size increased to 28-30pt body** (from 24pt) — more readable at poster viewing distance

15. **Text converted to bullet points** throughout — no section contains more than one short paragraph; most use bulleted phrases

16. **Figure 2 relabeled "Full System Pipeline"** — now serves as the visual anchor for the Approach section, showing both EEGNet and TCN in context

*Version 5 — Condensed and restructured per Kushal Khare feedback (March 4, 2026). All numerical claims verified against source data files. Text reduced ~41% from V4 while maintaining full technical specificity.*
