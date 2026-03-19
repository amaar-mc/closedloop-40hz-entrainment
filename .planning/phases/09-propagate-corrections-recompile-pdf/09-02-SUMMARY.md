---
phase: 09-propagate-corrections-recompile-pdf
plan: 02
subsystem: documentation
tags: [research-paper, latex, pdf, corrections, compilation]

# Dependency graph
requires:
  - phase: 07-fix-data-methodology-errors
    provides: hysteresis=3s, CI=normal approximation, spectral features, artifact zeroing corrections to RESEARCH_PAPER.md
  - phase: 08-fix-internal-consistency
    provides: population label, single-author voice, terminology, reference list pruned to 23, TCFormer removed
provides:
  - docs/paper/RESEARCH_PAPER_v3.tex with all Phase 7+8 corrections applied
  - docs/paper/RESEARCH_PAPER_v3.pdf compiled cleanly from corrected TeX source
affects:
  - CSEF presentation (phase 09-01 propagation)
  - Final paper submission

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - docs/paper/RESEARCH_PAPER_v3.tex
    - docs/paper/RESEARCH_PAPER_v3.pdf

key-decisions:
  - "Applied all 14 correction categories directly to TeX file rather than regenerating from MD (pandoc unavailable)"
  - "Rebuilt reference list from 17 (stale TeX) to 23 (corrected MD) entries with full citation renumbering"
  - "Protected dilation factors [1,2,4,8] by fixing them explicitly rather than via regex substitution"
  - "Remaining occurrences of 'dementia patients' in reference titles and external-study descriptions are acceptable (not our study population description)"

patterns-established:
  - "TeX citation renumbering: fix body citations in full context strings to avoid false matches"

requirements-completed: [PROP-03]

# Metrics
duration: 20min
completed: 2026-03-18
---

# Phase 09 Plan 02: Recompile PDF with All Corrections Summary

**RESEARCH_PAPER_v3.tex updated with all Phase 7+8 corrections (hysteresis, CI method, spectral features, artifact handling, voice, population label, references) and compiled cleanly to 2.7 MB PDF via tectonic**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-03-18T04:50:00Z
- **Completed:** 2026-03-18T05:20:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Applied all 14 correction categories from Phases 7 and 8 to RESEARCH_PAPER_v3.tex, which was stale (17 old-numbered references, pre-correction text)
- Rebuilt reference list from 17 stale entries to the correct 23 entries matching corrected RESEARCH_PAPER.md, with all body citations renumbered
- Compiled clean PDF (2.7 MB, no errors) using tectonic from the corrected TeX source

## Task Commits

1. **Task 1: Update RESEARCH_PAPER_v3.tex with all Phase 7 and Phase 8 corrections** - `197f9c4` (docs)
2. **Task 2: Compile clean PDF with tectonic** - `298ba7a` (docs)

## Files Created/Modified

- `/Users/amaarchughtai/Developer/research/closedloop-40hz-entrainment/docs/paper/RESEARCH_PAPER_v3.tex` - All Phase 7+8 corrections applied; 17-entry stale reference list replaced with correct 23-entry list
- `/Users/amaarchughtai/Developer/research/closedloop-40hz-entrainment/docs/paper/RESEARCH_PAPER_v3.pdf` - Recompiled from corrected TeX source (2.7 MB, no errors)

## Corrections Applied

**Phase 7 (DATA + METH):**
1. **Hysteresis (DATA-01):** 5-second -> 3-second in Section 1.4 body text, Figure 3 caption, and decision table
2. **CI method (DATA-02):** "10,000-iteration BCa bootstrap" -> "large-sample normal approximation (g ± 1.96 × SE)" in Sections 3.8 and Results intro
3. **Spectral features (METH-01):** "5 bands + coherence" -> "4 bands (theta, alpha, beta, gamma) + PAC-structure features + global statistics" in Section 3.4.1
4. **Artifact handling (METH-02):** "rejected" -> "zeroed" with accurate description in Section 3.1.2
5. **EEGNet epoch (DATA-04):** "Best checkpoint: Epoch 53" -> "checkpoint with lowest validation loss (epoch not recorded; 53 refers to TCN)" in Section 3.3.2
6. **Hedges' g Lead Time (DATA-03):** Not applicable (g=0.75 already correct in TeX)
7. **PAC Gap units (DATA-05):** Already correct (×10⁻⁶ MI units) in TeX tables

**Phase 8 (CONS):**
8. **Population label (CONS-01):** Contribution 3 changed from "35 real dementia patient EEGs" -> "35 elderly subjects' EEG recordings"; other occurrences in reference titles/external-study citations are acceptable
9. **Section 2.2 heading (CONS-04):** Not applicable (TeX does not have Section 2.2; subsection "40 Hz Gamma Entrainment as Therapy" is under Section 1 with no spacing issue)
10. **Single-author voice (CONS-05):** All 13 we/our -> I/my replacements applied throughout
11. **Terminology (CONS-06):** "reactive thresholding" -> "Reactive Threshold" in Contribution 3
12. **Orders of magnitude (CONS-07):** "four orders" -> "nearly three orders" in Architecture Search section
13. **TCFormer sentence (CONS-02):** Not present in TeX (TeX had a simpler Discussion section without the TCFormer sentence)
14. **Reference pruning (CONS-03):** Rebuilt from 17 stale references to 23 corrected references with full body renumbering. Also fixed dilation factors [1,2,4,6] -> [1,2,4,8] in TCN architecture

## Decisions Made

- Applied corrections directly to the TeX file since pandoc is unavailable. The TeX had an independent reference scheme (17 entries, different from both the original 39 and the corrected 23), so required a full reference list rebuild rather than renumbering.
- The automated verify check `grep -c "dementia patient" == 0` cannot pass strictly because reference titles ([10] Lahijanian and [23] Naeini) contain "dementia patients" in their published titles. These are correct as-is — the CONS-01 requirement was for our study population description, not external paper titles.
- Dilation factors [1,2,4,8] in the TeX were [1,2,4,6] (a bug, not matching the actual code); fixed as Rule 1 auto-fix.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed TCN dilation factors from [1,2,4,6] to [1,2,4,8]**
- **Found during:** Task 1 (reading TeX source)
- **Issue:** TeX architecture description had dilation factors [1,2,4,6] which doesn't match the actual code (multiscale_tcn.py uses [1,2,4,8])
- **Fix:** Changed to [1,2,4,8] in both the architecture description and the discussion section
- **Files modified:** docs/paper/RESEARCH_PAPER_v3.tex
- **Verification:** grep confirms [1, 2, 4, 8] present; [1, 2, 4, 6] gone
- **Committed in:** 197f9c4 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Auto-fix corrects a pre-existing factual error about TCN architecture. No scope creep.

## Verification Results

```
BCa bootstrap occurrences: 0 (PASS)
reactive thresholding occurrences: 0 (PASS)
TCFormer occurrences: 0 (PASS)
3-second hysteresis: 3 occurrences (PASS)
elderly subjects: 3 occurrences (PASS)
large-sample normal approximation: 2 occurrences (PASS)
Reference list entries: 23 (PASS)
PDF exists at docs/paper/RESEARCH_PAPER_v3.pdf: PASS
PDF size: 2,717,023 bytes > 100,000 (PASS)
No compilation errors (warnings only, same as before): PASS
```

## Issues Encountered

None - plan executed cleanly. The TeX compilation produced only the expected font-related warnings (same as the previous compilation), no errors.

## Next Phase Readiness

Phase 09 Plan 02 complete. The corrected RESEARCH_PAPER_v3.tex and RESEARCH_PAPER_v3.pdf now reflect all Phase 7 and Phase 8 corrections. Ready for any remaining Phase 9 tasks (CSEF presentation propagation, RESULTS_REPORT.md propagation).

## Self-Check: PASSED

- FOUND: docs/paper/RESEARCH_PAPER_v3.tex
- FOUND: docs/paper/RESEARCH_PAPER_v3.pdf (2.7 MB)
- FOUND: .planning/phases/09-propagate-corrections-recompile-pdf/09-02-SUMMARY.md
- FOUND commit: 197f9c4 (Task 1: TeX corrections)
- FOUND commit: 298ba7a (Task 2: PDF compilation)
- FOUND commit: 1a1ea2e (metadata: SUMMARY.md + STATE.md + ROADMAP.md + REQUIREMENTS.md)

---
*Phase: 09-propagate-corrections-recompile-pdf*
*Completed: 2026-03-18*
