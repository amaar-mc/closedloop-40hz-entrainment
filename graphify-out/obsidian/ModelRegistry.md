---
source_file: "temporal_multiscale/model_registry.py"
type: "code"
community: "Models, Streaming & Apps"
location: "L137"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Models,_Streaming_&_Apps
---

# ModelRegistry

## Connections
- [[.__init__()_68]] - `method` [EXTRACTED]
- [[.available()]] - `method` [EXTRACTED]
- [[.get()]] - `method` [EXTRACTED]
- [[.register()]] - `method` [EXTRACTED]
- [[Bonus register() rejects objects that don't satisfy TemporalModel Protocol.]] - `uses` [INFERRED]
- [[Name-keyed registry for TemporalModel instances.      Models are validated at re]] - `rationale_for` [EXTRACTED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[Test 1 ModelRegistry registers and retrieves a TCN model by name.]] - `uses` [INFERRED]
- [[Test 2 registry.available() lists registered model names.]] - `uses` [INFERRED]
- [[Test 3 registry.get('nonexistent') raises KeyError with available model list.]] - `uses` [INFERRED]
- [[Test 4 TCNTemporalModel wraps RealtimePACForecaster and exposes stepreset.]] - `uses` [INFERRED]
- [[Test 5 step() returns None until lookback windows accumulated, then dict.]] - `uses` [INFERRED]
- [[Test 6 isinstance(tcn_model, TemporalModel) returns True.]] - `uses` [INFERRED]
- [[Tests for temporal_multiscalemodel_registry.py.  Verifies 1. ModelRegistry reg]] - `uses` [INFERRED]
- [[build_default_registry()]] - `calls` [EXTRACTED]
- [[build_default_registry() returns registry with 'tcn' pre-registered.]] - `uses` [INFERRED]
- [[model_registry.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/Models,_Streaming_&_Apps