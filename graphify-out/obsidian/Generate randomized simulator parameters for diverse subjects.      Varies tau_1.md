---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L593"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Generate randomized simulator parameters for diverse subjects.      Varies tau

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[generate_subject_parameters()_1]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator