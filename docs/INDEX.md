# docs/ — Document Index

**Last reorganized:** 2026-02-18

## Current (Active Documents)

These reflect the actual implemented pipeline and verified results:

| Document | Description |
|----------|-------------|
| `CURRENT_METHODOLOGY.md` | **Start here.** Complete description of the implemented pipeline, model, training, results, and audit findings. |
| `PIPELINE_AUDIT_REPORT.md` | Independent audit of the multiscale TCN pipeline (Feb 2026). Covers leakage, results integrity, suspicious patterns, code integrity, deployment realism. |
| `COMPREHENSIVE_SUBMISSION_AUDIT_REPORT.md` | Leakage/causality audit from the submission gate scripts. |
| `TEMPORAL_MULTISCALE_AUDIT_REPORT.md` | File-by-file technical audit of `temporal_multiscale/` module. |
| `TEMPORAL_PREDICTION_DEEP_DIVE.md` | Analysis of why temporal PAC prediction is hard: raw R^2 ~0.07, smoothed R^2 ~0.75, autocorrelation ceiling. |

## Reference (Background Literature — Still Relevant)

These cover the scientific foundations and are still accurate as background:

| Document | Description |
|----------|-------------|
| `01_Foundational_Concepts_40Hz_Entrainment_AD.txt/.docx` | Neuroscience primer: gamma oscillations, PAC, 40 Hz entrainment, AD. Note: dataset description (13 subjects) is outdated — actual count is 35. |
| `02_Literature_Review_40Hz_Entrainment_AD.txt/.docx` | Literature synthesis: PAC as biomarker, entrainment mechanisms, clinical trials. Aspirational performance claims (87% accuracy) are not achieved. |
| `03_Technical_Methods_Signal_Processing.txt/.docx` | EEG signal processing reference: filtering, PAC computation (MI), DL architectures. Surveys architectures beyond what was actually built (GATs, Transformers, etc.). |
| `05_Annotated_Bibliography_Sources.txt/.docx` | 39 annotated references. Bibliographic data is accurate. |

## Archived (Outdated — Preserved for History)

Moved to `archive_pre_multiscale/`. These describe the **originally proposed** methodology, which differs significantly from what was implemented:

| Document | Why Archived |
|----------|-------------|
| `04_Research_Methodology_Proposed_Approach.txt/.docx` | Proposes GAT-Transformer + MIQP MPC (never built). Wrong dataset description (healthy adults, 64-128 channels, 500 Hz). Performance targets (R^2 > 0.80) not met on raw targets. |
| `AD_40Hz_Entrainment_Research_Paper_IEEE.txt/.docx` | Draft IEEE paper with placeholder results. Wrong subject count (13 vs. 35), fabricated preprocessing steps (ICA they didn't do), unimplemented methods. |
| `Comprehensive_Methodology_Closed_Loop_40Hz_Entrainment.txt/.docx` | Jan 2026 methodology. Wrong data loading (uses `read_raw_bids`), wrong PAC range assumptions, no temporal pipeline. |
| `STATUS_REPORT_Synopsys_Readiness.md` | Feb 5, 2026 progress report. Pre-pipeline-execution. 45% completion, old directory structure, wrong dataset assumptions. |

## Key Discrepancies: Proposal vs. Reality

| Aspect | Original Proposal | Actual Implementation |
|--------|------------------|----------------------|
| Architecture | GAT-Transformer (hundreds of K params) | EEGNet (1.5K) + causal TCN (31K) |
| Channels | 64-128 high-density | 7 frontal (10/20) |
| Subjects | "20-40 healthy adults, 18-35yo" | 35 elderly dementia patients |
| Sampling rate | 500-1000 Hz | 250 Hz |
| Control system | MIQP MPC with GUROBI | Threshold z-score with hysteresis |
| Static R^2 target | > 0.80 | 0.287 (achieved) |
| Temporal R^2 | > 0.80 for 5-10s ahead | 0.07 raw, 0.74 smoothed (ts=5, 1s ahead) |
| PAC range assumed | 0.001-0.3 | 0.0002-0.0046 (actual) |
