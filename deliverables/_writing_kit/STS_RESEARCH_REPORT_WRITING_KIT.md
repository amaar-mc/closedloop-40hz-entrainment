# STS Research Report — Human Writing Kit

**Venue:** Regeneron Science Talent Search 2027. **Deadline:** application + all
recommendations due November 5, 2026, 8:00 PM ET, no exceptions.
**Format:** up to a 20-page original scientific paper (the "Research Report"), plus
separate essay questions about you and your activities, recommendations, and
transcripts — submitted only through the smapply.org portal, no external links
permitted in the report.

**⚠ Before you write a single sentence:** you will sign the Society for Science Ethics
Statement certifying that the Research Report and your application answers are your own
composition. This kit exists so that certification is true and so you can still write
fast. Nothing below is a sentence you should paste in. Everything below is illustrative
fragments (always marked), vetted facts, and questions for you to answer in your own
words.

**Judging context to keep in your head while writing:** STS review is holistic, by 3+
PhD scientists, and STS does not publish a numeric rubric. Roughly 2,600+ entrants funnel
to ~300 Scholars (~11–15%) and ~40 Finalists (~1.5%). The Research Report carries the
greatest weight of any single component, but essays, activities, grades, and
recommendations are all explicitly part of the holistic read — a strong report does not
carry a weak application by itself. Judges are often reading _outside_ their own
subfield, so the report has to hold up for a generalist PhD scientist, not just an EEG
specialist.

---

## 0. Before you draft: the scientific spine of this report

Across every section, the strongest, most defensible narrative arc for this project is:
**built a model → it looked promising under one feature set → tested harder via
ablation → found the leaner 12-feature representation actually generalizes better across
subjects → applied that model to a downstream controller and got an honest, mixed
result → tested the target definition itself and found the strong forecasting number
partly depends on how the label is defined.** That's not spin — it's the actual sequence
your canonical results support, and it is the single most STS-legible structure
available: "I found something that looked strong, then I tested it harder; here's what
survived and what didn't."

Two number-pairs must **never** be mixed. Keep them straight in your own notes before you
write:

- **Feature-ablation experiment** (which features generalize): 73-feature set test R² =
  −0.025; 61-feature spectral-only = −0.420; 7-feature PAC-only = 0.344; 12-feature
  PAC+Stim = 0.558 (single-seed) / 0.606 (five-seed mean, range 0.558–0.647). Shuffle-label
  control = −0.332 (confirms the 0.558/0.606 signal is real, not noise).
- **Target-definition stress test** (whether the forecast survives a stricter, leakage-free
  label): under the event-summary target, TCN = 0.554, Ridge = 0.260, persistence = 0.104.
  Under the backward-looking (leakage-free) target, TCN = 0.212, Ridge = 0.216,
  persistence = −0.897. Under the realistic target the TCN's edge over Ridge collapses —
  it is _tied_ with Ridge, not beating it. Single-seed; flag for replication.

These are the same-experiment matched pairs (0.558/0.606 belongs with the ablation;
0.554→0.212 belongs with the stress test). Never write a sentence that pairs 0.606 with
0.212 as if they measured the same thing.

**There are two distinct causal TCN checkpoints in this project — never merge their
parameter counts with each other's results:**

- **Generation A — the experimental forecasting model** (hidden size 64, **22,914**
  trainable parameters, `archive/experimental/results/pac_stim_focused.json`). This is
  the model behind every number in Section 0 above: the feature-ablation R² values
  (−0.420 / −0.025 / 0.344 / 0.558) and the five-seed replication (mean 0.606, range
  0.558–0.647). A separate architecture-search pass at hidden size 32 (**5,154**
  parameters, same source file) reached comparable or even slightly higher single-seed
  R² on some configurations — a real result worth mentioning if you discuss architecture
  choices, but it is not the deployed model and not the source of the 0.606 figure.
- **Generation B — the deployed integrated controller checkpoint**
  (`models/best_12feat_tcn_lb20_hz5_ts1.pth`, hidden size 64, **27,139** trainable
  parameters). This is the model behind the controller-replay numbers only (62.23%
  alignment / 73.77% low-PAC stimulation / 50.68% high-PAC rest).

When you write the Methods section, say plainly that the forecasting study and the
controller integration used separately trained checkpoints of the same architecture
family with different parameter counts (22,914 vs. 27,139) — do not describe "the model"
as if there were only one, and never attach the 0.606 forecasting result to the
27,139-parameter figure.

---

## 1. Title & abstract

**Length target:** title is one line; STS itself doesn't set an abstract length limit in
the Research Report, but keep it to roughly 250–300 words — tight enough that a judge
reading fast gets the whole arc.

**Judging emphasis:** the abstract is often the first thing a judge reads and the last
thing they check against the body — it needs to promise exactly what the report delivers,
no more.

**Questions to answer, in order:**

1. In one sentence, what question were you actually trying to answer?
2. What did you build to answer it (one sentence — dataset, model type, what it forecasts)?
3. What is the single most important number, and what is it being compared against?
4. What is the honest complication — the mixed result or the caveat — that a careful
   reader needs to see even in the abstract?
5. What did you conclude, in one sentence, without overclaiming?

**Vetted facts to draw from:**

- Dataset: OpenNeuro ds005048 v1.0.1, 35 memory-clinic participants, 19 recorded EEG
  channels, 7 frontal channels used (Fp1, Fp2, F7, F3, Fz, F4, F8), 250 Hz.
- PAC = Tort 2010 Modulation Index, theta phase (4–8 Hz) crossed with gamma amplitude
  (38–42 Hz).
- Headline number: dropping 61 spectral features (73→12) raised cross-subject test R²
  from −0.025 to a five-seed mean of 0.606 (range 0.558–0.647).
- Current controller checkpoint: 12-feature causal TCN, 27,139 trainable parameters,
  20-step lookback, 5-step horizon.
- Controller replay is mixed, not a clean win (see Results section facts below).

**Fill-in-the-blank scaffold** (answer each blank in your own words, then write it as
connected prose — do not just concatenate the blanks):

> `[The problem, one sentence — what's hard about knowing when to stimulate]`.
> `[What you built — one sentence, name the model type and what it forecasts]`.
> Using EEG recordings from `[N]` participants, I found that `[the ablation headline,
in your own words, with the actual R² numbers]`. When I applied this model to `[the
downstream task — the controller]`, the result was `[honest characterization — mixed,
a tradeoff, not a clean improvement]`. `[One sentence bounding what this does and does
not show — retrospective replay, not clinical validation]`.

`ILLUSTRATIVE ONLY — rewrite in your own words:` "...raised test R² from below zero to
about 0.6..." — a fragment only, not a sentence to reuse.

---

## 2. Introduction & background

**Length target:** roughly 2–3 pages of the 20.

**Judging emphasis:** this is where a non-specialist PhD judge decides whether they trust
you to explain your own field. Define every term once, plainly, before you use it again.

**Questions to answer, in order:**

1. Why does this problem matter to you personally, and how do you want to state that —
   calmly, without overstatement?
2. What is 40 Hz auditory entrainment, and what does the existing evidence actually show
   (animal models vs. human evidence — keep these distinct)?
3. What is phase-amplitude coupling, in your own plain-language analogy, before the
   technical term?
4. Why would predicting PAC ahead of time (rather than reacting after a drop) matter for
   a stimulation system? What's the mechanistic argument?
5. What's the gap in prior approaches that your work addresses — is it that nobody had
   tried forecasting, or that a naive approach doesn't generalize, or something else?
6. What is your research question, stated as a single, falsifiable question?

**Vetted facts to draw from:**

- Grandmother / personal-stake framing (yours to state in your own words and your own
  register — this is the one place a generic scaffold genuinely doesn't help; it has to
  be exactly how you actually feel about it, stated calmly).
- The reactive-vs-predictive framing: a system that only responds after PAC has already
  dropped versus one that anticipates the drop before it happens.
- Citations you have already personally verified (do not add any you have not verified
  yourself against the source): Iaccarino et al. 2016 (Nature, animal model — 40 Hz
  reduces amyloid in mice; do NOT extend this claim to human auditory therapy without
  saying so explicitly), Tort et al. 2010 (J Neurophysiol — PAC Modulation Index method),
  Lawhern et al. 2018 (J Neural Eng — EEGNet), Lahijanian et al. 2024 (Sci Rep — the
  ds005048 dataset paper itself), Martorell et al. 2019 (Cell), Chan et al. 2025 (Alzheimer's
  & Dementia). Confirm each DOI yourself before citing (do not trust this list without
  re-checking; you verified these once already via CrossRef/PubMed — re-open each one).
- Note: STS Research Reports may not include clickable external links — format citations
  as a plain reference list, not hyperlinks.

**Fill-in-the-blank scaffold:**

> `[Personal-stake opening, 2-4 sentences, your own words, calm register]`
> `[The problem stated plainly: why timing of stimulation might matter more than just
whether stimulation happens]`
> `[Explain PAC with your own analogy, then name the term]`: phase-amplitude coupling.
> `[What prior approaches to this kind of system do — reactive, threshold-based]`, and
> `[why anticipating a change might do something a reactive system can't]`.
> `[The gap you address]`. My research question: `[state it as one falsifiable
question]`.

**STS-specific note:** if you discuss the earlier discovery of circular/leaky PAC
features in an earlier version of your code, this is a strength, not something to
downplay — STS explicitly rewards process-as-evidence. State what you found, how you
found it, and what you changed.

---

## 3. Research question & hypothesis

**Length target:** a half page to one page — often folded into the end of the
introduction rather than a fully separate section; STS doesn't require a rigid section
structure, use judgment.

**Judging emphasis:** a sharp, falsifiable question reads as more mature than a vague
one. Judges are checking whether you know what would count as a "no."

**Questions to answer, in order:**

1. State your research question as a single sentence that could be answered "yes,"
   "no," or "partially, with a caveat."
2. What would falsify your hypothesis — what result would have told you the approach
   doesn't work?
3. Did your original hypothesis survive, get revised, or get overturned as you worked?
   (If it changed, say so — that's real science, not a flaw.)

**Vetted facts to draw from:**

- The project's actual arc _was_ a revision: an initial larger feature set did not
  generalize; the leaner 12-feature representation did. That's a legitimate example of a
  hypothesis being revised by evidence mid-project.
- The stress-test result (0.554 → 0.212 under a stricter target) is itself a
  falsification test you ran on your own strongest number — name it as exactly that.

**Fill-in-the-blank scaffold:**

> Research question: `[one falsifiable sentence]`.
> Initial hypothesis: `[what you expected before running the ablation]`.
> What happened instead: `[how the evidence revised or confirmed it]`.
> A result that would have falsified this: `[state the counterfactual — e.g., what if
R² across feature sets had come back all similarly poor, or the stress test had shown
no drop at all]`.

---

## 4. Methods

**Length target:** roughly 4–6 pages — this is where a PhD judge checks rigor, so don't
compress it just to save space.

**Judging emphasis:** this is the section most checkable by a scientist outside your
subfield. Concrete, explainable engineering details (disjoint subject-level splits,
train-only normalization) are exactly the kind of rigor a non-EEG PhD judge can verify
and reward.

**Questions to answer, in order (work through each as its own paragraph):**

1. Where did the data come from, and why this dataset (public, de-identified — what does
   that solve for you, e.g., IRB/consent friction that a novel human-subjects study would
   create)?
2. What is PAC, computed how, over what frequency bands, over what window length and
   hop?
3. How did you split subjects into train/validation/test, and why is subject-level
   disjointness the thing that matters (what would leak if you split by window instead)?
4. What are the 12 input features, in your own words, grouped into their two categories?
5. What is the model architecture, at a level a non-ML PhD judge can follow (what does
   "causal" mean here, and why is it a design guarantee rather than a training
   convenience)?
6. How did you evaluate it — what baselines did you compare against, and why do those
   baselines matter (a model that doesn't beat a naive baseline hasn't shown anything)?
7. What is the controller, and how does replay work — critically, what does replay
   evaluate and what can it _not_ tell you (state this limitation here, in Methods, not
   only in Discussion)?
8. What did you do to check for leakage, and why did you do that check (this is a good
   place for the process-as-evidence move if applicable)?

**Vetted facts to draw from:**

- Dataset: OpenNeuro ds005048 v1.0.1; 35 participants; 19 recorded channels, 250 Hz; 7
  frontal channels selected (Fp1, Fp2, F7, F3, Fz, F4, F8); data already preprocessed
  upstream (1 Hz highpass, 50 Hz notch, ICA artifact removal, common average reference) —
  say plainly that this repo applies light additional filtering (0.5–80 Hz bandpass,
  50 Hz notch, common average reference), not the entire raw-acquisition cleaning
  pipeline.
- PAC: Tort 2010 Modulation Index, theta phase 4–8 Hz × gamma amplitude 38–42 Hz. Windows
  2 seconds at 250 Hz, 1-second hop.
- Splits: subject-level, fully disjoint, 24 train / 5 validation / 6 test participants
  (test subjects: sub-07, 08, 15, 21, 29, 35). No subject, future, normalization, or
  circular-PAC leakage in the current pipeline.
- The 12 features: 7 PAC-trajectory features (current PAC; trailing means over 2/4/8/16
  steps; differences over 1 and 4 steps) + 5 stimulation-context features (on/off state;
  normalized time since switch; recent stimulation fraction; protocol-cycle sine and
  cosine).
- Model family: causal temporal convolutional network (TCN), 20-step lookback, 5-step
  horizon. "Causal" means the architecture can only see past inputs — it cannot look at
  future timesteps even during training, by construction, not by a training-time rule
  that could be violated. Two separately trained checkpoints of this family appear in
  the report: the **22,914-parameter** forecasting-study model (feature ablation and
  five-seed replication) and the **27,139-parameter** deployed controller-integration
  checkpoint (controller replay only) — say so explicitly and never quote one
  checkpoint's parameter count next to the other's result.
- Baselines always reported alongside: persistence (assume PAC stays constant) and Ridge
  regression. Persistence is strong at short horizons — the TCN is only scientifically
  interesting where it beats both baselines at operationally relevant horizons.
- Static comparison model: EEGNet, 1,457 parameters, held-out test R² = 0.287 — this is a
  practical ceiling from noisy, event-level PAC labels and limited frontal-channel
  coverage, not a failure; multiple architectures converged here.
- Controller replay evaluates recorded PAC trajectories against what each control policy
  (fixed schedule / reactive threshold / TCN-predictive / alignment oracle) would have
  chosen — it does not estimate how the brain would have physiologically responded to a
  different stimulation decision. State this explicitly.
- Leakage audit: earlier archived experimental code circularly encoded the PAC target
  directly into a feature, inflating R² toward 0.999 — this was caught and those features
  are not used in any current model.

**Fill-in-the-blank scaffold:**

> Data source: `[dataset, N participants, channels, sampling rate — why public data solved
a specific problem for you]`.
> PAC computation: `[method, bands, window/hop]`.
> Splitting: `[train/val/test counts, disjointness, why it matters — what would leak
otherwise]`.
> Features: `[the two feature groups, in your own words]`.
> Model: `[architecture, lookback/horizon, param count, why "causal" is a guarantee]`.
> Baselines: `[persistence and Ridge, why comparing against them matters]`.
> Controller replay: `[what it evaluates, and the explicit limit on what it can't tell
you]`.
> Leakage check: `[what you checked, and if relevant, what you found and fixed]`.

---

## 5. Results

**Length target:** roughly 4–6 pages, with the ablation as the largest subsection — this
is your spine, give it the space, don't force other results into equal-sized sections
just for symmetry.

**Judging emphasis:** STS rewards a defensible, specific claim over a hedged non-claim.
Every number needs a comparison right next to it.

**Questions to answer, in order:**

1. What was the static-model ceiling, and what does converging on it across multiple
   architectures tell you?
2. What did the feature-ablation experiment show, across all four feature subsets, with
   the shuffle-label control as evidence the 12-feature result is real signal?
3. What did the five-seed replication add beyond the single-seed number?
4. What did the target-definition stress test show, and why does it matter that the
   strong forecasting number partly depends on how the label itself is defined?
5. What did the full-cohort controller replay show, across all four policies, and how do
   you characterize the tradeoff honestly (not as a win, not as a failure)?
6. What did the habituation/fatigue split show, and how do you avoid overclaiming it?

**Vetted facts to draw from (do not round or alter any of these):**

- Static EEGNet: 1,457 parameters, held-out test R² = 0.287.
- Feature ablation (single-seed): 73 features R² = −0.025; 61 spectral-only R² = −0.420;
  7 PAC-only R² = 0.344; 12 PAC+Stim R² = 0.558.
- Five-seed 12-feature replication: seed values 0.558, 0.620, 0.597, 0.608, 0.647; mean =
  0.606; range 0.558–0.647; population SD 0.0291 / sample SD 0.0326 (state which
  convention you use).
- Shuffle-label control: R² = −0.332 (confirms the 0.606 is a real signal, not noise).
- Target-definition stress test (single-seed, sliding-window comparison): event-summary
  target — TCN 0.554, Ridge 0.260, persistence 0.104, 104 unique held-out targets, 96.2%
  adjacent-window sameness. Backward-looking (leakage-free) target — TCN 0.212, Ridge
  0.216, persistence −0.897, 2,678 unique targets, 0.0% adjacent-window sameness. Under
  the realistic target, the TCN ties Ridge — it does not beat it.
- Full-cohort controller replay (35 recorded trajectories, current 12-feature
  checkpoint): Fixed schedule — 45.01% alignment, 61.43% low-PAC stimulation, 28.59%
  high-PAC rest, PAC gap −6.55e-6. Reactive threshold — 64.49% alignment, 51.67%
  low-PAC stimulation, 77.30% high-PAC rest, PAC gap +21.09e-6. TCN predictive — 62.23%
  alignment, 73.77% low-PAC stimulation, 50.68% high-PAC rest, PAC gap +21.02e-6.
  Alignment oracle — 100%/100%/100%, PAC gap +33.36e-6.
- Habituation split: 17 of 35 subjects (48.57%) show a declining PAC slope across
  stimulation blocks; paired t-test p = 0.542 — no significant net trend. This is a
  descriptive split only, not evidence that personalization "works."
- **Never** attribute the historical 73-feature-model numbers (72.1% alignment, 82.6%
  low-PAC targeting, 91% oracle-bound framing, "all 35 of 35 subjects benefit") to the
  current 12-feature, 27,139-parameter checkpoint. Those numbers belong to a different,
  larger (31,043-parameter) model and a different results file.

**Fill-in-the-blank scaffold:**

> Static model ceiling: `[R² value, what converging on it across architectures tells
you]`.
> Feature ablation: `[all four numbers, in order, with the shuffle-control as evidence
the result is signal not noise]`.
> Five-seed check: `[mean, range, what this adds beyond the single seed]`.
> Target-definition stress test: `[both target definitions' numbers, and the honest
statement that the TCN's edge collapses to tied-with-Ridge under the realistic
target]`.
> Controller replay: `[all four policies' alignment/low-PAC/high-PAC numbers, framed as
a tradeoff — TCN improves X but reduces Y, and its balanced alignment sits below
reactive]`.
> Habituation: `[the descriptive split and p-value, without claiming it validates
anything]`.

---

## 6. Discussion

**Length target:** roughly 2–3 pages.

**Judging emphasis:** this is where "consistent with" language matters most — judges are
watching for the line between what you measured and what you're inferring.

**Questions to answer, in order:**

1. What do you think the ablation result actually means — why might spectral features
   fail to generalize across subjects? State this as a hypothesis, not a fact.
2. What does the controller tradeoff suggest about how a real system would need to be
   tuned before it could be tested further?
3. What does the stress test tell you about how much of your headline number depends on
   label granularity — and what would a better label look like?
4. What are the real, specific limitations — not generic ones — and what do they threaten
   about your central claim?
5. How does this connect back to the clinical motivation from your introduction, and
   where exactly is the line between what you've shown and clinical relevance?

**Vetted facts / framing to draw from:**

- The spectral-feature failure is _consistent with_ those features encoding subject-
  specific anatomy that doesn't transfer across people — this is a hypothesis the
  ablation supports, not a proven mechanism. Say it that way explicitly.
- The controller tradeoff (better low-PAC coverage, worse high-PAC specificity, alignment
  below reactive) is a targeting calibration problem, not evidence the predictive
  approach is wrong in principle.
- The target-definition stress test is arguably the single most scientifically honest
  result in the whole project — naming it plainly, with its number, is a strength, not a
  weakness to bury.
- The three metric sources (forecasting study, stress test, controller replay) come from
  distinct generation paths and should not be pooled or averaged into one number.
- Boundary language to state explicitly somewhere in this section, in your own words:
  this is a retrospective, offline replay against recorded PAC trajectories; it does not
  estimate how the brain would have physiologically responded to a different stimulation
  decision; PAC labels are complete-event summaries assigned back to constituent windows,
  which limits event-level granularity and online availability of the label in a real
  system; this project makes no claim of clinical efficacy, disease modification, or
  prospective deployment.

**Fill-in-the-blank scaffold:**

> `[Your interpretation of the ablation, marked clearly as interpretation: "consistent
with," not "proves"]`.
> `[What the controller tradeoff suggests needs tuning before further testing]`.
> `[What the stress test tells you about label dependency, and what a better label would
need]`.
> `[The specific limitation that most threatens your central claim, named plainly]`.
> `[The explicit clinical-relevance boundary, in your own words]`.

---

## 7. Conclusion

**Length target:** half a page to one page. Short, and it should say something new — not
just repeat the abstract.

**Judging emphasis:** a conclusion that only summarizes reads as weaker than one that
names what changed and what you'd do next.

**Questions to answer, in order:**

1. What is the one thing you now believe that you didn't believe (or hadn't shown) before
   this project?
2. What's the next concrete question this raises — not a vague "more research needed,"
   but the actual next experiment you'd run?
3. What's the honest, one-sentence summary of what this does and doesn't show?

**Fill-in-the-blank scaffold:**

> `[The one belief that changed or was newly established]`.
> `[The specific next experiment — e.g., a better leakage-free label definition, a
controller re-tuned on the tradeoff, replication of the single-seed stress test]`.
> `[One sentence bounding the work — retrospective replay, not clinical validation]`.

---

## 8. References

**Length target:** as many as needed, no padding — every entry must be one you've
personally verified.

**Rule:** open every DOI yourself and confirm it resolves to the actual paper you mean,
with the right authors, journal, and year, and that it supports the specific sentence
citing it (not just an adjacent, similar-sounding claim). You have already done this
verification pass once for the poster references — re-open each one again for the report
rather than trusting a cached list, since venues that certify sole authorship also expect
you to personally stand behind every citation.

**Known correction to apply:** the reference sometimes attributed to "Fortunato et al.
2023, Frontiers in Neuroscience" is misattributed — the real paper is Sahu, P.P. &
Tseng, P. (2023), _Frontiers in Integrative Neuroscience_ 17:1146687, DOI
10.3389/fnint.2023.1146687. Use the correct author/journal if you cite this source.

**No external links in the body** — STS Research Reports may not include clickable
links; format this as a plain numbered or author-year reference list only.

---

## 9. Application essays (outside the Research Report itself, same authorship rule)

STS's application includes separate essay questions about you and your activities. These
are just as much your own composition as the report. A few prompts worth pre-thinking in
your own words (check the current smapply.org portal for the exact questions when it
opens, since essay prompts can be refined year to year):

1. What is the story of how you got into this project — not the polished version, the
   real one (why EEG, why your grandmother, why this specific angle)?
2. What is a moment you were wrong, and what did you do about it?
3. How would you describe your own role versus any outside help, precisely and honestly?
4. What do you want to do next, and why does this project point you there?

Answer these for yourself in plain notes before the portal opens — you'll have the
material ready and won't be starting cold in November.

---

## 10. Final reminders

- The signed Ethics Statement covers the Research Report _and_ your essay answers — both
  must be entirely your own words.
- Every mentor-adjacent field (recommenders, any acknowledgment of informal help) stays
  `[AUTHOR TO CONFIRM]` in your own notes until you have real names, institutions, dates,
  and consent — never let a recommender or a sentence imply institutional endorsement
  that doesn't exist. Your own high school affiliation (Valley Christian HS) is
  legitimate self-attribution and needs no confirmation.
- Before you submit, run the whole report against the self-check rubric in
  `WRITE_IN_YOUR_OWN_VOICE.md`.
