# <!--

# INTERNAL STATUS BLOCK — NOT PART OF THE SUBMITTED MANUSCRIPT

VENUE: MIT URTC 2026 — IEEE conference PAPER track (double-column IEEEtran, up to ~5 pages).
STATUS: SUBMISSION-READY TEXT, BUT HELD. Do NOT submit until BOTH conditions are met:
(a) Mentorship specifics are documented (name / institution / role / dates, with the mentor's
consent) OR the author confirms the paper-track eligibility rule is genuinely satisfied by
his own high-school work. Informal mentorship alone may not satisfy the paper track; the
poster/lightning track is unconditionally eligible (see the companion poster deliverable).
(b) The 2026 URTC cycle is confirmed OPEN with a live submission portal (as of last check, IEEE
Boston listed URTC 2026 but detailed 2026 info was pending; the live site still exposed 2025
language).
This file is a finished manuscript the author may submit ONCE (a) and (b) hold. It does not imply
the paper has been, or should be, submitted in its current held state.
Every number in this manuscript traces to RESULTS_CANONICAL.md (verified 2026-07-16). Figures are
hooked to real result files; see the [FIGURE n: ...] blocks. One figure (controller replay) has NO
current-generation source image and must be regenerated from JSON — see the margin note in §V.
============================================================
-->

# Feature Selection, Not Model Size, Governs Cross-Participant PAC Forecasting During 40 Hz Auditory Stimulation

**Amaar M. Chughtai**

_Valley Christian High School, San Jose, California, USA_

_Correspondence: amaardevx@gmail.com_

---

## Abstract

Adaptive 40 Hz auditory stimulation would need a brain-state variable that can be computed before each stimulation decision, not after it. I test whether frontal theta–gamma phase–amplitude coupling (PAC) can serve as that variable, forecast from its own recent history while stimulation is running. Using EEG from 35 participants with dementia (OpenNeuro ds005048), split by participant into 24 training, 5 validation, and 6 held-out test, I find that feature selection, not model size, drives cross-participant generalization: a 12-feature representation built from PAC history and recorded stimulation timing reaches held-out test R² = 0.558, while a 73-feature set that adds 61 spectral features falls to −0.025. Across five random seeds the 12-feature forecaster averages R² = 0.606 (range 0.558–0.647) against 0.104 for a persistence baseline. I then stress-test the result. Because the PAC labels are complete-event summaries assigned back to short windows, I recompute PAC from backward-looking contexts closer to online availability; in a matched single-seed comparison, forecasting R² drops from 0.554 to 0.212 and no longer beats Ridge regression (0.216). In retrospective replay across all 35 recorded trajectories, the forecast-driven controller covers more low-PAC periods than a reactive rule (73.8% vs 51.7%) but spares fewer high-PAC periods (50.7% vs 77.3%), so its balanced alignment (62.2%) trails reactive thresholding (64.5%). The contribution is a method and an audit, not a therapy.

**Index Terms** — auditory stimulation, closed-loop neuromodulation, cross-subject generalization, electroencephalography, phase–amplitude coupling, target-definition audit, temporal convolutional network.

---

## I. Introduction

My grandmother has dementia. That is why I started reading about 40 Hz stimulation, and it is the reason I kept going when the results turned out to be more complicated than I first hoped. I want to be plain about what this paper is and is not: it is an engineering study on recorded EEG, and it makes no claim about treating anyone.

Forty-hertz auditory stimulation is studied in Alzheimer's disease because gamma-band activity and network synchrony are altered in the disease. In transgenic mice, driving gamma at 40 Hz reduced amyloid load and changed microglial response [1]. Human evidence is younger and more cautious: an open-label extension study reported that participants with mild Alzheimer's dementia who received sustained 40 Hz multisensory stimulation retained EEG entrainment and showed less atrophy than matched controls [2]. The EEG I use here comes from a memory-clinic study that recorded brain activity during alternating 40 Hz auditory stimulation and rest, and reported increased 40 Hz frontoparietal synchronization during stimulation [3]. None of this shows that changing _when_ stimulation is delivered would help a patient. It does make the recordings useful for a narrower question.

That question is a timing question. A fixed protocol — for example, 40 seconds on and 20 seconds off, repeated for an hour — defines what sound is delivered. It says nothing about whether the person's measured EEG response is strengthening, fading, or being swamped by artifact at any given moment. A closed-loop system would instead compute a decision variable from recent measurements, apply a rule, and act [4]. The hard part is the lead time. A reactive rule waits until a measured feature has already crossed a threshold. A forecaster could, in principle, act _before_ a future low-coupling state — but only if the feature it needs is available at decision time, if it generalizes to people it was never trained on, and if it does not simply stimulate almost all the time and call the coverage a win.

I use frontal PAC as the decision variable. PAC measures whether the amplitude of a faster rhythm changes systematically with the phase of a slower one. Here the slow component is 4–8 Hz theta phase and the fast component is the 38–42 Hz amplitude envelope around the stimulation frequency. A higher modulation index means the 40 Hz-band amplitude concentrates in particular theta-phase bins; a lower value means it spreads out. I treat PAC as a compact, participant-normalized _timing_ variable to test, not as proof of therapeutic engagement or source-level gamma entrainment.

This paper contributes three linked analyses and one honest negative turn. First, I build a participant-disjoint temporal benchmark and show that a compact 12-feature representation forecasts held-out PAC far better than a 73-feature spectral-heavy set — the improvement comes from dropping features, not from adding model capacity. Second, I characterize where that advantage lives across prediction horizons, because a forecaster is only useful where it beats persistence at operationally relevant lead times. Third, I audit the target definition itself: when I recompute PAC to be closer to what an online system could actually observe, the nonlinear advantage collapses to Ridge-regression level. Finally, I replay the forecast-driven controller against all 35 recorded trajectories and report a mixed result — better low-PAC coverage, worse high-PAC sparing — plainly, because that tradeoff is the finding, not a blemish on it.

## II. Related Work

**Gamma entrainment and PAC in dementia.** The 40 Hz entrainment literature grows from animal work showing that driving gamma reduces amyloid pathology [1] and from multisensory extensions of that result [5]. Theta–gamma PAC is used as a biomarker of coordinated multi-frequency dynamics; the modulation index I use was introduced by Tort et al. [6] and quantifies how gamma amplitude is distributed across theta phase. Human translation remains early and is reported cautiously [2], [3]. A recurring motivation for adaptive delivery is that responses vary between people: prior reviews report substantial non-responder rates to gamma entrainment, which a fixed protocol cannot detect or accommodate [7]. <!-- [AUTHOR: verify non-responder source — the specific "~30% / 23 of 33" statistic may originate in a primary study, not in the Sahu & Tseng review; either locate the primary source or keep this softened wording without a numeric rate.] --> Within a single session, responses also drift as repeated identical stimulation produces habituation [8], which is one reason a state-aware controller is worth studying.

**Closed-loop neuromodulation.** Closing the loop between a measured brain signal and a stimulation decision is an active area, with the general requirement that the decision variable be computable from recent data and that the controller be validated before clinical use [4]. My work sits upstream of that: it asks whether a usable decision variable can be _forecast_ at all, on recorded data, before anyone builds a live loop.

**Deep learning for EEG.** Compact convolutional networks such as EEGNet [9] are standard for EEG regression and classification because they fit small datasets without overfitting. For sequence forecasting I use a dilated causal temporal convolutional network (TCN) [10], which respects temporal order by construction: with left-only padding, no later sample can influence an earlier representation. That causal guarantee is an architectural property, not just a training convention, which is why I chose it for a forecasting task where leakage would be easy to introduce by accident.

## III. Dataset and Methods

### A. Source EEG and signal conditioning

I use OpenNeuro ds005048 (v1.0.1), which records EEG during alternating 40 Hz auditory stimulation and rest in a memory-clinic cohort [3], [11]. The local BIDS release contains 35 participants with dementia. Recordings have 19 monopolar channels at 250 Hz. The dataset does not contain adaptive stimulation decisions, so every controller result below is a replay over recorded trajectories, not evidence about counterfactual physiology.

I selected seven frontal channels: Fp1, Fp2, F7, F3, Fz, F4, F8. The dataset providers had already preprocessed the recordings (1 Hz high-pass, 50 Hz line-noise removal, artifact-subspace reconstruction, ICA-based component rejection, average reference) [3]; released sidecar files independently report the 1 Hz high-pass, 50 Hz notch, and average reference. My local stage adds only light conditioning: a 0.5–80 Hz zero-phase band-pass, a 50 Hz zero-phase notch, absolute-amplitude masking above 100 µV (masked samples set to zero before rereferencing), and common-average rereferencing. This is not a validated artifact-removal pipeline for physiological PAC, and I do not present it as one — frontal gamma-band EEG is especially vulnerable to ocular and facial-muscle activity [12]. Each event period was segmented into 2-second windows with a 1-second hop, giving windows of shape (7 channels × 500 samples).

### B. PAC label construction

Theta–gamma PAC was computed with the Tort modulation index [6]: theta phase from 4–8 Hz, gamma amplitude from 38–42 Hz, and the gamma-amplitude distribution summarized over 18 theta-phase bins, then measured as the normalized divergence from uniform. Values were averaged across the seven channels to give one scalar frontal target per timestamp. I applied no surrogate correction or phase-clustering debiasing, so these values are retrospective EEG-derived targets, not definitive evidence of endogenous theta–gamma coupling [13].

PAC was computed over complete event periods rather than individual 2-second windows, because a 2-second window holds too few theta cycles for stable phase binning. Most events lasted 20 or 40 seconds. Each window then inherited the PAC value of its containing period. This stabilizes the label, but it has three consequences I return to repeatedly: labels repeat within a period, adjacent samples are not independent, and a value assigned to an early window summarizes EEG samples that occur _later_ in the same period. The forecasting results are therefore retrospective by construction; the online-availability limit is not a footnote but a first-class threat, audited in §IV-D.

### C. Temporally ordered forecasting dataset and features

Each temporal sample used a 20-step lookback and a target 5 steps ahead. With a 1-second hop, that is 20 seconds of stored history and a target 5 seconds after the sequence end. Sequences were built within each participant so none crossed a participant boundary, and no PAC-series entry at or after the target index was ever used as an input.

The candidate representation had 73 features per step: 61 spectral-power features; 7 PAC-history features (current PAC; trailing means over 2, 4, 8, and 16 steps; differences over 1 and 4 steps); and 5 stimulation-context features (on/off state; normalized time since the last switch; recent stimulation fraction; and sine/cosine protocol-phase terms). The 12-feature representation keeps only the PAC-history and stimulation-context features and drops all 61 spectral features. Because I chose the representation using this benchmark, I treat the ablation as exploratory and report it as such.

Data were split by participant into 24 training, 5 validation, and 6 test participants, giving 11,160 / 2,605 / 2,678 temporal sequences. Normalization statistics were fit on the training split only and reused everywhere else.

### D. Models and baselines

Current PAC can be estimated from a single raw-EEG window with EEGNet [9], a compact CNN of 1,457 parameters; that static estimator tops out at held-out test R² = 0.287, a ceiling I discuss in §IV-A. The forecaster is a dilated causal TCN: an input projection, four residual depthwise-separable temporal blocks (kernel size 3, dilations 1/2/4/8, LayerNorm, dropout 0.2), attention pooling over the 20-step sequence, and linear heads for future PAC and PAC change. Left-only padding keeps the network causal.

Two model instances appear in this paper, and I keep them separate on purpose. The feature-selection and five-seed forecasting experiments (§IV-A, §IV-B) use a compact experimental TCN of about 22,914 parameters. The target-definition stress test (§IV-D) and the deployed controller (§V) use the integrated architecture of 27,139 trainable parameters (hidden width 64), verified by summing the saved checkpoint's tensor shapes. These come from distinct training runs, so I never pool their metrics into a single "checkpoint performance" number. Training used Huber loss, AdamW, learning-rate reduction on plateau, early stopping, and deterministic seeding.

