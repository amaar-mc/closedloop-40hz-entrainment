---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L630"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Run one trial per subject with randomized simulator parameters.      Args:

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[run_population_diverse()_1]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator