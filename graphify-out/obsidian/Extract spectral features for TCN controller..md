---
source_file: "scripts/pipeline/run_tcn_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L106"
tags:
  - community/Multiscale_TCN_&_Features
---

# Extract spectral features for TCN controller.

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]
- [[extract_spectral_features()_2]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features