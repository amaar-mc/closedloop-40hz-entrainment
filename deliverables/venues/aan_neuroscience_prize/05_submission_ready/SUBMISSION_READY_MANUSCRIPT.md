# <!--

# RESIDUAL-RISK NOTE — NOT PART OF THE SUBMITTED TEXT. STRIP BEFORE SUBMITTING.

HIGHEST RESIDUAL-RISK VENUE IN THIS TRACK. Two blocking items the author must
resolve before this manuscript is submittable:

1. ORIGINALITY / AI-DRAFTING. AAN requires "the original research and WRITTEN
   WORK of the applicant." There is no explicit AI ban, but that clause is close
   enough that AI-assisted drafting is a live risk. Before submitting, the author
   should EITHER (a) rewrite this report in his own words, using this draft only
   as a scaffold and a source of his verified numbers, OR (b) email
   science@aan.com, describe the AI-assist roles (see AI_USE_DISCLOSURE.md), and
   confirm in writing that AI-assisted drafting with disclosure is acceptable.
   Keep drafts, notebooks, and result files as authorship evidence.

2. MENTOR E-SIGNATURE. AAN requires parent/guardian, teacher, AND mentor
   e-signatures. No named mentor is documented. Every mentor/advisor slot below
   is left "[AUTHOR TO CONFIRM]". If no real mentor can honestly verify the work
   and sign, the application is not submittable as-is — a structural gate,
   independent of the text.

# See MANUSCRIPT_SELF_CHECK.md for the full residual-risk detail.

-->

# Testing Whether EEG Phase–Amplitude Coupling Forecasts Survive a More Realistic Target Definition

**Amaar Chughtai**
Valley Christian High School, [AUTHOR TO CONFIRM: city, state]

_Submission for the American Academy of Neurology / Bhuwan Garg High School Neuroscience Research Prize._

---

## Structured Abstract (290 words; AAN limit 300)

**OBJECTIVE:** To test whether frontal-EEG phase–amplitude coupling (PAC) can be forecast across participants during 40 Hz auditory stimulation, and whether that conclusion holds when the PAC target is computed from backward-looking EEG rather than from complete-event summaries.

**BACKGROUND:** Forty-hertz auditory stimulation is being studied in neurodegeneration research. Any adaptive version of it would need EEG features available _before_ a stimulation decision. Retrospective labels can overstate forecasting accuracy if they summarize signal acquired after the modeled decision time, making target definition itself a methodological risk worth testing.

**DESIGN/METHODS:** I analyzed OpenNeuro ds005048, a public 40 Hz auditory-stimulation EEG dataset with 35 memory-clinic participants. From 7 frontal channels I computed PAC as the Tort Modulation Index — the dependence of 38–42 Hz gamma amplitude on 4–8 Hz theta phase. Participants were split by subject into 24 training, 5 validation, and 6 held-out test. A 12-feature causal temporal convolutional network (TCN) used PAC history and stimulation context to predict PAC five seconds ahead, benchmarked against persistence and Ridge regression. A stress test then recomputed PAC from five-second backward-looking windows and repeated the comparison.

**RESULTS:** On the event-summary target the TCN reached held-out R² = 0.554 (Ridge 0.260, persistence 0.104). But these labels repeated within stimulation periods: only 104 unique test targets, 96.2% identical to their neighbor. Backward-looking PAC raised unique targets to 2,678 and removed adjacent repetition. Under this stricter target the same model fell to R² = 0.212, matching Ridge (0.216) and no longer beating it; persistence collapsed to −0.897.

**CONCLUSIONS:** PAC forecasting carried real temporal structure, but target definition decided the model-selection conclusion in this single fixed-split test. Adaptive-stimulation work should validate streaming-available features and repeated participant splits before any live controller.

---

## Research Report

### Why I worked on this

Dementia is personal for me — it has touched my own family. But the reason I thought this specific problem was tractable is technical. Forty-hertz sensory stimulation has real preclinical support: driving gamma-frequency activity at 40 Hz reduced amyloid load in Alzheimer's-model mice (Iaccarino et al., 2016), and multisensory 40 Hz stimulation improved pathology and memory in later mouse work (Martorell et al., 2019). Human evidence is earlier-stage but growing; an open-label extension study reported retained EEG entrainment and less atrophy in mild Alzheimer's dementia (Chan et al., 2025), and the dataset I used comes from a human auditory-entrainment study in a dementia cohort (Lahijanian et al., 2024).

What struck me is that the delivery is almost always fixed. Stimulation runs on a set schedule — a fixed block on, a fixed block off — regardless of what the brain is doing at that moment. Two things make that a problem. People differ: prior work reports that a substantial fraction of participants show little measurable entrainment response. [AUTHOR: verify the exact non-responder source and rate before citing a specific figure; softened here on purpose.] And within a single session, responses habituate — a well-described feature of the nervous system since Thompson and Spencer (1966), the same reason you stop noticing a clock ticking. A fixed schedule cannot see either effect. So I asked a narrower, testable question: **can you forecast where coupling is heading a few seconds ahead, well enough that a controller could act before a decline instead of after it?**

