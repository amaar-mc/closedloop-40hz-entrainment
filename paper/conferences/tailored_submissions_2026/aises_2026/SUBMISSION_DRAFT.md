<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 AISES 2026 · priority #12
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G2 · 22% to submission · **eligibility:** conditional · label: `open-register-gate`  
> **Deadline:** 2026-08-14 (28d)  
> ⚑ **Integrity:** honest-identity-only, ai-policy-unknown-default-red  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# AISES 2026 Student Research Presentation Draft

## Venue Fit

**Submission type:** student research poster or oral presentation.  
**Deadlines:** priority deadline 1 is 2026-07-24 at 11:59 PM PST; priority deadline 2 is 2026-08-14; final deadline is 2026-09-04.  
**Eligibility:** AISES lists middle-school through doctoral students as eligible. Tribal affiliation is optional, but the application uses an Indigenous-centered abstract framework and requires current AISES membership before submission.  
**Required fields to confirm in portal:** community-impact category, presentation preference, 3-5 keywords, presenter information, co-presenters, and acknowledgments.  
**Hard caveat:** apply only if the "what / so what / now what" community-impact framework can be answered honestly. Do not force an Indigenous or community narrative that is not real.

## Recommended Title

Auditing EEG Forecasts Before Adaptive Auditory Stimulation

## Keywords

EEG; biomedical signal processing; adaptive stimulation; machine learning; target-definition audit

## Indigenous Abstract Framework Draft

### WHAT: Situate Yourself and the Research

I am a high-school student interested in building careful biomedical AI systems. This project studies a public EEG dataset from 35 participants receiving 40 Hz auditory stimulation. I tested whether a frontal EEG phase-amplitude-coupling feature could be forecast before a future adaptive stimulation decision.

### SO WHAT: Explain Project and Findings

The first benchmark made the model look strong: a compact 12-feature temporal convolutional network reached five-seed mean held-out `R^2 = 0.606`, compared with `R^2 = 0.104` for persistence. I then audited the target definition. Complete-event PAC labels assigned to early windows could include later EEG samples, which would not be available in a real-time system. Recomputing PAC from five-second backward-looking contexts increased unique held-out targets from 104 to 2678 and removed adjacent target repetition. Under this stricter benchmark, TCN performance dropped to `R^2 = 0.212` and did not exceed Ridge regression at `R^2 = 0.216`.

### NOW WHAT: Community Impact and Next Steps

The broader impact is a validation lesson for biomedical AI: models should be audited for information availability before they are described as adaptive or deployable. The next step is to repeat the backward-looking benchmark across participant splits, validate a streaming PAC estimator, and design controller objectives that balance low-PAC coverage and high-PAC sparing.

## Submission Strategy

- Choose poster unless oral is specifically encouraged for high-school students.
- Lead with responsible biomedical-AI validation.
- Do not claim a tribal/community impact unless it is specific and true.

## Official Sources

- `https://conference.aises.org/research/student`
- `https://conference.aises.org/research/faqs`
