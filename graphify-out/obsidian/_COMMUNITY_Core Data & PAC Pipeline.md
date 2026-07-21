---
type: community
members: 119
---

# Core Data & PAC Pipeline

**Members:** 119 nodes

## Members

- [[Add Gaussian noise at specified SNR.          Args             window EEG w]] - rationale - src/training.py
- [[Applies data augmentation to EEG windows.      Augmentation strategies]] - rationale - src/training.py
- [[Apply Butterworth bandpass filter to signal.          Args             signa]] - rationale - src/pac_computation.py
- [[Apply bandpass filter (0.5-80 Hz, 4th-order Butterworth).          Uses zero-p]] - rationale - src/preprocessing.py
- [[Apply common average reference (CAR).          Subtracts the mean of all chann]] - rationale - src/preprocessing.py
- [[Apply notch filter to remove powerline interference.          Removes 50 Hz (E]] - rationale - src/preprocessing.py
- [[Apply random augmentations.          Args             window Input window]] - rationale - src/training.py
- [[BIDS Data Loader for Closed-Loop 40Hz Entrainment Research  Loads OpenNeuro ds]] - rationale - src/data_loader.py
- [[Compute Modulation Index from phase and amplitude time series.          MI mea]] - rationale - src/pac_computation.py
- [[Compute PAC for a single-channel EEG signal.          This is the main user-fa]] - rationale - src/pac_computation.py
- [[Compute PAC for multi-channel EEG.          Args             signals Multi-]] - rationale - src/pac_computation.py
- [[Compute PAC using Tensorpac library (for validationcomparison).      Args]] - rationale - src/pac_computation.py
- [[Compute average PAC across all channels.          Args             signals]] - rationale - src/pac_computation.py
- [[Computes Phase-Amplitude Coupling using Modulation Index method.      The Modu]] - rationale - src/pac_computation.py
- [[Create PyTorch DataLoaders from splits.          Args             splits Di]] - rationale - src/data_loader.py
- [[Create trainvaltest splits by subject (leave-subject-out).          Ensures]] - rationale - src/data_loader.py
- [[DataAugmentor]] - code - src/training.py
- [[Detect and mark artifact samples using amplitude thresholding.          Marks]] - rationale - src/preprocessing.py
- [[Detect badnoisy channels using standard deviation criterion.          Channel]] - rationale - src/preprocessing.py
- [[EEG Preprocessing Pipeline for Closed-Loop 40Hz Entrainment  Implements signal]] - rationale - src/preprocessing.py
- [[EEGPreprocessor]] - code - src/preprocessing.py
- [[EEGWindowDataset]] - code - src/data_loader.py
- [[Estimate signal-to-noise ratio.          Uses gamma band (38-42 Hz) as signal]] - rationale - src/preprocessing.py
- [[Extract 2-second sliding windows segmented by stimulusrest events,         wit]] - rationale - src/data_loader.py
- [[Extract phase from low-frequency and amplitude from high-frequency.          A]] - rationale - src/pac_computation.py
- [[Full preprocessing pipeline.          Pipeline             1. Bandpass filte]] - rationale - src/preprocessing.py
- [[Full training loop with early stopping and checkpointing.          Args]] - rationale - src/training.py
- [[Get list of subjects in BIDS dataset.          Returns             subjects]] - rationale - src/data_loader.py
- [[Get session ID for a sample.]] - rationale - src/data_loader.py
- [[Get single window and its PAC label.          Args             idx Sample i]] - rationale - src/data_loader.py
- [[Get subject ID for a sample.]] - rationale - src/data_loader.py
- [[Handles model training, validation, and checkpointing.      Features]] - rationale - src/training.py
- [[Implements EEG signal preprocessing pipeline.      Pipeline stages         1]] - rationale - src/preprocessing.py
- [[Initialize BIDS data processor.          Args             bids_root Path to]] - rationale - src/data_loader.py
- [[Initialize EEG preprocessor.          Args             fs Sampling frequenc]] - rationale - src/preprocessing.py
- [[Initialize EEG window dataset.          Args             windows EEG window]] - rationale - src/data_loader.py
- [[Initialize PAC computer.          Args             theta_band (low, high) f]] - rationale - src/pac_computation.py
- [[Initialize augmentor.          Args             fs Sampling frequency (Hz)]] - rationale - src/training.py
- [[Initialize trainer.          Args             model PyTorch model]] - rationale - src/training.py
- [[Load EEGLAB .set file saved in MATLAB v7.3 (HDF5) format.          In ds005048]] - rationale - src/data_loader.py
- [[Load model checkpoint.]] - rationale - src/training.py
- [[Load raw EEG data for a subject.          Handles MATLAB v7.3 (HDF5) .set file]] - rationale - src/data_loader.py
- [[Main entry point for data loading pipeline.]] - rationale - src/data_loader.py
- [[Main entry point for training pipeline.]] - rationale - src/training.py
- [[ModelTrainer]] - code - src/training.py
- [[PACComputer]] - code - src/pac_computation.py
- [[Phase-Amplitude Coupling (PAC) Computation Module  Implements Modulation Index]] - rationale - src/pac_computation.py
- [[Plot frequency response of bandpass and notch filters.          Args]] - rationale - src/preprocessing.py
- [[Precompute filter coefficients for efficiency.]] - rationale - src/preprocessing.py
- [[Process entire BIDS dataset.          Pipeline per subject             1. Lo]] - rationale - src/data_loader.py
- [[PyTorch Dataset for EEG sliding windows with PAC labels.      Stores pre-compu]] - rationale - src/data_loader.py
- [[Randomly scale amplitude.          Args             window EEG window]] - rationale - src/training.py
- [[Randomly shift window in time along the last axis.          Args]] - rationale - src/training.py
- [[Recompute PAC per 2-second window instead of per epoch.  The original pipeline c]] - rationale - archive/perwindow_pac/recompute_pac.py
- [[Recompute PAC per window for one split file.      Args         input_path Path]] - rationale - archive/perwindow_pac/recompute_pac.py
- [[Return number of samples.]] - rationale - src/data_loader.py
- [[Save model checkpoint.]] - rationale - src/training.py
- [[Save trainvaltest splits to npz files.          Args             splits D]] - rationale - src/data_loader.py
- [[Select 7 frontal channels from full EEG montage.          Args             r]] - rationale - src/data_loader.py
- [[Test preprocessing pipeline with synthetic signal.]] - rationale - src/preprocessing.py
- [[Train for one epoch.          Args             train_loader Training DataLo]] - rationale - src/training.py
- [[Training Pipeline for EEGNet PAC Prediction Model  Implements model training w]] - rationale - src/training.py
- [[Validate PAC computation using synthetic signals.      Creates three test case]] - rationale - src/pac_computation.py
- [[Validate model on validation set.          Args             val_loader Vali]] - rationale - src/training.py
- [[__getitem__()_18]] - code - src/data_loader.py
- [[__init__()_145]] - code - src/pac_computation.py
- [[__init__()_149]] - code - src/data_loader.py
- [[__init__()_150]] - code - src/data_loader.py
- [[__init__()_151]] - code - src/preprocessing.py
- [[__init__()_156]] - code - src/training.py
- [[__init__()_157]] - code - src/training.py
- [[__len__()_18]] - code - src/data_loader.py
- [[_compute_filter_coefficients()]] - code - src/preprocessing.py
- [[_load_hdf5_set()]] - code - src/data_loader.py
- [[_save_checkpoint()]] - code - src/training.py
- [[add_gaussian_noise()]] - code - src/training.py
- [[amplitude_scaling()]] - code - src/training.py
- [[artifact_rejection()]] - code - src/preprocessing.py
- [[augment()]] - code - src/training.py
- [[bandpass_filter()]] - code - src/pac_computation.py
- [[bandpass_filter()_1]] - code - src/preprocessing.py
- [[common_average_reference()]] - code - src/preprocessing.py
- [[compute_modulation_index()]] - code - src/pac_computation.py
- [[compute_pac()]] - code - src/pac_computation.py
- [[compute_pac_average()]] - code - src/pac_computation.py
- [[compute_pac_multichannel()]] - code - src/pac_computation.py
- [[compute_pac_tensorpac()]] - code - src/pac_computation.py
- [[create_dataloaders()_1]] - code - src/data_loader.py
- [[create_splits()]] - code - src/data_loader.py
- [[data_loader.py]] - code - src/data_loader.py
- [[detect_bad_channels()]] - code - src/preprocessing.py
- [[estimate_snr()]] - code - src/preprocessing.py
- [[extract_phase_amplitude()_1]] - code - src/pac_computation.py
- [[extract_stimulus_windows()]] - code - src/data_loader.py
- [[get_session_id()]] - code - src/data_loader.py
- [[get_subject_id()]] - code - src/data_loader.py
- [[get_subject_list()]] - code - src/data_loader.py
- [[load_checkpoint()]] - code - src/training.py
- [[load_raw_data()]] - code - src/data_loader.py
- [[main()_18]] - code - archive/perwindow_pac/recompute_pac.py
- [[main()_76]] - code - src/data_loader.py
- [[main()_77]] - code - src/training.py
- [[notch_filter()]] - code - src/preprocessing.py
- [[pac_computation.py]] - code - src/pac_computation.py
- [[plot_filter_response()]] - code - src/preprocessing.py
- [[preprocess()]] - code - src/preprocessing.py
- [[preprocessing.py]] - code - src/preprocessing.py
- [[process_dataset()]] - code - src/data_loader.py
- [[recompute_pac.py]] - code - archive/perwindow_pac/recompute_pac.py
- [[recompute_pac_for_split()]] - code - archive/perwindow_pac/recompute_pac.py
- [[save_splits()]] - code - src/data_loader.py
- [[select_frontal_channels()]] - code - src/data_loader.py
- [[test_preprocessing()]] - code - src/preprocessing.py
- [[time_shift()]] - code - src/training.py
- [[train()]] - code - src/training.py
- [[train_epoch()_4]] - code - src/training.py
- [[training.py]] - code - src/training.py
- [[validate()_1]] - code - src/training.py
- [[validate_pac_computation()]] - code - src/pac_computation.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Core_Data_&_PAC_Pipeline
SORT file.name ASC
```

## Connections to other communities

- 17 edges to [[_COMMUNITY_Multiscale TCN & Features]]
- 17 edges to [[_COMMUNITY_Models, Streaming & Apps]]
- 1 edge to [[_COMMUNITY_Community 32]]
- 1 edge to [[_COMMUNITY_Community 35]]

## Top bridge nodes

- [[PACComputer]] - degree 34, connects to 2 communities
- [[training.py]] - degree 6, connects to 2 communities
- [[EEGPreprocessor]] - degree 34, connects to 1 community
- [[EEGWindowDataset]] - degree 27, connects to 1 community
- [[ModelTrainer]] - degree 11, connects to 1 community
