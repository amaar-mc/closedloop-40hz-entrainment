---
source_file: "temporal_multiscale/per_subject_adaptation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L128"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Per-subject Ridge: blend global with locally-fit Ridge.

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[ridge_per_subject()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features