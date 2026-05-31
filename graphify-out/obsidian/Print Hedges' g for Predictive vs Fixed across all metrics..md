---
source_file: "validation/rigorous_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L851"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Print Hedges' g for Predictive vs Fixed across all metrics.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[print_effect_sizes_predictive_vs_fixed()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator