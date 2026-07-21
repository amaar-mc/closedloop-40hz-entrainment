---
source_file: "validation/experiments/fatigue_model_sensitivity.py"
type: "rationale"
community: "Control Strategies & Validation"
location: "L468"
tags:
  - community/Control_Strategies_&_Validation
---

# Factory function to create a simulator instance for a given fatigue model.

## Connections

- [[ControlMethodBase]] - `uses` [INFERRED]
- [[FixedScheduleControl_5]] - `uses` [INFERRED]
- [[PredictiveLookAheadControl_5]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[TrialMetrics]] - `uses` [INFERRED]
- [[create_simulator()]] - `rationale_for` [EXTRACTED]

  #community/Control*Strategies*&\_Validation
