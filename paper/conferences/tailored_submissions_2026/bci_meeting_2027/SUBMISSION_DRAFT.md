<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 BCI Meeting 2027 · priority #13
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G2 · 22% to submission · **eligibility:** ok · label: `prepare-later`  
> **Deadline:** 2027-01-15 (182d)  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# International BCI Meeting 2027 Draft

## Venue Fit

**Submission type:** poster/oral abstract.  
**Timeline:** abstracts open 2026-11-09; deadline 2027-01-15; notification 2027-03-03.  
**Fit caveat:** this project is adjacent to BCI and adaptive neurotechnology, but not a classic communication/control BCI. The title and abstract should emphasize closed-loop EEG-feature forecasting and adaptive neurotechnology.

## Recommended Title

Information-Boundary Auditing for EEG Feature Forecasts in Adaptive Neurostimulation

## Abstract Draft

Closed-loop neurotechnology depends on signal features that are both predictive and available at decision time. We evaluated this issue in a retrospective EEG forecasting benchmark for adaptive 40 Hz auditory stimulation. Using OpenNeuro `ds005048`, we analyzed 35 auditory-stimulation EEG recordings and computed frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase. Participants were split into 24 training, 5 validation, and 6 held-out test participants. A 12-feature temporal convolutional network used PAC-history and stimulation-context features to forecast PAC five seconds ahead.

Under complete-event PAC summaries assigned to constituent windows, the TCN appeared strongly predictive, with five-seed mean held-out `R^2 = 0.606` versus `R^2 = 0.104` for persistence. However, complete-event assignment can make early-window PAC inputs depend on later EEG samples in the same event. We therefore recomputed PAC from five-second backward-looking contexts. This increased unique held-out targets from 104 to 2,678 and reduced adjacent target repetition from 96.2 percent to zero. Under the stricter backward-looking target construction, TCN `R^2` decreased to 0.212 and did not exceed Ridge regression at 0.216.

Offline replay of a predictive policy increased stimulation during low-PAC periods but reduced rest during above-median-PAC periods compared with reactive thresholding, indicating a controller-calibration problem rather than solved closed-loop control. These results argue that adaptive neurotechnology benchmarks should report target availability, simple baselines, and controller behavior before live deployment claims are made.

## BCI Meeting Optimization

- Frame as closed-loop validation methodology.
- Avoid implying participant communication/control.
- Add repeated participant-split results before submission if possible.

## Official Sources

- `https://bcisociety.org/`
- `https://bcisociety.org/bci-meeting/`
