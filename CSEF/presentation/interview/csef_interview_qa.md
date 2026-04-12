# CSEF 2026 Interview Preparation: Q&A Guide

**Project:** Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease

**Format reminder:** Judges have already read your 13-page presentation and abstract. They arrive with questions ready. Your opening summary should be 60 seconds max, then it becomes a conversation. Do not recite your poster — tell them what is not obvious from reading it.

---

## Your 60-Second Opening

> Alzheimer's affects 55 million people, and one of the most promising non-drug therapies is 40 Hz auditory stimulation — it drives gamma rhythms that help clear toxic amyloid plaques. But every clinical protocol delivers it on a fixed schedule, and about 30% of patients stop responding within minutes. I built a system that predicts when a patient's brain will lose entrainment five seconds before it happens, so stimulation can be timed to the moments it is actually needed.
>
> I used EEG from 35 dementia patients and trained a causal temporal convolutional network to forecast phase-amplitude coupling — the biomarker that measures whether the therapy is working. At five-to-ten-second horizons, every baseline collapses, but my model maintains R-squared of 0.60. When I plugged it into a closed-loop controller and replayed all 35 patients' recordings, it matched stimulation to need 72% of the time versus 64% for reactive control, and every single patient benefited.

Prepare 1-minute, 3-minute, and 5-minute versions. If a judge interrupts at 20 seconds with a question, stop and answer — that is a conversation, not a failure.

---

## TIER 1: THE WARM-UPS

These come first. Nail them cleanly and you set the tone.

---

### Q1. "Why did you choose this project?"

I read the Iaccarino 2016 Nature paper showing that 40 Hz stimulation reduced amyloid by 50% in mice, and I got excited about it as a potential therapy. But when I looked at the human clinical work, I noticed every protocol uses a fixed schedule — 40 seconds on, 20 seconds off, same for everyone. That struck me as a solvable engineering problem. Some patients habituate in minutes, others maintain entrainment for the whole session, and a fixed schedule serves neither group well. Fortunato et al. found about 30% are non-responders entirely. I wanted to see if predicting when a patient's brain is about to lose entrainment could make the therapy actually adaptive.

---

### Q2. "Walk me through your project timeline."

I started in early 2026. First month was literature review and getting familiar with the OpenNeuro EEG dataset. Then I built the preprocessing pipeline and PAC computation. I spent about three weeks on an architecture search — I tested eight different neural networks for static PAC prediction from EEG snapshots, and they all hit the same ceiling at R-squared 0.287. That was actually the turning point, because it told me the bottleneck was the feature representation, not the model. I pivoted to temporal forecasting, engineered the 12 PAC-trajectory features, trained the TCN, did the horizon sweep, and built the closed-loop controller. The last phase was the full 35-subject validation with all the statistical analysis.

---

### Q3. "What help did you receive?"

My AP Statistics teacher was consulted on the statistical analysis — specifically on choosing appropriate non-parametric tests for paired data. Everything else — the literature review, the code, the pipeline design, the feature engineering, the architecture decisions — I did independently. I used publicly available open-source libraries: PyTorch, MNE-Python, SciPy, NumPy. No university lab, no mentor, no summer program. My computing was my personal MacBook and a personal RTX 3080. The dataset is publicly available on OpenNeuro.

---

### Q4. "Is this a continuation of a previous project?"

No. This is entirely new work that I started this year. The concept came from my own literature review.

---

### Q5. "Describe your dataset."

OpenNeuro ds005048, published by Lahijanian et al. in Scientific Reports, 2024. Thirty-five elderly subjects — 17 with Alzheimer's, 6 with MCI, 10 healthy controls, and 2 unspecified. Seven frontal EEG channels sampled at 250 Hz. The protocol was 40 Hz auditory stimulation in cycles: 40 seconds on, 20 seconds off. I split by subject — 24 for training, 5 for validation, 6 for test — with zero overlap. The test subjects were never seen during training or hyperparameter selection.

---

## TIER 2: THE METHODOLOGY DEEP-DIVES

Judges will probe your technical understanding. They want to know you made deliberate choices.

---

### Q6. "What is phase-amplitude coupling, and why did you use it?"

