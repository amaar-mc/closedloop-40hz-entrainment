---
source_file: "validation/experiments/tcn_interpretability.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L492"
tags:
  - community/Multiscale_TCN_&_Features
---

# Find the index of the stim_state feature.      Args:         feature_names: L

## Connections
- [[AttentionPool1D_1]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[_find_stim_state_index()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features