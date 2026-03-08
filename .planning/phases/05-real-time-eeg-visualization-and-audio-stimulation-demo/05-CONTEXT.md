# Phase 5: Real-Time EEG Visualization and Audio Stimulation Demo - Context

**Gathered:** 2026-03-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Build an interactive Streamlit dashboard that demonstrates the closed-loop 40 Hz entrainment system in real time — visualizing simulated PAC dynamics across all four controller strategies and producing real 40 Hz audio click train stimulation output. This is a local-only research demo launched from the repo.

</domain>

<decisions>
## Implementation Decisions

### Demo Format & Platform
- Streamlit single-page dashboard (primary); matplotlib live animation as fallback if Streamlit doesn't work
- Single-page layout with everything visible at once — no tabs, no sidebar navigation
- Configure-then-run workflow: user sets parameters (controller type, simulation speed, fatigue on/off) upfront, then hits "Start" and watches
- Local only — runs from the repo with `streamlit run demo.py`, requires venv and model checkpoints

### Data Source
- Simulated brain dynamics only — use `EntrainmentSimulator` / `FatigueAwareSimulator`
- Fatigue on/off toggle — user can compare both to see why adaptive control matters
- All four controller strategies shown: Fixed Schedule, Reactive Threshold, Predictive Look-Ahead, Oracle
- Adjustable simulation speed: 1x / 5x / 10x / Max via slider

### Audio Stimulation
- 40 Hz click trains — matches the actual auditory entrainment stimulus from the research
- Binary on/off: clicks play during STIMULATE, silence during REST, instant switch
- Actually plays audio through speakers during the demo
- Fixed volume with mute button — no volume slider

### Visualization
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

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/simulator.py`: `EntrainmentSimulator` and `FatigueAwareSimulator` — ready to use for simulated brain dynamics
- `src/controller.py`: `ClosedLoopController` and `PredictiveLookAheadController` — reactive and predictive controllers
- `src/validation.py`: `FixedScheduleControl`, `ReactiveThresholdControl`, `PredictiveLookAheadControl`, `OracleControl` — all four strategy implementations
- `temporal_multiscale/realtime_inference.py`: `RealtimePACForecaster` — wraps TCN for online inference with rolling buffer
- `src/personalization.py`: `PersonalizationModule` — rolling z-score baseline
- `scripts/figures/generate_timeline_figure.py`: PAC timeline with stim/rest background shading — visual pattern to replicate

### Established Patterns
- All controllers implement `step(pac) -> action` and `reset()` interfaces
- Simulator uses `step(action) -> pac` interface with history tracking
- State management via `deque` rolling buffers with `reset()` methods
- `config.yaml` for runtime parameters, CLI args for overrides
- Matplotlib with `Agg` backend for headless rendering — Streamlit will need a different approach for live plots

### Integration Points
- New demo script should import from `src/` and `temporal_multiscale/` like existing `run_*.py` scripts
- Needs `sys.path.insert` for `src/` imports (existing pattern in `scripts/pipeline/run_*.py`)
- TCN checkpoint at `models/best_multiscale_tcn_lb20_hz5_ts1.pth` + scalers at `data/processed/multiscale_temporal/scalers.npz`
- EEGNet checkpoint at `models/best_eegnet.pth`

</code_context>

<specifics>
## Specific Ideas

- The four-panel stacked layout should make it immediately obvious which controller strategy is performing best — judges should be able to see at a glance that adaptive/predictive beats fixed schedule
- The fatigue toggle is the key narrative device: without fatigue, all strategies look similar; with fatigue, adaptive scheduling clearly wins
- 40 Hz click train audio makes the demo visceral — judges can hear the system making decisions

</specifics>

<deferred>
## Deferred Ideas

- Real EEG hardware integration (live data from headset)
- Recorded subject data replay mode
- Deployment to Streamlit Cloud for shareable link
- Summary metrics panel with live-updating numbers
- Simulated raw EEG waveform visualization

</deferred>

---

*Phase: 05-real-time-eeg-visualization-and-audio-stimulation-demo*
*Context gathered: 2026-03-08*
