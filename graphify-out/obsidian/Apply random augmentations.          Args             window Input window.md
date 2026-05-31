---
source_file: "src/training.py"
type: "rationale"
community: "Core Data & PAC Pipeline"
location: "L130"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Core_Data_&_PAC_Pipeline
---

# Apply random augmentations.          Args:             window: Input window

## Connections
- [[EEGNet_1]] - `uses` [INFERRED]
- [[EEGWindowDataset]] - `uses` [INFERRED]
- [[augment()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Core_Data_&_PAC_Pipeline