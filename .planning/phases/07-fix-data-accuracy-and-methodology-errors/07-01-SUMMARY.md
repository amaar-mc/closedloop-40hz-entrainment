---
phase: 07-fix-data-accuracy-and-methodology-errors
plan: 01
subsystem: documentation
tags: [research-paper, methodology, statistics, EEG, PAC, accuracy]

# Dependency graph
requires: []
provides:
  - "RESEARCH_PAPER.md corrected: 3-second hysteresis (3 locations), CI method, EEGNet epoch claim, artifact zeroing, spectral feature breakdown"
  - "RESULTS_REPORT.md corrected: Lead Time Hedges' g = 0.75, PAC Gap units = x10-6 MI"
affects: [08-fix-internal-consistency, 09-propagate-recompile]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Paper-to-code accuracy: all claims verified against source files before writing"
    - "Unit consistency: MI values labeled as dimensionless x10-6 MI units, not µV²"

key-files:
  created: []
  modified:
    - docs/paper/RESEARCH_PAPER.md
    - results/RESULTS_REPORT.md

key-decisions:
  - "Artifact handling: code zeroes samples (set to 0.0), does not reject/drop windows — paper updated to 'zeroed'"
  - "Hysteresis: run_tcn_validation.py line 253 confirms hysteresis_hold=3, not 5 — all 3 paper locations corrected"
  - "CI method: large-sample normal approximation (g ± 1.96 × SE) used, not BCa bootstrap — 2 paper locations corrected"
  - "Spectral features: 4 bands (theta/alpha/beta/gamma) x 7ch = 28 + 7 ratios + 21 PAC-struct + 5 globals = 61; no delta, no coherence"
  - "EEGNet epoch 53: confirmed only for TCN checkpoint; EEGNet best epoch was not recorded — claim qualified"
  - "Lead Time Hedges' g: exact value 0.7549 rounds to 0.75, paper had 0.76"
  - "PAC Gap units: MI is dimensionless; correct label is x10-6 MI units, not µV²"

patterns-established:
  - "Verify all quantitative claims against source code before including in paper"
  - "Use dimensionless MI units for PAC gap metrics, not voltage-squared units"

requirements-completed: [DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, METH-01, METH-02]

# Metrics
duration: 12min
completed: 2026-03-17
---

# Phase 07 Plan 01: Fix Data Accuracy and Methodology Errors Summary

**Seven factual corrections to RESEARCH_PAPER.md and RESULTS_REPORT.md aligning all claims with actual code: 3s hysteresis, normal-approx CIs, 4-band spectral features, artifact zeroing, qualified EEGNet epoch, corrected Hedges' g, and dimensionless MI units for PAC Gap.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-03-17T00:00:00Z
- **Completed:** 2026-03-17
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- Corrected 3 occurrences of "5-second hysteresis" to "3-second hysteresis" (matching run_tcn_validation.py hysteresis_hold = 3)
- Replaced "10,000-iteration BCa bootstrap" with "large-sample normal approximation (g ± 1.96 × SE)" in 2 locations
- Corrected Section 3.4.1 spectral feature breakdown from "5 bands + coherence = 61" to accurate "4 bands + PAC-structure + globals = 61"
- Changed Section 3.1.2 artifact handling language from "rejected" to "zeroed" to match src/preprocessing.py behavior
- Qualified unverified EEGNet "Best checkpoint: Epoch 53" — epoch 53 confirmed only for TCN
- Fixed RESULTS_REPORT.md Lead Time Hedges' g from 0.76 to 0.75 (exact value 0.7549)
- Replaced all 6 occurrences of "µV²" for PAC Gap with "×10⁻⁶ MI units" (MI is dimensionless)

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix hysteresis, CI method, artifact handling, EEGNet epoch claim** - `66970c5` (fix)
2. **Task 2: Fix spectral feature description Section 3.4.1** - `e6da0c8` (fix)
3. **Task 3: Fix RESULTS_REPORT.md Hedges' g and PAC Gap units** - `0203c06` (fix)

## Files Created/Modified
- `docs/paper/RESEARCH_PAPER.md` - 10 targeted text replacements correcting DATA-01, DATA-02, DATA-04, METH-01, METH-02
- `results/RESULTS_REPORT.md` - 6 targeted text replacements correcting DATA-03, DATA-05

## Decisions Made
- Artifact zeroing: code sets samples to 0.0 (not rejection), so "Artifact zeroing" and "were zeroed" are the accurate terms
- Spectral features: confirmed against archive/experimental_models/spectral_features.py lines 161-194 — 4 bands only, no delta, no cross-channel coherence
- EEGNet epoch: the TCN training log confirms epoch 53 for the TCN best checkpoint; EEGNet best epoch was not recorded in any artifact — qualified rather than removed
- PAC Gap: the Modulation Index is dimensionless (Tort 2010 formulation), so "µV²" is a unit error — corrected to "×10⁻⁶ MI units"

## Deviations from Plan

None - plan executed exactly as written. All text replacements matched exactly at the specified locations.

## Issues Encountered
- RESEARCH_PAPER.md is 86KB; read in targeted sections using offset/limit and grep to locate exact replacement strings before editing.
- Line 304 contains "Epoch 53" in the TCN performance table (which is correct — the TCN checkpoint IS epoch 53). Only the EEGNet claim at line 242 was the issue; fixed accurately.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All DATA and METH requirements resolved in RESEARCH_PAPER.md and RESULTS_REPORT.md
- Phase 8 (Fix Internal Consistency) can proceed: population label, orphan references, pronoun voice, section headings
- Phase 9 (Propagate & Recompile) will need these corrections as a base before propagating to CSEF presentation and recompiling PDF

---
*Phase: 07-fix-data-accuracy-and-methodology-errors*
*Completed: 2026-03-17*
