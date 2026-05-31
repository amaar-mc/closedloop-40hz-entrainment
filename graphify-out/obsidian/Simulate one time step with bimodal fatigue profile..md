---
source_file: "validation/experiments/fatigue_model_sensitivity.py"
type: "rationale"
community: "Control Strategies & Validation"
location: "L297"
tags:
  - community/Control_Strategies_&_Validation
---

# Simulate one time step with bimodal fatigue profile.

## Connections
- [[ControlMethodBase]] - `uses` [INFERRED]
- [[FixedScheduleControl_5]] - `uses` [INFERRED]
- [[PredictiveLookAheadControl_5]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[TrialMetrics]] - `uses` [INFERRED]
- [[step()_56]] - `rationale_for` [EXTRACTED]

  #community/Control_Strategies_&_Validation