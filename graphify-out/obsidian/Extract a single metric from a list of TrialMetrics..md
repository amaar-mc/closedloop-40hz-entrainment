---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L689"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Extract a single metric from a list of TrialMetrics.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[extract_metric_array()_1]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator