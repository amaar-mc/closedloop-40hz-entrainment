# AI-Generated Writing: Tells, Causes, and How to Avoid Them

**A grounded guide for the submission campaign.** Every writing and editing pass (workflow gate **G6**)
runs a draft against this document before it advances. The goal is not to "beat detectors" — it is to
produce writing that is genuinely specific, honest, and human-voiced, because that is what wins at
competitive venues and what survives integrity review.

> **Why this matters here.** Several venues in this campaign (Regeneron STS, JSHS) explicitly prohibit
> AI-written report/abstract text and require disclosure of tool use. Others (IEEE, BMES, MIT URTC)
> care about scientific voice and originality. A draft that reads as machine-generated is a double
> risk: it can trip integrity rules _and_ it signals shallow thinking to reviewers. This guide is about
> writing that is defensibly the student's own — clear, specific, and grounded.

---

## 0. The one-paragraph version

AI text has a recognizable fingerprint: a small set of over-used "elevated" style words (delve,
underscore, intricate, pivotal, meticulous, showcase), formulaic transitions (Moreover / Furthermore /
Additionally chains, "It is important to note that"), uniform sentence rhythm, mechanical structural
symmetry, hollow summaries, over-hedging, and — most dangerous for research — **confidently fabricated
or mismatched citations.** These arise because language models optimize for the statistically
"expected" next word and are tuned toward smooth, agreeable, generic prose. The fix is not a thesaurus
swap; it is concreteness: real numbers, specific methods, a genuine argument with real limitations, and
citations you have personally verified.

---

## 1. Lexical tells (word-level)

The strongest empirical signal. Kobak et al. (2024, _Science Advances_) analyzed >15 million PubMed
abstracts (2010–2024) and found an abrupt post-ChatGPT surge in _style_ words — verbs and adjectives,
not content nouns — estimating that **at least 13.5% of 2024 biomedical abstracts were LLM-processed**,
reaching ~40% in some subcorpora. The tell is not any single word but the **density** of these words.

**High-risk "elevated" vocabulary** (over-represented in LLM prose; use sparingly and only when precise):

| Category     | Words to watch                                                                                                                                           |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Verbs        | delve (into), underscore, showcase, highlight, foster, leverage, harness, boast, garner, illuminate, facilitate, bolster, enhance, align with, emphasize |
| Adjectives   | intricate, pivotal, crucial, meticulous, comprehensive, robust, nuanced, seamless, notable, commendable, invaluable, vibrant, enduring                   |
| Nouns        | realm, landscape, tapestry, beacon, testament, interplay, cornerstone, insights, framework (as filler)                                                   |
| Intensifiers | significantly, remarkably, substantially, notably, arguably, undoubtedly                                                                                 |

**Era note (from Wikipedia's "Signs of AI writing"):** the specific words drift over time — "delve"
peaked in 2023–early-2024 and dropped sharply by 2025, while later models lean on "highlighting,"
"showcasing," "emphasizing," "enhance." Do not treat any fixed blacklist as complete; watch for the
_pattern_ (unearned elevation), not just the 2024 words.

**Punctuation tell:** the em-dash (—) is over-associated with AI when it appears frequently as an
all-purpose connector. Em-dashes are legitimate; the tell is over-reliance. Vary punctuation.

**Bad → better:**

- ❌ "This study delves into the intricate interplay of PAC features, underscoring their pivotal role."
- ✅ "We tested whether 12 PAC and stimulation-context features predict coupling 5 seconds ahead on
  held-out participants. They explained more variance than the 73-feature set (R² 0.558 vs −0.025)."

The fix wasn't removing "delve" — it was **replacing vague elevation with a specific claim and a number.**

---

## 2. Stylistic / rhythm tells

- **Formulaic transitions.** "Moreover," "Furthermore," "Additionally," "Consequently" opening
  consecutive sentences; "In today's fast-paced world"; "It is important to note that." These are glue
  words that stitch ideas in predictable ways (a widely noted 2025 tell).
- **Uniform sentence length and shape.** Human technical writing varies: a long methods sentence, then
  a short blunt result. AI prose tends toward even, medium-length, comma-balanced sentences.
- **Rule-of-three overuse.** "clear, concise, and compelling" — tricolons everywhere.
- **Over-hedging.** Stacking "may," "could," "might potentially," "it is possible that" so nothing is
  actually claimed. (Distinct from _honest_ calibrated uncertainty, which names the specific limitation.)
- **Promotional adjectives** on ordinary things: "groundbreaking," "powerful," "invaluable,"
  "cutting-edge." Research prose earns adjectives with evidence, or drops them.
- **Grandiose closing sentence.** ChatGPT tends to end with a sweeping comprehensive statement
  ("This work paves the way for a new era of…"). Reviewers read these as empty.

**Bad → better:**

- ❌ "Furthermore, our robust and comprehensive framework paves the way for transformative advances."
- ✅ "The controller improves low-PAC coverage but loses high-PAC rest specificity — a tradeoff that
  must be calibrated before any live test."

---

## 3. Structural tells

- **Mechanical symmetry.** Every section the same length; every paragraph exactly three sentences;
  parallel headings that look generated ("Firstly / In contrast / Moreover / To conclude").
- **Restating the prompt / question** as the opening sentence of each section.
- **Over-signposting.** "In this section, we will discuss…" then "As discussed above…" everywhere.
- **Listicle-ification.** Turning prose that should argue into bulleted lists of near-equal items with
  bolded lead-ins. (Lists are fine when the content is genuinely a list; the tell is defaulting to them.)
- **Conclusions that only summarize.** A strong conclusion advances a claim, states what changed, and
  names the next question — it does not just recap the abstract.

---

## 4. Content / epistemic tells (the ones that matter most for research)

- **Fabricated or mismatched citations — the single biggest integrity risk.** Walters & Wilder (2023,
  _Scientific Reports_) found **55% of GPT-3.5 and 18% of GPT-4 citations were fabricated**, and among
  _real_ citations, 43% (GPT-3.5) / 24% (GPT-4) had substantive errors. Fabricated references often
  look perfect — real author names, correctly formatted DOIs that resolve to an unrelated paper. **Every
  citation in every submission must be personally verified against the actual source.** This is
  non-negotiable and is checked at gate G3.
- **Over-generalization / lack of specifics.** Vague claims where a number, method, or concrete example
  belongs. "The model performed well" instead of "test R² = 0.558, above persistence (0.104)."
- **Vague attribution.** "Studies have shown…," "It is widely known that…" with no specific source.
- **Both-sides flattening.** Presenting a balanced-sounding non-answer instead of taking a defensible
  position and defending it.
- **Absence of a genuine limitation.** Real research states what it cannot conclude. AI drafts often
  either omit limitations or list generic ones. This project's honest limitations (event-summary PAC
  labels, single fixed split, offline replay ≠ physiology) are _assets_ — they show maturity.
