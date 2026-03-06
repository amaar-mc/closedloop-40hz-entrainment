# Abstract Draft 2: Engineering Focus Approach

**Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease**

Amaar Chughtai

---

40 Hz auditory stimulation drives gamma-band neural entrainment that reduces amyloid pathology in Alzheimer's disease models. Clinical protocols deliver stimulation on fixed schedules, wasting therapeutic exposure when patients are already entrained and missing windows when entrainment fades. I engineered a closed-loop system that predicts brain entrainment state 5-10 seconds into the future, enabling adaptive scheduling that delivers stimulation precisely when needed.

From 35 dementia patients' EEG recordings (OpenNeuro ds005048, 7 frontal channels, 250 Hz), I extracted theta-gamma phase-amplitude coupling (PAC) as an entrainment biomarker and built two neural networks sized for the 17,283-sample dataset: an EEGNet (1,457 parameters) for real-time PAC estimation and a causal Temporal Convolutional Network (31,000 parameters) with dilated convolutions spanning a 44-second receptive field for temporal forecasting.

A horizon sweep across 1-10 seconds revealed the TCN's unique value: at 1-2 seconds, simple persistence suffices; at 5-10 seconds—the operationally relevant range—all baselines collapse to negative R-squared while the TCN maintains R-squared of 0.25 (+0.5 margin). Replaying the TCN controller on all 35 subjects' real EEG data, it achieved 72.1% epoch alignment versus 64.5% reactive (Hedges' g = 1.31, p < 0.001) and targeted 82.6% of low-PAC windows for stimulation versus 51.7% (g = 4.47, p < 0.001), reaching 91% of oracle performance. All 35 subjects benefited. In simulation, adaptive efficiency gains of +9-11% held across four different fatigue model assumptions (all p < 10^-13).

---

*Word count: 248 / 250 max*
