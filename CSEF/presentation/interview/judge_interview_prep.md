# Judge Interview Preparation Guide

**Complete Technical Deep-Dive for Synopsys Championship**
**Amaar Chughtai — March 10, 2026**

---

## 1. The 90-Second Verbal Summary

*Practice this until it's conversational, not rehearsed:*

"I built a deep learning system that personalizes 40 Hz auditory stimulation therapy for Alzheimer's patients. The basic idea is that 40 Hz sound pulses synchronize brain gamma waves, which activates immune cells that clear amyloid plaques. But current therapy uses the same fixed schedule for every patient — 40 seconds on, 20 seconds off. The problem is that half of patients habituate within minutes, while the other half stay fully engaged. A one-size-fits-all approach serves neither group.

My system predicts when a patient's brain is about to lose entrainment 5 seconds before it happens, and adapts stimulation accordingly. I trained a Temporal Convolutional Network on real EEG from 35 elderly subjects to forecast a biomarker called phase-amplitude coupling. The key finding is a horizon sweep: at 1-2 seconds ahead, simple baselines work fine. But at 5-10 seconds — where a controller actually needs predictions to act — all baselines fail and my model is the only one providing useful signal, with a +0.5 R-squared margin.

When I replayed my controller on all 35 patients' actual brain data, it achieved 72.1% alignment versus 64.5% for reactive control, directed stimulation to 83% of windows where the brain genuinely needed it, and reached 91% of the theoretical maximum. Every single patient benefited."

---

## 2. Data: Where It Came From, Every Detail

### The Dataset
- **Name:** OpenNeuro ds005048, version 1.0.1
- **Citation:** Lahijanian et al. (2024). "Auditory gamma-band entrainment enhances default mode network connectivity in dementia patients." Scientific Reports, 14, 13153.
- **Subjects:** 35 elderly participants with dementia diagnoses
- **Location:** Study conducted in Iran
- **Availability:** Freely downloadable from openneuro.org (CC0 license)
- **BIDS compliant:** Yes — standardized directory structure, events.tsv files, participants.tsv

### Recording Setup
- **EEG system:** 19 channels, international 10/20 montage, 250 Hz sampling rate
- **File format:** MATLAB v7.3 HDF5 (.set files) with companion binary (.fdt files)
- **Critical detail:** The .fdt files store float32 values in Fortran column-major order (`order='F'`). Using the wrong order scrambles channel assignments.
- **Already preprocessed by the dataset authors:** 1 Hz highpass, 50 Hz notch, ICA artifact removal, common average reference (Makoto's pipeline)

### What We Selected
- **7 frontal channels:** Fp1, Fp2, F7, F3, Fz, F4, F8
- **Why frontal?** Gamma entrainment from auditory stimulation is strongest at frontal sites. These channels capture the 40 Hz auditory steady-state response.
- **Why 7 channels?** Preliminary analysis showed adding temporal/occipital channels added noise but not signal for PAC prediction.

### The Paradigm
- **Stimulation:** 40 Hz amplitude-modulated auditory tones
- **Block structure:** Alternating Stimulus (20-40 seconds) and Rest (20 seconds) blocks
- **Short sessions:** 6 stim + 6 rest blocks
- **Long sessions:** 10 stim + 10 rest blocks
- **Total recording time per subject:** ~6-10 minutes
- **Events:** Segmented using BIDS events.tsv timestamps

### Data Processing Steps

1. **Load HDF5 .set files** — extract channel labels, sampling rate
2. **Read .fdt companion** — float32, Fortran order, reshape to (channels × samples)
3. **Select 7 frontal channels** by matching labels
4. **Light filtering:** Bandpass 0.5-80 Hz (4th-order Butterworth, zero-phase `filtfilt`), notch at 50 Hz (Q=30)
5. **Artifact rejection:** Remove windows where any channel exceeds ±100 µV (~2% of data removed)
6. **Common average reference:** Subtract mean across 7 channels at each timepoint
7. **Windowing:** 2-second non-overlapping segments aligned to BIDS event onsets
8. **PAC computation:** Modulation Index (Tort 2010) at epoch level

### Final Numbers
- **17,283 windows** total
- **Train:** 11,736 windows from 24 subjects
- **Validation:** 2,725 windows from 5 subjects
- **Test:** 2,822 windows from 6 subjects
- **Window shape:** (1, 7, 500) — 1 signal dimension, 7 channels, 500 samples (2s × 250 Hz)
- **PAC labels:** Range 0.0002 to 0.0046, mean ~0.001

---

## 3. Phase-Amplitude Coupling (PAC): The Biomarker

### What It Is
PAC (Phase-Amplitude Coupling) measures how well the timing of low-frequency brain waves controls the strength of high-frequency oscillations. Specifically:
- **Theta rhythm (4-8 Hz):** A slow wave that organizes neural processing
- **Gamma rhythm (38-42 Hz):** Fast oscillations associated with active neural computation
- When the brain is entrained by 40 Hz stimulation, gamma amplitude becomes "locked" to the theta phase — this coupling is the PAC signal.

### How It's Computed (Modulation Index, Tort et al. 2010)
1. Filter EEG to extract theta (4-8 Hz) → compute instantaneous phase via Hilbert transform
2. Filter EEG to extract gamma (38-42 Hz) → compute instantaneous amplitude via Hilbert transform
3. Divide theta phase into 18 bins (20° each, covering 0-360°)
4. For each bin, compute mean gamma amplitude
5. Compare the resulting distribution to a uniform distribution using Kullback-Leibler divergence
6. Normalize to get Modulation Index (MI)

### Why PAC, Not Just Gamma Power?
- Gamma power measures "how much gamma activity is present"
- PAC measures "how organized that gamma activity is relative to theta timing"
- Organized gamma (high PAC) indicates successful neural entrainment
- Disorganized gamma (low PAC) indicates the brain is NOT synchronized with the stimulus
- PAC is a more specific indicator of therapeutic 40 Hz entrainment than raw power

### PAC Label Assignment
- PAC is computed at the **epoch level** (full 20-40 second blocks)
- This epoch-level PAC is then assigned to ALL constituent 2-second windows within that epoch
- **Consequence:** Windows from the same epoch share identical PAC labels
- **Why this matters:** It means the model is predicting the overall epoch state, not instantaneous fluctuations

---

## 4. Model 1: EEGNet (Static PAC Predictor)

### Purpose
Estimates current PAC from a single 2-second EEG window. Used as the real-time input to the closed-loop controller.

### Architecture (1,457 Parameters)
```
Input: (batch, 1, 7, 500)

Block 1 — Temporal + Spatial:
  Conv2d: 1 → 8 filters, kernel 1×64
    → learns frequency-domain patterns (like a bank of bandpass filters)
  BatchNorm2d
  DepthwiseConv2d: 8 → 16, kernel 7×1
    → learns optimal spatial weighting across 7 channels
  BatchNorm2d
  ELU activation
  AvgPool2d(1,4) → reduce temporal dimension
  Dropout(0.5)

Block 2 — Separable Convolution:
  DepthwiseConv2d: 16 channels, kernel 1×16
  PointwiseConv2d: 16 → 16
  BatchNorm2d
  ELU
  AvgPool2d(1,8)
  Dropout(0.5)

Head:
  Flatten → Linear(features → 1)

Output: (batch, 1) — predicted PAC (z-score normalized)
```

### Why 1,457 Parameters?
- 17,283 samples / 1,457 params = **11.9 samples per parameter**
- Rule of thumb: you need at least 5-10 samples per parameter to avoid overfitting
- 8 architectures tested from 1.5K to 1.1M parameters — ALL converge at R²≈0.287
- **This proves the bottleneck is data, not model capacity**

### Training Details
- **Loss:** MSE (Mean Squared Error)
- **Optimizer:** Adam, learning rate 0.001
- **Scheduler:** ReduceLROnPlateau (reduce LR by 0.5 after 5 epochs of no improvement)
- **Early stopping:** patience 15 epochs
- **Target normalization:** Z-score (mean and std saved in checkpoint for inference)
- **Gradient clipping:** max_norm = 1.0
- **Test R²:** 0.287 (this is the ceiling, not a failure)

---

## 5. Model 2: MultiscaleCausalTCN (Temporal PAC Predictor)

### Purpose
Predicts future PAC (5 seconds ahead) from a sequence of 20 past observations, enabling proactive control decisions.

### Architecture (22,914 Parameters, PAC+Stim features)
```
Input: (batch, 20 timesteps, 12 features)

Input Projection:
  Linear(12 → 64) + LayerNorm + SiLU activation

4 Causal Depthwise-Separable Conv Blocks:
  Block 0: dilation=1, kernel=3 → receptive field covers 3 steps
  Block 1: dilation=2, kernel=3 → covers 5 steps
  Block 2: dilation=4, kernel=3 → covers 9 steps
  Block 3: dilation=8, kernel=3 → covers 17 steps
  Total receptive field: (1+2+4+8)×(3−1)+1 = 31 steps (covers full 20-step lookback with margin)

  Each block:
    Causal padding (LEFT ONLY — no future leakage)
    Depthwise Conv1d (64 channels, kernel=3, dilation=d)
    Pointwise Conv1d (64 → 64, kernel=1)
    GroupNorm(1, 64) — equivalent to LayerNorm
    SiLU activation
    Dropout(0.1)
    Residual connection (skip connection)

Attention Pooling:
  Query: Linear(64 → 1) → softmax over time → weighted sum
  Learns which timesteps are most informative

Dual Regression Heads:
  Future head: Linear(64→64) → SiLU → Dropout → Linear(64→1)
  Delta head: Linear(64→64) → SiLU → Dropout → Linear(64→1)

Output:
  future: predicted PAC at t+5 seconds
  delta: predicted PAC change (not used in final model)
```

### Why These Design Choices?

**Why TCN over LSTM?**
- TCN processes the full sequence in parallel (faster training)
- Causal padding guarantees no future leakage by construction
- LSTMs tested in `temporal/temporal_model.py` — inferior generalization, training instability

**Why TCN over Transformer?**
- Too many parameters for 17K samples
- Self-attention is O(n²) in sequence length — overkill for 20-step sequences
- TCN's inductive bias (local temporal patterns with increasing receptive field) matches the EEG signal structure

**Why dilations [1,2,4,8]?**
- Effective receptive field: (1+2+4+8)×(3−1)+1 = 31 steps — covers the full 20-step lookback window with margin
- Captures short-term dynamics (recent PAC trajectory) AND longer-term context (where in the stim/rest cycle)

**Why GroupNorm instead of BatchNorm?**
- BatchNorm statistics shift between subjects (different PAC magnitudes)
- GroupNorm(1, 64) normalizes within each sample independently
- Stable regardless of which subject's data is being processed

**Why attention pooling?**
- Learns which timesteps in the 20-step sequence are most informative for prediction
- Better than taking just the last step (which discards history)
- Better than mean pooling (which weights all steps equally)

**Why dual heads (future + delta)?**
- Delta head was intended to learn PAC change direction
- In final training, delta weight was set to 0.0 (cleaner optimization)
- The head architecture remains for potential future use

### 73 Input Features (Per Timestep)

| Feature Group | Count | Description |
|--------------|-------|-------------|
| Band power | 28 | Power in 4 frequency bands × 7 channels (theta, alpha, beta, gamma — no delta) |
| Theta/gamma ratios | 7 | Theta/gamma power ratio per channel |
| PAC-structure | 21 | Inter-channel PAC-derived features |
| Other spectral | 5 | Spectral entropy, peak frequency, bandwidth, asymmetry, concentration |
| PAC features | 7 | Current PAC, moving averages (2,4,8,16 step), first differences (1,4 step) |
| Stim context | 5 | Stim on/off, time since switch, recent stim fraction, cycle phase (sin, cos) |
| **TOTAL** | **73** | |

### Training Details
- **Loss:** Huber loss (robust to outliers in PAC)
- **Optimizer:** Adam, learning rate 0.001, weight decay 1e-3
- **Batch size:** 128
- **Scheduler:** ReduceLROnPlateau
- **Early stopping:** patience 20 epochs
- **Seed:** 42 (deterministic reproduction)
- **Best validation R²:** 0.411 (at horizon=5s, raw targets ts=1)
- **Test R²:** 0.170 (6 held-out subjects)
- **Test Pearson r:** 0.433

---

## 6. The Horizon Sweep: Your Intellectual Centerpiece

This is THE key result. Make sure you can explain it clearly.

### What Was Done
- Trained separate TCN models at horizons 1, 2, 3, 5, 8, and 10 seconds
- Compared against two baselines:
  - **Persistence:** "PAC won't change" — predict current value for all future times
  - **Ridge regression:** Linear model on same features

### Results

| Horizon | Persistence R² | Ridge R² | TCN R² (PAC+Stim, 12 feat) | Who Wins? |
|---------|---------------|---------|---------------------------|-----------|
| 1s | 0.760 | **0.812** | 0.725 | Ridge wins |
| 3s | 0.234 | 0.253 | **0.607** | TCN wins |
| 5s | -0.267 | -0.393 | **0.577** | **TCN +0.84 margin** |
| 8s | -0.276 | -0.211 | **0.370** | **TCN +0.65 margin** |
| 10s | -0.256 | -0.212 | **0.669** | **TCN +0.93 margin** |

*Note: TCN numbers above are from the PAC+Stim (12-feature) model. The earlier 73-feature TCN showed 0.254/0.240/0.278 at 5/8/10s — still beats baselines, but the 12-feature model is the submitted configuration.*

### Why This Matters — The Explanation for Judges

"At 1-2 seconds, PAC doesn't change much — you can literally just say 'it'll stay the same' and get R-squared of 0.76. A neural network is unnecessary here.

But at 5-10 seconds, the brain state has genuinely changed. Persistence predicts 'same as now,' but that's wrong — PAC has moved. Ridge regression tries to extrapolate linearly, but PAC dynamics are nonlinear. Both give **negative R-squared** — they're worse than just predicting the average for everyone.

The TCN using just 12 PAC trajectory and stimulation context features maintains R-squared of 0.577 at 5 seconds where nothing else works. That's a margin of +0.84 over persistence — the difference between 'useful prediction' and 'worse than guessing.'

And 5-10 seconds is exactly the range where a controller needs predictions: far enough ahead to make decisions and prepare stimulation, but close enough that the brain state is still somewhat predictable."

---

## 7. Closed-Loop Controller: How It Works

### The Decision Loop (1 Hz rate — one decision per second)

```
Every second:
  1. Receive latest 2-second EEG window
  2. Run EEGNet → estimate current PAC
  3. Add to 20-step history buffer
  4. Run TCN on history → get predicted PAC 5 seconds ahead
  5. Compute z-score of predicted PAC (against 30-second rolling baseline)
  6. Decision:
     - If predicted z < -0.5 → STIMULATE (PAC will drop)
     - If predicted z > +0.5 → REST (PAC is fine)
     - Otherwise → MAINTAIN current state
  7. Apply 3-second hysteresis (don't flip-flop)
```

### The 6 Controllers Compared

1. **Fixed Schedule:** 40s ON, 20s OFF (current clinical standard)
2. **Reactive Threshold:** Stimulate only when CURRENT PAC drops below threshold (waits for problem to occur)
3. **TCN Predictive:** Stimulate based on PREDICTED future PAC (acts before problem)
4. **Hybrid TCN+Reactive:** Reactive base + TCN override when it predicts decline
5. **PI Controller:** Proportional-integral feedback on PAC error
6. **Alignment Oracle:** Perfect future knowledge (theoretical upper bound)

### Key Results (N=35 subjects, real EEG replay)

| Controller | Alignment | Low-PAC Targeting | PAC Gap |
|-----------|-----------|-------------------|---------|
| Fixed Schedule | 45.0% | 61.4% | -6.6 ×10⁻⁶ MI (WRONG) |
| Reactive | 64.5% | 51.7% | +21.1 ×10⁻⁶ MI |
| **TCN Predictive** | **72.1%** | **82.6%** | **+30.5 ×10⁻⁶ MI** |
| Oracle | 100.0% | 100.0% | +33.3 ×10⁻⁶ MI |

### What the Metrics Mean

- **Alignment:** Percentage of time the controller makes the "right" decision (stimulate when PAC is low, rest when high). 72.1% means the TCN is correct 72% of the time.

- **Low-PAC Targeting:** Of all the windows where PAC is below median (brain needs therapy), what fraction did the controller actually stimulate? 82.6% means the TCN catches 83 out of every 100 windows needing treatment.

- **PAC Gap:** Mean PAC during rest minus mean PAC during stim. Positive means the controller correctly concentrates stimulation on low-PAC periods. Fixed schedule gets a NEGATIVE gap — it stimulates MORE during high PAC than low PAC.

---

## 8. Statistical Methods

### Why Wilcoxon Signed-Rank (Not t-test)?
- We have paired data (same 35 subjects, different controllers)
- PAC distributions may not be normal
- Wilcoxon is a non-parametric paired test — makes fewer assumptions
- All p-values < 0.001

### Why Hedges' g (Not Cohen's d)?
- Cohen's d overestimates effect size for small samples
- Hedges' g applies a correction factor for N=35
- Effect sizes:
  - g = 1.31 for alignment (large)
  - g = 4.47 for low-PAC targeting (very large)
  - g = 1.57 for PAC gap (large)

### 95% Confidence Intervals
- Large-sample normal approximation (g ± 1.96 × SE)
- Alignment g: [0.75, 1.87]
- Low-PAC targeting g: [3.33, 5.62]
- PAC gap g: [0.98, 2.17]
- None cross zero → results are significant

### Binomial Test: 35/35 Subjects
- Probability of 35/35 by chance (assuming 50/50): p = 2^(-35) < 10^(-10)
- This means the TCN's advantage is not driven by a few subjects — it's universal

---

## 9. Habituation / Fatigue Analysis

### Real Data Finding
- 17/35 subjects (49%) show declining PAC across stimulation blocks (habituation)
- 18/35 subjects (51%) show stable or increasing PAC
- Population-level: paired t-test p = 0.542 (NOT significant)
- **BUT individual variability is massive:**
  - Sub-35: -66.8% PAC decline (strong habituation)
  - Sub-27: +149.1% PAC increase (strong facilitation)

### Why This Matters
- A fixed schedule treats both groups identically — suboptimal for both
- The 50/50 split validates the need for personalized control
- This is the biological justification for adaptive scheduling

### Simulation Fatigue Results
- Efficiency gains +9% to +11.2% across 6 severity levels (all p < 0.001)
- Gains hold across 4 different fatigue model types:
  - Exponential decay: +9.0%, g=2.31
  - Step function: +6.9%, g=1.21
  - Heterogeneous population: +8.9%, g=1.71
  - Saturation (synaptic depletion): +19.0%, g=3.66

---

## 10. Anticipated Judge Questions & Answers

### Q1: "Why is your R-squared only 0.287 for EEGNet?"
**A:** "Eight different architectures from 1,500 to 1.1 million parameters all converge at this number. The bottleneck is the data, not the model — 7 frontal channels of noisy EEG simply contain limited information about PAC. This is the information ceiling of the problem, and recognizing that was an important finding in itself."

### Q2: "Did the TCN actually beat simple baselines?"
**A:** "At 1-2 seconds ahead, no — and I'm transparent about that. Persistence gets R²=0.76 at 1 second. But the whole point is that at 5-10 seconds, where a controller needs predictions to act proactively, persistence and Ridge both produce negative R-squared. The TCN maintains 0.25 — a +0.5 margin. The TCN's value is not in short-term prediction but in the operationally relevant horizon."

### Q3: "How do you know there's no data leakage?"
**A:** "Four safeguards: (1) Subject-level splits — the 6 test subjects were never seen during training or validation. (2) Causal construction — convolutions only use left padding, so no future information can leak. (3) Train-only normalization — z-score statistics computed from training data only. (4) Shuffle-label test — when I randomize the PAC labels, R² drops to -0.332, confirming the model learns real patterns."

### Q4: "Is your simulation realistic?"
**A:** "The simulation is only one piece of evidence. The primary results come from replaying the controller on all 35 subjects' actual EEG recordings — no simulation involved. The simulation provides complementary evidence about fatigue dynamics and was tested across four fundamentally different fatigue model assumptions to ensure robustness."

### Q5: "What does the model actually learn?"
**A:** "Feature ablation shows PAC-derived features alone give R²=0.859, while spectral-only features give 0.045. The model primarily learns the temporal dynamics of phase-amplitude coupling — how entrainment strength evolves over time. This is exactly the signal needed to predict future brain state."

### Q6: "Why not use a larger model / transformer / GPT?"
**A:** "I tested 8 architectures up to 1.1 million parameters. They all converge near the same performance. With 17,000 training samples from 35 subjects, the dataset is the bottleneck. A larger model would overfit without improving generalization. The TCN at 31,000 parameters is already at the sweet spot."

### Q7: "How would this help real patients?"
**A:** "The TCN controller directs 82.6% of stimulation to windows where the brain genuinely needs it, versus only 51.7% for reactive control. In a clinical music therapy session, this means therapeutic sound is delivered almost exclusively when the patient's neural coupling is weakest. For patients who habituate, the system would detect declining entrainment and schedule rest breaks before effectiveness drops — potentially extending the useful duration of each session."

### Q8: "Does the TCN actually drive the closed-loop controller?"
**A:** "Yes. The trained TCN from `models/best_multiscale_tcn_lb20_hz5_ts1.pth` is loaded and used for real-time inference in the controller. At each step, it receives the last 20 seconds of features and outputs a predicted PAC value 5 seconds in the future. The controller then decides STIMULATE, REST, or MAINTAIN based on that prediction."

### Q9: "Did you use AI tools to build this?"
**A:** "Yes, I used Claude Code for coding assistance — writing Python functions, debugging, and generating documentation. All experimental design decisions (which biomarker, which model architecture, which horizons to test) are mine. The research direction, scientific interpretation, and analysis are my own work. This is disclosed on my poster."

### Q10: "What would you do differently?"
**A:** "Three things: (1) Record longer sessions — 30-60 minutes instead of 6-10 minutes — to capture the full habituation curve. (2) Deploy the system in real-time with live EEG streaming, not just replay on recorded data. (3) Combine PAC with gamma power and auditory steady-state response amplitude for a multi-biomarker controller."

### Q11: "Why frontal channels? Why only 7?"
**A:** "Auditory 40 Hz entrainment produces the strongest response at frontal electrode sites. I tested adding temporal and occipital channels — they added noise without improving PAC prediction. Seven frontal channels capture the relevant signal while keeping the model small enough to deploy on embedded hardware."

### Q12: "What is the clinical path forward?"
**A:** "The next step would be a crossover clinical study: same patients receive both fixed and adaptive stimulation on different days, with real-time EEG monitoring. If adaptive scheduling maintains higher PAC with less total stimulation, it could reduce session length and patient burden in Alzheimer's stimulation therapy."

---

## 11. Key Numbers to Memorize

| Metric | Value | Context |
|--------|-------|---------|
| Subjects | 35 | Elderly subjects, OpenNeuro ds005048 |
| Channels | 7 | Frontal EEG (Fp1, Fp2, F7, F3, Fz, F4, F8) |
| Sampling rate | 250 Hz | |
| Windows | 17,283 | 2-second segments |
| EEGNet params | 1,457 | 12 samples/param |
| TCN params | 22,914 | PAC+Stim model (h=64) |
| TCN features | 12 | 7 PAC-derived + 5 stim context (spectral dropped) |
| Lookback | 20 steps | 20 seconds of history |
| Horizon | 5 seconds | |
| Dilations | [1,2,4,8] | 31-step receptive field |
| TCN R² at 5s | 0.606 | mean ± 0.032 across 5 seeds; +0.5 margin over baselines |
| Alignment | 72.1% vs 64.5% | TCN vs Reactive |
| Low-PAC targeting | 82.6% vs 51.7% | TCN vs Reactive |
| PAC gap | 30.5 vs 21.1 ×10⁻⁶ MI | TCN vs Reactive |
| Effect sizes | g=1.31, 4.47, 1.57 | All p<0.001 |
| Oracle % | 91% | TCN reaches 91% of oracle |
| Universal benefit | 35/35 | 100% of subjects |

---

## 12. Your Competitive Edge

Against comparable 2025 Synopsys projects:

1. **Closed-loop prediction, not just classification** — no other comparable project does temporal forecasting for proactive control
2. **Real-data validation on all 35 subjects** — not just test set accuracy
3. **100% per-subject benefit** — most ML projects have winners and losers
4. **8 architectures tested** — systematic exploration, not just "we tried one model"
5. **4 fatigue models tested** — addresses the "your simulation is too specific" concern
6. **Public dataset** — fully reproducible, unlike private hospital data
7. **Complete pipeline** — raw BIDS data → preprocessing → training → controller → validation → figures

---

*Prepared February 27, 2026*
*Good luck at the Synopsys Championship on March 10!*
