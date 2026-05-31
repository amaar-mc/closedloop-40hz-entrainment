---
source_file: "src/data_loader.py"
type: "rationale"
community: "Core Data & PAC Pipeline"
location: "L634"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Core_Data_&_PAC_Pipeline
---

# Save train/val/test splits to npz files.          Args:             splits: D

## Connections
- [[.save_splits()]] - `rationale_for` [EXTRACTED]
- [[EEGPreprocessor]] - `uses` [INFERRED]
- [[PACComputer]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Core_Data_&_PAC_Pipeline