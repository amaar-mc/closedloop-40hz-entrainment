<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 AAN Neuroscience Prize · priority #3
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** research report · **Canonical:** no (supporting file)  
> **Venue phase:** gate G2 · 28% to submission · **eligibility:** ok · label: `confirmed-open`  
> **Deadline:** 2026-10-20 (95d)  
> ⚑ **Integrity:** no-fabricated-mentor, mentor-esignature-required  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# AAN Neuroscience Research Prize Report Draft

## Title

Testing Whether EEG PAC Forecasts Survive a More Realistic Target Definition

## Abstract

Use the 300-word abstract in `SUBMISSION_DRAFT.md`.

## Introduction

Adaptive neurostimulation systems require EEG features that are available before stimulation decisions are made. Forty-hertz auditory stimulation has been studied in neurodegeneration contexts, but this project does not test treatment response. Instead, it asks whether a frontal EEG phase-amplitude-coupling feature can be forecast across participants during stimulation, and whether the result changes when the target is computed from backward-looking EEG rather than complete event summaries.

This distinction is important for neuroscience methods. A retrospective label may be stable because it summarizes a full event, but an adaptive system cannot use signal samples that occur after the decision point. If model performance depends on such a target definition, the forecasting result may not transfer to an online controller.

## Methods

The analysis used OpenNeuro `ds005048`, a public 40 Hz auditory-stimulation EEG dataset containing 35 memory-clinic participants. Seven frontal channels were analyzed: `Fp1`, `Fp2`, `F7`, `F3`, `Fz`, `F4`, and `F8`. PAC was computed using theta phase from `4-8 Hz` and 40 Hz amplitude from `38-42 Hz`, then averaged across the frontal channels as a scalar EEG timing target.

Participants were split into 24 training, 5 validation, and 6 held-out test participants. The forecasting model used 20 steps of history to predict PAC five steps ahead. The selected model was a compact 12-feature temporal convolutional network using PAC-history and stimulation-context inputs. Performance was compared with persistence and Ridge regression.

The main methodological audit recomputed PAC from five-second backward-looking EEG contexts. This stricter target definition was designed to reduce the future-sample availability problem created by complete-event PAC summaries.

## Results

Under complete-event PAC summaries, the selected TCN achieved five-seed mean held-out `R^2 = 0.606`, compared with `R^2 = 0.104` for persistence. This suggested that the stored PAC series contained predictable cross-participant structure.

The target-definition audit changed the interpretation. Complete-event PAC summaries produced only 104 unique held-out targets and 96.2 percent adjacent target repetition. Backward-looking PAC increased unique held-out targets to 2678 and reduced adjacent target repetition to zero. Under this stricter target, TCN performance decreased to `R^2 = 0.212` and did not exceed Ridge regression at `R^2 = 0.216`.

Offline replay of a predictive stimulation policy showed a tradeoff rather than solved control. The predictive policy increased stimulation during low-PAC periods relative to a reactive threshold policy, 73.8 percent versus 51.7 percent, but reduced rest during high-PAC periods, 50.7 percent versus 77.3 percent.

## Discussion

The main finding is that target definition changed the model conclusion in this fixed-split stress test. The event-summary benchmark made the nonlinear forecasting model appear strong, but the stricter backward-looking benchmark showed that a linear baseline performed similarly. This does not mean the project failed; it identifies a methodological problem that must be solved before EEG forecasts are used in adaptive stimulation systems.

The study has important limitations. It is retrospective, uses one public dataset, treats PAC as a scalar timing target rather than a confirmed physiological endpoint, and does not test a live controller. The backward-looking PAC stress test is closer to online availability than complete-event labels, but it is not yet a validated streaming PAC estimator.

## Conclusion

Frontal EEG PAC forecasting showed structure in retrospective data, but the apparent model advantage depended on the target definition. Future adaptive-stimulation studies should validate streaming-compatible features, repeat participant-level validation, and report simple baselines before testing live controllers.

## Bibliography

[1] M. Lahijanian, H. Aghajan, and Z. Vahabi, "Auditory gamma-band entrainment enhances default mode network connectivity in dementia patients," Scientific Reports, vol. 14, art. 13153, 2024.

[2] M. Lahijanian, H. Aghajan, and Z. Vahabi, "40Hz Auditory Entrainment," OpenNeuro dataset `ds005048`, version `1.0.1`, doi:10.18112/openneuro.ds005048.v1.0.1.

[3] A. B. L. Tort, R. Komorowski, H. Eichenbaum, and N. Kopell, "Measuring phase-amplitude coupling between neuronal oscillations of different frequencies," Journal of Neurophysiology, vol. 104, no. 2, pp. 1195-1210, 2010.

[4] J. Aru, J. Aru, V. Priesemann, et al., "Untangling cross-frequency coupling in neuroscience," Current Opinion in Neurobiology, vol. 31, pp. 51-61, 2015.
