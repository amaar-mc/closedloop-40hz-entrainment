# Documentation Index

**Last updated:** 2026-03-05

## Quick Navigation

| What you're looking for | Where to go |
|------------------------|-------------|
| Project overview & how to run | [`../README.md`](../README.md) |
| Complete findings & results | [`../FINDINGS.md`](../FINDINGS.md) |
| Comprehensive results report | [`../results/RESULTS_REPORT.md`](../results/RESULTS_REPORT.md) |
| Synopsys abstract (250 words) | [`abstract/ABSTRACT.md`](abstract/ABSTRACT.md) |
| Poster board content (V5, latest) | [`poster/POSTER_BOARD_V5.md`](poster/POSTER_BOARD_V5.md) |
| Lab notebook review bundle | [`notebook/README.md`](notebook/README.md) |
| Synopsys reference guide | [`reference/SYNOPSYS_REFERENCE.md`](reference/SYNOPSYS_REFERENCE.md) |
| Presentation script | [`reference/PRESENTATION.md`](reference/PRESENTATION.md) |
| Current methodology | [`methodology/CURRENT_METHODOLOGY.md`](methodology/CURRENT_METHODOLOGY.md) |
| Code architecture map | [`methodology/CODE_MAP.md`](methodology/CODE_MAP.md) |
| Judge interview prep | [`submission/reports/JUDGE_INTERVIEW_PREP.md`](submission/reports/JUDGE_INTERVIEW_PREP.md) |
| Pipeline audit results | [`audits/`](audits/) |
| Research background papers | [`research/`](research/) |
| Historical analysis reports | [`reports/`](reports/) |

---

## Directory Structure

```
docs/
  INDEX.md                  <-- You are here

  abstract/                 Synopsys abstract materials
    ABSTRACT.md               Latest 247-word abstract
    P10.Abstract.pdf          Generated PDF for submission
    archive/                  Earlier PDF + 3 rounds of drafts

  poster/                   Poster board materials
    POSTER_BOARD_V5.md        Latest poster content (visual-forward)
    POSTER_BOARD_V5.pdf       Rendered PDF
    Synopsys Poster Final.pptx  PowerPoint source
    Synopsys Poster Final.pdf   Print-ready PDF
    exports/                  Slide image exports (PNG)
    archive/                  V1-V4 poster drafts
    reference/                Example posters from other projects

  notebook/                 Notebook review-bundle pointer
    README.md                 Points to the preserved original, corrected candidate, evidence map, and manual PDF export utility

  methodology/              Technical methodology
    CURRENT_METHODOLOGY.md    Pipeline implementation details
    CODE_MAP.md               File-by-file architecture reference

  reference/                Reference & preparation materials
    SYNOPSYS_REFERENCE.md     Fair rules, deadlines, judging criteria
    PROJECT_DEEP_DIVE.md      Comprehensive glossary & judge prep
    PRESENTATION.md           Presentation script
    feedback-kushal.md        Mentor feedback notes
    Lab Notebook Requirements.md/pdf  Format requirements
    Project S-19-05 Research Notebook (1).pdf  Example notebook

  submission/               Championship submission package
    INDEX.md                  Submission navigation
    reports/                  Achievement report, winning analysis, Q&A prep
    audit/                    Comprehensive code audit

  audits/                   Pipeline integrity audits
    PIPELINE_AUDIT_REPORT.md
    COMPREHENSIVE_SUBMISSION_AUDIT_REPORT.md
    TEMPORAL_MULTISCALE_AUDIT_REPORT.md

  reports/                  Historical analysis reports
    SUMMARY_FOR_USER.md
    COMPREHENSIVE_ANALYSIS_ALL_ATTEMPTS.md
    TEMPORAL_PREDICTION_*.md  (3 reports)

  research/                 Background literature (7 papers, .docx/.txt)

  archive/                  Outdated docs (pre-multiscale era)
```

---

## Current (Active) Documents

| Document | Description |
|----------|-------------|
| [`methodology/CURRENT_METHODOLOGY.md`](methodology/CURRENT_METHODOLOGY.md) | **Start here.** Complete description of the implemented pipeline, model, training, results. |
| [`methodology/CODE_MAP.md`](methodology/CODE_MAP.md) | File-by-file map of the codebase architecture. |
| [`../FINDINGS.md`](../FINDINGS.md) | Consolidated findings: model results, comparisons, conclusions, limitations. |

