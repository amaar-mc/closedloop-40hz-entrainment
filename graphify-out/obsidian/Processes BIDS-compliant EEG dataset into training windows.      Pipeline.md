---
source_file: "src/data_loader.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L114"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Processes BIDS-compliant EEG dataset into training windows.      Pipeline:

## Connections
- [[BIDSDataProcessor]] - `rationale_for` [EXTRACTED]
- [[EEGPreprocessor]] - `uses` [INFERRED]
- [[PACComputer]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features