---
source_file: "scripts/pipeline/run_12feat_validation.py"
type: "code"
community: "12-Feature TCN Validation"
location: "line 1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/12-Feature_TCN_Validation
---

# Rationale: Drop Spectral Features (Indices 0-60) to Prevent Anatomy Overfitting

## Connections
- [[FeatureMaskedDataset (73→12 Feature Slice Dataset)]] - `rationale_for` [EXTRACTED]
- [[train_12feat_tcn()]] - `rationale_for` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/12-Feature_TCN_Validation