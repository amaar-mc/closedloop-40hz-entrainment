---
source_file: "validation/experiments/fatigue_model_sensitivity.py"
type: "rationale"
community: "Control Strategies & Validation"
location: "L668"
tags:
  - community/Control_Strategies_&_Validation
---

# Print a formatted summary table across all fatigue models.      Args:

## Connections
- [[ControlMethodBase]] - `uses` [INFERRED]
- [[FixedScheduleControl_5]] - `uses` [INFERRED]
- [[PredictiveLookAheadControl_5]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[TrialMetrics]] - `uses` [INFERRED]
- [[print_summary_table()_1]] - `rationale_for` [EXTRACTED]

  #community/Control_Strategies_&_Validation