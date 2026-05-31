---
source_file: "scripts/pipeline/run_12feat_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L1"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Train 12-feature TCN (PAC+context only) and run 35-subject controller replay.  D

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[run_12feat_validation.py]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features