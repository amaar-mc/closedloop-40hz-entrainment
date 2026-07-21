---
source_file: "validation/rigorous_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L549"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Run one trial per subject with randomized simulator parameters. Args:

## Connections

- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[run_population_diverse()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop*Control*&\_Simulator
