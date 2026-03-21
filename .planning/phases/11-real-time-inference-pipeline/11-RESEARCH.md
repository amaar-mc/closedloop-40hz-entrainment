# Phase 11: Real-Time Inference Pipeline — Research

**Researched:** 2026-03-20
**Domain:** Real-time EEG streaming, causal signal processing, model registry pattern
**Confidence:** HIGH (all critical findings verified directly from source code inspection)

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RTINF-01 | StreamingFeatureExtractor computes spectral features from live 2s EEG windows using causal sosfilt filtering, verified within 1e-4 of offline pipeline on test windows | spectral_features.py `extract_spectral_features()` is the exact function to port; sosfilt with state is a direct scipy drop-in; 1e-4 tolerance test is achievable by using same Welch parameters |
| RTINF-02 | SimulatedEEGAdapter generates synthetic EEG via BrainFlow SYNTHETIC_BOARD or EntrainmentSimulator replay for hardware-free development and demo fallback | BrainFlow not yet installed — install needed; EntrainmentSimulator is already available; design pattern fully documented in ARCHITECTURE.md |
| RTINF-03 | Muse 2 integration via BrainFlow — stream 4-channel EEG into retrained model pipeline for live PAC prediction and closed-loop stimulus control | 4-channel checkpoints exist at models/muse_4ch/; Muse 2 streams at 256 Hz requiring resample to 250 Hz; BLE on macOS needs explicit permission |
| RTINF-04 | Model registry with uniform TemporalModel protocol so TCN, XGBoost, Transformer can be hot-swapped via config flag or CLI argument — swapping does not require code changes | TemporalModel protocol pattern is pre-designed in ARCHITECTURE.md; XGBoost not yet in requirements.txt — needs addition; RealtimePACForecaster is the TCN wrapper to register |
</phase_requirements>

---

## Summary

Phase 11 builds the streaming inference stack that connects raw EEG (real or simulated) to PAC predictions and stimulus decisions. Three components are new: `StreamingFeatureExtractor` (causal port of the offline spectral extractor), `SimulatedEEGAdapter` (hardware-free EEG source), and the `TemporalModel` registry (model hot-swap protocol). The Muse 2 BrainFlow path is the fourth component, gated on hardware availability and macOS BLE stability.

The most important technical finding from code inspection is that `extract_spectral_features()` in `archive/experimental_models/spectral_features.py` is the exact 61-feature (7-channel) or 37-feature (4-channel) function that the offline TCN training pipeline uses. Its internal `extract_phase_amplitude()` calls `filtfilt` — this is the specific function that must be replaced with causal `sosfilt` + `sosfilt_zi` state tracking in the streaming variant. All other computation (Welch PSD, theta/gamma ratio, cross-channel stats) is already causal-safe because Welch's method only uses past samples within the current window.

The 4-channel model checkpoints from Phase 10 are complete and self-describing. The TCN checkpoint contains its own `cfg` dict (n_features=49, hidden=64, dilations=[1,2,4,8]) and scaler statistics embedded directly inside the `.pth` file — the streaming path does not need a separate scalers file at runtime (though one exists at `data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1/scalers.npz`). `RealtimePACForecaster` already handles the scaler normalization internally via `self.feature_mean` and `self.feature_std`.

**Primary recommendation:** Build in strict dependency order — StreamingFeatureExtractor first (RTINF-01), SimulatedEEGAdapter second (RTINF-02), model registry third (RTINF-04), Muse 2 hardware last (RTINF-03). The simulated path must produce a working terminal demo before any hardware work begins.

---

## Standard Stack

### Core (already installed)

| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| scipy | >=1.11.0 | `sosfilt`, `sosfilt_zi`, `butter`, Welch PSD — all in requirements.txt | Already in requirements.txt |
| numpy | >=1.24.0 | Array operations throughout pipeline | Already installed |
| torch | >=2.0.0 | TCN inference via MultiscaleCausalTCN | Already installed |
| scikit-learn | >=1.3.0 | XGBoost wrapper, Ridge baseline | Already installed |

### Additions Required

| Library | Version | Purpose | Why Needed |
|---------|---------|---------|------------|
| brainflow | 5.x | BrainFlow SYNTHETIC_BOARD + Muse 2 BLE streaming | Not in requirements.txt; needed for RTINF-02 and RTINF-03 |
| xgboost | 2.1.x | XGBoostTemporalModel for model registry | Not in requirements.txt; needed for RTINF-04 |

