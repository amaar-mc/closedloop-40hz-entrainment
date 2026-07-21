# MIT URTC Final Ambiguity Audit

**Audited:** 2026-06-23
**Standard:** wording should survive a skeptical technical reviewer without relying on charitable
interpretation

## Critical Clarification

### Stored-series causality is not online feature availability

The temporal builder constructs sequences so that the target index is five steps after the input
sequence endpoint. No later PAC-series entry enters an earlier sequence. However, the source pipeline
computes PAC over each complete event period and assigns that summary value to each constituent
two-second window. For an early window, the assigned PAC value summarizes EEG samples collected later
in the same event period.

The earlier manuscript wording could be read as evidence that all model inputs are already available
causally in a live stream. That interpretation is not supportable. The revised manuscript now states:

- the forecasting experiment is retrospective stored-series evaluation;
- event-period PAC back-assignment limits online availability;
- the model's left-only convolutions are ordered within the stored sequence;
- replay is not an end-to-end streaming predictor; and
- prospective work requires an online PAC estimator and higher-resolution targets.

## High-Priority Clarifications Applied

| Ambiguous wording or omission                             | Reviewer risk                                                 | Revision                                                                                     |
| --------------------------------------------------------- | ------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Title suggested an adaptive system had been evaluated     | Could be read as prospective closed-loop validation           | Title now names cross-participant PAC forecasts during auditory stimulation                  |
| Abstract used "persistence" without definition            | Baseline comparison was not self-contained                    | Defined it as a last-value persistence baseline at the same five-second horizon              |
| Replay scope could be mistaken for independent validation | Full-cohort replay could be mistaken for a second test        | Methods state that replay includes training, validation, and test trajectories               |
| Local artifact masking omitted its threshold and order    | Preprocessing was not reproducible from the paper             | Added `100 uV`, zero masking, and masking before rereferencing                               |
| Reactive controller lacked its numerical settings         | Replay could not be reconstructed from manuscript text        | Added 10-sample warm-up, 30-sample rolling baseline, and `-0.5` z-score trigger              |
| Predictive controller lacked its decision thresholds      | Decision logic was underspecified                             | Added normalized forecast-change thresholds `-0.3` and `+0.3`, fallback, and three-step hold |
| Oracle median was not explicitly retrospective            | Oracle could sound deployable                                 | Stated that it uses each full recorded trajectory and is neither causal nor deployable       |
| Horizon sweep was secondary and single-seed               | Could distract from the corrected target result               | Removed it from the final manuscript                                                         |
| Benchmark table duplicated Figure 1                       | Violated the guideline against duplicative tables and figures | Removed the table and retained exact values in prose and figure                              |
| Controller table abbreviates balanced alignment           | Metric name could be misread                                  | Defined balanced alignment immediately before the table                                      |
| Leakage paragraph used "causal indexing" broadly          | Could overstate end-to-end causality                          | Replaced with future-index ordering and separated it from online availability                |
| Gamma-band artifact warning lacked a citation             | Physiological limitation was asserted without support         | Added Hipp and Siegel's primary EEG artifact study                                           |

## Residual Scientific Risks

These are not wording problems and should remain visible:

1. PAC values are event-level summaries, not validated streaming estimates.
2. `82.2%` of five-step current-target pairs share the same PAC value.
3. Replay cannot model physiological response to counterfactual stimulation timing.
4. Replay protocol-context features come from the recorded schedule, not controller actions.
5. Controller replay includes all 35 trajectories and is not an independent held-out test.
6. The dataset is single-site and modest in size.

## Final Assessment

The revised paper is more conservative but materially stronger. It presents a defensible
retrospective forecasting result, a mixed offline controller result, and a concrete next validation
sequence without implying that a live therapeutic system has already been demonstrated.
