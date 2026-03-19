# Synopsys Championship: Oral Presentation & Judge Preparation Guide

## How This Document Is Organized

1. **Strategy Brief** -- What the rubric rewards and how your project maps to it
2. **The Full Presentation (~5 min)** -- 7-part walkthrough with delivery notes and poster gestures built in
3. **Judge Q&A Bank** -- 40+ anticipated questions with natural, first-person answers
4. **Danger Zones** -- The 5 questions that could sink you, with rehearsed answers
5. **Delivery Tips** -- Pacing, body language, common mistakes
6. **Quick Reference Card** -- Pocket index card with all key numbers and phrases

---

## 1. Strategy Brief

### What Judges Are Scoring (40 points total)

| Category (10 pts each) | What they want to see | Your strongest evidence |
|---|---|---|
| **Scientific Thought** | Significant problem, clear hypothesis, controls, justified conclusions, awareness of further research | 55M patients, $300B burden, clear gap (fixed vs adaptive), 6 controller comparisons as controls, honest limitations, future work section |
| **Creativity** | Original approach, novel hypothesis checking, YOUR contributions | Nobody has built a predictive closed-loop controller for 40 Hz therapy before. Architecture marathon (8 models) to prove data limitation. SpecTempNet leakage discovery. Horizon sweep as novel evaluation |
| **Independent Work/Skill** | Did YOU do it? Understanding appropriate for grade? Programming/analytical skills | You wrote every line of Python, you can explain PAC computation, causal convolutions, dilated receptive fields, why Ridge fails at 5s. Show notebook |
| **Thoroughness/Clarity** | Adequate data, replications, claims supported, notebook, clear answers | 35 subjects, all 35 showed improved alignment, Wilcoxon signed-rank, Hedges' g, 6 integrity checks, 4 fatigue models, threshold robustness sweep |

### Your Core Narrative Arc (What Judges Should Walk Away Remembering)

> "He took a real clinical therapy for Alzheimer's -- 40 Hz sound -- and asked: can we make it smarter? He built a deep learning system that predicts when a patient's brain will lose response, 5 seconds before it happens. It worked on all 35 patients. Nobody had done this before."

Every sentence you say should build toward judges being able to retell that story.

### A Note on Presentation Length

The Synopsys website says "1-2 minutes." In practice, that refers to the minimum -- if judges don't interrupt, you should keep going. Judges have about 10 minutes per project. The winners at ISEF typically spend about half the session presenting and half answering questions. This script is designed for ~5 minutes of uninterrupted speaking. If a judge jumps in with a question at any point, stop and answer it -- that's not a failure, that's a conversation. You can always skip ahead to results if you get cut short.

---

## 2. The Full Presentation (~5 minutes)

**Target time: 5-5.5 minutes.** Read this aloud multiple times. Time yourself. Adjust until it flows naturally at YOUR speaking pace -- don't speed up to fit it in, cut words instead.

This is NOT a script to memorize word-for-word. It's the content and flow to internalize. Know the key points of each section so you can say them naturally, in your own words, every time.

---

### Part 1: The Hook (30 seconds)

> My grandmother had dementia. I watched her lose the ability to recognize her own family -- to carry a conversation, to remember what she'd said moments earlier. That experience is what started this project.
>
> *(beat -- 1 second pause. Make eye contact.)*
>
> Alzheimer's disease affects over 55 million people worldwide. It's the leading cause of dementia. There's no cure. And it costs over 300 billion dollars a year in the US alone.

**Delivery:** Say the grandmother part simply and calmly -- don't be dramatic, don't rush. Let it sit. Then pivot to the scale of the problem. These two things together -- personal and global -- are your hook.

---

### Part 2: The Science -- Why 40 Hz Matters (45 seconds)

> *(gesture toward background section of poster)*
>
> But in 2016, a team at MIT discovered something remarkable. When they exposed Alzheimer's model mice to flickering light at 40 hertz -- the gamma frequency -- it triggered the brain's immune cells, called microglia, to clear amyloid-beta plaques. The toxic protein buildups that cause Alzheimer's. They saw 40 to 50 percent plaque reduction.
>
> Since then, follow-up studies have shown this also works with sound -- 40 hertz auditory stimulation -- and it works in humans. Clinical trials by Cognito Therapeutics showed that treated patients had slowed brain atrophy and preserved cognitive function. A 2024 Nature paper showed the clearance happens through the brain's glymphatic system -- essentially flushing the toxic proteins through cerebrospinal fluid.
>
> So the therapy works. The question is how to deliver it.

**Delivery:** This section establishes credibility. You're showing judges you did real literature research. Mention specific papers and specific results (Iaccarino, Cognito, Nature 2024). Don't rush through the science -- judges need to understand WHY this therapy matters before they can appreciate your contribution.

---

### Part 3: The Gap -- Why Current Protocols Fail (45 seconds)

> *(gesture toward the problem/gap section of poster)*
>
> Right now, every clinical protocol delivers 40 hertz stimulation the same way: 40 seconds of sound on, 20 seconds off, repeated for an hour. Every patient, same schedule, same timing.
>
> But brains are different. When I analyzed the EEG data from 35 elderly subjects, I found that about half of them -- 48.6 percent -- habituate. Their brain's response to the stimulus fades over time. But the other half -- 51.4 percent -- actually facilitate. Their response gets stronger. And at the population level, there's no net trend. The p-value is 0.542 -- not significant.
>
> *(gesture toward habituation figure if on poster)*
>
> So you have half your patients going one direction and half going the other. A fixed schedule can't adapt to that. It stimulates when the brain doesn't need it and misses windows when it does. That gap -- between a therapy with real disease-modifying potential and a delivery system that ignores individual brain responses -- is what this project addresses.

**Delivery:** This is your pivot. Your voice should sharpen slightly on "But brains are different." You're identifying the problem that YOU are going to solve. The habituation data is powerful because it's YOUR original finding from YOUR analysis -- not something you read in a paper.

---

### Part 4: What I Built (75 seconds)

> *(gesture toward methods/architecture section)*
>
> So I built a system that adapts. The core idea is: instead of using a timer, use the brain itself to decide when to stimulate.
>
> I used EEG recordings from 35 elderly subjects -- this is a publicly available dataset from OpenNeuro of subjects undergoing 40 hertz auditory stimulation. 19 channels, 250 hertz sampling rate.
>
> First, I needed a biomarker -- a way to measure, in real time, how well the brain is synchronizing to the stimulus. I used something called phase-amplitude coupling, or PAC. It measures how the power of gamma oscillations at 40 hertz is locked to the phase of slower theta oscillations. High PAC means the brain is entraining well. Low PAC means it's losing sync. I compute this using the Hilbert transform and Tort's Modulation Index, over sliding 2-second windows.
>
> Then I needed to predict where PAC is going. Not just react to what it is now, but forecast what it will be in the future. That's the key difference -- reactive versus predictive.
>
> I trained a causal Temporal Convolutional Network -- a type of deep learning model that uses dilated convolutions to look back over 20 seconds of EEG history. It has about 31,000 parameters and takes 73 input features -- 61 spectral features across 7 channels, 7 PAC-derived features, and 5 stimulus context features -- sampled at 1 Hz over 20 timesteps. The "causal" part means the network architecturally cannot see future data -- it uses left-only padding, so it only has access to past and present. That's critical because in a real-time system, you don't have the future yet.
>
> I plugged this model into a closed-loop controller. Every epoch, it reads the current EEG, computes features, gets the TCN's prediction of PAC 5 seconds from now, and decides: stimulate, or rest.

**Delivery:** This is the densest section. Speak clearly and at a measured pace. When you say "phase-amplitude coupling," point to the PAC diagram. When you say "dilated convolutions" or "20 seconds of history," point to the architecture diagram. You're showing judges you understand every component. Don't rush "left-only padding" -- that's a detail that proves deep understanding.

---

### Part 5: Why 5 Seconds Matters -- The Horizon Sweep (45 seconds)

> *(point to the horizon sweep figure -- this is your most important visual)*
>
> Before I show the controller results, I want to show why the TCN matters. I trained separate models to predict PAC at horizons from 1 second to 10 seconds ahead. At short horizons -- 1 to 2 seconds -- PAC changes so slowly that a trivial baseline works. Just repeat the last value. Persistence gets R-squared of 0.76 at 1 second.
>
> But at 5 seconds, everything changes. Persistence collapses to negative R-squared -- worse than just predicting the average. Ridge regression does the same. Every simple model fails. But the TCN maintains R-squared of 0.25.
>
> Now, 0.25 might not sound impressive, but this is 5 seconds into the future on a noisy biological signal. What matters is the margin: the TCN is at plus 0.25 while baselines are at negative 0.3. That's a 0.5 R-squared gap. And 5 seconds is exactly the horizon where a controller needs predictions to make proactive decisions. That's the TCN's value proposition.

**Delivery:** Slow down here. This is your most original finding and your strongest argument. Point at the horizon sweep figure and trace the lines as you talk. The moment where "everything changes" at 5 seconds should land with emphasis.

---

### Part 6: Results (60 seconds)

> *(gesture toward results / controller comparison)*
>
> I replayed the TCN controller on all 35 patients' real EEG recordings, alongside five other control strategies: fixed schedule, reactive threshold, PI controller, a hybrid system, and a theoretical oracle with perfect knowledge of the future.
>
> *(point to the controller comparison chart)*
>
> The TCN achieved 72.1 percent alignment -- meaning 72 percent of the time, the controller made the correct decision. That's versus 64.5 percent for reactive control. More importantly, when I look specifically at the windows where the brain actually needed stimulation -- low PAC moments -- the TCN caught 82.6 percent of them. Reactive only caught 51.7 percent. That's a 60 percent improvement in therapeutic precision.
>
> All of this is statistically significant. Wilcoxon signed-rank test, p below 0.001. Hedges' g of 1.31 for alignment -- that's a large effect size. And for the low-PAC targeting rate, Hedges' g is 4.47 -- a very large effect.
>
> *(point to per-subject scatter plot)*
>
> But the number I'm most proud of: all 35 out of 35 patients showed higher clinical utility with the TCN controller than with reactive control. Every single one. The probability of that by chance is less than one in 34 billion. And the TCN reaches 91 percent of the theoretical oracle's performance -- meaning we're already close to the ceiling of what's possible.

**Delivery:** Speak numbers clearly. "Seventy-two point one percent" not "72.1%." Slow down on "all 35 out of 35." Point at the scatter plot where every dot is above the diagonal. That visual, combined with your words, is your most powerful moment.

---

### Part 7: Significance and What's Next (30 seconds)

> *(make eye contact, slow down)*
>
> No one had built a predictive closed-loop controller for 40 hertz entrainment before. Existing approaches are either fixed-schedule or reactive at best. This project shows that predictive control is feasible, that it meaningfully outperforms current methods, and that every patient tested showed improved alignment.
>
> The immediate next step would be real-time validation on a streaming EEG system. The model runs in 2 milliseconds, so latency isn't a barrier. Beyond that, validation on additional patient cohorts and potentially using reinforcement learning to optimize the controller thresholds.

**Delivery:** Don't end with "thank you" or "any questions?" End with the forward-looking statement. Then stop. Silence after your last sentence signals confidence. If judges want to ask something, they will.

---

### Timing Breakdown

| Section | Target time |
|---|---|
| Part 1: Hook (grandmother + problem scale) | 30 sec |
| Part 2: Why 40 Hz matters (MIT, clinical trials) | 45 sec |
| Part 3: The gap (fixed schedule + habituation) | 45 sec |
| Part 4: What I built (PAC + TCN + controller) | 75 sec |
| Part 5: Horizon sweep (why 5 seconds) | 45 sec |
| Part 6: Results (controller comparison + stats) | 60 sec |
| Part 7: Significance + next steps | 30 sec |
| **Total** | **~5.5 min** |

### If You Get Interrupted

Judges may jump in with questions at any point. That's fine -- it means they're engaged. Answer the question, then pick up where you left off, or ask: "Should I continue, or would you like to ask more questions?" If you're running short on time and haven't reached results yet, skip ahead: "Let me jump to the results, since those are the most important part."

---

## 3. Judge Q&A Bank

After your presentation, judges will ask questions for the remaining time (~4-5 minutes). This is where you show depth of understanding. Some judges may also interrupt during your presentation to ask questions -- that's fine, it means they're engaged.

Answers are written in first person, as you would naturally say them. Practice saying them aloud, not reading them.

### Category: Your Process and Motivation

**Q: Why did you choose this project? How did you get the idea?**

> My grandmother had dementia, so Alzheimer's research was already on my mind. I came across the MIT studies on 40 Hz entrainment -- the idea that sound at a specific frequency can trigger plaque clearance -- and I was fascinated. But when I read the clinical protocols, I noticed they all used the same fixed timing for every patient. That seemed like an obvious problem to solve with machine learning: predict when a brain needs stimulation instead of guessing with a timer.

