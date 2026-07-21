---
source_file: "scripts/pipeline/run_full_pipeline.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L31"
tags:
  - community/Multiscale_TCN_&_Features
---

# Step 1: Preprocess raw BIDS data into train/val/test splits.

## Connections

- [[BIDSDataProcessor]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]
- [[step_preprocess()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale*TCN*&\_Features
