<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 BCI Award 2026 · priority #6
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** no (supporting file)  
> **Venue phase:** gate G2 · 22% to submission · **eligibility:** ok · label: `optional-stretch`  
> **Deadline:** 2026-09-01 (46d)  
> ⚑ **Integrity:** ai-policy-unknown-default-red  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# BCI Award 2026 Draft

## Venue Fit

**Submission type:** project award application.  
**Deadline:** 2026-09-01.  
**Required artifact:** PDF project description in English, maximum two pages, plus a short 16:9 project film. Both are required for a complete award package.  
**Fit caveat:** this is a stretch. The project is adaptive stimulation/neurotechnology, not a conventional BCI. Use only if the award accepts broader BCI/neurotechnology projects and if the submission can be framed as a validation method for closed-loop systems.
**Scoring caveat:** the BCI Award explicitly rewards online or real-time function, user benefit, accuracy/speed improvement, and patient or potential-user results. This project is offline and retrospective, so it is a low-probability stretch unless presented as an audit method rather than a finished BCI.

## Recommended Project Title

Auditing EEG Feature Forecasts Before Adaptive Neurostimulation

## Project Summary Draft

Closed-loop neurotechnology depends on predictive signal features that are available at the time a system makes a decision. I developed a retrospective EEG benchmark to test this requirement in the context of adaptive 40 Hz auditory stimulation. Using OpenNeuro `ds005048`, a public dataset of 35 memory-clinic participants, I built a participant-disjoint forecasting pipeline for frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase.

The initial model appeared strong: a compact 12-feature temporal convolutional network reached five-seed mean held-out `R^2 = 0.606`, outperforming persistence at `R^2 = 0.104`. I then audited the target definition and found that complete-event PAC summaries assigned to early windows could include later EEG samples from the same event. A stricter backward-looking benchmark recomputed PAC from five-second EEG contexts, increasing unique held-out targets from 104 to 2,678 and eliminating repeated adjacent targets. Under this stricter target, the TCN dropped to `R^2 = 0.212` and did not outperform Ridge regression at `R^2 = 0.216`.

The project's contribution is a practical information-boundary audit for adaptive neurotechnology. It shows that model complexity is less important than validating whether the EEG target is available, whether simple baselines perform similarly, and whether controller decisions balance low-PAC coverage and high-PAC sparing. This framework can help prevent premature claims in future closed-loop EEG systems.

## Award Pitch

The strongest pitch is not "I built a BCI." It is "I built a validation method that catches a common failure mode before adaptive neurotechnology reaches live deployment."

## Official Sources

- `https://www.bci-award.com/Home`
