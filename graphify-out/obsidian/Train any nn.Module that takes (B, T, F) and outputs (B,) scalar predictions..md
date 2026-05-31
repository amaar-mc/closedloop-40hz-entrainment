---
source_file: "temporal_multiscale/comparison_models.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L168"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/Multiscale_TCN_&_Features
---

# Train any nn.Module that takes (B, T, F) and outputs (B,) scalar predictions.

## Connections
- [[SequenceDataset]] - `uses` [INFERRED]
- [[train_pytorch_model()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/Multiscale_TCN_&_Features