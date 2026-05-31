---
source_file: "validation/experiments/tcn_interpretability.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L193"
tags:
  - community/Multiscale_TCN_&_Features
---

# Load the trained TCN checkpoint.      Args:         checkpoint_path: Path to

## Connections
- [[AttentionPool1D_1]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[load_model_and_scalers()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features