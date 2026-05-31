---
source_file: "src/validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L422"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Closed-Loop_Control_&_Simulator
---

# Initialize oracle control.          Args:             pac_target: Target PAC

## Connections
- [[ClosedLoopController]] - `uses` [INFERRED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[StimState]] - `uses` [INFERRED]
- [[__init__()_162]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Closed-Loop_Control_&_Simulator