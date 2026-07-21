# Multiscale Temporal PAC Module

This module implements a new leakage-safe temporal forecasting pipeline:

- **Input**: sequence of multiscale features (spectral + PAC history + stimulation context)
- **Model**: lightweight **causal multiscale TCN**
- **Targets**:
  - `future PAC` at horizon `h`
  - `delta PAC` = `PAC[t+h] - PAC[t]`

## Files

- `build_multiscale_dataset.py`: build normalized train/val/test temporal sequences
- `multiscale_tcn.py`: model definition
- `train_multiscale_tcn.py`: training and evaluation
- `audit_multiscale_pipeline.py`: leakage/correctness audit
- `realtime_inference.py`: rolling closed-loop inference wrapper

## Quick Start

```bash
python temporal_multiscale/train_multiscale_tcn.py --rebuild-dataset --lookback 20 --horizon 1 --target-smooth-window 5 --run-name multiscale_tcn_lb20_hz1_ts5
python temporal_multiscale/audit_multiscale_pipeline.py --dataset-dir data/processed/multiscale_temporal
```

## Recommended Hyperparameters

- `lookback=20` (20 seconds)
- `horizon=5` (predict 5 seconds ahead)
- `hidden=64`, `dilations=1,2,4,8`
- `batch_size=128`, `epochs=80`

For denoised latent-state forecasting (recommended in this repo):

- `horizon=1`
- `target_smooth_window=5`

## Closed-Loop Notes

- Model is causal and suitable for 1 Hz decision loops.
- Keep feature extraction deterministic and bounded in latency.
- Use `realtime_inference.py` to integrate with controller logic.

## Important Metric Note

- `target_smooth_window=1` predicts raw PAC directly (hard, noisier target).
- `target_smooth_window>1` predicts a causal denoised PAC state (more stable control target).
- Compare models only when target definitions are the same.
- Training now enforces metadata consistency by default; if reusing a dataset dir with different args, rebuild or pass `--allow-metadata-mismatch`.
