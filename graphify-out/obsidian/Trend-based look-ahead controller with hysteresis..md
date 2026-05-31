---
source_file: "scripts/pipeline/run_closed_loop_demo.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L106"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Closed-Loop_Control_&_Simulator
---

# Trend-based look-ahead controller with hysteresis.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[PredictiveLookAheadControl_1]] - `rationale_for` [EXTRACTED]
- [[StimAction]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Closed-Loop_Control_&_Simulator