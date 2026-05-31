---
source_file: "scripts/pipeline/run_12feat_validation.py"
type: "code"
community: "12-Feature TCN Validation"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/12-Feature_TCN_Validation
---

# 12-Feature TCN Validation Script (PAC+Context Only, N=35 Real EEG)

## Connections
- [[Alignment Score Metric (Low-PAC Stim + High-PAC Rest)  2]] - `implements` [EXTRACTED]
- [[TCNTribe Model (TRIBE-trained Causal TCN)]] - `semantically_similar_to` [INFERRED]
- [[run_replay()]] - `calls` [EXTRACTED]
- [[train_12feat_tcn()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/12-Feature_TCN_Validation