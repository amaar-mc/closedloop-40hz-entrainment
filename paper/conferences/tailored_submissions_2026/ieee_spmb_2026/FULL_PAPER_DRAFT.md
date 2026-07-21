<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 IEEE SPMB 2026 · priority #11
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** full-paper draft · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G2 · 28% to submission · **eligibility:** ok · label: `expired-this-cycle`  
> **Deadline:** 2026-07-01 (passed)  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# Target-Availability Stress Testing for Cross-Participant EEG PAC Forecasting

**Author:** Amaar M. Chughtai  
**Affiliation:** Valley Christian High School, San Jose, California, United States  
**Target venue:** IEEE SPMB 2026 full paper or poster abstract

**Format status:** this Markdown file is a content draft, not the final SPMB submission artifact. SPMB requires a PDF in the correct template; full papers are preferably 4-6 pages, two-column, 1 inch margins, 10 pt Times New Roman body text, abstract under 250 words, acknowledgments if appropriate, and IEEE-format references.

## Abstract

Adaptive neuromodulation requires EEG features that can be estimated and forecast before stimulation decisions are made. This retrospective signal-processing study evaluated whether frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase, can be forecast across participants during 40 Hz auditory stimulation, and whether performance survives a target construction closer to online availability. Using OpenNeuro `ds005048` (`N = 35`), a compact 12-feature temporal convolutional network achieved five-seed mean held-out `R^2 = 0.606` under complete-event PAC summaries, but dropped to `R^2 = 0.212` when PAC was recomputed from five-second backward-looking contexts and did not outperform Ridge regression (`R^2 = 0.216`). Offline replay showed that predictive control increased low-PAC stimulation coverage but reduced the above-median-PAC rest rate relative to reactive thresholding. These results show that information boundaries and target definitions can substantially alter model-selection conclusions in EEG forecasting pipelines.

**Keywords:** EEG, phase-amplitude coupling, signal processing, adaptive stimulation, temporal convolutional network, target definition

## I. Introduction

Closed-loop stimulation systems require signal features that are both meaningful and available before a decision is made. Retrospective EEG pipelines can violate this requirement if their targets summarize signal samples acquired after the modeled decision time. In adaptive auditory stimulation, this issue matters because a controller cannot use a future EEG summary when deciding whether to stimulate now.

This paper studies a narrow signal-processing question: can a frontal EEG PAC feature be forecast across participants during 40 Hz auditory stimulation, and does the conclusion hold when the PAC target is recomputed under a stricter information boundary? The project does not test clinical efficacy, source-level entrainment, or prospective stimulation response. PAC is used as a scalar EEG timing target for benchmarking.

The contribution is threefold. First, the study builds a held-out-participant forecasting benchmark using PAC-history and stimulation-context features. Second, it audits the target definition by replacing complete-event PAC labels with five-second backward-looking PAC estimates. Third, it evaluates an offline controller replay to expose the low-PAC-coverage/high-PAC-rest calibration problem produced by forecast-driven decisions.

## II. Data and Methods

The analysis used OpenNeuro `ds005048` version `1.0.1`, a public BIDS EEG dataset containing auditory-stimulation recordings from 35 memory-clinic participants. Recordings used 19 EEG channels sampled at 250 Hz. This study selected seven frontal channels: `Fp1`, `Fp2`, `F7`, `F3`, `Fz`, `F4`, and `F8`.

PAC was computed as a modulation-index feature using theta phase from `4-8 Hz` and gamma amplitude from `38-42 Hz`. Channel-level PAC values were averaged across the seven frontal channels to create one scalar target per timestamp. Because this PAC definition is used as an engineering feature, it should not be interpreted as definitive evidence of physiological theta-gamma coupling.

Participants were split into 24 training, 5 validation, and 6 held-out test participants. The temporal dataset contained 11,160 training, 2,605 validation, and 2,678 held-out test samples. Normalization statistics were fit on the training split only. Each sequence used a 20-step lookback and a five-step forecast horizon. The selected representation contained 12 inputs: 7 PAC-history features and 5 stimulation-context features.

The primary nonlinear model was a lightweight temporal convolutional network with residual temporal blocks, kernel size 3, dilations `[1, 2, 4, 8]`, and attention pooling before regression. Baselines included persistence and Ridge regression. Feature selection compared a 73-feature candidate representation, a spectral-only representation, PAC-history-only features, and PAC-history plus stimulation context.

The target-availability stress test recomputed PAC at each timestamp from a five-second backward-looking EEG context. This removes complete-event back-assignment and makes each PAC value depend only on EEG samples up to its timestamp. The stress test is closer to online availability than complete-event PAC summaries, but it is still not a validated streaming estimator because filtering and short-window PAC reliability remain limitations.

