---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L843"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Print Hedges' g for TCN-Predictive vs all other methods.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[print_tcn_vs_others()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator