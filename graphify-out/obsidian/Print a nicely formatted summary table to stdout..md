---
source_file: "validation/rigorous_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L794"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Print a nicely formatted summary table to stdout.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[print_summary_table()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator