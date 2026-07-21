---
source_file: "src/validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L161"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Initialize reactive control. Args: window_size: Baseline

## Connections

- [[ClosedLoopController]] - `uses` [INFERRED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[StimState]] - `uses` [INFERRED]
- [[__init__()_160]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop*Control*&\_Simulator
