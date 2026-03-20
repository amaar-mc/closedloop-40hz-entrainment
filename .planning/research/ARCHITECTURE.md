# Architecture Research

**Domain:** Closed-loop neurostimulation web platform with real-time EEG inference
**Researched:** 2026-03-20
**Confidence:** MEDIUM-HIGH (web app patterns HIGH, EEG hardware integration MEDIUM, dual-mode specifics MEDIUM)

## Standard Architecture

### System Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                        Browser (Next.js)                           │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────────────┐ │
│  │  Session UI │  │  EEG Viz Canvas  │  │  Web Audio Engine     │ │
│  │  (caregiver)│  │  (Chart.js/d3)   │  │  (AudioContext 40Hz)  │ │
│  └──────┬──────┘  └────────┬─────────┘  └──────────┬────────────┘ │
│         │                  │                        │              │
│         └──────────────────┴───────────┬────────────┘              │
│                                        │ WebSocket (ws://)          │
├────────────────────────────────────────┼───────────────────────────┤
│                    FastAPI Backend (Python)                         │
│  ┌──────────────────┐  ┌─────────────────────────────────────┐    │
│  │  /ws/session     │  │  REST: /session, /patient, /metrics │    │
│  │  WebSocket hub   │  │  (session CRUD, export, history)    │    │
│  └────────┬─────────┘  └─────────────────────────────────────┘    │
│           │                                                         │
│  ┌────────▼──────────────────────────────────────────────────────┐ │
│  │                   InferenceService                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────────────┐ │ │
│  │  │ EEGNet      │  │ TCN         │  │ New models (Xformer,  │ │ │
│  │  │ (static PAC)│  │ (future PAC)│  │ XGBoost, Ridge)       │ │ │
│  │  └─────────────┘  └─────────────┘  └───────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────────┘ │
│           │                                                         │
│  ┌────────▼──────────────────────────────────────────────────────┐ │
│  │               ControllerService (existing logic)               │ │
│  │   ClosedLoopController / PredictiveLookAheadController         │ │
│  │   PersonalizationModule, hysteresis, z-score                   │ │
│  └───────────────────────────────────────────────────────────────┘ │
│           │                                                         │
│  ┌────────▼──────────────────────────────────────────────────────┐ │
│  │                    DataSourceAdapter                           │ │
│  │  ┌───────────────────────────┐  ┌────────────────────────┐    │ │
│  │  │  RealEEGAdapter           │  │  SimulatedEEGAdapter    │    │ │
│  │  │  (BrainFlow → window)     │  │  (EntrainmentSimulator) │    │ │
│  │  └───────────────────────────┘  └────────────────────────┘    │ │
│  └───────────────────────────────────────────────────────────────┘ │
│           │                                                         │
│  ┌────────▼───────────────────────────────────────────────────┐    │
│  │              SessionStore (SQLite via SQLAlchemy)           │    │
│  │   sessions, patients, windows_log, decisions_log           │    │
│  └────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| Next.js frontend | Session UI, EEG waveform display, audio engine, QR landing | Next.js 15 + React + Tailwind |
| Web Audio Engine | Generate/gate 40Hz sine tone, ramp amplitude on stim signal | Browser AudioContext API |
| FastAPI backend | WebSocket hub, REST endpoints, model loading, session lifecycle | FastAPI + uvicorn (async) |
| InferenceService | Load models, run EEGNet/TCN/new-arch inference per window | PyTorch, scikit-learn |
| ControllerService | Wrap existing controller.py logic, expose step() over WebSocket | Existing src/ modules |
| DataSourceAdapter | Abstract over real vs simulated EEG; uniform window output | BrainFlow (real), EntrainmentSimulator (sim) |
| SessionStore | Persist sessions, patients, per-window logs | SQLite + SQLAlchemy (async) |

---

## Recommended Project Structure

New code lives in `webapp/` at the repo root. Existing `src/`, `temporal_multiscale/` are **not** modified — they are imported by the backend as a library.

```
webapp/
├── backend/
│   ├── main.py                  # FastAPI app, mounts routers + WebSocket
│   ├── routers/
│   │   ├── session.py           # POST /session, GET /session/{id}, DELETE
│   │   ├── patient.py           # CRUD for patient records
│   │   └── metrics.py           # GET session metrics, export CSV
│   ├── ws/
│   │   └── session_ws.py        # WebSocket handler: /ws/session/{id}
│   ├── services/
│   │   ├── inference_service.py # Loads models, runs step inference
│   │   ├── controller_service.py# Wraps ClosedLoopController / PredictiveLookAheadController
│   │   └── datasource/
│   │       ├── base.py          # Abstract DataSourceAdapter protocol
│   │       ├── simulated.py     # EntrainmentSimulator-backed adapter
│   │       └── real_eeg.py      # BrainFlow-backed adapter
│   ├── db/
│   │   ├── models.py            # SQLAlchemy ORM: Session, Patient, WindowLog
│   │   └── session_store.py     # Async CRUD helpers
│   └── config.py                # Pydantic settings (reads config.yaml + env vars)
│
└── frontend/
    ├── app/
    │   ├── page.tsx             # Landing / QR target
    │   ├── session/
    │   │   ├── [id]/page.tsx    # Live session view (caregiver)
    │   │   └── new/page.tsx     # Start session form
    │   └── patients/
    │       └── page.tsx         # Patient list + history
    ├── components/
    │   ├── EEGWaveform.tsx      # Canvas-based rolling EEG display
    │   ├── PACChart.tsx         # PAC + predicted-PAC time series (Chart.js)
    │   ├── StimIndicator.tsx    # STIMULATE / REST status with color
    │   ├── AudioEngine.tsx      # Web Audio API wrapper, receives stim commands
    │   └── SessionControls.tsx  # Start/stop/reset session
    ├── hooks/
    │   ├── useSessionWS.ts      # WebSocket client with reconnect logic
    │   └── useAudio.ts          # AudioContext lifecycle (suspend/resume)
    └── lib/
        └── api.ts               # REST client (fetch wrappers)
```

### Structure Rationale

- **`webapp/` at root:** Keeps the research pipeline (`src/`, `temporal_multiscale/`) untouched. The backend simply does `sys.path.insert(0, repo_root)` and imports them as a package.
- **`datasource/` adapter layer:** This is the critical seam. The entire rest of the backend doesn't care whether EEG is real or simulated. Switching mode is a single config flag or runtime parameter.
- **`ws/session_ws.py` separation:** WebSocket logic is intentionally not mixed into REST routers. Each session gets its own connection object and asyncio task for the inference loop.
- **Frontend in `webapp/frontend/`:** Co-located with backend for single-repo deploys (Vercel frontend, Railway/localhost backend). Decoupled enough to separate later.

---

## Architectural Patterns

### Pattern 1: WebSocket Inference Loop

**What:** A persistent WebSocket connection per active session drives the closed-loop tick. The backend owns the 1 Hz decision clock; the frontend is a display/audio subscriber, not a timer.

**When to use:** Real-time biofeedback with sub-2-second latency requirement and bidirectional control (start/stop/reset from UI).

**Trade-offs:** Simpler than SSE + REST, enables push from backend (stim commands), handles reconnection. Complexity: need graceful cleanup when connection drops mid-session.

**Pattern:**
```python
# webapp/backend/ws/session_ws.py
@router.websocket("/ws/session/{session_id}")
async def session_ws(websocket: WebSocket, session_id: str):
    await websocket.accept()
    session = await SessionStore.get(session_id)
    adapter = build_adapter(session.mode)  # "simulated" or "real"
    controller = ControllerService(session.config)

    try:
        async for window in adapter.stream():          # yields every 2s
            action, pac, z = controller.step(window)
            msg = {"action": int(action), "pac": pac, "z": z, "ts": time.time()}
            await SessionStore.log_window(session_id, msg)
            await websocket.send_json(msg)
    except WebSocketDisconnect:
        await SessionStore.mark_ended(session_id)
    finally:
        adapter.close()
```

### Pattern 2: DataSourceAdapter Protocol

**What:** A typed async generator protocol so `RealEEGAdapter` and `SimulatedEEGAdapter` are interchangeable behind the same `stream()` interface.

**When to use:** Any time you need dual-mode (demo vs. production) with zero controller code changes.

**Trade-offs:** Requires defining a clear protocol up front. Worth it — this is the core architectural decision that makes demo mode painless.

```python
# webapp/backend/services/datasource/base.py
from typing import AsyncIterator, Protocol
import numpy as np

class DataSourceAdapter(Protocol):
    async def stream(self) -> AsyncIterator[np.ndarray]:
        """Yields (7, 500) float32 EEG windows at 1 Hz."""
        ...
    def close(self) -> None: ...
```

```python
# webapp/backend/services/datasource/simulated.py
import asyncio, sys, numpy as np
sys.path.insert(0, REPO_ROOT)
from src.simulator import EntrainmentSimulator

class SimulatedEEGAdapter:
    def __init__(self, config: dict):
        self.sim = EntrainmentSimulator(**config)

    async def stream(self):
        while True:
            # Generate synthetic 2s EEG window (Gaussian noise + theta)
            t = np.linspace(0, 2, 500)
            eeg = np.random.randn(7, 500) * 10
            eeg += 5 * np.sin(2 * np.pi * 6 * t)   # theta carrier
            yield eeg
            await asyncio.sleep(2.0)   # match real EEG window rate

    def close(self): pass
```

```python
# webapp/backend/services/datasource/real_eeg.py
import asyncio, numpy as np
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

FRONTAL_CHANNELS = [0, 1, 2, 3, 4, 5, 6]   # map BrainFlow → 7 frontal

class RealEEGAdapter:
    def __init__(self, board_id: int = BoardIds.MUSE_2_BOARD):
        params = BrainFlowInputParams()
        self.board = BoardShim(board_id, params)
        self.board.prepare_session()
        self.board.start_stream()

    async def stream(self):
        FS = BoardShim.get_sampling_rate(self.board.get_board_id())
        n_samples = int(2.0 * FS)
        while True:
            await asyncio.sleep(2.0)
            data = self.board.get_current_board_data(n_samples)
            eeg_rows = [data[ch] for ch in FRONTAL_CHANNELS]
            window = np.array(eeg_rows, dtype=np.float32)   # (7, n_samples)
            if window.shape[1] != 500:
                # Resample to 250 Hz if device runs at different rate
                from scipy.signal import resample
                window = resample(window, 500, axis=1)
            yield window

    def close(self):
        self.board.stop_stream()
        self.board.release_session()
```

### Pattern 3: InferenceService — Model Registry

**What:** Load all model variants once at startup. Expose a uniform `predict(window)` that returns `{"pac": float, "future_pac": float | None, "delta_pac": float | None}`. New models (Transformer, XGBoost) slot in as additional entries in the registry.

**When to use:** Multiple model architectures need to run in parallel for a comparison study AND for real-time inference.

**Trade-offs:** Memory overhead of holding multiple models in RAM. At the sizes involved (EEGNet ~6 KB, TCN ~120 KB) this is irrelevant.

```python
# webapp/backend/services/inference_service.py
import sys, torch, numpy as np
sys.path.insert(0, REPO_ROOT)
from src.eegnet import EEGNet
from temporal_multiscale.realtime_inference import RealtimePACForecaster

class InferenceService:
    def __init__(self, eegnet_path: str, tcn_path: str, scalers_path: str):
        self.eegnet = _load_eegnet(eegnet_path)
        self.forecaster = RealtimePACForecaster(tcn_path, scalers_path)
        self.extra_models: dict = {}   # "xgboost" → fitted pipeline, etc.

    def register(self, name: str, model):
        """Register additional models (XGBoost, Transformer, Ridge) at startup."""
        self.extra_models[name] = model

    def predict(self, window: np.ndarray) -> dict:
        pac = _eegnet_predict(self.eegnet, window)
        spectral = _extract_spectral(window)
        prediction = self.forecaster.step(spectral, pac, ...)
        result = {"pac": pac, "future_pac": None, "delta_pac": None}
        if prediction:
            result["future_pac"] = prediction["future_pac"]
            result["delta_pac"] = prediction["delta_pac"]
        return result
```

### Pattern 4: New Model Architecture Integration

**What:** Transformer and XGBoost models slot into the existing training pipeline without touching `temporal_multiscale/`. They consume the same dataset files produced by `build_multiscale_dataset.py` and are evaluated by the same `sweep_horizons.py` comparison framework.

**When to use:** Architecture comparison study requiring apples-to-apples evaluation.

**Trade-offs:** XGBoost and Transformer use different training loops. Unify via a `BaseTemporalModel` adapter that wraps `.fit()` and `.predict()` behind a common interface.

```python
# temporal_multiscale/model_registry.py  (NEW FILE)
from dataclasses import dataclass
from typing import Protocol
import numpy as np

class TemporalModel(Protocol):
    def fit(self, X_train, y_train): ...
    def predict(self, X_test) -> np.ndarray: ...

# XGBoost variant — uses flattened sequences (lookback * n_features)
class XGBoostTemporalModel:
    def __init__(self, n_estimators=500, max_depth=6):
        import xgboost as xgb
        self.model = xgb.XGBRegressor(n_estimators=n_estimators, max_depth=max_depth,
                                      n_jobs=-1, random_state=42)
    def fit(self, X, y): self.model.fit(X.reshape(len(X), -1), y)
    def predict(self, X): return self.model.predict(X.reshape(len(X), -1))

# Transformer variant — reuses existing (T, F) sequence format
class TransformerTemporalModel(nn.Module):
    # Lightweight: d_model=64, nhead=4, 2 encoder layers, ~100K params
    ...
```

`sweep_horizons.py` gains a `--models` flag to select which architectures to evaluate. The existing TCN remains the default. Results feed the architecture comparison narrative for the paper.

### Pattern 5: Web Audio API Stimulus Control

**What:** The browser's AudioContext generates the 40Hz sine tone. The WebSocket stim command (`action: 0|1`) gates the oscillator. Audio runs entirely client-side — no audio data crosses the network.

**When to use:** Low-latency stimulus delivery with no server-side audio processing needed.

**Trade-offs:** AudioContext must be created after user gesture (browser autoplay policy). Build a "Start Session" button that initializes the context and requests microphone-absent permission. Suspend/resume with `audioCtx.suspend()` / `audioCtx.resume()`.

```typescript
// webapp/frontend/hooks/useAudio.ts
export function useAudio() {
  const ctxRef = useRef<AudioContext | null>(null)
  const oscRef = useRef<OscillatorNode | null>(null)
  const gainRef = useRef<GainNode | null>(null)

  const init = () => {
    const ctx = new AudioContext()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.type = "sine"
    osc.frequency.value = 40          // 40Hz gamma entrainment
    gain.gain.value = 0               // silent until STIMULATE
    osc.connect(gain).connect(ctx.destination)
    osc.start()
    ctxRef.current = ctx
    oscRef.current = osc
    gainRef.current = gain
  }

  const setStim = (active: boolean) => {
    if (!gainRef.current || !ctxRef.current) return
    const now = ctxRef.current.currentTime
    gainRef.current.gain.linearRampToValueAtTime(
      active ? 0.3 : 0,               // ramp prevents click artifacts
      now + 0.05                      // 50ms ramp
    )
  }

  return { init, setStim }
}
```

Frontend WebSocket handler calls `setStim(action === 1)` on each incoming message.

---

## Data Flow

### Real-Time Control Loop (1 Hz tick)

```
[DataSourceAdapter.stream()]
    ↓ yields np.ndarray (7, 500) every 2s
[InferenceService.predict(window)]
    → EEGNet → pac: float
    → RealtimePACForecaster.step() → future_pac, delta_pac
    ↓
[ControllerService.step(pac, prediction)]
    → PersonalizationModule z-score
    → hysteresis decision logic
    → returns StimState (STIMULATE | REST)
    ↓
[SessionStore.log_window()]       ← async DB write
    ↓
[WebSocket push to browser]
    {action, pac, future_pac, z_score, ts}
    ↓
[Browser: AudioEngine.setStim(action)]
[Browser: PACChart.update(pac, future_pac)]
```

### Dual-Mode Session Start

```
POST /session {"mode": "simulated" | "real", "patient_id": "...", "model": "tcn"}
    ↓
SessionStore.create() → session_id
    ↓
GET /ws/session/{session_id}  (browser upgrades to WebSocket)
    ↓
build_adapter(mode):
    "simulated" → SimulatedEEGAdapter(EntrainmentSimulator)
    "real"      → RealEEGAdapter(BrainFlow, board_id from config)
    ↓
inference loop starts (asyncio task)
```

### Session Persistence Data Model

```
sessions
    id TEXT PRIMARY KEY
    patient_id TEXT FK
    mode TEXT              -- "simulated" | "real"
    model TEXT             -- "eegnet_tcn" | "eegnet_tcn_xgboost" etc.
    started_at DATETIME
    ended_at DATETIME
    n_decisions INT
    pct_stim REAL

patients
    id TEXT PRIMARY KEY
    name TEXT
    facility TEXT          -- "Mission Villa" | "Valley Medical" etc.
    notes TEXT

window_log
    id INTEGER PK AUTOINCREMENT
    session_id TEXT FK
    ts REAL                -- unix timestamp
    pac REAL
    future_pac REAL
    delta_pac REAL
    z_score REAL
    action INT             -- 0=REST 1=STIMULATE
```

SQLite is correct for this scale (single-facility demo, <1000 sessions). Upgrade path to PostgreSQL is a one-line SQLAlchemy connection string change.

---

## New vs Modified Components

### Modified (minimal, surgical)

| Existing File | Change | Why |
|---------------|--------|-----|
| `temporal_multiscale/sweep_horizons.py` | Add `--models` flag to include XGBoost/Transformer | Architecture comparison study |
| `temporal_multiscale/` (new file only) | Add `model_registry.py` for new arch wrappers | Avoids touching existing training files |

### New (additive only)

| New Component | Location | Dependencies on Existing |
|---------------|----------|--------------------------|
| FastAPI backend | `webapp/backend/` | Imports `src.eegnet`, `src.controller`, `src.personalization`, `src.simulator`, `temporal_multiscale.realtime_inference` |
| DataSourceAdapter | `webapp/backend/services/datasource/` | `src.simulator` (sim), BrainFlow (real) |
| InferenceService | `webapp/backend/services/inference_service.py` | `src.eegnet`, `temporal_multiscale.realtime_inference` |
| ControllerService | `webapp/backend/services/controller_service.py` | `src.controller`, `src.personalization` |
| SessionStore + DB models | `webapp/backend/db/` | None (SQLAlchemy + aiosqlite) |
| Next.js frontend | `webapp/frontend/` | None (consumes backend WebSocket) |
| `model_registry.py` | `temporal_multiscale/` | XGBoost, PyTorch Transformer |

---

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1-3 concurrent sessions (pilot demo) | Single FastAPI process, SQLite, uvicorn — no changes needed |
| 10-50 sessions (multi-facility) | Keep single process; move SQLite to PostgreSQL; add Redis for WebSocket state if multi-worker |
| 100+ sessions | Multiple uvicorn workers behind nginx; Redis Pub/Sub for session state broadcast; replace SQLite with PostgreSQL |

For the CSEF demo and pilot facility visits, one FastAPI process on localhost or Railway is entirely sufficient. Don't over-engineer for scale that won't materialize by April 9.

---

## Anti-Patterns

### Anti-Pattern 1: Sending audio data over WebSocket

**What people do:** Stream raw audio samples from Python to the browser, or use server-side synthesis.

**Why it's wrong:** Adds network latency to the stimulus delivery path. Even 50ms jitter in 40Hz entrainment timing degrades coupling. The brain doesn't care about the PAC prediction latency — it cares about the stimulus clock jitter.

**Do this instead:** Keep AudioContext and OscillatorNode entirely in the browser. The WebSocket carries only `{action: 0|1}`. The browser gates the oscillator locally. Latency from network to ear is eliminated.

### Anti-Pattern 2: Running EEGNet inference in a synchronous request handler

**What people do:** POST `/predict` with window bytes, run `model(tensor)` synchronously inside the route handler.

**Why it's wrong:** Blocks the FastAPI event loop during inference, even though EEGNet (~6 KB) runs in < 5ms on CPU. Becomes a problem when multiple WebSocket sessions are open simultaneously.

**Do this instead:** Run `model(tensor)` inside `await asyncio.get_event_loop().run_in_executor(None, inference_fn)`. Or, since EEGNet is so small, the < 5ms sync call is acceptable — just don't put it in an HTTP handler that also handles DB writes.

### Anti-Pattern 3: Importing `src/` modules with relative paths from webapp

**What people do:** `from ../src.controller import ClosedLoopController` with fragile relative import chains.

**Why it's wrong:** Breaks when backend is launched from different working directories (Railway, uvicorn, pytest).

**Do this instead:** In `webapp/backend/config.py`, resolve repo root at import time:
```python
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
import sys
sys.path.insert(0, str(REPO_ROOT))
```
All `src.` and `temporal_multiscale.` imports then work regardless of CWD.

### Anti-Pattern 4: Subject-level EEG preprocessing in the web request path

**What people do:** Run the full BIDS `data_loader.py` → `preprocessing.py` pipeline per request, or re-instantiate `PersonalizationModule` per window.

**Why it's wrong:** `PersonalizationModule` holds a 30-second rolling baseline that must persist across windows within a session. Recreating it per request destroys personalization entirely.

**Do this instead:** `ControllerService` is instantiated once per session (tied to WebSocket connection lifetime), not per request. The `PersonalizationModule` lives inside `ControllerService` and accumulates state through the session's full duration.

### Anti-Pattern 5: One WebSocket connection per EEG channel

**What people do:** Open separate WebSocket streams for raw EEG visualization and for PAC/control signals.

**Why it's wrong:** Two connections per session, clock sync complexity, doubled reconnection logic.

**Do this instead:** Multiplex both display data and control signals through one WebSocket message. Add a `raw_eeg` field (downsampled to 50 Hz for display) alongside the control fields. Browser demultiplexes by field name.

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| BrainFlow (Muse 2 / OpenBCI) | Direct Python SDK import in `RealEEGAdapter` | BrainFlow abstracts Bluetooth/USB; unified API across devices. Muse 2 streams at 256 Hz, resample to 250 Hz. OpenBCI Cyton at 250 Hz, matches directly. Confidence: MEDIUM — BrainFlow Muse support requires `muselsl` or BrainFlow native; verify at hardware test time. |
| Web Audio API | Browser-native, no library | AudioContext requires `new AudioContext()` inside a user gesture handler. Safari on iOS requires explicit resume after page visibility change. |
| Chart.js (EEG/PAC visualization) | npm, used in frontend Canvas components | Chart.js streaming plugin (`chartjs-plugin-streaming`) handles rolling time-series well. Alternative: lightweight custom Canvas 2D for raw EEG waveform (Chart.js redraws are expensive at 50 Hz). |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `DataSourceAdapter` ↔ `ControllerService` | `np.ndarray (7, 500)` per 2s | This is the dual-mode seam. Everything upstream of this is hardware-specific; everything downstream is algorithm-specific. |
| `InferenceService` ↔ `ControllerService` | Python function call, dict return | No queue needed at 1 Hz decision rate. |
| `ControllerService` ↔ WebSocket handler | Python function call, `StimState` return | Controller is synchronous; WebSocket handler wraps in `asyncio.to_thread` if model grows. |
| FastAPI backend ↔ Next.js frontend | WebSocket (`ws://`) + REST (`http://`) | WebSocket for real-time loop; REST for session CRUD and metrics export. |
| `webapp/backend` ↔ `src/` + `temporal_multiscale/` | `sys.path` insert + direct import | No packaging needed for demo. If productized, package `src/` as a pip-installable internal library. |

---

## Build Order (Dependencies)

Build in this order to respect import and integration dependencies:

1. **`webapp/backend/db/`** — Models and SessionStore first. No dependencies on research code. Enables session lifecycle before inference exists.

2. **`webapp/backend/services/datasource/simulated.py`** — Simulated adapter before real. This unblocks all frontend and controller development without any hardware.

3. **`webapp/backend/services/inference_service.py` + `controller_service.py`** — Wire up existing `src/` modules. Test that import path resolution works.

4. **`webapp/backend/ws/session_ws.py` + REST routers** — Compose the full backend loop using simulated adapter. Validate end-to-end: session start → window → inference → decision → WebSocket push.

5. **`webapp/frontend/`** — Build UI against the working simulated backend. AudioEngine, PACChart, EEGWaveform, SessionControls.

6. **`temporal_multiscale/model_registry.py` + Transformer/XGBoost training** — Architecture comparison study. Slot new models into `sweep_horizons.py`. Doesn't block the web app at all.

7. **`webapp/backend/services/datasource/real_eeg.py`** — Real hardware adapter last. Requires physical device. All other components are already tested against simulated data, so hardware integration is an adapter swap only.

---

## Sources

- [FastAPI WebSockets documentation](https://fastapi.tiangolo.com/advanced/websockets/) — HIGH confidence
- [BrainFlow supported boards and Python SDK](https://brainflow.readthedocs.io/en/stable/SupportedBoards.html) — HIGH confidence
- [MDN Web Audio API — Advanced techniques](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Advanced_techniques) — HIGH confidence
- [EEG-PatchFormer EMBC-2025](https://github.com/yi-ding-cs/EEG-PatchFormer) — MEDIUM confidence (Transformer EEG architecture reference)
- [TCFormer: Temporal Convolutional Transformer for EEG](https://www.nature.com/articles/s41598-025-16219-7) — MEDIUM confidence
- [Muse LSL Python integration](https://github.com/alexandrebarachant/muse-lsl) — MEDIUM confidence (older library; BrainFlow is preferred)
- [Real-time EEG-guided binaural beat study](https://www.mdpi.com/2673-9488/5/4/44) — MEDIUM confidence (prior art for closed-loop audio stimulus)
- [FastAPI WebSocket real-time AI inference](https://medium.com/@kaushalsinh73/fastapi-websockets-real-time-ai-inference-at-scale-699d3c019339) — MEDIUM confidence

---

*Architecture research for: Closed-loop 40Hz entrainment web platform (v3.0)*
*Researched: 2026-03-20*
