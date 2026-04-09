# TRIBE V2 Architecture Deep Dive

**Project:** Closed-Loop 40Hz Entrainment — TRIBE V2 Integration Research
**Researched:** 2026-04-02
**Overall Confidence:** HIGH (source code + v1 paper + official docs)

---

## 1. Executive Summary

TRIBE V2 (TRImodal Brain Encoder v2) is Meta FAIR's foundation model for predicting fMRI brain responses to naturalistic stimuli. It processes video, audio, and text through frozen backbone encoders (V-JEPA2, Wav2Vec-BERT 2.0, LLaMA 3.2-3B), fuses them in a learned Transformer, and projects to ~20K cortical vertices on the fsaverage5 surface.

**Key numbers:**
- Output: `(n_timesteps, 20484)` cortical vertex predictions at ~1Hz (fMRI TR)
- Transformer: 8 layers, hidden dim 1152, low-rank head 2048
- Training: 451.6 hours fMRI from 25 subjects, 15 epochs, MSE loss
- Full model: ~4-5B params total (dominated by frozen backbones), ~50-100M trainable
- License: CC-BY-NC-4.0 (non-commercial)

**For our project:** The audio pathway through Wav2Vec-BERT → projector → Transformer produces rich neural-aligned representations that can serve as an in-silico model of auditory cortical processing for 40Hz entrainment stimuli.

---

## 2. Repository Structure

```
facebookresearch/tribev2/
├── tribev2/                    # Main package
│   ├── __init__.py             # Exports TribeModel only
│   ├── model.py                # FmriEncoder + FmriEncoderModel
│   ├── demo_utils.py           # TribeModel (inference API)
│   ├── main.py                 # TribeExperiment pipeline
│   ├── pl_module.py            # BrainModule (PyTorch Lightning)
│   ├── eventstransforms.py     # Stimulus event preprocessing
│   ├── utils.py                # ROI analysis, study management
│   ├── utils_fmri.py           # Surface projection, mesh handling
│   ├── grids/
│   │   ├── defaults.py         # Production hyperparameters
│   │   └── test_run.py         # Quick testing config
│   ├── plotting/               # PyVista brain visualization
│   └── studies/                # Dataset definitions
├── tribe_demo.ipynb            # Colab demo notebook
├── pyproject.toml              # Dependencies (Python >=3.11)
└── LICENSE                     # CC-BY-NC-4.0
```

**Public API surface:** Only `TribeModel` is exported. All inference goes through this class.

---

## 3. Complete Architecture

### 3.1 High-Level Pipeline

```
Raw Stimulus (video/audio/text)
        ↓
[Frozen Backbone Encoders]
  ├── V-JEPA2 ViT-G    → (B, L_v, D_v=1280, T)  video features
  ├── Wav2Vec-BERT 2.0  → (B, L_a, D_a=1024, T)  audio features
  └── LLaMA 3.2-3B      → (B, L_t, D_t=3072, T)  text features
        ↓
[Layer Aggregation] sum across sampled layers → (B, D_mod, T) per modality
        ↓
[Per-Modality Projectors] Linear+LayerNorm+GELU → (B, 384, T) each
        ↓
[Concatenation] → (B, 1152, T) = (B, hidden, T)
        ↓
[Combiner MLP] Linear+LayerNorm+GELU → (B, 1152, T)
        ↓
[Temporal Smoothing] Gaussian depthwise conv (kernel=9) (optional)
        ↓
[Transformer Encoder] 8 layers, 8 heads, positional + subject embeddings
        ↓
[Low-Rank Head] Linear 1152 → 2048
        ↓
[Subject Layers] subject-conditional projection 2048 → 20,484 vertices
        ↓
[Adaptive Avg Pool] → (B, 20484, n_output_timesteps)
        ↓
Output: predicted fMRI BOLD at ~1Hz on fsaverage5 cortex
```

### 3.2 Backbone Feature Extractors (Frozen)

All backbones are frozen during TRIBE training. Only intermediate layers are sampled.

#### Wav2Vec-BERT 2.0 (Audio)
- **Architecture:** Conformer-based, causal depthwise conv, mel-spectrogram input
- **Total layers:** 24 transformer layers
- **Hidden dimension:** 1024 per layer
- **Attention heads:** 16 per layer
- **Feed-forward dim:** 4096
- **Input:** Raw audio waveform → mel spectrogram
- **Native output rate:** 50 Hz
- **TRIBE resampling:** 50 Hz → 2 Hz (to match stimulus rate)
- **Layers sampled by TRIBE:** `[0.75, 1.0]` = layers 18 and 24 (2 layers)
- **Layer aggregation:** `sum` → single 1024-dim vector per 2Hz timestep
- **Source:** `facebook/w2v-bert-2.0` on HuggingFace

#### V-JEPA2 ViT-G (Video)
- **Architecture:** Vision Transformer Giant with 3D-RoPE
- **Parameters:** ~1B+
- **Hidden dimension:** 1280 per layer
- **Input:** 64 frames spanning 4 seconds, tubelets 2×16×16 (T×H×W)
- **Output:** Spatially averaged patch tokens → 1280-dim per timestep
- **Layers sampled by TRIBE:** `[0.75, 1.0]` (2 layers)
- **Layer aggregation:** `sum` → 1280-dim per 2Hz timestep
- **Clip duration:** 4 seconds (config: `clip_duration: 4`)
- **Note:** Spatial averaging discards retinotopic information

#### LLaMA 3.2-3B (Text)
- **Architecture:** Auto-regressive transformer, Grouped-Query Attention (GQA)
- **Parameters:** 3B
- **Hidden dimension:** 3072 (per layer output)
- **Total layers:** 28
- **Attention heads:** 24 (with 8 KV heads for GQA)
- **Context window:** 128K tokens
- **TRIBE processing:** Words from WhisperX transcription, prepend 1024 words context
- **Layers sampled by TRIBE:** `[0, 0.2, 0.4, 0.6, 0.8, 1.0]` (6 layers)
- **Layer aggregation:** `sum` → 3072-dim (but see note below)
- **Temporal alignment:** Word embeddings summed into 2 Hz time bins
- **Note:** Requires HuggingFace gated access for LLaMA weights

> **Dimension note from v1 paper:** The paper states text embeddings are 2048-dim. The discrepancy with 3072 may reflect different LLaMA configs or a hidden_size vs intermediate_size confusion. The actual dimension used by TRIBE's projector is whatever the backbone outputs. The projector compresses to 384 regardless.

### 3.3 FmriEncoder (Learned Component)

From `model.py` — the core trainable architecture:

```python
class FmriEncoder(BaseModelConfig):
    # Production values from grids/defaults.py:
    hidden: int = 1152              # Internal representation dimension
    encoder: TransformerEncoder     # 8 layers (depth=8)
    low_rank_head: int = 2048       # Bottleneck before vertex projection
    max_seq_len: int = 1024         # Max temporal positions
    dropout: float = 0.0            # (set via encoder subfields)
    modality_dropout: float = 0.3   # Random modality masking during training
    temporal_dropout: float = 0.0
    extractor_aggregation: "cat"    # Concatenate modality projections
    layer_aggregation: "cat"        # (overridden to sum in defaults)
    subject_layers: SubjectLayers   # Subject-conditional output projection
    temporal_smoothing: TemporalSmoothing  # Gaussian conv (kernel=9)
```

#### Per-Modality Projectors
Each modality gets its own `Mlp(norm_layer="layer", activation_layer="gelu")`:
- Input dim: raw feature dim after layer aggregation (1024 for audio, 1280 for video, 3072 for text)
- Output dim: `hidden // n_modalities` = 1152 // 3 = **384**
- Architecture: Linear → LayerNorm → GELU

#### Combiner
After concatenating 3 × 384 = 1152:
- `Mlp(norm_layer="layer", activation_layer="gelu")`
- Maps 1152 → 1152

#### Temporal Smoothing
```python
class TemporalSmoothing:
    kernel_size: int = 9
    sigma: float | None = None  # If set, uses fixed Gaussian; else learnable
```
Depthwise 1D convolution over the time axis, groups=dim (per-channel).

