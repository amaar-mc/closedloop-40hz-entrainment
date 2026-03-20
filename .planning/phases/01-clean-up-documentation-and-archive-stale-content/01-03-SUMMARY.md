---
phase: 01-clean-up-documentation-and-archive-stale-content
plan: 03
subsystem: documentation
tags: [docs, index, agents, claude-md, cleanup, consolidation]

# Dependency graph
requires:
  - phase: 01-clean-up-documentation-and-archive-stale-content
    plan: 01-01
    provides: "docs/reference/ established, reports/ moved to archive/reports/, stale dirs removed"
  - phase: 01-clean-up-documentation-and-archive-stale-content
    plan: 01-02
    provides: ".docx files removed, pre-multiscale reports archived to docs/archive/reports/"
provides:
  - "docs/INDEX.md accurately reflects post-cleanup directory structure with zero broken links"
  - "AGENTS.md eliminated; CLAUDE.md is single authoritative coding agent instruction file"
  - "All AGENTS.md sections (Code Style, Imports, Typing, Naming, Error Handling, ML Guardrails, Data Hygiene, When Adding New Code, Lint Checks, Validation Matrix) preserved in CLAUDE.md"
affects: [all-future-phases, coding-agents, documentation-navigation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single authoritative CLAUDE.md as agent instruction file (AGENTS.md pattern eliminated)"
    - "docs/INDEX.md as verified navigation hub — all links script-verified to exist on disk"

key-files:
  created:
    - ".planning/phases/01-clean-up-documentation-and-archive-stale-content/01-03-SUMMARY.md"
  modified:
    - "docs/INDEX.md"
    - "CLAUDE.md"
  deleted:
    - "AGENTS.md"

key-decisions:
  - "AGENTS.md eliminated in favor of single CLAUDE.md; all 10+ sections merged without information loss"
  - "Archived reports moved to docs/archive/reports/ in INDEX.md; Technical Reports section renamed Archived Reports"
  - "Reference files (COMPREHENSIVE_PROJECT_MAP.md, ML_ZERO_TO_HERO.md) linked from reference/ not docs/ root"
  - "Self-test patterns (python src/eegnet.py etc.) merged into CLAUDE.md Testing section from AGENTS.md"

patterns-established:
  - "Link verification pattern: python3 re/os check after any INDEX.md update"
  - "Merge-then-delete pattern for redundant instruction files (AGENTS.md -> CLAUDE.md)"

requirements-completed: [CLEAN-05, CLEAN-06]

# Metrics
duration: 5min
completed: 2026-03-19
---

# Phase 01 Plan 03: Update INDEX.md and Consolidate AGENTS.md into CLAUDE.md Summary

**docs/INDEX.md rewritten to reflect post-cleanup structure with zero broken links; AGENTS.md eliminated by merging all 10 sections (Code Style, Imports, Typing, Naming, Error Handling, ML Guardrails, Data Hygiene, New Code, Lint Checks, Validation Matrix) into CLAUDE.md (158 → 269 lines)**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-03-20T00:23:29Z
- **Completed:** 2026-03-20T00:28:30Z
- **Tasks:** 2
- **Files modified:** 2 (docs/INDEX.md, CLAUDE.md), 1 deleted (AGENTS.md)

## Accomplishments

- Rewrote docs/INDEX.md for post-cleanup structure: removed broken reports/ Quick Nav link, added COMPREHENSIVE_PROJECT_MAP.md at reference/ location, updated directory structure diagram, moved Technical Reports to Archived Reports section pointing at archive/reports/, removed .docx references, added paper/ and presentations/ to structure diagram
- All relative links in docs/INDEX.md verified by automated Python script — zero broken links
- Merged all 10+ AGENTS.md sections into CLAUDE.md with no information lost; CLAUDE.md grew from 158 to 269 lines
- Removed AGENTS.md via git rm — single authoritative instruction file now exists

## Task Commits

Each task was committed atomically:

1. **Task 1: Update docs/INDEX.md for post-cleanup structure** - `885ace1` (docs)
2. **Task 2: Merge ALL AGENTS.md sections into CLAUDE.md and remove AGENTS.md** - `1d6833f` (chore)

## Files Created/Modified

- `docs/INDEX.md` - Updated to reflect post-cleanup directory structure; all links verified
- `CLAUDE.md` - Expanded from 158 to 269 lines with 10 new sections merged from AGENTS.md
- `AGENTS.md` - Deleted (git rm); content fully preserved in CLAUDE.md

## Decisions Made

- AGENTS.md eliminated entirely: CLAUDE.md is the single source of truth for coding agents going forward. Both files existed as parallel instruction files with overlapping but divergent content — consolidation removes confusion about which is authoritative.
- Archived reports section in INDEX.md points to archive/reports/ (not the old reports/ location that no longer exists) — consistent with decision from plan 01-02 to move reports to archive/.
- COMPREHENSIVE_PROJECT_MAP.md and ML_ZERO_TO_HERO.md linked from reference/ in INDEX.md — consistent with decision from plan 01-01 to establish docs/reference/ as canonical location for educational/reference documents.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. The directory structure audit before writing confirmed all target link paths (archive/reports/, reference/COMPREHENSIVE_PROJECT_MAP.md, etc.) existed on disk before INDEX.md was written.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 01 Wave 2 complete. All three plans in phase 01 are now done.
- Documentation structure is clean, accurate, and fully cross-referenced.
- CLAUDE.md is the definitive coding agent instruction file — no ambiguity about which file takes precedence.

---
*Phase: 01-clean-up-documentation-and-archive-stale-content*
*Completed: 2026-03-19*
