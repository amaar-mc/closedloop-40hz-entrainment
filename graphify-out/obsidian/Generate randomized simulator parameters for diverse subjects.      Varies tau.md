---
source_file: "validation/rigorous_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L512"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Generate randomized simulator parameters for diverse subjects.      Varies tau

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[generate_subject_parameters()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator