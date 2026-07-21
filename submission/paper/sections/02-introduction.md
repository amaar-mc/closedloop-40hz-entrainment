# 2. Introduction

## 2.1 Clinical Burden of Alzheimer's Disease

Alzheimer's disease (AD) is a progressive neurodegenerative disorder and the leading cause of dementia worldwide. Over 55 million individuals currently live with dementia globally, a figure projected to nearly triple to 153 million by 2050 as populations age [1]. AD accounts for 60–70% of all dementia cases and imposes an enormous societal burden: in the United States alone, the annual economic cost exceeds $300 billion, and family caregivers contribute an estimated 18 billion hours of unpaid care each year [1]. Despite decades of pharmaceutical research, approved disease-modifying treatments remain narrow in their benefits and limited in accessibility, underscoring the urgent need for novel therapeutic strategies that can complement or amplify pharmacological interventions.

A rapidly emerging non-pharmacological approach is sensory-evoked gamma entrainment — the use of 40 Hz auditory or visual stimulation to synchronize gamma-frequency (30–100 Hz) brain oscillations. Iaccarino et al. [7] demonstrated in a landmark Nature study that optogenetically and sensory-driving gamma oscillations at 40 Hz in transgenic mouse models of AD reduced amyloid-beta (Aβ) by up to 50% through microglial activation and enhanced phagocytic clearance. Subsequent work expanded these effects to auditory modalities and multi-sensory stimulation, showing reductions in both Aβ and tau pathology alongside improvements in spatial memory. Most recently, Chan et al. [11] reported results from a Phase II open-label extension study at MIT and Cognito Therapeutics showing that sustained 40 Hz multisensory stimulation slowed brain atrophy in mild AD patients and reduced plasma phosphorylated tau (pTau217) by 19–47% — representing the first human clinical evidence of target engagement at this scale.

These findings position 40 Hz gamma entrainment as a promising, low-cost, and mechanistically grounded therapeutic avenue. However, all existing clinical implementations share a fundamental limitation: stimulation is delivered on a rigid fixed schedule, entirely independent of the patient's real-time neural state. This one-size-fits-all approach ignores two critical realities — substantial inter-individual variability in entrainment response and progressive intra-session habituation — that together render fixed protocols systematically suboptimal. The present work addresses this gap by developing and validating a predictive, closed-loop control system that forecasts future entrainment state to enable proactive, personalized stimulation timing.

## 2.2 40 Hz Gamma Entrainment as Therapy

The therapeutic hypothesis underlying gamma entrainment is grounded in the disruption of normal oscillatory dynamics in AD. Gamma oscillations (30–100 Hz) are fundamental to sensory binding, attention, working memory consolidation, and inter-regional neural communication; in AD, gamma activity is reduced early in disease progression, often preceding amyloid plaque formation and clinically detectable cognitive decline [3]. This dysregulation reflects a loss of fast-spiking parvalbumin-positive (PV) interneurons that normally pace cortical gamma rhythms, disrupting the network dynamics on which higher cognitive function depends [7].

The mechanistic pathway from 40 Hz stimulation to amyloid clearance involves multiple interconnected processes. First, optogenetic or sensory 40 Hz drive re-engages PV interneurons, restoring impaired gamma rhythms across cortical networks [7]. Second, this interneuronal activation triggers an immunological cascade: upregulation of cytokines including IL-6 and IL-4 promotes microglial morphological transformation and dramatically enhanced phagocytosis of Aβ plaques [13]. This cytokine profile is distinct from general neuroinflammation, representing a targeted neuroprotective response rather than a non-specific inflammatory reaction. Third, a recently identified glymphatic pathway contributes substantially to clearance: Murdock et al. [8] demonstrated in a 2024 Nature study using the 5XFAD mouse model that multisensory 40 Hz stimulation promotes cerebrospinal fluid (CSF) influx and interstitial fluid efflux in the cortex. Combined audiovisual stimulation produced stronger gamma oscillations than either modality alone, leading to marked microglial clustering within 25 µm of Aβ plaques and a whole-brain 37% reduction in neocortical plaque volume. Critically, pharmacological inhibition of glymphatic flow abolished the clearance effect, confirming this pathway as necessary — not merely contributory — to the therapeutic mechanism.

Translation to human subjects has progressed substantially in recent years. A 2025 study in aged rhesus monkeys found that long-term 40 Hz auditory stimulation elevated CSF Aβ levels, consistent with mobilization and clearance from brain tissue, with effects lasting up to five weeks post-treatment [10]. In humans, Chan et al. [11] reported an open-label extension study in which patients with mild AD who received sustained 40 Hz multisensory stimulation retained strong EEG entrainment responses over time and showed less hippocampal atrophy compared to matched controls — a finding corroborated by auditory gamma entrainment's demonstrated ability to enhance default mode network (DMN) connectivity in dementia patients [12]. These results collectively establish 40 Hz entrainment as a clinically relevant therapeutic modality and make the optimization of stimulation delivery an immediate practical priority.

## 2.3 Limitations of Fixed-Schedule Protocols

Despite the therapeutic promise of 40 Hz entrainment, current clinical protocols are uniformly open-loop: they deliver stimulation according to a predetermined schedule without reference to the patient's instantaneous neural state. The standard protocol in human trials consists of alternating 40-second stimulation blocks and 20-second rest periods, repeated continuously for one hour regardless of the patient's entrainment response [12, 39]. This approach is administratively simple but is systematically misaligned with the highly variable neural dynamics of the dementia population.

The first dimension of variability is inter-individual. Fortunato et al. [15] analyzed a cohort of participants receiving gamma entrainment therapy and found that 23 achieved measurable entrainment at 40 Hz as assessed by power spectral density, while 10 showed minimal or no measurable response — a non-responder fraction of approximately 30% that fixed protocols cannot detect, accommodate, or dynamically address. Cabral et al. [16] similarly identified baseline neural state, sensory processing abilities, prior cognitive reserve, and individual neural architecture as major determinants of entrainment efficacy, noting that these factors vary across individuals in ways that defy prediction from clinical characteristics alone. Personalized whole-brain neural mass modeling has further demonstrated that subject-specific computational approaches uncover synergistic Aβ and tau pathomechanistic interactions that population-level models obscure [17]. High-performing patients and non-responders thus receive identical stimulation despite profoundly different neural responses, yielding population-average outcomes that underperform what individualized targeting could achieve.

The second dimension of variability is intra-session habituation. Repeated identical stimuli cause progressive weakening of neural responses — a canonical phenomenon in sensory neuroscience described formally as neural adaptation (Thompson and Spencer, 1966) — and this effect is well-documented in the context of gamma entrainment. In the OpenNeuro ds005048 dataset used in this work, individual subjects exhibit PAC trajectories that rise, plateau, and decline within single sessions, reflecting the time course of habituation. Stimulation delivered during periods of already-strong coupling wastes therapeutic resources and may accelerate habituation; stimulation withheld during periods of declining coupling misses the windows of genuine therapeutic need where intervention would be most beneficial.

The convergence of inter-individual variability and intra-session habituation creates a compelling case for real-time brain-state monitoring and adaptive closed-loop control. What is required is a system capable not merely of detecting the current entrainment state reactively — which introduces an inherent control delay equal to the detection latency — but of forecasting the near-future trajectory of entrainment state with sufficient lead time to intervene proactively, before decline has occurred rather than in response to it. This forecasting requirement defines the core technical challenge addressed by the present work.

## 2.4 Problem Statement and Contributions

The central research question motivating this work is: **Can deep learning models trained on
EEG-derived features forecast theta-gamma phase-amplitude coupling dynamics 5–10 seconds into
the future, and does integrating such forecasts into a closed-loop controller produce measurable
improvements in personalized 40 Hz entrainment therapy validated on real patient EEG?**

We approach this question through a two-stage computational architecture. Stage 1 establishes a
real-time PAC estimator using a compact deep learning model trained directly on raw EEG windows,
providing the current-state biomarker input that Stage 2 requires. Stage 2 constructs a causal
temporal predictor that ingests a 20-second history of PAC estimates and spectral features to
forecast future PAC at clinically relevant horizons of 5–10 seconds, enabling proactive rather
than reactive control decisions. The closed-loop controller integrates these predictions with a
personalized rolling baseline and 5-second hysteresis logic to determine stimulation actions:
stimulate when predicted PAC is forecast to fall below a personalized threshold, rest when
forecast PAC is strong, and maintain the current state otherwise.

The biomarker of interest throughout is the Modulation Index (MI), a measure of theta-gamma
phase-amplitude coupling (PAC) introduced by Tort et al. [31] that quantifies the degree to which
gamma-band (38–42 Hz) amplitude is modulated by the phase of theta-band (4–8 Hz) oscillations.
Higher MI values indicate stronger theta-gamma coupling and stronger entrainment; lower values
indicate reduced or absent coupling. PAC is particularly well-suited as an entrainment biomarker
because it captures the coordinated multi-frequency dynamics that characterize successful neural
synchronization, rather than the raw power in a single frequency band that may reflect artifact or
non-specific broadband changes.

