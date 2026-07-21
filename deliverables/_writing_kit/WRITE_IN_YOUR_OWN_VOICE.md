# Write in your own voice — shared primer for every RED venue

Read this once before you draft anything for STS, JSHS, Synopsys, BMES, AAN, AISES,
SCCUR, BCI Award/Meeting, Sigma Xi, or SfN. It's short on purpose — the goal is to remind
you of habits you already have, not to hand you new ones.

## 1. The voice you're aiming for is already yours

You write in first person, plainly, from process. You open from something real (your
grandmother), you explain mechanisms with an everyday comparison before naming the
technical term, and you're comfortable saying what you got wrong. You undersell a number
and then argue why it matters instead of inflating the adjective in front of it. None of
that needs to be invented for a submission — it needs to be _kept_ under deadline pressure,
which is exactly when it's tempting to reach for stock academic phrasing instead.

**Moves that are genuinely yours — reuse the pattern, not the exact words:**

- **Personal-stake opening.** Grounding the "why" in your grandmother's condition, stated
  calmly, not dramatically.
- **Analogy before jargon.** Explain the mechanism in plain terms first, _then_ name the
  technical term. `ILLUSTRATIVE ONLY — rewrite in your own words:` describing habituation
  as tuning out a sound you've stopped noticing, before the word "habituation" shows up.
- **Reactive vs. predictive** as the core framing of why forecasting matters at all —
  anticipating a drop instead of only responding after it happens.
- **Honest-number move.** Name the real number, including when it's modest or mixed, then
  argue the margin. Not "strong performance" — the actual R² next to what it's being
  compared to.
- **Process-as-evidence.** The story of noticing something in the data, or catching your
  own mistake (like the earlier feature-leakage discovery), is not a confession to
  minimize — it's some of your strongest material for a judge who wants to see how you
  think.
- **The ceiling insight.** When several different approaches converge on the same number,
  that convergence is itself a finding — it says something about the data, not the model.
- **Causal-guarantee as design.** A model that can only look backward in time isn't a
  training accident — it's an architectural choice you made, and you can say why.
- **Independence statement.** You wrote the code, you made the design decisions, and any
  AI tool use in your _process_ was a learning aid, not a co-author — say this plainly
  wherever a venue asks about outside assistance.

## 2. Do / don't

| Do                                                                                                                                                        | Don't                                                                                                                 |
| --------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Lead a results sentence with the actual number, then interpret it                                                                                         | Open with an adjective ("robust," "strong") and let the number trail behind, or omit it                               |
| Report the controller replay as a tradeoff (better low-PAC coverage, worse high-PAC specificity, alignment below reactive)                                | Call the controller result a win, or bury the alignment shortfall                                                     |
| Say "consistent with" when you're explaining a possible mechanism you haven't proven (e.g., why spectral features might not generalize)                   | State a hypothesis as if it were a demonstrated fact                                                                  |
| Name the specific threat to a claim (event-summary PAC labels collapsing the leakage-free target to ~Ridge level)                                         | Write a generic limitations sentence ("further work is needed," "sample size was limited") and stop there             |
| Use plain, mechanistic words you already reach for: synchronize, lock on, entrain, habituate, margin, lead time, ceiling, forecast, sanity check, leakage | Reach for elevated filler: delve, underscore, showcase, leverage, harness, robust, meticulous, comprehensive, pivotal |
| Vary sentence length on purpose — a longer explanatory sentence, then a short blunt one                                                                   | Write every sentence to roughly the same length and rhythm                                                            |
| State the retrospective-replay boundary explicitly, early, in your own words                                                                              | Let a reader assume this is a live clinical test, or wait for them to ask before admitting it isn't                   |
| Keep every draft and dated note as your own authorship record                                                                                             | Discard drafts once you're happy with a version                                                                       |

## 3. Final self-check rubric

Before you consider a section done, read it out loud and check:

1. **Does it sound like you said it, not like it was written about you?** If you read it
   aloud and it doesn't sound like something you'd actually say to a person, rewrite it.
2. **Is there at least one detail only you could know** — a decision, a mistake, a moment
   you changed your mind — somewhere in this section?
3. **Does every results claim carry a specific number, not just an adjective?** If you
   removed all the adjectives, would the sentence still make its point on the number
   alone?
4. **Is the real limitation named**, the specific one that actually threatens the claim —
   not a generic hedge?
5. **Are observation and interpretation visibly separate?** Can a reader tell which
   sentences are "this is what the data showed" versus "this is what I think it means"?
6. **Sentence rhythm check:** read it aloud. Does it drone in even, medium-length,
   comma-balanced sentences? If so, break it up — a short blunt sentence after a longer
   one usually fixes it.
7. **Scan for elevated filler:** delve, underscore, showcase, intricate, pivotal,
   meticulous, comprehensive, robust, leverage, harness, realm, tapestry, testament,
   boast. If any appear more than once or twice, cut or replace with something plainer.
8. **Scan for formulaic glue:** two or more sentences/paragraphs in a row starting with
   Moreover / Furthermore / Additionally / Consequently; "it is important to note that."
   Replace with a real logical connector (but, so, because, yet) or just cut it.
9. **Does the number match the canonical source exactly** — no rounding, no mixing a
   feature-ablation number with a stress-test number, no attributing the old 73-feature
   controller numbers (72.1%/82.6%/91%/35-of-35) to the current 12-feature model?
10. **Does the conclusion say something new**, or does it only restate the abstract?
    A strong closing names what changed and what the next question is.
11. **Are you inside the hard claim boundary?** No clinical efficacy, no patient-outcome
    improvement, no disease-slowing, no prospective deployment, no live therapeutic
    validation, anywhere in the piece — including in the closing sentence, where
    over-claiming tends to creep in under deadline pressure.
12. **For STS/JSHS specifically: did you write every word yourself**, and if a form asks
    about outside assistance or tool use, have you answered it completely and honestly?

If a section fails more than one or two of these, it's worth a second pass before you
move on — not a sign to start over, just a sign it was drafted a little too fast.
