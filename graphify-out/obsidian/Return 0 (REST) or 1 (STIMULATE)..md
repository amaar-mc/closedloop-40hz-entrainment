---
source_file: "validation/rigorous_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L73"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Return 0 (REST) or 1 (STIMULATE).

## Connections

- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[step()_49]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop*Control*&\_Simulator
