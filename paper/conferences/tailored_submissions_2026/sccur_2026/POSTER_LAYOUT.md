<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 SCCUR 2026 · priority #14
>
> **Doc status:** REFERENCE — supporting material (layout/plan/script/checklist)  
> **Artifact type:** poster layout · **Canonical:** no (supporting file)  
> **Venue phase:** gate G2 · 28% to submission · **eligibility:** conditional · label: `conditional-eligibility`  
> **Deadline:** 2026-10-09 (84d)  
> ⚑ **Integrity:** no-fabricated-mentor, ai-policy-unknown-default-red  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# SCCUR 2026 Poster Layout

## Title

Stress-Testing an EEG Forecasting Model for Adaptive Auditory Stimulation

## One-Sentence Thesis

The model looked useful until the PAC target was recomputed under a stricter online-availability rule.

## Section 1: Research Question

Can a frontal EEG PAC feature be forecast across participants during 40 Hz auditory stimulation, and does the answer change when PAC is computed only from past EEG context?

## Section 2: Data

OpenNeuro `ds005048`, 35 participants, 19-channel EEG at 250 Hz. This project analyzed seven frontal channels and used participant-disjoint train, validation, and test splits.

## Section 3: Method

A 12-feature temporal convolutional network used PAC history and stimulation context to predict PAC five seconds ahead. Persistence and Ridge regression were used as baselines.

## Section 4: Initial Finding

Event-summary PAC labels produced five-seed mean held-out `R^2 = 0.606`, compared with `R^2 = 0.104` for persistence.

## Section 5: Audit Finding

Complete-event PAC summaries could include later samples from the same event. Backward-looking PAC increased unique held-out targets from 104 to 2678 and reduced adjacent target repetition from 96.2 percent to zero.

## Section 6: Revised Conclusion

Under the stricter target, TCN performance dropped to `R^2 = 0.212` and did not beat Ridge regression at `R^2 = 0.216`.

## Section 7: Why It Matters

For adaptive EEG systems, the target definition can matter more than model complexity. A deployable controller needs signal features that are available before the decision, not only after retrospective summarization.

## Presentation Strategy

Keep this less technical than SPMB. SCCUR reviewers should see the discovery process: initial model, limitation found, stricter test, narrower conclusion.
