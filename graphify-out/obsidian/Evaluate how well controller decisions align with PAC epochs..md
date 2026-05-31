---
source_file: "scripts/pipeline/run_tcn_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L454"
tags:
  - community/Multiscale_TCN_&_Features
---

# Evaluate how well controller decisions align with PAC epochs.

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]
- [[evaluate_epoch_alignment()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features