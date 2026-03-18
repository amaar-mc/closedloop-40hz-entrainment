# Requirements: Research Documentation Project

**Defined:** 2026-03-07
**Core Value:** Create an authentic chronological record that showcases scientific rigor through daily documentation of the complete research timeline.

## v1 Requirements

Requirements for the lab notebook conversion project.

### Content Extraction

- [ ] **CONT-01**: Extract all research content from existing notebook files
- [ ] **CONT-02**: Organize content by actual git commit dates (Dec 10, 2025 - Mar 6, 2026)
- [ ] **CONT-03**: Convert research paper format to daily log entry format
- [ ] **CONT-04**: Validate all data and results against repository sources

### Daily Entry Structure

- [ ] **ENTRY-01**: Create date headers for each research day
- [ ] **ENTRY-02**: Document daily goals and planned activities
- [ ] **ENTRY-03**: Record technical procedures and methods used
- [ ] **ENTRY-04**: Include results, observations, and data from that day
- [ ] **ENTRY-05**: Document failures, troubleshooting, and pivot decisions
- [ ] **ENTRY-06**: Add relevant code snippets from daily commits

### Visual Elements

- [ ] **VIS-01**: Include validated performance graphs and tables
- [ ] **VIS-02**: Add architecture diagrams showing model development
- [ ] **VIS-03**: Incorporate screenshots of results where appropriate
- [ ] **VIS-04**: Ensure all visuals are grounded in actual repository data

### Quality Standards

- [ ] **QUAL-01**: Follow Synopsys lab notebook formatting guidelines
- [ ] **QUAL-02**: Maintain scientific narrative consistency throughout
- [ ] **QUAL-03**: Keep document length to 8-10 pages (concise format)
- [ ] **QUAL-04**: Use only validated data - no fabrication

### Phase 4 Finalization

- [x] **FNL-01**: Re-anchor the notebook to the approval-era start date and preserve chronological order after the anchor
- [x] **FNL-02**: Produce a new review-ready notebook source without modifying or deleting existing notebook artifacts
- [x] **FNL-03**: Ensure every retained metric, date-sensitive claim, and pivotal figure is traceable to existing repository evidence or explicitly downgraded/removed
- [x] **FNL-04**: Use active-day headers plus explicit gap notes, with no hindsight narration and no fabricated content
- [ ] **FNL-05**: Package the final notebook in a review-safe way that supports manual PDF generation and resolves or documents path/tool mismatches
- [x] **FNL-06**: Provide a validation checklist separating automated sanity checks from human review of chronology, fairness, and judge readability

### Phase 5 Demo

- [x] **DEMO-01**: Streamlit single-page dashboard with configure-then-run workflow and matplotlib fallback
- [x] **DEMO-02**: Simulated brain dynamics using EntrainmentSimulator/FatigueAwareSimulator with fatigue on/off toggle
- [x] **DEMO-03**: All four controller strategies (Fixed Schedule, Reactive, Predictive Look-Ahead, Oracle) shown simultaneously
- [x] **DEMO-04**: Real 40 Hz click train audio output through speakers with mute button, binary on/off matching controller decisions
- [x] **DEMO-05**: Four stacked PAC trace panels with live animation and background stim/rest color bands
- [x] **DEMO-06**: Adjustable simulation speed (1x/5x/10x/Max) with progressive plot rendering

## v2.0 Requirements — Paper Audit & Corrections

### Data Accuracy

- [ ] **DATA-01**: Hysteresis duration corrected from "5-second" to "3-second" in all paper locations (Sections 1.4, 3.6.2, Figure 3 caption) and CSEF presentation
- [ ] **DATA-02**: CI method corrected from "10,000-iteration BCa bootstrap" to "large-sample normal approximation" in Section 3.8
- [ ] **DATA-03**: Lead time Hedges' g corrected from 0.76 to 0.75 in RESULTS_REPORT.md
- [ ] **DATA-04**: EEGNet "best epoch 53" removed or qualified as unverifiable in Section 3.3.2
- [ ] **DATA-05**: RESULTS_REPORT.md PAC Gap units corrected from "uV^2" to "x10^-6 MI units"

### Methodology

