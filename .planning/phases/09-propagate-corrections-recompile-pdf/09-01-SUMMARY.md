---
phase: 09-propagate-corrections-recompile-pdf
plan: 01
subsystem: documentation
tags: [corrections, consistency, CSEF, presentation, poster, methodology]

requires:
  - phase: 07-fix-data-accuracy-and-methodology-errors
    provides: Corrected RESEARCH_PAPER.md with hysteresis=3s, CI=normal approximation, spectral features=4 bands, artifact zeroing, Hedges g=0.75, PAC Gap=×10⁻⁶ MI
  - phase: 08-fix-internal-consistency
    provides: Corrected population label (35 elderly subjects), single-author voice, reference list pruned

provides:
  - All active CSEF presentation files updated with consistent, corrected factual values
  - RESULTS_REPORT.md verified clean (PROP-02 complete)
  - Zero contradictions between RESEARCH_PAPER.md and any active presentation file

affects: [10-future-phases, PDF-recompile]

tech-stack:
  added: []
  patterns:
    - "Population label: 35 elderly subjects (never dementia patients in our own text)"
    - "Hysteresis: 3-second (from run_tcn_validation.py, not src/controller.py default)"
    - "CI method: large-sample normal approximation (g ± 1.96 × SE)"
    - "PAC Gap units: ×10⁻⁶ MI (Modulation Index is dimensionless)"
    - "Spectral features: 4 bands (theta/alpha/beta/gamma) × 7ch = 28 + 7 ratios + 21 PAC-structure + 5 globals = 61"
    - "TCN params: 31,043 (not 135,000); receptive field: 31-step (not 44-second)"

key-files:
  created: []
  modified:
    - docs/poster/POSTER_BOARD_V5.md
    - docs/presentations/01_main_script.md
    - docs/presentations/02_short_version.md
    - docs/presentations/04_qa_bank_and_danger_zones.md
    - docs/presentations/05_qa_complete.md
    - docs/reference/PRESENTATION.md
    - docs/methodology/CURRENT_METHODOLOGY.md
    - docs/submission/reports/JUDGE_INTERVIEW_PREP.md
    - docs/reference/PROJECT_DEEP_DIVE.md
    - docs/submission/reports/PROJECT_ACHIEVEMENT_REPORT.md
    - docs/submission/audit/COMPREHENSIVE_CODE_AUDIT.md
    - docs/abstract/ABSTRACT.md
    - docs/INDEX.md

key-decisions:
  - "Left citation text unchanged (Lahijanian 2024 paper title, dataset description) per plan exception rule — only our own study population language was updated"
  - "5-second hysteresis in src/controller.py left unchanged (implementation); all presentation docs updated to say 3-second (matching run_tcn_validation.py which produced the reported results)"
  - "Paper sections (docs/paper/sections/) and RESEARCH_PAPER_v3.md out of scope for Phase 9 — not in files_modified list"
  - "Binary PDF files in docs/poster/reference/ excluded from µV² check (not editable)"

requirements-completed: [PROP-01, PROP-02]

duration: 11min
completed: 2026-03-18
---

# Phase 9 Plan 01: Propagate Corrections Summary

**Six category of errors (CONS-01, DATA-01, DATA-02, DATA-03, DATA-05, METH-01/02) propagated to all 13 active CSEF presentation and reference files; RESULTS_REPORT.md verified clean**

## Performance

- **Duration:** 11 min
- **Started:** 2026-03-18T04:50:17Z
- **Completed:** 2026-03-18T05:01:29Z
- **Tasks:** 2
- **Files modified:** 13

## Accomplishments

- Applied population label correction ("35 elderly subjects" replaces "dementia patients" in all active CSEF docs — 10/35 subjects are healthy controls)
- Applied hysteresis correction ("3-second" from run_tcn_validation.py replaces "5-second" in all active CSEF docs)
- Applied CI method correction (large-sample normal approximation replaces bootstrap in all active CSEF docs)
- Applied PAC Gap unit correction (×10⁻⁶ MI replaces µV²/uV^2 in all active CSEF docs)
- Applied spectral feature correction (4 bands + PAC-structure replaces 5 bands + coherence in all active CSEF docs)
- Applied TCN parameter/receptive field correction (31,043 params, 31-step RF replaces ~135,000 params, 44-second in PRESENTATION.md)
- Applied artifact handling correction ("artifact zeroing" replaces "artifact rejection" in CURRENT_METHODOLOGY.md)
- Applied Lead Time Hedges' g correction (+0.75 replaces +0.76 in PROJECT_DEEP_DIVE.md)
- PROP-02 verified: RESULTS_REPORT.md contains zero stale values (all corrected in Phase 7)

## Task Commits

1. **Task 1: Poster board and presentation scripts** - `d307662` (docs)
2. **Task 2: Reference, methodology, and submission docs** - `a33a452` (docs)

## Files Created/Modified

- `docs/poster/POSTER_BOARD_V5.md` - Population label, hysteresis, CI method corrected
- `docs/presentations/01_main_script.md` - Population label corrected
- `docs/presentations/02_short_version.md` - Population label corrected
- `docs/presentations/04_qa_bank_and_danger_zones.md` - Population label (3 instances), spectral features corrected
- `docs/presentations/05_qa_complete.md` - Population label, spectral features (73-feature breakdown) corrected
- `docs/reference/PRESENTATION.md` - Population label, PAC Gap units, TCN params/RF, "We"→first-person corrected
- `docs/methodology/CURRENT_METHODOLOGY.md` - Population label, artifact handling, spectral features, hysteresis, CI method, PAC Gap units corrected
- `docs/submission/reports/JUDGE_INTERVIEW_PREP.md` - Population label, PAC Gap units, CI method, spectral features table, hysteresis, receptive field corrected
- `docs/reference/PROJECT_DEEP_DIVE.md` - PAC Gap units, Lead Time g value (+0.76→+0.75), CI method, hysteresis, population label corrected
- `docs/submission/reports/PROJECT_ACHIEVEMENT_REPORT.md` - Population label (2 instances), PAC Gap units corrected
- `docs/submission/audit/COMPREHENSIVE_CODE_AUDIT.md` - CI method (2 instances), PAC Gap units corrected
- `docs/abstract/ABSTRACT.md` - Population label corrected
- `docs/INDEX.md` - Population label corrected

## Decisions Made

- Left citation text unchanged (Lahijanian 2024 paper title and dataset description phrases containing "dementia patients") per plan exception rule
- Treated "5-second horizons" (prediction horizon terminology) as NOT a stale value — only "5-second hysteresis/minimum hold time" is stale
- Project paper sections (docs/paper/sections/) and RESEARCH_PAPER_v3.md have remaining stale values (5-second hysteresis in some locations) but are out of scope for Phase 9 (not in files_modified list)
- Binary PDF example files in docs/poster/reference/ correctly excluded from changes

## Deviations from Plan

None — plan executed exactly as written. All corrections were applied as specified with the noted scope boundaries.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All active CSEF presentation files are consistent with RESEARCH_PAPER.md
- RESULTS_REPORT.md verified clean (PROP-02)
- Ready for PDF recompile (Phase 9 Plan 02 if applicable)
- Note: docs/paper/sections/ and RESEARCH_PAPER_v3.md still have 5-second hysteresis in some locations — would need a targeted fix if those files are used for any submission

---
*Phase: 09-propagate-corrections-recompile-pdf*
*Completed: 2026-03-18*
