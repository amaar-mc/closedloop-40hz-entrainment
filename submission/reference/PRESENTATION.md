# Adaptive Closed-Loop Scheduling for 40 Hz Auditory Gamma Entrainment

**Presentation Script**

---

## SLIDE 1: The Problem

Good afternoon. I want to talk about a treatment that uses sound to change brainwaves — and why the way we deliver it right now is wasteful.

There's a therapy called **40 Hz auditory entrainment**. You play a 40 Hz clicking sound, and the brain's gamma oscillations synchronize to it. This synchronization — called _entrainment_ — triggers the brain's immune cleanup system: microglia start clearing amyloid-beta and tau protein, the hallmarks of Alzheimer's disease. This was discovered by Li-Huei Tsai's lab at MIT in 2016, and clinical trials by Cognito Therapeutics are ongoing.

The problem is **how we deliver it**. Current protocols use a **fixed schedule**: 40 seconds of stimulation, 20 seconds of rest, repeated for an hour. Every patient gets the same timing regardless of what their brain is actually doing.

**The question I asked: Can we do better?**

---

## SLIDE 2: Why Fixed Schedules Are Wasteful

I analyzed real EEG data from 35 elderly subjects who underwent 40 Hz stimulation. The dataset is from OpenNeuro (ds005048) — 19-channel EEG at 250 Hz, already preprocessed.

I measured **phase-amplitude coupling (PAC)** — a metric that quantifies how well the brain's gamma oscillations (38-42 Hz) are locked to the theta rhythm (4-8 Hz). Higher PAC = stronger entrainment = more therapeutic benefit.

When I replayed the fixed schedule through the data, I found:

> **50.5% of all stimulation time is wasted.** During those moments, PAC was already high or flat — the brain was already entrained, and the stimulation added nothing.

Meanwhile, during the 33% of time the patient was resting, **50% of those rest periods had below-median PAC** — the brain had _lost_ entrainment, but no stimulation was being delivered.

Fixed scheduling stimulates when it doesn't need to and rests when it shouldn't.

---

## SLIDE 3: The Idea — Predict, Then Adapt

My approach has two parts:

**Part 1: Can we predict when the brain will lose entrainment?**
If we can forecast PAC 5-10 seconds into the future, we can stimulate _before_ the drop happens — proactive rather than reactive.

**Part 2: Can we build a controller that uses those predictions?**
Given a prediction of future brain state, decide: stimulate now, or rest?

The goal isn't to maximize stimulation — it's to **maximize entrainment per unit of stimulation**. Less is more, if it's timed well.

---

## SLIDE 4: The Data Pipeline

Starting from raw EEG recordings:

1. **17,283 two-second windows** extracted from 35 subjects
2. Each window: **7 frontal EEG channels** at 250 Hz (shape: 7 x 500 samples)
3. For each window, I compute a **PAC value** using the Modulation Index method (Tort et al. 2010) — theta phase crossed with gamma amplitude
4. PAC values range from 0.0002 to 0.0046 microvolts
5. **Subject-level splits** prevent data leakage: 24 subjects for training, 5 for validation, 6 for testing — no subject appears in more than one split

---

## SLIDE 5: Predicting Future PAC — The Model

I built a **Multiscale Causal Temporal Convolutional Network (TCN)**.

"Causal" is the key word. The model can only look at the past — padding is applied only to the left side of convolutions. This guarantees **no future information leaks** into predictions.

Architecture:

- Input: 20-step sequences (40 seconds of history), each step has 73 features — spectral power, PAC history, and stimulation context
- 4 dilated causal convolution blocks (dilations: 1, 2, 4, 8) giving a 31-step receptive field
- Attention-weighted pooling across time
- Dual output heads: predicted future PAC and predicted PAC change

31,043 parameters. Inference under 50 milliseconds.

---

## SLIDE 6: The Critical Result — Horizon Sweep

This is the most important finding of the project.

I tested how well different methods predict PAC at increasing time horizons — from 1 second ahead to 10 seconds ahead:

| Horizon | Persistence R-squared | Ridge Regression R-squared | TCN R-squared |
| ------- | --------------------- | -------------------------- | ------------- |
| 1 sec   | 0.76                  | **0.81**                   | 0.74          |
| 2 sec   | 0.49                  | **0.54**                   | 0.47          |
| 3 sec   | 0.23                  | 0.25                       | **0.28**      |
| 5 sec   | -0.27                 | -0.39                      | **0.25**      |
| 8 sec   | -0.28                 | -0.21                      | **0.24**      |
| 10 sec  | -0.26                 | -0.21                      | **0.28**      |

At 1-2 seconds ahead, you don't need a neural network. "PAC won't change much" (persistence) and a simple linear model (Ridge) both work fine.

**But at 5-10 seconds — exactly the horizon where a controller needs predictions — every baseline collapses to negative R-squared.** Negative R-squared means worse than just predicting the mean. They're useless.

**The TCN maintains R-squared of 0.25-0.28 across this entire range.** That's a margin of **+0.5 R-squared** over the best baseline. The TCN is the only method that provides any useful signal at the horizons that matter for closed-loop control.

---

## SLIDE 7: Does Adaptive Scheduling Actually Help?

I tested this with a closed-loop simulation. Four strategies:

1. **Fixed Schedule** — 40s on, 20s off (current clinical standard)
2. **Reactive Threshold** — stimulate when PAC drops below a rolling z-score threshold
3. **Predictive Look-Ahead** — use trend detection and z-score to anticipate drops
4. **Oracle** — knows the future perfectly (theoretical upper bound)

I also modeled **neural fatigue** — the brain habituating to repeated stimulation — at varying severity levels.

Results of the **fatigue sensitivity sweep**:

| Fatigue Level | Fixed Efficiency | Adaptive Efficiency | Gain  | p-value    |
| ------------- | ---------------- | ------------------- | ----- | ---------- |
| None (0%)     | 5.38             | 5.40                | +0.4% | 0.49 (ns)  |
| Mild          | 5.29             | 5.36                | +1.3% | 0.02 \*    |
| Moderate      | 5.22             | 5.33                | +2.1% | 0.01 \*\*  |
| Moderate-high | 5.10             | 5.23                | +2.6% | 0.01 \*\*  |
| High          | 4.97             | 5.18                | +4.3% | 0.002 \*\* |
| Severe        | 4.82             | 5.09                | +5.7% | 0.01 \*\*  |

(Efficiency = mean PAC / fraction of time stimulating. Higher is better.)

**At every non-zero fatigue level, adaptive scheduling is significantly more efficient** (all p < 0.05, Wilcoxon signed-rank). The advantage grows monotonically: the more the brain habituates, the more it benefits from intelligent rest breaks.

---

## SLIDE 8: Does This Hold on Real Data?

Simulation results are only as good as the brain model. So I went back to real data.

I replayed each subject's actual PAC time series through **8 different controllers** — no simulator, no synthetic dynamics, just real measurements and counterfactual decision-making.

The top results:

| Controller               | Stim Time | Hit Rate  | Wasted Stim |
| ------------------------ | --------- | --------- | ----------- |
| Fixed Schedule           | 66.6%     | 49.5%     | 50.5%       |
| **Reactive Threshold**   | **34.5%** | **81.2%** | **18.8%**   |
| Multi-Biomarker Reactive | 21.3%     | 79.4%     | 20.6%       |
| Phase-Aware Reactive     | 36.4%     | 79.1%     | 20.9%       |
| PI Controller            | 42.7%     | 74.8%     | 25.2%       |

"Hit rate" means: when the controller chose to stimulate, did PAC actually rise afterward? Higher is better. "Wasted stim" is the inverse.

The Fixed Schedule hits only **49.5%** — essentially a coin flip. The Reactive Threshold hits **81.2%** while using only **half the stimulation time**.

The Multi-Biomarker Reactive controller — which combines PAC with gamma power and theta power from the raw EEG — achieves a **79.4% hit rate using only 21.3% stimulation**. That's one-third the stimulation of the fixed schedule, with 30 percentage points better targeting.

All four new controllers significantly outperform Fixed Schedule (Wilcoxon p < 0.001, n=35 subjects).

---

## SLIDE 8b: TCN-Based Predictive Control on Real EEG Data

I then integrated the trained TCN directly into the closed-loop controller and replayed all 35 subjects' real EEG data through six control strategies.

| Controller          | Epoch Alignment | Low-PAC Targeting | PAC Gap (×10⁻⁶ MI) | Stim % |
| ------------------- | --------------- | ----------------- | ------------------ | ------ |
| Fixed Schedule      | 45.0%           | 61.4%             | −6.6 (WRONG)       | 66.6%  |
| Reactive Threshold  | 64.5%           | 51.7%             | +21.1              | 36.7%  |
| **TCN Predictive**  | **72.1%**       | **82.6%**         | **+30.5**          | 59.7%  |
| Hybrid TCN+Reactive | 73.8%           | 85.3%             | +34.0              | 60.8%  |
| Alignment Oracle    | 100.0%          | 100.0%            | +33.3              | 48.3%  |

**Key findings (all N=35, Wilcoxon p < 0.001):**

- TCN alignment 72.1% vs Reactive 64.5% — **Hedges' g = +1.31** (large effect)
- TCN targets 82.6% of low-PAC windows vs Reactive's 51.7% — **g = +4.47** (very large)
- TCN PAC targeting gap +30.5 ×10⁻⁶ MI vs Reactive +21.1 ×10⁻⁶ MI — **g = +1.57** (large), reaching 91% of oracle bound
- **35/35 subjects** (100%) show improved clinical utility with TCN (binomial p < 0.001)
- Results robust across all delta-z thresholds 0.2–1.0

The Fixed Schedule actually targets stimulation in the **wrong direction** (negative PAC gap — more stim during high-PAC periods). The TCN achieves near-oracle targeting with no future knowledge.

---

## SLIDE 9: Individual Variability — Why One Size Doesn't Fit All

When I measured habituation across subjects — does PAC decline over the course of a session? — the population-level answer was **no** (p = 0.54). But the individual answers told a different story:

- Subject 35: **-66.8%** PAC decline (severe habituation)
- Subject 19: **-57.0%** decline
- Subject 27: **+149.1%** increase (facilitation)
- Subject 20: **+93.0%** increase

**49% of subjects habituate; 51% don't.** A fixed schedule cannot accommodate both groups. An adaptive controller automatically adjusts — stimulating more for patients who maintain entrainment, and incorporating more rest breaks for those who habituate.

---

## SLIDE 10: Data Integrity

Every pipeline in machine learning needs to prove it isn't cheating. Here are the audit results:

| Check                                             | Result                                                            |
| ------------------------------------------------- | ----------------------------------------------------------------- |
| No future data leakage in temporal sequences      | PASS                                                              |
| Subject-level train/val/test separation           | PASS                                                              |
| Shuffle-label sanity (model on randomized labels) | R-squared = -0.33 (correctly learns nothing)                      |
| Causal convolution verification                   | PASS (padding on left only)                                       |
| Feature ablation                                  | PAC history dominates; spectral features alone: R-squared = 0.055 |

The model learns real signal, not artifacts.

---

## SLIDE 11: Limitations and Honest Assessment

I want to be upfront about what this work does and doesn't show.

**What it shows:**

- Future PAC is predictable at 5-10 second horizons where baselines fail
- Adaptive scheduling is more efficient than fixed scheduling, confirmed both in simulation and on real data
- The advantage grows with habituation severity

**What it doesn't show:**

- This has not been tested in a live closed-loop experiment. All results are from offline replay or simulation.
- The dataset has 35 subjects from a single clinic. Generalization to other populations is unconfirmed.
- Sessions are 6-10 minutes. Clinical protocols run 30-60 minutes, where fatigue effects may be more pronounced — which would actually _strengthen_ the case for adaptive scheduling.
- PAC is measured as a proxy for therapeutic benefit. The link between PAC and downstream outcomes (amyloid clearance, cognitive improvement) is supported by the literature but not directly measured here.

