<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 SfN 2026 (late-breaking) · priority #15
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G2 · 22% to submission · **eligibility:** blocked · label: `membership-blocked`  
> **Deadline:** 2026-09-15 (60d)  
> ⚑ **Integrity:** membership-gate-hard-blocker  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# SfN Neuroscience 2026 Late-Breaking Draft

## Venue Fit

**Submission type:** late-breaking abstract only.  
**Window:** 2026-09-08 to 2026-09-15 or until cap.  
**Length:** abstract body no more than 2,300 characters, excluding spaces.  
**Risk:** submit only if there is genuinely new analysis after the regular abstract deadline. Current results alone may not satisfy the spirit of late-breaking work.
**Presenter constraint:** verify the current SfN membership, presenter, fee, and abstract-sponsor requirements before using this. Treat this as blocked unless the presenting author and any sponsor/member requirements are satisfied.

## Recommended Title

Target Availability Alters Cross-Participant EEG PAC Forecasting During 40 Hz Auditory Stimulation

## Abstract Body Draft

Adaptive neuromodulation requires EEG features that can be estimated before stimulation decisions are made. We tested whether frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase, could be forecast across participants during auditory stimulation, and whether the conclusion depended on target availability. We analyzed OpenNeuro `ds005048`, a public 40 Hz auditory-stimulation EEG dataset containing 35 memory-clinic participants. Seven frontal channels were used to compute PAC from `4-8 Hz` phase and `38-42 Hz` amplitude. Participants were split into 24 training, 5 validation, and 6 held-out test participants. A compact 12-feature temporal convolutional network used PAC-history and stimulation-context inputs to forecast PAC five seconds ahead.

Under complete-event PAC summaries assigned back to constituent windows, the selected TCN achieved five-seed mean held-out `R^2 = 0.606`, compared with `R^2 = 0.104` for persistence. Because those event summaries can assign early windows values computed from later samples in the same event, we recomputed PAC from five-second backward-looking EEG contexts. This increased unique held-out targets from 104 to 2,678 and reduced adjacent target repetition from 96.2 percent to zero. Under this stricter single-seed benchmark, TCN performance decreased from `R^2 = 0.554` to `R^2 = 0.212` and did not exceed Ridge regression at `R^2 = 0.216`. Offline replay further showed that a predictive policy increased low-PAC stimulation coverage but reduced the above-median-PAC rest rate relative to reactive thresholding.

These results suggest that target construction can substantially change apparent EEG forecasting performance. PAC estimates here are scalar EEG timing targets, not definitive evidence of physiological theta-gamma coupling or therapeutic response. Prospective adaptive-stimulation studies should validate streaming-compatible PAC estimation, repeated participant-split robustness, and controller calibration before live testing.

## Submit / Do Not Submit

- Submit only if the portal allows this as late-breaking and the work is updated with new robustness analysis completed after the regular deadline.
- If no new results are added, prioritize MIT URTC, BMES, SCCUR, STS, and JSHS instead.

## Official Sources

- `https://www.sfn.org/meetings/neuroscience-2026/call-for-abstracts`
- `https://www.sfn.org/meetings/neuroscience-2026/call-for-abstracts/how-to-submit`
- `https://www.sfn.org/meetings/neuroscience-2026/general-information/dates-and-deadlines`
