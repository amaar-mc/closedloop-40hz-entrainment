# Round 2, Draft A: Best Narrative (Combines Draft 3 + Draft 4)

**Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease**

Amaar Chughtai

---

Sound pulses at 40 Hz synchronize brain gamma oscillations and activate immune cells that clear amyloid plaques—a hallmark of Alzheimer's disease. But clinical stimulation protocols use rigid fixed schedules that ignore individual responses. Half of patients habituate within minutes; the other half maintain strong neural coupling throughout. A one-size-fits-all approach serves neither group. This project asks: can we predict when a patient's brain is about to lose entrainment, and intervene before it happens?

I analyzed EEG from 35 dementia patients (OpenNeuro ds005048), computing phase-amplitude coupling (PAC) between theta and gamma rhythms as an entrainment biomarker. I trained a causal Temporal Convolutional Network (31,000 parameters, dilations [1,2,4,8]) to forecast PAC 5-10 seconds ahead. This horizon is critical: at 1-2 seconds, simple baselines suffice; at 5-10 seconds—where a controller must act—all baselines collapse to negative R-squared while the TCN maintains R-squared of 0.25, a +0.5 margin.

Validated on all 35 subjects' real EEG, the predictive controller achieved 72.1% alignment versus 64.5% reactive (Hedges' g = 1.31, p < 0.001). It directed stimulation to 82.6% of low-PAC windows versus 51.7% (g = 4.47, p < 0.001), reaching 91% of the theoretical oracle. Every patient benefited (binomial p < 0.001). Adaptive efficiency gains of +9-11% held across six fatigue levels and four different habituation model assumptions (all p < 10^-13), demonstrating robust personalized control.

---

_Word count: 240 / 250 max_
