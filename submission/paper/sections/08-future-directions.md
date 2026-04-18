# 8. Future Directions

This work establishes a computational foundation for personalized closed-loop 40 Hz gamma entrainment, validated on real patient EEG data. The immediate priorities for follow-on work are organized into two complementary tracks: a clinical translation pathway that moves from offline validation to live human study, and a set of technical extensions that would strengthen the system's robustness, generalizability, and real-world deployability.

---

## 8.1 Clinical Translation Pathway

The most consequential gap between the present work and clinical application is the transition from offline counterfactual replay to live closed-loop operation with real-time EEG streaming and genuine brain response. Closing this gap requires three phases of escalating rigor.

**Phase 1: IRB approval and live feasibility study.** The first step is Institutional Review Board (IRB) approval for a live closed-loop EEG study with the target patient population. This protocol would involve real-time EEG acquisition, online feature extraction and TCN inference (<50 ms per window, already demonstrated in simulation), and audio output routing through a low-latency speaker system. The primary technical requirement not yet evaluated is the full end-to-end latency chain from EEG sample acquisition through EEGNet inference, feature extraction, TCN inference, and audio onset — this must be characterized on target hardware before any human subject receives adaptive stimulation. A feasibility study (N=5–10 healthy adult participants) could verify that the live system produces the expected alignment improvement and that the system latency does not degrade the timing advantage over reactive control.

