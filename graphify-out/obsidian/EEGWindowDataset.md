---
source_file: "src/data_loader.py"
type: "code"
community: "Core Data & PAC Pipeline"
location: "L50"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Core_Data_&_PAC_Pipeline
---

# EEGWindowDataset

## Connections
- [[Add Gaussian noise at specified SNR.          Args             window EEG w]] - `uses` [INFERRED]
- [[Applies data augmentation to EEG windows.      Augmentation strategies]] - `uses` [INFERRED]
- [[Apply random augmentations.          Args             window Input window]] - `uses` [INFERRED]
- [[DataAugmentor]] - `uses` [INFERRED]
- [[Dataset]] - `inherits` [EXTRACTED]
- [[EEGPreprocessor]] - `uses` [INFERRED]
- [[Full training loop with early stopping and checkpointing.          Args]] - `uses` [INFERRED]
- [[Handles model training, validation, and checkpointing.      Features]] - `uses` [INFERRED]
- [[Initialize trainer.          Args             model PyTorch model]] - `uses` [INFERRED]
- [[Load model checkpoint.]] - `uses` [INFERRED]
- [[Main entry point for training pipeline.]] - `uses` [INFERRED]
- [[ModelTrainer]] - `uses` [INFERRED]
- [[PACComputer]] - `uses` [INFERRED]
- [[PyTorch Dataset for EEG sliding windows with PAC labels.      Stores pre-compu]] - `rationale_for` [EXTRACTED]
- [[Randomly scale amplitude.          Args             window EEG window]] - `uses` [INFERRED]
- [[Randomly shift window in time along the last axis.          Args]] - `uses` [INFERRED]
- [[Save model checkpoint.]] - `uses` [INFERRED]
- [[Train for one epoch.          Args             train_loader Training DataLo]] - `uses` [INFERRED]
- [[Training Pipeline for EEGNet PAC Prediction Model  Implements model training w]] - `uses` [INFERRED]
- [[Validate model on validation set.          Args             val_loader Vali]] - `uses` [INFERRED]
- [[__getitem__()_18]] - `method` [EXTRACTED]
- [[__init__()_149]] - `method` [EXTRACTED]
- [[__len__()_18]] - `method` [EXTRACTED]
- [[create_dataloaders()_1]] - `calls` [EXTRACTED]
- [[data_loader.py]] - `contains` [EXTRACTED]
- [[get_session_id()]] - `method` [EXTRACTED]
- [[get_subject_id()]] - `method` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/Core_Data_&_PAC_Pipeline