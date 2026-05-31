---
source_file: "scripts/pipeline/run_full_pipeline.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L1"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Full end-to-end pipeline: preprocess → spectral cache → temporal dataset → train

## Connections
- [[BIDSDataProcessor]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]
- [[run_full_pipeline.py]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features