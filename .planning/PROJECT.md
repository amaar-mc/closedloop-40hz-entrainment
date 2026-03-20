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

<!-- Current scope: v3.0 Deepen Research -->

**Research deepening (25%):**
- [ ] Comprehensive architecture comparison study (8 static + temporal models + new architectures)
- [ ] New model training (Transformer, XGBoost, etc.) to strengthen TCN selection narrative
- [ ] Statistical robustness analyses (cross-validation, sensitivity, ablation)
- [ ] Simulation accuracy defense (validation framework, comparison metrics)
- [ ] Timing advantage analysis (why prediction is necessary, operational window)
- [ ] Failure mode & limitations analysis (biggest reason this may NOT work)
- [ ] EEG+audio hardware research (headsets that record EEG + play stimulus)
- [ ] Multisensory stimulation expansion exploration

**Product platform (75%):**
- [ ] Web app — caregiver-facing closed-loop therapy platform
- [ ] Dual mode: simulated EEG (demo fallback) + real EEG headset integration
- [ ] Real-time adaptive auditory stimulus based on PAC prediction
- [ ] Session management, data logging, patient tracking
- [ ] Mobile app roadmap (productization narrative for judges)
- [ ] Productization documentation (clinical roadmap, integration with existing systems, remote monitoring)

**Presentation & pilot:**
- [ ] Updated poster board with QR code + human testing data
- [ ] Multiple presentation formats + 1-min elevator pitch
- [ ] Pilot demos at facilities (Mission Villa, Valley Medical Veterans Center, regional hospital)
- [ ] Flyer with QR code linking to live app

### Out of Scope

- Rewriting the paper's narrative structure — only fix factual errors
- Lab notebook phases 1-3 (deferred — content extraction, daily entries, visual polish)
- Full mobile app build (roadmap only — web app is primary)
- FDA regulatory submission (clinical testing plan documented but not executed)
- Manufacturing hardware (intelligence layer on existing hardware only)

## Current Milestone: v3.0 Deepen Research

**Goal:** Transform the research project into a productized, demo-ready platform while deepening ML rigor — targeting CSEF judging on 2026-04-09.

**Target features:**
- Comprehensive model architecture comparison study with new models trained
- Web app platform for caregiver-led closed-loop 40 Hz therapy sessions
- Dual-mode EEG (real hardware + simulated fallback) with adaptive stimulus
- Pilot demos at local facilities with collected feedback data
- Updated presentations, poster board with QR code, elevator pitch

**Framing guidance (from counselor):** "Predictive model for neural state with temporal forecasting" — NOT "AI for Alzheimer's." Intelligence layer on existing hardware. Project → solution → product.

**Split:** 25% research deepening / 75% product & presentation

## Context

**Shipped v2.0 (2026-03-18):**
Three parallel audit agents identified 6 critical, 5 important, and 4 minor issues in RESEARCH_PAPER.md. All were systematically corrected across phases 7-9 and propagated to 13+ supporting documents. Clean PDF compiled. 17/17 requirements verified.

**Current state:**
- Research paper: `docs/paper/RESEARCH_PAPER.md` (806 lines, 23 references, internally consistent)
- PDF: `docs/paper/RESEARCH_PAPER_v3.pdf` (2.7 MB, compiled from corrected TeX)
- Results: `results/RESULTS_REPORT.md` (verified clean — g=0.75, ×10⁻⁶ MI units)
- Poster: `docs/poster/POSTER_BOARD_V5.md` (all corrections propagated)
- Demo: `src/dashboard.py` (Streamlit, live PAC visualization + 40 Hz audio)

**CSEF context:**
- Admitted to California Science & Engineering Fair 2026
- Judging: 2026-04-09 (20 days from milestone start)
- Judges want productized, actionable solutions — not just research
- Pilot facilities identified: Mission Villa Alzheimer's Residence, Valley Medical Veterans Center, regional medical hospital
- Need: QR code on poster → live app, human testing data, clinical testing plan

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
*Last updated: 2026-03-20 after v3.0 milestone start*
