# Main Presentation Script

**4-5 minutes. The one to memorize.**

---

Hi, I'm Amaar Chughtai. It's a pleasure to meet you. Would you like me to walk you through my project?

_[Wait for them to nod or say yes.]_

So -- my grandmother had dementia. And watching someone you love lose the ability to recognize you, lose the thread of a conversation mid-sentence -- that changes how you think about this disease. It's not an abstract statistic for me. So when I came across the research on 40 hertz gamma entrainment -- this idea that sound at a specific frequency can actually trigger the brain to clear the toxic proteins behind Alzheimer's -- I was immediately drawn to it.

_[Gesture toward Background]_

A group at MIT showed in 2016 that 40 hertz stimulation activates the brain's immune cells and reduces amyloid plaques by 40 to 50 percent. Since then, this has been extended to sound and confirmed in human patients. The science is real.

But here's what bothered me as I read deeper.

_[Point to Figure 1: Fixed vs. Adaptive]_

Every clinical protocol delivers this stimulation the exact same way. Forty seconds on, twenty off, repeating for an hour. Same schedule, every patient, every session, regardless of how the brain is actually responding. And when I analyzed EEG data from 35 dementia patients, I found that about half of them habituate -- their brains tune out the stimulus over time -- while the other half actually get stronger. A fixed schedule can't handle that. It stimulates when the brain doesn't need it and rests when coupling is fading. And nobody was trying to predict this ahead of time. That gap is what this project is about.

_[Move to Model Approach. Point to Stage 1 table.]_

So my first question was: can I measure how well the brain is synchronizing in real time? I use a biomarker called phase-amplitude coupling -- PAC -- which measures how tightly 40 hertz gamma power locks to slower theta rhythms. High PAC means the therapy is working. Low PAC means the brain is losing sync.

To estimate PAC from raw EEG, I tested six different architectures -- from a 1,457-parameter EEGNet all the way up to a 2-million-parameter Vision Transformer. And every single one converged to the same R-squared: 0.287. The 2-million-parameter model actually scored _lower_ than the 1,457-parameter one because of overfitting.

_[Point to R-squared vs. params chart]_

When six completely different architectures hit the same ceiling, that's not a model problem -- it's a data problem. A 2-second snapshot simply contains a finite amount of information about PAC. That realization was actually one of the most valuable moments in the project, because it told me exactly where to go next.

_[Point to Stage 2: TCN]_

Instead of trying to predict PAC better from one snapshot, I shifted the question: what if I use a _sequence_ of snapshots to predict PAC _further into the future_? That's the Causal TCN. It takes 20 seconds of history -- 73 features per timestep -- and forecasts PAC 5 seconds ahead. The "causal" part means every convolution uses left-only padding, so the model physically cannot see future data. That's an architectural guarantee, not just a training rule.

_[Point to Figure 5: Horizon Sweep]_

This figure is where the whole project comes together. I trained models at horizons from 1 second to 10 seconds. At short horizons, the brain barely changes -- persistence alone gets R-squared of 0.81. But at 5 seconds, persistence and Ridge regression both collapse to negative R-squared -- worse than guessing the average. The TCN is the only method that provides useful prediction at that range, holding at 0.25 -- a plus-0.5 margin. And 5 seconds is exactly the lead time a controller needs for proactive decisions.

_[Move to Results. Point to Result 1 table.]_

I validated by replaying the TCN controller on all 35 patients' actual EEG -- real brain data, not simulation. The reactive approach catches 51.7% of the windows where the brain actually needed stimulation. The TCN catches 82.6%. That's a 60% improvement in therapeutic targeting, with Hedges' g of 4.47. And the TCN's targeting reaches 92% of a theoretical oracle with perfect future knowledge.

_[Point to Figure 9]_

All 35 out of 35 patients showed higher clinical utility with the TCN than reactive. Every individual, including 6 test subjects the model never saw during training.

_[Point to Result 3]_

And the advantage grows with neural fatigue -- from plus 9% to plus 11.2% as fatigue worsens, holding across four different mathematical models of fatigue. Exactly when personalization matters most.

_[Step back. Eye contact.]_

I want to be upfront about the main constraint: this is offline replay, not live closed-loop. The system makes decisions on real brain data, but it can't yet observe the brain's response to those decisions. The model runs in under 2 milliseconds, so real-time deployment is technically feasible -- the next step is live streaming validation and eventually a clinical crossover study.

Would you like me to go deeper into any part, or do you have questions?

---

## Timing map

| Section                                         | Time              | Poster location               |
| ----------------------------------------------- | ----------------- | ----------------------------- |
| Greeting + grandmother + 40 Hz science          | 50 sec            | Left column: Background       |
| The gap: fixed schedule + habituation           | 30 sec            | Left column: Intro + Fig 1    |
| Measuring PAC + architecture marathon + ceiling | 45 sec            | Center: Stage 1 table + chart |
| The pivot: TCN architecture                     | 20 sec            | Center: Stage 2 table         |
| Horizon sweep                                   | 30 sec            | Center: Figure 5              |
| Results: controller + 35/35 + fatigue           | 40 sec            | Right column: Results         |
| Limitation + next steps + open                  | 15 sec            | Step back from poster         |
| **Total**                                       | **~4 min 10 sec** |                               |

---

## What was cut from the 6-minute version (and why)

These are things you KNOW but don't say unprompted. If a judge asks, you have them ready.

| Cut from script                                    | Why                                                 | Ready if asked                                                                                        |
| -------------------------------------------------- | --------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Formal hypothesis statement                        | Already clear from the narrative                    | "My hypothesis was that a causal model could predict PAC 5-10 seconds ahead..."                       |
| Tort's Modulation Index / KL divergence detail     | Too granular for the flow                           | "I compute PAC using Tort's Modulation Index, which uses KL divergence across phase bins"             |
| TCN 73-feature breakdown (61+7+5)                  | Say "73 features" in the script, elaborate if asked | "61 spectral power, 7 PAC-derived like moving averages, 5 stimulation context"                        |
| Dilation factors 1,2,4,8 / 31-step receptive field | "Dilated causal convolutions" covers it             | "Dilation factors 1, 2, 4, and 8 give a 31-step receptive field -- about 62 seconds of history"       |
| Fixed schedule row-by-row walkthrough              | Only the contrast matters                           | "Fixed schedule is actually _negative_ PAC gap -- it stimulates in the wrong direction"               |
| 0.25 "doesn't sound impressive" hedging            | One sentence handles it now                         | "The controller doesn't need exact prediction, it needs direction. 0.25 is enough for 83% targeting." |
| Naming all four fatigue models                     | "Four different models" suffices                    | "Exponential decay, step function, heterogeneous population, synaptic saturation"                     |
| Three separate limitation details                  | One sentence now                                    | "Single cohort, 6-10 min sessions vs clinical 60 min, FDA clearance path"                             |
| Lahijanian 2024 extended description               | "Confirmed in human patients" covers it             | "Lahijanian et al. 2024 showed auditory entrainment enhances default mode network connectivity"       |
