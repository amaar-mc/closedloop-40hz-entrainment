---
phase: 07-fix-data-accuracy-and-methodology-errors
verified: 2026-03-17T00:00:00Z
status: passed
score: 7/7 must-haves verified
re_verification: false
gaps: []
human_verification: []
---

# Phase 7: Fix Data Accuracy and Methodology Errors — Verification Report

**Phase Goal:** The paper's factual claims about system implementation match the actual code and results — hysteresis duration, CI method, population composition, spectral feature set, and best-epoch claims are all accurate.
**Verified:** 2026-03-17
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | Every location that said "5-second hysteresis" in RESEARCH_PAPER.md now says "3-second hysteresis" (three locations: Section 1.4, Section 3.6.2, Figure 3 caption) | VERIFIED | Grep confirms 3 occurrences of "3-second hysteresis" (lines 65, 321, 339); zero occurrences of "5-second hysteresis" |
| 2  | Section 3.8 of RESEARCH_PAPER.md describes the CI method as "large-sample normal approximation (g ± 1.96 × SE)", not BCa bootstrap | VERIFIED | Line 371: "large-sample normal approximation (g ± 1.96 × SE)"; line 471: "large-sample normal approximation"; zero BCa occurrences |
| 3  | Section 3.4.1 describes 4 spectral bands (theta, alpha, beta, gamma) × 7 channels = 28 features, plus 7 theta-gamma ratios, 21 PAC-structure features, and 5 global stats | VERIFIED | Line 256 matches exactly; no delta band, no cross-channel coherence |
| 4  | Section 3.1.2 says artifact samples were "zeroed" not "rejected" | VERIFIED | Lines 183–184: "Artifact zeroing:", "were zeroed (set to 0.0)", "artifact zeroing was applied"; zero "artifact rejection" occurrences in that context |
| 5  | Section 3.3.2 contains no unqualified "Best checkpoint: Epoch 53" — the claim is removed or qualified as unverified for EEGNet | VERIFIED | Line 242: "epoch not recorded for EEGNet; epoch 53 refers to the TCN checkpoint" — appropriately qualified |
| 6  | RESULTS_REPORT.md Lead Time Hedges' g reads 0.75 (not 0.76) with matching CI [+0.25, +1.26] | VERIFIED | Line 62: "Lead Time | 0.8s | 0.2s | +0.75 [+0.25, +1.26]" |
| 7  | RESULTS_REPORT.md PAC Gap column header and all inline values use "×10⁻⁶ MI units" (not "µV²") | VERIFIED | Lines 37, 61, 83, 91, 125 all use "×10⁻⁶ MI"; zero µV² occurrences remain |

**Score:** 7/7 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `docs/paper/RESEARCH_PAPER.md` | Corrected paper text for all 7 DATA/METH requirements | VERIFIED | File exists; all 7 correction targets confirmed by grep |
| `results/RESULTS_REPORT.md` | Corrected Hedges' g and PAC Gap units | VERIFIED | File exists; 0.75 for Lead Time g; no µV² remaining |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| Section 3.4.1 description | `archive/experimental_models/spectral_features.py` lines 161–194 | 4 bands × 7ch = 28 + 7 ratios + 21 PAC-struct + 5 globals = 61 | WIRED | spectral_features.py lines 161–164 confirm theta/alpha/beta/gamma only; line 194 comment confirms 61 total; Section 3.4.1 matches exactly |
| Section 3.6.2 hysteresis | `scripts/pipeline/run_tcn_validation.py` line 283 | `hysteresis=3` (default parameter) | WIRED | Line 283: `hysteresis=3` in constructor signature; no hysteresis=5 anywhere in file; note: PLAN cited line 253 (file is at `scripts/pipeline/`, not root) — substance correct |
| Section 3.8 CI method | Actual computation used | g ± 1.96 × SE normal approximation | WIRED | Paper line 371 and 471 both reference "large-sample normal approximation"; no BCa code found |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| DATA-01 | 07-01-PLAN.md | Hysteresis corrected from "5-second" to "3-second" in all 3 paper locations | SATISFIED | "3-second hysteresis" at RESEARCH_PAPER.md lines 65, 321, 339 |
| DATA-02 | 07-01-PLAN.md | CI method corrected from BCa bootstrap to large-sample normal approximation | SATISFIED | Lines 371, 471; zero BCa occurrences |
| DATA-03 | 07-01-PLAN.md | Lead time Hedges' g corrected from 0.76 to 0.75 in RESULTS_REPORT.md | SATISFIED | RESULTS_REPORT.md line 62: +0.75 |
| DATA-04 | 07-01-PLAN.md | EEGNet "best epoch 53" qualified as unverifiable in Section 3.3.2 | SATISFIED | Line 242: fully qualified statement |
| DATA-05 | 07-01-PLAN.md | PAC Gap units corrected from µV² to ×10⁻⁶ MI units | SATISFIED | RESULTS_REPORT.md: 5 locations all use ×10⁻⁶ MI; zero µV² |
| METH-01 | 07-01-PLAN.md | Spectral features: 4 bands not 5, PAC-structure not coherence, global stats | SATISFIED | Section 3.4.1 line 256; also Section 4 line 461 updated to "spectral and PAC-structure features" |
| METH-02 | 07-01-PLAN.md | Artifact rejection language changed to "zeroed" in Section 3.1.2 | SATISFIED | Lines 183–184: "Artifact zeroing:", "were zeroed", "artifact zeroing" throughout |

**Orphaned requirements check:** REQUIREMENTS.md maps DATA-01 through DATA-05, METH-01, METH-02 exclusively to Phase 7 — all 7 are claimed by 07-01-PLAN.md and verified above. No orphaned requirements.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `docs/paper/RESEARCH_PAPER.md` | 304 | `Best checkpoint | Epoch 53 (validation R² = 0.411)` — this is the TCN table, not EEGNet | Info | Correct: line 304 is the TCN performance table where epoch 53 IS confirmed. Only the EEGNet claim at line 242 needed qualification. Both are now correct. |

No blockers or warnings found.

---

## Human Verification Required

None. All seven corrections are text replacements verifiable programmatically by grep.

---

## Commit Verification

All three task commits documented in SUMMARY are confirmed in git history:

- `66970c5` — fix(07-01): correct hysteresis, CI method, EEGNet epoch claim, artifact wording
- `e6da0c8` — fix(07-01): correct spectral feature description in Section 3.4.1
- `0203c06` — fix(07-01): correct Hedges' g and PAC Gap units in RESULTS_REPORT.md

---

## Summary

All 7 must-have truths are verified in the actual codebase. Every correction matches the ground-truth source:

- **Hysteresis:** `scripts/pipeline/run_tcn_validation.py` line 283 confirms `hysteresis=3`; all three paper locations now say "3-second"
- **CI method:** No BCa code found; paper consistently uses normal approximation language
- **Spectral features:** `archive/experimental_models/spectral_features.py` lines 161–194 confirms 4 bands (theta/alpha/beta/gamma), no delta, no coherence; Section 3.4.1 matches exactly
- **Artifact zeroing:** `src/preprocessing.py` line 173 (`signal_clean[artifact_mask] = 0.0`) confirms zeroing; Section 3.1.2 now uses zeroing language throughout
- **EEGNet epoch:** Qualified with explicit note that epoch 53 is TCN-only
- **Hedges' g 0.75:** RESULTS_REPORT.md Lead Time row corrected
- **PAC Gap units:** All 5 µV² occurrences replaced with ×10⁻⁶ MI

Phase goal achieved. The paper's factual claims now match the actual code and results.

---

_Verified: 2026-03-17T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
