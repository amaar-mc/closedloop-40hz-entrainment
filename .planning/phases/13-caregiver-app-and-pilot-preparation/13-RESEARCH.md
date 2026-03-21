# Phase 13: Caregiver App and Pilot Preparation - Research

**Researched:** 2026-03-20
**Domain:** Streamlit app development, deployment, QR code generation, presentation materials
**Confidence:** HIGH

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| APP-01 | Patient profiles — create/select patient, view session history with per-session metrics | JSON file storage on Streamlit Cloud filesystem (ephemeral, confirmed writable); `st.session_state` for in-session state; profile data committed to repo as seed JSON |
| APP-02 | Session management — start/stop therapy sessions, log per-window PAC and stimulus decisions, session completion summary with plain-language metrics | Existing `SimulatedEEGAdapter` + `StreamingFeatureExtractor` + `EEGNet` 4ch pipeline confirmed working via `tests/test_simulated_session.py`; summary dict pattern matches `ClosedLoopController.get_history()` |
| APP-03 | Caregiver-friendly UI — plain-language labels, volume slider, hardware status indicator, dual-mode toggle | `st.slider`, `st.toggle`, `st.metric`, `st.columns` — all in Streamlit 1.55.0 (installed); label translation layer maps PAC → "Brain Sync Level" |
| APP-04 | Real-time PAC trend chart and adaptive 40 Hz auditory stimulus with visual indicator | `st.line_chart` / matplotlib for PAC trend; `st.audio(bytes, loop=True, autoplay=True)` for 40 Hz tone (confirmed in Streamlit 1.35+); `sounddevice` only on local desktop, NOT on Cloud |
| APP-05 | Streamlit Cloud deployment with working QR code | Model files are tiny (128–136 KB), no LFS needed; `test_data.npz` (75 MB) must be excluded — app uses simulated EEG only; `requirements.txt` already exists; `.streamlit/config.toml` needed |
| PRES-01 | 1-minute elevator pitch script | Content research only — no code implementation |
| PRES-02 | One-page flyer PDF with QR code | `qrcode` + `Pillow` for QR generation; flyer layout in Markdown/LaTeX/reportlab; print-ready PDF |
| PRES-03 | Clinical roadmap document | Content writing only; existing `docs/` structure |
| PRES-04 | Pilot feedback Google Form QR code on poster | Google Form creation (manual); QR generated from Form URL using `qrcode` library |

</phase_requirements>

---

## Summary

Phase 13 builds a caregiver-facing Streamlit app and all CSEF presentation materials. The app is
a new file (`caregiver_app.py`) — distinct from `demo.py` which is the research-audience replay
tool. The caregiver app runs exclusively in simulated-EEG mode using the already-verified
4-channel pipeline (`SimulatedEEGAdapter` → `StreamingFeatureExtractor` → `EEGNet 4ch` →
`PredictiveLookAheadController`). This sidesteps the 75 MB `test_data.npz` deployment problem
entirely.

The deployment path is straightforward: all model files are under 136 KB (well within GitHub's
100 MB limit and Streamlit Cloud's 1 GB app limit). The one critical audio constraint is that
`sounddevice` works only on a local machine — on Streamlit Cloud the server has no audio output
device. The solution is `st.audio(bytes, loop=True, autoplay=True)` which plays a WAV-encoded
40 Hz tone in the browser. This is the correct pattern for cloud deployment.

Presentation materials (PRES-01 through PRES-04) are pure content tasks. The QR code for both
the app URL and the Google Form feedback URL are generated with the `qrcode` Python library
(already installable, no new dependency). A one-page PDF flyer can be authored in Markdown and
converted with `pandoc` + LaTeX, or built programmatically with `reportlab`.

**Primary recommendation:** Build `caregiver_app.py` as a multi-page Streamlit app using
`st.session_state` for in-session data and a committed JSON file for seed patient profiles.
Audio uses `st.audio` with `loop=True, autoplay=True` on a programmatically generated WAV
buffer. Deploy to Streamlit Cloud by connecting the GitHub repo directly — no data files in
the repo, only model weights and `scalers.npz`.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| streamlit | 1.55.0 (installed) | App UI framework | Already in project; cloud-deployable |
| numpy | >=1.24.0 (installed) | Audio buffer generation, data arrays | Already in project |
| torch | >=2.0.0 (installed) | 4ch EEGNet inference | Already in project |
| scipy | >=1.11.0 (installed) | WAV encoding via `scipy.io.wavfile` | Already in project |
| brainflow | >=5.21.0 (installed) | `SimulatedEEGAdapter` EEG source | Already in project |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| qrcode[pil] | latest (~8.x) | QR code PNG generation for app URL and Form URL | PRES-02, PRES-04 |
| Pillow | >=9.0 (installed transitively) | PNG image manipulation for QR codes in flyer | Required by qrcode |
| reportlab | 4.x | Programmatic PDF generation for flyer | If pandoc not available |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `st.audio(loop=True)` | `sounddevice` callback | sounddevice works locally, NOT on Streamlit Cloud — server has no audio output |
| JSON file (seed profiles) | SQLite via `st.connection` | SQLite more robust but overkill; seed profiles are read-mostly and small |
| reportlab PDF | pandoc + LaTeX | pandoc not guaranteed on deploying machine; reportlab is pure Python pip install |

**Installation (new dependencies only):**
```bash
pip install qrcode[pil] reportlab
```

---

## Architecture Patterns

### Recommended Project Structure

```
caregiver_app.py              # Streamlit entrypoint — multi-page navigation
data/
  caregiver_profiles.json     # Seed patient profiles (committed, read-only template)
.streamlit/
  config.toml                 # Theme, server config for Cloud deployment
models/muse_4ch/
  best_eegnet_4ch.pth         # 36 KB — committed to repo, no LFS needed
  best_multiscale_tcn_4ch_lb20_hz5_ts1.pth  # 128 KB — committed
data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1/
  scalers.npz                 # 4 KB — committed
docs/
  flyer/
    FACILITY_FLYER.md         # Flyer source
    facility_flyer.pdf        # Print-ready PDF
  ELEVATOR_PITCH.md           # PRES-01
  CLINICAL_ROADMAP.md         # PRES-03
scripts/
  generate_qr_codes.py        # Generates QR PNGs for app URL and Google Form URL
  generate_flyer_pdf.py       # Produces facility_flyer.pdf from template
```

### Pattern 1: Multi-Page Navigation with Session State

**What:** A single `caregiver_app.py` file manages multiple "pages" (Welcome, Patient Select,
Session, Summary) using `st.session_state.page` as the router.

**When to use:** When you need a linear flow (select patient → run session → view summary) where
back/forward must be controlled, not Streamlit's native multi-page sidebar.

**Example:**
```python
# Source: Streamlit session_state docs + existing demo.py pattern
import streamlit as st

if "page" not in st.session_state:
    st.session_state.page = "welcome"

if st.session_state.page == "welcome":
    render_welcome()
elif st.session_state.page == "patient_select":
    render_patient_select()
elif st.session_state.page == "session":
    render_session()
elif st.session_state.page == "summary":
    render_summary()
```

This mirrors the exact `configure` → `running` pattern in `demo.py` (lines 535–815), so the
transition is well-understood.

### Pattern 2: Audio via st.audio with Generated WAV Bytes

**What:** Generate a 40 Hz click-train WAV buffer at startup, cache it with `@st.cache_data`,
and display it with `st.audio(wav_bytes, format="audio/wav", loop=True, autoplay=True)`.

**When to use:** Cloud deployment where `sounddevice` is unavailable. The browser's audio
player handles the looping.

**Example:**
```python
# Source: st.audio docs + scipy.io.wavfile
import io
import numpy as np
from scipy.io import wavfile
import streamlit as st

@st.cache_data
def make_40hz_tone(duration_sec: float = 1.0, sample_rate: int = 44100) -> bytes:
    """Generate one second of 40 Hz click-train, loopable as WAV bytes."""
    period = sample_rate // 40  # 1102 samples per period
    click_n = int(0.001 * sample_rate)  # 1 ms click
    period_buf = np.zeros(period, dtype=np.float32)
    t = np.arange(click_n) / sample_rate
    period_buf[:click_n] = 0.3 * np.sin(2 * np.pi * 1000 * t).astype(np.float32)
    n_periods = int(duration_sec * sample_rate / period)
    audio = np.tile(period_buf, n_periods).astype(np.float32)
    buf = io.BytesIO()
    wavfile.write(buf, sample_rate, audio)
    return buf.getvalue()

# In session render:
if stimulating:
    wav = make_40hz_tone()
    st.audio(wav, format="audio/wav", loop=True, autoplay=True)
```

**Critical caveat:** `st.audio` with `autoplay=True` re-renders on every `st.rerun()`, which
causes the audio to restart. The workaround is to only render the `st.audio` widget when the
stimulus state _changes_ (add `st.empty()` placeholder and only update it on state transition),
or accept the browser-level audio restart — which is acceptable for a demo app.

### Pattern 3: Patient Profiles with JSON File

**What:** Load a seed `caregiver_profiles.json` at startup; hold current-session state in
`st.session_state`; write new session records back to the JSON file.

**Important constraint:** Streamlit Cloud's filesystem is writable but **ephemeral** — any
writes are lost when the container restarts. For a CSEF demo this is acceptable: the seed
profiles provide the "history" judges see, and live-session writes during the demo persist
for the duration of the session. The app should commit a pre-populated JSON with 2–3 realistic
patient entries.

```python
import json
from pathlib import Path
import streamlit as st

PROFILES_PATH = Path(__file__).parent / "data" / "caregiver_profiles.json"

@st.cache_data
def load_profiles() -> dict:
    if PROFILES_PATH.exists():
        return json.loads(PROFILES_PATH.read_text())
    return {"patients": []}

def save_session(patient_id: str, session_record: dict) -> None:
    """Append a session record. Ephemeral on Cloud — acceptable for demo."""
    profiles = load_profiles()
    # Mutate and persist within this container's lifetime
    for p in profiles["patients"]:
        if p["id"] == patient_id:
            p.setdefault("sessions", []).append(session_record)
            break
    PROFILES_PATH.write_text(json.dumps(profiles, indent=2))
    st.cache_data.clear()   # Invalidate cache so next load picks up new data
```

### Pattern 4: Label Translation Layer

**What:** A simple `dict` mapping internal metric names to caregiver-facing plain English.
No new framework needed.

```python
LABEL_MAP = {
    "pac": "Brain Sync Level",
    "pac_trend": "Neural Entrainment Trend",
    "stim_fraction": "Therapy Active (%)",
    "z_score": "Response to Therapy",
    "session_duration": "Session Duration",
    "alignment": "Targeting Accuracy",
}

def label(key: str) -> str:
    return LABEL_MAP.get(key, key.replace("_", " ").title())
```

### Pattern 5: QR Code Generation

```python
# Source: qrcode PyPI docs
import qrcode
from PIL import Image

def make_qr(url: str, output_path: str) -> None:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
```

### Anti-Patterns to Avoid

- **Using `sounddevice` in the cloud app:** It will silently fail or crash on Streamlit Cloud.
  Use `st.audio` for the caregiver app; `sounddevice` is fine in `demo.py` which is local-only.
- **Loading `test_data.npz` in the caregiver app:** 75 MB, not in the repo (gitignored for good
  reason), and the caregiver app should use simulated EEG. Do not add this file to the repo.
- **Calling `st.rerun()` inside a tight loop with `st.audio` autoplay:** Audio restarts on each
  rerun. Structure the session loop to batch updates and minimize unnecessary reruns.
- **Multi-threaded session loop without locking:** `demo.py` uses `threading.RLock()` around
  matplotlib. If the caregiver app uses background threads, apply the same pattern.
- **Committing raw EEG data to the repo for deployment:** The `data/` directory is 1.1 GB.
  Only commit `models/muse_4ch/` (300 KB total) and `data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1/scalers.npz` (4 KB).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| 40 Hz audio stimulus (cloud) | Custom WebSocket audio server | `st.audio(wav_bytes, loop=True, autoplay=True)` | Browser handles playback; no server-side audio device needed |
| QR code generation | Manual bitmap drawing | `qrcode[pil]` library | Error correction, sizing, format compliance handled |
| PDF flyer | Custom HTML-to-PDF pipeline | `reportlab` or `pandoc` | Reliable cross-platform PDF generation |
| PAC trend chart | Custom canvas rendering | `st.line_chart` or `st.pyplot` | Already in project (demo.py uses `plt`); no extra dependency |
| EEG simulation | Write synthetic EEG generator | `SimulatedEEGAdapter` (BrainFlow SYNTHETIC_BOARD) | Already tested and verified in `tests/test_simulated_session.py` |
| Feature extraction | Re-implement spectral features | `StreamingFeatureExtractor` from `src/streaming/feature_extractor.py` | Verified to match offline pipeline within 1e-4 |

**Key insight:** The entire inference pipeline (EEG → features → PAC → stimulus decision) is
already built, tested, and working. Phase 13 only adds the caregiver UI wrapper around it.

---

## Common Pitfalls

### Pitfall 1: sounddevice Fails Silently on Streamlit Cloud

**What goes wrong:** `sounddevice` imports fine (it's in `requirements.txt`) but
`sd.OutputStream(...)` either raises an error or produces no audio because the server
container has no audio output device.

**Why it happens:** `sounddevice` wraps PortAudio, which requires a hardware audio device.
Streamlit Cloud containers have no such device.

**How to avoid:** In `caregiver_app.py`, use only `st.audio`. Remove `sounddevice` from any
import path in the new app file. The existing `demo.py` already has a `_NoOpAudioEngine`
fallback pattern that demonstrates awareness of this issue.

**Warning signs:** `sounddevice` raises `sounddevice.PortAudioError: Error querying device -1`
or produces no audio on deploy.

### Pitfall 2: test_data.npz in the Deployment Repo

**What goes wrong:** The caregiver app accidentally imports or references `test_data.npz`.
The file is 75 MB and the entire `data/` directory is 1.1 GB — both exceed reasonable GitHub
limits.

**Why it happens:** Copy-paste from `demo.py` which loads `test_data.npz` for the research
replay demo.

**How to avoid:** The caregiver app uses `SimulatedEEGAdapter` exclusively. Never reference
`data/processed/test_data.npz` in `caregiver_app.py`. Confirm `.gitignore` excludes `data/`.

**Warning signs:** `git add` includes anything under `data/processed/` or the `data/raw/`
directory.

### Pitfall 3: st.audio Restarts on Every st.rerun()

**What goes wrong:** In a session loop that calls `st.rerun()` every 2 seconds, `st.audio`
re-renders and restarts the audio from position 0. The caregiver hears a click every 2 seconds
instead of continuous 40 Hz entrainment.

**Why it happens:** Streamlit re-executes the entire script on every rerun. Widgets are
stateless from the script's perspective.

**How to avoid:** Use an `st.empty()` placeholder for audio and only call
`placeholder.audio(...)` when `stim_active` changes state (not every loop iteration). Keep
the audio widget outside the per-step update path.

**Warning signs:** Audible restart clicks at regular intervals during a session.

### Pitfall 4: TCN Warmup Period Confusing Users

**What goes wrong:** The first 20 windows (40 seconds of simulated session) show no TCN
prediction. If the UI shows "PAC Prediction: —" with no explanation, judges or caregivers
think the app is broken.

**Why it happens:** `RealtimePACForecaster.step()` returns `None` until the lookback buffer
(20 windows) is full. This is documented in `tests/test_simulated_session.py` lines 201–211.

**How to avoid:** Show a "Warming up... (N/20 windows)" progress indicator during warmup.
After warmup, display the PAC trend chart and stimulus indicator.

**Warning signs:** Silent `None` returns from `tcn_model.step()` with no UI feedback.

### Pitfall 5: Import Path Errors on Streamlit Cloud

**What goes wrong:** `import eegnet` fails on Cloud because `src/` is not on `sys.path`.

**Why it happens:** Local dev inserts `src/` via `sys.path.insert()` in scripts. Streamlit
Cloud runs from the repo root.

**How to avoid:** Use the same path setup pattern as `demo.py` (lines 39–43):
```python
_ROOT = Path(__file__).resolve().parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))
```
And test deployment locally with `streamlit run caregiver_app.py` from the repo root before
pushing.

### Pitfall 6: Gitignore Excludes Required Model Files

**What goes wrong:** `.gitignore` may exclude `models/` or `*.pth` files.
`best_eegnet_4ch.pth` and `best_multiscale_tcn_4ch_lb20_hz5_ts1.pth` must be in the repo.

**How to avoid:** Verify with `git status` that the three deployment artifacts are tracked:
- `models/muse_4ch/best_eegnet_4ch.pth` (36 KB)
- `models/muse_4ch/best_multiscale_tcn_4ch_lb20_hz5_ts1.pth` (128 KB)
- `data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1/scalers.npz` (4 KB)

---

## Code Examples

Verified patterns from official sources and existing codebase:

### 40 Hz WAV generation for st.audio
```python
# Source: scipy.io.wavfile docs + AudioEngine pattern in demo.py (lines 386-426)
import io
import numpy as np
from scipy.io import wavfile

def make_40hz_wav(sample_rate: int = 44100) -> bytes:
    """One second of 40 Hz click-train, loopable WAV bytes."""
    period = sample_rate // 40
    click_n = int(0.001 * sample_rate)
    period_buf = np.zeros(period, dtype=np.float32)
    t = np.arange(click_n, dtype=np.float32) / sample_rate
    period_buf[:click_n] = 0.3 * np.sin(2 * np.pi * 1000 * t)
    audio = np.tile(period_buf, 40).astype(np.float32)  # 40 periods = 1 second
    buf = io.BytesIO()
    wavfile.write(buf, sample_rate, audio)
    return buf.getvalue()
```

### st.audio with loop and autoplay
```python
# Source: https://docs.streamlit.io/develop/api-reference/media/st.audio
# Confirmed: loop and autoplay added in Streamlit 1.35+ (installed: 1.55.0)
audio_placeholder = st.empty()
if stim_active:
    audio_placeholder.audio(wav_bytes, format="audio/wav", loop=True, autoplay=True)
else:
    audio_placeholder.empty()
```

### Streamlit Cloud config.toml
```toml
# .streamlit/config.toml
[theme]
base = "light"
primaryColor = "#1f77b4"

[server]
headless = true
port = 8501
enableCORS = false
```

### Minimal caregiver_profiles.json schema
```json
{
  "patients": [
    {
      "id": "demo-001",
      "name": "Margaret (Demo)",
      "age": 74,
      "diagnosis": "Mild Cognitive Impairment",
      "sessions": [
        {
          "date": "2026-04-01",
          "duration_min": 20,
          "brain_sync_level": 0.000062,
          "therapy_active_pct": 67.3,
          "targeting_accuracy_pct": 72.1,
          "notes": "Completed without interruption"
        }
      ]
    }
  ]
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `sounddevice` for Streamlit audio | `st.audio(loop=True, autoplay=True)` | Streamlit 1.35 | Enables cloud deployment without audio device |
| Local-only Streamlit | Streamlit Community Cloud free tier | 2021 (mature 2023) | One-click deploy from GitHub |
| External database for demo profiles | JSON file in repo (ephemeral on Cloud) | N/A — design choice | Simpler, no auth required, fine for CSEF demo |

**Deprecated/outdated:**
- `sounddevice` callback pattern: Works locally only. The existing `demo.py` `_NoOpAudioEngine`
  stub already documents this. For `caregiver_app.py` (cloud target), use `st.audio` exclusively.

---

## Open Questions

1. **Google Form QR code needs the Form URL before it can be generated**
   - What we know: The `qrcode` library can generate the QR from any URL in seconds
   - What's unclear: Google Form URL is only available after the form is created in Google Forms
   - Recommendation: Create the Google Form in Plan 3 (pilot materials plan); generate QR in the same plan step

2. **`st.audio autoplay=True` browser policy differences**
   - What we know: Modern browsers (Chrome 71+, Firefox) block autoplay of audio without user
     interaction. `st.audio(autoplay=True)` renders a play button that the user must click once.
   - What's unclear: Whether judges/caregivers will need to click "play" before audio starts,
     or whether the volume slider interaction counts as user gesture
   - Recommendation: Design the UI so starting a session requires a button click (which
     constitutes user interaction), placed before the `st.audio` widget renders. This satisfies
     browser autoplay policy.

3. **App URL for QR code is unknown until deployed**
   - What we know: Streamlit Cloud assigns URLs in the format `{custom-name}.streamlit.app`
   - What's unclear: The exact URL before deployment
   - Recommendation: Deploy a stub `caregiver_app.py` early in Plan 1 to lock the URL, then
     generate QR codes. Custom subdomain can be set via Streamlit Cloud settings.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Direct Python script execution (no pytest) — matches project convention |
| Config file | None — project uses `python script.py` pattern |
| Quick run command | `python tests/test_simulated_session.py` |
| Full suite command | `python tests/test_simulated_session.py && python tests/test_model_registry.py && python tests/test_streaming_parity.py` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| APP-01 | Patient profiles load and save correctly | unit | `python -c "from caregiver_app import load_profiles; p=load_profiles(); assert len(p['patients'])>0"` | ❌ Wave 0 |
| APP-02 | Session runs 10 steps and produces summary dict | integration | `python tests/test_simulated_session.py` | ✅ |
| APP-03 | UI renders without exceptions (smoke) | smoke | `python -m py_compile caregiver_app.py` | ❌ Wave 0 |
| APP-04 | 40 Hz WAV buffer is valid WAV bytes > 0 length | unit | `python scripts/generate_qr_codes.py --check` (or inline check) | ❌ Wave 0 |
| APP-05 | Deployment dependencies resolve (requirements.txt syntax) | smoke | `pip install -r requirements.txt --dry-run` | ✅ |
| PRES-02 | QR PNG files exist and are non-empty | smoke | `python scripts/generate_qr_codes.py` (exit 0 if files created) | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m py_compile caregiver_app.py && python tests/test_simulated_session.py`
- **Per wave merge:** Full suite above
- **Phase gate:** App loads in browser via `streamlit run caregiver_app.py` before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_caregiver_app_smoke.py` — import + profile load smoke test (covers APP-01, APP-03)
- [ ] `scripts/generate_qr_codes.py` — QR generation script (covers PRES-02, PRES-04); must accept `--app-url` and `--form-url` args
- [ ] `data/caregiver_profiles.json` — seed patient profiles file
- [ ] `.streamlit/config.toml` — required for Cloud deployment

---

## Sources

### Primary (HIGH confidence)
- `demo.py` (lines 386–426, 520–598) — AudioEngine implementation and Streamlit page-state pattern
- `tests/test_simulated_session.py` — Confirms 4-channel pipeline is working end-to-end
- `src/streaming/adapters.py` — `SimulatedEEGAdapter` interface
- `src/streaming/feature_extractor.py` — `StreamingFeatureExtractor` interface
- `models/muse_4ch/` — Confirms model weights are 36–128 KB (no LFS needed)
- [st.audio docs](https://docs.streamlit.io/develop/api-reference/media/st.audio) — `loop=True, autoplay=True` confirmed in 1.35+

### Secondary (MEDIUM confidence)
- [Streamlit Community Cloud deployment docs](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) — requirements.txt, subdomain config
- [Streamlit App dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) — `requirements.txt` auto-detected
- [qrcode PyPI](https://pypi.org/project/qrcode/) — current version, Pillow dependency

### Tertiary (LOW confidence)
- Multiple Streamlit forum threads (2024) — `st.audio autoplay` browser policy behavior; needs validation by running locally before CSEF

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries already installed and used in project
- Architecture: HIGH — `demo.py` is a working Streamlit reference implementation in this repo
- Pitfalls: HIGH (sounddevice, test_data.npz) / MEDIUM (autoplay browser policy) — sounddevice
  and data file pitfalls are confirmed by existing code; autoplay policy is forum-sourced
- Deployment: HIGH — model files confirmed tiny; no LFS needed

**Research date:** 2026-03-20
**Valid until:** 2026-04-15 (stable stack; Streamlit Cloud policies stable)
