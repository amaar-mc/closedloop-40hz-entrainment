---
source_file: "scripts/pipeline/run_tcn_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L265"
tags:
  - community/Multiscale_TCN_&_Features
---

# Hybrid controller: reactive base + TCN proactive override.      The reactive c

## Connections
- [[HybridTCNCtrl]] - `rationale_for` [EXTRACTED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]

  #community/Multiscale_TCN_&_Features