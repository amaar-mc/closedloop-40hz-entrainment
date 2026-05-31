---
source_file: "validation/experiments/tcn_interpretability.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L531"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Compute prediction performance conditioned on stimulation state.      Splits t

## Connections
- [[AttentionPool1D_1]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[analyze_stimulation_conditional()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features