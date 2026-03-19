# 7. Discussion

This section interprets the experimental findings in relation to the central research question: can temporal PAC forecasting enable proactive closed-loop gamma entrainment that outperforms reactive threshold control? We discuss the mechanistic basis for the prediction horizon inflection point, the clinical interpretation of the proactive-vs-reactive trade-off, how this work positions relative to prior closed-loop neuromodulation research, and the limitations of the current validation methodology.

---

## 7.1 Interpretation of the Prediction Horizon Inflection Point

The clearest finding from the horizon sweep is that the utility of temporal modeling is horizon-dependent. At 1–2 second prediction horizons, the PAC signal is autocorrelated enough that a simple persistence forecast ("the future will look like the present") outperforms the TCN. At horizons beyond ~3 seconds, this autocorrelation decays to the point where persistence becomes worse than predicting the mean, and all linear and simple baselines collapse to negative R². The TCN, by contrast, maintains R²≈0.25 at 5–10 seconds — a regime where baselines are actively harmful as forecasters.

**Why does persistence fail beyond 3 seconds?** PAC dynamics in this dataset are non-stationary on the timescale of individual 20–40 second Stimulus and Rest epochs. Within an epoch, PAC evolves according to exponential dynamics: it rises upon stimulation onset (as gamma oscillations become entrained to the 40 Hz carrier) and decays during rest periods (as coupling dissipates through passive neural dynamics and habituation). These transitions occur on timescales of 5–15 seconds. When a forecaster predicts 1–2 seconds ahead, the current value is still within the same phase of an ongoing rise or decay and is genuinely predictive of the near future. At 5+ seconds, the forecaster must anticipate a qualitative state transition — from rising to plateauing, from plateauing to declining — that the current observation cannot predict without temporal context.

**Why does the TCN succeed where baselines fail?** The TCN's causal dilated convolutions with dilations [1, 2, 4, 8] create an effective receptive field of 31 time steps (31 seconds at 1s/step), spanning multiple within-epoch and inter-epoch transitions. Within this window, the TCN can observe: (a) the current stimulation state and how long it has been active, encoded in the 5 stimulation context features; (b) the trajectory of spectral power across theta, alpha, beta, and gamma bands over the past 20 seconds, which are informative about the direction and rate of PAC change; and (c) moving averages of PAC estimates at windows [2, 4, 8, 16], which provide explicit multi-scale trend information in the 7 PAC-derived features. Together, these multi-scale temporal features allow the TCN to distinguish between "PAC is low because stimulation just ended and PAC will recover" and "PAC is low because the patient has habituated and further stimulation is unlikely to restore coupling." This distinction is beyond the capacity of any single-step or linear forecaster.

**The ~3 second inflection point as a design parameter.** The inflection horizon is not merely a statistical artifact — it has a concrete mechanistic interpretation related to the autocorrelation time constant of PAC in this population.
This time constant is implicitly encoded in the empirical R² curves and likely reflects the characteristic time constant of theta-gamma coupling dynamics in elderly frontal cortex during auditory stimulation.
Future work could estimate this time constant directly from the autocorrelation function of PAC time series, which would provide a principled basis for selecting the minimum prediction horizon required for temporal modeling to add value in a given patient or paradigm.
Different patient populations, stimulation paradigms, or EEG recording montages may exhibit different inflection points; the horizon sweep methodology introduced here can be applied to any new setting to identify the appropriate boundary before committing to a temporal model architecture.

---

## 7.2 Why Proactive Outperforms Reactive Control

The 7.6 percentage-point alignment improvement of the TCN over reactive threshold control (72.1% vs 64.5%) can be decomposed into two mechanistic contributions: timing and targeting.

**Timing contribution.** The TCN achieves a mean lead time of 0.8 seconds before PAC decline onset, compared to 0.2 seconds for reactive control.
This 0.6-second advantage reflects the difference between predicting a transition (TCN) and detecting one after it has begun (reactive).
In practical terms, 0.8 seconds of lead time allows the controller to begin stimulus preparation before the PAC decline is detectable from the current window.
This is particularly relevant for auditory stimulation, where onset of a new audio segment has finite preparation latency (buffering, routing, mixing) that may consume 100–300 ms in a low-latency embedded system, and potentially 500+ ms in a software-only implementation.
A controller with 0.8s lead time can absorb this latency and still deliver stimulation at or near PAC decline onset; a controller with 0.2s lead time cannot reliably do so without risking that the audio onset arrives after the PAC has already begun recovering.

**Targeting contribution.** The more dramatic difference is in Low-PAC Stim Rate: the TCN stimulates 82.6% of below-median PAC windows compared to 51.7% for reactive control — a 60% improvement in therapeutic recall. This difference arises because reactive control misses PAC decline events that occur and recover within a single 2-second window, or that are below the detection threshold at the moment of observation. The TCN, by forecasting from a 20-second context window, can anticipate these brief declines based on their spectral precursors and stimulation context.

