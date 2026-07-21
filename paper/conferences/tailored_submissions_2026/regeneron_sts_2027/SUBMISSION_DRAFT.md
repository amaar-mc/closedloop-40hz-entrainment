<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 Regeneron STS 2027 · priority #2
>
> **Doc status:** SCAFFOLD ONLY — planning aid; final text MUST be human-authored (venue AI rules)  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G1 · 11% to submission · **eligibility:** ok · label: `scaffold-only / student-must-write`  
> **Deadline:** 2026-11-05 (111d)  
> ⚑ **Integrity:** no-AI-text, no-fabricated-mentor  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# Regeneron STS 2027 Draft Core

## Venue Fit

**Application window:** 2026-06-01 to 2026-11-05 at 8 PM ET.  
**Required components:** original independent research report, recommendations, application sections, short essays, optional test scores, and disclosures of support.  
**Strategy:** STS is not about a quick conference line. It rewards scientific maturity, independence, integrity, and future potential. The best version of this project is the story of discovering and correcting a misleading target definition.
**AI-writing rule:** do not submit this generated text, or close paraphrases of it, in STS. STS rules prohibit using ChatGPT or similar tools to answer application questions or draft the research report. Use this file only as planning scaffolding, then write the application/report yourself and disclose tool use accurately.

## Recommended Project Title

Auditing EEG Target Definitions for Adaptive 40 Hz Auditory Stimulation

## Project Summary Planning Scaffold - Do Not Submit

I developed a retrospective computational neuroscience study testing whether frontal EEG phase-amplitude-coupling features could support future adaptive auditory-stimulation systems. Using OpenNeuro `ds005048`, a public dataset of 35 participants exposed to 40 Hz auditory stimulation, I built a participant-disjoint forecasting benchmark with 24 training, 5 validation, and 6 held-out test participants. An initial temporal convolutional network appeared to predict stored PAC values well, reaching five-seed mean held-out `R^2 = 0.606`. I then identified a methodological limitation: event-level PAC labels were assigned back to earlier windows, making some inputs unavailable in a real streaming system. A stricter backward-looking PAC stress test eliminated target repetition and reduced TCN performance to `R^2 = 0.212`, approximately matching Ridge regression. The final contribution is not an overclaimed clinical model. It is an audit showing that target availability, baseline comparisons, and controller calibration must be validated before EEG forecasts are treated as adaptive neuromodulation components.

## Research Report Positioning

### Problem

Closed-loop stimulation systems need EEG features that are available at decision time. Retrospective EEG pipelines can overestimate performance if labels summarize future signal samples. This project asks whether a PAC forecasting model still appears useful after its target definition is stress-tested.

### Hypothesis

PAC history and stimulation context would contain cross-participant predictive signal, but model conclusions would weaken when PAC was recomputed from backward-looking contexts.

### Methods

Use the current manuscript methods, but simplify the prose. STS readers may not all be EEG experts. Define PAC as an engineering feature, explain participant-disjoint splitting, and explain why train-only normalization matters.

### Results to Feature

1. Compact features beat the 73-feature candidate set in the event-summary benchmark.
2. Five-seed event-summary performance was positive and above persistence.
3. The backward-looking stress test changed the conclusion: the nonlinear model did not beat Ridge.
4. Controller replay showed a low-PAC-coverage/high-PAC-rest calibration problem, not a solved controller.

### Best Narrative

The strongest STS story is intellectual honesty: you built a system, found a result that looked strong, discovered why it might be misleading, ran a stricter test, and narrowed the claim. That reads as independent research maturity.

## Required Recommenders to Prepare

- Educator recommendation: science/math/CS teacher who can speak to independence and rigor.
- Project recommendation: someone who can verify the project process. If there was no mentor, choose the adult who can most accurately describe what they observed, without inventing supervision.
- High school report: school counselor/transcript process.

## Integrity Notes

- Disclose AI/tool assistance and all external support accurately.
- Do not imply clinical trial, therapeutic efficacy, or university affiliation.
- If public data were used, explain why human-subject risk is limited but still discuss ethics.

## Official Sources

- `https://www.societyforscience.org/regeneron-sts/application-requirements/`
- `https://sciencetalentsearch.smapply.org/prog/lst/`
- `https://www.societyforscience.org/regeneron-sts/frequently-asked-questions/`
