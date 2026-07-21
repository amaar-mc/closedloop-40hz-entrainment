# Abstract

**P10: Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's**

Amaar Chughtai

---

Alzheimer's disease affects over 55 million people worldwide, and emerging research shows that 40 Hz auditory stimulation can drive gamma-frequency brain rhythms that help clear toxic amyloid-β plaques. Current protocols deliver this therapy on a fixed schedule, ignoring individual responses; some patients habituate within minutes while others maintain entrainment. This project presents a closed-loop deep learning system to predict when a patient's brain will lose entrainment, enabling individualized stimulation timing.

I analyzed EEG recordings from 35 elderly subjects including dementia patients and healthy controls (OpenNeuro ds005048) and computed phase-amplitude coupling (PAC), the coordination between slow theta-band and fast gamma-band brain rhythms, as a real-time biomarker of entrainment strength. A systematic feature ablation study revealed that 12 PAC trajectory and stimulation context features outperform the full 73-feature set by five-fold on held-out test subjects (test R² = 0.606 vs -0.025), identifying subject-specific spectral features as the primary source of cross-subject overfitting. I trained a causal Temporal Convolutional Network (TCN) on these 12 features to forecast PAC five to ten seconds ahead and integrated it into a closed-loop controller validated on all 35 subjects' EEG.

The controller matched stimulation to periods of need 72.1% of the time versus 64.5% for reactive control (p < 0.001) and targeted 82.6% of low-PAC windows versus 51.7% (p < 0.001), reaching 91% of the theoretical oracle. Every subject showed improved alignment in offline validation (p < 0.001), and the advantage held across six simulated fatigue severity levels.

These results demonstrate that a minimal feature set capturing PAC dynamics outperforms complex spectral models, offering a practical path toward personalized 40 Hz therapy that is both more accurate and more deployable.

_Word count: ~240 / 250 max_

_Category: Biological Science and Engineering, Computational Biology and Bioinformatics_
_Synopsys Championship — Santa Clara County, March 2026_
