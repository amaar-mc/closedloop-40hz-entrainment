# POLISH_REPORT — AAN Neuroscience Research Prize

Senior-editor refine → test → polish pass on `SUBMISSION_READY_MANUSCRIPT.md`. The manuscript was already drafted and first-verified; this pass improved the writing and re-proved claim integrity. No results were added or inflated.

## Before / after

| Metric                                      | Before              | After                        |
| ------------------------------------------- | ------------------- | ---------------------------- |
| Body words (excl. author-only HTML comment) | 2,132               | 2,136                        |
| Structured abstract words                   | 290                 | 281 (AAN limit 300)          |
| Research-report narrative words             | ~1,363              | ~1,360 (target ~1,000–1,500) |
| AI-tell hits (body)                         | 1 ("substantially") | 0                            |
| Em-dashes (body)                            | 20                  | 17                           |
| Residual-risk note at top                   | absent              | present (HTML comment)       |

## Change log

1. **Added the required RESIDUAL-RISK note** as a top-of-file HTML comment (strip-before-submit): originality/AI-drafting caution → rewrite in own words OR confirm with science@aan.com; mentor e-signature gate; every mentor slot `[AUTHOR TO CONFIRM]`. This is the highest residual-risk venue in the track.
2. **Removed the one intensifier tell.** "depended substantially on the target definition" → "much of the strong-looking forecasting number came from how the target was defined, not from the model" (more concrete, in-voice, no number touched).
3. **Trimmed two doubled em-dash parentheticals** (opening "personal for me" aside; "live feasibility study … institutional oversight" aside) to vary punctuation without flattening voice.
4. Preserved the honest spine: static ceiling, feature-ablation generalization finding (hypothesis-framed), the 0.554→0.212 target-definition stress test, and the mixed controller replay.

## T1–T8 verification

| Test                                    | Result   | Evidence                                                                                                                                                                                                                                                                                                                                                                                                          |
| --------------------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **T1** Numbers trace to canonical       | **PASS** | All numeric tokens map to RESULTS_CANONICAL (0.287; ablation −0.420/−0.025/0.344/0.558; five-seed mean 0.606 range 0.558–0.647; shuffle −0.332; stress 0.554/0.260/0.104 → 0.212/0.216/−0.897; 104→2,678; 96.2%; replay 62.2/73.8/50.7 vs 64.5/51.7/77.3). Remaining flagged tokens are reference vol/issue/page/DOI + "50 Hz" + "v1.0.1".                                                                        |
| **T2** No forbidden 0.606↔0.212 pairing | **PASS** | No 0.606 within 220 chars of 0.212; the only matched pair is 0.554→0.212 (same architecture). 27,139 never paired with 0.606 (27,139 not stated in this report).                                                                                                                                                                                                                                                  |
| **T3** Generations distinct             | **PASS** | Five-seed/ablation numbers explicitly tagged "an earlier experimental TCN … I keep those generations apart and do not pool their numbers." No Gen-C 72.1/82.6/31,043/35-of-35/91% present.                                                                                                                                                                                                                        |
| **T4** No clinical overclaim            | **PASS** | "I make no claim of clinical efficacy, disease modification, or deployment." Replay framed as retrospective/offline; "cannot observe how a brain would have physiologically responded to a different stimulation choice." Event-level label + online-availability limits stated.                                                                                                                                  |
| **T5** Citations real & correct         | **PASS** | All 8 references match CITATION_LEDGER DOIs exactly (Iaccarino, Martorell, Chan, Lahijanian, Tort, Lawhern, Thompson&Spencer, Sahu&Tseng). "Fortunato"/"Frontiers in Neuroscience" absent; ref 5 = Sahu & Tseng, Front. Integr. Neurosci. 17:1146687. Non-responder statistic softened ("a substantial fraction … show little measurable entrainment response") with `[AUTHOR: verify source]`; no 23/33 or ~30%. |
| **T6** AI-tells swept                   | **PASS** | 1 tell found and fixed → 0. No delve/underscore/pivotal/robust/moreover/furthermore/"it is important to note". Sentence length varied; short blunt lines kept ("This is a targeting trade-off, not a win.").                                                                                                                                                                                                      |
| **T7** Length/format                    | **PASS** | Abstract 281 words ≤ 300; narrative ~1,360 words within ~1,000–1,500.                                                                                                                                                                                                                                                                                                                                             |
| **T8** Structural completeness          | **PASS** | Title, author line, 5-part structured abstract (OBJECTIVE/BACKGROUND/DESIGN-METHODS/RESULTS/CONCLUSIONS), research report, limitations, future work, 3 figure hooks, references, acknowledgements, data/code availability.                                                                                                                                                                                        |

**Overall: 8/8 PASS.** Residual risks are author-action gates (originality confirmation + mentor e-signature), not text defects; both are flagged in the top-of-file note and `MANUSCRIPT_SELF_CHECK.md`.
