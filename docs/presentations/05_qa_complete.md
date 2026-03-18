# Complete Q&A -- Basic to Hardest

Every answer is backed by your actual data. No fluff. Memorize the core of each answer; the exact words can be your own.

---

## TIER 1: BASIC -- Every judge will ask at least one of these

**What is your project about?**

I built a deep learning system that predicts when an Alzheimer's patient's brain is about to lose response to 40 hertz auditory stimulation, 5 seconds before it happens. It then adapts stimulation timing to target the moments the brain actually needs it, instead of using the same fixed schedule for every patient.

---

**Why did you choose this project? How did you come up with this idea?**

My grandmother had dementia. That put Alzheimer's research on my radar. I came across the MIT studies on 40 hertz entrainment -- sound that triggers the brain to clear amyloid plaques -- and I was fascinated. But when I read the clinical protocols, they all used the same rigid timing for every patient. That seemed like an obvious engineering problem: the therapy is personalized by nature, but the delivery isn't. I wanted to fix that.

---

**What was your hypothesis?**

That a causal deep learning model could predict phase-amplitude coupling 5 to 10 seconds into the future with enough accuracy to drive a closed-loop controller that outperforms both fixed scheduling and reactive approaches on real patient EEG data.

---

**What background research/reading did YOU do?**

I read the foundational papers: Iaccarino 2016 showing 40-50% plaque reduction in mice with 40 Hz light, Martorell 2019 extending it to multi-sensory stimulation, Lahijanian 2024 showing auditory entrainment enhances default mode network connectivity in human dementia patients, Tort 2010 on the Modulation Index for computing PAC, and Thompson & Spencer 1966 on neural habituation. These shaped every design decision -- PAC as the biomarker, frontal channels as the signal source, and adaptive scheduling as the intervention.

---

**What data did you use? How much data did you collect?**

I used a publicly available dataset from OpenNeuro -- ds005048 by Lahijanian et al. 2024. 35 elderly subjects, 7 frontal EEG channels at 250 Hz, alternating 40 Hz auditory stimulation and rest epochs. I extracted 17,283 two-second windows. Subject-level splits: 24 train, 5 validation, 6 test -- no patient appears in more than one split.

---

**How long did this take?**

About four months of focused work. The first phase was data loading, preprocessing, and PAC computation. The second was the architecture marathon -- testing six models for static PAC estimation. The third was building the temporal prediction pipeline and the causal TCN. The fourth was the controller, validation, and statistical analysis.

---

## TIER 2: METHODOLOGY -- How did you do it?

**What is phase-amplitude coupling? Why did you use it?**

PAC measures how tightly the amplitude of fast gamma oscillations at 40 Hz is locked to the phase of slower theta oscillations at 4-8 Hz. High PAC means the brain is synchronized to the stimulus -- the therapy is working. Low PAC means it's losing sync. I used it because it's more specific than raw gamma power. Gamma power tells you how much 40 Hz activity there is; PAC tells you whether that activity is actually organized and entrained. It's the validated biomarker for entrainment quality in the literature.

---

**How do you compute PAC?**

I bandpass filter the EEG into theta (4-8 Hz) and gamma (38-42 Hz). I extract theta phase and gamma amplitude using the Hilbert transform. Then I compute Tort's Modulation Index, which divides the theta cycle into 18 phase bins, computes mean gamma amplitude in each, and measures how non-uniform that distribution is using Kullback-Leibler divergence against a uniform distribution. If gamma peaks at one specific theta phase, PAC is high. If it's spread evenly, PAC is near zero.

---

**Why frontal channels? Why only 7 of the 19?**

Auditory 40 Hz stimulation produces the strongest entrainment response at frontal electrode sites -- Fp1, Fp2, F3, F4, F7, F8, Fz. I tested adding temporal and occipital channels; they added noise without improving PAC prediction. Seven channels captures the relevant signal while keeping the model small enough for real-time inference.

---

**What is EEGNet? Why did you choose it?**

EEGNet is a compact convolutional neural network designed for EEG-based brain-computer interfaces. It uses temporal convolutions followed by depthwise spatial convolutions -- essentially learning frequency filters and then spatial channel weightings. I chose it because it matched the best R-squared (0.287) with only 1,457 parameters. That's 12 training samples per parameter, well within safe overfitting margins. It's also fast enough for real-time inference on embedded hardware.

---

**What is a Temporal Convolutional Network? Why not LSTM or Transformer?**

A TCN uses 1D dilated convolutions to capture temporal patterns. Each layer's dilation factor doubles, so the receptive field grows exponentially without adding parameters. I chose it over LSTMs because TCNs are causal by construction -- left-only padding means no future leakage is architecturally possible. They're also faster to train and more parallelizable. I didn't use a Transformer because with only 35 subjects and 20-step sequences, self-attention would overfit. The TCN's inductive bias -- local temporal patterns with increasing receptive field -- matches EEG signal structure.

---

**What does "causal" mean here?**

The network can only see past and present, never future. This is enforced by padding convolutions only on the left side. It's not a training rule that could be violated -- it's a structural property of the architecture. In a real-time clinical system, you don't have the future. This model is built so it can't accidentally cheat.

---

**What are the 73 input features?**

28 band power features (power in theta, alpha, beta, gamma across 7 channels — no delta band), 7 theta/gamma power ratio features (one per channel), 21 PAC-structure features (inter-channel PAC-derived), 5 global statistics (spectral entropy, peak frequency, bandwidth, asymmetry, concentration) = 61 spectral features total; plus 7 PAC-derived features (current PAC, moving averages at 2/4/8/16 steps, first differences at 1/4 steps), and 5 stimulation context features (stim on/off, time since last switch, recent stim fraction, cycle phase encoded as sine and cosine).

---

**How did you avoid data leakage?**

Four safeguards. First, subject-level splits -- the 6 test patients were never seen during training or validation. Second, causal architecture -- left-only padding prevents future information access. Third, train-only normalization -- z-score statistics computed from training data only, then applied to validation and test. Fourth, shuffle-label sanity check -- when I randomized PAC labels, R-squared dropped to negative 0.33, confirming the model learns real signal.

---

**What loss functions did you use?**

MSE for EEGNet -- straightforward regression. Huber loss for the TCN -- it's robust to PAC outliers, which matter because PAC distributions have long tails. Huber acts like MSE for small errors and like MAE for large ones, preventing extreme outliers from dominating the gradient.

---

**What regularization did you use?**

Dropout (0.5 for EEGNet, 0.1 for TCN), weight decay of 1e-3 in the TCN optimizer, early stopping on validation loss (patience 20 for TCN, 15 for EEGNet), gradient clipping at max_norm 1.0 for EEGNet, and intentionally small model size -- 31K parameters for the TCN when I could have used more.

---

## TIER 3: RESULTS & VALIDATION

**Walk me through your results.**

Four key results. First, the TCN predictive controller achieves 72.1% alignment and catches 82.6% of low-PAC windows on all 35 subjects' real EEG, versus 64.5% and 51.7% for reactive -- that's Hedges' g of 1.31 and 4.47, both p less than 0.001. Second, all 35 out of 35 patients individually benefit -- binomial p less than 0.001. Third, the advantage grows with neural fatigue, from +9% to +11.2%. Fourth, results hold across four different mathematical fatigue models.

---

**How did you validate? What makes this trustworthy?**

Two independent protocols. Primary: I replayed the TCN controller on all 35 subjects' actual EEG recordings -- real brain data, not simulation. The controller only sees data available in real time. Secondary: closed-loop simulation with neural fatigue modeling across 6 severity levels, 50 trials each, 600 seconds per trial. Statistics: Wilcoxon signed-rank tests (non-parametric, paired), bootstrap 95% confidence intervals, and Hedges' g effect sizes. Compared against fixed schedule, reactive threshold, PI controller, and a theoretical oracle.

---

**What controllers did you compare against?**

Four. Fixed schedule (40s on, 20s off -- the clinical standard). Reactive threshold (stimulate when current PAC drops below a cutoff). PI controller (proportional-integral feedback). Alignment oracle (perfect future knowledge -- the theoretical ceiling). The TCN reaches 92% of the oracle's targeting performance.

---

**What do alignment and low-PAC targeting mean?**

Alignment is the percentage of time the controller makes the correct decision -- stimulating when PAC is low OR resting when PAC is high. Low-PAC targeting is more specific: of all the moments where the brain genuinely needed stimulation (PAC below median), what fraction did the controller actually catch? TCN catches 82.6%. Reactive catches 51.7%. That's the clinically important metric -- are you getting stimulation to the patients who need it, when they need it?

---

**Why Wilcoxon instead of a t-test? Why Hedges' g instead of Cohen's d?**

Wilcoxon signed-rank is a non-parametric paired test. With 35 subjects I can't confidently assume normality, so Wilcoxon makes fewer assumptions -- it ranks differences instead of assuming a specific distribution shape. Hedges' g is like Cohen's d but corrected for small-sample bias. Cohen's d overestimates effect size when n is small. With n=35, the correction matters.

---

**Tell me about the habituation finding.**

17 of 35 patients (49%) show declining PAC across stimulation blocks -- they habituate. 18 (51%) show stable or increasing PAC -- they facilitate. Population-level, the paired t-test is not significant (p = 0.542). But individual variability is massive -- one patient declined 67%, another increased 149%. This is the biological justification for adaptive control. If everyone habituated identically, you could build one declining schedule. But since half go one direction and half go the other, you genuinely need per-patient adaptation.

---

## TIER 4: PROCESS & INDEPENDENCE -- From the judging criteria

**How did you progress from hypothesis to results?**

Step by step. First I loaded and preprocessed the EEG data, computing PAC for each epoch. Then I tried to predict PAC from single windows -- that's the architecture marathon, six models, all hitting R-squared 0.287. That ceiling told me single-snapshot prediction was maxed out. So I pivoted to temporal prediction -- using sequences of past observations to forecast future PAC. Built the causal TCN, ran the horizon sweep to prove it adds value at 5+ seconds, then plugged it into a closed-loop controller and validated on all 35 patients' real EEG.

---

**Did you discover any errors or problems? How did you address them?**

Yes. The biggest one was SpecTempNet. Early on, it appeared to hit R-squared of 0.69 -- way above everything else. I was suspicious, so I investigated the input features and found that PAC itself was accidentally included as an input. The model was being given a version of the answer. Once I removed it, performance dropped to 0.236, consistent with everything else. That taught me to audit every feature for circularity. It also reinforced that the 0.287 ceiling was real, which is what ultimately motivated the pivot to temporal modeling.

---

**How much did you do yourself? Did AI write your code?**

I wrote all the code myself -- data loading, preprocessing, PAC computation, model architectures, training loops, controller logic, statistical validation. I used AI tools as a learning resource, the same way you'd use a textbook or Stack Overflow -- to understand concepts like dilated convolutions or to debug error messages. But every design decision was mine. The SpecTempNet leakage discovery is a good example: no tool told me the R-squared was suspicious. I noticed it, traced it to the input features, and fixed it. The scientific reasoning and engineering judgment are my own.

---

**What resources did you have?**

A laptop with Apple Silicon (M-series). No cloud GPUs, no lab access, no advisor. Python 3.13, PyTorch, and standard scientific Python libraries. The dataset is publicly available on OpenNeuro. I ran everything locally -- the models are small enough that training takes minutes, not hours.

---

**Is the work complete?**

The offline validation pipeline is complete -- from raw EEG data all the way through to statistically validated controller comparison. What remains is live closed-loop validation, which requires a real-time EEG streaming setup. The model architecture, the controller logic, and the validation framework are all finished and tested. The next phase is deployment, not development.

---

## TIER 5: HARD -- Challenge questions and skepticism

**R-squared of 0.25 at 5 seconds seems low. Is that actually useful?**

Yes, and here's why. The controller doesn't need the exact PAC value -- it needs direction. Is coupling trending down or holding steady? R-squared 0.25 is enough for the controller to target 82.6% of low-PAC windows versus 51.7% for reactive. The proof that 0.25 is useful isn't the number itself -- it's the downstream result. 72% alignment, 83% therapeutic targeting, all 35 patients benefit. The controller amplifies even modest prediction accuracy into meaningful therapeutic improvement.

---

**This is just a simulation, not a real system.**

The primary results are NOT simulation. I replayed the controller on all 35 patients' actual EEG recordings. Real brain data, real timing. The model only sees data that would be available in real time. The simulation is secondary evidence about fatigue dynamics, tested across four different fatigue model assumptions for robustness. Offline replay is the standard validation approach in brain-computer interface research before moving to live systems. And I'm transparent about this as a limitation on my poster.

---

**35 patients isn't enough data.**

Three things give me confidence despite the small sample. First, the effect sizes are very large -- Hedges' g of 1.31 to 4.47 -- so the differences are clear, not subtle. Second, all 35 out of 35 patients benefited individually, not just on average. Third, I used Wilcoxon signed-rank, a non-parametric test appropriate for small samples. This is also the largest publicly available EEG dataset with this protocol during 40 Hz stimulation. It's the best data currently accessible for this question.

---

**How is this different from just a reactive controller?**

Reactive responds after the brain has already lost entrainment. By the time PAC drops and you detect it, you've missed the therapeutic window. My system predicts the drop 5 seconds in advance and starts stimulation before the brain loses sync. The difference shows in the numbers: TCN catches 82.6% of low-PAC windows, reactive catches 51.7%. Reactive misses almost half of the moments that need treatment.

---

**Why not use a larger model, a Transformer, or GPT?**

I tested six architectures from 1,457 to 2 million parameters. They all converge near the same performance for static PAC estimation. The 2-million-parameter model scored lower than the 1,457-parameter one due to overfitting. With 17,000 training samples from 35 subjects, the dataset is the bottleneck. A Transformer's self-attention is O(n-squared) in sequence length -- overkill for 20-step sequences and prone to overfitting with this data size. The TCN's inductive bias of local temporal patterns with exponentially growing receptive field matches EEG signal structure.

---

**What's actually novel about your approach?**

Three things. First, no one has built a predictive closed-loop controller for 40 Hz entrainment -- existing approaches are reactive at best. I searched the literature extensively. Second, the horizon sweep methodology -- evaluating where a forecasting model adds value relative to baselines across the full prediction horizon, rather than reporting a single accuracy number. Third, systematically testing six architectures to prove the performance ceiling is a data limitation and using that finding to justify the pivot to temporal modeling.

---

**Could this actually be used on real patients?**

The model runs in 2 milliseconds on a standard laptop. Latency isn't the barrier. The challenges for clinical deployment are: FDA clearance as a medical device, integration with commercial EEG hardware, and clinical validation trials showing that improved PAC targeting translates to better patient outcomes -- cognitive improvement or plaque reduction. This project demonstrates feasibility and quantifies the advantage. A crossover clinical study would be the natural next step.

---

**What are the biggest limitations?**

Three. First, offline replay, not live closed-loop -- the system makes decisions on real data but can't observe the brain's response to those decisions. Second, single cohort of 35 patients from one study site -- cross-population generalization is unconfirmed. Third, sessions are 6-10 minutes while clinical protocols run 30-60 minutes -- habituation dynamics could differ at longer timescales, though that would likely strengthen the case for adaptive scheduling.

---

**What would you do differently?**

Three things. First, get access to longer recording sessions -- 30-60 minutes instead of 6-10 -- to capture the full habituation time course. Second, deploy with live EEG streaming for real-time crossover validation: same patients, adaptive versus fixed, within the same session. Third, replace the heuristic z-score controller thresholds with reinforcement learning, which could find better decision boundaries through optimization rather than domain knowledge.

---

**What does the model actually learn? How do you know it's learning real patterns?**

Feature ablation shows PAC-derived features alone give the TCN R-squared of 0.859, while spectral-only features give 0.045. The model primarily learns the temporal dynamics of phase-amplitude coupling -- how entrainment strength evolves over time. The shuffle-label sanity check confirms real learning: randomized labels give R-squared of negative 0.33, meaning the model correctly learns nothing from noise.

---

**How does the closed-loop controller actually make decisions?**

Every second, EEGNet estimates current PAC from raw EEG. That estimate joins a 20-step history buffer. The TCN reads the buffer and predicts PAC 5 seconds ahead. That prediction is converted to a z-score against the patient's rolling baseline. If the z-score drops below negative 0.5, the brain is predicted to lose entrainment, so it triggers stimulation. If above positive 0.5, it rests. There's a hysteresis mechanism to prevent rapid on-off switching and a minimum stimulation duration to ensure therapeutic meaning.

---

**What's the difference between your primary and secondary validation?**

Primary is real data: I replayed the controller on all 35 subjects' recorded EEG. No simulation, no synthetic dynamics. The controller makes counterfactual decisions on real brain signals. Secondary is simulation: a closed-loop model with neural fatigue dynamics across 6 severity levels, 50 trials each, 600 seconds per trial. The simulation addresses a question the replay can't -- what happens under sustained fatigue over longer periods. The primary validation is the stronger evidence; the simulation is complementary.

---

**What about the architecture marathon? Why was that important?**

Before building the temporal system, I tested six architectures for static PAC estimation. EEGNet (1,457 params), SpecTempNet (180K), ViT-TCNet (2M), Ridge regression (135 coefficients), ATCNet (25K), and EEGNetLarge (141K). All three simplest models -- EEGNet, Ridge, EEGNetLarge -- converge at R-squared 0.287. The complex ones performed worse due to overfitting. That convergence proves 0.287 is a data ceiling, not a model limitation. Recognizing that was what justified the entire pivot from static to temporal prediction. Without the marathon, I might have kept trying bigger models and never moved forward.

---

**Do the conclusions follow from the data?**

Every conclusion maps to a specific finding. "TCN outperforms reactive" maps to Hedges' g = 1.31 for alignment and 4.47 for targeting, both p less than 0.001 on 35 subjects. "Every patient benefits" maps to 35/35 above-diagonal scatter, binomial p less than 10 to the negative 10. "Advantage grows with fatigue" maps to a monotonic trend from +9% to +11.2% across 6 severity levels, confirmed across 4 fatigue model assumptions. The limitation -- offline replay -- is stated explicitly on the poster.

---

**What's the clinical or societal impact?**

Alzheimer's affects 55 million people worldwide. If 40 Hz entrainment reaches clinical adoption -- and multiple trials are underway -- the delivery system matters. My results show you can get 60% more therapeutic targeting with adaptive control. For patients who habituate, that could mean the difference between a therapy that works for 10 minutes and fades, versus one that maintains effectiveness through the full session. Less wasted stimulation also means potentially shorter sessions and less patient burden.
