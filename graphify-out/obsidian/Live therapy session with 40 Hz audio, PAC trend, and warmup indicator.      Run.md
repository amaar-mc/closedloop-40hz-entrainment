---
source_file: "apps/caregiver_app.py"
type: "rationale"
community: "Models, Streaming & Apps"
location: "L311"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Models,_Streaming_&_Apps
---

# Live therapy session with 40 Hz audio, PAC trend, and warmup indicator.      Run

## Connections
- [[EEGNet_1]] - `uses` [INFERRED]
- [[SimulatedEEGAdapter]] - `uses` [INFERRED]
- [[StreamingFeatureExtractor]] - `uses` [INFERRED]
- [[TCNTemporalModel]] - `uses` [INFERRED]
- [[render_session()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Models,_Streaming_&_Apps