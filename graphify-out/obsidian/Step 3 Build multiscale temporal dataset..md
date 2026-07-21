---
source_file: "scripts/pipeline/run_full_pipeline.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L98"
tags:
  - community/Multiscale_TCN_&_Features
---

# Step 3: Build multiscale temporal dataset.

## Connections

- [[BIDSDataProcessor]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]
- [[step_build_dataset()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale*TCN*&\_Features
