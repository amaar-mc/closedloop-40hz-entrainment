# Phase 18: Lab Notebook Comprehensive Rewrite - Research

## RESEARCH COMPLETE

### Source: Multi-Agent Audit (5 Opus agents, April 9, 2026)

### Critical Issues (from audit reports)

**1. Code-Notebook Misalignment**
- Wilson-Cowan: notebook says tau_e=0.010, actual code says 0.004
- ParametricCorticalModel: notebook says tau_rise=0.05, actual config says onset_tau_sec=1.5
- Code snippets were written from memory, not copied from repo

**2. Poster Contradictions**
- Poster says 3s hysteresis, code and notebook say 5s
- Poster pairs 5,154 params with R2=0.606, but 0.606 was computed on 22,914-param model
- Stale poster conclusions: "R2=0.25" is from old 73-feature model

**3. AI Voice (66/100)**
- Tonal break at March section boundary (Jan-Feb = paper voice, March = student voice)
- Zero imperfections across 886 lines
- Em-dashes concentrated only in March section (12 instances)
- Literature review reads like a paper intro

**4. Clinical Relevance (68/100)**
- No molecular pathway detail (how does gamma activate microglia?)
- No regulatory discussion (FDA pathway)
- No engagement with Soula 2023 critique
- No clinical trial design discussion

**5. Missing Content (62/100)**
- No learning curves or training logs
- No sample EEG traces
- No PAC distribution plots
- No error analysis on controller failures

### Actual Codebase Parameters (verified)
- `src/tribe_v2/neural_mass.py`: tau_e=0.004, tau_i=0.008
- `src/tribe_v2/cortical_model.py`: onset_tau_sec=1.5, offset_tau_sec=2.0
- `config.yaml`: hold_time_sec=5.0
- `src/controller.py`: hold_time_sec=5.0 (default)
- `src/pac_computation.py`: theta_band=(4.0,8.0), gamma_band=(38.0,42.0), n_bins=18
- `experimental/results/horizon_sweep_pac_stim.json`: persistence at h=5 is 0.104 (NOT -0.267)

### Validation Architecture

All changes verified by:
1. Grep actual codebase for parameter values
2. Cross-reference numbers against JSON result files
3. Compare with printed poster PDF
4. Read CSEF judging handbook for what judges evaluate
