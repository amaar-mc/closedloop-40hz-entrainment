# <!--

# INTERNAL NOTE — NOT PART OF THE SUBMITTED EXTENDED ABSTRACT

VENUE: MIT URTC 2026 — poster + lightning-talk track (extended abstract, ~750–1000 words).
ELIGIBILITY: unconditional for a sole high-school author per the URTC FAQ — NO eligibility hold
(unlike the paper track). Submittable once the 2026 cycle portal is confirmed open.
This file contains the submission-ready extended abstract (body ~840 words) plus a lightning-talk
script and figure hooks. All numbers trace to RESULTS_CANONICAL.md (verified 2026-07-16).
Strip this comment and the "Figure hooks" / "Lightning-talk script" sections if the portal wants
only the abstract body; keep them for the poster and the 5-minute talk.
============================================================
-->

# Feature Selection Beats Model Size: Auditing a Cross-Participant PAC Forecaster for Adaptive 40 Hz Auditory Stimulation

**Amaar M. Chughtai** — Valley Christian High School, San Jose, California, USA

_Track: Technology of Computation / Technology of Humanity. Poster + lightning talk._

---

## Extended Abstract

A fixed 40 Hz auditory stimulation protocol defines the sound schedule, but not whether the listener's measured EEG response is strengthening, fading, or being swamped by artifact from one moment to the next. An adaptive protocol would need a brain-state variable it can compute _before_ each stimulation decision. I asked a narrow, testable version of that question on recorded data: can frontal theta–gamma phase–amplitude coupling (PAC), the dependence of 38–42 Hz EEG amplitude on 4–8 Hz theta phase, be forecast across participants during stimulation, and does that conclusion survive when the PAC target is made closer to what an online system could actually observe?

I used OpenNeuro dataset ds005048 (v1.0.1): EEG recorded during alternating 40 Hz auditory stimulation and rest in 35 memory-clinic participants with dementia. I selected seven frontal channels, computed PAC with the Tort modulation index as one scalar timing target per timestamp, and split participants into 24 training, 5 validation, and 6 held-out test — no participant in more than one split. Each temporal sample used 20 seconds of stored PAC history and predicted PAC five seconds ahead. A dilated causal temporal convolutional network (TCN) was the forecaster; it is causal by construction, so no future sample can enter an earlier representation.

**The main finding is about features, not architecture.** A candidate representation with 73 features (61 spectral-power features plus PAC history and stimulation context) reached only R² = −0.025 on held-out participants. Dropping the 61 spectral features and keeping only the 12 PAC-history and stimulation-context features raised held-out R² to 0.558, and across five random seeds the 12-feature model averaged R² = 0.606 (range 0.558–0.647), against 0.104 for a last-value persistence baseline and −0.332 for a shuffled-label control. No architecture change I tried moved the number that much. That echoed something I had already seen upstream: a range of static PAC estimators, from about 1,457 to roughly two million parameters, all converged near R² = 0.287, telling me the ceiling was in the data rather than the model. One explanation consistent with the ablation is that the spectral features encode participant-specific anatomy that does not transfer; the ablation supports that idea but does not prove it. A horizon sweep showed the TCN's advantage over persistence is real from 3 to 10 seconds of lead time, which is the range proactive control would need; persistence is competitive only at 1–2 seconds.

**Then I stress-tested my own result, and it got smaller.** Those PAC labels were computed over complete 20–40 second events and assigned back to shorter windows, so an early window's "current PAC" input can encode samples that occur later in the same event. To test how much of the strong number depended on that, I recomputed PAC from five-second backward-looking contexts ending at each timestamp. Unique held-out targets rose from 104 to 2,678 and adjacent target repetition fell from 96.2% to zero. In this matched, single-seed comparison, forecasting R² dropped from 0.554 to 0.212 — and no longer beat Ridge regression at 0.216. On a target closer to online availability, the nonlinear model ties a linear one. The strong headline number was contingent on the target definition, which I report rather than hide.

**The controller result is mixed, and that is the point.** I integrated the forecaster into a stimulate/rest/maintain controller and replayed its decisions offline against all 35 recorded PAC trajectories. Relative to a reactive-threshold rule, the predictive controller covered more low-PAC periods (73.8% vs 51.7%) but rested during fewer high-PAC periods (50.7% vs 77.3%), so its balanced alignment (62.2%) came in just below the reactive rule (64.5%). This is a targeting tradeoff, not a dominance result. The replay scores decisions against recorded PAC; it cannot estimate how a brain would have responded physiologically to counterfactual stimulation, and it spans all splits, so it is an integration diagnostic rather than a held-out test.

