---
source_file: "scripts/pipeline/run_tribe_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L175"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Closed-Loop_Control_&_Simulator
---

# Perfect knowledge oracle.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[OracleControl_2]] - `rationale_for` [EXTRACTED]
- [[StimAction]] - `uses` [INFERRED]
- [[TribeEnhancedSimulator]] - `uses` [INFERRED]
- [[TribeSimulatorConfig]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Closed-Loop_Control_&_Simulator