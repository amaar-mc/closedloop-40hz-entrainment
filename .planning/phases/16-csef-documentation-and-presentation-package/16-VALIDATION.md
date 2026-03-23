---
phase: 16
slug: csef-documentation-and-presentation-package
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-23
---

# Phase 16 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual grep + document audit (documentation-only phase — no code tests) |
| **Config file** | none |
| **Quick run command** | `grep -rn "73 feat\|61 spectral\|R² ≈ 0.25\|R² = 0.170" docs/ CSEF/` |
| **Full suite command** | `grep -rn "73 feat\|61 spectral\|R² ≈ 0.25\|R² = 0.170\|0\.254\|0\.240\|0\.278" docs/ CSEF/` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `grep -rn "73 feat\|61 spectral\|R² ≈ 0.25\|R² = 0.170" docs/ CSEF/`
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite must return zero matches in updated files (historical/comparison context excepted)
- **Max feedback latency:** 2 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | N/A | grep audit | `grep -rn "73 feat" <target-file>` | N/A | pending |

*Status: pending · green · red · flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements. No test framework install needed — grep is sufficient for document audits.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Every R² value traces to source file | Number accuracy | Semantic check | Cross-reference each R² in output doc against source map in 16-RESEARCH.md |
| Presentation stays under 13 pages | CSEF page limit | PDF rendering check | Generate PDF and count pages |
| docs/ and CSEF/ are in sync | Submission integrity | File comparison | `diff docs/poster/POSTER_BOARD_V6.md CSEF/Poster/POSTER_BOARD_V6.md` |
| Lab notebook entries are not backdated | Scientific integrity | Date review | Verify new entries are dated March 2026+ |

*All phase behaviors require manual verification — this is a documentation phase.*

---

## Validation Sign-Off

- [ ] All tasks have manual verify steps defined
- [ ] Sampling continuity: grep audit after every commit
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 2s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
