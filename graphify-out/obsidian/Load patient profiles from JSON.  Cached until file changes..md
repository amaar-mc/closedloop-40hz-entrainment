---
source_file: "apps/caregiver_app.py"
type: "rationale"
community: "Models, Streaming & Apps"
location: "L129"
tags:
  - community/Models,_Streaming_&_Apps
---

# Load patient profiles from JSON.  Cached until file changes.

## Connections
- [[EEGNet_1]] - `uses` [INFERRED]
- [[SimulatedEEGAdapter]] - `uses` [INFERRED]
- [[StreamingFeatureExtractor]] - `uses` [INFERRED]
- [[TCNTemporalModel]] - `uses` [INFERRED]
- [[load_profiles()]] - `rationale_for` [EXTRACTED]

  #community/Models,_Streaming_&_Apps