---
source_file: "validation/experiments/run_all_experiments.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L215"
tags:
  - community/Multiscale_TCN_&_Features
---

# Evaluate model on a data split.      Args:         model: Trained model.

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[ModelConfig_1]] - `uses` [INFERRED]
- [[MultiTaskTCN]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[TransformerConfig]] - `uses` [INFERRED]
- [[evaluate()_8]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features