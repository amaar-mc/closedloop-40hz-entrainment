---
gsd_state_version: 1.0
milestone: v2.0
milestone_name: Paper Audit & Corrections
current_plan: Not started
status: Roadmap defined — ready to plan Phase 7
stopped_at: null
last_updated: "2026-03-17"
last_activity: 2026-03-17
progress:
  total_phases: 3
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State: Research Documentation Project

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-17)

**Core value:** Every claim must be verifiably accurate against actual code, data, and results.
**Current focus:** v2.0 Paper Audit & Corrections — roadmap defined, ready to begin Phase 7.

## Current Status

**Milestone:** v2.0 Paper Audit & Corrections
**Phase:** Phase 7 (not yet started) — Fix Data Accuracy & Methodology Errors
**Plan:** —
**Status:** Roadmap defined — ready to plan Phase 7
**Last activity:** 2026-03-17 — Roadmap created with Phases 7, 8, 9

**Progress bar:** [----------] 0% (0/3 phases complete)

## v2.0 Phase Summary

| Phase | Goal | Status |
|-------|------|--------|
| 7. Fix Data & Methodology Errors | Correct hysteresis, CI method, population labels, spectral features, artifact handling in RESEARCH_PAPER.md | Not started |
| 8. Fix Internal Consistency | Fix population label, references, section heading, voice, and terminology throughout RESEARCH_PAPER.md | Not started |
| 9. Propagate & Recompile | Propagate all corrections to CSEF presentation and RESULTS_REPORT.md; recompile paper PDF | Not started |

## Accumulated Context

### v1.0 Completed Work
- Phase 4 delivered V1/V2 notebook pair with 19-check verification script.
- Phase 5 built Streamlit demo with simulated dynamics (real TCN needs 73 features from real EEG).
- Phase 6 wrote complete IMRAD research paper (11,647 words, 39 references).

### v2.0 Audit Findings (2026-03-17)
- Three audit agents completed 2026-03-17: found 6 critical, 5 important, 4 minor issues.
- Key principle: fix paper to match code, not code to match paper.
- Critical: hysteresis is 3s in code (paper says 5s); CI uses normal approximation (paper says BCa bootstrap).
- Critical: 10/35 subjects are healthy controls (paper says "dementia patients" in 2 locations).
- Critical: spectral features are 4 bands + PAC-structure (paper describes 5 bands + coherence).
- Critical: reference [25] misattributed (TCFormer cited as EEGNet paper).
- Important: 16/39 references are orphans (never cited in text).
- Important: paper uses "we/our" throughout (single-author paper should use "I").

### Key Files for Phase 7-9
- `docs/paper/RESEARCH_PAPER.md` — primary correction target
- `docs/paper/RESEARCH_PAPER_v3.md` — may be newer version; confirm before editing
- `results/RESULTS_REPORT.md` — secondary correction target (DATA-03, DATA-05, PROP-02)
- CSEF presentation — tertiary correction target (PROP-01)
- `temporal_multiscale/build_multiscale_dataset.py` — source of truth for spectral features (METH-01)
- `src/controller.py` — source of truth for hysteresis value (DATA-01)

## Blockers/Concerns

None identified.

---
Last activity: 2026-03-17 - Roadmap created for v2.0 milestone (Phases 7, 8, 9)
