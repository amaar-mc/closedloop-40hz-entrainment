<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 MIT URTC 2026 (paper) · priority #9
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** manuscript · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G8 · 89% to submission · **eligibility:** conditional · label: `conditional-eligibility`  
> **Deadline:** no date posted  
> ⚑ **Integrity:** no-fabricated-affiliation  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# Auditing PAC Forecast Targets During 40 Hz Auditory Stimulation

**Author:** Amaar M. Chughtai  
**Affiliation:** Valley Christian High School, San Jose, California, United States  
**Contact:** amaardevx@gmail.com

## Abstract

Fixed 40 Hz auditory stimulation protocols can be evaluated from the delivered sound schedule, but
an adaptive protocol would need an EEG quantity that is available before each decision. This
retrospective study tests whether frontal phase-amplitude coupling (PAC), the dependence of
`38-42 Hz` EEG amplitude on the phase of `4-8 Hz` theta activity, can serve as a forecast target
during 40 Hz auditory stimulation. Using 35 OpenNeuro `ds005048` participants, seven frontal
channels were split by participant into 24 training, 5 validation, and 6 held-out test participants.
With PAC computed over complete stimulation/rest events and assigned to constituent two-second
windows, a 12-feature temporal convolutional network (TCN) using PAC history and recorded
stimulation timing reached held-out R-squared of 0.558, compared with -0.025 for a 73-feature
candidate set and 0.606 mean R-squared across five seeds versus 0.104 for persistence. The central
audit asked whether this result survived a target definition closer to online availability.
Recomputing PAC from five-second backward-looking signal contexts increased unique held-out targets
from 104 to 2,678, eliminated adjacent target repetition, and reduced TCN R-squared from 0.554 to
0.212, slightly below Ridge regression at 0.216. Offline replay then showed that forecast-driven
decisions stimulated more below-median PAC periods but spared fewer above-median PAC periods than a
reactive rule. These results make the next step specific: adaptive 40 Hz stimulation needs a
streaming PAC estimator and controller calibration before any physiological or therapeutic claim is
warranted.

**Keywords:** auditory stimulation, phase-amplitude coupling, EEG, temporal convolutional network,
target-definition audit, retrospective replay

## I. Introduction

Forty-hertz auditory stimulation is being studied because gamma-band activity and network synchrony
are altered in Alzheimer’s disease models and dementia cohorts. In 5XFAD mice, experimentally
induced 40 Hz activity reduced amyloid burden and altered microglial response [1]. The human dataset
used here comes from Lahijanian et al., who recorded EEG during alternating 40 Hz auditory
stimulation and rest in memory-clinic participants. Their analysis measured power at the stimulation
frequency and phase-locking-value connectivity across frontal and parietal sites; they reported a
40 Hz stimulus-period power peak and increased 40 Hz frontoparietal synchronization during
stimulation [2]. That prior work makes the recordings useful for a narrower engineering question:
can an EEG-derived state variable be estimated early enough to inform future stimulation timing? It
does not show that changing stimulation timing would improve physiology or symptoms.

A fixed auditory protocol defines what sound is delivered, not whether the participant's measured
EEG response is strengthening, fading, or being dominated by artifact. Fixed schedules are therefore
reproducible but blind to within-session state. Closed-loop neuromodulation instead requires a
decision variable computed from recent measurements, a rule for when to stimulate or rest, and
evidence that the variable can be estimated or forecast before the next decision [4].

This study uses frontal phase-amplitude coupling as that decision variable. PAC measures whether the
amplitude of a faster oscillatory component changes systematically with the phase of a slower
component. Here, the slower component is `4-8 Hz` theta phase and the faster component is the
`38-42 Hz` amplitude envelope surrounding the 40 Hz stimulation frequency. A higher modulation index
means that 40 Hz-band amplitude is concentrated in particular theta-phase bins; a lower value means
the amplitude is distributed more evenly across the theta cycle. This is not treated as proof of
therapeutic engagement, source-level gamma entrainment, or disease state. It is a compact frontal EEG
timing variable that can be tested as a target for future adaptive control.

The low-PAC replay target follows from the controller question rather than from a clinical claim. If
a controller is designed to deliver stimulation when the chosen EEG feature is low relative to that
participant's recent or full-session distribution, then below-median PAC gives a concrete,
participant-normalized timing objective. The analysis therefore asks whether a model can identify
and forecast low-coupling periods better than fixed or reactive rules. It does not assume that low
PAC marks therapeutic need, and it does not test whether stimulation raises PAC.

