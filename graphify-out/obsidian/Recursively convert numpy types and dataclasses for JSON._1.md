---
source_file: "validation/experiments/tcn_integrated_simulation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L882"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Recursively convert numpy types and dataclasses for JSON.

## Connections

- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[_make_serializable()_1]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop*Control*&\_Simulator
