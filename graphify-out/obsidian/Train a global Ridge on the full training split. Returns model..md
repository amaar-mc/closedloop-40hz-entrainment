---
source_file: "temporal_multiscale/per_subject_adaptation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L113"
tags:
  - community/Multiscale_TCN_&_Features
---

# Train a global Ridge on the full training split. Returns model.

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[ridge_global()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features