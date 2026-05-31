---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L778"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Format a value with its 95% CI.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[_fmt_ci()_1]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator