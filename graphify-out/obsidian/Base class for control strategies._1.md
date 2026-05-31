---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L234"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Base class for control strategies.

## Connections
- [[ControlMethodBase_1]] - `rationale_for` [EXTRACTED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]

  #community/Closed-Loop_Control_&_Simulator