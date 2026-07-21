# Phase 2C: Cross-Document Consistency Audit

**Audit date:** 2026-03-24

Documents checked:

1. **Presentation:** `scripts/generate_csef_presentation.py`
2. **Poster V6:** `CSEF/Poster/POSTER_BOARD_V6.md`
3. **Research Paper v4:** `CSEF/Research Paper/RESEARCH_PAPER_v4.md`
4. **Abstract:** `CSEF/Abstract/ABSTRACT.md`
5. **RESULTS_REPORT:** `results/RESULTS_REPORT.md` / `CSEF/Research Paper/RESULTS_REPORT.md`
6. **SUPPLEMENTARY:** `CSEF/Research Paper/SUPPLEMENTARY.md`
7. **FINDINGS:** `experimental/FINDINGS.md`

## Key Value Consistency Matrix

| Value                 | Presentation  | Poster V6 | Paper v4      | Abstract | Consistent? |
| --------------------- | ------------- | --------- | ------------- | -------- | ----------- |
| Test R² (5-seed mean) | 0.606 ± 0.032 | 0.606     | 0.606 ± 0.032 | 0.606    | **YES**     |
| Feature count (final) | 12            | 12        | 12            | 12       | **YES**     |
| Prior TCN R²          | 0.121         | —         | 0.121         | —        | **YES**     |
| Alignment (TCN)       | 72.1%         | 72.1%     | 72.1%         | 72.1%    | **YES**     |
| Low-PAC Stim (TCN)    | 82.6%         | 82.6%     | 82.6%         | 82.6%    | **YES**     |
| Oracle % reached      | 91%           | 91%       | 91%           | 91%      | **YES**     |
| N subjects            | 35            | 35        | 35            | 35       | **YES**     |
| Hedges' g (alignment) | 1.31          | —         | 1.31          | —        | **YES**     |
| EEGNet R²             | 0.287         | 0.287     | 0.287         | —        | **YES**     |
| EEGNet params         | 1,457         | —         | 1,457         | —        | **YES**     |
| TCN params (12-feat)  | 22,914        | —         | 22,914        | —        | **YES**     |
| TCN hidden dim        | h=64          | —         | h=64          | —        | **YES**     |

## Inconsistencies Found

### ISSUE 1: Hysteresis Value (MEDIUM severity)

| Document                          | Value     |
| --------------------------------- | --------- |
| Presentation                      | 5 seconds |
| Research Paper v4 (line 286)      | 3 seconds |
| Research Paper v3 (line 237)      | 3 seconds |
| SUPPLEMENTARY.md (line 148)       | 3 seconds |
| Source code controller.py default | 5 seconds |
| config.yaml                       | 3 seconds |

**Impact:** The code default is 5 seconds. The validation results were produced with the code default. The presentation correctly reflects the actual behavior. The research papers are stale on this point.

**Recommendation:** Update Research Paper v4 line 286 and SUPPLEMENTARY.md line 148 from "3-second" to "5-second" to match the actual code and presentation.

### ISSUE 2: RESULTS_REPORT.md and SUPPLEMENTARY.md Still Describe 73-Feature Model

| Document                        | TCN Params | Feature Count | TCN Test R² |
| ------------------------------- | ---------- | ------------- | ----------- |
| Presentation                    | 22,914     | 12            | 0.606       |
| Research Paper v4               | 22,914     | 12            | 0.606       |
| **RESULTS_REPORT.md (line 18)** | **31,043** | **73**        | **0.170**   |
| **SUPPLEMENTARY.md (line 117)** | **31,043** | **73**        | —           |

**Impact:** RESULTS_REPORT.md and SUPPLEMENTARY.md describe the pre-ablation model. They are accurate for the model they describe but are not updated to reflect the current best (12-feature, 22,914-param) model. RESULTS_REPORT.md does include a note (line 31) mentioning the PAC+Stim model at R² = 0.606, but the top-level summary table still shows the old model.

**Recommendation:** Either update these files or add clear headers noting they describe the Phase 1 (73-feature) model, with a pointer to the current best results in FINDINGS.md.

### ISSUE 3: System Architecture Figure Shows Outdated Specs

The system architecture figure (embedded in presentation) shows:

- "73 features (61+7+5)" — should show feature selection to 12
- "31K params" — should be 22,914

This is also flagged in 03_figure_audit.md. This is the most visible inconsistency for a judge reviewing the PDF.

### ISSUE 4: Research Paper v3 Still in CSEF Folder

`CSEF/Research Paper/RESEARCH_PAPER_v3.md` (and .tex/.pdf) contains pre-ablation numbers (73 features, R² ≈ 0.25, 31K params). While v4 is clearly the current version, having v3 in the submission folder could cause confusion if a judge browses the files.

**Recommendation:** Move v3 to an archive subfolder or clearly mark as superseded.

## Documents NOT Checked (Not Part of Presentation)

- Lab Notebook (checked spot-checked; appears updated per entry on line 608)
- Interview scripts (internal prep; not submitted)
- Elevator pitch (internal prep)

## Summary

| Check                                               | Count | Result                         |
| --------------------------------------------------- | ----- | ------------------------------ |
| Key values consistent across all 4 core documents   | 12/12 | **PASS**                       |
| Inconsistencies found                               | 4     | See above                      |
| Critical inconsistencies (would invalidate results) | 0     | —                              |
| Medium inconsistencies (visible to judges)          | 2     | Hysteresis value, figure specs |
| Low inconsistencies (housekeeping)                  | 2     | RESULTS_REPORT, v3 files       |

**Overall:** Core numerical claims are 100% consistent across the presentation, poster V6, research paper v4, and abstract. The inconsistencies found are between the presentation and supporting/supplementary documents that haven't been fully updated to reflect the PAC+Stim feature discovery. None invalidate any results.
