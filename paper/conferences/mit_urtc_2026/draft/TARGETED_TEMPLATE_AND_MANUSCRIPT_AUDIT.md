# MIT URTC Targeted Template and Manuscript Audit

**Audited:** 2026-06-25  
**Artifacts:** `MANUSCRIPT.md`, `MIT_URTC_MANUSCRIPT.docx`, `MIT_URTC_MANUSCRIPT_REPORTLAB_PROOF.pdf`,
and the stale pre-revision `MIT_URTC_MANUSCRIPT.pdf`  
**Verdict:** source text, DOCX, and text-proof layout are submission-ready; the Microsoft Word PDF
export, eligibility, and authenticated 2026 portal details remain stop-ship checks.

## Official-Source Status

Live checks established the following:

- `https://cmt3.research.microsoft.com/URTC2026` exists and requires authentication.
- IEEE Boston lists URTC 2026 for October 9-11, 2026.
- MIT's public homepage and submission page still show the 2025 deadline and link the 2025-labeled
  guideline PDF.
- MIT's public Word-template URL still returns the same file downloaded on 2026-05-31. SHA-256:
  `c8e86eabd52a42f4326fd87b9af0269624c6d72d11ea4adc5e6ac4c626b123ed`.
- The 2026 paper deadline, camera-ready deadline, track list, presenter limit, and author-registration
  rules were not visible in public official material and must be checked inside CMT.

## Requirement and Template Compliance

| Check                             | Verdict                         | Evidence                                                                                                                                                                               |
| --------------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| English manuscript                | PASS                            | Full manuscript is in English.                                                                                                                                                         |
| Five-page maximum                 | NEEDS RECHECK                   | The current ReportLab proof is five US Letter pages. The Microsoft Word PDF predates the 2026-06-25 abstract revision and must be re-exported from the current DOCX before submission. |
| Single-spaced                     | PASS                            | Body styles use single spacing.                                                                                                                                                        |
| Minimum 10-point manuscript text  | PASS                            | Body, abstract, tables, captions, and references are at least 10 points; the 24-point title and 11-point author style match the template hierarchy.                                    |
| Abstract no longer than 500 words | PASS                            | Abstract is 245 words.                                                                                                                                                                 |
| MIT-provided Word template        | PASS                            | Generator loads a Word-converted working copy of MIT's strict-OOXML template and retains its styles and geometry.                                                                      |
| Template geometry                 | PASS                            | 0.75-inch top, 1-inch bottom, approximately 0.63-inch side margins, two columns, 0.25-inch column gap.                                                                                 |
| Template guidance removed         | PASS                            | No sample title, instructional text, red warning, or example reference remains.                                                                                                        |
| Figures and tables                | PASS                            | Two tables and one figure; no figure/table duplicates the same result block.                                                                                                           |
| Figure labels                     | PASS                            | Figure-internal text follows the template's 8-point figure-label instruction; the caption is 10 points.                                                                                |
| References                        | PASS                            | Eight numbered references; no duplicate numbering; primary or appropriate sources support the claims.                                                                                  |
| Word/PDF integrity                | DOCX PASS; PDF RE-EXPORT NEEDED | DOCX passes `unzip -t`. The current text-proof PDF is unencrypted and has no JavaScript; the Word-exported PDF must be regenerated from the revised DOCX before submission.            |
| High-school paper eligibility     | STOP-SHIP                       | The manuscript lists only a high-school affiliation. A qualifying university relationship is not documented in the repository.                                                         |
| 2026 portal metadata              | STOP-SHIP                       | Deadline, track, presenter limit, and author-registration rules require authenticated CMT verification.                                                                                |

The public 2025 guideline PDF says only the title should appear on the title page, while the linked
Word template uses a full-width title, author block, abstract, and keywords followed by a two-column
body. The manuscript follows the more specific Word template requested for this submission.

## Scientific and ML Audit

| Area                           | Verdict                | Finding                                                                                                                                                                                                                                                                                              |
| ------------------------------ | ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Participant leakage            | PASS                   | Train/validation/test contain 24/5/6 disjoint participants.                                                                                                                                                                                                                                          |
| Stored-series target ordering  | PASS                   | Every target index is five steps after the sequence endpoint.                                                                                                                                                                                                                                        |
| Normalization leakage          | PASS                   | Stored feature and target scalers reproduce from training data only.                                                                                                                                                                                                                                 |
| Event-summary PAC availability | FAIL FOR STREAMING USE | Complete-event PAC assigned to early windows includes later samples from the same event. The paper now treats this only as a retrospective benchmark.                                                                                                                                                |
| Feature selection independence | SUSPECT                | The 12-feature representation was selected using performance on the fixed held-out test split. The paper labels the ablation exploratory and does not call the test estimate an unbiased final model-selection result.                                                                               |
| Initialization robustness      | PARTIAL                | Five seeds give mean event-summary test R-squared 0.606, sample SD 0.033, range 0.558-0.647, but use one fixed participant split.                                                                                                                                                                    |
| Corrected-target model value   | NEGATIVE RESULT        | Under backward-looking PAC, TCN R-squared is 0.212 and Ridge is 0.216. The paper does not claim nonlinear superiority.                                                                                                                                                                               |
| PAC physiological validity     | SUSPECT                | No surrogate correction or phase-clustering debiasing was run; 38-42 Hz overlaps the stimulation frequency and sensor-level gamma is vulnerable to myogenic/ocular artifacts. The paper frames PAC as a retrospective EEG-derived target, not proof of physiological coupling or treatment response. |
| Controller replay independence | FAIL AS VALIDATION     | Replay uses all 35 trajectories, nominal recorded stimulation context, and no counterfactual physiological response. The paper calls it an offline diagnostic.                                                                                                                                       |
| Controller outcome             | MIXED                  | Predictive replay raises low-PAC stimulation coverage from 51.7% to 73.8% but lowers the above-median-PAC rest rate from 77.3% to 50.7%; balanced alignment is lower than reactive control.                                                                                                          |

## Surgical Revisions Applied

1. Rebuilt the DOCX from MIT's linked template instead of a generic blank document.
2. Corrected margins, title hierarchy, heading numbering, column geometry, reference styling, and
   Word-export workflow.
3. Removed the single-seed horizon-sweep table because it was secondary to the target-definition
   result and depended on the weaker complete-event target.
4. Removed the benchmark table that duplicated Figure 1; the exact values remain in the result text
   and figure.
5. Moved Figure 1 into the Results section, removed its internal repository filename, and kept the
   figure and caption together.
6. Fixed numbered lists that previously continued across sections, table rows that could split, a
   duplicated figure label, and duplicated reference numbers.
7. Added Hipp and Siegel's primary EEG artifact study to support the gamma-band cranial/ocular
   artifact warning.
8. Preserved the negative corrected-target result and mixed controller result instead of replacing
   them with older stronger metrics from incompatible checkpoints.
9. Rewrote the title, abstract, introduction, dataset opening, PAC rationale, and replay-language
   sections to explain why PAC was used, why low-PAC replay is a timing objective rather than a
   therapy claim, and why the backward-looking PAC audit matters.
10. Removed the previously flagged weak shorthand and clinical-style replay framing from the active
    manuscript and immediate venue drafts.

## Verification Evidence

- `results/rigor_audit/models/leakage_check.py`: all stored-series split, ordering, and scaler checks
  passed; the script separately warns that online PAC availability is not established.
- Five declared event-summary seeds recomputed to mean `0.605953`, sample SD `0.032564`, and range
  `0.557862-0.646583`.
- Controller alignment arithmetic reproduces from low-PAC stimulation coverage and
  above-median-PAC rest rate.
- DOCX structure: 2 sections, 90 paragraphs, 2 tables, 1 embedded figure, 8 reference paragraphs.
- Current proof PDF: ReportLab creator, five pages, US Letter, no JavaScript, and contains the
  revised title and abstract.
- Stale Word PDF: `MIT_URTC_MANUSCRIPT.pdf` is the 2026-06-23 Microsoft Word export and still
  contains the old title and weak PAC/replay phrasing. It must be regenerated from the current DOCX
  and visually inspected before upload.

## Final Submission Gate

The paper should be submitted only after the author confirms a genuine qualifying university
relationship and checks the authenticated `URTC2026` CMT instructions. No further scientific
claim expansion is justified by the current evidence. If new experiments are run, the highest-value
addition is repeated participant-level splits on the backward-looking target, not more analysis of
the complete-event benchmark.
