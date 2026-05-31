---
source_file: "apps/demo.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L386"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# Produces 40 Hz click-train audio during stimulation periods.

## Connections
- [[AudioEngine]] - `rationale_for` [EXTRACTED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]

  #community/Closed-Loop_Control_&_Simulator