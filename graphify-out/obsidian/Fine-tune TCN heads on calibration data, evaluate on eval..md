---
source_file: "temporal_multiscale/per_subject_adaptation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L165"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# Fine-tune TCN heads on calibration data, evaluate on eval.

## Connections
- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[tcn_finetune()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Multiscale_TCN_&_Features