- [ ] **METH-01**: Spectral features description corrected to match actual code (4 bands not 5, PAC-structure features not coherence, global stats) in Section 3.4.1
- [ ] **METH-02**: Artifact rejection description corrected from "rejected" to "zeroed" in Section 3.1.2

### Internal Consistency

- [ ] **CONS-01**: Population description fixed from "35 dementia patients" to "35 elderly subjects" in Contribution 3 and Conclusion
- [ ] **CONS-02**: Reference [25] misattribution fixed (TCFormer citation corrected or removed)
- [ ] **CONS-03**: Orphan references pruned — keep only references actually cited in text
- [ ] **CONS-04**: Section 2.2 heading formatting fixed ("2.240 Hz" to "2.2 40 Hz")
- [ ] **CONS-05**: Mixed first person resolved — "we" changed to "I" throughout (single-author paper)
- [ ] **CONS-06**: "Reactive thresholding" standardized to "Reactive Threshold" at L80
- [ ] **CONS-07**: Orders of magnitude inconsistency resolved ("nearly three" vs "four")

### Propagation

- [ ] **PROP-01**: All corrections propagated to CSEF presentation PDF
- [ ] **PROP-02**: All corrections propagated to RESULTS_REPORT.md
- [ ] **PROP-03**: Research paper PDF recompiled after all fixes

## Out of Scope

| Feature | Reason |
|---------|--------|
| Rewriting paper narrative | Only fix factual errors, not restructure |
| Retraining models | Code produced actual results; fix descriptions |
| Re-running validation with 5s hysteresis | Document what was actually used (3s) |
| Adding new analyses | Paper scope is frozen |

## v1.0 Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CONT-01 | Phase 1 | Pending |
| CONT-02 | Phase 1 | Pending |
| CONT-03 | Phase 2 | Pending |
| CONT-04 | Phase 2 | Pending |
| ENTRY-01 | Phase 2 | Pending |
| ENTRY-02 | Phase 2 | Pending |
| ENTRY-03 | Phase 2 | Pending |
| ENTRY-04 | Phase 2 | Pending |
| ENTRY-05 | Phase 2 | Pending |
| ENTRY-06 | Phase 2 | Pending |
| VIS-01 | Phase 3 | Pending |
| VIS-02 | Phase 3 | Pending |
| VIS-03 | Phase 3 | Pending |
| VIS-04 | Phase 3 | Pending |
| QUAL-01 | Phase 3 | Pending |
| QUAL-02 | Phase 3 | Pending |
| QUAL-03 | Phase 3 | Pending |
| QUAL-04 | Phase 3 | Pending |
| FNL-01 | Phase 4 | Complete |
| FNL-02 | Phase 4 | Complete |
| FNL-03 | Phase 4 | Complete |
| FNL-04 | Phase 4 | Complete |
| FNL-05 | Phase 4 | Pending |
| FNL-06 | Phase 4 | Complete |
| DEMO-01 | Phase 5 | Complete |
| DEMO-02 | Phase 5 | Complete |
| DEMO-03 | Phase 5 | Complete |
| DEMO-04 | Phase 5 | Complete |
| DEMO-05 | Phase 5 | Complete |
| DEMO-06 | Phase 5 | Complete |

## v2.0 Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 7 | Pending |
| DATA-02 | Phase 7 | Pending |
| DATA-03 | Phase 7 | Pending |
| DATA-04 | Phase 7 | Pending |
| DATA-05 | Phase 7 | Pending |
| METH-01 | Phase 7 | Pending |
| METH-02 | Phase 7 | Pending |
| CONS-01 | Phase 8 | Pending |
| CONS-02 | Phase 8 | Pending |
| CONS-03 | Phase 8 | Pending |
| CONS-04 | Phase 8 | Pending |
| CONS-05 | Phase 8 | Pending |
| CONS-06 | Phase 8 | Pending |
| CONS-07 | Phase 8 | Pending |
| PROP-01 | Phase 9 | Pending |
| PROP-02 | Phase 9 | Pending |
| PROP-03 | Phase 9 | Pending |

**Coverage:**
- v2.0 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-07*
*Last updated: 2026-03-17 after v2.0 audit requirements added*
