# Key Citations: Know These Cold

Every paper you might need to reference during an interview. Format: Author (Year). What it proved. Memorization hook.

---

## The Core Papers (Must Know)

**Iaccarino et al. (2016). "Gamma frequency entrainment attenuates amyloid load and modifies microglia." Nature, 540(7632), 230-235.**
- 40 Hz visual flicker reduced amyloid-beta by 40-50% in 5XFAD mice after 1 hour
- Microglia transformed from resting to phagocytic state
- *Hook: "Iaccarino 2016 -- the MIT paper that started everything. 50% amyloid reduction, one hour."*

**Murdock et al. (2024). "Multisensory gamma stimulation promotes glymphatic clearance of amyloid." Nature, 627, 149-156.**
- Identified the actual clearance mechanism: VIP interneurons -> arterial pulsatility -> AQP4 -> glymphatic flow
- Blocking glymphatic clearance eliminated the amyloid-clearing effect
- Also showed combined audiovisual was more effective than single-modality
- *Hook: "Murdock 2024 -- proved HOW it works. AQP4 channels, glymphatic flow. Necessary, not just correlated."*

**Lahijanian et al. (2024). "40-Hz auditory entrainment in elderly." Scientific Reports, 14.**
- Published the OpenNeuro ds005048 dataset (your data source)
- 35 elderly subjects (17 AD, 6 MCI, 10 HC, 2 unspecified)
- Showed enhanced default mode network connectivity from auditory 40 Hz
- *Hook: "Lahijanian 2024 -- the dataset. 35 patients, auditory 40 Hz, publicly available on OpenNeuro."*

**Tort et al. (2010). "Measuring phase-amplitude coupling between neuronal oscillations of different frequencies." Journal of Neurophysiology, 104(2), 1195-1210.**
- Defined the Modulation Index for PAC computation using KL divergence across phase bins
- The standard PAC computation method
- *Hook: "Tort 2010 -- how I compute PAC. KL divergence, 18 phase bins."*

---

## Important Supporting Papers

**Chan et al. (2025). "Long-term safety of 40 Hz sensory stimulation." [Journal TBD]**
- 2-year safety study in 5 Alzheimer's patients
- Slower cognitive decline in 3 of 5 patients
- APOE genotype affected response
- *Hook: "Chan 2025 -- two-year safety, no adverse effects. Cognitive benefit in 3/5."*

**Soula et al. (2023). "40 Hz sensory stimulation does not entrain native gamma oscillations in Alzheimer's disease model mice." Nature Neuroscience.**
- Critique: visual flicker drives SSVEP, not endogenous gamma entrainment
- Your response: applies to visual, not auditory; controller is mechanism-agnostic
- *Hook: "Soula 2023 -- the critique. SSVEP not entrainment. But I use auditory, and my system doesn't depend on which mechanism is correct."*

**Fortunato et al. [Year varies]. Non-responder rate ~30%.**
- Found approximately 30% of patients don't respond to 40 Hz
- Motivates adaptive delivery (detect non-response faster)
- *Hook: "Fortunato -- 30% non-responders. Fixed schedule can't detect that."*

---

## Industry & Regulatory

**Cognito Therapeutics**
- HOPE trial: 670 patients, Phase 3, randomized, sham-controlled
- Spectris device: combined audiovisual 40 Hz, 1 hour daily
- FDA Breakthrough Device Designation
- $105 million raised March 2026
- *Hook: "Cognito -- furthest along. 670-patient Phase 3, Breakthrough Device. But fixed schedule."*

**FDA (April 2025)**
- Announced phasing out mandatory animal testing for many drug types
- Favoring computational/in-silico methods
- *Hook: "FDA is moving toward computational validation before clinical trials."*

**Medtronic Adaptive DBS (February 2025)**
- FDA approved closed-loop DBS for Parkinson's using beta power biomarker
- Same principle as your system but for Parkinson's with different biomarker
- *Hook: "Closed-loop DBS -- same concept, different disease. FDA-approved Feb 2025."*

---

## Dataset Details (if pressed)

**OpenNeuro ds005048, version 1.0.1**
- Authors: Lahijanian et al.
- Year: 2024
- Journal: Scientific Reports
- Subjects: 35 elderly (17 Alzheimer's, 6 MCI, 10 healthy controls, 2 unspecified)
- EEG: 19 channels recorded, 7 frontal selected
- Sampling: 250 Hz
- Protocol: 40 Hz amplitude-modulated auditory tones, 40s on / 20s off cycles
- Already preprocessed: 1 Hz HP, 50 Hz notch, ICA, CAR (by Makoto's pipeline)