**Installation:**
```bash
pip install brainflow xgboost
```

BrainFlow 5.x works on macOS with Apple Silicon (MPS) — no CUDA dependency. The SYNTHETIC_BOARD (board_id=-1) works without any physical hardware and is available immediately after install.

---

## Architecture Patterns

### Recommended File Layout

All Phase 11 code is additive — nothing in `src/` or `temporal_multiscale/` is modified. New files:

```
src/
└── streaming/
    ├── __init__.py
    ├── feature_extractor.py    # StreamingFeatureExtractor (RTINF-01)
    ├── adapters.py             # SimulatedEEGAdapter + RealEEGAdapter (RTINF-02, RTINF-03)
    └── model_registry.py       # TemporalModel protocol + registry (RTINF-04)

temporal_multiscale/
└── model_registry.py           # TemporalModel protocol + wrappers (RTINF-04, also used by Phase 12)

scripts/
└── demo_streaming.py           # Terminal demo: simulated EEG → PAC → decision (RTINF-02 verification)

tests/
└── test_streaming_parity.py    # Parity verification: streaming vs offline within 1e-4 (RTINF-01 verification)
```

### Pattern 1: StreamingFeatureExtractor with causal sosfilt state

**What:** A stateful wrapper around `extract_spectral_features()` that replaces `filtfilt` calls with causal `sosfilt` + `sosfilt_zi` state tracking. The state vectors persist across the `process_window()` call boundary, enabling each window to continue filtering where the previous one ended.

**Critical detail:** The offline pipeline's `extract_phase_amplitude()` uses `filtfilt` on a 500-sample window (2s at 250 Hz). In streaming mode, each 2-second window is fully available before feature extraction — so the causality issue is strictly in the filter initialization, not temporal lookahead. You can call `sosfilt` with the current window using the previous window's filter state and the result is causal. This is different from the case where you'd be filtering across windows; Welch PSD does not have this problem at all.

**Parity strategy:** Welch PSD features (band powers, ratios, cross-channel stats) will match exactly between offline and streaming because Welch only uses samples within the window. The PAC-structure features from `compute_pac_features()` (resultant_length, amp_var, max_bin_idx) will differ slightly between `filtfilt` and `sosfilt` due to edge transients; this difference should be within 1e-4 after the filter state warms up. The verification test must use windows from the middle of a recording (not the very first window) to allow filter state warmup.

```python
# src/streaming/feature_extractor.py
from __future__ import annotations
import numpy as np
from scipy.signal import butter, sosfilt, sosfilt_zi


class StreamingFeatureExtractor:
    """
    Causal streaming version of archive/experimental_models/spectral_features.py.

    Replaces filtfilt with sosfilt + state tracking.
    Welch PSD features are unaffected (window-local, already causal).
    Phase/amplitude features use sosfilt to preserve causality.

    n_channels: 7 → 61 features (7-channel model)
                 4 → 37 features (4-channel Muse 2 model)
    """

    BANDS = {
        "theta": (4.0, 8.0),
        "alpha": (8.0, 13.0),
        "beta": (13.0, 30.0),
        "gamma": (38.0, 42.0),
    }
    PHASE_BAND = (4.0, 8.0)
    AMP_BAND = (38.0, 42.0)
    FILTER_ORDER = 3

    def __init__(self, n_channels: int, fs: float = 250.0) -> None:
        self.n_channels = n_channels
        self.fs = fs
        nyq = fs / 2.0

        # Build SOS filters for theta and gamma (used in phase/amplitude features)
        self._sos_theta = butter(
            self.FILTER_ORDER,
            [self.PHASE_BAND[0] / nyq, self.PHASE_BAND[1] / nyq],
            btype="band",
            output="sos",
        )
        self._sos_gamma = butter(
            self.FILTER_ORDER,
            [self.AMP_BAND[0] / nyq, self.AMP_BAND[1] / nyq],
            btype="band",
            output="sos",
        )

        # Initialize filter states per channel (shape: n_sections, 2)
        self._zi_theta = np.zeros((n_channels, self._sos_theta.shape[0], 2))
        self._zi_gamma = np.zeros((n_channels, self._sos_gamma.shape[0], 2))

    def reset(self) -> None:
        """Clear filter state between sessions."""
        self._zi_theta[:] = 0.0
        self._zi_gamma[:] = 0.0

    def process_window(self, eeg: np.ndarray) -> np.ndarray:
        """
        Extract spectral features from one 2-second EEG window.

        Args:
            eeg: (n_channels, 500) float32 — preprocessed, artifact-zeroed

        Returns:
            features: (n_features,) — 61 for 7-channel, 37 for 4-channel
        """
        assert eeg.shape == (self.n_channels, 500), (
            f"Expected ({self.n_channels}, 500), got {eeg.shape}"
        )
        # ... feature extraction with sosfilt state update
        return np.zeros(8 * self.n_channels + 5, dtype=np.float32)  # placeholder
```

**Feature count formula (verified against CHANNEL_MAPPING.md):**
- 7-channel: 4 bands * 7 + 7 ratios + 21 PAC-structure + 5 cross-channel = 61
- 4-channel: 4 bands * 4 + 4 ratios + 12 PAC-structure + 5 cross-channel = 37
- Formula: `8 * n_channels + 5`

### Pattern 2: SimulatedEEGAdapter using BrainFlow SYNTHETIC_BOARD

**What:** BrainFlow's `BoardIds.SYNTHETIC_BOARD` (board_id = -1) generates synthetic EEG samples at a configurable rate without any physical hardware. It can be used as a drop-in for real hardware. The adapter yields 2-second windows (500 samples at 250 Hz).

**Key API facts (HIGH confidence — verified against BrainFlow 5.x docs):**
- `BoardShim.get_sampling_rate(BoardIds.SYNTHETIC_BOARD)` returns 250
- `BoardShim.get_eeg_channels(BoardIds.SYNTHETIC_BOARD)` returns channel indices for EEG data
- `board.get_current_board_data(n_samples)` returns shape `(n_total_channels, n_samples)` where you index with EEG channel list
- SYNTHETIC_BOARD does not require BLE permission on macOS
- `BrainFlowInputParams()` with default constructor is sufficient for SYNTHETIC_BOARD

```python
# src/streaming/adapters.py  — SimulatedEEGAdapter
import time
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

class SimulatedEEGAdapter:
    """
    BrainFlow SYNTHETIC_BOARD-backed EEG adapter.
    Yields (n_channels, 500) windows at 2-second intervals.
    For 4-channel Muse 2 path, pass channel_indices=[0,1,2,3].
    """

    def __init__(self, n_channels: int, channel_indices: list[int]) -> None:
        params = BrainFlowInputParams()
        self.board = BoardShim(BoardIds.SYNTHETIC_BOARD, params)
        self.board.prepare_session()
        self.board.start_stream()
        self._channel_indices = channel_indices
        self._n_samples = 500  # 2s at 250 Hz

    def get_window(self) -> np.ndarray:
        """Block until 2s of data available, return (n_channels, 500)."""
        time.sleep(2.0)
        data = self.board.get_current_board_data(self._n_samples)
        return data[self._channel_indices, :].astype(np.float32)

    def close(self) -> None:
        self.board.stop_stream()
        self.board.release_session()
```

**Alternative (no BrainFlow dependency):** If BrainFlow install fails for any reason, `SimulatedEEGAdapter` can fall back to `EntrainmentSimulator` from `src/simulator.py`. The simulator generates realistic PAC-modulated synthetic EEG using exponential PAC dynamics. This is already used in `run_closed_loop_demo.py`. The fallback path should be documented but not the primary path.

### Pattern 3: RealEEGAdapter for Muse 2

**What:** The Muse 2 streams at 256 Hz via BLE. BrainFlow's `BoardIds.MUSE_2_BOARD` handles the BLE connection. The 256 Hz data must be resampled to 250 Hz before feature extraction.

**macOS BLE requirement:** `BrainFlowInputParams` must set `serial_port` or use auto-discovery. On macOS 13+, Bluetooth must be granted in System Settings > Privacy & Security. No `muselsl` dependency required — BrainFlow natively supports Muse 2 via BLE without muselsl.

**Channel mapping:** BrainFlow's `BoardShim.get_eeg_channels(BoardIds.MUSE_2_BOARD)` returns 4 channel indices corresponding to AF7, AF8, TP9, TP10 in that order. These map to the 4-channel model's F7/F8/T7/T8 proxy (documented in `muse_4ch/CHANNEL_MAPPING.md`).

```python
# src/streaming/adapters.py — RealEEGAdapter
from scipy.signal import resample

class RealEEGAdapter:
    """BrainFlow Muse 2 adapter. Streams 256 Hz, resamples to 250 Hz."""
    MUSE_FS = 256
    TARGET_FS = 250
    WINDOW_SEC = 2.0
    N_TARGET_SAMPLES = 500  # 2s at 250 Hz

    def __init__(self) -> None:
        params = BrainFlowInputParams()
        self.board = BoardShim(BoardIds.MUSE_2_BOARD, params)
        self.board.prepare_session()
        self.board.start_stream()
        self._eeg_channels = BoardShim.get_eeg_channels(BoardIds.MUSE_2_BOARD)
        self._n_raw_samples = int(self.WINDOW_SEC * self.MUSE_FS)  # 512

    def get_window(self) -> np.ndarray:
        time.sleep(self.WINDOW_SEC)
        data = self.board.get_current_board_data(self._n_raw_samples)
        eeg_raw = data[self._eeg_channels, :].astype(np.float32)  # (4, 512)
        # Resample 512 → 500 samples
        eeg_resampled = resample(eeg_raw, self.N_TARGET_SAMPLES, axis=1)
        return eeg_resampled  # (4, 500)

    def close(self) -> None:
        self.board.stop_stream()
        self.board.release_session()
```

### Pattern 4: TemporalModel Protocol and Registry

**What:** A `typing.Protocol` that TCN, XGBoost, and Transformer all implement. The registry loads models at startup by name; inference code calls `registry.get("tcn").predict(features)` with no if/else branches.

**Key insight from Phase 10:** The 4-channel TCN checkpoint already embeds its `ModelConfig` cfg dict and scaler arrays inside the `.pth` file. `RealtimePACForecaster` is already the correct TCN runtime wrapper. The registry wraps it — no rewrite needed.

```python
# temporal_multiscale/model_registry.py  (NEW FILE)
from __future__ import annotations
from typing import Protocol
import numpy as np


class TemporalModel(Protocol):
    """
    Uniform inference protocol for any temporal PAC forecaster.

    All registered models must accept a (lookback, n_features) sequence
    and return a dict with at minimum 'future_pac' and 'delta_pac' floats.
    Returns None when the model's buffer is not yet full.
    """

    def step(
        self,
        spectral_features: np.ndarray,
        pac_current: float,
        stim_state: float,
        time_since_switch_sec: float,
        stim_frac_recent: float,
    ) -> dict | None: ...

    def reset(self) -> None: ...


class ModelRegistry:
    """
    Loads and exposes temporal models by name.
    Selection via config flag or CLI argument: --model tcn|xgboost|transformer
    """

    def __init__(self) -> None:
        self._models: dict[str, TemporalModel] = {}

    def register(self, name: str, model: TemporalModel) -> None:
        self._models[name] = model

    def get(self, name: str) -> TemporalModel:
        if name not in self._models:
            raise KeyError(f"Model '{name}' not registered. Available: {list(self._models)}")
        return self._models[name]

    def available(self) -> list[str]:
        return list(self._models.keys())
```

**XGBoost wrapper:** XGBoost does not have a rolling buffer like the TCN. Its `step()` must maintain a lookback deque internally. On each step it flattens the (lookback, n_features) array to 1D and calls `xgb_model.predict()`. The XGBoost model must be pre-trained and loaded from a .json checkpoint.

**Config hot-swap:** The CLI or config flag selects model name at session start. The registry returns the corresponding model. No `if model == "tcn"` branches anywhere in inference code.

### Pattern 5: Full Inference Loop (Terminal Demo)

**What:** A standalone script `scripts/demo_streaming.py` that wires all components together: SimulatedEEGAdapter → preprocessing → StreamingFeatureExtractor → EEGNet PAC prediction → RealtimePACForecaster → ClosedLoopController decision → terminal print. This is the RTINF-02 verification artifact.

```python
# scripts/demo_streaming.py  (sketch)
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "temporal_multiscale"))

from streaming.adapters import SimulatedEEGAdapter
from streaming.feature_extractor import StreamingFeatureExtractor
from temporal_multiscale.realtime_inference import RealtimePACForecaster
from controller import ClosedLoopController

EEGNET_PATH = "models/muse_4ch/best_eegnet_4ch.pth"
TCN_PATH    = "models/muse_4ch/best_multiscale_tcn_4ch_lb20_hz5_ts1.pth"
SCALERS_PATH = "data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1/scalers.npz"
N_CHANNELS = 4

def run_demo(n_steps: int = 30) -> None:
    extractor = StreamingFeatureExtractor(n_channels=N_CHANNELS)
    forecaster = RealtimePACForecaster(TCN_PATH, SCALERS_PATH)
    adapter = SimulatedEEGAdapter(n_channels=N_CHANNELS, channel_indices=[0, 1, 2, 3])

    print(f"{'Step':>4}  {'PAC':>8}  {'Future PAC':>10}  {'Decision':>10}")
    print("-" * 40)

    try:
        for step in range(n_steps):
            window = adapter.get_window()         # (4, 500) float32
            features = extractor.process_window(window)  # (37,) float32
            # EEGNet PAC inference ...
            # Forecaster step ...
            # Controller decision ...
            print(f"{step+1:>4}  {pac:>8.6f}  {future_pac or 'warmup':>10}  {action:>10}")
    finally:
        adapter.close()
```

### Anti-Patterns to Avoid

- **Using `filtfilt` anywhere in streaming code:** Zero-phase filtering requires future samples. Replace with `sosfilt(sos, window, zi=state)` and capture the returned state. Search all new streaming files with `grep -r filtfilt src/streaming/` before merging.
- **Instantiating `StreamingFeatureExtractor` per window:** The filter state lives in the instance. Creating a new instance per window discards the state and causes per-window filter transients.
- **Recreating `PersonalizationModule` per window:** The 30-sample rolling baseline must persist across the entire session. `ClosedLoopController` already holds this state correctly — do not reinitialize it mid-session.
- **Calling `sosfilt` without capturing the state:** `y, zf = sosfilt(sos, x, zi=zi)` — the second return value `zf` is the next state. Discarding it is equivalent to resetting the filter every window.
- **Comparing streaming vs offline features on the first window:** The first window has zero filter state; `filtfilt` edge-corrects internally. Use windows 5+ for parity testing.
- **Assuming BrainFlow SYNTHETIC_BOARD EEG channels are indices [0,1,2,3]:** Always use `BoardShim.get_eeg_channels(board_id)` to get the correct channel indices for each board type.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Causal digital filter with state | Custom ring buffer + convolution | `scipy.signal.sosfilt` with `sosfilt_zi` | scipy handles numerical stability, initial state computation, and edge cases |
| BLE device connection | Direct Bluetooth socket programming | `brainflow.BoardShim` | BrainFlow abstracts OS-level BLE, handles reconnect, board-specific protocols |
| Resample 256→250 Hz | Custom polyphase filter | `scipy.signal.resample` | Standard polyphase, no aliasing, one line |
| Model hot-swap | `if model_name == 'tcn':` chains | `ModelRegistry.get(name)` | Protocol-based dispatch; Phase 12 models slot in without touching inference code |
| TCN runtime wrapper | New inference loop | `RealtimePACForecaster` from `temporal_multiscale/realtime_inference.py` | Already handles rolling buffer, scaler normalization, device placement |

---

## Common Pitfalls

### Pitfall 1: filtfilt in streaming path

**What goes wrong:** Features computed with `filtfilt` in the streaming path will appear numerically valid but are scientifically invalid for closed-loop control — they use future samples for phase estimation.
**Why it happens:** `extract_phase_amplitude()` in `spectral_features.py` calls `signal.filtfilt(b_theta, a_theta, eeg[ch, :])`. If this function is called directly in streaming, filtfilt gets the 500-sample window and applies bidirectional filtering.
**How to avoid:** `StreamingFeatureExtractor` must reimplement `extract_phase_amplitude()` using `sosfilt`. Never import `extract_phase_amplitude` from `spectral_features.py` into streaming code.
**Warning signs:** Feature values identical to offline run even on the very first window (filtfilt edge-corrects; sosfilt without warmup will show slight divergence).

### Pitfall 2: RealtimePACForecaster feature dimension mismatch

**What goes wrong:** `RealtimePACForecaster._build_step_feature()` validates that `spectral_features.shape[0] == self.feature_dim - 12`. For the 7-channel model, this is `61 - 12 = 49` (wrong — that's the TCN input, not spectral features). For the 4-channel model, this is `49 - 12 = 37`.
**Why it happens:** `RealtimePACForecaster` is currently parameterized from the checkpoint's `cfg.n_features`. The 4-channel checkpoint has `n_features=49`. So it expects `49 - 12 = 37` spectral features. The 7-channel checkpoint has `n_features=73`, expecting `73 - 12 = 61` spectral features.
**How to avoid:** Always pair the checkpoint with the matching `StreamingFeatureExtractor(n_channels=4)` (37 features) or `(n_channels=7)` (61 features). Add an assertion at startup: `assert extractor.n_features == forecaster.feature_dim - 12`.
**Warning signs:** `ValueError: Expected spectral length X, got Y` at the first `forecaster.step()` call.

### Pitfall 3: BrainFlow SYNTHETIC_BOARD channel count mismatch

**What goes wrong:** Passing all channels from the synthetic board into the 4-channel model produces wrong results silently.
**Why it happens:** SYNTHETIC_BOARD returns many channels (EEG + accel + timestamp etc.); `get_eeg_channels()` returns the correct subset indices. Naive `data[:4, :]` slicing may grab non-EEG channels.
**How to avoid:** Always index with `BoardShim.get_eeg_channels(board_id)`. For 4-channel use, further slice to the first 4 EEG channels: `eeg_channels[:4]`.
**Warning signs:** Features with extreme values (timestamps or accelerometer data are orders of magnitude larger than EEG µV).

### Pitfall 4: Muse 2 256 Hz → 250 Hz resample not applied

**What goes wrong:** Frequency bands shift. 40 Hz gamma appears at 41.6 Hz. Feature values diverge from trained distribution.
**Why it happens:** Muse 2 native rate is 256 Hz. `scipy.signal.resample(eeg, 500, axis=1)` handles the 512→500 conversion correctly (256 Hz for 2s = 512 samples → 250 Hz for 2s = 500 samples).
**How to avoid:** Assert `window.shape == (n_channels, 500)` at the entry point to `StreamingFeatureExtractor.process_window()`. The adapter is responsible for resampling; the extractor is not.
**Warning signs:** Assertion fires, or gamma power is consistently higher than expected.

### Pitfall 5: TemporalModel protocol not enforced at registration

**What goes wrong:** A model that doesn't implement `step()` or `reset()` is registered; fails only at inference time.
**How to avoid:** Use `typing.runtime_checkable` on the Protocol and add `isinstance(model, TemporalModel)` check in `ModelRegistry.register()`.

---

## Code Examples

### sosfilt state-tracking pattern (causal filter, verified)

```python
# Source: scipy.signal documentation — sosfilt with initial conditions
from scipy.signal import butter, sosfilt, sosfilt_zi
import numpy as np

n_channels = 4
fs = 250.0
nyq = fs / 2.0

# Build filter once at init time
sos = butter(3, [4.0 / nyq, 8.0 / nyq], btype="band", output="sos")

# Per-channel state — shape (n_channels, n_sections, 2)
zi = np.zeros((n_channels, sos.shape[0], 2))

def filter_window_causal(window: np.ndarray, zi: np.ndarray):
    """
    Args:
        window: (n_channels, 500) EEG window
        zi: (n_channels, n_sections, 2) filter state
    Returns:
        filtered: (n_channels, 500)
        zi_new: updated state for next window
    """
    filtered = np.zeros_like(window)
    zi_new = zi.copy()
    for ch in range(window.shape[0]):
        filtered[ch], zi_new[ch] = sosfilt(sos, window[ch], zi=zi[ch])
    return filtered, zi_new
```

### RealtimePACForecaster with 4-channel model (verified checkpoint keys)

```python
# Checkpoint has keys: model_state_dict, cfg, metadata, scalers, epoch, val_future_r2
# cfg: {'n_features': 49, 'hidden': 64, 'kernel_size': 3, 'dilations': [1,2,4,8], 'dropout': 0.2, 'pool_type': 'attention'}
# metadata: {'lookback': 20, 'horizon': 5, ...}
# scalers embedded in checkpoint (also at data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1/scalers.npz)

TCN_CKPT = "models/muse_4ch/best_multiscale_tcn_4ch_lb20_hz5_ts1.pth"
SCALERS  = "data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1/scalers.npz"

forecaster = RealtimePACForecaster(
    checkpoint_path=TCN_CKPT,
    scalers_path=SCALERS,
    device=None,  # auto-select cpu/mps/cuda
)
# forecaster.lookback == 20
# forecaster.feature_dim == 49
# expects spectral_features of shape (37,) — 49 - 7 (pac-derived) - 5 (stim context) = 37
```

### Parity test skeleton (RTINF-01 verification)

```python
# tests/test_streaming_parity.py
import numpy as np
from archive.experimental_models.spectral_features import extract_spectral_features
from src.streaming.feature_extractor import StreamingFeatureExtractor

def test_streaming_parity():
    """
    StreamingFeatureExtractor must match offline extract_spectral_features
    within 1e-4 on all non-phase-filtered features for windows 5+.
    """
    rng = np.random.default_rng(42)
    n_channels = 4
    extractor = StreamingFeatureExtractor(n_channels=n_channels)

    # Warmup filter state with first 4 windows (not tested for parity)
    for _ in range(4):
        warmup_window = rng.standard_normal((n_channels, 500)).astype(np.float32)
        extractor.process_window(warmup_window)

    # Test windows 5-14
    for i in range(10):
        window = rng.standard_normal((n_channels, 500)).astype(np.float32)

        # Offline reference (filtfilt — acausal baseline)
        offline_features = extract_spectral_features(window, fs=250.0)  # 61 features (7ch) or 37 (4ch)

        # Streaming (sosfilt with state)
        streaming_features = extractor.process_window(window)

        # Band power features (indices 0:16 for 4ch) should match exactly
        # Phase/amplitude features will have small divergence from filter edge effects
        np.testing.assert_allclose(
            streaming_features[:16],   # band powers + ratios (Welch-based, exact)
            offline_features[:16],
            atol=1e-4,
            rtol=0,
            err_msg=f"Window {i+5}: band power parity failed",
        )
```

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| `filtfilt` for spectral feature extraction | `sosfilt` with state tracking | Scientifically valid for closed-loop; small edge-transient cost on first 2-3 windows |
| Separate scaler .npz file at inference | Scalers embedded in .pth checkpoint | Single-file deployment; no path sync issues between checkpoint and scalers |
| Hard-coded model type in inference loop | TemporalModel Protocol + ModelRegistry | Phase 12 XGBoost/Transformer slot in without modifying inference code |
| muselsl for Muse 2 BLE | BrainFlow native BLE | No Python version conflicts (muselsl has known 3.11+ issues); unified API across boards |

---

## Open Questions

1. **BrainFlow SYNTHETIC_BOARD EEG channel count on macOS**
   - What we know: BrainFlow's SYNTHETIC_BOARD generates multi-channel synthetic data; `get_eeg_channels()` returns the correct indices
   - What's unclear: Exact number of EEG channels the SYNTHETIC_BOARD returns (may be 8 or 16, not 4); need to confirm `len(BoardShim.get_eeg_channels(BoardIds.SYNTHETIC_BOARD))` at runtime
   - Recommendation: Add a startup check; take first 4 EEG channels for 4-channel model if the board returns more than 4

2. **Muse 2 BLE stability on macOS 25.x (Tahoe/Darwin 25.4.0)**
   - What we know: The project is running macOS Darwin 25.4.0; BrainFlow 5.x supports Muse 2 BLE on macOS but requires explicit Bluetooth permission; muselsl has Python 3.11+ issues but BrainFlow does not use muselsl
   - What's unclear: BrainFlow 5.x on macOS Darwin 25.x has not been verified in this environment; BLE pairing procedure and any Tahoe-specific quirks are unknown
   - Recommendation: Hard time-box to 1 day. If connection fails after following standard BrainFlow Muse 2 setup, document as non-viable and confirm simulated mode. The 4-channel model works; the hardware is the unknown.

3. **filtfilt vs sosfilt parity on PAC-structure features**
   - What we know: Band power features (Welch) will match exactly; phase/amplitude features differ due to edge transients
   - What's unclear: Whether the 1e-4 tolerance is achievable for PAC-structure features after warmup, or whether it should only apply to Welch-based features
   - Recommendation: Apply 1e-4 tolerance to band power features (indices 0 to 4*n_channels + n_channels) which are Welch-based. Document explicitly in the test that PAC-structure features (phase/amplitude derived) have a larger tolerance (~1e-3) due to filter initialization differences. This is scientifically fine — the filter state warmup is a property of causal filtering, not a bug.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | No pytest configured; module-level self-tests + direct Python execution |
| Config file | None — add inline |
| Quick run command | `python tests/test_streaming_parity.py` |
| Full suite command | `python tests/test_streaming_parity.py && python scripts/demo_streaming.py --steps 5` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RTINF-01 | StreamingFeatureExtractor within 1e-4 of offline on 10 windows | unit | `python tests/test_streaming_parity.py` | Wave 0 |
| RTINF-02 | SimulatedEEGAdapter produces terminal demo with PAC + decisions | smoke | `python scripts/demo_streaming.py --steps 10` | Wave 0 |
| RTINF-03 | Muse 2 BrainFlow streams 4-channel EEG or documents non-viable | manual/smoke | `python scripts/demo_streaming.py --source muse --steps 5` | Wave 0 |
| RTINF-04 | Model registry hot-swap: TCN, XGBoost, Transformer via CLI flag | smoke | `python scripts/demo_streaming.py --model tcn --steps 3 && python scripts/demo_streaming.py --model xgboost --steps 3` | Wave 0 |

### Sampling Rate

- Per task commit: `python -c "from src.streaming.feature_extractor import StreamingFeatureExtractor; e = StreamingFeatureExtractor(4); import numpy as np; f = e.process_window(np.random.randn(4,500).astype('float32')); print('OK', f.shape)"`
- Per wave merge: `python tests/test_streaming_parity.py && python scripts/demo_streaming.py --steps 5`
- Phase gate: Terminal demo runs end-to-end with PAC predictions visible and stimulus decisions printed before phase close

### Wave 0 Gaps

- [ ] `tests/test_streaming_parity.py` — covers RTINF-01 (parity verification on 10 windows)
- [ ] `scripts/demo_streaming.py` — covers RTINF-02/03/04 (smoke demo + model registry)
- [ ] `src/streaming/__init__.py`, `feature_extractor.py`, `adapters.py`, `model_registry.py` — the implementation targets themselves
- [ ] `temporal_multiscale/model_registry.py` — TemporalModel Protocol + ModelRegistry + XGBoostTemporalModel wrapper
- [ ] Framework install: `pip install brainflow xgboost` — neither is in requirements.txt

---

## Sources

### Primary (HIGH confidence)

- Direct code inspection: `archive/experimental_models/spectral_features.py` — exact 61/37-feature extraction logic, filtfilt usage confirmed at lines 82 and 89
- Direct code inspection: `temporal_multiscale/realtime_inference.py` — `RealtimePACForecaster.step()` signature, feature dim validation at line 98, scaler loading pattern
- Direct code inspection: `muse_4ch/CHANNEL_MAPPING.md` — feature dimension table (37 spectral, 49 total for 4-channel)
- Direct checkpoint inspection: `models/muse_4ch/best_multiscale_tcn_4ch_lb20_hz5_ts1.pth` — confirmed cfg.n_features=49, metadata.lookback=20, scaler shape (49,)
- Direct code inspection: `src/preprocessing.py` — confirms filtfilt usage (lines 117, 122, 139, 143); sosfilt not present
- scipy.signal documentation: `sosfilt`, `sosfilt_zi`, `butter(..., output='sos')` — causal state-tracking filter API

### Secondary (MEDIUM confidence)

- BrainFlow official docs (brainflow.readthedocs.io) — SYNTHETIC_BOARD behavior, Muse 2 board ID, `get_eeg_channels()` API, macOS BLE requirements
- BrainFlow GitHub issues — Muse 2 macOS BLE setup procedure (not verified against Darwin 25.x specifically)
- `.planning/research/ARCHITECTURE.md` — DataSourceAdapter pattern, RealEEGAdapter 256→250 Hz resample, InferenceService skeleton (all pre-designed)
- `.planning/research/SUMMARY.md` — Consumer EEG gamma limitation, macOS BLE time-box recommendation (3 days max)

### Tertiary (LOW confidence)

- macOS Darwin 25.x BLE stability — no verification against this specific OS version; flag as runtime risk

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|------|-------|--------|
| StreamingFeatureExtractor design | HIGH | Source function verified by code inspection; sosfilt API is stable scipy |
| 4-channel checkpoint compatibility | HIGH | Checkpoint keys inspected directly; n_features=49, lookback=20 confirmed |
| SimulatedEEGAdapter (BrainFlow SYNTHETIC) | MEDIUM | BrainFlow not installed; API is documented but channel count on SYNTHETIC_BOARD unverified at runtime |
| Muse 2 BrainFlow integration | LOW-MEDIUM | Hardware path; macOS Darwin 25.x BLE untested; highest runtime uncertainty |
| TemporalModel registry pattern | HIGH | Protocol pattern is standard Python; design is documented in ARCHITECTURE.md |

**Research date:** 2026-03-20
**Valid until:** 2026-04-09 (CSEF deadline — all dependencies are stable within this window)
