<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 Sigma Xi Showcase 2027 · priority #8
>
> **Doc status:** REFERENCE — supporting material (layout/plan/script/checklist)  
> **Artifact type:** plan/checklist · **Canonical:** no (supporting file)  
> **Venue phase:** gate G2 · 22% to submission · **eligibility:** ok · label: `backup-online`  
> **Deadline:** no date posted  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# Sigma Xi Student Research Showcase Website and Video Plan

## Artifact Status

The official showcase is not just an abstract submission. It expects a public project website with an abstract, a technical slideshow, and a video presentation. The 2027 cycle is not posted yet, so this is a preparation plan based on the current showcase structure.

## Website Sections

### 1. Project Title

When an EEG Forecast Looks Good: Auditing Target Definitions in Adaptive Stimulation Research

### 2. Abstract

Use the one-paragraph abstract from `SUBMISSION_DRAFT.md`, then revise to the current portal limit when the 2027 rules post.

### 3. Research Question

Can frontal EEG PAC be forecast across participants during 40 Hz auditory stimulation, and does the result survive a backward-looking target definition?

### 4. Methods

Use a simple pipeline graphic:

OpenNeuro EEG -> frontal channels -> scalar PAC timing target -> participant-disjoint split -> TCN/Ridge/persistence -> target-definition stress test.

### 5. Results

Show one table:

| Benchmark            |                TCN |                  Baseline |
| -------------------- | -----------------: | ------------------------: |
| Event-summary PAC    | `R^2 = 0.606` mean | persistence `R^2 = 0.104` |
| Backward-looking PAC |      `R^2 = 0.212` |       Ridge `R^2 = 0.216` |

Show one target-definition table:

| Target property            | Event-summary | Backward-looking |
| -------------------------- | ------------: | ---------------: |
| Unique held-out targets    |           104 |             2678 |
| Adjacent target repetition |         96.2% |             0.0% |

### 6. Conclusion

In this fixed-split stress test, the target definition changed the model-selection conclusion. The nonlinear model looked strong under complete-event labels but did not outperform Ridge under backward-looking PAC.

### 7. Limitations

Retrospective public data, one dataset, scalar PAC timing target, no live controller, no clinical efficacy claim.

## Technical Slideshow

1. Problem: adaptive stimulation needs decision-time EEG features.
2. Dataset: OpenNeuro `ds005048`, 35 participants.
3. Model: 12-feature TCN and baselines.
4. Initial result: event-summary benchmark.
5. Audit: backward-looking PAC target.
6. Revised conclusion and future work.

## Short Video Script

My project asks whether an EEG feature can be forecast before a future adaptive stimulation decision. I used a public 40 Hz auditory-stimulation EEG dataset and built a participant-disjoint benchmark for a frontal PAC feature. The first model looked strong, reaching mean held-out R2 of 0.606. Then I found a limitation: the target was computed over complete events and assigned back to shorter windows, so early windows could inherit later signal samples. When I recomputed PAC from five-second backward-looking contexts, the target became harder and the TCN dropped to R2 of 0.212, slightly below Ridge regression at 0.216. The main result is that target definition mattered more than model complexity. Before adaptive EEG systems are tested live, their targets and baselines need to be audited for information availability.
