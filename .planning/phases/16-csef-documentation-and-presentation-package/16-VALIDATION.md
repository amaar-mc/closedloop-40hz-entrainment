---
phase: 16
slug: csef-documentation-and-presentation-package
status: ready
nyquist_compliant: true
wave_0_complete: true
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
| **Full suite command** | `grep -rn "73 feat\|61 spectral\|R² ≈ 0.25\|R² = 0.170\|0\.254\|0\.240\|0\.278" docs/ CSEF/ scripts/generate_csef_presentation.py` |
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
| 16-01-T1 | 16-01 | 1 | CSEF-INTERVIEW-SCRIPTS | grep audit | `grep -rn "73 feat" CSEF/Presentation/01_main_script.md CSEF/Presentation/02_short_version.md CSEF/Presentation/03_memorization_guide.md CSEF/Presentation/04_qa_bank_and_danger_zones.md CSEF/Presentation/05_qa_complete.md \| grep -v "previous\|before\|old\|baseline\|was\|dropped from" \| wc -l \| xargs test 0 -eq` | yes | pending |
| 16-01-T2 | 16-01 | 1 | CSEF-ELEVATOR-PITCH | diff + grep | `diff docs/ELEVATOR_PITCH.md CSEF/Presentation/ELEVATOR_PITCH.md && grep -c "0.60\|0.606" docs/ELEVATOR_PITCH.md \| xargs test 0 -lt` | yes | pending |
| 16-02-T1 | 16-02 | 1 | CSEF-POSTER-V6 | grep audit | `grep -c "12 features\|12 PAC" docs/poster/POSTER_BOARD_V6.md \| xargs test 0 -lt && grep -c "0.606\|0.577\|0.430" docs/poster/POSTER_BOARD_V6.md \| xargs test 0 -lt && grep "73 feat" docs/poster/POSTER_BOARD_V6.md \| grep -v "previous\|before\|old\|dropped\|removing\|was" \| wc -l \| xargs test 0 -eq` | N/A (created) | pending |
| 16-02-T2 | 16-02 | 1 | CSEF-POSTER-V6 | diff | `diff docs/poster/POSTER_BOARD_V6.md CSEF/Poster/POSTER_BOARD_V6.md` | N/A (created) | pending |
| 16-03-T1 | 16-03 | 1 | CSEF-PRESENTATION-PDF | compile + grep | `python3 -m py_compile scripts/generate_csef_presentation.py && grep -c "12 features\|0.606\|PAC.*stim" scripts/generate_csef_presentation.py \| xargs test 0 -lt && grep -n "73 feat\|61 spectral\|R2 = 0.170" scripts/generate_csef_presentation.py \| grep -v "#.*previous\|#.*before\|#.*old\|#.*baseline\|#.*original\|#.*was" \| wc -l \| xargs test 0 -eq` | yes | pending |
| 16-03-T2 | 16-03 | 1 | CSEF-PRESENTATION-PDF | size + page count | `python3 -c "import os; from pypdf import PdfReader; s1=os.path.getsize('docs/presentations/CSEF_2026_Presentation.pdf'); s2=os.path.getsize('CSEF/Presentation/CSEF_2026_Presentation.pdf'); assert s1>10000; assert s1==s2; r=PdfReader('docs/presentations/CSEF_2026_Presentation.pdf'); assert len(r.pages)<=13"` | N/A (generated) | pending |
| 16-04-T1 | 16-04 | 1 | CSEF-RESEARCH-PAPER | grep audit | `test -f docs/paper/RESEARCH_PAPER_v4.md && grep -c "feature ablation\|ablation study" docs/paper/RESEARCH_PAPER_v4.md \| xargs test 0 -lt && grep -c "0.606" docs/paper/RESEARCH_PAPER_v4.md \| xargs test 0 -lt && grep "73 feat" docs/paper/RESEARCH_PAPER_v4.md \| grep -v "previous\|before\|original\|baseline\|ablation\|compared\|reduced from\|dropped" \| wc -l \| xargs test 0 -eq` | N/A (created) | pending |
| 16-04-T2 | 16-04 | 1 | CSEF-RESEARCH-PAPER | diff | `diff "docs/paper/RESEARCH_PAPER_v4.md" "CSEF/Research Paper/RESEARCH_PAPER_v4.md"` | N/A (created) | pending |
| 16-05-T1 | 16-05 | 2 | CSEF-LAB-NOTEBOOK | grep count | `grep -c "March.*2026\|PAC.Stim\|feature ablation\|0.606" "CSEF/Lab Notebook/P10_Lab_Notebook_VFINAL.md" \| xargs test 3 -le` | yes | pending |
| 16-05-T2 | 16-05 | 2 | CSEF-FINAL-SYNC-AUDIT | grep + diff + generator audit | `grep -c "0.606" CSEF/Abstract/ABSTRACT.md \| xargs test 0 -lt && grep -rn "73 feat" CSEF/Presentation/01_main_script.md CSEF/Poster/POSTER_BOARD_V6.md CSEF/Abstract/ABSTRACT.md 2>/dev/null \| grep -v "previous\|before\|old\|dropped\|removing\|was\|baseline\|original" \| wc -l \| xargs test 0 -eq && grep -n "73 feat\|61 spectral\|R2 = 0.170" scripts/generate_csef_presentation.py 2>/dev/null \| grep -v "previous\|before\|old\|dropped\|removing\|was\|baseline\|original" \| wc -l \| xargs test 0 -eq` | yes | pending |
| 16-05-T3 | 16-05 | 2 | CSEF-FINAL-SYNC-AUDIT | checkpoint | Human review of complete CSEF submission package | yes | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements. No test framework install needed — grep is sufficient for document audits. pypdf is needed for PDF page count verification (install with `pip install pypdf` if missing).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Every R2 value traces to source file | Number accuracy | Semantic check | Cross-reference each R2 in output doc against source map in 16-RESEARCH.md |
| Presentation stays under 13 pages | CSEF page limit | Visual rendering check | Open PDF and visually confirm layout (automated page count catches overflow but not layout issues) |
| docs/ and CSEF/ are in sync | Submission integrity | File comparison | `diff docs/poster/POSTER_BOARD_V6.md CSEF/Poster/POSTER_BOARD_V6.md` |
| Lab notebook entries are not backdated | Scientific integrity | Date review | Verify new entries are dated March 2026+ |
| Presentation PDF content matches generator source | Binary artifact | Cannot grep PDF | Verify generator script has correct numbers (automated in 16-03-T1) |
| Narrative flow in presentation script | Judge experience | Subjective quality | Read 01_main_script.md — PAC+Stim discovery should be the climax |

*All phase behaviors also benefit from human review via checkpoint 16-05-T3.*

---

## Validation Sign-Off

- [x] All tasks have automated verify commands defined
- [x] Sampling continuity: grep audit after every commit
- [x] Wave 0 covers all MISSING references (none — grep is sufficient)
- [x] No watch-mode flags
- [x] Feedback latency < 2s
- [x] `nyquist_compliant: true` set in frontmatter
- [x] Generator script stale-number audit included (prevents binary PDF contamination)

**Approval:** ready
