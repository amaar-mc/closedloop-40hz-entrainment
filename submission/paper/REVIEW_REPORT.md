# Full-Spectrum Critical Review: Master Synthesis Report

**Date:** 2026-03-18
**Scope:** 7 parallel review agents across 8 divisions
**Source of truth:** Codebase and data files (no code changes permitted)

---

## Executive Summary

| Severity  | Count                      | Action Required                      |
| --------- | -------------------------- | ------------------------------------ |
| CRITICAL  | 19 (14 unique after dedup) | Must fix before submission           |
| IMPORTANT | 28                         | Should fix or explicitly acknowledge |
| MINOR     | 18                         | Fix if time permits                  |
| VERIFIED  | 150+                       | Claims confirmed accurate            |

**Overall assessment:** The paper's core statistical claims are accurate and well-supported. The primary results (72.1% alignment, effect sizes, 35/35 subject benefit) are verified against source data. However, there are significant issues in three areas: (1) the ts=5 vs ts=1 target definition conflation in the abstract and horizon sweep, (2) cross-document inconsistencies between paper/TeX/poster/presentation/supplementary, and (3) potentially unverifiable references. The paper needs revision before submission.

---

## CRITICAL FINDINGS (Deduplicated, Ranked by Severity)

### Tier 1: Factual Errors That Mislead Readers

**CR-01: Abstract conflates ts=5 horizon sweep R² with deployed model performance**

- Divisions: 1+7 (C1, C2), 4+5 (M3)
- Abstract says "TCN maintained R²≈0.25, a +0.5 margin" — this is from the ts=5 (smoothed target) sweep
- Deployed model (ts=1, raw targets) achieves test R²=0.170
- Section 5.6 also mis-labels persistence R²=-0.267 as "ts=1" when it's actually from the ts=5 sweep
- **Fix:** Either report ts=1 numbers in abstract, or explicitly qualify as "under smoothed target evaluation (ts=5)"

**CR-02: References [16] and [17] may be fabricated or unverifiable**

- Division: 2 (C2, C3)
- Ref [16] "PRIME framework" (Barham MP et al.) has a bioRxiv DOI with a date component of Aug 2025
- Ref [17] "Brian Intensify" (Patel V et al.) has arXiv ID 2511.xxxxx (Nov 2025) but is dated "2024"
- Both preprints need verification — if they don't exist, these are fabricated citations
- **Fix:** Verify both references exist. Remove any that cannot be confirmed.

**CR-03: Supplementary materials contain stale/incorrect data**

- Divisions: 1+7 (C3, C4), 1+7 (I3, I4)
- Feature table says "5 bands x 7 channels = 35 + coherence (26)" — should be "4 bands x 7 = 28 + ratios (7) + PAC-structure (21) + global (5)"
- Figure S2 caption says delta-z=0.5 but TCN Predictive uses delta-z=0.3
- Line 146 says "5-second hold time" — should be 3-second
- Line 113 says "EEGNet best checkpoint at epoch 53" — main paper says epoch 53 is TCN only
- **Fix:** Update all four items in SUPPLEMENTARY.md

**CR-04: Fatigue data inconsistency between paper and poster**

- Division: 8 (C4, C5, C6)
- Paper abstract says "six fatigue severity levels"; ABSTRACT.md and poster say "four fatigue model assumptions"
- Paper Section 5.4 shows efficiency improvements +0.4% to +5.7%; poster shows +9.0% to +11.2%
- Poster Result 4 (four fatigue model types with Hedges' g values) has no equivalent in the paper
- These are different analyses presented as though they are the same finding
- **Fix:** Reconcile — either add the four-model analysis to the paper, or align poster to paper's six-level sweep. ABSTRACT.md must match paper abstract.

**CR-05: Clinical utility metric is flawed (Fixed Schedule > TCN > Oracle)**

- Division: 4+5 (C3)
- The composite clinical utility metric gives Fixed Schedule the highest score (0.697) because its lead_time component awards credit for always being on
- Selectively reporting only TCN vs Reactive comparison hides this flaw
- **Fix:** Either redesign the metric, drop it, or report all controllers and acknowledge the limitation

### Tier 2: Methodology/Architecture Omissions

**CR-06: TCN double-SiLU activation not described in paper**

- Division: 3A (C1)
- Code applies SiLU after GroupNorm AND on the residual sum — non-standard design
- Code comment explicitly acknowledges: "This applies SiLU twice... Standard residual blocks typically use a single activation"
- **Fix:** Add to Section 3.5.1: "a second SiLU on the residual sum (retained from trained checkpoint)"

**CR-07: Figure 3 (system architecture) shows "5s hysteresis" — contradicts paper text and code (3s)**

- Divisions: 4+5 (C1), 3B (C1), 8 (C7)
- Paper text, TeX, poster, methodology all say 3-second (correct per validation code)
- Both diagram versions (v3 and v5) show 5s — both are wrong
- CLAUDE.md also says 5-second (stale)
- **Fix:** Regenerate figure with "3 s hysteresis". Update CLAUDE.md.

**CR-08: Reference [1] used for WHO epidemiological statistics**

- Division: 2 (C1)
- "55 million dementia," "$300 billion," "18 billion hours" are WHO/Alzheimer's Association data
- Wang et al. [1] is a gamma oscillation review, not an epidemiology source
- **Fix:** Add proper WHO/Alzheimer's Association citation as primary source

**CR-09: Reference [11] first author likely incorrect**

- Division: 2 (I2)
- "Bhatt DL" is the cardiologist Deepak L. Bhatt — the 2020 J. Neuroscience gamma/neuroimmune paper is from the Tsai/Singer lab
- **Fix:** Verify and correct the first author (likely Adaikkan C)

### Tier 3: Cross-Document Inconsistencies

**CR-10: Paper vs TeX have different section structures**

- Division: 8 (C1, I1, I2)
- MD has standalone Literature Review (Section 2) and Future Directions (Section 7)
- TeX omits Literature Review section entirely, folds Future Directions into Discussion subsection
- All section numbers after the introduction are different
- **Fix:** Decide which structure is for submission and align the other

**CR-11: Architecture count: 8 in paper vs 6 in poster/presentation**

- Division: 8 (C9)
- Paper Table 1 lists 8 models (V1-V8)
- Poster/presentation say "6 architectures" (intentional correction per poster changelog)
- **Fix:** Reconcile — either the paper should say 6 (excluding Ridge baseline and one variant), or poster should say 8

**CR-12: Oracle percentage: 91% in paper vs 92% in poster/presentation**

- Division: 8 (C3)
- 30.5/33.3 = 91.6% — paper rounds to 91%, poster rounds to 92%
- **Fix:** Pick one and apply consistently

**CR-13: Threshold sweep vs main table inconsistency (72.1% vs 73.7% at same delta-z)**

- Division: 4+5 (C2)
- Threshold sweep uses simplified feature construction (stim context all zeros)
- Main validation uses actual stim context features — produces different results
- **Fix:** Either rerun sweep with same features, or note the simplified pipeline in Section 5.5

**CR-14: Presentation says persistence R²=0.81 but that's actually Ridge**

- Division: 8 (I1)
- Persistence at 1s = 0.760; Ridge at 1s = 0.812
- **Fix:** Correct presentation to say "Ridge alone gets 0.81" or "persistence gets 0.76"

---

## IMPORTANT FINDINGS (Top 15)

| ID    | Finding                                                                                                            | Division |
| ----- | ------------------------------------------------------------------------------------------------------------------ | -------- |
| IM-01 | Abstract implies fatigue robustness is from real EEG data — it's simulated                                         | 6, 1+7   |
| IM-02 | Abstract "benefited" implies therapeutic benefit — should say "showed improved alignment"                          | 1+7      |
| IM-03 | Abstract closing overstates: "enables personalized 40 Hz therapy" — should say "enables a computational framework" | 1+7      |
| IM-04 | TCN validation uses ground-truth PAC input, not EEGNet estimates — abstract doesn't caveat                         | 6        |
| IM-05 | Validation on all 35 subjects including 24 training subjects — no separate test-only metrics                       | 6        |
| IM-06 | No negative/null results acknowledged in literature review                                                         | 2        |
| IM-07 | Counterfactual replay causal limitation under-discussed                                                            | 6        |
| IM-08 | Epoch-level PAC label invariance creates classification-like evaluation not discussed                              | 6        |
| IM-09 | g=4.47 for Low-PAC Stim is implausibly large — needs context (algorithmic not clinical superiority)                | 4+5      |
| IM-10 | TCN dropout (0.2) and EEGNet dropout (0.5) omitted from paper                                                      | 3A, 3B   |
| IM-11 | GroupNorm(1, C) is effectively LayerNorm — not specified                                                           | 3A       |
| IM-12 | Portiloop/Lacroix, Rosin, Herron cited inline in Discussion without reference numbers                              | 2        |
| IM-13 | Figure 7 plots Clinical Utility but caption says "Alignment"                                                       | 4+5      |
| IM-14 | "Irreducible noise" claim in Section 4.3 overstates the R²=0.287 ceiling                                           | 1+7      |
| IM-15 | 50 Hz notch filter rationale (Tehran power grid) not stated                                                        | 6        |

---

## VERIFIED CLAIMS (150+ confirmed accurate)

The following core claims were verified across multiple agents and source files:

**Statistics (all match RESULTS_REPORT.md and source JSON):**

- TCN alignment 72.1% vs Reactive 64.5% (g=+1.31 [+0.75, +1.87], p<0.001)
- Low-PAC Stim 82.6% vs 51.7% (g=+4.47 [+3.33, +5.62], p<0.001)
- PAC Gap 30.5 vs 21.1 x10^-6 (g=+1.57 [+0.98, +2.17], p<0.001)
- High-PAC Rest trade-off: 61.6% vs 77.3% (g=-2.41, honestly reported)
- 35/35 subjects benefit (binomial p<0.001)
- All six controller comparison values verified to 3+ significant figures
- All 18 horizon sweep values verified against source JSON

**Architecture (verified against source code):**

- EEGNet: 1,457 parameters (exact count confirmed)
- TCN: 31,043 parameters (exact count confirmed)
- 73 features = 61 spectral + 7 PAC-derived + 5 stim context (code verified)
- Dilations [1,2,4,8], kernel_size=3, receptive field=31 steps
- All EEGNet layer specs (F1=8, D=2, F2=16, kernel_length=64, pool_size 4/8)

**Data pipeline (76 claims verified by Div 3A agent):**

- BIDS format, HDF5 .set + .fdt companion, Fortran order
- 7 frontal channels, 250 Hz, 2s windows, 1s hop
- Bandpass 0.5-80 Hz (4th-order Butterworth, zero-phase)
- Notch 50 Hz (Q=30), artifact zeroing at +/-100 uV before CAR
- Tort 2010 MI: theta 4-8 Hz phase x gamma 38-42 Hz amplitude, 18 bins
- Subject-level splits: 24/5/6 subjects, seed=42, no within-subject leakage
- 17,283 total windows (11,736 + 2,725 + 2,822)

**Training (verified against code):**

- EEGNet: MSE loss, Adam, lr=0.001, patience=15, z-score targets
- TCN: Huber loss (delta=1.0), AdamW, lr=1e-3, weight_decay=1e-3, patience=20
- Both: gradient clipping max_norm=1.0, ReduceLROnPlateau

**Controller (verified against validation code):**

- z-score thresholds +/-0.5, 3-second hysteresis, 30-second rolling baseline
- Six strategies compared: Fixed, Reactive, TCN Predictive, Hybrid, PI, Oracle
- Wilcoxon signed-rank (appropriate for N=35 paired), Hedges' g with bias correction

**Honest reporting (verified):**

- Paper acknowledges counterfactual (not live) validation
- Paper acknowledges EEGNet not in validation loop
- Paper acknowledges single-dataset limitation
- Paper reports trade-offs (High-PAC Rest Rate, higher stim %)
- Paper reports R²=0.287 static ceiling and discusses causes

---

## RECOMMENDED ACTION

**The paper needs targeted revision, not a rewrite.** The core results are sound and thoroughly verified. The issues fall into four actionable categories:

### Category A: Must Fix (submission-blocking)

1. Verify references [16] and [17] exist — remove if fabricated
2. Fix SUPPLEMENTARY.md (4 stale values)
3. Reconcile ts=5 vs ts=1 in abstract and Section 5.6
4. Regenerate Figure 3 with "3s hysteresis"
5. Reconcile fatigue claims between paper/poster/abstract
6. Fix or drop clinical utility metric

### Category B: Should Fix (reviewer would flag)

7. Add TCN dropout (0.2) and EEGNet dropout (0.5) to paper
8. Describe double-SiLU activation pattern
9. Qualify abstract language ("enables a framework" not "enables therapy")
10. Add context for g=4.47 (algorithmic superiority)
11. Add negative/null 40 Hz entrainment literature
12. Fix reference [11] first author
13. Add inline-cited papers (Portiloop, Rosin, Herron) as numbered references

### Category C: Should Reconcile (cross-document)

14. Align paper vs TeX section structure
15. Align architecture count (8 vs 6) across all documents
16. Align oracle percentage (91% vs 92%)
17. Fix threshold sweep discrepancy or explain it
18. Fix Figure 7 caption (Clinical Utility, not Alignment)
19. Fix presentation persistence R² (0.76, not 0.81)

### Category D: Acknowledge in Paper (transparency)

20. State that Hedges' g uses pooled-SD (independent) not paired formulation
21. Specify GroupNorm(1, C) = LayerNorm
22. State delta_z=0.3 was used in primary comparison
23. Note epoch-level PAC label granularity effect on alignment metrics
24. Report anticipation rate (88.2% vs 90.1% — Reactive wins)

---

_Report generated: 2026-03-18_
_7 review agents, 8 divisions, ~700K tokens of analysis_
