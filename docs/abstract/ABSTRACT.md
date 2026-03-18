# Abstract

**P10: Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's**

Amaar Chughtai

---

Alzheimer's disease affects over 55 million people worldwide, and emerging research shows that 40 Hz auditory stimulation can drive gamma-frequency brain rhythms that help clear toxic amyloid-β plaques. Current protocols deliver this therapy on a fixed schedule, ignoring individual responses; some patients habituate within minutes while others maintain entrainment. This project proposes a closed-loop deep learning system to predict when a patient's brain will lose entrainment, enabling individualized stimulation timing.

I analyzed EEG recordings from 35 elderly subjects (OpenNeuro ds005048) and computed phase-amplitude coupling (PAC), the coordination between slow theta-band and fast gamma-band brain rhythms, as a real-time biomarker of entrainment strength. I engineered 73 causal features from spectral, PAC-history, and stimulation-context signals, then trained a causal Temporal Convolutional Network (TCN, 31,000 parameters) to forecast PAC five to ten seconds ahead. The TCN was integrated into a closed-loop controller and validated on all 35 subjects' EEG.

At five-to-ten-second horizons all baselines collapsed to negative R-squared while the TCN maintained R-squared of 0.25, a +0.5 margin. The controller matched stimulation to periods of need 72.1% of the time versus 64.5% for reactive control (p < 0.001) and targeted 82.6% of low-PAC windows versus 51.7% (p < 0.001), reaching 91% of the theoretical oracle. Every patient benefited (p < 0.001), and the advantage held across four fatigue model assumptions.

These results demonstrate that forecasting PAC enables personalized 40 Hz therapy that outperforms fixed and reactive protocols, a path toward more efficient treatment for Alzheimer's disease.

*Word count: ~247 / 250 max*

*Category: Biological Science and Engineering, Computational Biology and Bioinformatics*
*Synopsys Championship — Santa Clara County, March 2026*
