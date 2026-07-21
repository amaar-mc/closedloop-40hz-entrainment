<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 BMES 2026 (general abstract) · priority #16
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G2 · 22% to submission · **eligibility:** blocked · label: `expired-this-cycle`  
> **Deadline:** 2026-06-15 (passed)  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# BMES 2026 General Abstract Draft

## Venue Fit

**Submission type:** General abstract, professional pool.  
**Deadline status:** extended 2026 window ends 2026-06-15.  
**Required structure:** Introduction, Materials and Methods, Results/Conclusions/Discussion. BMES lists 50-250 words for Introduction and Methods, and 50-350 words for the combined Results/Conclusions/Discussion field.
**Hard caveat:** do not submit this as a high-school sole presenter unless BMES explicitly confirms eligibility. The safer BMES route is the High School Poster Expo.

## Recommended Title

Target-Definition Stress Testing of Cross-Participant EEG PAC Forecasts During 40 Hz Auditory Stimulation

## Introduction

Closed-loop neuromodulation systems require EEG features that can be estimated before a stimulation decision is made. Forty-hertz auditory stimulation has been studied in neurodegeneration contexts, but adaptive timing requires a separate engineering question: whether an EEG feature can be forecast across participants under a target definition that is available online. This retrospective study tested whether frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase, could be predicted during auditory stimulation, and whether model conclusions changed when PAC targets were recomputed from backward-looking EEG rather than complete event summaries.

## Materials and Methods

The analysis used OpenNeuro `ds005048` version `1.0.1`, a public auditory-stimulation EEG dataset containing 35 memory-clinic participants. Seven frontal channels were analyzed. PAC was computed from `4-8 Hz` theta phase and `38-42 Hz` amplitude and averaged across channels as a scalar EEG timing target. Participants were split into 24 training, 5 validation, and 6 held-out test participants. Temporal samples used a 20-step lookback and a five-step forecast horizon. A compact 12-feature temporal convolutional network using PAC-history and stimulation-context inputs was compared with persistence and Ridge baselines. A stress test recomputed PAC at each timestamp from five-second backward-looking contexts to reduce future-sample availability artifacts.

## Results, Conclusions, and Discussion

In the event-summary benchmark, the 12-feature TCN achieved held-out test `R^2 = 0.558`, compared with `R^2 = -0.025` for a 73-feature candidate representation. Across five training seeds on the fixed participant split, mean TCN `R^2` was 0.606 versus 0.104 for persistence. The event-summary target, however, repeated within stimulation periods and assigned complete-period PAC values to earlier windows. Recomputing PAC from backward-looking contexts increased unique held-out targets from 104 to 2,678 and reduced adjacent target repetition from 96.2 percent to zero. Under this stricter single-seed benchmark, TCN performance decreased to `R^2 = 0.212` and did not exceed Ridge regression at `R^2 = 0.216`. Offline controller replay increased low-PAC stimulation coverage relative to reactive thresholding, 73.8 percent versus 51.7 percent, but reduced the above-median-PAC rest rate, 50.7 percent versus 77.3 percent. These results indicate that target availability and controller calibration are central validation requirements before adaptive auditory-stimulation systems can be tested prospectively.

## Risk Note

This is an urgent professional abstract and likely the wrong pool for a 17-year-old high-school presenter. BMES states General Abstracts are for graduate, doctoral, and professional submissions only. Submit only if BMES confirms you may be presenting author, and only if the BMES account, nonrefundable extended-deadline fee, 2026-08-03 presenter registration, travel, and attendance requirements are realistic. Default to `../bmes_high_school_poster_expo/SUBMISSION_DRAFT.md`.

## Official Sources

- `https://www.bmes.org/2026/annualmeeting/abstracts`
- `https://www.bmes.org/2026/annualmeeting/high-school-poster-expo`
