---
source_file: "scripts/tools/demo_streaming.py"
type: "rationale"
community: "Models, Streaming & Apps"
location: "L66"
tags:
  - community/Models,_Streaming_&_Apps
---

# Return 'mps' if available, else 'cuda' if available, else 'cpu'.

## Connections
- [[EEGNet_1]] - `uses` [INFERRED]
- [[PersonalizationModule]] - `uses` [INFERRED]
- [[SimulatedEEGAdapter]] - `uses` [INFERRED]
- [[StreamingFeatureExtractor]] - `uses` [INFERRED]
- [[auto_device()]] - `rationale_for` [EXTRACTED]

  #community/Models,_Streaming_&_Apps