---
source_file: "validation/experiments/tcn_interpretability.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L279"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Concatenate all captured weights into (N, T) array.

## Connections
- [[.get_all_weights()]] - `rationale_for` [EXTRACTED]
- [[AttentionPool1D_1]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features