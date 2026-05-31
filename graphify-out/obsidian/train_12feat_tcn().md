---
source_file: "scripts/pipeline/run_12feat_validation.py"
type: "code"
community: "12-Feature TCN Validation"
location: "L88"
tags:
  - community/12-Feature_TCN_Validation
---

# train_12feat_tcn()

## Connections
- [[12-Feature TCN Validation Script (PAC+Context Only, N=35 Real EEG)]] - `calls` [EXTRACTED]
- [[FeatureMaskedDataset]] - `calls` [EXTRACTED]
- [[FeatureMaskedDataset (73→12 Feature Slice Dataset)]] - `calls` [EXTRACTED]
- [[Rationale Drop Spectral Features (Indices 0-60) to Prevent Anatomy Overfitting]] - `rationale_for` [EXTRACTED]
- [[Train MultiscaleCausalTCN with 12 features, save checkpoint, return path.]] - `rationale_for` [EXTRACTED]
- [[_r2()_7]] - `calls` [EXTRACTED]
- [[main()_45]] - `calls` [EXTRACTED]
- [[run_12feat_validation.py]] - `contains` [EXTRACTED]
- [[step()_36]] - `calls` [EXTRACTED]

  #community/12-Feature_TCN_Validation