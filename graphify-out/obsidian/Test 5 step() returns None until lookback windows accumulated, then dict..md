---
source_file: "tests/test_model_registry.py"
type: "rationale"
community: "Models, Streaming & Apps"
location: "L108"
tags:
  - community/Models,_Streaming_&_Apps
---

# Test 5: step() returns None until lookback windows accumulated, then dict.

## Connections

- [[ModelRegistry]] - `uses` [INFERRED]
- [[TCNTemporalModel]] - `uses` [INFERRED]
- [[TemporalModel]] - `uses` [INFERRED]
- [[test_tcn_step_returns_none_then_dict()]] - `rationale_for` [EXTRACTED]

  #community/Models,_Streaming_&\_Apps
