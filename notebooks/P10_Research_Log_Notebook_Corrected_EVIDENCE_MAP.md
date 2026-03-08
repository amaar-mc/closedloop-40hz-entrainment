# P10 Corrected Notebook Evidence Map

Use this file to trace every retained or rewritten claim, date anchor, and figure in the corrected notebook.

## Disposition Legend

- `keep` - retain as-is because the claim already matches repository evidence
- `rewrite` - keep the topic but rewrite the wording or timing
- `drop` - remove because the claim is unsupported, stale, or misleading
- `gap note` - replace unsupported daily detail with a shorter supported span note

## Entry Templates

| Entry ID | Entry Type | Notebook Target | Claim / Date / Figure | Source Path | Source Evidence | Disposition | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ANCHOR-01 | date | Approval Anchor | `January 15, 2026` default approval-era start | `.planning/phases/04-finalize-lab-notebook/04-CONTEXT.md` | Locked phase decision uses Jan 15 unless stronger proof appears. | keep | Replace only if stronger approval evidence is found. |
| CHRON-01 | claim | Active-Day Chronology | First populated entry after approval anchor | `notebooks/P10_Lab_Notebook_FINAL.md` | Legacy notebook content to be re-anchored and rewritten. | rewrite | Later plans should split this into day-specific rows. |
| FIG-01 | figure | Sparse Figure Placement | Placeholder for first pivotal figure | `docs/submission/reports/PROJECT_ACHIEVEMENT_REPORT.md` | Use only after verifying figure relevance and chronology fit. | gap note | Convert to a real figure row only when a specific artifact is selected. |

## Review Notes

- Add one row per claim, date-sensitive statement, or figure before it appears in the corrected notebook.
- Prefer repository paths over memory-based explanations.
- If evidence is thin, use `gap note` or `drop` instead of inventing detail.
