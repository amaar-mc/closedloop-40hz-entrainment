---
source_file: "src/validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L118"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Fixed 40s ON + 20s OFF schedule (control condition).

## Connections

- [[ClosedLoopController]] - `uses` [INFERRED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[FixedScheduleControl_7]] - `rationale_for` [EXTRACTED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[StimState]] - `uses` [INFERRED]

  #community/Closed-Loop*Control*&\_Simulator
