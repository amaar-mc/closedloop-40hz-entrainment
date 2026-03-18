# Roadmap: Research Documentation Project

**Created:** 2005-03-07
**Project:** Research Documentation Project
**Core Value:** Create an authentic chronological record that showcases scientific rigor through daily documentation of the complete research timeline.

## Phases Overview

**9 phases** | **28 v1 requirements + 17 v2.0 requirements mapped** | v2.0 Paper Audit & Corrections added 2026-03-17

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Content Foundation | Extract and organize research content | 4 | 2 |
| 2 | Daily Entries | Create chronological lab notebook structure | 8 | 1/2 | In Progress|  | Visual Polish | Add visuals and ensure quality standards | 4 | 3 |
| 4 | Finalize Lab Notebook | ~~Finalize a judge-ready review bundle without touching original notebook files~~ DONE | 6 | 5/5 | Complete   | 2026-03-15 | Real-Time Demo | Interactive Streamlit dashboard with live PAC visualization and 40 Hz audio | 6 | 3 |
| 6 | Write Research Paper | Comprehensive venue-agnostic research paper with full IMRAD structure | 10 | 4 |
| 7 | 1/1 | Complete   | 2026-03-18 | 3 |
| 8 | Fix Internal Consistency | Resolve all internal consistency issues in RESEARCH_PAPER.md (population labels, references, formatting, voice, terminology) | 7 | 4 |
| 9 | Propagate & Recompile | Propagate all corrections to CSEF presentation and RESULTS_REPORT.md, then recompile the paper PDF | 3 | 3 |

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
**Plans:** 5/5 plans complete

**Success Criteria:**
1. Complete assembled research paper (docs/paper/RESEARCH_PAPER.md) with all sections from Abstract through References
2. Two new publication-quality figures generated (system block diagram, horizon sweep)
3. Supplementary materials with additional figures, tables, and ts=1/ts=5 comparison
4. All metrics cross-checked for consistency with submitted abstract and validated result files

Plans:
- [ ] 06-01-PLAN.md — Generate two new publication figures (horizon sweep + system block diagram) and create paper directory structure
- [x] 06-02-PLAN.md — Write front matter: Abstract, Introduction, and Literature Review
- [ ] 06-03-PLAN.md — Write Methods and Architecture Search sections
- [ ] 06-04-PLAN.md — Write Results, Discussion, Future Directions, and Conclusion
- [ ] 06-05-PLAN.md — Assemble complete paper, write references and supplementary materials, cross-check consistency, human review

### Phase 7: Fix Data Accuracy & Methodology Errors

**Goal:** The paper's factual claims about system implementation match the actual code and results — hysteresis duration, CI method, population composition, spectral feature set, and best-epoch claims are all accurate.

**Depends on:** Phase 6
**Requirements:** DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, METH-01, METH-02
**Plans:** 1/1 plans complete

**Success Criteria (what must be TRUE):**
1. A reader of RESEARCH_PAPER.md can find "3-second" hysteresis in every location that previously said "5-second" (Sections 1.4, 3.6.2, Figure 3 caption)
2. Section 3.8 describes the CI method as large-sample normal approximation and RESULTS_REPORT.md shows the corrected Hedges' g of 0.75 for lead time with PAC gap units changed to "x10^-6 MI units"
3. Section 3.4.1 describes 4 spectral bands (not 5), PAC-structure features (not coherence), and global stats — matching what `temporal_multiscale/build_multiscale_dataset.py` actually computes
4. Section 3.1.2 says artifacts are "zeroed" (not "rejected") and Section 3.3.2 contains no unqualified "best epoch 53" claim

Plans:
- [ ] 07-01-PLAN.md — Correct all 7 data accuracy and methodology errors in RESEARCH_PAPER.md and RESULTS_REPORT.md

### Phase 8: Fix Internal Consistency

**Goal:** RESEARCH_PAPER.md is internally consistent — population label, references, formatting, grammatical voice, and terminology are uniform throughout.

**Depends on:** Phase 7
**Requirements:** CONS-01, CONS-02, CONS-03, CONS-04, CONS-05, CONS-06, CONS-07
**Plans:** 2/2 plans complete

**Success Criteria (what must be TRUE):**
1. Every mention of the subject population uses "35 elderly subjects" (not "35 dementia patients"), and the reference list contains only references that are cited somewhere in the text body
2. Reference [25] correctly attributes the EEGNet paper (not TCFormer), and Section 2.2 heading renders as "2.2 40 Hz Entrainment" (not "2.240 Hz")
3. Every first-person pronoun in the paper is "I" — no "we" or "our" — matching the single-author declaration
4. The terms "Reactive Threshold" (not "Reactive thresholding") and a single consistent orders-of-magnitude phrase are used wherever that controller and PAC scale are mentioned

Plans:
- [x] 08-01-PLAN.md — Fix population label, section heading, first-person voice, terminology, and magnitude phrase (CONS-01, CONS-04, CONS-05, CONS-06, CONS-07)
- [x] 08-02-PLAN.md — Remove TCFormer sentence and prune/renumber orphan references (CONS-02, CONS-03)

### Phase 9: Propagate Corrections & Recompile PDF

**Goal:** All corrections made in Phases 7 and 8 are reflected in the CSEF presentation and RESULTS_REPORT.md, and a clean PDF of the corrected paper exists.

**Depends on:** Phase 8
**Requirements:** PROP-01, PROP-02, PROP-03
**Plans:** TBD

**Success Criteria (what must be TRUE):**
1. Every factual claim corrected in RESEARCH_PAPER.md (hysteresis, CI method, population label, spectral features, artifact handling) matches the corresponding slide or section in the CSEF presentation
2. RESULTS_REPORT.md reflects the corrected Hedges' g (0.75) and corrected PAC gap units (x10^-6 MI units) with no contradicting values anywhere in the file
3. A PDF of RESEARCH_PAPER.md exists that compiles cleanly from the corrected source, contains no placeholder text, and shows all section headings correctly formatted

---

## Dependencies

- Phase 2 requires Phase 1 completion (need organized content before structuring entries)
- Phase 3 requires Phase 2 completion (need entries before adding visuals)
- Phase 7 requires Phase 6 completion (paper must exist before corrections)
- Phase 8 requires Phase 7 completion (factual errors fixed before consistency pass)
- Phase 9 requires Phase 8 completion (all paper corrections done before propagation)

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Content Foundation | - | Not started | - |
| 2. Daily Entries | - | Not started | - |
| 3. Visual Polish | - | Not started | - |
| 4. Finalize Lab Notebook | 3/3 | Complete | 2026-03-15 |
| 5. Real-Time Demo | 1/1 | Complete | - |
| 6. Write Research Paper | 5/5 | Complete | - |
| 7. Fix Data & Methodology Errors | 1/1 | Complete | 2026-03-17 |
| 8. Fix Internal Consistency | 2/2 | Complete | 2026-03-18 |
| 9. Propagate & Recompile | 0/TBD | Not started | - |

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
