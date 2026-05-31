---
source_file: "src/data_loader.py"
type: "rationale"
community: "Core Data & PAC Pipeline"
location: "L450"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Core_Data_&_PAC_Pipeline
---

# Process entire BIDS dataset.          Pipeline per subject:             1. Lo

## Connections
- [[.process_dataset()]] - `rationale_for` [EXTRACTED]
- [[EEGPreprocessor]] - `uses` [INFERRED]
- [[PACComputer]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Core_Data_&_PAC_Pipeline