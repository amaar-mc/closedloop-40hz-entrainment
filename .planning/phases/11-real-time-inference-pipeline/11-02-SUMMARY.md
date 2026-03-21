---
phase: 11-real-time-inference-pipeline
plan: 02
subsystem: inference
tags: [brainflow, eeg-streaming, model-registry, protocol, tcn, real-time]

# Dependency graph
requires:
  - phase: 11-real-time-inference-pipeline
    provides: plan 11-01 StreamingFeatureExtractor and 4-channel TCN checkpoint from Phase 10

provides:
  - SimulatedEEGAdapter: BrainFlow SYNTHETIC_BOARD source yielding (n_channels, 500) float32 EEG windows
  - RealEEGAdapter stub with documented Plan 03 Muse 2 integration notes
  - TemporalModel runtime_checkable Protocol defining step()/reset() contract
  - TCNTemporalModel: adapter wrapping RealtimePACForecaster without changing its API
  - ModelRegistry: register/get/available with Protocol validation at registration time
  - build_default_registry() factory with 4-channel TCN pre-registered as "tcn"
  - 24-test suite verifying all registry/Protocol/warmup behaviors

affects:
  - 11-03 (Muse 2 hardware adapter will extend RealEEGAdapter stub)
  - 12 (Phase 12 comparison study registers XGBoost/Transformer via same registry)
  - Streamlit caregiver app (uses registry.get("tcn") for model selection)

# Tech tracking
tech-stack:
  added:
    - brainflow==5.21.0 (SYNTHETIC_BOARD for hardware-free EEG simulation)
    - xgboost==3.2.0 (baseline model, Phase 12 will register it)
  patterns:
    - Protocol-based model dispatch — registry.get("tcn") replaces if/else branches
    - BoardShim.get_eeg_channels() for channel discovery — never hardcoded indices
    - LogLevels.LEVEL_OFF to suppress BrainFlow C++ debug output
    - TDD RED/GREEN with [PASS]/[FAIL] style matching repo audit conventions

key-files:
  created:
    - src/streaming/adapters.py
    - temporal_multiscale/model_registry.py
    - tests/test_model_registry.py
  modified:
    - requirements.txt (added brainflow and xgboost lines)
    - src/streaming/__init__.py (restored StreamingFeatureExtractor import after overwrite)

key-decisions:
  - "TemporalModel Protocol is runtime_checkable so isinstance() validates conformance without subclassing"
  - "TCNTemporalModel wraps RealtimePACForecaster unchanged — Protocol adapter, not subclass"
  - "ModelRegistry validates at register() time so inference hot-path never gets surprises"
  - "cycle_phase_sin/cos always default 0.0/1.0 in TCNTemporalModel.step() — not exposed via Protocol"
  - "XGBoost and Transformer added in Phase 12 via registry.register() — zero changes to model_registry.py"

patterns-established:
  - "Protocol pattern: new model types satisfy TemporalModel by implementing step()/reset() — no registry edits needed"
  - "BrainFlow pattern: always query get_eeg_channels() at runtime, suppress logging with LEVEL_OFF"
  - "Test style: print [PASS]/[FAIL] per assertion, exit(1) on any failure — matches repo audit convention"

requirements-completed:
  - RTINF-02
  - RTINF-04

# Metrics
duration: 35min
completed: 2026-03-20
---

# Phase 11 Plan 02: Simulated EEG Adapter and Model Registry Summary

**BrainFlow SYNTHETIC_BOARD adapter streaming (4, 500) float32 windows and a runtime_checkable TemporalModel Protocol registry with TCN loaded by name string**

## Performance

- **Duration:** 35 min
- **Started:** 2026-03-20T00:00:00Z
- **Completed:** 2026-03-20T00:35:00Z
- **Tasks:** 2 (Task 1: SimulatedEEGAdapter; Task 2: TemporalModel/ModelRegistry TDD)
- **Files modified:** 5

## Accomplishments

- SimulatedEEGAdapter wraps BrainFlow SYNTHETIC_BOARD: auto-discovers EEG channels via get_eeg_channels(), suppresses C++ logging, yields (n_channels, 500) float32 at 2-second intervals, context manager cleanup
- TemporalModel Protocol (runtime_checkable) and ModelRegistry eliminate all if/else model-type branches from inference code — new models register in one line
- TCNTemporalModel delegates to RealtimePACForecaster without API changes: lookback=20, feature_dim=49, returns None until buffer full then prediction dict
- All 24 tests pass covering: register/get/available, KeyError with model list, TypeError on bad registration, Protocol isinstance, step() warmup (None→dict), reset()

## Task Commits

Each task was committed atomically:

1. **Task 1: Install brainflow/xgboost, create SimulatedEEGAdapter** - `373ed53` (feat)
2. **Fix: restore __init__.py overwritten in Task 1** - `3f7b7b6` (fix)
3. **Task 2 RED: add failing tests for TemporalModel/ModelRegistry** - `75c2921` (test)
4. **Task 2 GREEN: implement TemporalModel Protocol, ModelRegistry, TCNTemporalModel** - `c01d14d` (feat)

_Note: TDD task 2 produced test then implementation commits (RED/GREEN cycle)_

## Files Created/Modified

- `src/streaming/adapters.py` - SimulatedEEGAdapter (BrainFlow SYNTHETIC_BOARD) and RealEEGAdapter stub
- `src/streaming/__init__.py` - Restored conditional import of adapters alongside StreamingFeatureExtractor
- `temporal_multiscale/model_registry.py` - TemporalModel Protocol, TCNTemporalModel, ModelRegistry, build_default_registry()
- `tests/test_model_registry.py` - 8 test functions, 24 assertions, [PASS]/[FAIL] style
- `requirements.txt` - Added brainflow>=5.21.0 and xgboost>=3.2.0

## Decisions Made

- TemporalModel uses `@runtime_checkable` Protocol so isinstance() works without subclassing — consistent with Python structural typing
- ModelRegistry validates at register() time (not get() time) so hot-path never encounters non-conformant objects
- TCNTemporalModel does not expose cycle_phase_sin/cos via Protocol — defaults 0.0/1.0 are appropriate for closed-loop inference without explicit protocol timing
- XGBoost/Transformer registration deferred to Phase 12 — build_default_registry() designed for zero-edit extension

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Restored src/streaming/__init__.py overwritten during Task 1**
- **Found during:** Between Task 1 commit and Task 2 start
- **Issue:** My Task 1 write of `__init__.py` replaced Plan 11-01's version (which imports StreamingFeatureExtractor). The auto-tool restored the correct version after my commit.
- **Fix:** Staged and committed the restored version as a follow-up fix commit (3f7b7b6)
- **Files modified:** src/streaming/__init__.py
- **Verification:** `from src.streaming import SimulatedEEGAdapter` succeeds after fix
- **Committed in:** 3f7b7b6

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug, overwrite of prior plan's file)
**Impact on plan:** Fix was necessary for package import correctness. No scope creep.

## Issues Encountered

- `src/streaming/__init__.py` was overwritten during Task 1 (my write replaced Plan 11-01's version). Detected immediately from system notification and fixed with a follow-up commit before any test was run.

## User Setup Required

None — no external service configuration required. BrainFlow SYNTHETIC_BOARD runs without hardware.

## Next Phase Readiness

- Plan 11-03 (Muse 2 RealEEGAdapter) can extend the stub in adapters.py — all integration notes documented in the stub
- Phase 12 comparison study can register XGBoost and Transformer via `registry.register("xgboost", ...)` without touching model_registry.py
- Caregiver Streamlit app can call `build_default_registry().get("tcn")` for inference

---
*Phase: 11-real-time-inference-pipeline*
*Completed: 2026-03-20*
