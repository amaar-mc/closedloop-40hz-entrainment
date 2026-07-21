<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 Synopsys Championship 2027 · priority #5
>
> **Doc status:** REFERENCE — supporting material (layout/plan/script/checklist)  
> **Artifact type:** plan/checklist · **Canonical:** no (supporting file)  
> **Venue phase:** gate G2 · 28% to submission · **eligibility:** ok · label: `senior-year-fair`  
> **Deadline:** no date posted  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# Synopsys / ISEF Research Plan and Forms Checklist

## Status

This checklist does not replace the official ISEF Rules Wizard or Synopsys registration portal. Use it to prepare, then verify the current 2027 requirements before submission.

## Likely Project Type

Computational research using public de-identified EEG data. No new human participants, no intervention, no diagnosis, and no treatment claim.

## Rules Wizard Inputs to Verify

- Public dataset: OpenNeuro `ds005048`.
- No new human-subject data collection.
- No interaction with participants.
- No medical diagnosis or treatment claim.
- No regulated research institution unless a real external lab/mentor was involved.
- Continuation status: verify whether this is a continuation of previous work and whether Form 7 applies.

## Adult Sponsor / School Items

- Identify the high-school teacher/adult sponsor who can truthfully sign.
- Confirm whether the project was done at home/school or in a regulated research institution.
- Confirm local Santa Clara County school eligibility.
- Keep a copy of all source-code, dataset, and result artifacts.

## Research Plan Outline

### Question

Can a frontal EEG PAC feature be forecast across participants during 40 Hz auditory stimulation, and does the conclusion change when PAC is recomputed from backward-looking EEG contexts?

### Hypothesis

PAC history and stimulation context will predict event-summary PAC, but performance will weaken under backward-looking PAC targets.

### Methods

Use OpenNeuro `ds005048`, seven frontal EEG channels, scalar PAC timing target, participant-disjoint split, 12-feature TCN, persistence and Ridge baselines, and a backward-looking PAC stress test.

### Risk and Ethics

This is secondary analysis of a public de-identified dataset. The original dataset includes ethics approval and informed consent documentation. No new human-subject interaction occurs in this project.

### Claims to Avoid

- Do not claim diagnosis.
- Do not claim treatment benefit.
- Do not claim a deployed medical device.
- Do not claim live closed-loop control.

## Forms to Check

- ISEF Form 1: Checklist for Adult Sponsor.
- ISEF Form 1A: Student Checklist / Research Plan.
- ISEF Form 1B: Approval Form.
- ISEF Form 7: Continuation Projects, if applicable.
- Additional forms only if Rules Wizard says they apply.
