---
phase: 08-fix-internal-consistency
plan: 01
subsystem: documentation
tags: [research-paper, text-consistency, single-author-voice]

# Dependency graph
requires:
  - phase: 07-fix-data-accuracy
    provides: corrected RESEARCH_PAPER.md with accurate data and methodology
provides:
  - "Consistent population label (35 elderly subjects) throughout RESEARCH_PAPER.md"
  - "Section 2.2 heading correctly spaced"
  - "Single-author first-person voice (I/my) throughout paper body"
  - "Standardized Reactive Threshold terminology"
  - "Consistent nearly three orders of magnitude phrasing"
affects:
  - "09-propagate-recompile"

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - "docs/paper/RESEARCH_PAPER.md"

key-decisions:
  - "Replaced 'reactive thresholding' with 'Reactive Threshold' (capitalized) at Contribution 3 to match controller variant naming in Section 3.6.3"
  - "All 13 self-referential we/our replaced with I/my; verified zero remaining occurrences"
  - "Section 2.2 heading space fix: 2.240 Hz -> 2.2 40 Hz (was rendering as 2.240 Hz without the space)"

patterns-established:
  - "Population label: Always '35 elderly subjects' (never 'dementia patients' or 'elderly dementia patients')"
  - "Voice: Single-author first-person singular (I/my) throughout body"
  - "Orders of magnitude phrasing: 'nearly three orders of magnitude' (1,457 to 1.1M params = ~2.88 orders)"

requirements-completed: [CONS-01, CONS-04, CONS-05, CONS-06, CONS-07]

# Metrics
duration: 12min
completed: 2026-03-17
---

# Phase 08 Plan 01: Fix Internal Consistency Summary

**Five targeted text consistency fixes in RESEARCH_PAPER.md: population label, section heading, single-author voice (13 replacements), terminology standardization, and orders-of-magnitude phrasing**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-03-17T~09:45:00Z
- **Completed:** 2026-03-17T~09:57:00Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- CONS-01: Both incorrect population labels corrected to "35 elderly subjects" (Contribution 3 L79 and Conclusion L732)
- CONS-04: Section 2.2 heading restored from "2.240 Hz" to "2.2 40 Hz" — renders correctly in all markdown processors
- CONS-05: All 13 self-referential "we/our" replaced with "I/my" throughout paper body; Abstract (already correct) left unchanged
- CONS-06: "reactive thresholding" standardized to "Reactive Threshold" at Contribution 3 to match controller variant name in Section 3.6.3
- CONS-07: "four orders of magnitude" corrected to "nearly three orders of magnitude" at Section 4.3 — now consistent with L74 which was already correct (1,457 to 1.1M = log10 ~2.88)

## Task Commits

1. **Task 1: Fix population label, section heading, terminology, and magnitude phrase** - `c054539` (fix)
2. **Task 2: Replace all we/our with I/my throughout body (CONS-05)** - `cd06141` (fix)

## Files Created/Modified

- `docs/paper/RESEARCH_PAPER.md` — Five text consistency corrections spanning 18 individual line edits

## Decisions Made

- "Reactive Threshold" capitalized (not "Reactive threshold") because it refers to a named controller variant in Table/Section 3.6.3
- Abstract already used "I" correctly; confirmed unchanged after Task 2 replacements
- No changes made to quoted text from other authors or third-party dataset descriptions

## Deviations from Plan

None - plan executed exactly as written.

## Verification Output

All five grep checks return 0:

```
grep -n "dementia patient EEGs"          → 0
grep -n "35 elderly dementia"            → 0
grep -n "2\.240 Hz"                      → 0
grep -n "reactive thresholding"          → 0
grep -n "four orders of magnitude"       → 0
grep -n "\bwe\b|\bour\b|\bWe\b|\bOur\b" → 0
```

## Issues Encountered

None.

## Next Phase Readiness

- RESEARCH_PAPER.md now has consistent population labels, voice, terminology, and magnitude phrasing
- Ready for Plan 02: Reference renumbering pass (removing orphan references, correcting [25] misattribution)

---
*Phase: 08-fix-internal-consistency*
*Completed: 2026-03-17*
