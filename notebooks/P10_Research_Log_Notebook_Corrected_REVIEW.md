# P10 Corrected Notebook Review Bundle

This sidecar explains what changed from the preserved legacy notebook, what still needs human editorial judgment, and how the corrected notebook should be approved before any manual PDF export.

## Bundle Files

- `notebooks/P10_Research_Log_Notebook_Corrected.md` - approval-anchored review candidate used by the existing PDF generator contract
- `notebooks/P10_Research_Log_Notebook_Corrected_REVIEW.md` - this review checklist and packaging sidecar
- `notebooks/P10_Research_Log_Notebook_Corrected_EVIDENCE_MAP.md` - whitelist for date-sensitive claims, figures, and corrections
- `notebooks/P10_Lab_Notebook_FINAL.md` - preserved legacy notebook source
- `notebooks/P10_Lab_Notebook_FINAL.pdf` - preserved legacy rendered PDF
- `notebooks/generate_notebook_pdf.py` - existing manual export utility

## Change Log

| Date | Author | Legacy notebook issue | Corrected review-bundle change | Status |
| --- | --- | --- | --- | --- |
| 2026-03-08 | OpenCode | Visible timeline started in December private-prep mode. | Re-anchored the corrected candidate to the approval-era fallback start of `January 15, 2026` and compressed earlier work into background framing plus gap notes. | ready for review |
| 2026-03-08 | OpenCode | Legacy notebook blended chronology, errata, and final interpretation too tightly. | Added `notebooks/P10_Research_Log_Notebook_Corrected_EVIDENCE_MAP.md` so retained dates, figures, and metrics can be checked against repository evidence before signoff. | ready for review |
| 2026-03-08 | OpenCode | Earlier wording blurred the Feb 21 replay-framework work with the final Feb 26 TCN replay result. | Rewrote the corrected notebook so Feb 21 stays infrastructure-focused and the locked `72.1%` controller result lands on Feb 26. | ready for review |
| 2026-03-08 | OpenCode | Packaging path was confusing because docs navigation pointed to a missing notebook location. | Added a docs pointer page and explicit instructions that manual PDF export happens only after review approval. | ready for review |

## Unresolved Questions

- No tighter in-repo approval artifact has been found yet, so `January 15, 2026` remains a documented fallback anchor rather than a claim about a specific approval document.
- The corrected notebook intentionally keeps only one embedded figure by default. Any additional visual should be justified as a pivotal-day artifact before approval.
- If any claim in `notebooks/P10_Lab_Notebook_FINAL.md` is still desired but does not appear in `notebooks/P10_Research_Log_Notebook_Corrected_EVIDENCE_MAP.md`, it should stay out of the corrected notebook until evidence is cited.

## Reviewer Checklist

- [ ] Original notebook artifacts remain untouched while this review bundle evolves.
- [ ] The corrected notebook stays anchored to the approval anchor rather than the earlier December draft timeline.
- [ ] The change log above fairly describes the major differences between the legacy notebook and the corrected review candidate.
- [ ] Every retained claim, date, and figure has an evidence-map row before final signoff.
- [ ] The docs pointer in `docs/notebook/README.md` makes the review bundle easy to find from `docs/INDEX.md`.
- [ ] The final prose feels concise and judge readability stays higher than the legacy paper-like draft.

## Human Chronology and Fairness Review

- [ ] Active-day entries only state what was knowable on that date.
- [ ] Gap notes are used instead of fabricated day-by-day backfill.
- [ ] No hindsight narration reveals later conclusions too early.
- [ ] Approval anchor treatment is fair, explicit, and consistent.
- [ ] Sensitive moments cross-check cleanly against `notebooks/P10_Research_Log_Notebook_Corrected_EVIDENCE_MAP.md`.
- [ ] Any rewritten metric or figure language matches repository evidence.
- [ ] Sparse visuals are limited to pivotal days and transitions rather than used as filler.
- [ ] Overall flow feels concise, judge readability is strong, and the result does not read like a polished paper rewrite.

## Manual PDF Export After Approval

Manual PDF export happens only after the corrected notebook and sidecars are approved.

1. Confirm `notebooks/P10_Research_Log_Notebook_Corrected.md` is the approved source.
2. Confirm remaining review notes in `notebooks/P10_Research_Log_Notebook_Corrected_REVIEW.md` are either resolved or intentionally documented.
3. Run `source venv/bin/activate && python notebooks/generate_notebook_pdf.py` from the repository root.
4. Verify the output file `P10_Research_Log_Notebook_Corrected.pdf` is created in `notebooks/`.
5. Spot-check the generated PDF for missing sections, broken tables, missing assets, or layout regressions before submission.
