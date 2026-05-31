---
source_file: "src/validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L432"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Make optimal decision based on perfect information.          Args:

## Connections
- [[ClosedLoopController]] - `uses` [INFERRED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[StimState]] - `uses` [INFERRED]
- [[step()_71]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator