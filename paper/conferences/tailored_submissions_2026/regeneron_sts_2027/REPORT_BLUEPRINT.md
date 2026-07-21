<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 Regeneron STS 2027 · priority #2
>
> **Doc status:** SCAFFOLD ONLY — planning aid; final text MUST be human-authored (venue AI rules)  
> **Artifact type:** research report · **Canonical:** no (supporting file)  
> **Venue phase:** gate G1 · 11% to submission · **eligibility:** ok · label: `scaffold-only / student-must-write`  
> **Deadline:** 2026-11-05 (111d)  
> ⚑ **Integrity:** no-AI-text, no-fabricated-mentor  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# Regeneron STS 2027 Research Report Blueprint

Do not submit generated prose from this file, or close paraphrases of it. STS prohibits using ChatGPT or similar tools to answer application questions or draft the research report. Use this as a structure checklist, then write the report yourself and disclose tool use accurately.

## Title

Auditing EEG Target Definitions for Adaptive 40 Hz Auditory Stimulation

## Core Story

You built a computational neuroscience benchmark, found a result that looked strong, discovered a target-availability limitation, stress-tested it with a backward-looking definition, and narrowed the claim. That is the strongest STS narrative because it shows independence and scientific judgment.

## Suggested Report Structure

### Official Format Constraints

- Include a title page.
- Include the abstract as the second page.
- Keep the research report within the official 20-page maximum.
- Put the bibliography at the end.
- Do not include hyperlinks except in references.
- Do not use generative AI to draft the report or application answers.

### 1. Abstract

Write 200-250 words. Include the dataset, participant-disjoint split, initial event-summary result, backward-looking stress test, and final conclusion that target definition changed the model-selection result in a fixed-split stress test.

### 2. Introduction

Explain fixed versus adaptive stimulation. Define the engineering question: a controller needs an EEG feature available before the decision. Avoid disease-treatment claims.

### 3. Background

Define EEG, PAC, 40 Hz auditory stimulation, and temporal forecasting for a broad scientific audience. State that PAC is used as a scalar EEG timing target, not proof of physiological coupling.

### 4. Research Question and Hypothesis

Research question: can frontal PAC be forecast across participants, and does performance survive a stricter target definition?  
Hypothesis: PAC history plus stimulation context would contain predictive structure, but performance would weaken under backward-looking PAC.

### 5. Data and Ethics

Describe OpenNeuro `ds005048`, public de-identified EEG, 35 participants, and why human-subject risk is limited. Explain that no new participant data were collected.

### 6. Methods

Describe channel selection, PAC computation, participant split, model inputs, TCN, baselines, train-only normalization, and the backward-looking PAC recomputation.

### 7. Results

Report the four main result blocks:

- Feature ablation: 12 features beat the 73-feature candidate set.
- Five-seed event-summary result: mean `R^2 = 0.606`; persistence `R^2 = 0.104`.
- Backward-looking stress test: unique targets `104 -> 2678`; repetition `96.2% -> 0%`; TCN `R^2 = 0.212`; Ridge `R^2 = 0.216`.
- Controller replay: higher low-PAC stimulation coverage but lower above-median-PAC rest rate.

### 8. Discussion

Explain why the first result was limited. The important sentence: target availability changed the scientific conclusion, so the stronger-looking model should not be treated as ready for closed-loop control.

### 9. Limitations

Include single dataset, small held-out participant count, no prospective testing, PAC without surrogate correction, no validated streaming PAC estimator, and replay that cannot model physiological response to counterfactual stimulation.

### 10. Future Work

Repeat participant splits, run multi-seed backward-looking PAC, validate streaming PAC estimation, compare simple baselines, and design a controller objective that balances low-PAC coverage and high-PAC sparing.

## Recommendation Requests

- Educator recommendation: ask a science, math, or CS teacher who can verify your independence and rigor.
- Project recommendation: ask only someone who actually observed or supervised the research process.
- Counselor/school report: start early; the deadline includes support materials.
