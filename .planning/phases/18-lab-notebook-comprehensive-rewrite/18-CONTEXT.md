# Phase 18: Lab Notebook Comprehensive Rewrite - Context

**Gathered:** 2026-04-09
**Status:** Ready for planning
**Source:** Multi-agent audit findings (5 Opus agents)

<domain>
## Phase Boundary

Rewrite both lab notebook files to score 95+ on all audit dimensions. The notebook must be consistent with the printed CSEF poster, use correct code from the actual codebase, sound human (not AI), and demonstrate clinical depth appropriate for Medicine & Physiology judges.

Files in scope:
- `CSEF/Lab Notebook/P10_Lab_Notebook_VFINAL.md` (original, Jan 15 - March 22)
- `CSEF_presentation/notebook/v1_lab_notebook_extension.md` (extension, March 24 - April 8)
- `CSEF_presentation/notebook/generate_notebook_pdf.py` (PDF generator)
- `CSEF_presentation/notebook/P10_Lab_Notebook_COMPLETE.pdf` (output)

Files that are FROZEN (cannot change):
- `CSEF_FINAL/CSEF_FINAL.pdf` (printed poster)
- `CSEF/Presentation/CSEF_2026_Presentation.pdf` (submitted 13-page presentation)

</domain>

<decisions>
## Implementation Decisions

### Audit Scores to Fix (current -> target)

| Dimension | Current | Target |
|---|---|---|
| AI Voice (overall) | 66 | 95+ |
| - Tonal Consistency | 60 | 95+ |
| - Imperfection Quotient | 55 | 95+ |
| Judge Perspective (overall) | 79 | 95+ |
| - Clinical Relevance | 68 | 95+ |
| Technical Depth (overall) | 74 | 95+ |
| - Missing Content | 62 | 95+ |
| - Code-Notebook Alignment | 72 | 95+ |
| Poster Alignment | 68 | 95+ |

### Locked Decisions
- All code snippets MUST match actual codebase parameters (tau_e=0.004, onset_tau_sec=1.5, etc.)
- Hysteresis is 5.0 seconds in code. Poster says 3s. Notebook must say 5s and note the discrepancy.
- TCN params: 31,043 (73-feature), 22,914 (12-feature h=64), 5,154 (12-feature h=32). Each must be labeled clearly.
- Controller results (72.1% alignment) were from 73-feature model. Must be stated explicitly.
- Oracle proximity: 91% consistently.
- Em-dashes: zero. Use -- throughout.
- No AI voice patterns: no parallel structure, no corporate language, no hedging.
- Add genuine imperfections: corrections, failed attempts, confusion, typos.
- Add clinical context: molecular pathways, regulatory discussion, Soula 2023 engagement.
- Horizon sweep in extension must use correct persistence values from horizon_sweep_pac_stim.json.
- Fortunato reference [8] must be included.

### Claude's Discretion
- Exact wording of humanized entries
- Where to place corrections and UPDATE notes
- Which code snippets to include from actual codebase
- How to structure the clinical context entry

</decisions>

<deferred>
## Deferred Ideas

None -- this phase covers the complete notebook rewrite.

</deferred>

---

*Phase: 18-lab-notebook-comprehensive-rewrite*
*Context gathered: 2026-04-09 via audit findings*
