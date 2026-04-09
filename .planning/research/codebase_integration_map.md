# Codebase Integration Map for TRIBE V2

**Analysis Date:** 2026-04-02
**Purpose:** Map all integration points where Meta's TRIBE V2 brain foundation model can be injected into the closed-loop 40Hz gamma entrainment system.

---

## 1. Simulator Architecture (Primary Integration Target)

### 1.1 EntrainmentSimulator (`src/simulator.py:45-181`)

**Current brain model:** Simple exponential approach.

```python
# Line 128: Core dynamics equation
pac_new = self.pac + tau * (target - self.pac)
```

**Parameters:**
| Parameter | Default | Role |
|-----------|---------|------|
| `tau_rise` | 0.15 | PAC increase rate during stimulation (~6s time constant) |
| `tau_decay` | 0.10 | PAC decrease rate during rest (~10s time constant) |
| `pac_max` | 0.3 | Maximum achievable PAC (normalized) |
| `pac_min` | 0.05 | Minimum PAC baseline (normalized) |
| `noise_std` | 0.02 | Gaussian noise standard deviation |
| `initial_pac` | pac_min | Starting PAC value |

**Interface — `step()` method (line 102-143):**
```python
def step(self, action: int) -> float:
    # Input: action (0=REST, 1=STIMULATE)
    # Output: float — updated PAC value
    # Side effects: updates self.pac, self.pac_history, self.action_history
```

**TRIBE V2 Integration Hook:** Replace the exponential approach equation at line 128 with a TRIBE V2-driven brain response. The `step()` interface (action in, PAC out) is the primary contract that must be preserved. Any TRIBE V2-based simulator must:
1. Accept a binary action (REST/STIMULATE)
2. Return a scalar PAC value in [pac_min, pac_max]
3. Maintain `pac_history` and `action_history` lists
4. Support `reset()` and `get_history()` methods

**Additional state methods to preserve:**
- `reset(initial_pac)` — line 145-156
- `get_state()` → dict — line 158-164
- `get_history()` → dict with `pac`, `action`, `pac_mean`, `pac_std`, `stimulation_time` — line 166-174

### 1.2 FatigueAwareSimulator (`src/simulator.py:183-307`)

**Extends EntrainmentSimulator with habituation dynamics:**

```python
# Line 258-263: Fatigue modulates rise effectiveness
self.fatigue += self.fatigue_rate * (self.max_fatigue - self.fatigue)
effectiveness = 1.0 - self.fatigue
effective_tau = self.tau_rise * effectiveness
target = self.pac_max
pac_new = self.pac + effective_tau * (target - self.pac)
```

**Additional fatigue parameters:**
| Parameter | Default | Role |
|-----------|---------|------|
| `fatigue_rate` | 0.008 | Fatigue accumulation rate during stimulation |
| `recovery_rate` | 0.03 | Fatigue recovery rate during rest |
| `max_fatigue` | 0.7 | Maximum fatigue level (caps effectiveness reduction) |

**Fatigue state:** `self.fatigue` (0.0 to max_fatigue), tracked in `self.fatigue_history`.

**TRIBE V2 Integration Hook:** TRIBE V2 could model habituation biologically rather than with exponential approximation. The fatigue dynamics (lines 256-269) model synaptic fatigue from continuous 40Hz stimulation — TRIBE V2's neural network representations could provide biologically-grounded alternatives.

### 1.3 Parameter Extraction (`src/simulator.py:310-367`)

```python
def extract_tau_parameters_from_data(pac_values, actions, fs, pac_max, pac_min) -> Dict[str, float]:
```

Fits tau parameters empirically from observed PAC transitions. Returns `tau_rise`, `tau_decay`, plus transition counts. Could be extended to calibrate TRIBE V2 parameters from real EEG data.

### 1.4 How Simulations Are Orchestrated

**`scripts/pipeline/run_closed_loop_demo.py`** is the top-level demo script.

**Simulation runner (`run_trial`, lines 190-243):**
```python
def run_trial(method, sim, duration_sec=360, seed=None) -> Dict:
    sim.reset()
    method.reset()
    for _ in range(duration_sec):  # 1 Hz decision rate
        pac = sim.pac                # Read current state
        action = method.step(pac)    # Controller decides
        sim.step(action)             # Simulator advances
```

**Key: The simulator is pluggable.** The demo creates simulator instances via factory lambdas:
```python
# Line 402-405: No-fatigue scenario
sim_factory=lambda: EntrainmentSimulator(tau_rise=0.15, ...)

# Line 417-420: Fatigue scenario
sim_factory=lambda: FatigueAwareSimulator(tau_rise=0.15, ..., fatigue_rate=0.008, ...)
```

**TRIBE V2 Integration Point:** Add a third scenario with a `TribeV2Simulator` factory:
```python
sim_factory=lambda: TribeV2Simulator(tribe_model=..., eeg_bridge=...)
```

---

## 2. Controller Architecture

### 2.1 ClosedLoopController (`src/controller.py:49-291`)

**EEGNet-based reactive controller.**

**Constructor (lines 73-131):**
- Loads EEGNet model from checkpoint
- Loads PAC normalization stats (pac_mean, pac_std)
- Creates PersonalizationModule(window_size=30, min_samples=10)
- State: current_state (STIMULATE/REST), time_in_state, hold_samples

**`step()` method (lines 133-189):**
```python
def step(self, eeg_window: np.ndarray) -> Tuple[StimState, float, Optional[float]]:
    # Input: eeg_window shape (7, 500) or (1, 7, 500)
    # Pipeline:
    #   1. Reshape to (1, 1, 7, 500) tensor
    #   2. EEGNet inference → z-normalized PAC
    #   3. Denormalize: pac_pred = pac_z * pac_std + pac_mean
    #   4. Compute z-score BEFORE updating baseline
    #   5. Update personalization baseline
    #   6. _make_decision(z_score)
    # Output: (action, pac_pred, z_score)
```

**Decision logic (`_make_decision`, lines 191-229):**
- z < -0.5 → STIMULATE
- z > +0.5 → REST
- -0.5 ≤ z ≤ +0.5 → MAINTAIN current state
- Hysteresis: only transition if time_in_state >= hold_samples (default 5)

**TRIBE V2 Integration Hook:** The controller uses predicted PAC to make decisions. TRIBE V2 features could augment the PAC prediction (via EEGNet or TCN) or provide additional brain-state features for the decision logic.

### 2.2 PredictiveLookAheadController (`src/controller.py:293-498`)

**TCN-based proactive controller.** Uses `RealtimePACForecaster` for future PAC predictions.

**`step()` method (lines 355-418):**
```python
def step(self, spectral_features, pac_current, stim_state,
         time_since_switch_sec, stim_frac_recent,
         cycle_phase_sin, cycle_phase_cos):
    # 1. Compute z-score, update personalization
    # 2. Get TCN prediction via self.forecaster.step(...)
    # 3. _make_decision(z_score, prediction)
    # Returns: (action, pac_current, prediction_dict_or_None)
```

**Decision logic (`_make_decision`, lines 420-468):**
- Priority 1: TCN prediction → delta_pac < -0.3 → STIMULATE; > +0.3 → REST
- Priority 2: z-score fallback (same thresholds as reactive)
- Hysteresis: same hold_time logic

**TRIBE V2 Integration Hook:** The `spectral_features` input (61-dim) could be augmented with TRIBE V2 brain-state embeddings. The `forecaster.step()` interface accepts explicit features — adding new feature dimensions requires changes to the TCN input projection layer and the scaler.

### 2.3 PersonalizationModule (`src/personalization.py:36-156`)

**Rolling baseline z-score computation.**

- `__init__(window_size=30, min_samples=10)` — circular deque buffer
- `update(pac_value)` — appends to buffer
- `compute_zscore(pac_value)` → Optional[float] — `(pac - mean) / (std + 1e-8)`
- `get_baseline_stats()` → (mean, std) with caching
- `reset()`, `is_ready()`, `get_buffer_size()`

**Also: `MultiChannelPersonalization` (lines 158-241)** — independent baselines per channel.

**TRIBE V2 Integration Hook:** Personalization currently operates on scalar PAC. Could be extended to track TRIBE V2-derived brain state vectors for richer subject adaptation.

---

## 3. PAC Computation Pipeline

### 3.1 PACComputer (`src/pac_computation.py:29-212`)

**Implements Tort et al. (2010) Modulation Index.**

**Frequency bands (from `config.yaml:74-83`):**
- Theta phase: 4.0–8.0 Hz
- Gamma amplitude: 38.0–42.0 Hz
- Phase bins: 18 (20° per bin)
- Filter order: 4 (Butterworth)

**Core computation chain:**
1. `bandpass_filter(signal, band)` — Butterworth filtfilt (lines 75-89)
2. `extract_phase_amplitude(signal, phase_band, amp_band)` — Hilbert transform → phase (angle), amplitude (magnitude) (lines 91-118)
3. `compute_modulation_index(phase, amplitude)` — KL divergence from uniform, normalized by log(n_bins) (lines 120-158)

**Key formula (line 153):**
```python
kl_div = np.sum(mean_amp_norm * np.log((mean_amp_norm + 1e-10) / uniform))
mi = kl_div / np.log(self.n_bins)
```

**Multi-channel support:**
- `compute_pac_multichannel(signals)` — per-channel PAC (lines 182-198)
- `compute_pac_average(signals)` — mean across channels (lines 200-212)

**What TRIBE V2 bridge must produce:** A scalar PAC value (Modulation Index) in the range [0.000006, 0.000701] (raw dataset range, mean ~0.000044) — or the normalized equivalent. The PAC value is the core currency of the entire system.

### 3.2 EEGPreprocessor (`src/preprocessing.py:30-336`)

**Signal conditioning pipeline:**
1. Bandpass: 0.5–80 Hz, 4th-order Butterworth, zero-phase (filtfilt)
2. Notch: 50 Hz, Q=30
3. Artifact rejection: ±100 µV threshold → zeroed samples
4. Common average reference (CAR)
5. Quality assessment: SNR estimation, bad channel detection

**TRIBE V2 Relevance:** TRIBE V2 operates on fMRI data, not EEG. The bridge module would need to map between fMRI activations (TR-level, ~1-2s resolution) and EEG-derived features (250 Hz, window-level). The preprocessing pipeline itself wouldn't change, but the bridge needs to understand what preprocessing has been applied to properly align modalities.

---

## 4. TCN Prediction Pipeline

### 4.1 Feature Composition (73 features total)

From `temporal_multiscale/build_multiscale_dataset.py`:

**61 spectral features** (loaded from `{split}_spectral_cache.npy`):
- Pre-computed spectral features from EEG windows
- Index: `spectral_00` through `spectral_60`

**7 PAC-derived features** (`_pac_multiscale_features`, lines 140-163):
| Feature | Description |
|---------|-------------|
| `pac_current` | Current PAC value |
| `pac_ma2` | Causal moving average, window=2 |
| `pac_ma4` | Causal moving average, window=4 |
| `pac_ma8` | Causal moving average, window=8 |
| `pac_ma16` | Causal moving average, window=16 |
| `pac_diff1` | PAC[t] - PAC[t-1] |
| `pac_diff4` | PAC[t] - PAC[t-4] |

**5 stimulation context features** (`_stim_context_from_events`, lines 81-137):
| Feature | Description |
|---------|-------------|
| `stim_state` | Current stimulation state (0=rest, 1=stim) |
| `time_since_switch_60s` | Time since last state switch, normalized to [0,1] by /60 |
| `stim_frac_20s` | Fraction of stimulation in last 20 seconds |
| `cycle_phase_sin` | sin(2π × (t mod 60) / 60) — protocol phase |
| `cycle_phase_cos` | cos(2π × (t mod 60) / 60) — protocol phase |

**Feature assembly order (line 223):**
```python
step_feat = np.concatenate([subj_spec, pac_feats, ctx], axis=1)
# shape: (n_windows, 73) = (61 spectral) + (7 PAC) + (5 stim context)
```

**TRIBE V2 Integration Hook:** TRIBE V2 embeddings could be concatenated as a 4th feature group. This would change `n_features` in `ModelConfig` and require the `in_proj` layer in the TCN to accept the expanded dimension. The scaler (`_normalize_with_train_stats`) would also need to be refit.

### 4.2 MultiscaleCausalTCN (`temporal_multiscale/multiscale_tcn.py:103-182`)

**Architecture (~31K params):**
```
Input: (B, T, F)  where T=lookback=20, F=73 features
  → in_proj: Linear(73, 64) + LayerNorm + SiLU
  → TCN: 4x CausalDSConvBlock(64, kernel=3, dilation=[1,2,4,8])
  → AttentionPool1D(64) → (B, 64)
  → future_head: Linear(64,64) + SiLU + Dropout + Linear(64,1) → (B,)
  → delta_head:  Linear(64,64) + SiLU + Dropout + Linear(64,1) → (B,)
```

**Key components:**
- `CausalDSConvBlock` (lines 20-58): Causal depthwise-separable conv + GroupNorm + SiLU + residual. Double-SiLU pattern (noted in comments as trained this way).
- `AttentionPool1D` (lines 61-73): Conv1d(C,1) → softmax weights → weighted sum over time.
- `LastStepPool` (lines 76-87): Alternative — just take last timestep.
- `ModelConfig` dataclass (lines 89-101): n_features, hidden=64, kernel_size=3, dilations=[1,2,4,8], dropout=0.1, pool_type="attention".

**Dual-head output:**
```python
return {"future": future, "delta": delta}
# future: predicted absolute PAC at t+horizon
# delta: predicted PAC change (future - current)
```

**Fine-tuning support:**
- `freeze_backbone()` (lines 165-173): Freeze all except regression heads.
- `unfreeze_all()` (lines 175-178): Reverses freeze.

**TRIBE V2 Integration Hook:** To add TRIBE V2 features:
1. Increase `ModelConfig.n_features` from 73 to 73+N (where N is TRIBE V2 embedding dim)
2. The `in_proj` layer (line 119) automatically adjusts: `nn.Linear(n_features, hidden)`
3. Must retrain from scratch or use `freeze_backbone()` + expand in_proj

### 4.3 RealtimePACForecaster (`temporal_multiscale/realtime_inference.py:20-163`)

**Rolling-buffer wrapper for online inference.**

**Constructor (lines 33-64):**
- Loads TCN checkpoint (model + config + metadata)
- Loads scalers (feature_mean, feature_std, y_future_mean/std, y_delta_mean/std)
- Creates rolling `seq_buffer` (deque, maxlen=lookback) and `pac_buffer`

**Feature assembly (`_build_step_feature`, lines 85-117):**
```python
# Expected: 61 spectral + 7 PAC-derived + 5 stim context = 73
x = np.concatenate([spectral_features, pac_feats, ctx])
x = (x - self.feature_mean) / (self.feature_std + 1e-8)
```

**`step()` method (lines 119-163):**
```python
def step(self, spectral_features, pac_current, stim_state,
         time_since_switch_sec, stim_frac_recent,
         cycle_phase_sin=0.0, cycle_phase_cos=1.0) -> Optional[Dict[str, float]]:
    # Returns None until lookback is filled
    # Then returns: {
    #   "future_pac": float,
    #   "delta_pac": float,
    #   "current_pac": float,
    #   "implied_future_from_delta": float
    # }
```

**TRIBE V2 Integration Hook:** The `_build_step_feature()` method is the natural injection point. TRIBE V2 embeddings could be appended to the feature vector before normalization. This requires:
1. Pre-computed feature_mean/std that include the TRIBE V2 features
2. Updated TCN model with matching n_features
3. Extended `step()` signature to accept TRIBE V2 features

---

## 5. Validation Framework (`src/validation.py`)

### 5.1 Control Method Base Class (lines 84-115)

```python
class ControlMethodBase:
    def __init__(self, name: str): ...
    def reset(self): ...
    def step(self, pac_current: float) -> int: ...  # 0=REST, 1=STIMULATE
```

All control strategies inherit this. The `step()` signature takes only `pac_current` as input.

### 5.2 Four Strategies Compared

| Strategy | Class | Logic |
|----------|-------|-------|
| Fixed Schedule | `FixedScheduleControl` (lines 117-153) | 40s ON + 20s OFF cycle |
| Reactive Threshold | `ReactiveThresholdControl` (lines 156-228) | Z-score with hysteresis |
| Predictive Look-Ahead | `PredictiveLookAheadControl` (lines 231-415) | Trend or TCN-based |
| Oracle | `OracleControl` (lines 418-442) | Perfect information |

### 5.3 SimulationValidator (lines 445-793)

**`run_simulation()` (lines 478-608):**
```python
def run_simulation(self, method, duration_sec=360, fs=1.0,
                   tau_rise=0.15, tau_decay=0.10, seed=None,
                   use_fatigue=False, fatigue_rate=0.008,
                   recovery_rate=0.03, max_fatigue=0.7,
                   spectral_features=None) -> ValidationMetrics:
```

Creates simulator, runs method.step(pac) in loop, computes metrics.

**Metrics (`ValidationMetrics` dataclass, lines 59-81):**
- pac_mean, pac_std, pac_improvement (%), pac_variance_ratio
- stimulation_time (%), efficiency_ratio
- r2_score, rmse, mae (optional, for predictive methods)

**Statistical comparison (lines 647-715):** One-way ANOVA, Cohen's d for 2-group.

**TRIBE V2 Integration Hook:** Add `use_tribe=True` flag to `run_simulation()` that creates a `TribeV2Simulator` instead of `EntrainmentSimulator`/`FatigueAwareSimulator`. This is a clean, minimally-invasive integration point.

---

## 6. EEGNet Static Predictor (`src/eegnet.py`)

**Architecture (~1,457 params):**
```
Input: (B, 1, 7, 500)
Block 1:
  Conv2d(1, F1=8, kernel=(1,64)) + BN → (B, 8, 7, 500)
  DepthwiseConv2d(8, 16, kernel=(7,1)) + BN + ELU → (B, 16, 1, 500)
  AvgPool2d(1, 4) → (B, 16, 1, 125)
  Dropout(0.5)
Block 2:
  SeparableConv2d(16→16→16) + BN + ELU → (B, 16, 1, 125)
  AvgPool2d(1, 8) → (B, 16, 1, 15)
  Dropout(0.5)
FC: Linear(240, 1) → (B, 1)
```

Used by `ClosedLoopController` for real-time PAC prediction from raw EEG windows.

**TRIBE V2 Relevance:** EEGNet operates on raw EEG (7 ch × 500 samples). It predicts current PAC, not future PAC. TRIBE V2 is more relevant to the TCN pipeline (future prediction) and the simulator (brain modeling). However, TRIBE V2-derived features could augment EEGNet via a fusion architecture.

---

## 7. Configuration (`config.yaml`)

### Key Configuration Sections for TRIBE V2

**Simulator section (lines 206-222):**
```yaml
simulator:
  tau_rise: 0.15
  tau_decay: 0.10
  pac_max: 0.3
  pac_min: 0.05
  noise_std: 0.02
  extraction_method: "heuristic"
  simulation_duration_sec: 360
  decision_rate_hz: 1.0
```

**TRIBE V2 additions needed:**
```yaml
simulator:
  # ... existing params ...
  tribe_v2:
    enabled: false
    model_path: "models/tribe_v2_bridge.pth"
    embedding_dim: 768  # TRIBE V2 output dimension
    region_mapping: "frontal_7ch"  # which brain regions to map
    temporal_resolution: 2.0  # seconds per step
    modality_bridge: "linear"  # or "mlp", "attention"
```

**Paths section (lines 313-329):**
```yaml
paths:
  models:
    checkpoint: "models"
    best: "models/best_eegnet.pth"
```

Would need to add TRIBE V2 model paths.

---

## 8. Complete Data Flow

```
RAW EEG (7 channels, 250 Hz, 2s windows)
    │
    ├─→ src/preprocessing.py:EEGPreprocessor.preprocess()
    │     Bandpass 0.5-80 Hz → Notch 50 Hz → Artifact rejection → CAR
    │
    ├─→ src/pac_computation.py:PACComputer.compute_pac()
    │     Theta(4-8 Hz) phase × Gamma(38-42 Hz) amplitude → MI scalar
    │
    ├─→ src/data_loader.py → data/processed/{train,val,test}_data.npz
    │     Windows: (n, 1, 7, 500), PAC: (n,), Subjects: (n,)
    │
    ├─→ temporal_multiscale/build_multiscale_dataset.py
    │     61 spectral features + 7 PAC features + 5 stim context = 73 features
    │     Causal sequences: X[t-20:t] → Y[t+5]
    │     Z-score normalization (train stats only)
    │
    ├─→ temporal_multiscale/train_multiscale_tcn.py
    │     MultiscaleCausalTCN(73 features, hidden=64, dilations=[1,2,4,8])
    │     Dual-head: future_pac + delta_pac
    │     Huber loss + multi-task delta/consistency penalty
    │
    ├─→ temporal_multiscale/realtime_inference.py:RealtimePACForecaster
    │     Rolling buffer, online prediction, denormalization
    │
    ├─→ src/controller.py
    │     ├─ ClosedLoopController: EEGNet → PAC → z-score → decision
    │     └─ PredictiveLookAheadController: TCN → future PAC → proactive decision
    │
    └─→ src/simulator.py
          ├─ EntrainmentSimulator: PAC(t+1) = PAC(t) + τ(target - PAC(t)) + noise
          └─ FatigueAwareSimulator: + fatigue accumulation/recovery dynamics
```

**TRIBE V2 enters at three possible levels:**

1. **Simulator replacement** (highest impact): Replace exponential dynamics with TRIBE V2-driven brain response model. Requires fMRI→EEG bridge for PAC computation.

2. **Feature augmentation** (moderate impact): Add TRIBE V2 brain-state embeddings to the TCN's 73-feature input vector. Requires bridge layer that maps EEG windows to TRIBE V2's latent space.

3. **Dual prediction** (advanced): Use TRIBE V2 in parallel with EEGNet/TCN, then ensemble predictions. Most complex but potentially most powerful.

---

## 9. Integration Hooks Summary

| Hook Location | File:Line | Current Interface | What Changes |
|---|---|---|---|
| Simulator core dynamics | `src/simulator.py:128` | `pac_new = pac + tau*(target - pac)` | Replace with TRIBE V2 forward pass |
| Fatigue dynamics | `src/simulator.py:256-263` | Exponential fatigue model | TRIBE V2 habituation model |
| Simulator factory | `scripts/pipeline/run_closed_loop_demo.py:402` | Lambda creating EntrainmentSimulator | Add TribeV2Simulator factory |
| Validation sim creation | `src/validation.py:524-541` | Creates EntrainmentSimulator or FatigueAwareSimulator | Add use_tribe flag |
| TCN input features | `temporal_multiscale/build_multiscale_dataset.py:223` | 73 features concatenated | Append TRIBE V2 embeddings |
| TCN model config | `temporal_multiscale/multiscale_tcn.py:91` | `n_features: int` in ModelConfig | Increase to 73+N |
| Realtime feature build | `temporal_multiscale/realtime_inference.py:85-117` | Assembles 73-dim vector | Add TRIBE V2 features |
| Forecaster step | `temporal_multiscale/realtime_inference.py:119-163` | Accepts spectral + PAC + stim features | Add tribe_embedding param |
| Config file | `config.yaml:206-222` | Simulator params only | Add tribe_v2 section |
| Controller decision | `src/controller.py:420-468` | Uses delta_pac for look-ahead | Could weight by TRIBE V2 confidence |

---

## 10. Key Constraints for Integration

1. **PAC Scale:** Raw PAC range is [0.000006, 0.000701], mean ~0.000044. Normalized to [pac_min=0.05, pac_max=0.3] in simulation. Any TRIBE V2 output must map to this scale.

2. **Temporal Resolution:** The system operates at 1 Hz decision rate with 2-second EEG windows. fMRI TRs are typically 1-2 seconds — this is a fortunate alignment.

3. **Causal Constraint:** The TCN pipeline is strictly causal (no future information). Any TRIBE V2 features must also be strictly causal.

4. **Subject-Level Splits:** Train/val/test splits are by subject (24/5/6). TRIBE V2 training must respect this.

5. **7 Frontal Channels:** EEG uses Fp1, Fp2, F7, F3, Fz, F4, F8. The fMRI-to-EEG bridge must map to these specific electrode positions.

6. **Leakage Warning:** PAC features computed from raw MI values are circular (directly encode the target). Only spectral features are safe. Any TRIBE V2 features that implicitly encode PAC would create the same leakage.

7. **Persistence Baseline:** At 1-2s horizons, persistence (PAC[t+1] ≈ PAC[t]) beats the TCN. TRIBE V2 integration must demonstrate value at the 5-10s operational horizon.
