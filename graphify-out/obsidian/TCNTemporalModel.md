---
source_file: "temporal_multiscale/model_registry.py"
type: "code"
community: "Models, Streaming & Apps"
location: "L75"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Models,_Streaming_&_Apps
---

# TCNTemporalModel

## Connections
- [[.__init__()_67]] - `method` [EXTRACTED]
- [[.reset()_10]] - `method` [EXTRACTED]
- [[.step()_9]] - `method` [EXTRACTED]
- [[Adapter that wraps RealtimePACForecaster to satisfy the TemporalModel Protocol.]] - `rationale_for` [EXTRACTED]
- [[Append a session record to the given patient and clear cache.]] - `uses` [INFERRED]
- [[Bonus register() rejects objects that don't satisfy TemporalModel Protocol.]] - `uses` [INFERRED]
- [[Convert raw PAC to 0-100 Brain Sync Level for caregiver display.]] - `uses` [INFERRED]
- [[Ensure all session-state keys exist with defaults.]] - `uses` [INFERRED]
- [[Entry point — configure page, init state, route to active page.]] - `uses` [INFERRED]
- [[Grid of patient cards with Start Session and View History actions.]] - `uses` [INFERRED]
- [[Landing page with app title and call-to-action.]] - `uses` [INFERRED]
- [[Live therapy session with 40 Hz audio, PAC trend, and warmup indicator.      Run]] - `uses` [INFERRED]
- [[Load 4-channel EEGNet + TCNTemporalModel. Cached across reruns.      Returns (ee]] - `uses` [INFERRED]
- [[Load patient profiles from JSON.  Cached until file changes.]] - `uses` [INFERRED]
- [[Look up a patient by ID from the cached profiles.]] - `uses` [INFERRED]
- [[Map internal metric keys to plain-language labels.]] - `uses` [INFERRED]
- [[NeuroCare 40Hz Therapy — Caregiver Dashboard  Multi-page Streamlit app for careg]] - `uses` [INFERRED]
- [[One second of 40 Hz click-train, loopable WAV bytes for st.audio.]] - `uses` [INFERRED]
- [[Per-patient session history table and summary metrics.]] - `uses` [INFERRED]
- [[Persistent sidebar with hardware status, Real EEG toggle, and navigation.]] - `uses` [INFERRED]
- [[Post-session summary with plain-language metrics and session saving.]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[Set the active page in session state.]] - `uses` [INFERRED]
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