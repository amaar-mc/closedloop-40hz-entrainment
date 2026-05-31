---
source_file: "validation/experiments/fatigue_model_sensitivity.py"
type: "rationale"
community: "Control Strategies & Validation"
location: "L408"
tags:
  - community/Control_Strategies_&_Validation
---

# Run one simulation trial and return metrics.      Args:         method: Contr

## Connections
- [[ControlMethodBase]] - `uses` [INFERRED]
- [[FixedScheduleControl_5]] - `uses` [INFERRED]
- [[PredictiveLookAheadControl_5]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[TrialMetrics]] - `uses` [INFERRED]
- [[run_single_trial()_1]] - `rationale_for` [EXTRACTED]

  #community/Control_Strategies_&_Validation