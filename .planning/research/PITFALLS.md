# Pitfalls Research

**Domain:** Productized closed-loop 40Hz EEG entrainment — adding real-time hardware integration, web app, and clinical pilot to a validated research pipeline
**Researched:** 2026-03-20
**Confidence:** HIGH (verified against source code + peer-reviewed literature; LOW where noted)

---

## Critical Pitfalls

### Pitfall 1: Consumer EEG Cannot Reliably Measure Gamma Band PAC

**What goes wrong:**
The entire pipeline — EEGNet, TCN, PAC computation, z-score controller — is built around gamma amplitude (38–42 Hz) cross-coupled with theta phase (4–8 Hz). Consumer EEG devices like Muse and Emotiv have documented, severe limitations in the gamma band specifically. Multiple 2024–2025 studies confirm that gamma correlations between consumer and research-grade devices are either weak (R≈0.38–0.47) or completely absent at frontal sites. Muse places electrodes at AF7/AF8/TP9/TP10 — exactly the frontal locations where muscle (EMG) contamination is worst for gamma. The ds005048 training data was recorded with full research-grade systems (with ICA, Makoto preprocessing, and gel electrodes) on 35 elderly subjects seated in controlled lab conditions.

A model trained on clean 7-channel frontal research EEG will produce meaningless PAC predictions when given Muse-quality gamma-band data. The R²=0.287 that took 8 architecture iterations to reach would likely collapse to near zero or negative on real Muse data — with no warning, because the model outputs a number regardless.

**Why it happens:**
The fundamental physics are unfavorable. Gamma amplitudes are the smallest of all brainwave bands. Scalp EMG from facial and scalp muscles overlaps 20–80 Hz and is orders of magnitude stronger than gamma EEG at frontal dry-electrode sites. Consumer devices with dry electrodes and no ICA have no way to separate these signals. Additionally, consumer headsets fix electrode positions to a rigid form factor — users with different head shapes get systematically biased signal.

**How to avoid:**
There are two defensible strategies, and you must commit to one before writing any real-time integration code:

Strategy A (Recommended for 20-day timeline): Do NOT attempt live gamma PAC measurement. Use the consumer EEG only for lower-frequency features (alpha/theta) as a proxy signal, and use the simulator as the ground-truth closed-loop demonstration. Frame the real-hardware integration as "proof of concept for signal acquisition architecture" — not as validated gamma measurement. For CSEF demo: Muse provides live alpha/theta visualization to show the loop is plumbing-connected. Gamma PAC comes from replaying ds005048 held-out data.

Strategy B (Correct but risky for timeline): Use OpenBCI Cyton with gel electrodes positioned at Fz, F3, F4, FCz, FC3, FC4, Cz — matching the ds005048 channel subset. This is research-grade quality at consumer price (~$500). But setup takes ~45 minutes per session, gel is messy, and software integration is harder.

**Warning signs:**
- Model predicts PAC values consistently near the training set mean (≈0.000044) regardless of what the participant is doing — this is the model defaulting when signal quality fails
- PAC predictions show zero variance across a 10-minute session
- "Signal quality" indicator shows green but measured gamma power is 10x higher than alpha power (indicates EMG contamination)

**Phase to address:**
Hardware selection phase (first decision before writing any web app code). Must be resolved in week 1.

---

### Pitfall 2: TCN Spectral Features Require Offline Preprocessing Steps That Don't Exist in Real-Time

**What goes wrong:**
The TCN's 61 spectral features are computed by `build_multiscale_dataset.py` from already-preprocessed windows in `data/processed/`. The preprocessing chain is: raw BIDS → `data_loader.py` → `preprocessing.py` (bandpass + notch + artifact zeroing + CAR) → `pac_computation.py` (epoch-level MI) → spectral extraction. None of this is designed for online streaming. The `RealtimePACForecaster.step()` method takes `spectral_features: np.ndarray` of shape `(61,)` as an input — but there is no existing code that computes those 61 features from a live 2-second window in real time.