**The R-squared of 0.25 at 5-10 seconds is modest in absolute terms.** But the right comparison isn't against 1.0 — it's against the baselines, which produce negative R-squared at those horizons. The TCN extracts the only useful signal available.

---

## SLIDE 12: Summary

1. **The problem:** Fixed 40 Hz stimulation schedules waste over 50% of stimulation time.

2. **The prediction:** A causal TCN predicts future brain entrainment 5-10 seconds ahead (R-squared = 0.25) where all baselines fail (R-squared < 0).

3. **The control:** Adaptive controllers achieve 79-81% hit rate using 21-35% stimulation time, versus 49.5% hit rate at 67% stimulation for fixed schedules. Verified on real data from 35 subjects (Wilcoxon p < 0.001).

4. **The clinical case:** Efficiency advantage scales with patient habituation (+1.3% to +5.7%, all p < 0.05). Half of patients habituate — they stand to benefit most.

5. **The deployment path:** EEGNet (1,457 parameters, <10ms) for real-time PAC estimation. TCN (31K parameters, <50ms) for prediction. Both fit on embedded hardware for a wearable device.

**Bottom line:** The system can cut stimulation time by half while improving when it stimulates by 30 percentage points — just by listening to the brain and responding to what it's telling us.

Thank you.

---

## Appendix: Technical Details

### Model Architectures

**EEGNet (Static PAC Predictor)**

- 1,457 parameters
- Input: (batch, 1, 7, 500)
- Block 1: temporal conv (1x64) + depthwise spatial (7x1)
- Block 2: separable conv (1x16)
- Output: scalar PAC prediction
- Test R-squared: 0.287

**Multiscale Causal TCN (Temporal Predictor)**

- 31,043 parameters
- Input: (batch, 20, 73) — 20 timesteps x 73 features
- 4 causal depthwise-separable conv blocks, dilations [1, 2, 4, 8]
- GroupNorm (not BatchNorm) for cross-subject stability
- Attention-weighted temporal pooling
- Dual heads: future PAC + delta PAC

### Dataset

- **Source:** OpenNeuro ds005048
- **Subjects:** 35 elderly subjects
- **Recording:** 19-channel EEG (10/20), 250 Hz, MATLAB v7.3 HDF5 format
- **Preprocessing:** 1 Hz highpass, 50 Hz notch, ICA artifact removal, common average reference
- **Windows:** 17,283 total (2-second, 7 frontal channels)
- **Splits:** 24 train / 5 validation / 6 test (subject-level, no leakage)
- **PAC range:** 0.0002 - 0.0046 (Modulation Index, Tort 2010)

### Eight Controllers Compared

1. **Fixed Schedule** — replays actual BIDS event timing
2. **Reactive Threshold** — rolling z-score on PAC, stimulate when z < -0.5
3. **Predictive Look-Ahead** — trend detection + z-score with 5-step hysteresis
4. **Oracle** — knows future PAC (theoretical upper bound)
5. **CUSUM Change Detection** — cumulative sum algorithm detecting sustained PAC drops (Page 1954)
6. **Multi-Biomarker Reactive** — weighted z-scores: 0.5*PAC + 0.3*gamma_power + 0.2\*theta_power
7. **Phase-Aware Reactive** — reactive with threshold modulated by theta-gamma phase coherence
8. **PI Controller** — proportional-integral control on PAC error with anti-windup

### Key References

- Tsai et al. (2016). Gamma frequency entrainment attenuates amyloid load. _Nature_, 540, 230-235.
- Tort et al. (2010). Measuring phase-amplitude coupling. _Journal of Neurophysiology_, 104(2), 1195-1210.
- Page (1954). Continuous inspection schemes. _Biometrika_, 41(1/2), 100-115.