Every forecasting number is reported next to two baselines: **persistence** (predict the last observed value) and **Ridge regression** on the same features. Persistence is the honest bar to clear, because it is strong at short horizons; the TCN is only interesting where it beats persistence and Ridge at lead times a controller could act on.

## IV. Experiments

### A. Feature selection, not model size, drives generalization

Table I reports a single-seed ablation on the fixed participant split at the 5-second horizon. The pattern is the main scientific result of this work: adding the spectral feature set _hurt_ cross-participant generalization, and the compact PAC-plus-stimulation representation was strongest.

**TABLE I. Single-seed feature ablation (held-out test R², 5 s horizon)**

| Input representation                 | # features |   Test R² |
| ------------------------------------ | ---------: | --------: |
| Spectral only                        |         61 |    −0.420 |
| All candidate features               |         73 |    −0.025 |
| PAC trajectory only                  |          7 |     0.344 |
| PAC trajectory + stimulation context |         12 | **0.558** |

Dropping the 61 spectral features raised held-out R² from below zero to 0.558. No architecture change I tried moved the number that much. I want to state the interpretation carefully, because it is easy to overclaim: the ablation shows that the larger spectral representation carries variation that does not transfer to unseen participants. One explanation _consistent with_ this is that spectral features encode participant-specific anatomy rather than the dynamics that generalize. The ablation supports that idea; it does not prove it, and I do not present it as proven.

This connects to a separate observation about the static estimator. Across a range of architectures from about 1,457 to roughly two million parameters, held-out current-PAC estimation converged near R² = 0.287. When that many models land on the same number, the ceiling is in the data — the noisy, event-level PAC labels and the seven-channel frontal montage — not in the model. That is what pushed me away from building a bigger network and toward asking which _features_ transfer.

### B. The advantage lives at 3–10 s lead time

A forecaster that only matches persistence at 1 second is useless for proactive control. Fig. 1 sweeps the prediction horizon for the 12-feature TCN against persistence. At 1 second the two are tied (0.725 vs 0.726). By 3 seconds persistence has collapsed to 0.178 while the TCN holds 0.607, and the gap stays open through 10 seconds. Across five seeds at the 5-second horizon, the 12-feature TCN averaged R² = 0.606 (range 0.558–0.647); persistence was 0.104. A shuffled-label control gave R² = −0.332, so the signal is real rather than an artifact of the fit.

[FIGURE 1: Prediction-horizon sweep. Held-out test R² for the 12-feature PAC+stimulation TCN versus a last-value persistence baseline at horizons of 1, 3, 5, 8, and 10 s. Persistence is competitive only at 1–2 s and turns negative by 8 s; the TCN's advantage occupies the 3–10 s band that proactive control needs. The 10 s point is single-seed and should be replicated before it is treated as stable. A 4-channel consumer-montage variant is shown for context. — source results/figures/horizon_sweep_pac_stim.png]

### C. Five-seed stability

The five-seed spread (0.558–0.647, mean 0.606) estimates initialization variability on one fixed split. It does not estimate sensitivity to _which_ participants are held out; that would require repeated participant-level resampling, which I flag as necessary future work. I report the mean and range rather than a single standard deviation to avoid an unstated convention (population SD 0.029, sample SD 0.033 on these five values).

### D. The target definition controls the conclusion

Here is where the strong-looking number has to survive contact with a harder question. The event-summary labels of §III-B assign one PAC value to a whole 20–40 s period, so an early window's "current PAC" input can encode samples that have not happened yet at decision time. To test how much of the result rests on that, I rebuilt the benchmark with a leakage-free target: at each timestamp I recomputed PAC from a 5-second backward-looking context ending at that timestamp, using the same lookback, horizon, 12 features, participant splits, and train-only normalization. For contexts shorter than three seconds at segment boundaries, PAC used 9 rather than 18 phase bins.

The change is dramatic (Fig. 2). Unique held-out targets rose from 104 to 2,678, and adjacent target repetition fell from 96.2% to zero. Persistence R² fell from 0.104 to −0.897, confirming that the event-summary target had a repeated-value shortcut. Under the leakage-free target, the same 27,139-parameter architecture dropped from R² = 0.554 to 0.212 — and it no longer beat Ridge regression, which was 0.216. On this target the TCN and Ridge are tied. The matched before/after comparison is 0.554 → 0.212 for the TCN; I do not compare it to the five-seed 0.606, which comes from the separate experimental model and the event-summary target.

[FIGURE 2: Target-definition stress test. (A) Event-summary PAC is assigned to each 2 s window, so early inputs include later samples — retrospective only. (B) Backward-looking PAC uses a 5 s context ending at forecast time t, so no sample after t enters the PAC context. Bars: single-seed fixed-split held-out test R² (n = 2,678) for persistence, Ridge, and TCN under each target. Under the backward-looking target the TCN (0.212) ties Ridge (0.216); no confidence intervals are shown. — source paper/conferences/mit_urtc_2026/figures/pac_benchmark_stress_test.png]

The reading I take from this is not that the forecaster failed. It is that the target definition, not the model class, was carrying the strong event-summary result — so target construction should be benchmarked before model complexity is added.

### E. Leakage and validity checks

I audited the stored temporal dataset for the three failure modes that would quietly inflate these numbers. No participant appeared in more than one split. Every target index was exactly five steps after its sequence end. Training statistics recomputed from the split matched the stored normalizers. The shuffled-label control (R² = −0.332) rules out a fit-to-noise explanation. What these checks cannot fix is the label-resolution caveat itself: the event-summary inputs are not yet a validated online feature, which is precisely why §IV-D exists.

## V. Retrospective Controller Replay

<!-- MARGIN NOTE FOR AUTHOR — FIGURE INTEGRITY:
The existing image results/figures/controller_comparison.png is the SUPERSEDED Gen-C figure. It shows
the HISTORICAL 73-feature model (alignment 72.1%, low-PAC 82.6%, Hedges' g = 1.31 / 4.47, plus "PI" and
"Hybrid" strategies) and MUST NOT be used to illustrate the current 12-feature checkpoint. Regenerate a
new bar chart from results/metrics/controller_comparison_12feat.json (the four strategies and exact
values in Table II) before adding any figure to this section. -->

I integrated the 12-feature checkpoint (27,139 parameters) into a controller with stimulate / rest / maintain states, a rolling PAC baseline, z-score thresholds, and a three-step minimum hold before switching. I then replayed its decisions offline against all 35 recorded PAC trajectories, spanning the training, validation, and test splits. This is a full-cohort integration diagnostic, not an additional held-out forecasting test, and it is a replay against recorded PAC — it cannot estimate how a brain would have physiologically responded to counterfactual decisions.

I compared four strategies. **Fixed schedule** replays the nominal recorded protocol. **Reactive threshold** stimulates, after a warm-up, when current PAC is more than 0.5 SD below its 30-sample rolling baseline. **TCN predictive** stimulates or rests when the normalized forecast PAC change crosses ±0.3, with a current-PAC fallback. **Alignment oracle** stimulates below each participant's full-trajectory median PAC — it uses the entire recorded trajectory and is neither causal nor deployable; it is an upper bound only. I define balanced alignment as the mean of the low-PAC stimulation rate (fraction of below-median PAC points assigned stimulation) and the high-PAC rest rate (fraction of above-median points assigned rest).

**TABLE II. Retrospective controller replay on 35 recorded trajectories**

| Strategy                 | Bal. align. | Low-PAC stim | High-PAC rest | PAC gap (×10⁻⁶) |
| ------------------------ | ----------: | -----------: | ------------: | --------------: |
| Fixed schedule           |       45.0% |        61.4% |         28.6% |           −6.55 |
| Reactive threshold       |   **64.5%** |        51.7% |     **77.3%** |           21.09 |
| TCN predictive (12-feat) |       62.2% |    **73.8%** |         50.7% |           21.02 |
| Alignment oracle         |        100% |         100% |          100% |           33.36 |

The honest reading is a tradeoff, not a win. The predictive controller covered 22.1 percentage points more low-PAC periods than the reactive rule (73.8% vs 51.7%), but its high-PAC rest rate fell by 26.6 points (50.7% vs 77.3%). The net effect is that its balanced alignment (62.2%) is _below_ reactive thresholding (64.5%). The PAC gap — mean PAC during rest minus mean PAC during stimulation, positive when stimulation concentrates in lower-PAC periods — was essentially identical for the two (21.02 vs 21.09 ×10⁻⁶), about 63% of the oracle's gap, despite very different action profiles. So the forecaster found more of the periods a low-PAC-seeking controller is designed to catch, but it did so by stimulating too often during periods it should have left alone. That is the next thing to fix, and naming it precisely is more useful than hiding it.

## VI. Limitations

I state these plainly because several of them are the point of the paper.

1. **Retrospective replay is not clinical validation.** The controller decides on real brain data but never observes the physiological response to its decisions. No patient outcome, disease-progression, or deployment claim is made or supported.
2. **The controller result is mixed.** Balanced alignment (62.2%) is below reactive thresholding (64.5%); the TCN trades better low-PAC sensitivity for worse high-PAC specificity. Any framing that implies dominance over all baselines would be false for this checkpoint.
3. **Full-cohort replay is not held-out generalization.** The 35-trajectory replay spans all splits; the held-out forecasting evidence is the five-seed R² on the subject-level split, not the replay table.
4. **Primary PAC inputs are complete-event summaries.** They are not validated as streaming-available features, and the leakage-free target reduces forecasting R² to Ridge level (0.212 vs 0.216). The strong event-summary result depends partly on the target definition.
5. **The backward-looking stress test is still not a production estimator.** It uses zero-phase filtering inside bounded contexts, and 5-second contexts give limited theta-cycle support. It is an information-boundary probe, not a deployable streaming PAC estimator.
6. **The 38–42 Hz band overlaps the stimulation frequency.** PAC estimates may reflect stimulation-locked steady-state response or residual artifact rather than endogenous gamma coupling [12], [13].
7. **Small, single-site cohort, single split.** n = 35 from one dataset, seven frontal channels, one fixed participant split; single-seed points (including the 10 s horizon and the ablation) are provisional until replicated.

Because of these, the responsible next steps are concrete: implement a streaming-compatible PAC estimator, evaluate additional backward-looking context lengths, measure performance across repeated participant splits, calibrate the controller objective for both low-PAC coverage and high-PAC sparing on held-out participants, feed counterfactual actions back into the stimulation-context features during simulation, and only then consider a prospective streaming test.

## VII. Conclusion

On an event-summary benchmark, a 12-feature TCN forecast held-out PAC better than a 73-feature spectral-heavy set, and the gain came from dropping features rather than adding capacity. Across five seeds it reached mean R² = 0.606; its advantage over persistence held from 3 to 10 seconds, the lead time proactive control needs. That five-seed result belongs to the event-summary target. In a separate matched single-seed test, moving the integrated architecture to a leakage-free target dropped its score from R² = 0.554 to 0.212, level with Ridge (0.216), so the nonlinear advantage was specific to how the target was defined. Offline replay then showed a low-PAC-coverage versus high-PAC-sparing tradeoff that leaves the controller's alignment below a simple reactive rule. The compact representation is a genuine, transferable finding; the strong headline number is contingent on how the target is defined. A streaming PAC estimator, repeated-split validation, artifact-sensitivity analysis, and a separately calibrated controller are prerequisites before any live adaptive-stimulation test — and stating that boundary clearly is part of the result.

## Acknowledgment

This project was conducted independently by the author. Statistical test selection was discussed with an AP Statistics instructor. [AUTHOR TO CONFIRM: whether to acknowledge informal mentorship, and if so the mentor's name, role, and institution, with their permission — do not name a mentor or institution until documented.] EEG data are from the open-access OpenNeuro dataset ds005048 (v1.0.1) and were used under its open-access license; all analysis code is the author's own. The author used AI tools as an assistive resource for software engineering and for drafting this text; the study design, analysis, interpretation, and final decisions are the author's own (see the accompanying AI-use disclosure).

## References

[1] H. F. Iaccarino, A. C. Singer, A. J. Martorell, _et al._, "Gamma frequency entrainment attenuates amyloid load and modifies microglia," _Nature_, vol. 540, no. 7632, pp. 230–235, 2016, doi: 10.1038/nature20587.

[2] D. Chan, H. J. Suk, B. L. Jackson, _et al._, "Gamma sensory stimulation in mild Alzheimer's dementia: An open-label extension study," _Alzheimer's & Dementia_, vol. 21, no. 10, art. e70792, 2025, doi: 10.1002/alz.70792.

[3] M. Lahijanian, H. Aghajan, and Z. Vahabi, "Auditory gamma-band entrainment enhances default mode network connectivity in dementia patients," _Scientific Reports_, vol. 14, art. 13153, 2024, doi: 10.1038/s41598-024-63727-z.

[4] G. Soleimani, M. A. Nitsche, T. O. Bergmann, _et al._, "Closing the loop between brain and electrical stimulation: towards precision neuromodulation treatments," _Translational Psychiatry_, vol. 13, art. 279, 2023, doi: 10.1038/s41398-023-02565-5.

[5] A. J. Martorell, A. L. Paulson, H. J. Suk, _et al._, "Multi-sensory gamma stimulation ameliorates Alzheimer's-associated pathology and improves cognition," _Cell_, vol. 177, no. 2, pp. 256–271, 2019, doi: 10.1016/j.cell.2019.02.014.

[6] A. B. L. Tort, R. Komorowski, H. Eichenbaum, and N. Kopell, "Measuring phase–amplitude coupling between neuronal oscillations of different frequencies," _Journal of Neurophysiology_, vol. 104, no. 2, pp. 1195–1210, 2010, doi: 10.1152/jn.00106.2010.

[7] P. P. Sahu and P. Tseng, "Gamma sensory entrainment for cognitive improvement in neurodegenerative diseases: opportunities and challenges ahead," _Frontiers in Integrative Neuroscience_, vol. 17, art. 1146687, 2023, doi: 10.3389/fnint.2023.1146687.

[8] R. F. Thompson and W. A. Spencer, "Habituation: A model phenomenon for the study of neuronal substrates of behavior," _Psychological Review_, vol. 73, no. 1, pp. 16–43, 1966, doi: 10.1037/h0022681.

[9] V. J. Lawhern, A. J. Solon, N. R. Waytowich, _et al._, "EEGNet: a compact convolutional neural network for EEG-based brain–computer interfaces," _Journal of Neural Engineering_, vol. 15, no. 5, art. 056013, 2018, doi: 10.1088/1741-2552/aace8c.

[10] S. Bai, J. Z. Kolter, and V. Koltun, "An empirical evaluation of generic convolutional and recurrent networks for sequence modeling," _arXiv:1803.01271_, 2018.

[11] M. Lahijanian, H. Aghajan, and Z. Vahabi, "40Hz Auditory Entrainment," OpenNeuro dataset ds005048, ver. 1.0.1, doi: 10.18112/openneuro.ds005048.v1.0.1.

[12] J. F. Hipp and M. Siegel, "Dissociating neuronal gamma-band activity from cranial and ocular muscle activity in EEG," _Frontiers in Human Neuroscience_, vol. 7, art. 338, 2013, doi: 10.3389/fnhum.2013.00338.

[13] J. Aru, J. Aru, V. Priesemann, _et al._, "Untangling cross-frequency coupling in neuroscience," _Current Opinion in Neurobiology_, vol. 31, pp. 51–61, 2015, doi: 10.1016/j.conb.2014.08.002.
