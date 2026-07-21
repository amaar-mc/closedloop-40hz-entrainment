---
source_file: "scripts/pipeline/run_12feat_validation.py"
type: "code"
community: "Multiscale TCN & Features"
location: "L53"
tags:
  - community/Multiscale_TCN_&_Features
---

# FeatureMaskedDataset

## Connections

- [[Dataset]] - `inherits` [EXTRACTED]
- [[Load multiscale npz, slice features to PAC+context only.]] - `rationale_for` [EXTRACTED]
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[__getitem__()_14]] - `method` [EXTRACTED]
- [[__init__()_95]] - `method` [EXTRACTED]
- [[__len__()_14]] - `method` [EXTRACTED]
- [[run_12feat_validation.py]] - `contains` [EXTRACTED]
- [[train_12feat_tcn()]] - `calls` [EXTRACTED]

  #community/Multiscale*TCN*&\_Features
