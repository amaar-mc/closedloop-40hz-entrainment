<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 BMES 2026 HS Poster Expo · priority #1
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G4 · 67% to submission · **eligibility:** ok · label: `strong-fit`  
> **Deadline:** 2026-08-14 (28d)  
> ⚑ **Integrity:** ai-policy-unknown-default-red  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# BMES 2026 High School Poster Expo Draft

## Venue Fit

**Best submission type:** High School Poster Expo.  
**Meeting:** BMES 2026 Annual Meeting, 2026-10-21 to 2026-10-24 in Orlando.  
**Deadline:** 2026-08-18; applicants notified on or before 2026-08-25.  
**Audience:** biomedical engineering community, professors, trainees, and industry reviewers.  
**Fit angle:** engineering a safer validation benchmark for adaptive neurotechnology, not proving treatment benefit.  
**Eligibility note:** high-school juniors/seniors by Fall 2026; under-18 students need an adult/guardian.
**Registration note:** accepted students and chaperones each receive a discounted $100 registration rate; student and chaperone registrations are separate.
**Format note:** BMES points applicants to an abstract template with title, introduction, methods, results/discussion, conclusion, and optional acknowledgements/references. One figure or table may be embedded if the portal/template permits. Do not write "results will be presented."

## Recommended Title

Engineering a Retrospective EEG Benchmark for Adaptive Auditory Stimulation

## Template-Structured Poster Abstract Draft

### Introduction

Adaptive neuromodulation systems require EEG features that can be estimated and forecast before stimulation decisions are made. This project tested whether a frontal EEG phase-amplitude-coupling feature could support adaptive 40 Hz auditory-stimulation timing in retrospective data, while auditing whether the target definition was realistic for a future online system.

### Materials and Methods

I analyzed OpenNeuro `ds005048`, a public auditory-stimulation EEG dataset with 35 memory-clinic participants. Seven frontal channels were used to compute frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase. Participants were split into 24 training, 5 validation, and 6 held-out test participants. A compact 12-feature temporal convolutional network used PAC history and recorded stimulation timing to forecast PAC five seconds ahead.

### Results and Discussion

In an initial event-summary benchmark, the 12-feature model achieved held-out test `R^2 = 0.558`, and across five training seeds reached mean `R^2 = 0.606`, compared with `R^2 = 0.104` for persistence. Because event-summary PAC labels assigned complete-period values back to earlier windows, I then recomputed PAC from five-second backward-looking EEG contexts. This removed adjacent target repetition and increased unique held-out targets from 104 to 2,678. Under this stricter benchmark, TCN performance dropped to `R^2 = 0.212`, approximately matching Ridge regression at `R^2 = 0.216`.

### Conclusion

Offline replay of a predictive stimulation policy showed a controller-calibration problem: low-PAC stimulation coverage improved, but the above-median-PAC rest rate declined. The result is a biomedical engineering lesson: before adaptive stimulation can be tested prospectively, feature availability, model baselines, and controller objectives must be validated together.

## Why This Is BMES-Optimized

- Leads with biomedical engineering design requirements.
- Treats PAC as a scalar EEG timing target, not a clinical endpoint.
- Highlights validation and safety before deployment.
- Avoids overclaiming disease treatment.

## Poster Sections

1. Motivation: adaptive stimulation needs live-available EEG features.
2. Dataset: OpenNeuro auditory-stimulation EEG, 35 participants.
3. Model: 12-feature TCN, participant-disjoint split.
4. Key stress test: event-summary PAC versus backward-looking PAC.
5. Controller replay: low-PAC coverage versus above-median-PAC rest rate.
6. Takeaway: target-definition audits are required before prospective adaptive systems.

## Official Sources

- `https://www.bmes.org/2026/annualmeeting/high-school-poster-expo`
- `https://www.bmes.org/2026/annualmeeting/abstracts`
