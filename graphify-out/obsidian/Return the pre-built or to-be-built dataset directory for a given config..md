---
source_file: "temporal_multiscale/run_comparison_study.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L66"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Return the pre-built or to-be-built dataset directory for a given config.

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[SequenceDataset]] - `uses` [INFERRED]
- [[SimpleLSTM]] - `uses` [INFERRED]
- [[SimpleTransformer]] - `uses` [INFERRED]
- [[_dataset_dir()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features