# Polish Report — MIT URTC 2026 (IEEE Paper Track)

_Senior-editor refine → test → polish pass on `SUBMISSION_READY_MANUSCRIPT.md`. Verified against RESULTS_CANONICAL.md, METHODS_CANONICAL.md, RESEARCH_CORE.md, LIMITATIONS_AND_THREATS.md, and CITATION_LEDGER.csv (all dated 2026-07-16). Pass performed 2026-07-17._

**Verdict: all of T1–T8 PASS.** The incoming draft was already strong and factually clean; this pass made three targeted edits (one factual-contradiction fix, two claim-integrity/clarity fixes in the conclusion) and proved the result. No claims were inflated and no results were added.

- **Word count before:** 3,891 body words (excl. HTML comments and references); 4,595 raw file words.
- **Word count after:** 3,892 body words (excl. HTML comments and references); 4,276 words excl. HTML comments incl. references. (Raw-file drop from 4,595 is the internal comments; submitted text is essentially length-neutral.)
- **AI lexical tells found:** 0 (draft already clean). **Substantive edits made:** 3.
- **Residual honest-risk framing preserved:** yes — mixed controller result, target-definition fragility, and all hard boundaries intact and foregrounded.

---

## T1–T8 verification table

| Test                                             | Result   | Evidence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------------------------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **T1** — every numeric claim traces to canonical | **PASS** | 41/44 spot-checked canonical numbers appear verbatim in the submitted text; the 3 not in prose (single-seed horizon TCN 0.577 @5 s, 0.370 @8 s, 0.669 @10 s) are intentionally carried by the Figure 1 hook (source `results/figures/horizon_sweep_pac_stim.png`, data = RESULTS_CANONICAL A3). §IV-B prose states the 1 s tie (0.725 vs 0.726), 3 s divergence (0.607 vs 0.178), five-seed 0.606/0.104 @5 s, shuffle −0.332; the claim "the gap stays open through 10 seconds" holds at every horizon in A3. See the number-source list below.                                           |
| **T2** — no forbidden 0.606↔0.212 pairing        | **PASS** | Zero unsafe 0.606↔0.212 proximities. The only two proximities (§IV-D, §VII) both carry the disambiguating 0.554 anchor or the explicit "I do not compare it to the five-seed 0.606" sentence. The legitimate matched pair `0.554 → 0.212` is present. `27,139 ↔ 0.606` proximity = **0** (verified programmatically).                                                                                                                                                                                                                                                                     |
| **T3** — model generations kept distinct         | **PASS** | Submitted text contains 22,914 (Gen-A experimental, tied to ablation + five-seed 0.606) and 27,139 (Gen-B/integrated, tied to stress test + controller replay), introduced in one §III-D sentence that keeps them apart. **31,043 / "35/35" / "35 out of 35" / 72.1% / 82.6% / 91% / g=1.31 / g=4.47 appear NOWHERE in the submitted text** — 72.1%/82.6% occur only inside the §V HTML-comment margin note explicitly labeled "HISTORICAL 73-feature model."                                                                                                                             |
| **T4** — no clinical overclaim                   | **PASS** | No efficacy / patient-outcome / disease-slowing / prospective-deployment / therapeutic-validation phrase present. "Retrospective controller replay" / "offline replay" used throughout; §V and §VI-1 state the replay "cannot estimate how a brain would have physiologically responded to counterfactual decisions." "improves cognition" appears only inside a reference title (Martorell 2019, ref [5]).                                                                                                                                                                               |
| **T5** — every citation real & verified          | **PASS** | 13 references, all cited in body ([1]–[13]), all drawn from CITATION_LEDGER.csv or brief-verified. Bad "Fortunato et al. 2023 Front Neurosci" **removed**; correct **Sahu, P. P. & Tseng, P. (2023), Front. Integr. Neurosci. 17:1146687** present as [7]. Non-responder stat softened to "prior work reports substantial non-responder rates" with no numeric rate + `[AUTHOR: verify]` margin note. Three brief-added refs formatted correctly: [4] Soleimani doi 10.1038/s41398-023-02565-5; [12] Hipp & Siegel doi 10.3389/fnhum.2013.00338; [13] Aru doi 10.1016/j.conb.2014.08.002. |
| **T6** — AI-writing tells swept                  | **PASS** | 0 hits on the full lexical blacklist (delve, underscore, showcase, intricate, pivotal, meticulous, leverage, harness, realm, tapestry, testament, groundbreaking, transformative, "paves the way," "it is worth noting," "moreover/furthermore/additionally," "in conclusion," cutting-edge, seamless, robust-as-filler). 0 sentence-initial transition chains. Em-dashes = 21 across ~4,276 words (~1 per 204 words — well below "one per line"). Sentence length mean 21.5 w, range 4–61 w (deliberate rhythm: "The controller result is mixed." vs packed methods sentences).          |
| **T7** — length / format compliance              | **PASS** | Body (no refs, no comments) = 3,892 w; submitted incl. refs = 4,276 w. Within the ~4,500–5,500-word working envelope for ~5 IEEEtran double-column pages with 2 tables + 2 figures. `[AUTHOR: confirm final page count after IEEEtran typesetting; trim §II or §VI if >5 pp]` retained.                                                                                                                                                                                                                                                                                                   |
| **T8** — structural completeness                 | **PASS** | All required elements present: Title; author + Valley Christian HS; Abstract (~215 w); Index Terms; I Introduction; II Related Work; III Dataset & Methods (A–D); IV Experiments (A ablation, B horizon, C five-seed, D target-definition stress test, E leakage checks); V Retrospective Controller Replay; VI Limitations (7 items); VII Conclusion; Acknowledgment; References [1]–[13]; Table I; Table II; Figure 1 hook; Figure 2 hook.                                                                                                                                              |

---

## T1 number-source map (submitted-text numbers → canonical source)

| Number(s)                                                                                                                           | §/element         | Canonical source                                                        |
| ----------------------------------------------------------------------------------------------------------------------------------- | ----------------- | ----------------------------------------------------------------------- |
| 35 participants; 19 ch @ 250 Hz; 7 frontal (Fp1,Fp2,F7,F3,Fz,F4,F8)                                                                 | Abstract, §III-A  | RESEARCH_CORE §6 / METHODS M1                                           |
| Split 24/5/6; samples 11,160 / 2,605 / 2,678                                                                                        | §III-C            | METHODS M3                                                              |
| EEGNet 1,457 params; static R² = 0.287                                                                                              | §III-D, §IV-A     | METHODS M4 / RESULTS EEGNet table                                       |
| Ablation −0.420 / −0.025 / 0.344 / 0.558                                                                                            | Table I           | RESULTS A1                                                              |
| Five-seed mean 0.606, range 0.558–0.647; population SD 0.029 / sample SD 0.033                                                      | §IV-B, §IV-C      | RESULTS A2                                                              |
| Shuffle-label control −0.332                                                                                                        | §IV-B, §IV-E      | RESULTS A2                                                              |
| Horizon (prose) 0.725/0.726 @1 s, 0.607/0.178 @3 s; (Fig. 1) 0.577/0.370/0.669 TCN, persistence to −0.081                           | §IV-B, Fig. 1     | RESULTS A3                                                              |
| Stress test 0.554 → 0.212 (TCN), Ridge 0.216, persistence 0.104 → −0.897; 104 → 2,678 targets; 96.2% → 0 adjacency                  | §IV-D, Fig. 2     | RESULTS A4 / stress-test                                                |
| Controller replay align 45.0/64.5/62.2/100; low-stim 61.4/51.7/73.8/100; high-rest 28.6/77.3/50.7/100; gaps −6.55/21.09/21.02/33.36 | Table II          | RESULTS B2                                                              |
| 22,914 (Gen-A experimental) / 27,139 (Gen-B integrated) params                                                                      | §III-D, §IV-D, §V | RESULTS Gen map / B1                                                    |
| Δlow-PAC +22.1 pp; Δhigh-rest −26.6 pp; PAC-gap ≈63% of oracle                                                                      | §V                | Derived (recomputed): 73.8−51.7=22.1; 77.3−50.7=26.6; 21.02/33.36=0.630 |

Derived values recomputed, not typed from memory: 73.77−51.67 = **22.10 pp**; 77.30−50.68 = **26.62 pp**; 21.02/33.36 = **0.630 → 63%**. All consistent with the manuscript.

---

## Change log (this pass)

1. **§III-A cohort — FACTUAL CONTRADICTION FIXED.**
   _Before:_ "The local BIDS release contains 35 participants **spanning normal cognition, mild cognitive impairment, and Alzheimer's disease labels (two participants have missing group labels)**."
   _After:_ "The local BIDS release contains 35 participants **with dementia**."
   _Why:_ the old sentence was an unsourced elaboration that contradicted the manuscript's own abstract ("35 participants with dementia") and all three canonical sources (METHODS M1, RESEARCH_CORE §6 — both "35 dementia participants"). A reviewer comparing abstract to methods would flag the mismatch. Corrected to the canonical descriptor.

2. **§VII conclusion — CLAIM-PAIRING ANCHOR ADDED (T2 hardening).**
   _Before:_ 0.606 and 0.212 sat two sentences apart with no disambiguating anchor — a skimming reader could misread a "0.606 → 0.212" drop.
   _After:_ inserted the short sentence "That five-seed result belongs to the event-summary target." and rewrote the next sentence to state the matched pair explicitly: "In a separate matched single-seed test, moving the integrated architecture to a leakage-free target dropped its score from R² = 0.554 to 0.212, level with Ridge (0.216) …".
   _Why:_ mirrors the protective framing §IV-D already uses; makes the forbidden pairing unmisreadable even out of context. (Also improves rhythm with a 6-word sentence and removes one em-dash pair.)

3. **§VII conclusion — GENERATION BOUNDARY SHARPENED (T3 hardening).**
   Within the same edit, "moving the same architecture" → "moving **the integrated** architecture," so the stress-test model (27,139, integrated) is not blurred with the five-seed model (22,914, experimental). Matches §IV-D's "the same 27,139-parameter architecture."

_No other text changed._ The honest framing (mixed controller result, target-definition fragility as a genuine contribution), the first-person author voice, the HELD-status HTML comment, the §V superseded-figure margin note, and all `[AUTHOR TO CONFIRM]` markers are preserved.

---

## Verified non-errors (do NOT "fix")

- **Ref [13] "J. Aru, J. Aru, V. Priesemann, et al."** is correct — the paper has two Aru authors (Juhan Aru and Jaan Aru), both initial "J." Not a duplication.
- **Ref [2] page/article "e70792" and ref [3] article "13153"** are article numbers, not page ranges (correct for Alzheimer's & Dementia and Scientific Reports).
- **Single-seed horizon values live in Figure 1, not prose** — this is a deliberate figure-carries-the-sweep choice, not a missing number.
- **Static R² = 0.287 reported as a data ceiling** (not a failure) — matches RESULTS_CANONICAL framing.

---

## Residual items for the author (decisions only the author can make — unchanged from prior self-check)

1. Confirm mentorship specifics OR paper-track eligibility, then fill the Acknowledgment `[AUTHOR TO CONFIRM]` placeholder. (Paper track may require more than informal mentorship; the poster/lightning track is unconditionally eligible.)
2. Confirm the 2026 URTC submission cycle is open with a live portal before submitting (HELD condition (b)).
3. Verify (or keep softened, number-free) the non-responder statistic in §II; resolve the `[AUTHOR: verify non-responder source]` note.
4. Regenerate the §V controller figure from `results/metrics/controller_comparison_12feat.json` — do **not** reuse `results/figures/controller_comparison.png` (superseded Gen-C figure showing 72.1%/82.6%).
5. Confirm final IEEEtran page count ≤ 5 after typesetting; trim §II or §VI if over.
6. Confirm the hardware string for a methods/repro note (METHODS M10 flags a poster inconsistency: "Apple Silicon (MPS)" vs "RTX 3080").
