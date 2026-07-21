---
source_file: "scripts/pipeline/run_tribe_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L238"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Run methods on both simulation backends.

## Connections

- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[TribeEnhancedSimulator]] - `uses` [INFERRED]
- [[TribeSimulatorConfig]] - `uses` [INFERRED]
- [[run_comparison()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop*Control*&\_Simulator
