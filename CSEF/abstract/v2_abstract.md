# Abstract

**Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease**

Amaar Chughtai

---

Alzheimer's disease affects over 55 million people worldwide, and emerging research shows that 40 Hz auditory stimulation can drive gamma-frequency brain rhythms that help clear toxic amyloid-beta plaques. Current protocols deliver this therapy on a fixed schedule, ignoring individual responses; some patients habituate within minutes while others maintain entrainment. This project develops a closed-loop deep learning system to predict when a patient's brain will lose entrainment, enabling individualized stimulation timing.

I analyzed EEG from 35 elderly subjects (OpenNeuro ds005048) and computed phase-amplitude coupling (PAC), the coordination between theta-band and gamma-band rhythms, as a biomarker of entrainment strength. A feature ablation study revealed that 12 PAC-trajectory and stimulation-context features outperform the full 73-feature set five-fold on held-out subjects (test R-squared = 0.606 +/- 0.032, 5 seeds, vs. -0.025), identifying spectral features as the source of cross-subject overfitting. I trained a causal Temporal Convolutional Network (TCN, 22,914 parameters) on these 12 features to forecast PAC five seconds ahead and integrated it into a closed-loop controller validated on all 35 subjects' EEG.

At five-to-ten-second horizons all baselines collapsed to negative R-squared while the TCN maintained 0.37-0.67. The controller directed stimulation to 82.6% of low-PAC windows versus 51.7% for reactive control (g = 4.47, p < 0.001) and achieved 72.1% alignment versus 64.5% (g = 1.31, p < 0.001), reaching 91% of the oracle's targeting gap. All 35 subjects benefited (p < 0.001). These results demonstrate that PAC forecasting enables personalized 40 Hz therapy outperforming fixed and reactive protocols, advancing treatment for Alzheimer's disease.

*Word count: 250 / 250 max | Characters: 1,790 / 1,800 max*

*California Science and Engineering Fair (CSEF) — April 2026*
