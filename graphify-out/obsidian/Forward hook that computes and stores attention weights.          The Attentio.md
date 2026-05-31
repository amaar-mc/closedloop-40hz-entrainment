---
source_file: "validation/experiments/tcn_interpretability.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L257"
tags:
  - community/Multiscale_TCN_&_Features
---

# Forward hook that computes and stores attention weights.          The Attentio

## Connections
- [[AttentionPool1D_1]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[_hook_fn()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features