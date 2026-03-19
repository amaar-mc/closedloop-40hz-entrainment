# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v2.0 — Paper Audit & Corrections

**Shipped:** 2026-03-18
**Phases:** 3 (v2.0 scope: 7-9) | **Plans:** 5 | **Commits:** 23

### What Was Built
- Systematic correction of 7 factual errors and 7 internal consistency issues across RESEARCH_PAPER.md
- Propagation of all corrections to 13 active CSEF presentation documents
- Updated LaTeX source and clean 2.7 MB PDF compilation
- Verified RESULTS_REPORT.md consistency (Hedges' g, PAC units)

### What Worked
- **Three-phase pipeline (fix → consistency → propagate)** kept corrections surgical and traceable
- **Parallel wave execution** in phase 9 saved time — doc propagation and PDF recompile ran simultaneously
- **Verification after each phase** caught residual misses (compound citation [12,39], bootstrap CI in QA doc) before they compounded
- **Integration checker at milestone audit** found 2 more propagation misses that phase-level verification missed — the cross-file perspective is valuable

### What Was Inefficient
- **Reference renumbering** missed compound citations (`[12, 39]` format) — the regex replacement approach needed to handle multi-citation groups, not just standalone `[N]` patterns
- **Propagation plan enumerated specific lines** rather than using correction categories with automated search — caused 2 files to have partial fixes
- **Phase 9 scope** excluded `docs/paper/sections/*.md` and `SUPPLEMENTARY.md` — these still contain stale values (tech debt)

### Patterns Established
- **Audit-first approach**: Run parallel audit agents before correction work to enumerate all issues systematically
- **Source-of-truth chain**: RESEARCH_PAPER.md → TeX → PDF; all other docs are downstream consumers
- **Verification-driven completion**: Phase isn't done until verifier confirms all must_haves

### Key Lessons
1. **Regex replacements on citations need compound-pattern handling** — always test `[N, M]` and `[N-M]` formats, not just standalone `[N]`
2. **Propagation plans should search-and-replace by value, not by line number** — line numbers shift after earlier edits
3. **Integration checking catches what phase-level verification misses** — always run milestone audit before shipping

### Cost Observations
- Model mix: ~10% opus (orchestration), ~90% sonnet (execution, verification)
- Sessions: 3 (phase 8 execution, phase 9 plan+execute, milestone audit+complete)
- Notable: Entire v2.0 milestone completed in under 2 days

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v2.0 | 3 | 3 (7-9) | Introduced audit-first workflow with parallel agents |

### Top Lessons (Verified Across Milestones)

1. Phase-level verification catches most issues; milestone-level integration checking catches the rest
2. Document corrections propagate better with search-by-value than with line-number targeting
