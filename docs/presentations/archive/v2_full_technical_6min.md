# Full Technical Presentation -- "The Full Deal"

**5-6 minutes. For judges who want depth.**
**This is a story of an investigation, not a product pitch.**

---

Hi, I'm Amaar Chughtai. It's a pleasure to meet you. Would you like me to walk you through my project?

*[Wait for them to say yes or nod. Don't just launch.]*

So -- my grandmother had dementia. And watching someone you love lose the ability to recognize you, lose the thread of a conversation mid-sentence -- that changes how you think about this disease. It's not an abstract statistic for me. So when I came across the research on 40 hertz gamma entrainment -- this idea that sound at a specific frequency can actually trigger the brain to clear the toxic proteins behind Alzheimer's -- I was immediately drawn to it.

*[Gesture toward Background section]*

The science behind it is real and it's compelling. In 2016, a group at MIT showed that exposing Alzheimer's-model mice to 40 hertz stimulation activated microglia -- the brain's immune cells -- and reduced amyloid-beta plaques by 40 to 50 percent. Since then, multiple groups have extended this to sound, to multi-sensory stimulation, and most importantly to humans. A 2024 study by Lahijanian and colleagues showed that auditory 40 hertz entrainment enhances default mode network connectivity in dementia patients. So there's a growing body of evidence that this works.

But here's what bothered me as I read deeper into the literature.

*[Gesture to Introduction, then to Figure 1: Fixed vs. Adaptive]*

Every single clinical protocol delivers this stimulation the exact same way. Forty seconds of sound on, twenty seconds off, repeating for an hour. Same schedule for every patient, every session, regardless of how the brain is actually responding. And I kept thinking -- if the whole point of this therapy is to synchronize brain oscillations, shouldn't we be *checking* whether the brain is actually synchronized before we decide to keep stimulating or give it a rest?

So I went looking for what was out there. And the answer was: not much. The existing approaches either use fixed schedules with no adaptation at all, or reactive thresholds that wait until the brain has *already* lost synchronization and then respond after the fact. Nobody was trying to predict it ahead of time. That gap is what this project is about.

*[Gesture to Hypothesis]*

My hypothesis was that a causal deep learning model could predict brain entrainment 5 to 10 seconds into the future -- far enough ahead that a controller could actually do something useful with that prediction -- and that plugging those predictions into a closed-loop system would outperform both fixed scheduling and reactive approaches on real patient data.

Now, before I could predict anything, I had to figure out how to *measure* entrainment in real time. The biomarker I use is called phase-amplitude coupling, or PAC. What it measures is how tightly the amplitude of fast gamma oscillations at 40 hertz is locked to the phase of slower theta waves between 4 and 8 hertz. When PAC is high, the brain is synchronized to the stimulus -- the therapy is working. When PAC drops, synchronization is fading. I compute it using Tort's Modulation Index, which is a well-validated method based on the Kullback-Leibler divergence of the amplitude distribution across phase bins.

*[Move to Model Approach. Point to Stage 1 architecture table.]*

So my first challenge was: can I estimate current PAC from raw EEG? I used a publicly available dataset of 35 dementia patients from OpenNeuro -- 7 frontal EEG channels at 250 hertz -- and I tried to build a model that takes a 2-second window of raw brainwaves and outputs a PAC estimate.

And this is where the project took its first interesting turn. I didn't just try one model. I systematically tested six different architectures -- from a 1,457-parameter EEGNet all the way up to a 2-million-parameter Vision Transformer hybrid. And every single one of them converged to the same R-squared: 0.287. The 2-million-parameter model actually performed *worse* than the 1,457-parameter one because of overfitting.

*[Point to the R-squared vs. parameters chart]*

When six architectures with completely different inductive biases all hit the same ceiling, that tells you something important: the bottleneck isn't the model, it's the data. A 2-second snapshot of 7 frontal channels simply contains a finite amount of information about epoch-level PAC. That realization was actually one of the most valuable parts of the project because it told me exactly where to go next.

*[Point to Stage 2: TCN section]*

Instead of trying to squeeze more accuracy out of a single snapshot, I shifted the question entirely. I asked: what if I use a *sequence* of snapshots to predict PAC not just better, but *further into the future*? That's where the Causal Temporal Convolutional Network comes in.

It takes 20 seconds of history -- 73 features per timestep, including spectral power across frequency bands, PAC-derived features like moving averages and trends, and stimulation context -- and forecasts what PAC will be 5 seconds from now. The architecture uses dilated causal convolutions with dilation factors 1, 2, 4, and 8, which gives it a 31-step receptive field. And the "causal" part is critical -- every convolution uses left-only padding, which means the model physically cannot look at future data. That's not just a training constraint; it's an architectural guarantee. In a real-time clinical system, you don't have the future, and this model is built so it can never accidentally cheat.

*[Point to Figure 5: Prediction Horizon Sweep]*

Now, this figure is where the whole project comes together. I trained separate models at prediction horizons from 1 second all the way out to 10 seconds. And what you see is really interesting.

At 1 to 2 seconds ahead, the brain barely changes. A trivial baseline -- just saying "PAC will be the same as it is right now" -- gets R-squared of 0.81. You genuinely don't need deep learning for short-horizon prediction.

But watch what happens at 5 seconds. Persistence collapses to negative R-squared, meaning it's literally worse than guessing the average. Ridge regression does the same. The only method that provides *any* useful prediction at 5 seconds and beyond is the TCN, which holds at R-squared of about 0.25.

Now, I want to be honest about that number -- 0.25 doesn't sound impressive on its own. But what matters isn't the absolute value; it's the margin. At the horizons where a controller actually needs predictions to make proactive decisions, the TCN has a plus-0.5 R-squared advantage over every baseline. And the proof that this level of prediction is actually useful is in the downstream controller performance, which I'll show you now.

*[Move to Results. Point to Result 1 table.]*

For my primary validation, I replayed the TCN controller on all 35 subjects' actual EEG recordings. This isn't simulation -- it's real brain data with counterfactual decision-making. The controller sees only data that would be available in real time, makes a decision to stimulate or rest, and I compare that against what the brain actually needed.

*[Point along the table rows]*

The fixed schedule -- which is the current clinical standard -- gets 45% alignment. And its PAC gap is actually *negative*, meaning it stimulates more when coupling is already strong than when it's weak. It's not just suboptimal; it's pointing in the wrong direction.

The reactive approach does better at 64.5% alignment, but here's its weakness: it only catches 51.7% of the windows where the brain actually needed stimulation. It misses almost half of the therapeutic opportunities because by definition, it can only respond after the drop has already started.

The TCN predictive controller reaches 72.1% alignment and catches 82.6% of low-PAC windows. That's a 60% improvement in therapeutic targeting over reactive, with Hedges' g of 4.47 -- a very large effect size. And its PAC targeting gap reaches 92% of the theoretical oracle, which has perfect future knowledge.

*[Point to Figure 9: Per-Subject scatter]*

But I think the most compelling result is this: all 35 out of 35 patients showed higher clinical utility with the TCN than with reactive control. Not just on average -- every individual. Including 6 test subjects the model had never seen during training. The probability of that happening by chance is less than one in 34 billion.

*[Point to Result 3 fatigue table]*

And when I tested in simulation across different levels of neural fatigue -- which is when the brain progressively tunes out repeated stimulation -- the adaptive advantage actually *grows* as fatigue gets worse. From plus 9% at mild fatigue to plus 11.2% at severe, with Hedges' g between 1.7 and 2.4. I also tested across four completely different mathematical models of fatigue -- exponential decay, step function, heterogeneous population, and synaptic saturation -- and the results hold across all of them.

*[Step back. Eye contact.]*

Now, I want to be upfront about the constraints of this work. This is offline replay, not live closed-loop. The system makes real decisions on real brain data, but it can't observe how the brain would have responded to those decisions. That's the standard validation approach in brain-computer interface research before moving to live systems, but it's still a limitation.

The data comes from a single cohort of 35 patients, and the sessions are only 6 to 10 minutes -- much shorter than a real clinical hour. And while the model runs in under 2 milliseconds, clinical deployment would require FDA clearance, hardware integration, and proper clinical trials.

The next steps I'd want to pursue are real-time streaming validation with a live EEG setup, longer recording sessions to capture the full habituation time course, and eventually replacing the heuristic controller thresholds with reinforcement learning for long-horizon optimization.

Would you like me to go deeper into any particular part, or do you have questions?

---

## What this script implicitly addresses for the judge

| Judging criterion | Where it's addressed |
|---|---|
| **Research Problem** (practical need, constraints) | The grandmother connection, the fixed-schedule waste, the gap in existing approaches, the 5-second minimum lead-time constraint |
| **Design & Methodology** (explored alternatives, identified solution) | The 6-architecture marathon, the data ceiling discovery, the deliberate pivot to temporal modeling |
| **Execution & Testing** (multiple conditions, skill, completeness) | 35-subject replay, 6 fatigue levels, 4 fatigue model assumptions, 4 controller comparisons, statistical validation with effect sizes |
| **Creativity** (novelty) | Nobody had built a predictive controller for this therapy; the horizon sweep methodology; the architecture marathon as a principled way to prove a data ceiling |
| **Interview** (independence, understanding, limitations, impact, further research) | Explaining *why* each decision was made, honest limitations section, concrete next steps, showing the reasoning chain not just the results |

| Judge mindset question | Where it's addressed |
|---|---|
| How much did you do yourself? | "I systematically tested six architectures"; first-person throughout; describing the discovery process |
| How deeply do you understand it? | Explaining KL divergence, causal padding, why 0.25 is useful, what negative R-squared means |
| Did you discover errors? | SpecTempNet leakage (ready as a follow-up if asked); the data ceiling itself was a "discovery" |
| How did you progress from problem to result? | Entire narrative arc: grandmother → literature → gap → measure → model → ceiling → pivot → predict → validate |
| How new or different is this? | "Nobody was trying to predict it ahead of time. That gap is what this project is about." |
| Do conclusions follow from data? | Every claim tied to a specific number, p-value, or effect size |
| Is the work complete? | Full pipeline demonstrated; honest about what remains (live validation) |
