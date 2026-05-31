---
source_file: "validation/rigorous_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L256"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Compute bootstrap confidence interval.      Args:         data: 1-D array of

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[bootstrap_ci()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator