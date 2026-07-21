---
source_file: "apps/demo.py"
type: "rationale"
community: "Closed-Loop Control & Simulator"
location: "L89"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# 40s ON + 20s OFF (standard clinical protocol).

## Connections

- [[FixedScheduleControl_4]] - `rationale_for` [EXTRACTED]
- [[RealtimePACForecaster]] - `uses` [INFERRED]
- [[StimAction]] - `uses` [INFERRED]

  #community/Closed-Loop*Control*&\_Simulator
