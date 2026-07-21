---
source_file: "validation/experiments/tcn_variants.py"
type: "code"
community: "Community 60"
location: "class TransformerTCN"
tags:
  - community/Community_60
---

# TransformerTCN (4-layer Causal Transformer Encoder, ~85K params)

## Connections

- [[AttentionPool1D (Temporal Attention Pooling)]] - `calls` [EXTRACTED]
- [[CausalSinusoidalPE (Sinusoidal Positional Encoding for Transformer)]] - `calls` [EXTRACTED]
- [[TransformerConfig Dataclass (Transformer Variant Configuration)]] - `shares_data_with` [EXTRACTED]
- [[TransformerTCN Hypothesis (Self-Attention vs Fixed Dilation)]] - `rationale_for` [EXTRACTED]
- [[VARIANT_REGISTRY (Model Variant Registry Dict)]] - `references` [EXTRACTED]

  #community/Community_60
