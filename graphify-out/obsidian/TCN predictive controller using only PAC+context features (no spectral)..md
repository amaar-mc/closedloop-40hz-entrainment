---
source_file: "scripts/pipeline/run_12feat_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L256"
tags:
  - community/Multiscale_TCN_&_Features
---

# TCN predictive controller using only PAC+context features (no spectral).

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[TCN12FeatCtrl]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features