## Submission Documents

| Document | Description |
|----------|-------------|
| [`abstract/ABSTRACT.md`](abstract/ABSTRACT.md) | 247-word abstract for PDF upload. |
| [`notebook/README.md`](notebook/README.md) | Notebook review bundle pointer for the preserved original, corrected candidate, and manual PDF export path. |
| [`poster/POSTER_BOARD_V5.md`](poster/POSTER_BOARD_V5.md) | Final poster content (V5, visual-forward). |

## Audit Reports

| Document | Description |
|----------|-------------|
| [`audits/PIPELINE_AUDIT_REPORT.md`](audits/PIPELINE_AUDIT_REPORT.md) | Independent audit of the multiscale TCN pipeline. Covers leakage, results integrity, code quality. |
| [`audits/COMPREHENSIVE_SUBMISSION_AUDIT_REPORT.md`](audits/COMPREHENSIVE_SUBMISSION_AUDIT_REPORT.md) | Leakage/causality audit from submission gate scripts. |
| [`audits/TEMPORAL_MULTISCALE_AUDIT_REPORT.md`](audits/TEMPORAL_MULTISCALE_AUDIT_REPORT.md) | File-by-file technical audit of `temporal_multiscale/` module. |

## Technical Reports

| Document | Description |
|----------|-------------|
| [`reports/TEMPORAL_PREDICTION_DEEP_DIVE.md`](reports/TEMPORAL_PREDICTION_DEEP_DIVE.md) | Why temporal PAC prediction is hard: raw R^2 ~0.07, smoothed R^2 ~0.75, autocorrelation ceiling. |
| [`reports/TEMPORAL_PREDICTION_REPORT.md`](reports/TEMPORAL_PREDICTION_REPORT.md) | Temporal prediction approach and initial results. |
| [`reports/TEMPORAL_PREDICTION_FINAL_REPORT.md`](reports/TEMPORAL_PREDICTION_FINAL_REPORT.md) | Final temporal prediction report with all horizon results. |
| [`reports/COMPREHENSIVE_ANALYSIS_ALL_ATTEMPTS.md`](reports/COMPREHENSIVE_ANALYSIS_ALL_ATTEMPTS.md) | Analysis of all model architecture attempts (v1-v8). |
| [`reports/SUMMARY_FOR_USER.md`](reports/SUMMARY_FOR_USER.md) | Plain-English project summary. |

## Research Background

| Document | Description |
|----------|-------------|
| `research/01_Foundational_Concepts_*` | Neuroscience primer: gamma oscillations, PAC, 40 Hz entrainment, AD. |
| `research/02_Literature_Review_*` | Literature synthesis: PAC as biomarker, entrainment mechanisms, clinical trials. |
| `research/03_Technical_Methods_*` | EEG signal processing reference: filtering, PAC computation, DL architectures. |
| `research/04_Research_Methodology_*` | Research methodology and proposed approach. |
| `research/05_Annotated_Bibliography_*` | 39 annotated references. |
| `research/AD_40Hz_Entrainment_Research_Paper_IEEE.*` | IEEE-format research paper. |
| `research/Comprehensive_Methodology_*` | Full methodology document. |

## Archive (Outdated)

Pre-multiscale versions preserved for history. See [`archive/`](archive/) -- these contain outdated assumptions (wrong subject counts, unimplemented architectures, placeholder results).

## Key Discrepancies: Proposal vs. Reality

| Aspect | Original Proposal | Actual Implementation |
|--------|------------------|----------------------|
| Architecture | GAT-Transformer (hundreds of K params) | EEGNet (1.5K) + causal TCN (31K) |
| Channels | 64-128 high-density | 7 frontal (10/20) |
| Subjects | "20-40 healthy adults, 18-35yo" | 35 elderly dementia patients |
| Sampling rate | 500-1000 Hz | 250 Hz |
| Control system | MIQP MPC with GUROBI | Threshold z-score with hysteresis |
| Static R^2 target | > 0.80 | 0.287 (achieved) |
| Temporal R^2 | > 0.80 for 5-10s ahead | 0.25 at 5-10s horizon (TCN), -0.27 persistence |
| PAC range assumed | 0.001-0.3 | 0.0002-0.0046 (actual) |
