# SCCUR 2026 — Submission-Ready Abstract

**Author:** Amaar Chughtai, Valley Christian High School, [AUTHOR TO CONFIRM: city, state]
**Faculty advisor:** [AUTHOR TO CONFIRM — SCCUR requires a named faculty advisor who reviews the abstract; see MANUSCRIPT_SELF_CHECK. Submission is gated on this.]

---

## Title (79 / 200 characters)

Stress-Testing an EEG Forecasting Model for Adaptive 40 Hz Auditory Stimulation

## Abstract (1,467 / 1,500 characters; no citations, per SCCUR rules)

Adaptive stimulation needs a brain-state feature it can estimate before each control decision. I tested whether a frontal-EEG phase-amplitude-coupling (PAC) feature could be forecast across participants during 40 Hz auditory stimulation, and whether that held once the target was made closer to online use.

I analyzed OpenNeuro ds005048, a public EEG dataset of 35 memory-clinic participants. From 7 frontal channels I computed PAC, the dependence of 38-42 Hz gamma amplitude on 4-8 Hz theta phase. Participants were split by subject into 24 training, 5 validation, and 6 held-out test, so no participant crossed splits. A 12-feature causal temporal convolutional network (TCN) used PAC history and stimulation context to predict PAC five seconds ahead, against persistence and Ridge baselines.

On an initial event-summary target the TCN reached held-out R2 = 0.554, above Ridge (0.260) and persistence (0.104). But these labels assigned one whole-event PAC value back to every window: only 104 unique test targets, 96.2 percent identical to their neighbor. I recomputed PAC from five-second backward-looking windows, raising unique targets to 2,678 and removing the repetition. On this stricter target the same model scored R2 = 0.212, matching Ridge (0.216) and no longer beating it.

In this fixed-split stress test, target definition decided the model-selection conclusion. The audit shows what must be validated before EEG forecasts drive adaptive stimulation.

---

## Presentation notes (not part of the submitted abstract)

- **Format:** poster preferred. A poster invites methodological discussion of the stress test on the author's terms; an oral slot invites harder live scrutiny of the single-fixed-split design, which is a real limitation.
- **The one-line story if asked:** "My model looked strong until I fixed how the target was defined — then it only tied a linear baseline. That's the result."
- **Honest framing to hold to in Q&A:** the numbers are single fixed-split; the controller replay (not in this abstract) is a mixed offline result, not a win; nothing here is clinical.