Forecasting is useful only if it changes the decision before a reactive threshold would. A reactive
rule waits until the measured feature has already crossed a threshold. A forecaster could, in
principle, initiate or withhold stimulation before a future low-PAC state. That claim has three
requirements: the input features must be available at decision time, performance must generalize to
participants excluded from training, and the controller must not gain low-PAC coverage by simply
stimulating almost all the time. Those requirements motivated the target-availability audit and the
offline replay metrics used here.

This study therefore contributes three linked analyses. First, it builds a participant-disjoint
temporal benchmark using seven frontal EEG channels from 35 participants and tests whether compact
PAC-history plus recorded-stimulation features predict stored PAC values five seconds ahead. Second,
it audits the target definition by recomputing PAC from five-second backward-looking signal contexts
instead of complete stimulation/rest events. This matters because complete-event PAC is stable but
assigns the same summary value to early windows before all contributing EEG samples have occurred.
Third, it uses offline replay to test whether forecasts improve decision alignment relative to fixed
and reactive rules. The resulting conclusion is intentionally bounded: compact temporal features
predict stored event-summary PAC, but the nonlinear advantage weakens under a target definition
closer to online availability, and replay exposes a low-PAC coverage versus high-PAC sparing tradeoff
that must be calibrated before live testing.

## II. Data and Methods

### A. Source EEG Dataset and Signal Conditioning

OpenNeuro `ds005048` version `1.0.1` was selected because it contains the ingredients needed to ask
a closed-loop timing question retrospectively: repeated 40 Hz auditory stimulation and rest blocks,
event annotations, participant-level clinical labels, and continuous EEG from a memory-clinic cohort
[3]. The dataset does not contain adaptive stimulation decisions, so every controller result below
is a replay over recorded trajectories rather than evidence about counterfactual physiology.

The local BIDS release contains recordings from 35 participants. Participant labels include normal
cognition, mild cognitive impairment, and Alzheimer's disease classifications; two participants have
missing group labels. The source study recorded 19 monopolar EEG channels at 250 Hz during 40 Hz
auditory stimulation trials interleaved with rest periods [2]. The source study's primary analysis
focused on 40 Hz power, entrainment score, and phase-locking-value connectivity. This paper uses the
same recordings for a different purpose: forecasting a scalar frontal PAC target from temporally
ordered histories.

Seven frontal channels were selected: `Fp1`, `Fp2`, `F7`, `F3`, `Fz`, `F4`, and `F8`. The source
study reports Makoto-pipeline preprocessing, including a `1 Hz` high-pass filter, `50 Hz`
line-noise removal, artifact subspace reconstruction, average rereferencing, and ICA-based
component rejection [2]. Released sidecar files independently report the `1 Hz` high-pass filter,
`50 Hz` notch filter, and average reference. The local processing stage then applied an additional
`0.5-80 Hz` zero-phase band-pass filter, a `50 Hz` zero-phase notch filter, absolute-amplitude
masking above `100 microvolts`, and common-average rereferencing. Masked samples were set to zero
before rereferencing. Because frontal/frontopolar gamma-band EEG is vulnerable to ocular and
facial-muscle activity [6], this deterministic conditioning should not be read as a validated
artifact-removal pipeline for physiological PAC. Each event period was segmented into two-second
windows with a one-second hop.

### B. PAC Label Construction

Theta-gamma PAC was measured using the modulation index introduced by Tort et al. [5]. For each
channel, theta phase was extracted from `4-8 Hz`, gamma amplitude from `38-42 Hz`, and the gamma
amplitude distribution was summarized over 18 theta-phase bins. The normalized divergence from a
uniform distribution produced a dimensionless modulation-index value. Values were averaged across
the seven selected channels to create one scalar frontal timing target, not a spatial connectivity
analysis.

These modulation-index values are used as retrospective EEG-derived targets. No surrogate
correction or phase-clustering debiasing was applied, so the values should not be read as
definitive evidence of physiological theta-gamma coupling, endogenous gamma activity, source-level
entrainment, or therapeutic response [7].

PAC was computed over complete event periods rather than individual two-second windows because short
windows provide too few theta cycles for stable phase binning. Most event periods lasted 20 or 40
seconds, with brief final rest periods also present. Each two-second window inherited the PAC value
of its containing period. This stabilizes the
label but has three consequences: labels repeat within periods, adjacent samples are not independent,
and a PAC value assigned to an early window summarizes signal samples acquired later in that period.
The present analysis is therefore retrospective; an online estimator must be evaluated before live
use.

### C. Temporally Ordered Forecasting Dataset

Each temporal sample used a 20-step lookback and a target five steps into the future. With a
one-second hop, this corresponds to 20 stored-series seconds of history and a target five seconds
after the sequence endpoint. Sequences were constructed separately within each participant so that
no sequence crossed a participant boundary. Target indexing uses no later PAC-series entry as an
input, but it does not resolve the online-availability limitation of the event-period PAC summaries.

The initial representation contained 73 candidate features per time step:

- 61 spectral features;
- 7 PAC-history features: current PAC, trailing means over 2, 4, 8, and 16 steps, and differences
  over 1 and 4 steps;
- 5 stimulation-context features: stimulation state, normalized time since switch, recent
  stimulation fraction, and sine/cosine protocol-phase terms.

An exploratory ablation identified the 12 PAC-history and stimulation-context features as the
best-performing held-out test representation in this fixed split. Because representation choice was
informed by this benchmark, the result should be treated as exploratory until repeated
participant-level splits or nested model selection are run. The data were divided by participant into
24 training, 5 validation, and 6 test participants. The resulting temporal dataset contained 11,160
training, 2,605 validation, and 2,678 test sequences. Normalization statistics were fit on the
training split only and then applied to all splits.

### D. Backward-Looking PAC Stress Test

To test how strongly the event-summary target definition influenced the result, an additional
benchmark reconstructed contiguous event segments from the overlapping windows and recomputed PAC at
each timestamp from a five-second backward-looking context ending at that timestamp. The benchmark
used the same 20-step lookback, five-step horizon, 12 features, participant splits, and train-only
normalization. For contexts shorter than three seconds at segment boundaries, the PAC computation
used 9 rather than 18 phase bins.

In this stress test, each input PAC value was computed without EEG samples after its own timestamp.
However, the benchmark still used zero-phase filtering within each bounded context, and five-second
PAC contexts provide limited theta-cycle support. It is therefore an information-boundary stress
test that is closer to online availability than complete-event back-assignment, but it is not a
validated streaming estimator.

### E. Temporal Model

The selected forecaster is a lightweight temporal convolutional network (TCN), which applies temporal
convolutions to ordered samples [8]. An input projection is followed by four residual
depthwise-separable temporal blocks with kernel size 3 and dilations `[1, 2, 4, 8]`. Within the
stored input sequence, left-only padding prevents later entries from entering an earlier temporal
representation. Attention pooling summarizes the 20-step sequence before regression heads estimate
future PAC and PAC change.

The primary forecasting study evaluated the selected 12-feature representation across five random
seeds. For controller integration, a dual-head 12-feature checkpoint was trained separately with the
same hidden-64 architecture. That architecture contains 27,139 trainable parameters.
Forecasting-study, stress-test, and controller-replay results are reported separately because they
come from distinct retraining or replay runs.

### F. Retrospective Controller Replay

The integrated checkpoint was evaluated in offline replay on all 35 recorded PAC trajectories,
including the training, validation, and test splits. This replay probes controller behavior; it is
not an additional held-out forecasting test. The replay compared four strategies:

1. **Fixed schedule:** replay the nominal recorded stimulation schedule.
2. **Reactive threshold:** after a 10-sample warm-up, stimulate when current PAC is more than `0.5`
   standard deviations below its 30-sample rolling baseline; otherwise rest.
3. **TCN predictive:** stimulate or rest when normalized forecast PAC change crosses `-0.3` or
   `+0.3`; otherwise use a current-PAC threshold fallback with a three-step minimum hold before
   switching state.
4. **Alignment oracle:** stimulate below each participant's full-trajectory median PAC and rest
   otherwise.

The oracle uses the entire recorded trajectory and is not a causal or deployable strategy. For each
participant, low PAC was defined relative to that participant's full-trajectory median. The low-PAC
stimulation rate measured the fraction of below-median PAC points assigned stimulation. The
high-PAC rest rate measured the fraction of above-median PAC points assigned rest. Balanced
alignment was their mean:

`alignment = (low-PAC stimulation rate + high-PAC rest rate) / 2`.

The replay evaluates decision alignment against recorded PAC. It does not estimate how PAC would
physiologically change if counterfactual stimulation decisions were delivered. Because the
stimulation-context features are computed from the nominal recorded protocol rather than the
controller's decisions, replay does not model a closed feedback loop. It is an offline controller
diagnostic, not a prospective experiment.

## III. Results

### A. Feature Selection Improved Held-Out Forecasting

Table I shows a single-seed TCN ablation on the same participant split. Adding the spectral feature
set reduced held-out-participant generalization, while PAC history and stimulation context produced
the strongest result.

