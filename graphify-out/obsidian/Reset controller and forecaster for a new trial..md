---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L353"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Closed-Loop_Control_&_Simulator
---

# Reset controller and forecaster for a new trial.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[reset()_56]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Closed-Loop_Control_&_Simulator