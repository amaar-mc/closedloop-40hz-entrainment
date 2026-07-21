# Paper Narrative Arc

## The story in one paragraph

Current 40 Hz auditory entrainment protocols for Alzheimer's disease use fixed schedules that ignore real-time brain state. Reactive systems help but respond only after decline has occurred. We ask: can we predict entrainment loss 5-10 seconds ahead and stimulate proactively? We find that standard spectral EEG features fail to generalize across patients because they encode subject-specific anatomy. Using only 12 features derived from PAC trajectory and stimulation context — portable across patients — a causal TCN achieves R²=0.606 on held-out subjects and enables a controller that targets 82.6% of low-PAC windows for stimulation (vs 51.7% reactive), reaching 91% of the theoretical oracle bound on real EEG from 35 dementia patients.

---

## Section-by-section arc

### Abstract

Problem → gap → our approach → headline numbers (R²=0.606, 72.1% vs 64.5%, 91% oracle).

### Introduction

1. Alzheimer's — scale of problem, no cure
2. 40 Hz entrainment — evidence, mechanism (PAC)
3. Why fixed schedules fail (inter-patient variability + habituation)
4. Why reactive is insufficient (acts after decline, not before)
5. Our contribution: proactive prediction + closed-loop control
6. Preview of key findings

### Related Work

- 40 Hz entrainment literature (Iaccarino 2016, Martorell 2019, Lahijanian 2024)
- PAC as entrainment biomarker (Tort 2010)
- EEG-based neural state prediction (BCI literature)
- Closed-loop neurostimulation systems (prior reactive approaches)
- TCN for time series (Bai 2018) — justify architectural choice

### Methods

- Dataset (ds005048, 35 subjects, 7 channels)
- Stage 1: static PAC estimation (EEGNet, architecture search)
- Stage 2: temporal prediction (feature design → ablation → causal TCN)
- Controller (z-score baseline, hysteresis, 3-state decision)
- Evaluation (replay validation, alignment metric definition)
- Statistical analysis (Hedges' g, Wilcoxon signed-rank, Bonferroni)

### Results

1. Architecture search: R²=0.287 ceiling, model size irrelevant
2. Feature ablation: spectral → generalization failure; PAC+Stim → R²=0.606
3. Horizon sweep: TCN maintains R²=0.577-0.669 at 3-10s where baselines collapse
4. Controller validation: alignment, low-PAC targeting, PAC gap, per-subject utility
5. Fatigue robustness: advantage grows with habituation severity

### Discussion

- Feature generalization failure: WHY spectral features fail (anatomy hypothesis)
- Horizon sweet spot: why short horizons favor persistence (autocorrelation)
- Clinical interpretation: 91% oracle = near-maximal with imperfect prediction
- Limitations: offline replay, dataset size, simulated fatigue model
- Broader applicability: TMS, tDCS, other repetitive neurostimulation

### Conclusion

- Feature selection > architecture for cross-subject generalization
- Proactive control is achievable and clinically meaningful
- Path to deployment: live EEG streaming, RL controller, multi-biomarker

---

## Tone guidance

- Write for ML + neuroscience dual audience (IEEE EMBC / NeurIPS workshop)
- Lead with clinical motivation, resolve with ML rigor
- Every claim grounded in ground truth (poster, lab notebook, RESULTS_REPORT.md)
- Acknowledge limitations clearly — don't hide the offline replay constraint
