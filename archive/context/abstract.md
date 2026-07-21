# Abstract

**Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease**

Amaar Chughtai

---

40 Hz auditory stimulation synchronizes brain gamma oscillations, reducing amyloid pathology in Alzheimer's disease models. Current clinical protocols use fixed schedules (40 seconds on, 20 seconds off), ignoring individual brain responses. This project developed a deep learning system that predicts when a patient's brain will lose entrainment and times stimulation accordingly.

Using EEG recordings from 35 dementia patients (OpenNeuro ds005048), I computed theta-gamma phase-amplitude coupling (PAC) as a real-time entrainment biomarker. I built a causal Temporal Convolutional Network (31,000 parameters) with dilated convolutions to predict future PAC, integrated into a closed-loop controller validated on real patient data.

The central prediction finding is a horizon sweep: at 1-2 second horizons, simple baselines suffice. At 5-10 seconds — the operationally relevant range for proactive control — all baselines collapse to negative R-squared while the TCN maintains R-squared of 0.24-0.28 (+0.5 margin).

When integrated into a closed-loop controller and replayed on all 35 subjects' real EEG, the TCN achieved 72.1% epoch alignment versus 64.5% for reactive control (Hedges' g = 1.31, p < 0.001, Wilcoxon signed-rank). It targeted 82.6% of low-PAC windows for stimulation versus 51.7% reactive (g = 4.47, p < 0.001), reaching 91% of the theoretical oracle bound. All 35 subjects benefited (binomial p < 0.001). In simulation, adaptive scheduling efficiency increased with fatigue severity (+9.0% to +11.2%, all p < 0.001), and the advantage held across four different fatigue model assumptions (+6.9% to +19.0%, all p < 10^-13). Half of subjects habituate while half do not, validating the need for personalized control.

---

_Word count: 247 / 250 max_

_Category: Biological Science and Engineering, Computational Biology and Bioinformatics_
_Synopsys Championship — Santa Clara County, March 2026_
