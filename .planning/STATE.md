---
gsd_state_version: 1.0
milestone: v2.0
milestone_name: milestone
status: completed
last_updated: "2026-03-18T05:10:57.932Z"
last_activity: 2026-03-18 — Completed 09-02 TeX corrections and PDF recompile (2 commits)
progress:
  total_phases: 9
  completed_phases: 6
  total_plans: 14
  completed_plans: 14
---

# Project State: Research Documentation Project

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-17)

**Core value:** Every claim must be verifiably accurate against actual code, data, and results.
**Current focus:** v2.0 Paper Audit & Corrections — roadmap defined, ready to begin Phase 7.

## Current Status

**Milestone:** v2.0 Paper Audit & Corrections
**Phase:** Phase 9 (Plan 02 complete) — Propagate & Recompile PDF COMPLETE
**Plan:** 09-02 complete
**Status:** Milestone complete
**Last activity:** 2026-03-18 — Completed 09-02 TeX corrections and PDF recompile (2 commits)

**Progress bar:** [█████████░] 93% (13/14 plans complete)

## v2.0 Phase Summary

| Phase | Goal | Status |
|-------|------|--------|
| 7. Fix Data & Methodology Errors | Correct hysteresis, CI method, population labels, spectral features, artifact handling in RESEARCH_PAPER.md | Plan 01 complete |
| 8. Fix Internal Consistency | Fix population label, references, section heading, voice, and terminology throughout RESEARCH_PAPER.md | COMPLETE (Plans 01-02) |
| 9. Propagate & Recompile | Propagate all corrections to CSEF presentation and RESULTS_REPORT.md; recompile paper PDF | Plan 02 complete (PDF recompiled) |

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

## Accumulated Decisions (Phase 7)

- **Hysteresis=3s:** run_tcn_validation.py confirms hysteresis_hold=3; all 3 paper locations corrected from 5s
- **CI method:** large-sample normal approximation (g ± 1.96 × SE) used, not BCa bootstrap; 2 locations corrected
- **Spectral features:** 4 bands (theta/alpha/beta/gamma) × 7ch = 28 + 7 ratios + 21 PAC-struct + 5 globals = 61; no delta, no coherence
- **Artifact zeroing:** src/preprocessing.py sets samples to 0.0 (does not drop windows); wording corrected throughout Section 3.1.2
- **EEGNet epoch 53:** confirmed only for TCN; EEGNet best epoch not recorded; claim qualified in Section 3.3.2
- **Hedges' g Lead Time:** exact value 0.7549 rounds to 0.75 (not 0.76); RESULTS_REPORT.md corrected
- **PAC Gap units:** MI is dimensionless (Tort 2010); correct unit is ×10⁻⁶ MI units, not µV²; 6 locations in RESULTS_REPORT.md corrected

## Accumulated Decisions (Phase 8)

- **Population label:** "35 elderly subjects" is the consistent phrasing (never "dementia patients" — 10/35 are healthy controls); corrected at Contribution 3 and Conclusion
- **Single-author voice:** All 13 self-referential "we/our" replaced with "I/my"; Abstract already used I correctly and was left unchanged
- **Reactive Threshold capitalized:** Matches named controller variant in Section 3.6.3; "reactive thresholding" at Contribution 3 corrected
- **Orders of magnitude:** "nearly three orders of magnitude" is correct (1,457 to 1.1M = log10 ~2.88); Section 4.3 now consistent with L74
- **TCFormer sentence removed:** Sentence misattributing [25] as TCFormer deleted from Section 2.5.2; EEGNet [25] (now [18]) citation in 2.5.1 intact
- **Reference list pruned to 23:** 16 orphan references deleted; surviving 23 renumbered [1]-[23]; EEGNet=[18], Tort PAC=[22]
- **Single-pass citation replacement:** Used re.sub callback to avoid cascading replacement bugs when renumbering

## Accumulated Decisions (Phase 9 Plan 01)

- **CSEF propagation scope:** 13 active presentation/reference files corrected; docs/paper/sections/ and RESEARCH_PAPER_v3.md excluded from Phase 9-01 scope
- **Citation text exception:** Lahijanian 2024 paper title and dataset description phrases with "dementia patients" left unchanged per plan rule
- **Hysteresis in CSEF docs:** Updated to 3-second (from run_tcn_validation.py) across all active CSEF files
- **PROP-02 verified:** RESULTS_REPORT.md clean — zero stale values (µV², BCa bootstrap, 0.76 Lead Time, 5-second hysteresis)
- **Spectral features:** 73-feature breakdown corrected in 05_qa_complete.md and JUDGE_INTERVIEW_PREP.md (4 bands, not 5; PAC-structure, not coherence)

## Accumulated Decisions (Phase 9 Plan 02)

- **TeX correction approach:** Applied all corrections directly to RESEARCH_PAPER_v3.tex (pandoc unavailable); rebuilt stale 17-entry reference list to correct 23 entries with full body renumbering
- **TCN dilation factors:** Fixed [1,2,4,6] -> [1,2,4,8] in TeX (was a pre-existing bug in the TeX file not caught in Phases 7-8)
- **Remaining dementia patients in TeX:** 4 occurrences remain in reference titles and external-study citations — all acceptable, only Contribution 3 language was required to change

## Blockers/Concerns

None identified.

---
Last activity: 2026-03-18 - Completed Phase 9 Plan 02: TeX corrections + PDF recompile — all Phase 7+8 fixes propagated to RESEARCH_PAPER_v3.tex; clean 2.7 MB PDF compiled (PROP-03)
