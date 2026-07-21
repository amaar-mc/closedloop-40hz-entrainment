# Poster Presentation Script -- Synopsys Championship

**Target: 4-4.5 minutes** uninterrupted, leaving judges 5-6 minutes for Q&A.
**Poster**: Synopsys Poster FINAL.pdf

This script maps exactly to the final poster layout. Every gesture reference points to a specific section, figure, or table on the printed poster. Read aloud 3 times tonight. Time yourself.

This is NOT a script to memorize word-for-word. Internalize the flow and key points so you can say them naturally each time.

---

## Part 1: The Hook (25 seconds)

_[Stand to the left of your poster. Face the judges. Don't touch the poster yet.]_

> My grandmother had dementia. I watched her lose the ability to recognize her own family. That experience is what started this project.
>
> _(1-second pause. Eye contact.)_
>
> Alzheimer's disease affects over 55 million people worldwide, with no cure and limited treatment options. But there's a promising therapy -- 40 Hz auditory stimulation -- that can synchronize brain oscillations and trigger amyloid plaque clearance. The problem isn't the therapy. It's how we deliver it.

**Delivery:** Say the grandmother part simply and calmly. Don't be dramatic. Let it sit. Then pivot to scale. Personal + global = your hook.

---

## Part 2: The Problem (30 seconds)

_[Gesture to the Introduction section on the left column of the poster]_

> Right now, clinical protocols deliver 40 Hz sound on a rigid fixed schedule -- 40 seconds on, 20 seconds off, repeating for an hour, the same for every patient.
>
> _[Point to Figure 1: "Fixed vs. Adaptive Scheduling" diagram at bottom of Introduction]_
>
> But when I analyzed EEG data from 35 dementia patients, I found that half of them habituate -- their brain tunes out the stimulus -- while the other half actually get stronger over time. A fixed schedule can't handle that. It stimulates when the brain doesn't need it and rests when coupling is fading.
>
> This project asks: can we predict when a patient's brain will lose entrainment, and deliver stimulation proactively, before the decline occurs?

**Delivery:** Your voice should sharpen slightly on "But when I analyzed..." You're identifying the problem YOU are solving. The habituation finding is YOUR original analysis -- not something from a paper.

---

## Part 3: The Two-Stage Model (60 seconds)

_[Move to the center of the poster. Point to the Model Approach column.]_

> The system works in two stages.
>
> _[Point to the Stage 1 architecture comparison table -- the one showing EEGNet, SpecTempNet, ViT-TCNet, Ridge, ATCNet, EEGNetLarge]_
>
> First, I needed to estimate current brain entrainment from raw EEG. I tested six different architectures, from 1,400 parameters to 2 million. Every single one converged at R-squared of 0.287. When six very different models hit the same ceiling, that tells you the bottleneck is the data, not the model. So I chose EEGNet -- the lightest at just 1,457 parameters -- because it matches the best performance while being fast enough for real-time inference on embedded devices.
>
> _[Point to Figure 3: System Architecture Flowchart]_
>
> But R-squared 0.287 from a single snapshot isn't enough for control. So stage two shifts the question: instead of predicting PAC better from one window, predict it further into the future from a _sequence_ of windows.
>
> _[Point to the EEGNet vs Causal TCN comparison table below the flowchart]_
>
> The Causal TCN ingests 20 seconds of history -- 73 features per timestep including spectral power, PAC trends, and stimulation context -- and forecasts phase-amplitude coupling 5 seconds ahead. "Causal" means the network architecturally cannot see future data. It uses left-only padding, so in deployment, it only has access to what a real-time system would actually have.

**Delivery:** Speak clearly and at a measured pace. When you say "six different architectures," point at the table and let judges see it. When you say "causal," slow down -- that detail proves deep understanding.

---

## Part 4: The Horizon Sweep -- Why 5 Seconds Matters (40 seconds)

_[Point directly to Figure 5: Prediction Horizon Sweep -- the line chart in the Data, Charts & Models section]_

> This is the most important figure on the poster.
>
> I trained models at every horizon from 1 second to 10 seconds. At 1-2 seconds, PAC barely changes -- just repeating the last value gives you R-squared of 0.81. You don't need deep learning for that.
>
> But at 5 seconds -- _[trace your finger to the 5-second mark on the x-axis]_ -- everything changes. Persistence and Ridge regression both collapse to negative R-squared. They're worse than predicting the average. But the TCN holds at R-squared 0.25. That's a plus-0.5 margin at exactly the horizon where a controller needs predictions to act proactively. That margin is the entire value proposition.

**Delivery:** Slow down here. This is your most original finding. Trace the lines on the figure as you talk. The crossover at 3-5 seconds should land with emphasis.

---

## Part 5: Results (60 seconds)

_[Move to the right side of the poster. Point to the Results & Findings column.]_

> I replayed the TCN controller on all 35 patients' actual EEG recordings, alongside fixed schedule, reactive threshold, and a theoretical oracle.
>
> _[Point to the Result 1 controller comparison table]_
>
> The TCN achieved 72.1% alignment -- meaning it made the right decision 72% of the time -- versus 64.5% for reactive control. But more importantly, look at the low-PAC targeting column: the TCN caught 82.6% of windows where the brain genuinely needed stimulation. Reactive only caught 51.7%. That's a 60% improvement in therapeutic precision. And the TCN uses _less_ stimulation than the fixed schedule -- 59.7% versus 66.6%.
>
> _[Point to Figure 9: Per-Subject Clinical Utility scatter plot]_
>
> The number I'm most proud of: 35 out of 35 patients showed higher clinical utility with the TCN. Every single one. Including 6 held-out test subjects the model never saw during training. The probability of that happening by chance is less than one in 34 billion.
>
> _[Point to the Result 3 fatigue severity table]_
>
> And the advantage increases with fatigue. As the brain habituates more, the system's benefit grows from 9% to over 11% -- exactly when personalization matters most. All effects are large to very large, Hedges' g of 1.7 to 2.4.

**Delivery:** Speak numbers clearly. "Seventy-two point one percent," not "72.1%." Slow down on "35 out of 35." Point at the scatter plot where every dot is above the diagonal. That visual combined with your words is your most powerful moment.

---

## Part 6: Conclusions and What's Next (30 seconds)

_[Step back slightly from the poster. Make eye contact with judges.]_

> Three takeaways. One: at 5-10 second horizons, the TCN is the only model providing useful predictions where all baselines fail. Two: on real patient EEG, predictive control targets 83% of the windows that need treatment versus 52% for reactive -- that's clinically meaningful. Three: every patient benefits, and the advantage grows with habituation, which is exactly when fixed schedules fail most.
>
> The main limitation is that this is offline replay, not live closed-loop. The system makes decisions on real brain data, but can't observe the brain's response to those decisions. The next step is real-time streaming validation -- and the model runs in under 2 milliseconds, so latency isn't the barrier.

_[Stop. Don't say "thank you" or "any questions?" Silence after your last sentence signals confidence. Judges will speak when ready.]_

---

## Timing Summary

| Section                                               | Target Time      |
| ----------------------------------------------------- | ---------------- |
| Part 1: Hook (grandmother + problem scale)            | 25 sec           |
| Part 2: The problem (fixed schedule + habituation)    | 30 sec           |
| Part 3: Two-stage model (architecture marathon + TCN) | 60 sec           |
| Part 4: Horizon sweep (why 5 seconds)                 | 40 sec           |
| Part 5: Results (controller + per-subject + fatigue)  | 60 sec           |
| Part 6: Conclusions + next steps                      | 30 sec           |
| **Total**                                             | **~4 min 5 sec** |

If judges don't interrupt and you want to fill toward 5-6 minutes, expand Part 3 (model details) or Part 5 (statistical methods). If they interrupt early, skip to Part 5 -- results are what matters most.

---

## If You Get Interrupted

Judges jumping in with questions is a good sign -- it means they're engaged. Answer the question, then ask: "Should I continue, or would you like to ask more questions?" If you haven't reached results yet and time is short, say: "Let me jump to the results -- they're the most important part" and go to Part 5.

---

## Key Numbers to Have Cold

```
PROBLEM SCALE:
  55 million patients worldwide
  No cure, limited treatment options

DATASET:
  35 dementia patients, OpenNeuro ds005048
  7 frontal EEG channels (Fp1, Fp2, F3, F4, F7, F8, Fz)
  250 Hz sampling rate
  17,283 two-second windows
  Subject-level splits: 24 train / 5 val / 6 test

MODELS:
  EEGNet: 1,457 params, R^2 = 0.287 (data ceiling -- 6 architectures converge here)
  TCN: 31,043 params, 73 features x 20 timesteps, dilations [1,2,4,8]

HORIZON SWEEP:
  1s: persistence R^2 = 0.81 (trivial, no DL needed)
  5s: persistence negative, Ridge negative, TCN R^2 = 0.25
  The +0.5 margin at 5s is the value proposition

CONTROLLER RESULTS (all 35 subjects, real EEG replay):
  Alignment: 72.1% TCN vs 64.5% reactive (p < 0.001, g = 1.31)
  Low-PAC targeting: 82.6% vs 51.7% (p < 0.001, g = 4.47)
  PAC gap: +30.5 vs +21.1 (g = 1.57)
  TCN reaches 92% of oracle performance
  35/35 patients benefited (binomial p < 0.001)
  Less stim than fixed: 59.7% vs 66.6%

FATIGUE:
  Advantage grows: +9.0% (none) to +11.2% (severe)
  All p < 0.001, Hedges' g = 1.7-2.4
  Robust across 4 fatigue model assumptions

HABITUATION FINDING:
  ~49% habituate, ~51% facilitate
  Population-level: not significant (validates need for per-patient adaptation)
```

---

## Verbal Value-Adds (say these naturally -- they're NOT on the poster)

These give judges information they can't just read. Use them to expand sections or answer follow-up prompts:

**On the grandmother hook:**
"That experience is what started this -- wanting to find a way to make the therapy work better for people like her."

**On the data ceiling (Part 3):**
"When six architectures from 1,400 to 2 million parameters all hit the same wall, that's not a failure -- it's a discovery. The data tells you its own limits. That's what motivated the entire pivot to temporal modeling."

**On what PAC actually is (if asked):**
"Phase-amplitude coupling measures how the power of gamma oscillations at 40 Hz is locked to the phase of slower theta waves. High PAC means the brain is synchronizing to the stimulus. Low PAC means it's losing sync. I compute it using the Hilbert transform and Tort's Modulation Index."

**On causal padding (Part 3):**
"In a real hospital, you don't have the future yet. The model is built so it can never cheat, even accidentally."

**On the R^2 = 0.25 being useful (Part 4):**
"0.25 might not sound impressive, but the controller doesn't need the exact PAC value -- it needs the direction. Is coupling trending down? That's enough signal to decide: stimulate now, or wait. The proof is downstream: 72% alignment and 83% therapeutic targeting from a 0.25 R-squared prediction."

**On 35/35 (Part 5):**
"The probability of all 35 patients benefiting by chance alone is less than one in 34 billion."

**On the limitation (Part 6):**
"I'm honest that this is offline replay. But the standard in brain-computer interface research is to validate on replay before moving to live systems. Every decision the controller makes is based only on data it would actually have in real time."

**On clinical deployment path:**
"The model runs in 2 milliseconds on a standard laptop. The barrier isn't compute -- it's regulatory validation and clinical trials."

**On using AI tools (if asked):**
"I used AI as a learning tool, similar to a textbook or Stack Overflow -- for understanding concepts like dilated convolutions or debugging. But every design decision, every architecture choice, and every scientific interpretation is my own. For example, when one model showed suspiciously high accuracy, I was the one who traced it to data leakage and fixed it."

---

## Poster Navigation Map

Where to point for each topic. Practice this physically -- build muscle memory.

```
LEFT COLUMN:
  Introduction          --> Hook, problem statement, 55M statistic
  Figure 1              --> Fixed vs. Adaptive Scheduling diagram
  Background            --> PAC definition, habituation, prior work
  Hypothesis            --> Core claim (read from poster if needed)
  References            --> Only if judges ask about sources

CENTER-LEFT:
  Stage 1 table         --> 6 architectures, R^2 = 0.287 ceiling
  R^2 vs params chart   --> Visual of all models converging
  Stage 2 comparison    --> EEGNet vs TCN table
  Figure 3              --> System Architecture Flowchart
  Figure 5              --> HORIZON SWEEP (most important figure)
  Figure 6              --> Controller Timeline (real subject example)

CENTER-RIGHT:
  Figure 2              --> Dataset overview (channels, protocol, splits)
  Figure 4              --> Full Training & Validation Protocol
  Materials             --> Dataset details, 35 patients, 7 channels
  Procedures            --> Training details, validation protocols, stats

RIGHT COLUMN:
  Result 1 table        --> Controller comparison (72.1% alignment)
  Figure 7              --> Metric definitions diagram
  Figure 8              --> Controller Comparison bar chart
  Figure 9              --> Per-Subject Clinical Utility scatter
  Result 3 table        --> Fatigue severity levels
  Result 4 table        --> Robustness across fatigue models
  Conclusions           --> 5 numbered takeaways
  Further Research      --> Next steps (live streaming, RL, multi-biomarker)
```

---

## Top 5 Danger Zone Questions

Have these answers ready. They're the questions that could cost you points.

### 1. "Did AI write your code?"

> I used AI as a learning tool, the same way someone would use Stack Overflow or a textbook -- to explain concepts or debug errors. But I made every design decision: which biomarker, which model, when to pivot from static to temporal. The SpecTempNet leakage discovery is a good example -- no tool told me the R-squared was suspicious. I noticed it, traced it to the input features, and fixed it. That's the kind of scientific reasoning that matters.

**Key:** Don't be defensive. Frame it as a tool. Pivot immediately to a concrete example of YOUR reasoning.

### 2. "R-squared of 0.25 doesn't seem very good"

> You're right to push on that -- I pushed on it too. The key insight is that the controller doesn't need perfect prediction. It needs directional accuracy: is PAC going up or down? 0.25 at 5 seconds provides enough signal for the controller to target 83% of low-PAC windows versus 52% for reactive. The proof that 0.25 is useful isn't the number itself -- it's the 72% alignment and the fact that all 35 patients benefited.

### 3. "This is just a simulation, not a real system"

> The primary results are NOT simulation -- they're replay on real patient EEG. I took all 35 patients' actual brain recordings and replayed the controller on them. The system only sees data that would be available in real time. The simulation results are complementary evidence about fatigue dynamics. And I tested across 4 different fatigue model assumptions to make sure the results aren't specific to one model.

### 4. "35 patients isn't enough data"

> It's a real limitation and I acknowledge it. But three things give me confidence. First, the effect sizes are very large -- Hedges' g of 1.31 to 4.47. Second, all 35 of 35 subjects showed improvement, not just the average. Third, I used non-parametric statistics appropriate for small samples. This is also the largest publicly available dataset of dementia patients during 40 Hz stimulation.

### 5. "How is this different from a reactive controller?"

> Reactive controllers respond after the brain has already lost entrainment. By the time PAC drops and you detect it, you've missed the therapeutic window. My system predicts the drop 5 seconds in advance, so it can start stimulation before the brain loses synchronization. The difference between a smoke detector that goes off during the fire versus one that goes off before the fire starts. The numbers show it: TCN targets 83% of low-PAC windows, reactive only catches 52%.

---

## Night-Before Checklist

- [ ] Read this script aloud 3 times. Time yourself each run.
- [ ] Practice pointing to each figure/table on your poster (or a photo of it on your phone).
- [ ] Read the 5 Danger Zone answers aloud until they feel natural.
- [ ] Skim the full Q&A banks in `docs/ORAL_PRESENTATION.md` and `docs/submission/reports/JUDGE_INTERVIEW_PREP.md`.
- [ ] Memorize the Key Numbers block above.
- [ ] Lay out your clothes.
- [ ] Sleep. A rested brain answers questions better than one that crammed until 2am.