## III. Results

In the exploratory feature ablation, the 12-feature PAC-history plus stimulation-context representation outperformed broader alternatives on the fixed held-out split. Spectral-only features reached `R^2 = -0.420`, all 73 candidate features reached `R^2 = -0.025`, PAC-history-only features reached `R^2 = 0.344`, and the selected 12-feature representation reached `R^2 = 0.558`.

Across five random seeds on the same participant split, the selected TCN reached mean held-out test `R^2 = 0.606`, with a range from `0.558` to `0.647`. Persistence reached `R^2 = 0.104` at the same five-step horizon. This initial result indicates that the stored PAC series contained predictable structure across held-out participants.

The target-definition audit changed the conclusion. Complete-event PAC labels produced 104 unique held-out target values and 96.2 percent adjacent target repetition. Backward-looking PAC produced 2,678 unique held-out target values and zero adjacent target repetition. Under this stricter target definition, TCN performance dropped from `R^2 = 0.554` to `R^2 = 0.212`, while Ridge regression reached `R^2 = 0.216`.

Offline controller replay showed a separate tradeoff. A TCN predictive policy stimulated during low-PAC periods more often than a reactive threshold policy, 73.8 percent versus 51.7 percent. However, it rested during high-PAC periods less often, 50.7 percent versus 77.3 percent. Balanced alignment was therefore lower for the predictive policy than for the reactive threshold, 62.2 percent versus 64.5 percent.

## IV. Discussion

The event-summary benchmark supports one limited conclusion: a compact temporal model can predict structure in stored PAC-series entries across held-out participants. It does not establish that the same model is sufficient for online control. Once the PAC target was recomputed from backward-looking contexts, the nonlinear model no longer exceeded a linear Ridge baseline.

This matters for biomedical signal-processing work because retrospective targets often become easier than prospective targets. Complete-event labels can stabilize noisy estimates, but they can also make early windows inherit information from later signal samples. Reporting target construction, target repetition, and simple baselines is therefore necessary before treating a forecasting result as a control component.

The controller replay reinforces the same point. Increasing stimulation during low-PAC periods is not enough if the policy also reduces rest during above-median-PAC periods. A controller objective must balance low-PAC coverage and high-PAC sparing, and replay cannot estimate the physiological response to counterfactual stimulation decisions.

## V. Conclusion

In this fixed-split retrospective EEG benchmark, target definition changed the model-selection conclusion. A compact TCN appeared strong under complete-event PAC summaries, but under backward-looking PAC targets it did not outperform Ridge regression. Future adaptive auditory-stimulation work should validate streaming-compatible PAC estimation, repeat participant-level splits, and report low-PAC coverage/high-PAC-rest controller behavior before prospective testing.

## Acknowledgment

No external project funding was used for this student analysis. The author acknowledges Lahijanian, Aghajan, and Vahabi for releasing OpenNeuro `ds005048`.

## References

[1] M. Lahijanian, H. Aghajan, and Z. Vahabi, "Auditory gamma-band entrainment enhances default mode network connectivity in dementia patients," Scientific Reports, vol. 14, art. 13153, 2024.

[2] M. Lahijanian, H. Aghajan, and Z. Vahabi, "40Hz Auditory Entrainment," OpenNeuro dataset `ds005048`, version `1.0.1`, doi:10.18112/openneuro.ds005048.v1.0.1.

[3] A. B. L. Tort, R. Komorowski, H. Eichenbaum, and N. Kopell, "Measuring phase-amplitude coupling between neuronal oscillations of different frequencies," Journal of Neurophysiology, vol. 104, no. 2, pp. 1195-1210, 2010.

[4] J. Aru, J. Aru, V. Priesemann, et al., "Untangling cross-frequency coupling in neuroscience," Current Opinion in Neurobiology, vol. 31, pp. 51-61, 2015.

[5] S. Bai, J. Z. Kolter, and V. Koltun, "An empirical evaluation of generic convolutional and recurrent networks for sequence modeling," arXiv:1803.01271, 2018.

## Submission Notes

- Convert this to the current IEEE two-column SPMB template before submission.
- If time is short, submit the shorter poster abstract version in `SUBMISSION_DRAFT.md`.
- Add the benchmark figure from `../../mit_urtc_2026/figures/pac_benchmark_stress_test.png` if using the full paper route.

## Official Sources

- `https://www.ieeespmb.org/2026/`
- `https://isip.piconepress.com/conferences/ieee_spmb/2026/html/guidelines.shtml`
