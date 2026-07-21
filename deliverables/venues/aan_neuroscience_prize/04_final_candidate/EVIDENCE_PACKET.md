# EVIDENCE_PACKET.md — AAN Neuroscience Research Prize

**Purpose:** a vetted, on-artifact set of facts and numbers to draw from while writing the AAN application, abstract, and full report **in your own words**. Nothing in this file is submittable prose — it is the evidence bank. Every number below traces to `RESULTS_CANONICAL.md`, `RESEARCH_CORE.md`, or `LIMITATIONS_AND_THREATS.md` (verified on-artifact, 2026-07-16). If a poster or older README ever disagrees with a number here, this file (and its sources) wins.

**Judge audience reminder:** AAN reviewers are practicing neurologists and academic neuroscience researchers. They will read "neuroscience relevance," "creativity," "interpretation of data / pitfalls addressed," and "report quality" — the venue's own four criteria — more carefully than any other audience in this campaign. Lead every section with the brain-electrophysiology framing, not the machine-learning framing.

---

## 1. The neuroscience framing (lead with this, not the ML framing)

- The measured quantity is **phase–amplitude coupling (PAC)**, computed with the **Tort et al. (2010) Modulation Index**: theta phase (4–8 Hz) crossed with gamma amplitude (38–42 Hz), from frontal EEG. This is a scalar electrophysiological timing measure — not a clinical score, not a diagnosis.
- 40 Hz sensory (gamma) stimulation is an active line of Alzheimer's neuroscience: Iaccarino et al. (2016) reported reduced amyloid load and altered microglial state in mouse models under 40 Hz light flicker; Martorell et al. (2019) reported multisensory (audio-visual) 40 Hz stimulation improved pathology and some cognitive measures in mice. Auditory gamma entrainment has also been studied in a human dementia cohort (Lahijanian 2024 — this is the dataset's own provenance paper; check `CITATION_LEDGER` for the exact verified citation before using it).
- **The open neuroscience question this project addresses:** stimulation protocols in this literature are typically delivered on a **fixed schedule** (e.g., a fixed on/off duty cycle), independent of the individual's moment-to-moment brain state. If cortical entrainment (as reflected in PAC) fades at different times in different people — or within a session — a fixed schedule may stimulate when coupling is already high and miss the windows where it has dropped. This project asks: **can PAC decline be forecast early enough to allow a state-dependent, individualized stimulation schedule**, and does a forecast-driven controller actually target stimulation better than fixed or simple reactive rules?

## 2. Dataset and methods (state precisely, once, early)

- Source: **OpenNeuro ds005048, version 1.0.1** — a public dataset of **35 dementia participants** undergoing alternating 40 Hz auditory stimulation and rest epochs, EEG recorded at **19 channels, 250 Hz**.
- This pipeline uses **7 frontal channels** (Fp1, Fp2, F7, F3, Fz, F4, F8) — chosen for the frontal-midline theta/gamma coupling literature, and a practical constraint worth stating honestly: fewer channels is more compatible with a lightweight, less-obtrusive future recording setup.
- The dataset was already preprocessed upstream by its providers (1 Hz highpass, 50 Hz notch, ICA artifact removal, common average reference). This pipeline adds only light additional filtering (0.5–80 Hz bandpass, 50 Hz notch, artifact handling, common average reference) — **do not claim this project performs full raw-EEG clinical cleaning**; it builds on an already-cleaned public release.
- PAC windows: **2 seconds at 250 Hz, 1 second hop** between windows.
- Subject-level data split (never overlapping): **24 train / 5 validation / 6 test participants** (35 total), corresponding to **11,160 / 2,605 / 2,678** temporal samples. Held-out test participants: sub-07, 08, 15, 21, 29, 35. Subject-level splitting matters scientifically — it is the only way to know the model generalizes to a _new person_, not just a new moment from someone it has already seen.

## 3. Two-stage model architecture (state what each stage is _for_)

**Stage 1 — Static PAC estimation (EEGNet).** A compact convolutional network (**1,457 trainable parameters**) estimates the _current_ PAC value from one 2-second raw-EEG window. Held-out test **R² = 0.287**.

- This number should be framed as a **practical ceiling**, not a weak result: six to eight architectures spanning **1,457 to ~2,000,000 parameters** (Ridge regression, EEGNetLarge, SpecRNN, ViT-TCNet, ATCNet) were tried and none exceeded R² ≈ 0.29. Convergence of very different model sizes on the same ceiling is itself evidence — it points to the ceiling being set by the _data_ (noisy, event-level PAC labels; a 7-channel montage), not by model capacity. This kind of negative architecture search is a legitimate, reportable finding, not a null result to hide.

**Stage 2 — Temporal PAC forecasting (causal dilated TCN).** A temporal convolutional network with strictly causal convolutions (it can only look backward in time — an architectural guarantee, not just a training convention) ingests a 20-step lookback window and forecasts PAC **5 steps (~5 seconds) ahead**.

**There are several real parameter counts in this project's history — never collapse them, and always report the count tied to the specific result being cited:**

| Parameter count | What it is                                                                                                      | Which result it belongs to                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| --------------: | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
|           1,457 | Static EEGNet (Stage 1)                                                                                         | Held-out test R² = 0.287                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|          22,914 | Experimental hidden-64 (h=64) forecasting TCN, archived (`archive/experimental/results/*.json`)                 | The feature-ablation result (§4 below: −0.420 / −0.025 / 0.344 / 0.558) **and** the five-seed mean R² = 0.606 (range 0.558–0.647) — verified on-artifact by summing this checkpoint family's saved tensor shapes.                                                                                                                                                                                                                                                                                                                    |
|           5,154 | A real h=32 (narrower hidden width) architecture-search variant, archived alongside the h=64 runs               | Single-seed test R² = 0.639 (`tcn_h32_pac_stim`) and 0.684 (`tcn_h32_highreg_pac_stim`), the two primary 12-feature/7-channel logged variants. Shows the generalization gain comes from feature selection, not model size — a smaller network reaches comparable (in fact higher single-seed) performance. **This is a real logged result, not the deployed model, and it is not the source of the 0.606 five-seed figure.** Mention it only when specifically discussing the architecture search, and label it as the h=32 variant. |
|      **27,139** | **The deployed, integrated controller checkpoint**: `models/best_12feat_tcn_lb20_hz5_ts1.pth` (hidden width 64) | This is the checkpoint that drives the retrospective controller replay (§7 below: 62.23% / 73.77% / 50.68%). Verified on-artifact by summing the checkpoint's raw saved tensor sizes (108,556 bytes ÷ 4 bytes/float32 = 27,139).                                                                                                                                                                                                                                                                                                     |
|          31,043 | Historical 73-feature model, superseded                                                                         | The historical 72.1%/82.6%/91%-oracle numbers (see §8) — **do not use for the current project.**                                                                                                                                                                                                                                                                                                                                                                                                                                     |

**The rule to hold in every sentence you write:** never write "the 27,139-parameter model achieves R² = 0.606" — that pairs the deployed integration checkpoint's parameter count with a result that actually comes from the separate 22,914-parameter experimental run. If you state a parameter count, state the result that specific checkpoint produced, and nothing else.

## 4. Headline finding A — feature selection, not architecture, drove the gain (main current scientific finding)

