# Manuscript Self-Check — MIT URTC 2026 (IEEE Paper Track)

_One-page integrity checklist for `SUBMISSION_READY_MANUSCRIPT.md`. Every box confirmed against RESULTS_CANONICAL.md, METHODS_CANONICAL.md, LIMITATIONS_AND_THREATS.md, and CITATION_LEDGER.csv (all verified 2026-07-16)._

## 1. Every number traces to RESULTS_CANONICAL

| Manuscript number                                                                                                                         | Where used        | Canonical source              | ✓   |
| ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------- | ----------------------------- | --- |
| 35 participants **with dementia**; 19 ch @ 250 Hz; 7 frontal                                                                              | Abstract, §III-A  | RESEARCH_CORE §6 / METHODS M1 | ✓   |
| Split 24/5/6; samples 11,160 / 2,605 / 2,678                                                                                              | §III-C            | M3                            | ✓   |
| EEGNet 1,457 params; static R² = 0.287                                                                                                    | §III-D, §IV-A     | EEGNet static / M4            | ✓   |
| Ablation −0.420 / −0.025 / 0.344 / 0.558                                                                                                  | Table I           | A1                            | ✓   |
| Five-seed mean 0.606, range 0.558–0.647                                                                                                   | §IV-B, §IV-C      | A2                            | ✓   |
| Shuffle-label control −0.332                                                                                                              | §IV-B, §IV-E      | A2                            | ✓   |
| Horizon sweep TCN 0.725/0.607/0.577/0.370/0.669; persist 0.726/0.178/0.104/−0.007/−0.081                                                  | §IV-B, Fig. 1     | A3                            | ✓   |
| Stress test matched pair 0.554 → 0.212; Ridge 0.260 → 0.216; persist 0.104 → −0.897; 104 → 2,678 targets; 96.2% → 0 adjacency             | §IV-D, Fig. 2     | A4 / stress-test              | ✓   |
| Controller replay 45.0/64.5/62.2/100 (align); 61.4/51.7/73.8/100 (low-stim); 28.6/77.3/50.7/100 (high-rest); gaps −6.55/21.09/21.02/33.36 | Table II          | B2                            | ✓   |
| 27,139 params = integrated/stress-test/controller architecture                                                                            | §III-D, §IV-D, §V | B1                            | ✓   |
| 22,914 params = experimental TCN behind ablation + five-seed                                                                              | §III-D            | Gen A                         | ✓   |
| Δlow-PAC +22.1 pp; Δhigh-rest −26.6 pp; gap ≈63% of oracle                                                                                | §V                | derived, recomputed           | ✓   |

_Derived values (22.1, 26.6, 63%, five-seed mean/range) were recomputed in-kernel, not typed from memory._

## 2. No forbidden pairing / generation mixing

- [x] **0.606 is never paired with 0.212 as a before/after.** The only matched drop stated is **0.554 → 0.212** (§IV-D; abstract "in a matched single-seed comparison, forecasting R² drops from 0.554 to 0.212"; and the conclusion, hardened this pass: "That five-seed result belongs to the event-summary target. In a separate matched single-seed test, moving the integrated architecture to a leakage-free target dropped its score from R² = 0.554 to 0.212, level with Ridge (0.216)"). Where 0.606 and 0.212 appear in the same passage (abstract, conclusion, §IV-D), 0.212 is anchored to **Ridge 0.216** and to 0.554, and §IV-D explicitly states _"I do not compare it to the five-seed 0.606, which comes from the separate experimental model."_ Verified programmatically: 0 unsafe 0.606↔0.212 proximities; 27,139↔0.606 proximity = 0.
- [x] **No "27,139-param model achieves 0.606."** 27,139 is attached only to the integrated architecture / stress test / controller. The 0.606 is attributed to the five-seed experimental (22,914-param) TCN. The two param counts are introduced in one sentence in §III-D that keeps them apart on purpose.
- [x] **Historical Gen-C numbers (72.1% / 82.6% / 91% oracle / 35/35 benefit / 31,043 params / g=1.31/4.47) are NOT in the submitted text.** They appear once, inside an HTML comment margin note in §V, explicitly labeled "HISTORICAL 73-feature model" as a warning to regenerate the stale figure. HTML comments do not render in the compiled PDF/portal text.
- [x] **The 5,154 phantom param count does not appear.**
- [x] Forecasting-study, stress-test, and controller-replay numbers are presented as distinct generation paths and never pooled (stated in §III-D and §V).

## 3. No clinical / out-of-bounds claims

- [x] No efficacy, patient-outcome, disease-slowing, prospective-deployment, or live-therapeutic claim anywhere.
- [x] "Retrospective controller replay" / "offline replay" used throughout; §V and §VI-1 state the replay cannot estimate physiological response to counterfactual decisions.
- [x] PAC label limitation (complete-event summaries assigned back to windows; online-availability limit) stated in §III-B, §IV-D, §IV-E, and §VI-4.
- [x] Controller result framed as **mixed** (better low-PAC coverage, worse high-PAC sparing, alignment below reactive) in abstract, §V, §VI-2, and conclusion.
- [x] Spectral-feature explanation phrased as a **hypothesis** ("consistent with… does not prove," §IV-A), not fact.
- [x] Persistence **and** Ridge reported next to every TCN forecasting claim (Table I context, §IV-B, §IV-D, Fig. 2).
- [x] Static R² = 0.287 framed as a data ceiling, not a failure (§IV-A).

## 4. Citations verified

- [x] All 13 references drawn from CITATION_LEDGER.csv or verified this session. Refs [1]–[9], [11] map to ledger rows (LOW risk). [4] Soleimani, [12] Hipp & Siegel, [13] Aru re-verified against CrossRef this session; [10] Bai TCN confirmed via arXiv 1803.01271.
- [x] **Corrected the known bad citation:** the old "Fortunato et al. 2023 Front Neurosci" is replaced by the correct **Sahu, P. P. & Tseng, P. (2023), _Frontiers in Integrative Neuroscience_ 17:1146687** (ref [7]).
- [x] **Non-responder statistic softened.** §II says "prior work reports substantial non-responder rates" with NO specific 23/33 or ~30% number, plus an `[AUTHOR: verify non-responder source]` margin note — because Sahu & Tseng is a review and the primary source of that statistic is not confirmed.
- [x] Dataset citation [3]/[11] = Lahijanian et al. 2024 (doi 10.1038/s41598-024-63727-z) + OpenNeuro ds005048 v1.0.1, matching the dataset's own HowToAcknowledge field.

## 5. AI-writing tells swept

- [x] Lexical scan (delve, underscore, showcase, intricate, pivotal, meticulous, leverage, harness, realm, tapestry, testament, boast, seamless, comprehensive, robust, groundbreaking, transformative, "paves the way," "it is worth noting," "moreover/furthermore/additionally") → **0 hits**.
- [x] No formulaic transition chains; transitions are "but / so / because / yet" doing real logical work.
- [x] Sentence length varied deliberately (short declaratives — "My grandmother has dementia." "That is the next thing to fix." — against longer methods sentences).
- [x] Em-dashes used but not over-relied (≈26 across ~4,300 words including refs; not one per line).
- [x] Conclusion advances a bounded claim and names the next question; it does not merely restate the abstract.
- [x] First-person author voice per AUTHOR_VOICE_GUIDE: personal-stake opening, analogy-before-jargon, honest-number move, "architectural guarantee" causal framing, ceiling insight. Historical spoken numbers updated to current 12-feature results.
- [x] At least one detail only the author could supply (the ceiling-convergence pivot in §IV-A; the "target definition was carrying the result" realization in §IV-D).

## 6. Affiliation / authorship

- [x] Author line: Amaar M. Chughtai, Valley Christian High School (legitimate self-attribution).
- [x] No mentor, lab, or institution named. Acknowledgment carries the literal `[AUTHOR TO CONFIRM ...]` placeholder.
- [x] Independence + AI-assistance stated in Acknowledgment; full disclosure in AI_USE_DISCLOSURE.md.

## 7. Structure & length

- [x] IEEE sections present: Title; Author + Valley Christian HS; Abstract (~215 w); Index Terms; I Introduction; II Related Work; III Dataset & Methods; IV Experiments (ablation + five-seed + horizon sweep + target-definition stress test); V Retrospective Controller Replay; VI Limitations; VII Conclusion; Acknowledgment; References (IEEE numbered).
- [x] Body ≈ 3,892 words (excl. internal comments and references); 4,276 words excl. comments incl. references → fits ~5 double-column IEEEtran pages with 2 figures + 2 tables. **[AUTHOR: confirm final page count after IEEEtran typesetting; trim §II or §VI if over 5 pp.]**
- [x] HELD-status header block present as an HTML comment: do not submit until (a) mentorship/eligibility documented and (b) 2026 URTC cycle confirmed open.

## Residual items for the author (not defects — decisions only you can make)

1. Confirm mentorship specifics OR paper-track eligibility, then fill the Acknowledgment placeholder.
2. Confirm the 2026 URTC submission cycle is open before submitting.
3. Verify (or drop the number for) the non-responder statistic in §II.
4. Regenerate the §V controller figure from `results/metrics/controller_comparison_12feat.json` (do NOT reuse `results/figures/controller_comparison.png` — it is the superseded Gen-C figure).
5. Confirm final IEEEtran page count ≤ 5.
