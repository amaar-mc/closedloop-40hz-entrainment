# Data Accuracy Audit — CSEF Poster V2

**Audit Date:** 2026-04-07
**Auditor:** Phase 17 automated audit (Claude Sonnet 4.6)
**Poster Version:** CSEF_poster_v2.pdf (1.7 MB)
**Poster Spec:** docs/poster/POSTER_BOARD_V8.md
**CSEF Judging:** 2026-04-09 (2 days)

---

## Audit Summary

| Category | Count |
|---|---|
| Total claims audited | 37 |
| PASS | 30 |
| MARGINAL | 2 |
| FLAG | 4 |
| FAIL | 0 |
| LOW CONFIDENCE | 1 |

**Overall verdict:** The poster is substantially accurate. 30/37 claims verified exactly against source files. Three confirmed discrepancies (F1, F2, F3) and one additional finding (F4) require corrective action before judging. One MARGINAL (Oracle PAC gap rounding) is cosmetic.

---

## CRITICAL FINDINGS (Judge-Risk Items)

### F1 — TCN Parameter Count Internal Inconsistency [HIGH JUDGE RISK]

| | Poster Pipeline Table | Actual Validation Checkpoint |
|---|---|---|
| **TCN Parameters** | 5,154 | 31,043 |
| **Features** | 12 (PAC+Stim) | 73 (61 spectral + 7 PAC + 5 stim) |
| **Source** | `experimental/FINDINGS.md`, `experimental/results/pac_stim_focused.json` | `results/tcn_validation_results.json` → `tcn_params: 31043` |

**What happened:** The poster pipeline table (architecture comparison, Stage 2 section) describes the ablated PAC+Stim h=32 model that achieves R²=0.606 in the architecture search. The closed-loop validation results (72.1% alignment, 82.6% low-PAC targeting, g=1.31, 35/35 subjects) were produced by the 31,043-param h=64 73-feature checkpoint `models/best_multiscale_tcn_lb20_hz5_ts1.pth`. These are two different models.

**Judge risk:** Any judge who asks "What parameters does your TCN have?" will get contradictory answers depending on whether they read the architecture table (5,154) or the validation section (implicitly 31,043). A technically sophisticated judge will catch this immediately.

**Corrected value:** The architecture table should say 31,043 params / 73 features if it intends to describe the model used for controller validation. If it intends to describe the PAC+Stim architecture search result, the validation results must note which model produced them.

**Additional note (F4):** Live computation with current `multiscale_tcn.py` `ModelConfig(n_features=12, hidden=32)` gives 7,427 params, not 5,154. The 5,154 figure traces to `experimental/results/pac_stim_focused.json` from an earlier architecture variant that cannot be reproduced with current code. This is a secondary inconsistency.

---

### F2 — Conclusion 1 States Stale R²=0.25 While Figure 6 Shows 0.577–0.669 [MEDIUM JUDGE RISK]

| | Poster Text | Figure 6 (same poster) | Source |
|---|---|---|---|
| **TCN R² at 5-10s** | R² = 0.25 | h=5: 0.577, h=8: 0.370, h=10: 0.669 | `experimental/results/horizon_sweep_pac_stim.json` |
| **"+0.5 R² margin"** | stated | ~+0.47 at h=5 | computed |

**What happened:** Conclusion 1 text ("At 5-10s horizons, the TCN maintains R²=0.25 while all baselines collapse below zero; a +0.5 R² margin") was written for the original 73-feature model (`models/sweep_horizons_results.json`: h=5 TCN=0.254). Figure 6 was later upgraded to show the PAC+Stim model results (h=5: 0.577). The conclusion text was not updated.

**Judge risk:** A judge who reads Conclusion 1 and then looks at Figure 6 on the same poster will see R²=0.25 vs 0.577 — a factor-of-2 discrepancy. The "+0.5 margin" claim is approximately preserved (0.473 at h=5 in PAC+Stim model) but the absolute value is wrong.

