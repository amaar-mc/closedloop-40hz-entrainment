---
source_file: "temporal_multiscale/run_ablation_study.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L214"
tags:
  - community/Multiscale_TCN_&_Features
---

# Train a single variant and return its result dict.

## Connections
- [[AttentionPool1D_1]] - `uses` [INFERRED]
- [[CausalDSConvBlock_1]] - `uses` [INFERRED]
- [[LastStepPool_1]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SequenceDataset]] - `uses` [INFERRED]
- [[train_variant()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features