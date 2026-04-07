---
phase: 17-poster-board-deep-audit-data-accuracy-figures-visual-cohesion-and-judge-readiness
plan: 01
subsystem: documentation
tags: [csef, audit, poster, data-accuracy, figures]

requires:
  - phase: 16-csef-documentation-and-presentation-package
    provides: poster artifacts (CSEF_poster_v2.pdf, CSEF_poster.pptx) and poster spec (POSTER_BOARD_V8.md)

provides:
  - 17-01-DATA-ACCURACY-AUDIT.md: 37-claim PASS/FLAG/FAIL audit against JSON ground truth
  - 17-01-FIGURE-AUDIT.md: 13-figure assessment across 6 dimensions
  - Corrective actions ranked P0/P1/P2 for pre-judging triage (2 days to CSEF)

affects:
  - Any phase that modifies the poster based on audit findings

tech-stack:
  added: []
  patterns:
    - "PASS/FLAG/FAIL classification for claim-level audit reports"
    - "P0/P1/P2 priority triage for corrective actions under time pressure"

key-files:
  created:
    - .planning/phases/17-poster-board-deep-audit-data-accuracy-figures-visual-cohesion-and-judge-readiness/17-01-DATA-ACCURACY-AUDIT.md
    - .planning/phases/17-poster-board-deep-audit-data-accuracy-figures-visual-cohesion-and-judge-readiness/17-01-FIGURE-AUDIT.md
  modified: []

key-decisions:
  - "17-01: Three confirmed discrepancies (F1: TCN params 5154 vs 31043, F2: Conclusion R2=0.25 vs Fig 6 shows 0.577-0.669, F3: Exp Decay g=2.01 vs JSON 2.313) — all three require correction before CSEF judging 2026-04-09"
  - "17-01: F1 is highest judge risk — TCN parameter count inconsistency (pipeline text vs validation results) will be immediately apparent to a technical judge"
  - "17-01: Fatigue Results 3 and 4 use heuristic adaptive controller, not trained TCN — this disclosure gap is not a numerical error but a framing risk"
  - "17-01: 30/37 numerical claims verified PASS against source JSON; poster is substantially accurate"

patterns-established:
  - "Audit reports cite exact source file path and line/key for every finding"
  - "Corrective actions use P0/P1/P2 triage aligned with time remaining before deadline"

requirements-completed:
  - AUDIT-DATA
  - AUDIT-FIGURES

duration: 8min
completed: 2026-04-07
---

# Phase 17 Plan 01: Data Accuracy and Figure Audit Summary

**Claim-by-claim verification of 37 poster numerical claims against source JSON, plus 13-figure visual assessment — finding 4 discrepancies and 5 flagged figures with actionable P0/P1/P2 corrections for CSEF 2026-04-09 judging**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-07T00:05:25Z
- **Completed:** 2026-04-07T00:13:32Z
- **Tasks:** 2
- **Files created:** 2

## Accomplishments

- Data accuracy audit: 37 numerical poster claims cross-referenced against 6 source files (`results/tcn_validation_results.json`, `results/fatigue_sensitivity.json`, `experimental/results/horizon_sweep_pac_stim.json`, `rigor/experiments/fatigue_model_sensitivity_results.json`, etc.) — 30 PASS, 2 MARGINAL, 4 FLAG, 0 FAIL
- Figure audit: All 13 figures visible in the PDF assessed across data accuracy, labels, attribution, color consistency, caption accuracy, and readability — 7 PASS, 5 FLAG, 1 embedded PASS
- Three confirmed pre-known discrepancies (F1, F2, F3) documented with exact corrected values, source citations, judge risk ratings, and actionable corrective steps ranked P0/P1/P2

## Task Commits

1. **Task 1: Data Accuracy Audit** - `7f412e4` (docs)
2. **Task 2: Figure Audit** - `8d39990` (docs)

## Files Created/Modified

- `.planning/phases/17-.../17-01-DATA-ACCURACY-AUDIT.md` — 269-line claim-by-claim audit, 37 claims, 4 flags, corrective actions section
- `.planning/phases/17-.../17-01-FIGURE-AUDIT.md` — 427-line per-figure assessment, 13 figures, 5 flags, source file cross-reference table

## Decisions Made

- F1 (TCN params 5,154 vs 31,043): Highest judge risk — a technical judge can immediately spot the contradiction between the pipeline table (5,154 params, 12 features) and the validation results (which required the 73-feature, 31,043-param checkpoint). P0 fix: update architecture table or add model-identity disclaimer.
- F2 (R²=0.25 stale): Conclusion 1 text was written for the original 73-feature model and not updated when Figure 6 was upgraded to PAC+Stim results. P0 fix: replace "R²=0.25" with "R²=0.58" in Conclusion 1.
- F3 (g=2.01 vs 2.313): Exponential Decay Hedges' g in Result 4 table does not match JSON source. P1 fix (lower visibility than F1/F2).
- Fatigue controller framing gap: Results 3 and 4 use a heuristic adaptive controller, not the trained TCN — not disclosed on poster. Logged as additional finding, not a numerical discrepancy.

## Deviations from Plan

None — plan executed exactly as written. Both audit reports delivered per spec:
- DATA-ACCURACY-AUDIT.md: >100 lines, 30+ claims classified, all three confirmed discrepancies documented
- FIGURE-AUDIT.md: >80 lines, every figure assessed across 6 dimensions

## Issues Encountered

- `rigor/experiments/fatigue_model_sensitivity_results.json` exceeds 10,000-token read limit — used targeted grep and offset-based reads to extract the relevant Hedges' g values (lines 148, 170, 192, 214, 236)
- Poster PDF figure numbering (Figures 12, 13, 16) does not align with POSTER_BOARD_V8.md sequential spec (Figs 1–10) — PDF uses PPTX output numbering. Documented and accounted for in figure audit.

## User Setup Required

None — audit-only phase, no external services or configuration required.

## Next Phase Readiness

The audit reports are complete and actionable. Two options for next steps:

1. **If doing corrections (recommended):** A follow-on phase should address P0 items (F1 TCN param inconsistency + F2 stale R²=0.25 in Conclusion 1) in the PPTX and re-export PDF before 2026-04-09 judging.
2. **If no corrections:** Judges should be prepared to explain: (a) the distinction between the architecture search model (5,154 params) and the validation checkpoint (31,043 params), and (b) that Conclusion 1's R²=0.25 refers to the original 73-feature model while Figure 6 shows the improved PAC+Stim model.

The 30/37 PASS rate confirms the poster is substantially accurate. The three discrepancies are known and correctable.

---
*Phase: 17-poster-board-deep-audit-data-accuracy-figures-visual-cohesion-and-judge-readiness*
*Completed: 2026-04-07*
