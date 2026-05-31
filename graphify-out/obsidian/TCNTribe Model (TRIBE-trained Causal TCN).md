---
source_file: "scripts/pipeline/run_tribe_tcn_validation.py"
type: "code"
community: "TRIBE-TCN Validation"
location: "line 184"
tags:
  - community/TRIBE-TCN_Validation
---

# TCNTribe Model (TRIBE-trained Causal TCN)

## Connections
- [[12-Feature TCN Validation Script (PAC+Context Only, N=35 Real EEG)]] - `semantically_similar_to` [INFERRED]
- [[CausalConv1dBlock (Dilated Residual Conv Block)]] - `implements` [EXTRACTED]
- [[Rationale Domain Mismatch Between Real EEG TCN and TRIBE Simulator]] - `rationale_for` [EXTRACTED]
- [[TCNTribeController (Proactive Closed-Loop Controller)]] - `references` [EXTRACTED]
- [[build_features_from_sequence()]] - `shares_data_with` [INFERRED]
- [[train_tcn_tribe()]] - `calls` [EXTRACTED]

  #community/TRIBE-TCN_Validation