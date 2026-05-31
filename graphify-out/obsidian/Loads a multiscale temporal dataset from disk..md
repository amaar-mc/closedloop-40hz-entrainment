---
source_file: "validation/experiments/run_all_experiments.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L68"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Loads a multiscale temporal dataset from disk.

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[ModelConfig_1]] - `uses` [INFERRED]
- [[MultiTaskTCN]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SequenceDataset_1]] - `rationale_for` [EXTRACTED]
- [[TransformerConfig]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features