PAC measures whether the brain's fast oscillations are synchronized with its slow oscillations — specifically, whether gamma amplitude at 38-42 Hz is locked to the phase of the theta rhythm at 4-8 Hz. I compute it using the Modulation Index from Tort et al. 2010, which uses KL divergence across 18 phase bins to quantify how non-uniform the amplitude distribution is. A flat distribution means no coupling, a peaked distribution means strong coupling.

I chose it because theta-gamma PAC is directly tied to the mechanism of entrainment. When 40 Hz stimulation is working, gamma amplitude becomes phase-locked to theta. When entrainment weakens, that coupling breaks down. It is both a biomarker of therapeutic effect and a signal the controller can act on. Lahijanian et al. used it as their primary coupling measure in the same dataset, so it is well-validated for this population.

---

### Q7. "Why a TCN instead of an LSTM or Transformer?"

Three reasons. First, a TCN is architecturally causal — the dilated convolutions with causal padding physically cannot access future time steps. With an LSTM, causality depends on correct implementation of hidden states, which is easier to accidentally violate. Second, TCNs process the full sequence in parallel, which matters for real-time inference — my system runs under 50 milliseconds per prediction. Third, with 17,000 training windows and a 20-step lookback, I do not have enough data for self-attention. Transformers are O(n-squared) in sequence length and need substantially more data to avoid overfitting on short sequences. I tested this — the TCN outperforms the alternatives I tried.

---

### Q8. "Explain the feature engineering. Why 12 features instead of 73?"

This was one of the most important findings. I originally used 73 features — 61 spectral power features across the 7 channels plus 12 PAC-derived and stimulation context features. The test R-squared was negative 0.025. When I dropped all 61 spectral features and kept only the 12 PAC-trajectory and stimulation context features, R-squared jumped to 0.558 on a single seed, and the 5-seed mean is 0.606.

The spectral features were encoding subject-specific EEG characteristics — individual anatomy, recording conditions, electrode impedance. They let the model identify which subject it was looking at and memorize that subject's patterns, which does not generalize. The val-test gap shrank from 0.358 to 0.246 when I removed them. The 12 surviving features are: current PAC value, causal moving averages at 2, 4, 8, and 16 windows, first-order and 4-step differences, stimulation state, time since last switch, stimulation fraction over 20 seconds, and cycle phase encoded as sine and cosine. All strictly causal.

---

### Q9. "What are the 8 architectures you tested, and why did they all hit R-squared 0.287?"

I tested EEGNet, a deeper CNN, a ResNet-style model, an attention-based architecture, and several variants with different filter counts, up to 1.1 million parameters. Every single one converged to approximately R-squared 0.287 on the test set. That was the ceiling for static PAC prediction from 2-second EEG snapshots.

The reason is that PAC is computed at the epoch level — full 20-to-40-second blocks — and then assigned to all constituent 2-second windows within each epoch. So every window in the same epoch shares the same PAC label, but the EEG content varies window to window. A 2-second snapshot does not contain enough information to perfectly reconstruct the epoch-level coupling. The bottleneck was the data representation, not model capacity. That finding is what redirected me toward temporal forecasting, where sequences of PAC values over 20 seconds contain the trajectory information needed for prediction.

---

### Q10. "Explain your closed-loop controller."

The controller has three components. First, a personalization module that maintains a 30-second rolling baseline of PAC values for each subject and converts the current prediction to a z-score — how many standard deviations from that patient's recent average. This makes the system self-calibrating to each patient.

Second, a decision rule: if z is below negative 0.5, the brain is losing entrainment and we stimulate. If z is above positive 0.5, entrainment is strong and we rest. Otherwise, we maintain the current state.

Third, a 5-second hysteresis to prevent rapid oscillation between states. The system cannot switch from stimulate to rest or vice versa more than once every 5 seconds, which prevents unstable flickering behavior.

I compared six variants: Fixed Schedule, Reactive Threshold (responds to current PAC only, no prediction), TCN Predictive (my system), Hybrid, PI Controller, and an Alignment Oracle that has perfect hindsight. The TCN Predictive outperformed everything except the oracle.

---

### Q11. "How did you validate the system?"

Offline counterfactual replay on all 35 subjects' recorded EEG. I feed the real recorded EEG through the pipeline — preprocessing, EEGNet PAC estimation, feature extraction, TCN forecasting, controller decision — and evaluate what the controller would have decided at each time step. I compare the controller's decisions against the ground-truth PAC labels.

I used ground-truth PAC labels as TCN input rather than EEGNet estimates, specifically to isolate the forecaster's contribution from EEGNet estimation error. The metrics are: Alignment (percentage of time the controller's decision matches the optimal action), Low-PAC Stim Rate (percentage of low-coupling windows that received stimulation), and PAC Targeting Gap (difference in mean PAC during rest versus stimulation). Statistics are Wilcoxon signed-rank tests with Hedges' g effect sizes and 95% BCa bootstrap confidence intervals from 10,000 iterations.

---

### Q12. "Why Hedges' g instead of Cohen's d?"

Hedges' g applies a small-sample correction factor. With 35 paired observations, Cohen's d would slightly overestimate the effect size. The correction is small at this sample size but it is the appropriate choice, and it shows I am not inflating my results.

---

### Q13. "Why Wilcoxon signed-rank instead of a paired t-test?"

Two reasons. First, with 35 subjects, I cannot reliably verify normality of the difference scores, and the PAC distributions are right-skewed. Second, Wilcoxon is a rank-based test that is robust to outliers and non-normal distributions. It is the standard choice for paired comparisons when you cannot assume normality. For this sample size, it has nearly the same power as a t-test when normality holds, and much better power when it does not.

---

## TIER 3: THE RESULTS CHALLENGES

Judges will push on whether your numbers mean what you say they mean.

---

### Q14. "Your R-squared is 0.606. Is that good?"

It depends on the context, and that is exactly why I report baselines. At 5-second horizons, persistence — just predicting that PAC will stay the same — gives R-squared of 0.104. Ridge regression gives similar. Both collapse to negative values at 8-10 seconds. My model maintains R-squared of 0.37 to 0.67 across that entire 3-to-10-second range. The 0.606 is the 5-seed mean at the 5-second horizon, with a range of 0.558 to 0.647.

What matters clinically is not the R-squared in isolation but whether the predictions are accurate enough to improve controller decisions. The answer is yes — the controller built on these predictions achieved 72.1% alignment versus 64.5% for reactive control, a statistically significant improvement with a large effect size.

---

### Q15. "72% alignment — 28% of decisions are wrong. Is that acceptable?"

The oracle — which has perfect knowledge of future PAC — only achieves around 100% alignment because it can see ahead perfectly. My system reaches 91% of the oracle's PAC targeting gap. The 28% suboptimal decisions are distributed roughly evenly between false stimulation and missed stimulation, and they are concentrated at the boundaries between high and low coupling states, where the correct action is ambiguous even in hindsight.

The relevant comparison is not perfection but the alternative. Fixed schedule gets 45% alignment. Reactive gets 64.5%. Every percentage point of improvement means more stimulation is reaching moments when the brain actually needs it. And the Hybrid controller that combines prediction with reactive feedback reaches 74.4%, suggesting there is still room to improve.

---

### Q16. "All 35 subjects benefited. Does that seem too good?"

It is a strong result, and I was surprised by it too — the binomial probability of 35/35 by chance is less than 0.001. But I think it makes sense when you look at why. The predictive controller has a structural advantage: it has all the information the reactive controller has, plus a 5-second forecast. It is strictly more informed. A subject would only fail to benefit if the TCN's predictions actively misled the controller worse than random, and the forecaster is substantially above chance at every horizon from 3 to 10 seconds.

That said, the magnitude of benefit varies considerably across subjects. Some subjects improved their alignment by 15 percentage points, others by only 2-3. The scatter plot in Figure 4 shows this spread. The claim is that all 35 benefited, not that all 35 benefited equally.

---

### Q17. "You tested on 6 subjects. Is that enough?"

Six held-out test subjects is a small test set, and I am transparent about that. That is why I also report the result on all 35 subjects — including training and validation subjects — and show that the advantage is consistent across all three splits. The per-subject scatter plot shows no systematic difference between train, validation, and test subjects.

If the model were overfitting to training subjects, you would see a cluster of training dots above the diagonal and test dots on or below it. Instead, the test subjects are interleaved with the rest. But yes, a larger multi-site dataset is a clear next step, and I list it as a limitation.

---

### Q18. "You report multiple metrics. Did you correct for multiple comparisons?"

My primary outcome is Alignment — that is the single metric I designed the controller to optimize. Low-PAC Stim Rate and PAC Targeting Gap are secondary metrics that decompose alignment into interpretable components. I report all three for transparency, not because I went fishing across many metrics. All three show significant effects with large effect sizes, so even with a Bonferroni correction dividing alpha by 3, every result remains significant at p < 0.003.

---

### Q19. "The horizon sweep is single-seed. How reliable is that?"

Fair point. The sweep at horizons 1 through 10 uses seed 42 only. The 5-seed validation at the 5-second horizon shows a standard deviation of 0.032, suggesting the single-seed results are representative but could shift by a few hundredths. The qualitative story — persistence collapses above 3 seconds while the TCN maintains meaningful R-squared — would not change with different seeds, because the inflection point reflects the PAC autocorrelation timescale, not random initialization.

Ideally, I would run 5 seeds at every horizon. I ran it at the primary horizon to keep compute reasonable and to establish reproducibility where it matters most.

---

### Q20. "Could your results be explained by something other than the TCN's predictive ability?"

The main alternative explanation would be that the controller improvements come from the personalization module rather than the TCN. But the reactive controller uses the same personalization module — same rolling baseline, same z-score thresholds, same hysteresis. The only difference is that reactive uses the current PAC estimate while predictive uses the 5-second-ahead forecast. So any improvement is attributable to the prediction.

Another concern would be data leakage. I verified this explicitly: subject-level splits with no within-subject overlap, causal features with no future information, and z-score normalization fit on training data only. I run an automated leakage audit before every training run.

---

## TIER 4: THE HARD QUESTIONS

These separate a good project from an ISEF-winning project.

---

### Q21. "What is the weakest part of your project?"

The validation is offline counterfactual replay, not real-time closed-loop control. I am measuring the quality of the decisions the system would make, not whether those decisions actually change brain dynamics in a live patient. In a real closed-loop system, the stimulation itself changes the neural state, which feeds back into the model — and that feedback loop does not exist in replay. The transition from "this controller makes good decisions on recorded data" to "this controller improves patient outcomes in real time" is the most important gap.

---

### Q22. "What would you do differently if you started over?"

The biggest thing I learned is that data representation matters more than model architecture. I spent three weeks testing eight neural networks that all converged to the same ceiling. If I started over, I would begin with the feature ablation study on day one. I would also design a longer recording protocol — 60-minute sessions instead of 10-minute cycles — to capture the full habituation arc. The dataset has subjects who habituate in minutes and subjects who maintain entrainment throughout, but I cannot see what happens beyond 10 minutes. That trajectory information would make the forecaster significantly better at predicting long-term dynamics.

---

### Q23. "What would disprove your approach?"

If a real-time pilot showed that stimulation decisions based on 5-second-ahead PAC predictions do not actually change entrainment outcomes — meaning the feedback loop renders the predictions obsolete — that would challenge the core assumption. Another falsifier: if a simple reactive controller with a very short response latency (under 500 milliseconds) matched the predictive controller's performance, it would mean the prediction horizon is unnecessary and reactive control is sufficient when latency is low enough.

---

### Q24. "Your dataset is from one clinic in Tehran. How do you know this generalizes?"

It is a real limitation. Single-site data means the recording conditions, electrode placement, stimulation equipment, and patient demographics are all fixed. My model could be learning site-specific artifacts rather than universal PAC dynamics.

Two things give me some confidence. First, the subject-level splits mean the 6 test subjects are genuinely new to the model — they are not the same patients recorded on a different day. Second, the 12 PAC-trajectory features I selected are biologically motivated and invariant to recording setup — they capture the shape of the PAC timecourse, not absolute power levels. The spectral features I removed were the ones encoding site-specific characteristics.

But the definitive test is multi-site replication, which is a clear next step.

---

### Q25. "What happens if the model fails in real time? What is the fail-safe?"

The fail-safe is the reactive controller. If the TCN's predictions become unreliable — say, due to electrode drift or unexpected neural dynamics — the system can fall back to reactive threshold control, which uses only the current PAC estimate and does not depend on the forecaster at all. Reactive control is worse than predictive, but it is always better than fixed schedule. The Hybrid controller in my comparison already demonstrates this principle — it blends prediction with reactive feedback.

In a clinical system, you would also want an artifact detection layer that flags when the EEG signal quality degrades below a threshold and automatically switches to conservative mode. That is standard practice in closed-loop DBS systems like Medtronic's adaptive DBS for Parkinson's.

---

### Q26. "How does your work compare to Cognito Therapeutics?"

Cognito is the most advanced company in 40 Hz therapy. They have FDA Breakthrough Device Designation, completed enrollment of a 670-patient Phase 3 trial, and raised $105 million in March 2026. Their Spectris device delivers combined audiovisual 40 Hz stimulation, one hour daily.

But Cognito uses a fixed-schedule protocol. My system is complementary — it is the intelligence layer that could make their therapy adaptive. Instead of one hour of continuous stimulation, an adaptive system would concentrate stimulation on the windows when the brain needs it and rest when entrainment is strong. That could reduce session length, reduce habituation, and improve outcomes. The controller is device-agnostic — it takes EEG input and outputs stimulation timing decisions. It does not care whether the stimulation is Cognito's audiovisual system or any other 40 Hz device.

---

### Q27. "What about the Soula et al. 2023 critique that 40 Hz flickering does not actually entrain native gamma?"

That is an important paper. Soula et al. showed in Nature Neuroscience that 40 Hz visual flicker drives a steady-state evoked potential rather than entraining endogenous gamma oscillations. That is a real distinction — the SSVEP is a different neurophysiological phenomenon.

My response is two-fold. First, auditory stimulation may behave differently from visual flicker — the dataset I used is auditory 40 Hz, not visual, and auditory gamma entrainment engages different cortical pathways. Second, my system does not depend on which downstream mechanism is correct. Whether the therapeutic benefit comes from genuine gamma entrainment, from SSVEPs, from glymphatic clearance, or from some combination, the controller optimizes the delivery timing based on a measurable biomarker. If PAC tracks therapeutic effect — and the Lahijanian data suggests it does — then optimizing PAC is valuable regardless of the mechanistic debate.

---

### Q28. "What is the mechanism — how does 40 Hz stimulation actually help?"

The current understanding involves at least two pathways. The original Iaccarino 2016 paper showed microglial activation — 40 Hz stimulation triggers microglia to engulf amyloid plaques. The Murdock 2024 Nature paper added a second mechanism: glymphatic clearance. Forty Hz neural activity drives arterial pulsatility through VIP interneurons, which increases cerebrospinal fluid flow through aquaporin-4 channels on astrocytic endfeet, physically flushing amyloid into the drainage system. Critically, when Murdock's group blocked glymphatic clearance pharmacologically, the amyloid-clearing effect disappeared — meaning glymphatic flow is necessary, not just correlated.

The human evidence is still early. Chan et al. 2025 showed 2-year safety and slower cognitive decline in 3 of 5 patients, and Cognito's Phase 2 showed preserved white matter. But Phase 3 efficacy data does not exist yet. I am careful not to claim this therapy cures Alzheimer's — what I claim is that adaptive delivery outperforms fixed delivery for any protocol that uses 40 Hz stimulation.

---

### Q29. "Explain your project to me like I know nothing about neuroscience."

Alzheimer's patients lose brain cells partly because of a toxic protein called amyloid that builds up in the brain. Scientists discovered that playing a 40 Hz tone — a low hum — triggers the brain to clean up that protein. Think of it like vibrating a dirty filter to shake the debris loose.

The problem is that every patient's brain responds differently, and the response changes during the session. Some patients' brains tune out the sound after a few minutes, like how you stop noticing background music. Current systems cannot detect this — they just keep playing the sound on a timer.

My system reads brainwaves in real time and predicts when a patient is about to tune out, five seconds before it happens. When the brain is about to lose its response, we play the tone. When the brain is responding well, we give it a rest. On 35 patients' brain recordings, this approach matched the right action to the right moment 72% of the time, compared to 64% for a system that can only react to what is happening now, not predict what is coming next.

---

### Q30. "What is the regulatory pathway to get this to patients?"

It depends on the claims. If the system is marketed as a wellness device — "supports brain fitness" — it could potentially fall under FDA general wellness guidance, which does not require clearance. The moment it claims to treat Alzheimer's or any disease, it becomes a medical device.

For a medical device claim, the most likely pathway is De Novo classification, which is what Cognito is pursuing with Breakthrough Device Designation. That requires clinical trial data demonstrating safety and efficacy. The realistic path is: first, an IRB-approved observational pilot where I collect real-time EEG during supervised sessions to validate that the system works in live patients, not just on recorded data. Then a small feasibility study — 5 to 10 patients — comparing adaptive versus fixed stimulation and measuring actual cognitive outcomes. That data would support a regulatory submission.

The hardware cost is under $250 per patient — a consumer EEG headset like the Muse 2 at around $200 paired with standard headphones. The adaptive controller runs as a web application on any computer. No clinical hardware is required, which makes it accessible for home use once validated.

---

## TIER 5: THE "GOTCHA" QUESTIONS

These test intellectual honesty and scientific maturity.

---

### Q31. "What was your biggest failure?"

The eight-architecture search. I spent three weeks convinced that a better neural network would solve the PAC prediction problem. I tried everything from 1,457 parameters to 1.1 million — EEGNet, deeper CNNs, ResNets, attention models. Every single one converged to R-squared 0.287. It was frustrating because I thought I was failing. But that convergence was itself the most important finding of the project — it proved the bottleneck was the features, not the model. Once I understood that, the feature ablation study took my R-squared from negative 0.025 to 0.606. The failure was the turning point.

---

### Q32. "What is the single most important decision you made?"

Dropping the 61 spectral features. Everything in the project before that decision was dead-ended at R-squared 0.287 or worse. Everything after it worked. The counterintuitive insight — that more features made the model worse because they were encoding subject identity rather than generalizable dynamics — was not in any paper I read. I found it through systematic ablation. A post-hoc comparison of 10 temporal architectures confirmed it: they all converge to R-squared 0.61-0.65 on the 12 features, and none exceeds R-squared 0.28 on 73 features.

---

### Q33. "Are your findings statistically significant or clinically significant?"

Both, and they are different things. Statistically significant means the observed differences are unlikely to arise by chance — all three primary comparisons have p < 0.001. Clinically significant means the improvement is large enough to matter in practice. The effect sizes are large: Hedges' g of 1.31 for alignment and 4.47 for low-PAC targeting. For context, a Hedges' g above 0.8 is considered large in the behavioral sciences. The low-PAC targeting improvement — from 51.7% to 82.6% — means that the predictive controller directs stimulation to the right moments 60% more often than reactive control. That is a meaningful difference for a patient receiving daily therapy.

---

### Q34. "Did you use AI tools to build this?"

I used Claude and ChatGPT during development as coding assistants — for debugging, generating boilerplate code, and exploring implementation approaches. All AI usage is documented in my Assistance Disclosure Form. The key intellectual contributions — identifying the research gap, designing the feature ablation study, discovering the 12-feature representation, designing the closed-loop controller, and conducting the statistical analysis — were my own work. The AI tools did not design the experiment, choose the methodology, or interpret the results.

---

### Q35. "If you had unlimited resources and one more year, what would you do?"

A randomized crossover study. Same patients receive both fixed-schedule and adaptive 40 Hz stimulation on different days, with cognitive testing before and after each session. The primary endpoint would be whether adaptive stimulation produces measurably better memory performance — not just better biomarker alignment, but actual cognitive outcomes. I would record 60-minute sessions to capture the full habituation arc, stratify by patient subtype, and include genotype information because Chan et al. 2025 showed APOE genotype affects response. I would also test whether the optimal prediction horizon differs between patients who habituate quickly versus those who maintain entrainment — my current data hints at this but I do not have enough resolution to prove it.

---

### Q36. "Who would be most interested in your results?"

Three audiences. First, the 40 Hz therapy companies — Cognito Therapeutics is running a 670-patient Phase 3 trial with fixed-schedule delivery, and an adaptive controller could improve their outcomes without changing their hardware. Second, memory care facilities — the system under $250 per patient makes it accessible for nursing homes and day programs that cannot afford clinical-grade neurostimulation equipment. Third, the closed-loop neuromodulation research community — the principle that predictive control outperforms reactive control at multi-second horizons applies beyond 40 Hz entrainment to any brain stimulation paradigm where the biomarker changes slowly enough to forecast.

---

### Q37. "Why should this become a product rather than stay a research project?"

Because the gap between what is known and what is delivered is enormous. We know 40 Hz stimulation promotes amyloid clearance. Cognito has Breakthrough Device Designation. But every protocol in clinical trials right now uses fixed schedules, which waste stimulation on moments when the brain does not need it and miss moments when it does. An adaptive controller that runs on a $200 consumer headset and a laptop could make personalized 40 Hz therapy available without a clinician present, in a patient's home, at a fraction of the cost of clinical visits. The intelligence layer is device-agnostic — only the sensor changes. That changes the cost structure from "come to the clinic three times a week" to "wear a headset at home for 15 minutes."

---

### Q38. "What happens if 40 Hz therapy turns out not to work?"

Even if the Phase 3 results are negative for 40 Hz specifically, the closed-loop control framework generalizes. The approach — use a biomarker to forecast neural state and time interventions proactively — applies to any brain stimulation protocol where the response is variable and predictable. Closed-loop DBS for Parkinson's was FDA-approved in February 2025 using the same principle with a different biomarker (beta power instead of PAC). If 40 Hz does not pan out, the controller architecture transfers to other stimulation frequencies, other modalities, or other conditions.

---

## QUICK-REFERENCE: Numbers You Must Know Cold

| Metric | Value |
|--------|-------|
| Dataset | OpenNeuro ds005048, 35 subjects, 7 frontal channels, 250 Hz |
| Splits | 24 train / 5 val / 6 test (subject-level, no leakage) |
| Windows | 17,283 total (2s windows, 1s hop) |
| Static ceiling | R-squared = 0.287 (8 architectures, 1,457 to 1.1M params) |
| TCN params | 22,914 (h=64), 12 PAC+Stim features, 20-step lookback |
| TCN R-squared (5s horizon) | 0.606 +/- 0.032 (5 seeds, range 0.558-0.647) |
| TCN R-squared (10s horizon) | 0.669 (single seed) |
| Persistence R-squared (5s) | 0.104 |
| Persistence R-squared (10s) | -0.081 |
| Alignment: TCN vs Reactive | 72.1% vs 64.5%, g=1.31, p<0.001 |
| Low-PAC targeting | 82.6% vs 51.7%, g=4.47, p<0.001 |
| PAC Gap | 30.5 vs 21.1, g=1.57, p<0.001 |
| Oracle alignment | 100% (perfect hindsight upper bound) |
| PAC Gap % of oracle | 91% (30.5/33.3) |
| Subjects benefiting | 35/35 (binomial p<0.001) |
| Inference time | <50 ms |
| Hardware cost | Under $250 (Muse 2 ~$200 + headphones) |
| Cognito Phase 3 | HOPE trial, 670 patients, results mid-2026 |

---

## INTERVIEW TACTICS

**Gauge and pivot.** Start at medium technical depth. If the judge nods, go deeper. If they look uncertain, say "Let me put that more concretely" and drop to analogy level. Do not wait for them to ask you to simplify.

**Failure = finding.** Every dead end you hit was a discovery. The 8-architecture convergence was not a failure — it was proof that the bottleneck is data, not model capacity. Frame it that way.

**Honest baselines.** Always contextualize your numbers against baselines. Never say "R-squared of 0.60" without saying "versus persistence at 0.10." The comparison is the story.

**Bridge from "I do not know."** Never bluff. Say: "That is outside what I tested, but based on [related finding], I would hypothesize [educated guess]. That would be a good follow-up experiment."

**The sentence judges retell.** Give them one sentence for deliberation: "He built a system that predicts when a patient's brain will lose response five seconds before it happens, and it worked on all 35 patients."

**Point at figures.** When you reference a result, physically point to the relevant figure or table on your display. It directs attention and gives you natural movement.

**Do not recite.** You have 1-minute, 3-minute, and 5-minute versions ready. But never memorize word-for-word. Know your key numbers and let the phrasing be natural.
