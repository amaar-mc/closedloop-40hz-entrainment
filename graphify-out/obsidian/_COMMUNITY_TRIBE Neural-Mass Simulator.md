---
type: community
members: 115
---

# TRIBE Neural-Mass Simulator

**Members:** 115 nodes

## Members
- [[40 Hz Auditory Stimulus Generator for TRIBE V2 Integration  Generates auditory c]] - rationale - src/tribe_v2/stimulus_generator.py
- [[Alzheimer's Disease Modeling Layer for TRIBE V2 Integration  Models the effects]] - rationale - src/tribe_v2/alzheimer_model.py
- [[AlzheimerProfile]] - code - src/tribe_v2/alzheimer_model.py
- [[Apply cosine onsetoffset ramp to prevent spectral artifacts.]] - rationale - src/tribe_v2/stimulus_generator.py
- [[Apply disease modification to cortical activation level.          Reduces activa]] - rationale - src/tribe_v2/alzheimer_model.py
- [[Apply disease modifications to neural mass parameters.]] - rationale - src/tribe_v2/enhanced_simulator.py
- [[Apply region-specific disease modification to ROI activations.          Differen]] - rationale - src/tribe_v2/alzheimer_model.py
- [[Audit script for TRIBE V2 integration module.  Validates     1. All module impo]] - rationale - src/tribe_v2/audit_tribe_integration.py
- [[Biophysically grounded brain entrainment simulator.      This simulator replaces]] - rationale - src/tribe_v2/enhanced_simulator.py
- [[Check all module imports.]] - rationale - src/tribe_v2/audit_tribe_integration.py
- [[Compute PAC (Modulation Index) from a simulated signal.          Uses the same T]] - rationale - src/tribe_v2/neural_mass.py
- [[Compute average PAC across channels from multi-channel EEG.          Args]] - rationale - src/tribe_v2/enhanced_simulator.py
- [[Configuration for 40 Hz auditory stimulus generation.]] - rationale - src/tribe_v2/stimulus_generator.py
- [[Configuration for Wilson-Cowan neural mass model.      Default parameters tuned]] - rationale - src/tribe_v2/neural_mass.py
- [[Configuration for cortical response model.]] - rationale - src/tribe_v2/cortical_model.py
- [[Cortical Response Model — TRIBE V2 Integration with Biophysical Fallback  Wraps]] - rationale - src/tribe_v2/cortical_model.py
- [[CorticalResponseConfig]] - code - src/tribe_v2/cortical_model.py
- [[CorticalResponseModel]] - code - src/tribe_v2/cortical_model.py
- [[Create a default frontal lead field approximation.      Based on typical volume]] - rationale - src/tribe_v2/neural_mass.py
- [[Create an interpolated profile from a continuous severity score.      Allows fin]] - rationale - src/tribe_v2/alzheimer_model.py
- [[Disease-specific parameter profile for Alzheimer's simulation.      Each paramet]] - rationale - src/tribe_v2/alzheimer_model.py
- [[Factory function for creating a configured TRIBE V2-enhanced simulator.      Arg]] - rationale - src/tribe_v2/enhanced_simulator.py
- [[Full configuration for TRIBE V2-enhanced simulator.]] - rationale - src/tribe_v2/enhanced_simulator.py
- [[Generate a 40 Hz amplitude-modulated tone.      An AM tone has a carrier frequen]] - rationale - src/tribe_v2/stimulus_generator.py
- [[Generate a 40 Hz click train stimulus.      Click trains are the standard ASSR s]] - rationale - src/tribe_v2/stimulus_generator.py
- [[Generate a silence stimulus (rest condition).      Args         duration_sec D]] - rationale - src/tribe_v2/stimulus_generator.py
- [[Generate auditory stimulus based on configuration.      Args         cfg Stimu]] - rationale - src/tribe_v2/stimulus_generator.py
- [[Get Alzheimer's profile by severity name.      Args         severity One of h]] - rationale - src/tribe_v2/alzheimer_model.py
- [[Get current ROI activations for the simulation step.          In parametric mode]] - rationale - src/tribe_v2/cortical_model.py
- [[Get current simulator state._1]] - rationale - src/tribe_v2/enhanced_simulator.py
- [[Get full simulation history. Compatible with EntrainmentSimulator.          Retu]] - rationale - src/tribe_v2/enhanced_simulator.py
- [[Load TRIBE V2 model from HuggingFace Hub.]] - rationale - src/tribe_v2/cortical_model.py
- [[Load fsaverage5 atlas labels and build ROI vertex index map.]] - rationale - src/tribe_v2/cortical_model.py
- [[Map mean cortical activation to PAC value.          Uses a sigmoidal mapping cal]] - rationale - src/tribe_v2/enhanced_simulator.py
- [[Modify exponential simulator parameters for AD simulation.          Compatible w]] - rationale - src/tribe_v2/alzheimer_model.py
- [[Modify neural mass model external drive for AD simulation.          Args]] - rationale - src/tribe_v2/alzheimer_model.py
- [[NeuralMassConfig]] - code - src/tribe_v2/neural_mass.py
- [[Pre-generate a library of stimuli at various durations.      Creates both click]] - rationale - src/tribe_v2/stimulus_generator.py
- [[Predict ROI activations using TRIBE V2 model.          Note TRIBE V2 requires n]] - rationale - src/tribe_v2/cortical_model.py
- [[Predicts cortical ROI activations in response to 40 Hz auditory stimulation.]] - rationale - src/tribe_v2/cortical_model.py
- [[Reset simulator to initial state._1]] - rationale - src/tribe_v2/enhanced_simulator.py
- [[Reset state variables to initial conditions.]] - rationale - src/tribe_v2/neural_mass.py
- [[Reset to initial resting state.]] - rationale - src/tribe_v2/cortical_model.py
- [[Run a brief warmup to establish baseline PAC.]] - rationale - src/tribe_v2/enhanced_simulator.py
- [[Save stimulus as WAV file for TRIBE V2 input.      Args         signal Audio w]] - rationale - src/tribe_v2/stimulus_generator.py
- [[Sigmoidal activation function for population firing rate.]] - rationale - src/tribe_v2/neural_mass.py
- [[Simulate multi-channel EEG from multiple ROI activations.          Each ROI driv]] - rationale - src/tribe_v2/neural_mass.py
- [[Simulate neural mass dynamics and return EEG-rate output.          Generates a s]] - rationale - src/tribe_v2/neural_mass.py
- [[Simulate one time step of neural dynamics.          Pipeline             1. Get]] - rationale - src/tribe_v2/enhanced_simulator.py
- [[StimAction_1]] - code - src/tribe_v2/enhanced_simulator.py
- [[StimulusConfig]] - code - src/tribe_v2/stimulus_generator.py
- [[TRIBE V2 Integration Module for Closed-Loop 40Hz Entrainment  Integrates Meta's]] - rationale - src/tribe_v2/__init__.py
- [[TRIBE V2-Enhanced Brain Entrainment Simulator  Replaces the simple exponential P]] - rationale - src/tribe_v2/enhanced_simulator.py
- [[TribeEnhancedSimulator]] - code - src/tribe_v2/enhanced_simulator.py
- [[TribeSimulatorConfig]] - code - src/tribe_v2/enhanced_simulator.py
- [[Validate Alzheimer's disease profiles.]] - rationale - src/tribe_v2/audit_tribe_integration.py
- [[Validate cortical response model dynamics.]] - rationale - src/tribe_v2/audit_tribe_integration.py
- [[Validate disease severity produces monotonic PAC degradation.]] - rationale - src/tribe_v2/audit_tribe_integration.py
- [[Validate enhanced simulator compatibility and dynamics.]] - rationale - src/tribe_v2/audit_tribe_integration.py
- [[Validate neural mass model PAC generation.]] - rationale - src/tribe_v2/audit_tribe_integration.py
- [[Validate stimulus generation.]] - rationale - src/tribe_v2/audit_tribe_integration.py
- [[Wilson-Cowan Neural Mass Model for Theta-Gamma Oscillatory Dynamics  Converts co]] - rationale - src/tribe_v2/neural_mass.py
- [[Wilson-Cowan neural mass model producing theta-gamma coupled oscillations.]] - rationale - src/tribe_v2/neural_mass.py
- [[WilsonCowanModel]] - code - src/tribe_v2/neural_mass.py
- [[__init__()_168]] - code - src/tribe_v2/neural_mass.py
- [[__init__()_169]] - code - src/tribe_v2/enhanced_simulator.py
- [[__init__()_170]] - code - src/tribe_v2/cortical_model.py
- [[_activation_to_pac()]] - code - src/tribe_v2/enhanced_simulator.py
- [[_apply_disease_to_neural_mass()]] - code - src/tribe_v2/enhanced_simulator.py
- [[_apply_ramp()]] - code - src/tribe_v2/stimulus_generator.py
- [[_compute_pac_from_eeg()]] - code - src/tribe_v2/enhanced_simulator.py
- [[_default_frontal_mixing_matrix()]] - code - src/tribe_v2/neural_mass.py
- [[_load_roi_indices()]] - code - src/tribe_v2/cortical_model.py
- [[_load_tribe_model()]] - code - src/tribe_v2/cortical_model.py
- [[_sigmoid()]] - code - src/tribe_v2/neural_mass.py
- [[_warmup()]] - code - src/tribe_v2/enhanced_simulator.py
- [[alzheimer_model.py]] - code - src/tribe_v2/alzheimer_model.py
- [[apply_to_activation()]] - code - src/tribe_v2/alzheimer_model.py
- [[apply_to_roi_activations()]] - code - src/tribe_v2/alzheimer_model.py
- [[audit_alzheimer_model()]] - code - src/tribe_v2/audit_tribe_integration.py
- [[audit_cortical_model()]] - code - src/tribe_v2/audit_tribe_integration.py
- [[audit_disease_sweep()]] - code - src/tribe_v2/audit_tribe_integration.py
- [[audit_enhanced_simulator()]] - code - src/tribe_v2/audit_tribe_integration.py
- [[audit_imports()]] - code - src/tribe_v2/audit_tribe_integration.py
- [[audit_neural_mass()]] - code - src/tribe_v2/audit_tribe_integration.py
- [[audit_stimulus_generator()]] - code - src/tribe_v2/audit_tribe_integration.py
- [[audit_tribe_integration.py]] - code - src/tribe_v2/audit_tribe_integration.py
- [[check()_1]] - code - src/tribe_v2/audit_tribe_integration.py
- [[compute_pac_from_signal()]] - code - src/tribe_v2/neural_mass.py
- [[cortical_model.py]] - code - src/tribe_v2/cortical_model.py
- [[create_simulator()_1]] - code - src/tribe_v2/enhanced_simulator.py
- [[enhanced_simulator.py]] - code - src/tribe_v2/enhanced_simulator.py
- [[generate_am_tone()]] - code - src/tribe_v2/stimulus_generator.py
- [[generate_click_train()]] - code - src/tribe_v2/stimulus_generator.py
- [[generate_silence()]] - code - src/tribe_v2/stimulus_generator.py
- [[generate_stimulus()]] - code - src/tribe_v2/stimulus_generator.py
- [[generate_stimulus_library()]] - code - src/tribe_v2/stimulus_generator.py
- [[get_activations()]] - code - src/tribe_v2/cortical_model.py
- [[get_history()_4]] - code - src/tribe_v2/enhanced_simulator.py
- [[get_profile()]] - code - src/tribe_v2/alzheimer_model.py
- [[get_state()_2]] - code - src/tribe_v2/enhanced_simulator.py
- [[interpolate_profile()]] - code - src/tribe_v2/alzheimer_model.py
- [[main()_79]] - code - src/tribe_v2/audit_tribe_integration.py
- [[modify_neural_mass_drive()]] - code - src/tribe_v2/alzheimer_model.py
- [[modify_simulator_params()]] - code - src/tribe_v2/alzheimer_model.py
- [[neural_mass.py]] - code - src/tribe_v2/neural_mass.py
- [[predict_tribe_v2()]] - code - src/tribe_v2/cortical_model.py
- [[reset()_68]] - code - src/tribe_v2/neural_mass.py
- [[reset()_69]] - code - src/tribe_v2/enhanced_simulator.py
- [[reset()_70]] - code - src/tribe_v2/cortical_model.py
- [[save_stimulus_wav()]] - code - src/tribe_v2/stimulus_generator.py
- [[simulate()]] - code - src/tribe_v2/neural_mass.py
- [[simulate_multichannel()]] - code - src/tribe_v2/neural_mass.py
- [[step()_72]] - code - src/tribe_v2/enhanced_simulator.py
- [[stimulus_generator.py]] - code - src/tribe_v2/stimulus_generator.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/TRIBE_Neural-Mass_Simulator
SORT file.name ASC
```

## Connections to other communities
- 26 edges to [[_COMMUNITY_Closed-Loop Control & Simulator]]
- 3 edges to [[_COMMUNITY_Models, Streaming & Apps]]
- 1 edge to [[_COMMUNITY_Community 32]]

## Top bridge nodes
- [[TRIBE V2 Integration Module for Closed-Loop 40Hz Entrainment  Integrates Meta's]] - degree 9, connects to 2 communities
- [[TribeEnhancedSimulator]] - degree 39, connects to 1 community
- [[TribeSimulatorConfig]] - degree 29, connects to 1 community