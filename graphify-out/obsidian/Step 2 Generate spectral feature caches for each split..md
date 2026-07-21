---
source_file: "scripts/pipeline/run_full_pipeline.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L56"
tags:
  - community/Multiscale_TCN_&_Features
---

# Step 2: Generate spectral feature caches for each split.

## Connections

- [[BIDSDataProcessor]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]
- [[step_spectral_cache()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale*TCN*&\_Features