#### Transformer Encoder
- **Depth:** 8 layers
- **Heads:** 8 attention heads
- **Dim:** 1152
- **Context window:** 100 TRs (~149 seconds at TR=1.49s, or ~100s at TR=1.0s)
- **Positional embeddings:** Learnable (`time_pos_embed: nn.Parameter(1, max_seq_len, hidden)`)
- **Subject embeddings:** Optional learnable per-subject vectors
- **Implementation:** `neuraltrain.models.transformer.TransformerEncoder` (likely uses `x_transformers` given the dep)

#### Low-Rank Head
Linear projection: 1152 → 2048 (no bias). Reduces the effective rank before the large vertex projection.

#### Subject Layers (Output Head)
- `SubjectLayers` from `neuraltrain.models.common`
- Subject-conditional linear: 2048 → 20,484 vertices
- Enables per-subject brain geometry adaptation
- For inference with pretrained model: uses "average subject" mode

#### Output Pooling
`nn.AdaptiveAvgPool1d(n_output_timesteps)` compresses the temporal sequence to match fMRI TR count.

### 3.4 Forward Pass (Detailed)

From `FmriEncoderModel.forward()`:

```python
def forward(self, batch: SegmentData, pool_outputs: bool = True) -> torch.Tensor:
    # 1. Aggregate features from all modalities
    x = self.aggregate_features(batch)       # (B, T, 1152)

    # 2. Optional temporal smoothing (Gaussian depthwise conv)
    if hasattr(self, "temporal_smoothing"):
        x = self.temporal_smoothing(x.transpose(1, 2)).transpose(1, 2)

    # 3. Transformer forward (if not linear baseline)
    if not self.config.linear_baseline:
        x = self.transformer_forward(x, subject_id)  # (B, T, 1152)

    x = x.transpose(1, 2)                   # (B, 1152, T)

    # 4. Low-rank bottleneck
    if self.config.low_rank_head is not None:
        x = self.low_rank_head(x.transpose(1, 2)).transpose(1, 2)  # (B, 2048, T)

    # 5. Subject-conditional vertex projection
    x = self.predictor(x, subject_id)        # (B, 20484, T)

    # 6. Temporal pooling to match fMRI resolution
    if pool_outputs:
        out = self.pooler(x)                 # (B, 20484, T')

    return out
```

### 3.5 Hemodynamic Response Modeling

**TRIBE does NOT explicitly model the HRF.** Instead:
- Predictions are offset by **5 seconds in the past** to compensate for hemodynamic delay
- This is a fixed temporal shift, not a learned HRF convolution
- The Transformer's 100-second context window implicitly captures slow hemodynamic dynamics
- fMRI targets are the raw BOLD signal (z-scored per session per parcel/vertex)

---

## 4. Audio Processing Pathway (Critical for Our Integration)

This is the most relevant pathway for 40Hz auditory entrainment:

### 4.1 End-to-End Audio Flow

```
Raw audio waveform (16kHz)
    ↓
Wav2Vec-BERT 2.0 (frozen)
    ├── Mel spectrogram extraction
    ├── Conformer encoder (24 layers)
    └── Output: (seq_len, 1024) at 50Hz
    ↓
Resample 50Hz → 2Hz (temporal alignment with video/text)
    ↓
Select layers [0.75, 1.0] → layers 18 & 24
    ↓
Sum layers → (T, 1024) at 2Hz
    ↓
Audio Projector MLP: 1024 → 384 (with LayerNorm + GELU)
    → Output shape: (B, T, 384)
    ↓
Concatenate with video (384) + text (384) → (B, T, 1152)
    ↓
Combiner MLP → (B, T, 1152)
    ↓
Transformer Encoder (8 layers) → (B, T, 1152)
    ↓
Low-rank head → (B, T, 2048)
    ↓
Subject layers → (B, T, 20484)
    ↓
Pool → (B, n_fmri_timepoints, 20484)
```

### 4.2 Extractable Intermediate Representations

For our closed-loop system, we can extract activations at multiple points:

| Extraction Point | Shape per timestep | Temporal Res | What It Represents |
|---|---|---|---|
| Wav2Vec-BERT raw output | (1024,) | 50 Hz | Low-level audio features |
| Wav2Vec-BERT resampled | (1024,) | 2 Hz | Temporally aligned audio features |
| Audio projector output | (384,) | 2 Hz | Compressed audio representation |
| Post-concatenation | (1152,) | 2 Hz | Multimodal fused representation |
| Post-transformer (layer N) | (1152,) | 2 Hz | Contextual neural state prediction |
| Post-low-rank head | (2048,) | 2 Hz | Pre-cortical latent representation |
| Cortical prediction | (20484,) | ~1 Hz | Predicted BOLD at every vertex |
| ROI extraction | (N_roi,) | ~1 Hz | Mean prediction per brain region |

### 4.3 Audio-Only Inference

TRIBE supports **modality dropout** (p=0.3 during training), meaning it was trained to handle missing modalities. For audio-only inference:
- Pass zero tensors for video and text features
- The model has learned to compensate (modality dropout regularization)
- Prediction quality degrades but remains informative for auditory cortex regions

### 4.4 Temporal Resolution Considerations

- **Native Wav2Vec-BERT:** 50 Hz (20ms frames) — much higher than our EEG (250 Hz / 2s windows)
- **TRIBE internal:** 2 Hz (500ms bins) — still faster than fMRI TR
- **TRIBE output:** ~1 Hz (matched to fMRI TR ≈ 1-1.5s)
- **Our EEG windows:** 0.5 Hz (2-second windows)

The 2 Hz internal rate is compatible with our 2-second EEG window rate.

---

## 5. ROI Extraction and Brain Region Analysis

### 5.1 Available ROI Tools

From `utils.py`:

```python
# HCP parcellation on fsaverage5
get_hcp_labels()           # Returns HCP atlas labels
get_hcp_vertex_labels()    # Maps vertex index → anatomical label
get_hcp_roi_indices(rois)  # Get vertex indices for named ROIs (wildcard support)
summarize_by_roi(data)     # Mean prediction per region
get_topk_rois(data)        # Highest-activation regions per hemisphere
```

### 5.2 Relevant Brain Regions for 40Hz Entrainment

Using HCP parcellation, we can extract predictions for:

| Region | HCP Label Pattern | Relevance |
|---|---|---|
| Primary auditory cortex | `*A1*`, `*auditory*` | Direct target of 40Hz auditory stimulation |
| Superior temporal gyrus | `*STG*`, `*STS*` | Auditory processing |
| Prefrontal cortex | `*PFC*`, `*frontal*` | Cognitive control, entrainment modulation |
| Hippocampus | (subcortical, 8802 voxels) | Memory consolidation, gamma entrainment target |
| Temporal pole | `*temporal*pole*` | Semantic processing of auditory stimuli |

### 5.3 Surface Projection Utilities

From `utils_fmri.py`:
- `TribeSurfaceProjector`: Projects volumetric fMRI to cortical surfaces
- Supports fsaverage through fsaverage6 meshes
- Uses `nilearn.surface.vol_to_surf` for projection
- Configurable depth sampling between pial and white matter surfaces

---

## 6. Inference Pipeline (TribeModel API)

### 6.1 Loading the Model

```python
from tribev2 import TribeModel

model = TribeModel.from_pretrained(
    "facebook/tribev2",        # HuggingFace repo ID
    cache_folder="./cache",    # Local cache for weights
)
# Internally:
#   1. Downloads config YAML + checkpoint from HF Hub
#   2. Strips 'model.' prefix from state dict keys
#   3. Loads to CPU, then moves to specified device
#   4. Sets eval mode
```

### 6.2 Preparing Events

```python
# From video (extracts audio + transcribes text automatically)
df = model.get_events_dataframe(video_path="path/to/video.mp4")

# The pipeline applies:
# 1. ExtractAudioFromVideo()
# 2. ChunkEvents() - segments to 30-60 second clips
# 3. ExtractWordsFromAudio() - WhisperX transcription
# 4. AddText(), AddSentenceToWords(), AddContextToWords()
# 5. RemoveMissing()
```

### 6.3 Running Inference

```python
preds, segments = model.predict(events=df)
# preds shape: (n_timesteps, 20484) — numpy array
# segments: list of segment metadata

# Internally:
# 1. Creates segments at TR intervals
# 2. Runs FmriEncoderModel.forward()
# 3. Applies rearrange('b d t -> (b t) d')
# 4. Returns predictions on fsaverage5 surface
```

### 6.4 Custom Audio-Only Inference (For Our Use Case)

For 40Hz entrainment audio stimuli, we would need to:

```python
# 1. Extract Wav2Vec-BERT features directly
from transformers import Wav2Vec2BertModel, AutoFeatureExtractor

wav2vec = Wav2Vec2BertModel.from_pretrained("facebook/w2v-bert-2.0")
processor = AutoFeatureExtractor.from_pretrained("facebook/w2v-bert-2.0")

# 2. Process 40Hz click train audio
inputs = processor(audio_array, sampling_rate=16000, return_tensors="pt")
outputs = wav2vec(**inputs, output_hidden_states=True)

# 3. Extract layers 18 and 24 (indices ~18, 23 of 24 layers)
layer_18 = outputs.hidden_states[18]  # (1, seq_len, 1024)
layer_24 = outputs.hidden_states[23]  # (1, seq_len, 1024)
audio_features = layer_18 + layer_24  # sum aggregation

# 4. Resample from 50Hz to 2Hz
# (average pool every 25 frames)

# 5. Feed through TRIBE's audio projector + transformer
# (requires loading TRIBE checkpoint and extracting submodules)
```

---

## 7. Training Details

### 7.1 Production Configuration (from `grids/defaults.py`)

| Parameter | Value |
|---|---|
| Hidden dim | 1152 |
| Encoder depth | 8 layers |
| Low-rank head | 2048 |
| Learning rate | 1e-4 (Adam) |
| Scheduler | OneCycleLR, 10% warmup |
| Batch size | 8 |
| Epochs | 15 |
| Loss | MSELoss (no reduction) |
| Seed | 33 |
| Subject dropout | 0.1 |
| Modality dropout | 0.3 |
| Metric | Pearson correlation (per-sample + grouped by subject) |

### 7.2 Training Data

| Study | Content | Subjects | Hours |
|---|---|---|---|
| Study 1 | Movies | ~6 subjects | ~100+ hrs |
| Study 2 | Podcasts | ~6 subjects | ~100+ hrs |
| Study 3 | Silent videos | ~6 subjects | ~100+ hrs |
| Study 4 | Mixed | ~7 subjects | ~100+ hrs |
| **Total** | **Naturalistic** | **25 subjects** | **451.6 hrs** |

**Extended dataset claim:** Meta also references "720 subjects" and "1000+ hours" — this likely includes evaluation/zero-shot subjects beyond the core training set.

### 7.3 Infrastructure

- Training: 1 GPU per node (V100/A100 implied), 128GB system memory
- Feature extraction: Separate SLURM jobs with 20 CPUs
- Training timeout: 72 hours
- Multi-GPU: FSDP strategy for distributed training

---

## 8. Hardware Requirements and Device Compatibility

### 8.1 Estimated Memory Footprint

| Component | Parameters | FP16 Size |
|---|---|---|
| LLaMA 3.2-3B (frozen) | 3.0B | ~6 GB |
| V-JEPA2 ViT-G (frozen) | ~1.1B | ~2.2 GB |
| Wav2Vec-BERT 2.0 (frozen) | ~600M | ~1.2 GB |
| FmriEncoder (trainable) | ~50-100M est. | ~0.1-0.2 GB |
| **Total (all modalities)** | **~4.7B** | **~9.6 GB** |
| **Audio-only subset** | **~650M** | **~1.4 GB** |

### 8.2 Apple Silicon / MPS Compatibility

**Assessment: LIKELY COMPATIBLE for audio-only inference, UNCERTAIN for full model.**

- Wav2Vec-BERT 2.0: Standard transformer ops, should work on MPS
- FmriEncoder: Standard PyTorch (nn.Linear, nn.Conv1d, transformer) — MPS compatible
- LLaMA 3.2-3B: Known to work on MPS (Apple has optimized this)
- V-JEPA2 ViT-G: May have MPS-incompatible ops (3D convolutions, custom attention) — needs testing
- `x_transformers` dependency: May use ops not yet on MPS — needs verification

**For our project's Apple Silicon (M-series) system:**
- Audio-only pipeline (~1.4 GB): Should fit comfortably in unified memory
- Full model (~9.6 GB): Fits on M1 Pro/Max/Ultra (16-64 GB unified memory)
- Feature extraction can be batched to manage memory

### 8.3 Inference Speed Estimate

- **Feature extraction** dominates inference time (backbone forward passes)
- **Wav2Vec-BERT:** ~100ms per 60-second audio chunk on V100 (estimated)
- **FmriEncoder forward:** <10ms per segment (small model)
- **For real-time 40Hz audio:** We extract features offline or use a sliding window
- **The 2Hz internal rate** means we need 1 forward pass per 500ms of audio

---

## 9. Key Differences: TRIBE V1 → V2

| Aspect | V1 | V2 |
|---|---|---|
| Spatial resolution | 1,000 parcels (Schaefer) | 20,484 vertices (fsaverage5) |
| Hidden dimension | 1,024 | 1,152 |
| Output projection | Direct linear to parcels | Low-rank (2048) + subject layers |
| Training data | 4 subjects, 80+ hrs each (NeuroMod) | 25 subjects, 451.6 hrs (4 studies) |
| Zero-shot capability | No (per-subject only) | Yes (average subject + transfer) |
| Subcortical support | No | Yes (8,802 subcortical voxels) |
| Resolution improvement | Baseline | 70× over v1 |
| Layer aggregation default | cat | sum (per defaults.py) |
| Temporal smoothing | Not mentioned | Gaussian depthwise conv (kernel=9) |

---

## 10. Integration Points for Closed-Loop 40Hz Entrainment

### 10.1 What We Can Extract

1. **Auditory cortex predictions:** ROI-specific fMRI predictions for A1, STG, STS regions during 40Hz stimulation audio
2. **Transformer hidden states:** 1152-dim contextual representations capturing temporal dynamics of auditory processing
3. **Pre-cortical latent space:** 2048-dim representations from the low-rank head, encoding predicted brain state
4. **Audio projector features:** 384-dim compressed audio representations aligned with brain processing

### 10.2 Potential Architecture for EEG-fMRI Bridge

```
40Hz Audio Stimulus → Wav2Vec-BERT → TRIBE Audio Projector
                                          ↓
                    TRIBE Transformer Hidden States (1152-dim)
                                          ↓
                    [Learned Bridge Network] ← EEG features (from our TCN)
                                          ↓
                    Enhanced PAC/Entrainment Prediction
```

### 10.3 Concrete Integration Strategy

**Option A: TRIBE as Feature Extractor (Simplest)**
- Use TRIBE's audio pathway to generate predicted cortical responses to our 40Hz stimuli
- Extract ROI-level predictions for auditory + frontal regions
- Use as additional input features to our TCN temporal model
- Pro: No retraining of TRIBE needed
- Con: 2Hz temporal resolution may miss fast PAC dynamics

**Option B: TRIBE Latent Space Alignment (Medium Complexity)**
- Extract TRIBE's 1152-dim transformer representations for our audio stimuli
- Train a lightweight bridge network to map between TRIBE latents and EEG-derived features
- Use the bridge for cross-modal data augmentation
- Pro: Richer representations than ROI averages
- Con: Requires training the bridge

**Option C: TRIBE as Brain Digital Twin (Most Ambitious)**
- Use full TRIBE model to simulate brain response to different stimulation parameters
- Optimize stimulation timing/frequency in-silico before applying to real EEG
- Generate synthetic training data for our PAC predictor
- Pro: Could dramatically expand effective training data
- Con: fMRI temporal resolution (1Hz) vs. EEG gamma dynamics (40Hz) mismatch

### 10.4 Critical Limitations

1. **Temporal resolution gap:** TRIBE operates at 1-2 Hz; our EEG PAC dynamics are at 40 Hz gamma / 4-8 Hz theta. The model cannot capture fast oscillatory dynamics directly.
2. **Modality gap:** TRIBE predicts fMRI BOLD (hemodynamic, ~5s delay); our system measures EEG (electromagnetic, ~ms resolution). The relationship between BOLD and EEG gamma power is indirect.
3. **Spatial resolution vs. temporal resolution tradeoff:** TRIBE excels at spatial specificity (20K vertices) but has poor temporal specificity. Our EEG has the opposite profile.
4. **Non-commercial license:** CC-BY-NC-4.0 limits commercial deployment but is fine for research/CSEF.

---

## 11. Dependencies

### Core Requirements (from `pyproject.toml`)

