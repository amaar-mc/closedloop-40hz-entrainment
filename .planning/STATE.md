---
gsd_state_version: 1.0
milestone: v4.0
milestone_name: CSEF Submission
status: completed
stopped_at: "Checkpoint: Task 3 human-verify in 16-csef-documentation-and-presentation-package/16-05-PLAN.md"
last_updated: "2026-03-23T03:06:05.042Z"
last_activity: 2026-03-21 — Completed 14-02 4ch vs 7ch R2 gap report (RSRCH-05)
progress:
  total_phases: 1
  completed_phases: 1
  total_plans: 5
  completed_plans: 5
  percent: 97
---

# Project State: Research Documentation Project

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-20)

**Core value:** Every claim in every document must be verifiably accurate against actual code, data, and results.
**Current focus:** v3.0 Deepen Research — Phase 14: Scope Lock Completion

## Current Position

Phase: 14 (Scope Lock Completion)
Plan: 2 of 2 in current phase
Status: Complete
Last activity: 2026-03-21 — Completed 14-02 4ch vs 7ch R2 gap report (RSRCH-05)

Progress: [██████████] 97%

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

### Roadmap Evolution
- Phase 12.1 inserted after Phase 12: Improved TCN: Enhanced Features + Multi-Task + Self-Attention (URGENT)
- Phase 16 added: CSEF Documentation and Presentation Package (v4.0 milestone)

### Blockers/Concerns

- Muse S BLE not viable on current macOS 25.x host — resolved: simulated mode ships, full hardware implementation retained in RealEEGAdapter for future BLE-enabled system.
- pytorch-forecasting + existing torch version compatibility unverified — use lightweight custom Transformer if conflict.
- Hard deadline: CSEF judging 2026-04-09 (20 days from milestone start).

## Session Continuity

Last session: 2026-03-23T03:06:05.040Z
Stopped at: Checkpoint: Task 3 human-verify in 16-csef-documentation-and-presentation-package/16-05-PLAN.md
Resume file: None
