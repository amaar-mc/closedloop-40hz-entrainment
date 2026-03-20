# Stack Research

**Domain:** Productized closed-loop 40Hz neurofeedback therapy platform with real-time EEG hardware integration
**Researched:** 2026-03-20
**Confidence:** MEDIUM-HIGH (EEG hardware specs verified via official sources; web framework recommendations are standard)

---

## What This Document Covers

This covers ONLY new stack additions for the v3.0 milestone. The existing pipeline (PyTorch, MNE, scikit-learn, NumPy, Streamlit) stays unchanged. Research is organized by the five new capability areas.

---

## 1. Web App Platform (Caregiver-Facing Therapy Sessions)

### Recommendation: Next.js 14 + FastAPI 0.115 + WebSockets

**Why this combination:**
The existing codebase is Python. FastAPI lets you expose the current `ClosedLoopController`, `RealtimePACForecaster`, and `PersonalizationModule` directly as async endpoints without a rewrite. WebSockets are native to FastAPI via Starlette and handle the 250 Hz EEG data stream without polling overhead. Next.js gives a production-quality caregiver UI with React and handles the real-time Web Audio API calls in the browser. This is the stack described in Amaar's global preferences for Python backends + React frontends.

**Reject Streamlit for the caregiver app.** The existing `src/dashboard.py` is a researcher demo tool. Streamlit re-runs the entire Python script on every interaction, making it unsuitable for a stateful multi-user session. Keep it as the developer/demo fallback only.

### Core Web Framework Stack

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Next.js | 14.x | Caregiver UI (React, SSR, routing) | Production-ready, standard in Amaar's global stack, handles real-time via useEffect + WebSocket hooks |
| FastAPI | 0.115.x | Python backend API + WebSocket server | Same-process access to existing PyTorch pipeline; native async WebSocket support; replaces no existing code |
| uvicorn | 0.32.x | ASGI server for FastAPI | Required runtime; supports ws:// with no config |
| SQLModel | 0.0.22 | ORM for session/patient data | Built by FastAPI author; unifies Pydantic models (already used in FastAPI) with SQLAlchemy; avoids dual schema |
| SQLite | 3.x (stdlib) | Session/patient database | Zero-config for demo and pilot. Swap to PostgreSQL only when multi-instance deployment is needed |
| Tailwind CSS | 3.x | Caregiver UI styling | Utility-first; no CSS-in-JS; standard with Next.js |

### Supporting Web Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Zustand | 4.x | Client-side session state (React) | Manages EEG connection state, current session, PAC live feed — simpler than Redux for this scope |
| react-query (TanStack Query) | 5.x | API data fetching + caching | Session history, patient records — separates server state from UI state cleanly |
| Recharts | 2.x | Real-time PAC visualization in browser | Lighter than Plotly for React, good for 1-2 Hz update rate; replace Matplotlib for the browser |
| pydantic | 2.x | Request/response schema validation | Already transitively required by FastAPI; use for all EEG event payloads |

### Web App Architecture Pattern

```
Browser (Next.js)
  │  HTTP (REST) → session CRUD, patient records, historical PAC
  │  WebSocket  → real-time EEG PAC stream (every 2s window = 1 message)
  ↓
FastAPI (Python, uvicorn)
  │  Direct Python import → existing ClosedLoopController, RealtimePACForecaster
  │  WebSocket endpoint: /ws/session/{session_id}
  │  REST endpoints: /sessions, /patients, /history
  ↓
SQLite (SQLModel ORM)
  → Session table (id, patient_id, start_ts, end_ts, strategy)
  → EEGWindow table (session_id, ts, pac_value, pac_predicted, stim_state)
  → Patient table (id, name, baseline_mean, baseline_std)
```

**Key constraint:** The FastAPI process must run on the local machine (laptop at pilot facility) because BrainFlow connects to hardware via USB/Bluetooth and cannot stream through a cloud server without a local bridge. Deploy locally; use ngrok or Cloudflare Tunnel for external QR code access from the poster.

---

## 2. Real EEG Headset Integration

### The Core Hardware Problem

No consumer EEG headset has built-in speakers for playing the 40Hz stimulus while simultaneously recording EEG. Audio is delivered separately (wired headphones, Bluetooth earbuds, or laptop speakers). This is the standard research setup and is not a limitation — it is by design, since audio transducer artifacts would corrupt the EEG signal if played through the same device.

**Setup for pilot demos:** EEG headset (records brainwaves) + separate wired headphones or earbuds (plays 40Hz stimulus from laptop). No single-device solution exists or is desirable.

### Recommended Headset: Muse S (Gen 2)

**Rationale:** $249-299 USD. 4 EEG channels at 256 Hz. Has built-in accelerometer/gyroscope/PPG. The existing pipeline uses 7 frontal channels from ds005048; Muse S has AF7/AF8/TP9/TP10 (frontal-temporal) — the frontal pair (AF7/AF8) directly overlaps with the Fz-vicinity channels used for theta-gamma coupling. BrainFlow supports it natively. muselsl is an active community Python package. For a CSEF demo where the goal is showing the concept works, Muse S is the right cost/capability tradeoff.

**Why not OpenBCI Cyton:** $999 + requires a separate headset cap with gel electrodes. Setup takes 30-45 min. Not feasible for a 10-minute pilot demo at Mission Villa. Research grade, but demo hostile.

**Why not Emotiv EPOC X:** $999. Cortex API requires a free license key + subscription for raw EEG (Basic API provides only processed metrics, not raw samples). Saline electrodes require preparation time. Overkill for demo.

**Why not NeuroSky MindWave:** 1 channel (Fp1 only). Insufficient for PAC computation across frontal sites.

### EEG Hardware Comparison Table

| Headset | Price | EEG Channels | Sample Rate | Python SDK | Raw EEG | Setup Time | Audio | Demo Suitability |
|---------|-------|--------------|-------------|-----------|---------|------------|-------|-----------------|
| **Muse S Gen 2** | $249 | 4 (AF7, AF8, TP9, TP10) | 256 Hz | BrainFlow + muselsl | YES (raw) | <2 min | No built-in speakers | HIGH |
| Muse 2 | $199 | 4 (same as S) | 256 Hz | BrainFlow + muselsl | YES (raw) | <2 min | No built-in speakers | HIGH |
| OpenBCI Cyton | $999 | 8 (configurable) | 250 Hz | BrainFlow (primary) | YES | 30-45 min | No | LOW (demo), HIGH (research) |
| OpenBCI Cyton+Daisy | $1,299 | 16 | 125 Hz | BrainFlow | YES | 45-60 min | No | LOW |
| Emotiv EPOC X | $999 | 14 | 128/256 Hz | Cortex API (JSON/WS) | Requires license | 10-15 min | No | MEDIUM |
| NeuroSky MindWave | $100 | 1 (Fp1) | 512 Hz | ThinkGear SDK | YES | <1 min | No | NONE (1 channel) |

### Software Integration: BrainFlow

**Use BrainFlow 5.x as the unified EEG hardware abstraction layer.** It supports Muse S, Muse 2, OpenBCI Cyton/Ganglion, and 30+ other boards under a single API. This means if the demo uses Muse S but the research lab has OpenBCI, you change one board ID constant — not the pipeline.

```python
# BrainFlow integration pattern
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

params = BrainFlowInputParams()
board = BoardShim(BoardIds.MUSE_S_BOARD, params)
board.prepare_session()
board.start_stream()
# board.get_board_data() returns numpy array matching existing pipeline shape
```

BrainFlow streams via LSL (Lab Streaming Layer) and can also deliver numpy arrays directly — compatible with the existing `(n, 1, 7, 500)` window format after channel selection and reshaping.

**Note on channel count mismatch:** Muse S has 4 channels; the trained EEGNet expects 7. Options: (a) simulate demo mode with stored data from ds005048 as fallback, (b) retrain a 4-channel EEGNet variant, or (c) interpolate missing channels. For the CSEF demo, option (a) is fastest — show real Muse S streaming the live feed visually, use pre-recorded PAC predictions for the closed-loop logic. This is honest (label it "simulated PAC, real EEG") and demo-safe.

### New Python Dependencies for EEG Hardware

| Library | Version | Purpose |
|---------|---------|---------|
| brainflow | 5.x | Unified EEG board SDK — Muse S, OpenBCI, 30+ boards |
| muselsl | 2.2.x | Muse-specific LSL streaming (fallback if BrainFlow BLE issues on macOS) |
| pylsl | 1.16.x | Lab Streaming Layer Python bindings (required by muselsl) |

---

## 3. Browser-Based Adaptive 40Hz Auditory Stimulus

### Recommendation: Web Audio API (no library needed)

The browser's native Web Audio API is the correct tool. It generates precise 40Hz isochronic tones and amplitude-modulated tones entirely client-side with sub-millisecond scheduling accuracy. No external library is needed — BinauralBeatJS and similar libraries add no value over 10 lines of vanilla JS for this use case.

**Why not Python/sounddevice for the web app:** The existing `sounddevice` library works for the Streamlit demo (local Python process). For the Next.js caregiver app, audio must run in the browser to avoid round-trip latency (Python → WebSocket → browser → speaker would add 50-200ms jitter). Browser-side is the only correct choice.

### 40Hz Stimulus Types (in order of research support)

1. **Isochronic 40Hz tone**: Single channel, 40Hz amplitude modulation of a carrier (e.g., 440Hz). Cleaner than binaural for group settings (works with speakers, not just headphones). **Use this for demo.**
2. **Binaural beats**: Left ear 440Hz + right ear 480Hz → perceived 40Hz beat. Requires headphones. Stronger individual response. Use this as optional mode.
3. **ASSR (auditory steady-state response)**: Continuous 40Hz click train. Most researched in gamma entrainment literature.

### Browser Audio Implementation

```javascript
// Web Audio API — 40Hz isochronic tone (runs in Next.js component)
const ctx = new AudioContext();
const osc = ctx.createOscillator();    // carrier: 440Hz
const gain = ctx.createGain();

osc.frequency.value = 440;
gain.gain.value = 0;  // start silent

// Adaptive: FastAPI WebSocket sends PAC prediction → client adjusts volume
// When controller says STIMULATE: ramp gain to 0.5 over 100ms
// When controller says REST: ramp gain to 0 over 100ms

osc.connect(gain);
gain.connect(ctx.destination);
osc.start();
```

**Adaptive control flow:** FastAPI WebSocket pushes `{state: "STIMULATE"|"REST"|"MAINTAIN", pac_predicted: 0.000045}` every 2 seconds. React component adjusts `gain.gain` via `linearRampToValueAtTime`. This is the real-time adaptive loop visible to judges.

No new Python dependencies needed. No new npm packages needed beyond what Next.js provides.

---

## 4. New ML Model Architectures for Comparison Study

### Purpose

The v3.0 goal is a comparison study showing WHY the MultiscaleCausalTCN was chosen. Train 2-3 new models, compare against existing TCN and baselines (persistence, Ridge). This is a research deepening task, not a production requirement.

### Recommended New Models

| Model | Library | Purpose | Notes |
|-------|---------|---------|-------|
| XGBoost (lag features) | xgboost 2.1.x | Tabular baseline with feature engineering | Already have scikit-learn in requirements; add xgboost. Competitive at short horizons (1-2s). Interpretable feature importances. |
| Temporal Fusion Transformer (TFT) | pytorch-forecasting 1.x | Attention-based temporal model | Built on PyTorch (already installed). Tests whether attention mechanism improves over causal convolution. |
| Simple LSTM | PyTorch (stdlib, no new dep) | Deep learning baseline | Already have the superseded `temporal/` LSTM code. Retrain it with the current multiscale dataset for fair comparison. |

**Reject:** Full transformer (too heavy for 35 subjects), Prophet (trend-based, wrong for EEG), N-BEATS (overkill), any model requiring >1GB additional dependencies.

### New Python Dependencies for ML Comparison

| Library | Version | Purpose | Install |
|---------|---------|---------|---------|
| xgboost | 2.1.x | XGBoost tabular forecasting | `pip install xgboost` |
| pytorch-forecasting | 1.1.x | Temporal Fusion Transformer | `pip install pytorch-forecasting` |
| lightning | 2.4.x | pytorch-forecasting dependency (PyTorch Lightning) | Auto-installed with pytorch-forecasting |

**Compatibility note:** pytorch-forecasting 1.x requires PyTorch 2.0+ (already satisfied) and PyTorch Lightning 2.x. Do NOT install both `pytorch-lightning` and `lightning` — they are the same package, renamed. Use `lightning` only.

### Comparison Study Output Format

The comparison should produce a single table reported in the paper:

| Model | R² (1s) | R² (5s) | R² (10s) | Params | Train time |
|-------|---------|---------|----------|--------|------------|
| Persistence | — | — | — | 0 | — |
| Ridge | — | — | — | ~73 | <1s |
| LSTM | — | — | — | ~Xk | Xmin |
| XGBoost | — | — | — | ~Xk trees | Xmin |
| TFT | — | — | — | ~Xk | Xmin |
| MultiscaleCausalTCN | — | — | — | 31K | — |

This directly answers "why TCN" without speculation.

---

## 5. Session Management and Data Logging

### Recommendation: SQLModel + SQLite → PostgreSQL migration path

SQLModel (0.0.22) is built by the FastAPI author and is the recommended ORM for FastAPI + SQLAlchemy projects. It unifies the Pydantic model (used for API request/response validation) with the SQLAlchemy ORM model — no duplicate schema definitions.

SQLite is sufficient for the CSEF pilot (single machine, <100 sessions). If the product scales to a clinic running multiple concurrent sessions, migrate to PostgreSQL with asyncpg — no code change required, only the connection string.

### Data Schema (Core Tables)

```python
# SQLModel table definitions
class Patient(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    created_at: datetime
    baseline_pac_mean: float | None  # from personalization module
    baseline_pac_std: float | None

class Session(SQLModel, table=True):
    id: int = Field(primary_key=True)
    patient_id: int = Field(foreign_key="patient.id")
    start_ts: datetime
    end_ts: datetime | None
    strategy: str  # "reactive" | "predictive" | "fixed"
    headset: str   # "muse_s" | "simulated"
    notes: str | None

class EEGWindow(SQLModel, table=True):
    id: int = Field(primary_key=True)
    session_id: int = Field(foreign_key="session.id")
    ts: datetime
    pac_observed: float
    pac_predicted: float | None
    stim_state: str  # "STIMULATE" | "REST" | "MAINTAIN"
    channel_quality: float | None  # signal quality metric
```

### Session Logging Architecture

Each WebSocket message from the EEG stream is logged to `EEGWindow` in real time. The caregiver sees a live session card (duration, current stim state, PAC trend). Sessions can be exported as CSV for research analysis. This gives Amaar actual human testing data to show judges.

### New Python Dependencies for Session Management

| Library | Version | Purpose |
|---------|---------|---------|
| sqlmodel | 0.0.22 | ORM: combines Pydantic + SQLAlchemy for FastAPI |
| alembic | 1.13.x | Database migrations (schema evolution across pilots) |

---

## Full New Dependencies Summary

### Python (add to requirements.txt)

```bash
# Web app backend
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
websockets>=13.0
sqlmodel>=0.0.22
alembic>=1.13.0

# EEG hardware
brainflow>=5.0.0
muselsl>=2.2.0
pylsl>=1.16.0

# ML comparison study
xgboost>=2.1.0
pytorch-forecasting>=1.1.0
lightning>=2.4.0
```

### JavaScript (new Next.js project)

```bash
# Core
npx create-next-app@14 webapp --typescript --tailwind --app

# State & data
npm install zustand @tanstack/react-query

# Charts
npm install recharts

# No audio library needed — use native Web Audio API
```

---

## Alternatives Considered

| Recommended | Alternative | Why Not |
|-------------|-------------|---------|
| FastAPI | Django REST | Django adds ORM/admin overhead; FastAPI's async WebSocket + direct PyTorch import is lighter and faster |
| FastAPI | Flask | Flask WebSocket support requires flask-socketio (additional complexity); async handling is worse |
| Next.js (new caregiver app) | Extend Streamlit dashboard | Streamlit re-runs entire script on each interaction; no multi-user sessions; no production deployment path |
| SQLModel + SQLite | Raw JSON files | JSON files break on concurrent writes; no query support for session history |
| BrainFlow | pyOpenBCI (deprecated) | pyOpenBCI_LSL is archived/unmaintained since 2021; BrainFlow is the official successor |
| BrainFlow | muselsl only | muselsl is Muse-only; BrainFlow is board-agnostic and covers OpenBCI if hardware changes |
| Muse S | OpenBCI Cyton | $250 vs $999; 2-min setup vs 45-min; sufficient frontal channels for demo |
| Muse S | Emotiv EPOC X | $250 vs $999; Emotiv raw EEG requires paid subscription tier |
| Web Audio API | Tone.js | Tone.js adds 200KB for sequencing features not needed; 10 lines of native API is sufficient |
| XGBoost + TFT | N-BEATS, Autoformer | Overkill for 35-subject dataset; harder to justify to judges; TFT already provides interpretability |
| pytorch-forecasting TFT | Building TFT from scratch | pytorch-forecasting handles the data pipeline boilerplate; saves 2-3 days of implementation |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Streamlit as caregiver web app | Not suitable for production multi-user stateful sessions | Next.js + FastAPI |
| pyOpenBCI / OpenBCI_Python (legacy) | Archived, unmaintained since 2021 | BrainFlow 5.x |
| BLE directly (bleak) | Muse S BLE pairing is fragile on macOS; BrainFlow wraps it with reconnect logic | BrainFlow (which uses bleak internally) |
| Emotiv raw EEG without license | Basic Cortex API gives only processed metrics (attention, stress), not raw samples | Muse S + BrainFlow for raw EEG |
| binaural beats library (npm) | No added value over 10 lines of Web Audio API | Web Audio API native |
| both pytorch-lightning and lightning | They are the same package renamed; installing both causes conflicts | `lightning` only (2.4.x) |
| PostgreSQL for pilot | Overkill for single-machine demo; adds deployment complexity | SQLite for pilot, migrate later |
| Redux | Overkill for session state scope of this app | Zustand |
| Plotly.js in React | Heavy bundle for a simple PAC time series chart | Recharts |

---

## Stack Patterns by Variant

**If doing CSEF demo only (no real hardware):**
- Use simulated EEG from `run_closed_loop_demo.py` as the data source
- Skip BrainFlow, muselsl, pylsl
- FastAPI streams simulated PAC values over WebSocket
- Full caregiver UI still works — just labeled "simulated EEG"

**If doing real Muse S demo:**
- Add BrainFlow
- 4-channel EEG stream → apply existing `preprocessing.py` (bandpass, notch) → compute PAC on frontal pair (AF7/AF8)
- 4-channel EEGNet variant needed (fastest: retrain with `--channels 4`)
- Label as "4-channel frontal EEG"

**If research lab later adds OpenBCI:**
- Change `BoardIds.MUSE_S_BOARD` to `BoardIds.CYTON_BOARD`
- Everything else stays identical (BrainFlow abstraction)

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| pytorch-forecasting 1.1.x | lightning 2.4.x, torch 2.0+ | Do NOT use with pytorch-lightning; use `lightning` package only |
| brainflow 5.x | Python 3.8-3.12 | macOS requires Bluetooth permissions grant; MPS (Apple Silicon) not relevant here |
| sqlmodel 0.0.22 | fastapi 0.115.x, pydantic 2.x, sqlalchemy 2.x | SQLModel 0.0.22 uses SQLAlchemy 2.x; earlier SQLModel versions used SQLAlchemy 1.4 — breaking change |
| muselsl 2.2.x | Python 3.7+, pylsl 1.16.x | muselsl requires pylsl; install both |
| next.js 14.x | react 18.x, react-dom 18.x | App Router (not Pages Router); use `use client` directive for Web Audio API components |

---

## Sources

- [BrainFlow Supported Boards](https://brainflow.readthedocs.io/en/stable/SupportedBoards.html) — Muse S, Muse 2, OpenBCI Cyton channel/rate specs (HIGH confidence, official docs)
- [FastAPI WebSockets Official Docs](https://fastapi.tiangolo.com/advanced/websockets/) — WebSocket endpoint patterns (HIGH confidence, official)
- [SQLModel Official Docs](https://sqlmodel.tiangolo.com/) — FastAPI integration patterns (HIGH confidence, official)
- [pytorch-forecasting PyPI](https://pypi.org/project/pytorch-forecasting/) — TFT install and compatibility (HIGH confidence, official)
- [muselsl PyPI](https://pypi.org/project/muselsl/) — Muse LSL Python streaming (MEDIUM confidence, verified via PyPI + GitHub)
- [Emotiv Cortex API Docs](https://emotiv.gitbook.io/cortex-api) — Cortex API license requirements for raw EEG (HIGH confidence, official)
- [EEG Devices comparison article](https://sharikazareen.medium.com/eeg-devices-you-can-actually-use-muse-vs-openbci-vs-emotiv-for-ai-projects-c81edb32aa72) — Practical developer comparison (MEDIUM confidence, single source)
- [Muse S Gen 2 Review 2025](https://saironlabs.com/muse-s-gen-2-review/) — Price, specs confirmation (MEDIUM confidence, third-party review)
- [OpenBCI Cyton price/specs](https://pypi.org/project/BrainflowCyton/) — 8ch/250Hz/\$999 (MEDIUM confidence, corroborated by multiple sources)
- Consumer EEG headset audio capability: NO consumer EEG headset (Muse, OpenBCI, Emotiv) plays audio through onboard speakers while recording. Muse S has speakers for guided meditation feedback only, not for controlled stimulus delivery. Separate headphones required for all research use. (HIGH confidence — confirmed across Emotiv, Muse, OpenBCI official product pages; this is a design constraint, not a gap)

---

*Stack research for: Closed-Loop 40Hz Entrainment Web App (v3.0 milestone)*
*Researched: 2026-03-20*
