---
source_file: "src/validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L285"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Closed-Loop_Control_&_Simulator
---

# Reset state for a new trial.

## Connections
- [[ClosedLoopController]] - `uses` [INFERRED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[StimState]] - `uses` [INFERRED]
- [[reset()_66]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Closed-Loop_Control_&_Simulator