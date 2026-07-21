---
source_file: "validation/rigorous_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L924"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Recursively convert numpy types and dataclasses for JSON.

## Connections

- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[_make_serializable()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop*Control*&\_Simulator
