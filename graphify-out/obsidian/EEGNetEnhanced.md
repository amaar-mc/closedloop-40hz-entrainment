---
source_file: "validation/eegnet_enhanced.py"
type: "code"
community: "Models, Streaming & Apps"
location: "L36"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Models,_Streaming_&_Apps
---

# EEGNetEnhanced

## Connections
- [[Compute aggregate statistics across seeds for each metric.      Computes mean,]] - `uses` [INFERRED]
- [[Create a DataLoader from numpy arrays.      Args         windows EEG window]] - `uses` [INFERRED]
- [[Create trainvaltest splits by subject with a given random seed.      Ensures]] - `uses` [INFERRED]
- [[EEGNet_1]] - `uses` [INFERRED]
- [[Enhanced EEGNet with increased capacity (~35K parameters, ~24x original).]] - `rationale_for` [EXTRACTED]
- [[Instantiate a model by name and move to device.      Args         model_name]] - `uses` [INFERRED]
- [[Load and concatenate trainvaltest npz splits into a single pool.      The or]] - `uses` [INFERRED]
- [[Multi-Seed Training for Robustness Evaluation  Trains EEGNet variants (origina]] - `uses` [INFERRED]
- [[Run multi-seed training experiment.]] - `uses` [INFERRED]
- [[Train a model for one seed and evaluate on the test split.      Uses Huber los]] - `uses` [INFERRED]
- [[__init__()_123]] - `method` [EXTRACTED]
- [[eegnet_enhanced.py]] - `contains` [EXTRACTED]
- [[forward()_37]] - `method` [EXTRACTED]
- [[get_feature_maps()]] - `method` [EXTRACTED]
- [[test_all()]] - `calls` [EXTRACTED]
- [[test_eegnet_enhanced()]] - `calls` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/Models,_Streaming_&_Apps