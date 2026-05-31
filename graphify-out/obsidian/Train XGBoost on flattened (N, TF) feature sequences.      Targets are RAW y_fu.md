---
source_file: "temporal_multiscale/comparison_models.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L314"
tags:
  - community/Multiscale_TCN_&_Features
---

# Train XGBoost on flattened (N, T*F) feature sequences.      Targets are RAW y_fu

## Connections
- [[SequenceDataset]] - `uses` [INFERRED]
- [[train_xgboost_model()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features