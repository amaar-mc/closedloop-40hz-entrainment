# JSHS Research Paper — Human Writing Kit

## ⚠ Program status — read this before investing writing time

The national Junior Science & Humanities Symposium program's federal funding was
suspended effective around October 1, 2025. As of the most recent dossier check
(2026-07-16), the JSHS Northern California region page shows no 2026–27 cycle
information, and dozens of other regional hosts display an identical suspension
notice directing questions to the program's outreach contact. Whether NorCal will run
a JSHS-branded regional competition with a National-JSHS pathway this cycle is
**currently unconfirmed** — this is not a routine date delay, it's an open funding
question. Some regions have run non-JSHS-branded local substitutes in the interim that
do not feed into the national competition.

**Why this kit exists anyway:** the writing skills a JSHS research paper demands —
a tight abstract, a defensible methods section, honest reporting of a mixed result,
preparing for an oral-defense Q&A — transfer directly to STS, Synopsys, and every other
research-paper or oral-presentation venue in your list, whether or not JSHS itself runs
this cycle. Use this kit as general research-paper writing practice, and check the
regional page (jshs.org/region/california-northern/) periodically for an actual
resumption announcement before committing to a JSHS-specific deadline.

**If JSHS does resume:** historically, the regional research-paper submission deadline
has fallen in mid-January for a late-February regional symposium at San Francisco State
University — but treat any specific 2027 date as unconfirmed until officially posted.

---

**⚠ Before you write a single sentence:** the JSHS Statement of Outside Assistance (SOA)
requires disclosing any outside help, including AI tool use, in your research and
writing process. The Core Rules of Competition distinguish permitted editing assistance
from prohibited AI-drafted-then-edited content. The simplest, safest, and most honest
answer on this front is that you wrote the paper yourself — which is also what this kit
is built to make fast. Nothing below is a sentence to paste in; everything is a
question, a vetted fact, or a fill-in-the-blank scaffold.

**Format reminders:** a 250-word maximum abstract, plus a full research paper (JSHS
NorCal has historically required a full paper as part of the regional application, not
just the abstract). No teacher, mentor, or school sponsorship is required to register —
independent research is fully eligible. Projects that are demonstrations, "library"
research, or purely informational are explicitly not appropriate for competition — this
project (raw EEG → PAC computation → temporal forecasting → controller replay, with real
executed results) is squarely original, applied research.

**Judging context to keep in your head while writing:** JSHS's stated evaluative
question is "what was learned" — not just what the result was. Advancing students give
an oral presentation and defend it in Q&A, so this kit treats the oral defense as part
of the writing process, not an afterthought.

---

## 0. The scientific spine (same underlying results as every other venue kit)

The strongest, most defensible arc for this project: **built a model → it looked
promising under one feature set → tested harder via ablation → found a leaner
representation actually generalizes better across subjects → applied that model to a
downstream controller and got an honest, mixed result → tested the target definition
itself and found the strong forecasting number partly depends on how the label is
defined.** That sequence _is_ what happened — it isn't packaging.

**Two number-pairs must never be mixed:**

- **Feature-ablation experiment**: 73-feature test R² = −0.025; 61-feature
  spectral-only = −0.420; 7-feature PAC-only = 0.344; 12-feature PAC+Stim = 0.558
  (single-seed) / 0.606 (five-seed mean, range 0.558–0.647). Shuffle-label control =
  −0.332 (confirms the signal is real).
- **Target-definition stress test**: event-summary target — TCN 0.554, Ridge 0.260,
  persistence 0.104. Backward-looking (leakage-free) target — TCN 0.212, Ridge 0.216,
  persistence −0.897. Under the realistic target, the TCN ties Ridge rather than beating
  it. Single-seed; flag for replication.

Never pair 0.606 with 0.212 as if they measured the same thing.

**Two distinct TCN checkpoints exist — keep their parameter counts with their own
results, never each other's:**

- The **22,914-parameter** experimental forecasting model (hidden size 64,
  `archive/experimental/results/pac_stim_focused.json`) is behind the feature-ablation
  and five-seed numbers above (0.558/0.606). A separate 5,154-parameter (hidden size 32)
  architecture-search variant from the same file reached comparable single-seed R² on
  some configurations — real, but not the deployed model, and not the source of 0.606.
- The **27,139-parameter** deployed controller checkpoint
  (`models/best_12feat_tcn_lb20_hz5_ts1.pth`) is behind the controller-replay numbers
  only (62.23% alignment / 73.77% low-PAC stimulation / 50.68% high-PAC rest).

Say plainly in your Methods that these are two separately trained checkpoints of the
same architecture family, not one model wearing two parameter counts.

---

## 1. Abstract (250-word maximum)

**Length target:** 250 words, hard maximum. This is tight — expect several redrafts.

**Judging emphasis:** the abstract alone may determine whether your paper is read
closely; it has to carry your research question, method, headline result, and honest
caveat in a very small space.

**Questions to answer, in order:**

1. What question does this paper answer, in one sentence?
2. What did you build and evaluate it on (dataset, model type, one sentence)?
3. What is the headline result, with its actual number?
4. What is the one honest complication a careful reader needs even at 250 words?
5. What's the one-sentence takeaway?

**Vetted facts to draw from:**

- Dataset: OpenNeuro ds005048 v1.0.1, 35 participants, 7 frontal EEG channels, 250 Hz.
- Headline: dropping 61 spectral features (73→12) raised cross-subject test R² from
  −0.025 to a five-seed mean of 0.606 (range 0.558–0.647), on the 22,914-parameter
  forecasting model.
- Complication: the downstream controller replay (27,139-parameter deployed checkpoint)
  is a mixed result — better low-PAC coverage, worse high-PAC specificity, alignment
  below reactive thresholding.

**Fill-in-the-blank scaffold** (250 words is short — write tight, cut ruthlessly):

> `[Research question, one sentence]`. `[What you built and tested, one sentence]`.
> `[Headline result with the real number]`. `[The honest complication, one sentence]`.
> `[Takeaway, one sentence — no overclaiming]`.

`ILLUSTRATIVE ONLY — rewrite in your own words:` "...raised cross-subject R² from below
zero to about 0.6 across five seeds..." — a fragment only.

---

## 2. Introduction & background

**Length target:** roughly 1.5–2.5 pages, proportional to your overall paper length.

**Judging emphasis:** JSHS panels often include STEM-education faculty who are not EEG
specialists — write for a smart generalist.

**Questions to answer, in order:**

1. Why does this matter to you — state the personal stake calmly, in your own words.
2. What is 40 Hz auditory entrainment, and what does the evidence actually show (keep
   animal-model evidence and human evidence explicitly separate)?
3. What is phase-amplitude coupling — your own analogy first, then the term?
4. Why forecasting rather than reacting — what's the mechanistic argument for
   anticipating a PAC drop instead of only responding after it happens?
5. What's the specific gap your work addresses?
6. What is your research question, stated as one falsifiable sentence?

**Vetted facts to draw from:**

