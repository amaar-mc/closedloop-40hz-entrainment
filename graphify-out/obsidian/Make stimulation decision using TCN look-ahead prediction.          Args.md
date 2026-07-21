---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L390"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Make stimulation decision using TCN look-ahead prediction. Args:

## Connections

- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[step()_61]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop*Control*&\_Simulator
