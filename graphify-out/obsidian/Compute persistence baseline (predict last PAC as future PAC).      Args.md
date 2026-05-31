---
source_file: "validation/experiments/run_all_experiments.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L270"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Compute persistence baseline (predict last PAC as future PAC).      Args:

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[ModelConfig_1]] - `uses` [INFERRED]
- [[MultiTaskTCN]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[TransformerConfig]] - `uses` [INFERRED]
- [[_persistence_baseline()_1]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features