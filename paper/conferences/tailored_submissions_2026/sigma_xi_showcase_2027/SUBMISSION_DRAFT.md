<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 Sigma Xi Showcase 2027 · priority #8
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G2 · 22% to submission · **eligibility:** ok · label: `backup-online`  
> **Deadline:** no date posted  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# Sigma Xi Student Research Showcase Draft

## Venue Fit

**Best submission type:** online research presentation / showcase.  
**Audience:** broad STEM judges across high school, undergraduate, and graduate levels.  
**Strategy:** make the project accessible and emphasize scientific communication, not conference-paper density.
**Format target:** one-paragraph abstract, no formal citations, keep near 250 words.
**Current-status note:** use this as a 2027 planning draft until Sigma Xi posts the next Student Research Showcase cycle.

## Recommended Title

When an EEG Forecast Looks Good: Auditing Target Definitions in Adaptive Stimulation Research

## Abstract Draft

Machine-learning models can appear successful if the target they predict is easier than it would be in a real system. This project tested that issue in a retrospective EEG forecasting task related to future adaptive auditory stimulation. I analyzed OpenNeuro ds005048, a public dataset of 35 participants receiving 40 Hz auditory stimulation. Seven frontal EEG channels were used to compute frontal phase-amplitude coupling (PAC), the dependence of 38-42 Hz EEG amplitude on 4-8 Hz theta phase. A temporal convolutional network predicted PAC five seconds ahead using a 20-second history, with training, validation, and test sets split by participant. In the first benchmark, PAC was computed over complete stimulation or rest periods and assigned to shorter windows. Under that target definition, the model reached five-seed mean held-out R2 of 0.606, while persistence reached 0.104. I then found that early windows could inherit PAC values computed from later samples. A stricter stress test recomputed PAC from five-second backward-looking EEG contexts. This removed repeated adjacent targets and reduced TCN performance to R2 of 0.212, approximately matching Ridge regression at 0.216. The main finding is that target definition mattered more than neural-network complexity. The project shows why retrospective biomedical AI systems should be audited for information availability before they are treated as deployable control systems.

## Presentation Plan

- Slide 1: problem - adaptive stimulation needs live-available EEG features.
- Slide 2: dataset and model.
- Slide 3: strong initial result.
- Slide 4: why the initial target was limited.
- Slide 5: backward-looking target result and takeaway.

## Official Sources

- `https://www.sigmaxi.org/meetings-events/student-research-showcase`
- `https://www.sigmaxi.org/meetings-events/student-research-showcase/competition-timeline`
