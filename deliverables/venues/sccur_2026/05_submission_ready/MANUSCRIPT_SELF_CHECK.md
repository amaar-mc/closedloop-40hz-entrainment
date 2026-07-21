# Manuscript Self-Check — SCCUR 2026

## ⚠️ RESIDUAL-RISK FLAG (READ FIRST) — text ready, submission GATED

**SCCUR structurally requires a named faculty advisor who reviews the abstract** — this is a required form field, not optional. High-school presenters are admitted only in the undergraduate faculty-guided research category. Consequences:

- **The abstract text is submission-READY. The submission itself is BLOCKED** until the author either (a) secures a faculty advisor who will review and endorse the abstract, OR (b) emails **2026sccur@sdsu.edu** to confirm whether an independent high-school project qualifies without a faculty advisor.
- The author has ongoing _informal_ mentorship by a professor but has provided no name/institution/role. Informal mentorship may or may not satisfy SCCUR's "faculty-guided" requirement — **the author must confirm before submitting.** The advisor slot is left `[AUTHOR TO CONFIRM]`.
- **Do not submit until the advisor field can be filled honestly.** This is an eligibility gate, independent of text quality.

## Number-tracing (every figure traces to RESULTS_CANONICAL)

| Claim                        | Value                                                         | Canonical source             | OK  |
| ---------------------------- | ------------------------------------------------------------- | ---------------------------- | --- |
| Dataset                      | ds005048, 35 participants, 7 frontal                          | RESEARCH_CORE §6             | ✅  |
| Split                        | 24 train / 5 val / 6 test, subject-disjoint                   | METHODS_CANONICAL M3         | ✅  |
| **Stress-test matched pair** | **0.554 → 0.212** (same architecture, single seed)            | task TARGET-DEFINITION block | ✅  |
| Stress-test baselines        | event: Ridge 0.260 / persist 0.104; leakage-free: Ridge 0.216 | task brief                   | ✅  |
| Unique targets / repetition  | 104 → 2,678; 96.2% adjacent-same                              | task brief; existing draft   | ✅  |

## Forbidden-pairing sweep (critical — this venue's draft had the defect)

- [x] **0.606 does NOT appear in the SCCUR abstract.** The existing draft paired the five-seed 0.606 with the stress-test "dropped to 0.212" — that is forbidden pairing #4 (Gen-A result vs Gen-B stress test). **Fixed:** the submission-ready abstract uses only the matched single-seed pair **0.554 → 0.212**, both from the same architecture.
- [x] No 27,139-param-count-with-0.606 pairing (param count not stated in the character-limited abstract).
- [x] No 72.1% / 82.6% / 91% oracle / "35/35 benefit" (controller replay not included in this short abstract).
- [x] Persistence AND Ridge reported next to both TCN numbers (0.554 and 0.212).

## Clinical-claim sweep

- [x] No efficacy / patient benefit / disease-slowing / deployment claim.
- [x] Framed as a forecasting-methods audit; PAC treated as a scalar EEG timing target.
- [x] Event-level PAC label granularity is the explicit subject of the abstract (the whole point).
- [x] "What must be validated before EEG forecasts drive adaptive stimulation" — future-facing, not a deployment claim.

## Citation check

- [x] **No citations, per SCCUR rules** (abstract ≤1,500 chars, no references). Nothing to verify in-text; no "Fortunato" or non-responder statistic used.
- [x] Dataset named as "OpenNeuro ds005048" without a formatted reference (allowed — it is a dataset identifier, not a citation).

## AI-tells sweep

- [x] No delve / underscore / showcase / intricate / pivotal / robust / leverage / harness / realm.
- [x] No "It is important to note," "In today's world," "plays a pivotal role."
- [x] No Moreover/Furthermore/Additionally chains.
- [x] Sentence length varied; a short blunt closer ("... and no longer beating it." / "target definition decided the model-selection conclusion").
- [x] First-person; the story is the author's own pivot (distrusting the strong number, rebuilding the target).
- [x] Conclusion advances a claim (target definition decided the conclusion), not a summary.

## Format / venue fit (hard limits — measured)

- [x] **Title 79 / 200 characters.** ✅
- [x] **Abstract 1,491 / 1,500 characters** (measured programmatically on the vetted string). ✅ — **re-measure if the author edits a single word; there are only 9 characters of headroom.**
- [x] No citations/references in the abstract. ✅
- [x] Poster format recommended over oral (see presentation notes).
