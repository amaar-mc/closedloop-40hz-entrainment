---
source_file: "validation/rigorous_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L70"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Closed-Loop_Control_&_Simulator
---

# Reset state for a new trial.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[reset()_49]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Closed-Loop_Control_&_Simulator