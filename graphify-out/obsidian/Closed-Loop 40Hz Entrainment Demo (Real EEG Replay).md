---
source_file: "apps/demo.py"
type: "code"
community: "Community 91"
location: "module"
tags:
  - community/Community_91
---

# Closed-Loop 40Hz Entrainment Demo (Real EEG Replay)

## Connections

- [[Audio Engine (40 Hz click-train via sounddevice)]] - `calls` [EXTRACTED]
- [[Fixed Schedule Controller (40s ON20s OFF)]] - `calls` [EXTRACTED]
- [[Oracle Controller (perfect knowledge baseline)]] - `calls` [EXTRACTED]
- [[Predictive Look-Ahead Controller (trend+hysteresis)]] - `calls` [EXTRACTED]
- [[Reactive Threshold Controller (Z-score)]] - `calls` [EXTRACTED]
- [[TCN Checkpoint (best_multiscale_tcn_lb20_hz5_ts1.pth)]] - `references` [EXTRACTED]
- [[TCN Controller (causal forecaster, primary contribution)]] - `calls` [EXTRACTED]
- [[_build_figure()]] - `calls` [EXTRACTED]
- [[load_subject_data()]] - `calls` [EXTRACTED]

  #community/Community_91
