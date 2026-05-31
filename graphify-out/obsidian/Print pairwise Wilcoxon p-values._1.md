---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L823"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Print pairwise Wilcoxon p-values.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[print_wilcoxon_table()_1]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator