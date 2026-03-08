# Phase 5: Real-Time EEG Visualization and Audio Stimulation Demo - Research

**Researched:** 2026-03-08
**Domain:** Streamlit real-time dashboard with audio output, simulated PAC dynamics, matplotlib/plotly visualization
**Confidence:** HIGH

## Summary

This phase builds an interactive Streamlit single-page dashboard that runs four closed-loop controller strategies simultaneously on simulated brain dynamics, visualizing PAC traces live and playing 40 Hz click train audio through speakers. The implementation requires solving three core technical challenges: (1) real-time plot updates in Streamlit, (2) real-time audio output synchronized with simulation state, and (3) a simulation loop with configurable speed that keeps the UI responsive.

The existing codebase provides all simulation and controller logic needed — `EntrainmentSimulator`, `FatigueAwareSimulator`, and all four controller classes (`FixedScheduleControl`, `ReactiveThresholdControl`, `PredictiveLookAheadControl`, `OracleControl`) from `src/validation.py` and `scripts/pipeline/run_closed_loop_demo.py`. The demo script pattern in `run_closed_loop_demo.py` shows the exact simulation loop structure (create simulator, call `method.step(pac)`, call `sim.step(action)`) that the dashboard will reuse. The key engineering challenge is the UI layer, not the science layer.

**Primary recommendation:** Use Streamlit with `st.empty()` containers and matplotlib figure replacement for the four-panel live PAC visualization, `sounddevice` for real-time 40 Hz click train audio, and `st.session_state` to manage simulation state across Streamlit reruns. Use a simple `time.sleep`-based simulation loop inside the Streamlit script (not threading) since Streamlit's execution model already handles this pattern via its blocking run model.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Streamlit single-page dashboard (primary); matplotlib live animation as fallback if Streamlit doesn't work
- Single-page layout with everything visible at once — no tabs, no sidebar navigation
- Configure-then-run workflow: user sets parameters (controller type, simulation speed, fatigue on/off) upfront, then hits "Start" and watches
- Local only — runs from the repo with `streamlit run demo.py`, requires venv and model checkpoints
- Simulated brain dynamics only — use `EntrainmentSimulator` / `FatigueAwareSimulator`
- Fatigue on/off toggle — user can compare both to see why adaptive control matters
- All four controller strategies shown: Fixed Schedule, Reactive Threshold, Predictive (TCN), Oracle
- Adjustable simulation speed: 1x / 5x / 10x / Max via slider
- 40 Hz click trains — matches the actual auditory entrainment stimulus from the research
- Binary on/off: clicks play during STIMULATE, silence during REST, instant switch
- Actually plays audio through speakers during the demo
- Fixed volume with mute button — no volume slider
- Four stacked PAC trace panels, one per controller strategy (vertically stacked)
- Background color bands for stim/rest periods (green=STIM, red/gray=REST) — matches existing `generate_timeline_figure.py` pattern
- Live animation: plots draw progressively as each timestep computes, synced to simulation speed

### Claude's Discretion
- Exact Streamlit layout details (spacing, column widths, font sizes)
- Color palette beyond the green/red stim-rest bands
- How configuration controls are grouped in the setup panel
- Loading/progress indicators between configure and simulation start
- Whether to include a brief text description or instructions on the page
- Matplotlib fallback implementation details

### Deferred Ideas (OUT OF SCOPE)
- Real EEG hardware integration (live data from headset)
- Recorded subject data replay mode
- Deployment to Streamlit Cloud for shareable link
- Summary metrics panel with live-updating numbers
- Simulated raw EEG waveform visualization
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DEMO-01 | Streamlit single-page dashboard with configure-then-run workflow and matplotlib fallback | Streamlit `st.empty()` + `st.pyplot()` pattern for live plot updates; `st.session_state` for configure-then-run state machine; fallback via pure matplotlib `FuncAnimation` script |
| DEMO-02 | Simulated brain dynamics using EntrainmentSimulator/FatigueAwareSimulator with fatigue on/off toggle | Direct import from `src/simulator.py`; toggle selects `EntrainmentSimulator` vs `FatigueAwareSimulator`; both use identical `step(action)->pac` interface |
| DEMO-03 | All four controller strategies (Fixed Schedule, Reactive, Predictive TCN, Oracle) shown simultaneously | All four classes available in `src/validation.py` with identical `step(pac)->action` / `reset()` interface; `run_closed_loop_demo.py` shows the exact pattern |
| DEMO-04 | Real 40 Hz click train audio output through speakers with mute button, binary on/off matching controller decisions | `sounddevice.OutputStream` callback-based audio; pre-generate 40 Hz click train buffer; toggle audio stream write between clicks and silence based on any controller's STIMULATE state |
| DEMO-05 | Four stacked PAC trace panels with live animation and background stim/rest color bands | Four `st.empty()` placeholders each redrawn with `st.pyplot(fig)`; `axvspan()` for green/red stim/rest bands matching `generate_timeline_figure.py` pattern |
| DEMO-06 | Adjustable simulation speed (1x/5x/10x/Max) with progressive plot rendering | Speed multiplier controls `time.sleep()` between steps (1x=1s, 5x=0.2s, 10x=0.1s, Max=0); batch N steps per plot redraw at higher speeds to avoid rendering bottleneck |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| streamlit | >=1.35.0 | Dashboard framework | Locked decision; supports `st.empty()`, `st.pyplot()`, `st.session_state`, `st.fragment` |
| matplotlib | >=3.7.0 | PAC trace visualization | Already in `requirements.txt`; needed for stacked panels with `axvspan()` background shading |
| sounddevice | >=0.5.0 | Real-time 40 Hz audio output | PortAudio-based, callback streams for continuous audio, NumPy-native, cross-platform |
| numpy | >=1.24.0 | Audio waveform generation, simulation arrays | Already in `requirements.txt` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| plotly | >=5.0 | Alternative interactive charts | Only if matplotlib `st.pyplot` redraw is too slow; Streamlit has built-in plotly support |
| threading (stdlib) | N/A | RLock for matplotlib thread safety | Required per Streamlit docs — matplotlib is not thread-safe |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| sounddevice | simpleaudio | simpleaudio can't do real-time streaming; only plays pre-baked WAV buffers. sounddevice supports callback-driven continuous output needed for instant stim/rest switching |
| sounddevice | pyaudio | pyaudio has worse cross-platform support and more complex installation (requires PortAudio headers). sounddevice wraps PortAudio more cleanly |
| st.pyplot (matplotlib) | st.plotly_chart | Plotly would give smoother updates and interactivity but the existing codebase uses matplotlib exclusively; the `generate_timeline_figure.py` pattern uses `axvspan()` which is matplotlib-specific. Sticking with matplotlib reduces risk |
| st.pyplot (matplotlib) | st.line_chart | Streamlit's built-in line_chart is simpler but doesn't support `axvspan()` background color bands, which are essential for the stim/rest visualization. Also, `add_rows()` is deprecated |

**Installation:**
```bash
pip install streamlit sounddevice
```

Note: `sounddevice` requires PortAudio system library. On macOS it's bundled; on Linux: `sudo apt-get install libportaudio2`; on Windows it's bundled with the pip package.

## Architecture Patterns

### Recommended Project Structure
```
demo/                        # New demo directory at repo root
├── app.py                   # Main Streamlit dashboard entry point
├── audio.py                 # 40 Hz click train audio engine
├── simulation.py            # Simulation loop orchestrator (wraps existing controllers/simulators)
└── visualization.py         # Four-panel matplotlib figure builder
```

Or alternatively, a single file:
```
demo.py                      # Single-file Streamlit app (simpler, recommended)
```

**Recommendation:** Single file `demo.py` at repo root. The demo is self-contained enough that splitting into modules adds complexity without benefit. Keep it under ~400 lines by importing all science logic from existing `src/` modules.

