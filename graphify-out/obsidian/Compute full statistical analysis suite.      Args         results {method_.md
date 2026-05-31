---
source_file: "validation/rigorous_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L731"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Compute full statistical analysis suite.      Args:         results: {method_

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[compute_all_statistics()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator