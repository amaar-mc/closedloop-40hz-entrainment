---
source_file: "src/validation.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L458"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Closed-Loop_Control_&_Simulator
---

# Initialize validator.          Args:             output_dir: Directory for sa

## Connections
- [[ClosedLoopController]] - `uses` [INFERRED]
- [[EntrainmentSimulator]] - `uses` [INFERRED]
- [[FatigueAwareSimulator]] - `uses` [INFERRED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]
- [[StimState]] - `uses` [INFERRED]
- [[__init__()_163]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Closed-Loop_Control_&_Simulator