In other words: `realtime_inference.py` exists but the code that *feeds* it during live operation does not. This is the single biggest gap between the current research pipeline and a working real-time demo.

**Why it happens:**
The research pipeline was designed for offline batch processing. `build_multiscale_dataset.py` processes the entire dataset at once. It was never designed to emit one feature vector per 2-second window from a live stream. Someone building a web app on top of this may not notice until they try to wire it together.

**How to avoid:**
Write a `StreamingFeatureExtractor` class that replicates exactly the offline spectral feature extraction from a 2-second EEG window, using only causal operations (no future data). The class must:
1. Accept `(7, 500)` float32 arrays one at a time
2. Apply the same bandpass + notch + CAR from `preprocessing.py`
3. Compute the same 4-band spectral features + PAC-derived features
4. Output a `(61,)` vector normalized with the training-set scaler values stored in `data/processed/multiscale_temporal/scalers.npz`

Verify by: take 10 consecutive windows from the test set, run them through both the offline pipeline and the new streaming extractor, assert the feature vectors are identical within floating-point tolerance.

**Warning signs:**
- TCN always returns `None` from `step()` for the first 20 seconds (expected during lookback warmup — do not confuse this with a bug)
- Feature vectors have zero variance across time steps (normalization applied twice, or wrong scaler)
- Predictions jump wildly between consecutive steps (normalization applied with wrong scaler statistics)

**Phase to address:**
Real-time inference pipeline phase. Must be the first technical task before any web app work.

---

### Pitfall 3: Simulator Parameters Are Not Empirically Validated — This Is the Weakest Defense Point

**What goes wrong:**
`simulator.py` uses an exponential approach model with τ_rise=0.15, τ_decay=0.10, PAC_max=0.3, PAC_min=0.05, noise_std=0.02. The docstring says these are "empirically extracted from dataset" but this is a claim that requires active defense. The real ds005048 data has PAC labels ranging [0.000006, 0.000701] with mean ≈0.000044 — these are in Modulation Index units (×10⁻⁶ scale). The simulator uses PAC values in [0.05, 0.3] — a completely different scale and normalization. CSEF judges with neuroscience backgrounds will ask: "How did you validate your simulator dynamics against real entrainment data?"

The current answer is that the controller comparison results (TCN vs Reactive vs Fixed) were validated on *real* ds005048 replay data via `run_tcn_validation.py`, not on the simulator alone. But if a judge focuses on the simulation framework itself, the τ values and PAC ranges are internally defined, not fit from literature or data.

**Why it happens:**
The simulator was built for prototyping and comparing controller architectures — a valid and common approach in closed-loop research. The mistake is presenting simulation results without a clear statement of what the simulator does and does not claim to represent.

**How to avoid:**
Preempt the question. Add one section to the poster/presentation: "Simulation vs. Real Data." Show that the key finding — TCN predictive advantage at 5–10s horizons — was replicated on real ds005048 data with R²=0.24–0.28 and g=1.31 alignment advantage. The simulator was used for controller comparison; all outcome claims are backed by real EEG replay. Explicitly state simulator limitations: "The exponential model approximates average population dynamics; individual variability and fatigue effects are modeled parametrically and validated by sensitivity sweep."

For the τ parameter values specifically: cite that exponential approach models for gamma entrainment are consistent with Iaccarino et al. (2016) GENUS response timescales and Alagapan et al. closed-loop entrainment literature. The exact τ values are a modeling choice, bounded by the ranges reported in the literature.

**Warning signs:**
- Judges ask "why 0.15 specifically?" and there is no answer — either cite it or frame it as a sensitivity-swept range
- Simulation results show 100% improvement over baseline — this is implausibly large and will be challenged
- Demo shows smooth perfect convergence in simulator but real-data replay shows variance — acknowledge this discrepancy explicitly

**Phase to address:**
Research deepening phase (25% allocation). Add a simulation validation section that shows correlation between simulated PAC trajectory shape and real subject PAC trajectory shape from ds005048.

---

### Pitfall 4: 20-Day Timeline Will Break If Real-Time EEG Hardware Integration Is Attempted Seriously

**What goes wrong:**
Integrating a real consumer EEG headset into a web app requires: device SDK/driver setup, Bluetooth streaming library, real-time Python buffer management, signal quality monitoring, and fallback handling for dropped packets. Each of these is independently a multi-day debugging problem. Emotiv has a proprietary API that requires license keys, SDK downloads, and Python wrapper setup. Muse requires `muse-lsl` or `muselsl` — which has known compatibility issues with Python 3.11+ and Apple Silicon. OpenBCI requires Cyton board + USB dongle + OpenBCI_GUI or Brainflow SDK. Any of these can eat 3–5 days of the 20-day window.

Given that the real-time hardware loop (after Pitfall 1) cannot reliably measure gamma PAC anyway on consumer devices, the risk-reward ratio of deep hardware integration is very poor.

**Why it happens:**
The project narrative calls for "real EEG headset integration" and judges respond positively to live demos. The temptation is to build the full live pipeline. But hardware debugging in unfamiliar SDKs during the last 3 weeks before a major competition has a high failure probability.

**How to avoid:**
Implement dual-mode as described in PROJECT.md, but scope the "real EEG mode" to: headset connects, raw signal streams, alpha/theta power visualizes in real time, signal quality indicator shows green. The closed-loop PAC decision layer uses simulated EEG or ds005048 replay data. Label this clearly in the UI: "Live EEG signal (hardware connected)" for the streaming visualization, and "PAC-based therapy session" for the control loop. This is honest and defensible.

Total time budget for hardware integration: 3 days maximum. If it takes longer, ship with simulated mode only and call it "simulation with validated real-EEG transfer demonstrated offline."

**Warning signs:**
- Day 5 and still fighting Bluetooth/SDK connection issues
- First working hardware connection appears on Day 10
- Spending time on impedance checks, electrode gel, or hardware documentation

**Phase to address:**
Hardware integration phase. Hard time-box: 3 days, then pivot to simulated fallback if not working.

---

### Pitfall 5: Web App Framework Choice Can Multiply Development Time

**What goes wrong:**
The current demo is Streamlit (`demo.py`). Streamlit re-runs the entire script on every user interaction and has a single-threaded execution model that breaks with WebSocket-style streaming. Building a production web app in Streamlit with real-time EEG visualization, session management, and audio stimulus playback requires workarounds (`st.empty()`, threading locks, background threads) that are fragile and hard to maintain. If "web app" is interpreted as React + FastAPI (the standard production stack from Amaar's global preferences), that's a 10–15 day build for this feature set.

**Why it happens:**
"Production web app" and "demo-quality web app" have very different implementation costs. A CSEF demo that looks polished and works reliably during a 10-minute judging session is not the same as a deployed clinical platform.

**How to avoid:**
Keep Streamlit for the demo, but make it look production-quality through CSS theming and layout polish. Use `st.session_state` carefully for state persistence. For real-time EEG visualization, use `streamlit-autorefresh` or the `st.empty()` + `time.sleep(0.1)` pattern that already works in `demo.py`. The goal is "looks like a product" not "is a product." If judges ask about production architecture, have a 2-slide technical roadmap showing: current (Streamlit research demo) → next (FastAPI + React with WebSocket EEG streaming) → production (hosted, multi-user, HIPAA-compliant).

Do not start a React rewrite. Do not start a FastAPI backend rewrite. Polish what exists.

**Warning signs:**
- Starting a new `frontend/` or `backend/` directory more than 3 days in
- Installing React, Next.js, or TypeScript tooling
- Any sentence containing "I'll just quickly migrate to..."

**Phase to address:**
Web app phase. Constraint: extend Streamlit demo only.

---

### Pitfall 6: "Simulation Is Accurate" Defense Has Two Specific Weak Points Judges Will Find

**What goes wrong:**
Two specific claims are vulnerable to judge challenge:

Weak point A — "Empirically extracted parameters": The simulator's τ_rise=0.15 and τ_decay=0.10 are stated as "empirically extracted from the dataset" in the simulator docstring, but there is no script in the codebase that fits these values from data. They appear to have been chosen by hand. If a judge asks to see the empirical extraction, it doesn't exist.

Weak point B — "Transfer to real humans": The entire project studied 35 elderly EEG subjects who had already been exposed to gamma stimulation (the ds005048 protocol). Generalizing to Alzheimer's patients in a clinical setting requires: different population (AD patients have different baseline theta-gamma coupling), different environment (clinical facility, not lab), different equipment (consumer vs. research grade — see Pitfall 1). The simulation validated control logic, but the claim "this would work in a clinical setting" is a significant extrapolation.

**Why it happens:**
Research projects naturally present their best results. The simulator was built for controller comparison and it served that purpose. The transfer-to-clinical claim is part of the product narrative and is legitimately forward-looking. The problem is not the claims themselves but being caught without a calibrated answer.

**How to avoid:**
For weak point A: either add a `fit_simulator_params.py` script that actually fits τ from the ds005048 data (a few hours of work), or change the docstring to say "manually calibrated to approximate reported gamma entrainment timescales from literature (Iaccarino et al. 2016; Alagapan et al.)" — which is honest and defensible.

For weak point B: prepare a 3-sentence answer: "Our current validation used 35 elderly subjects from a controlled lab study. Translation to AD patients requires clinical trials, which is the proposed next step in our roadmap. The simulation demonstrates that the control architecture is sound; clinical efficacy requires Phase II trials, which we have outlined in our clinical testing plan."

**Warning signs:**
- Judges specifically asking "where did 0.15 come from?"
- Judges asking "have you tested this on actual Alzheimer's patients?"
- Any question containing "how do you know the simulation is realistic?"

**Phase to address:**
Research deepening phase. Fix the simulator parameter documentation before the poster is finalized.

---

### Pitfall 7: EEG-to-Feature Pipeline Has a Specific Architecture Mismatch at the Channel Level

**What goes wrong:**
The ds005048 dataset uses 7 frontal channels: Fz, F3, F4, FCz, FC3, FC4, Cz (or equivalent). The exact channel labels matter because:

1. EEGNet's first layer is a spatial filter over exactly 7 channels with learned depthwise weights. A consumer headset like Muse only has 4 channels (AF7, AF8, TP9, TP10) — none of which are in the set the model was trained on. Connecting Muse to the controller directly will produce garbage output with no error.

2. Even if using OpenBCI with 7 channels, electrode placement must match the training set positions or the spatial filter weights are meaningless. AF7/AF8 are not equivalent to F3/F4.

3. The TCN's 61 spectral features are computed from these specific 7 channels. Substituting 4 channels without retraining changes the feature space entirely.

**Why it happens:**
EEG hardware selection is often driven by cost and availability. Muse is the cheapest and most accessible consumer headset. It's easy to assume "EEG is EEG" when the technical reality is that the spatial encoding is specific to electrode positions.

**How to avoid:**
If using a consumer headset for live data: the visualization loop (raw signal, alpha/theta band power) can use whatever channels the headset provides. The PAC-based closed-loop control must either (a) use offline ds005048 data for demonstration or (b) retrain EEGNet and the TCN feature extractor on new data collected from the specific headset's electrode configuration — a weeks-long process. This is why Strategy A from Pitfall 1 is recommended: keep the demo honest about which parts are live hardware and which parts are validated offline.

**Warning signs:**
- Trying to pad Muse's 4-channel output to 7 channels with zeros
- Any code that renames Muse channels to ds005048 channel names without retraining
- EEGNet running without error on (4, 500) input that was reshaped or zero-padded to (7, 500)

**Phase to address:**
Hardware integration phase. Define channel mapping before writing any signal acquisition code.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Use Streamlit for demo instead of React/FastAPI | 5–10 days saved | Cannot scale to multi-user clinical deployment; re-run model on every interaction | For CSEF demo only — never for production |
| Simulated EEG fallback for closed-loop demo | 3–5 days saved vs. live hardware integration | Judges see a simulation, not a product | Acceptable with clear labeling; document validation evidence |
| Reuse ds005048 test subject replay as "real-time" demo | 2 days saved | Loop is deterministic, not truly reactive to live input | Acceptable if presented accurately as validated real-data replay |
| Skip retraining on consumer EEG data | 2–4 weeks saved | Model performance on consumer devices is unknown and likely poor | Only acceptable if demo does not claim live gamma PAC measurement from consumer device |
| Hard-code scaler values in real-time extractor | 1 day saved | If dataset is rebuilt with different normalization, extractor silently gives wrong values | Never — load scalers from checkpoint file |
| Use `filtfilt` (zero-phase) in real-time path | Easier to implement | `filtfilt` is non-causal; it uses future samples. Introduces 0–200ms of algorithmic latency and is scientifically incorrect for closed-loop | Never — use causal `lfilter` or `sosfilt` with state tracking in real-time path |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Consumer EEG headset SDK | Assume Python SDK works on current OS/Python version out of box | Test SDK connection on target hardware before committing to that headset. `muse-lsl` frequently breaks with Python 3.11+ and macOS Sonoma. Allow 2 days for setup. |
| EEG streaming → PAC computation | Compute PAC on every 2-second window independently | The existing PAC computation is epoch-level (full 20–40s blocks). For real-time, use the spectral features as proxy and reserve PAC estimation for display-only at 30s intervals |
| Browser audio → 40Hz stimulus | Use Web Audio API's `OscillatorNode` for 40Hz | Web Audio is correct but binaural beats require stereo, not mono. 40Hz pure tone is different from 40Hz binaural beat. Verify which the research literature uses — the current `sounddevice`-based implementation plays 40Hz pure tone. Match this in the web app. |
| Streamlit + background EEG thread | Use `st.session_state` to share data between background thread and UI | Threading in Streamlit has race conditions. Use a thread-safe `queue.Queue` or `collections.deque(maxlen=N)` for the ring buffer. The existing `demo.py` already shows the correct pattern. |
| PyTorch model in web server | Reload model on every request | Load model once at server startup into a module-level singleton. EEGNet is 1,457 params — forward pass is <5ms on CPU. TCN is ~31K params — forward pass is <20ms on CPU. Neither is the bottleneck. |
| `pac_computation.py` in real-time | Run full Modulation Index computation on every 2s window | MI requires 30+ seconds of data for reliable estimation. In real-time, compute spectral power proxy metrics. True PAC can only be estimated over the 20–40s epoch window, same as in training. |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Using `filtfilt` in streaming path | Filter works correctly in test, latency seems acceptable, but response is 100–400ms late relative to actual neural events | Replace with causal `sosfilt(..., zi=state)` — maintain filter state across windows | Immediately in closed-loop; scientifically invalid from day 1 |
| Re-running full bandpass on every 2s window with fresh filter state | Each window independently filtered, creates edge artifacts that look like bursts at window boundaries | Use stateful filtering — initialize filter state from last 0.5s of previous window | Symptoms appear as spurious gamma bursts every 2 seconds |
| Computing PAC every 2s window | PAC values extremely noisy, model predictions erratic | Use spectral features for per-window inference; use PAC only over 30s sliding window | Any real-time use |
| PyTorch inference cold start | First inference call takes 500ms–2s, subsequent calls are fast | Call model once with dummy input at startup to trigger JIT compilation and allocator warmup | Demo startup — looks like system is frozen |
| Not warming up the TCN lookback buffer | TCN returns None for first 20 seconds (lookback=20 windows at 1Hz) — UI shows no prediction | Seed the buffer with replayed data or show a "warming up" indicator | Every session start |
| EEG data dropping frames at 250Hz | Visible gaps in visualization, controller gets incorrect timestamps | Use a ring buffer large enough to absorb burst latency (~5 seconds = 1250 samples). Flag and interpolate dropped frames. | Immediately with Bluetooth transport |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Storing patient session data in unencrypted local JSON | HIPAA violation even for pilot demo involving real patients | For pilot facility visits: collect no identifying patient data; record aggregate session metrics only with explicit verbal consent. No names, dates of birth, diagnoses stored. |
| QR code links to a localhost demo | App unreachable by judges scanning QR code on phones | Deploy to a public URL (Streamlit Community Cloud is free and takes <30 minutes to set up) before finalizing poster |
| Hardcoding model paths as absolute local paths | Demo fails on any machine that isn't Amaar's laptop | Use `Path(__file__).resolve().parent` for all path resolution — already the pattern in `temporal_multiscale/` |
| Sharing `data/processed/` or `data/raw/` via web app | Raw EEG data from OpenNeuro has usage restrictions | Web app must not serve raw data files. Serve only model outputs and aggregated statistics. |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Displaying PAC values in raw MI units (0.000044) | Numbers are uninterpretable to caregivers and judges alike | Display z-scores and categorical states (HIGH / NORMAL / LOW coupling) with color coding. Show raw numbers only in a "technical" expandable section. |
| No loading state during 20-second TCN warmup | Demo appears frozen/broken for first 20 seconds | Show explicit "Calibrating (18s remaining)..." countdown during lookback buffer fill |
| Stimulation plays continuously during demo with loud 40Hz tone | Fatigue and discomfort for everyone at the demo table | Default volume to 30%, allow mute, start with stimulus OFF until user explicitly starts a session |
| Demo fails when model checkpoint path is wrong | Unrecoverable crash at startup | Load model at startup with a clear error message and a "run in simulated mode without models" fallback |
| Showing 7-panel real-time EEG visualization with Muse-quality data | Noisy, jerky signals look broken to non-experts | If using consumer EEG, show only 1–2 channels (frontal) with a clear label, and suppress gamma band display if hardware cannot reliably measure it |

---

## "Looks Done But Isn't" Checklist

- [ ] **Real-time streaming:** Demo appears to stream but is actually replaying pre-loaded data at wall-clock speed — verify that the data source is genuinely streaming (either live hardware or explicitly labeled as "validated data replay")
- [ ] **Dual-mode switch:** UI has a "Real EEG / Simulated" toggle but both modes call the same code path — verify mode actually changes the data source
- [ ] **TCN predictions active:** Dashboard shows a prediction panel but TCN is returning None due to insufficient buffer fill — verify predictions appear after 20s of session time
- [ ] **Audio works in demo environment:** Laptop audio output connected to speakers before demo; 40Hz tone tested at low volume without feedback; sounddevice import succeeds
- [ ] **QR code resolves on mobile:** Test QR code on an iPhone/Android device at the venue — not just on the development laptop
- [ ] **Channel mismatch caught:** If real hardware is connected, verify channel count matches model expectation (7) before passing to inference — add a shape assertion at the boundary
- [ ] **Normalization applied:** Verify that live spectral features are normalized with training set mean/std from the saved scaler file, not re-fit on the current session
- [ ] **Simulator parameters documented:** Docstring or inline comment traces each parameter to either a data fit or a literature citation
- [ ] **Pilot facility consent:** Any session with a real person has verbal consent documented, no PII recorded

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Consumer EEG gamma failure discovered Day 10 | LOW (if dual-mode was built) / HIGH (if entire demo depends on live PAC) | Switch to "Simulated EEG + Validated Replay" mode; update demo narrative to match |
| Real-time streaming feature extractor wrong — wrong PAC predictions | MEDIUM | Compare feature vectors to offline pipeline on a single test window; fix normalization or feature computation; re-verify |
| Streamlit demo crashes at fair due to missing dependency | LOW | Pin requirements.txt; deploy backup demo to Streamlit Cloud; have a recorded video demo as last resort |
| QR code on poster links to broken URL | LOW | Deploy to Streamlit Cloud 48h before fair; test QR on phone |
| Judge catches simulator parameter claim | LOW | Acknowledge the limitation honestly: "the τ values were chosen to approximate literature-reported response timescales; our key results are validated on real ds005048 data, not just simulation" |
| Hardware headset fails to connect at demo | LOW (if dual-mode built) / HIGH (if no fallback) | Dual-mode fallback; show hardware physically present and explain integration architecture conceptually |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Consumer EEG gamma failure | Hardware selection (Phase 1, Day 1–2) | Decision documented in code: which device, which channels, what the device measures vs. what the model uses |
| Missing real-time spectral extractor | Real-time inference pipeline (Phase 2, Day 3–5) | Feature vectors from streaming path match offline pipeline on 10 test windows within 1e-4 tolerance |
| Simulator parameter defense | Research deepening (runs parallel, Week 1) | τ values traced to either fit script or literature citation in simulator docstring |
| 20-day timeline / scope creep | Phase 1 scope lock (Day 1) | No new directories created after Day 3; no framework migrations |
| Web app framework trap | Web app phase (Phase 3) | Built on Streamlit; no React/Next.js directories exist |
| Causality violation (`filtfilt`) | Real-time inference pipeline (Phase 2) | All streaming code uses `sosfilt` with state tracking; no `filtfilt` calls in real-time path |
| Channel mismatch | Hardware integration (Phase 2) | Shape assertion `assert eeg_window.shape == (7, 500)` at controller boundary |
| Cold start / warmup visibility | Web app phase (Phase 3) | Demo tested cold with no pre-loaded state; warmup countdown visible |
| QR code resolution | Presentation phase (Phase 4) | QR tested on phone 48h before fair |
| HIPAA / data privacy at pilot | Pilot phase (Phase 4) | Session data schema reviewed; no PII fields |

---

## Sources

- Bahador, N. et al. (2025). "A comprehensive evaluation framework for consumer-grade EEG devices: signal quality, robustness, and usability." *Scientific Reports*. https://www.nature.com/articles/s41598-026-39056-8
- Comparisons of consumer vs research EEG spectral characteristics (2024). *PMC*. https://pmc.ncbi.nlm.nih.gov/articles/PMC11679099/
- Scoping review on consumer-grade EEG research use. *PMC / PLOS ONE*. https://pmc.ncbi.nlm.nih.gov/articles/PMC10917334/
- Beyond the lab: real-world wearable EEG benchmarking for BCIs. *Brain Informatics* (2025). https://link.springer.com/article/10.1186/s40708-025-00290-x
- OpenBCI Forum discussion: gamma neurofeedback with consumer hardware. https://openbci.com/forum/index.php?p=/discussion/3017/use-openbci-gui-for-neurofeedback-in-gamma-resolved
- Iaccarino, H.F. et al. (2016). "Gamma frequency entrainment attenuates amyloid load and modifies microglia." *Nature*, 540, 230–235. (Entrainment timescale reference for simulator parameter defense)
- Existing project code: `src/controller.py`, `temporal_multiscale/realtime_inference.py`, `src/simulator.py`, `src/preprocessing.py`, `demo.py` (direct code inspection — highest confidence for project-specific claims)
- OpenNeuro ds005048 dataset characteristics: CLAUDE.md, `src/data_loader.py` comments
- CSEF 2026 judging criteria: https://csef.natsci.colostate.edu/wp-content/uploads/2024/03/Judging-Criteria.pdf
- Building real-time EEG apps with Flask/BrainFlow (2024). https://mindgardenai.com/blog/2024-09-27-building-an-advanced-real-time-eeg-analysis-app-with-python-and-brainflow/

---
*Pitfalls research for: productized 40Hz closed-loop entrainment web app with real EEG hardware integration*
*Researched: 2026-03-20*
*Timeline constraint: 20 days to CSEF (April 9, 2026)*
