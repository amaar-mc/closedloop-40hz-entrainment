---
source_file: "src/validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L178"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Reset baseline buffer and state.

## Connections
- [[ClosedLoopController]] - `uses` [INFERRED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[StimState]] - `uses` [INFERRED]
- [[reset()_65]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator