---
gsd_state_version: 1.0
milestone: v4.0
milestone_name: CSEF Submission
status: completed
stopped_at: Completed 18-lab-notebook-comprehensive-rewrite/18-01-PLAN.md
last_updated: "2026-04-10T10:16:10.568Z"
last_activity: 2026-04-10 — Completed 18-01 lab notebook validation + final PDF regeneration
progress:
  total_phases: 3
  completed_phases: 3
  total_plans: 8
  completed_plans: 8
  percent: 100
---

# Project State: Research Documentation Project

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-20)

**Core value:** Every claim in every document must be verifiably accurate against actual code, data, and results.
**Current focus:** v3.0 Deepen Research — Phase 14: Scope Lock Completion

## Current Position

Phase: 18 (Lab Notebook Comprehensive Rewrite)
Plan: 1 of 1 in current phase
Status: Complete
Last activity: 2026-04-10 — Completed 18-01 lab notebook validation + final PDF regeneration

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**
- Total plans completed: 0 (v3.0)
- Average duration: unknown
- Total execution time: 0h

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

*Updated after each plan completion*
| Phase 11-real-time-inference-pipeline P01 | 239 | 1 tasks | 3 files |
| Phase 11-real-time-inference-pipeline P02 | 35 | 2 tasks | 5 files |
| Phase 11-real-time-inference-pipeline P03 | 2100 | 2 tasks | 3 files |
| Phase 12-architecture-comparison-study P02 | 23 | 2 tasks | 4 files |
| Phase 12-architecture-comparison-study P01 | 102 | 2 tasks | 4 files |
| Phase 12.1-improved-tcn-enhanced-features-multi-task-self-attention P01 | 18 | 1 tasks | 3 files |
| Phase 12.1-improved-tcn-enhanced-features-multi-task-self-attention P02 | 7 | 2 tasks | 5 files |
| Phase 13 P01 | 196 | 2 tasks | 6 files |
| Phase 13 P02 | 32 | 3 tasks | 1 files |
| Phase 13 P03 | 12 | 3 tasks | 8 files |
| Phase 14-scope-lock-completion P02 | 88 | 1 tasks | 1 files |
| Phase 16-csef-documentation-and-presentation-package P02 | 4 | 2 tasks | 2 files |
| Phase 16-csef-documentation-and-presentation-package P03 | 5 | 2 tasks | 3 files |
| Phase 16 P04 | 7 | 2 tasks | 2 files |
| Phase 16-csef-documentation-and-presentation-package P01 | 3 | 2 tasks | 3 files |
| Phase 16-csef-documentation-and-presentation-package P05 | 6 | 2 tasks | 7 files |
| Phase 17-poster-board-deep-audit-data-accuracy-figures-visual-cohesion-and-judge-readiness P02 | 4 | 2 tasks | 2 files |
| Phase 17-poster-board-deep-audit-data-accuracy-figures-visual-cohesion-and-judge-readiness P01 | 8 | 2 tasks | 2 files |
| Phase 18-lab-notebook-comprehensive-rewrite P01 | 5 | 2 tasks | 4 files |

## Accumulated Context

### Key Decisions

