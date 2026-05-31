---
source_file: "temporal_multiscale/run_multiseed_study.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L90"
tags:
  - community/Multiscale_TCN_&_Features
---

# Train Full TCN for one seed and return per-seed metrics.      CRITICAL: Datasets

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SequenceDataset]] - `uses` [INFERRED]
- [[train_one_seed()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features