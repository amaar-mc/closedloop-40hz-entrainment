---
source_file: "src/preprocessing.py"
type: "code"
community: "Core Data & PAC Pipeline"
location: "L30"
tags:
  - community/Core_Data_&_PAC_Pipeline
---

# EEGPreprocessor

## Connections
- [[BIDS Data Loader for Closed-Loop 40Hz Entrainment Research  Loads OpenNeuro ds]] - `uses` [INFERRED]
- [[BIDSDataProcessor]] - `uses` [INFERRED]
- [[Create PyTorch DataLoaders from splits.          Args             splits Di]] - `uses` [INFERRED]
- [[Create trainvaltest splits by subject (leave-subject-out).          Ensures]] - `uses` [INFERRED]
- [[EEGWindowDataset]] - `uses` [INFERRED]
- [[Extract 2-second sliding windows segmented by stimulusrest events,         wit]] - `uses` [INFERRED]
- [[Get list of subjects in BIDS dataset.          Returns             subjects]] - `uses` [INFERRED]
- [[Get session ID for a sample.]] - `uses` [INFERRED]
- [[Get single window and its PAC label.          Args             idx Sample i]] - `uses` [INFERRED]
- [[Get subject ID for a sample.]] - `uses` [INFERRED]
- [[Implements EEG signal preprocessing pipeline.      Pipeline stages         1]] - `rationale_for` [EXTRACTED]
- [[Initialize BIDS data processor.          Args             bids_root Path to]] - `uses` [INFERRED]
- [[Initialize EEG window dataset.          Args             windows EEG window]] - `uses` [INFERRED]
- [[Load EEGLAB .set file saved in MATLAB v7.3 (HDF5) format.          In ds005048]] - `uses` [INFERRED]
- [[Load raw EEG data for a subject.          Handles MATLAB v7.3 (HDF5) .set file]] - `uses` [INFERRED]
- [[Main entry point for data loading pipeline.]] - `uses` [INFERRED]
- [[Process entire BIDS dataset.          Pipeline per subject             1. Lo]] - `uses` [INFERRED]
- [[Processes BIDS-compliant EEG dataset into training windows.      Pipeline]] - `uses` [INFERRED]
- [[PyTorch Dataset for EEG sliding windows with PAC labels.      Stores pre-compu]] - `uses` [INFERRED]
- [[Return number of samples.]] - `uses` [INFERRED]
- [[Save trainvaltest splits to npz files.          Args             splits D]] - `uses` [INFERRED]
- [[Select 7 frontal channels from full EEG montage.          Args             r]] - `uses` [INFERRED]
- [[__init__()_151]] - `method` [EXTRACTED]
- [[_compute_filter_coefficients()]] - `method` [EXTRACTED]
- [[artifact_rejection()]] - `method` [EXTRACTED]
- [[bandpass_filter()_1]] - `method` [EXTRACTED]
- [[common_average_reference()]] - `method` [EXTRACTED]
- [[detect_bad_channels()]] - `method` [EXTRACTED]
- [[estimate_snr()]] - `method` [EXTRACTED]
- [[notch_filter()]] - `method` [EXTRACTED]
- [[plot_filter_response()]] - `method` [EXTRACTED]
- [[preprocess()]] - `method` [EXTRACTED]
- [[preprocessing.py]] - `contains` [EXTRACTED]
- [[test_preprocessing()]] - `calls` [EXTRACTED]

  #community/Core_Data_&_PAC_Pipeline