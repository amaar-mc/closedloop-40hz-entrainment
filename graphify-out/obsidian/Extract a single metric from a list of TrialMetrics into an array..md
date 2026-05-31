---
source_file: "validation/rigorous_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L659"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Extract a single metric from a list of TrialMetrics into an array.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[extract_metric_array()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator