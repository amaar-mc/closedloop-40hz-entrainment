# Master Q&A Bank: CSEF 2026

**Format:** Judges have read your 13-page presentation and abstract. They arrive with questions. This is your drill material. 100+ questions, organized by category.

---

## Quick Reference Numbers

| Metric                  | Value                                      |
| ----------------------- | ------------------------------------------ |
| Subjects                | 35 elderly (17 AD, 6 MCI, 10 HC, 2 unspec) |
| Channels                | 7 frontal (Fp1, Fp2, F7, F3, Fz, F4, F8)   |
| Sampling rate           | 250 Hz                                     |
| Windows                 | 17,283 (2s each, 1s hop)                   |
| Splits                  | 24 train / 5 val / 6 test (subject-level)  |
| EEGNet params           | 1,457                                      |
| EEGNet R2               | 0.287 (8 architectures converge here)      |
| TCN params              | 22,914                                     |
| TCN features            | 12 (7 PAC + 5 stim context)                |
| Lookback                | 20 steps (20 seconds)                      |
| Dilations               | [1, 2, 4, 8] -> 31-step receptive field    |
| TCN R2 (5s, 5-seed)     | 0.606 +/- 0.032                            |
| Persistence R2 (5s)     | 0.104                                      |
| Alignment               | 72.1% (TCN) vs 64.5% (Reactive)            |
| Low-PAC targeting       | 82.6% vs 51.7%                             |
| Effect size (alignment) | g = 1.31, p < 0.001                        |
| Effect size (low-PAC)   | g = 4.47, p < 0.001                        |
| Oracle proximity        | 91% of theoretical max                     |
| Subjects benefiting     | 35/35 (binomial p < 0.001)                 |
| Inference time          | < 50 ms                                    |
| Hardware cost           | ~ $250 (Muse 2 + headphones)               |

---

## 1. MOTIVATION & BACKGROUND

**Q1. "Why did you choose this project?"**
I read Iaccarino's 2016 Nature paper showing 40 Hz stimulation reduced amyloid by 50% in mice and got interested. But when I looked at the clinical protocols, every single one uses a fixed schedule -- same timing for every patient. That seemed like a solvable problem. About half of patients habituate within minutes, and a fixed schedule can't adapt. Nobody was trying to predict that ahead of time.

**Q2. "What's the personal connection?"**
My grandmother had dementia. Watching someone you love lose the ability to recognize you changes how you think about the disease. It's not abstract for me.

**Q3. "Walk me through your timeline."**
Started early 2026. First month: literature review and getting familiar with the dataset. Then I built preprocessing and PAC computation. Spent three weeks testing eight architectures -- they all hit the same ceiling. That was the turning point. I pivoted to temporal forecasting, engineered the 12 features, trained the TCN, did the horizon sweep, built the controller, ran the 35-subject validation. After the project presentation deadline, I did the feature ablation study that raised R2 from near zero to 0.60.

**Q4. "What help did you receive?"**
My AP Statistics teacher was consulted on choosing appropriate non-parametric tests. Everything else -- literature review, code, pipeline design, feature engineering, architecture decisions -- I did independently. I used open-source libraries: PyTorch, MNE-Python, SciPy, NumPy. Computing was my personal MacBook and an RTX 3080. No university lab, no mentor, no summer program.

**Q5. "Is this a continuation of a previous project?"**
No. Entirely new work this year.

**Q6. "How did you come up with the idea for predicting ahead instead of just reacting?"**
The 8-architecture search. When I saw that every model -- from 1,500 to 1.1 million parameters -- converged to R2 of 0.287, I knew the information ceiling was in the data, not the model. A 2-second snapshot just doesn't contain enough. That forced me to think about what information you get from sequences that you don't get from snapshots: trajectories, trends, momentum. That's what temporal prediction captures.

**Q7. "How much of the work did you do this year vs. reusing prior work?"**
All of it is this year. The dataset is publicly available, and the libraries are open-source, but every line of analysis code, every design decision, and every experiment is from the past four months.

---

## 2. SCIENTIFIC FOUNDATION

**Q8. "What is phase-amplitude coupling?"**
It measures how coordinated two brain rhythms are. The brain has a slow theta rhythm at 4-8 Hz and a fast gamma rhythm at 40 Hz. When the therapy is working, gamma amplitude becomes tightly locked to the phase of theta -- they move in sync. PAC quantifies how tight that lock is. I compute it with Tort's Modulation Index, which uses KL divergence across 18 phase bins. Flat distribution means no coupling. Peaked means strong coupling. [Point to Figure 1]

**Q9. "What are gamma oscillations and why do they matter for Alzheimer's?"**
Gamma oscillations are fast brain rhythms around 30-100 Hz, with 40 Hz being particularly important. In healthy brains, gamma supports attention, sensory processing, and memory consolidation. In Alzheimer's patients, gamma power is reduced and gamma-theta coupling is disrupted. Restoring 40 Hz activity through external stimulation appears to reactivate the brain's immune and clearance systems.

**Q10. "How does 40 Hz stimulation actually clear amyloid?"**
Two known pathways. First, Iaccarino 2016 showed microglial activation -- 40 Hz drives microglia to engulf amyloid. Second, Murdock 2024 showed glymphatic clearance: 40 Hz neural activity drives arterial pulsation through VIP interneurons, which increases cerebrospinal fluid flow through aquaporin-4 channels on astrocytic endfeet, physically flushing amyloid into the drainage system. When they blocked glymphatic clearance pharmacologically, the amyloid reduction disappeared. So glymphatic flow is necessary, not just correlated.

**Q11. "What evidence exists that this works in humans?"**
Still early. Chan et al. 2025 showed 2-year safety and slower cognitive decline in 3 of 5 patients. Cognito's Phase 2 showed preserved white matter integrity. Lahijanian 2024 showed enhanced default mode network connectivity. But Phase 3 efficacy data doesn't exist yet. I'm careful not to claim 40 Hz cures Alzheimer's -- I claim adaptive delivery outperforms fixed delivery for whatever protocol is used.

**Q12. "What's the difference between auditory and visual 40 Hz stimulation?"**
The original Iaccarino paper used visual flicker. Auditory came later and engages different cortical pathways -- primarily auditory cortex and temporal regions rather than visual cortex. The Lahijanian dataset I used is auditory. The Soula 2023 critique about SSVEPs versus endogenous gamma applies primarily to visual flicker. Auditory may produce more robust entrainment through different mechanisms, but the field is still sorting this out. My system is agnostic -- it monitors PAC regardless of stimulation modality.

**Q13. "What about the Soula critique -- that this is just an SSVEP, not real entrainment?"**
Important paper. Soula showed in Nature Neuroscience that 40 Hz visual flicker drives a steady-state evoked potential rather than entraining endogenous gamma. Two responses: first, my dataset uses auditory, not visual stimulation -- different cortical pathways. Second, my controller doesn't depend on which mechanism is correct. Whether the benefit comes from genuine entrainment, SSVEPs, glymphatic clearance, or some combination, the controller optimizes delivery timing based on a measurable biomarker. If PAC tracks therapeutic effect -- and the Lahijanian data suggests it does -- optimizing PAC is valuable regardless of the mechanistic debate.

---

## 3. METHODOLOGY

**Q14. "Why a TCN and not an LSTM or Transformer?"**
Three reasons. First, causality is architectural -- dilated convolutions with causal padding physically cannot see future time steps. With an LSTM, causality depends on correct hidden state management, which is easier to violate accidentally. Second, TCNs process the full sequence in parallel, important for real-time inference. Third, with 17,000 windows and length-20 sequences, I don't have enough data for self-attention. I tested this -- TCN outperformed the alternatives.

**Q15. "What are the 12 features?"**
Current PAC value, causal moving averages at 2, 4, 8, and 16 windows, first-order and 4-step differences, stimulation state (binary), time since last state switch normalized to 60 seconds, stimulation fraction over the past 20 seconds, and cycle phase encoded as sine and cosine. All strictly causal.

**Q16. "Why 20 seconds of lookback?"**
The stimulation protocol uses 20-40 second stimulus blocks and 20 second rest blocks. A 20-step lookback at 1-second resolution captures approximately one full stim-rest cycle, which contains the trajectory information the model needs. The TCN's dilations of 1, 2, 4, 8 give an effective receptive field of 31 steps -- covering more than one full cycle. Shorter lookbacks miss the trajectory; longer lookbacks didn't improve performance.

**Q17. "Why did you choose this specific dataset?"**
OpenNeuro ds005048 was the only publicly available EEG dataset I found that had (a) 40 Hz auditory stimulation, (b) alternating stimulus and rest blocks, (c) multiple sessions per protocol, and (d) enough subjects for meaningful train/val/test splits. Lahijanian et al. published it in Scientific Reports in 2024 with 35 elderly subjects including Alzheimer's, MCI, and healthy controls.

**Q18. "How did you preprocess the EEG data?"**
The data was already partially preprocessed by the authors -- 1 Hz highpass, 50 Hz notch, ICA, and common average reference. I applied additional light filtering: bandpass 0.5-80 Hz, notch at 50 Hz, and artifact zeroing where any sample exceeds 100 microvolts. Then I segmented into 2-second windows at 1-second hop. [Point to Figure 4]

**Q19. "What does 'causal' mean in this context?"**
The model can only use information from the past and present to make predictions about the future. Every convolution uses left-only padding so the computation at time T only depends on time T and earlier. This is an architectural constraint built into the network design, not a training procedure that could accidentally leak. In a real-time system, you don't have access to future data, so the model has to work the same way.

**Q20. "Why Huber loss instead of MSE?"**
Huber loss is less sensitive to outliers than MSE. PAC values have a right-skewed distribution with occasional extreme values. MSE would overweight those outliers and destabilize training. Huber loss acts like MSE for small errors and like MAE for large errors, giving more stable gradients.

---

## 4. RESULTS & VALIDATION

**Q21. "Your R-squared is 0.606. Is that good?"**
Context is everything. At 5-second horizons, persistence gives 0.104 and Ridge gives similar. Both go negative at 8-10 seconds -- worse than guessing the mean. My model holds at 0.37-0.67 across 3-10 seconds. The 0.606 is the 5-seed mean at 5 seconds, range 0.558-0.647. More importantly, the controller built on these predictions improved alignment from 64.5% to 72.1% with a large effect size. The predictions are useful.

**Q22. "72% alignment -- 28% of decisions are wrong. Is that acceptable?"**
The oracle with perfect future knowledge gets 100%. My system reaches 91% of the oracle's PAC targeting gap. The 28% suboptimal decisions are concentrated at boundaries between high and low PAC states, where the correct action is ambiguous even in hindsight. The comparison that matters: fixed schedule gets 45%, reactive gets 64.5%. Every point of improvement means more stimulation reaching moments when the brain actually needs it. [Point to Result 1 table]

**Q23. "All 35 subjects benefited. Doesn't that seem too good?"**
I was surprised too. Binomial probability is less than 0.001. But it makes sense -- the predictive controller has strictly more information than reactive. It sees everything reactive sees plus a 5-second forecast. A subject would only fail to benefit if the TCN's predictions actively misled the controller worse than random, and the forecaster is well above chance. But the magnitude varies -- some improved by 15 points, others by 2-3. The scatter shows the spread. [Point to Result 2]

**Q24. "How did you validate?"**
Offline counterfactual replay on all 35 subjects. Real EEG goes through preprocessing, PAC estimation, feature extraction, TCN forecasting, and controller decisions. I compare what the controller would have decided at each time step against the ground-truth optimal action. I used ground-truth PAC as TCN input to isolate forecaster contribution from EEGNet error. Statistics: Wilcoxon signed-rank (non-parametric, paired), Hedges' g effect sizes, 95% BCa bootstrap CIs from 10,000 iterations.

**Q25. "Explain the six controllers you compared."**
Fixed schedule: 40 on, 20 off, blind. Reactive: responds to current PAC only, no prediction. TCN Predictive: my system, uses 5-second forecast. Hybrid: blends TCN prediction with reactive feedback. PI Controller: proportional-integral, classic control theory. Oracle: has perfect hindsight, upper bound. Fixed is actually worse than random -- negative PAC gap. Reactive is decent. TCN beats everything except oracle. [Point to Result 1]

---

## 5. STATISTICAL RIGOR

**Q26. "Why Hedges' g instead of Cohen's d?"**
Hedges' g applies a small-sample correction factor. With 35 paired observations, Cohen's d slightly overestimates effect size. The correction is small at N=35 but it's the appropriate choice. Shows I'm not inflating results.

**Q27. "Why Wilcoxon signed-rank instead of a paired t-test?"**
Two reasons. With 35 subjects, I can't reliably verify normality of difference scores, and PAC distributions are right-skewed. Wilcoxon is rank-based, robust to outliers and non-normality. For this sample size, it has nearly the same power as a t-test when normality holds, and much better power when it doesn't.

**Q28. "Did you correct for multiple comparisons?"**
Alignment is my primary outcome. Low-PAC targeting and PAC gap are secondary metrics that decompose alignment into interpretable components. I report all three for transparency, not because I fished across many metrics. Even with Bonferroni correction dividing alpha by 3, every result stays significant at p < 0.003.

**Q29. "The horizon sweep uses one seed. How reliable is that?"**
The full sweep at horizons 1-10 uses seed 42 only. At the primary 5-second horizon, I ran 5 seeds: mean 0.606, std 0.032, range 0.558-0.647. The qualitative story -- persistence collapses above 3 seconds, TCN holds -- wouldn't change with different seeds because the inflection point reflects the PAC autocorrelation timescale, not random initialization.

---

## 6. LIMITATIONS & HONESTY

**Q30. "What's the weakest part of your project?"**
The validation is offline replay, not live closed-loop. I measure the quality of decisions, not whether those decisions change patient outcomes. In a live system, stimulation changes neural state, which feeds back to the model -- that loop doesn't exist in replay. The gap between "makes good decisions on recorded data" and "improves outcomes in real time" is the most important one to close.

**Q31. "What would you do differently if you started over?"**
Start with the feature ablation study on day one. I spent three weeks testing eight architectures that all converge to the same ceiling. If I'd started with feature representation instead of model architecture, I'd have saved weeks. I'd also design a longer recording protocol -- 60-minute sessions instead of 10-minute cycles -- to capture the full habituation arc.

**Q32. "What would disprove your approach?"**
If a real-time pilot showed that stimulation decisions based on 5-second forecasts don't actually change entrainment outcomes -- meaning the feedback loop renders predictions obsolete. Or if a simple reactive controller with very short latency (under 500 ms) matched the predictive controller's performance -- that would mean prediction is unnecessary when reaction is fast enough.

**Q33. "What's the most important thing you don't know?"**
Whether the relationship between PAC and therapeutic outcome holds in real-time closed-loop. In replay, I'm correlating controller decisions with ground-truth PAC. In a live system, the controller's decisions change the neural state. The dynamics might be different. That's the key unknown.

---

## 7. CLINICAL TRANSLATION

**Q34. "How would you design the first clinical trial?"**
A randomized crossover study. Same patients receive both fixed-schedule and adaptive stimulation on different days. Primary endpoint: mean theta-gamma PAC during sessions. Secondary: cognitive testing before and after. Stratify by diagnosis (AD vs. MCI vs. HC) and APOE genotype. Record 60-minute sessions to capture the full habituation trajectory.

**Q35. "What's the regulatory pathway?"**
If marketed as a wellness device -- "supports brain fitness" -- it might fall under FDA general wellness guidance, no clearance needed. For a disease treatment claim, most likely De Novo classification, which is what Cognito is pursuing. The path: IRB-approved observational pilot first, then feasibility study comparing adaptive vs. fixed, then regulatory submission with that data.

**Q36. "How much would the full system cost?"**
Under $250 per patient. Muse 2 headset at about $200, standard headphones, and the controller runs as a web application on any laptop or smartphone. No clinical-grade hardware required. That's what makes home deployment realistic.

**Q37. "Who would use this?"**
Three audiences. Cognito and other 40 Hz therapy companies -- the adaptive controller is device-agnostic and could improve their fixed-schedule protocols. Memory care facilities -- the $250 cost makes it accessible for nursing homes. And eventually home caregivers -- the system doesn't require a clinician to operate.

---

## 8. COMPETITIVE LANDSCAPE

**Q38. "How does this compare to Cognito Therapeutics?"**
Cognito is the furthest along -- Breakthrough Device Designation, $105 million raised in March 2026, 670-patient Phase 3 HOPE trial. Their Spectris device delivers combined audiovisual 40 Hz, one hour daily. But they use a fixed schedule. My system is complementary -- it's the intelligence layer that makes their therapy adaptive. Instead of one hour of continuous stimulation, an adaptive system concentrates delivery on the moments when the brain needs it.

**Q39. "What about the MIT Tsai Lab?"**
The Tsai Lab did the original Iaccarino work and continues to lead basic science research. Their protocols are lab-based, not deployable. My system runs on consumer hardware. Different contribution -- they establish the mechanism, I build the delivery optimization.

**Q40. "Why hasn't anyone done this before?"**
Two reasons I can see. First, the computational neuroscience and clinical neurostimulation communities don't overlap much -- the ML tools existed but weren't being applied to this specific problem. Second, the Lahijanian dataset that makes this possible was only published in 2024. Before that, there wasn't a publicly available EEG dataset with 40 Hz auditory stimulation and enough subjects for ML.

---

## 9. FUTURE DIRECTIONS

**Q41. "What's the next experiment?"**
Live crossover study. Same patients, both fixed and adaptive, different days. Measuring real-time PAC and cognitive outcomes. This closes the offline-to-online gap.

**Q42. "Could this work for other conditions?"**
The closed-loop principle applies to any brain stimulation where the response is variable. Closed-loop DBS for Parkinson's uses beta power instead of PAC but the same predictive control concept. The architecture is modular -- swap the biomarker and the stimulation parameters.

**Q43. "What about combined audiovisual stimulation?"**
Cognito uses audiovisual and sees strong results. My dataset is audio-only. Adding visual would likely strengthen entrainment. The controller framework doesn't change -- PAC is still the biomarker, only the stimulus modality differs.

**Q44. "How would you handle patients who don't respond at all?"**
Fortunato et al. found about 30% are non-responders. An adaptive system detects non-response faster than a fixed schedule because it's monitoring PAC continuously. If PAC doesn't rise after several stimulation attempts, the system could flag that patient for alternative treatment. Better than discovering non-response after weeks of fixed-schedule therapy.

---

## 10. PROCESS & META

**Q45. "How long did this take?"**
About four months of focused work, starting early 2026.

**Q46. "Did you use AI tools?"**
Yes -- Claude and ChatGPT for debugging, boilerplate code, and exploring implementation options. All documented per ISEF rules. The research questions, experiment design, feature engineering, architecture decisions, and result interpretation were my work. The most important decisions -- the 0.287 ceiling realization, the temporal pivot, the spectral feature discovery -- came from analyzing my own results.

**Q47. "What was your biggest failure?"**
The 8-architecture search. Three weeks convinced that a better model would solve the problem. Every one converged to 0.287. It felt like wasted time. But that convergence was itself the most important finding -- it proved the bottleneck was features, not model capacity. The failure was the turning point.

**Q48. "What was the most surprising finding?"**
That removing 61 features improved performance five-fold. Counter-intuitive -- more information should help, not hurt. But those features were encoding the wrong thing. Subject identity instead of transferable dynamics.

**Q49. "What's the single most important decision you made?"**
Dropping the spectral features. Everything before that was stuck at 0.287 or worse. Everything after it worked.

---

## 11. FUNDAMENTAL CONCEPTS (for non-technical judges)

**Q50. "Explain your project to me like I know nothing about neuroscience."**
Alzheimer's patients lose brain cells partly because of a toxic protein called amyloid. Scientists found that playing a 40 Hz tone -- a low hum -- triggers the brain to clean up that protein. Think of it like vibrating a dirty filter to shake debris loose. But every patient responds differently, and some brains tune it out after a few minutes, like how you stop noticing background music. My system reads brainwaves and predicts when a patient is about to tune out, five seconds before it happens. When the brain is fading, we play the tone. When it's responding well, we rest. On 35 patients' brain recordings, this caught the right moments 83% of the time versus 52% for a system that only reacts.

**Q51. "What is EEG?"**
Electroencephalography -- electrodes on the scalp that measure the brain's electrical activity. Like a heart monitor, but for the brain. It picks up oscillations at different frequencies that correspond to different brain states.

**Q52. "What is machine learning, in this context?"**
I'm training a mathematical model to find patterns in brain data that predict what happens next. I show it thousands of examples of "here's what the brain looked like for the last 20 seconds" paired with "here's what happened 5 seconds later." It learns the relationship. Then on new patients it hasn't seen, it makes predictions based on those learned patterns.

**Q53. "What does 'closed-loop' mean?"**
The therapy adjusts based on what the brain is doing, rather than following a preset timer. Open-loop: play sound for 40 seconds, rest for 20, repeat. Closed-loop: read the brain, predict what it needs, deliver accordingly. Like a thermostat versus a space heater on a timer.

---

## 12. ADDITIONAL LIKELY QUESTIONS

**Q54. "Why 7 frontal channels?"**
Frontal regions show the strongest 40 Hz entrainment response. I used Fp1, Fp2, F7, F3, Fz, F4, F8. These are also the channels most accessible to consumer EEG headsets like the Muse 2, which supports real-world deployment.

**Q55. "What's the PAC label range?"**
Modulation Index values range from about 0.000006 to 0.000701, mean approximately 0.000044. These are dimensionless, and the absolute values depend on the computation method. What matters is the relative change over time.

**Q56. "Why not just measure gamma power directly instead of PAC?"**
Gamma power alone can increase from the stimulus without the brain actually entraining -- it could just be a steady-state evoked potential. PAC captures the coordination between gamma and theta, which is more specifically tied to the entrainment mechanism. It's a more informative biomarker.

**Q57. "How does the personalization module work?"**
It maintains a 30-second rolling baseline of PAC values for each subject and converts current predictions to z-scores -- how many standard deviations from that patient's recent average. This makes the system self-calibrating. A z below -0.5 triggers stimulation. Above +0.5 triggers rest. There's a 5-second hysteresis to prevent rapid oscillation between states.

**Q58. "What computing resources did you use?"**
Personal MacBook with Apple Silicon for data processing and analysis. Personal NVIDIA RTX 3080 for training. No cloud GPUs, no university computing clusters.

**Q59. "How fast is the inference?"**
Under 50 milliseconds per prediction on a laptop. Well within real-time requirements -- the brain state changes on a timescale of seconds, so 50 ms latency is negligible.

**Q60. "Could someone replicate your results?"**
Yes. The dataset is public on OpenNeuro (ds005048). My code is on GitHub. The preprocessing, feature engineering, model architecture, and training procedure are all documented. I used deterministic seeding for reproducibility. Anyone could run this.

**Q61. "What happens between interviews?"**
I'll be at my display. If you have follow-up questions or want to see the live demo, I'm happy to show you.

**Q62. "Do you have any questions for me?"**
[Always have one ready.] I'd be curious -- in your experience, what's the biggest barrier to translating computational neuroscience into clinical practice? / What would you want to see in a first clinical pilot of this kind of system?
