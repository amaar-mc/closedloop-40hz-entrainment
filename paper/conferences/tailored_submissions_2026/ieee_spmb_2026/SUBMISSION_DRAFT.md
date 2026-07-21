<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 IEEE SPMB 2026 · priority #11
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** no (supporting file)  
> **Venue phase:** gate G2 · 28% to submission · **eligibility:** ok · label: `expired-this-cycle`  
> **Deadline:** 2026-07-01 (passed)  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# IEEE SPMB 2026 Draft

## Venue Fit

**Venue:** IEEE Signal Processing in Medicine and Biology Symposium.  
**Deadline:** paper submission 2026-07-01; notification 2026-09-01; conference 2026-12-05.  
**Submission mechanics:** email one PDF submission to `submit@ieeespmb.org`. SPMB accepts full papers and poster abstracts. Full papers are usually 4-6 pages in IEEE two-column style; poster abstracts may be 1-4 pages, with one page preferred.  
**Format status:** this Markdown draft is not itself submission-ready. Convert it to the SPMB PDF template with required title formatting, margins, fonts, acknowledgments, and IEEE references before emailing.  
**Acceptance strategy:** lead with signal-processing validation, information boundaries, and baseline comparisons. Do not sell this as a clinical efficacy paper.

## Recommended Title

Target-Availability Stress Testing for Cross-Participant EEG PAC Forecasting

## Poster Abstract / Short Paper Draft

### Abstract

Adaptive neuromodulation requires EEG quantities that can be estimated and forecast before stimulation decisions are made. This retrospective signal-processing study evaluated whether frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase, can be forecast across participants during 40 Hz auditory stimulation, and whether performance survives a target construction closer to online availability. Using OpenNeuro `ds005048` (`N = 35`), a compact 12-feature temporal convolutional network achieved five-seed mean held-out `R^2 = 0.606` under complete-event PAC summaries, but dropped to `R^2 = 0.212` when PAC was recomputed from five-second backward-looking contexts and did not outperform Ridge regression (`R^2 = 0.216`). The result shows that information boundaries and target definitions can substantially alter model-selection conclusions in EEG forecasting pipelines.

### Methods

The dataset contained 19-channel auditory-stimulation EEG recorded at 250 Hz. Seven frontal channels (`Fp1`, `Fp2`, `F7`, `F3`, `Fz`, `F4`, `F8`) were analyzed. PAC was computed from `4-8 Hz` theta phase and `38-42 Hz` amplitude using a modulation-index feature averaged across channels. Participants were split into 24 training, 5 validation, and 6 held-out test participants. Each sample used a 20-step lookback and a five-step forecast horizon. Inputs contained 7 PAC-history features and 5 stimulation-context features. Comparisons included persistence, Ridge regression, and a lightweight temporal convolutional network.

### Results

In a single-seed feature ablation, the 12-feature representation improved held-out test `R^2` from `-0.025` for all 73 candidate features to `0.558`. Across five seeds on the same participant split, the selected TCN achieved mean `R^2 = 0.606` compared with `R^2 = 0.104` for persistence. However, event-level PAC summaries repeated labels within periods and assigned complete-event values to constituent windows. In a backward-looking PAC stress test, unique held-out targets increased from 104 to 2,678 and adjacent target repetition decreased from 96.2 percent to zero. Under this stricter target construction, TCN `R^2` decreased from `0.554` to `0.212`, while Ridge reached `0.216`.

### Discussion

The event-summary benchmark demonstrates predictable stored-series structure, but the backward-looking target benchmark changes the model-selection conclusion. For this task, a nonlinear temporal model was not yet justified over a linear baseline once target availability was constrained. Offline replay further showed a controller-calibration problem: predictive control increased low-PAC stimulation coverage but reduced the above-median-PAC rest rate. These findings support target-availability audits, stimulation-context ablations, and repeated participant-split validation as prerequisites before prospective adaptive stimulation.

### Acknowledgment

No external project funding was used for this student analysis. The author acknowledges Lahijanian, Aghajan, and Vahabi for releasing OpenNeuro `ds005048`.

### References

[1] M. Lahijanian, H. Aghajan, and Z. Vahabi, "Auditory gamma-band entrainment enhances default mode network connectivity in dementia patients," Scientific Reports, vol. 14, art. 13153, 2024.

[2] M. Lahijanian, H. Aghajan, and Z. Vahabi, "40Hz Auditory Entrainment," OpenNeuro dataset `ds005048`, version `1.0.1`, doi:10.18112/openneuro.ds005048.v1.0.1.

[3] A. B. L. Tort, R. Komorowski, H. Eichenbaum, and N. Kopell, "Measuring phase-amplitude coupling between neuronal oscillations of different frequencies," Journal of Neurophysiology, vol. 104, no. 2, pp. 1195-1210, 2010.

### Submission Risk

This is close to SPMB fit, but before submitting a full paper, the strongest improvement is to repeat the backward-looking PAC benchmark across seeds and participant splits.

## Official Sources

- `https://www.ieeespmb.org/2026/`
- `https://isip.piconepress.com/conferences/ieee_spmb/2026/html/guidelines.shtml`