```
Python >= 3.11
torch >= 2.5.1, < 2.7
numpy == 2.2.6
torchvision >= 0.20, < 0.22
x_transformers == 1.27.20
neuralset == 0.0.2          # Meta's neural dataset library
neuraltrain == 0.0.2        # Meta's neural training library
transformers                # HuggingFace (for backbone loading)
huggingface_hub
moviepy >= 2.2.1
spacy, langdetect, soundfile
einops, julius
pyyaml
```

### Optional
```
# Plotting: nibabel, matplotlib, nilearn, pyvista, scipy
# Training: lightning, wandb, torchmetrics
```

### Potential Conflicts with Our Project
- Our project uses Python 3.13.3; TRIBE requires >= 3.11 (compatible)
- numpy == 2.2.6 is a pinned version — may conflict with our existing numpy
- torch >= 2.5.1 — need to check against our installed version
- `neuralset` and `neuraltrain` are Meta-internal packages, pip-installable from the tribev2 package

---

## 12. Source Confidence Assessment

| Claim | Source | Confidence |
|---|---|---|
| FmriEncoder architecture (hidden=1152, depth=8) | Source code `model.py` + `defaults.py` | HIGH |
| Wav2Vec-BERT layers/dims | HuggingFace docs + v1 paper | HIGH |
| V-JEPA2 ViT-G architecture | HuggingFace docs + Meta blog | HIGH |
| LLaMA 3.2-3B dims | HuggingFace model card | HIGH |
| 5-second hemodynamic offset | Multiple sources + v1 paper | HIGH |
| Training data (451.6 hrs, 25 subjects) | WebSearch (multiple sources) | MEDIUM |
| Memory footprint estimates | Calculated from parameter counts | MEDIUM |
| MPS compatibility | Inferred from standard PyTorch ops | LOW |
| Inference speed | Estimated, not benchmarked | LOW |
| Audio-only mode quality | Inferred from modality dropout training | MEDIUM |

---

## 13. Open Questions

1. **What are the exact `neuralset`/`neuraltrain` internal APIs?** These Meta packages are not well-documented externally. The `SegmentData` class, `SubjectLayers`, and `TransformerEncoder` implementations need further investigation.
2. **Can we extract per-layer transformer activations from the FmriEncoder?** The code doesn't expose intermediate layer hooks directly — we'd need to modify the forward pass or use PyTorch hooks.
3. **How does the "average subject" mode work in the pretrained checkpoint?** For inference without a specific subject ID, how are subject layers handled?
4. **What is the actual parameter count of the trained FmriEncoder?** The subject layers alone are 2048 × 20484 = ~42M parameters per subject. With average subject mode, this is a single set of weights.
5. **Can Wav2Vec-BERT features for 40Hz click trains be meaningful?** The model was trained on natural audio (speech, music, environmental sounds). Periodic 40Hz click trains are highly non-naturalistic — the features may not transfer well to auditory cortex predictions for entrainment-specific stimuli.

---

## References

- [TRIBE V2 GitHub Repository](https://github.com/facebookresearch/tribev2)
- [TRIBE V2 HuggingFace Model](https://huggingface.co/facebook/tribev2)
- [Meta AI Blog: Introducing TRIBE V2](https://ai.meta.com/blog/tribe-v2-brain-predictive-foundation-model/)
- [Research Paper: A foundation model of vision, audition, and language for in-silico neuroscience](https://ai.meta.com/research/publications/a-foundation-model-of-vision-audition-and-language-for-in-silico-neuroscience/)
- [TRIBE V1 Paper (ArXiv)](https://arxiv.org/html/2507.22229v1) — Architecture basis for V2
- [Wav2Vec2-BERT Documentation](https://huggingface.co/docs/transformers/en/model_doc/wav2vec2-bert)
- [V-JEPA2 Documentation](https://huggingface.co/docs/transformers/model_doc/vjepa2)
- [Neuroscience News Coverage](https://neurosciencenews.com/meta-tribe-ai-brain-decoding-30398/)
- [MarkTechPost Technical Summary](https://www.marktechpost.com/2026/03/26/meta-releases-tribe-v2-a-brain-encoding-model-that-predicts-fmri-responses-across-video-audio-and-text-stimuli/)
