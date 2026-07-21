<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 JSHS NorCal 2027 · priority #10
>
> **Doc status:** SCAFFOLD ONLY — planning aid; final text MUST be human-authored (venue AI rules)  
> **Artifact type:** report blueprint · **Canonical:** no (supporting file)  
> **Venue phase:** gate G1 · 11% to submission · **eligibility:** monitor · label: `suspended-monitor`  
> **Deadline:** no date posted  
> ⚑ **Integrity:** no-AI-text  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# Northern California JSHS Research Paper Blueprint

Do not submit generated prose from this file, or close paraphrases of it. JSHS rules forbid ChatGPT or other generative AI tools from writing the research paper or abstract. Use this as an outline and write the paper yourself. The 2027 Northern California packet was not verified in this audit; wait for the current regional rules before final formatting.

## Target Length

Use a concise paper, not the maximum. Aim for 8-12 double-spaced pages before references and appendices unless the current regional packet says otherwise.

## Title

Evaluating EEG Forecasts for Future Adaptive Auditory Stimulation

## Abstract

Use the abstract scaffold in `SUBMISSION_DRAFT.md` only to understand what content must be covered. Do not submit that generated text; write your own abstract from scratch.

## Section Plan

### 1. Introduction

Explain the problem in plain language: adaptive stimulation requires a brain-signal feature that can be measured before the system acts.

### 2. Background

Define EEG, 40 Hz auditory stimulation, PAC, and forecasting. Keep this short. Judges need enough context to understand the question, not a literature review.

### 3. Research Question

Can a frontal EEG PAC feature be forecast across participants during 40 Hz auditory stimulation, and does the result change when PAC is recomputed from backward-looking EEG contexts?

### 4. Methods

Include:

- OpenNeuro `ds005048`, public EEG dataset.
- Seven frontal channels.
- PAC feature: theta phase and 40 Hz amplitude.
- Participant-disjoint split: 24 train, 5 validation, 6 test.
- 12-feature TCN.
- Persistence and Ridge baselines.
- Backward-looking PAC stress test.

### 5. Results

Use a small number of clear tables:

| Result                           |         Value |
| -------------------------------- | ------------: |
| Event-summary five-seed TCN mean | `R^2 = 0.606` |
| Persistence baseline             | `R^2 = 0.104` |
| Backward-looking TCN             | `R^2 = 0.212` |
| Backward-looking Ridge           | `R^2 = 0.216` |

Add one figure showing the performance drop and target-repetition removal.

### 6. Discussion

The key explanation: the model looked strong when the target was easier, but under a stricter online-availability target the neural network did not beat a linear baseline.

### 7. Limitations

Name the limitations directly: retrospective public data, one dataset, scalar PAC timing target, no prospective participants, no live controller, and no proof of treatment benefit.

### 8. Conclusion

In this fixed-split stress test, target definition changed the model-selection conclusion. Future adaptive EEG work must validate feature availability before live use.

## Statement of Outside Assistance Prompts

Prepare honest answers for:

- Who helped formulate the research question?
- Who helped with code, statistics, writing, or editing?
- Which parts were done independently?
- What data came from an outside/public source?
- Were AI tools used, and for what tasks?
