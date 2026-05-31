---
source_file: "src/controller.py"
type: "code"
community: "Closed-Loop Control & Simulator"
location: "L34"
tags:
  - community/Closed-Loop_Control_&_Simulator
---

# StimState

## Connections
- [[Abstract base class for all control strategies.      Subclasses must implement]] - `uses` [INFERRED]
- [[Add control method to comparison.]] - `uses` [INFERRED]
- [[Compare methods using statistical tests on multi-trial data.          Uses acc]] - `uses` [INFERRED]
- [[Compute recent PAC slope over last k steps (trend fallback).          Uses o]] - `uses` [INFERRED]
- [[Container for validation metrics.]] - `uses` [INFERRED]
- [[ControlMethodBase_2]] - `uses` [INFERRED]
- [[Convert to dictionary.]] - `uses` [INFERRED]
- [[Determine action based on fixed schedule.          Args             pac_curr]] - `uses` [INFERRED]
- [[EEGNet_1]] - `uses` [INFERRED]
- [[Fixed 40s ON + 20s OFF schedule (control condition)._1]] - `uses` [INFERRED]
- [[FixedScheduleControl_7]] - `uses` [INFERRED]
- [[Generate comparison plots.          Args             output_name Output fil]] - `uses` [INFERRED]
- [[Initialize control method.          Args             name Human-readable na]] - `uses` [INFERRED]
- [[Initialize fixed schedule.          Args             stim_duration Stimulat]] - `uses` [INFERRED]
- [[Initialize oracle control.          Args             pac_target Target PAC]] - `uses` [INFERRED]
- [[Initialize reactive control.          Args             window_size Baseline]] - `uses` [INFERRED]
- [[Initialize validator.          Args             output_dir Directory for sa]] - `uses` [INFERRED]
- [[IntEnum]] - `inherits` [EXTRACTED]
- [[Main entry point for validation.]] - `uses` [INFERRED]
- [[Make a stimulation decision using look-ahead prediction.          When a TCN f]] - `uses` [INFERRED]
- [[Make a stimulation decision.          Args             pac_current Current]] - `uses` [INFERRED]
- [[Make optimal decision based on perfect information.          Args]] - `uses` [INFERRED]
- [[Make reactive decision based on current PAC.          Maintains current state]] - `uses` [INFERRED]
- [[Oracle perfect knowledge of optimal PAC (theoretical upper bound).]] - `uses` [INFERRED]
- [[OracleControl_6]] - `uses` [INFERRED]
- [[PersonalizationModule]] - `uses` [INFERRED]
- [[Predictive look-ahead control for proactive stimulation scheduling.      When]] - `uses` [INFERRED]
- [[PredictiveLookAheadControl_6]] - `uses` [INFERRED]
- [[Reactive control based on current PAC vs. baseline with hysteresis.]] - `uses` [INFERRED]
- [[ReactiveThresholdControl_6]] - `uses` [INFERRED]
- [[Reset baseline buffer and state.]] - `uses` [INFERRED]
- [[Reset method state for a new trial.]] - `uses` [INFERRED]
- [[Reset state for a new trial._2]] - `uses` [INFERRED]
- [[Reset to start of cycle.]] - `uses` [INFERRED]
- [[Run all methods multiple times with matched noise per trial.          Each tri]] - `uses` [INFERRED]
- [[Run simulation for a single control method.          Seeds the RNG before each]] - `uses` [INFERRED]
- [[SimulationValidator]] - `uses` [INFERRED]
- [[Stimulation state enumeration.      Values         STIMULATE = 1 Active 40]] - `rationale_for` [EXTRACTED]
- [[Validates and compares control strategies using simulation.      Workflow]] - `uses` [INFERRED]
- [[Validation and Comparison Framework for Closed-Loop Control Strategies.  Compa]] - `uses` [INFERRED]
- [[ValidationMetrics]] - `uses` [INFERRED]
- [[Whether a trained TCN forecaster is available.]] - `uses` [INFERRED]
- [[__str__()]] - `method` [EXTRACTED]
- [[controller.py]] - `contains` [EXTRACTED]

  #community/Closed-Loop_Control_&_Simulator