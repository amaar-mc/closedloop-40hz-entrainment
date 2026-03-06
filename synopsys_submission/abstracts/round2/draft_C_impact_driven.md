# Round 2, Draft C: Impact-Driven (Combines Draft 1 + Draft 4)

**Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease**

Amaar Chughtai

---

Alzheimer's disease affects 55 million people worldwide. A landmark discovery showed 40 Hz sound pulses can synchronize brain gamma waves and trigger immune cells to clear toxic amyloid plaques. Clinical trials now deliver stimulation on fixed schedules—but individual brains respond differently. Half of patients habituate within minutes while others maintain strong neural coupling, yet everyone receives the same rigid protocol.

I built an AI system that predicts when each patient's brain will lose its therapeutic rhythm 5-10 seconds before it happens, enabling personalized stimulation. Using EEG from 35 dementia patients (OpenNeuro ds005048), I measured theta-gamma phase-amplitude coupling (PAC) as a biomarker and trained a causal Temporal Convolutional Network (31,000 parameters) with dilated convolutions spanning a 44-second receptive field. The key finding: at 5-10 second horizons—where a controller must act to preempt loss—every baseline method fails (negative R-squared) while my model maintains R-squared of 0.25, a +0.5 margin.

Validated on all 35 subjects' real brain recordings, the predictive controller achieved 72.1% optimal alignment versus 64.5% reactive (Hedges' g = 1.31, p < 0.001, Wilcoxon). It directed stimulation to 82.6% of windows needing treatment versus 51.7% reactive (g = 4.47, p < 0.001), reaching 91% of the theoretical maximum. Every patient benefited. Adaptive scheduling gains of +9-11% held across six fatigue levels and four habituation model types (all p < 10^-13), demonstrating the system's robustness.

---

*Word count: 243 / 250 max*
