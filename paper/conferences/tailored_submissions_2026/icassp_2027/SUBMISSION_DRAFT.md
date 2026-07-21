<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 ICASSP 2027 · priority #7
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G2 · 22% to submission · **eligibility:** ok · label: `do-not-submit-as-is`  
> **Deadline:** 2026-09-16 (61d)  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# ICASSP 2027 Draft

## Venue Fit

**Submission type:** full signal-processing paper.  
**Deadline:** full paper submission deadline 2026-09-16; paper acceptance notification 2027-01-13.  
**Tier:** high reach. ICASSP is an IEEE Signal Processing Society flagship conference.  
**Verdict:** do not submit the current manuscript as-is. The topic is signal-processing-adjacent, but the current result is better suited to SPMB because the backward-looking benchmark shows a Ridge tie and the streaming PAC estimator is not validated.
**Format note:** ICASSP requires a full conference paper, not a short abstract. Prepare in the current IEEE ICASSP template with the official page limits and the optional reference/ethics page only if allowed by the current call.

## Recommended Title If Submitting After Upgrades

Target-Availability Audits for EEG Phase-Amplitude Coupling Forecasts in Adaptive Stimulation

## Abstract Draft

Retrospective biomedical signal-processing pipelines can overestimate forecasting performance when targets summarize signal samples unavailable at decision time. We study this issue in cross-participant EEG forecasting during 40 Hz auditory stimulation. Using OpenNeuro `ds005048`, a public EEG dataset with 35 participants, we compute frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase. A 12-feature temporal convolutional network using PAC history and stimulation context achieves five-seed mean held-out `R^2 = 0.606` under complete-event PAC summaries, compared with `R^2 = 0.104` for persistence. We then audit target availability by recomputing PAC from five-second backward-looking EEG contexts. This increases unique held-out targets from 104 to 2678 and reduces adjacent target repetition from 96.2 percent to zero. Under the stricter target, TCN performance decreases to `R^2 = 0.212` and does not exceed Ridge regression at `R^2 = 0.216`. Offline replay further shows a low-PAC-coverage/high-PAC-rest calibration problem in forecast-driven stimulation decisions. These results motivate target-availability reporting and baseline audits for adaptive EEG forecasting benchmarks.

## Minimum Upgrades Before ICASSP

1. Repeat the backward-looking PAC benchmark across multiple participant splits and seeds.
2. Add confidence intervals or bootstrap uncertainty at participant level.
3. Validate a causal/streaming PAC estimator instead of zero-phase bounded-context filtering.
4. Add linear, tree, and shallow neural baselines under the backward-looking target.
5. Add ablations under the backward-looking target: PAC-only, stimulation-only, spectral-only, and combined.
6. Add a stronger signal-processing contribution, not only an application audit.

## Submission Strategy

If these upgrades are not done by early September 2026, skip ICASSP and put the time into STS, JSHS, BMES, MIT URTC, and SPMB.

## Official Sources

- `https://signalprocessingsociety.org/events/2027-ieee-international-conference-acoustics-speech-and-signal-processing-icassp`
- `https://2027.ieeeicassp.org/wp-content/uploads/sites/13/2019/08/ICASSP2027-CallForPapers-draft-Jun7.pdf`
