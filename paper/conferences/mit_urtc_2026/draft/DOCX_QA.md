# Manuscript DOCX QA

## Artifact

[`MIT_URTC_MANUSCRIPT.docx`](MIT_URTC_MANUSCRIPT.docx) is a clean editable Word file generated from
[`MANUSCRIPT.md`](MANUSCRIPT.md) and includes the 2026-06-25 manuscript-level title, abstract,
introduction, dataset-framing, and replay-language revision.
[`MIT_URTC_MANUSCRIPT_REPORTLAB_PROOF.pdf`](MIT_URTC_MANUSCRIPT_REPORTLAB_PROOF.pdf) is a
lower-fidelity text proof generated from the same source. [`MIT_URTC_MANUSCRIPT.pdf`](MIT_URTC_MANUSCRIPT.pdf)
is the 2026-06-23 Microsoft Word export and must be re-exported from the updated DOCX before
submission.

The older `MANUSCRIPT_CONTENT_REVIEW_DRAFT.docx` file was removed after Microsoft Word reported
unreadable content. Do not use that older filename.

The generator now loads a transitional Microsoft Word conversion of MIT's linked strict-OOXML
template, removes all template guidance text, and preserves the template's US Letter geometry,
24-point title style, author block, continuous two-column body, heading hierarchy, and numbering.
The public 2025 guideline PDF separately says that only the title should appear on the title page;
the manuscript follows the more specific linked Word template.

## Structural Checks

Verified on 2026-06-25 for the DOCX/source text; page-level Word PDF inspection must be repeated
after Microsoft Word re-export:

- The DOCX is a valid transitional OOXML package and passes `unzip -t`.
- `python-docx` opens the generated file without error.
- The document contains two US Letter sections: a one-column title and abstract section followed by
  a continuous two-column manuscript section.
- Margins match the template: 0.75 inch top, 1 inch bottom, and approximately 0.63 inch left/right;
  the two-column gap is 0.25 inch.
- Manuscript text sizes range from 10 to 24 points; body, captions, tables, and references are at
  least 10 points. Figure-internal labels follow the template's 8-point figure-label instruction.
- Both result tables and the target-definition stress-test figure are present.
- The abstract contains 245 words and avoids mathematical symbols in the abstract text.
- The abstract and keyword labels use colons; no visible double-hyphen labels remain.
- All eight manuscript references were checked against primary or appropriate sources, including a
  standalone OpenNeuro dataset citation for `ds005048` version `1.0.1` and a PAC-interpretation
  caveat source. A primary EEG study now supports the gamma-band ocular/myogenic-artifact warning.
- The active manuscript does not contain the stale historical `72.1%` or `82.6%` controller
  headlines.
- The controller replay was refreshed with `python3 scripts/pipeline/run_12feat_validation.py
--no-train`; its 35-trajectory table matches the manuscript.
- The final ambiguity audit distinguishes stored-series future indexing from online PAC-feature
  availability. The manuscript does not imply that an end-to-end streaming estimator has been
  validated.
- The revised manuscript reports the backward-looking PAC stress test separately from the
  event-summary benchmark and does not present it as a validated streaming estimator.
- Numbered lists restart correctly at 1 in each section.
- The figure and caption remain together, tables do not split across pages, references are numbered
  once, and no template guidance text remains.
- The ReportLab proof is five US Letter pages, within the currently published five-page maximum,
  and contains the revised title and abstract text.
- The previous Microsoft Word PDF metadata reports Microsoft Word as creator and the file is tagged,
  but it predates the 2026-06-25 abstract revision.

## Remaining Submission Checks

1. Confirm the qualifying university relationship for the high-school paper track.
2. Confirm the 2026 deadline, track, presenter limit, and author-registration rules in CMT.
3. Re-export the current DOCX from Microsoft Word, then repeat the five-page visual inspection.
