---
source_file: "scripts/pipeline/run_12feat_validation.py"
type: "code"
community: "12-Feature TCN Validation"
location: "line 53"
tags:
  - community/12-Feature_TCN_Validation
---

# FeatureMaskedDataset (73→12 Feature Slice Dataset)

## Connections
- [[Rationale Drop Spectral Features (Indices 0-60) to Prevent Anatomy Overfitting]] - `rationale_for` [EXTRACTED]
- [[train_12feat_tcn()]] - `calls` [EXTRACTED]

  #community/12-Feature_TCN_Validation