---
source_file: "scripts/pipeline/run_12feat_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L256"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# TCN predictive controller using only PAC+context features (no spectral).

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[TCN12FeatCtrl]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features