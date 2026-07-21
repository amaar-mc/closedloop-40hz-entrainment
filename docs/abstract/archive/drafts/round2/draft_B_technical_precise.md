# Round 2, Draft B: Technical Precision (Combines Draft 2 + Draft 5)

**Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease**

Amaar Chughtai

---

40 Hz auditory stimulation drives gamma-band neural entrainment that reduces amyloid pathology in Alzheimer's disease models. Current protocols deliver stimulation on fixed schedules, ignoring that half of patients habituate rapidly while others maintain coupling. I engineered a closed-loop system that predicts brain entrainment state 5-10 seconds ahead, enabling adaptive stimulation targeted to periods of genuine therapeutic need.

From 35 dementia patients' EEG (OpenNeuro ds005048, 7 frontal channels, 250 Hz), I extracted theta-gamma phase-amplitude coupling (PAC) as a biomarker and built two neural networks: an EEGNet (1,457 parameters) for real-time PAC estimation and a causal Temporal Convolutional Network (31,000 parameters, dilations [1,2,4,8], 44-second receptive field) for temporal forecasting. A horizon sweep revealed the TCN's value: at 1-2 seconds, persistence suffices; at 5-10 seconds—the operationally relevant range—all baselines collapse to negative R-squared while the TCN maintains 0.25 (+0.5 margin).

Replaying the TCN controller on all 35 subjects' real EEG, it achieved 72.1% epoch alignment versus 64.5% reactive (Hedges' g = 1.31, p < 0.001, Wilcoxon signed-rank) and targeted 82.6% of low-PAC windows for stimulation versus 51.7% (g = 4.47, p < 0.001), reaching 91% of oracle performance. All 35 subjects benefited (binomial p < 0.001). In simulation, adaptive efficiency gains (+9-11%) held across six fatigue levels and four different habituation models (all p < 10^-13), confirming robustness independent of any single fatigue assumption.

---

_Word count: 245 / 250 max_
