---
phase: 13-caregiver-app-and-pilot-preparation
plan: 01
subsystem: ui
tags: [streamlit, caregiver-app, patient-profiles, deployment]

# Dependency graph
requires:
  - phase: 12.1-improved-tcn-enhanced-features-multi-task-self-attention
    provides: "4ch TCN model checkpoints and scalers for Cloud deployment"
  - phase: 11-real-time-inference-pipeline
    provides: "StreamingFeatureExtractor and SimulatedEEGAdapter interfaces"
provides:
  - "Multi-page Streamlit caregiver app skeleton with page routing"
  - "Seed patient profiles JSON with demo session history"
  - "Streamlit Cloud deployment config (.streamlit/config.toml)"
  - "Git-tracked model artifacts (eegnet, TCN, scalers) for Cloud deployment"
affects: [13-02-PLAN, 13-03-PLAN]

# Tech tracking
tech-stack:
  added: [qrcode-pil, reportlab]
  patterns: [LABEL_MAP plain-language metric mapping, session_state page router]

key-files:
  created:
    - caregiver_app.py
    - data/caregiver_profiles.json
    - .streamlit/config.toml
  modified:
    - requirements.txt

key-decisions:
  - "model artifacts tracked in models/muse_4ch/ subdirectory — gitignore models/*.pth only catches top-level, no exception needed"
  - "3 demo patients with realistic Alzheimer/MCI demographics and metric ranges matching actual PAC values"

patterns-established:
  - "LABEL_MAP dict for translating internal metric keys to plain-language labels"
  - "session_state page router pattern: navigate() + st.rerun() for multi-page flow"
  - "_ROOT / sys.path pattern from demo.py reused for import resolution"

requirements-completed: [APP-01, APP-05]

# Metrics
duration: 3min
completed: 2026-03-21
---

# Phase 13 Plan 01: Deployment Scaffolding and Caregiver App Skeleton Summary

**Streamlit caregiver app with 3-patient profile system, multi-page routing, session history view, and Cloud deployment artifacts (config.toml, scalers.npz, model checkpoints)**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-21T08:36:06Z
- **Completed:** 2026-03-21T08:39:22Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- Deployment scaffolding: .streamlit/config.toml, requirements.txt with qrcode/reportlab, scalers.npz copied to git-tracked location
- All 4ch model artifacts (eegnet, TCN, training history, scalers) now git-tracked in models/muse_4ch/
- Caregiver app skeleton with 5 pages: welcome, patient_select, patient_history, session (stub), summary (stub)
- Seed profiles with 3 demo patients, 6 total sessions, realistic PAC/targeting metrics

## Task Commits

Each task was committed atomically:

1. **Task 1: Deployment scaffolding** - `d6065d4` (chore)
2. **Task 2: Patient profiles and app skeleton** - `1b9f8c7` (feat)

## Files Created/Modified
- `.streamlit/config.toml` - Streamlit Cloud server config with light theme
- `requirements.txt` - Added qrcode[pil] and reportlab dependencies
- `models/muse_4ch/scalers.npz` - TCN normalization scalers (copied from data/processed for Cloud)
- `models/muse_4ch/best_eegnet_4ch.pth` - Now git-tracked (was untracked)
- `models/muse_4ch/best_multiscale_tcn_4ch_lb20_hz5_ts1.pth` - Now git-tracked
- `models/muse_4ch/history_multiscale_tcn_4ch_lb20_hz5_ts1.json` - Now git-tracked
- `caregiver_app.py` - Multi-page Streamlit app with profile loading, routing, history view
- `data/caregiver_profiles.json` - 3 demo patients with session history

## Decisions Made
- Model artifacts in models/muse_4ch/ are not caught by the top-level `models/*.pth` gitignore pattern, so no exception rules were needed
- Used 3 demo patients with "(Demo)" suffix to clearly label synthetic data
- Metric values (brain_sync_level 0.000045-0.000068) match actual PAC ranges from the real dataset

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- caregiver_app.py skeleton is ready for Plan 02 to replace render_session() and render_summary() stubs with live session UI
- All model artifacts are git-tracked and will be available on Streamlit Cloud
- LABEL_MAP and save_session() utilities are in place for Plan 02's live metrics display

## Self-Check: PASSED

All 6 created files verified present. Both task commits (d6065d4, 1b9f8c7) verified in git log.

---
*Phase: 13-caregiver-app-and-pilot-preparation*
*Completed: 2026-03-21*
