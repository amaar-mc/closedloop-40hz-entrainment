---
source_file: "temporal_multiscale/run_comparison_study.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L151"
tags:
  - community/Multiscale_TCN_&_Features
---

# Ridge with alpha auto-scaled to input dimensionality. alpha=1.0 overflows w

## Connections

- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SequenceDataset]] - `uses` [INFERRED]
- [[SimpleLSTM]] - `uses` [INFERRED]
- [[SimpleTransformer]] - `uses` [INFERRED]
- [[_run_ridge()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale*TCN*&\_Features
