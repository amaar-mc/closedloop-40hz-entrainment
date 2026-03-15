---
phase: 06
slug: write-research-paper
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-15
---

# Phase 06 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual review + empirical validation (no pytest — this is a documentation phase) |
| **Config file** | `config.yaml` (runtime parameters for figure generation) |
| **Quick run command** | `python temporal/validate_code.py` |
| **Full suite command** | `python temporal_multiscale/comprehensive_submission_audit.py` |
| **Estimated runtime** | ~30 seconds (validate_code.py) |

---

## Sampling Rate

- **After every task commit:** Cross-check any numeric claim against source JSON/report files
- **After every plan wave:** Run full audit to confirm no regression in existing pipeline
- **Before `/gsd:verify-work`:** Manual review of all claims against validated sources
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | Figure generation | Code review | `python scripts/generate_paper_figures.py` | ❌ W0 | ⬜ pending |
| 06-02-01 | 02 | 1 | Paper content accuracy | Manual review | Cross-check vs results/*.json | N/A | ⬜ pending |
| 06-02-02 | 02 | 1 | Claim consistency | Manual diff | Compare vs CURRENT_METHODOLOGY.md | N/A | ⬜ pending |
| 06-03-01 | 03 | 2 | Supplementary materials | Manual review | Verify figures match JSON sources | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `scripts/generate_paper_figures.py` — horizon sweep figure + system block diagram generation
- [ ] `docs/paper/` directory — for paper output files

*Existing infrastructure covers pipeline validation; this phase adds figure generation scripts.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Claim accuracy | All numbers match source files | Semantic comparison needed | Cross-check abstract, results tables, and inline claims against results/*.json and RESULTS_REPORT.md |
| Figure accuracy | Horizon sweep figure matches JSON | Visual inspection | Compare generated figure data points against models/sweep_horizons_results.json |
| Metric consistency | Paper matches CURRENT_METHODOLOGY.md | Domain knowledge needed | Verify TCN patience=20, EEGNet loss=MSE, best epoch=53, subject counts |
| Citation accuracy | All citations traceable | Source verification | Cross-check against docs/research/05_Annotated_Bibliography_Sources.txt |
| No fabrication | Only validated repository data used | Ethics requirement | Spot-check 5 randomly selected numeric claims |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
