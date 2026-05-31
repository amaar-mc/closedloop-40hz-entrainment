---
source_file: "validation/experiments/tcn_interpretability.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L273"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Remove the forward hook.

## Connections
- [[.remove()]] - `rationale_for` [EXTRACTED]
- [[AttentionPool1D_1]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features