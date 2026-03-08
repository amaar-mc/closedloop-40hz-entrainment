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
| **Quick run command** | `python -m py_compile demo/app.py` |
| **Full suite command** | `streamlit run demo/app.py` (visual verification) |
| **Estimated runtime** | ~5 seconds (syntax check), manual for visual |

---

## Sampling Rate

- **After every task commit:** Run `python -m py_compile demo/app.py`
- **After every plan wave:** Run `streamlit run demo/app.py` — visual smoke test
- **Before `/gsd-verify-work`:** Full manual demo walkthrough of all 6 DEMO requirements
- **Max feedback latency:** 5 seconds (syntax check)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | DEMO-01 | smoke | `python -m py_compile demo/app.py` | ❌ W0 | ⬜ pending |
| 05-01-02 | 01 | 1 | DEMO-02 | smoke | `python -c "from src.simulator import EntrainmentSimulator, FatigueAwareSimulator; print('OK')"` | ✅ existing | ⬜ pending |
| 05-02-01 | 02 | 1 | DEMO-03 | smoke | `python -c "import demo.controllers; print('OK')"` | ❌ W0 | ⬜ pending |
| 05-02-02 | 02 | 1 | DEMO-04 | manual | Listen — requires human ear | ❌ manual | ⬜ pending |
| 05-03-01 | 03 | 2 | DEMO-05 | manual | Visual verification via `streamlit run demo/app.py` | ❌ manual | ⬜ pending |
| 05-03-02 | 03 | 2 | DEMO-06 | manual | Visual verification of speed differences | ❌ manual | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `demo/app.py` — main Streamlit app file (does not exist yet)
- [ ] `pip install streamlit sounddevice` — new dependencies not in `requirements.txt`
- [ ] Import path verification — confirm `sys.path.insert` pattern works from demo/ location

*This phase is primarily a UI/demo phase — most validation is manual/visual rather than automated.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dashboard launches with config controls | DEMO-01 | Visual UI | Run `streamlit run demo/app.py`, verify page loads with config panel |
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
