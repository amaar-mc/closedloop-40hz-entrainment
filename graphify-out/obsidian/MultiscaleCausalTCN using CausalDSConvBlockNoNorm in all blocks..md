---
source_file: "temporal_multiscale/run_ablation_study.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L75"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# MultiscaleCausalTCN using CausalDSConvBlockNoNorm in all blocks.

## Connections
- [[AttentionPool1D_1]] - `uses` [INFERRED]
- [[CausalDSConvBlock_1]] - `uses` [INFERRED]
- [[LastStepPool_1]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[MultiscaleCausalTCNNoNorm]] - `rationale_for` [EXTRACTED]
- [[SequenceDataset]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features