---
phase: 13
slug: caregiver-app-and-pilot-preparation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | python -m py_compile + manual Streamlit verification |
| **Config file** | none — app validates via browser |
| **Quick run command** | `python -m py_compile caregiver_app.py` |
| **Full suite command** | `python -m compileall caregiver_app/ && streamlit run caregiver_app.py --server.headless true` |
| **Estimated runtime** | ~5 seconds (compile), manual for UI |

---

## Sampling Rate

- **After every task commit:** Run `python -m py_compile` on changed files
- **After every plan wave:** Run full compile + smoke test
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 13-01-01 | 01 | 1 | APP-01, APP-02 | compile+manual | `python -m py_compile caregiver_app.py` | ❌ W0 | ⬜ pending |
| 13-02-01 | 02 | 2 | APP-03, APP-04, APP-05 | compile+manual | `python -m py_compile caregiver_app.py` | ❌ W0 | ⬜ pending |
| 13-03-01 | 03 | 2 | PRES-01, PRES-02, PRES-03, PRES-04 | file existence | `ls docs/flyer.pdf` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] No test framework needed — validation is compile checks + manual browser testing
- [ ] Model files verified present before deployment

*Existing infrastructure covers compile-level requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| QR code scans to correct URL | APP-01 | Requires phone camera | Scan with phone, verify URL opens app |
| Audio plays 40 Hz stimulus | APP-03 | Requires browser audio | Start session, verify sound plays |
| Session workflow is self-explanatory | APP-01 | UX judgment | Have someone unfamiliar try the app |
| Flyer is print-ready | PRES-01 | Visual quality check | Print at actual size, verify readability |
| Google Form collects responses | PRES-04 | External service | Submit test response, verify in Sheets |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
