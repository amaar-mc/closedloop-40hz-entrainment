---
phase: 16-csef-documentation-and-presentation-package
plan: "02"
subsystem: documentation
tags: [poster, csef, pac-stim, feature-discovery, v6]
dependency_graph:
  requires: []
  provides: [docs/poster/POSTER_BOARD_V6.md, CSEF/Poster/POSTER_BOARD_V6.md]
  affects: [CSEF presentation package]
tech_stack:
  added: []
  patterns: [numerical-traceability, source-verified-claims]
key_files:
  created:
    - docs/poster/POSTER_BOARD_V6.md
    - CSEF/Poster/POSTER_BOARD_V6.md
  modified: []
decisions:
  - "V6 includes 73-feature comparison in narrative context (ablation table) — this is scientifically required to explain the 5x improvement, not a stale claim"
  - "TCN params reported as 5,154 (h=32 PAC+stim model) rather than 31,043 (old 73-feature model)"
  - "Horizon sweep data uses pac_stim JSON values, not sweep_horizons_results.json (which is the old 73-feature sweep)"
metrics:
  duration: "4m"
  completed_date: "2026-03-23"
  tasks_completed: 2
  tasks_total: 2
  files_created: 2
  files_modified: 0
---

# Phase 16 Plan 02: Poster Board V6 Summary

POSTER_BOARD_V6.md created in docs/poster/ and CSEF/Poster/ with 12-feature PAC+Stim breakthrough replacing stale 73-feature numbers — test R² updated from −0.025 to 0.606 mean (5-seed), horizon sweep updated to pac_stim values, 4ch comparison added, conclusions reframed with feature selection as primary finding.

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Create POSTER_BOARD_V6.md with PAC+Stim updates | ebda050 | docs/poster/POSTER_BOARD_V6.md |
| 2 | Sync poster V6 to CSEF/ directory | 992f09b | CSEF/Poster/POSTER_BOARD_V6.md |

## Key Changes in V6

### Numerical Updates (all verified against source)

| Item | V5 Value | V6 Value | Source |
|------|----------|----------|--------|
| Feature count | 73 | 12 | experimental/FINDINGS.md |
| TCN R² at h=5 | 0.254 | 0.577 (7ch) | horizon_sweep_pac_stim.json |
| TCN R² mean | — | 0.606 ± 0.032 | experimental/FINDINGS.md |
| TCN R² 4ch | — | 0.430 | experimental/FINDINGS.md |
| TCN params | 31,043 | 5,154 (h=32) | experimental/FINDINGS.md |
| h=3 R² (7ch) | 0.277 | 0.607 | horizon_sweep_pac_stim.json |
| h=8 R² (7ch) | 0.240 | 0.370 | horizon_sweep_pac_stim.json |
| h=10 R² (7ch) | 0.278 | 0.669 | horizon_sweep_pac_stim.json |
| h=5 R² (4ch) | — | 0.398 | horizon_sweep_pac_stim.json |
| Fair name | Synopsys Championship | CSEF | plan spec |

### Unchanged from V5 (verified)

- Controller comparison: 72.1% vs 64.5%, g=1.31, all p-values — from results/RESULTS_REPORT.md
- Architecture Exploration table: static EEGNet R² = 0.287 — unaffected by feature discovery
- Fatigue simulation results — separate evaluation path
- Per-subject consistency: 35/35 subjects — unaffected

### New Sections Added

1. Feature ablation table (Val R² / Test R² for 4 feature subsets)
2. 12 PAC+Stim features list (explicit bullet points)
3. Multi-seed reproducibility statement (0.606 ± 0.032, 5 seeds)
4. 7ch vs 4ch comparison table with consumer EEG deployment narrative
5. Comprehensive V6 changelog with numerical verification log

## Deviations from Plan

None — plan executed exactly as written.

## Verification Results

- `test -f docs/poster/POSTER_BOARD_V6.md`: PASS
- `grep -c "12 features|12 PAC" docs/poster/POSTER_BOARD_V6.md`: 8 matches (>0) PASS
- `grep -c "0.606|0.577|0.430" docs/poster/POSTER_BOARD_V6.md`: 19 matches (>0) PASS
- `diff docs/poster/POSTER_BOARD_V6.md CSEF/Poster/POSTER_BOARD_V6.md`: no output (identical) PASS
- Stale number audit (73 feat/61 spectral/R²≈0.25/R²=0.170/test R2=0.121 outside context): 0 stale matches PASS
- V5 preserved in both locations: PASS

## Self-Check: PASSED

Files created:
- `docs/poster/POSTER_BOARD_V6.md` — FOUND
- `CSEF/Poster/POSTER_BOARD_V6.md` — FOUND

Commits verified:
- ebda050 (feat(16-02): create POSTER_BOARD_V6) — FOUND
- 992f09b (chore(16-02): sync POSTER_BOARD_V6 to CSEF) — FOUND
