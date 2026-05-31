---
type: community
members: 15
---

# Community 73

**Members:** 15 nodes

## Members
- [[73-Feature Breakdown 61 spectral (28 band power + 7 thetagamma ratio + 21 PAC-structure + 5 global) + 7 PAC-derived + 5 stim context]] - document - archive/CSEF_Old/Presentation/CURRENT_METHODOLOGY.md
- [[Active src Modules data_loader, preprocessing, pac_computation, eegnet, training, controller, personalization, simulator, validation, utils, spectral_features]] - document - archive/CSEF_Old/Presentation/CODE_MAP.md
- [[Architecture Timeline Phase 1 (V1-V8 static, Feb 5-16), Phase 2 (temporal LSTM, Feb 16-17), Phase 3 (multiscale TCN, Feb 17)]] - document - archive/CSEF_Old/Presentation/CODE_MAP.md
- [[Closed-Loop Controller Design Slide z-score thresholds ±0.5, 5s hysteresis, offline counterfactual replay validation]] - document - archive/CSEF_Old/CSEF_2026_Presentation.pdf
- [[Closed-Loop Controller z−0.5→STIMULATE, z+0.5→REST, 3s hysteresis, 30s rolling baseline]] - document - archive/CSEF_Old/Presentation/CURRENT_METHODOLOGY.md
- [[Discussion Slide spectral features encode anatomy, 3s inflection = PAC autocorrelation timescale, single-site limitation]] - document - archive/CSEF_Old/CSEF_2026_Presentation.pdf
- [[EEGNet Architecture (B,1,7,500) → (B,1), 1,457 params, temporal+depthwise spatial conv, R²=0.287]] - document - archive/CSEF_Old/Presentation/CURRENT_METHODOLOGY.md
- [[Feature Engineering Summary raw EEG (1,7,500), spectral 61-dim, wavelet 74-dim, PAC features 116-dim (circular), multiscale 73-dim]] - document - archive/CSEF_Old/Presentation/CODE_MAP.md
- [[Model Zoo EEGNet R²=0.287, EEGNetV2 R²=0.06, SpecTempNet R²=0.236, ViT-TCNet R²=0.252, LSTM R²=−0.05, MultiscaleCausalTCN R²=0.74]] - document - archive/CSEF_Old/Presentation/CODE_MAP.md
- [[MultiscaleCausalTCN Architecture (B,20,73)→future PAC+delta, 31,043 params, dilation 1,2,4,8, receptive field 31 steps]] - document - archive/CSEF_Old/Presentation/CURRENT_METHODOLOGY.md
- [[Project Limitations offline replay only, single dataset, short sessions (6-10 min), static PAC ceiling, heuristic thresholds]] - document - archive/CSEF_Old/Presentation/PROJECT_ACHIEVEMENT_REPORT.md
- [[Q&A Tier 2 Methodology PAC computation, EEGNet rationale, TCN vs LSTM, causality guarantee, 73-feature breakdown, leakage safeguards]] - document - archive/CSEF_Old/Presentation/05_qa_complete.md
- [[Q&A Tier 5 Hard R²=0.25 usefulness defense, offline vs live argument, sample size defense, novelty claims]] - document - archive/CSEF_Old/Presentation/05_qa_complete.md
- [[Rationale for Architecture Marathon 8 configs (1.5K–1.1M params) all converge at R²=0.287, proving data ceiling not model limitation]] - document - archive/CSEF_Old/Presentation/05_qa_complete.md
- [[Rationale TCN chosen over LSTMTransformer — causal by construction, faster, less overfit risk with 35 subjects, inductive bias matches EEG]] - document - archive/CSEF_Old/Presentation/05_qa_complete.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_73
SORT file.name ASC
```
