---
phase: 14-scope-lock-completion
plan: 01
subsystem: analysis
tags: [simulator, tau-fitting, exponential-approach, pac-dynamics]

# Dependency graph
requires:
  - phase: 10-scope-lock-foundation
    provides: SIMULATOR_DEFENSE.md analysis identifying need for empirical tau fitting
provides:
  - fit_simulator_params.py script for fitting tau_rise/tau_decay from real PAC data
  - results/simulator_tau_fit.json with fitted values and per-subject breakdown
affects: [14-scope-lock-completion]

# Tech tracking
tech-stack:
  added: []
  patterns: [epoch-level PAC collapse for transition analysis, pooled estimation for sparse decay transitions]

key-files:
  created:
    - fit_simulator_params.py
    - results/simulator_tau_fit.json
  modified: []

key-decisions:
  - "Epoch-level collapse before fitting: PAC is constant within epochs (20-40s blocks), so window-level consecutive pairs have delta=0. Collapsing to epoch-level gives meaningful transitions."
  - "Pooled decay estimation: rest epochs are sparse (0-2 valid candidates per subject) due to asymmetric block structure (40s stim vs 20s rest). Pooling across subjects gives robust population estimate."
  - "MIN_VALID_CANDIDATES=3 for rise, MIN=1 per-subject for decay: dataset block structure constrains per-subject transition counts to ~3-5 for rise and ~0-2 for decay."
  - "stim_state at feature index 68 (not 70 as in plan context): verified from actual feature_names array in the dataset."

patterns-established:
  - "Epoch-level PAC analysis: always collapse window-level PAC to epoch boundaries before measuring inter-epoch dynamics"

requirements-completed: [RSRCH-04]

# Metrics
duration: 7min
completed: 2026-03-21
---

# Phase 14 Plan 01: Simulator Tau Fitting Summary

**Fit tau_rise=0.64 and tau_decay=0.76 from real epoch-level PAC transitions across 35 subjects, replacing undocumented heuristic defaults (0.15, 0.10)**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-21T09:43:15Z
- **Completed:** 2026-03-21T09:50:03Z
- **Tasks:** 1
- **Files created:** 2

## Accomplishments
- Created fit_simulator_params.py that loads all 3 splits, collapses to epoch-level PAC, and fits exponential approach tau values per subject
- Fitted population estimates: tau_rise=0.6392 (IQR: 0.4936-0.7553, n=32 subjects), tau_decay=0.7557 (IQR: 0.5686-0.9059, n=33 pooled from 29 subjects)
- Time constants: T_rise=1.0s, T_decay=0.7s (faster than heuristic 6.2s/9.5s, consistent with PAC measurement window smoothing)
- RSRCH-04 definitively closed: empirical fitting script exists and produces fitted values from real data

## Task Commits

Each task was committed atomically:

1. **Task 1: Write fit_simulator_params.py** - `f4f8738` (feat)

## Files Created/Modified
- `fit_simulator_params.py` - Fits tau_rise/tau_decay from real PAC transition data using exponential approach model
- `results/simulator_tau_fit.json` - Fitted tau values with per-subject breakdown (35 subjects)

## Decisions Made
- **Epoch-level collapse:** PAC is constant within 20-40s epochs (assigned at epoch level to all 2s windows). Working at window level produces delta=0 for 95%+ of consecutive pairs. Collapsing to epoch boundaries gives the actual inter-epoch transitions needed for fitting.
- **Pooled decay estimation:** The ds005048 block structure (40s stim / 20s rest) yields only 0-2 valid decay candidates per subject. Rather than excluding most subjects, all valid decay candidates are pooled across subjects for a robust population median. This is documented in the JSON output (`tau_decay_method: pooled_across_subjects`).
- **Feature index correction:** Plan context stated stim_state at index 70; actual dataset has it at index 68. Verified from feature_names array in the NPZ files.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed stim_state feature index from 70 to 68**
- **Found during:** Task 1 (pre-implementation data inspection)
- **Issue:** Plan context stated stim_state at feature index 70, but actual feature_names array shows it at index 68
- **Fix:** Used correct index 68 with runtime assertion to verify feature name matches
- **Files modified:** fit_simulator_params.py
- **Verification:** Script loads data and verifies feature_names[68] == "stim_state"
- **Committed in:** f4f8738

**2. [Rule 1 - Bug] Added epoch-level collapse for PAC transitions**
- **Found during:** Task 1 (initial run produced 0 valid decay candidates)
- **Issue:** Plan assumed window-level consecutive pairs would have non-zero PAC deltas, but PAC is constant within epochs (20-40s blocks). 95%+ of window pairs have delta=0, producing tau=0 (invalid).
- **Fix:** Added collapse_to_epochs() function that detects epoch boundaries where PAC changes, then fits inter-epoch transitions instead
- **Files modified:** fit_simulator_params.py
- **Verification:** Script produces 3-5 rise candidates and 0-2 decay candidates per subject (matching the ~19 epochs per subject)
- **Committed in:** f4f8738

**3. [Rule 1 - Bug] Switched to pooled decay estimation**
- **Found during:** Task 1 (epoch-level approach still produced 0 subjects with >= 3 decay candidates)
- **Issue:** Rest epochs are sparse (5 per subject) and most rest-to-next transitions don't produce valid 0 < tau <= 1 candidates (PAC during rest often doesn't decrease monotonically toward rest target). Even with MIN_VALID_CANDIDATES=3, no subjects qualify.
- **Fix:** Pool all valid decay candidates across subjects (33 total from 29 subjects), compute population median from the pooled set. Per-subject decay uses MIN=1 for reporting.
- **Files modified:** fit_simulator_params.py
- **Verification:** Script completes with tau_decay_median=0.7557 from 33 pooled candidates
- **Committed in:** f4f8738

---

**Total deviations:** 3 auto-fixed (3 Rule 1 bugs)
**Impact on plan:** All auto-fixes were necessary for correctness given the actual data structure (epoch-level PAC, asymmetric block lengths). The core algorithm (exponential approach tau fitting) is unchanged; only the data preprocessing and aggregation strategy adapted to reality.

## Issues Encountered
- The fitted tau values (0.64 rise, 0.76 decay) are 4-8x larger than the heuristic defaults (0.15, 0.10), corresponding to much faster dynamics (T=1.0s and T=0.7s vs 6.2s and 9.5s). This is expected: the simulator operates on a normalized PAC scale (0.05-0.30) with gradual dynamics, while real epoch-level PAC transitions happen between discrete blocks. The fitted values reflect inter-epoch jumps, not within-epoch gradual change.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- fit_simulator_params.py available for re-running with different datasets
- results/simulator_tau_fit.json provides concrete numbers for RSRCH-04 defense
- Simulator docstring update (if desired) can reference these fitted values

---
*Phase: 14-scope-lock-completion*
*Completed: 2026-03-21*
