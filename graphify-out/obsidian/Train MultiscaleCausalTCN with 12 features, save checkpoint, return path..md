---
source_file: "scripts/pipeline/run_12feat_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L89"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Train MultiscaleCausalTCN with 12 features, save checkpoint, return path.

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[train_12feat_tcn()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features