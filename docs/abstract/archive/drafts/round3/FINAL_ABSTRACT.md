# FINAL ABSTRACT (Round 3)

**Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease**

Amaar Chughtai

---

Sound pulses at 40 Hz synchronize brain gamma oscillations and activate immune cells that clear amyloid plaques—a hallmark of Alzheimer's disease. But clinical protocols use rigid fixed schedules that ignore individual brain responses. Half of patients habituate within minutes; the other half maintain strong neural coupling. A one-size-fits-all approach serves neither group. This project asks: can we predict when a patient's brain will lose entrainment, and intervene before it happens?

I analyzed EEG from 35 dementia patients (OpenNeuro ds005048), computing phase-amplitude coupling (PAC) between theta and gamma rhythms as an entrainment biomarker. I trained a causal Temporal Convolutional Network (31,000 parameters, dilations [1,2,4,8]) to forecast PAC 5-10 seconds ahead. This horizon is critical: at 1-2 seconds, simple baselines suffice; at 5-10 seconds—where a controller must act—all baselines collapse to negative R-squared while the TCN maintains R-squared of 0.25, a +0.5 margin.

Validated on all 35 subjects' real EEG, the predictive controller achieved 72.1% alignment versus 64.5% reactive (Hedges' g = 1.31, p < 0.001). It directed stimulation to 82.6% of low-PAC windows versus 51.7% (g = 4.47, p < 0.001), reaching 91% of the theoretical oracle. Every patient benefited (binomial p < 0.001). Adaptive efficiency gains of +9-11% held across six fatigue levels and four different habituation model assumptions (all p < 10^-13), demonstrating robust personalized control.

---

_Word count: 240 / 250 max_
_Category: Biological Science and Engineering, Computational Biology and Bioinformatics_
_Synopsys Championship — Santa Clara County, March 2026_

## Why This Is the Final Version

**Structure analysis:**

1. **Hook (2 sentences):** Opens with the striking biological mechanism — 40 Hz sound activates immune cells to clear plaques. Immediately establishes clinical significance.
2. **Problem (2 sentences):** Fixed schedules ignore individual responses. The habituation split (50/50) is a concrete, memorable detail.
3. **Research question (1 sentence):** Direct, clear, and compelling.
4. **Methods (2 sentences):** Concise technical description — PAC biomarker, TCN architecture, specific parameters.
5. **Central finding (2 sentences):** The horizon sweep is the intellectual heart — explains _why_ the TCN matters at the specific horizons that matter.
6. **Validation results (3 sentences):** Real-data validation, specific effect sizes and p-values, oracle comparison, universal benefit.
7. **Robustness (1 sentence):** Four fatigue models, six severity levels — addresses the "is this just one simulation?" concern.

**Strengths over earlier drafts:**

- Opens with biology (accessible), not statistics (intimidating)
- "Sound pulses at 40 Hz" is concrete and evocative
- "One-size-fits-all approach serves neither group" — clear problem motivation
- Horizon sweep explanation is the key intellectual contribution — clearly stated
- Numbers are specific but not overwhelming (6 key statistics)
- "Every patient benefited" is the most powerful sentence (100% consistency)
- Ends with robustness — the last thing the judge reads is confidence in results
