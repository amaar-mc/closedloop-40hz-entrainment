---
phase: 16-csef-documentation-and-presentation-package
plan: "04"
subsystem: research-paper
tags: [csef, research-paper, feature-ablation, pac-stim, documentation]
dependency_graph:
  requires: [experimental/FINDINGS.md, docs/paper/RESEARCH_PAPER_v3.md, results/4ch_vs_7ch_r2_gap_report.md, experimental/results/horizon_sweep_pac_stim.json]
  provides: [docs/paper/RESEARCH_PAPER_v4.md, CSEF/Research Paper/RESEARCH_PAPER_v4.md]
  affects: [CSEF submission package]
tech_stack:
  added: []
  patterns: [feature-ablation-study, multi-seed-robustness, surgical-document-update]
key_files:
  created:
    - docs/paper/RESEARCH_PAPER_v4.md
    - CSEF/Research Paper/RESEARCH_PAPER_v4.md
  modified: []
decisions:
  - "Paper v4 describes 12 PAC+Stim features as the primary configuration, not 73; 73-feature set remains as historical baseline in ablation discussion"
  - "Horizon sweep results use ts=1 (raw PAC) from horizon_sweep_pac_stim.json — not the ts=5 smoothed sweep from v3"
  - "4ch result reported as R2=0.430 from TCN h=32 dedicated run, consistent with experimental/FINDINGS.md"
  - "Stale number audit false positives are legitimate contextualized mentions of 73/61-feature set in ablation discussion — not actual stale claims"
metrics:
  duration_minutes: 7
  completed_date: "2026-03-23"
  tasks_completed: 2
  files_created: 2
  files_modified: 0
---

# Phase 16 Plan 04: Research Paper v4 Summary

**One-liner:** Surgical update of research paper from v3 to v4 integrating PAC+Stim 12-feature ablation discovery (R2=0.606±0.032), multi-seed robustness, 4ch comparison, and updated PAC+Stim horizon sweep.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create RESEARCH_PAPER_v4.md with feature ablation updates | ebbb0c6 | docs/paper/RESEARCH_PAPER_v4.md |
| 2 | Sync paper v4 to CSEF/ directory | 55a7ba8 | CSEF/Research Paper/RESEARCH_PAPER_v4.md |

## What Was Built

Research Paper v4 is a surgical update to v3 with the following changes across four sections:

**Abstract:** Updated TCN result from "R-squared ≈ 0.25" (smoothed) to "test R-squared = 0.606 ± 0.032 (5-seed mean)". Replaced "73 features" as the primary description with "12 PAC trajectory and stimulation context features". Added the spectral overfitting discovery sentence.

**Methods — Feature Engineering (Section 2.4):** Expanded from one paragraph to a full subsection with four sub-sections: (1) original 73-feature set historical description, (2) ablation study design, (3) ablation results table (6 rows), (4) selected 12 PAC+Stim features enumerated with rationale. Leakage verification statement included.

**Results (Sections 4.1-4.5 added/updated):**
- Section 4.1: Feature ablation results with interpretation
- Section 4.2: Multi-seed robustness table (5 seeds, mean 0.606 ± 0.032)
- Section 4.3: Architecture search on PAC+Stim (TCN h=32/64/128 comparison)
- Section 4.4: PAC+Stim horizon sweep — 7ch and 4ch tables from `horizon_sweep_pac_stim.json` (ts=1); comparison to 73-feature model
- Section 4.5: 4ch vs 7ch static and temporal comparison (EEGNet -0.271 delta vs TCN -0.176 delta)
- Summary of findings updated to 6 points (was 4)

**Discussion:**
- Section 5.1 (new): Why spectral features fail — mechanistic interpretation of subject-specific anatomy vs universal dynamics
- Section 5.4 (new): 4-channel consumer hardware viability — Muse 2 proxy result, practical implication, caveat about proxy vs real hardware
- Contributions updated from 4 to 5 (ablation study added as Contribution 2)
- TCN parameter count corrected to 22,914 (h=64) throughout

## Deviations from Plan

### False Positive in Verification

**Found during:** Overall verification
**Issue:** The plan's stale-number audit grep (`grep -n "73 feat\|61 spectral\|R² ≈ 0.25\|test R2 = 0.170" ... | grep -v "previous\|before\|original\|baseline\|ablation\|compared"`) flags legitimate contextualized mentions in the ablation discussion (Section 2.4.1, Table 3, Section 4.5) because those sentences don't use the excluded keywords.
**Resolution:** Reviewed each flagged line manually. All 6 matches are correct contextual usage: historical descriptions in the ablation study section, architecture table, and comparison tables. The primary claims (abstract, contributions, results summary) correctly use 12 features and R2=0.606.
**Impact:** None — paper is correctly written.

None — plan executed as specified.

## Number Traceability

| Number | Source | Location in Paper |
|--------|--------|-------------------|
| R2=0.606±0.032 | experimental/FINDINGS.md (Multi-Seed table) | Abstract, Table 2, Section 2.5.3, Section 4.2 |
| R2=0.558 (single seed) | experimental/FINDINGS.md (seed 42) | Table A1, Table 2 |
| R2=0.430 (4ch) | experimental/FINDINGS.md (4ch results) | Table 4, Section 4.5, Discussion 5.4 |
| Ablation table | experimental/FINDINGS.md (Feature Ablation Results) | Table A1, Section 4.1 |
| 7ch horizon sweep | experimental/results/horizon_sweep_pac_stim.json | Section 4.4 |
| 4ch horizon sweep | experimental/results/horizon_sweep_pac_stim.json | Section 4.4 |
| 7ch EEGNet R2=0.287 | results/4ch_vs_7ch_r2_gap_report.md | Table 4 |
| 4ch EEGNet R2=0.016 | results/4ch_vs_7ch_r2_gap_report.md | Table 4 |
| Controller results (72.1%, 64.5%, etc.) | results/RESULTS_REPORT.md (unchanged from v3) | Sections 4.6-4.7 |

## Self-Check: PASSED

- FOUND: docs/paper/RESEARCH_PAPER_v4.md
- FOUND: CSEF/Research Paper/RESEARCH_PAPER_v4.md
- FOUND: .planning/phases/16-csef-documentation-and-presentation-package/16-04-SUMMARY.md
- FOUND commit: ebbb0c6 (Task 1)
- FOUND commit: 55a7ba8 (Task 2)
