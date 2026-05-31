# Manuscript DOCX QA

## Artifact

[`MIT_URTC_MANUSCRIPT.docx`](MIT_URTC_MANUSCRIPT.docx) is a clean editable Word file generated from
[`MANUSCRIPT.md`](MANUSCRIPT.md). [`MIT_URTC_MANUSCRIPT.pdf`](MIT_URTC_MANUSCRIPT.pdf) is a
visually inspected PDF proof generated from the same audited manuscript source.

The older `MANUSCRIPT_CONTENT_REVIEW_DRAFT.docx` file was removed after Microsoft Word reported
unreadable content. Do not use that older filename.

The current proof follows the first-page structure shown in MIT's linked Word template: title,
author block, abstract, and keywords followed by a two-column paper body. The older 2025 guideline
PDF separately says that only the title should appear on the title page. Recheck this discrepancy
when MIT confirms the Fall 2026 instructions.

## Structural Checks

Verified on 2026-05-31:

- The DOCX is a valid transitional OOXML package and passes `unzip -t`.
- `python-docx` opens the generated file without error.
- Quick Look opens the DOCX without a recovery warning.
- The document contains two US Letter sections: a one-column title and abstract section followed by
  a continuous two-column manuscript section.
- Explicit text sizes range from 10 to 18 points; no explicit text size is below 10 points.
- All three result tables are present.
- The abstract contains 229 words and avoids mathematical symbols in the abstract text.
- The abstract and keyword labels use colons; no visible double-hyphen labels remain.
- All six manuscript references were checked against primary sources, including a standalone
  OpenNeuro dataset citation for `ds005048` version `1.0.1`.
- The active manuscript does not contain the stale historical `72.1%` or `82.6%` controller
  headlines.
- The controller replay was refreshed with `python3 scripts/pipeline/run_12feat_validation.py
  --no-train`; its checkpoint metadata and 35-trajectory table match the manuscript.
- The final ambiguity audit distinguishes stored-series future indexing from online PAC-feature
  availability. The manuscript does not imply that an end-to-end streaming estimator has been
  validated.
- The PDF proof is three US Letter pages, within the currently published five-page maximum.
- All three PDF pages were rendered to images and visually inspected.

## Layout Limitation

Quick Look renders the continuous section transition as a small square marker in its thumbnail
preview and does not faithfully preview the two-column flow. The marker is not present as manuscript
text in the DOCX package or in the inspected PDF proof.

LibreOffice is not installed in this environment, so the canonical DOCX-to-PNG renderer cannot run.
The clean DOCX package, Quick Look open check, and independently generated PDF proof were therefore
used for QA.

## Submission Conversion

After MIT URTC publishes or confirms the Fall 2026 template:

1. Recheck the author and affiliation block.
2. Compare the manuscript against the confirmed proceedings template.
3. Render or export from Microsoft Word to PDF.
4. Inspect every page and keep the complete paper within the five-page maximum.