None of this validates a treatment system, and I make no clinical, disease-modifying, or deployment claim. What the project delivers is a method and an audit: a compact PAC-plus-stimulation representation that transfers across participants, and a demonstration that target construction and information availability, not model size, control whether an EEG forecaster looks successful. The concrete next steps follow directly: a streaming-compatible PAC estimator, validation across repeated participant splits, artifact-sensitivity analysis, and a controller objective calibrated to balance low-PAC coverage against unnecessary stimulation during high-PAC periods. For an undergraduate research audience, the transferable lesson is that the most useful thing I did was try to break my own best result before believing it.

---

## Figure hooks (poster panels)

- **[FIGURE 1 — the ablation, headline panel]:** Held-out test R² by feature set at the 5 s horizon: spectral-only 61 feat = −0.420; all 73 feat = −0.025; PAC-trajectory 7 feat = 0.344; PAC+stim 12 feat = 0.558. Caption: "Dropping 61 spectral features raised cross-participant R² from below zero to 0.558; feature selection, not model size, drove generalization." Source: build from RESULTS_CANONICAL Table A1 (no standalone ablation image exists yet; generate a simple bar chart).
- **[FIGURE 2 — horizon sweep]:** Held-out test R² vs prediction horizon (1/3/5/8/10 s) for the 12-feature TCN (0.725/0.607/0.577/0.370/0.669) and persistence (0.726/0.178/0.104/−0.007/−0.081). Caption: "TCN advantage lives at 3–10 s lead time; persistence collapses by 3 s. 10 s point is single-seed." Source: results/figures/horizon_sweep_pac_stim.png.
- **[FIGURE 3 — target-definition stress test]:** Event-summary vs backward-looking PAC; persistence 0.104 → −0.897, Ridge 0.260 → 0.216, TCN 0.554 → 0.212 (single-seed, n = 2,678). Caption: "Under a target closer to online availability, the TCN (0.212) ties Ridge (0.216)." Source: paper/conferences/mit_urtc_2026/figures/pac_benchmark_stress_test.png.
- **[FIGURE 4 — controller replay]:** Balanced alignment / low-PAC stim / high-PAC rest for Fixed (45.0/61.4/28.6), Reactive (64.5/51.7/77.3), TCN predictive (62.2/73.8/50.7), Oracle (100/100/100). Caption: "Predictive controller improves low-PAC coverage but reduces high-PAC sparing; alignment trails reactive — a mixed offline result." Source: regenerate from results/metrics/controller_comparison_12feat.json. **Do NOT reuse results/figures/controller_comparison.png. That is the superseded historical (73-feature) figure showing 72.1%/82.6%.**

---

## Lightning-talk script (~5 minutes, 7 slides)

**Slide 1 — Why.** My grandmother has dementia, which is how I got here. Forty-hertz auditory stimulation is being studied for Alzheimer's, but it is delivered on a fixed schedule that ignores whether the brain is actually responding at that moment. I wanted to know if you could see the response coming.

**Slide 2 — The variable.** I use frontal PAC, how much 40 Hz-band amplitude locks to theta phase, as a timing signal, forecast five seconds ahead, on EEG from 35 dementia participants (OpenNeuro ds005048), split by participant so the model is always tested on people it never saw.

**Slide 3 — The finding.** The surprise was that dropping features helped. A 73-feature spectral-heavy set scored below zero across participants (−0.025); the 12-feature PAC-plus-stimulation set scored 0.558, five-seed mean 0.606, versus 0.104 for persistence. Feature selection beat every architecture change.

**Slide 4 — Where it works.** That advantage lives at 3–10 seconds of lead time — exactly where a proactive controller would act, and exactly where persistence gives up.

**Slide 5 — Breaking my own result.** Then I checked whether it was real. My PAC labels summarized whole events, so early windows could peek at later samples. I recomputed PAC to only look backward. The strong number fell from 0.554 to 0.212 and tied Ridge regression. The model wasn't the hero — the target definition was.

**Slide 6 — The controller, honestly.** In offline replay the forecast-driven controller caught more low-PAC windows (74% vs 52%) but rested through fewer high-PAC windows (51% vs 77%), so its overall alignment was a hair _below_ a simple reactive rule. A tradeoff, not a win.

**Slide 7 — What it is.** This isn't a treatment or a clinical result. It's a method that transfers across people and an audit showing what has to be fixed — streaming PAC estimation, repeated-split validation, a calibrated controller — before anyone trusts a forecast in an adaptive stimulation loop. The best thing I did was try to break my own best result first.
