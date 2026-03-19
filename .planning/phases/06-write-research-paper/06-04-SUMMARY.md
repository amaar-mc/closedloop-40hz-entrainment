---
phase: 06-write-research-paper
plan: "04"
subsystem: documentation
tags: [alzheimers, 40hz-entrainment, pac, tcn, eeg, closed-loop, research-paper, results, discussion, future-directions, conclusion]

requires:
  - phase: 06-write-research-paper
    provides: Methods and Architecture Search sections (plans 03); Abstract, Introduction, Literature Review (plan 02)
  - phase: 06-write-research-paper
    provides: results/RESULTS_REPORT.md, results/tcn_validation_results.json, results/fatigue_sensitivity.json, results/effect_sizes_lb20_hz5_ts1.json

provides:
  - docs/paper/sections/06-results.md — Complete Results section (203 lines) with horizon sweep, controller comparison, per-subject, fatigue robustness, threshold sensitivity, and deployed model performance
  - docs/paper/sections/07-discussion.md — Discussion section (102 lines) with mechanistic interpretation, prior art comparison, and explicit limitations
  - docs/paper/sections/08-future-directions.md — Future Directions (73 lines) with IRB pathway, pilot study design, and 6 technical extensions
  - docs/paper/sections/09-conclusion.md — Conclusion (55 lines) summarizing 4 contributions without overclaiming

affects:
  - 06-write-research-paper (final paper assembly will combine all 9 sections)

tech-stack:
  added: []
  patterns:
    - "Results section: Wilcoxon W + p + Hedges g + 95% CI format for all primary comparisons"
    - "PAC gap in dimensionless Modulation Index units (×10⁻⁶) — never uV-squared"
    - "Precise 91.6% (not 91%) for oracle comparison (30.5/33.3=0.9159)"
    - "Per-subject range stated with concrete values: 0.1 to 14.9 percentage points"
    - "Horizon sweep target clarification: ts=5 for sweep, ts=1 for deployed model"

key-files:
  created:
    - docs/paper/sections/06-results.md
    - docs/paper/sections/07-discussion.md
    - docs/paper/sections/08-future-directions.md
    - docs/paper/sections/09-conclusion.md
  modified: []

key-decisions:
  - "Results section adds Section 6.6 (deployed model performance) to clarify R²=0.170 vs ts=5 sweep results — prevents reader confusion about two different target definitions"
  - "Discussion 7.3 compares to Portiloop (detection vs forecasting distinction), Scalable Framework (classification vs regression), and DBS work (invasive vs non-invasive)"
  - "Conclusion uses 'computational validation on real EEG data' explicitly and contrasts it with 'clinical validation' — precise scope boundary per plan requirement"
  - "Future Directions 8.1 specifies N=20 pilot crossover design with specific outcome measures and safety monitoring per plan requirement for clinical translation pathway"
  - "Forecasting-vs-control performance gap discussed: Pearson r=0.433 directional signal drives g=+1.31 alignment advantage, threshold-crossing accuracy more relevant than absolute R²"

patterns-established:
  - "Statistical reporting: '(Wilcoxon signed-rank: W=0, p<0.001; Hedges' g=+1.31, 95% CI [+0.75, +1.87], N=35 paired subjects)'"
  - "Limitation framing: each limitation includes a forward-looking statement linking to future work"
  - "Horizon sweep table format: rows by horizon, columns for Persistence/Ridge/TCN R² and TCN margin over Persistence"
  - "Controller comparison table: Alignment / Low-PAC Stim / High-PAC Rest / Stim % / PAC Gap (×10⁻⁶)"

requirements-completed: [PAPER-STRUCTURE, PAPER-RESULTS, PAPER-CLINICAL, PAPER-FUTURE]

duration: 15min
completed: 2026-03-15
---

# Phase 6 Plan 04: Results, Discussion, Future Directions, and Conclusion Summary

**Complete data-driven Results section with 5 subsections (203 lines), mechanistic Discussion comparing to Portiloop/DBS/scalable-framework prior art, IRB-pathway Future Directions, and concise Conclusion scoped to computational validation.**

## Performance

- **Duration:** ~15 minutes
- **Started:** 2026-03-15T21:42:26Z
- **Completed:** 2026-03-15T21:57:37Z
- **Tasks:** 2/2
- **Files created:** 4

## Accomplishments

- Written 06-results.md (203 lines): 6.1 Horizon sweep with inflection point at ~3s; 6.2 Controller comparison table matching RESULTS_REPORT.md exactly; 6.3 Per-subject analysis (0.1 to 14.9 pp range computed from JSON); 6.4 Fatigue robustness monotonic growth; 6.5 Threshold sensitivity plateau at δz≥0.3; 6.6 Deployed model (R²=0.170, Pearson r=0.433)
- Written 07-discussion.md (102 lines): 7.1 Mechanistic inflection explanation (autocorrelation decay, TCN multi-scale context); 7.2 Timing (0.6s lead advantage) and targeting (60% recall improvement) decomposition; 7.3 Prior art (Portiloop, Scalable Framework, DBS); 7.4 Five explicit limitations including offline replay and EEGNet not in loop
- Written 08-future-directions.md (73 lines): IRB approval, N=20 pilot crossover design with specific outcome measures, Phase 3 regulatory; 6 technical extensions including RL controller and multi-biomarker
- Written 09-conclusion.md (55 lines): 4 contributions summarized; "computational validation on real EEG data" — no clinical overclaiming; 91.6% oracle (precise); per-subject 0.1 to 14.9 pp

## Task Commits

1. **Task 1: Write Results section** — `d5df0a5` (feat)
2. **Task 2: Write Discussion, Future Directions, and Conclusion** — `00f19b1` (feat)

## Files Created/Modified

- `docs/paper/sections/06-results.md` — Complete Results section (203 lines): 6 subsections with horizon sweep, controller comparison (N=35), per-subject universality, fatigue robustness, threshold sensitivity, deployed model metrics
- `docs/paper/sections/07-discussion.md` — Discussion section (102 lines): mechanistic interpretation of inflection, proactive/reactive trade-off, prior art comparison, 5 explicit limitations
- `docs/paper/sections/08-future-directions.md` — Future Directions (73 lines): clinical translation pathway (IRB, pilot design, regulatory), 6 technical extensions
- `docs/paper/sections/09-conclusion.md` — Conclusion (55 lines): 4 contributions, computational validation scoping, clinical translation roadmap

## Decisions Made

- Added Section 6.6 (deployed model performance) not explicitly in the plan to clarify the ts=5 horizon sweep R² vs the ts=1 deployed checkpoint R²=0.170. This prevents a reader from thinking the deployed model achieves R²≈0.25 (the sweep result) when it achieves R²=0.170 on raw targets. Treated as Rule 2 (missing critical context for correctness).
- Computed per-subject alignment improvement range (0.097pp to 14.924pp) directly from `results/tcn_validation_results.json` per_subject data at execution time. Rounded to 0.1pp and 14.9pp per plan instruction.
- 91.6% = 30.5/33.3 (precise arithmetic) used throughout — not "91%" (truncation error in RESULTS_REPORT.md) and not "92%" (poster V5's upward rounding). STATE.md decision log records "91% in text" but the plan explicitly requires "91.6%".
- Discussion does not repeat "Hedges g" as a label (it would be redundant after the Results section), but correctly references the statistical findings and interprets them mechanistically.

## Deviations from Plan

### Auto-added: Section 6.6 Deployed Model Performance

**Rule 2 — Missing critical context**

- **Found during:** Task 1 (Results section)
- **Issue:** The plan specifies reporting horizon sweep results (ts=5 targets, R²≈0.25 at 5-10s) and also states the deployed checkpoint uses ts=1 (raw targets, R²=0.170). Without a dedicated section, a reader comparing the sweep R² to the deployed model R² would be confused about why they differ.
- **Fix:** Added Section 6.6 explaining both configurations, clarifying that they measure different things and cannot be directly compared.
- **Files modified:** docs/paper/sections/06-results.md
- **Verification:** Section addresses the "Note on target definition" requirement explicitly stated in Task 1 action text.
- **Committed in:** d5df0a5

---

**Total deviations:** 1 auto-added (Rule 2 - missing critical context)
**Impact on plan:** Additive only — improved clarity without scope creep. Line count reached 203 (>200 minimum).

## Issues Encountered

- Initial Results section was 127 lines, below the 200-line minimum. Resolved by expanding with clinical significance of inflection point, PI controller behavior analysis, secondary Hybrid TCN+Reactive comparison, forecasting-vs-control performance gap discussion, data integrity verification block, and figure reference appendix. Final count: 203 lines.
- Per-subject improvement range required computing from raw JSON (not available in RESULTS_REPORT.md as pre-computed values). Computed via Python: min=0.097pp (rounds to 0.1pp), max=14.924pp (rounds to 14.9pp), all 35 subjects positive.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All four sections (Results, Discussion, Future Directions, Conclusion) complete and committed.
- Combined with plans 02-03 sections (Abstract through Architecture Search), the paper now has 9 complete sections (01 through 09).
- All numerical claims have been verified against source JSON files (tcn_validation_results.json, fatigue_sensitivity.json, effect_sizes_lb20_hz5_ts1.json, sweep_horizons_results.json).
- No blockers — paper sections are ready for assembly into a single document or LaTeX compilation.

## Self-Check: PASSED

- FOUND: docs/paper/sections/06-results.md (committed d5df0a5)
- FOUND: docs/paper/sections/07-discussion.md (committed 00f19b1)
- FOUND: docs/paper/sections/08-future-directions.md (committed 00f19b1)
- FOUND: docs/paper/sections/09-conclusion.md (committed 00f19b1)
- FOUND commit d5df0a5 (Task 1: Results section)
- FOUND commit 00f19b1 (Task 2: Discussion + Future Directions + Conclusion)
- Results: 203 lines (>=200 minimum) — PASS
- Discussion: 102 lines (>=100 minimum) — PASS
- Future Directions: 73 lines (>=60 minimum) — PASS
- Conclusion: 55 lines (>=30 minimum) — PASS
- 91.6% present: 3 instances across 06-results.md and 09-conclusion.md — PASS
- No "µV²/uV²/microvolts squared": 0 instances — PASS
- Per-subject range (0.1 pp to 14.9 pp): present in 06-results.md lines 86 and 183 — PASS
- "offline" / "counterfactual" in Discussion: 6 instances — PASS
- "IRB" / "pilot study" in Future Directions: 5 instances — PASS
- "computational validation" in Conclusion: present — PASS
- "clinical validation" only as negation ("not a clinical validation") — PASS

---
*Phase: 06-write-research-paper*
*Completed: 2026-03-15*
