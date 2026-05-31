---
source_file: "scripts/pipeline/run_tcn_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L482"
tags:
  - community/Multiscale_TCN_&_Features
---

# Evaluate how early the controller responds to PAC drop transitions.      For e

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]
- [[evaluate_transition_anticipation()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features