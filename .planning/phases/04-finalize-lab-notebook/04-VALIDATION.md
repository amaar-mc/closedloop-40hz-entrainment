---
phase: 4
slug: finalize-lab-notebook
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-08
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | other - ad hoc Python checks plus human review |
| **Config file** | none - Wave 0 creates `scripts/verify_notebook_finalization.py` |
| **Quick run command** | `python scripts/verify_notebook_finalization.py --quick` |
| **Full suite command** | `python scripts/verify_notebook_finalization.py --full` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python scripts/verify_notebook_finalization.py --quick`
- **After every plan wave:** Run `python scripts/verify_notebook_finalization.py --full`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | FNL-02 | smoke | `python scripts/verify_notebook_finalization.py --check preservation` | ❌ W0 | ⬜ pending |
| 04-01-02 | 01 | 1 | FNL-06 | smoke | `python scripts/verify_notebook_finalization.py --check checklist` | ❌ W0 | ⬜ pending |
| 04-02-01 | 02 | 2 | FNL-01 | docs-lint | `python scripts/verify_notebook_finalization.py --check chronology` | ❌ W0 | ⬜ pending |
| 04-02-02 | 02 | 2 | FNL-03 | docs-lint | `python scripts/verify_notebook_finalization.py --check evidence` | ❌ W0 | ⬜ pending |
| 04-03-01 | 03 | 3 | FNL-04 | manual-review-backed smoke | `python scripts/verify_notebook_finalization.py --check checklist` | ❌ W0 | ⬜ pending |
| 04-03-02 | 03 | 3 | FNL-05 | smoke | `python scripts/verify_notebook_finalization.py --check packaging` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `scripts/verify_notebook_finalization.py` — quick/full checks for chronology, preservation, evidence, checklist, and packaging
- [ ] `notebooks/P10_Research_Log_Notebook_Corrected_EVIDENCE_MAP.md` — approved evidence inventory for dates, metrics, and visuals
- [ ] `notebooks/P10_Research_Log_Notebook_Corrected_REVIEW.md` — human checklist for fairness, hindsight, sparse visuals, and judge readability

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Entries reflect only what was reasonably knowable on that day | FNL-04 | Hindsight and fabrication cannot be proven reliably by static checks alone | Review the corrected notebook against the evidence map and confirm early entries do not reveal later conclusions or unsupported specifics. |
| Sparse visuals appear only on pivotal days and major transitions | FNL-04 | Figure appropriateness is editorial and audience-dependent | Count embedded visuals, verify each is justified by a pivotal day, and confirm no filler visuals were added. |
| Final notebook feels concise, judge-readable, and aligned with the Kushal example | FNL-05 | Presentation quality requires human judgment | Compare the corrected notebook to `docs/reference/Project S-19-05 Research Notebook (1).pdf` and confirm the final flow is credible, chronological, and presentable. |
| Manual PDF generation produces an acceptable review artifact | FNL-05 | User explicitly performs the final export step | After signoff, run the existing PDF utility manually and inspect the generated PDF for missing assets, broken formatting, or path confusion. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
