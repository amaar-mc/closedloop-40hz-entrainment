---
phase: 06-write-research-paper
plan: "03"
subsystem: paper-writing
tags: [methods, architecture-search, EEGNet, TCN, PAC, research-paper]
dependency_graph:
  requires: []
  provides:
    - docs/paper/sections/04-methods.md
    - docs/paper/sections/05-architecture-search.md
  affects:
    - docs/paper/sections/06-results.md
    - docs/paper/sections/07-discussion.md
tech_stack:
  added: []
  patterns:
    - venue-agnostic academic writing
    - table-first architecture comparison format
    - IMRAD section structure
key_files:
  created:
    - docs/paper/sections/04-methods.md
    - docs/paper/sections/05-architecture-search.md
  modified: []
decisions:
  - "Methods written with reproducibility-grade detail across all 8 subsections; all numbers sourced from CURRENT_METHODOLOGY.md"
  - "Architecture search uses table-first format per research doc recommendation; V1-V8 described chronologically in both table and prose"
  - "Synthesis subsection (5.5) added with three lessons distilled from search — improves narrative flow from static ceiling to temporal pivot"
metrics:
  duration: "5 minutes"
  completed: "2026-03-15"
  tasks_completed: 2
  files_created: 2
---

# Phase 6 Plan 3: Methods and Architecture Search Sections Summary

**One-liner:** Reproducibility-grade Methods section (8 subsections, 268 lines) plus Architecture Search section presenting systematic 8-model comparison that frames R²=0.287 as a data ceiling motivating temporal prediction.

---

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Write Methods section | 40c0f24 | docs/paper/sections/04-methods.md |
| 2 | Write Architecture Search section | d8a1bcc | docs/paper/sections/05-architecture-search.md |

---

## Artifacts Produced

### `docs/paper/sections/04-methods.md` (268 lines)

Complete Methods section with 8 subsections:

- **4.1 Dataset and Preprocessing** — OpenNeuro ds005048 v1.0.1, 35 dementia patients, 19 channels at 250 Hz, BIDS format, 7 frontal channels, bandpass/notch/artifact rejection/CAR preprocessing pipeline, 2s sliding windows, subject-level splits (24/5/6), 17,283 total windows.
- **4.2 Phase-Amplitude Coupling Computation** — Modulation Index (Tort 2010), theta (4–8 Hz) × gamma (38–42 Hz), epoch-level computation assigned to windows, dimensionless MI units (range 6×10⁻⁶ to 7×10⁻⁴).
- **4.3 Static PAC Estimation: EEGNet** — 1,457 parameters, MSE loss, Adam, ReduceLROnPlateau, gradient clipping, best epoch=53, R²=0.287.
- **4.4 Feature Engineering** — 73-dimensional causal feature vector: 61 spectral (5 bands × 7 channels + coherence) + 7 PAC-derived (current, MA2/4/8/16, diff1/4) + 5 stimulation context features.
- **4.5 Temporal PAC Forecasting: MultiscaleCausalTCN** — 31,043 parameters, causal depthwise-separable convs with dilations [1,2,4,8], GroupNorm, attention pooling, dual heads, Huber loss, patience=20, best epoch=53, R²=0.170 at 5s horizon.
- **4.6 Closed-Loop Controller Design** — PersonalizationModule (30s rolling baseline), z-score thresholds (±0.5), 5s hysteresis, 6 controller variants (Fixed Schedule, Reactive, TCN Predictive, Hybrid, PI Controller, Oracle).
- **4.7 Validation Protocol** — Offline counterfactual replay on all 35 subjects; ground-truth PAC as TCN input to isolate predictive contribution; 4 metrics (Alignment, Low-PAC Stim Rate, High-PAC Rest Rate, PAC Gap).
- **4.8 Statistical Analysis** — Wilcoxon signed-rank (paired, N=35), Hedges' g with 95% BCa bootstrap CIs, binomial test for per-subject breadth, threshold sensitivity sweep (0.2–1.0).

### `docs/paper/sections/05-architecture-search.md` (107 lines)

Architecture Search section with 5 subsections:

- **5.1 Problem Framing** — Clinical motivation for static prediction, systematic Feb 5–16 search.
- **5.2 8-Model Comparison Table** — Clean table-first format with all 8 models (V1-V8); prose narrative for each highlighting key discoveries.
- **5.3 R²=0.287 Data Ceiling** — Framed as scientific finding analogous to Bayes error rate; epoch-level label assignment as structural cause; 135-parameter Ridge equaling 1.1M-parameter ViT as proof.
- **5.4 Temporal Prediction Pivot** — Constructive implication: PAC dynamics (5–10s) may be predictable even when instantaneous PAC is bounded; autocorrelation, stimulation context, and spectral precursors as motivating evidence.
- **5.5 Synthesis: Lessons from Architecture Search** — Three distilled lessons shaping TCN design: (1) feature quality dominates, (2) spectral features are near-optimal for instantaneous prediction, (3) relevant signal is temporal not instantaneous.

---

## Accuracy Verification

All critical numbers cross-checked against `docs/methodology/CURRENT_METHODOLOGY.md` and `docs/methodology/CODE_MAP.md`:

| Claim | Source | Verified |
|-------|--------|---------|
| TCN patience=20 | CURRENT_METHODOLOGY.md §4.3 | PASS |
| EEGNet loss=MSE | CURRENT_METHODOLOGY.md §4.1 | PASS |
| Best epoch=53 | CURRENT_METHODOLOGY.md §4.3 | PASS |
| PAC dimensionless MI units | CURRENT_METHODOLOGY.md §3.1 | PASS |
| "counterfactual replay" | Methods 4.7 | PASS |
| R²=0.287 ceiling | CODE_MAP.md Model Zoo | PASS |
| V1-V8 R² values | CODE_MAP.md Model Zoo | PASS |
| No "µV²" for PAC | — | PASS (0 instances) |
| No Synopsys/CSEF | — | PASS (0 instances) |
| Methods ≥250 lines | wc -l = 268 | PASS |
| Arch Search ≥100 lines | wc -l = 107 | PASS |

---

## Deviations from Plan

### Auto-added: Section 5.5 Synthesis

**Found during:** Task 2 — Architecture Search section was 93 lines, below the 100-line minimum.

**Fix:** Added a Section 5.5 "Synthesis: Lessons from the Architecture Search" that distills three actionable lessons from the V1-V8 exploration and connects them explicitly to the TCN design decisions. This improves narrative cohesion while satisfying the length requirement.

**Files modified:** `docs/paper/sections/05-architecture-search.md`

**Rule:** Rule 2 (missing critical functionality — minimum length requirement not met).

---

## Self-Check

**Checking created files exist:**
- `docs/paper/sections/04-methods.md` — FOUND (committed at 40c0f24)
- `docs/paper/sections/05-architecture-search.md` — FOUND (committed at d8a1bcc)

**Checking commits exist:**
- 40c0f24 — Task 1 Methods section commit
- d8a1bcc — Task 2 Architecture Search section commit

## Self-Check: PASSED
