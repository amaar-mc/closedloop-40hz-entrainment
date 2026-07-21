# Temporal Multiscale Pipeline Audit Report (Feb 17, 2026)

## Scope

This report audits newly added files under `temporal_multiscale/` for:

- data leakage risks,
- temporal causality correctness,
- closed-loop feasibility,
- scientific coherence with the target task (future PAC / delta PAC forecasting).

## File-by-file review

## `temporal_multiscale/build_multiscale_dataset.py`

- Uses existing subject-level splits (`train/val/test_data.npz`), preserving no-subject-overlap policy.
- Builds sequences with strict causality:
  - input window: `[t-lookback+1, ..., t]`
  - target index: `t + horizon`
- Creates only causal derived features (moving averages and differences from current/past PAC).
- Adds stimulation context from BIDS `events.tsv` (`value=1/2`) without future peeking.
- Fits normalization on train split only, then applies to val/test.

## `temporal_multiscale/multiscale_tcn.py`

- Causal temporal convolutions with left padding only.
- No bidirectional layers, no future-context attention.
- Lightweight architecture for real-time deployment.

## `temporal_multiscale/train_multiscale_tcn.py`

- Uses train/val/test loaders without split mixing.
- Early stopping on validation metric.
- Saves run-scoped artifacts (`run_name`) to avoid accidental overwrite ambiguity.
- Reports both future PAC and delta PAC metrics.

## `temporal_multiscale/realtime_inference.py`

- Maintains rolling history buffers.
- Produces predictions only after sufficient lookback is accumulated.
- No access to future samples by construction.

## `temporal_multiscale/audit_multiscale_pipeline.py`

- Programmatic checks:
  - subject split overlap,
  - index causality (`target_idx > end_idx`),
  - finite values,
  - normalization sanity.

## `temporal_multiscale/sweep_multiscale_configs.py`

- Orchestrates controlled sweeps over lookback/horizon.
- Aggregates comparable summary metrics across runs.

## Executed audit outcomes

Command run:

- `python temporal_multiscale/audit_multiscale_pipeline.py --dataset-dir data/processed/multiscale_temporal_lb20_hz1_v2`

Result:

- **PASS** on all checks, including no subject overlap and temporal causality.

## Closed-loop runtime feasibility

Measured inference latency for the trained model (`best_multiscale_tcn_lb20_hz1_v2.pth`):

- CPU: ~1.07 ms / inference
- GPU: ~1.17 ms / inference

This is comfortably below a 1 Hz decision budget (1000 ms).

## Scientific limitations (explicit)

- Future PAC R² remains modest on unseen subjects (as expected from prior analyses).
- Data noise and inter-subject heterogeneity remain primary bottlenecks.
- Current implementation is scientifically conservative (causal, leakage-safe), but additional gains likely require better targets/features (e.g., stronger denoising, richer causal context, or protocol redesign).

## Update: denoised latent target run

A follow-up run used causal target smoothing (`target_smooth_window=5`) with:

- lookback=20, horizon=1, hidden=64.

Artifact:

- `models/summary_multiscale_tcn_lb20_hz1_ts5.json`

Observed metrics:

- Test future `R²=0.7503`, corr `0.8731`
- Test delta `R²=0.2335`, corr `0.4901`

Interpretation:

- Strong predictability is achievable for **denoised latent PAC state**.
- This does **not** mean raw instantaneous PAC is equally predictable.
- For closed-loop control, latent-state forecasting is often the more stable objective.