- Roadmap: Keep Streamlit — no React/FastAPI rewrite for v3.0. Production stack is presentation narrative only.
- Roadmap: Dual-mode confirmed — simulated EEG is primary PAC control path; Muse 2 for alpha/theta viz only (consumer EEG gamma unreliable).
- Roadmap: Phase 10 must complete before Phase 11 — 4-channel channel mapping is a hard prerequisite for StreamingFeatureExtractor.
- Roadmap: RSRCH-04 simulator defense = fit_simulator_params.py or cite Iaccarino et al. (2016) τ values — "empirically extracted" claim is a live judging risk.
- 11-01: PAC parity test uses valid-range checks — causal sosfilt vs non-causal two-pass is a systematic algorithmic difference, not a tolerance matter.
- 11-01: src/streaming/__init__.py conditional import for adapters.py so package remains importable before Plan 03 implements hardware adapters.
- 11-03: Muse 2 BLE non-viable on Darwin 25.4.0 (BOARD_NOT_READY_ERROR:7 — BLE not enabled); SimulatedEEGAdapter confirmed as shipping demo path (RTINF-02, RTINF-03 complete).
- 11-03: demo_streaming.py --source muse falls back to simulated with warning — never attempts board connection on unpaired host.
- 12.1-02: norm_first=True in TransformerEncoderLayer — pre-LayerNorm for stable gradients; per-subject causal trailing mean for auxiliary smooth targets prevents cross-subject NPZ contamination.
- 12.1-02: 4ch ImprovedTCN beats baseline (+0.054 R2 at hz=5); 7ch degrades (-0.195) — 2.3x more params overfit at same 11K dataset size. Evaluation uses future head only for apples-to-apples baseline comparison.
- 13-01: Model artifacts tracked in models/muse_4ch/ subdirectory — gitignore models/*.pth only catches top-level, no exception needed.
- 13-01: 3 demo patients with (Demo) suffix and realistic PAC ranges (0.000045-0.000068) matching actual dataset values.
- 13-02: EEGNet constructor uses n_samples=500 (not n_times) and no n_classes -- actual class signature differs from plan spec.
- 13-02: 40 Hz click-train WAV via scipy.io.wavfile cached with st.cache_data; Real EEG Mode toggle disabled with BLE tooltip (APP-03).
- 13-03: Elevator pitch framed as "predictive model for neural state" not "AI for Alzheimer's" — scientifically honest framing for CSEF judges.
- 13-03: Clinical roadmap uses 3-phase approach (observational, feasibility, comparative) matching real clinical trial design.
- 13-03: QR generation and PDF generation split into separate CLI scripts for independent re-runs when URLs change.
- 14-02: Used dedicated 4ch TCN run R2=0.156 (not sweep 0.112) as primary comparison number -- dedicated run more representative.
- 14-02: Baseline-relative comparison (TCN vs persistence gain) is the honest metric across configurations with different PAC labels.
- 16-01: Scripts 01-04 and 04_qa_bank already had correct PAC+Stim numbers from prior work — only 05_qa_complete.md and both elevator pitch files needed updating.
- 16-01: docs/ and CSEF/ elevator pitch copies kept byte-identical per project convention; elevator pitch script tightened to ~130 words to fit 60s constraint.
- 16-03: 12 PAC+Stim features (not 73) is the correct model description — feature ablation study raises test R2 from -0.025 to 0.606.
- 16-03: Productization section replaces generic future-work in Conclusions — caregiver app (HF Spaces) + 3-phase clinical roadmap (observational, feasibility, comparative).
- 18-01: Notebook rewrite was staged earlier today in-place; Task 1 ran validation-only (all 17 checks passed, zero surgical fixes required). Audit dimensions covered: em-dashes, code params (tau_e/onset_tau_sec/hold_time_sec), Fortunato [8], hysteresis, TCN param labeling, horizon sweep persistence, controller results (72.1/82.6/91), feature ablation, clinical depth.
- 18-01: Added Fortunato [8] to PDF generator refs list and renumbered extension refs (Murdock->[9], Soula->[10], TRIBE V2->[11]) so PDF numbering matches notebook body. Kept hardcoded ref list rather than parsing markdown References section.
- 18-01: Verified PDF content via pypdf text extraction (0 em-dashes, Fortunato present, all TCN param variants, all key numerical claims) instead of visual inspection — deterministic and greppable.

### Roadmap Evolution
- Phase 12.1 inserted after Phase 12: Improved TCN: Enhanced Features + Multi-Task + Self-Attention (URGENT)
- Phase 16 added: CSEF Documentation and Presentation Package (v4.0 milestone)
- Phase 17 added: Poster board deep audit — data accuracy, figures, visual cohesion, and judge-readiness
- Phase 18 added: Lab Notebook Comprehensive Rewrite — score 95+ on all audit dimensions, fix code/poster alignment, add clinical depth

### Blockers/Concerns

- Muse S BLE not viable on current macOS 25.x host — resolved: simulated mode ships, full hardware implementation retained in RealEEGAdapter for future BLE-enabled system.
- pytorch-forecasting + existing torch version compatibility unverified — use lightweight custom Transformer if conflict.
- Hard deadline: CSEF judging 2026-04-11 (Saturday). Lab notebook validated and final PDF regenerated 2026-04-10.

## Session Continuity

Last session: 2026-04-10T10:05:30Z
Stopped at: Completed 18-lab-notebook-comprehensive-rewrite/18-01-PLAN.md
Resume file: None
