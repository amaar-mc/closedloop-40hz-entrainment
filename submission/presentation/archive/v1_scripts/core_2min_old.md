# 2-Minute Core Presentation

The standard interview opening. Judges have read your 13-page presentation, so don't recite -- tell them what's surprising. Expandable to 3-4 minutes if they're engaged and not interrupting.

---

Hi, I'm Amaar. Thanks for stopping by -- would you like me to walk you through the project?

_[Wait for nod.]_

So the core problem: 40 hertz auditory stimulation is one of the most promising non-drug approaches for Alzheimer's. It drives gamma oscillations that activate the brain's cleanup system -- microglia and glymphatic flow -- to clear amyloid plaques. Iaccarino showed 40 to 50 percent amyloid reduction in mice, and Murdock identified the actual mechanism last year through aquaporin-4 channels. Cognito Therapeutics has a 670-patient Phase 3 trial running right now.

_[gesture toward Background]_

But every protocol delivers this on a fixed schedule. Same timing for every patient, regardless of whether their brain is responding. And when I analyzed EEG recordings from 35 elderly subjects, I found that about half habituate -- their brains tune out within minutes -- while the other half actually get more responsive. A one-size-fits-all schedule wastes stimulation on patients who don't need it and misses the windows when they do.

_[gesture toward Figure 2]_

So I asked: can I predict when a patient's brain is about to lose its response, before it actually happens?

The answer required two stages. First, I needed to measure brain synchronization in real time. I use phase-amplitude coupling -- PAC -- which tracks how tightly 40 hertz gamma power locks to theta rhythms. High PAC means the therapy is working. I tested eight different neural network architectures for this, from 1,500 parameters to 1.1 million, and they all converged to the same R-squared of 0.287. That convergence was actually one of the most important findings -- it told me the bottleneck was the data, not the model.

_[gesture toward Stage 1 table]_

So I shifted the question. Instead of predicting PAC better from a single snapshot, I built a Temporal Convolutional Network that takes 20 seconds of history and forecasts PAC five seconds into the future. And I made an unexpected discovery -- my original 73 features included 61 spectral features that were encoding individual brain anatomy rather than generalizable dynamics. When I dropped those and kept only 12 PAC-trajectory and stimulation context features, test R-squared jumped from essentially zero to 0.60.

_[gesture toward Stage 2 / Data Analysis]_

The reason five seconds matters is right here.

_[point to horizon sweep figure if visible, or Results section]_

At short horizons, the brain barely changes -- just guessing "same as now" works fine. But at five seconds, every simple method collapses. My model is the only one that holds. And that's exactly the lead time a controller needs for proactive decisions.

When I ran the full system on all 35 patients' actual EEG recordings, the predictive controller caught 83 percent of the moments when the brain needed stimulation. Reactive control caught 52 percent. Every single patient -- all 35 out of 35 -- did better with my system. The effect size was Hedges' g of 4.47 for low-PAC targeting, which is massive.

_[gesture toward Results]_

The main limitation is that this is offline replay on recorded data, not live closed-loop. The model runs fast enough -- under 50 milliseconds -- but the next step is live clinical validation. The whole system runs on a $200 consumer headset and a laptop. No clinical hardware needed.

_[step back, eye contact]_

What would you like to dig into?

---

## Timing (~150 words/min)

| Section                               | Words    | Time      |
| ------------------------------------- | -------- | --------- |
| Greeting                              | 18       | 7s        |
| Problem + science                     | 60       | 24s       |
| The gap + habituation                 | 58       | 23s       |
| Stage 1 (PAC + architecture marathon) | 62       | 25s       |
| Stage 2 (TCN + feature discovery)     | 66       | 26s       |
| Horizon sweep                         | 42       | 17s       |
| Results (controller + 35/35)          | 55       | 22s       |
| Limitation + next steps + open        | 48       | 19s       |
| **Total**                             | **~409** | **~2:43** |

About 2:45. Most judges will interrupt somewhere during Stage 1 or Stage 2 with a question. If they let you run, you finish naturally under 3 minutes.

## Expansion modules (if they ask follow-ups)

**"How does PAC actually work?"**

> It measures coordination between two brain rhythms. Theta oscillates at 4 to 8 hertz, gamma at 40. When entrainment is working, gamma amplitude peaks at a specific phase of each theta cycle -- they move in lockstep. I compute that using Tort's Modulation Index, which uses KL divergence across 18 phase bins. Flat distribution means no coupling. Peaked means strong coupling.

**"Why a TCN and not an LSTM or Transformer?"**

> Causality. A TCN with causal padding physically cannot see future data -- it's an architectural guarantee. LSTMs depend on correct hidden state implementation. And with 17,000 training windows and length-20 sequences, I don't have enough data for self-attention.

**"What are the 12 features exactly?"**

> Current PAC, four causal moving averages at 2, 4, 8, and 16 windows, first-order and 4-step differences for trajectory, then binary stimulation state, time since last state switch, stimulation fraction over 20 seconds, and cycle phase encoded as sine and cosine. All strictly causal -- nothing from the future.

**"Could this actually help patients?"**

> The immediate next step is a crossover study -- same patients get both fixed and adaptive on different days, measuring whether adaptive maintains better synchronization. Long term, this becomes a wearable: a Muse 2 headset at about $200 paired with headphones, running the controller as a web app. No clinician needs to be present. That changes 40 hertz therapy from "come to the clinic three times a week" to "wear a headset at home for 15 minutes."

**"Tell me about the spectral feature drop -- that's not in the project presentation."**

> I did this work after submitting the project presentation. The original model used 73 features and plateaued at R-squared of 0.12 on test subjects. When I investigated the gap between validation and test performance, I traced it to the 61 spectral features encoding subject-specific brain anatomy -- skull thickness, electrode impedance, individual oscillation profiles. Information that helps identify which subject you're looking at but doesn't generalize. Removing those and keeping only the 12 features that track PAC dynamics and stimulation context jumped test R-squared to 0.60. The 5-seed mean is 0.606 plus-or-minus 0.032.
