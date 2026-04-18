# Abstract

> **Status:** placeholder — draft after conference target confirmed (page limit affects length)
> **Target length:** 150-250 words (IEEE EMBC) / 250-300 words (NeurIPS workshop)

---

## Draft

Fixed-schedule 40 Hz auditory entrainment protocols for Alzheimer's disease ignore real-time brain state, delivering stimulation regardless of whether the patient's brain is entrained. Reactive closed-loop systems improve on fixed schedules but respond only after entrainment loss has already occurred. We present a two-stage predictive system that forecasts theta-gamma phase-amplitude coupling (PAC) 5–10 seconds into the future, enabling proactive stimulation scheduling.

Our key finding is methodological: spectral EEG features — which encode subject-specific brain anatomy — fail to generalize across patients, causing temporal prediction to collapse (test R² = −0.025). Using only 12 portable features derived from PAC trajectory and stimulation context raises test R² to 0.606 ± 0.032 (5-seed mean), a 5-fold improvement over the full 73-feature model. At 3–10 second horizons — the operationally relevant range for proactive control — a causal temporal convolutional network (TCN) maintains R² = 0.577–0.669 while persistence and Ridge regression collapse to negative R².

Validated on real EEG from 35 dementia patients (OpenNeuro ds005048), the TCN predictive controller achieves 72.1% epoch alignment versus 64.5% for reactive control (Hedges' g = 1.31, p < 0.001), targets 82.6% of low-PAC windows for stimulation versus 51.7% (g = 4.47, p < 0.001), and reaches 91% of the theoretical oracle bound. All 35 patients benefit. The adaptive advantage grows with neural habituation severity, confirming clinical utility precisely when personalization matters most.

---

## Alternate shorter version (150 words)

[to fill in once conference confirmed]
