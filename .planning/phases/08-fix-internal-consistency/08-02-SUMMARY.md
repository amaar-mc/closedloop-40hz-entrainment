---
phase: 08-fix-internal-consistency
plan: 02
subsystem: documentation
tags: [research-paper, references, citations, consistency]

# Dependency graph
requires:
  - phase: 08-fix-internal-consistency
    provides: 08-01 text consistency fixes (population label, voice, terminology)
provides:
  - RESEARCH_PAPER.md with clean 23-entry reference list and consistent citation numbering
  - Removal of erroneous TCFormer citation
  - All body citations in [1]-[23] range with every reference cited
affects:
  - 09-propagate-recompile (reference numbering must be consistent with any cross-file propagation)

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - docs/paper/RESEARCH_PAPER.md

key-decisions:
  - "Used single-pass regex callback to update body citations — eliminates cascading replacement bugs"
  - "Built new reference list from scratch by parsing entries and filtering orphans — cleaner than in-place deletion"
  - "Dilation factors [1, 2, 4, 8] protected with placeholder before citation replacement"

patterns-established:
  - "Reference renumbering: parse entries into dict, build new list from scratch, update body in single regex pass"

requirements-completed: [CONS-02, CONS-03]

# Metrics
duration: 6min
completed: 2026-03-18
---

# Phase 08 Plan 02: Fix Internal Consistency (References) Summary

**Removed erroneous TCFormer sentence and pruned 16 orphan references, renumbering the surviving 23 entries [1]-[23] throughout docs/paper/RESEARCH_PAPER.md**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-03-18T04:13:00Z
- **Completed:** 2026-03-18T04:18:57Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Removed the TCFormer sentence from Section 2.5.2 that misattributed [25] as TCFormer (CONS-02); EEGNet [25] citation in Section 2.5.1 remains intact
- Deleted 16 orphan reference entries that were never cited in the body text (CONS-03)
- Renumbered surviving 23 references to sequential [1]-[23] and updated all body citations in a single pass
- EEGNet now correctly cited as [18] (was [25]); Tort PAC measure as [22] (was [31])
- Updated footer: "References: 39" → "References: 23"

## Task Commits

1. **Task 1: Remove TCFormer sentence (CONS-02)** - `840a7e2` (fix)
2. **Task 2: Prune orphan references and renumber citations (CONS-03)** - `2b447ff` (fix)

## Files Created/Modified

- `docs/paper/RESEARCH_PAPER.md` - TCFormer sentence removed from Section 2.5.2; reference list pruned from 39 to 23 entries; all body citations renumbered

## Decisions Made

- Used single-pass `re.sub` with a callback function to update body citations, ensuring no cascading replacement bugs (where [3]→[2] could then incorrectly affect previously-converted citations)
- Built the new reference list by parsing all 39 entries into a dictionary, then constructing the 23-entry list from scratch in the correct order — cleaner than in-place deletion
- Protected the dilation factors `[1, 2, 4, 8]` in Section 2.5.2 with a placeholder before citation replacement to prevent false matches

## Deviations from Plan

None — plan executed exactly as written, though two intermediate implementation attempts were discarded due to cascading replacement bugs (identified during verification and corrected before commit).

## Old-to-New Citation Mapping Applied

| Old | New | Author |
|-----|-----|--------|
| [1]  | [1]  | Wang Y (gamma oscillations) |
| [3]  | [2]  | Zhurakovskaya E (theta/gamma dynamics) |
| [4]  | [3]  | Dimitriadis SI (abnormal gamma PAC) |
| [5]  | [4]  | Backus AR (theta-gamma coupling working memory) |
| [6]  | [5]  | Klimesch W (theta-gamma coupling elderly) |
| [7]  | [6]  | Iaccarino HG (gamma entrainment Nature 2016) |
| [8]  | [7]  | Murdock MH (glymphatic clearance Nature 2024) |
| [10] | [8]  | Goutier L (monkey model PNAS 2025) |
| [11] | [9]  | Chan D (gamma sensory open-label) |
| [12] | [10] | Lahijanian B (DMN connectivity Scientific Reports) |
| [13] | [11] | Bhatt DL (neuroimmune signaling Journal Neuroscience) |
| [15] | [12] | Fortunato C (gamma sensory entrainment review) |
| [16] | [13] | Cabral J (personalized digital therapeutics) |
| [17] | [14] | Rathour RK (whole-brain neural mass models) |
| [19] | [15] | Schirrmeister RT (systematic comparison deep learning EEG) |
| [23] | [16] | Barham MP (PRIME framework bioRxiv) |
| [24] | [17] | Patel V (Brian Intensify) |
| [25] | [18] | Lawhern VJ (EEGNet) |
| [26] | [19] | Zamora-Pardo A (DBS deep learning MPC) |
| [27] | [20] | Bergey GK (closed-loop neuromodulation) |
| [28] | [21] | Tafazoli S (precision neuromodulation) |
| [31] | [22] | Tort ABL (measuring PAC, Journal Neurophysiology) |
| [39] | [23] | Naeini AH (non-invasive auditory brain stimulation) |

## Deleted Orphan References (16 entries)

| Old # | Author | Reason |
|-------|--------|--------|
| [2]  | Naeini Z (cross-frequency neuromodulation) | Never cited in body |
| [9]  | Chen X (40 Hz multisensory stimulation SAGE) | Never cited in body |
| [14] | Modi MN (40 Hz sensory stimulation CA3-CA1) | Never cited in body |
| [18] | Cavedo E (treatment non-responders) | Never cited in body |
| [20] | Altaheri H (transformers in EEG analysis) | Never cited in body |
| [21] | Demir A (graph embeddings EEG) | Never cited in body |
| [22] | Li Y (graph-generative neural network) | Never cited in body |
| [29] | Indiveri G (neuromorphic neuromodulation) | Never cited in body |
| [30] | Dupré da Silva N (extended modulation index) | Never cited in body |
| [32] | Miyakoshi M (semi-automatic EEG preprocessing) | Never cited in body |
| [33] | Winkler I (high-pass filtering ICA) | Never cited in body |
| [34] | Sanda P (time-frequency PAC measure) | Never cited in body |
| [35] | Nunez PL (computational models EEG) | Never cited in body |
| [36] | Haufe S (EEGSourceSim) | Never cited in body |
| [37] | Raj A (spectral graph model EEG) | Never cited in body |
| [38] | OpenNeuro Dataset ds005048 description | Never cited in body (cited as [39] Naeini AH) |

## Verification Results

```
grep -c "TCFormer" docs/paper/RESEARCH_PAPER.md  → 0
grep -c "^\[" docs/paper/RESEARCH_PAPER.md        → 23
All body citations [1]-[23]: PASS
Every body citation has a reference entry: PASS
Every reference is cited in body: PASS
Dilation [1, 2, 4, 8] preserved: PASS
Reference list sequential [1]-[23]: PASS
EEGNet [18] in Section 2.5.1: PASS
Tort [22] in Sections 1.4 and 2.1.2: PASS
Footer "References: 23": PASS
```

## Issues Encountered

Two intermediate Python script runs produced incorrect output due to:
1. First run: negative lookahead `(?![\d,])` blocked replacement of `[N],` patterns (citation followed by comma)
2. Second run (on already-partially-transformed file): cascading replacements corrupted citation numbers

Both issues were identified via verification checks and resolved by restoring from the Task 1 commit and using a single-pass `re.sub` callback approach.

## Next Phase Readiness

Phase 08 Plan 02 complete. Both remaining Phase 8 issues resolved:
- CONS-02 (TCFormer misattribution) — fixed
- CONS-03 (orphan references, renumbering) — fixed

Ready for Phase 9: Propagate & Recompile (propagate corrections to CSEF presentation and RESULTS_REPORT.md; recompile paper PDF).

---
*Phase: 08-fix-internal-consistency*
*Completed: 2026-03-18*
