# Phase 1C: Figure and Visual Compliance Audit

**Audit date:** 2026-03-24
**Source:** `scripts/generate_csef_presentation.py`

## Figures Referenced in Script

The script references one figure:

### Figure 1: System Architecture

| Property | Value | Status |
|---|---|---|
| Primary path | `results/figures/ai_generated/system_architecture_v5.png` | **EXISTS** |
| Fallback path | `results/figures/ai_generated/system_architecture_v3.png` | EXISTS (fallback not needed) |
| Script lines | 478-488 | — |
| Caption present | Yes | **PASS** |
| Caption text | "Figure 1. System architecture of the closed-loop 40 Hz entrainment system..." (line 482-488) | Descriptive ✓ |
| Width | 82% of text width (`TW * 0.82`) | — |

**File verified:** `system_architecture_v5.png` exists at 305,535 bytes (297 KB).

## Figure Content Accuracy Issue

**WARN: The system architecture figure contains outdated specifications.**

From visual inspection of the rendered PDF (page 6), the figure shows:
- "73 features (61+7+5)" in the Feature Engineering box
- "31K params" in the Causal TCN box
- "5 s hysteresis" in the Adaptive Controller box

The presentation TEXT (which is authoritative) describes:
- **12 features** (PAC+Stim) as the final model input
- **22,914 parameters** (h=64) for the final TCN
- **5-second hysteresis** (matches figure, matches code default)

The figure appears to show the FULL pipeline (all 73 features are computed during feature engineering), but a judge might interpret "73 features" as the TCN's input dimensionality — which would be wrong. The figure should either:
1. Show the feature selection step (73 → 12), or
2. Show "12 PAC+Stim features" as the TCN input

The "31K params" is the parameter count for the original 73-feature TCN (31,043 params per RESULTS_REPORT.md). The actual model that achieves R² = 0.606 has 22,914 parameters. This discrepancy could be flagged by a judge.

## Prohibited Visual Elements

| Check | Status |
|---|---|
| No animations in PDF | **PASS** (static PDF) |
| No embedded videos | **PASS** |
| No transitions | **PASS** |
| No prohibited content in figures | **PASS** |

## Missing Figures

The presentation is text-heavy with only one figure (the system architecture). CSEF judges may expect additional figures (e.g., horizon sweep plot, controller comparison bar chart, per-subject scatter). These figures exist in `results/figures/` but are not included in the presentation. This is a design choice, not a compliance violation.

Available but unused figures:
- `results/figures/horizon_sweep.png` (176 KB)
- `results/figures/controller_comparison.png` (120 KB)
- `results/figures/per_subject_utility.png` (153 KB)
- `results/figures/pac_targeting_gap.png` (89 KB)
- `results/figures/stim_vs_alignment.png` (152 KB)
- `results/figures/threshold_sensitivity.png` (186 KB)

## Summary

- **PASS:** 5 checks
- **FAIL:** 0
- **WARN:** 1 (system architecture figure shows outdated 73-feature/31K-param specs instead of the final 12-feature/22,914-param model)

**Recommendation:** Update `system_architecture_v5.png` (or create v7) to show the feature selection step (73 → 12 PAC+Stim features) and correct the parameter count to 22,914. This is the most visible inconsistency a judge would notice between the figure and the surrounding text.
