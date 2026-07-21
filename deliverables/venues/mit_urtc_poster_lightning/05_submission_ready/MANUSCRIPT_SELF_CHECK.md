# Manuscript Self-Check — MIT URTC 2026 (Poster + Lightning)

_One-page integrity checklist for the extended abstract `SUBMISSION_READY_MANUSCRIPT.md`. All numbers confirmed against RESULTS_CANONICAL.md (verified 2026-07-16)._

## 1. Every number traces to RESULTS_CANONICAL

| Number                                                                                           | Where            | Canonical source   | ✓   |
| ------------------------------------------------------------------------------------------------ | ---------------- | ------------------ | --- |
| 35 participants; 7 frontal channels; split 24/5/6                                                | Abstract         | Dataset facts / M3 | ✓   |
| Ablation −0.025 (73 feat) → 0.558 (12 feat); 7-feat 0.344; 61-feat −0.420                        | Abstract, Fig. 1 | A1                 | ✓   |
| Five-seed mean 0.606 (range 0.558–0.647); persistence 0.104; shuffle −0.332                      | Abstract         | A2                 | ✓   |
| Static ceiling R² = 0.287 across ~1,457–~2M params                                               | Abstract         | EEGNet static      | ✓   |
| Horizon sweep 0.725/0.607/0.577/0.370/0.669 vs 0.726/0.178/0.104/−0.007/−0.081                   | Fig. 2           | A3                 | ✓   |
| Stress test 104 → 2,678 targets; 96.2% → 0 adjacency; 0.554 → 0.212; Ridge 0.216; persist −0.897 | Abstract, Fig. 3 | A4                 | ✓   |
| Controller 45.0/64.5/62.2/100; 61.4/51.7/73.8/100; 28.6/77.3/50.7/100                            | Abstract, Fig. 4 | B2                 | ✓   |

## 2. No forbidden pairing / generation mixing

- [x] **0.606 and 0.212 never stated as a before/after pair.** The matched drop is **0.554 → 0.212**; 0.212 is anchored to Ridge 0.216 ("no longer beat Ridge regression at 0.216").
- [x] **No param count paired with the wrong result** (the extended abstract avoids stating 22,914 / 27,139 explicitly to keep the ~800-word text clean; where params matter for the ceiling point, only the static-search range ~1,457–~2M is used, which is the correct EEGNet-static context).
- [x] **Historical Gen-C numbers (72.1% / 82.6% / 91% / 35/35 / 31,043 params) absent from the submitted abstract, script, and figure captions.** They appear only inside the author-facing HTML-comment note and the FIGURE 4 warning, explicitly labeled "superseded historical" so the author does not reuse the stale image.
- [x] The phantom 5,154 param count does not appear.

## 3. No clinical / out-of-bounds claims

- [x] Explicit: "none of this validates a treatment system… I make no clinical, disease-modifying, or deployment claim."
- [x] "Offline replay" / "replay against recorded PAC" language; states it cannot estimate physiological response to counterfactual stimulation and spans all splits (integration diagnostic, not held-out test).
- [x] PAC label limitation (complete-event summaries; online-availability) stated and made central to the stress-test paragraph.
- [x] Controller framed as a **mixed tradeoff** (better low-PAC coverage, worse high-PAC sparing, alignment below reactive).
- [x] Spectral-anatomy explanation phrased as hypothesis ("consistent with… does not prove").
- [x] Persistence **and** Ridge reported next to TCN numbers.

## 4. Citations

- [x] Extended abstract makes no numbered in-text citations (poster format); the dataset is named (OpenNeuro ds005048 v1.0.1) and the PAC method is attributed to Tort in prose. Full references live on the poster's reference strip — reuse the verified list from the paper deliverable (all 13 checked against CITATION_LEDGER / CrossRef / arXiv this session).
- [x] No non-responder statistic is quoted, so no citation risk there.

## 5. AI-writing tells swept

- [x] Lexical scan → **0 hits** (delve, underscore, showcase, pivotal, leverage, harness, comprehensive, robust, "paves the way," moreover/furthermore/additionally, etc.).
- [x] Sentence rhythm varied; bold lead-ins carry real claims, not decoration.
- [x] Author voice per AUTHOR_VOICE_GUIDE: grandmother personal-stake opening (lightning slide 1), honest-number move, "try to break my own best result" process line, causal-guarantee framing.
- [x] Closing advances a bounded claim (method + audit; named next steps), not a grandiose sweep.

## 6. Affiliation / authorship / eligibility

- [x] Author: Amaar M. Chughtai, Valley Christian High School (self-attribution).
- [x] No mentor/lab/institution named.
- [x] **Eligibility: unconditional** for this track (sole HS author per URTC FAQ) — no hold, unlike the paper track.

## 7. Length & structure

- [x] Extended-abstract body **774 words** → within the 750–1000 target.
- [x] Includes lightning-talk script (7 slides / ~5 min) and four figure hooks (two to verified existing images, two to regenerate from canonical data/JSON).

## Residual items for the author

1. Confirm the 2026 URTC cycle/portal is open before submitting (no eligibility hold on this track).
2. Regenerate the controller figure (Fig. 4) from `results/metrics/controller_comparison_12feat.json`; do NOT reuse `results/figures/controller_comparison.png` (superseded Gen-C, 72.1%/82.6%).
3. Build the Fig. 1 ablation bar chart (no standalone image exists yet) from RESULTS_CANONICAL Table A1.
4. Reuse the verified reference list from the paper deliverable for the poster's reference strip.
