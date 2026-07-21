# Abstract Draft 1: Clinical Hook Approach

**Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease**

Amaar Chughtai

---

Alzheimer's disease affects 55 million people worldwide, with no cure. A breakthrough discovery showed that 40 Hz sensory stimulation can reduce toxic amyloid plaques in mouse brains by synchronizing neural gamma oscillations (Iaccarino et al., 2016). Clinical trials now test this in humans using fixed schedules—40 seconds of stimulation, 20 seconds of rest, repeated for an hour—but this ignores that every patient's brain responds differently, and many habituate within minutes.

I developed a deep learning system that predicts when a patient's brain will lose gamma entrainment 5-10 seconds before it happens, enabling adaptive stimulation that targets therapeutic delivery to periods of genuine need. Using EEG recordings from 35 dementia patients (OpenNeuro ds005048), I computed theta-gamma phase-amplitude coupling (PAC) as a real-time entrainment biomarker and built a causal Temporal Convolutional Network (31,000 parameters) to forecast future brain state.

The central finding: at 5-10 second prediction horizons—the range needed for proactive control—all baseline methods collapse to negative R-squared while the TCN maintains R-squared of 0.24-0.28, a +0.5 margin. Integrated into a closed-loop controller and validated on all 35 subjects' real EEG, the system achieved 72.1% epoch alignment versus 64.5% for reactive control (Hedges' g = 1.31, p < 0.001), targeted 82.6% of low-coupling windows for stimulation versus 51.7% reactive (g = 4.47, p < 0.001), and reached 91% of the theoretical oracle bound. All 35 subjects benefited, with results robust across four different fatigue model assumptions.

---

_Word count: 242 / 250 max_
