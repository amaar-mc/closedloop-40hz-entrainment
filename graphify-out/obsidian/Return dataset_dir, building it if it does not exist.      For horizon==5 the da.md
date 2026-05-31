---
source_file: "temporal_multiscale/run_comparison_study.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L79"
tags:
  - community/Multiscale_TCN_&_Features
---

# Return dataset_dir, building it if it does not exist.      For horizon==5 the da

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SequenceDataset]] - `uses` [INFERRED]
- [[SimpleLSTM]] - `uses` [INFERRED]
- [[SimpleTransformer]] - `uses` [INFERRED]
- [[_ensure_dataset()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale_TCN_&_Features