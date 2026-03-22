# Milestones

## v3.0 Deepen Research (Shipped: 2026-03-22)

**v3.0 scope:** Phases 10-15 (13 plans) — ML research deepening, real-time inference, caregiver app, deployment
**Requirements:** 18/18 satisfied (RSRCH ×5, RTINF ×4, APP ×5, PRES ×4)

**Key accomplishments:**
1. Streaming inference pipeline — causal spectral feature extractor + Muse 2 BLE adapter + model registry with hot-swap (TCN/XGBoost/Transformer)
2. 6-model architecture comparison across horizons 1-10s on both 7ch and 4ch datasets (60 evaluation runs)
3. PAC+Stim feature breakthrough — R² from 0.12 to 0.60 (7ch) / 0.43 (4ch) by discovering spectral features cause subject-specific overfitting (50+ experiments, 7-test empirical audit)
4. Live mission control dashboard (neurocare_live.py) — real Muse 2 connection, 5-band power visualization, direct PAC computation (Tort 2010 MI), closed-loop 40Hz auditory stimulus
5. Caregiver app deployed to HF Spaces with patient profiles, session management, plain-language metrics, QR codes
6. Simulator τ parameters fit from real PAC transitions (35 subjects), 4ch vs 7ch gap formally documented
7. All CSEF presentation materials: elevator pitch, clinical roadmap, facility flyer PDF, pilot feedback Google Form

**Timeline:** 2026-03-19 → 2026-03-22 (4 days)
**Commits:** 94 | **Files:** 180 changed (+28,433 lines) | **Python LOC:** 26,096

---

## v2.0 Paper Audit & Corrections (Shipped: 2026-03-18)

**v2.0 scope:** Phases 7-9 (5 plans) — Paper Audit & Corrections
**Full project:** 6 completed phases (4-9), 14 plans total

**Key accomplishments:**
1. Corrected 7 factual errors in RESEARCH_PAPER.md (hysteresis 5s→3s, CI method, spectral features, artifact handling, EEGNet epoch, Hedges' g, PAC units)
2. Fixed 7 internal consistency issues (population labels, TCFormer misattribution, 16 orphan references pruned, heading formatting, single-author voice, terminology, magnitude phrase)
3. Propagated all corrections to 13 active CSEF presentation documents
4. Updated LaTeX source and recompiled clean 2.7 MB PDF
5. Verified RESULTS_REPORT.md consistency (g=0.75, ×10⁻⁶ MI units)
6. 17/17 v2.0 requirements satisfied, milestone audit passed

**Timeline:** 2026-03-17 → 2026-03-18 (2 days)
**Commits:** 23 (phases 7-9)

---

