# Project Research Summary

**Project:** Closed-Loop 40Hz Entrainment — v3.0 CSEF Demo
**Domain:** BCI/neurofeedback caregiver therapy app with ML research deepening
**Researched:** 2026-03-20
**Confidence:** MEDIUM-HIGH

## Executive Summary

This project productizes a validated closed-loop 40Hz gamma entrainment research pipeline into a caregiver-facing demo application, targeting CSEF judging on April 9, 2026 — a hard 20-day window. The core ML pipeline (EEGNet static predictor at R²=0.287, MultiscaleCausalTCN temporal forecaster at R²=0.25 at 5-10s horizons, four-strategy closed-loop controller with validated real-EEG results) is complete and must not be touched. Everything new is additive: a Streamlit-based caregiver UI with patient profiles and session logging, a streaming feature extractor bridging the offline pipeline to real-time inference, an architecture comparison study (XGBoost + Transformer vs. TCN), and optional consumer EEG hardware integration.

The recommended approach is to keep the demo entirely on the existing Streamlit foundation and extend it surgically. The research establishes that a React/FastAPI rewrite is architecturally correct for production but would consume 10-15 days of the 20-day budget — an unacceptable risk. The FastAPI/Next.js stack documented in STACK.md and ARCHITECTURE.md is the right production target and should be presented as the technical roadmap slide, not built for CSEF. Streamlit polished with CSS theming and careful `st.session_state` management can look like a clinical product without a rewrite.

The critical risk is the consumer EEG gamma band measurement problem: Muse-class headsets cannot reliably measure gamma PAC at frontal sites due to EMG contamination, and the trained EEGNet/TCN expect 7-channel research-grade input. This is not a fixable problem in the demo timeline. The defensible and honest strategy is dual-mode: live consumer EEG for alpha/theta visualization (proving the hardware loop is plumbed), and validated ds005048 replay for the PAC-based closed-loop control. Every other risk in the research has a clear mitigation that fits inside the 20-day window.

## Key Findings

### Recommended Stack

The existing stack (PyTorch, MNE, scikit-learn, NumPy, Streamlit) is unchanged. New additions are minimal and targeted. For the demo, Streamlit extensions are the only required web changes. For ML rigor, add `xgboost` (2.1.x) for a tabular temporal baseline and optionally `pytorch-forecasting` (1.1.x) for the Temporal Fusion Transformer — both plug directly into the existing `build_multiscale_dataset.py` outputs. For hardware, BrainFlow (5.x) is the correct unified abstraction over Muse, OpenBCI, and 30+ other boards — change one board ID constant to switch devices. SQLite + SQLModel is sufficient for pilot-scale session persistence.

**Core technologies:**
- Streamlit (extend existing): caregiver UI — fastest path to a polished demo; keep for v3.0, document React/FastAPI as production path
- BrainFlow 5.x: EEG hardware abstraction — board-agnostic, supports Muse S/2, OpenBCI, synthetic board for simulation; single API
- Muse S Gen 2 ($249): hardware demo — lowest cost/setup for a CSEF demo; 4 frontal channels, 2-min setup; use for alpha/theta viz only, not gamma PAC
- xgboost 2.1.x: ML comparison study — competitive tabular baseline at short horizons; interpretable feature importances; one `pip install`
- pytorch-forecasting 1.1.x + lightning 2.4.x: Transformer comparison — tests whether attention beats causal convolution; uses existing dataset format
- SQLModel 0.0.22: session persistence — FastAPI author's ORM; unifies Pydantic + SQLAlchemy; trivial migration from SQLite to PostgreSQL when needed
- FastAPI 0.115.x + Next.js 14.x: production roadmap target — correct architecture for multi-user clinical deployment; do not build for CSEF

### Expected Features

**Must have (P1 — table stakes for CSEF April 9):**
- Patient profile + session log — makes the app a clinical product rather than a research script
- Hardware status indicator + dual-mode toggle (simulated / real EEG) — trust signal for judges and facility staff
- Caregiver narrative framing in UI labels — rename raw metrics to patient-facing language
- Session completion summary with plain-language metrics — every therapy app does this
- 40Hz volume slider (not just mute) — elderly patient auditory comfort
- Ablation study (TCN with components removed) — CSEF Scientific Thought rubric requires this
- New model trained (XGBoost minimum, Transformer if time permits) — strengthens TCN selection narrative
- Multi-seed training results (mean ± std R²) — reproducibility claim
- Streamlit Cloud deployment + working QR code — judges and facility visitors must be able to scan and try
- Printed one-page facility explainer — leave-behind artifact for Mission Villa / Valley Medical visits

**Should have (P2 — add if time permits):**
- BrainFlow synthetic board integration test documented — proves hardware path works
- Feature importance / attribution results from `tcn_interpretability.py` — already exists, needs surfacing
- Pilot feedback form (embedded or QR-linked) — CSEF "human testing data" claim
- Clinical roadmap PDF — product narrative for follow-up with facilities

**Defer (P3 / v4+):**
- PAC trend chart across sessions (multi-session view) — requires multiple real sessions first
- Real hardware BrainFlow closed-loop integration — blocked by gamma band reliability problem
- Mobile iOS/Android app — 6-month project; roadmap only
- Multisensory stimulation (audio + visual flicker) — requires hardware; literature-supported but out of scope
- EHR integration — HIPAA; institutional partnership required
- React/FastAPI production web app — correct architecture, wrong timeline

### Architecture Approach

All new code lives in `webapp/` at the repo root. The existing `src/` and `temporal_multiscale/` pipelines are imported as libraries via `sys.path.insert` — nothing existing is modified. The architecture hinges on a `DataSourceAdapter` protocol that abstracts over real hardware (`RealEEGAdapter` via BrainFlow) and simulation (`SimulatedEEGAdapter` via `EntrainmentSimulator`), making the entire control stack hardware-agnostic. A persistent WebSocket connection per session drives the 1 Hz closed-loop tick from the backend; the browser handles audio synthesis entirely client-side via Web Audio API, never crossing the network with audio data. For the CSEF demo, the Streamlit path is simpler — the architecture diagram is for the production roadmap presentation.

**Major components:**
1. DataSourceAdapter (simulated/real) — the critical seam; `(7, 500)` EEG windows flow uniformly downstream regardless of source
2. StreamingFeatureExtractor — missing link between offline batch pipeline and real-time TCN inference; must be built before any web app wiring
3. InferenceService (model registry) — loads EEGNet + TCN once at startup; new architectures (XGBoost, Transformer) register via a uniform `TemporalModel` protocol
4. ControllerService (wraps existing `src/`) — instantiated once per session so `PersonalizationModule` accumulates state across the full session duration
5. SessionStore (SQLite via SQLAlchemy) — persists patients, sessions, per-window PAC/stim logs; single connection string change to PostgreSQL
6. WebSocket hub (`/ws/session/{id}`) — multiplexes display data and control signals through one connection per session; no separate channel per EEG channel
7. Frontend Audio Engine (Web Audio API) — browser-side `OscillatorNode` gated by stim command; no audio crosses the network

### Critical Pitfalls

1. **Consumer EEG cannot reliably measure gamma PAC** — Muse-class dry frontal electrodes are dominated by EMG in the 38-42 Hz band; the model was trained on research-grade ICA-cleaned data. Never pass live Muse gamma as input to the trained EEGNet/TCN. Use Muse only for alpha/theta visualization; use validated ds005048 replay for the PAC control loop. Decision must be made and documented by Day 1.

2. **Real-time spectral feature extractor does not exist** — `RealtimePACForecaster.step()` takes a pre-computed `(61,)` feature vector; no code in the repo computes these 61 features from a live 2-second window. Build `StreamingFeatureExtractor` first, verify feature vectors match offline pipeline within 1e-4 tolerance on 10 test windows, before writing any web app code. This is the single most likely cause of a broken demo.

3. **`filtfilt` is non-causal and cannot be used in the streaming path** — `filtfilt` uses future samples; using it in real-time introduces 100-400ms latency and is scientifically invalid for closed-loop control. Use causal `sosfilt` with state tracking across windows. Add a `grep -r filtfilt webapp/` check before any real-time integration is merged.

4. **20-day timeline collapses if real hardware integration is attempted seriously** — BLE SDK setup, Python version incompatibilities (`muselsl` on Python 3.11+), and channel mismatch debugging each take 2-5 days. Hard time-box hardware integration to 3 days maximum. If not working by Day 5, ship with simulated mode only.

5. **Simulator parameter defense is the weakest judge-facing claim** — `simulator.py` states τ values are "empirically extracted" but no fit script exists. Either add `fit_simulator_params.py` (a few hours) or update the docstring to cite Iaccarino et al. (2016) GENUS response timescales. The key result — TCN predictive advantage — is validated on real ds005048 data; the simulation is for controller comparison only. Prepare a 3-sentence answer for the judge who asks.

## Implications for Roadmap

Based on combined research, the recommended structure is 4 phases ordered by dependency and risk front-loading, targeted at CSEF April 9, 2026.

### Phase 1: Scope Lock and Research Deepening
**Rationale:** The most dangerous pitfalls (consumer EEG gamma failure, scope creep into React/FastAPI, simulator parameter weakness) must be resolved as documented decisions before any code is written. This phase produces no demo features but eliminates the conditions that cause demo failures on Day 18.
**Delivers:** Hardware mode decision documented (Strategy A confirmed), simulator τ parameter citation added, `fit_simulator_params.py` or docstring update, architecture comparison study plan locked (which models, which horizons), no new directories created
**Addresses:** ML rigor features (ablation study setup, multi-seed plan, architecture comparison table structure)
**Avoids:** Consumer EEG gamma failure (Pitfall 1), scope creep into full web app rewrite (Pitfall 5), simulator parameter exposure at judging (Pitfall 6)
**Research flag:** Standard — this is decision documentation, not research. Skip `/gsd:research-phase`.

### Phase 2: Real-Time Inference Pipeline
**Rationale:** `StreamingFeatureExtractor` is the missing technical link identified as the single highest-probability demo failure point. Nothing in the web app can be meaningfully tested without it. Architecture research identifies build order starting with data source adapters before any frontend work.
**Delivers:** `StreamingFeatureExtractor` class with verified feature parity to offline pipeline (within 1e-4 on 10 test windows), causal `sosfilt` filter state management, `SimulatedEEGAdapter` (unblocks all downstream development without hardware), channel shape assertion at controller boundary, PyTorch model warm-up at startup
**Uses:** BrainFlow `SYNTHETIC_BOARD` (simulated path), existing `src/preprocessing.py` patterns, existing `temporal_multiscale/realtime_inference.py`
**Implements:** DataSourceAdapter protocol, StreamingFeatureExtractor, model registry foundation
**Avoids:** Missing feature extractor (Pitfall 2), `filtfilt` causality violation (Pitfall 3), channel mismatch silent failures (Pitfall 7)
**Research flag:** Standard patterns — BrainFlow synthetic board and scipy filter state are well-documented. Skip `/gsd:research-phase`.

### Phase 3: Architecture Comparison Study
**Rationale:** The ML rigor features (ablation study, new model training, multi-seed results) are the highest-weight CSEF scoring items (Scientific Thought + Creativity, 20/40 points). They are also independent of the web app — can run in parallel or sequentially without blocking the demo. Research confirms XGBoost + Transformer + LSTM retraining on the existing multiscale dataset is sufficient to produce the comparison table.
**Delivers:** `temporal_multiscale/model_registry.py` with `XGBoostTemporalModel` and `TransformerTemporalModel`, `sweep_horizons.py` extended with `--models` flag, architecture comparison table (persistence + Ridge + LSTM + XGBoost + Transformer + TCN across horizons 1-10s), ablation study (GroupNorm off / attention off / multi-scale off / single dilation), multi-seed training (3-5 seeds, mean ± std R²), per-subject R² distribution
**Uses:** xgboost 2.1.x, pytorch-forecasting 1.1.x + lightning 2.4.x (or lightweight Transformer from scratch to avoid heavy dependency)
**Implements:** TemporalModel protocol (Pattern 4 from ARCHITECTURE.md)
**Avoids:** Weak "why TCN" justification at judging; single-run reproducibility challenge

### Phase 4: Caregiver UI and Pilot Preparation
**Rationale:** Demo-facing features come last because they depend on a working inference pipeline (Phase 2) and the ML comparison results (Phase 3) to populate the scientific content. Streamlit extensions are fast — the research confirms the full P1 feature list is achievable in Streamlit with existing demo.py as the base.
**Delivers:** Patient profile + session log (SQLite via SQLModel or simple JSON for demo), hardware status indicator + dual-mode toggle (sim vs. real label), caregiver-friendly UI labels ("Brain Sync Level" not "PAC value"), session completion summary screen, 40Hz volume slider, TCN warmup countdown ("Calibrating — 18s remaining"), Streamlit Cloud deployment + QR code tested on phone, printed one-page facility explainer, pilot feedback form (Google Form QR)
**Uses:** Streamlit + `st.session_state`, SQLite (via direct sqlite3 or SQLModel), existing `demo.py` AudioEngine
**Implements:** Caregiver UI layer, session persistence, dual-mode surface
**Avoids:** Web app framework trap (Pitfall 5), QR code broken at demo (security checklist), PAC units uninterpretable to caregivers (UX pitfall), cold-start freeze appearance (warmup visibility pitfall)
**Research flag:** Standard patterns. Skip `/gsd:research-phase`.

### Phase Ordering Rationale

- Phase 1 before everything else because the hardware mode decision and scope lock prevent wasted work in all subsequent phases. Five days of consumer EEG debugging (Pitfall 4) is only avoidable if the decision is made explicitly before anyone opens the BrainFlow documentation.
- Phase 2 before Phase 4 because `StreamingFeatureExtractor` is a prerequisite for any real-time demo path. The simulated adapter also unblocks all UI testing without hardware.
- Phase 3 is independent and can overlap with Phase 2 or Phase 4 if time permits, but the comparison table content is needed before the poster is finalized.
- Phase 4 last because it is the most visible and least technically risky — given working inference infrastructure, Streamlit UI changes are the fastest iteration cycle.
- No Phase builds a React/FastAPI app. That is the production roadmap narrative presented to judges as a slide, not implemented code.

### Research Flags

Phases needing deeper research during planning:
- **Phase 3 (Architecture Comparison):** Transformer architecture choice (EEG-PatchFormer vs. lightweight custom vs. TFT from pytorch-forecasting) needs a quick feasibility check on the 35-subject dataset size before committing to the full pytorch-forecasting dependency. Consider `/gsd:research-phase` if the dependency chain (lightning + pytorch-forecasting) creates conflicts with existing torch/lightning installs.

Phases with standard patterns (skip research-phase):
- **Phase 1:** Decision documentation — no code, no research needed
- **Phase 2:** BrainFlow synthetic board, scipy filter state, and numpy feature extraction are all well-documented with official sources
- **Phase 4:** Streamlit extensions, SQLite, Google Forms — all trivially documented

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Core new dependencies (BrainFlow, xgboost, SQLModel) verified against official docs; version compatibility confirmed (sqlmodel 0.0.22 requires SQLAlchemy 2.x; pytorch-forecasting requires `lightning` not `pytorch-lightning`); Muse S hardware specs from official BrainFlow docs |
| Features | HIGH | Caregiver UX features from live competitor platforms (Myndlift, Divergence Neuro); CSEF judging rubric verified from official source; clinical pilot expectations from peer-reviewed Cognito OVERTURE trial design |
| Architecture | MEDIUM-HIGH | Web app patterns are HIGH confidence from official FastAPI/MDN docs; EEG hardware integration is MEDIUM — BrainFlow Muse support requires verification at hardware test time; dual-mode seam design is well-reasoned but unverified against real Muse device on macOS |
| Pitfalls | HIGH | Consumer EEG gamma limitation backed by 4 peer-reviewed 2024-2025 sources; code-specific pitfalls (missing streaming extractor, `filtfilt` causality, channel mismatch) verified by direct source inspection; timeline risk from prior BLE/SDK integration experience |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Muse S BLE stability on macOS 25.x (Sequoia/Tahoe):** BrainFlow's macOS Bluetooth support requires system permission grant; `muselsl` has known Python 3.11+ issues. Test SDK connection on target hardware before committing more than 1 day to it. If connection fails, ship Strategy A (simulated only) without further debugging.
- **pytorch-forecasting + existing lightning version:** Verify `pytorch-forecasting 1.1.x` installs cleanly alongside the existing `torch` version in `requirements.txt`. If there are conflicts, use a lightweight custom Transformer (~100K params, d_model=64, nhead=4) instead — avoids the dependency entirely and is more defensible to judges.
- **Simulator τ parameter fit:** The gap between "empirically extracted" (current docstring claim) and actual data-fit τ values is a live judging risk. Either run `fit_simulator_params.py` in Phase 1 or update documentation before poster finalization.
- **ds005048 channel labels:** The exact 7 channels used in training should be confirmed in `src/data_loader.py` or `config.yaml` before writing any channel mapping code for real hardware. Mislabeled channels produce silent wrong predictions, not errors.

## Sources

### Primary (HIGH confidence)
- BrainFlow official docs (brainflow.readthedocs.io) — Muse S/2/OpenBCI board IDs, channel counts, sample rates, synthetic board
- FastAPI official docs (fastapi.tiangolo.com) — WebSocket patterns, async handlers
- MDN Web Audio API (developer.mozilla.org) — AudioContext, OscillatorNode, autoplay policy
- SQLModel official docs (sqlmodel.tiangolo.com) — FastAPI integration, SQLAlchemy 2.x compatibility
- CSEF 2026 judging criteria (csef.usc.edu) — 40-point rubric breakdown
- Cognito OVERTURE trial (PMC10957179) — caregiver-assisted home use design, clinical pilot expectations
- MIT News 40Hz gamma evidence 2025 (news.mit.edu) — stimulus delivery rationale
- Project source code (direct inspection) — `src/controller.py`, `temporal_multiscale/realtime_inference.py`, `src/simulator.py`, `demo.py`

### Secondary (MEDIUM confidence)
- Bahador et al. (2025), Scientific Reports — consumer EEG gamma band reliability benchmarking
- PMC11679099 (2024) — consumer vs. research EEG spectral comparison
- PMC10917334 — consumer-grade EEG research use scoping review
- Brain Informatics (2025) — wearable EEG real-world benchmarking for BCIs
- Myndlift / Divergence Neuro product docs — caregiver dashboard feature expectations
- pytorch-forecasting PyPI — install and compatibility notes
- EEG-PatchFormer (EMBC-2025 GitHub) — Transformer EEG architecture reference
- Feasibility of EEG headsets with elderly AD patients (PMC9228283) — pilot demo expectations

### Tertiary (LOW confidence)
- Muse S Gen 2 review (saironlabs.com) — price/specs confirmation (corroborated by primary sources)
- EEG devices comparison article (sharikazareen.medium.com) — practical developer comparison (single source, not peer-reviewed)
- UX for BCI devices (kryshiggins.com) — accessibility requirements (practitioner blog)

---
*Research completed: 2026-03-20*
*Ready for roadmap: yes*