### Data and the coupling measure

I used OpenNeuro ds005048 (v1.0.1): 35 memory-clinic participants, EEG recorded at 250 Hz across 19 channels, alternating 40 Hz auditory stimulation and rest. I selected 7 frontal channels (Fp1, Fp2, F7, F3, Fz, F4, F8). The data were already cleaned upstream by the dataset providers (1 Hz high-pass, 50 Hz notch, ICA, common average reference); I added only light extra filtering, so I am not claiming to clean raw EEG from scratch. I measured entrainment as theta–gamma PAC using the Tort Modulation Index (Tort et al., 2010): 4–8 Hz theta phase crossed with 38–42 Hz gamma amplitude. Windows are 2 seconds with a 1-second hop; the split is subject-level (24 train / 5 validation / 6 test; 11,160 / 2,605 / 2,678 windows) so no participant appears in two splits.

One label detail matters for everything that follows, and I want to state it up front: PAC was computed over a full stimulation or rest event and then assigned back to every 2-second window inside that event. The labels are complete-event summaries, not independent per-window measurements.

### A ceiling I did not expect

I first tried to estimate _current_ PAC from a single raw-EEG window. I ran eight architectures, from a 1,457-parameter EEGNet (Lawhern et al., 2018) up to models near a million parameters. They converged on essentially the same held-out score, R² ≈ 0.287. When a tiny linear model and a large network land in the same place, the limit is in the data, not the architecture — here, the event-level labels and a 7-channel frontal montage. I treat 0.287 as a practical ceiling, not a failure. It also redirected me: instead of estimating the instantaneous value better, I should ask whether the _trajectory_ of PAC is predictable.

### The feature-selection finding

Moving to forecasting, I compared feature sets in an earlier experimental TCN (a separate, smaller model from the one used in the stress test and controller below — I keep those generations apart and do not pool their numbers). A 73-feature set dominated by spectral power generalized poorly across subjects (single-seed R² = −0.025; a spectral-only subset was worse at −0.420). Dropping the spectral features and keeping 12 PAC-trajectory and stimulation-context features reversed that: a 7-feature PAC-only set reached 0.344, and the 12-feature set reached 0.558 single-seed, with a five-seed mean of 0.606 (range 0.558–0.647). A shuffled-label control sat at −0.332, so the signal is real. The interpretation I find most plausible is that spectral features encode subject-specific anatomy that does not transfer, while PAC dynamics do — but that is a hypothesis consistent with the ablation, not something the ablation proves.

### The stress test I most want a neuroscientist to check

The feature result looked strong. I did not trust it, because of the label detail above. If a PAC value summarizes a whole event and is copied onto every window in that event, then predicting "the future" can partly mean predicting a number the model has effectively already seen. So I measured it. On the held-out set the event-summary target had only 104 unique values, and 96.2% of consecutive targets were identical to their neighbor. That is not a forecasting problem so much as a copying problem.

I rebuilt the target to be leakage-free: PAC recomputed from a five-second backward-looking window, so each window's label depends only on its own recent past. That raised the number of unique held-out targets from 104 to 2,678 and eliminated the adjacent repetition. Then I re-ran the same architecture on both targets. On the event-summary target it scored R² = 0.554 (Ridge 0.260, persistence 0.104). On the leakage-free target it scored R² = 0.212 — and at that point it no longer beat Ridge regression (0.216), though both stayed well above persistence, which collapsed to −0.897. The honest reading is that much of the strong-looking forecasting number came from how the target was defined, not from the model. I am reporting this rather than burying it, because it is the single most important thing I learned.

### Putting the forecaster into a controller — a mixed result

I connected the forecasts to a closed-loop controller (stimulate / rest / maintain, with a personalized rolling baseline and hysteresis) and replayed its decisions offline against all 35 recorded PAC trajectories, alongside a fixed schedule, a reactive threshold, and an oracle upper bound. The predictive controller did one thing clearly better: it covered 73.8% of low-PAC windows that need stimulation, versus 51.7% for the reactive controller. But it gave up specificity on the other side, resting during only 50.7% of high-PAC windows versus the reactive controller's 77.3%. Netting those out, its balanced alignment (62.2%) came in just below reactive thresholding (64.5%), and its PAC targeting gap was essentially tied with reactive and about two-thirds of the oracle's. This is a targeting trade-off, not a win.

Two boundaries on that result. It is a retrospective replay against _recorded_ trajectories: it scores what each controller would have decided, and cannot observe how a brain would have physiologically responded to a different stimulation choice. And because the replay spans all 35 participants across all splits, it is a full-cohort integration check, not an additional held-out test.

### What I take from this

For a neuroscience audience the useful contribution here is not a controller that works. It is a demonstration that in EEG-biomarker forecasting, the target definition can decide the conclusion — and that this is measurable and fixable. I make no claim of clinical efficacy, disease modification, or deployment. Numbers from the forecasting experiment, the target-definition stress test, and the controller replay come from distinct model generations and are not pooled into one performance figure.

### Limitations

The event-summary labels are the central threat, and the backward-looking target is my attempt to bound it. All headline numbers come from a single fixed subject split; repeated splits or cross-validation are needed before the forecasting numbers should be trusted as stable. The offline replay is not physiology. The montage is 7 frontal channels from one dataset of 35 people, with no external replication. The static ceiling (R² = 0.287) would feed forward into any live pipeline that used estimated rather than ground-truth PAC. And the spectral-anatomy explanation is a hypothesis, not a demonstrated mechanism.

### What I would do next

The priorities follow directly from the limitations: repeated participant splits and cross-validation; a feature set restricted to what is genuinely available online; an end-to-end test with the PAC estimator inside the loop instead of ground-truth PAC; and a second, demographically distinct dataset. Only after that would a live feasibility study, under appropriate institutional oversight, be worth designing.

---

### Figures (author to insert; captions written to current numbers)

- **[FIGURE 1: PAC forecasting R² versus prediction horizon for the TCN, persistence, and Ridge on the event-summary target. Persistence is competitive at 1 s (≈0.73) and collapses by 3 s; the TCN holds R² ≈ 0.58 at 5 s where persistence is ≈0.10. — source results/figures/horizon_sweep.png; AUTHOR: confirm the archived figure reflects the event-summary target sweep in RESULTS_CANONICAL, not an older smoothed-target version.]**
- **[FIGURE 2: Target-definition stress test — held-out R² for TCN / Ridge / persistence on the event-summary target (0.554 / 0.260 / 0.104) versus the leakage-free backward-looking target (0.212 / 0.216 / −0.897), with unique-target counts 104 vs 2,678. — AUTHOR TO CREATE from the stress-test values in this report; do not reuse an older figure.]**
- **[FIGURE 3: Retrospective controller replay across 35 trajectories — alignment, low-PAC stimulation rate, and high-PAC rest rate for fixed / reactive / TCN-predictive / oracle. — source results/figures/controller_comparison.png; AUTHOR: regenerate from results/metrics/controller_comparison_12feat.json, since the archived figure shows superseded 73-feature numbers.]**

### References

1. Iaccarino HF, et al. Gamma frequency entrainment attenuates amyloid load and modifies microglia. _Nature_ 540(7632):230–235, 2016. doi:10.1038/nature20587
2. Martorell AJ, et al. Multi-sensory gamma stimulation ameliorates Alzheimer's-associated pathology and improves cognition. _Cell_ 177(2):256–271, 2019. doi:10.1016/j.cell.2019.02.014
3. Chan D, et al. Gamma sensory stimulation in mild Alzheimer's dementia: an open-label extension study. _Alzheimer's & Dementia_ 21(10):e70792, 2025. doi:10.1002/alz.70792
4. Lahijanian M, et al. Auditory gamma-band entrainment enhances default mode network connectivity in dementia patients. _Scientific Reports_ 14:13153, 2024. doi:10.1038/s41598-024-63727-z
5. Sahu PP, Tseng P. Gamma sensory entrainment for cognitive improvement in neurodegenerative diseases: opportunities and challenges ahead. _Frontiers in Integrative Neuroscience_ 17:1146687, 2023. doi:10.3389/fnint.2023.1146687
6. Tort ABL, et al. Measuring phase–amplitude coupling between neuronal oscillations of different frequencies. _Journal of Neurophysiology_ 104(2):1195–1210, 2010. doi:10.1152/jn.00106.2010
7. Lawhern VJ, et al. EEGNet: a compact convolutional neural network for EEG-based brain–computer interfaces. _Journal of Neural Engineering_ 15(5):056013, 2018. doi:10.1088/1741-2552/aace8c
8. Thompson RF, Spencer WA. Habituation: a model phenomenon for the study of neuronal substrates of behavior. _Psychological Review_ 73(1):16–43, 1966. doi:10.1037/h0022681

### Acknowledgements

This project was conducted independently by the author. Statistical test selection was discussed with an AP Statistics instructor. [AUTHOR TO CONFIRM: whether to acknowledge informal mentorship, and if so the mentor's name, role, and institution, with their permission — AAN requires a mentor e-signature, so this must be a real person who can verify the work.] EEG data are from the open-access OpenNeuro dataset ds005048 (v1.0.1); all analysis code is the author's own.

### Data and code availability

EEG data: OpenNeuro ds005048 (https://openneuro.org/datasets/ds005048). Analysis code available from the author on reasonable request.
