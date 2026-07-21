---
source_file: "scripts/pipeline/run_tcn_validation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L610"
tags:
  - community/Multiscale_TCN_&_Features
---

# Wilcoxon signed-rank test with zero-difference handling.

## Connections

- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]
- [[paired_wilcoxon()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale*TCN*&\_Features
