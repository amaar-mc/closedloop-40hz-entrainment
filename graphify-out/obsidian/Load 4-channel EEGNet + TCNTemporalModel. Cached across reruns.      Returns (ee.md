---
source_file: "apps/caregiver_app.py"
type: "rationale"
community: "Models, Streaming & Apps"
location: "L82"
tags:
  - community/Models,_Streaming_&_Apps
---

# Load 4-channel EEGNet + TCNTemporalModel. Cached across reruns.      Returns (ee

## Connections
- [[EEGNet_1]] - `uses` [INFERRED]
- [[SimulatedEEGAdapter]] - `uses` [INFERRED]
- [[StreamingFeatureExtractor]] - `uses` [INFERRED]
- [[TCNTemporalModel]] - `uses` [INFERRED]
- [[load_models()]] - `rationale_for` [EXTRACTED]

  #community/Models,_Streaming_&_Apps