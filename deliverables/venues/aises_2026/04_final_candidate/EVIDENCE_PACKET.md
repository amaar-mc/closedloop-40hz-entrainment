# EVIDENCE_PACKET.md — AISES 2026 Student Research Presentations

**Purpose:** vetted, on-artifact facts and numbers for Amaar to draw from while writing his own AISES abstract/poster text. This packet is technical/project evidence only — it does **not** contain a community-impact narrative, because only Amaar can honestly supply that (see the gate question in `FINAL_CANDIDATE_STATUS.md`). Every number below is sourced to the canonical project facts verified 2026-07-16; do not use numbers from older README summaries if they conflict with this packet.

**RED-venue reminder:** AISES prohibits nothing explicitly on AI-drafting (their policy is UNKNOWN, not confirmed-permissive), but this campaign treats every RED/UNKNOWN venue with report-style text as human-authored-only. Use this packet as a fact reference, not a source of sentences to copy.

---

## 1. The problem, in facts (no framing supplied — that's the author's job)

- Alzheimer's/dementia research has shown that rhythmic 40 Hz sensory stimulation (light and/or sound) can entrain gamma-band brain activity in some studies. This project builds a system to predict, from EEG, whether a person's brain is currently in a favorable state for that stimulation — rather than delivering it on a fixed timer.
- The physiological signal used is **phase-amplitude coupling (PAC)**, specifically the **Tort 2010 Modulation Index** between theta phase (4–8 Hz) and gamma amplitude (38–42 Hz).
- Dataset: **OpenNeuro ds005048**, version 1.0.1 — 35 dementia-clinic participants, 19 recorded EEG channels at 250 Hz, publicly available. This project uses 7 frontal channels (Fp1, Fp2, F7, F3, Fz, F4, F8). The paradigm alternates 40 Hz auditory stimulation blocks with rest blocks.
- Subject-level train/validation/test split: 24 / 5 / 6 participants (35 total), fully disjoint — no participant appears in more than one split. This matters because leaking a participant's own data across splits would inflate results artificially.

## 2. What was built (three stages — pick the one(s) relevant to the abstract's scope)

### Stage A — Static PAC estimation from raw EEG

- Model: **EEGNet**, a compact convolutional architecture, **1,457 trainable parameters**.
- Held-out test **R² = 0.287**.
- Context: multiple architectures (including much larger ones) were tried and converged near this same ceiling — evidence the limiting factor is label noise and channel coverage (7 frontal channels, event-level PAC labels), not model capacity. This is a genuine, defensible finding, not a shortfall to hide.

### Stage B — Forecasting future PAC (the temporal model)

**⚠️ Five distinct parameter counts exist across this project's history (four TCN variants plus the static EEGNet) — never collapse them. Report the count tied to the specific result being discussed, per RESULTS_CANONICAL.md's Generation A/B/C boundaries:**

|     Params | What it is                                                                                                                   | What result it's tied to                                                                                                                                                                                                                                                                                          |
| ---------: | ---------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|      1,457 | Static EEGNet current-PAC estimator (Stage A)                                                                                | R² = 0.287                                                                                                                                                                                                                                                                                                        |
| **22,914** | Gen-A **experimental** forecasting TCN (hidden=64, 12-feature input)                                                         | **The feature-ablation and five-seed results below (−0.025→0.558, five-seed mean 0.606) come from THIS model.**                                                                                                                                                                                                   |
|      5,154 | A real h=32 architecture-search variant (single-seed test R² ≈ 0.613)                                                        | Shows the signal is in the feature set, not model size — an architecture-search data point, not the deployed model. Mention only if discussing the architecture search itself.                                                                                                                                    |
| **27,139** | Gen-B **deployed** integrated controller checkpoint (`models/best_12feat_tcn_lb20_hz5_ts1.pth`, hidden=64, 12-feature input) | **This is the model behind the controller replay in Stage C below (62.23%/73.77%/50.68%).** Its own checkpoint metadata prints `test_r2=0.5844` — do not use that number as a standalone manuscript result; different generation paths produce the forecasting-study, stress-test, and replay metrics separately. |
|     31,043 | Gen-C historical 73-feature model                                                                                            | Superseded — behind the OLD 72.1%/82.6% controller numbers; do not use.                                                                                                                                                                                                                                           |

**Never write "the 27,139-param model achieves R² = 0.606" — that pairs a Gen-B fact (params) with a Gen-A result (the ablation/five-seed R²). If a sentence needs both a parameter count and an R² in the same breath, check which generation each belongs to first.**

