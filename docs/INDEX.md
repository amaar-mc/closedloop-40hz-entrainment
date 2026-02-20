# Documentation Index

**Last updated:** 2026-02-20

## Quick Navigation

| What you're looking for | Where to go |
|------------------------|-------------|
| Project overview & how to run | [`../README.md`](../README.md) |
| Complete findings & results | [`../FINDINGS.md`](../FINDINGS.md) |
| Current methodology | [`CURRENT_METHODOLOGY.md`](CURRENT_METHODOLOGY.md) |
| Code architecture map | [`CODE_MAP.md`](CODE_MAP.md) |
| Pipeline audit results | [`audits/`](audits/) |
| Research background papers | [`research/`](research/) |
| Historical analysis reports | [`reports/`](reports/) |

---

## Directory Structure

```
docs/
  INDEX.md                  <-- You are here
  CURRENT_METHODOLOGY.md    Current pipeline methodology
  CODE_MAP.md               Code architecture & file reference
  STATUS_REPORT_Synopsys_Readiness.md   Progress report
  LAB_NOTEBOOK.txt          Chronological development log

  research/                 Background literature & research papers
    01_Foundational_Concepts_40Hz_Entrainment_AD.*
    02_Literature_Review_40Hz_Entrainment_AD.*
    03_Technical_Methods_Signal_Processing.*
    04_Research_Methodology_Proposed_Approach.*
    05_Annotated_Bibliography_Sources.*
    AD_40Hz_Entrainment_Research_Paper_IEEE.*
    Comprehensive_Methodology_Closed_Loop_40Hz_Entrainment.*

  reports/                  Technical analysis & results reports
    SUMMARY_FOR_USER.md
    COMPREHENSIVE_ANALYSIS_ALL_ATTEMPTS.md
    TEMPORAL_PREDICTION_REPORT.md
    TEMPORAL_PREDICTION_FINAL_REPORT.md
    TEMPORAL_PREDICTION_DEEP_DIVE.md

  audits/                   Pipeline integrity & leakage audits
    PIPELINE_AUDIT_REPORT.md
    COMPREHENSIVE_SUBMISSION_AUDIT_REPORT.md
    TEMPORAL_MULTISCALE_AUDIT_REPORT.md

  archive/                  Outdated docs (pre-multiscale era)
    04_Research_Methodology_Proposed_Approach.*  (original proposal)
    AD_40Hz_Entrainment_Research_Paper_IEEE.*    (draft with placeholders)
    Comprehensive_Methodology_Closed_Loop_40Hz_Entrainment.*
    STATUS_REPORT_Synopsys_Readiness.md
```

---

## Current (Active) Documents

| Document | Description |
|----------|-------------|
| [`CURRENT_METHODOLOGY.md`](CURRENT_METHODOLOGY.md) | **Start here.** Complete description of the implemented pipeline, model, training, results. |
| [`CODE_MAP.md`](CODE_MAP.md) | File-by-file map of the codebase architecture. |
| [`../FINDINGS.md`](../FINDINGS.md) | Consolidated findings: model results, comparisons, conclusions, limitations. |

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