**Q: What did you learn from your background/literature research?**

> Three things shaped my approach. First, the Iaccarino et al. 2016 paper showing 40-50% amyloid clearance in mice with 40 Hz light. Second, the 2024 Nature paper showing the mechanism works through the glymphatic system in humans. Third, studies showing that about 30% of patients are non-responders and that individual responses vary enormously -- some habituate, some don't. That variability is what makes a one-size-fits-all schedule inadequate.

**Q: What was your hypothesis?**

> My hypothesis was that a deep learning model trained on temporal EEG features could predict phase-amplitude coupling 5 seconds ahead with enough accuracy to drive a closed-loop controller that outperforms fixed and reactive scheduling on therapeutic targeting metrics.

**Q: What would you do differently if you did this again?**

> Two things. First, I'd try to get access to longer recording sessions. Our data was 6-10 minute sessions, but real clinical protocols run 30-60 minutes. Habituation dynamics might look very different over longer timescales. Second, I'd explore reinforcement learning for the controller thresholds instead of setting them with domain knowledge. Right now the z-score thresholds are heuristic -- an RL agent could potentially find better decision boundaries.

### Category: Technical Understanding

**Q: What is phase-amplitude coupling? Why did you use it?**

> Phase-amplitude coupling measures how the power of a fast oscillation -- in this case, gamma at 40 Hz -- is locked to the phase of a slower oscillation -- theta, around 4-8 Hz. High PAC means the brain is successfully entraining to the 40 Hz stimulus. I used it because it's a validated biomarker for entrainment quality. It's more informative than just measuring gamma power alone, because it captures the cross-frequency interaction that indicates actual neural synchronization.

**Q: How do you actually compute PAC?**

> I bandpass filter the EEG into theta (4-8 Hz) and gamma (38-42 Hz) bands. I extract the phase of theta using the Hilbert transform, and the amplitude envelope of gamma the same way. Then I compute the Modulation Index, which measures how non-uniformly the gamma amplitude is distributed across theta phases. If gamma power peaks at a specific theta phase, you get high PAC. If it's evenly spread, PAC is near zero. I compute this over 2-second sliding windows with 50% overlap.

**Q: What is a Temporal Convolutional Network? Why not an LSTM or Transformer?**

> A TCN uses 1D convolutions with dilation -- meaning the filter skips over inputs at exponentially increasing intervals -- to capture long-range temporal patterns. With each stacked layer, the receptive field doubles, so a small network can see 20 seconds of history. I chose it over LSTMs because TCNs are causal by construction -- they use left-only padding so no future information can leak in. They're also faster to train and more parallelizable. I did test an LSTM during development, and the TCN outperformed it. I didn't use a Transformer because with only 35 patients and relatively small sequences, self-attention would be overkill and prone to overfitting.

**Q: What does "causal" mean in the context of your TCN?**

> It means the network can only see past and present data when making a prediction -- never future data. This is enforced architecturally through left-only padding in the convolutional layers. It's critical for a real-time system because in deployment, you genuinely don't have access to future EEG values. If I'd used standard centered convolutions, the model would cheat by peeking at data that wouldn't exist yet in a live system.

**Q: What are dilated convolutions? Why do they matter?**

> A normal convolution looks at adjacent time steps. A dilated convolution inserts gaps -- the dilation factor determines how many steps it skips. In my TCN, the first layer has dilation 1 (adjacent steps), the second has dilation 2 (every other step), the fourth has dilation 8. This means layer by layer, the network's receptive field grows exponentially without adding parameters. My network has about 31,000 parameters but can see 20 seconds of EEG history. Without dilation, you'd need either a much deeper network or much larger filters.

**Q: Explain the horizon sweep. Why is 5 seconds the key?**

> I trained separate models to predict PAC at horizons from 1 to 10 seconds. At 1-2 seconds, PAC changes so slowly that just repeating the last value works well -- persistence gets R-squared of 0.76. But at 5 seconds, persistence collapses to negative R-squared, meaning it's worse than just predicting the average. The TCN maintains R-squared of 0.25 at 5 seconds. That 0.5 margin is the TCN's entire value proposition -- it's the only model that gives useful predictions at the timescale a controller actually needs for proactive decisions. A controller needs at least 3-5 seconds of lead time to schedule stimulation meaningfully.

**Q: R-squared of 0.25 seems low. Is that actually useful?**

> It does seem low if you compare it to, say, a weather model. But in this context, it's very useful. The controller doesn't need to predict the exact PAC value -- it just needs to predict the direction: is PAC trending down (brain losing entrainment) or staying high (brain is fine)? An R-squared of 0.25 at 5 seconds means the model explains 25% of future PAC variance, which is enough to make directional calls that are right far more often than chance. The proof is in the downstream result: when I plug these predictions into a controller, it achieves 72% alignment and targets 83% of low-PAC windows. The controller amplifies even modest prediction accuracy into meaningful therapeutic improvement.

**Q: What is your model's architecture exactly? How many parameters?**

> The TCN has 4 causal depthwise-separable conv blocks, each with GroupNorm, SiLU activation, and Dropout of 0.2. Dilation factors are 1, 2, 4, 8 with kernel size 3, giving a receptive field of 31 steps. Input is 73 features times 20 timesteps (20 seconds at 1 Hz). The output is a single scalar: predicted PAC at the target horizon. About 31,000 total parameters. That's intentionally small -- with only 35 subjects, a larger model would overfit.

**Q: What are the 73 input features?**

> They break down into three groups. First, 61 spectral features: 4 frequency bands times 7 channels gives 28 band powers, plus 7 band-power ratios, 21 PAC-structure features, and 5 global spectral descriptors. Second, 7 PAC-derived features computed from the 7 frontal channels. Third, 5 stimulus context features encoding the current stimulation state. All computed from 7 frontal EEG channels: Fp1, Fp2, F3, F4, F7, F8, and Fz. These were selected because frontal regions show the strongest 40 Hz entrainment response.

**Q: How did you avoid data leakage?**

> Three ways. First, subject-level split: the 35 patients are divided into training, validation, and test sets with zero overlap. No patient's data appears in more than one split. Second, temporal causality: all features are computed from past and current data only, and the TCN architecture enforces causal-only access. Third, normalization: the mean and standard deviation used to scale the data are computed on the training set only, then applied to validation and test. I also ran a shuffle-label sanity check -- when I randomly shuffle the target labels, the model gets R-squared of negative 0.33, confirming it's learning real patterns, not artifacts.

**Q: Tell me about the architecture marathon. You tested 8 models?**

> Yes. Before building the temporal system, I tried to predict PAC from a single EEG window -- a static prediction task. I tested 8 architectures ranging from 135 parameters to about 1.1 million: a small CNN, a medium CNN, EEGNet, ResNet, SpecTempNet, and several others. Every single one converged to R-squared of approximately 0.287. When 8 very different architectures all hit the same ceiling, that tells you the bottleneck is the data, not the model. 7 frontal channels at 250 Hz simply don't contain enough information for a single snapshot to predict PAC better than that. That's what motivated the shift to temporal modeling -- using sequences of windows instead of individual ones.

**Q: What was the SpecTempNet leakage issue?**

> Early in development, one of my models -- SpecTempNet -- appeared to achieve R-squared of 0.69, which was suspiciously high. When I investigated, I found that the input features included PAC itself. The model was essentially being given a version of the answer in the input. Once I removed PAC from the input features, performance dropped to 0.236, consistent with all the other architectures. That was actually a valuable lesson -- it taught me to be extremely careful about what information flows into the model and to always check for circular features.

### Category: Results and Validation

**Q: How does the closed-loop controller work?**

> The controller runs a loop every epoch. It gets the current EEG, computes features, feeds them to the TCN, and gets a predicted PAC value for 5 seconds from now. It converts that prediction to a z-score relative to the patient's historical distribution. If the z-score drops below a threshold -- meaning the brain is predicted to lose entrainment -- it triggers stimulation. If the prediction is above threshold, it allows the brain to rest. There's also a hysteresis mechanism to prevent rapid on-off switching, and a minimum stimulation duration to ensure each pulse is therapeutically meaningful.

**Q: What controllers did you compare against?**

> Six total. Fixed schedule -- 40 seconds on, 20 off -- which is the clinical standard. Reactive threshold -- stimulate whenever current PAC drops below a cutoff. PI controller -- a proportional-integral feedback controller. TCN predictive -- my system. Hybrid -- TCN plus reactive fallback. And an oracle that has perfect future knowledge, as an upper bound. The TCN predictive achieves 91% of the oracle's PAC targeting performance.

**Q: You say all 35 patients showed improved alignment. How do you know?**

> For every patient, I computed an alignment score under both TCN and reactive control. In a scatter plot with reactive on the x-axis and TCN on the y-axis, all 35 points fall above the diagonal line. That means for every single subject, TCN alignment was higher than reactive alignment. The probability of that happening by chance alone -- 35 out of 35 -- is less than one in 34 billion. The formal binomial p-value is below 0.001.

**Q: What's the difference between alignment and low-PAC targeting?**

> Alignment is the fraction of epochs where the controller makes the "right" decision -- stimulating when PAC is low OR resting when PAC is high. Low-PAC targeting rate is more specific: of all the epochs where the brain actually needed stimulation (PAC was low), what fraction did the controller catch? The TCN gets 72% alignment overall, but more importantly, it catches 83% of the low-PAC windows. Reactive only catches 52%. That means the TCN is far better at concentrating stimulation where it's actually needed.

**Q: What is Hedges' g? Why use Wilcoxon instead of a t-test?**

> Hedges' g is an effect size measure -- it tells you how many standard deviations apart two conditions are, corrected for small sample bias. A g above 0.8 is considered a large effect. Our primary metric has g of 1.31. I used the Wilcoxon signed-rank test instead of a paired t-test because with 35 subjects, I can't confidently assume the data is normally distributed. Wilcoxon is a non-parametric test that doesn't require that assumption -- it ranks the differences instead of assuming a specific distribution shape.

**Q: What about the habituation finding?**

> Across all 35 patients, 17 showed declining PAC over stimulation blocks -- they habituated -- and 18 showed increasing PAC -- they facilitated. The population-level paired t-test is not significant (p = 0.542), meaning there's no net trend. But individual variability is enormous: some patients decline by 67%, others increase by 149%. This is actually the most important finding for motivating adaptive control. If everyone habituated the same way, you could just build one declining schedule. But since half go one direction and half go the other, you genuinely need a system that monitors each individual brain and adapts.

### Category: Creativity and Independence

**Q: What's novel about your approach?**

> Three things. First, no one has built a predictive closed-loop controller specifically for 40 Hz entrainment -- existing systems are reactive at best. Second, the horizon sweep methodology is a novel way to evaluate forecasting models: instead of reporting a single accuracy number, I show where the model adds value relative to baselines across the entire prediction horizon. Third, the architecture marathon -- systematically testing 8 models to prove the performance ceiling is a data limitation, not a model limitation -- is an unusual but rigorous approach to justifying a major design pivot.

**Q: How much help did you receive? Did anyone write code for you?**

> I wrote all the code myself. I used AI tools as a learning resource -- similar to how you'd use Stack Overflow or a textbook -- for understanding concepts like dilated convolutions or the Hilbert transform. But every design decision, every architecture choice, every debugging session was mine. For example, when SpecTempNet showed suspiciously high R-squared, I was the one who traced it to PAC features leaking into the input. When the architecture marathon showed a ceiling, I was the one who decided to pivot to temporal modeling. The scientific reasoning and engineering decisions are entirely my own work.

**Q: Is this project based on anything from the internet?**

> The underlying therapy -- 40 Hz entrainment -- comes from published research by Tsai and others at MIT. The machine learning techniques (TCNs, PAC computation) are established methods. But the specific application -- building a predictive controller for adaptive 40 Hz stimulation delivery -- is original. No existing paper or project does what mine does. I reviewed the literature extensively and couldn't find any prior work that combines temporal PAC forecasting with closed-loop stimulation control.

### Category: Future Work and Limitations

**Q: What are the biggest limitations?**

> The biggest limitation is that this is offline replay, not live closed-loop. I validated by replaying recorded EEG, but I haven't tested it in real time with actual latency and system integration challenges. Second, all 35 patients are from a single Iranian cohort, so I don't know how it generalizes across populations. Third, the recording sessions are only 6-10 minutes, while real clinical sessions run 30-60 minutes. Habituation dynamics might be very different over longer durations. I'm honest about these in my poster.

**Q: What are the next steps?**

> The immediate next step would be real-time validation -- deploying the model on a streaming EEG system to measure actual inference latency and controller performance under realistic conditions. Beyond that, I'd want to validate on a different patient cohort to test cross-population generalization. Long-term, the controller thresholds could be optimized with reinforcement learning instead of heuristic settings, and the approach could potentially extend to other entrainment frequencies beyond 40 Hz.

**Q: Could this actually be used in a clinic?**

> The core system -- TCN inference on a single EEG window -- runs in about 2 milliseconds on a standard laptop, so latency is not a barrier. The bigger challenges for clinical translation are regulatory (this would need FDA clearance as a medical device), integration with commercial EEG hardware, and clinical validation trials to show that improved PAC targeting actually translates to better patient outcomes like cognitive improvement or plaque reduction. This project demonstrates feasibility and the performance advantage, but clinical deployment would require substantial additional validation.

**Q: Why only 35 subjects? Is that enough?**

> The dataset is from OpenNeuro ds005048, which is one of the only publicly available EEG datasets of 40 Hz auditory stimulation in elderly subjects with cognitive impairment. 35 subjects is small for a machine learning study, but three things give me confidence. First, the results are consistent across all 35 -- not driven by outliers. Second, the statistical tests I used (Wilcoxon signed-rank) are appropriate for small samples. Third, the effect sizes are very large (Hedges' g above 1.3), meaning the differences aren't subtle -- they're clear enough to detect reliably even with 35 subjects.

### Category: Technical Deep Dives (If Judges Are Domain Experts)

**Q: Why frontal channels? Why only 7 of the 19?**

> Frontal channels (Fp1, Fp2, F3, F4, F7, F8, Fz) show the strongest 40 Hz auditory steady-state response. The stimulus is auditory, so the primary cortical response propagates from auditory cortex to frontal regions. Using only frontal channels also reduces computational cost and noise from less relevant posterior regions. The 7-channel choice was informed by literature on auditory steady-state responses.

**Q: What's the difference between your PAC and Tort's Modulation Index?**

> I use Tort's Modulation Index, which is based on the Kullback-Leibler divergence between the observed amplitude distribution across phase bins and a uniform distribution. It's normalized to range from 0 (no coupling) to 1 (perfect coupling). I chose it because it's well-validated, relatively robust to noise, and widely used in the entrainment literature. There are other methods -- like the mean vector length or the phase-locking value -- but Tort's MI is the most common in 40 Hz studies.

**Q: How did you handle the train/val/test split with only 35 subjects?**

> I used a subject-level split: approximately 70% train, 15% validation, 15% test. The key constraint is that no subject appears in more than one split. Within each subject's data, I preserve temporal order -- I never shuffle time steps, because that would break causal relationships. The validation set is used for early stopping and hyperparameter selection. The test set is only touched for final evaluation.

**Q: What regularization did you use?**

> Dropout of 0.2 in the conv blocks and prediction heads, weight decay of 1e-3 in the AdamW optimizer, and early stopping based on validation loss with patience of 20. The model is intentionally kept small (31K parameters) to limit capacity. GroupNorm also provides some implicit regularization by stabilizing training across subjects.

**Q: What loss function?**

> Huber loss with delta equal to 1.0. PAC prediction is a regression task -- I'm predicting a continuous value. I chose Huber over MSE because it's more robust to outlier PAC values, which can occur during artifact-heavy windows. I also computed MAE and R-squared as evaluation metrics, but training optimized Huber loss.

---

## 4. Danger Zones

These are the moments that could cost you points. Have answers ready.

### Danger Zone 1: "Did AI write your code?"

**What they're probing for:** Independent Work / Skill (10 points)

**Your answer:**
> I used AI as a learning tool, the same way someone would use Stack Overflow, a textbook, or a professor's office hours. I'd ask it to explain a concept like dilated convolutions, or help me debug an error message. But I made every design decision -- which model to try, how to compute PAC, when to pivot from static to temporal -- and I wrote the implementation. The SpecTempNet leakage discovery is a good example: no tool told me the R-squared was suspiciously high. I noticed it, traced it to PAC features in the input, and fixed it. That's the kind of scientific reasoning that matters.

**Key:** Don't be defensive. Frame it as a tool. Then immediately pivot to a concrete example of YOUR independent reasoning.

### Danger Zone 2: "R-squared of 0.25 doesn't seem very good"

**Your answer:**
> You're right to push on that -- I pushed on it too. The key insight is that the downstream controller doesn't need perfect prediction. It needs directional accuracy: is PAC going up or down? An R-squared of 0.25 at 5 seconds ahead provides enough signal for the controller to target 83% of low-PAC windows, compared to 52% for reactive. The proof that 0.25 is useful isn't the number itself -- it's the 72% alignment and the fact that all 35 patients showed improved alignment.

### Danger Zone 3: "This is just a simulation, not a real system"

**Your answer:**
> That's correct -- it's offline replay, not live deployment, and I'm explicit about that as a limitation. But the replay uses real patient EEG, real timing, and the model only sees data that would be available in real time. It's the standard validation approach in BCI research before moving to live systems. The results demonstrate feasibility and quantify the advantage. Clinical deployment would be the natural next step, and the model's 2-millisecond inference time suggests real-time operation is feasible.

### Danger Zone 4: "35 patients isn't enough data"

**Your answer:**
> It's a real limitation, and I acknowledge it. But three things give me confidence. First, the effect sizes are very large -- Hedges' g of 1.31 for alignment -- so the differences are detectable even with 35 subjects. Second, all 35 of 35 subjects showed improvement, not just the average. Third, I used non-parametric statistics that are appropriate for small samples. This is also the largest publicly available EEG dataset with this protocol during 40 Hz stimulation, so it's the best data currently accessible.

### Danger Zone 5: "How is this different from just a reactive controller?"

**Your answer:**
> Reactive controllers respond after the brain has already lost entrainment. By the time PAC drops and you detect it, you've already missed the therapeutic window. My system predicts the drop 5 seconds in advance, so it can start stimulation before the brain loses synchronization. That's the difference between a smoke detector that goes off during the fire and one that goes off before the fire starts. The numbers show the difference: the TCN targets 83% of low-PAC windows while reactive only catches 52%.

---

## 5. Delivery Tips

### Pacing
- Speak at about 70% of your normal conversational speed. Judges are processing technical content.
- Pause after every key number. "Seventy-two percent alignment... (beat) ...versus sixty-five for reactive."
- If you catch yourself speeding up, take a breath. It's okay to pause.

### Body Language
- Stand slightly to one side of your poster, not directly in front of it. Judges need to see the board.
- Face the judges, not the poster. Glance at the board only when pointing to something specific.
- Open palm gestures toward the poster. Never point with one finger -- it looks aggressive.
- Keep your hands visible. Don't fold arms or put hands in pockets.

### Answering Questions
- If you don't know the answer, say: "That's a great question -- I'm not sure about that specific aspect, but here's what I do know..." Then pivot to related knowledge.
- Never bluff. Judges can tell. Honesty about limitations scores higher than a fabricated answer.
- If a question is ambiguous, ask for clarification: "When you say X, do you mean A or B?" This shows analytical thinking.
- After answering, stop. Don't keep talking to fill silence. Let the judge process.

### Common Mistakes to Avoid
- Don't read from notes or your poster. You should know this cold.
- Don't use filler words: "like," "um," "basically," "so yeah." Practice eliminating them.
- Don't apologize for your work or hedge excessively. State results confidently with appropriate caveats.
- Don't mention tools, frameworks, or libraries unless asked. Say "I computed PAC using the Hilbert transform," not "I used SciPy's hilbert function."
- Don't speak to your poster. Speak to the humans.
- Don't say "I just" or "It's just." Those words minimize your work.

### The Night Before
- Read through this script 3 times aloud. Time yourself.
- Pick 5 Q&A answers you feel weakest on and practice those aloud.
- Get your notebook ready, tabbed to key sections (data integrity checks, habituation analysis, architecture comparison).
- Lay out your clothes. Dress one notch above what you'd normally wear.
- Sleep. A well-rested brain answers questions better than one that crammed until 2am.

---

## Quick Reference Card (Print This on an Index Card for Your Pocket)

```
KEY NUMBERS:
- 55 million patients, $300B/year
- 35 elderly subjects, 19 EEG channels, 250 Hz
- TCN: 31K parameters, 4 residual blocks, dilation 1/2/4/8
- 73 input features, 20-second lookback at 1 Hz
- Horizon sweep: R² = 0.25 at 5s (baselines: negative)
- Alignment: 72.1% TCN vs 64.5% reactive (p < 0.001)
- Low-PAC targeting: 82.6% vs 51.7% (g = 4.47)
- 35/35 subjects showed improved alignment (binomial p < 0.001)
- 91% of oracle bound
- Habituation: 48.6% habituate, 51.4% facilitate (p = 0.542)

KEY PHRASES:
- "Predict before the brain loses sync, not react after"
- "The proof is in the downstream controller performance"
- "Not the number -- it's that all 35 patients showed improved alignment"
- "Data limitation, not model limitation"
- "Causal means no access to future data"
```
