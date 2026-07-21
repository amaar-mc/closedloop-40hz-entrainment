# Temporal PAC Forecasting Deep Dive (Feb 17, 2026)

## 1) What the dataset papers actually did

### Dataset and associated publication context

- OpenNeuro dataset: **ds005048 v1.0.1** (40 Hz auditory entrainment EEG).  
  Link: https://openneuro.org/datasets/ds005048/versions/1.0.1
- The dataset metadata (`dataset_description.json`) points to:
  - Scientific Reports (2024): https://doi.org/10.1038/s41598-024-63727-z
  - Original preprint link: https://doi.org/10.1101/2021.09.30.462389
- Dataset description paper (Data in Brief, 2022):  
  https://pubmed.ncbi.nlm.nih.gov/35782724/

### Key finding for our question (prediction + R²)

- These associated papers are primarily about **entrainment characterization**, **connectivity**, and **cross-frequency coupling**, not a direct PAC-future regression benchmark in the style `predict PAC[t+h]` with reported `R²`.
- In other words: there is **no canonical “paper baseline R²=0.8 for future PAC forecasting”** tied to ds005048 in the core associated papers.
- Scientific Reports does report strong relationships (for example entrainment-related correlations), and uses time-resolved analysis (including short windows with overlap), but not a direct held-out future PAC forecasting R² benchmark.

## 2) Why our current temporal R² is low

Empirically in this repo:

- Current-window Ridge is strongest practical baseline around `R² ~ 0.287`.
- Pure temporal prediction from short-window PAC history has underperformed.

Likely causes:

1. **Target noise**: short-window PAC is noisy.
2. **Missing exogenous driver**: stimulation state/history strongly influences dynamics.
3. **Cross-subject heterogeneity**: dynamics vary by subject.
4. **Model/feature mismatch**: heavy models overfit; simple models miss long-range context.

## 3) Candidate architecture options

### A. Heavy Transformer on raw EEG sequences

- Pros: expressive.
- Cons: high overfitting risk on this dataset; expensive inference.
- Verdict: not ideal for closed-loop 1 Hz decisions.

### B. LSTM/GRU on PAC + spectral history

- Pros: simple temporal modeling.
- Cons: struggles when signal is noisy and exogenous context is missing/weak.
- Verdict: better than static, but already tested with limited gains.

### C. Classical linear model with engineered temporal features

- Pros: very fast and robust.
- Cons: limited nonlinear capacity for conditional temporal effects.
- Verdict: strong fallback baseline.

### D. **Chosen**: Causal multiscale TCN + stimulation context + dual targets

- Pros:
  - Causal, low-latency inference.
  - Dilated convolutions capture short/medium temporal dependencies efficiently.
  - Exogenous stimulation-context features add causal signal.
  - Dual-task prediction (`future PAC` + `delta PAC`) improves training signal.
- Cons: still bounded by data quality.
- Verdict: best practical tradeoff for this repo’s closed-loop constraints.

## 4) Noise reduction and data strategy

1. **Multiscale PAC history features** (causal MA 2/4/8/16 + derivatives).
2. **Stim context features from BIDS events**:
   - state (stim/rest), time since switch, recent stim fraction, cycle phase.
3. **Dual target training**:
   - future PAC and delta PAC simultaneously.
4. **Train-only normalization** for all scalers.
5. **Subject-level splits preserved** to avoid leakage.

Window strategy:

- Keep inference cadence at 1 Hz (operationally useful).
- Use multiscale features instead of one fixed long window only.
- Optionally sweep `(lookback, horizon)` over `{10,20,30} x {3,5,8}`.

## 5) Implemented solution in this repo

New module: `temporal_multiscale/`

- `build_multiscale_dataset.py`
  - Builds leakage-safe sequence datasets from existing splits.
  - Adds event-driven stim context from `events.tsv`.
  - Saves normalized train/val/test artifacts + scaler stats.
- `multiscale_tcn.py`
  - Lightweight causal depthwise-separable TCN with dilations.
  - Attention pooling + dual heads (`future`, `delta`).
- `train_multiscale_tcn.py`
  - Trains/evaluates the new model.
  - Uses future + delta + consistency loss.
- `audit_multiscale_pipeline.py`
  - Validates split integrity, temporal causality, finite values, normalization behavior.
- `realtime_inference.py`
  - Rolling realtime wrapper for closed-loop use.

## 6) Scientific/leakage safeguards explicitly enforced

- No subject overlap across splits.
- Sequence target index is strictly after sequence end index.
- Causal feature construction only uses current/past samples.
- All normalization parameters are fit on train split only.
- Audit script verifies these constraints on produced artifacts.

## 7) Recommended next experiment order

1. Run baseline chosen config (`lookback=20`, `horizon=5`).
2. Run small grid sweep on lookback/horizon.
3. Compare against existing Ridge baseline and prior temporal scripts.
4. Keep architecture only if it beats current-window baseline or provides superior control utility (delta sign accuracy, stable latency).

## 8) Initial implementation results (this repo run)

Quick sweep with the new pipeline (`lookback=20`, hidden=64):

- `horizon=1`: test future `R²=0.0699`, corr `0.2730`
- `horizon=2`: test future `R²=0.0645`, corr `0.2671`
- `horizon=5`: test future `R²=0.0533`, corr `0.2500`

Interpretation:

- Shorter horizons are more predictable (expected in noisy PAC forecasting).
- This is still below desired levels for strong proactive MPC.
- The architecture is operationally valid and fast, but data/target noise remains the main bottleneck.

Chosen practical default:

- **Use this multiscale causal TCN with `horizon=1` as the near-term real-time predictor**, and retain the sweep framework for ongoing iteration.

## 9) Refined strategy: latent-state target denoising

A key observation from this repository:

- Raw 1-step PAC prediction is weak.
- Causally smoothed PAC state is highly predictable.

Implemented refinement:

- Add `target_smooth_window` to dataset builder.
- `target_smooth_window=5` defines a causal denoised target:
  - each target uses only current/past PAC samples at that time index.

Result for `lookback=20, horizon=1, target_smooth_window=5`:

- test future `R²=0.7503`, corr `0.8731`
- test delta `R²=0.2335`, corr `0.4901`

Practical interpretation:

- For closed-loop music timing, forecasting a denoised latent coupling state is more robust than chasing raw instantaneous PAC noise.
