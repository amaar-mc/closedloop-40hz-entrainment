---
source_file: "validation/experiments/tcn_interpretability.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L507"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Find the index of the time_since_switch feature.      Args:         feature_n

## Connections
- [[AttentionPool1D_1]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[_find_time_since_switch_index()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features