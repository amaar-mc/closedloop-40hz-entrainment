# 3. Literature Review

The present work sits at the intersection of four active research areas: (1) the neurophysiology
of gamma oscillations and their disruption in Alzheimer's disease, (2) sensory-evoked 40 Hz
entrainment as a therapeutic modality, (3) closed-loop neuromodulation systems, and (4) deep
learning methods for EEG time-series analysis. This section reviews the foundational and recent
literature in each area, contextualizes the specific gaps that motivate the present work, and
positions the proposed approach within the broader landscape of computational neuroscience and
biomedical AI.

---

## 3.1 Gamma Oscillations and Theta-Gamma PAC in Alzheimer's Disease

### 3.1.1 Gamma Oscillations in Healthy and Pathological States

Gamma-band oscillations (30–100 Hz) emerge from the coordinated activity of inhibitory
fast-spiking parvalbumin-positive (PV) interneuron networks that generate rhythmic inhibitory
postsynaptic potentials at gamma frequencies. These rhythms play a fundamental role in
cognitive processing, serving as temporal scaffolds for sensory feature binding, attention
allocation, working memory maintenance, and long-range cortical communication. The disruption
of these rhythms in Alzheimer's disease has been recognized as an early and sensitive marker
of the underlying neurodegeneration.

Gamma oscillations are disrupted in AD across multiple scales of measurement. At the cellular
level, PV interneuron populations are among the earliest neuronal subtypes to be affected by
Aβ accumulation, with interneuron-specific synaptic dysfunction documented in preclinical
models before plaque formation [3]. At the network level, reduced gamma power and increased
gamma variability have been characterized in EEG and MEG recordings from AD patients and those
with mild cognitive impairment (MCI). A comprehensive review by Wang et al. [1] surveyed
gamma oscillation disruptions across AD, Parkinson's disease, stroke, and schizophrenia,
concluding that gamma entrainment-inducing stimulation methods offer notable neuroprotection
and emphasizing gamma restoration as a transdiagnostic therapeutic target.

Particularly relevant to the 40 Hz entrainment paradigm, Iaccarino et al. [7] demonstrated
that Aβ overproduction in 5XFAD transgenic mice was associated with a selective reduction
of gamma activity that preceded plaque formation, and that driving gamma at 40 Hz by
optogenetically activating PV interneurons was sufficient to reduce soluble Aβ by ~50%.
This mechanistic connection between gamma oscillation restoration and amyloid clearance
established the scientific rationale for non-invasive entrainment approaches.

### 3.1.2 Theta-Gamma Phase-Amplitude Coupling as a Biomarker

While raw gamma power provides a useful readout of oscillatory activity, phase-amplitude
coupling (PAC) between theta and gamma bands offers a more sensitive and specific biomarker
of the coordinated multi-frequency dynamics that characterize successful neural entrainment.
PAC, in the theta-gamma formulation, describes the degree to which the amplitude of gamma-band
oscillations (30–100 Hz, or more narrowly 38–42 Hz in the entrainment context) is modulated
by the phase of theta-band oscillations (4–8 Hz). Strong theta-gamma PAC reflects the
coordination of fast inhibitory interneurons by slower excitatory theta cycles — a mechanism
critical for organizing information processing across hippocampal-cortical circuits.

The disruption of theta-gamma PAC in AD is well-documented and closely linked to cognitive
impairment. Dimitriadis et al. [4] demonstrated that gamma PAC in parahippocampal cortices,
particularly the left parahippocampus, is significantly reduced in AD patients compared to
healthy controls, and that these reductions are most pronounced in patients with co-occurring
epileptiform activity — pointing to network hyperexcitability as a mechanistic pathway.
Strikingly, PAC reductions were found to be a more sensitive index of AD-related network
dysfunction than gamma power alone, supporting PAC over simpler spectral measures as the
primary biomarker.

Theta-gamma coupling has also been characterized as a powerful predictor of cognitive function.
Backus et al. [5] reported that theta-gamma coupling (TGC) was the single strongest predictor
of working memory performance across AD, MCI, and healthy control participants, with a
standardized beta of 0.693 (p < 0.001) — substantially exceeding the predictive value of
gamma power (beta = 0.253) and theta power alone (beta = −0.019, non-significant). A 2024
replication [6] confirmed these relationships in an independent sample, further validating
TGC as the primary outcome measure for entrainment-based therapy.