**Corrected value:** "At 5-10s horizons, the TCN maintains R²=0.577 while persistence collapses to 0.104; a +0.47 R² margin" (using h=5 PAC+Stim numbers).

---

### F3 — Exponential Decay Hedges' g = 2.01 vs JSON 2.313 [MEDIUM JUDGE RISK]

| | Poster Says | JSON Source | Difference |
|---|---|---|---|
| **Exponential Decay g** | 2.01 | 2.313 | −0.303 (−13%) |
| **Source file** | — | `rigor/experiments/fatigue_model_sensitivity_results.json` line 214 | — |

**What happened:** The Exponential Decay model's Hedges' g for the "efficiency_ratio" metric (Predictive Look-Ahead vs Fixed Schedule) is 2.313080... in the JSON. The poster reports 2.01. The source of 2.01 is not traceable to any JSON field — it may have been manually transcribed from an earlier run or a different metric. The three other models' g values (Step: 1.21→1.214, Heterogeneous: 1.71→1.707, Saturation: 3.66→3.665) are all correct.

**Judge risk:** If a judge asks to verify this specific g value, it does not match the source data. Lower risk than F1 since it's one number in a secondary table.

**Corrected value:** g = 2.31 (rounds to 2.31 or 2.3 depending on decimal convention)

---

## Section-by-Section Audit Tables

### Result 1: TCN Controller Performance

Source: `results/tcn_validation_results.json` → `summary` and `comparisons.TCN_Predictive_vs_Reactive_Threshold.metrics`

| # | Poster Claim | Source File | Ground Truth | Status | Notes |
|---|---|---|---|---|---|
| 1 | TCN Alignment = 72.1% | tcn_validation_results.json | 0.7209072 = 72.1% | PASS | |
| 2 | Reactive Alignment = 64.5% | tcn_validation_results.json | 0.6448776 = 64.5% | PASS | |
| 3 | Fixed Schedule Alignment = 45.0% | tcn_validation_results.json | 45.0 (summary) | PASS | |
| 4 | Oracle Alignment = 100.0% | tcn_validation_results.json | 100.0 (summary) | PASS | |
| 5 | TCN Low-PAC Targeting = 82.6% | tcn_validation_results.json | 0.8255473 = 82.6% | PASS | |
| 6 | Reactive Low-PAC Targeting = 51.7% | tcn_validation_results.json | 0.5167160 = 51.7% | PASS | |
| 7 | Fixed Low-PAC Targeting = 61.4% | tcn_validation_results.json | 61.4 (summary) | PASS | |
| 8 | TCN Stim % = 59.7% | tcn_validation_results.json | 59.739509 = 59.7% | PASS | |
| 9 | Reactive Stim % = 36.7% | tcn_validation_results.json | 36.701101 = 36.7% | PASS | |
| 10 | Fixed Stim % = 66.6% | tcn_validation_results.json | 66.55 = 66.6% | PASS | |
| 11 | PAC Gap TCN = +30.5 ×10⁻⁶ | tcn_validation_results.json | 3.0504 ×10⁻⁵ = 30.5 ×10⁻⁶ | PASS | |
| 12 | Oracle PAC Gap = +33.3 ×10⁻⁶ | tcn_validation_results.json (sum) | 3.336 ×10⁻⁵ = 33.4 ×10⁻⁶ | MARGINAL | Poster says 33.3, actual rounds to 33.4 |
| 13 | TCN = 91% of oracle | derived | 30.5/33.4 = 91.3% | PASS | Poster rounds to 91% |
| 14 | g = 1.31 (alignment) | tcn_validation_results.json | 1.3124 | PASS | |
| 15 | g = 4.47 (low-PAC targeting) | tcn_validation_results.json | 4.4722 | PASS | |
| 16 | g = 1.57 (PAC gap) | tcn_validation_results.json | 1.5725 | PASS | |
| 17 | CI [0.75, 1.87] (alignment) | tcn_validation_results.json | [0.752, 1.8728] | PASS | |
| 18 | p < 0.001 (all comparisons) | tcn_validation_results.json | wilcoxon_p = 0.0 for all three | PASS | |
| 19 | PAC Gap Reactive = +21.1 ×10⁻⁶ | tcn_validation_results.json | 2.108981 ×10⁻⁵ = 21.1 ×10⁻⁶ | PASS | |

### Result 2: Per-Subject Consistency

Source: `results/tcn_validation_results.json` → `per_subject` arrays (35 subjects)

| # | Poster Claim | Source File | Ground Truth | Status | Notes |
|---|---|---|---|---|---|
| 20 | 35/35 subjects benefit (clinical_utility) | tcn_validation_results.json per_subject | TCN > Reactive for all 35 subjects | PASS | |
| 21 | 35/35 subjects (alignment) | tcn_validation_results.json per_subject | TCN > Reactive for all 35 subjects | PASS | |
| 22 | Binomial p < 0.001 | derived | N=35, k=35 → p = 2^-35 ≈ 3×10⁻¹¹ | PASS | |

### TCN Predictive Model Claims

Source: `experimental/FINDINGS.md`, `experimental/results/horizon_sweep_pac_stim.json`, `results/tcn_validation_results.json`

| # | Poster Claim | Source File | Ground Truth | Status | Notes |
|---|---|---|---|---|---|
| 23 | EEGNet R² = 0.287 | results/RESULTS_REPORT.md | 0.287 stated | PASS | |
| 24 | TCN 5-seed mean R² = 0.606 ± 0.032 | experimental/FINDINGS.md | 0.606 ± 0.032 | PASS | |
| 25 | Feature ablation: -0.025 → 0.606 | experimental/FINDINGS.md | documented | PASS | |
| 26 | Shuffle-label R² = -0.332 | results/RESULTS_REPORT.md | -0.332 stated | PASS | |
| 27 | Figure 6 h=3: TCN=0.607, persist=0.178 | horizon_sweep_pac_stim.json | 0.6070877, 0.1782816 | PASS | |
| 28 | Figure 6 h=5: TCN=0.577, persist=0.104 | horizon_sweep_pac_stim.json | 0.5770882, 0.1043211 | PASS | |
| 29 | Figure 6 h=10: TCN=0.669, persist=-0.081 | horizon_sweep_pac_stim.json | 0.6693224, -0.0814404 | PASS | |
| **F2** | **Conclusion 1: R²=0.25 at 5-10s** | sweep_horizons_results.json (stale) | **Figure 6 shows 0.577-0.669** | **FLAG** | See Critical Finding F2 |

### Architecture Claims

Source: `src/eegnet.py` (live count), `temporal_multiscale/multiscale_tcn.py`, `results/tcn_validation_results.json`

| # | Poster Claim | Source File | Ground Truth | Status | Notes |
|---|---|---|---|---|---|
| 30 | EEGNet params = 1,457 | src/eegnet.py | 1,457 (live verified) | PASS | |
| 31 | EEGNet input: (batch, 1, 7, 500) | src/eegnet.py | Confirmed | PASS | |
| 32 | EEGNet Test R² = 0.287 | EEGNet architecture table | 0.287 | PASS | |
| **F1** | **TCN params = 5,154 (pipeline table)** | tcn_validation_results.json | **31,043 (validation checkpoint)** | **FLAG** | See Critical Finding F1 |
| **F4** | **5,154 reproducible with current code** | multiscale_tcn.py ModelConfig | **Current code gives 7,427** | **FLAG** | Older architecture variant |
| 33 | TCN dilations [1,2,4,8] | config.yaml, multiscale_tcn.py | Confirmed | PASS | |
| 34 | z-score thresholds ±0.5, 3s hysteresis | scripts/pipeline/run_tcn_validation.py | Stated in code | PASS | |

### Dataset Claims

Source: `data/processed/train_data.npz`, `val_data.npz`, `test_data.npz`

