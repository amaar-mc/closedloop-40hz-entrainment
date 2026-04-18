# Clinical Roadmap — From Research to Practice

**Document purpose:** Structured clinical pathway for judges, facility partners, and potential
collaborators. Demonstrates that the research has a realistic path toward clinical utility.

---

## 1. Current State

### System Capabilities

- **Hardware:** Muse 2 consumer EEG headset (4 dry electrodes: TP9, AF7, AF8, TP10)
- **Software:** Two-stage deep learning pipeline — EEGNet (1,457 params) for real-time PAC
  estimation + Causal TCN (31,043 params) for 5-10 second temporal forecasting
- **Interface:** Streamlit caregiver application with patient profiles, session history, and
  live brain state visualization
- **Deployment:** Simulated EEG for safe demonstration; real-time inference pipeline ready
  for live streaming when hardware is paired

### Validation Summary

| Metric | Value | Method |
|--------|-------|--------|
| Dataset | N = 35 elderly subjects | OpenNeuro ds005048 (Lahijanian 2024) |
| TCN R-squared at 5-10s horizons | 0.24 - 0.28 | Cross-validated, subject-level splits |
| Targeting alignment | 72.1% vs 64.5% reactive | Offline replay on real EEG |
| Low-PAC sensitivity | 82.6% vs 51.7% reactive | Real EEG, p < 0.001 |
| Oracle proximity | 91% of theoretical best | PAC gap: 30.5 vs 33.3 |
| Patient generalization | 35/35 benefit (100%) | Including 6 held-out test subjects |

### Current Limitations

- Validation is offline replay (counterfactual decisions on recorded EEG), not live closed-loop
- Session durations are 6-10 minutes; clinical protocols run 60 minutes
- Consumer EEG gamma signal-to-noise ratio is limited compared to research-grade systems
- No longitudinal data (repeated sessions over weeks/months)

---

## 2. Integration Path — Fitting Into Existing Care

### Target Setting

Memory care facilities and neurology clinics that already provide cognitive therapy,
neurofeedback, or structured activity programs for dementia patients.

### Role: Decision Support, Not Autonomous Treatment

The system is positioned as **decision support for therapy scheduling** — it advises caregivers
on when to initiate and pause 40 Hz auditory stimulation sessions. It does not operate
autonomously. The caregiver retains full control at all times.

### Integration Points

| Existing Workflow | System Role |
|-------------------|-------------|
| Morning cognitive therapy sessions | Suggest optimal session timing based on baseline PAC trends |
| Neurofeedback programs | Complement existing protocols with predictive 40 Hz scheduling |
| Activity directors' daily schedules | Provide data-driven input on which patients benefit most |
| Family caregiver home sessions | Mobile app guides session start/stop with real-time feedback |

### Key Principle: Augment, Do Not Replace

Caregivers and clinicians know their patients. The system provides quantitative neural state
information that is otherwise invisible — it does not override clinical judgment. Every
stimulation decision can be manually overridden from the app.

---

## 3. Clinical Testing Plan

### Phase A: Observational (No Stimulation)

**Goal:** Establish EEG baselines and validate real-time PAC estimation in a clinical setting.

