---
source_file: "scripts/pipeline/run_closed_loop_demo.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L173"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Perfect knowledge — stimulate when below target.

## Connections

- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[OracleControl_1]] - `rationale_for` [EXTRACTED]
- [[StimAction]] - `uses` [INFERRED]

  #community/Closed-Loop*Control*&\_Simulator
