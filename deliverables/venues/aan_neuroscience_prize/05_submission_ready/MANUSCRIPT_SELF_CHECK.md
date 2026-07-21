# Manuscript Self-Check — AAN Neuroscience Research Prize

## ⚠️ RESIDUAL-RISK FLAG (READ FIRST) — highest-risk venue in this track

AAN requires "the original research and **written work** of the applicant" and requires **parent/guardian, teacher, and mentor e-signatures**. Two blocking items:

1. **Originality clause vs. AI-assisted drafting.** No explicit AI ban, but the "written work of the applicant" language is adjacent. This drafted manuscript is a **strong reference/starting point, not a paste-ready submission.** Before submitting, the author should EITHER (a) rewrite the report in his own words using this as a scaffold, OR (b) email **science@aan.com** to confirm AI-assisted drafting with disclosure is acceptable. **This is the highest residual-risk venue in the high-school-competition track.**
2. **Mentor e-signature.** AAN requires a mentor e-signature. The author has not documented a named mentor (see CONTRIBUTIONS_AND_AFFILIATIONS). The acknowledgements slot is left as `[AUTHOR TO CONFIRM]`. **If there is no real mentor who can honestly verify the work and sign, this application is not submittable as-is** — this is a structural gate, independent of the text.

## Number-tracing (every figure traces to RESULTS_CANONICAL)

| Claim in manuscript            | Value                                                                        | Canonical source                  | OK  |
| ------------------------------ | ---------------------------------------------------------------------------- | --------------------------------- | --- |
| Dataset                        | ds005048 v1.0.1, 35 participants, 19 ch @ 250 Hz, 7 frontal                  | RESEARCH_CORE §6                  | ✅  |
| Split / samples                | 24/5/6; 11,160/2,605/2,678                                                   | METHODS_CANONICAL M3              | ✅  |
| Static ceiling                 | R² = 0.287, 8 architectures, 1,457-param EEGNet                              | RESULTS_CANONICAL EEGNet table    | ✅  |
| Feature ablation (single-seed) | −0.420 / −0.025 / 0.344 / 0.558                                              | RESULTS_CANONICAL A1              | ✅  |
| Five-seed 12-feat              | mean 0.606, range 0.558–0.647                                                | RESULTS_CANONICAL A2              | ✅  |
| Shuffle control                | −0.332                                                                       | RESULTS_CANONICAL A2              | ✅  |
| **Stress-test matched pair**   | **0.554 → 0.212** (same architecture, single seed)                           | task brief / RESULTS_CANONICAL A4 | ✅  |
| Stress-test baselines          | event: Ridge 0.260, persist 0.104; leakage-free: Ridge 0.216, persist −0.897 | task TARGET-DEFINITION block      | ✅  |
| Unique targets / repetition    | 104 → 2,678; 96.2% adjacent-same → 0                                         | task brief; existing draft        | ✅  |
| Controller replay              | 62.2 / 73.8 / 50.7 (TCN) vs 64.5 / 51.7 / 77.3 (reactive)                    | RESULTS_CANONICAL B2              | ✅  |

## Forbidden-pairing sweep

- [x] **0.606 NEVER paired with 0.212.** The stress-test before/after uses **0.554 → 0.212** only. The 0.606 five-seed number appears once, in the feature-selection paragraph, explicitly tagged as a different (earlier, smaller) model generation and never as the stress-test "before."
- [x] **No "27,139-param model achieves R² = 0.606."** The 27,139 param count is not stated in this report; the forecasting numbers (0.606, 0.558) are attributed to the earlier experimental model, and the controller numbers to the deployed model, without pairing a Gen-B count to a Gen-A result.
- [x] **No 72.1% / 82.6% / 91% oracle / "35/35 benefit"** anywhere. Controller numbers are the current 62.2 / 73.8 / 50.7.
- [x] Persistence AND Ridge reported next to every TCN forecasting number (horizon caption, stress test).
- [x] Metrics from the three generations are explicitly not pooled (stated in text).

## Clinical-claim sweep

- [x] No efficacy, no patient-outcome improvement, no disease-slowing, no prospective/live deployment, no therapeutic validation.
- [x] "Retrospective replay" / "offline replay" language used; replay-≠-physiology stated explicitly.
- [x] Event-level PAC label granularity + online-availability limit stated (it is the spine of the report).
- [x] Spectral-anatomy explanation phrased as a hypothesis ("consistent with the ablation, not something the ablation proves").
- [x] Controller result framed as a mixed trade-off (alignment below reactive), not a win.

## Citation check (all from CITATION_LEDGER)

- [x] Iaccarino 2016, Martorell 2019, Chan 2025, Lahijanian 2024, Tort 2010, Lawhern 2018, Thompson & Spencer 1966 — all LOW-risk verified entries.
- [x] Sahu & Tseng 2023 (Front. Integr. Neurosci. 17:1146687) used with corrected author/journal — **NOT** "Fortunato / Front. Neurosci."
- [x] Non-responder statistic **softened** ("a substantial fraction … show little measurable entrainment") with an explicit `[AUTHOR: verify source]` note; no specific 23/33 or ~30% number stated. Reason: the ledger flags the 23/33 figure as coming from a source distinct from the review actually cited.

## AI-tells sweep (against AI_WRITING_TELLS_AND_AVOIDANCE)

- [x] No delve / underscore / showcase / intricate / pivotal / robust / leverage / harness / tapestry / realm.
- [x] No "It is important to note," "In today's world," "plays a pivotal role."
- [x] No Moreover/Furthermore/Additionally chains.
- [x] Sentence length varied; short blunt lines used ("This is a targeting trade-off, not a win.").
- [x] Em-dashes present but not on every line.
- [x] First-person author voice; personal stake stated calmly, not dramatically; process-and-mistake content included (the unexpected ceiling; distrusting the strong result).
- [x] Conclusion advances a claim (target definition can decide the conclusion) rather than only summarizing.

## Format / venue fit

- [x] 300-word structured abstract (OBJECTIVE / BACKGROUND / DESIGN-METHODS / RESULTS / CONCLUSIONS) — **verify final count = 300 after any author edits.**
- [x] Longer research-report narrative (~1,150 words) with background, methods, results, interpretation, limitations, future work.
- [x] Framed as a neuroscience-methods project (PAC as a scalar EEG timing target), not an engineering conference paper — matches AAN reader expectations and the "interpretation of data / pitfalls" that AAN rewards.
- [x] Figures carried as hooks with author-insert instructions; no invented figure data.
