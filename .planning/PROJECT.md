# Research Documentation Project

## What This Is

A comprehensive research project on "Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease" — including a complete computational pipeline, research paper, lab notebook, demo dashboard, and CSEF presentation materials. All documents are now internally consistent and verified against source code.

## Core Value

Every claim in every document must be verifiably accurate against the actual code, data, and results — scientific integrity is non-negotiable.

## Requirements

### Validated

- ✓ Lab notebook finalized (V1/V2 pair) — v1.0 Phase 4
- ✓ Real-time demo dashboard (Streamlit + 40 Hz audio) — v1.0 Phase 5
- ✓ Complete research paper (11,647 words, 23 references) — v1.0 Phase 6
- ✓ CSEF 2026 presentation PDF (12 pages, Times New Roman) — v1.0
- ✓ Hysteresis corrected to 3-second throughout all documents — v2.0
- ✓ CI method corrected to large-sample normal approximation — v2.0
- ✓ Spectral features corrected (4 bands + PAC-structure, not 5 + coherence) — v2.0
- ✓ Population label standardized to "35 elderly subjects" — v2.0
- ✓ References pruned from 39 to 23, all renumbered and consistent — v2.0
- ✓ Single-author voice (I/my) throughout paper — v2.0
- ✓ All corrections propagated to CSEF docs, RESULTS_REPORT, TeX, PDF — v2.0

### Active

(No active requirements — next milestone not yet defined)

### Out of Scope

- Rewriting the paper's narrative structure — only fix factual errors
- Running new experiments or retraining models
- Adding new analyses not in the original paper
- Lab notebook phases 1-3 (deferred — content extraction, daily entries, visual polish)

## Context

**Shipped v2.0 (2026-03-18):**
Three parallel audit agents identified 6 critical, 5 important, and 4 minor issues in RESEARCH_PAPER.md. All were systematically corrected across phases 7-9 and propagated to 13+ supporting documents. Clean PDF compiled. 17/17 requirements verified.

**Current state:**
- Research paper: `docs/paper/RESEARCH_PAPER.md` (806 lines, 23 references, internally consistent)
- PDF: `docs/paper/RESEARCH_PAPER_v3.pdf` (2.7 MB, compiled from corrected TeX)
- Results: `results/RESULTS_REPORT.md` (verified clean — g=0.75, ×10⁻⁶ MI units)
- Poster: `docs/poster/POSTER_BOARD_V5.md` (all corrections propagated)
- Demo: `src/dashboard.py` (Streamlit, live PAC visualization + 40 Hz audio)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Chronological daily format | Demonstrates real scientific process | ✓ Good |
| Use git dates as backbone | Ensures authenticity | ✓ Good |
| Fix paper to match code (not vice versa) | Code produced the actual results | ✓ Good |
| Document 3s hysteresis (not change to 5s) | Results were generated with 3s | ✓ Good |
| Prune orphan references (39→23) | Clean citation list, every ref cited | ✓ Good |
| Single-author voice (I not we) | Single-author paper declaration | ✓ Good |
| Out-of-scope docs/paper/sections/ from propagation | RESEARCH_PAPER.md is assembled source of truth | ✓ Good |

## Constraints

- **Data integrity**: Fix descriptions to match code, never change code to match descriptions
- **Consistency**: All corrections must propagate to CSEF presentation and RESULTS_REPORT
- **Accuracy**: Every number must be traceable to a source file

---
*Last updated: 2026-03-18 after v2.0 milestone*
