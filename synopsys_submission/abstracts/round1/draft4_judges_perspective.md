# Abstract Draft 4: Judge-Friendly (Accessible + Impressive)

**Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease**

Amaar Chughtai

---

Sound pulses at 40 Hz can synchronize brain waves and trigger immune cells to clear toxic amyloid plaques in Alzheimer's disease. Current therapies deliver stimulation on fixed schedules, but individual brains respond differently—half of patients habituate within minutes while others maintain strong neural coupling throughout. I built an AI system that predicts when each patient's brain will lose its therapeutic rhythm, enabling personalized stimulation that responds to real-time brain state.

Using EEG from 35 dementia patients (OpenNeuro ds005048), I measured theta-gamma phase-amplitude coupling as an entrainment biomarker and trained a Temporal Convolutional Network (31,000 parameters) with causal architecture to forecast coupling strength 5-10 seconds ahead. This prediction horizon is critical: at shorter intervals, simply assuming "nothing changes" works. At 5-10 seconds—where a controller must act to preempt entrainment loss—every baseline method fails (negative R-squared), while my model maintains R-squared of 0.25, a +0.5 margin.

Validated on all 35 subjects' real brain recordings, the predictive controller achieved 72.1% optimal alignment versus 64.5% for reactive control (Hedges' g = 1.31, p < 0.001). It directed stimulation to 82.6% of therapeutically needed windows versus 51.7% reactive (g = 4.47, p < 0.001), reaching 91% of the theoretical maximum. Every patient benefited. Simulations confirmed adaptive scheduling efficiency gains of +9-11% across six fatigue levels and four different habituation models, demonstrating robustness beyond any single assumption.

---

*Word count: 241 / 250 max*
