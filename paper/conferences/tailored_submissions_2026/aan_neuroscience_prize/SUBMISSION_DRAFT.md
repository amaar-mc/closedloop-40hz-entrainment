<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 AAN Neuroscience Prize · priority #3
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G2 · 28% to submission · **eligibility:** ok · label: `confirmed-open`  
> **Deadline:** 2026-10-20 (95d)  
> ⚑ **Integrity:** no-fabricated-mentor, mentor-esignature-required  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# AAN / Bhuwan Garg High School Neuroscience Research Prize Draft

## Venue Fit

**Current status:** official AAN page says the application period is closed; monitor for the next cycle.  
**Likely artifact:** application, maximum 300-word abstract, research report, bibliography, and e-signatures from parent/guardian, teacher, and mentor.  
**Strategy:** make this a neuroscience-methods project, not an engineering conference paper. AAN readers need clear biological restraint: PAC is a scalar EEG timing target here, not proof of endogenous theta-gamma coupling or treatment response.

## Recommended Title

Testing Whether EEG PAC Forecasts Survive a More Realistic Target Definition

## 300-Word Abstract Draft

**OBJECTIVE:** To test whether frontal EEG phase-amplitude-coupling features can be forecast across participants during 40 Hz auditory stimulation, and whether model conclusions change when the PAC target is computed from backward-looking EEG rather than complete event summaries.

**BACKGROUND:** Forty-hertz auditory stimulation is being studied in neurodegeneration research, but adaptive stimulation requires EEG features that are available before decisions are made. Retrospective EEG labels can overstate forecasting performance if they summarize signal samples acquired after the modeled decision time.

**DESIGN/METHODS:** I analyzed OpenNeuro `ds005048`, a public 40 Hz auditory-stimulation EEG dataset containing 35 memory-clinic participants. Seven frontal channels were used to compute frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase. Participants were split into 24 training, 5 validation, and 6 held-out test participants. A 12-feature temporal convolutional network used PAC-history and stimulation-context inputs to predict PAC five seconds ahead. Performance was compared with persistence and Ridge regression baselines. A stress test recomputed PAC from five-second backward-looking EEG contexts.

**RESULTS:** In the event-summary benchmark, the 12-feature TCN achieved five-seed mean held-out `R^2 = 0.606`, compared with `R^2 = 0.104` for persistence. However, event-summary labels repeated within stimulation periods and assigned complete-event PAC values to earlier windows. Backward-looking PAC increased unique held-out targets from 104 to 2,678 and reduced adjacent target repetition from 96.2 percent to zero. Under this stricter target definition, TCN performance decreased to `R^2 = 0.212` and did not exceed Ridge regression at `R^2 = 0.216`.

**CONCLUSIONS:** PAC forecasting showed retrospective structure, but target definition changed the main conclusion in this fixed-split stress test. Future adaptive-stimulation studies should validate streaming-compatible features and repeated participant-split performance before testing live controllers.

## AAN Optimization

- Put the neuroscience caveat upfront.
- Emphasize research skill and methodological discipline.
- Avoid disease-treatment language.
- AAN requires parent/guardian, teacher, and mentor e-signatures. Use only people who can honestly verify the work; if there is no real mentor, this is not submission-ready.

## Official Sources

- `https://www.aan.com/research/neuroscience-research-prize`
