---
source_file: "validation/rigorous_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L667"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Compute per-method summary statistics with bootstrap CIs.      Args:

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[compute_summary_stats()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator