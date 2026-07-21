# Brainstorm — Ideas, Framings, Open Questions

## Core narrative options

### Framing A: "Feature selection > architecture"

The headline finding: removing 61 spectral features (which encode subject anatomy) raised test R² from −0.025 to 0.606. This is a generalizable ML lesson — spectral features are not portable across subjects. Lead with this, use the controller validation as downstream proof.

**Strength:** Novel, counterintuitive, clean lesson for ML audience.
**Weakness:** May read as "we made a mistake and fixed it" rather than "we discovered something."

### Framing B: "Proactive vs reactive neurostimulation"

Lead with the clinical gap: existing closed-loop systems are reactive. We show a proactive approach (5-10s prediction) that outperforms reactive by Hedges' g=1.31. Feature discovery is a methods subsection.

**Strength:** Clinically motivating, strong real-data validation story.
**Weakness:** Harder to differentiate from prior closed-loop BCI literature.

### Framing C: "Horizon-dependent generalization in PAC forecasting"

The horizon sweep is striking: persistence and Ridge beat TCN at 1-2s, TCN dominates at 3-10s. This + the feature ablation = a characterization of what's predictable in gamma entrainment.

**Strength:** Novel characterization contribution. Works for ML and neuroscience venues.
**Weakness:** Less immediately clinically motivating.

**Recommendation:** Combine A + B. Title leads with clinical framing, abstract foregrounds the feature discovery as the mechanism behind the clinical win.

---

## Title candidates

1. "Predictive Closed-Loop 40 Hz Gamma Entrainment via Causal Temporal Convolutional Networks: Feature Generalization Enables 5–10 Second Forecasting"
2. "Spectral Features Fail to Generalize: PAC Trajectory Enables Proactive Closed-Loop Gamma Entrainment"
3. "Beyond Reactive Neurostimulation: Causal TCN Forecasting of Phase-Amplitude Coupling for Adaptive 40 Hz Entrainment"
4. "Personalizing 40 Hz Auditory Entrainment via Predictive PAC Modeling: A Closed-Loop System for Alzheimer's Disease"

---

## Potential weaknesses reviewers will flag

1. **Offline replay, not live closed-loop** — we make decisions on real brain data but cannot observe the brain's response to those decisions. Must acknowledge prominently.
2. **Dataset size** — 35 subjects is modest. Counter: subject-level splits, all 35 benefit, held-out test subjects.
3. **PAC label granularity** — epoch-level labels on 2s windows create a ceiling (R²=0.287). Be explicit this is a data design constraint.
4. **Simulator not validated** — fatigue model is phenomenological. Separate clearly from real-data results.
5. **No comparison to prior closed-loop BCI systems** — need a related work section that addresses existing adaptive stimulation literature.

---

## Open questions to resolve before submission

- [ ] Which conference? (sets page limit, format, tone)
- [ ] Include TRIBE V2 results or leave for future work?
- [ ] Include 4ch Muse results or leave for future work?
- [ ] Feature ablation — is it a main result or a methods finding?
- [ ] Multi-seed results (0.606 ± 0.032) — include as reproducibility table?
- [ ] Threshold sweep — include in main or supplementary?

---

## Differentiators vs prior work

- First causal TCN for PAC temporal prediction (prior: LSTM, reactive threshold)
- First characterization of spectral feature generalization failure in EEG-based PAC prediction
- First demonstration of proactive (not reactive) closed-loop gamma entrainment on real EEG
- Real patient EEG (N=35) not simulated — most prior work uses simulation only
