# fMRI-to-EEG Bridge: Methods Research for TRIBE V2 Integration

**Researched:** 2026-04-02
**Overall Confidence:** MEDIUM
**Domain:** Computational neuroscience — multimodal brain signal mapping

---

## Executive Summary

Bridging Meta's TRIBE V2 fMRI predictions to our EEG-based closed-loop system requires solving four linked problems: (1) mapping fMRI cortical activations to neural current sources, (2) projecting those sources through a volume conduction model to EEG scalp signals, (3) bridging the temporal resolution gap (1.49s TR → 4ms EEG), and (4) generating oscillatory dynamics (theta 4-8 Hz, gamma 38-42 Hz) from activation envelopes. Each layer has established methods with Python implementations. The recommended approach uses MNE-Python's forward model pipeline as the backbone, with a simplified Wilson-Cowan neural mass model to generate PAC-relevant oscillations from TRIBE V2's cortical activation predictions.

**Critical finding:** TRIBE V2 outputs predictions on the **Schaefer 1000-parcel atlas** (not individual fsaverage5 vertices as initially assumed). Each parcel gets one BOLD activation value per TR (1.49s). This means our bridge must: (a) identify the ~50-100 frontal/temporal parcels relevant to our 7 EEG channels, (b) convert parcel-level BOLD activations to neural current densities, and (c) project through a lead field matrix to scalp EEG.

---

## 1. TRIBE V2 Architecture (What We're Working With)

