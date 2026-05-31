---
source_file: "validation/experiments/fatigue_model_sensitivity.py"
type: "rationale"
community: "Control Strategies & Validation"
location: "L531"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Control_Strategies_&_Validation
---

# Run a full experiment for one fatigue model.      Compares Fixed Schedule vs P

## Connections
- [[ControlMethodBase]] - `uses` [INFERRED]
- [[FixedScheduleControl_5]] - `uses` [INFERRED]
- [[PredictiveLookAheadControl_5]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[TrialMetrics]] - `uses` [INFERRED]
- [[run_fatigue_model_experiment()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Control_Strategies_&_Validation