---
source_file: "validation/experiments/fatigue_model_sensitivity.py"
type: "rationale"
community: "Control Strategies & Validation"
location: "L147"
tags:
  - community/Control_Strategies_&_Validation
---

# Return human-readable model description.

## Connections
- [[ControlMethodBase]] - `uses` [INFERRED]
- [[FixedScheduleControl_5]] - `uses` [INFERRED]
- [[PredictiveLookAheadControl_5]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[TrialMetrics]] - `uses` [INFERRED]
- [[get_description()]] - `rationale_for` [EXTRACTED]

  #community/Control_Strategies_&_Validation