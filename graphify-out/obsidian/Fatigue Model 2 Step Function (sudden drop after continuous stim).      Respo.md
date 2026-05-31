---
source_file: "validation/experiments/fatigue_model_sensitivity.py"
type: "rationale"
community: "Control Strategies & Validation"
location: "L155"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Control_Strategies_&_Validation
---

# Fatigue Model 2: Step Function (sudden drop after continuous stim).      Respo

## Connections
- [[ControlMethodBase]] - `uses` [INFERRED]
- [[FixedScheduleControl_5]] - `uses` [INFERRED]
- [[PredictiveLookAheadControl_5]] - `uses` [INFERRED]
- [[StepFunctionSimulator]] - `rationale_for` [EXTRACTED]
- [[StimAction]] - `uses` [INFERRED]
- [[TrialMetrics]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Control_Strategies_&_Validation