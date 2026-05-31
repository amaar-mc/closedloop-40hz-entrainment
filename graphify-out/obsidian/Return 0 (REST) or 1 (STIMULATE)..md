---
source_file: "validation/rigorous_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L73"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Closed-Loop_Control_&_Simulator
---

# Return 0 (REST) or 1 (STIMULATE).

## Connections
- [[.step()_48]] - `rationale_for` [EXTRACTED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Closed-Loop_Control_&_Simulator