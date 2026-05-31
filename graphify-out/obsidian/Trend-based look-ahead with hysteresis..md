---
source_file: "scripts/pipeline/run_tribe_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L115"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Closed-Loop_Control_&_Simulator
---

# Trend-based look-ahead with hysteresis.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[PredictiveLookAheadControl_3]] - `rationale_for` [EXTRACTED]
- [[StimAction]] - `uses` [INFERRED]
- [[TribeEnhancedSimulator]] - `uses` [INFERRED]
- [[TribeSimulatorConfig]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Closed-Loop_Control_&_Simulator