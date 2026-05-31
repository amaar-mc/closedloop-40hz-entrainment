---
source_file: "scripts/pipeline/run_tcn_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L596"
tags:
  - community/Multiscale_TCN_&_Features
---

# Compute Hedges' g with 95% CI between paired samples.

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]
- [[hedges_g()_1]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features