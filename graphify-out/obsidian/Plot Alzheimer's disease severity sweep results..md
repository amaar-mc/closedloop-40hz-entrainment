---
source_file: "scripts/pipeline/run_tribe_validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L369"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Plot Alzheimer's disease severity sweep results.

## Connections
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[TribeEnhancedSimulator]] - `uses` [INFERRED]
- [[TribeSimulatorConfig]] - `uses` [INFERRED]
- [[plot_disease_sweep()]] - `rationale_for` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator