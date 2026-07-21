# 4-5 Minute Full Presentation

For the rare judge who says "walk me through everything from the beginning." Follows the poster left-to-right. Includes gesture cues tied to the physical board.

---

Hi, I'm Amaar Chughtai. Thanks for coming by. Would you like me to walk you through the project?

_[Wait.]_

**[BACKGROUND -- left column, top]**

So my grandmother had dementia. Watching someone you love lose the ability to recognize you -- that's what got me into this. I came across the research on 40 hertz entrainment, this idea that playing a rhythmic sound at 40 beats per second can drive the brain to synchronize its electrical activity in a way that actually clears the toxic proteins behind Alzheimer's.

The science goes back to 2016. Iaccarino's group at MIT showed in Nature that 40 hertz stimulation activates microglia -- the brain's immune cells -- and reduced amyloid plaques by 40 to 50 percent in mice. Then Murdock, just last year in Nature, found the actual mechanism: 40 hertz neural activity drives arterial pulsation through VIP interneurons, which increases cerebrospinal fluid flow through aquaporin-4 channels on astrocytic endfeet. It physically flushes amyloid out. And when they blocked glymphatic clearance pharmacologically, the clearing effect disappeared entirely. So we know it's necessary, not just correlated.

The human evidence is still early but growing. Chan showed 2-year safety in 5 patients. Cognito Therapeutics has Breakthrough Device Designation and is running a 670-patient Phase 3 trial right now.

_[gesture toward Figure 1: PAC illustration]_

**[THE PROBLEM -- left column]**

But here's what I noticed when I read deeper. Every clinical protocol -- Cognito included -- delivers this on a fixed schedule. Forty seconds on, twenty off, repeating for an hour. Same for every patient. And that assumption is wrong.

_[point to Figure 2: Fixed vs. Adaptive]_

When I analyzed EEG recordings from 35 elderly subjects in a published dataset, I found that about half of them habituate -- their brain gradually tunes out the stimulus over the session, like how you stop noticing a ticking clock. The other half actually get more responsive. A fixed schedule stimulates when the brain doesn't need it and rests when coupling is fading. Nobody was trying to predict this ahead of time. That's the gap this project fills.

**[STAGE 1 -- center-left, System Architecture]**

_[point to Stage 1 table]_

My first question was: can I measure how well the brain is synchronizing in real time? I use a biomarker called phase-amplitude coupling -- PAC. It measures how tightly gamma power at 40 hertz locks to the phase of slower theta rhythms. High PAC means the therapy is engaging. Low PAC means the brain is drifting.

To estimate PAC from raw EEG, I tested eight neural network architectures, from a 1,457-parameter EEGNet up to a 1.1-million-parameter Vision Transformer. Every single one converged to R-squared of 0.287. The million-parameter model actually scored lower because it overfit. When eight completely different architectures hit the same ceiling, that's not a model problem. It's a data problem. A 2-second EEG snapshot simply doesn't contain enough information about epoch-level coupling.

That realization was one of the most valuable moments in the project, because it told me exactly where to go.

**[STAGE 2 -- center-left]**

_[point to Stage 2 table]_

Instead of predicting PAC better from one snapshot, I shifted the question: what if I use a sequence of snapshots to predict PAC further into the future? That's the Causal TCN -- it takes 20 seconds of history and forecasts PAC 5 seconds ahead. Causal means every convolution uses left-only padding. The model physically cannot see future data. That's architectural, not just a training rule.

**[FEATURE DISCOVERY -- center]**

_[point to Data Analysis section]_

Then I made an unexpected discovery. My original TCN used 73 features per timestep -- 61 spectral power features plus 12 PAC and stimulation features. Test R-squared was negative 0.025. Worse than guessing the average.

When I investigated, I found the 61 spectral features were encoding subject-specific brain anatomy -- skull thickness, electrode impedance, individual oscillation profiles. The model was memorizing who it was looking at, not learning generalizable dynamics. The val-test gap was 0.358.

I dropped all 61 spectral features and kept only 12: 7 that track PAC trajectory and 5 that encode stimulation context. Test R-squared jumped from essentially zero to 0.60. The val-test gap shrank to 0.246. I validated across 5 random seeds -- mean 0.606, standard deviation 0.032, range 0.558 to 0.647.

**[HORIZON SWEEP -- right column area]**

This is where the whole project comes together.

_[point toward Results section]_

I trained models at horizons from 1 to 10 seconds. At short horizons, the brain barely changes -- persistence alone gets R-squared of 0.73. But at 5 seconds, persistence and Ridge regression both collapse to negative R-squared -- worse than guessing. The TCN is the only method that holds, at 0.60. And 5 seconds is exactly the lead time a controller needs for proactive decisions.

**[RESULTS -- right column]**

_[point to Result 1 table]_

I validated by replaying the TCN controller on all 35 patients' real EEG -- actual brain recordings, not simulation. The reactive approach catches 51.7 percent of the windows where the brain needed stimulation. My system catches 82.6 percent. That's a 60 percent improvement in therapeutic targeting, with Hedges' g of 4.47.

_[point to Result 2]_

All 35 out of 35 patients showed higher clinical utility with the predictive controller. Including the 6 test subjects the model never saw during training. Binomial probability of that by chance is less than 0.001.

_[point to Result 3]_

And the advantage actually grows under neural fatigue -- from plus 9 percent to plus 11 percent as fatigue worsens. Exactly when personalization matters most.

The TCN's targeting reaches 91 percent of a theoretical oracle that has perfect future knowledge.

**[FUTURE DIRECTIONS + CLINICAL USE -- right column, bottom]**

_[step back slightly]_

I want to be upfront about the main constraint. This is offline replay. The system makes decisions on real brain data, but it can't yet observe the brain's response to those decisions. The model runs in under 50 milliseconds, so real-time deployment is technically feasible.

The next step is a crossover clinical study -- same patients get both fixed and adaptive stimulation on different days. The full system runs on a Muse 2 headset at about $200 and a laptop. No clinical hardware required. I've deployed a live caregiver app where you can see the controller running in real time with simulated EEG.

_[eye contact]_

What would you like to go deeper on?

---

## Timing map (~150 words/min)

| Section                                | Words    | Time      | Poster location            |
| -------------------------------------- | -------- | --------- | -------------------------- |
| Greeting                               | 18       | 7s        | --                         |
| Background + science                   | 130      | 52s       | Left: Background, Fig 1    |
| The problem + habituation              | 95       | 38s       | Left: Intro, Fig 2         |
| Stage 1 (PAC + architecture)           | 110      | 44s       | Center-left: Stage 1 table |
| Stage 2 (TCN)                          | 55       | 22s       | Center-left: Stage 2 table |
| Feature discovery                      | 105      | 42s       | Center: Data Analysis      |
| Horizon sweep                          | 55       | 22s       | Right: Results area        |
| Results (controller + 35/35 + fatigue) | 100      | 40s       | Right: Results 1-3         |
| Future + limitation + open             | 80       | 32s       | Right: Future Directions   |
| **Total**                              | **~748** | **~4:59** |                            |

Right at 5 minutes. Natural interruption points throughout. Most judges will jump in during Stage 1 or the feature discovery -- both are natural question magnets.

## What was cut (ready if asked)

| Topic                             | Why cut                                  | Ready answer                                                                                                   |
| --------------------------------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Tort's Modulation Index detail    | Too granular                             | "KL divergence across 18 phase bins. Flat = no coupling, peaked = strong coupling."                            |
| 12-feature enumeration            | "7 PAC + 5 stim context" covers it       | "pac_current, pac_ma2/4/8/16, pac_diff1/4, stim_state, time_since_switch, stim_frac_20s, cycle_sin, cycle_cos" |
| Dilation factors                  | "Causal dilated convolutions" covers it  | "1, 2, 4, 8 -- gives 31-step receptive field, about 31 seconds of history"                                     |
| GroupNorm vs BatchNorm            | Internal detail                          | "GroupNorm is stable across subjects. BatchNorm statistics shift per-subject."                                 |
| All 6 controller variants         | Only TCN vs. Reactive contrast matters   | "Fixed, Reactive, TCN Predictive, Hybrid, PI, Oracle. Fixed is actually negative PAC gap."                     |
| Wilcoxon/Hedges' g rationale      | Too statistical                          | "Non-parametric paired test for N=35. Hedges' g for small-sample effect size."                                 |
| 4ch Muse-compatible results       | Only if asked about deployment           | "4ch test R-squared = 0.430 vs persistence 0.117 -- 3.7x improvement"                                          |
| TRIBE v2 / brain foundation model | Experimental work, not core contribution | "Meta's brain foundation model for in-silico validation -- in progress"                                        |
