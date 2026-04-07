# Phase 17: Poster Board Deep Audit — Research

**Researched:** 2026-04-07
**Domain:** Scientific poster audit — data accuracy, figure quality, visual cohesion, judge-readiness
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Audit ONLY — no modifications to poster files, source code, figures, or any project artifacts
- All outputs are markdown audit reports written to the phase directory
- Cross-reference every number on the poster against actual result files in `results/`
- Verify every statistic, R-squared value, p-value, effect size, sample count, and percentage on the poster against ground-truth JSON/MD in `results/`
- Check all architecture descriptions (parameter counts, layer descriptions, input/output shapes) against actual model code in `src/` and `temporal_multiscale/`
- Verify dataset claims (35 subjects, 17,283 windows, split sizes, channel counts) against `data/processed/` and `src/data_loader.py`
- Flag any number that cannot be verified or that contradicts source data
- Assess every figure for: accuracy of plotted data, axis labels, legends, readability at poster scale, color accessibility
- Verify figure captions match what the figure actually shows
- Check that all "Diagram created by Amaar Chughtai" attributions are present where needed
- Assess figure numbering consistency and cross-references in text
- Evaluate layout balance, whitespace usage, section flow (left-to-right, top-to-bottom reading order)
- Check font consistency, color palette consistency, heading hierarchy
- Assess whether the poster tells a coherent visual story from problem to solution to results
- Compare PDF render against PPTX source for any rendering artifacts
- Evaluate from perspective of CSEF judges: Is the hypothesis clear? Are results compelling? Are limitations honest?
- Check for common judge concerns: overclaiming, missing controls, unclear methodology
- Assess whether the "Summary of Key Results" box and "Conclusions" are judge-friendly
- Evaluate the Future Directions and Clinical Use sections for realism and scientific rigor
- Check references for completeness and proper formatting

### Claude's Discretion
- Specific report structure and section ordering within audit documents
- Level of detail in figure-by-figure analysis
- Whether to produce one consolidated report or separate reports per audit dimension
- Statistical verification methodology (which JSON files to cross-reference)

### Deferred Ideas (OUT OF SCOPE)
- Any actual modifications to the poster based on audit findings (would be a separate phase if needed)
- Re-generation of figures
- PPTX template redesign
</user_constraints>

---

## Summary

This phase is a read-only audit of the CSEF 2026 poster board (`CSEF/Poster/csef_posters/CSEF_poster_v2.pdf` + `.pptx`). The poster specification is `docs/poster/POSTER_BOARD_V8.md`. All numerical claims have been systematically cross-referenced against ground-truth JSON and Markdown files in `results/`, `experimental/`, and `rigor/`. Model architecture claims have been verified by live parameter counts from `src/eegnet.py` and `temporal_multiscale/multiscale_tcn.py`. Dataset claims have been verified against `data/processed/` numpy archives.

**Three confirmed discrepancies require audit findings:** (1) the pipeline text describes a 5,154-param TCN but the closed-loop validation results were produced by a 31,043-param checkpoint; (2) Conclusion 1 states R²=0.25 at 5-10s which is stale from the 73-feature model while Figure 6 shows the PAC+Stim model at 0.577-0.669; (3) the Exponential Decay Hedges' g in Result 4 reads 2.01 in the poster but 2.313 in the source JSON. The remaining ~30 numerical claims are verified correct.

**Primary recommendation:** The planner should structure the deliverable as a single consolidated audit report covering all four dimensions (data accuracy, figures, visual cohesion, judge-readiness), with a machine-readable findings table that flags each claim as PASS / FLAG / FAIL with the source file and corrected value.

---

## Poster Artifacts and Specification

| Artifact | Path | Status |
|----------|------|--------|
| Rendered poster (V2) | `CSEF/Poster/csef_posters/CSEF_poster_v2.pdf` | 1.7 MB — exists |
| Editable source | `CSEF/Poster/csef_posters/CSEF_poster.pptx` | 7.6 MB — exists |
| Poster specification | `docs/poster/POSTER_BOARD_V8.md` | Full content — readable |
| Prior coherence audit | `docs/poster/POSTER_COHERENCE_AUDIT.md` | Exists — partially stale, useful reference |

The poster spec (`POSTER_BOARD_V8.md`) is the authoritative description of intended content. It includes a `## NUMERICAL VERIFICATION` table (lines 1134–1157) that documents claimed sources and prior self-verification. The planner's audit should use this table as a starting checklist and extend it with ground-truth cross-reference results.

---

## Data Accuracy Findings (Pre-Verified)

All cross-references executed against live data files. Results below are authoritative for the planner.

### Controller Performance Claims (Result 1)

Source: `results/tcn_validation_results.json` — summary table and per-subject arrays.

| Poster Claim | JSON Value | Status |
|---|---|---|
| TCN Alignment = 72.1% | 0.7209 → 72.1% | PASS |
| Reactive Alignment = 64.5% | 0.6449 → 64.5% | PASS |
| Fixed Schedule Alignment = 45.0% | 45.0 (summary) | PASS |
| TCN Low-PAC Targeting = 82.6% | 0.8255 → 82.6% | PASS |
| Reactive Low-PAC Targeting = 51.7% | 0.5167 → 51.7% | PASS |
| Fixed Schedule Low-PAC Targeting = 61.4% | 61.4 (summary) | PASS |
| Oracle Alignment = 100.0% | 100.0 (summary) | PASS |
| TCN Stim % = 59.7% | 59.739 → 59.7% | PASS |
| Reactive Stim % = 36.7% | 36.701 → 36.7% | PASS |
| Fixed Stim % = 66.6% | 66.55 → 66.6% | PASS |
| PAC Gap TCN = +30.5 ×10⁻⁶ | 3.050 ×10⁻⁵ → 30.50 ×10⁻⁶ | PASS |
| PAC Gap Reactive = +21.1 ×10⁻⁶ | 2.109 ×10⁻⁵ → 21.09 ×10⁻⁶ | PASS |
| Fixed PAC Gap = -6.6 ×10⁻⁶ | -6.6 (RESULTS_REPORT.md) | PASS |
| Oracle PAC Gap = +33.3 ×10⁻⁶ | 3.336 ×10⁻⁵ → 33.36 ×10⁻⁶ (rounds to 33.4) | MARGINAL — poster says 33.3, actual is 33.4 |
| TCN = 91% of oracle | 30.50/33.36 = 91.5% | PASS (poster rounds down to 91%) |

### Effect Size Claims (Result 1)

Source: `results/tcn_validation_results.json` → `comparisons.TCN_Predictive_vs_Reactive_Threshold.metrics`

| Poster Claim | JSON Value | Status |
|---|---|---|
| g = 1.31 (alignment) | 1.3124 | PASS (rounds to 1.31) |
| g = 4.47 (low-PAC targeting) | 4.4722 | PASS (rounds to 4.47) |
| g = 1.57 (PAC gap) | 1.5725 | PASS (rounds to 1.57) |
| CI [0.75, 1.87] (alignment) | [0.752, 1.8728] | PASS |
| p < 0.001 (all three) | wilcoxon_p = 0.0 for all three | PASS |
| 95% CI for g=1.31: [0.75, 1.87] | [0.752, 1.8728] | PASS |

### Per-Subject Consistency (Result 2)

Source: `results/tcn_validation_results.json` → `per_subject` arrays, verified via live Python computation.

| Poster Claim | Verified Value | Status |
|---|---|---|
| 35/35 subjects benefit (clinical_utility) | 35/35 | PASS |
| 35/35 subjects (alignment) | 35/35 | PASS |
| Binomial p < 0.001 | N=35, k=35, p = 2^-35 ≈ 3×10⁻¹¹ | PASS |

### TCN Model R² Claims

Source: `results/tcn_validation_results.json`, `results/multiseed_summary.json`, `experimental/FINDINGS.md`

| Poster Claim | Source Value | Status |
|---|---|---|
| EEGNet Test R² = 0.287 | RESULTS_REPORT.md, CLAUDE.md | PASS |
| TCN 5-seed mean R² = 0.606 ± 0.032 | `experimental/FINDINGS.md` line 78; experimental/results/pac_stim_focused.json entries with n_params=5154 confirm ~0.56–0.68 range | PASS — sourced from 5-seed PAC+Stim experiment |
| PAC+Stim TCN at h=5: R² = 0.577 | `experimental/results/horizon_sweep_pac_stim.json` h=5 7ch: 0.5771 | PASS |
| Feature ablation: -0.025 → 0.606 | FINDINGS.md; rigor_audit/04_content_accuracy.md PASS | PASS |

### CRITICAL: TCN Parameter Count Mismatch

**This is the most important discrepancy in the poster.**

The poster pipeline text (POSTER_BOARD_V8.md line 278) states:
> `EEGNet (1,457 params) → ... → Causal TCN (5,154 params)`

The checkpoint that produced all closed-loop validation results (72.1%, 82.6%, g=1.31, g=4.47, 35/35 subjects) is `models/best_multiscale_tcn_lb20_hz5_ts1.pth`, which has **31,043 parameters** (73 features, h=64, attention pool — verified live).

The 5,154-param model is the h=32 PAC+Stim architecture from `experimental/results/pac_stim_focused.json`. It was identified in the architecture search and achieves R²=0.639 (single seed) but was NOT used to produce the controller validation numbers.

The POSTER_COHERENCE_AUDIT.md (`docs/poster/POSTER_COHERENCE_AUDIT.md`) already flags: "Controller comparison — still uses 31K-param, 73-feature TCN" and "NOT Re-run with Ablated Model."

| Component | Poster Says | Validation Actually Used | Status |
|---|---|---|---|
| TCN params | 5,154 (h=32) | 31,043 (h=64, 73 features) | FLAG — internal inconsistency |
| TCN features | 12 (PAC+Stim) | 73 (61 spectral + 7 PAC + 5 stim) | FLAG — internal inconsistency |
| EEGNet params | 1,457 | 1,457 — VERIFIED CORRECT | PASS |

**Audit finding:** The poster accurately describes the architecture search finding (5,154-param model with 12 features achieves R²=0.606) but claims this model was used for the 72.1%/82.6% controller validation. Those results came from the 31,043-param model. This is a pre-existing known inconsistency flagged in the coherence audit.

### Conclusion Text Stale R² Claim

Poster Conclusion 1 (POSTER_BOARD_V8.md line 440):
> "At 5-10s horizons, the TCN maintains R² = 0.25 while all baselines collapse below zero; a +0.5 R² margin"

Source of 0.25: `models/sweep_horizons_results.json` (original 73-feature model, ts=5 smoothing):
- h=5: TCN=0.254, persistence=-0.267, margin=0.521

But Figure 6 of the same poster shows PAC+Stim model:
- h=5: TCN=0.577, persistence=0.104, margin=0.473

These are two different models. The Conclusion text was not updated when Figure 6 data was upgraded to the PAC+Stim model. The "+0.5 R² margin" is approximately correct for the original model (0.521) and approximately correct for the ablated model (0.473), but "R²=0.25" is wrong relative to Figure 6.

| Claim | Text Says | Figure 6 Shows | Status |
|---|---|---|---|
| TCN R² at 5-10s | 0.25 | 0.577 (h=5), 0.370 (h=8), 0.669 (h=10) | FLAG — stale value |
| +0.5 margin | +0.52 (original) / +0.47 (ablated) | +0.47 at h=5 | MARGINAL — approximately correct |

### Fatigue Results (Result 3)

Source: `results/fatigue_sensitivity.json` (6 entries)

| Poster Row | JSON Fatigue Rate | Gain in Poster | Gain in JSON | Status |
|---|---|---|---|---|
| None | 0.0 | +0.4% | 0.388% | PASS |
| Mild | 0.008 | +1.3% | 2.144% | FLAG — poster says 1.3% but this entry is rate=0.008 not 0.004 |
| Moderate | 0.015 | +2.6% | 2.551% | PASS |
| Severe | 0.025 | +4.3% | 4.350% | PASS |
| High | 0.04 | +5.7% | 5.653% | PASS |

**Note on Mild row:** The JSON has 6 entries (rates: 0.0, 0.004, 0.008, 0.015, 0.025, 0.04). The poster shows 5 rows. The rate=0.004 entry (gain=1.27%) is omitted. The "Mild" label in the poster at 1.3% maps to rate=0.008 (JSON gain=2.144%), not rate=0.004 (JSON gain=1.27%). The RESULTS_REPORT uses six entries with different labeling (None/Very Low/Low/Moderate/High/Very High). The poster compressed to 5 rows using a different label scheme. This is a MINOR DISCREPANCY in labeling, not the values.

**More precisely verified:**
- Poster "Mild" = 1.3% → JSON rate=0.004 entry = 1.269% → PASS (rounds to 1.3%)
- Poster "Moderate" = 2.6% → JSON rate=0.015 entry = 2.551% → PASS

The 5-row mapping omits rate=0.008 (2.144%) and skips from rate=0.004 to rate=0.015. This is selective presentation but the shown values are all accurate.

### Result 4 Fatigue Model Comparison

