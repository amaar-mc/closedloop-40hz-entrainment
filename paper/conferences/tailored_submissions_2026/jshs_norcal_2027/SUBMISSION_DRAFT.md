<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 JSHS NorCal 2027 · priority #10
>
> **Doc status:** SCAFFOLD ONLY — planning aid; final text MUST be human-authored (venue AI rules)  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G1 · 11% to submission · **eligibility:** monitor · label: `suspended-monitor`  
> **Deadline:** no date posted  
> ⚑ **Integrity:** no-AI-text  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# Northern California JSHS 2027 Draft

## Venue Fit

**Best submission type:** regional research paper, with poster/oral selection if accepted.  
**Audience:** high-school research judges, faculty reviewers, STEM educators.  
**Strategy:** JSHS rewards original independent research, clear scientific method, and presentation quality. Make the project easier to understand than the IEEE manuscript.
**AI-writing rule:** do not submit this generated abstract, or close paraphrases of it, to JSHS. JSHS rules forbid ChatGPT or other generative AI tools from writing the research paper or abstract. Use this file only as planning scaffolding, then write your own paper and Statement of Outside Assistance.
**Current-status blocker:** the 2027 Northern California regional packet was not verified in this audit. Do not submit until the official regional portal and current rules are posted.

## Recommended Title

Evaluating EEG Forecasts for Future Adaptive Auditory Stimulation

## Abstract Planning Scaffold - Do Not Submit

Adaptive brain-stimulation systems require EEG features that can be measured before stimulation decisions are made. This project tested whether a frontal EEG phase-amplitude-coupling feature could be forecast across participants during 40 Hz auditory stimulation, and whether the result changed when the target was made more realistic for future online use.

I used OpenNeuro `ds005048`, a public EEG dataset containing 35 memory-clinic participants exposed to 40 Hz auditory stimulation. Seven frontal channels were used to compute frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase. Participants were split into 24 training, 5 validation, and 6 held-out test participants. A compact 12-feature temporal convolutional network predicted PAC five seconds ahead using PAC history and stimulation-context inputs.

In the first benchmark, event-level PAC labels were assigned to shorter windows. Under that definition, the model achieved five-seed mean held-out `R^2 = 0.606`, outperforming a persistence baseline at `R^2 = 0.104`. I then identified a limitation: early windows received PAC labels computed using later samples from the same event. A stricter stress test recomputed PAC only from five-second backward-looking EEG contexts. This increased unique held-out test targets from 104 to 2,678 and removed repeated adjacent targets. Under the stricter definition, model performance dropped to `R^2 = 0.212` and did not exceed Ridge regression at `R^2 = 0.216`.

The results show that target definition can matter more than model complexity. This work supports further validation of streaming EEG features before adaptive auditory stimulation is tested prospectively.

## JSHS Paper Outline

1. Introduction: adaptive stimulation and why online EEG features matter.
2. Background: EEG, PAC, and 40 Hz stimulation, with clear caveats.
3. Methods: dataset, preprocessing, split design, forecasting model, baselines.
4. Results: event-summary result, backward-looking stress test, replay tradeoff.
5. Discussion: why the stronger-looking result was limited.
6. Conclusion: what must be validated next.
7. Statement of Outside Assistance: prepare a precise, honest version.

## Presentation Strategy

Use simple diagrams. Judges should be able to explain the key point back as: "He found that the model looked good until he tested whether the target was actually available in time."

## Official Sources

- `https://cob.sfsu.edu/initiatives-centers/jshs`
- `https://www.jshs.org/`
