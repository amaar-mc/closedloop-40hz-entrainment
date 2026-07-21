<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 BCI Award 2026 · priority #6
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** two-page description (primary artifact) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G2 · 22% to submission · **eligibility:** ok · label: `optional-stretch`  
> **Deadline:** 2026-09-01 (46d)  
> ⚑ **Integrity:** ai-policy-unknown-default-red  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# BCI Award 2026 Two-Page Project Description Draft

## Status

This is a text draft for the required maximum two-page PDF. It still needs layout as a PDF and should be submitted only with the required short film. This is a low-probability stretch because the project is retrospective and offline, not an online BCI.

## Project Title

Auditing EEG Biomarker Forecasts Before Adaptive Neurostimulation

## 3-5 Sentence Summary

Closed-loop neurotechnology depends on EEG features that are available when a system makes a decision. I built a retrospective EEG benchmark to test that requirement in adaptive 40 Hz auditory stimulation. A compact temporal convolutional network looked strong under complete-event PAC labels, but under five-second backward-looking PAC targets it dropped to `R^2 = 0.212` and did not outperform Ridge regression at `R^2 = 0.216`. The project is therefore an information-boundary audit for adaptive EEG systems, not a finished online BCI.

## Description

This project evaluates a common failure mode in retrospective adaptive-neurotechnology pipelines: a model can appear useful if the predicted target summarizes signal samples that would not be available at decision time. The analysis used OpenNeuro `ds005048`, a public 40 Hz auditory-stimulation EEG dataset with 35 memory-clinic participants. Seven frontal channels were used to compute frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase.

Participants were split into 24 training, 5 validation, and 6 held-out test participants. A 12-feature temporal convolutional network used PAC-history and stimulation-context inputs to forecast PAC five seconds ahead. Under complete-event PAC summaries assigned back to shorter windows, the model reached five-seed mean held-out `R^2 = 0.606`, compared with `R^2 = 0.104` for persistence.

The target audit changed the interpretation. Complete-event PAC labels assigned to early windows could include later EEG samples from the same event. I recomputed PAC from five-second backward-looking contexts. This increased unique held-out targets from 104 to 2,678 and reduced adjacent target repetition from 96.2 percent to zero. Under this stricter target definition, TCN performance dropped to `R^2 = 0.212` and did not outperform Ridge regression at `R^2 = 0.216`.

Offline replay of a predictive stimulation policy showed a controller-calibration problem. The predictive policy stimulated during low-PAC periods more often than a reactive threshold policy, but rested during above-median-PAC periods less often. This indicates that target availability, baseline comparison, and controller calibration must be validated together before live adaptive stimulation is attempted.

## Current Status

Retrospective benchmark and offline replay completed. No live controller, online BCI, user study, or patient benefit claim has been demonstrated.

## Why This Matters for BCI / Neurotechnology

The contribution is a validation method: it catches target-definition errors before adaptive EEG models are treated as deployable control components.
