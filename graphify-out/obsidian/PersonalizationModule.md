---
source_file: "src/personalization.py"
type: "code"
community: "Closed-Loop Control & Simulator"
location: "L22"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# PersonalizationModule

## Connections

- [[Closed-Loop Controller for Real-Time PAC-Based Neuromodulation  Implements thr]] - `uses` [INFERRED]
- [[ClosedLoopController]] - `uses` [INFERRED]
- [[End-to-end streaming inference demo for closed-loop 40 Hz entrainment.  Runs the]] - `uses` [INFERRED]
- [[Execute one control step with look-ahead prediction.          Args]] - `uses` [INFERRED]
- [[Execute one control step.          Processes incoming EEG window and makes sti]] - `uses` [INFERRED]
- [[Get current controller state.          Returns             state Dictionary]] - `uses` [INFERRED]
- [[Get full history of decisions and measurements.          Returns]] - `uses` [INFERRED]
- [[Get full history of decisions, measurements, and predictions.]] - `uses` [INFERRED]
- [[Get personalization baseline statistics.          Returns             stats]] - `uses` [INFERRED]
- [[Initialize closed-loop controller.          Args             model_path Pat]] - `uses` [INFERRED]
- [[Initialize predictive look-ahead controller.          Args             forec]] - `uses` [INFERRED]
- [[Load 4-channel EEGNet from checkpoint.      Returns         model EEGNet in ev]] - `uses` [INFERRED]
- [[Maintains patient-specific baseline statistics and computes z-scores.      The]] - `rationale_for` [EXTRACTED]
- [[Make proactive stimulation decision using predicted PAC trajectory.          P]] - `uses` [INFERRED]
- [[Make stimulation decision based on z-score.          Logic             - If]] - `uses` [INFERRED]
- [[Predictive closed-loop controller using a trained TCN to forecast     future PA]] - `uses` [INFERRED]
- [[PredictiveLookAheadController]] - `uses` [INFERRED]
- [[Reactive z-score stimulus decision with hysteresis hold.      Args         pac_]] - `uses` [INFERRED]
- [[Real-time closed-loop controller for adaptive neuromodulation.      Integrates]] - `uses` [INFERRED]
- [[Reset controller and forecaster for a new session.]] - `uses` [INFERRED]
- [[Reset controller for new session.          Clears all state, baseline, and his]] - `uses` [INFERRED]
- [[Return 'mps' if available, else 'cuda' if available, else 'cpu'.]] - `uses` [INFERRED]
- [[Run EEGNet on a (n_channels, 500) window and return denormalised PAC.      Args]] - `uses` [INFERRED]
- [[StimState]] - `uses` [INFERRED]
- [[Stimulation state enumeration.      Values         STIMULATE = 1 Active 40]] - `uses` [INFERRED]
- [[Test controller with synthetic EEG and simulated PAC.]] - `uses` [INFERRED]
- [[__init__()_152]] - `method` [EXTRACTED]
- [[__init__()_153]] - `calls` [EXTRACTED]
- [[compute_zscore()]] - `method` [EXTRACTED]
- [[get_baseline_stats()_1]] - `method` [EXTRACTED]
- [[get_buffer_contents()]] - `method` [EXTRACTED]
- [[get_buffer_size()]] - `method` [EXTRACTED]
- [[is_ready()]] - `method` [EXTRACTED]
- [[personalization.py]] - `contains` [EXTRACTED]
- [[reset()_59]] - `method` [EXTRACTED]
- [[test_personalization()]] - `calls` [EXTRACTED]
- [[update()]] - `method` [EXTRACTED]

  #community/Closed-Loop*Control*&\_Simulator
