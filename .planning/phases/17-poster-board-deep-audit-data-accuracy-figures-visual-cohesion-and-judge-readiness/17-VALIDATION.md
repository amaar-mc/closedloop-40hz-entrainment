---
phase: 17
slug: poster-board-deep-audit-data-accuracy-figures-visual-cohesion-and-judge-readiness
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-07
---

# Phase 17 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual review + JSON cross-reference scripts |
| **Config file** | none — audit-only phase, no code changes |
| **Quick run command** | `python -c "import json; print('results accessible')"` |
| **Full suite command** | `python -m compileall src temporal temporal_multiscale` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Verify audit report markdown renders correctly
- **After every plan wave:** Cross-check all flagged numbers against source JSON
- **Before `/gsd:verify-work`:** All discrepancies categorized with source citations
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 17-01-01 | 01 | 1 | Data accuracy | manual + json cross-ref | Read results/*.json | N/A | pending |
| 17-01-02 | 01 | 1 | Figure audit | visual inspection | Read PDF + PNG files | N/A | pending |
| 17-02-01 | 02 | 1 | Visual cohesion | visual inspection | Read PDF + PPTX | N/A | pending |
| 17-02-02 | 02 | 1 | Judge-readiness | expert review | Read poster + docs | N/A | pending |

*Status: pending - all manual verification for audit-only phase*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements. This is an audit-only phase — no new code, tests, or frameworks needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Data accuracy | Every number matches source | Requires reading JSON + comparing to poster text | Cross-reference each claim against results/*.json |
| Figure quality | Figures readable and accurate | Requires visual inspection of PDF | Read PDF, check axes, labels, legends |
| Visual cohesion | Layout and design consistency | Subjective design assessment | Review PDF for font, color, spacing consistency |
| Judge-readiness | Poster survives judge scrutiny | Requires domain expertise | Evaluate from CSEF judge perspective |

*All phase behaviors are manual verification — this is an audit/review phase.*

---

## Validation Sign-Off

- [x] All tasks have manual verify procedures defined
- [x] Sampling continuity: every task has verification criteria
- [x] Wave 0 not needed — audit-only phase
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
