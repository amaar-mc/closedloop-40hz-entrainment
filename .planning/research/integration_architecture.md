# TRIBE V2 Integration Architecture

## Problem Statement

TRIBE V2 predicts fMRI cortical surface activations from stimuli (audio/video/text).
Our closed-loop system operates on EEG (7 frontal channels, 250 Hz, theta-gamma PAC).
We need a biophysically grounded bridge between these modalities.

## Architecture Overview

```
40 Hz Auditory Stimulus (tone bursts)
        |
        v
+-------------------+
| TRIBE V2 Model    |  Wav2Vec-BERT audio encoder
| (fMRI Encoding)   |  + Unified Transformer
+-------------------+
        |
        v
Cortical Surface Activations (~20k vertices, fsaverage5)
        |
        v
+-------------------+
| ROI Extraction    |  Destrieux/DK atlas parcellation
| (Auditory + Frontal ROIs)
+-------------------+
        |
        v
Regional Activation Levels (scalar per ROI)
        |
        v
+-------------------+
| Neural Mass Model |  Wilson-Cowan oscillatory dynamics
| (Activation → Oscillations)
+-------------------+
        |
        v
Source-level theta (4-8 Hz) + gamma (38-42 Hz) oscillations
        |
        v
+-------------------+
| EEG Forward Model |  Lead field matrix (MNE-Python)
| (Source → Scalp)  |  fsaverage5 → 7 frontal channels
+-------------------+
        |
        v
Simulated 7-channel EEG with realistic PAC
        |
        v
+-------------------+
| PAC Computation   |  Tort MI (existing module)
+-------------------+
        |
        v
+-------------------+
| Closed-Loop       |  Controller + Personalization
| Controller        |  (existing pipeline)
+-------------------+
```

## Layer 1: TRIBE V2 Cortical Response Predictor

### Input
- 40 Hz auditory tone bursts (click trains or AM tones)
- Generated as WAV files with configurable parameters:
  - Carrier frequency: 40 Hz
  - Duration: matches simulation step (2s windows)
  - Modulation: ON (stimulation) or OFF (rest/silence)

### Processing
```python
from tribev2 import TribeModel

model = TribeModel.from_pretrained("facebook/tribev2", cache_folder="./cache")
df = model.get_events_dataframe(audio_path="stimuli/40hz_tone.wav")
preds, segments = model.predict(events=df)
# preds.shape: (n_timesteps, ~20000)
```

### Output
- Cortical activation map: (n_timesteps, n_vertices) on fsaverage5
- 5-second hemodynamic lag compensation built into TRIBE V2

### Caching Strategy
- Pre-compute cortical responses for:
  1. 40 Hz stimulation (various durations: 2s, 5s, 10s, 20s, 40s)
  2. Silence/rest (matching durations)
  3. Transition periods (onset, offset)
- Cache as .npz files → fast lookup during simulation

## Layer 2: ROI Extraction