### Pattern 1: Configure-Then-Run State Machine
**What:** Use `st.session_state` to implement a two-phase UI: configuration → running simulation.
**When to use:** Always — this is the locked user decision.
**Example:**
```python
# Source: Streamlit official docs (st.session_state)
import streamlit as st

if 'phase' not in st.session_state:
    st.session_state.phase = 'configure'  # 'configure' or 'running'
    st.session_state.sim_step = 0

if st.session_state.phase == 'configure':
    # Show configuration controls
    fatigue = st.toggle("Enable Fatigue Model")
    speed = st.select_slider("Speed", options=["1x", "5x", "10x", "Max"])
    if st.button("Start Simulation"):
        st.session_state.phase = 'running'
        st.session_state.fatigue = fatigue
        st.session_state.speed = speed
        st.rerun()

elif st.session_state.phase == 'running':
    # Show live simulation with stop button
    if st.button("Stop"):
        st.session_state.phase = 'configure'
        st.rerun()
    run_simulation_loop()  # blocking loop with time.sleep
```

### Pattern 2: Live Plot Update via st.empty()
**What:** Create `st.empty()` placeholder, then overwrite it each simulation step with a new matplotlib figure via `st.pyplot()`.
**When to use:** For the four stacked PAC trace panels that update each timestep.
**Example:**
```python
# Source: Streamlit docs (st.empty)
import streamlit as st
import matplotlib.pyplot as plt
from threading import RLock
import time

_lock = RLock()
plot_placeholder = st.empty()

for step in range(duration):
    # ... run simulation step ...
    
    with _lock:
        fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
        for i, (name, data) in enumerate(controllers.items()):
            ax = axes[i]
            ax.plot(data['pac'][:step], color='#333333', linewidth=1.2)
            # Background color bands for stim/rest
            for j in range(step):
                color = '#4CAF50' if data['actions'][j] == 1 else '#FFCDD2'
                ax.axvspan(j, j+1, alpha=0.3, color=color)
            ax.set_ylabel(name, fontsize=9)
        axes[-1].set_xlabel('Time (s)')
        fig.tight_layout()
        plot_placeholder.pyplot(fig)
        plt.close(fig)
    
    time.sleep(sleep_interval)
```

### Pattern 3: Sounddevice Callback Audio
**What:** Use `sounddevice.OutputStream` with a callback to continuously output 40 Hz click train or silence based on a shared state variable.
**When to use:** For the real-time audio output (DEMO-04).
**Example:**
```python
# Source: python-sounddevice docs (callback streams)
import sounddevice as sd
import numpy as np

SAMPLE_RATE = 44100
CLICK_FREQ = 40  # Hz

# Pre-generate one period of click train (25ms)
period_samples = SAMPLE_RATE // CLICK_FREQ  # 1102 samples per click
click_waveform = np.zeros(period_samples, dtype=np.float32)
# Sharp click: short burst at start of each period
click_duration = int(0.002 * SAMPLE_RATE)  # 2ms click
click_waveform[:click_duration] = 0.5 * np.sin(
    2 * np.pi * 1000 * np.arange(click_duration) / SAMPLE_RATE
)  # 1kHz tone burst = audible click

class AudioEngine:
    def __init__(self):
        self.stimulating = False
        self.muted = False
        self.phase = 0
        self.stream = None
    
    def callback(self, outdata, frames, time_info, status):
        if self.muted or not self.stimulating:
            outdata[:] = 0
            return
        for i in range(frames):
            outdata[i, 0] = click_waveform[self.phase % len(click_waveform)]
            self.phase += 1
    
    def start(self):
        self.stream = sd.OutputStream(
            samplerate=SAMPLE_RATE, channels=1,
            callback=self.callback, dtype='float32'
        )
        self.stream.start()
    
    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
```

### Pattern 4: Speed Control via Sleep Interval
**What:** Map speed multiplier to sleep time between simulation steps.
**When to use:** For DEMO-06 speed control.
**Example:**
```python
SPEED_MAP = {
    "1x": 1.0,    # 1 second per timestep (real-time)
    "5x": 0.2,    # 5 timesteps per second
    "10x": 0.1,   # 10 timesteps per second
    "Max": 0.0,   # No sleep, as fast as rendering allows
}

# At higher speeds, batch multiple simulation steps per plot redraw
BATCH_MAP = {
    "1x": 1,     # Redraw every step
    "5x": 1,     # Redraw every step
    "10x": 2,    # Redraw every 2 steps
    "Max": 10,   # Redraw every 10 steps
}
```

### Pattern 5: Background Color Bands (from generate_timeline_figure.py)
**What:** Use `axvspan()` to paint green (STIMULATE) or red/gray (REST) background bands behind the PAC trace.
**When to use:** For every panel in the four-panel display (DEMO-05).
**Example:**
```python
# Source: scripts/figures/generate_timeline_figure.py (verified from codebase)
# Green for STIM, light red/gray for REST
for t_idx in range(len(actions)):
    color = '#4CAF50' if actions[t_idx] == 1 else '#EEEEEE'
    ax.axvspan(t_idx, t_idx + 1, alpha=0.3 if actions[t_idx] == 1 else 0.5,
               color=color, zorder=0)
```

### Anti-Patterns to Avoid
- **Threading inside Streamlit for simulation loop:** Streamlit's execution model reruns the entire script on interaction. Using background threads creates state synchronization nightmares. Use a simple blocking loop with `time.sleep()` inside the script instead — Streamlit handles this fine since the UI is server-rendered.
- **FuncAnimation in Streamlit:** Matplotlib's `FuncAnimation` doesn't work with `st.pyplot()` because Streamlit renders static figures, not interactive matplotlib backends. Use `st.empty()` + figure replacement instead.
- **add_rows() for live charts:** Streamlit's `add_rows()` is officially deprecated and slated for removal. Don't use it.
- **Plotly animation for live updates:** Plotly's animation frames are pre-computed, not truly live. For frame-by-frame updates, the `st.empty()` replacement pattern is more reliable.
- **Per-step axvspan() accumulation:** Don't call `axvspan()` once per timestep per historical step — this creates O(n²) rendering cost. Instead, consolidate consecutive same-action periods into single `axvspan()` calls.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Simulation + controller loop | Custom sim loop from scratch | Import `FixedScheduleControl`, `ReactiveThresholdControl`, `PredictiveLookAheadControl`, `OracleControl` from `src/validation.py` or `scripts/pipeline/run_closed_loop_demo.py` and `EntrainmentSimulator`/`FatigueAwareSimulator` from `src/simulator.py` | Exact step/reset interfaces already exist and are validated |
| 40 Hz audio timing | Manual timer-based audio toggling | `sounddevice.OutputStream` callback | Callback runs in a separate high-priority audio thread with precise timing; manual approaches drift |
| PAC shading visualization | Custom drawing code | Follow `generate_timeline_figure.py` pattern with `axvspan()` | Proven visual pattern already used in repo figures |
| Real-time state management in Streamlit | Custom state tracking | `st.session_state` | Streamlit's built-in session state persists across reruns and handles widget state |

**Key insight:** The entire science layer already exists. The demo is purely a UI and audio integration exercise. Import everything from `src/` and `scripts/pipeline/` — don't reimplement controllers or simulators.

## Common Pitfalls

### Pitfall 1: Matplotlib Thread Safety
**What goes wrong:** Streamlit serves multiple concurrent users. Matplotlib is not thread-safe. Concurrent `plt.subplots()` calls from different sessions corrupt shared state.
**Why it happens:** Matplotlib maintains global state (current figure, current axes) that is not session-aware.
**How to avoid:** Use `threading.RLock` around all matplotlib figure creation/rendering, as recommended in Streamlit's official `st.pyplot` docs. Always create explicit `fig, axes = plt.subplots()` (never use `plt.plot()` implicit figure). Always call `plt.close(fig)` after rendering.
**Warning signs:** Garbled plots, `RuntimeError` from matplotlib, figures appearing in wrong panels.

### Pitfall 2: O(n²) axvspan Rendering
**What goes wrong:** At step N, drawing N `axvspan()` rectangles makes rendering time grow quadratically. At 360 steps, the 360th frame draws 360 rectangles × 4 panels = 1440 draw calls.
**Why it happens:** Naive approach redraws all historical shading from scratch each frame.
**How to avoid:** Two strategies: (A) Consolidate runs of consecutive identical actions into single `axvspan()` calls (O(k) where k = number of transitions, typically ~10-20 per 360s). (B) Only redraw the last N steps as a scrolling window if performance requires it.
**Warning signs:** Simulation slows down dramatically after 100+ steps; "Max" speed is still slow.

### Pitfall 3: Streamlit Rerun on Widget Interaction
**What goes wrong:** Clicking the "Stop" or "Mute" button during simulation triggers a full script rerun, resetting the simulation.
**Why it happens:** Streamlit's execution model re-executes the entire script on any widget interaction.
**How to avoid:** Store ALL simulation state in `st.session_state` (controller objects, simulator objects, PAC history arrays, current step). On rerun, check if `st.session_state.phase == 'running'` and resume from stored state rather than restarting. The simulation loop checks for stop/mute buttons via session state callbacks, not via button return values in the loop.
**Warning signs:** Simulation restarts when user clicks mute; state lost on browser tab interaction.

### Pitfall 4: Audio Continuing After Simulation Stops
**What goes wrong:** The `sounddevice.OutputStream` callback keeps running after the simulation ends, playing clicks indefinitely.
**Why it happens:** The audio stream runs in a separate thread; stopping the Streamlit simulation loop doesn't automatically stop the audio stream.
**How to avoid:** Explicitly call `stream.stop()` and `stream.close()` when simulation ends or user clicks Stop. Use a try/finally pattern or Streamlit's `@st.cache_resource` with cleanup.
**Warning signs:** Audio continues after clicking Stop; audio from previous simulation bleeds into next run.

### Pitfall 5: sys.path Import Issues
**What goes wrong:** `from simulator import EntrainmentSimulator` fails because `src/` is not on `sys.path`.
**Why it happens:** Streamlit runs from the repo root, but `src/` modules expect `src/` to be on the path. The existing `scripts/pipeline/` scripts handle this with `sys.path.insert(0, str(ROOT / "src"))`.
**How to avoid:** At the top of `demo.py`, add `sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))` — matching the exact pattern used by `run_closed_loop_demo.py`.
**Warning signs:** `ModuleNotFoundError: No module named 'simulator'`.

### Pitfall 6: sounddevice Blocking Streamlit
**What goes wrong:** `sd.play()` or `sd.wait()` blocks the Streamlit event loop, freezing the UI.
**Why it happens:** Convenience functions like `sd.play()` are blocking. Using them inside the simulation loop prevents UI updates.
**How to avoid:** Use the callback-based `sd.OutputStream` API exclusively. The callback runs in a separate high-priority audio thread and never blocks the main thread. Toggle the `stimulating` flag from the simulation loop; the callback reads it asynchronously.
**Warning signs:** UI freezes when audio starts; plot updates stop during stimulation.

## Code Examples

### Complete Simulation Loop Pattern
```python
# Source: scripts/pipeline/run_closed_loop_demo.py (verified from codebase)
# This is the exact pattern to reuse in the Streamlit demo

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from simulator import EntrainmentSimulator, FatigueAwareSimulator, StimAction
from validation import (FixedScheduleControl, ReactiveThresholdControl,
                        PredictiveLookAheadControl, OracleControl)

# Create controllers
controllers = {
    "Fixed Schedule": FixedScheduleControl(),
    "Reactive Threshold": ReactiveThresholdControl(),
    "Predictive Look-Ahead": PredictiveLookAheadControl(),
    "Oracle": OracleControl(),
}

# Create simulators (one per controller — they need independent state)
def make_sim(use_fatigue):
    if use_fatigue:
        return FatigueAwareSimulator(
            tau_rise=0.15, tau_decay=0.10,
            pac_max=0.3, pac_min=0.05, noise_std=0.02,
            fatigue_rate=0.008, recovery_rate=0.03, max_fatigue=0.7,
        )
    return EntrainmentSimulator(
        tau_rise=0.15, tau_decay=0.10,
        pac_max=0.3, pac_min=0.05, noise_std=0.02,
    )

# Simulation step (called once per timestep)
def sim_step(controllers, simulators):
    """Returns dict of {name: (pac, action)} for current timestep."""
    results = {}
    for name, ctrl in controllers.items():
        sim = simulators[name]
        pac = sim.pac
        action = ctrl.step(pac)
        sim.step(action)
        results[name] = (pac, action)
    return results
```

### Controller Interface Reference
```python
# Source: src/validation.py (verified from codebase)
# All four controllers share this interface:

class ControlMethodBase:
    def __init__(self, name: str): ...
    def reset(self): ...
    def step(self, pac_current: float) -> int:
        """Returns 0 (REST) or 1 (STIMULATE)."""
        ...

# FixedScheduleControl: 40s ON / 20s OFF cycle
# ReactiveThresholdControl: z-score based, 30-sample baseline
# PredictiveLookAheadControl: trend-based look-ahead with hysteresis
# OracleControl: stimulate when PAC < target (0.2)
```

### 40 Hz Click Train Generation
```python
# Verified approach for audible 40 Hz click train
import numpy as np

SAMPLE_RATE = 44100
CLICK_FREQ = 40  # Hz — matches 40 Hz gamma entrainment

# One period = 25ms = 1102.5 samples
period_samples = SAMPLE_RATE // CLICK_FREQ  # 1102

# Generate click: short burst (1-2ms) of 1kHz sine at start of each period
click_ms = 0.001  # 1ms click duration
click_n = int(click_ms * SAMPLE_RATE)  # 44 samples
t_click = np.arange(click_n, dtype=np.float32) / SAMPLE_RATE
click_burst = 0.3 * np.sin(2 * np.pi * 1000 * t_click).astype(np.float32)

# Full period: click then silence
click_period = np.zeros(period_samples, dtype=np.float32)
click_period[:click_n] = click_burst

# This repeating waveform produces 40 clicks per second
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `add_rows()` for live Streamlit charts | `st.empty()` + full figure replacement | Streamlit v1.35+ (2024) | `add_rows()` deprecated; placeholder replacement is the standard pattern |
| `st.experimental_rerun()` | `st.rerun()` | Streamlit v1.27 (2023) | Stable API for triggering reruns |
| No fragment support | `@st.fragment` decorator | Streamlit v1.33 (2024) | Enables partial reruns — could be used for control buttons without resetting whole page |

**Deprecated/outdated:**
- `add_rows()`: Officially deprecated, slated for removal. Don't use for live chart updates.
- `st.experimental_rerun()`: Renamed to `st.rerun()`. Use the stable name.
- `use_container_width` parameter: Deprecated in favor of `width="stretch"` parameter.

## Open Questions

1. **Rendering Performance at Max Speed**
   - What we know: At "Max" speed, the simulation loop will try to update 4 matplotlib panels every step with no delay. Matplotlib figure creation + `st.pyplot()` serialization likely takes 50-200ms per frame.
   - What's unclear: Whether the effective frame rate will be acceptable (>5 fps) for a smooth "fast-forward" experience at 360+ steps.
   - Recommendation: Implement batch rendering — at "Max" speed, simulate N steps (e.g., 10) then render once. If still too slow, consider switching to Plotly for faster rendering or reducing redraw frequency.

2. **Audio on macOS with Streamlit**
   - What we know: `sounddevice` uses PortAudio which works on macOS. Streamlit runs as a local server.
   - What's unclear: Whether macOS security permissions (microphone/audio) will interfere with `sounddevice.OutputStream` when launched from a Streamlit process.
   - Recommendation: Test early. If audio permissions are an issue, fall back to generating a WAV buffer and using `st.audio(autoplay=True)` — though this won't support instant on/off switching.

3. **Which Controller Module to Import From**
   - What we know: Both `src/validation.py` and `scripts/pipeline/run_closed_loop_demo.py` define all four controller classes. The `run_closed_loop_demo.py` versions are simpler (standalone, no external imports beyond `StimAction`).
   - What's unclear: Which module is more stable / canonical for import.
   - Recommendation: Import from `scripts/pipeline/run_closed_loop_demo.py` — its controller implementations are self-contained with minimal dependencies. Alternatively, duplicate the four small controller classes directly in `demo.py` (~100 lines) to avoid fragile import paths entirely.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | No formal test framework (per AGENTS.md) |
| Config file | None — module self-tests and smoke runs |
| Quick run command | `streamlit run demo.py` (visual verification) |
| Full suite command | `python -c "from demo import ...; ..."` (smoke test imports) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DEMO-01 | Streamlit dashboard launches and shows config controls | manual-only | `streamlit run demo.py` — verify page loads | ❌ Wave 0 |
| DEMO-02 | Fatigue toggle switches simulator type | smoke | `python -c "from src.simulator import EntrainmentSimulator, FatigueAwareSimulator; print('OK')"` | ✅ existing |
| DEMO-03 | All 4 controllers run simultaneously | smoke | `python -c "from scripts.pipeline.run_closed_loop_demo import FixedScheduleControl, ReactiveThresholdControl, PredictiveLookAheadControl, OracleControl; print('OK')"` | ✅ existing |
| DEMO-04 | 40 Hz audio plays through speakers | manual-only | Listen — requires human ear | ❌ manual |
| DEMO-05 | Four stacked panels with color bands | manual-only | Visual verification via `streamlit run demo.py` | ❌ manual |
| DEMO-06 | Speed control works (1x through Max) | manual-only | Visual verification of speed differences | ❌ manual |

### Sampling Rate
- **Per task commit:** `python -m py_compile demo.py` (syntax check)
- **Per wave merge:** `streamlit run demo.py` — visual smoke test
- **Phase gate:** All six DEMO requirements verified via manual demo walkthrough

### Wave 0 Gaps
- [ ] `demo.py` — main Streamlit app file (does not exist yet)
- [ ] `pip install streamlit sounddevice` — new dependencies not in `requirements.txt`
- [ ] Import path verification — confirm `sys.path.insert` pattern works for demo location

*(This phase is primarily a UI/demo phase — most validation is manual/visual rather than automated)*

## Sources

### Primary (HIGH confidence)
- Streamlit official docs v1.55.0 — `st.pyplot`, `st.empty`, `st.session_state`, `st.fragment`, `st.audio`, `st.plotly_chart`, `st.line_chart` (all fetched and verified)
- python-sounddevice v0.5.1 docs — usage, callback streams, OutputStream API (fetched and verified)
- Codebase files (verified by direct reading):
  - `src/simulator.py` — `EntrainmentSimulator`, `FatigueAwareSimulator` interfaces
  - `src/validation.py` — All four controller classes + `SimulationValidator`
  - `src/controller.py` — `ClosedLoopController`, `PredictiveLookAheadController`
  - `scripts/pipeline/run_closed_loop_demo.py` — Complete simulation loop pattern
  - `scripts/figures/generate_timeline_figure.py` — PAC timeline visualization with `axvspan()` pattern

### Secondary (MEDIUM confidence)
- Streamlit threading warning for matplotlib — from official `st.pyplot` docs, verified
- sounddevice PortAudio bundling on macOS/Windows — from official docs, verified

### Tertiary (LOW confidence)
- Rendering performance estimates (50-200ms per matplotlib frame in Streamlit) — based on general experience, not benchmarked for this specific use case. Should be validated empirically in Wave 0.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified via official docs; codebase integration points confirmed by reading source files
- Architecture: HIGH - Streamlit patterns verified from official docs v1.55.0; simulation loop pattern directly from existing `run_closed_loop_demo.py`
- Pitfalls: HIGH - Thread safety warning is from official Streamlit docs; import path issues observed in existing codebase; audio stream lifecycle is from sounddevice docs
- Audio approach: MEDIUM - sounddevice callback pattern is well-documented but audio permissions on macOS with Streamlit not tested

**Research date:** 2026-03-08
**Valid until:** 2026-04-08 (Streamlit and sounddevice are stable libraries; patterns unlikely to change in 30 days)
