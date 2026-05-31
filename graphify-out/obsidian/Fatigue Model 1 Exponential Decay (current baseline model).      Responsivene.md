---
source_file: "validation/experiments/fatigue_model_sensitivity.py"
type: "rationale"
community: "Control Strategies & Validation"
location: "L84"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Control_Strategies_&_Validation
---

# Fatigue Model 1: Exponential Decay (current baseline model).      Responsivene

## Connections
- [[ControlMethodBase]] - `uses` [INFERRED]
- [[ExponentialDecaySimulator]] - `rationale_for` [EXTRACTED]
- [[FixedScheduleControl_5]] - `uses` [INFERRED]
- [[PredictiveLookAheadControl_5]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[TrialMetrics]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Control_Strategies_&_Validation