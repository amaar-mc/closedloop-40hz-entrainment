---
source_file: "scripts/pipeline/run_tcn_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L131"
tags:
  - community/Multiscale_TCN_&_Features
---

# Reactive z-score threshold controller on rolling PAC baseline.

## Connections

- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[ReactiveCtrl_1]] - `rationale_for` [EXTRACTED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]

  #community/Multiscale*TCN*&\_Features