- Verified citations only (re-check each yourself before use): Iaccarino et al. 2016
  (Nature — animal-model evidence; do not extend to human auditory therapy without
  saying so explicitly), Tort et al. 2010 (J Neurophysiol — PAC method), Lawhern et al.
  2018 (J Neural Eng — EEGNet), Lahijanian et al. 2024 (Sci Rep — the ds005048 dataset
  paper), Martorell et al. 2019 (Cell), Chan et al. 2025 (Alzheimer's & Dementia).
- The reactive-vs-predictive framing: a system reacting after PAC has already dropped
  versus one anticipating the drop before it happens.

**Fill-in-the-blank scaffold:**

> `[Personal-stake opening, your own words, calm]`.
> `[The problem stated plainly]`.
> `[PAC explained with your own analogy, then the term]`: phase-amplitude coupling.
> `[Why anticipating matters, mechanistically]`.
> `[The gap you address]`. Research question: `[one falsifiable sentence]`.

---

## 3. Methods

**Length target:** roughly 2–4 pages — JSHS panels reward concrete, checkable rigor.

**Judging emphasis:** subject-level splitting and train-only normalization are
explainable rigor points a non-EEG panelist can still verify and reward.

**Questions to answer, in order:**

1. Data source and why public, de-identified data solved a specific problem for you.
2. PAC computation: method, bands, window/hop.
3. Subject-level train/validation/test splitting, and why disjointness matters — what
   would leak if you split by window instead of by subject?
4. The 12 input features, in your own words, by their two groups.
5. Model architecture — what "causal" means as a design guarantee, and the two-checkpoint
   distinction from Section 0 above (22,914 vs. 27,139 parameters, stated explicitly).
6. Baselines you compared against (persistence, Ridge) and why a model that doesn't beat
   them hasn't shown anything.
7. What the controller replay evaluates, and what it explicitly cannot tell you (this
   belongs in Methods, not just Discussion).
8. What leakage checks you ran, and why.

**Vetted facts to draw from:**

- Dataset: OpenNeuro ds005048 v1.0.1; 35 participants; 19 recorded channels, 250 Hz; 7
  frontal channels used (Fp1, Fp2, F7, F3, Fz, F4, F8); data already preprocessed
  upstream (1 Hz highpass, 50 Hz notch, ICA artifact removal, common average reference)
  — this pipeline adds light additional filtering (0.5–80 Hz bandpass, 50 Hz notch,
  common average reference), not the full raw-acquisition cleaning pipeline.
- PAC: Tort 2010 Modulation Index, theta phase 4–8 Hz × gamma amplitude 38–42 Hz.
  Windows 2 s at 250 Hz, 1-second hop.
- Splits: subject-level, fully disjoint, 24 train / 5 validation / 6 test (test
  subjects: sub-07, 08, 15, 21, 29, 35). No subject, future, normalization, or
  circular-PAC leakage.
- 12 features: 7 PAC-trajectory (current PAC; trailing means over 2/4/8/16 steps;
  differences over 1 and 4 steps) + 5 stimulation-context (on/off state; normalized time
  since switch; recent stimulation fraction; protocol-cycle sine and cosine).
- Model family: causal TCN, 20-step lookback, 5-step horizon. Two checkpoints: the
  22,914-parameter forecasting-study model and the 27,139-parameter deployed controller
  checkpoint (see Section 0).
- Static comparison: EEGNet, 1,457 parameters, held-out test R² = 0.287 — a practical
  ceiling from noisy, event-level labels and limited channel coverage, not a failure.
- Controller replay evaluates recorded PAC trajectories against what each policy would
  have chosen — it does not estimate how the brain would have physiologically responded
  to a different stimulation decision.
- Earlier archived experimental code circularly encoded the PAC target into a feature,
  inflating R² toward 0.999 — caught, and not used in any current model. Worth
  mentioning if you discuss "what was learned" — this is exactly that.

**Fill-in-the-blank scaffold:**

> Data: `[dataset, N, channels, sampling rate, why public data helped]`.
> PAC: `[method, bands, window/hop]`.
> Splits: `[counts, disjointness, what would leak otherwise]`.
> Features: `[the two groups, your own words]`.
> Model: `[architecture, lookback/horizon; both checkpoints named with their own
parameter counts and which results belong to which]`.
> Baselines: `[persistence, Ridge, why they matter]`.
> Controller replay: `[what it evaluates and its explicit limit]`.
> Leakage check: `[what you found and fixed, if applicable]`.

---

## 4. Results

**Length target:** roughly 2–4 pages, ablation as the largest subsection.

**Judging emphasis:** "what was learned" — a number without a comparison and an
interpretation reads as incomplete for this venue.

**Questions to answer, in order:**

1. What did the static-model ceiling show, and what does convergence across
   architectures tell you?
2. What did the four-subset feature ablation show, with the shuffle-control as evidence
   of real signal?
3. What did the five-seed replication add?
4. What did the target-definition stress test show, and why does the strong number
   depend partly on label definition?
5. What did the full-cohort controller replay show across all four policies, framed
   honestly as a tradeoff?
6. What did the habituation split show, without overclaiming it?

**Vetted facts (exact numbers, do not round):**

- Static EEGNet: 1,457 params, test R² = 0.287.
- Feature ablation (single-seed, 22,914-param model): 73 features R² = −0.025; 61
  spectral-only = −0.420; 7 PAC-only = 0.344; 12 PAC+Stim = 0.558.
- Five-seed 12-feature replication (same 22,914-param model): seeds 0.558, 0.620,
  0.597, 0.608, 0.647; mean 0.606; range 0.558–0.647; population SD 0.0291 / sample SD
  0.0326 (state your convention).
- Shuffle-label control: R² = −0.332.
- Target-definition stress test (single-seed): event-summary target — TCN 0.554, Ridge
  0.260, persistence 0.104, 104 unique held-out targets, 96.2% adjacent-window
  sameness. Backward-looking target — TCN 0.212, Ridge 0.216, persistence −0.897, 2,678
  unique targets, 0.0% adjacent-window sameness. TCN ties Ridge under the realistic
  target.
- Full-cohort controller replay (35 trajectories, 27,139-param deployed checkpoint):
  Fixed — 45.01% alignment / 61.43% low-PAC / 28.59% high-PAC / gap −6.55e-6. Reactive
  — 64.49% / 51.67% / 77.30% / +21.09e-6. TCN predictive — 62.23% / 73.77% / 50.68% /
  +21.02e-6. Oracle — 100/100/100 / +33.36e-6.
- Habituation: 17 of 35 subjects (48.57%) show declining PAC slope; paired t-test p =
  0.542 — no significant net trend. Descriptive only.
- **Never** attribute the historical 73-feature-model numbers (72.1% alignment, 82.6%
  low-PAC, 91% oracle framing, "35 of 35 benefit") to the current 12-feature, 27,139-
  parameter checkpoint — those belong to a different, 31,043-parameter model.

**Fill-in-the-blank scaffold:**

> Static ceiling: `[R², what convergence tells you]`.
> Feature ablation: `[all four numbers with the shuffle control as evidence of signal]`.
> Five-seed check: `[mean, range, what it adds]`.
> Stress test: `[both targets' numbers, honest statement that the TCN ties Ridge under
the realistic target]`.
> Controller replay: `[all four policies, framed as a tradeoff]`.
> Habituation: `[split and p-value, without overclaiming]`.

---

## 5. Discussion / conclusion — "what was learned"

**Length target:** roughly 1–2 pages. JSHS's core evaluative question is literally "what
was learned" — make this section answer that directly.

**Questions to answer, in order:**

1. What do you think the ablation result means — stated as a hypothesis ("consistent
   with"), not a proven mechanism?
2. What does the controller tradeoff suggest needs tuning before further testing?
3. What does the stress test say about how much of your headline number depends on
   label granularity?
4. What's the specific, real limitation that most threatens your central claim?
5. Where exactly is the line between what you've shown and clinical relevance?
6. What is the one thing you now believe that you didn't before this project — and
   what's the concrete next experiment?

**Vetted facts / framing to draw from:**

- The spectral-feature failure is _consistent with_ those features encoding
  subject-specific anatomy that doesn't transfer — a hypothesis the ablation supports,
  not a proven mechanism.
- The controller tradeoff (better low-PAC coverage, worse high-PAC specificity,
  alignment below reactive) is a targeting-calibration problem, not evidence the
  predictive approach is wrong in principle.
- The three metric sources (forecasting study, stress test, controller replay) come from
  distinct generation paths and are not pooled.
- Boundary language to state explicitly, in your own words: this is a retrospective,
  offline replay against recorded PAC trajectories; it does not estimate how the brain
  would have physiologically responded to a different stimulation decision; PAC labels
  are complete-event summaries assigned back to constituent windows, which limits
  event-level granularity and online availability of the label in a real system; this
  project makes no claim of clinical efficacy, disease modification, or prospective
  deployment.

**Fill-in-the-blank scaffold:**

> `[Interpretation of the ablation, marked as interpretation]`.
> `[What the controller tradeoff suggests needs tuning]`.
> `[What the stress test says about label dependency]`.
> `[The specific limitation that most threatens the central claim]`.
> `[The clinical-relevance boundary, your own words]`.
> `[The one belief that changed, and the concrete next experiment]`.

---

## 6. Preparing the oral defense

**Judging emphasis:** JSHS's regional format includes an oral presentation and Q&A
defense for advancing students. Your own project's honest limitations are unusually
strong preparation for this format — you already have the hard questions and honest
answers worked out from writing the Discussion section above.

**Questions to rehearse answering out loud, in your own words:**

1. Does the TCN actually beat the baselines? Where, and where does it not (the stress
   test tying Ridge is the honest answer here)?
2. Is PAC label granularity a problem? (Yes — event-summary labels assigned back to
   windows; state the specific limitation.)
3. Is this evidence the therapy helps patients? (No — retrospective replay against
   recorded trajectories, not a live intervention; say why those are different.)
4. Why does subject-level splitting matter, and what would happen without it?
5. Why is the spectral-feature failure your main finding rather than a footnote?
6. What outside assistance did you use, and how do you disclose it honestly on the SOA?

Write a one-sentence honest answer to each of these in your own words before the
symposium (if it runs) — rehearsing your own real answers, not a memorized script, is
what will hold up under follow-up questions.

---

## 7. Final reminders

- Complete the Statement of Outside Assistance with full honesty about any tool use in
  your research or writing process.
- No formal mentor or lab sponsorship is required — independent research is fully
  eligible. Keep any mentor-adjacent field `[AUTHOR TO CONFIRM]` until you have real
  names, institutions, dates, and consent.
- Before submitting anywhere, run the whole paper against the self-check rubric in
  `WRITE_IN_YOUR_OWN_VOICE.md`.
- Check jshs.org/region/california-northern/ for an actual 2026–27 cycle announcement
  before treating any specific deadline as real.
