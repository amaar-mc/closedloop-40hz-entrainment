---
source_file: "temporal_multiscale/realtime_inference.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L21"
tags:
  - community/Multiscale_TCN_&_Features
---

# Realtime PAC forecaster with causal rolling buffer.      Expected per-step input

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features