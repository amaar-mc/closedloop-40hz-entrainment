---
source_file: "validation/experiments/fatigue_model_sensitivity.py"
type: "rationale"
community: "Control Strategies & Validation"
location: "L460"
tags:
  - community/Control_Strategies_&_Validation
---

# Configuration for a fatigue model experiment.

## Connections
- [[ControlMethodBase]] - `uses` [INFERRED]
- [[FatigueModelConfig]] - `rationale_for` [EXTRACTED]
- [[FixedScheduleControl_5]] - `uses` [INFERRED]
- [[PredictiveLookAheadControl_5]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[TrialMetrics]] - `uses` [INFERRED]

  #community/Control_Strategies_&_Validation