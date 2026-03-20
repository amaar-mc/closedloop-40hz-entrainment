# Feature Research

**Domain:** BCI/neurofeedback caregiver therapy app with closed-loop 40Hz entrainment + ML research deepening
**Researched:** 2026-03-20
**Confidence:** MEDIUM-HIGH (caregiver UX and EEG streaming from live platforms; ML rigor from ISEF rubric + published standards; clinical pilot from Cognito OVERTURE trial data)

---

## Context: What Already Exists (v2.0)

The following are NOT new features — they exist and must not be rebuilt:

- Static PAC prediction (EEGNet, R² ≈ 0.287)
- Temporal PAC forecasting 5–10s ahead (MultiscaleCausalTCN, R² ≈ 0.25 at 5s)
- Closed-loop simulation with 4 controllers (Fixed / Reactive / Predictive / Oracle)
- Personalization module (30s rolling baseline, z-score decision)
- Streamlit demo dashboard (`demo.py`) — replay real EEG, 40Hz click audio, 4-controller side-by-side viz
- Full audit/validation pipeline, research paper, poster, presentation materials

All new features below are additive for v3.0.

---

## Feature Landscape by Domain

### Domain 1: Caregiver-Facing Therapy Session App

What therapist/caregiver-facing neurofeedback platforms (Myndlift, Divergence Neuro, BrainBit) treat as non-negotiable.

#### Table Stakes (Caregiver UX)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Patient profile — name, age, session count | Every clinical tool has patient records; missing = not a clinical product | LOW | Store locally or simple JSON; no auth required for demo |
| Session log — date, duration, controller used, % stim time | Caregivers need to review what happened; a tool with no history is a black box | LOW | Append CSV or SQLite per session; already computed in demo.py |
| Start / Stop session control with clear state indicator | Users must know if a session is running; ambiguity causes fear with EEG hardware | LOW | Already exists in demo.py but needs clearer "session active" UI state |
| Real-time PAC indicator during session | Core feedback signal; without it the app feels like a black box to the caregiver | MEDIUM | PAC is already computed; needs a simple live gauge or colored indicator |
| Session completion summary screen | Every therapy app shows a post-session recap; missing = unfinished feeling | LOW | Summary table already exists in demo.py; needs patient-friendly language |
| Hardware status indicator (connected / not connected / simulated) | Users need to know if the EEG device is real or demo mode; confusion = loss of trust | LOW | Boolean flag with colored dot; critical for dual-mode credibility |
| 40Hz audio volume control | Caregivers need to set appropriate volume for elderly patients; auditory sensitivity varies | LOW | Already have mute toggle; need slider instead |

#### Differentiators (Caregiver UX)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Adaptive controller selection visible to caregiver | Shows that the system is "smart" — not just playing a tone on a timer; key product narrative | LOW | Add a clear label "TCN Predictive Mode" with a brief explanation |
| PAC trend chart across sessions (multi-session view) | Caregivers want to see if the patient is improving over weeks; this is the retention hook | MEDIUM | Requires session log; plot PAC mean and targeting rate over time |
| Pilot feedback form embedded in app | Collect structured data at facilities for CSEF human testing claim | LOW | 5-question Google Form embedded via iframe or QR code |
| Subject-agnostic mode (no personal data) | Privacy-safe for facility demos; removes friction when staff won't allow patient data collection | LOW | Default mode for pilot; "Demo Subject" profile |

#### Anti-Features (Caregiver UX)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| EHR integration | Seems clinical-grade | HIPAA complexity, 6-month project, out of scope for CSEF | Document it as "future integration point" in clinical roadmap |
| Custom protocol editor | Power-user appeal | Adds complexity, breaks the "adaptive AI decides" narrative | Expose 2 presets: TCN Adaptive and Fixed Schedule comparison |
| User authentication / login | Looks like a real product | Adds weeks of development, irrelevant for demo purposes | Single shared device profile is fine for pilot |
| Biometric data storage | Completeness | Privacy/regulatory minefield; no HIPAA compliance in scope | Store only summary metrics (mean PAC, stim %), never raw EEG |

---

### Domain 2: Real-Time EEG Streaming into Web App

#### Table Stakes (EEG Streaming)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Simulated EEG fallback mode | Required for demos without hardware; judges will not have a headset | LOW | BrainFlow's `SYNTHETIC_BOARD` serves this role; already partially present in demo.py via test data replay |
| Hardware connection status with graceful degradation | If the headset drops, the app must not crash or freeze; clinical context demands stability | LOW | Try-connect → fallback to sim; single status flag in UI |
| Raw EEG waveform display (frontal channel) | Standard in every BCI app; shows the device is "doing something real" | LOW | Already implemented in demo.py (`continuous_eeg` display) |
| Latency under 5s from signal to control decision | TCN inference is 2ms; pipeline overhead must stay reasonable for live use | MEDIUM | Real hardware path adds BrainFlow polling + feature extraction; profile this when hardware is added |
| Python bridge: BrainFlow → feature extraction → TCN | The only proven open-source cross-hardware EEG streaming library with synthetic board | MEDIUM | BrainFlow supports Muse 2, OpenBCI Ganglion, Neurosity Crown, and 30+ others via uniform API; synthetic board = same code path |

#### Differentiators (EEG Streaming)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Dual-mode toggle in UI (Real EEG / Demo Mode) | Lets judges experience the "real thing" narrative without requiring hardware setup | LOW | Boolean flag; demo.py already has hardware vs replay modes conceptually |
| Specific headset recommendation in UI | Judges will ask "what headset?"; naming Muse 2 or OpenBCI Ganglion makes it concrete | LOW | Documentation + UI label; no code required |
| Streaming EEG → WebSocket → browser (future) | Standard for web-based BCI apps (Neurosity SDK, muse-js via Web Bluetooth) | HIGH | Out of scope for v3.0; current Python/Streamlit path is sufficient for CSEF |

#### Anti-Features (EEG Streaming)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Web Bluetooth / muse-js in browser | Seems impressive | Muse SDK is deprecated for official support; Web Bluetooth is Chrome-only; adds browser compatibility hell | BrainFlow Python bridge to Streamlit covers all hardware without browser constraints |
| Real-time EEG storage to cloud | Completeness | HIPAA, privacy, bandwidth; overkill for demo | Log only derived metrics (PAC values, decisions) locally |
| Multi-channel spatial map display | Visual appeal | Adds significant complexity; 7 frontal channels in a waveform is sufficient | Single-channel frontal waveform with labeled channels in legend |

---

### Domain 3: Adaptive Auditory Stimulus

#### Table Stakes (Auditory Stimulus)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| 40Hz click train during stimulation windows | Core therapy mechanism; without it the system is just a visualizer | LOW | Already implemented in AudioEngine (demo.py); 1kHz sine bursts at 40Hz rate |
| Silence during rest windows | Clinical protocol; continuous tone defeats the closed-loop purpose | LOW | Already implemented via `stimulating` flag |
| Volume control (not just mute) | Elderly patient comfort; auditory sensitivity varies with age and hearing aids | LOW | Slider 0–100%; mute is a toggle not a replacement |
| Stimulus type indicator in UI | Caregiver needs to confirm "yes, audio is happening"; visual confirmation | LOW | Blinking indicator or color change during active stim |

#### Differentiators (Auditory Stimulus)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| PAC-gated stimulus (adaptive on/off) | Core product claim: stimulus adapts to brain state, not a fixed timer; this IS the product | LOW | Already implemented via TCN controller → AudioEngine; needs to be clearly labeled in UI |
| Stimulus log (when on/off, for how long) | Allows post-session analysis of "did the brain respond to stimulation?"; judges will ask | LOW | Log each stim ON/OFF event with timestamp; already tracked in action_histories |
| Multisensory (audio + visual 40Hz flicker) | Cognito's Spectris uses both; combined stimulation shows 2x effect in literature | HIGH | Out of scope for v3.0 hardware; document as expansion path |
| Isochronic tone variant (pure 40Hz sine carrier vs click train) | Some patients may find click trains aversive; sine wave at 40Hz is gentler | LOW | Web Audio API oscillator vs current click train; toggle in UI |

#### Anti-Features (Auditory Stimulus)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Binaural beats for 40Hz | Sounds scientific | Binaural beats require frequency offset between ears; 40Hz binaural would need 200Hz + 240Hz carrier — not the same as GENUS-validated 40Hz monaural click train | Use monaural 40Hz isochronic tones consistent with published GENUS protocol |
| Adaptive frequency (vary Hz based on PAC) | Interesting concept | No clinical evidence for frequencies other than 40Hz in Alzheimer's context; would undermine the established science claim | Stick to 40Hz; document as future research direction |
| Spatial audio / HRTF | Modern audio appeal | No entrainment benefit demonstrated; adds complexity | Monophonic 40Hz click train |

---

### Domain 4: Model Comparison Study (ML Rigor)

What ISEF/CSEF judges score under Scientific Thought (10pts) and Creativity (10pts), based on published judging rubrics. Winning biomedical projects demonstrate: significant problem, clear hypothesis, controls, justified conclusions, awareness of further research.

#### Table Stakes (ML Rigor for Science Fair)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Multiple baselines reported alongside TCN | Without persistence and Ridge comparisons, judges cannot assess TCN's contribution; "our model is good" without a reference is not science | LOW | Already computed in sweep_horizons.py; need to surface these clearly in presentation |
| Ablation study: TCN with components removed | Judges ask "what specifically makes your model work?"; can't answer without ablations | MEDIUM | Test: no GroupNorm, no attention pooling, no multi-scale, single dilation; report R² delta per ablation |
| Cross-validation or multi-seed training | Single-run results are not replicable; judges with stats background will call this out | MEDIUM | 3-5 seeds already partially in rigor/multi_seed_training.py; report mean ± std |
| Architecture comparison table (8 static models + temporal models) | The "architecture marathon" is already a key narrative; needs a clean summary table | LOW | Exists in archive; needs a presentable comparison table with R², params, training time |
| Feature importance / interpretability | Judges ask "what EEG features matter most?"; rigor/experiments/tcn_interpretability.py exists | LOW | Already exists; extract top-5 features by attribution score and add to poster/paper |
| Statistical test selection justification | Using Wilcoxon + Hedges' g is already done; judges with stats knowledge will probe why non-parametric | LOW | Already documented in QA bank; add one-liner to paper methods section |

#### Differentiators (ML Rigor)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| New architecture trained: Transformer or XGBoost for temporal | "I tested new architectures for this project specifically" is stronger than "I reviewed the literature" | MEDIUM | Train Transformer (small) and XGBoost regressor on same temporal dataset; show they lose to TCN at 5-10s; strengthens TCN selection narrative |
| Per-subject R² distribution (not just mean) | Shows generalizability; judges ask "does this work for everyone?"; 35/35 claim is more credible with distribution | LOW | Already have per-subject data; add box plot to results |
| Confusion matrix / direction accuracy | "Does the model correctly predict PAC going up vs down?" is more clinically interpretable than R²; direction_classifier.py exists | LOW | Already exists; add to poster as supplementary result |
| Timing advantage analysis | "Why 5 seconds specifically?" needs quantitative support beyond just showing the horizon sweep | LOW | Show the controller decision window: minimum lead time for proactive stimulation = 3-5s based on AudioEngine latency + controller hysteresis |

#### Anti-Features (ML Rigor)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| SHAP values for EEG features | Interpretability is valuable | SHAP on time-series TCN is computationally expensive and methodologically complex; results can be misleading | Use simpler input perturbation or gradient-based attribution; tcn_interpretability.py already does this |
| Train on additional public EEG datasets | Shows generalizability | Different hardware, different protocols, different populations = not comparable to ds005048; risks introducing confounds | Document cross-population as future work; 35/35 within-dataset generalization is the correct claim |
| Hyperparameter search / AutoML | Thoroughness | Adds weeks; no meaningful gain over current Huber + AdamW + ReduceLROnPlateau for a 31K-param model | Document hyperparameter choices with justification in methods |

---

### Domain 5: Clinical Pilot Demos

What Alzheimer's care facilities (Mission Villa, Valley Medical Veterans Center) and research judges expect to see from a pilot demonstration. Based on Cognito's OVERTURE trial design and neurofeedback feasibility studies with Alzheimer's patients.

