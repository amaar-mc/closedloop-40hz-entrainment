---
source_file: "temporal_multiscale/run_ablation_study.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L59"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# CausalDSConvBlock with GroupNorm replaced by Identity (ablation).

## Connections
- [[AttentionPool1D_1]] - `uses` [INFERRED]
- [[CausalDSConvBlock_1]] - `uses` [INFERRED]
- [[CausalDSConvBlockNoNorm]] - `rationale_for` [EXTRACTED]
- [[LastStepPool_1]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SequenceDataset]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features