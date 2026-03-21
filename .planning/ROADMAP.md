# Roadmap: Research Documentation Project

**Created:** 2026-03-07
**Project:** Research Documentation Project
**Core Value:** Every claim in every document must be verifiably accurate against actual code, data, and results.

## Milestones

- ✅ **v2.0 Paper Audit & Corrections** — Phases 4-9 (shipped 2026-03-18)
- 🚧 **v3.0 Deepen Research** — Phases 10-13 (in progress — deadline 2026-04-09)

## Phases

<details>
<summary>✅ v2.0 Paper Audit & Corrections (Phases 4-9) — SHIPPED 2026-03-18</summary>

- [x] Phase 4: Finalize Lab Notebook (3/3 plans) — completed 2026-03-15
- [x] Phase 5: Real-Time Demo (1/1 plan) — completed
- [x] Phase 6: Write Research Paper (5/5 plans) — completed
- [x] Phase 7: Fix Data & Methodology Errors (1/1 plan) — completed 2026-03-17
- [x] Phase 8: Fix Internal Consistency (2/2 plans) — completed 2026-03-18
- [x] Phase 9: Propagate & Recompile (2/2 plans) — completed 2026-03-18

</details>

<details>
<summary>Deferred (v1 Lab Notebook Phases)</summary>

- [ ] Phase 1: Content Foundation — Extract and organize research content
- [ ] Phase 2: Daily Entries — Create chronological lab notebook structure
- [ ] Phase 3: Visual Polish — Add visuals and ensure quality standards

</details>

### 🚧 v3.0 Deepen Research (In Progress — deadline 2026-04-09)

**Milestone Goal:** Transform the research project into a productized, demo-ready platform while deepening ML rigor for CSEF judging.

- [ ] **Phase 10: Scope Lock and Foundation** - Simulator defense, hardware mode decision, 4-channel Muse 2 model retraining
- [x] **Phase 11: Real-Time Inference Pipeline** - StreamingFeatureExtractor, SimulatedEEGAdapter, Muse 2 integration, model registry (completed 2026-03-21)
- [x] **Phase 12: Architecture Comparison Study** - XGBoost + Transformer training, ablation, multi-seed reproducibility (completed 2026-03-21)
- [ ] **Phase 13: Caregiver App and Pilot Preparation** - Full caregiver UI, Streamlit Cloud deployment, presentation and pilot materials

## Phase Details

### Phase 10: Scope Lock and Foundation
**Goal**: All risk-elimination decisions are documented and the 4-channel retrained models exist, unblocking the real-time pipeline
**Depends on**: Nothing (first v3.0 phase)
**Requirements**: RSRCH-04, RSRCH-05
**Success Criteria** (what must be TRUE):
  1. Hardware mode decision is written as a one-page decision doc — dual-mode confirmed, consumer EEG gamma limitation documented, simulated path as primary PAC control loop
  2. Simulator τ parameters are either fit from real data (fit_simulator_params.py exists) or the docstring cites Iaccarino et al. (2016) with the specific τ values used — no "empirically extracted" claim without backing
  3. EEGNet and TCN retrained on 4-channel subset (F7/F8/TP9/TP10 channels) with checkpoint saved and R² gap vs 7-channel baseline documented in a comparison table
  4. 4-channel feature dimensions confirmed and written into a channel mapping file so RTINF-01/03 can reference it without ambiguity
**Plans**: TBD

### Phase 11: Real-Time Inference Pipeline
**Goal**: A verified streaming feature extractor exists and the full inference path from simulated EEG through PAC prediction is runnable without hardware
**Depends on**: Phase 10
**Requirements**: RTINF-01, RTINF-02, RTINF-03, RTINF-04
**Success Criteria** (what must be TRUE):
  1. StreamingFeatureExtractor produces feature vectors within 1e-4 of the offline pipeline on 10 test windows — verified by a documented test run
  2. Running the simulated adapter produces a working demo session with PAC predictions and stimulus decisions visible in the terminal — no hardware required
  3. Muse 2 BrainFlow integration is either working (streams 4-channel EEG into retrained model) or documented as non-viable with fallback to simulated mode confirmed
  4. TCN, XGBoost, and Transformer can be selected via a single config flag or CLI argument — swapping models does not require code changes
**Plans:** 3/3 plans complete
Plans:
- [ ] 11-01-PLAN.md — StreamingFeatureExtractor with causal sosfilt and parity verification
- [ ] 11-02-PLAN.md — SimulatedEEGAdapter (BrainFlow) and TemporalModel registry with TCN wrapper
- [ ] 11-03-PLAN.md — End-to-end terminal demo wiring and Muse 2 hardware integration attempt

### Phase 12: Architecture Comparison Study
**Goal**: A complete architecture comparison table and ablation results exist that justify TCN selection and satisfy the CSEF Scientific Thought rubric
**Depends on**: Phase 10 (for 4-channel checkpoint paths and TemporalModel protocol from Phase 11)
**Requirements**: RSRCH-01, RSRCH-02, RSRCH-03
**Success Criteria** (what must be TRUE):
  1. Comparison table exists with R² and RMSE across horizons 1-10s for at minimum: persistence, Ridge, LSTM, XGBoost, Transformer, and TCN — one file, ready to paste into the paper and poster
  2. Ablation table shows R² impact of removing each TCN component (GroupNorm, attention, multi-scale dilation, single dilation) — TCN's advantage is quantified not claimed
  3. Multi-seed results (3-5 seeds) for TCN report mean ± std R² — a single lucky seed is ruled out
**Plans:** 2/2 plans complete
Plans:
- [ ] 12-01-PLAN.md — Architecture comparison: build SimpleLSTM/Transformer/XGBoost and sweep all 6 models across horizons 1,3,5,8,10
- [ ] 12-02-PLAN.md — TCN ablation (5 variants) and multi-seed reproducibility (5 seeds, 4ch+7ch)

### Phase 13: Caregiver App and Pilot Preparation
**Goal**: A live caregiver-facing app is deployed on Streamlit Cloud with a working QR code, patient profiles, session logging, and all CSEF presentation materials are ready
**Depends on**: Phase 11 (inference pipeline), Phase 12 (comparison results for poster content)
**Requirements**: APP-01, APP-02, APP-03, APP-04, APP-05, PRES-01, PRES-02, PRES-03, PRES-04
**Success Criteria** (what must be TRUE):
  1. A judge or caregiver can scan the QR code on the poster, open the app on their phone, and start a simulated therapy session without any explanation
  2. The app shows patient profiles, session history with per-session metrics, and a session completion summary using plain-language labels ("Brain Sync Level" not "PAC value")
  3. The app displays a real-time PAC trend chart and plays adaptive 40 Hz auditory stimulus with a visual stimulus-active indicator and volume slider
  4. One-page facility flyer exists (PDF, print-ready) with QR code, plain-language description, and contact info — ready to leave at Mission Villa and Valley Medical
  5. Pilot feedback Google Form exists and its QR code is on the poster — at least one test response collected before CSEF judging
**Plans**: TBD

## Progress

**Execution Order:** 10 → 11 → 12 → 13

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Content Foundation | v1 deferred | - | Deferred | - |
| 2. Daily Entries | v1 deferred | - | Deferred | - |
| 3. Visual Polish | v1 deferred | - | Deferred | - |
| 4. Finalize Lab Notebook | v2.0 | 3/3 | Complete | 2026-03-15 |
| 5. Real-Time Demo | v2.0 | 1/1 | Complete | - |
| 6. Write Research Paper | v2.0 | 5/5 | Complete | - |
| 7. Fix Data & Methodology Errors | v2.0 | 1/1 | Complete | 2026-03-17 |
| 8. Fix Internal Consistency | v2.0 | 2/2 | Complete | 2026-03-18 |
| 9. Propagate & Recompile | v2.0 | 2/2 | Complete | 2026-03-18 |
| 10. Scope Lock and Foundation | v3.0 | 0/TBD | Not started | - |
| 11. Real-Time Inference Pipeline | 3/3 | Complete    | 2026-03-21 | - |
| 12. Architecture Comparison Study | 2/2 | Complete    | 2026-03-21 | - |
| 13. Caregiver App and Pilot Preparation | v3.0 | 0/TBD | Not started | - |

---

_Full phase details for v2.0 archived in `.planning/milestones/v2.0-ROADMAP.md`_
