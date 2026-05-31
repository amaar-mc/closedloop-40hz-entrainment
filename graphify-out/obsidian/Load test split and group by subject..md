---
source_file: "temporal_multiscale/per_subject_adaptation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L62"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Load test split and group by subject.

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[load_test_by_subject()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features