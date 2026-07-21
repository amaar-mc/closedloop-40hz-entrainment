<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 MIT URTC 2026 (poster/lightning) · priority #4
>
> **Doc status:** REFERENCE — supporting material (layout/plan/script/checklist)  
> **Artifact type:** poster layout · **Canonical:** no (supporting file)  
> **Venue phase:** gate G8 · 89% to submission · **eligibility:** ok · label: `strong-default`  
> **Deadline:** no date posted  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# MIT URTC Poster Layout and Lightning Script

## Poster Layout

**Title:** Stress-Testing PAC Forecasts for Adaptive 40 Hz Auditory Stimulation

**Panel 1: Problem**

Fixed 40 Hz auditory-stimulation schedules cannot respond to short-term EEG state. A future adaptive system would need an EEG feature that is available before the controller decides whether to stimulate.

**Panel 2: Dataset**

OpenNeuro `ds005048`, 35 memory-clinic participants, 19-channel EEG at 250 Hz. This project used seven frontal channels and split participants into 24 train, 5 validation, and 6 held-out test participants.

**Panel 3: Feature and Model**

Operational PAC feature: theta phase `4-8 Hz` and 40 Hz amplitude `38-42 Hz`, averaged across frontal channels. Forecasting model: compact 12-feature TCN using PAC history plus stimulation context.

**Panel 4: Result That Looked Strong**

Event-summary PAC benchmark: five-seed mean held-out `R^2 = 0.606`, compared with `R^2 = 0.104` for persistence.

**Panel 5: The Audit**

Complete-event PAC labels assigned to early windows could include later signal samples. Backward-looking PAC recomputation increased unique held-out targets from 104 to 2678 and removed adjacent target repetition.

**Panel 6: Corrected Conclusion**

Under backward-looking PAC, TCN performance dropped to `R^2 = 0.212` and did not exceed Ridge regression at `R^2 = 0.216`. Target definition mattered more than neural-network complexity.

**Panel 7: Controller Replay**

Predictive replay increased low-PAC stimulation coverage, 73.8 percent versus 51.7 percent for reactive thresholding, but reduced the above-median-PAC rest rate, 50.7 percent versus 77.3 percent.

**Panel 8: Takeaway**

Before adaptive auditory stimulation is tested live, the EEG target, simple baselines, and controller objective need to be validated under online information boundaries.

## Five-Minute Lightning Script

I tested a failure mode in retrospective EEG forecasting for adaptive auditory stimulation.

The goal was not to prove a treatment effect. The engineering question was narrower: if a future controller needed to decide whether to deliver 40 Hz auditory stimulation, could a frontal EEG PAC feature be forecast before that decision?

I used OpenNeuro ds005048, a public auditory-stimulation EEG dataset with 35 memory-clinic participants. I computed frontal phase-amplitude coupling as a scalar EEG timing target and split the data by participant into training, validation, and held-out test sets.

The first result looked strong. A compact 12-feature temporal convolutional network reached five-seed mean held-out R2 of 0.606, while persistence reached 0.104.

Then I audited the target. The original PAC labels were complete-event summaries assigned back to shorter windows, so early windows could inherit information from later samples in the same event. I recomputed PAC using five-second backward-looking contexts. That increased unique held-out targets from 104 to 2678 and removed adjacent repetition.

Under that stricter target, the TCN dropped to R2 of 0.212 and did not beat Ridge regression at 0.216. The core finding is that target definition changed the model conclusion in this fixed-split stress test.

I also replayed a predictive stimulation policy offline. It stimulated more low-PAC periods than a reactive threshold, but rested during fewer above-median-PAC periods, so it exposed a controller-calibration problem rather than a solved controller.

The takeaway is that adaptive EEG systems need target-availability audits before their forecasts are trusted.
