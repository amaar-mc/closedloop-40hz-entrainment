---
phase: 06-write-research-paper
plan: 01
subsystem: research-paper
tags: [matplotlib, figures, publication, horizon-sweep, block-diagram, paper-structure]

# Dependency graph
requires:
  - phase: temporal-multiscale
    provides: models/sweep_horizons_results.json with TCN vs baseline R² at horizons 1-10s
provides:
  - scripts/generate_paper_figures.py — deterministic figure generation from JSON data
  - results/figures/horizon_sweep.{png,pdf} — TCN vs Persistence vs Ridge line graph (6 horizons)
  - results/figures/system_block_diagram.{png,pdf} — full EEG-to-stimulation pipeline diagram
  - docs/paper/sections/ — directory ready for parallel section writing by Plans 02-05
affects:
  - 06-02, 06-03, 06-04, 06-05 — all paper writing plans reference these figures

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Figure generation via standalone script reading JSON data source — no hardcoded values"
    - "Force-add figures to git (-f flag) to match existing tracked figures despite .gitignore"
    - "System python3 used (no venv present in repo); matplotlib 3.10.0 available globally"

key-files:
  created:
    - scripts/generate_paper_figures.py
    - results/figures/horizon_sweep.png
    - results/figures/horizon_sweep.pdf
    - results/figures/system_block_diagram.png
    - results/figures/system_block_diagram.pdf
    - docs/paper/sections/.gitkeep
  modified: []

key-decisions:
  - "Force-add figures with git add -f to match existing tracked figure pattern; .gitignore has results/figures/*.png and *.pdf but existing figures are already tracked"
  - "Use system python3 (matplotlib 3.10.0) — no venv exists in the repository"

patterns-established:
  - "Paper figures are generated from JSON data sources, not hardcoded, for reproducibility"
  - "docs/paper/sections/ is the canonical directory for parallel section writing"

requirements-completed:
  - PAPER-FIG

# Metrics
duration: 3min
completed: 2026-03-15
---

# Phase 6 Plan 01: Generate Paper Figures and Directory Structure Summary

**Horizon sweep (TCN vs Persistence vs Ridge, 6 horizons 1-10s) and system block diagram (EEG-to-stimulation pipeline) generated as PNG+PDF; docs/paper/sections/ directory created for parallel section writing**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-03-15T21:30:19Z
- **Completed:** 2026-03-15T21:32:49Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Created `scripts/generate_paper_figures.py` with two publication-quality figure generation functions, reading exact R² values from `models/sweep_horizons_results.json` (6 entries across horizons 1, 2, 3, 5, 8, 10s)
- Horizon sweep figure shows clear TCN advantage at 5-10s: TCN R²≈0.25-0.28 while Persistence and Ridge collapse to R²≈-0.27 to -0.39; shaded green region marks operationally useful range
- System block diagram shows the full pipeline: Patient EEG → Preprocessing → EEGNet (1,457 params) → Feature Extraction (73 features) → Causal TCN (31K params, 20s lookback) → Closed-Loop Controller → 40 Hz Audio, with colour-coded block types and feedback arc
- Created `docs/paper/sections/` directory ready for Plans 02-05 to write section markdown files

## Task Commits

Each task was committed atomically:

1. **Task 1: Create figure generation script and produce both new figures** - `1dde516` (feat)
2. **Task 2: Create paper directory structure** - `3a201ab` (chore)

## Files Created/Modified

- `scripts/generate_paper_figures.py` — Standalone figure generation script; reads sweep JSON, produces both figures as PNG (300 dpi) and PDF
- `results/figures/horizon_sweep.png` — 189 KB, 300 dpi, 8x5 inches
- `results/figures/horizon_sweep.pdf` — 18 KB vector, for paper submission
- `results/figures/system_block_diagram.png` — 223 KB, 300 dpi, 14x6 inches
- `results/figures/system_block_diagram.pdf` — 45 KB vector, for paper submission
- `docs/paper/sections/.gitkeep` — Tracks empty directory for parallel section writing

## Decisions Made

- **Force-add figures to git:** `.gitignore` has `results/figures/*.png` and `results/figures/*.pdf`, but existing figures (controller_comparison, etc.) are already tracked with force-add. New figures follow the same pattern with `git add -f`.
- **System python3, no venv:** The repository has no `venv/` directory. System Python 3.13.3 with matplotlib 3.10.0 is the execution environment. Script uses `python3` directly.
- **Caption note as script comment (not file):** The ts=5 vs ts=1 caveat ("Evaluated with 5-window causal target smoothing (ts=5). Deployed checkpoint uses raw targets (ts=1); see Supplementary Table S1 for absolute performance under that condition.") is embedded as a docstring comment in the generation script per plan specification.

## Deviations from Plan

None — plan executed exactly as written.

Minor discovery (not a deviation): `.gitignore` blocks `results/figures/*.{png,pdf}`, requiring `-f` flag for new figures. Existing figures in the repo were already tracked this way, so the pattern was already established. No gitignore modification needed.

## Issues Encountered

- `source venv/bin/activate` failed — no `venv/` directory exists in the repository. Resolved by using system `python3` (matplotlib 3.10.0 confirmed available). Script runs identically.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Both new figures are committed and ready for reference in all paper section plans (06-02 through 06-05)
- `docs/paper/sections/` is ready for parallel section writing
- Figure captions for the paper should reference the ts=5 smoothing caveat per the embedded script comment
- `scripts/generate_paper_figures.py` can be re-run at any time to regenerate figures if data changes

## Self-Check: PASSED

All created files confirmed present:
- [OK] scripts/generate_paper_figures.py
- [OK] results/figures/horizon_sweep.png
- [OK] results/figures/horizon_sweep.pdf
- [OK] results/figures/system_block_diagram.png
- [OK] results/figures/system_block_diagram.pdf
- [OK] docs/paper/sections/.gitkeep

All task commits confirmed present:
- [OK] 1dde516 (Task 1: figures)
- [OK] 3a201ab (Task 2: directory)
- [OK] 71d218d (metadata)

---
*Phase: 06-write-research-paper*
*Completed: 2026-03-15*
