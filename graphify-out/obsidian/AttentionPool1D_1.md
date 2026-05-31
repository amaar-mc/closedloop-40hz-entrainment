---
source_file: "temporal_multiscale/multiscale_tcn.py"
type: "code"
community: "Multiscale TCN & Features"
location: "L61"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Multiscale_TCN_&_Features
---

# AttentionPool1D

## Connections
- [[.__init__()_60]] - `method` [EXTRACTED]
- [[.__init__()_61]] - `calls` [EXTRACTED]
- [[.forward()_30]] - `method` [EXTRACTED]
- [[AblationVariant]] - `uses` [INFERRED]
- [[Attention pooling over time axis._1]] - `rationale_for` [EXTRACTED]
- [[AttentionWeightCapture]] - `uses` [INFERRED]
- [[CausalDSConvBlock with GroupNorm replaced by Identity (ablation).]] - `uses` [INFERRED]
- [[CausalDSConvBlockNoNorm]] - `uses` [INFERRED]
- [[Compute R-squared, returning 0.0 when variance is near zero.]] - `uses` [INFERRED]
- [[Compute prediction performance conditioned on stimulation state.      Splits t]] - `uses` [INFERRED]
- [[Compute standard regression metrics.]] - `uses` [INFERRED]
- [[Concatenate all captured weights into (N, T) array.]] - `uses` [INFERRED]
- [[Denormalize z-scored predictions._1]] - `uses` [INFERRED]
- [[Find the index of the stim_state feature.      Args         feature_names L]] - `uses` [INFERRED]
- [[Find the index of the time_since_switch feature.      Args         feature_n]] - `uses` [INFERRED]
- [[Forward hook that computes and stores attention weights.          The Attentio]] - `uses` [INFERRED]
- [[Hook-based capture of AttentionPool1D attention weights.      Registers a forw]] - `uses` [INFERRED]
- [[InterpretabilityDataset]] - `uses` [INFERRED]
- [[Load the trained TCN checkpoint.      Args         checkpoint_path Path to]] - `uses` [INFERRED]
- [[Loads multiscale temporal dataset with metadata for interpretability.      Ext]] - `uses` [INFERRED]
- [[Map feature group names to column indices using prefix matching.      Args]] - `uses` [INFERRED]
- [[MultiscaleCausalTCN using CausalDSConvBlockNoNorm in all blocks.]] - `uses` [INFERRED]
- [[MultiscaleCausalTCNNoNorm]] - `uses` [INFERRED]
- [[Parse command-line arguments._2]] - `uses` [INFERRED]
- [[Print attention weight analysis summary.]] - `uses` [INFERRED]
- [[Print feature group ablation summary.]] - `uses` [INFERRED]
- [[Print stimulation-conditional performance summary.]] - `uses` [INFERRED]
- [[Recursively convert numpy types for JSON serialization.]] - `uses` [INFERRED]
- [[Remove the forward hook.]] - `uses` [INFERRED]
- [[Run all interpretability analyses.]] - `uses` [INFERRED]
- [[Run the test set through the model and capture attention weights.      Args]] - `uses` [INFERRED]
- [[TCN Interpretability Analysis for Multiscale Causal TCN.  Performs three inter]] - `uses` [INFERRED]
- [[TCN ablation study quantify contribution of each architectural component.  Trai]] - `uses` [INFERRED]
- [[Train a single variant and return its result dict.]] - `uses` [INFERRED]
- [[Zero-ablation experiment zero out each feature group and measure R2 drop.]] - `uses` [INFERRED]
- [[multiscale_tcn.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/Multiscale_TCN_&_Features