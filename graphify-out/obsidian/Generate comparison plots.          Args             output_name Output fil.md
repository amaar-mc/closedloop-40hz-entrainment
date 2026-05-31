---
source_file: "src/validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L718"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Generate comparison plots.          Args:             output_name: Output fil

## Connections
- [[ClosedLoopController]] - `uses` [INFERRED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[StimState]] - `uses` [INFERRED]
- [[plot_comparison()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator