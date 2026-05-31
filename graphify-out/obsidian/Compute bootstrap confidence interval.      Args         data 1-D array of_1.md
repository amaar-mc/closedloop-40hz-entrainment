---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L103"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Compute bootstrap confidence interval.      Args:         data: 1-D array of

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[bootstrap_ci()_1]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator