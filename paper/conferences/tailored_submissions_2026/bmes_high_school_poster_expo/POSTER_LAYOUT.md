<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 BMES 2026 HS Poster Expo · priority #1
>
> **Doc status:** REFERENCE — supporting material (layout/plan/script/checklist)  
> **Artifact type:** poster layout · **Canonical:** no (supporting file)  
> **Venue phase:** gate G4 · 67% to submission · **eligibility:** ok · label: `strong-fit`  
> **Deadline:** 2026-08-14 (28d)  
> ⚑ **Integrity:** ai-policy-unknown-default-red  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# BMES High School Poster Layout

## Title

Engineering a Retrospective EEG Benchmark for Adaptive Auditory Stimulation

## Abstract Box

Use the abstract from `SUBMISSION_DRAFT.md`. Keep the framing biomedical-engineering first: validation benchmark, adaptive neurotechnology, information boundaries, and controller tradeoffs.

## Section 1: Biomedical Engineering Problem

Adaptive stimulation systems need EEG features that can be estimated before stimulation decisions are made. A retrospective model can look strong if the target is not available at the decision time.

## Section 2: Dataset and Signal Feature

- Dataset: OpenNeuro `ds005048`, 35 participants.
- EEG: 19 channels at 250 Hz; seven frontal channels used here.
- Feature: frontal phase-amplitude coupling, treated as a scalar EEG timing target.

## Section 3: Forecasting Benchmark

- Split by participant: 24 train, 5 validation, 6 held-out test.
- Model: 12-feature TCN with PAC history and stimulation context.
- Baselines: persistence and Ridge regression.

## Section 4: Key Result

Event-summary benchmark: five-seed mean held-out `R^2 = 0.606`, persistence `R^2 = 0.104`.

## Section 5: Stress Test

Problem: complete-event PAC labels can assign future samples to earlier windows.  
Fix: recompute PAC from five-second backward-looking contexts.  
Effect: unique targets increased from 104 to 2678; adjacent repetition dropped from 96.2 percent to zero.

## Section 6: Corrected Result

Backward-looking PAC benchmark: TCN `R^2 = 0.212`, Ridge `R^2 = 0.216`. The nonlinear model was not justified over the linear baseline under the stricter target.

## Section 7: Design Takeaway

Before adaptive auditory stimulation can be tested prospectively, the benchmark needs streaming-compatible PAC estimation, repeated participant-split validation, and controller objectives that balance low-PAC coverage against high-PAC sparing.

## Figure Recommendation

Use one central figure: event-summary benchmark versus backward-looking PAC benchmark, with the target-repetition change shown next to the performance drop.
