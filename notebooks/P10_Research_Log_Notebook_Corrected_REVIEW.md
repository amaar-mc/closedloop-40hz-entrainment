# P10 Corrected Notebook Review Bundle

This sidecar tracks what changed, what still needs human judgment, and how to package the corrected notebook after approval.

## Bundle Files

- `notebooks/P10_Research_Log_Notebook_Corrected.md`
- `notebooks/P10_Research_Log_Notebook_Corrected_REVIEW.md`
- `notebooks/P10_Research_Log_Notebook_Corrected_EVIDENCE_MAP.md`
- `notebooks/P10_Lab_Notebook_FINAL.md`
- `notebooks/P10_Lab_Notebook_FINAL.pdf`
- `notebooks/generate_notebook_pdf.py`

## Change Log

| Date | Author | Change | Status |
| --- | --- | --- | --- |
| 2026-03-08 | OpenCode | Created corrected notebook scaffold at the generator contract path. | open |
| 2026-03-08 | OpenCode | Added review sidecar for chronology, fairness, and packaging signoff. | open |
| 2026-03-08 | OpenCode | Added evidence-map scaffold for claim/date/figure tracing. | open |

## Unresolved Questions

- Is there stronger approval evidence than the current `January 15, 2026` fallback anchor?
- Which 3-4 days deserve sparse visuals after the chronology rewrite is complete?
- Are any claims in the legacy notebook still unsupported after the evidence map is populated?

## Reviewer Checklist

- [ ] Original notebook artifacts remain untouched while this review bundle evolves.
- [ ] The corrected notebook stays anchored to the approval anchor rather than the earlier December draft timeline.
- [ ] Every retained claim, date, and figure has an evidence-map row before final signoff.
- [ ] Sparse visuals are limited to pivotal days and transitions.
- [ ] The final prose feels concise and judge readability stays higher than the legacy paper-like draft.

## Human Chronology and Fairness Review

- [ ] Active-day entries only state what was knowable on that date.
- [ ] Gap notes are used instead of fabricated day-by-day backfill.
- [ ] No hindsight narration reveals later conclusions too early.
- [ ] Approval anchor treatment is fair, explicit, and consistent.
- [ ] Any rewritten metric or figure language matches repository evidence.

## Manual PDF Export After Approval

Manual PDF export happens only after the corrected notebook and sidecars are approved.

1. Confirm `notebooks/P10_Research_Log_Notebook_Corrected.md` is the approved source.
2. Confirm review notes are resolved in `notebooks/P10_Research_Log_Notebook_Corrected_REVIEW.md`.
3. Run `python notebooks/generate_notebook_pdf.py` from the repository root.
4. Verify the output file `P10_Research_Log_Notebook_Corrected.pdf` is created in `notebooks/`.
5. Spot-check the generated PDF for missing sections, broken tables, or layout regressions before submission.
