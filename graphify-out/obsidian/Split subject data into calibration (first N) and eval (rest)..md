---
source_file: "temporal_multiscale/per_subject_adaptation.py"
type: "rationale"
community: "Multiscale TCN & Features"
location: "L83"
tags:
  - community/Multiscale_TCN_&_Features
---

# Split subject data into calibration (first N) and eval (rest).

## Connections

- [[ModelConfig]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN]] - `uses` [INFERRED]
- [[split_calibration()]] - `rationale_for` [EXTRACTED]

  #community/Multiscale*TCN*&\_Features
