---
phase: 13-caregiver-app-and-pilot-preparation
plan: 02
subsystem: ui
tags: [streamlit, eeg, pac, audio, wav, closed-loop, caregiver]

requires:
  - phase: 13-01
    provides: "Caregiver app skeleton with page router, patient profiles, session history stubs"
  - phase: 11
    provides: "SimulatedEEGAdapter, StreamingFeatureExtractor, PredictiveLookAheadController"
provides:
  - "Live session loop with 2-second EEG inference and PAC display"
  - "40 Hz auditory click-train stimulus via st.audio"
  - "PAC trend chart with Brain Sync Level metric"
  - "Session summary with plain-language metrics saved to patient profile"
  - "Disabled Real EEG Mode toggle (APP-03 Cloud constraint)"
affects: [13-03, deployment]

tech-stack:
  added: [scipy.io.wavfile]
  patterns: [st.cache_resource for PyTorch model caching, st.rerun loop for real-time simulation, pac_to_display z-score normalization]

key-files:
  created: []
  modified:
    - caregiver_app.py

key-decisions:
  - "EEGNet constructor uses n_samples=500 (not n_times) and no n_classes parameter -- discovered during checkpoint verification"
  - "40 Hz stimulus uses 1ms click-train WAV via scipy.io.wavfile, cached with st.cache_data"
  - "PAC-to-display converts raw PAC to 0-100 scale via z-score clamped to [-3,3]"
  - "Real EEG Mode toggle present but disabled with tooltip explaining Cloud BLE limitation"

patterns-established:
  - "st.rerun() with time.sleep(2.0) for simulated real-time session loop"
  - "st.cache_resource for PyTorch model + controller singleton across reruns"
  - "pac_to_display() as the single raw-PAC to caregiver-facing metric conversion"

requirements-completed: [APP-02, APP-03, APP-04]

duration: 32min
completed: 2026-03-21
---

# Phase 13 Plan 02: Live Session Loop Summary

**Live EEG inference loop with 40 Hz click-train audio, PAC trend chart, and session summary using PredictiveLookAheadController and SimulatedEEGAdapter**

## Performance

- **Duration:** ~32 min (across two executor sessions with checkpoint)
- **Started:** 2026-03-21T08:15:00Z
- **Completed:** 2026-03-21T08:57:13Z
- **Tasks:** 3 (2 auto + 1 human-verify checkpoint)
- **Files modified:** 1 (caregiver_app.py)

## Accomplishments
- Full render_session() implementation: 2-second inference loop with warmup indicator, Brain Sync Level metric, stimulus ACTIVE/REST badge, PAC trend line chart
- 40 Hz auditory click-train stimulus via st.audio with volume slider and loop/autoplay
- Session summary page with 3 plain-language metrics (Brain Sync Level, Therapy Active %, Targeting Accuracy %) and automatic save to patient profile
- Disabled Real EEG Mode toggle satisfying APP-03 while being honest about Cloud BLE constraints

## Task Commits

Each task was committed atomically:

1. **Task 1: 40 Hz WAV generator and model loader helpers** - `617fdd2` (feat)
2. **Task 2: Live session render, PAC chart, audio, and summary page** - `682229a` (feat)
3. **Task 3: Checkpoint: Verify live session loop, audio, and summary flow** - human-verify approved

**Post-checkpoint bugfix:** `9eb2258` (fix) - EEGNet constructor uses n_samples not n_times, no n_classes parameter

## Files Created/Modified
- `caregiver_app.py` - Full caregiver app with live session loop, 40 Hz audio, PAC trend chart, session summary (623 lines)

## Decisions Made
- EEGNet constructor signature uses `n_samples=500` (not `n_times`) and omits `n_classes` -- discovered during live testing at checkpoint, fixed in commit 9eb2258
- 40 Hz stimulus implemented as 1ms click-train WAV (40 periods/second, 1kHz sine click) generated via scipy.io.wavfile, cached with `@st.cache_data`
- PAC-to-display conversion uses z-score normalization clamped to [-3, 3] mapped to [0, 100] range -- gives caregivers an intuitive 0-100 "Brain Sync Level" scale
- Real EEG Mode toggle is present in sidebar but disabled with tooltip explaining BLE hardware requirement -- satisfies APP-03 UI presence while being honest about Cloud deployment constraints

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] EEGNet constructor argument mismatch**
- **Found during:** Task 3 (checkpoint verification)
- **Issue:** Plan specified `EEGNet(n_channels=4, n_times=500, n_classes=1)` but actual EEGNet constructor uses `n_samples` parameter name and has no `n_classes` argument
- **Fix:** Changed to `EEGNet(n_channels=4, n_samples=500)` matching the actual class signature
- **Files modified:** caregiver_app.py
- **Verification:** App loads and runs sessions without constructor errors
- **Committed in:** `9eb2258`

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Constructor argument fix was essential for app functionality. No scope creep.

## Issues Encountered
None beyond the EEGNet constructor mismatch documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- caregiver_app.py is fully functional locally (streamlit run caregiver_app.py)
- Plan 13-03 (presentation materials, facility flyer, QR codes) can proceed independently
- Streamlit Cloud deployment ready -- all model artifacts tracked in models/muse_4ch/
- App satisfies the core CSEF demo moment: judge scans QR, selects patient, runs live session

## Self-Check: PASSED

All artifacts verified:
- caregiver_app.py: FOUND
- Commit 617fdd2 (Task 1): FOUND
- Commit 682229a (Task 2): FOUND
- Commit 9eb2258 (bugfix): FOUND
- 13-02-SUMMARY.md: FOUND

---
*Phase: 13-caregiver-app-and-pilot-preparation*
*Completed: 2026-03-21*
