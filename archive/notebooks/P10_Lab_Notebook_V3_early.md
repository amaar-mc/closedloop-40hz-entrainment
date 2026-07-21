# Project P10 Research Log Notebook

**Synopsys Science and Engineering Fair 2026**

## Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Phase-Amplitude Coupling in Alzheimer's Disease

**Researcher:** Amaar Chughtai  
**School:** Valley Christian High School  
**Official Notebook Timeline:** January 15, 2026 - March 1, 2026  
**Project Dataset:** OpenNeuro ds005048 - 35 dementia patients, 19 EEG channels, 250 Hz

---

## Background Framing

This notebook begins once the project question, dataset choice, and analysis plan are stable enough to keep as the official Synopsys record. Earlier December reading and brainstorming are folded into this framing note rather than reconstructed day by day. The central question is now clear: can EEG be used not only to measure current entrainment during 40 Hz auditory stimulation, but also to predict when entrainment is about to weaken so stimulation can be timed proactively?

The biological motivation is strong. Alzheimer's disease is associated with disrupted gamma activity, and prior work shows that 40 Hz sensory stimulation can drive gamma entrainment and improve disease-relevant biomarkers. The engineering gap is just as clear. Clinical protocols still use a fixed 40 second ON / 20 second OFF schedule, even though patients do not respond the same way across a session. I am treating theta-gamma phase-amplitude coupling (PAC) as the control biomarker because it captures whether gamma amplitude is actually locking to theta phase. If PAC drops, the stimulation schedule should adapt rather than continue blindly.

---

## January 15, 2026: Research Framing and Build Plan

**Daily Goal:** Lock the project question, choose the control biomarker, and outline the software path from raw EEG to controller decisions.

**Background Context:** I am narrowing the project around Alzheimer's disease, 40 Hz auditory entrainment, and closed-loop control. The literature from Iaccarino et al. (2016), Martorell et al. (2019), Lahijanian et al. (2024), Tort et al. (2010), and Lawhern et al. (2018) makes the problem concrete. Fixed stimulation schedules ignore whether the brain is still entrained. PAC gives me a measurable way to track that state.

**Procedure:** I review the OpenNeuro dataset structure and write out the minimum viable pipeline in my notes: custom data loading, preprocessing, PAC computation, model training, and controller logic. I also decide that subject-level separation is non-negotiable. If one patient's windows appear in both training and evaluation, the reported performance will be inflated and clinically meaningless.

**Results:** The project question is now specific enough to build around: can I forecast entrainment far enough ahead to make stimulation proactive instead of reactive? I commit to PAC as the control biomarker, frontal EEG as the initial signal source, and a controller-centric pipeline rather than a descriptive EEG study.

**Problems and Checks:** The main uncertainty is still technical. I do not yet know whether the MATLAB v7.3 EEG files can be loaded safely, and I do not yet know whether the useful problem formulation is static PAC estimation, temporal forecasting, or a combination of both.

**Next Step:** Start the active build once school workload eases and get the raw dataset into a form I can trust.

---

**Gap note (January 16-February 4, 2026):** I continue reading, planning, and sketching the pipeline during this stretch, but I do not have enough day-level repository evidence to justify dense dated entries. The work here is real but light: PAC method selection, notebook planning, split-leakage precautions, and review of habituation literature. I keep this interval summarized rather than padded with unsupported detail.

---

## February 6, 2026: First End-to-End Pipeline Build

**Daily Goal:** Get the raw dataset loading correctly and connect the first end-to-end path from EEG files to trainable windows.

**Background Context:** The ds005048 files are not a clean plug-and-play EEG import. The `.set` files use MATLAB v7.3 HDF5 structure, and the signal itself lives in companion `.fdt` binary files. This is the first real engineering gate in the project because every later result depends on the loader being exactly right.

**Procedure:** I build a custom loader that reads the `.set` metadata with `h5py`, resolves the companion `.fdt` file, and reshapes the binary signal array in Fortran order rather than the default C order. I validate the output by checking signal dimensions, channel layout, and whether the spectral content looks physiologic rather than scrambled. Once the raw load is stable, I connect preprocessing, epoch-level PAC computation, window extraction, subject-level splits, baseline training code, controller scaffolding, personalization logic, and validation utilities into one working path.