- Input representation for both the Gen-A ablation runs and the Gen-B deployed checkpoint: **12 features** — 7 PAC-trajectory features (current PAC, trailing means over 2/4/8/16 steps, 1-step and 4-step differences) + 5 stimulation-context features (on/off state, normalized time since switch, recent stimulation fraction, protocol-cycle sine/cosine). Lookback 20 steps, horizon 5 steps (2 s windows, 1 s hop → forecasts ~5 s ahead).
- **Headline finding (feature ablation, Gen A, 22,914-param experimental TCN):** dropping 61 spectral/frequency-band features and keeping only the 12 PAC+stimulation-context features **raised** cross-subject held-out test R² from **−0.025** (all 73 candidate features) to **0.558** (single seed) / **0.606** (five-seed mean, range 0.558–0.647, population SD 0.029). A shuffled-label control scored **−0.332**, confirming the model is learning real structure, not fitting noise.
- Interpretation available to draw from (state as hypothesis, not fact): the spectral features may have been fitting subject-specific anatomy that doesn't transfer across people, while the simpler PAC-trajectory-plus-context features capture dynamics that do generalize. The ablation supports this; it does not prove the mechanism.
- **Honest caveat (important for a STEM-competency/rigor-minded rubric like Four Strands):** using a stricter, leakage-free "backward-looking" target definition instead of the complete-event target collapses the forecasting result from R² ≈ 0.606 toward **≈0.212**, roughly tying a simple Ridge regression baseline (both checkpoints in this stress test are the 27,139-param Gen-B architecture). This is a single-seed result and needs replication, but it is disclosed deliberately — it shows where a promising number depends on how the target was defined.
- Always report baselines alongside the TCN: **persistence** (repeat the last value) and **Ridge regression**, not the TCN number alone.

### Stage C — Closed-loop controller replay (retrospective, not clinical)

- The **deployed 27,139-param Gen-B checkpoint** (`models/best_12feat_tcn_lb20_hz5_ts1.pth`) was used to replay stimulation decisions against all 35 recorded PAC trajectories (train+val+test combined — this is an integration diagnostic, not a held-out generalization test).
- Results (alignment / low-PAC-stimulation coverage / high-PAC-rest specificity / PAC gap):
  - Fixed schedule: 45.01% / 61.43% / 28.59% / −6.55e-6
  - Reactive threshold: 64.49% / 51.67% / 77.30% / +21.09e-6
  - **TCN predictive (current 27,139-param model): 62.23% / 73.77% / 50.68% / +21.02e-6**
  - Alignment oracle (upper bound): 100% / 100% / 100% / +33.36e-6
- **Honest framing, not a clean win:** the predictive controller catches more of the moments that need stimulation (73.8% vs. reactive's 51.7%) but gives up specificity on the high-PAC/rest side (50.7% vs. reactive's 77.3%), and its overall balanced alignment (62.2%) is actually _below_ the simpler reactive controller (64.5%). This tradeoff — not a sweep — is the real result.

## 3. The process story (this is often the strongest material for a STEM-identity-oriented rubric)

- An earlier experimental architecture (documented in `archive/experimental_models/`) used PAC-derived features that turned out to circularly encode the prediction target, inflating R² to an implausible ~0.999. Recognizing and correcting this — treating an unrealistically good result as a signal to audit, not celebrate — is a genuine, personally-lived research moment available to draw from.
- The 73→12 feature reduction and the leakage-free-target stress test were both **audits Amaar ran on his own results**, not steps in an original plan. That arc (build → get a suspiciously strong number → investigate → find and fix the problem → report the corrected, more honest result) is real and specific to him — it is exactly the kind of concrete process detail this guide's companion (`AI_WRITING_TELLS_AND_AVOIDANCE.md`) flags as the antidote to vague, generic-sounding writing.

## 4. Hard boundaries — do not cross these in any AISES text

- No claim of clinical efficacy, patient-outcome improvement, disease slowing, prospective deployment, or live therapeutic validation.
- Say "retrospective controller replay" or "offline replay," never "clinical validation" or "clinical trial."
- The replay evaluates decisions against _recorded_ PAC trajectories; it does not know how a real brain would have responded to a different stimulation choice — state this if describing the controller.
- PAC labels are complete-event summaries assigned back to individual windows; state this granularity limit if discussing the forecasting numbers in any detail.
- Do not state as proven fact that spectral features "encode anatomy" — that is a hypothesis consistent with the ablation, not a demonstrated mechanism.
- Do not use the historical numbers 72.1% alignment / 82.6% low-PAC coverage / "91% oracle-bound" / "all 35 of 35 subjects benefit" — those belong to an older 73-feature, 31,043-parameter checkpoint, not the current model.

## 5. Personal/background facts (for the author to decide whether/how to use — not supplied as a narrative)

- Sole author: Amaar M. Chughtai, high-school student, Valley Christian High School, San Jose, CA.
- Personal motivation on record elsewhere in this project: a family member's dementia. (Use only if genuinely his to share, in his own words.)
- No documented mentor is named in the project's affiliation records; any mentor field must read `[AUTHOR TO CONFIRM]` unless Amaar supplies verified name/institution/dates/consent.