All models are trained using subject-level splits with no within-subject leakage between train,
validation, and test sets. Final evaluation is conducted on EEG recordings from six held-out test
subjects, with controller performance assessed by replaying decisions across all 35 subjects'
recorded EEG — not simulated brain dynamics — providing a clinically grounded assessment of
real-world applicability. The strict subject-level separation ensures that all reported
generalization metrics reflect genuine cross-subject transfer rather than memorization of
individual recording characteristics.

This paper makes the following specific contributions:

**Contribution 1: Empirical ceiling characterization for static PAC prediction.**
A systematic architecture search across eight neural network configurations spanning three orders of magnitude in parameter count (1,457 to 2 million) demonstrates that all architectures converge to R² ≈ 0.287 on held-out test subjects. This convergence reveals an information ceiling imposed by the epoch-level structure of PAC labels (computed over 20–40 second blocks and assigned uniformly to constituent 2-second windows) and the limited discriminative capacity of instantaneous EEG snapshots from seven frontal channels. This is a data-structural finding rather than a capacity limitation of any individual model: larger and more complex architectures — including Vision Transformer hybrids with 2 million parameters — perform no better than the 1,457-parameter EEGNet. The ceiling motivates the transition from static estimation to temporal sequence modeling.

**Contribution 2: Causal TCN for 5–10 second ahead PAC forecasting.**
A multiscale causal Temporal Convolutional Network (31,043 parameters) trained on 73 engineered features — 61 spectral power features, 7 PAC-derived history features, and 5 stimulation-context features — achieves R² ≈ 0.25–0.28 at prediction horizons of 5–10 seconds. At these horizons, all baseline methods including persistence and Ridge regression collapse to negative R² (persistence: −0.267 at 5s; Ridge: −0.393 at 5s), representing a +0.5 R² margin for the TCN. An inflection point near 3 seconds marks the boundary where temporal sequence modeling becomes essential and simpler baselines cease to provide useful predictions.

**Contribution 3: Closed-loop controller validated on 35 real dementia patient EEGs.**
The TCN-based predictive controller achieves 72.1% alignment with patient therapeutic need versus 64.5% for reactive thresholding (p < 0.001, Hedges' g = 1.31), and targets 82.6% of low-PAC windows — the periods of genuine therapeutic need — versus 51.7% for reactive control (p < 0.001, g = 4.47), reaching 91% of the theoretical oracle upper bound. Every individual patient (35/35) benefits from the predictive controller relative to reactive thresholding (binomial p < 0.001), and the advantage holds for the six held-out test subjects unseen during training.

**Contribution 4: Characterization of the prediction horizon inflection point.**
Analysis across prediction horizons 1–10 seconds reveals a clear transition near 3 seconds where persistence and linear baselines cease to provide useful predictions. At 1–2 second horizons, persistence achieves R² = 0.76 and Ridge achieves R² = 0.81, while the TCN underperforms both (R² = 0.74). At 5+ second horizons, the ranking inverts completely: baselines go negative while the TCN maintains R² ≈ 0.25. This inflection defines the operationally critical horizon range for proactive neuromodulation — short enough to enable meaningful proactive control, long enough that temporal sequence modeling is the only viable approach.

The remainder of this paper is organized as follows.
Section 3 reviews the relevant literature covering gamma oscillations and PAC in AD,
40 Hz entrainment mechanisms and clinical evidence, inter-individual variability and
personalization challenges, closed-loop neuromodulation paradigms, and deep learning methods
for EEG time-series analysis.
Section 4 describes the dataset, preprocessing pipeline, PAC computation methodology,
feature engineering approach, and model architectures in full detail.
Section 5 presents the systematic architecture search findings and motivates the transition
from static PAC estimation to temporal sequence prediction.
Section 6 reports closed-loop controller performance on real patient EEG, including the
four-strategy comparison, fatigue model analysis across six severity levels and four
habituation models, and threshold sensitivity analysis.
Section 7 discusses the clinical implications of the findings, key limitations of the
offline validation approach, and future directions toward real-time hardware deployment
and reinforcement learning-based control.
Section 8 concludes with a summary of the main contributions and their broader significance
for personalized neuromodulation in Alzheimer's disease and beyond.