Source: `rigor/experiments/fatigue_model_sensitivity_results.json`

| Model | Poster Fixed | Poster Adaptive | Poster g | JSON g | Status |
|---|---|---|---|---|---|
| Exponential Decay | 5.381 | 5.401 | 2.01 | 2.313 | FLAG — g mismatch |
| Step Function | 4.947 | 5.361 | 1.21 | 1.214 | PASS |
| Heterogeneous | 5.101 | 5.231 | 1.71 | 1.707 | PASS |
| Saturation (logistic) | 4.819 | 5.092 | 3.66 | 3.665 | PASS |

The efficiency values (5.xxx) come from `results/closed_loop_demo_results.json` (simulated PAC efficiency metric). The Hedges' g values come from `rigor/experiments/fatigue_model_sensitivity_results.json`. For Exponential Decay: poster says g=2.01 but JSON says 2.313. The source of 2.01 is not traceable to any JSON file — it may have been manually transcribed or from an earlier run.

### Dataset Claims

Source: `data/processed/train_data.npz`, `val_data.npz`, `test_data.npz` — verified via numpy shape inspection.

| Poster Claim | Verified Value | Status |
|---|---|---|
| 35 subjects total | 24+5+6 = 35 | PASS |
| 17,283 windows total | 11,736+2,725+2,822 = 17,283 | PASS |
| 7 frontal EEG channels | Shape (N, 1, 7, 500) confirmed | PASS |
| 250 Hz sampling rate | 500 samples = 2s @ 250 Hz | PASS |
| 24 train / 5 val / 6 test subjects | Confirmed | PASS |
| "35 dementia patients" | Lahijanian 2024 paper describes dementia patients | PASS |
| Temporal sequences: 11,160 train | `data/processed/multiscale_temporal_lb20_hz5_ts1/train_multiscale.npz` shape (11160, 20, 73) | PASS |

### Architecture Claims

Source: live parameter counts from Python3 execution.

| Poster Claim | Verified Value | Status |
|---|---|---|
| EEGNet params = 1,457 | `sum(p.numel() for p in EEGNet().parameters())` = 1,457 | PASS |
| TCN params = 31,043 (validation checkpoint) | `tcn_validation_results.json` tcn_params=31043; `MultiscaleCausalTCN(ModelConfig(n_features=73, hidden=64))` = 31,043 | PASS |
| TCN params = 5,154 (poster pipeline text) | `MultiscaleCausalTCN(ModelConfig(n_features=12, hidden=32))` = 7,427 (NOT 5,154) | FLAG — 5,154 comes from older architecture variant |
| 73 features (original model) | `data/processed/multiscale_temporal_lb20_hz5_ts1/train_multiscale.npz` feature_names shape (73,) | PASS |
| EEGNet input: (batch, 1, 7, 500) | Code verified | PASS |
| TCN input: 12 features × 20 timesteps | Consistent with PAC+Stim design | PASS (for PAC+Stim model) |
| Dilations [1,2,4,8] | `config.yaml` and `multiscale_tcn.py` default | PASS |
| z-score thresholds ±0.5, 3s hysteresis | POSTER_BOARD_V8.md cites `scripts/pipeline/run_tcn_validation.py` line 283 | NEEDS FIELD VERIFY in .pptx |

**Note on 5,154 params:** Live computation with `ModelConfig(n_features=12, hidden=32, pool_type='attention')` gives 7,427 params. The 5,154 value traces to `experimental/results/pac_stim_focused.json` entries with `n_params: 5154` and name `tcn_h32_pac_stim`. This was a slightly different architecture configuration (likely different head size or layer structure from the experimental module, not the current `multiscale_tcn.py`). The number is documented and consistent within the experiment files but cannot be reproduced with the current architecture code.

### Hardware Cost Claims

| Poster Claim | Verifiable? | Status |
|---|---|---|
| Muse 2 = $249 | Consumer product price — not from code | LOW confidence, externally verifiable |
| Total cost < $300 | Headband + headphones estimate | LOW confidence, externally verifiable |

---

## Figure Inventory and Status

From `docs/poster/POSTER_BOARD_V8.md` Figure Inventory (lines 1163–1177), all 10 figures were marked "TO GENERATE" via Nano Banana Pro. The `results/figures/ai_generated/` directory contains rendered versions.

