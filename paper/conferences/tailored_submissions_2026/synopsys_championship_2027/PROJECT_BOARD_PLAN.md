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

# Synopsys Championship Project Board Plan

## Board Thesis

An EEG forecasting model can look strong if its target is computed from future signal samples; a fair adaptive-stimulation benchmark needs targets available before the decision.

## Board Sections

### Question

Can frontal EEG PAC be forecast across participants during 40 Hz auditory stimulation, and does the result survive a backward-looking target definition?

### Hypothesis

PAC history plus stimulation context will predict event-summary PAC, but model performance will weaken when PAC is recomputed from backward-looking EEG contexts.

### Data

OpenNeuro `ds005048`, public de-identified EEG, 35 participants, seven frontal channels used.

### Methods

Show a flow diagram:

Raw EEG -> frontal channels -> PAC feature -> participant split -> TCN and baselines -> backward-looking stress test -> offline replay.

### Results

Use two tables:

| Benchmark            |                TCN |                  Baseline |
| -------------------- | -----------------: | ------------------------: |
| Event-summary PAC    | `R^2 = 0.606` mean | persistence `R^2 = 0.104` |
| Backward-looking PAC |      `R^2 = 0.212` |       Ridge `R^2 = 0.216` |

| Target property            | Event-summary | Backward-looking |
| -------------------------- | ------------: | ---------------: |
| Unique held-out targets    |           104 |             2678 |
| Adjacent target repetition |         96.2% |             0.0% |

### Conclusion

In this fixed-split stress test, target definition changed the main conclusion. Under the stricter target, the neural network did not beat a linear baseline.

### Limitations

Retrospective public data, one dataset, no live controller, scalar PAC timing target, and no treatment claims.

### Future Work

Repeated participant splits, streaming-compatible PAC estimator, and controller objectives that balance low-PAC coverage and high-PAC sparing.
