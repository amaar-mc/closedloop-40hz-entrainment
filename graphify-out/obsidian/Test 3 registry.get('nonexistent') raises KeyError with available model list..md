---
source_file: "tests/test_model_registry.py"
type: "rationale"
community: "Models, Streaming & Apps"
location: "L78"
tags:
  - community/Models,_Streaming_&_Apps
---

# Test 3: registry.get('nonexistent') raises KeyError with available model list.

## Connections
- [[ModelRegistry]] - `uses` [INFERRED]
- [[TCNTemporalModel]] - `uses` [INFERRED]
- [[TemporalModel]] - `uses` [INFERRED]
- [[test_registry_get_nonexistent_raises_key_error()]] - `rationale_for` [EXTRACTED]

  #community/Models,_Streaming_&_Apps