| Figure | Purpose | AI-Generated Available | Data-Backed |
|---|---|---|---|
| Fig 1: Fixed vs Adaptive | Conceptual diagram | `closedloop_vs_fixed_v3.png` | Conceptual — no exact data |
| Fig 2: Dataset Overview | EEG channels + protocol | None found | Conceptual + data |
| Fig 3: Feature Ablation | -0.025 → 0.606 | None found | `experimental/FINDINGS.md` data |
| Fig 4: System Architecture | Hero flowchart | `system_architecture_v7.png` | Architecture description |
| Fig 5: Controller Comparison Bar | 72.1% vs 64.5% | None found — would use result data | `results/tcn_validation_results.json` |
| Fig 6: Horizon Sweep | TCN vs persistence | `horizon_inflection_v1.png` | `experimental/results/horizon_sweep_pac_stim.json` |
| Fig 7: Per-Subject Scatter | 35/35 benefit | None found | `results/tcn_validation_results.json` per_subject |
| Fig 8: Brain Mechanism | 40 Hz entrainment | `entrainment_mechanism_v2.png` | Conceptual diagram |
| Fig 9: Training/Validation Protocol | Pipeline description | None found | Conceptual + data |
| Fig 10: Real-Data Timeline | sub-15 example | `results/figures/timeline_example.png` | Real data |

**Existing `results/figures/` data plots** (generated from real data, not AI): `controller_comparison_v2.png`, `per_subject_utility.png`, `horizon_sweep_pac_stim.png`, `timeline_example.png`, `threshold_sensitivity.png`, `pac_targeting_gap.png`, `system_block_diagram.png`. These may already be in the PPTX. The audit needs to verify which figures actually appear in the PDF vs which were regenerated via Nano Banana Pro.

### Figure Data Accuracy Issues to Audit

**Figure 5 (Controller Bar Chart):** The bar chart prompt in POSTER_BOARD_V8.md specifies exact values (72.1%, 82.6%, 45.0%, etc.) that are all verified correct. The audit must confirm the rendered bar chart in the PDF matches these values.

**Figure 6 (Horizon Sweep):** The prompt specifies exact values verified against `experimental/results/horizon_sweep_pac_stim.json`. All values match. The audit must confirm the PDF figure shows these values correctly.

**Figure 7 (Per-Subject Scatter):** X-axis range "0.43 to 0.80" and Y-axis range "0.58 to 0.90" should be verified against actual per-subject data from `results/tcn_validation_results.json`. Per-subject alignment ranges across 35 subjects should be extracted to confirm these bounds are accurate.

---

## Visual Cohesion Checklist (Pre-Research)

From `POSTER_BOARD_V8.md` global style specification:

| Property | Specified Value | Audit Check |
|---|---|---|
| Background | #FFFFFF | Check PDF |
| Primary color | #1B6B6E (dark teal) | Check consistent across TCN/positive elements |
| Secondary | #1B2A4A (dark navy) | Check text and axes |
| Accent gold | #D4A843 | Check callout boxes |
| Accent coral | #C85A4A | Check fixed schedule / negative bars |
| Font headers | Amaranth Bold | Check PPTX fonts |
| Font body | Titillium Web | Check PPTX fonts |
| Attribution | "Generated by Amaar Chughtai" on each figure | Check each figure |

**CSEF compliance checklist** (from POSTER_BOARD_V8.md):
- [x] No school name/logo on board (per spec)
- [x] No student contact info (per spec)
- [x] No QR codes on board (per spec)
- [x] No photos of people (per spec)
- [x] No previous fair awards (per spec)
- [ ] **TO VERIFY IN PDF:** All 10 figure attributions present

---

## Judge-Readiness Analysis

### Hypothesis Clarity
The hypothesis is explicitly stated: "A causal TCN trained on PAC trajectory features can forecast coupling dynamics 5-10 seconds ahead, a horizon where simpler baselines collapse, enabling a closed-loop controller that delivers stimulation proactively rather than reactively."

This is clear, falsifiable, and directly tested by the results. HIGH confidence.

### Controls Present
- Fixed Schedule (blind control)
- Reactive Threshold (active comparator)
- PI Controller (engineering comparator)
- Alignment Oracle (theoretical upper bound)
- Persistence baseline (trivial prediction comparator)
- Shuffle-label test (R²=-0.332, confirms real signal)
- Multi-seed robustness (5 seeds)
- Threshold sensitivity sweep (δz=0.1 to 1.0)
- Subject-level splits (no data leakage)

Controls are comprehensive and well-documented.

### Identified Judge Risks

**Risk 1 — TCN/Architecture Inconsistency (HIGH judge risk):** A judge asking "what parameters does your TCN have?" will get a contradictory answer depending on whether they read the pipeline table (5,154) or understand the validation was run on the 31,043-param checkpoint. This is the single highest judge-readiness risk.

**Risk 2 — "R²=0.25 at 5-10s" inconsistency with Figure 6 (MEDIUM risk):** Conclusion 1 text says R²=0.25 but Figure 6 shows 0.577-0.669. A judge who reads the conclusions and then looks at Figure 6 will see a mismatch. The coherence audit flagged this as STALE.

**Risk 3 — Real-data validation uses offline replay (ACKNOWLEDGED in poster):** The limitation "offline replay, not live closed-loop" is explicitly stated in the Limitation section. This is properly disclosed and should satisfy most judges.

**Risk 4 — "Dementia patients" claim:** The poster says "35 dementia patients" consistently. The Lahijanian 2024 paper is titled "Auditory Gamma-band Entrainment Enhances Default Mode Network Connectivity in Dementia Patients" — so this is accurate. PASS.

**Risk 5 — Fatigue results use heuristic controller, not TCN (COHERENCE AUDIT flagged):** Result 3 (fatigue sweep) and Result 4 (fatigue model robustness) compare Fixed Schedule vs "Adaptive" using a trend-based heuristic controller, not the trained TCN. This is not disclosed on the poster. A judge may assume these results reflect the TCN's performance.

**Risk 6 — Exponential Decay g=2.01 mismatch:** If a judge asks to see source data for Result 4, the g=2.01 value does not match the JSON (2.313). This is a factual error.

### Reference Format Check

References on poster:
1. Iaccarino et al. Nature 540(76323), 230-235, 2016.
2. Martorell et al. Cell 177(2), 256-271, 2019.
3. Tort et al. J Neurophysiol 104(2), 1195-1210, 2010.
4. Lawhern et al. J Neural Eng 15(5), 056013, 2018.
5. Lahijanian et al. Sci Rep 14, 13153, 2024.
6. Thompson & Spencer. Psychol Rev 73(1), 16-43, 1966.
7. Chan et al. Alz & Dem 21(10), e70792, 2025.
8. Fortunato et al. Front Neurosci 17, 2023.

Note: Reference 1 has "76323" for page number which appears to be a journal code rather than standard page format for Nature (should be 230-235 without the journal code). Reference 7 (Chan 2025) is cited as future work evidence — verify year is correct (2025 or 2022).

---

## Architecture Patterns for Audit Reports

### Recommended Report Structure

The planner should produce one consolidated audit report with four clearly labeled sections matching the four audit dimensions from CONTEXT.md. Alternatively, four separate reports can be produced (one per dimension) with a master summary. Given CSEF judging is 2026-04-09 (2 days away), a single consolidated report maximizes readability.

**Recommended file:** `17-AUDIT-REPORT.md` covering all four dimensions.

Sections:
1. Data Accuracy Audit — tabular findings per claim, PASS/FLAG/FAIL, source file, corrected value
2. Figure Audit — per-figure checklist covering data accuracy, labels, readability, attribution
3. Visual Cohesion Audit — layout, fonts, colors, reading flow
4. Judge-Readiness Audit — hypothesis clarity, controls, limitations, judge risks

### Finding Classification

| Class | Meaning | Action |
|---|---|---|
| PASS | Verified correct | Document |
| FLAG | Discrepancy found, needs decision | Document with corrected value |
| FAIL | Cannot be verified against any source | Document with investigation path |
| RISK | Correct data, but judge-facing framing risk | Document with recommended answer |

---

## Common Pitfalls for This Audit

### Pitfall 1: Treating Coherence Audit as Complete
**What goes wrong:** The existing `docs/poster/POSTER_COHERENCE_AUDIT.md` was written before V8 and before some discrepancies were confirmed. Treating it as the final word will miss the ExponentialDecay g mismatch and the current parameter count status.
**Prevention:** Use coherence audit as starting checklist, verify all flagged items independently against JSON source files.

### Pitfall 2: Missing the Model Identity Split
**What goes wrong:** The poster describes two distinct TCN configurations: (a) the 5,154-param h=32 PAC+Stim model (R²=0.606, architecture search result) and (b) the 31,043-param h=64 73-feature model (validation checkpoint). Conflating them produces wrong answers to every model-related question.
**Prevention:** Track which model each claim is about. The R²=0.606 claim is about (a). The 72.1%/82.6% claim is about (b).

### Pitfall 3: Conclusion-Figure Inconsistency
**What goes wrong:** Reading conclusion text at face value without cross-checking against figures, creating the impression all conclusions are internally consistent.
**Prevention:** For each numbered conclusion, check which data source it cites and whether that source matches the cited value.

### Pitfall 4: Unverifiable PDF Content
**What goes wrong:** The PPTX and PDF cannot be parsed programmatically for text content by the planner. The audit of actual rendered content (which numbers appear in the PDF, which figures are present) requires reading the PDF directly or reading the PPTX structure.
**Prevention:** The planner should use Claude's PDF reading capability to view `CSEF/Poster/csef_posters/CSEF_poster_v2.pdf` and compare rendered content against POSTER_BOARD_V8.md spec. The `Read` tool can view the PDF.

---

## Pre-Verified Data Reference Card

The planner can use this table directly in the audit report.

### All Verified Numerical Claims

| # | Claim | Source File | Ground Truth | Status |
|---|---|---|---|---|
| 1 | TCN Alignment = 72.1% | tcn_validation_results.json | 0.7209 = 72.1% | PASS |
| 2 | Reactive Alignment = 64.5% | tcn_validation_results.json | 0.6449 = 64.5% | PASS |
| 3 | Fixed Alignment = 45.0% | tcn_validation_results.json summary | 45.0 | PASS |
| 4 | TCN Low-PAC = 82.6% | tcn_validation_results.json | 0.8255 = 82.6% | PASS |
| 5 | Reactive Low-PAC = 51.7% | tcn_validation_results.json | 0.5167 = 51.7% | PASS |
| 6 | Fixed Low-PAC = 61.4% | tcn_validation_results.json summary | 61.4 | PASS |
| 7 | g=1.31 (alignment) | tcn_validation_results.json | 1.3124 | PASS |
| 8 | g=4.47 (low-PAC) | tcn_validation_results.json | 4.4722 | PASS |
| 9 | g=1.57 (PAC gap) | tcn_validation_results.json | 1.5725 | PASS |
| 10 | p<0.001 all comparisons | tcn_validation_results.json | wilcoxon_p=0.0 | PASS |
| 11 | PAC gap = 30.5 ×10⁻⁶ | tcn_validation_results.json | 30.50 | PASS |
| 12 | Oracle PAC gap = 33.3 ×10⁻⁶ | tcn_validation_results.json per-subject | 33.36 | MARGINAL |
| 13 | 91% of oracle | derived | 91.5% | PASS |
| 14 | 35/35 subjects benefit | tcn_validation_results.json per_subject | 35/35 verified | PASS |
| 15 | 35 subjects total | data/processed/*.npz shapes | 35 | PASS |
| 16 | 17,283 windows | data/processed/*.npz shapes | 17,283 | PASS |
| 17 | 7 frontal channels | data/processed/train_data.npz shape | (11736,1,7,500) | PASS |
| 18 | 250 Hz | 500 samples = 2s | implied | PASS |
| 19 | 24/5/6 subject splits | npz unique subjects | 24, 5, 6 | PASS |
| 20 | EEGNet R²=0.287 | RESULTS_REPORT.md, CLAUDE.md | stated | PASS |
| 21 | EEGNet params = 1,457 | src/eegnet.py live count | 1,457 | PASS |
| 22 | TCN checkpoint params = 31,043 | tcn_validation_results.json tcn_params | 31,043 | PASS |
| 23 | TCN R²=0.606 (5-seed mean) | experimental/FINDINGS.md | 0.606 ± 0.032 | PASS |
| 24 | Feature ablation: -0.025→0.606 | experimental/FINDINGS.md | documented | PASS |
| 25 | Figure 6 h=5: TCN=0.577, persist=0.104 | horizon_sweep_pac_stim.json | 0.5771, 0.1043 | PASS |
| 26 | Figure 6 h=3: TCN=0.607, persist=0.178 | horizon_sweep_pac_stim.json | 0.6071, 0.1783 | PASS |
| 27 | Figure 6 h=10: TCN=0.669, persist=-0.081 | horizon_sweep_pac_stim.json | 0.6693, -0.0814 | PASS |
| 28 | Fatigue: +0.4% to +5.7% | fatigue_sensitivity.json | 0.388% to 5.653% | PASS |
| 29 | Fatigue: 6 severity levels | fatigue_sensitivity.json | 6 entries | PASS |
| 30 | Result 4 Step g=1.21 | fatigue_model_sensitivity_results.json | 1.214 | PASS |
| 31 | Result 4 Heterogeneous g=1.71 | fatigue_model_sensitivity_results.json | 1.707 | PASS |
| 32 | Result 4 Saturation g=3.66 | fatigue_model_sensitivity_results.json | 3.665 | PASS |
| 33 | Shuffle-label R²=-0.332 | experimental/LAB_NOTEBOOK sources | -0.332 | PASS (source is notebook, not JSON) |
| **F1** | **TCN params in pipeline = 5,154** | **best_multiscale_tcn_lb20_hz5_ts1.pth cfg** | **31,043 (validation model)** | **FLAG** |
| **F2** | **Conclusion R²=0.25 at 5-10s** | **sweep_horizons_results.json** | **Fig 6 shows 0.577-0.669** | **FLAG** |
| **F3** | **Exponential Decay g=2.01** | **fatigue_model_sensitivity_results.json** | **2.313** | **FLAG** |
| **F4** | **5,154 reproducible with current code** | **multiscale_tcn.py ModelConfig** | **7,427 (current code)** | **FLAG** |

---

## Validation Architecture

Note: `workflow.nyquist_validation` is `true` in `.planning/config.json`. This is an audit-only phase that produces only markdown report files. There is no code execution or test infrastructure needed.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None — audit-only phase |
| Config file | None |
| Quick run command | N/A |
| Full suite command | N/A |

### Phase Requirements → Test Map
This phase has no automated tests. Verification is through human review of the audit report deliverable. The planner should include a self-check: after writing the audit report, count the total PASS/FLAG/FAIL cells and confirm they match the 33+ claims in the pre-verified reference card above.

### Wave 0 Gaps
None — no test infrastructure needed.

---

## Sources

### Primary (HIGH confidence)
- `results/tcn_validation_results.json` — controller comparison metrics, per-subject data, Hedges' g values, p-values
- `results/fatigue_sensitivity.json` — fatigue sweep 6 severity levels
- `results/RESULTS_REPORT.md` — comprehensive narrative with all primary statistics
- `results/ablation_table.json` — architecture ablation variants
- `results/effect_sizes_lb20_hz5_ts1.json` — independent effect size computation
- `results/threshold_sweep.json` — threshold sensitivity data
- `results/multiseed_summary.json` — 5-seed reproducibility data
- `experimental/results/horizon_sweep_pac_stim.json` — PAC+Stim horizon sweep (Figure 6 source)
- `experimental/results/pac_stim_focused.json` — source of 5,154-param architecture data
- `rigor/experiments/fatigue_model_sensitivity_results.json` — Result 4 source data
- `src/eegnet.py` — EEGNet architecture (live param count: 1,457)
- `temporal_multiscale/multiscale_tcn.py` — TCN architecture (live param count: 31,043 for validation config)
- `data/processed/*.npz` — dataset window/subject counts
- `data/processed/multiscale_temporal_lb20_hz5_ts1/` — temporal dataset sequence counts

### Secondary (MEDIUM confidence)
- `docs/poster/POSTER_BOARD_V8.md` — authoritative poster specification
- `docs/poster/POSTER_COHERENCE_AUDIT.md` — prior audit (partially stale, still useful)
- `experimental/FINDINGS.md` — source documentation for R²=0.606 5-seed mean
- `models/best_multiscale_tcn_lb20_hz5_ts1.pth` — validation checkpoint metadata (cfg: n_features=73, hidden=64)
- `results/rigor_audit/04_content_accuracy.md` — prior content accuracy audit

### Tertiary (LOW confidence)
- Hardware prices (Muse 2 = $249) — not verifiable from code; externally verifiable

---

## Metadata

**Confidence breakdown:**
- Data accuracy audit: HIGH — all primary claims verified against JSON ground truth with live computation
- Architecture audit: HIGH — parameter counts verified via live Python execution
- Figure content audit: MEDIUM — figure data verified against source JSON but PDF content requires direct reading
- Visual cohesion audit: MEDIUM — spec verified against POSTER_BOARD_V8.md but requires visual inspection of PDF
- Judge-readiness: HIGH — risks identified from systematic inconsistency analysis

**Research date:** 2026-04-07
**Valid until:** 2026-04-09 (CSEF judging date — this research expires after judging)
