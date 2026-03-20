# Hardware Mode Decision: Dual-Mode Strategy

**Decision date:** 2026-03-20
**Status:** Confirmed

## Decision

The app operates in **dual mode**:

1. **Simulated mode** (primary, always available): Uses BrainFlow SYNTHETIC_BOARD or ds005048 replay data. The full closed-loop pipeline runs on validated research-quality data. This is the reliable demo path.

2. **Real EEG mode** (Muse 2, when hardware available): Muse 2 headset streams 4-channel EEG (AF7, AF8, TP9, TP10) via BrainFlow. Data feeds a retrained 4-channel model (F7/F8/T7/T8 proxy from ds005048). Stimulus decisions are made from live predictions.

## Consumer EEG Gamma Limitation

Consumer dry-electrode headsets (Muse 2, NeuroSky, etc.) cannot reliably measure gamma-band (38-42 Hz) brain activity at frontal sites due to:

- **EMG contamination**: Frontalis muscle activity peaks at 30-40 Hz, directly overlapping gamma. Dry electrode impedance (300+ kOhm) is too high to reject this artifact.
- **Validation evidence**: Kuziek et al. (2024) found Muse frontal gamma correlation with research-grade EEG of only r=0.47. Krigolson et al. (2021) excluded gamma entirely from Muse validation.
- **TP9/TP10 signal quality**: Multiple studies report majority of recordings at these positions show non-physiological signals (Ratti et al., 2017).

**Mitigation**: The model is trained on research-quality data at approximate Muse positions (F7/F8/T7/T8 from ds005048). At demo time, the model will receive noisier input and predictions will be less accurate. This is acknowledged and documented. The 40 Hz ASSR (stimulus-induced, phase-locked) may be more detectable than spontaneous gamma, partially mitigating the noise.

## CSEF Pitch

"I validated the model on research-grade 7-channel EEG from 35 patients. Then I adapted it for a $100 consumer headset to demonstrate that the architecture transfers to accessible hardware. Performance drops from R²=X (research) to R²=Y (consumer-proxy), which quantifies the hardware quality gap. With clinical-grade EEG ($600 OpenBCI), near-research performance is recoverable. The intelligence layer is hardware-agnostic."

## Hardware Budget

| Item | Cost |
|------|------|
| Muse 2 (refurbished) | ~$100-130 |
| Standard headphones (for 40 Hz audio) | ~$20 |
| **Total** | **~$120-150** |

## Upgrade Path (for judges)

| Hardware Tier | Cost | Channels | Gamma Quality |
|--------------|------|----------|---------------|
| Muse 2 (demo) | $130 | 4, dry | Poor — EMG contaminated |
| OpenBCI Ganglion + gel cups | $280 | 4, gel | Moderate — better impedance |
| OpenBCI Cyton + gel cap | $2,280 | 8, gel | Good — research-validated |
| Clinical EEG system | $10K+ | 19-64, gel | Excellent — gold standard |
