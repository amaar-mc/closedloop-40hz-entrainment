---
source_file: "validation/experiments/fatigue_model_sensitivity.py"
type: "rationale"
community: "Control Strategies & Validation"
location: "L131"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Control_Strategies_&_Validation
---

# Simulate one time step with exponential fatigue dynamics.

## Connections
- [[.step()_53]] - `rationale_for` [EXTRACTED]
- [[ControlMethodBase]] - `uses` [INFERRED]
- [[FixedScheduleControl_5]] - `uses` [INFERRED]
- [[PredictiveLookAheadControl_5]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[TrialMetrics]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Control_Strategies_&_Validation