**Phase 2: Pilot study with dementia patients.**
Following feasibility validation, a pilot randomized controlled trial would compare adaptive (TCN predictive) versus fixed-schedule 40 Hz auditory stimulation in Alzheimer's disease patients.
The recommended design is a within-subject crossover: each participant completes both conditions across separate sessions, with order counterbalanced.
Appropriate sample size for the primary alignment outcome can be estimated from the current effect size (Hedges' g=+1.31): power analysis suggests N=12–20 subjects would be sufficient to detect this effect at 80% power with alpha=0.05, although the actual required N may differ in a live setting where EEGNet estimation error and real brain responses to stimulation are present.
The crossover design controls for inter-subject variability in baseline PAC levels and cognitive function, and counterbalancing protects against period effects (e.g., practice effects on cognitive assessments or learning effects in PAC response to stimulation).

**Recommended pilot study design:**

- **Population:** N=20 patients with mild-to-moderate Alzheimer's disease or amnestic mild cognitive impairment
- **Design:** Within-subject crossover (fixed schedule vs TCN predictive adaptive), 2 sessions per condition, 60 minutes per session, sessions separated by at least 48 hours
- **Hardware:** Consumer-grade dry-electrode EEG headset (minimum 7 frontal channels at 250 Hz, e.g., OpenBCI Cyton or comparable device), laptop with real-time inference pipeline, standard speaker or insert earphones for 40 Hz AM auditory delivery
- **Inference requirement:** <50 ms end-to-end latency (EEG → audio decision), achievable with the current TCN architecture on commodity CPU hardware
- **Primary outcome:** Session-averaged Modulation Index (theta-gamma PAC) measured from offline analysis of the continuous EEG recording
- **Secondary outcomes:** Stimulation alignment score (computed post-hoc from recorded PAC), cognitive battery pre/post session (MoCA, RAVLT, digit span), patient comfort and tolerability ratings
- **Safety monitoring:** Audio levels maintained below 70 dB SPL per session; adverse event reporting for any unexpected neurological or audiological symptoms; protocol reviewed by audiologist and ethics board before enrollment

**Phase 3: Regulatory and scaling considerations.**
If pilot results are positive, scaling to a multi-site trial would require FDA device classification review for adaptive neurostimulation software.
The current system would likely qualify as Software as a Medical Device (SaMD) under the FDA's Digital Health Center of Excellence guidelines, requiring documentation of the algorithm's decision logic, training data provenance, and performance bounds across the intended use population.
Regulatory engagement should begin during the pilot phase, not after, to identify any required modifications to the algorithm design or validation protocol before a larger study is committed.
Multi-site deployment would also require cross-site EEG calibration to account for differences in electrode placement, amplifier specifications, and recording environment that may shift the feature distributions seen during training — an active area of research in the domain generalization literature for EEG systems.

---

## 8.2 Technical Extensions

Several technical improvements would strengthen the system's robustness and clinical relevance, independent of the clinical translation pathway.

**Online per-subject adaptation.**
The current TCN model is trained on a population of 24 subjects and applied to new subjects without any fine-tuning.
Initial results from `temporal_multiscale/per_subject_adaptation.py` suggest that brief subject-specific fine-tuning (using the first 5–10 minutes of a new patient's session) can improve prediction accuracy for that individual.
Integrating online adaptation into the deployed system would allow the controller to personalize its forecasts in real time as it accumulates subject-specific EEG history.
This could be implemented as a lightweight linear adaptation layer trained while the session proceeds, with the base TCN serving as a frozen feature extractor — an approach analogous to meta-learning frameworks where a fast-adapting head is added to a slow-learning backbone.

**End-to-end validation with EEGNet in the loop.**
As discussed in Section 7.4, the current validation uses ground-truth PAC labels as TCN input.
An important next step is to evaluate the full chained pipeline (raw EEG → EEGNet → feature extraction → TCN → controller) end-to-end on the existing dataset.
This would quantify the degradation in alignment due to EEGNet estimation noise and determine whether the control advantage is preserved when the TCN operates on imperfect input features.
If the advantage degrades substantially, targeted improvements to EEGNet (possibly using the 5s-smoothed target formulation to reduce label noise, or by adding more training subjects through data augmentation) could recover it.
This validation can be performed on the existing dataset with no additional data collection and is the highest-priority next step before any live human study.

**Multi-site dataset validation.** The model was trained and evaluated exclusively on OpenNeuro ds005048. Validation on at least one additional dataset — ideally a demographically distinct population or a different EEG recording system — would substantially strengthen the generalizability claim. Several relevant datasets are publicly available, including datasets from non-clinical populations exposed to 40 Hz auditory stimulation (e.g., healthy young adults), which could be used to characterize how the model behaves outside its training distribution.

**Exploration of combined stimulation modalities.** The current system targets auditory 40 Hz amplitude modulation. Martorell et al. (2019) demonstrated that multi-sensory (combined auditory and visual) 40 Hz stimulation produces stronger effects on tau pathology and cognitive outcomes than unimodal stimulation in mouse models. A natural extension would be to design a controller that coordinates auditory and visual (flickering) stimulation modalities — potentially delivering both when PAC is predicted to decline, and withdrawing both during predicted recovery periods. This would require a modified output head producing joint stimulation decisions and evaluation of how PAC responds to multi-sensory vs unimodal adaptive stimulation.

**Extension to other brain-state biomarkers.** The current system uses theta-gamma PAC as the sole brain state biomarker. Additional EEG biomarkers — including frontal theta power (associated with cognitive load and working memory encoding), gamma power spectral density (measuring broadband gamma entrainment independent of coupling), and inter-regional connectivity measures (coherence between frontal and temporal regions) — could be integrated as additional control targets or weighting factors in the reward function. A multi-biomarker controller might achieve more nuanced brain state targeting by optimizing for a composite therapeutic objective rather than a single coupling metric.

**Reinforcement learning for controller policy.**
The current controller uses a fixed threshold policy (z-score thresholds ±0.5 with 5-second hysteresis).
An alternative approach would be to frame the closed-loop control problem as a sequential decision problem and train a reinforcement learning agent to discover an optimal stimulation policy.
The TCN forecaster would serve as a model of the environment (predicting future PAC given current features and proposed action), and the RL agent would learn a policy that maximizes cumulative PAC gap over the session.
This model-based RL framework would remove the need to manually specify threshold values and could discover non-threshold strategies — such as varying stimulation duration dynamically, or scheduling short rest periods within long stimulation windows to prevent habituation — that may outperform the current fixed-threshold policy.
This extension would also enable a principled treatment of the exploration-exploitation trade-off inherent in adaptive neurostimulation: how much should the controller exploit known-good strategies vs explore new stimulation patterns that might unlock higher PAC responses in a given patient?

---

## Timeline and Priority

The clinical and technical work streams are not mutually exclusive, but they have different timelines. IRB approval and hardware assembly for Phase 1 can proceed in parallel with the technical extensions. The end-to-end validation and per-subject adaptation work are lower-cost (no human subject involvement) and can be completed first, providing additional evidence to support the IRB application. Multi-site validation and regulatory engagement are longer-horizon activities that require funding and institutional partnerships beyond what a single research group can accomplish independently.

The single highest-priority next step is end-to-end validation with EEGNet in the loop on the existing dataset. This would directly address the most significant gap in the current validation and would either confirm that the control advantage is preserved under real conditions or identify the modifications needed to preserve it.
