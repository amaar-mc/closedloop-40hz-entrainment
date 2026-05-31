---
source_file: "scripts/pipeline/run_12feat_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L54"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Load multiscale npz, slice features to PAC+context only.

## Connections
- [[FeatureMaskedDataset]] - `rationale_for` [EXTRACTED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features