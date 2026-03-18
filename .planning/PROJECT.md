# Research Documentation Project

## What This Is

A comprehensive research project on "Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease" — including a complete computational pipeline, research paper, lab notebook, demo dashboard, and CSEF presentation materials.

## Core Value

Every claim in every document must be verifiably accurate against the actual code, data, and results — scientific integrity is non-negotiable.

## Current Milestone: v2.0 Paper Audit & Corrections

**Goal:** Systematically fix all issues identified by three parallel audit agents (data accuracy, methodology, internal consistency) so the research paper is submission-ready.

**Target fixes:**
- Correct all factual errors (hysteresis, CI method, population labels, spectral features)
- Fix citation errors and prune orphan references
- Resolve internal inconsistencies
- Propagate corrections to CSEF presentation and RESULTS_REPORT.md

## Requirements

### Validated

- ✓ Lab notebook finalized (V1/V2 pair) — v1.0 Phase 4
- ✓ Real-time demo dashboard (Streamlit + 40 Hz audio) — v1.0 Phase 5
- ✓ Complete research paper (11,647 words, 39 references) — v1.0 Phase 6
- ✓ CSEF 2026 presentation PDF (12 pages, Times New Roman) — v1.0

### Active

See `.planning/REQUIREMENTS.md` for v2.0 audit requirements.

### Out of Scope

- Rewriting the paper's narrative structure — only fix factual errors
- Running new experiments or retraining models
- Adding new analyses not in the original paper
- Re-running validation with different hysteresis (document what was actually used)

## Context

**Audit findings (2026-03-17):**
Three parallel agents audited RESEARCH_PAPER.md against source code, results files, and itself. Found 6 critical, 5 important, and 4 minor issues. All findings are documented in the audit agent outputs.

**Key discrepancies found:**
1. Hysteresis described as 5s in paper, but validation code uses 3s
2. CI method described as BCa bootstrap, but code uses normal approximation
3. Population labeled "dementia patients" in 2 locations, but 10/35 are healthy controls
4. Spectral features composition described incorrectly (no delta band, no coherence in code)
5. Reference [25] misattributed (TCFormer cited as EEGNet paper)
6. 16 of 39 references never cited in text

## Constraints

- **Data integrity**: Fix descriptions to match code, never change code to match descriptions
- **Consistency**: All corrections must propagate to CSEF presentation and RESULTS_REPORT
- **Accuracy**: Every number must be traceable to a source file

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Chronological daily format | Demonstrates real scientific process | ✓ Good |
| Use git dates as backbone | Ensures authenticity | ✓ Good |
| Fix paper to match code (not vice versa) | Code produced the actual results | — Pending |
| Document 3s hysteresis (not change to 5s) | Results were generated with 3s | — Pending |

---
*Last updated: 2026-03-17 after v2.0 milestone initialization*
