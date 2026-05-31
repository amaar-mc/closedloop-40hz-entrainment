---
source_file: "scripts/pipeline/run_closed_loop_demo.py"
type: "code"
community: "Closed-Loop Control & Simulator"
location: "L42"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# FixedScheduleControl

## Connections
- [[40s ON + 20s OFF (standard clinical protocol).]] - `rationale_for` [EXTRACTED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[__init__()_80]] - `method` [EXTRACTED]
- [[main()_40]] - `calls` [EXTRACTED]
- [[reset()_18]] - `method` [EXTRACTED]
- [[run_closed_loop_demo.py]] - `contains` [EXTRACTED]
- [[step()_18]] - `method` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator