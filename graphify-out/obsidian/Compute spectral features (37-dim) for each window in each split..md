---
source_file: "archive/muse_4ch/retrain_pipeline.py"
type: "rationale"
community: "Models, Streaming & Apps"
location: "L135"
tags:
  - community/Models,_Streaming_&_Apps
---

# Compute spectral features (37-dim) for each window in each split.

## Connections
- [[BIDSDataProcessor]] - `uses` [INFERRED]
- [[EEGNet_1]] - `uses` [INFERRED]
- [[step2_spectral_caches()]] - `rationale_for` [EXTRACTED]

  #community/Models,_Streaming_&_Apps