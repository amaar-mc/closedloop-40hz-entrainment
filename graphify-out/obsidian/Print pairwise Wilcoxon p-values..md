---
source_file: "validation/rigorous_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L831"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Print pairwise Wilcoxon p-values.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[print_wilcoxon_table()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator