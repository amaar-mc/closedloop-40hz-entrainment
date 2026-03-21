---
phase: 12
slug: architecture-comparison-study
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python scripts with assertion checks + result file validation |
| **Config file** | none — scripts produce JSON/markdown artifacts |
| **Quick run command** | `python -m py_compile temporal_multiscale/model_comparison.py` |
| **Full suite command** | `python temporal_multiscale/model_comparison.py --dry-run && python temporal_multiscale/ablation_study.py --dry-run` |
| **Estimated runtime** | ~10 seconds (dry-run), ~30 min (full training) |

---

## Sampling Rate

- **After every task commit:** Run `python -m py_compile` on changed files
- **After every plan wave:** Verify output artifacts exist (JSON results, markdown tables)
- **Before `/gsd:verify-work`:** Full comparison table and ablation table must exist as files
- **Max feedback latency:** 10 seconds (compilation check)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | RSRCH-01 | integration | check results JSON exists | ❌ W0 | ⬜ pending |
| 12-02-01 | 02 | 1 | RSRCH-02 | integration | check ablation JSON exists | ❌ W0 | ⬜ pending |
| 12-02-02 | 02 | 1 | RSRCH-03 | integration | check multi-seed JSON exists | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Verify both datasets exist (4ch and 7ch multiscale temporal)
- [ ] Verify existing TCN checkpoints loadable

*Existing infrastructure covers dataset requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Comparison table readable | RSRCH-01 | Visual formatting | Review markdown table in results file |
| Ablation table interpretable | RSRCH-02 | Scientific validity | Verify each component removal degrades R² |
| Multi-seed variance reasonable | RSRCH-03 | Statistical judgment | Check std < mean for R² values |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