### Relevant ROIs (Destrieux atlas on fsaverage5)
- **Primary auditory cortex** (Heschl's gyrus): Direct 40 Hz ASSR
- **Superior temporal gyrus (STG)**: Auditory processing
- **Inferior frontal gyrus (IFG)**: Frontal gamma entrainment
- **Middle frontal gyrus (MFG)**: Executive attention
- **Superior frontal gyrus (SFG)**: Higher-order processing
- **Medial frontal/Cingulate**: Attentional modulation

### Mapping to EEG Channels
| EEG Channel | Primary ROI Sources |
|-------------|-------------------|
| Fp1, Fp2    | Medial/Superior frontal, Orbital frontal |
| F3, F4      | Middle frontal gyrus, Precentral |
| F7, F8      | Inferior frontal gyrus, Temporal pole |
| Fz          | Medial frontal, Supplementary motor area |

### Implementation
```python
import mne
labels = mne.read_labels_from_annot('fsaverage', parc='aparc', subjects_dir=...)
# Extract mean activation per ROI from TRIBE V2 predictions
roi_activations = extract_roi_means(preds, labels, relevant_rois)
```

## Layer 3: Neural Mass Model (Wilson-Cowan)

### Purpose
Convert fMRI-level activation envelopes to oscillatory dynamics with
theta-gamma coupling. This is the biophysical bridge.

### Model
Simplified Wilson-Cowan equations for excitatory-inhibitory population:

```
dE/dt = (-E + S(c_ee * E - c_ei * I + P_ext)) / tau_e
dI/dt = (-I + S(c_ie * E - c_ii * I)) / tau_i
```

Where:
- E, I = excitatory/inhibitory population activity
- S(x) = sigmoid activation function
- P_ext = external drive from TRIBE V2 cortical activation
- tau_e, tau_i = time constants tuned for theta and gamma

### Key Parameters
- **Gamma generation**: tau_e ~ 4ms (25 Hz carrier, tuned to 40 Hz with P_ext)
- **Theta modulation**: Slower modulatory loop (tau ~ 50-100ms)
- **PAC emerges** naturally when gamma amplitude is modulated by theta phase
- **P_ext scaling**: TRIBE V2 activation level scales the external drive,
  determining the strength of gamma entrainment

### Parameterization from TRIBE V2
- Higher cortical activation → stronger P_ext → stronger gamma → higher PAC
- Auditory cortex activation → gamma power
- Frontal activation → theta-gamma coupling strength
- The activation level directly modulates PAC_max in the simulation

## Layer 4: EEG Forward Model

### Purpose
Project source-level oscillations to 7 frontal EEG channels.

### Implementation
Use MNE-Python's forward model with fsaverage:
```python
fwd = mne.make_forward_solution(info, trans='fsaverage', src=src, bem=bem)
leadfield = fwd['sol']['data']  # (n_channels, n_sources)
# Project: eeg = leadfield @ source_activity
```

### Simplification for Simulation
For real-time simulation, precompute a reduced lead field:
- 7 frontal channels x N_ROI sources
- Static mixing matrix applied at each timestep
- ~0.1ms computation per step

## Layer 5: Alzheimer's Disease Modeling

### Cortical Atrophy
- Apply AD-specific atrophy maps to scale TRIBE V2 activations
- Published atrophy patterns (Braak staging):
  - Stage I-II: Entorhinal/hippocampal (minimal frontal impact)
  - Stage III-IV: Temporal, parietal spread
  - Stage V-VI: Frontal cortex involvement

### Impaired Gamma Entrainment
- Reduce gamma power generation in neural mass model
- Scale factor: 0.3-0.7x for mild-moderate AD
- Reduced ASSR amplitude (documented in AD literature)

### Altered PAC
- Decrease theta-gamma coupling coefficient
- Increase theta power (characteristic of AD)
- Net effect: lower PAC baseline, reduced response to stimulation

### Disease Severity Parameters
```python
@dataclass
class AlzheimerProfile:
    severity: str  # "healthy", "mild", "moderate", "severe"
    cortical_atrophy_scale: float  # 1.0 = healthy, 0.3 = severe
    gamma_efficacy: float  # 1.0 = healthy, 0.3 = severe
    theta_power_multiplier: float  # 1.0 = healthy, 2.0 = severe
    pac_coupling_scale: float  # 1.0 = healthy, 0.4 = severe
    fatigue_rate_multiplier: float  # 1.0 = healthy, 1.5 = severe (faster habituation)
```

## Integration with Existing Codebase

### New Files
```
src/
  tribe_v2/
    __init__.py
    cortical_model.py        # TRIBE V2 wrapper + cortical activation extraction
    neural_mass.py           # Wilson-Cowan oscillatory dynamics
    eeg_forward.py           # Source-to-scalp projection
    alzheimer_model.py       # AD pathology parameters
    enhanced_simulator.py    # TribeEnhancedSimulator class
    stimulus_generator.py    # 40 Hz auditory stimulus generation
    config.py                # TRIBE V2 integration config
```

### Modified Files
- `config.yaml` → Add `tribe_v2` section
- `scripts/pipeline/run_closed_loop_demo.py` → Add TRIBE V2-enhanced scenario
- `src/validation.py` → Add TribeEnhanced control method comparison

### New Entry Points
- `run_tribe_validation.py` → Full comparison: original vs TRIBE V2-enhanced
- `run_alzheimer_simulation.py` → Disease severity sweep

## Validation Plan

### 1. Biological Plausibility
- Verify TRIBE V2 cortical predictions show expected auditory cortex activation
- Verify neural mass model produces theta-gamma PAC in physiological range
- Compare PAC dynamics with real EEG from ds005048

### 2. Simulation Improvement
- Compare original exponential simulator vs TRIBE V2-enhanced:
  - PAC dynamics realism (compare with real data distributions)
  - Transition dynamics (stim onset/offset)
  - Subject variability

### 3. Closed-Loop Performance
- Run all 4 strategies on TRIBE V2-enhanced simulator
- Compare alignment accuracy, stimulation efficiency
- Show that biologically grounded simulation produces more meaningful results

### 4. Alzheimer's Disease Modeling
- Sweep disease severity and show expected degradation pattern
- Verify 40 Hz stimulation benefit is greatest in mild-moderate AD
- Demonstrate adaptive controller advantage in AD simulation

## Hardware Requirements
- TRIBE V2 model: ~4-8 GB (fits Apple Silicon MPS)
- Inference: ~1-2s per prediction (precompute → negligible runtime)
- Total pipeline: ~10 GB RAM
