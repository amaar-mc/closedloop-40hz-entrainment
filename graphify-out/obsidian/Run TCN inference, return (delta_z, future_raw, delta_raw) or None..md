---
source_file: "scripts/pipeline/run_tcn_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L198"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Run TCN inference, return (delta_z, future_raw, delta_raw) or None.

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]
- [[_predict()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features