**Checkpoint note:** every number in this section comes from the archived experimental hidden-64 TCN (**22,914 parameters** — see §3's parameter-count table), not from the 27,139-parameter deployed integration checkpoint. Keep this attribution when writing.

Single-seed test R² across feature subsets used as TCN input:

| Feature subset                       | # features |    Test R² |
| ------------------------------------ | ---------: | ---------: |
| Spectral-only                        |         61 | **−0.420** |
| All candidate features               |         73 | **−0.025** |
| PAC-trajectory-only                  |          7 |  **0.344** |
| PAC trajectory + stimulation context |         12 |  **0.558** |

Five-seed replication of the 12-feature model (seeds 42/123/456/789/2024): **0.558 / 0.620 / 0.597 / 0.608 / 0.647** → **mean R² = 0.606**, range **0.558–0.647** (population SD 0.0291 / sample SD 0.0326 — state which convention you use if you report an SD). A shuffled-label control on the same 12 features scored **R² = −0.332**, confirming the signal is real and not an artifact of the pipeline.

**What the 12 features are:** 7 PAC-trajectory features (current PAC; trailing means over 2/4/8/16 steps; differences over 1 and 4 steps) + 5 stimulation-context features (on/off state; normalized time since the last switch; recent stimulation fraction; and two features — sine and cosine — encoding position in the protocol cycle).

**Interpretation boundary (say this explicitly, don't let it be implicit):** dropping 61 spectral features improved cross-subject generalization more than any architecture change tested. One explanation _consistent with_ this finding is that the spectral features were fitting subject-specific characteristics (e.g., individual anatomy or skull/scalp conductance) that do not transfer to a new person, while the PAC-trajectory and stimulation-context features capture the _dynamics_ that do transfer. **This is a hypothesis the ablation supports — it is not a demonstrated mechanism**, and the AAN report should say so in exactly those terms.

## 5. Headline finding B — horizon behavior (where the forecast actually earns its keep)

Single-seed horizon sweep, test R² for TCN vs. a naive persistence baseline (predict "no change from now"):

| Horizon |   TCN | Persistence |
| ------: | ----: | ----------: |
|     1 s | 0.725 |       0.726 |
|     3 s | 0.607 |       0.178 |
|     5 s | 0.577 |       0.104 |
|     8 s | 0.370 |      −0.007 |
|    10 s | 0.669 |      −0.081 |

Persistence is competitive (even slightly ahead) at 1 second and collapses by 3 seconds. The TCN's real advantage lives in the **3–10 second band** — the lead time a proactive controller actually needs to act before coupling has already dropped. (The 10 s point is single-seed; label it as provisional and note it should be replicated before being treated as a stable number.)

## 6. The most important honest caveat — the target-definition stress test

This is the single strongest piece of evidence of scientific rigor in the whole project, and it directly answers the AAN rubric's "potential pitfalls of the methodology or interpretation have been addressed" criterion. State it plainly, not buried in a limitations appendix:

- PAC labels in this dataset are **complete-event summaries** — a single PAC value computed over an entire stimulation or rest event and then assigned back to every 2-second window inside that event. This means many adjacent windows share an identical label (measured at 96.2% adjacent-window label repetition under the event-summary definition), which inflates how "predictable" PAC looks at these short horizons — a model that just tracks slow block-level structure can look strong.
- Under a **leakage-free, strictly backward-looking target** (a label built only from information available up to that moment, with 0.0% adjacent-window repetition and 2,678 unique target values instead of only 104), the same experiment's forecasting R² **collapses from 0.554 to 0.212** — down to roughly Ridge-regression level (Ridge itself scores ~0.216–0.260 under the two target definitions; persistence collapses further, to −0.897, under the realistic target).
- **Read this pairing correctly:** the 0.554 → 0.212 comparison is the matched pair from the _same_ target-definition stress-test experiment. It is a _different_ experiment from the 73→12 feature-ablation result (which reports 0.558 single-seed / 0.606 five-seed-mean). **Never present 0.606 and 0.212 as if they were the same comparison** — that would misrepresent two separate experiments as one number moving.
- Honest headline sentence to build from (in your own words): under the realistic, leakage-free target definition, the TCN's forecasting advantage over Ridge regression **mostly disappears** — the two are roughly tied. The strong-looking 0.606 depends in part on how the event-summary label smooths the target.

## 7. Headline finding C — retrospective controller replay (mixed result, report honestly)

**Checkpoint note:** this replay uses the **deployed integration checkpoint**, `models/best_12feat_tcn_lb20_hz5_ts1.pth` — **27,139 parameters** (see §3's parameter-count table) — not the 22,914-parameter experimental run behind §4/§5's forecasting numbers. These are two different checkpoints from the same 12-feature architecture family; keep them distinct when writing.

The TCN's PAC forecasts were used to drive a stimulate/rest/maintain controller (with hysteresis), replayed offline against all **35 recorded PAC trajectories**, and compared against three baselines:

| Strategy                               |  Alignment | Low-PAC stimulation (sensitivity) | High-PAC rest (specificity) | PAC gap (×10⁻⁶) |
| -------------------------------------- | ---------: | --------------------------------: | --------------------------: | --------------: |
| Fixed schedule                         |     45.01% |                            61.43% |                      28.59% |           −6.55 |
| Reactive threshold                     | **64.49%** |                            51.67% |                  **77.30%** |           21.09 |
| **TCN predictive (12-feature)**        |     62.23% |                        **73.77%** |                      50.68% |           21.02 |
| Alignment oracle (perfect information) |    100.00% |                           100.00% |                     100.00% |           33.36 |

**Definitions to state once, in your own words, before the table:** _alignment_ = fraction of time the controller's stimulate/rest decision matches what the oracle (which sees the true future) would have chosen; _low-PAC stimulation_ = of the moments where PAC was actually low (stimulation was needed), the fraction the controller correctly stimulated during (sensitivity); _high-PAC rest_ = of the moments where PAC was actually high (rest was appropriate), the fraction the controller correctly rested during (specificity); _PAC gap_ = the average PAC difference the strategy achieves relative to not intervening.

**The honest reading (state this, don't soften it):** the TCN-driven controller improves low-PAC coverage substantially over reactive thresholding (73.77% vs. 51.67%) — it catches more of the moments that actually need stimulation. But it gives up specificity on the high-PAC side (50.68% vs. reactive's 77.30%), and its overall balanced alignment (62.23%) is **below** simple reactive thresholding (64.49%). This is a **targeting tradeoff, not a clean win** — exactly the kind of mixed result the AAN "interpretation of data" criterion rewards when it is reported candidly rather than spun as a success.

**Scope limit to state explicitly:** this replay spans all 35 participants across train/validation/test — it is a full-cohort **integration diagnostic**, not an additional held-out generalization test. The held-out generalization evidence is the five-seed forecasting R² above, not this table.

## 8. Hard claim boundaries (the AAN judge pool will probe these — pre-empt, don't wait to be asked)

State these early — ideally in the first paragraph of the abstract, not the limitations section, because this audience is a clinical/academic-neuroscience judge pool that will look for exactly this kind of overclaim:

- **No clinical efficacy claim.** No patient outcomes, no disease-progression slowing, no prospective or live deployment, no therapeutic validation is made or implied.
- **Replay ≠ clinical validation.** The controller's decisions are scored against _already-recorded_ PAC trajectories. This offline replay **cannot** estimate how a person's brain would have physiologically responded to a different (counterfactual) stimulation decision — it only tells you how well the controller's choices would have tracked the trajectory that was actually recorded.
- **Event-level label granularity.** PAC labels are complete-event summaries assigned back to constituent windows (see §6) — this limits the temporal resolution of what "prediction" means here and must be stated alongside any forecasting number.
- **Metrics are not pooled across experiments.** The feature-ablation study, the target-definition stress test, and the controller replay come from three distinct analyses and must never be combined into a single "model performance" claim.
- **Do not use the historical numbers.** An older 73-feature, 31,043-parameter model reported alignment 72.1%, low-PAC targeting 82.6%, "91% of oracle," and "35 of 35 subjects benefit." **None of these belong to the current 12-feature, 27,139-parameter checkpoint.** If you ever reference them, they must be explicitly labeled as historical/superseded context, never as the current result.

## 9. What makes this a good AAN fit (for your own framing decisions, not to paste)

- Direct category match to "Relevance to Neuroscience": PAC is a direct electrophysiological (anatomy/physiology/function) measure, not a behavior/psychology proxy the rubric discourages.
- "Interpretation of Data" / "potential pitfalls addressed": §6 (target-definition stress test) and §7 (mixed controller result) are exactly this criterion's target — they are the strongest, most defensible content in the whole packet.
- "Creativity": the reframing from "detect current PAC" to "forecast PAC 3–10 s ahead to enable proactive, individualized control" is the creative core — say why forecasting (not just measuring) matters for closed-loop stimulation.
- A structurally similar past AAN-winning pattern: a named computational tool for interpreting a specific neurological disease's imaging/signal data (2021 winner, MRI-based) — this project is the same shape (computational interpretation/forecasting tool for a specific neurological disease's EEG signal), different modality.

## 10. Sources for verified background citations (verify each yourself before using — do not paste a citation you have not personally opened)

- Tort, A.B.L. et al. (2010) — Modulation Index method for phase-amplitude coupling.
- Iaccarino, H.F. et al. (2016) — 40 Hz light-flicker gamma stimulation, amyloid/microglia effects in mouse models.
- Martorell, A.J. et al. (2019) — multisensory (audio-visual) 40 Hz gamma stimulation, mouse pathology/cognition.
- Dataset provenance paper (Lahijanian et al. 2024, or the exact citation in `CITATION_LEDGER`) — human auditory 40 Hz entrainment study underlying OpenNeuro ds005048. **Confirm the exact citation and DOI from `CITATION_LEDGER` before use — do not rely on this packet's memory of the author/year.**

---

_This packet mirrors `RESULTS_CANONICAL.md`, `RESEARCH_CORE.md`, and `LIMITATIONS_AND_THREATS.md` verified on-artifact 2026-07-16. If any number here is ever superseded by those files, the source files win._