The quantitative measure used throughout the present work, the Modulation Index (MI) introduced
by Tort et al. [31], operationalizes PAC as the Kullback-Leibler divergence between the
observed distribution of gamma amplitude over theta phase bins and a uniform (no coupling)
reference distribution. Higher MI values indicate that gamma amplitude is strongly concentrated
in specific theta phase windows, reflecting strong coupling; values near zero indicate the
coupling is absent. The MI has become the standard measure for PAC computation in the
neuroscience literature and provides the scalar entrainment biomarker that the proposed
closed-loop system estimates and forecasts.

---

## 3.2 40 Hz Sensory Entrainment: Mechanisms and Clinical Evidence

### 3.2.1 Landmark Animal Studies

The modern investigation of 40 Hz sensory entrainment as a therapeutic modality for AD
originates with Iaccarino et al. [7], whose 2016 Nature paper demonstrated that visual flicker
at 40 Hz — but not at other tested frequencies — drove gamma oscillations in visual cortex
of 5XFAD transgenic mice and produced a rapid, robust reduction in Aβ1-40 and Aβ1-42 levels
in the visual cortex. Crucially, this effect was accompanied by microglial morphological
transformation (cell body enlargement, process retraction) and upregulation of phagocytosis-
promoting genes, establishing a mechanistic link between gamma oscillation entrainment and
cellular Aβ clearance. The frequency specificity — 40 Hz but not 20, 80, or random flickering —
demonstrated that the therapeutic effect was not a generic response to visual stimulation but
reflected genuine gamma-frequency network recruitment.

Subsequent research extended these findings to auditory stimulation and multi-sensory paradigms.
Multisensory approaches combining auditory and visual 40 Hz stimulation were found to produce
stronger and more widespread gamma entrainment than either modality alone, with corresponding
improvements in amyloid clearance. A landmark 2024 Nature study by Murdock et al. [8]
identified the glymphatic system as a previously unrecognized clearance pathway activated by
multisensory gamma entrainment: 40 Hz combined audiovisual stimulation promoted CSF influx
and interstitial fluid efflux throughout cortex, leading to a 37% reduction in neocortical
plaque volume in 5XFAD mice. Pharmacological inhibition of aquaporin-4 water channels —
the cellular machinery of glymphatic transport — abolished this clearance, confirming the
glymphatic pathway as mechanistically necessary rather than epiphenomenal.

At the immunological level, Bhatt et al. [13] characterized the cytokine and chemokine
signaling profile induced by 40 Hz visual stimulation, finding upregulation of IL-6, IL-4,
and macrophage-colony-stimulating factor (M-CSF) — molecules that collectively promote
microglial phagocytic competence and distinguish the gamma-induced immune response from
general neuroinflammation. This immunological characterization is important for understanding
the dose-response relationships that motivate personalized delivery: insufficient stimulation
fails to engage the microglial response, while excessive or poorly timed stimulation risks
habituation without therapeutic benefit.

### 3.2.2 Translation to Human Trials

Translation of 40 Hz entrainment to human clinical trials has proceeded rapidly since 2016.
Initial safety and tolerability studies confirmed that 40 Hz auditory and visual stimulation
is well-tolerated in elderly populations and produces measurable EEG entrainment responses.
However, substantial individual variability in entrainment magnitude was noted from the
earliest human studies, foreshadowing the personalization challenges that the present work
addresses.

The most significant human clinical evidence to date comes from Chan et al. [11], who reported
results from an open-label extension study of 40 Hz multisensory stimulation in patients
with mild Alzheimer's dementia, conducted under the auspices of MIT and Cognito Therapeutics.
Three female participants with late-onset AD retained strong EEG entrainment responses across
the extension period and showed markedly less hippocampal and cortical atrophy compared to
matched controls. Plasma pTau217 — a leading blood biomarker of AD pathology — showed
reductions of 47% and 19% in the two patients for whom serial plasma samples were available.
These findings provide the strongest available evidence of target engagement in humans
and establish pTau217 reduction as a validated biological endpoint for future controlled trials.

In a non-human primate model that bridges the gap between mouse studies and human application,
Goutier et al. [10] demonstrated that 40 Hz auditory stimulation delivered to aged rhesus
monkeys over five or more weeks elevated CSF Aβ levels in a manner consistent with mobilization
from brain parenchyma and active clearance — effects that persisted for up to five weeks
after cessation of stimulation. This prolonged duration of effect has important implications
for scheduling optimization: clearance dynamics that operate over minutes-to-hours timescales
require correspondingly long-horizon monitoring and control strategies.

The OpenNeuro ds005048 dataset [39], produced by Lahijanian et al. [12], provides the EEG
recording resource underlying the present work. This dataset contains recordings from 13
dementia patients undergoing 40 Hz auditory entrainment using a 5 kHz carrier amplitude-
modulated at 40 Hz (4% duty cycle), with alternating 40-second stimulation and 20-second
rest trials in BIDS format. The dataset descriptor [39] introduced an entrainment score (ES)
based on 40 Hz power and validated phase-locking value (PLV) measurements as metrics of
network synchronization. Lahijanian et al. [12] subsequently showed that this entrainment
paradigm enhances frontoparietal DMN connectivity, mimicking connectivity patterns observed
in healthy brains — confirming that auditory gamma entrainment produces functionally
meaningful network changes in dementia patients.

---

## 3.3 Inter-Individual Variability and the Need for Personalization

### 3.3.1 Responder and Non-Responder Populations

A consistent finding across both animal and human studies of gamma entrainment is the
substantial inter-individual variability in response magnitude. In healthy participants,
40 Hz stimulation produces robust power increases at the stimulation frequency in most
individuals; in dementia patients, the distribution of entrainment responses is considerably
wider, with a meaningful fraction showing minimal or absent entrainment.

Fortunato et al. [15] conducted a systematic analysis of 40 Hz entrainment in a mixed cohort
of healthy participants and dementia patients, partitioning participants into entrained and
non-entrained groups based on 40 Hz power spectral density during stimulation. Of 33 total
participants, 23 showed measurable entrainment while 10 did not — a non-responder rate of
approximately 30%. Crucially, the authors noted that baseline neural characteristics such as
resting-state gamma power and individual alpha-peak frequency predicted entrainment success
to some degree, suggesting that personalized pre-screening could improve the efficiency of
therapy delivery. However, no simple single-biomarker predictor was sufficient to reliably
classify responders in advance, motivating a dynamic, session-by-session approach.

Cabral et al. [16] extended this analysis to highlight the multidimensional nature of
individual differences in entrainment response, identifying baseline neural state, sensory
processing abilities, cultural background, and personal preferences as factors that collectively
modulate entrainment efficacy. The authors advocated explicitly for AI-driven biofeedback as
the most promising path toward personalized digital therapeutics, framing the closed-loop
control problem as one of real-time biomarker tracking rather than static individual profiling.

Personalized computational modeling approaches have further illuminated the mechanistic basis
of individual differences. Rathour et al. [17] demonstrated that subject-specific whole-brain
neural mass models reveal synergistic Aβ and tau pathomechanistic interactions that are
obscured in population-average analyses, and that whole-brain and hippocampal volumes
distinguish between responders and non-responders in AD drug trials. These findings suggest
that future personalized entrainment systems may need to integrate structural neuroimaging
biomarkers alongside EEG to fully characterize individual treatment response potential.

### 3.3.2 Intra-Session Habituation

Intra-session habituation — the progressive reduction in neural responsiveness to repeated
identical stimuli — presents an equally important challenge for fixed-protocol entrainment
therapy. Neural adaptation to repetitive sensory stimuli is a fundamental property of sensory
cortex and has been characterized at every level of the neural hierarchy from single-unit
responses to scalp EEG [3]. In the gamma entrainment context, habituation manifests as a
temporal decline in the strength of theta-gamma coupling within a single session, even among
patients who show robust initial entrainment responses.

The practical consequence is that a fixed schedule treating all time points equivalently
will systematically over-stimulate during periods of strong coupling (potentially accelerating
adaptation) and under-stimulate during periods of declining coupling (missing the windows of
greatest therapeutic need). An adaptive system that monitors coupling dynamics in real time
and modulates stimulation accordingly can in principle avoid both failure modes — but only if
it can detect declining coupling early enough to adjust proactively. This temporal constraint
defines the minimum forecasting horizon requirement: 5–10 seconds ahead must be achievable
to enable meaningful proactive intervention before coupling has already deteriorated.

---

## 3.4 Closed-Loop Neuromodulation Paradigms

### 3.4.1 Deep Brain Stimulation and the Closed-Loop Rationale

The concept of closed-loop neuromodulation — adjusting stimulation parameters in real time
based on neural feedback — is well-established in deep brain stimulation (DBS) for movement
disorders. Conventional open-loop DBS for Parkinson's disease delivers continuous stimulation
at fixed amplitude and frequency regardless of the patient's momentary motor state, leading
to stimulation during symptom-free periods, unnecessary battery consumption, and progressive
tolerance. Rosin et al. and Herron et al. established that triggering DBS in response to
pathological beta-band oscillations reduced motor symptoms while consuming less energy and
slowing the development of patient habituation [27]. Tafazoli et al. extended closed-loop
principles to more complex stimulation patterns, demonstrating that state-responsive DBS
could achieve outcomes not achievable by any open-loop protocol. Data-driven control design
using autoregressive models fitted from patient-specific recordings has further demonstrated
feasibility for personalized model predictive control in parkinsonian tremor [28], providing
a direct methodological antecedent for the temporal prediction approach used in the present
work.

Responsive neurostimulation (RNS), FDA-approved since 2013 for medically refractory focal
epilepsy, provides the most clinically mature closed-loop neuromodulation system. The RNS
device continuously monitors intracranial EEG from stimulating electrodes, detects ictal
and pre-ictal patterns using embedded classifiers, and delivers brief stimulation bursts in
response to detected activity. Long-term outcome data demonstrate seizure reduction rates
comparable to repeat surgical resection, with a favorable safety profile [27]. The epilepsy
closed-loop paradigm establishes key engineering constraints — specifically, the tolerance
for false-positive and false-negative detection errors — that are directly relevant to
designing closed-loop systems for gamma entrainment.

### 3.4.2 Deep Learning-Based Closed-Loop Systems

The emergence of embedded deep learning has expanded the design space for closed-loop systems
beyond simple threshold detectors to expressive learned classifiers and predictors. Lacourse
et al. demonstrated the Portiloop system — a real-time, wearable closed-loop EEG device
for sleep spindle-locked transcranial alternating current stimulation — using a convolutional
network running on a Raspberry Pi to detect upcoming spindle events with sufficient accuracy
and latency for real-time phase-locked delivery. This work established that consumer-grade
embedded hardware is sufficient for real-time EEG-based closed-loop control with deep learning
inference.

A scalable closed-loop EEG framework for neural stimulation responsiveness (PMC, 2023)
demonstrated EEGNet-based binary classification for predicting whether a given 2-second EEG
segment would benefit from stimulation, reporting 78.5% accuracy in offline cross-validation.
This work provides direct precedent for using the EEGNet architecture in a closed-loop
stimulation pipeline and establishes baseline performance expectations for static, window-level
EEG classifiers — performance levels that the present work builds upon by adding a temporal
forecasting layer.

The critical gap in the existing closed-loop literature is the absence of systems targeting
PAC dynamics specifically for gamma entrainment optimization. Existing DBS systems target
local field potential amplitude; epilepsy systems target waveform morphology; sleep systems
target spindle occurrence. None of the prior work has attempted to forecast the multi-frequency
theta-gamma coupling trajectory over 5–10 second horizons — the specific technical challenge
that defines the operationally useful range for proactive gamma entrainment control.

---

## 3.5 Deep Learning for EEG Time-Series Analysis

### 3.5.1 EEGNet and Compact BCI Architectures

Systematic comparisons of deep learning architectures for EEG time-series analysis [19]
have established that LSTMs, CNNs, and related architectures each offer complementary
strengths: LSTMs excel at modeling temporal dependencies from raw signals without feature
engineering, while CNNs excel at learning spatial filter banks from electrode arrays.
EEGNet, introduced by Lawhern et al. [25] in 2018, established a compact and generalizable
convolutional neural network for BCI applications by combining the spatial filtering strength
of CNNs with aggressive parameter reduction, resulting in a widely-used benchmark architecture. EEGNet employs two convolutional blocks: a temporal convolution
that learns frequency-selective filters, followed by a depthwise spatial convolution that
learns electrode-specific spatial filters from the temporal features. A separable convolution
block completes the feature extraction, followed by a classification or regression head.
The full architecture contains fewer than 2,000 parameters for most BCI configurations and
trains in minutes on standard hardware — properties that make it particularly attractive
for embedded deployment.

In the context of the present work, EEGNet is used in a regression formulation to predict
current theta-gamma PAC (Modulation Index) from 2-second raw EEG windows across 7 frontal
channels. The architecture's depthwise spatial convolution is especially well-suited to this
task, as it learns subject-agnostic spatial filters over the frontal electrode array without
requiring the large parameter counts that full spatial convolutions would entail. The observed
R² ≈ 0.287 ceiling represents the upper bound of information available in instantaneous
2-second windows for predicting epoch-level PAC labels, rather than a limitation of EEGNet
specifically — a conclusion supported by the systematic architecture search in Section 5.

