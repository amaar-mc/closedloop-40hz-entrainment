---
source_file: "src/data_loader.py"
type: "code"
community: "Multiscale TCN & Features"
location: "L113"
tags:
  - community/Multiscale_TCN_&_Features
---

# BIDSDataProcessor

## Connections

- [[4-Channel Muse 2 Model Retraining Pipeline  Retrains the full EEGNet + TCN pipel]] - `uses` [INFERRED]
- [[Build causal temporal sequences for TCN training.]] - `uses` [INFERRED]
- [[Compute spectral features (37-dim) for each window in each split.]] - `uses` [INFERRED]
- [[EEGPreprocessor]] - `uses` [INFERRED]
- [[Full end-to-end pipeline preprocess → spectral cache → temporal dataset → train]] - `uses` [INFERRED]
- [[Generate a comparison report 4-channel vs 7-channel models.]] - `uses` [INFERRED]
- [[Load raw BIDS data, select F7F8T7T8, preprocess, window, compute PAC.]] - `uses` [INFERRED]
- [[PACComputer]] - `uses` [INFERRED]
- [[Processes BIDS-compliant EEG dataset into training windows.      Pipeline]] - `rationale_for` [EXTRACTED]
- [[Step 1 Preprocess raw BIDS data into trainvaltest splits.]] - `uses` [INFERRED]
- [[Step 2 Generate spectral feature caches for each split.]] - `uses` [INFERRED]
- [[Step 3 Build multiscale temporal dataset.]] - `uses` [INFERRED]
- [[Step 4 Train multiscale causal TCN.]] - `uses` [INFERRED]
- [[Step 5 Replay real data through controllers including TCN-based predictive.]] - `uses` [INFERRED]
- [[Step 6 Compute proper effect sizes and clinical interpretability.]] - `uses` [INFERRED]
- [[Train EEGNet on 4-channel windows for static PAC prediction.]] - `uses` [INFERRED]
- [[Train TCN on 4-channel multiscale temporal dataset.]] - `uses` [INFERRED]
- [[__init__()_150]] - `method` [EXTRACTED]
- [[_load_hdf5_set()]] - `method` [EXTRACTED]
- [[create_dataloaders()_1]] - `method` [EXTRACTED]
- [[create_splits()]] - `method` [EXTRACTED]
- [[data_loader.py]] - `contains` [EXTRACTED]
- [[extract_stimulus_windows()]] - `method` [EXTRACTED]
- [[get_subject_list()]] - `method` [EXTRACTED]
- [[load_raw_data()]] - `method` [EXTRACTED]
- [[main()_76]] - `calls` [EXTRACTED]
- [[process_dataset()]] - `method` [EXTRACTED]
- [[save_splits()]] - `method` [EXTRACTED]
- [[select_frontal_channels()]] - `method` [EXTRACTED]

  #community/Multiscale*TCN*&\_Features
