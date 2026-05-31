---
source_file: "src/pac_computation.py"
type: "code"
community: "Core Data & PAC Pipeline"
location: "L29"
tags:
  - community/Core_Data_&_PAC_Pipeline
---

# PACComputer

## Connections
- [[BIDS Data Loader for Closed-Loop 40Hz Entrainment Research  Loads OpenNeuro ds]] - `uses` [INFERRED]
- [[BIDSDataProcessor]] - `uses` [INFERRED]
- [[Computes Phase-Amplitude Coupling using Modulation Index method.      The Modu]] - `rationale_for` [EXTRACTED]
- [[Create PyTorch DataLoaders from splits.          Args             splits Di]] - `uses` [INFERRED]
- [[Create trainvaltest splits by subject (leave-subject-out).          Ensures]] - `uses` [INFERRED]
- [[EEGWindowDataset]] - `uses` [INFERRED]
- [[Extract 2-second sliding windows segmented by stimulusrest events,         wit]] - `uses` [INFERRED]
- [[Get list of subjects in BIDS dataset.          Returns             subjects]] - `uses` [INFERRED]
- [[Get session ID for a sample.]] - `uses` [INFERRED]
- [[Get single window and its PAC label.          Args             idx Sample i]] - `uses` [INFERRED]
- [[Get subject ID for a sample.]] - `uses` [INFERRED]
- [[Initialize BIDS data processor.          Args             bids_root Path to]] - `uses` [INFERRED]
- [[Initialize EEG window dataset.          Args             windows EEG window]] - `uses` [INFERRED]
- [[Load EEGLAB .set file saved in MATLAB v7.3 (HDF5) format.          In ds005048]] - `uses` [INFERRED]
- [[Load raw EEG data for a subject.          Handles MATLAB v7.3 (HDF5) .set file]] - `uses` [INFERRED]
- [[Main entry point for data loading pipeline.]] - `uses` [INFERRED]
- [[NeuroCare 40Hz -- Live Mission Control v5  Uses st.empty() placeholders for flic]] - `uses` [INFERRED]
- [[Process entire BIDS dataset.          Pipeline per subject             1. Lo]] - `uses` [INFERRED]
- [[Processes BIDS-compliant EEG dataset into training windows.      Pipeline]] - `uses` [INFERRED]
- [[PyTorch Dataset for EEG sliding windows with PAC labels.      Stores pre-compu]] - `uses` [INFERRED]
- [[Recompute PAC per 2-second window instead of per epoch.  The original pipeline c]] - `uses` [INFERRED]
- [[Recompute PAC per window for one split file.      Args         input_path Path]] - `uses` [INFERRED]
- [[Return number of samples.]] - `uses` [INFERRED]
- [[Save trainvaltest splits to npz files.          Args             splits D]] - `uses` [INFERRED]
- [[Select 7 frontal channels from full EEG montage.          Args             r]] - `uses` [INFERRED]
- [[__init__()_145]] - `method` [EXTRACTED]
- [[bandpass_filter()]] - `method` [EXTRACTED]
- [[compute_modulation_index()]] - `method` [EXTRACTED]
- [[compute_pac()]] - `method` [EXTRACTED]
- [[compute_pac_average()]] - `method` [EXTRACTED]
- [[compute_pac_multichannel()]] - `method` [EXTRACTED]
- [[extract_phase_amplitude()_1]] - `method` [EXTRACTED]
- [[pac_computation.py]] - `contains` [EXTRACTED]
- [[validate_pac_computation()]] - `calls` [EXTRACTED]

  #community/Core_Data_&_PAC_Pipeline