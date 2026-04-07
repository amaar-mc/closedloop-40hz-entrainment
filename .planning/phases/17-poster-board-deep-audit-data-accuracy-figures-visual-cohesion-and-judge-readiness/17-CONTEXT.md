# Phase 17: Poster Board Deep Audit — Context

**Gathered:** 2026-04-07
**Status:** Ready for planning
**Source:** User direction (inline with /gsd:plan-phase invocation)

<domain>
## Phase Boundary

This phase is **audit-only**. No poster files, code, or figures are modified. The deliverable is a comprehensive audit report covering data accuracy, figure quality, visual cohesion, and judge-readiness for CSEF 2026 judging (2026-04-09).

**Poster artifacts under audit:**
- `CSEF/Poster/csef_posters/CSEF_poster_v2.pdf` — rendered/printed poster (V2)
- `CSEF/Poster/csef_posters/CSEF_poster.pptx` — editable source file

**Scope:** Read-only analysis. All outputs are reports/documentation in the phase directory.

</domain>

<decisions>
## Implementation Decisions

### Audit Scope
- Audit ONLY — no modifications to poster files, source code, figures, or any project artifacts
- All outputs are markdown audit reports written to the phase directory
- Cross-reference every number on the poster against actual result files in `results/`

### Data Accuracy Audit
- Verify every statistic, R-squared value, p-value, effect size, sample count, and percentage on the poster against ground-truth JSON/MD in `results/`
- Check all architecture descriptions (parameter counts, layer descriptions, input/output shapes) against actual model code in `src/` and `temporal_multiscale/`
- Verify dataset claims (35 subjects, 17,283 windows, split sizes, channel counts) against `data/processed/` and `src/data_loader.py`
- Flag any number that cannot be verified or that contradicts source data

### Figure Audit
- Assess every figure for: accuracy of plotted data, axis labels, legends, readability at poster scale, color accessibility
- Verify figure captions match what the figure actually shows
- Check that all "Diagram created by Amaar Chughtai" attributions are present where needed
- Assess figure numbering consistency and cross-references in text

### Visual Cohesion Audit
- Evaluate layout balance, whitespace usage, section flow (left-to-right, top-to-bottom reading order)
- Check font consistency, color palette consistency, heading hierarchy
- Assess whether the poster tells a coherent visual story from problem to solution to results
- Compare PDF render against PPTX source for any rendering artifacts

### Judge-Readiness Audit
- Evaluate from perspective of CSEF judges: Is the hypothesis clear? Are results compelling? Are limitations honest?
- Check for common judge concerns: overclaiming, missing controls, unclear methodology
- Assess whether the "Summary of Key Results" box and "Conclusions" are judge-friendly
- Evaluate the Future Directions and Clinical Use sections for realism and scientific rigor
- Check references for completeness and proper formatting

### Claude's Discretion
- Specific report structure and section ordering within audit documents
- Level of detail in figure-by-figure analysis
- Whether to produce one consolidated report or separate reports per audit dimension
- Statistical verification methodology (which JSON files to cross-reference)

</decisions>

<specifics>
## Specific Ideas

- The poster has 13+ figures — each needs individual assessment
- Key results to verify: R2=0.287 (EEGNet), R2=0.606 (PAC+Stim TCN), 72.1% alignment, 82.6% low-PAC targeting, g=1.31, g=4.47, 35/35 subjects benefit
- Feature ablation: 73 -> 12 features, R2 from -0.025 to 0.606
- Fatigue simulation: 4 models, 6 severity levels, n=50 trials each
- Hardware claims: Muse 2 ($249), total cost <$300
- Cross-reference against: `results/RESULTS_REPORT.md`, `results/tcn_validation_results.json`, `results/effect_sizes_lb20_hz5_ts1.json`, `results/fatigue_sensitivity.json`, `results/ablation_table.json`

</specifics>

<deferred>
## Deferred Ideas

- Any actual modifications to the poster based on audit findings (would be a separate phase if needed)
- Re-generation of figures
- PPTX template redesign

</deferred>

---

*Phase: 17-poster-board-deep-audit-data-accuracy-figures-visual-cohesion-and-judge-readiness*
*Context gathered: 2026-04-07 via user direction*
