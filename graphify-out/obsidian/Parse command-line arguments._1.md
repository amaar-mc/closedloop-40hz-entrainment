---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L908"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Parse command-line arguments.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[parse_args()_20]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator