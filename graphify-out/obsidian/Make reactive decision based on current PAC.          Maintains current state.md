---
source_file: "src/validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L184"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Make reactive decision based on current PAC. Maintains current state

## Connections

- [[ClosedLoopController]] - `uses` [INFERRED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[StimState]] - `uses` [INFERRED]
- [[step()_69]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop*Control*&\_Simulator
