---
phase: 11
slug: real-time-inference-pipeline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-20
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python module self-tests + manual verification scripts |
| **Config file** | none — project uses ad-hoc testing |
| **Quick run command** | `python -m py_compile webapp/streaming.py && python webapp/test_streaming_parity.py` |
| **Full suite command** | `python webapp/test_streaming_parity.py && python webapp/test_simulated_session.py` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m py_compile` on changed files
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | RTINF-01 | integration | `python webapp/test_streaming_parity.py` | ❌ W0 | ⬜ pending |
| 11-01-02 | 01 | 1 | RTINF-02 | integration | `python webapp/test_simulated_session.py` | ❌ W0 | ⬜ pending |
| 11-02-01 | 02 | 2 | RTINF-03 | manual | BLE hardware test | N/A | ⬜ pending |
| 11-02-02 | 02 | 2 | RTINF-04 | unit | `python webapp/test_model_registry.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `webapp/test_streaming_parity.py` — verify StreamingFeatureExtractor matches offline within 1e-4
- [ ] `webapp/test_simulated_session.py` — verify full simulated session produces PAC predictions
- [ ] `webapp/test_model_registry.py` — verify model swap via config flag
- [ ] `pip install brainflow` — BrainFlow not currently installed

*These stubs are created during Wave 1 alongside the implementation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Muse 2 BLE connection | RTINF-03 | Requires physical hardware | Pair Muse 2, run `python webapp/test_muse_connection.py`, verify data streams |
| Real-time PAC display | RTINF-02 | Visual confirmation | Start simulated session, verify PAC values print to terminal every 2s |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
