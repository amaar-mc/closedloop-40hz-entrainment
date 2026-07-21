# QUESTION_BASED_OUTLINE.md — AAN Neuroscience Research Prize

**How to use this file:** this is not a template to fill in with generic phrases — it is a list of questions. Answer each one **in your own words**, out loud or in a first draft, before you try to make it sound polished. The facts and numbers you need for each section are listed under it, drawn from `EVIDENCE_PACKET.md` — go pull the exact number from there, don't retype from memory. **No sentence in this file is meant to be copied into your application.** Where an example fragment is shown, it is marked ILLUSTRATIVE ONLY and is a fragment, not a sentence — rewrite it in your own words.

Reminder: AAN's Round 1 is **abstract-only**. Whatever you write in the abstract has to stand completely on its own — don't assume the full-round judges will "get to" your best material later, because many won't see it at all if the abstract doesn't advance.

---

## Section 1 — Abstract (≤300 words, Round 1 screening — the most important section in this application)

1. **Why this problem, and why you?** What is your personal connection to this project, and how do you want to state it — briefly, factually, without over-dramatizing? (Your voice guide calls this the "personal-stake opening" — calm, not dramatic, then straight into the science.)
2. **What is the actual neuroscience question?** In one sentence: what brain measure are you studying (name it precisely — phase-amplitude coupling, theta-gamma), and what open question in 40 Hz gamma-stimulation research does your project address? Don't lead with "machine learning" — lead with the brain.
3. **What did you build, in the fewest words that are still accurate?** Two stages: (a) a small network that reads raw EEG and estimates PAC, and (b) a network that forecasts PAC several seconds ahead and feeds a stimulation controller. Can you say this in two sentences without jargon-stacking?
4. **What is the one number a neurologist-reviewer should remember from your abstract?** Is it the feature-ablation result (§4 of the evidence packet), the honest target-definition stress test (§6), or the mixed controller result (§7)? You have to pick — the abstract can't carry all three with equal weight. Which one is _your_ strongest, most defensible claim?
5. **Where do you state the non-clinical boundary?** Given this is a clinical-neurology judge pool, where in your 300 words does the sentence "this is retrospective/offline replay, not clinical validation" go — first paragraph, or last? Why?
6. **What is the one honest limitation you name, even in a 300-word abstract?** You don't have room for all of them — which single limitation is both true and most relevant to a first-round reviewer skimming quickly?

## Section 2 — Introduction / Background (full report)

1. What does the existing 40 Hz gamma-stimulation literature actually show, in your own words, and what does it _not_ yet answer? (Use evidence packet §1 for the two mouse studies and the human dataset provenance study — but explain the gap yourself, don't just list the citations.)
2. Why does a _fixed_ stimulation schedule have a real limitation, mechanistically? Can you explain in your own analogy (your voice guide likes analogy-before-jargon) why brain state might drift within or across sessions in a way a fixed on/off timer can't track?
3. What is your research question, stated as a question a neurologist would recognize as answerable with data (not just "can AI help with dementia")?

## Section 3 — Methods (full report)

1. What is the dataset, in enough detail that a reviewer could evaluate whether your conclusions are appropriately scoped to it? (Cohort size, channels used vs. recorded, sampling rate, subject-level split — evidence packet §2.)
2. Why does the split have to be subject-level, and what would go wrong scientifically if it weren't? (This is a "did you actually think about validity" question — answer it in terms of what you'd be fooling yourself about, not just "to avoid leakage.")
3. How exactly is PAC computed, and why does its definition (event-summary vs. window-level) matter for what you claim later? (Set this up here so §6 of your results lands without needing new explanation.)
4. What are your two model stages _for_, separately? Why not just one model that goes straight from raw EEG to a stimulation decision?
5. What does "causal" mean for your forecasting network, and why is it an architectural property rather than something you just have to remember to enforce in training? (Your own phrase for this — "architectural guarantee, not just a training rule" — is worth keeping in your own words.)

## Section 4 — Results (full report — this is where the honest-numbers discipline matters most)

1. **Static PAC estimation.** What R² did you get, and why do you present it as a ceiling rather than a disappointment? What evidence do you have that it's a data ceiling and not just "your model wasn't good enough"? (Evidence packet §3 — the multi-architecture convergence.)
2. **Feature ablation — your main finding.** Walk through the four numbers (61-feature, 73-feature, 7-feature, 12-feature) in order. What does the _pattern_ across these four numbers tell you, that any single number wouldn't? What's your own explanation for why fewer, more targeted features generalized better — and can you state that explanation as a hypothesis rather than a proven fact?
3. **Horizon behavior.** At what horizon does persistence (just guessing "no change") stop being a fair baseline, and why does that matter for whether your forecasting result is scientifically meaningful?
4. **The target-definition stress test.** This is the section your evidence packet calls the strongest evidence of rigor in the whole project — why? What would it have meant if you had _not_ run this check and just reported 0.606? What does it mean that Ridge and the TCN come out roughly tied under the realistic target? Can you explain, in your own words, why an event-summary label makes forecasting look artificially easy?
5. **Controller replay.** Define alignment, sensitivity (low-PAC stimulation), and specificity (high-PAC rest) for a reader who has never seen these terms in this context. Then: is your controller a win, a loss, or a tradeoff? Defend your answer with the actual numbers, not an adjective.

## Section 5 — Discussion / Interpretation of Data (full report — maps directly onto the AAN "Interpretation of Data" rubric criterion)

1. What is the single potential pitfall of your methodology that you think a careful reviewer would raise first — and have you already addressed it? (This is literally the rubric language: "potential pitfalls of the methodology or interpretation have been addressed.")
2. Given the mixed controller result, what would you want to try next, specifically — not "more data" in the abstract sense, but a concrete next experiment?
3. What can this work _not_ tell us, that a clinical audience might be tempted to assume it can? Write the sentence that closes that door explicitly.
4. Is there a clean way to state what would need to be true — what evidence, what study design — before this approach could ever be tested as an actual live intervention? (This shows scientific maturity without promising anything.)

## Section 6 — Conclusion (full report)

1. What's the one thing you learned from this project that you didn't expect going in? (Not a recap of results — a genuine surprise or pivot, per your voice guide's "process-as-evidence" habit.)
2. What is the smallest, most honest one-sentence summary of what you found — not what you hoped to find?
3. What's the next question this work raises that you'd want to chase, if you kept working on it?

## Section 7 — Independence / process statement (if the application asks for one, or if you want to include one)

1. How do you want to describe your use of AI tools in developing this project, accurately and specifically? (Your existing framing — "similar to using a textbook or asking a professor," used as a learning resource, all code/design/judgment calls your own — evidence packet does not cover this; pull your own accurate statement from your prior CSEF materials and update it for the current pipeline.)
2. Is there anything about your process (a mistake you caught, a pivot you made) that belongs in this statement as evidence of genuine, independent authorship?

---

**Illustrative fragment only (rewrite in your own words — this is a scaffold shape, not a sentence to reuse):**

> "State the neuroscience question in one sentence: \_**\_. State the honest headline number, with its boundary, in one sentence: \_\_**. State the non-clinical limitation in one sentence: \_\_\_\_."

Do not submit any sentence from this file. Every section above should be written cold, by you, from the questions and the facts — not edited from a draft someone else produced.
