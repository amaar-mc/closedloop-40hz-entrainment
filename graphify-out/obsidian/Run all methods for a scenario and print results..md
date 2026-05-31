---
source_file: "scripts/pipeline/run_closed_loop_demo.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L254"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Run all methods for a scenario and print results.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[run_scenario()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator