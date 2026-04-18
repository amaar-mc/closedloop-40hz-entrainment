# Answer Depth Guide: 20 Key Questions at 3 Levels

How to read the judge: If they nod and say "mmhm" -- they get it, go deeper. If they tilt their head or look slightly lost -- simplify immediately. If they interrupt with a follow-up -- great, answer at their level. Never default to the deepest level. Start at Level 1 or 2 and let them pull you deeper.

---

## 1. "What is your project about?"

**L1 (Layman):** I built a system that predicts when an Alzheimer's patient's brain is about to stop responding to sound therapy, five seconds before it happens. That way, we can time the therapy to the moments it actually matters. On 35 patients, it worked better than any other approach.

**L2 (Intermediate):** I developed a causal temporal convolutional network that forecasts theta-gamma phase-amplitude coupling five seconds ahead using 12 PAC-trajectory features. The predictive controller achieves 72% alignment versus 64% for reactive, with every patient benefiting. The key discovery was that spectral EEG features hurt generalization -- dropping them raised R-squared from near zero to 0.60.

**L3 (Expert):** MultiscaleCausalTCN with depthwise-separable convolutions, dilations [1,2,4,8], 22,914 params. 12 features: 7 PAC-derived (current + causal MAs + diffs) and 5 stim context (binary state, switch timing, fraction, cycle phase sin/cos). 5-seed validation at h=5s: R2 = 0.606 +/- 0.032. Controller: z-score personalization with 30s rolling baseline, delta-z = 0.5, 5s hysteresis. Validated via offline counterfactual replay, Wilcoxon signed-rank, Hedges' g with BCa bootstrap CIs.

---

## 2. "How does 40 Hz therapy work?"

**L1:** Playing a rhythmic sound at 40 beats per second makes brain cells synchronize. When they synchronize, the brain's cleanup crew activates and starts clearing the toxic buildup that causes Alzheimer's. Like vibrating a filter to shake loose the dirt.

**L2:** 40 Hz auditory stimulation entrains gamma oscillations, activating two clearance pathways: microglial phagocytosis of amyloid-beta and glymphatic drainage through increased CSF flow. Iaccarino 2016 showed 50% amyloid reduction in mice. Murdock 2024 identified the glymphatic mechanism through VIP interneurons and aquaporin-4 channels.

**L3:** The mechanism is bifold. First, gamma entrainment triggers microglial morphological transformation from ramified to phagocytic state, directly engulfing Abeta oligomers and fibrils (Iaccarino 2016). Second, 40 Hz neural activity activates VIP+ interneurons that increase arteriolar pulsatility, driving perivascular CSF influx through AQP4 water channels on astrocytic endfeet. This is the glymphatic pathway. Murdock 2024 proved necessity: AQP4 knockout ablated the clearing effect. Hemispheric specificity was also demonstrated via unilateral stimulation.

---

## 3. "What did you discover?"

**L1:** I found that most of the brain data I was feeding my model was actually confusing it. When I removed the wrong kind of brain measurements and kept only the ones tracking how therapy response changes over time, prediction improved five-fold.

**L2:** 61 spectral EEG features were encoding subject-specific brain anatomy -- skull thickness, electrode impedance -- rather than transferable dynamics. Dropping them and keeping 12 PAC-trajectory features raised test R-squared from negative 0.03 to 0.60. This held across 5 seeds and 10 different model architectures.

**L3:** Feature ablation revealed that spectral power features in 7 channels produced a val-test R2 gap of 0.358, indicating memorization of subject-specific recording characteristics. The 12 surviving features capture strictly causal PAC dynamics and stim context. Post-hoc comparison across TCN, Transformer, GRU, LSTM, CNN, XGBoost, Ridge, and linear models showed all Tier 1 architectures converge to R2 0.61-0.65 on the reduced features, confirming this is a representation result, not an architecture result.

---

## 4. "Why should I care about predicting 5 seconds ahead?"

**L1:** If you wait to see that the brain has stopped responding, you've already lost time. Five seconds of lead time lets the system stimulate proactively -- before the brain drifts, not after.

**L2:** At short horizons, the brain barely changes -- just guessing "same as now" works fine. But at 5 seconds, every simple method collapses to negative R-squared. The TCN is the only method that holds. And 5 seconds is exactly the lead time a controller needs for proactive rather than reactive decisions.

**L3:** The PAC autocorrelation function decays with a time constant of approximately 3 seconds, corresponding to the stim-rest transition dynamics. Below 3s, the persistence baseline (naive copier) dominates with R2 > 0.5. Above 3s, persistence gives negative R2 -- worse than the marginal mean. The TCN's value is exclusively in the 3-10s regime where temporal dynamics deviate from autoregressive extrapolation. The 5s horizon was selected as the pragmatic operating point: sufficient lead time for controller action while maintaining R2 > 0.55.

---

## 5. "How do you know the model isn't just memorizing?"

**L1:** Three checks. No patient appears in more than one group -- the 6 test patients were completely hidden. The model architecture physically prevents seeing the future. And when I scrambled all the labels, the model learned nothing -- performance dropped to below zero.

**L2:** Subject-level splits with zero leakage. Architectural causality via left-only padding. Label permutation test returned R2 = -0.33. Additionally, the feature ablation study itself was a memorization diagnostic: when the model was memorizing (via spectral features), the val-test gap was 0.358. After removing the memorization pathway, the gap shrank to 0.246.

**L3:** Multi-layered leakage prevention. Subject-level partitioning verified by automated audit (temporal/validate_code.py). Causal architecture with no bidirectional components. Z-score scalers fit on train split only. The 73-to-12 feature ablation served as an explicit deconfounding step: spectral features explained subject identity (enabling train-set memorization), while PAC-trajectory features captured transferable dynamics. The val-test gap reduction from 0.358 to 0.246 quantifies the memorization removed. Permutation baseline R2 = -0.33 confirms signal is in labels, not feature structure.

---

## 6-20: Abbreviated (same format)

**6. "How does your controller decide when to stimulate?"**
L1: It converts the brain prediction to a score relative to that patient's recent history. Score too low = stimulate. Score high = rest. With a pause to prevent rapid switching.
L2: 30-second rolling z-score. z < -0.5 = STIMULATE. z > +0.5 = REST. 5-second hysteresis.
L3: Per-subject online z-normalization over 30-sample causal window. Dual-threshold decision rule (delta_z = 0.5) with minimum inter-decision interval of 5 seconds to prevent state oscillation. The hybrid controller additionally blends TCN forecast with instantaneous PAC estimate via weighted averaging.

**7. "What's the clinical significance of a 7.6 percentage point alignment improvement?"**
L1: It means 7.6% more of the therapy is reaching the brain at the right time. Over an hour session, that's several more minutes of effective stimulation.
L2: The effect size is Hedges' g = 1.31 (large). For low-PAC targeting specifically, the improvement is from 52% to 83% -- a 60% relative improvement in catching the moments when the brain actually needs stimulation.
L3: The absolute alignment delta of 7.6pp corresponds to g=1.31 [0.75, 1.87]. More clinically meaningful is the low-PAC targeting: from 51.7% to 82.6% (g=4.47 [3.33, 5.62]). The PAC gap metric -- difference in mean PAC between rest and stimulation states -- is 30.5 vs 21.1 (x10^-6 MI), reaching 91.6% of the theoretical oracle. In a 60-minute clinical session, this translates to approximately 12 additional minutes of correctly-timed stimulation.

**8. "Could this work in real time?"**
L1: Yes -- the model runs in under 50 milliseconds, and the brain changes on a timescale of seconds. Speed isn't the issue. The issue is we haven't tested the full feedback loop yet.
L2: Inference latency is <50ms on CPU. The Muse 2 streams at 256 Hz over Bluetooth. The pipeline bottleneck is BLE latency (~20-50ms), not model inference.
L3: Feature extraction 5ms, TCN forward pass 2ms on CPU, controller decision 1ms. Total <10ms. Consumer BLE EEG adds 20-50ms transport latency. At 250 Hz sample rate with 1-second prediction intervals, total system latency of ~70ms is negligible relative to the 5-second prediction horizon.

**9. "What's the difference between your approach and neurofeedback?"**
L1: Neurofeedback shows you your own brain activity and asks you to change it consciously. My system automatically adjusts therapy delivery without the patient doing anything.
L2: Neurofeedback is operant conditioning -- the patient learns to modulate their own brain state. My system is automated closed-loop control -- the patient is passive, and the system adjusts stimulation timing based on predicted brain state. No learning required from the patient.
L3: Architecturally distinct. Neurofeedback uses the human as the controller in a biofeedback loop. My system uses an algorithmic controller with a predictive model in the loop. The patient is not aware of and does not need to respond to the feedback. This is critical for Alzheimer's patients who may have impaired executive function and cannot reliably perform voluntary modulation tasks.

**10. "What would a larger study need to demonstrate?"**
L1: That adaptive stimulation actually improves memory and thinking, not just brain wave patterns. And that it works on patients from different clinics and backgrounds.
L2: Primary endpoint would be cognitive outcomes (MoCA/MMSE change), not just PAC alignment. Multi-site data to test generalization. Stratification by disease stage and APOE genotype. Longer sessions (60 min) to capture full habituation dynamics.
L3: Powered crossover design with cognitive primary endpoints. MCID for MMSE is typically 2-3 points over 6 months. Would need ~50 patients per arm to detect this with 80% power at alpha=0.05, assuming moderate effect. Multi-site (3+ centers) to assess generalizability. Biomarker secondary endpoints: session-level PAC, inter-session PAC trajectory, structural MRI annually. Pre-registered protocol with adaptive interim analysis.
