---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L786"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Print a formatted summary table to stdout.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[print_summary_table()_2]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator