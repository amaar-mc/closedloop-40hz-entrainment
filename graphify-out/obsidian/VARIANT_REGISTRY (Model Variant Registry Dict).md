---
source_file: "validation/experiments/tcn_variants.py"
type: "code"
community: "Community 60"
location: "VARIANT_REGISTRY"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_60
---

# VARIANT_REGISTRY (Model Variant Registry Dict)

## Connections
- [[DeepDilationTCN (Dilations 1,2,4,8,16,32, 127-step RF)]] - `references` [EXTRACTED]
- [[MultiTaskTCN (lambda_delta=0.3, lambda_consistency=0.1)]] - `references` [EXTRACTED]
- [[TransformerTCN (4-layer Causal Transformer Encoder, ~85K params)]] - `references` [EXTRACTED]
- [[WiderTCN (hidden=128, ~120K params)]] - `references` [EXTRACTED]
- [[build_variant()]] - `calls` [EXTRACTED]
- [[run_benchmark()]] - `references` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_60