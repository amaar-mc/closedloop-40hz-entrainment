---
source_file: "validation/rigorous_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L78"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Fixed 40 s ON + 20 s OFF schedule (control condition).

## Connections

- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[FixedScheduleControl_5]] - `rationale_for` [EXTRACTED]
- [[StimAction]] - `uses` [INFERRED]

  #community/Closed-Loop*Control*&\_Simulator
