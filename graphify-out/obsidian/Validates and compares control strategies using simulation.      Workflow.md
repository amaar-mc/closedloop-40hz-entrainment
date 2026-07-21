---
source_file: "src/validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L446"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Validates and compares control strategies using simulation. Workflow:

## Connections

- [[ClosedLoopController]] - `uses` [INFERRED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[SimulationValidator]] - `rationale_for` [EXTRACTED]
- [[StimAction]] - `uses` [INFERRED]
- [[StimState]] - `uses` [INFERRED]

  #community/Closed-Loop*Control*&\_Simulator
