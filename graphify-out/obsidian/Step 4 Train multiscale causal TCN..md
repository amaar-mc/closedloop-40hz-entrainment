---
source_file: "scripts/pipeline/run_full_pipeline.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L137"
tags:
  - community/Multiscale_TCN_&_Features
---

# Step 4: Train multiscale causal TCN.

## Connections
- [[BIDSDataProcessor]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]
- [[step_train_tcn()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features