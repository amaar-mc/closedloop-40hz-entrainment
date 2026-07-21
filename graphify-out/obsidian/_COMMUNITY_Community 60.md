---
type: community
members: 18
---

# Community 60

**Members:** 18 nodes

## Members

- [[AttentionPool1D (Temporal Attention Pooling)]] - code - validation/experiments/tcn_variants.py
- [[AttentionWeightCapture (Hook-Based Attention Weight Capture)]] - code - validation/experiments/tcn_interpretability.py
- [[CausalDSConvBlock (Residual Depthwise-Separable Causal Block)]] - code - validation/experiments/tcn_variants.py
- [[CausalSinusoidalPE (Sinusoidal Positional Encoding for Transformer)]] - code - validation/experiments/tcn_variants.py
- [[Data Limitation as Performance Ceiling Rationale]] - document - validation/experiments/EXPERIMENT_DESIGN.md
- [[DeepDilationTCN (Dilations 1,2,4,8,16,32, 127-step RF)]] - code - validation/experiments/tcn_variants.py
- [[DeepDilationTCN Hypothesis (Extended Receptive Field)]] - document - validation/experiments/EXPERIMENT_DESIGN.md
- [[ModelConfig Dataclass (TCN Variant Configuration)]] - code - validation/experiments/tcn_variants.py
- [[MultiTaskTCN (lambda_delta=0.3, lambda_consistency=0.1)]] - code - validation/experiments/tcn_variants.py
- [[MultiTaskTCN Hypothesis (Delta Head Regularization)]] - document - validation/experiments/EXPERIMENT_DESIGN.md
- [[Synthetic Benchmark Results (All Variants PASS)]] - document - validation/experiments/EXPERIMENT_DESIGN.md
- [[TCN Architecture Experiment Design]] - document - validation/experiments/EXPERIMENT_DESIGN.md
- [[TransformerConfig Dataclass (Transformer Variant Configuration)]] - code - validation/experiments/tcn_variants.py
- [[TransformerTCN (4-layer Causal Transformer Encoder, ~85K params)]] - code - validation/experiments/tcn_variants.py
- [[TransformerTCN Hypothesis (Self-Attention vs Fixed Dilation)]] - document - validation/experiments/EXPERIMENT_DESIGN.md
- [[VARIANT_REGISTRY (Model Variant Registry Dict)]] - code - validation/experiments/tcn_variants.py
- [[WiderTCN (hidden=128, ~120K params)]] - code - validation/experiments/tcn_variants.py
- [[WiderTCN Hypothesis (64-dim Bottleneck Limit)]] - document - validation/experiments/EXPERIMENT_DESIGN.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_60
SORT file.name ASC
```

## Connections to other communities

- 4 edges to [[_COMMUNITY_Multiscale TCN & Features]]

## Top bridge nodes

- [[VARIANT_REGISTRY (Model Variant Registry Dict)]] - degree 6, connects to 1 community
- [[MultiTaskTCN (lambda_delta=0.3, lambda_consistency=0.1)]] - degree 4, connects to 1 community
- [[AttentionWeightCapture (Hook-Based Attention Weight Capture)]] - degree 2, connects to 1 community
