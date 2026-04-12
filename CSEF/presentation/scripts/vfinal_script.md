# Final Presentation Script (vFinal)

**For Medicine & Physiology judges.** Full 3–4 minute boardwalk with scientific history, specific numbers, and physical product demo. Target: ~3:50, modular for interruption.

Judges here are MDs and physiologists. Rigor shows through mechanism and clinical framing, not ML architecture detail. Cite the literature by name — they respect it.

---

Hi, I'm Amaar. Thanks for coming by. Let me walk you through this.

[Point to **Introduction**, top left.]

Alzheimer's affects more than 55 million people worldwide and there is still no cure. One of the most promising non-drug approaches is 40 hertz auditory stimulation. The idea goes back to work by Tsai's lab at MIT in 2016. Iaccarino and colleagues showed that pulsing sensory input at 40 hertz activates microglia and reduces amyloid plaque load in mouse models by about 40 to 50 percent. Since then, Murdock 2024 identified a glymphatic clearance mechanism, and Chan 2025 showed long-term safety in human trials. The mechanism is real.

[Point down to **Figure 3: Fixed vs. Adaptive Stimulation Scheduling**.]

But every clinical protocol delivers this therapy the same way. Forty seconds on, twenty off, cycling for an hour. Same schedule, every patient, regardless of how the brain is actually responding.

When I analyzed EEG from 35 elderly dementia patients, I found that roughly half habituate during a session. Their brains tune out the stimulus over time, exactly what Thompson and Spencer described in 1966. The other half actually get stronger. A fixed schedule cannot serve both groups. And no existing system predicts this ahead of time. That gap is the project.

[Move to **Materials** and the dataset overview figure.]

The dataset is OpenNeuro ds005048, published by Lahijanian 2024. Thirty-five subjects, seven frontal EEG channels at 250 hertz, subject-level train, validation, and test splits with zero overlap.

[Move to **System Architecture**. Pause. Do not point to a stage yet.]

Before I walk through the system — everything here is built around one biomarker: phase-amplitude coupling, PAC.

PAC measures how tightly 40 hertz gamma amplitude locks to the phase of theta waves, roughly 4 to 8 hertz. When that coupling is strong, the brain is entrained — firing in sync with the stimulus. When PAC drops, the circuit has gone quiet. The therapy is no longer landing.

This is the only number that matters in this system. It is what tells us whether stimulation is working right now, and it is what we need to predict in advance to do something about it before the window closes.

[Point to **Stage 1**.]

The system runs in two stages. The first stage estimates current PAC from raw EEG.

To estimate PAC, I tested eight different model configurations, from a small EEGNet with about 1,500 parameters up to a Vision Transformer with around two million. Every single one converged to essentially the same R squared, 0.287. The million-parameter model actually performed slightly worse because of overfitting. That convergence told me I was hitting a data ceiling, not a model ceiling. A two-second EEG window simply does not contain enough information to estimate epoch-level coupling more precisely.

[Point lower to **Stage 2: Temporal Prediction; Causal TCN**.]

So I changed the question. Instead of trying to estimate current PAC better from one snapshot, I asked whether I could predict future PAC from a sequence of snapshots. That is the causal temporal convolutional network. It takes twenty seconds of history and forecasts PAC five seconds ahead. The causal constraint is architectural, not just a training rule. The convolutions use left-only padding so the model physically cannot access future data.

[Point to the feature reduction visuals.]

I also made an unexpected discovery. My original model used seventy-three features per timestep, including sixty-one spectral power features across the frontal channels. Test R squared was essentially zero. When I investigated the validation-test gap, I realized those spectral features were encoding subject-specific anatomy, things like skull conductivity and electrode impedance, which let the model memorize individual patients instead of learning generalizable coupling dynamics. When I dropped all sixty-one spectral features and kept only twelve features that track PAC trajectory and stimulation context, test R squared jumped from negative 0.025 to 0.606. I validated across five random seeds. The signal was never in the spectral fingerprint. It was in the dynamics.

[Move to **Data Analysis** and point to the horizon figure.]

This is where the project holds together. At one or two seconds ahead, simple persistence wins because the brain barely changes in that window. But at five seconds out, persistence and Ridge regression both collapse to negative R squared, worse than guessing the average. The TCN is the only method that maintains useful prediction at that horizon. And five seconds is exactly the lead time a controller needs to actually change stimulation state before coupling drops.

[Move to **Results / Findings**. Point to the main controller table.]

I validated by replaying the controller on all 35 patients' real EEG recordings. The reactive controller catches 51.7 percent of the windows where the brain actually needed stimulation. The predictive TCN catches 82.6 percent. Overall alignment is 72.1 percent versus 64.5 percent for reactive, with a Hedges' g of 1.31 and p less than 0.001. The targeting improvement is a Hedges' g of 4.47, which is a very large effect size. And the system reaches 91 percent of a theoretical oracle that has perfect future knowledge.

[Point to **Result 2: Every Patient Benefits**.]

Every single one of the 35 patients benefited, including the six held-out test subjects the model never saw during training. This is not an average effect. It is universal.

[Point to **Result 3: Advantage Increases with Fatigue**.]

And the advantage actually grows as fatigue worsens, across five severity levels in simulation, which is exactly when personalization matters most clinically.

[Step back slightly. Optionally hold up the physical Muse 2 headset and headphones.]

I want to be clear about where this becomes a product. The full pipeline runs in real time on consumer hardware. This is a Muse 2 headband, which is 249 dollars and uses four dry electrodes, paired with standard headphones that deliver the 40 hertz amplitude-modulated audio. Processing runs on a single laptop with under fifty milliseconds end-to-end inference latency. Total cost per patient is under three hundred dollars. This is not a lab instrument. It is a deployable system for a memory care facility or home use.

The honest limitation is that this is still offline replay on recorded EEG, not live closed-loop streaming where stimulation actually changes the next brain state. The next step is a crossover clinical study comparing adaptive and fixed timing in the same patients on different days.

In one sentence: I built a system that predicts when an Alzheimer's patient's brain is about to lose response to 40 hertz therapy, and times stimulation to the moments it actually matters.

What would you like me to go deeper on?

---

## Timing map

| Beat | Section | Time | Poster location |
|---|---|---|---|
| 1 | Greeting + disease + 40 Hz mechanism + citations | 45 sec | Introduction + Background |
| 2 | Fixed schedule gap + habituation + dataset | 40 sec | Fig 3 + Materials |
| 3 | PAC biomarker — what it is, why it's the signal | 30 sec | System Arch (before Stage 1) |
| 4 | Stage 1 + 8-architecture ceiling + data ceiling insight | 40 sec | Stage 1 table |
| 5 | Stage 2 TCN + causal constraint | 25 sec | Stage 2 table |
| 6 | Feature ablation discovery + 5-seed validation | 35 sec | Feature reduction visual |
| 7 | Horizon sweep + 5s operational range | 25 sec | Data Analysis |
| 8 | Controller results + 35/35 + fatigue | 40 sec | Results column |
| 9 | Product demo + limitation + next steps + closer | 30 sec | Towards Clinical Use + step back |
| | **Total** | **~4:10** | |

---

## Delivery Notes

- Pace: direct, calm, unhurried. This is a conversation with an MD, not a pitch.
- Specificity over flash. Cite Iaccarino 2016, Murdock 2024, Chan 2025, Thompson and Spencer 1966 by name. Judges in this category respect the literature.
- Do not explain what an EEG channel is. Do not explain what theta or gamma mean. These judges know.
- Do explain the data ceiling insight clearly. That is the moment of scientific reasoning that separates this from a tutorial project.
- Pick up the Muse 2 headset when you get to the product section. Tangible product changes the room.
- If interrupted, stop immediately. Every section is modular. You can resume from any heading.
- Do not reference CS jargon like "depthwise separable" or "dilation factors" unless a judge asks. They are in the Q&A bank.

---

## What stays in this script vs what moves to Q&A

**In-script (scientific rigor signal):**
- Tsai lab / Iaccarino 2016 / MIT context
- Murdock 2024 glymphatic mechanism
- Chan 2025 long-term safety
- Thompson and Spencer 1966 habituation
- Lahijanian 2024 dataset provenance
- The 8-architecture convergence at R² = 0.287
- Spectral feature discovery with val-test gap reasoning
- Horizon sweep inflection at 5 seconds
- Hedges' g = 1.31, 4.47 with p < 0.001
- 91% of oracle
- Muse 2 $249 + under $300 total

**Held for Q&A (detail on demand):**
- Tort 2010 Modulation Index implementation
- Depthwise separable convolutions and dilation factors
- Exact 12-feature list (pac_ma2, pac_ma4, etc.)
- Feature ablation ablation table
- 4-channel Muse-compatible downgrade results
- Wilcoxon signed-rank vs paired t-test rationale
- AP stats teacher consultation on test selection
- Per-subject scatter plot details
- Fatigue model variants and severity levels
