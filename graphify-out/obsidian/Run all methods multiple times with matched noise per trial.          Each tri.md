---
source_file: "src/validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L612"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Run all methods multiple times with matched noise per trial.          Each tri

## Connections
- [[ClosedLoopController]] - `uses` [INFERRED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[StimState]] - `uses` [INFERRED]
- [[run_all()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator