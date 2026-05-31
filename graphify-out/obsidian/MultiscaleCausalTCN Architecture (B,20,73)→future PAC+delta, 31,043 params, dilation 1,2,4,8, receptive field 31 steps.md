---
source_file: "archive/CSEF_Old/Presentation/CURRENT_METHODOLOGY.md"
type: "document"
community: "Community 73"
location: "Section 4.2"
tags:
  - graphify/document
  - graphify/EXTRACTED
  - community/Community_73
---

# MultiscaleCausalTCN Architecture: (B,20,73)→future PAC+delta, 31,043 params, dilation [1,2,4,8], receptive field 31 steps

## Connections
- [[73-Feature Breakdown 61 spectral (28 band power + 7 thetagamma ratio + 21 PAC-structure + 5 global) + 7 PAC-derived + 5 stim context]] - `references` [EXTRACTED]
- [[Closed-Loop Controller z−0.5→STIMULATE, z+0.5→REST, 3s hysteresis, 30s rolling baseline]] - `references` [EXTRACTED]
- [[EEGNet Architecture (B,1,7,500) → (B,1), 1,457 params, temporal+depthwise spatial conv, R²=0.287]] - `references` [EXTRACTED]
- [[Rationale TCN chosen over LSTMTransformer — causal by construction, faster, less overfit risk with 35 subjects, inductive bias matches EEG]] - `rationale_for` [EXTRACTED]

#graphify/document #graphify/EXTRACTED #community/Community_73