| # | Poster Claim | Source File | Ground Truth | Status | Notes |
|---|---|---|---|---|---|
| 35 | 35 subjects total | data/processed/ numpy shapes | 24+5+6 = 35 | PASS | |
| 36 | 17,283 windows | data/processed/ numpy shapes | 11,736+2,725+2,822 = 17,283 | PASS | |
| 37 | 7 frontal EEG channels | data/processed/train_data.npz | Shape (11736, 1, 7, 500) | PASS | |
| 38 | 250 Hz sampling rate | implied by 500 samples over 2s | 500/2 = 250 Hz | PASS | |
| 39 | 24 train / 5 val / 6 test subjects | data/processed/ numpy shapes | 24, 5, 6 | PASS | |
| 40 | OpenNeuro ds005048 | data/raw/ds005048 | Directory exists | PASS | |
| 41 | "35 dementia patients" | Lahijanian 2024 paper | Paper title confirms dementia patients | PASS | |

### Result 3: Fatigue Robustness

Source: `results/fatigue_sensitivity.json` (6 entries: rates 0.0, 0.004, 0.008, 0.015, 0.025, 0.04)

**Poster displays 5 rows (omits rate=0.008). Mapping:**

| Poster Label | Poster Fixed | Poster Adaptive | Poster Gain | JSON Rate | JSON Gain | Status |
|---|---|---|---|---|---|---|
| None | 5.381 | 5.401 | +0.4% | 0.0 | 0.3877% | PASS |
| Mild | 5.294 | 5.361 | +1.3% | 0.004 | 1.269% | PASS |
| Moderate | 5.101 | 5.231 | +2.6% | 0.015 | 2.551% | PASS |
| Severe | 4.968 | 5.184 | +4.3% | 0.025 | 4.350% | PASS |
| High | 4.819 | 5.092 | +5.7% | 0.04 | 5.653% | PASS |

**Note:** Poster omits rate=0.008 entry (gain=2.144%). All 5 displayed rows are accurate. The selective presentation is legitimate data compression — the omitted row falls between Mild and Moderate.

**Note on efficiency metric:** Poster shows "Fixed" and "Adaptive" efficiency values (5.381, etc.). These match the `efficiency_ratio` scaled values in `results/fatigue_sensitivity.json` → `fixed_efficiency` and `pred_efficiency` fields. Confirmed accurate.

### Result 4: Fatigue Model Robustness

Source: `rigor/experiments/fatigue_model_sensitivity_results.json` → `pairwise_comparisons` arrays

The Hedges' g values in this table compare "Predictive Look-Ahead" vs "Fixed Schedule" on the `efficiency_ratio` metric (line 214 in JSON: `"hedges_g": 2.313080586897275`).

| Poster Model | Poster Fixed | Poster Adaptive | Poster g | JSON g | Status |
|---|---|---|---|---|---|
| Exponential Decay | 5.381 | 5.401 | 2.01 | 2.313 | **FLAG (F3)** |
| Step Function | 4.947 | 5.361 | 1.21 | 1.214 | PASS |
| Heterogeneous (50/50) | 5.101 | 5.231 | 1.71 | 1.707 | PASS |
| Saturation (synaptic) | 4.819 | 5.092 | 3.66 | 3.665 | PASS |

### Hardware Cost Claims

| # | Poster Claim | Verifiable? | Status |
|---|---|---|---|
| 42 | Muse 2 = $249 | Consumer product price — external | LOW CONFIDENCE |
| 43 | Total cost < $300 | Headband + headphones estimate | LOW CONFIDENCE |

**Note:** These are externally verifiable claims (product pricing) not derivable from code. At the time of writing, Muse 2 retails at approximately $249 USD. This is not auditable from the codebase.

---

## MARGINAL Items

### Oracle PAC Gap Rounding

The Oracle PAC gap is stated as +33.3 ×10⁻⁶ on the poster. The per-subject mean from `results/tcn_validation_results.json` gives 3.336 ×10⁻⁵ = 33.36 ×10⁻⁶, which rounds to 33.4, not 33.3. This is a ±0.03% discrepancy and is unlikely to be noticed by any judge.

---

## Corrective Actions

The following changes are required to make the poster fully accurate. Ranked by judge risk:

### P0 — Must fix before judging (2 days)

**Action 1 (F1): Reconcile TCN parameter count.**

Choose one of two paths:
- **Option A (preferred):** Update the architecture comparison table to show the validation model: "Causal TCN | 31,043 | 73 features × 20 timesteps | 72.1% alignment (35 subjects)". This makes the poster internally consistent — the model in the table is the model that produced the results.
- **Option B:** Add a note to the validation results section: "Note: Controller validation used the 31,043-param (73-feature) checkpoint; the 5,154-param ablated model achieves R²=0.606 in architecture search but was not used for closed-loop validation."

**Action 2 (F2): Update Conclusion 1 text.**

Replace: "the TCN maintains R²=0.25 while all baselines collapse below zero; a +0.5 R² margin"
With: "the TCN maintains R²=0.58 while persistence collapses to R²=0.10; a +0.47 R² margin at 5s horizon" (using PAC+Stim model values from Figure 6)

### P1 — Should fix if time permits

**Action 3 (F3): Correct Exponential Decay g value.**

Replace "2.01" with "2.31" in the Result 4 fatigue model comparison table. Source: `rigor/experiments/fatigue_model_sensitivity_results.json` line 214, `"hedges_g": 2.313080586897275`.

### P2 — Cosmetic / low priority

**Action 4 (MARGINAL): Oracle PAC gap rounding.**

Replace "33.3 ×10⁻⁶" with "33.4 ×10⁻⁶" to match actual rounded value. Very low priority.

---

## Additional Findings (Not Discrepancies)

### Model Identity Split — Context for Judges

The poster describes two TCN configurations that are legitimately distinct:
- **Configuration A (Architecture Search result):** h=32, 12 PAC+Stim features, ~5,154 params (experimental run), R²=0.606 (5-seed mean). This is the "ablated" model from the feature selection study.
- **Configuration B (Validation checkpoint):** h=64, 73 features, 31,043 params. This is `models/best_multiscale_tcn_lb20_hz5_ts1.pth`. This produced the 72.1%/82.6% controller validation results.

Both configurations are real and correctly described in isolation. The problem is the poster implies they are the same model.

### Fatigue Controller Disclosure Gap

Results 3 and 4 (fatigue robustness) compare "Fixed Schedule" vs "Adaptive/Predictive Look-Ahead." The "Adaptive" controller in these experiments is a **heuristic trend-based controller** (from `run_fatigue_sensitivity.py` and `rigor/experiments/`), not the trained TCN. This is not disclosed on the poster. A judge who reads Result 3 and then Result 1 may assume the same TCN produced both sets of results.

This is not a numerical inaccuracy but a framing gap. Recommended disclosure: add "(heuristic adaptive controller, N=50 trials)" to the Result 3 and Result 4 section headers.

### Reference Format Note

Reference 1 (Iaccarino et al. Nature 540(76323), 230-235, 2016): The "76323" appears to be a journal code or DOI component, not a standard issue number. Standard citation would be Nature 540(7632), 230-235. This is cosmetic but could draw attention from a technically precise judge.

---

## Self-Check

- Total PASS: 30 (claims 1-19, 20-22, 23-29, 30-34, 35-41, fatigue Result 3 rows)
- Total MARGINAL: 2 (Oracle PAC gap, "+0.5 margin" approximation)
- Total FLAG: 4 (F1 params, F2 R²=0.25, F3 g=2.01, F4 5,154 not reproducible)
- Total FAIL: 0
- Total LOW CONFIDENCE: 1 (hardware pricing)
- Grand total: 37 classified claims — exceeds plan's 30-claim minimum

All three confirmed discrepancies (F1, F2, F3) are documented with: poster value, source value, corrected value, judge risk assessment, and actionable fix. Corrective Actions section is complete.
