---
phase: 5
slug: real-time-eeg-visualization-and-audio-stimulation-demo
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-08
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | No formal test framework (per AGENTS.md — module self-tests and smoke runs) |
| **Config file** | None — Wave 0 installs dependencies |
| **Quick run command** | `python -m py_compile demo.py` |
| **Full suite command** | `streamlit run demo.py` (visual verification) |
| **Estimated runtime** | ~5 seconds (syntax check), manual for visual |

---

## Sampling Rate

- **After every task commit:** Run `python -m py_compile demo.py`
- **After every plan wave:** Run `streamlit run demo.py` — visual smoke test
- **Before `/gsd-verify-work`:** Full manual demo walkthrough of all 6 DEMO requirements
- **Max feedback latency:** 5 seconds (syntax check)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-T1 | 01 | 1 | DEMO-01, DEMO-02, DEMO-03, DEMO-05, DEMO-06 | smoke | `python -m py_compile demo.py` | ❌ W0 | ⬜ pending |
| 05-01-T2 | 01 | 1 | DEMO-04 | smoke | `python -c "import sounddevice; print('OK')"` | ❌ W0 | ⬜ pending |
| 05-01-T3 | 01 | 1 | ALL | manual | `streamlit run demo.py` — full walkthrough | ❌ manual | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `demo.py` — main Streamlit app file (does not exist yet)
- [ ] `pip install streamlit sounddevice` — new dependencies not in `requirements.txt`
- [ ] Import path verification — confirm `sys.path.insert` pattern works from repo root

*This phase is primarily a UI/demo phase — most validation is manual/visual rather than automated.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dashboard launches with config controls | DEMO-01 | Visual UI | Run `streamlit run demo.py`, verify page loads with config panel |
| 40 Hz clicks play through speakers | DEMO-04 | Audio output | Run demo, enable stim, verify clicks audible, test mute button |
| Four stacked PAC panels with color bands | DEMO-05 | Visual layout | Run demo, start simulation, verify 4 panels with green/red bands |
| Speed control affects animation rate | DEMO-06 | Timing behavior | Run demo at 1x and 10x, verify visible speed difference |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
