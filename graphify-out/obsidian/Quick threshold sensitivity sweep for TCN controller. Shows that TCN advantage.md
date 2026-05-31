---
source_file: "scripts/pipeline/run_threshold_sweep.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L1"
tags:
  - community/Multiscale_TCN_&_Features
---

# Quick threshold sensitivity sweep for TCN controller. Shows that TCN advantage

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]
- [[run_threshold_sweep.py]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features