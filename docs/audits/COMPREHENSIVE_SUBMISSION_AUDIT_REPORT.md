# Comprehensive Submission Audit Report

Date: February 17, 2026  
Repository: `closedloop-40hz-entrainment`

## Scope

Audited the new multiscale temporal pipeline under `temporal_multiscale/` for:
- subject split leakage,
- temporal causality leakage,
- normalization leakage,
- label-shuffle sanity,
- model dependency on PAC-oracle features at inference.

Audited datasets:
- `data/processed/multiscale_temporal_lb20_hz1_ts1` (`target_smooth_window=1`)
- `data/processed/multiscale_temporal_lb20_hz1_ts5_clean` (`target_smooth_window=5`)
- `data/processed/multiscale_temporal_lb20_hz1_ts15` (`target_smooth_window=15`)

## Commands Executed

Structural + statistical audit:
```powershell
.\venv\Scripts\python.exe temporal_multiscale\comprehensive_submission_audit.py --dataset-dir data/processed/multiscale_temporal_lb20_hz1_ts1 --output-json models/comprehensive_audit_multiscale_ts1.json
.\venv\Scripts\python.exe temporal_multiscale\comprehensive_submission_audit.py --dataset-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean --output-json models/comprehensive_audit_multiscale_ts5_clean.json
.\venv\Scripts\python.exe temporal_multiscale\comprehensive_submission_audit.py --dataset-dir data/processed/multiscale_temporal_lb20_hz1_ts15 --output-json models/comprehensive_audit_multiscale_ts15.json
```

Deployment realism audit:
```powershell
.\venv\Scripts\python.exe temporal_multiscale\checkpoint_deployment_audit.py --checkpoint models/best_multiscale_tcn_lb20_hz1_ts1_audit.pth --dataset-dir data/processed/multiscale_temporal_lb20_hz1_ts1 --output-json models/deployment_audit_multiscale_ts1.json
.\venv\Scripts\python.exe temporal_multiscale\checkpoint_deployment_audit.py --checkpoint models/best_multiscale_tcn_lb20_hz1_ts5_audit.pth --dataset-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean --output-json models/deployment_audit_multiscale_ts5_clean.json
.\venv\Scripts\python.exe temporal_multiscale\checkpoint_deployment_audit.py --checkpoint models/best_multiscale_tcn_lb20_hz1_ts15_audit.pth --dataset-dir data/processed/multiscale_temporal_lb20_hz1_ts15 --output-json models/deployment_audit_multiscale_ts15.json
```

## Core Findings

## 1) Leakage Integrity Checks
- No subject overlap across train/val/test: **PASS**.
- Temporal causality (`target_idx > end_idx`): **PASS**.
- Train-only normalization behavior: **PASS**.
- Label-shuffle sanity (performance collapses): **PASS**.

Conclusion: no direct train/test leakage or future-index leakage detected.

## 2) Why Very High R² Appears

High R² is strongly tied to target smoothing and PAC-history inputs:

- `target_smooth_window=1`:
  - TCN test future R²: ~0.07
- `target_smooth_window=5`:
  - TCN test future R²: ~0.75
- `target_smooth_window=15`:
  - TCN test future R²: ~0.88-0.91

This is expected because smoothing increases autocorrelation of the target latent state.

## 3) PAC Oracle Dependency (Deployment Risk)

From deployment audits:
- `ts5` checkpoint baseline future R²: ~0.7485
- `ts5` with PAC features zeroed: ~-0.0370
- `ts15` baseline future R²: ~0.8821
- `ts15` with PAC features zeroed: ~0.0430

Interpretation:
- The model critically relies on PAC-derived input channels.
- This is not a temporal leakage bug, but it means real deployment quality depends on how accurately `pac_current` is estimated online.

## 4) Naming/Experiment Hygiene Issue Found

A prior run reused dataset path `..._ts5` while setting `target_smooth_window=15`.  
This caused confusing labels (path name no longer matched target definition).  

Mitigation implemented:
- Added strict metadata mismatch guard in `temporal_multiscale/train_multiscale_tcn.py` (requires `--rebuild-dataset` or explicit `--allow-metadata-mismatch`).

## Final Verdict

- **Pipeline leakage status:** PASS (no direct data leakage found).
- **Scientific interpretation:** high scores are valid for denoised latent targets, but must be reported as such.
- **Deployment realism caveat:** if real-time `pac_current` estimator is weak, live performance will drop substantially.

## Submission Recommendation

For judging/reporting, present all three:
1. Raw target (`target_smooth_window=1`) performance.
2. Smoothed latent target (`target_smooth_window=5` and/or 15) performance.
3. Deployment audit with PAC-feature corruption/ablation to quantify sensitivity.

That framing is rigorous, transparent, and defensible.

