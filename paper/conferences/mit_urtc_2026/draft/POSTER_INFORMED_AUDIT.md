# Poster-Informed Manuscript Audit

**Audited:** 2026-05-31  
**Target:** MIT URTC manuscript  
**Poster artifacts visually inspected:** `submission/poster/vfinal_poster.pdf` and
`archive/CSEF_Old/Poster_FINAL/CSEF_FINAL.pdf`

## Executive Finding

The posters reveal a broader and more impressive engineering story than the original MIT URTC draft:
the project explored raw-EEG PAC estimation, temporal feature design, forecasting, controller replay,
and a future streaming path. That systems arc is worth preserving.

The posters are not a safe source for copying headline claims directly into the paper. They combine
multiple experimental generations. The revised manuscript therefore imports the defensible
engineering structure while reporting only results traceable to the final paper evidence map.

## Claim Map

| Poster claim                                                                  | Status for MIT manuscript | Reason                                                                                                                                                    |
| ----------------------------------------------------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 73 features to 12 features improves event-summary forecasting                 | SUPPORTED                 | The manuscript reports the matched ablation and five-seed event-summary benchmark.                                                                        |
| Feature selection matters more than adding spectral inputs                    | SUPPORTED WITH BOUNDARY   | The ablation supports the performance conclusion. It does not prove a biological mechanism for spectral-feature failure.                                  |
| Broader two-stage prototype: current-PAC estimation then temporal forecasting | SUPPORTED WITH BOUNDARY   | Useful system context. The raw-EEG estimator is not composed with the forecasting or replay loop validated in the manuscript.                             |
| `72.1%` alignment and `82.6%` low-PAC targeting                               | HISTORICAL ONLY           | These values come from the older 73-feature replay. The refreshed 12-feature replay is `62.2%` balanced alignment and `73.8%` low-PAC targeting.          |
| 35 of 35 subjects benefit                                                     | EXCLUDED                  | This is tied to the older replay and should not be presented as a final-checkpoint result.                                                                |
| TCN is robust across fatigue models                                           | EXCLUDED                  | The poster's fatigue experiments use a trend-based adaptive heuristic, not the TCN.                                                                       |
| Full pipeline runs in real time on consumer hardware                          | EXCLUDED                  | Prototype direction only. End-to-end EEGNet-to-TCN-to-controller streaming validation is not established.                                                 |
| Causal TCN has no future leakage                                              | REVISED                   | Left-only TCN padding is correct within the stored series, but complete-event PAC back-assignment makes primary inputs unavailable at live decision time. |
| 35 dementia patients                                                          | REVISED                   | The source cohort includes normal cognition, mild cognitive impairment, and Alzheimer's disease classifications.                                          |

## Important New Evidence Added to the Manuscript

The revised manuscript now includes the backward-looking PAC stress test from
`archive/experimental/sliding_pac`. It is the clearest response to a skeptical reviewer:

| Metric                  | Event-summary PAC | Backward-looking PAC |
| ----------------------- | ----------------: | -------------------: |
| Unique held-out targets |               104 |                2,678 |
| Adjacent same targets   |             96.2% |                 0.0% |
| Persistence R-squared   |             0.104 |               -0.897 |
| Ridge R-squared         |             0.260 |            **0.216** |
| TCN R-squared           |         **0.554** |                0.212 |

This result is more impressive scientifically than repeating the poster's strongest headline. It
shows that the project identified a realistic failure mode, quantified it, and changed the
interpretation rather than hiding it.

## Manuscript Edits Completed

1. Retitled the paper around target-definition stress testing.
2. Rewrote the abstract to report the event-summary result and the backward-looking PAC stress test.
3. Added a bounded statement about the broader raw-EEG prototype.
4. Added a methods subsection describing the backward-looking PAC benchmark and its zero-phase-filter
   limitation.
5. Added a one-column figure explaining the two information boundaries.
6. Added a results table comparing persistence, Ridge, and TCN under both target constructions.
7. Reframed the discussion and conclusion around target-definition audits, compact feature design,
   and disciplined separation of replay from deployment claims.

## Residual Risks

- The backward-looking benchmark uses `filtfilt` inside each bounded context. It prevents samples
  after the forecast endpoint from entering the input, but it is not a production streaming filter.
- The backward-looking comparison is single-seed and should be replicated.
- Repeated participant-level splits or grouped cross-validation remain important.
- Paper-track eligibility for a high-school author still requires confirmation of the qualifying
  university relationship.
