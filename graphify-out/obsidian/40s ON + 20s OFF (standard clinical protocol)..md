---
source_file: "scripts/pipeline/run_closed_loop_demo.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L43"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# 40s ON + 20s OFF (standard clinical protocol).

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[FixedScheduleControl_1]] - `rationale_for` [EXTRACTED]
- [[StimAction]] - `uses` [INFERRED]

  #community/Closed-Loop_Control_&_Simulator