**The specificity trade-off.** The TCN sacrifices High-PAC Rest Rate (61.6% vs 77.3% for reactive control), meaning it delivers some stimulation during windows when PAC is adequate. This trade-off is clinically favorable in the context of auditory 40 Hz entrainment for the following reason: the cost of unnecessary stimulation (the patient hears amplitude-modulated audio when their gamma coupling is already strong) is low — the content is designed to be pleasant and non-disruptive — while the cost of missed stimulation (the patient's coupling declines without therapeutic support) is high in terms of therapeutic efficiency. A system optimizing for recall at moderate precision cost is the appropriate design for this application. This reasoning would differ for invasive neurostimulation therapies where overstimulation carries direct physiological risk; in that context, a more conservative (reactive) approach or a hybrid system might be preferred.

**Lead time as a clinical parameter.** The 0.6-second mean lead time advantage may seem modest, but it should be understood as a lower bound.
The validation protocol measures lead time as the time between controller decision and PAC decline onset for the subset of transitions where the controller correctly anticipates the decline.
For the many cases where the TCN predicts 5 seconds ahead — the full forecasting horizon — the lead time is substantially longer, but these cases are more difficult to characterize precisely within the offline counterfactual replay framework used here.
The offline replay cannot capture whether early stimulation (before PAC decline) actually prevents the decline from occurring, which would be the ultimate test of proactive control's value.
Future live validation would measure realized lead times directly, and would also allow assessment of whether early stimulation onset shortens the duration or depth of PAC declines — a question that is unanswerable from the present data.

---

## 7.3 Comparison to Prior Closed-Loop Neuromodulation Work

This work builds on a small but growing literature on deep-learning-based closed-loop neuromodulation. Three comparison points are particularly relevant.

**Portiloop (Lacroix et al., PLOS ONE 2022).** Portiloop is the closest architectural precedent: a convolutional LSTM that detects sleep spindles in EEG and triggers targeted memory reactivation (TMR) auditory cues within the spindle trough. Like the present work, it uses causal real-time inference on frontal EEG with sub-second decision latency. However, Portiloop addresses a fundamentally different control problem: spindle detection is a binary classification (spindle vs non-spindle), where the target event has a clear, sharp onset. PAC forecasting addresses a continuous regression problem with gradual, non-stationary transitions. Portiloop achieves high detection accuracy (>90%) because spindles have stereotyped waveform morphology visible in single channels; the PAC prediction problem is harder because the biomarker is computed across frequency bands and reflects multi-second temporal structure that no single-window classifier can fully capture. The present work complements Portiloop by demonstrating that *forecasting* (predicting future states before they occur) rather than *detection* (identifying current states) is necessary for certain closed-loop applications.

**Scalable Framework (Rashidi et al., PMC 2023).** This work proposed a general framework for closed-loop EEG-based neurofeedback using convolutional networks for brain state classification. It demonstrated classification-based closed-loop control in a real-time streaming setting but did not address temporal forecasting or the question of prediction horizon. The architecture used single-window classification rather than sequence modeling, which limits its applicability to proactive control applications where future state prediction is required. The present work identifies the prediction horizon inflection point as the key boundary above which classification-based approaches (which are implicitly single-step predictors) fail while temporal sequence models succeed.

**DBS literature (Rosin et al., Science 2011; Herron et al., J Neural Eng 2017).** Deep brain stimulation (DBS) work has demonstrated that adaptive, closed-loop stimulation (triggered by local field potential biomarkers) outperforms open-loop stimulation in Parkinson's disease. The structural analogy is clear: as in the present work, adaptive stimulation concentrates therapeutic energy on periods of genuine need. However, DBS is invasive, targets basal ganglia circuits, and uses power spectral markers (beta band suppression) rather than PAC. The present work provides a non-invasive analog for gamma entrainment in Alzheimer's disease, extending the adaptive stimulation paradigm to a population and application where invasive approaches are neither appropriate nor available.

**What is novel about this work.** Three contributions distinguish this work from the prior literature:
(1) PAC-specific temporal forecasting — no prior system forecasts theta-gamma PAC at 5–10 second horizons or characterizes the prediction horizon inflection point as a clinically meaningful boundary;
(2) horizon-dependent evaluation — the horizon sweep methodology provides a systematic characterization of when temporal modeling adds value relative to simpler methods, applicable to any EEG biomarker forecasting problem;
(3) universal per-subject validation on real patient EEG — prior deep learning closed-loop papers have typically validated on simulation or small N (5–10 subjects), while this work validates on 35 subjects with consistent per-individual results.
The combination of these three contributions — a theoretically motivated forecasting analysis, a practically validated controller, and broad subject-level evidence — provides a more complete evidence base for clinical translation than any prior work in gamma entrainment control.

---

## 7.4 Limitations

The following limitations should be understood before interpreting these results or planning follow-on work.

**1. Offline counterfactual replay, not live closed-loop.**
The primary validation replays TCN controller decisions against recorded EEG, but cannot observe the brain's response to the controller's stimulation decisions.
In a real closed-loop system, stimulation delivered during a low-PAC period would (ideally) elevate PAC in subsequent windows, creating a feedback loop that changes the brain state and therefore the subsequent PAC sequence observed by the controller.
The offline replay method cannot model this interaction — it can only assess whether the controller's decisions *would have been* aligned with the brain's natural PAC trajectory absent any stimulation effect.
This limitation is acknowledged in the validation design (Section 4.7) and means that the 72.1% alignment figure measures counterfactual decision quality, not realized therapeutic benefit.
Live closed-loop validation with real-time EEG streaming and online PAC computation is required to confirm that the decision quality translates to improved therapeutic outcomes.

**2. EEGNet is not in the validation loop.**
The closed-loop controller experiments used ground-truth PAC labels as TCN input, isolating the TCN's predictive contribution.
In a deployed system, the TCN would receive EEGNet-estimated PAC (R²=0.287) rather than ground-truth PAC, introducing estimation noise into the input feature vector.
The effect of EEGNet estimation error on TCN forecasting accuracy and controller alignment is unknown and must be characterized in future end-to-end validation.
The chained pipeline (EEGNet → feature extraction → TCN → controller) may perform differently than the idealized TCN-with-ground-truth evaluated here, and the magnitude of the degradation will determine whether further improvements to the static estimator are warranted before clinical deployment.

**3. Single-site dataset with specific population characteristics.**
The OpenNeuro ds005048 dataset was collected at a single clinical site (Tehran memory clinic) from elderly patients (likely with mild cognitive impairment or early dementia) using a specific 40 Hz amplitude-modulated auditory stimulation protocol.
Generalizability to other populations — younger healthy controls, patients at different stages of Alzheimer's disease, patients receiving different stimulation modalities (visual flicker, multi-sensory), or different EEG recording equipment — is unknown.
The training procedure does not include any explicit domain adaptation or cross-site normalization, which may limit transferability to settings with different electrode impedance characteristics, amplifier noise floors, or recording environments.

**4. Seven frontal channels and PAC labeling granularity.**
The model uses 7 frontal EEG channels (Fp1, Fp2, F3, F4, F7, F8, Fz).
Relevant theta-gamma coupling has been reported in parietal and temporal regions, which are not captured by this channel selection.
Additionally, PAC is computed at the epoch level (full 20–40 second blocks) and assigned to all constituent 2-second windows within each epoch.
This means that all windows within the same epoch share identical PAC labels, creating a target variable that is constant within epoch and discontinuous at epoch boundaries.
This labeling granularity contributes to the R²=0.287 ceiling for static prediction (Section 5.3) and introduces a training signal that is not perfectly aligned with within-epoch PAC dynamics.
Future work could use shorter epoch windows for PAC computation, or compute a sliding-window PAC estimate with 50% overlap, to create higher-resolution target labels that would allow the model to learn finer-grained temporal PAC structure.

**5. The R²=0.287 static ceiling may be partly due to label assignment.**
As described in point 4, epoch-level PAC assigned to 2-second windows creates a target variable that cannot reflect within-epoch PAC variation.
It is possible that a portion of the R²=0.287 gap to 1.0 reflects this labeling artifact rather than fundamental limits of EEG predictability.
This question can be addressed by comparing model performance under epoch-level vs window-level PAC labels, though window-level PAC estimation introduces its own bias-variance trade-off due to the shorter time window available for spectral analysis.
Alternatively, the ceiling could be characterized as an upper bound rather than a precise estimate by testing whether any feature set — including perfectly informative features constructed from the epoch label itself — produces R² above 0.287 on the same windows; if not, the ceiling reflects a fundamental label assignment constraint rather than a model limitation.

---

## Summary

The prediction horizon inflection point at ~3 seconds is the central mechanistic finding: it defines the boundary above which temporal sequence modeling is necessary for PAC forecasting and below which simpler baselines suffice. The proactive TCN controller exploits this forecasting advantage to achieve 72.1% alignment — 91.6% of the theoretical oracle — with universal benefit across all 35 subjects. Prior closed-loop neuromodulation work has not characterized this horizon boundary or demonstrated PAC-specific temporal forecasting; this work fills that gap. The primary limitation is that validation is offline counterfactual replay, not live feedback with real neural response. Addressing this limitation through live closed-loop trials with IRB oversight is the critical next step for clinical translation, as outlined in Section 8.
