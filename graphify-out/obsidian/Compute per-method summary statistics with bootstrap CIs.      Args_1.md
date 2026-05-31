---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L697"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Compute per-method summary statistics with bootstrap CIs.      Args:

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[compute_summary_stats()_1]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator