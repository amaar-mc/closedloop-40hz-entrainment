---
source_file: "validation/experiments/tcn_interpretability.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L230"
tags:
  - community/Multiscale_TCN_&_Features
---

# Hook-based capture of AttentionPool1D attention weights.      Registers a forw

## Connections
- [[AttentionPool1D_1]] - `uses` [INFERRED]
- [[AttentionWeightCapture]] - `rationale_for` [EXTRACTED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]

  #community/Multiscale_TCN_&_Features