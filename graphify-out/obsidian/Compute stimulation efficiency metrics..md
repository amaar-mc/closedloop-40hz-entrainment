---
source_file: "scripts/pipeline/run_tcn_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L533"
tags:
  - community/Multiscale_TCN_&_Features
---

# Compute stimulation efficiency metrics.

## Connections

- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]
- [[evaluate_efficiency()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale*TCN*&\_Features
