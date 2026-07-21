<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 BCI Award 2026 · priority #6
>
> **Doc status:** REFERENCE — supporting material (layout/plan/script/checklist)  
> **Artifact type:** talk/video script · **Canonical:** no (supporting file)  
> **Venue phase:** gate G2 · 22% to submission · **eligibility:** ok · label: `optional-stretch`  
> **Deadline:** 2026-09-01 (46d)  
> ⚑ **Integrity:** ai-policy-unknown-default-red  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# BCI Award 2026 Short Film Script

## Use Case

Use only if submitting to the BCI Award. The award favors online or real-time BCI systems, so this video should be honest: this project is a validation audit for adaptive neurotechnology, not a deployed BCI.

## Two-Minute Script

Closed-loop neurotechnology depends on one simple requirement: the system must use information that is actually available at the time it makes a decision.

My project tested that requirement in a retrospective EEG forecasting benchmark for adaptive 40 Hz auditory stimulation. I used OpenNeuro ds005048, a public dataset with 35 memory-clinic participants, and computed frontal phase-amplitude coupling as a scalar EEG timing target.

At first, the model looked promising. A compact temporal convolutional network reached five-seed mean held-out R2 of 0.606, clearly above a persistence baseline. But I then found the key failure mode: the PAC targets were complete-event summaries assigned back to earlier windows. That means early windows could inherit information from later EEG samples in the same event.

I rebuilt the benchmark using five-second backward-looking PAC targets. This increased unique held-out targets from 104 to 2678 and eliminated repeated adjacent targets. Under this stricter test, the neural network dropped to R2 of 0.212 and did not outperform Ridge regression at 0.216.

The contribution is not a claim that this is a finished BCI. The contribution is a practical audit for future adaptive EEG systems: before a controller is tested live, the EEG target, simple baselines, and control objective must all be checked against real-time information boundaries.