**Results:** The loader finally becomes trustworthy. All 35 subjects can be read consistently, and the processed dataset settles into the representation I want to use for the static task: 7 frontal channels (`Fp1`, `Fp2`, `F3`, `F4`, `F7`, `F8`, `Fz`), 2-second windows, and subject-level splits of 24 train / 5 validation / 6 test subjects. The full processed set contains 17,283 windows. PAC is computed at the epoch level for stability and then assigned to the constituent windows so the labels stay numerically usable.

**Problems and Checks:** The most important bug today is the matrix order. Without `order='F'`, the data still looks superficially plausible, which makes it dangerous. I treat that as a warning sign for the rest of the project: good-looking results are not enough unless the data path has been audited.

**Next Step:** Start training and compare several static PAC predictors before assuming that any one architecture is the answer.

---

## February 16, 2026: Architecture Marathon and Leakage Correction

**Daily Goal:** Push static PAC prediction as far as it will go and test whether model capacity is the real bottleneck.

**Background Context:** With the data path working, I expect that a better architecture might raise static PAC accuracy substantially. I start the day assuming the problem is architectural. By the end of the day, that assumption is mostly gone.

**Procedure:** I train and compare a series of static PAC models that span simple linear baselines, compact EEG-specific networks, and much larger deep architectures. I also test feature-rich hybrids that combine handcrafted spectral summaries with learned components. Whenever a result jumps sharply, I inspect the feature set and the dependence structure before keeping it.

**Results:** The official static comparison stabilizes at the following values:

| Architecture          | Parameters | Test R^2 | Interpretation                    |
| --------------------- | ---------: | -------: | --------------------------------- |
| EEGNet (V1)           |       1457 |    0.287 | Compact baseline and tied best    |
| SpecTempNet (V3)      |       180K |    0.236 | Usable only after leakage removal |
| ViT-TCNet (V4)        |        ~2M |    0.252 | Larger model, no real gain        |
| Ridge Regression (V5) |  135 coefs |    0.287 | Matches EEGNet exactly            |
| ATCNet (V8)           |        25K |    0.075 | Underperforms badly               |

An intermediate `R^2 = 0.69` appears when the spectral-temporal model is allowed to see Modulation Index features that already encode the target. The number looks exciting for a few minutes, but the feature audit makes the problem obvious: the model is reading PAC to predict PAC. I remove the circular features, rerun the model, and keep the corrected `R^2 = 0.236` instead.

The deeper lesson arrives when Ridge Regression ties EEGNet at `R^2 = 0.287`. A model with 135 coefficients is matching the best neural model I have. At that point the interpretation changes. The static ceiling is no longer a missing-architecture problem. It looks like a data-and-label problem: short windows, noisy PAC, and a limited number of patients.

**Problems and Checks:** Data leakage is the main danger today. I explicitly drop the leaked intermediate result from the official notebook record. I also keep the comparison honest by not hiding the failures of delta-style and other side experiments that do not beat the baseline.

**Next Step:** Stop asking how to predict the current PAC value a little better and start asking whether future PAC can be predicted far enough ahead to matter for control.

---

## February 17, 2026: Temporal Forecasting Pivot and Multiscale Causal TCN

**Daily Goal:** Reformulate the project around future PAC prediction and build the first causal temporal model.

**Background Context:** The static ceiling around `R^2 = 0.287` is too stable to ignore. A closed-loop controller does not actually need a perfect estimate of the current state. It needs lead time. If I can say where PAC is heading 5-10 seconds from now, the controller can intervene before entrainment fades.

**Procedure:** I redesign the problem as sequence forecasting. Each timestep now carries 73 causal features built from the recent history: 61 spectral features, 7 PAC-history features, and 5 stimulation-context features extracted from the BIDS event structure. I use a 20-second lookback window, a 5-second prediction horizon, and left-only causal padding so the model never sees future samples. The temporal model is a compact MultiscaleCausalTCN with dilations `[1, 2, 4, 8]`, a 31-step receptive field, and about 31,043 parameters.

| Feature Group        | Count | Role                                              |
| -------------------- | ----: | ------------------------------------------------- |
| Spectral features    |    61 | Current EEG state across frontal channels         |
| PAC-history features |     7 | Current value, moving averages, and trends        |
| Stimulation context  |     5 | ON/OFF state, timing since switch, cycle position |

**Results:** The temporal formulation is immediately more promising from a control perspective than the static one. The new feature set lets the model see not just what the brain is doing now, but what the stimulation schedule has been doing to it over the last 20 seconds. The causal design also makes the final deployment story more believable because every feature is available online.

**Problems and Checks:** Target definition becomes the new risk. Smoothed targets look much easier than raw PAC, so I make a note today that any strong temporal result will need to be separated into "smoothed state tracking" and "raw noisy PAC forecasting" before I present it.

**Next Step:** Audit the temporal pipeline carefully and only keep claims that survive leakage, split, and target-definition checks.

---

## February 18, 2026: Audit and Methodology Hardening

**Daily Goal:** Make the temporal pipeline harder to fool myself with and write down the assumptions explicitly.

**Background Context:** Yesterday's temporal results are encouraging, but encouragement is not the same as evidence. The project already taught me once that a flattering number can be caused by leakage or by a target that is easier than it looks.

**Procedure:** I audit the sequence builder, normalization path, and evaluation logic. I check that subject boundaries are preserved, that every target index comes strictly after the end of its input sequence, and that scalers are fit on the training subjects only. I also document the difference between raw-target forecasting and smoothed-target forecasting so I do not accidentally report one as if it were the other.

**Results:** The main integrity checks pass. Subject overlap stays at zero. Temporal construction is causal. The train-only normalization rule holds. A shuffled-label sanity run gives `R^2 = -0.332`, which is exactly what I want to see if the model is learning real structure rather than exploiting bookkeeping artifacts. Writing the methodology also forces a more honest limitation statement: the temporal model relies heavily on PAC history, so in live deployment those inputs will eventually have to come from a noisy real-time estimator rather than ground-truth labels.

**Problems and Checks:** The key communication problem is now obvious. A high number on a smoothed target can sound better than it really is if I do not explain why the target is easier. I am also careful not to blur "pipeline audit complete" with "controller validation complete" - those are separate milestones.

**Next Step:** Run the horizon sweep and show exactly where the TCN adds value over persistence and Ridge baselines.

---

## February 19, 2026: Horizon Sweep, Habituation Check, and Closed-Loop Integration

**Daily Goal:** Find the useful forecasting horizon, connect the predictor to the controller, and check whether the real dataset actually shows patient-to-patient habituation differences.

**Background Context:** If the TCN only helps at 1 second, it is not worth the added complexity. The controller needs a forecast horizon long enough to act on. At the same time, the whole adaptive-scheduling motivation depends on real subjects responding differently across repeated stimulation.

**Procedure:** I run the horizon sweep across multiple forecast lengths and compare the TCN against two baselines: persistence (`future PAC = current PAC`) and Ridge Regression on the same temporal feature set. I then inspect PAC trajectories across stimulation blocks to see whether the population behaves uniformly or splits into different response types. Finally, I wire the temporal model into the controller path with personalization and hysteresis so the output can be turned into actual stimulate/rest decisions.

**Results:** The horizon sweep gives the clearest technical result in the project.

| Horizon | Persistence R^2 | Ridge R^2 | TCN R^2 |
| ------- | --------------: | --------: | ------: |
| 1 s     |           0.760 |     0.812 |   0.735 |
| 5 s     |          -0.267 |    -0.393 |   0.254 |
| 10 s    |          -0.256 |    -0.212 |   0.278 |

At 1 second, the simple baselines win. At 5-10 seconds, both baselines collapse below zero while the TCN stays positive around `R^2 ~ 0.25`. That is the value proposition. The model does not win by being universally better. It wins specifically at the medium horizons that matter for proactive control.

The habituation check is equally important. There is no strong population-wide decline across the short sessions, but the subject-level spread is large:

| Response Pattern                             |         Count | Range          |
| -------------------------------------------- | ------------: | -------------- |
| Subjects declining across stimulation blocks | 17/35 (48.6%) | -66.8% to -5%  |
| Subjects stable or increasing                | 18/35 (51.4%) | +5% to +149.1% |

The average hides the real story. Roughly half the cohort trends downward and half does not. That means a single fixed schedule is a poor fit for the group as a whole even if the population mean looks stable.

The controller path now has the right structure for testing: EEG-derived current state, temporal forecast, personalized baseline, and a decision rule with hysteresis so the controller does not flicker on and off.

**Problems and Checks:** The habituation analysis comes with an honest caveat. These sessions are only about 6-10 minutes long, while clinical sessions are often 30-60 minutes. I can show heterogeneity now, but I cannot prove how it will evolve over a full treatment session.

**Next Step:** Build replay analysis and robustness experiments so the controller can be judged on real subject trajectories and not just on model metrics.

---

## February 21, 2026: Replay Framework, Robustness Setup, and Fatigue Sensitivity

**Daily Goal:** Build the replay-analysis framework, pressure-test the adaptive advantage under multiple fatigue assumptions, and tighten the statistical story before the final real-data TCN lock.

**Background Context:** The project is now close to a judge-facing form, which means the weak spots need to be identified on purpose. I want a replay framework on real trajectories, stronger statistics for the simulation side, and a clear answer if someone asks whether the adaptive advantage only appears because I chose a convenient fatigue model.

**Procedure:** I set up replay tooling that can run different controllers against recorded subject trajectories without claiming a live closed loop. In parallel, I re-run the simulation side with stronger statistics, multiple fatigue severities, and four different mathematical fatigue models. I also formalize the ML/AI compliance and interpretability notes so the project is explicit about what is validated and what is still a limitation.

**Results:** The simulation-side adaptive advantage holds across both severity sweeps and model families.

**Fatigue severity sweep**

| Fatigue Level | Fixed Efficiency | Adaptive Efficiency | Improvement |
| ------------- | ---------------: | ------------------: | ----------: |
| None          |            0.343 |               0.375 |       +9.5% |
| Mild          |            0.341 |               0.375 |      +10.0% |
| Moderate      |            0.335 |               0.366 |       +9.0% |
| High          |            0.319 |               0.354 |      +10.8% |
| Severe        |            0.316 |               0.352 |      +11.2% |

**Fatigue-model robustness**

| Fatigue Model         | Advantage |      P-value | Hedges' g |
| --------------------- | --------: | -----------: | --------: |
| Exponential Decay     |     +9.0% | 1.8 x 10^-15 |      2.31 |
| Step Function         |     +6.9% | 4.4 x 10^-14 |      1.21 |
| Heterogeneous (50/50) |     +8.9% | 2.5 x 10^-14 |      1.71 |
| Saturation (synaptic) |    +19.0% | 1.8 x 10^-15 |      3.66 |

These results tell me the adaptive advantage is not tied to one narrow simulator choice. The exact gain changes with the fatigue mechanism, but the sign of the effect does not flip.

I also use this rigor pass to check whether the static ceiling was caused by an undersized baseline. A larger `EEGNetLarge` model at roughly 141K parameters still lands at `R^2 = 0.287`, which supports the same working conclusion as February 16: more capacity is not rescuing the static task.

**Problems and Checks:** I am careful not to overclaim what is finished today. The replay framework is in place, but the final TCN-integrated real-data validation is not yet the locked result. I also keep the concept-level predictive simulation separate from the later TCN replay on real EEG so the notebook does not blur those two stages.

**Next Step:** Finish the final TCN replay on all 35 subjects, generate the figure-ready comparison, and freeze the controller table only when the run is complete.

---

**Gap note (February 22-February 25, 2026):** I use this span for threshold checks, cleanup, figure plumbing, and validation preparation, but I do not claim the final 72.1% controller result yet. The work is transitional: tightening scripts, resolving presentation details, and preparing the real-data replay run that will lock the final comparison.

---

## February 26, 2026: Real-Data TCN Validation Locked

**Daily Goal:** Run the final TCN-integrated replay analysis on all 35 subjects and freeze the controller comparison for the fair materials.

**Background Context:** This is the milestone that moves the project from promising forecasting to a real controller comparison on recorded patient data. The purpose of the replay is narrow and important: measure whether the TCN makes better stimulation decisions than fixed and reactive baselines when evaluated on the actual EEG/PAC trajectories from the dataset.

**Procedure:** I replay the controller against all 35 subjects' recorded sessions and compare four policies: Fixed Schedule, Reactive Threshold, TCN Predictive, and an Oracle upper bound. For this validation pass, ground-truth PAC labels are used as the TCN input so the replay isolates the predictive contribution of the temporal model rather than mixing it with the upstream EEGNet estimation error. I keep the evaluation offline and counterfactual, which lets me test decisions on real brain data without pretending I have live closed-loop feedback.

**Results:** The final controller table is strong and internally consistent.

| Controller         | Alignment | Low-PAC Targeting | PAC Gap (x10^-6) |    Stim % |
| ------------------ | --------: | ----------------: | ---------------: | --------: |
| Fixed Schedule     |     45.0% |             61.4% |             -6.6 |     66.6% |
| Reactive Threshold |     64.5% |             51.7% |            +21.1 |     36.7% |
| **TCN Predictive** | **72.1%** |         **82.6%** |        **+30.5** | **59.7%** |
| Oracle             |    100.0% |            100.0% |            +33.3 |     48.3% |

Three points stand out immediately. First, the fixed schedule is not just weaker - its PAC gap points in the wrong direction, which means the timing is poorly aligned to need. Second, the TCN reaches about 92% of the oracle PAC-targeting gap (`30.5` versus `33.3`). Third, the TCN improves low-PAC targeting from `51.7%` to `82.6%`, and every one of the 35 subjects shows higher utility with the predictive controller than with the reactive one.

The pairwise statistics against the reactive controller are also strong: alignment `g = 1.31`, low-PAC targeting `g = 4.47`, and PAC gap `g = 1.57`, all with `p < 0.001`. I keep the notebook centered on the simplified four-policy table here so the written record matches the final locked comparison exactly.

**Problems and Checks:** I keep one limitation visible even on the strongest day in the notebook. This is still offline replay on recorded EEG, not a live streaming system that can observe how the brain responds to its own decisions in real time. I also label PAC gap as dimensionless `x10^-6` throughout this entry to avoid the unit mistake that appeared in earlier drafts.

**Next Step:** Freeze the science and move into packaging - notebook, poster, abstract, figures, and wording all need to say the same thing.

---

## March 1, 2026: Documentation Freeze and Submission Packaging

**Daily Goal:** Consolidate the final notebook, poster, abstract, and figure set into a submission-ready package without changing the science.

**Background Context:** I am treating this as a documentation-freeze day rather than a new science day. The project does not need another architecture or another metric now. It needs consistency. Every table, figure caption, and headline claim has to agree on the same dates, the same units, and the same interpretation.

**Procedure:** I go through the final materials and keep the narrative disciplined. The poster emphasizes the controller comparison, the horizon sweep, and the robustness results. The notebook keeps the build-debug-validate arc instead of turning into a polished retrospective paper. I also make sure the limitations remain visible: single public dataset, short sessions, offline replay rather than live closed loop, and temporal prediction that still depends heavily on PAC history.

**Results:** The project package is now coherent across its main components. The static story is honest about the `R^2 = 0.287` ceiling. The temporal story is honest about where the TCN wins and where simple baselines still win. The controller story is anchored to the locked February 26 replay table. The robustness story stays in the simulation lane rather than being mixed into the real-data validation claims.

**Problems and Checks:** The main risk at this stage is narrative drift - changing wording in one document and forgetting to update the others. I am treating the poster numbers as the final public truth source for the fair-facing materials and checking the notebook against that standard.

**Next Step:** Export the final notebook PDF, print the fair materials, and keep the presentation focused on the evidence that survives audit.

---

## References

1. Iaccarino, H. F., et al. (2016). Gamma frequency entrainment attenuates amyloid load and modifies microglia. _Nature_, 540(7632), 230-235.
2. Martorell, A. J., et al. (2019). Multi-sensory gamma stimulation ameliorates Alzheimer's-associated pathology and improves cognition. _Cell_, 177(2), 256-271.
3. Tort, A. B., et al. (2010). Measuring phase-amplitude coupling between neuronal oscillations of different frequencies. _Journal of Neurophysiology_, 104(2), 1195-1210.
4. Lawhern, V. J., et al. (2018). EEGNet: A compact convolutional neural network for EEG-based brain-computer interfaces. _Journal of Neural Engineering_, 15(5), 056013.
5. Lahijanian, M., et al. (2024). Auditory gamma-band entrainment enhances default mode network connectivity in dementia patients. _Scientific Reports_, 14, 13153.
6. Thompson, R. F., & Spencer, W. A. (1966). Habituation: a model phenomenon for the study of neuronal substrates of behavior. _Psychological Review_, 73(1), 16-43.
