# Abstract Draft 3: Problem-Solution Narrative

**Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease**

Amaar Chughtai

---

When 40 Hz sound pulses synchronize brain gamma oscillations, microglia activate and clear amyloid plaques—a hallmark of Alzheimer's disease. But current therapy protocols stimulate on rigid 40-second-on, 20-second-off schedules. Half of patients habituate within minutes; the other half maintain strong coupling throughout. A fixed schedule serves neither group optimally. This project asks: can we predict when the brain is about to lose entrainment, and intervene before it happens?

I analyzed EEG from 35 dementia patients (OpenNeuro ds005048), computing phase-amplitude coupling (PAC) between theta and gamma rhythms as a real-time entrainment biomarker. I trained a causal Temporal Convolutional Network (31,000 parameters, dilations [1,2,4,8], 44-second receptive field) to predict future PAC. At 5-10 second horizons—where proactive control decisions must be made—persistence and Ridge regression produce negative R-squared (worse than guessing the mean), while the TCN maintains R-squared of 0.24-0.28.

I integrated the TCN into a closed-loop controller and replayed it on all 35 subjects' real EEG. The predictive controller achieved 72.1% alignment between stimulation and need, versus 64.5% for reactive control (Hedges' g = 1.31, p < 0.001, Wilcoxon signed-rank). It targeted 82.6% of low-PAC windows versus 51.7% reactive (g = 4.47, p < 0.001), reaching 91% of the theoretical oracle. Every subject benefited (binomial p < 0.001). Adaptive efficiency gains held across four different fatigue assumptions (+6.9% to +19.0%, all p < 10^-13).

---

_Word count: 244 / 250 max_
