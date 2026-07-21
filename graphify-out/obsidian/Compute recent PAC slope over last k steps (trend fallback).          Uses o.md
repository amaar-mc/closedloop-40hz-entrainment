---
source_file: "src/validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L294"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Compute recent PAC slope over last _k_ steps (trend fallback). Uses o

## Connections

- [[ClosedLoopController]] - `uses` [INFERRED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[StimState]] - `uses` [INFERRED]
- [[_pac_trend()_1]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop*Control*&\_Simulator
