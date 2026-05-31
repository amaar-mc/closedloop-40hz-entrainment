---
type: community
members: 56
---

# Archived Temporal PAC Predictor

**Members:** 56 nodes

## Members
- [[.__getitem__()_7]] - code - archive/temporal_legacy/train_temporal_long_windows.py
- [[.__init__()_23]] - code - archive/temporal_legacy/train_temporal_long_windows.py
- [[.__init__()_25]] - code - archive/temporal_legacy/temporal_model.py
- [[.__init__()_26]] - code - archive/temporal_legacy/temporal_model.py
- [[.__init__()_27]] - code - archive/temporal_legacy/temporal_model.py
- [[.__len__()_7]] - code - archive/temporal_legacy/train_temporal_long_windows.py
- [[.count_parameters()_6]] - code - archive/temporal_legacy/temporal_model.py
- [[.count_parameters_by_component()]] - code - archive/temporal_legacy/temporal_model.py
- [[.forward()_16]] - code - archive/temporal_legacy/temporal_model.py
- [[.forward()_17]] - code - archive/temporal_legacy/temporal_model.py
- [[.forward()_18]] - code - archive/temporal_legacy/temporal_model.py
- [[Args             batch Dictionary with keys                 'eeg']] - rationale - archive/temporal_legacy/temporal_model.py
- [[Args             lookback Number of windows to look back (5 windows = 20 seco]] - rationale - archive/temporal_legacy/train_temporal_long_windows.py
- [[Args             n_channels Number of EEG channels             n_samples Sa]] - rationale - archive/temporal_legacy/temporal_model.py
- [[Args             x (batch, n_channels, n_samples) single EEG window]] - rationale - archive/temporal_legacy/temporal_model.py
- [[Compute regression metrics in original (denormalized) PAC scale.      Returns]] - rationale - archive/temporal_legacy/train_temporal.py
- [[Count parameters per component.]] - rationale - archive/temporal_legacy/temporal_model.py
- [[Count total trainable parameters.]] - rationale - archive/temporal_legacy/temporal_model.py
- [[Create trainvaltest dataloaders with temporal split.      Args         dat]] - rationale - archive/temporal_legacy/train_temporal_long_windows.py
- [[Evaluate model and return metrics in original scale.]] - rationale - archive/temporal_legacy/train_temporal_long_windows.py
- [[Evaluate model on a data split.      Returns metrics in ORIGINAL PAC scale (de]] - rationale - archive/temporal_legacy/train_temporal.py
- [[Extension Predict PAC at multiple future horizons simultaneously.      Shares]] - rationale - archive/temporal_legacy/temporal_model.py
- [[Full training pipeline for temporal PAC prediction.]] - rationale - archive/temporal_legacy/train_temporal.py
- [[LSTM-based temporal predictor for future PAC values.      Takes a sequence of]] - rationale - archive/temporal_legacy/temporal_model.py
- [[Lightweight spatial encoder for individual EEG windows.      Reduces (7, 500)]] - rationale - archive/temporal_legacy/temporal_model.py
- [[LongWindowTemporalDataset]] - code - archive/temporal_legacy/train_temporal_long_windows.py
- [[MultiHorizonPredictor]] - code - archive/temporal_legacy/temporal_model.py
- [[MultiHorizonPredictor (Multi-Head LSTM)]] - code - archive/temporal_legacy/temporal_model.py
- [[Rationale LSTM for Model Predictive Control of 40Hz Entrainment]] - document - archive/temporal_legacy/__init__.py
- [[Returns dict mapping horizon → prediction.]] - rationale - archive/temporal_legacy/temporal_model.py
- [[SpatialEncoder]] - code - archive/temporal_legacy/temporal_model.py
- [[SpatialEncoder (CNN Window Encoder)]] - code - archive/temporal_legacy/temporal_model.py
- [[Temporal PAC Prediction Models  LSTM and GRU architectures for predicting futu]] - rationale - archive/temporal_legacy/temporal_model.py
- [[Temporal dataset for 8-second windows with 4-second hop.      With 4-second ho]] - rationale - archive/temporal_legacy/train_temporal_long_windows.py
- [[TemporalPACPredictor]] - code - archive/temporal_legacy/temporal_model.py
- [[TemporalPACPredictor (LSTMGRU Model)]] - code - archive/temporal_legacy/temporal_model.py
- [[Test the temporal prediction model.]] - rationale - archive/temporal_legacy/temporal_model.py
- [[Train for one epoch. Returns average loss.]] - rationale - archive/temporal_legacy/train_temporal.py
- [[Train models for multiple prediction horizons (1, 3, 5, 10 seconds)     to char]] - rationale - archive/temporal_legacy/train_temporal.py
- [[Train temporal PAC predictor using 8-second windows.  Expected improvement -]] - rationale - archive/temporal_legacy/train_temporal_long_windows.py
- [[Training Pipeline for Temporal PAC Prediction  Trains the LSTM temporal predic]] - rationale - archive/temporal_legacy/train_temporal.py
- [[compute_metrics()_1]] - code - archive/temporal_legacy/train_temporal.py
- [[create_dataloaders()]] - code - archive/temporal_legacy/train_temporal_long_windows.py
- [[create_temporal_features (Flat Feature Vector Builder)]] - code - archive/temporal_legacy/train_sklearn_temporal.py
- [[evaluate()_3]] - code - archive/temporal_legacy/train_temporal_long_windows.py
- [[evaluate()_4]] - code - archive/temporal_legacy/train_temporal.py
- [[main()_13]] - code - archive/temporal_legacy/train_temporal_long_windows.py
- [[run_multi_horizon_experiment()]] - code - archive/temporal_legacy/train_temporal.py
- [[temporal_model.py]] - code - archive/temporal_legacy/temporal_model.py
- [[test_temporal_model()]] - code - archive/temporal_legacy/temporal_model.py
- [[train_and_evaluate (Ridge + MLP Sklearn Baseline)]] - code - archive/temporal_legacy/train_sklearn_temporal.py
- [[train_epoch()_2]] - code - archive/temporal_legacy/train_temporal_long_windows.py
- [[train_one_epoch()_2]] - code - archive/temporal_legacy/train_temporal.py
- [[train_temporal.py]] - code - archive/temporal_legacy/train_temporal.py
- [[train_temporal_long_windows.py]] - code - archive/temporal_legacy/train_temporal_long_windows.py
- [[train_temporal_predictor()]] - code - archive/temporal_legacy/train_temporal.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Archived_Temporal_PAC_Predictor
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Multiscale TCN & Features]]

## Top bridge nodes
- [[LongWindowTemporalDataset]] - degree 8, connects to 1 community
- [[train_temporal.py]] - degree 8, connects to 1 community
- [[train_temporal_predictor()]] - degree 8, connects to 1 community