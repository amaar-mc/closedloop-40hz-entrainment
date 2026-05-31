---
source_file: "scripts/pipeline/run_full_pipeline.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L327"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Step 5: Replay real data through controllers including TCN-based predictive.

## Connections
- [[BIDSDataProcessor]] - `uses` [INFERRED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SpectralFeatureExtractor]] - `uses` [INFERRED]
- [[step_replay_with_tcn()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features