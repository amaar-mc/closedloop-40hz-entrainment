---
source_file: "tests/test_model_registry.py"
type: "rationale"
community: "Models, Streaming & Apps"
location: "L96"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Models,_Streaming_&_Apps
---

# Test 4: TCNTemporalModel wraps RealtimePACForecaster and exposes step/reset.

## Connections
- [[ModelRegistry]] - `uses` [INFERRED]
- [[TCNTemporalModel]] - `uses` [INFERRED]
- [[TemporalModel]] - `uses` [INFERRED]
- [[test_tcn_temporal_model_wraps_forecaster()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Models,_Streaming_&_Apps