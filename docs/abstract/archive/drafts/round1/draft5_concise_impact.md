# Abstract Draft 5: Concise High-Impact

**Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease**

Amaar Chughtai

---

40 Hz auditory stimulation synchronizes brain gamma oscillations and reduces amyloid pathology in Alzheimer's disease. Clinical protocols use fixed stimulation schedules that ignore individual brain responses—half of patients habituate rapidly while others do not. I developed a predictive closed-loop system that forecasts entrainment state and adapts stimulation timing to each patient's neural dynamics.

From 35 dementia patients' EEG recordings (OpenNeuro ds005048), I computed theta-gamma phase-amplitude coupling (PAC) as a biomarker and trained a causal Temporal Convolutional Network (31,000 parameters) to predict future PAC 5-10 seconds ahead. At these horizons—the critical range for proactive intervention—all baseline predictors collapse to negative R-squared (worse than the population mean), while the TCN maintains R-squared of 0.24-0.28, a +0.5 margin that enables meaningful control decisions.

The TCN-based controller, validated by replaying real EEG from all 35 subjects, achieved 72.1% epoch alignment versus 64.5% for reactive control (Hedges' g = 1.31, p < 0.001, Wilcoxon signed-rank). It directed stimulation to 82.6% of low-coupling windows needing treatment versus 51.7% reactive (g = 4.47, p < 0.001), a 60% improvement in therapeutic targeting that reached 91% of the theoretical oracle bound. All 35 subjects benefited (binomial p < 0.001). Simulation confirmed the adaptive advantage holds across six fatigue severity levels (+9-11%, all p < 0.001) and four different habituation mechanisms (+6.9% to +19.0%, all p < 10^-13), ruling out model-specific artifacts.

---

*Word count: 243 / 250 max*
