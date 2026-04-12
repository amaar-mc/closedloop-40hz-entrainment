# 3-Minute Project of the Year Synopsis

Extended version for POTY review. Handbook says "3 minutes or less." Same audience as the 1-minute: judges from ALL categories. Keep accessible.

---

Alzheimer's disease affects 55 million people worldwide. One of the most promising non-drug therapies is 40 hertz auditory stimulation -- playing a rhythmic tone that drives the brain's electrical activity to synchronize. When that synchronization happens, it activates the brain's own cleanup system. In 2016, Iaccarino showed in Nature that this reduced amyloid plaques -- the toxic protein behind Alzheimer's -- by 40 to 50 percent in mice. Last year, Murdock identified the actual mechanism: 40 hertz activity drives cerebrospinal fluid flow that physically flushes amyloid out. Cognito Therapeutics has FDA Breakthrough Device Designation and is running a 670-patient Phase 3 clinical trial right now.

The problem is delivery. Every protocol uses a fixed schedule -- same timing, every patient, every session. But patients respond differently. When Amaar analyzed EEG recordings from 35 elderly subjects in a published dataset, he found that about half habituate within minutes -- their brains tune out the sound -- while the other half get more responsive. A fixed schedule cannot serve both groups. It wastes stimulation on moments when the brain doesn't need it and misses the windows when it does.

Amaar built a system that solves this by predicting when a patient's brain will lose its therapeutic response before it actually happens.

The approach is two stages. First, a lightweight neural network estimates brain synchronization in real time using a biomarker called phase-amplitude coupling. He tested eight different architectures for this, from 1,500 to 1.1 million parameters, and they all converged to the same accuracy -- proving the bottleneck was the data representation, not model capacity.

That insight led to the second stage: a Temporal Convolutional Network that takes 20 seconds of brain history and forecasts synchronization 5 seconds into the future. During this work, he made a critical discovery. His original 73-feature model was failing because 61 spectral features were encoding individual brain anatomy -- information that doesn't transfer across patients. Dropping those features and keeping only 12 that track synchronization dynamics raised accuracy from R-squared near zero to 0.60 -- a five-fold improvement confirmed across 5 random seeds. At this prediction horizon, every baseline method -- persistence, regression, averaging -- collapses to worse than random. The TCN is the only method that holds.

When tested as a closed-loop controller on all 35 patients' actual brain recordings, the predictive system caught 83 percent of the moments when the brain needed stimulation. Reactive control -- which responds only to what's already happened -- caught 52 percent. Every single patient benefited. The effect size of 4.47 is extremely large, and the system reached 91 percent of the theoretical maximum achievable with perfect future knowledge.

The significance extends beyond the numbers. The complete system runs on a $200 consumer EEG headset and a laptop. No clinical hardware required. This means personalized 40 hertz therapy could move from "visit the clinic three times a week" to "wear a headset at home for 15 minutes." The immediate next step is a live crossover clinical study, and the controller architecture is device-agnostic -- it could integrate with any existing 40 hertz stimulation system, including Cognito's.

---

## Word count: ~430 words = ~2:52 at 150 wpm

## Key differences from 1-minute version
- Explains the mechanism (glymphatic clearance) -- accessible to biologists and chemists
- Includes the 8-architecture convergence story -- resonates with engineers
- Explains WHY the feature discovery matters -- transfers across disciplines
- Ends with commercial viability -- the "worldly application" POTY criterion
