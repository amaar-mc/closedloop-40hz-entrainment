<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 SCCUR 2026 · priority #14
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G2 · 28% to submission · **eligibility:** conditional · label: `conditional-eligibility`  
> **Deadline:** 2026-10-09 (84d)  
> ⚑ **Integrity:** no-fabricated-mentor, ai-policy-unknown-default-red  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# SCCUR 2026 Draft

## Venue Fit

**Venue:** Southern California Conferences for Undergraduate Research, 2026 at San Diego State University.  
**Best submission type:** Poster, with oral acceptable if the portal allows preference.  
**Deadline:** abstract submission is open now; registration opens 2026-07-31; final abstract deadline 2026-10-09; conference 2026-11-21.  
**Eligibility caveat:** SCCUR is undergraduate-focused. High-school students are listed as eligible only when they have participated in sustained college-level or equivalent faculty-guided research or creative activity. If this project is fully independent, email `2026sccur@sdsu.edu` before submitting.
**Format constraint:** title should be no more than 200 characters; abstract should be no more than 1,500 characters and should not include citations or references.

## Recommended Title

Stress-Testing an EEG Forecasting Model for Adaptive Auditory Stimulation

## 1500-Character Abstract Draft

Adaptive stimulation systems need EEG features that can be estimated before a control decision. This project tested whether a frontal phase-amplitude-coupling feature could be forecast across participants during 40 Hz auditory stimulation, and whether the conclusion changed when the target was made closer to online use.

I analyzed OpenNeuro ds005048, a public EEG dataset with 35 memory-clinic participants. Seven frontal channels were used to compute frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase. Participants were split into 24 training, 5 validation, and 6 held-out test participants. A 12-feature temporal convolutional network used PAC history and stimulation context to predict PAC five seconds ahead.

In the initial event-summary benchmark, mean held-out R2 across five seeds was 0.606 versus 0.104 for persistence. But complete-event PAC summaries assigned to early windows could include later samples from the same event. I recomputed PAC from five-second backward-looking EEG contexts. This increased unique held-out targets from 104 to 2678 and reduced adjacent target repetition from 96.2 percent to 0.0 percent. Under this stricter benchmark, TCN performance dropped to R2=0.212 and did not beat Ridge regression at R2=0.216.

In this fixed-split stress test, target definition changed the model-selection conclusion. This audit identifies what must be validated before EEG forecasts are used in adaptive stimulation systems.

## SCCUR Optimization

- Emphasize discovery, student ownership, and clear method.
- Prefer poster if eligibility is uncertain; oral may invite harder methodological scrutiny.
- Get faculty/teacher support before submission.

## Official Sources

- `https://www.sccur.org/`
- `https://research.sdsu.edu/sccur-2026`
- `https://www.sccur.org/abstracts`
