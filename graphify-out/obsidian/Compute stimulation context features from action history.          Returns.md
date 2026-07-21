---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L364"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Compute stimulation context features from action history. Returns:

## Connections

- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[_compute_stim_context()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop*Control*&\_Simulator
