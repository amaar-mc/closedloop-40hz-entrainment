# Research Documentation Project

## What This Is

A closed-loop 40 Hz gamma entrainment system for Alzheimer's disease that predicts theta-gamma phase-amplitude coupling 5-10 seconds ahead and adaptively delivers auditory stimulation. Includes a complete ML pipeline (EEGNet + PAC+Stim TCN), live Muse 2 EEG dashboard, caregiver-facing web app, and all CSEF 2026 presentation materials.

## Core Value

Every claim in every document must be verifiably accurate against the actual code, data, and results — scientific integrity is non-negotiable.

## Requirements

### Validated

- ✓ Lab notebook finalized (V1/V2 pair) — v1.0 Phase 4
- ✓ Real-time demo dashboard (Streamlit + 40 Hz audio) — v1.0 Phase 5
- ✓ Complete research paper (11,647 words, 23 references) — v1.0 Phase 6
- ✓ CSEF 2026 presentation PDF (12 pages, Times New Roman) — v1.0
- ✓ All factual errors corrected and propagated across 13+ documents — v2.0
- ✓ Architecture comparison (6 models × 5 horizons × 2 channel configs) — v3.0
- ✓ TCN ablation study quantifying each component's contribution — v3.0
- ✓ Multi-seed reproducibility (5 seeds, R²=0.606±0.032) — v3.0
- ✓ Simulator τ parameters fit from real data (35 subjects) — v3.0
- ✓ 4ch vs 7ch performance gap documented — v3.0
- ✓ Streaming inference pipeline (causal sosfilt, Muse 2 BLE, model registry) — v3.0
- ✓ PAC+Stim feature discovery (R² 0.12→0.60 by dropping spectral features) — v3.0
- ✓ Caregiver app with patient profiles, session management, 40Hz audio — v3.0
- ✓ Live mission control dashboard with real Muse 2 connection — v3.0
- ✓ HF Spaces deployment with QR codes — v3.0
- ✓ Elevator pitch, clinical roadmap, facility flyer, pilot feedback form — v3.0

### Active

(No active milestone — next milestone TBD)

### Out of Scope

- Lab notebook phases 1-3 (deferred — content extraction, daily entries, visual polish)
- React/FastAPI production rewrite (Streamlit sufficient for CSEF)
- Full mobile app build (roadmap narrative only)
- FDA regulatory submission (clinical testing plan documented but not executed)
- Manufacturing hardware (intelligence layer on existing hardware only)
- Web Bluetooth for remote Muse 2 connection (BLE is local-only)

## Current State

**Shipped v3.0 (2026-03-22):**

Key breakthrough: dropping 61 spectral features and using only 12 PAC trajectory + stim context features raises temporal PAC prediction R² from 0.12 to 0.60 (7ch) / 0.43 (4ch) at 5-second horizon. Spectral features encode subject-specific anatomy that doesn't generalize. Audited with 7 empirical tests — no data leakage.

**Live systems:**
- `neurocare_live.py` — Muse 2 mission control with direct PAC, band powers, closed-loop 40Hz stimulus
- `caregiver_app.py` — Patient-facing app deployed at https://huggingface.co/spaces/amaarc/neurocare-40hz
- Pilot feedback form: https://forms.gle/NFkh2oWA1st3YrZT8

**Models (production):**
- EEGNet 4ch: 1,409 params, static PAC estimation
- PAC+Stim TCN 4ch: 6,338 params, 12 features, R²=0.43 on held-out test subjects
- Direct PAC computation (Tort 2010 MI) for live Muse 2 sessions

**Codebase:** 26,096 Python LOC across src/, temporal_multiscale/, experimental/, improved_tcn/, scripts/

**CSEF context:**
- Judging: 2026-04-09
- Poster, elevator pitch, clinical roadmap, facility flyer all ready
- Pilot facilities: Mission Villa, Valley Medical, regional hospital, senior center

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Fix paper to match code (not vice versa) | Code produced the actual results | ✓ Good |
| Drop spectral features for temporal prediction | Subject-specific overfitting destroys generalization | ✓ Good — R² 5× improvement |
| Direct PAC computation instead of EEGNet for live | EEGNet doesn't generalize to Muse 2 dry electrodes | ✓ Good — no domain gap |
| HF Spaces instead of Streamlit Cloud | Repo is private, Streamlit Cloud requires public | ✓ Good |
| Simulated-only for cloud, real EEG local only | BLE is physical, can't bridge to cloud server | ✓ Good |
| Session-adaptive normalization | Training z-scores saturate on Muse 2 signal | ✓ Good |
| Z-score + hysteresis for stimulus decisions | Prevents twitchy flip-flopping from noisy predictions | ✓ Good |
| Keep Streamlit (no React rewrite) | 20-day deadline, Streamlit sufficient for demo | ✓ Good |

## Constraints

- **Data integrity**: Fix descriptions to match code, never change code to match descriptions
- **Consistency**: All corrections must propagate to CSEF presentation and RESULTS_REPORT
- **Accuracy**: Every number must be traceable to a source file
- **Deadline**: CSEF judging 2026-04-09

---
*Last updated: 2026-03-22 after v3.0 milestone*