- **Confident wrongness.** Plausible-sounding but incorrect technical statements. Verify every claim
  against `paper/data/key_results.md`.

---

## 5. Why these patterns arise (mechanisms)

Understanding the cause helps you edit at the root instead of chasing symptoms:

1. **Next-token probability smoothing.** Models pick high-probability continuations, which biases toward
   the most "expected," generic phrasing and the vocabulary that co-occurs with formal writing.
2. **RLHF toward agreeableness and polish.** Human-feedback tuning rewards fluent, hedged, non-committal,
   "helpful-sounding" prose — which produces smoothness and over-hedging.
3. **Training distribution.** Heavy exposure to a certain register (and to American academic English)
   makes the model reproduce that register's clichés at inflated rates.
4. **No grounded memory of sources.** The model generates citations that _look_ like the training
   distribution of citations rather than retrieving real ones — hence fabrication.
5. **No intrinsic sense of rhythm.** Lacking a reader's ear, models default to even sentence shapes and
   over-use the em-dash as a general connector.

The practical implication: **the cure is concreteness and genuine authorship**, not word-swapping. A
draft rewritten to include real numbers, specific methods, a real argument, and verified citations stops
reading as AI because it now contains information only the author could supply.

---

## 6. Detection reality — do NOT over-trust detector scores

AI-text detectors are **unreliable and biased**, and this cuts both ways for the applicant.

- **False positives are common and unfairly distributed.** A Stanford study (Liang et al., 2023,
  _Patterns_) found detectors were near-perfect on US-born 8th-grader essays but misclassified **61.3%
  of non-native (TOEFL) essays as AI-generated**; at least one detector flagged 97.8% of them. A later
  synthesis reported false-positive rates of 50–61% for non-native English writing vs <5% for native
  writers.
- **Consequences:** authentically human writing — especially by multilingual or atypical writers — gets
  flagged. Editors of English teaching journals have called detectors "ineffective, unreliable and
  harmful."
- **Implication for this campaign:**
  1. **Do not treat a low detector score as proof of quality, or a high score as proof of cheating.**
     Detectors are noisy signals, not verdicts.
  2. Write genuinely (real numbers, specific methods, verified citations) — that is what actually
     matters to reviewers and integrity panels.
  3. Do **not** "launder" text by paraphrasing to dodge a detector; that neither improves the writing
     nor satisfies venues that require genuine authorship. For STS/JSHS, the student must actually write
     the text and disclose tool use as required.
  4. If the student is a non-native English writer, know that detectors may false-flag their genuine
     work; keep drafts, notes, and version history as evidence of authorship.

---

## 7. QUICK RED-FLAG SCAN (5-minute pass before any submission)

Run this checklist against a draft. Each "yes" is a flag to fix.

**Vocabulary & rhythm**

- [ ] Does any of {delve, underscore, showcase, intricate, pivotal, meticulous, leverage, harness,
      realm, tapestry, testament, boast, comprehensive, robust} appear more than once or twice?