### Model Overview
- **Paper:** [TRIBE: TRImodal Brain Encoder for whole-brain fMRI response prediction](https://arxiv.org/abs/2507.22229) (2025/2026)
- **Code:** [github.com/facebookresearch/tribev2](https://github.com/facebookresearch/tribev2)
- **Winner:** Algonauts 2025 brain encoding competition (1st place)

### Key Technical Specs
| Property | Value |
|----------|-------|
| Input modalities | Video, Audio, Text (trimodal) |
| Architecture | Transformer mapping multimodal representations to cortical surface |
| Output parcellation | **Schaefer 1000 parcels** (MNI152NLin2009cAsym space) |
| Cortical vertices | 20,484 cortical + 8,802 subcortical voxels (for visualization) |
| Surface template | fsaverage5 (for visualization/projection) |
| Temporal resolution | TR = 1.49s, features extracted at 2 Hz |
| Training data | 451.6 hours fMRI from 25 subjects |
| Evaluation metric | Pearson correlation between predicted and ground-truth BOLD |

### Output Structure
```python
preds, segments = model.predict(events=df)
print(preds.shape)  # (n_timesteps, n_vertices) or (n_timesteps, 1000) for parcels
# Temporal offset: 5 seconds backward for hemodynamic lag
# Represents "average" subject prediction
```

### Regional Performance
- **Strongest:** Auditory cortex, language areas (near noise ceiling)
- **Weakest:** Primary visual cortex (multimodal underperforms unimodal vision)
- **Largest gains from multimodality:** Associative cortices (up to 30% improvement)
- **Modality dominance:** Audio → temporal gyrus, Video → occipital, Text → parietal/prefrontal

### Critical Limitation (from paper)
> "The precise temporal dynamics of neuronal activity, and the exact neural assemblies underlying these macroscopic signals, remain, here, unresolved."

This means TRIBE V2 predicts **hemodynamic envelopes**, not neural oscillations. The entire bridge is about converting these envelopes into oscillatory dynamics.

**Confidence: HIGH** (based on official paper + GitHub repo)

---

## 2. fMRI-to-EEG Forward Modeling

### The Forward Problem
The goal: map cortical source activations → scalp EEG signals.

**Mathematical formulation:**
```
V_scalp = L × J_source
```
Where:
- `V_scalp` = EEG voltage at scalp electrodes (7 channels × time)
- `L` = Lead field matrix (7 channels × N_sources), encodes volume conduction
- `J_source` = Neural current density at cortical sources (N_sources × time)

### Lead Field Matrix via MNE-Python

MNE-Python provides the complete pipeline for computing forward solutions on fsaverage5:

```python
import mne

# 1. Set up source space on fsaverage5
src = mne.setup_source_space('fsaverage', spacing='ico5',
                              subjects_dir=subjects_dir)
# ico5 → 10,242 vertices per hemisphere → 20,484 total (matches TRIBE V2)

# 2. Create BEM model (3-layer: brain, skull, scalp)
model = mne.make_bem_model('fsaverage', conductivity=(0.3, 0.006, 0.3),
                            subjects_dir=subjects_dir)
bem = mne.make_bem_solution(model)

# 3. Define EEG montage (our 7 frontal channels)
montage = mne.channels.make_standard_montage('standard_1020')
# Select: Fp1, Fp2, F3, F4, F7, F8, Fz

# 4. Compute forward solution
fwd = mne.make_forward_solution(info, trans='fsaverage',
                                 src=src, bem=bem, eeg=True)

# 5. Extract lead field matrix
fwd_fixed = mne.convert_forward_solution(fwd, surf_ori=True,
                                          force_fixed=True)
leadfield = fwd_fixed['sol']['data']  # Shape: (7, 20484)
```

### Sensitivity Maps

MNE can compute [sensitivity maps](https://mne.tools/stable/auto_examples/forward/forward_sensitivity_maps.html) showing which cortical regions each electrode is most sensitive to. This directly maps which Schaefer parcels contribute most to each of our 7 frontal channels.

### Volume Conduction Model Options

| Method | Tool | Accuracy | Speed | Recommendation |
|--------|------|----------|-------|----------------|
| 3-layer BEM | MNE + OpenMEEG | HIGH | Moderate | **Use this** |
| Single-sphere | MNE built-in | LOW | Fast | Too simple |
| FEM | SimNIBS, FieldTrip | HIGHEST | Slow | Overkill for this project |

**Recommendation:** Use MNE-Python's 3-layer BEM with OpenMEEG backend. It's the standard in the field, well-documented, and produces physiologically realistic lead fields.

**Confidence: HIGH** (MNE documentation is authoritative; [forward model tutorial](https://mne.tools/stable/auto_tutorials/forward/30_forward.html))

---

## 3. Cortical ROI Mapping

### Schaefer Parcels → Our 7 Frontal Channels

The Schaefer 1000 atlas organizes parcels into [7 or 17 Yeo networks](https://github.com/ThomasYeoLab/CBIG/tree/master/stable_projects/brain_parcellation/Schaefer2018_LocalGlobal). The atlas is available in fsaverage5 space via [nilearn](https://nilearn.github.io/dev/modules/description/schaefer_2018.html):

```python
from nilearn.datasets import fetch_atlas_schaefer_2018
atlas = fetch_atlas_schaefer_2018(n_rois=1000, resolution_mm=2)
# Labels follow format: "7Networks_LH_PFC_1", "7Networks_RH_Aud_2", etc.
```

**Relevant networks for our channels:**

| EEG Channel | Primary Cortical Sources | Schaefer Network(s) |
|-------------|--------------------------|---------------------|
| Fp1, Fp2 | Orbitofrontal, frontopolar | Frontoparietal, Default |
| F3, F4 | Dorsolateral prefrontal | Frontoparietal, Control |
| F7, F8 | Inferior frontal, anterior temporal | Ventral Attention, Default |
| Fz | Medial prefrontal, ACC | Default, Control |

**Estimated relevant parcels:** ~80-120 of 1000 parcels map to regions visible from frontal electrodes.

### 40 Hz ASSR Source Propagation

The [40 Hz auditory steady-state response (ASSR)](https://www.jneurosci.org/content/44/24/e2029232024) is generated primarily in:
- **Primary auditory cortex** (Heschl's gyrus, bilateral)
- **Secondary auditory cortex** (superior temporal gyrus)
- **Prefrontal associative cortex** (with longer latency)

Source localization studies show 40 Hz ASSR sources are bilateral in primary auditory cortex, but volume conduction spreads the signal to [frontal-central EEG channels](https://pmc.ncbi.nlm.nih.gov/articles/PMC7814770/). This is directly relevant: TRIBE V2's strong auditory cortex predictions will propagate to our frontal channels through the lead field matrix.

### Destrieux Atlas ROIs for Gamma Entrainment

Key Destrieux ROIs relevant to 40 Hz entrainment:
- `G_temp_sup-Plan_tempo` — planum temporale (ASSR generator)
- `S_temporal_transverse` — transverse temporal sulcus (Heschl's gyrus)
- `G_front_middle` — middle frontal gyrus (gamma entrainment target)
- `G_front_sup` — superior frontal gyrus (frontal gamma)
- `G_cingul-Post-dorsal` — posterior cingulate (default mode, PAC modulation)

The Destrieux atlas has 148 parcels and maps directly to fsaverage5. Can be loaded via:
```python
labels = mne.read_labels_from_annot('fsaverage', parc='aparc.a2009s',
                                     subjects_dir=subjects_dir)
```

**Confidence: HIGH** (well-established neuroanatomy + nilearn/MNE documentation)

---

## 4. Temporal Resolution Bridge

### The Core Problem
- TRIBE V2 output: 1 prediction per TR (1.49s) → ~0.67 Hz
- Our EEG system: 250 Hz (4ms resolution)
- We need oscillatory dynamics at theta (4-8 Hz) and gamma (38-42 Hz)

This is a **375x temporal upsampling** problem. Direct interpolation is meaningless — you can't extract 40 Hz oscillations from 0.67 Hz samples. Instead, we need a **generative model** that uses TRIBE V2's activation envelopes as constraints.

### Approach 1: HRF Deconvolution → Neural Activity Envelopes

**Step 1:** Convert BOLD predictions back to estimated neural activity using HRF deconvolution.

The [Balloon/Windkessel model (Friston 2000)](https://pubmed.ncbi.nlm.nih.gov/10988040/) describes the forward hemodynamic transform:
```
Neural activity → blood flow → blood volume → BOLD signal
```

The inverse (deconvolution) recovers estimated neural activity envelopes from BOLD:

```python
# Using nilearn/nistats
from nilearn.glm.first_level import compute_regressor

# Or using rsHRF toolbox for deconvolution
# pip install rsHRF
# rsHRF provides blind HRF deconvolution from BOLD timeseries

# Simplified canonical HRF deconvolution:
import numpy as np
from scipy.signal import deconvolve

def hrf_canonical(t, peak=6.0, undershoot=16.0, ratio=6.0):
    """Canonical double-gamma HRF (Glover 1999)."""
    from scipy.stats import gamma as gamma_dist
    h = gamma_dist.pdf(t, peak) - gamma_dist.pdf(t, undershoot) / ratio
    return h / h.max()

# Deconvolve BOLD to get neural activity envelope
# This gives ~1s resolution neural activity estimates
```

**Limitation:** HRF deconvolution gives ~1s temporal resolution at best. Still insufficient for oscillatory dynamics. But it recovers the **neural activity envelope** that modulates oscillation amplitude.

**Step 2:** Use the neural activity envelope to parameterize a neural mass model (see Section 5).

### Approach 2: Neural Mass Model Driven by Activation Envelopes

**This is the recommended approach.** Rather than trying to extract fast dynamics from slow fMRI, use TRIBE V2's predictions as:
1. **Tonic drive level** (P_external) to a neural mass model
2. **Regional activation strength** → scales oscillation amplitude
3. **Stimulation context** → modulates gamma power envelope

The neural mass model generates the fast oscillatory dynamics; TRIBE V2 constrains the slow envelope.

### Approach 3: Simultaneous EEG-fMRI Coupling Models

Research on [simultaneous EEG-fMRI](https://pmc.ncbi.nlm.nih.gov/articles/PMC8952790/) has established empirical coupling models:
- Alpha power correlates negatively with BOLD in visual cortex
- Gamma power correlates positively with BOLD in task-active regions
- The relationship is approximately: `log(gamma_power) ∝ BOLD_activation`

This gives us a direct empirical mapping:
```python
def bold_to_gamma_power(bold_activation, scaling_factor=1.0):
    """Convert BOLD activation to estimated gamma power.
    
    Based on empirical EEG-fMRI coupling (Laufs et al. 2003, Logothetis 2003).
    Gamma power is the neural correlate most strongly coupled to BOLD.
    """
    # BOLD ∝ log(gamma_power) → gamma_power ∝ exp(BOLD)
    gamma_power = np.exp(scaling_factor * bold_activation)
    return gamma_power
```

**Confidence: MEDIUM** (established principles but parameter fitting is empirical)

---

## 5. Oscillatory Dynamics from Cortical Activation

### Recommended: Modified Wilson-Cowan Model

The [Wilson-Cowan model](https://en.wikipedia.org/wiki/Wilson%E2%80%93Cowan_model) is the most direct choice for generating theta-gamma PAC from activation levels. It has been explicitly [shown to generate PAC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4620035/) (Onslow et al., 2014; Chehelcheraghi et al., 2016).

**Core equations:**
```
τ_E × dE/dt = -E + S(w_EE × E - w_IE × I + P_ext)
τ_I × dI/dt = -I + S(w_EI × E - w_II × I)

S(x) = 1 / (1 + exp(-r(x - v0)))  # Sigmoid transfer function
```

Where:
- `E`, `I` = excitatory and inhibitory population firing rates
- `P_ext` = **external drive (← this is where TRIBE V2 activation enters)**
- `τ_E`, `τ_I` = time constants (control oscillation frequency)
- `w_XY` = connectivity weights (control coupling strength)

**PAC-generating parameterization** (from [Chehelcheraghi et al., 2016](https://link.springer.com/article/10.1007/s00422-016-0687-5)):
```python
# Parameters that produce theta-gamma PAC
params = {
    'tau_E': 0.0032,    # seconds (→ gamma ~50 Hz)
    'tau_I': 0.0052,    # seconds
    'w_EE': 2.4,        # E→E coupling
    'w_IE': 2.0,        # I→E coupling
    'w_EI': 2.1,        # E→I coupling
    'w_II': 0.0,        # I→I coupling
    'r': 4.0,           # sigmoid steepness
    'v0': 1.0,          # sigmoid threshold
    'S0': 1.0,          # sigmoid scale
    # External drive: P_ext = P0 + A_theta × cos(2π × f_theta × t)
    'P0': 0.6,          # tonic drive level (← TRIBE V2 activation)
    'A_theta': 0.1,     # theta modulation amplitude
    'f_theta': 4.0,     # theta frequency (Hz)
}
```

**Key relationship: TRIBE V2 activation → PAC**

The amplitude, frequency, and phase-locking of PAC are dependent on:
1. **Strength of P_ext** (tonic drive) → controls gamma power
2. **Amplitude of theta modulation** → controls PAC depth
3. **Connectivity weights** → control oscillation frequency

Higher TRIBE V2 activation → higher P_ext → stronger gamma oscillations → higher PAC when modulated by theta. This matches the empirical finding that BOLD correlates positively with gamma power.

### Implementation Strategy

```python
import numpy as np

class WilsonCowanPACGenerator:
    """Generate theta-gamma PAC from cortical activation levels.
    
    Uses Wilson-Cowan neural mass model driven by TRIBE V2 predictions.
    """
    
    def __init__(self, fs: float = 250.0, dt: float = 0.001):
        self.fs = fs
        self.dt = dt  # Integration timestep (1ms for stability)
        
        # Wilson-Cowan parameters for PAC
        self.tau_E = 0.0032
        self.tau_I = 0.0052
        self.w_EE = 2.4
        self.w_IE = 2.0
        self.w_EI = 2.1
        self.w_II = 0.0
        self.r = 4.0
        self.v0 = 1.0
        
    def sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-self.r * (x - self.v0)))
    
    def generate(self, activation_level: float, 
                 duration_s: float = 2.0,
                 theta_freq: float = 6.0,
                 theta_amp: float = 0.1) -> np.ndarray:
        """Generate EEG-like signal with PAC from activation level.
        
        Args:
            activation_level: TRIBE V2 activation (scales P_ext)
            duration_s: Duration in seconds
            theta_freq: Theta modulation frequency
            theta_amp: Theta modulation depth
            
        Returns:
            signal: EEG-like signal at self.fs sampling rate
        """
        n_steps = int(duration_s / self.dt)
        E = np.zeros(n_steps)
        I = np.zeros(n_steps)
        E[0] = 0.1
        I[0] = 0.05
        
        t = np.arange(n_steps) * self.dt
        # P_ext driven by activation + theta modulation
        P_ext = activation_level + theta_amp * np.cos(2 * np.pi * theta_freq * t)
        
        for i in range(1, n_steps):
            dE = (-E[i-1] + self.sigmoid(
                self.w_EE * E[i-1] - self.w_IE * I[i-1] + P_ext[i]
            )) / self.tau_E
            dI = (-I[i-1] + self.sigmoid(
                self.w_EI * E[i-1] - self.w_II * I[i-1]
            )) / self.tau_I
            
            E[i] = E[i-1] + self.dt * dE
            I[i] = I[i-1] + self.dt * dI
        
        # Downsample to EEG sampling rate
        downsample_factor = int(1.0 / (self.fs * self.dt))
        eeg_signal = E[::downsample_factor]
        
        return eeg_signal[:int(duration_s * self.fs)]
```

### Alternative: The Virtual Brain (TVB)

[TVB](https://thevirtualbrain.org/) (`pip install tvb-library`) provides a complete framework:
- Built-in [Jansen-Rit](https://docs.thevirtualbrain.org/_modules/tvb/simulator/models/jansen_rit.html) and Wilson-Cowan models
- EEG forward model with cortical surface projection
- Connectivity matrices from DTI tractography
- Generates EEG, MEG, and BOLD signals

TVB is more comprehensive but heavier. For our use case (generating PAC from activation levels), a standalone Wilson-Cowan implementation is simpler and more controllable.

### Alternative: Brian2

[Brian2](https://brian2.readthedocs.io/) (`pip install brian2`) is a spiking neural network simulator that can model gamma/theta oscillations at the network level. More biophysically detailed than Wilson-Cowan but much slower. Not recommended for real-time closed-loop applications.

**Recommendation:** Custom Wilson-Cowan implementation for speed and control. Use TVB for validation/comparison.

**Confidence: MEDIUM-HIGH** (mathematical models are well-established; parameter tuning for realistic PAC will need empirical fitting)

---

## 6. Alzheimer's Disease Modifications

### How AD Affects 40 Hz Stimulation Response

| AD Effect | Mechanism | How to Model |
|-----------|-----------|--------------|
| Reduced gamma power | GABAergic interneuron loss | Lower `w_IE` in Wilson-Cowan |
| Impaired ASSR | Disrupted thalamocortical circuit | Reduce P_ext coupling gain |
| Reduced theta-gamma PAC | Hippocampal tau pathology | Reduce theta modulation amplitude |
| Cortical atrophy | Neuronal loss, thinning | Scale activation by atrophy factor |
| Increased theta power | Cortical slowing | Increase theta drive, reduce alpha |
| Abnormal gamma PAC | Parahippocampal hyperexcitability | Modify PAC parameters regionally |

### Published AD Cortical Atrophy Maps

AD atrophy follows a well-characterized [spatial pattern](https://www.pnas.org/doi/10.1073/pnas.052587399):
1. **Early:** Entorhinal cortex, hippocampus (medial temporal)
2. **Moderate:** Temporal pole, inferior parietal, posterior cingulate, precuneus
3. **Late:** Frontal cortex, anterior cingulate, lateral temporal

For our frontal EEG channels, AD effects are:
- **Mild AD:** Minimal frontal atrophy; primarily temporal/parietal
- **Moderate AD:** Significant frontal atrophy; [increased frontal theta, decreased alpha](https://pmc.ncbi.nlm.nih.gov/articles/PMC11515355/)
- **Severe AD:** Widespread cortical thinning including frontal

### Modeling AD in the Bridge

```python
class ADModifier:
    """Modify TRIBE V2 predictions for Alzheimer's disease severity."""
    
    # Regional atrophy factors by Schaefer network (0 = no atrophy, 1 = complete)
    ATROPHY_PATTERNS = {
        'mild': {
            'Default': 0.15,       # Medial temporal, posterior cingulate
            'Limbic': 0.20,        # Temporal pole, orbitofrontal
            'Frontoparietal': 0.05, # Minimal frontal involvement
            'DorsalAttention': 0.08,
            'VentralAttention': 0.10,
            'Somatomotor': 0.03,
            'Visual': 0.02,
        },
        'moderate': {
            'Default': 0.35,
            'Limbic': 0.40,
            'Frontoparietal': 0.20,
            'DorsalAttention': 0.25,
            'VentralAttention': 0.25,
            'Somatomotor': 0.10,
            'Visual': 0.08,
        }
    }
    
    # PAC impairment factors
    PAC_IMPAIRMENT = {
        'mild': {'gamma_reduction': 0.20, 'pac_reduction': 0.25},
        'moderate': {'gamma_reduction': 0.40, 'pac_reduction': 0.50},
    }
```

### Key References
- [Multisensory gamma stimulation promotes glymphatic clearance of amyloid](https://www.nature.com/articles/s41586-024-07132-6) (Nature, 2024)
- [Safety, tolerability, and efficacy of 40 Hz in mild-moderate AD](https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2024.1343588/full) (Frontiers, 2024)
- [Audiovisual gamma stimulation for neurodegeneration](https://pmc.ncbi.nlm.nih.gov/articles/PMC10842797/) (Blanco-Duque, 2024)
- [Abnormal gamma PAC in parahippocampal cortex in AD](https://academic.oup.com/braincomms/article/6/2/fcae121/7642857) (Brain Communications, 2024)

**Key finding:** AD patients show paradoxically *increased* 40 Hz ASSR in some studies, possibly reflecting compensatory hyperexcitability rather than healthy entrainment. This means TRIBE V2 predictions for healthy subjects need AD-specific correction, not just attenuation.

**Confidence: MEDIUM** (atrophy patterns are well-established; specific parameter modifications for PAC impairment need experimental validation)

---

## 7. Validation Approach

### Metrics for Physiological Plausibility

| Metric | What It Tests | Target Range | Tool |
|--------|---------------|--------------|------|
| Spectral power distribution | Realistic 1/f spectrum | Slope -1 to -2 | `scipy.signal.welch` |
| Theta peak (4-8 Hz) | Theta oscillation present | SNR > 3 dB above background | `mne.time_frequency` |
| Gamma peak (38-42 Hz) | Gamma oscillation present | SNR > 2 dB above background | `mne.time_frequency` |
| PAC (MI) value range | Realistic coupling strength | 0.00001-0.001 (matches ds005048) | Our `PACComputer` |
| Topographic consistency | Frontal distribution matches known patterns | Correlation > 0.7 with ASSR templates | `mne.viz.plot_topomap` |
| Temporal autocorrelation | Realistic temporal dynamics | ACF decay similar to real EEG | `numpy.correlate` |
| Cross-channel correlation | Realistic spatial structure | Fp1-Fp2 high, Fp1-F8 moderate | `numpy.corrcoef` |

### Comparison Benchmarks

1. **Baseline (current simulator):** Our `EntrainmentSimulator` uses exponential approach with no spatial/spectral structure. Any bridge output should produce more realistic signals than this.

2. **Real data benchmark:** ds005048 provides ground truth EEG statistics:
   - PAC range: [0.000006, 0.000701], mean ~0.000044
   - 7 frontal channels, 250 Hz, 2s windows
   - Known stim/rest transitions with measurable dynamics

3. **Forward model validation:** Use [EEGSourceSim](https://pmc.ncbi.nlm.nih.gov/articles/PMC6815881/) framework for systematic validation of simulated scalp data using MRI-based forward models.

### Validation Protocol

```
Step 1: Generate TRIBE V2 predictions for known stimuli (40 Hz click trains)
Step 2: Run through fMRI→EEG bridge pipeline
Step 3: Compare output statistics with ds005048 real data:
  - Power spectral density shape
  - PAC magnitude distribution
  - Stim/rest transition dynamics
  - Cross-channel spatial patterns
Step 4: Statistical tests:
  - KS test on PAC distributions (bridge vs real)
  - Spectral similarity (coherence between bridge and real spectra)
  - Temporal dynamics correlation (stim onset → PAC rise time)
```

**Confidence: HIGH** (validation metrics are standard; real data provides clear benchmarks)

---

## 8. Complete Pipeline Architecture

### End-to-End Flow

```
40 Hz Audio Stimulus
        │
        ▼
┌─────────────────┐
│   TRIBE V2      │  Input: audio waveform
│   (Transformer) │  Output: (n_TR, 1000) parcel activations
└────────┬────────┘
         │  Schaefer 1000 parcels × n_timepoints
         ▼
┌─────────────────┐
│  ROI Selection  │  Select ~80 frontal/temporal parcels
│  + AD Modifier  │  Apply atrophy correction if AD mode
└────────┬────────┘
         │  ~80 parcel activations × n_timepoints
         ▼
┌─────────────────┐
│ HRF Deconvolution│  BOLD → neural activity envelopes
│ (Canonical HRF) │  Temporal resolution: ~1s
└────────┬────────┘
         │  ~80 neural activity envelopes × n_timepoints
         ▼
┌─────────────────┐
│ Neural Mass Model│  Wilson-Cowan with theta drive
│ (per parcel)    │  Input: activation envelope → P_ext
│                 │  Output: oscillatory signal (250 Hz)
└────────┬────────┘
         │  ~80 source signals × n_samples (250 Hz)
         ▼
┌─────────────────┐
│ Forward Model   │  Lead field matrix L: (7, ~80)
│ (MNE-Python)   │  V_scalp = L × J_source
└────────┬────────┘
         │  7 EEG channels × n_samples (250 Hz)
         ▼
┌─────────────────┐
│ PAC Computation │  Existing PACComputer module
│ (Tort MI)       │  Theta phase × gamma amplitude
└────────┬────────┘
         │  PAC value per window
         ▼
┌─────────────────┐
│ Closed-Loop     │  Existing controller pipeline
│ Controller      │  Compare with TCN predictions
└─────────────────┘
```

### Simplified Alternative (Recommended for MVP)

For a student research project, the full pipeline above may be over-engineered. A simplified version:

```
TRIBE V2 parcel activations
        │
        ▼
┌───────────────────┐
│ Frontal ROI       │  Average activations in frontal parcels
│ Aggregation       │  → 1 activation value per channel per TR
└────────┬──────────┘
         │  7 activation envelopes (1 per channel)
         ▼
┌───────────────────┐
│ Activation → PAC  │  Empirical mapping function:
│ Transfer Function │  PAC = f(activation, stim_context)
│                   │  Based on BOLD-gamma coupling literature
└────────┬──────────┘
         │  7 PAC estimates per TR
         ▼
┌───────────────────┐
│ Temporal Interp   │  Interpolate PAC to 1 Hz decision rate
│ + Noise Model     │  Add physiologically realistic noise
└────────┬──────────┘
         │  PAC timeseries at controller rate
         ▼
┌───────────────────┐
│ Existing Pipeline │  ClosedLoopController
│                   │  PersonalizationModule
└───────────────────┘
```

This approach replaces the neural mass model with a direct empirical transfer function, which is simpler but less biophysically grounded.

---

## 9. Implementation Recommendations

### Priority Order (for student research project)

| Priority | Component | Complexity | Value | Libraries |
|----------|-----------|------------|-------|-----------|
| 1 | TRIBE V2 inference wrapper | LOW | HIGH | PyTorch, tribev2 |
| 2 | Schaefer→frontal ROI mapping | LOW | HIGH | nilearn, MNE |
| 3 | BOLD→activation transfer function | MEDIUM | HIGH | scipy, numpy |
| 4 | Forward model (lead field) | MEDIUM | MEDIUM | MNE-Python |
| 5 | Wilson-Cowan PAC generator | MEDIUM | HIGH | numpy (custom) |
| 6 | AD atrophy modifier | LOW | MEDIUM | numpy (lookup tables) |
| 7 | Full TVB simulation | HIGH | LOW | tvb-library |

### Required Dependencies

```bash
# Core (already in project)
pip install numpy scipy torch

# New: neuroimaging
pip install mne nilearn

# New: TRIBE V2
pip install tribev2  # or clone from github.com/facebookresearch/tribev2

# Optional: validation
pip install tvb-library  # The Virtual Brain
pip install rsHRF         # HRF deconvolution
```

### Key Papers

| Paper | Year | Relevance |
|-------|------|-----------|
| TRIBE: TRImodal Brain Encoder (Meta FAIR) | 2025 | Source model architecture |
| Schaefer et al. — Local-Global Parcellation | 2018 | Atlas for ROI mapping |
| Tort et al. — Measuring PAC | 2010 | PAC computation method (already used) |
| Chehelcheraghi et al. — Neural mass model of PAC | 2016 | Wilson-Cowan PAC parameterization |
| Onslow et al. — PAC from detailed to NMM | 2014 | PAC generation theory |
| Friston — Nonlinear fMRI: Balloon model | 2000 | HRF deconvolution |
| Gramfort et al. — MNE software | 2013 | Forward model implementation |
| Sanz-Leon et al. — TVB simulator | 2013 | Whole-brain simulation |
| Logothetis — BOLD coupling to neural activity | 2003 | BOLD-gamma relationship |
| Iaccarino et al. — Gamma entrainment in AD | 2016 | 40 Hz stimulation in AD mice |
| Multisensory gamma → glymphatic clearance | 2024 | 40 Hz mechanism in AD |

---

## 10. Risks and Open Questions

### Technical Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| TRIBE V2 predictions may not capture 40 Hz-specific cortical responses | HIGH | Validate against known ASSR fMRI patterns; fall back to empirical mapping |
| Wilson-Cowan parameters may not generalize to all subjects | MEDIUM | Use parameter ranges from literature; personalize with real EEG data |
| Forward model assumptions (3-layer BEM) may oversimplify | LOW | Standard approach; validated against intracranial recordings |
| HRF deconvolution introduces temporal uncertainty | MEDIUM | Use canonical HRF; validate temporal dynamics against real transitions |
| Computational cost of per-parcel NMM simulation | MEDIUM | Run only ~80 frontal parcels; pre-compute lead field; batch processing |

### Open Questions

1. **Has TRIBE V2 been tested with 40 Hz click train stimuli?** The model was trained on naturalistic stimuli (movies, podcasts). Its accuracy for repetitive auditory stimulation is unknown.

2. **How should we handle the "average subject" limitation?** TRIBE V2 predicts group-average brain responses. Individual variation in cortical folding and EEG topography is not captured.

3. **What is the appropriate noise model?** Real EEG has 1/f noise, muscle artifacts, eye blinks, and volume conduction mixing. The bridge needs a realistic noise injection pipeline.

4. **Can we validate without simultaneous EEG-fMRI data?** Ideally we'd compare bridge outputs to actual simultaneous recordings. Without that, validation relies on matching statistical properties of real EEG.

5. **Should we use TRIBE V2's subcortical predictions?** The model also predicts 8,802 subcortical voxels. Thalamic predictions could inform theta rhythm generation (thalamo-cortical loops drive theta).

---

## 11. Feasibility Assessment

**Verdict: YES, feasible for a student research project, with caveats.**

The full biophysical pipeline (TRIBE V2 → HRF deconv → Wilson-Cowan NMM → forward model → PAC) is scientifically sound but complex. For CSEF, recommend the **simplified MVP approach**:

1. **Use TRIBE V2 as a "cortical activation oracle"** — provides spatially-resolved brain responses to stimuli
2. **Map to frontal ROIs** using Schaefer atlas + lead field sensitivity
3. **Convert activation → PAC** using empirical transfer function (not full NMM)
4. **Integrate with existing closed-loop controller** as an enhanced simulator

This preserves the scientific narrative (brain-encoding model → personalized stimulation) while keeping implementation tractable. The full NMM pipeline is a stretch goal.

**Timeline estimate:**
- MVP (empirical transfer function): 2-3 weeks
- Full pipeline (with NMM): 5-7 weeks
- Validation: 1-2 weeks on top
