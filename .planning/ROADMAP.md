# Roadmap: Research Documentation Project

**Created:** 2005-03-07
**Project:** Research Documentation Project
**Core Value:** Create an authentic chronological record that showcases scientific rigor through daily documentation of the complete research timeline.

## Phases Overview

**6 phases** | **28 requirements mapped** | Phase 5 demo requirements added | Phase 6 paper requirements added

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Content Foundation | Extract and organize research content | 4 | 2 |
| 2 | Daily Entries | Create chronological lab notebook structure | 8 | 4 |
| 3 | Visual Polish | Add visuals and ensure quality standards | 4 | 3 |
| 4 | Finalize Lab Notebook | ~~Finalize a judge-ready review bundle without touching original notebook files~~ DONE | 6 | 3 |
| 5 | Real-Time Demo | Interactive Streamlit dashboard with live PAC visualization and 40 Hz audio | 6 | 3 |
| 6 | Write Research Paper | Comprehensive venue-agnostic research paper with full IMRAD structure | 10 | 4 |

## Phase Details

### Phase 1: Content Foundation

**Goal:** Extract all research content and organize by chronological timeline using git commit history.

**Requirements:** CONT-01, CONT-02, CONT-03, CONT-04

**Success Criteria:**
1. All existing research content extracted from notebooks/ folder
2. Complete timeline mapped to git commits (Dec 10, 2025 - Mar 6, 2026) with work identified for each date

### Phase 2: Daily Entries

**Goal:** Transform research paper content into daily lab notebook entries with proper scientific logging structure.

**Requirements:** ENTRY-01, ENTRY-02, ENTRY-03, ENTRY-04, ENTRY-05, ENTRY-06

**Success Criteria:**
1. Daily date headers for each research day
2. Each entry contains: goals, procedures, results, failures documented
3. Relevant code snippets included from daily commits
4. Scientific narrative flows chronologically showing real research process

### Phase 3: Visual Polish

**Goal:** Add validated visual elements and ensure lab notebook meets quality standards.

**Requirements:** VIS-01, VIS-02, VIS-03, VIS-04, QUAL-01, QUAL-02, QUAL-03, QUAL-04

**Success Criteria:**
1. All performance graphs and tables validated against repository data
2. Architecture diagrams show model development progression
3. Final document is 8-10 pages following Synopsys guidelines

### Phase 5: Real-Time EEG Visualization and Audio Stimulation Demo

**Goal:** Build an interactive Streamlit dashboard that demonstrates the closed-loop 40 Hz entrainment system in real time — visualizing simulated PAC dynamics across all four controller strategies with live 40 Hz audio click train stimulation output.

**Requirements:** DEMO-01, DEMO-02, DEMO-03, DEMO-04, DEMO-05, DEMO-06
**Depends on:** Phase 4
**Plans:** 1 plan

**Success Criteria:**
1. `streamlit run` launches a single-page dashboard with configuration controls and four live PAC trace panels
2. All four controller strategies run simultaneously on simulated brain dynamics with fatigue toggle, producing visible performance differences
3. 40 Hz click trains play through speakers during STIMULATE periods with mute control

Plans:
- [x] 05-01-PLAN.md — Complete demo dashboard: Streamlit app with simulation engine, four-panel live PAC visualization, and 40 Hz audio stimulation

### Phase 6: Write Research Paper

**Goal:** Write a comprehensive, venue-agnostic research paper documenting the full closed-loop 40 Hz entrainment system — from clinical motivation through architecture exploration to TCN-based predictive control and validated results. Full IMRAD structure with dedicated Literature Review, Architecture Search, and Future Directions sections.

**Requirements:** PAPER-FIG, PAPER-STRUCTURE, PAPER-LITREV, PAPER-TONE, PAPER-CLINICAL, PAPER-ARCHSEARCH, PAPER-METHODS, PAPER-RESULTS, PAPER-FUTURE, PAPER-REFS, PAPER-SUPPLEMENT, PAPER-CONSISTENCY
**Depends on:** Phase 5
**Plans:** 5 plans

**Success Criteria:**
1. Complete assembled research paper (docs/paper/RESEARCH_PAPER.md) with all sections from Abstract through References
2. Two new publication-quality figures generated (system block diagram, horizon sweep)
3. Supplementary materials with additional figures, tables, and ts=1/ts=5 comparison
4. All metrics cross-checked for consistency with submitted abstract and validated result files

Plans:
- [ ] 06-01-PLAN.md — Generate two new publication figures (horizon sweep + system block diagram) and create paper directory structure
- [ ] 06-02-PLAN.md — Write front matter: Abstract, Introduction, and Literature Review
- [ ] 06-03-PLAN.md — Write Methods and Architecture Search sections
- [ ] 06-04-PLAN.md — Write Results, Discussion, Future Directions, and Conclusion
- [ ] 06-05-PLAN.md — Assemble complete paper, write references and supplementary materials, cross-check consistency, human review

---

## Dependencies

- Phase 2 requires Phase 1 completion (need organized content before structuring entries)
- Phase 3 requires Phase 2 completion (need entries before adding visuals)

## Timeline Estimate

- **Phase 1:** Content extraction and organization (moderate scope)
- **Phase 2:** Daily entry creation (largest scope - 16 requirements total across timeline)
- **Phase 3:** Visual elements and polishing (focused scope)

### Phase 4: Finalize Lab Notebook

**Goal:** Finalize a judge-ready, approval-anchored lab notebook review bundle that preserves originals, documents evidence, and supports manual PDF generation.

**Requirements:** FNL-01, FNL-02, FNL-03, FNL-04, FNL-05, FNL-06
**Depends on:** Phase 3
**Plans:** 3 plans

**Success Criteria:**
1. A new corrected notebook source exists at the generator contract path without overwriting the original notebook files.
2. The corrected notebook is re-anchored to the approval-era start date, uses active-day entries plus gap notes, and keeps claims traceable to repository evidence.
3. The review bundle includes automated sanity checks, a human review checklist, and minimal docs packaging for manual PDF export.

Plans:
- [x] 04-01-PLAN.md — Create the Wave 0 verifier and non-destructive review bundle skeleton.
- [x] 04-02-PLAN.md — Populate evidence mapping and rewrite the corrected notebook to the approval-era chronology.
- [x] 04-03-PLAN.md — Package the review bundle, reorganize to V1/V2 naming, and gate final signoff with human review.
