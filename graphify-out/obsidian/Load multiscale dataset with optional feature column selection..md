---
source_file: "results/rigor_audit/run_feature_ablation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L42"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Load multiscale dataset with optional feature column selection.

## Connections
- [[MaskedSequenceDataset]] - `rationale_for` [EXTRACTED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features