- [ ] Do ≥2 consecutive sentences (or paragraphs) start with Moreover / Furthermore / Additionally?
- [ ] Any "It is important to note that," "In today's world," "plays a pivotal role"?
- [ ] Are most sentences the same length? Is there no short, blunt sentence anywhere?
- [ ] Em-dashes on nearly every line?

**Substance**

- [ ] Any claim without a specific number, method, or example where one belongs?
- [ ] Any "studies have shown" / "it is well known" without a named source?
- [ ] Does every citation resolve to a real paper you have personally opened? (Check DOIs — a resolving
      DOI can still point to the wrong paper.)
- [ ] Does the piece state a real, specific limitation (not a generic one)?
- [ ] Does the conclusion say something new, or only summarize?

**Voice & integrity**

- [ ] Does it read like _this student_ wrote it (specific to their process, choices, setbacks)?
- [ ] For STS/JSHS: is this the student's own writing, with tool use disclosed as the rules require?
- [ ] Any promotional adjective ("groundbreaking," "transformative") not backed by evidence?
- [ ] Any claim outside the project's boundaries (therapy, clinical validation, deployment)? → cut it.

---

## 8. DO INSTEAD — positive practices

1. **Lead with specifics.** Numbers, method names, exact conditions. "test R² = 0.558 (five-seed mean
   0.606, range 0.558–0.647)" beats "strong performance."
2. **Vary sentence rhythm deliberately.** Follow a long, qualified sentence with a short declarative one.
   Read it aloud; if it drones, it will read as machine-smooth.
3. **Earn every transition.** Use "but," "so," "because," "yet" to signal real logical relationships,
   not "Moreover" as filler.
4. **State genuine limitations plainly.** They are the mark of a real scientist and are, for this
   project, the _core story_ (target-definition audit, event-summary labels, offline replay).
5. **Take a position.** Say what you conclude and why, then bound it. Reviewers reward a defensible
   argument over a hedged non-claim.
6. **Verify every citation by hand.** Open the paper. Confirm authors, year, venue, and that it actually
   supports the sentence citing it. Keep a reference-checking log.
7. **Cut elevated words that aren't precise.** If "utilize" can be "use," use "use." If an adjective
   isn't backed by evidence, delete it.
8. **Write from your own process.** What surprised you? What did you get wrong first? What did you change?
   Only the author knows this — and it is exactly what competitions like STS reward.
9. **Prefer plain, precise language.** Peer reviewers respect clarity, not ornamentation.
10. **Keep drafts and notes.** Version history is both good practice and evidence of genuine authorship
    if a detector false-flags the work.

---

## Sources

All real, retrieved for this guide. Verify before citing in any submission.

1. Kobak, D. et al. (2025). _Delving into LLM-assisted writing in biomedical publications through excess
   vocabulary._ Science Advances. https://www.science.org/doi/10.1126/sciadv.adt3813 (preprint:
   https://arxiv.org/abs/2406.07016) — ≥13.5% of 2024 PubMed abstracts LLM-processed; style-word surge.
2. Liang, W. et al. (2023). _GPT detectors are biased against non-native English writers._ Patterns
   (Cell Press). https://pmc.ncbi.nlm.nih.gov/articles/PMC10382961/ — 61.3% false-positive rate on TOEFL
   essays. Stanford HAI summary: https://hai.stanford.edu/news/ai-detectors-biased-against-non-native-english-writers
3. Walters, W. H. & Wilder, E. I. (2023). _Fabrication and errors in the bibliographic citations
   generated by ChatGPT._ Scientific Reports 13. https://www.nature.com/articles/s41598-023-41032-5 —
   55% (GPT-3.5) / 18% (GPT-4) fabricated citations; substantive errors in many real ones.
4. Wikipedia. _Signs of AI writing._ https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing —
   community-maintained catalog of LLM word/format conventions and their drift across model "eras."
5. Emerald, _English Teaching: Practice & Critique_ (2026). _AI writing detectors are ineffective,
   unreliable and harmful._ https://www.emerald.com/etpc/article/doi/10.1108/ETPC-07-2025-0155
6. MacDonald et al. (2024), reported in PsyPost. _ChatGPT hallucinates fake but plausible scientific
   citations._ https://www.psypost.org/chatgpt-hallucinates-fake-but-plausible-scientific-citations-at-a-staggering-rate-study-finds/ — 32.3% of 300 citations hallucinated; 6–60% by subfield.
7. Deakin University study (2025), reported in StudyFinds. GPT-4o fabricated ~1 in 5 citations; 56% of
   all citations fake or containing errors. https://studyfinds.org/chatgpts-hallucination-problem-fabricated-references/
8. The Markup (2023). _AI Detection Tools Falsely Accuse International Students of Cheating._
   https://themarkup.org/machine-learning/2023/08/14/ai-detection-tools-falsely-accuse-international-students-of-cheating

_Note on figures:_ citation-fabrication rates vary widely by study, model version, and topic (roughly
18–55%+ across GPT-3.5/GPT-4 studies). The specific percentages are less important than the settled
conclusion: **AI-generated citations are frequently fabricated or mismatched and must be verified by
hand.**