**Table I. Original exploratory single-seed feature ablation at a five-second horizon**

| Input representation                 | Features | Test R-squared |
| ------------------------------------ | -------: | -------------: |
| Spectral only                        |       61 |         -0.420 |
| All candidate features               |       73 |         -0.025 |
| PAC trajectory only                  |        7 |          0.344 |
| PAC trajectory + stimulation context |       12 |      **0.558** |

The ablation does not prove a biological mechanism for the spectral features' failure. It shows that
the larger spectral representation introduces variation that does not transfer effectively to the
held-out participants in this dataset.

Across five seeds, the selected 12-feature TCN achieved mean test `R-squared = 0.606`, with a range
from `0.558` to `0.647`. At the same five-second horizon, a last-value persistence baseline achieved
`R-squared = 0.104`.

### B. Backward-Looking PAC Changed the Model-Selection Result

Figure 1 compares the event-summary benchmark with the backward-looking PAC stress test using the
same TCN architecture at one random seed and one fixed split. Unique held-out targets increased from
104 to 2,678, and adjacent target repetition decreased from 96.2% to 0.0%. Persistence R-squared
decreased from 0.104 to -0.897. The backward-looking target retained modest predictable structure,
but the TCN did not outperform Ridge regression (0.212 versus 0.216). The event-summary result is a
diagnostic of stored-series structure, not evidence that a nonlinear TCN is necessary for an
online-compatible forecaster.

![Target-definition stress test. Complete-event PAC back-assignment includes later samples in early-window inputs; backward-looking PAC restricts each context to samples available by its timestamp. Bars show single-seed fixed-split R-squared on six held-out participants (2,678 sequences); no confidence intervals are shown.](../figures/pac_benchmark_stress_test.png)

### C. Predictive Replay Increased Low-PAC Coverage but Did Not Improve Overall Alignment

Table II reports offline replay of the integrated 12-feature checkpoint across all 35 recorded
trajectories. The predictive controller improved low-PAC stimulation coverage by 22.1 percentage
points relative to reactive thresholding, assigning stimulation to more below-median PAC samples.
However, the above-median-PAC rest rate decreased by 26.6 points. The predictive rule therefore
found more low-PAC periods, but it did so by stimulating more often during periods that the replay
metric would prefer to leave at rest.

**Table II. Retrospective controller replay on 35 recorded trajectories**

| Strategy                    | Bal. align. | Low stim. | High rest | MI gap x 10^-6 |
| --------------------------- | ----------: | --------: | --------: | -------------: |
| Fixed schedule              |       45.0% |     61.4% |     28.6% |          -6.55 |
| Reactive threshold          |   **64.5%** |     51.7% | **77.3%** |      **21.09** |
| TCN predictive (12-feature) |       62.2% | **73.8%** |     50.7% |          21.02 |
| Alignment oracle            |        100% |      100% |      100% |          33.36 |

The PAC gap is mean PAC during rest minus mean PAC during stimulation, reported in x 10^-6
modulation-index units. A positive value indicates
that stimulation decisions are concentrated more strongly in lower-PAC periods. The predictive and
reactive strategies produced nearly identical PAC gaps despite different action profiles.

### D. Leakage Checks and Label-Resolution Caveat

The stored temporal dataset was audited for subject overlap, future-index ordering, and normalization
contamination. No participant appeared in more than one split. Every target index was exactly five
steps after the sequence endpoint. Recomputed training statistics matched the stored normalizers. A
reduced-model permutation test produced approximately zero validation `R-squared` across five
independent label shuffles.

The main caveat is how PAC labels were computed and assigned. Because PAC is computed over complete
event periods, `82.2%` of five-step sample pairs have identical current and target PAC values.
Persistence still achieves only `R-squared = 0.104` on the held-out test split and
`R-squared = -0.272` on cross-event transitions. However, event-period back-assignment means that the
stored current-PAC input is not yet a validated online feature. The forecasting results evaluate
retrospective temporal structure, not an end-to-end streaming predictor.

## IV. Discussion

The forecasting results show that stored PAC histories and stimulation context contain information
that predicts PAC in held-out participants under the event-summary label definition. Feature
selection mattered within that benchmark: the compact representation transferred to unseen
participants more effectively than the larger candidate set. The target definition mattered more.
When PAC was recomputed from backward-looking contexts, Ridge and TCN both had positive held-out
R-squared, but the nonlinear advantage disappeared. This suggests that target construction should be
benchmarked before adding model complexity.