| Parameter | Value |
|-----------|-------|
| Participants | 10 (mild cognitive impairment or early Alzheimer's) |
| Duration | 2 weeks, 3 sessions per week, 30 minutes each |
| Protocol | Wear EEG headset during normal activities; no stimulation delivered |
| Primary outcome | PAC estimation accuracy vs research-grade ground truth |
| Secondary outcomes | Comfort ratings, headset compliance, baseline PAC variability |
| Regulatory | Exempt from IRB review (observational, no intervention) |
| Estimated timeline | 4-6 weeks including recruitment |

**Success criteria:** Real-time PAC estimation within 15% of offline computation. Compliance
rate above 80% (patients tolerate 30-minute sessions with headset).

### Phase B: Feasibility (Controlled Stimulation)

**Goal:** Validate that the closed-loop controller makes safe and appropriate decisions in a
live setting with actual stimulation delivery.

| Parameter | Value |
|-----------|-------|
| Participants | 20 (stratified by MCI severity) |
| Duration | 4 weeks, 5 sessions per week, 60 minutes each |
| Protocol | Closed-loop adaptive stimulation vs sham (randomized crossover) |
| Primary outcome | Session-level PAC maintenance (adaptive vs sham) |
| Secondary outcomes | Comfort, side effects, caregiver usability ratings |
| Regulatory | **IRB approval required** — informed consent, DSMB oversight |
| Estimated timeline | 3-4 months including approval |

**Safety controls:** Maximum stimulation volume capped at 70 dB SPL. Automatic session
termination if patient distress detected. Clinician override at all times.

### Phase C: Comparative (Predictive vs Reactive)

**Goal:** Demonstrate that predictive (TCN) control produces measurably better cognitive
outcomes than reactive control over a multi-week intervention.

| Parameter | Value |
|-----------|-------|
| Participants | 50 (mild to moderate Alzheimer's) |
| Duration | 8 weeks, daily 60-minute sessions |
| Protocol | Predictive TCN controller vs reactive threshold controller (crossover) |
| Primary outcome | MMSE score change from baseline |
| Secondary outcomes | PAC maintenance, habituation rate, caregiver burden (ZBI) |
| Regulatory | **IRB approval required**, registered at ClinicalTrials.gov |
| Estimated timeline | 6-8 months |

**Power analysis:** Based on pilot effect size (d = 1.31 for alignment), 50 participants
provides >95% power to detect a 2-point MMSE difference at alpha = 0.05.

---

## 4. Remote Monitoring Vision

### Architecture

```
Patient Home / Facility          Cloud Infrastructure          Clinician Portal
+------------------+          +---------------------+       +------------------+
| Muse 2 headset   |  BLE  →  | Session data store  |  →    | Dashboard        |
| Caregiver app    |  WiFi →  | PAC trend analytics |       | Patient overview  |
| Local inference  |          | Anomaly detection   |       | Alerts           |
+------------------+          +---------------------+       +------------------+
```

### Caregiver App (Current)

- Patient profiles with session history
- Real-time brain state visualization during sessions
- Session summary with PAC metrics and targeting accuracy
- Works offline for session recording; syncs when connected

### Cloud Dashboard (Planned)

- Longitudinal PAC trend graphs per patient
- Cross-patient comparison within a facility
- Automated alerts: significant PAC decline, missed sessions, unusual patterns
- Export to CSV/PDF for clinical records

### Clinician Review Portal (Planned)

- Multi-facility overview for neurologists overseeing distributed patients
- Weekly summary reports with statistical trend analysis
- Medication interaction flags (e.g., cholinesterase inhibitors affecting EEG)
- Secure HIPAA-compliant data handling

### Alert Examples

| Alert Type | Trigger | Action |
|------------|---------|--------|
| PAC Decline | 3-session downward trend | Notify clinician for protocol review |
| Habituation Spike | Within-session PAC drop > 40% | Suggest session structure change |
| Compliance Drop | < 3 sessions in 7 days | Caregiver reminder notification |
| Anomalous Pattern | EEG artifact or electrode quality issue | Flag for technical review |

---

## 5. Hardware Scaling Path

### Tier 1: Consumer (Current)

| Specification | Value |
|---------------|-------|
| Device | Muse 2 |
| Channels | 4 dry electrodes (TP9, AF7, AF8, TP10) |
| Resolution | 12-bit |
| Sampling rate | 256 Hz |
| Cost | ~$200 |
| Gamma SNR | Baseline (limited by dry electrode contact) |
| Setting | Home use, memory care facility common areas |

**Strengths:** No gel, no technician, comfortable for elderly patients, affordable.
**Limitations:** Gamma band (38-42 Hz) signal-to-noise ratio is marginal with dry electrodes.

### Tier 2: Research-Grade Portable (Next Step)

| Specification | Value |
|---------------|-------|
| Device | OpenBCI Cyton |
| Channels | 8 gel electrodes (configurable montage) |
| Resolution | 24-bit |
| Sampling rate | 250 Hz |
| Cost | ~$500 |
| Gamma SNR | ~4x improvement over Muse 2 |
| Setting | Supervised facility sessions, clinical pilot |

**Strengths:** 24-bit resolution dramatically improves gamma band fidelity. 8 channels enable
better spatial coverage of frontal and temporal regions. Open-source and programmable.
**Upgrade path:** Same software stack — only the sensor adapter layer changes. The
StreamingFeatureExtractor and TCN model are hardware-agnostic.

### Tier 3: Clinical (Long-Term)

| Specification | Value |
|---------------|-------|
| Device | EGI HydroCel or BrainProducts actiCHamp |
| Channels | 64-128 electrodes |
| Resolution | 24-bit |
| Sampling rate | 500-1000 Hz |
| Cost | $15,000-$30,000 |
| Gamma SNR | Research gold standard |
| Setting | Hospital neurology department, clinical trial |

**Strengths:** Gold-standard signal quality for clinical validation and regulatory submission.
**Key point:** The intelligence layer (EEGNet + TCN + controller) is identical across all
three tiers. Only the sensor interface changes. Models trained on higher-quality data will
produce better predictions, but the architecture and control logic remain the same.

### Scaling Diagram

```
Consumer          Research          Clinical
Muse 2    →    OpenBCI Cyton  →   64-ch Cap
4 ch, dry       8 ch, gel         64+ ch, gel
$200            $500              $15,000+
Home/Facility   Supervised        Hospital

        Same Software Stack Throughout
   EEGNet → Feature Extraction → Causal TCN → Controller
```

---

## 6. Community Benefit Narrative

### The Problem at Scale

- **6.7 million** Americans currently living with Alzheimer's disease
- **$321 billion** annual cost of Alzheimer's care in the United States
- **11 million** unpaid caregivers providing 15.3 billion hours of care annually
- By 2050, projected to reach 12.7 million patients and $1 trillion in costs
- Average time from diagnosis to loss of independence: 4-8 years

### Who This System Helps

**Patients:** Receive stimulation therapy that adapts to their individual brain state rather
than following a generic schedule. The system learns their patterns — when they respond best,
when they habituate, when to rest.

**Caregivers:** Reduce guesswork in therapy scheduling. Instead of following a rigid protocol
and hoping it works, caregivers get quantitative feedback on whether the therapy is engaging
the patient's brain. This reduces caregiver stress and improves therapy confidence.

**Facilities:** Data-driven therapy scheduling across multiple patients. Activity directors
can prioritize sessions for patients showing declining PAC trends. Facilities that adopt
adaptive protocols can demonstrate measurable outcomes to families and insurers.

**Clinicians:** Longitudinal neural state data that is currently invisible. Neurologists can
track whether 40 Hz therapy is producing sustained PAC improvement over weeks and months,
informing treatment decisions.

### Facility Partnerships

**Mission Villa Memory Care** (Santa Clara County)
- Contacted for observational pilot partnership
- Interest in non-pharmacological therapy augmentation
- 40-bed memory care unit with existing activity program

**Valley Medical Center** (Neurology Department)
- Potential clinical validation partner for Phase B/C trials
- Access to diagnosed Alzheimer's and MCI patient population
- IRB infrastructure for human subjects research

### Accessibility Commitment

The consumer hardware tier ($200 Muse 2) is deliberately chosen to make this system accessible
outside of hospital settings. The goal is not to build a $30,000 clinical device — it is to
bring personalized neural therapy guidance into the homes and community facilities where
patients spend most of their time.

The software is open-source. The models are lightweight enough to run on a smartphone. The
clinical roadmap includes a free tier for individual caregivers.

---

## Regulatory Considerations

### Current Status

The system in its current form is a **research tool** operating on recorded and simulated EEG
data. It does not deliver therapeutic stimulation to patients and does not require FDA clearance
for demonstration or research use.

### Path to Regulatory Approval

| Milestone | Regulatory Requirement |
|-----------|----------------------|
| Observational study (Phase A) | IRB exemption (no intervention) |
| Feasibility study (Phase B) | IRB approval, informed consent, DSMB |
| Comparative study (Phase C) | IRB approval, ClinicalTrials.gov registration |
| Commercial deployment | FDA 510(k) or De Novo classification |
| Clinical claims | FDA-cleared indication for use |

### Classification Pathway

The most likely FDA pathway is **De Novo classification** as a Class II medical device for
"EEG-guided auditory neurostimulation scheduling." Predicate devices include existing
neurofeedback systems (e.g., NeurOptimal) and auditory stimulation devices.

### Timeline Estimate

| Year | Milestone |
|------|-----------|
| 2026 | Phase A observational pilot complete |
| 2027 | Phase B feasibility study with IRB approval |
| 2028 | Phase C comparative trial begins |
| 2029 | FDA De Novo submission |
| 2030 | Initial commercial deployment (if approved) |

---

*Document version: 1.0 — March 2026*
*Author: Amaar Chughtai*
*For questions: amaardevx@gmail.com*
