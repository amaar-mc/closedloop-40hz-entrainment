---
source_file: "archive/muse_4ch/retrain_pipeline.py"
type: "rationale"
community: "Models, Streaming & Apps"
location: "L82"
tags:
  - community/Models,_Streaming_&_Apps
---

# Load raw BIDS data, select F7/F8/T7/T8, preprocess, window, compute PAC.

## Connections

- [[BIDSDataProcessor]] - `uses` [INFERRED]
- [[EEGNet_1]] - `uses` [INFERRED]
- [[step1_process_data()]] - `rationale_for` [EXTRACTED]

  #community/Models,_Streaming_&\_Apps