The replay separates forecast quality from controller performance. The integrated checkpoint
stimulates more low-PAC periods, but it also stimulates too frequently during above-median-PAC
periods. A future controller should tune its objective for both low-PAC coverage and high-PAC
sparing, evaluate thresholds on held-out participants, feed counterfactual actions back into
stimulation-context features during simulation, and replace back-assigned PAC summaries with an
online estimator. A corrected-target feature ablation should also separate PAC-only,
stimulation-context-only, and combined inputs to distinguish biomarker dynamics from recorded
schedule structure.

The study has seven main limitations:

1. The controller evaluation is retrospective replay, not a live intervention.
2. The replay cannot estimate physiological responses to counterfactual stimulation timing.
3. Primary PAC inputs are complete-event summaries assigned back to constituent windows and are not
   validated as streaming-available features.
4. The backward-looking stress test uses zero-phase filtering inside bounded contexts and is not a
   production streaming estimator.
5. PAC estimates may be sensitive to filtering, artifact handling, and finite-sample bias.
6. The `38-42 Hz` amplitude band overlaps the auditory stimulation frequency, so PAC estimates may
   reflect stimulation-locked steady-state response or residual artifact rather than endogenous
   gamma coupling.
7. The dataset is single-site and modest in size; the current results use one fixed participant
   split.

Because of these limitations, this study should not make clinical or therapeutic efficacy claims.
The next experiments should evaluate additional backward-looking PAC context lengths, implement a
streaming-compatible PAC estimator, measure repeated participant-split performance, calibrate
controller objectives using held-out participants, and then test a prospective streaming
implementation.

## V. Conclusion

In an event-summary benchmark, a 12-feature TCN predicted stored PAC-series entries on held-out
participants more accurately than a larger 73-feature candidate representation. Across five training
seeds on the same fixed split, mean forecasting performance reached `R-squared = 0.606`; this
estimates initialization variability, not sensitivity to which participants are held out. A
backward-looking PAC stress test then removed the repeated-target shortcut: the TCN retained positive
held-out R-squared but did not exceed Ridge regression. Offline replay showed stronger low-PAC
coverage without improved balanced alignment. The results support compact temporal features as a
retrospective benchmark, but they also show that the PAC target definition controls the conclusion.
A streaming PAC estimator, artifact sensitivity analysis, repeated participant-split validation, and
a separately validated controller are required before live adaptive-stimulation testing.

## References

[1] H. F. Iaccarino, A. C. Singer, A. J. Martorell, et al., "Gamma frequency entrainment
attenuates amyloid load and modifies microglia," _Nature_, vol. 540, pp. 230-235, 2016.
doi:10.1038/nature20587.

[2] M. Lahijanian, H. Aghajan, and Z. Vahabi, "Auditory gamma-band entrainment enhances default
mode network connectivity in dementia patients," _Scientific Reports_, vol. 14, art. 13153, 2024.
doi:10.1038/s41598-024-63727-z.

[3] M. Lahijanian, H. Aghajan, and Z. Vahabi, "40Hz Auditory Entrainment," OpenNeuro dataset
`ds005048`, ver. `1.0.1`. doi:10.18112/openneuro.ds005048.v1.0.1.

[4] G. Soleimani, M. A. Nitsche, T. O. Bergmann, et al., "Closing the loop between brain and
electrical stimulation: towards precision neuromodulation treatments," _Translational Psychiatry_,
vol. 13, art. 279, 2023. doi:10.1038/s41398-023-02565-5.

[5] A. B. L. Tort, R. Komorowski, H. Eichenbaum, and N. Kopell, "Measuring phase-amplitude
coupling between neuronal oscillations of different frequencies," _Journal of Neurophysiology_,
vol. 104, no. 2, pp. 1195-1210, 2010. doi:10.1152/jn.00106.2010.

[6] J. F. Hipp and M. Siegel, "Dissociating neuronal gamma-band activity from cranial and ocular
muscle activity in EEG," _Frontiers in Human Neuroscience_, vol. 7, art. 338, 2013.
doi:10.3389/fnhum.2013.00338.

[7] J. Aru, J. Aru, V. Priesemann, et al., "Untangling cross-frequency coupling in neuroscience,"
_Current Opinion in Neurobiology_, vol. 31, pp. 51-61, 2015. doi:10.1016/j.conb.2014.08.002.

[8] S. Bai, J. Z. Kolter, and V. Koltun, "An empirical evaluation of generic convolutional and
recurrent networks for sequence modeling," arXiv:1803.01271, 2018.