#### Table Stakes (Clinical Pilot)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Self-contained demo that runs without internet | Facilities have locked-down networks; a cloud-dependent demo will fail on-site | LOW | Streamlit runs locally; check all imports work offline; pre-download model checkpoint |
| Demo mode with simulated EEG (no hardware required) | Facilities will not let you plug hardware into patients for a first visit; must show concept without real EEG | LOW | Already in demo.py via test data replay; needs to be framed as "this is what it would look like on a real patient" |
| One-page printed explainer for facility staff | Staff will not remember what you showed them; leave something behind | LOW | 1-page PDF: what the therapy is, what the system does, how to participate, QR code to app |
| Structured feedback collection | CSEF asks for "human testing data"; need at least 3-5 structured observations from facility staff | LOW | 5-question form: device comfort, ease of use, interest in further testing, questions raised, overall impression |
| Session takes under 5 minutes to run | Care facilities have limited time; a 10-minute demo setup means they won't engage | LOW | Target: 2-minute setup, 3-minute demo replay at 10x speed, 2-minute Q&A |

#### Differentiators (Clinical Pilot)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Caregiver narrative framing in UI | "This is what the app shows the nurse during a session" vs "this is a research visualization" — same data, different framing | LOW | Rename labels: "Stimulation Active" not "StimAction.STIMULATE"; "Brain Sync Level" not "PAC value" |
| Session replay with real patient initials | "Here is what a real session from our dataset looks like" — specific > abstract; makes it tangible | LOW | Add patient anonymized label to subject selector: "Patient A (8m 12s)" |
| Facility visit log in app | Documents that pilots happened; judges want evidence of real-world engagement | LOW | Add a "Pilot Visits" section to the app: date, facility name, n_staff_shown, notes |
| Leave-behind QR code → live app | Judges want to scan and see the product themselves; facilities expect you to follow up | LOW | Deploy Streamlit to Streamlit Cloud (free); QR code on poster and flyer |

#### Anti-Features (Clinical Pilot)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Actual patient testing (EEG on Alzheimer's patients) | Seems like the natural next step | IRB required; legally prohibited without institutional approval; CSEF rules prohibit human experimentation on minors or vulnerable populations without proper oversight | Frame as "staff observation" and "caregiver UX feedback" — no EEG on patients |
| Clinical outcome claims | Strengthens the impact narrative | Cannot claim therapeutic benefit without RCT evidence; would be scientifically dishonest | Claim "feasibility demonstration" and "caregiver UX validation"; cite Cognito's published results for outcome claims |
| Remote monitoring dashboard for multiple patients | Shows product vision | Massively out of scope; requires auth, HIPAA, multi-tenant architecture | Include in written clinical roadmap document; show the architecture diagram as "Phase 3 vision" |

---

### Domain 6: Intelligence Layer on Existing Hardware

The counselor's framing: "intelligence layer on existing hardware" — not building a new device, not building software from scratch, but adding predictive ML to commodity EEG headsets that already deliver 40Hz audio.

#### Table Stakes (Intelligence Layer Narrative)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Named hardware compatibility list | Judges ask "what headset does this work with?"; vague answer loses credibility | LOW | BrainFlow supports: Muse 2 (~$250), OpenBCI Cyton ($500), OpenBCI Ganglion ($200), Neurosity Crown ($999); pick 1-2 to demonstrate with |
| Architecture diagram: headset → BrainFlow → feature extraction → TCN → AudioEngine | The "stack" must be visualizable; a diagram makes the intelligence layer concept concrete | LOW | Generate_system_architecture scripts already exist; update to show new hardware integration point |
| Hardware-agnostic feature extraction | Proves the intelligence layer is portable — not locked to one vendor | LOW | BrainFlow's uniform API means the same feature extraction code works with any supported board; document explicitly |
| "Plug our software into any EEG headset" claim | Core product positioning; differentiates from Cognito (proprietary hardware) and Myndlift (locked to BrainBit) | LOW | True for BrainFlow-supported devices; verify with synthetic board test that feature dimensions match |

#### Differentiators (Intelligence Layer)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Comparison slide: Fixed-schedule device vs Adaptive TCN device | The intelligence layer claim needs a before/after; "any headset + our software" vs "any headset without our software" | LOW | Reframe demo.py's Fixed Schedule vs TCN comparison as exactly this: same hardware, different software |
| Hardware cost breakdown in app or presentation | Makes the product roadmap credible: "a $250 Muse 2 + our software costs less than Cognito's $5,000 device" | LOW | Add cost comparison table to presentation and poster |
| Documented integration test with BrainFlow synthetic board | Proves the hardware path works; judges who ask about real-time validity can be shown the test | MEDIUM | Run BrainFlow synthetic board through full pipeline (feature extraction → TCN → controller → AudioEngine); document output |
| Clinical roadmap document: how this becomes a product | Judges want to see that you've thought beyond the demo; "intelligence layer" narrative requires a go-to-market story | LOW | 1-2 page PDF: hardware partners, regulatory path (FDA 510(k)), pricing model, Phase 1-3 clinical validation plan |

#### Anti-Features (Intelligence Layer)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Custom hardware design / PCB | "Building the whole stack" sounds impressive | Manufacturing is explicitly out of scope per PROJECT.md; distracts from the ML contribution | Emphasize software portability; "works with hardware you already have" is the differentiator |
| Proprietary headset recommendation only | Simplifies the demo | Locks the narrative to one device; undermines the "intelligence layer on any hardware" claim | BrainFlow's device-agnostic API is the technical proof; name 2-3 compatible headsets |
| Closed Android/iOS app | Product completeness | 6-month project; not buildable before CSEF; Streamlit web app is sufficient for demo | Include mobile app in written roadmap as "Phase 2 product"; show mockup if time allows |

---

## Feature Dependencies

```
[Patient Profile]
    └──requires──> [Session Log]

[Session Log]
    └──enhances──> [PAC Trend Chart (multi-session)]

[BrainFlow Python Bridge]
    └──requires──> [Hardware-Agnostic Feature Extraction]
                       └──enables──> [Real EEG Mode]
                       └──enables──> [Simulated EEG Mode (SYNTHETIC_BOARD)]

[Real EEG Mode] ──conflicts──> [Simulated EEG Mode]
    (can only be one at a time; toggle in UI)

[Adaptive Auditory Stimulus (PAC-gated)]
    └──requires──> [TCN Controller producing stim decisions]
                   (already built; AudioEngine in demo.py)

[Clinical Pilot Demo]
    └──requires──> [Demo Mode (no hardware)]
    └──requires──> [Self-contained offline deployment]
    └──enhances──> [Caregiver narrative framing in UI]

[Architecture Comparison Table]
    └──requires──> [New models trained (Transformer, XGBoost)]
    └──requires──> [Existing baseline results (persistence, Ridge)]

[Ablation Study]
    └──requires──> [Component-stripped TCN variants trained]
    └──enhances──> [Architecture Comparison Table]

[Intelligence Layer Diagram]
    └──requires──> [BrainFlow integration documented]
    └──requires──> [Hardware compatibility list]

[QR Code → Live App]
    └──requires──> [Streamlit Cloud deployment]
```

### Dependency Notes

- **Session Log requires Patient Profile:** You cannot log sessions without a patient context to attach them to. Even a minimal profile (name, ID) unblocks the session log.
- **BrainFlow bridge enables both modes:** The synthetic board path is the same code as the real hardware path, just with a different board ID. Implementing the bridge for simulated mode first means real hardware support is a one-line change.
- **Ablation study enhances architecture comparison:** The ablation results go in the same comparison table; they are the same experiment type run at different granularity.
- **QR code conflicts with local-only deployment:** Must deploy to Streamlit Cloud before printing poster with QR code. Deploy first, then print.

---

## MVP Definition

The MVP is specifically: "enough to demonstrate at CSEF judging on 2026-04-09 and at pilot facility visits."

### Launch With (v3.0 Demo-Ready)

- [ ] Patient profile + session log — makes the app feel like a clinical product, not a research script
- [ ] Hardware status indicator + dual-mode toggle (simulated / real) — essential for pilot credibility
- [ ] 40Hz volume slider (not just mute toggle) — table stakes for elderly patient use case
- [ ] Caregiver narrative framing in UI labels — same data, patient-facing language
- [ ] Session completion summary with plain-language metrics — "Your patient's brain was well-synced 72% of the time"
- [ ] Ablation study + architecture comparison table — CSEF Scientific Thought score depends on this
- [ ] New model trained (at minimum XGBoost; Transformer if time allows) — strengthens TCN selection narrative
- [ ] Multi-seed training results (mean ± std R²) — reproducibility claim
- [ ] BrainFlow synthetic board integration test documented — proves hardware path
- [ ] Streamlit Cloud deployment + QR code — pilot visitors and judges can scan and try
- [ ] Printed one-page explainer for facility visits
- [ ] Pilot feedback form embedded or QR-linked

### Add After Validation (v3.x — post-CSEF)

- [ ] PAC trend chart across sessions (multi-session view) — requires multiple real sessions to be meaningful
- [ ] Isochronic tone variant (40Hz sine carrier) — nice-to-have audio variant
- [ ] Per-subject R² box plot in app — currently in scripts; needs UI integration
- [ ] Clinical roadmap PDF — document for follow-up with facilities

### Future Consideration (v4+)

- [ ] Real hardware integration (BrainFlow → Muse 2 or OpenBCI Ganglion) — requires hardware access and testing time
- [ ] Mobile app (iOS/Android) — 6-month project; roadmap only
- [ ] Multisensory stimulation (audio + visual 40Hz flicker) — requires hardware; expand per literature
- [ ] EHR integration hooks — HIPAA; institutional partnership required
- [ ] Reinforcement learning for controller thresholds — noted as future work in paper

---

## Feature Prioritization Matrix

| Feature | User Value (CSEF Judge) | User Value (Facility Staff) | Implementation Cost | Priority |
|---------|------------------------|----------------------------|---------------------|----------|
| Caregiver narrative framing (UI labels) | HIGH — makes product feel real | HIGH — they understand it | LOW | P1 |
| Patient profile + session log | MEDIUM — shows product thinking | HIGH — basic clinical expectation | LOW | P1 |
| Hardware status indicator + dual-mode | HIGH — proves "works with real EEG" claim | HIGH — trust signal | LOW | P1 |
| Ablation study (ML rigor) | HIGH — Scientific Thought rubric | LOW | MEDIUM | P1 |
| New architecture trained (XGBoost/Transformer) | HIGH — Creativity rubric | LOW | MEDIUM | P1 |
| Multi-seed training (mean ± std) | HIGH — reproducibility | LOW | LOW | P1 |
| Streamlit Cloud deployment + QR code | HIGH — live demo touchpoint | MEDIUM — follow-up mechanism | LOW | P1 |
| Volume slider (not just mute) | LOW | HIGH — elderly patient comfort | LOW | P1 |
| Printed explainer for facilities | LOW | HIGH — leave-behind artifact | LOW | P1 |
| BrainFlow synthetic board documented | MEDIUM | LOW | MEDIUM | P2 |
| Feature importance / attribution results | MEDIUM — judges ask "what features matter?" | LOW | LOW (exists) | P2 |
| Pilot feedback form | MEDIUM — "human testing data" claim | MEDIUM — structured feedback | LOW | P2 |
| Clinical roadmap PDF | MEDIUM — product narrative | MEDIUM — demonstrates seriousness | LOW | P2 |
| PAC trend chart (multi-session) | LOW | HIGH — therapy progress | MEDIUM | P3 |
| Isochronic tone variant | LOW | MEDIUM — patient comfort | LOW | P3 |
| Real hardware BrainFlow integration | HIGH — "real closed-loop" claim | HIGH — actual use case | HIGH | P3 |

**Priority key:**
- P1: Must have for CSEF April 9 demo
- P2: Should have; add if time allows
- P3: Future; include in written roadmap only

---

## Competitor Feature Analysis

| Feature | Cognito Spectris / GENUS | Myndlift | Divergence Neuro | This Project |
|---------|--------------------------|----------|------------------|--------------|
| Stimulus delivery | Fixed 40Hz AV, personalized intensity at setup | Neurofeedback (threshold-based) | Neurofeedback (threshold-based) | Adaptive TCN-gated 40Hz audio |
| Closed-loop control | No (fixed schedule with EEG verification at enrollment) | Reactive threshold | Reactive threshold | Predictive TCN (5s ahead) |
| Hardware | Proprietary GammaSense device | BrainBit headband (locked) | BrainBit (locked) | Hardware-agnostic via BrainFlow |
| Caregiver dashboard | Not public-facing; clinical trial protocol | Full dashboard: session log, progress, live streaming | Full dashboard: custom protocols, assessments | v3.0 target: basic session log, status, summary |
| Patient profiles | Study-managed | Yes — full patient management | Yes — full patient management | v3.0 target: basic name + session count |
| Session reports | Trial data only | Automated reports with brain maps | Custom reports with qEEG | v3.0 target: post-session summary screen |
| Remote monitoring | No | Live session streaming | Live session streaming | Out of scope for v3.0 |
| Cost | ~$5,000/device (clinical trial) | $120–$490/mo subscription | $120–$490/mo subscription | Open-source software on $250 headset (roadmap) |

**Our differentiation vs Cognito:** They have a fixed schedule with upfront EEG verification. We adapt every 5 seconds. That is the core research contribution.

**Our differentiation vs Myndlift/Divergence:** They use reactive threshold control (stimulate when PAC drops). We predict the drop 5 seconds before it happens and stimulate preemptively. The 60% improvement in low-PAC targeting (83% vs 52%) is the proof.

---

## CSEF-Specific Feature Expectations

Based on the judging rubric (40 points total: Scientific Thought 10, Creativity 10, Independent Work/Skill 10, Thoroughness/Clarity 10) and the stated desire for "productized, actionable solutions":

**Scientific Thought (10pts) — what features support it:**
- Ablation study with component-level R² deltas
- Multi-seed training with mean ± std
- Architecture comparison table (8 static + LSTM + XGBoost + Transformer + TCN)
- Feature importance results from tcn_interpretability.py
- Per-subject distribution plot (not just mean results)

**Creativity (10pts) — what features support it:**
- Live QR code → deployed web app (nobody brings a live deployed product to CSEF)
- Caregiver-facing session app (most projects stop at research visualization)
- Pilot facility visits with structured feedback (human engagement data)
- New model training post-paper-submission (shows ongoing research not just a static project)

**Independent Work/Skill (10pts) — what features support it:**
- BrainFlow integration test (proves you understand the hardware stack, not just the ML)
- The leakage discovery narrative (already strong; don't bury it)
- Dashboard code authored entirely by you (demo.py is clean Python; own every line)

**Thoroughness/Clarity (10pts) — what features support it:**
- Session log that records everything (caregiver app completeness)
- Pilot feedback form with responses (quantified human engagement)
- Hardware compatibility list with named devices and prices
- Plain-language metrics in the caregiver UI (judges walk through the UI)

---

## Sources

- [Myndlift — clinician platform features](https://www.myndlift.com/) (MEDIUM confidence — live product, no version date)
- [Divergence Neuro — therapist dashboard features](https://www.divergenceneuro.com/product/) (MEDIUM confidence — live product documentation)
- [BrainFlow — supported boards including synthetic board](https://brainflow.readthedocs.io/en/stable/SupportedBoards.html) (HIGH confidence — official documentation)
- [muse-js — Web Bluetooth JavaScript library for Muse](https://github.com/urish/muse-js) (MEDIUM confidence — community project, Muse SDK deprecated for official support)
- [Cognito Therapeutics OVERTURE trial — caregiver-assisted home use design](https://pmc.ncbi.nlm.nih.gov/articles/PMC10957179/) (HIGH confidence — peer-reviewed)
- [ALZFORUM — Cognito GENUS / Spectris device details](https://www.alzforum.org/therapeutics/genus) (HIGH confidence — primary source tracker)
- [MIT News — 40Hz gamma stimulation evidence 2025](https://news.mit.edu/2025/evidence-40hz-gamma-stimulation-promotes-brain-health-expanding-0314) (HIGH confidence — official source)
- [ISEF Grand Award Judging Criteria](https://www.societyforscience.org/isef/grand-award/criteria/) (HIGH confidence — official rubric)
- [CSEF 2026 awards and judging process](https://csef.usc.edu/Info_Genl/Awards.html) (HIGH confidence — official source)
- [Feasibility of EEG headsets with elderly AD patients](https://pmc.ncbi.nlm.nih.gov/articles/PMC9228283/) (HIGH confidence — peer-reviewed feasibility study)
- [Unleashing potential: 40Hz multisensory therapy review 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC11952037/) (HIGH confidence — peer-reviewed review)
- [UX for BCI devices — accessibility requirements](https://www.kryshiggins.com/ux-bcis/) (LOW confidence — practitioner blog)

---

*Feature research for: Productized closed-loop 40Hz entrainment therapy app with ML rigor deepening*
*Researched: 2026-03-20*