### 3.5.2 Temporal Convolutional Networks for Sequence Prediction

Temporal Convolutional Networks (TCNs), introduced by Bai et al. and subsequently developed
for multiple EEG applications, offer a compelling alternative to recurrent architectures for
sequence-to-sequence prediction tasks. TCNs use dilated, causal convolutions to capture
long-range temporal dependencies without the vanishing gradient problems that affect vanilla
RNNs, and without the computational overhead of the backpropagation-through-time algorithm
required by LSTMs. The causal constraint — enforced by masking future time steps during
convolution — ensures that predictions at time t depend only on observations at time t and
earlier, a requirement that is non-negotiable for real-time closed-loop applications where
future data is unavailable.

Critically for the EEG domain, TCNs offer parallelizable training (unlike LSTMs, which must
be unrolled sequentially) and deterministic, fixed-latency inference — both important
properties for clinical deployment. The Temporal Convolutional Transformer architecture
(TCFormer, [25]) represents a recent hybrid that combines TCN feature extraction with
Transformer-based long-range dependency modeling, achieving state-of-the-art results on
motor imagery and other EEG benchmarks. For the present PAC forecasting task, the dilated
causal TCN is preferred over hybrid architectures because the prediction target is a smooth,
quasi-stationary signal (PAC dynamics evolve over seconds, not milliseconds), the receptive
field can be precisely controlled, and the model size constraint of <100K parameters is
more easily satisfied.

The multiscale TCN architecture used in this work employs four dilated convolution blocks
with dilation factors [1, 2, 4, 8], creating a 31-timestep causal receptive field (covering
31 seconds of history at 1-second time steps). GroupNorm normalization across channels
provides cross-subject stability without requiring batch statistics to be accumulated during
inference, an important property for personalized real-time deployment. Attention pooling
across the temporal dimension selectively weights the most informative timesteps in the
history window before the final regression head.

### 3.5.3 Positioning Against Related Work

Two recent systems provide the closest published analogues to the approach developed here,
and contextualizing against them clarifies the specific novelty of the present work.

Brian Intensify [24] is an adaptive machine learning framework for auditory EEG stimulation
and cognitive enhancement that predicts EEG responses with R² ≥ 0.80 using supervised
learning. It employs Bayesian optimization for real-time frequency tuning, identifying
13 Hz as the optimal stimulation frequency in over 80% of participants. While Brian Intensify
demonstrates that ML-based personalization is technically achievable for EEG stimulation,
it targets a fundamentally different prediction problem (which stimulation frequency to
deliver, not when to deliver 40 Hz stimulation) and does not address the temporal forecasting
challenge that defines the present work.

The PRIME framework [23] (Personalized Real-time Inference of Momentary Excitability) uses
an end-to-end deep learning model trained on raw EEG to predict momentary cortical
excitability, demonstrating feasibility of personalized real-time EEG biomarker estimation.
PRIME's approach is most analogous to the EEGNet Stage 1 component of the present work —
real-time estimation of a neural state from EEG — but does not address the multi-step
forecasting problem, the closed-loop control architecture, or the gamma entrainment application
context.

The deep learning MPC approach for Parkinson's DBS [26] provides the closest methodological
parallel for the temporal prediction and control aspects. This system uses input-convex neural
networks to model multi-step beta oscillation dynamics and solves an MPC optimization problem
online to determine stimulation timing and amplitude. The approach outperforms linear MPC by
10% and PI controllers by 20% while reducing energy consumption by 5%. The present work
adopts a similar predictive control philosophy — forecast future neural state, then make
stimulation decisions to optimize a therapeutic objective — but targets theta-gamma PAC
dynamics in the gamma entrainment context rather than beta oscillations in DBS, and uses
a simpler threshold-based controller rather than model predictive optimization, reflecting
the current state of knowledge about the PAC-to-therapy relationship.

Collectively, these works establish that (1) deep learning-based real-time EEG biomarker
estimation is feasible and clinically relevant, (2) temporal prediction of neural dynamics
enables superior neuromodulation relative to reactive and open-loop approaches, and (3) the
specific problem of forecasting theta-gamma PAC at 5–10 second horizons for proactive gamma
entrainment control has not been addressed in the prior literature. The present work fills
this gap.
