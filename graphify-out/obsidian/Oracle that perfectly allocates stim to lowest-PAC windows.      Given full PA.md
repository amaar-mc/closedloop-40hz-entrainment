---
source_file: "scripts/pipeline/run_tcn_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L418"
tags:
  - community/Multiscale_TCN_&_Features
---

# Oracle that perfectly allocates stim to lowest-PAC windows.      Given full PA

## Connections
- [[AlignmentOracleCtrl]] - `rationale_for` [EXTRACTED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]

  #community/Multiscale_TCN_&_Features