# Q&A prep: Lightning Talk ID-1269

Answer in one or two sentences, give the number, then stop. Every number here traces to
`results/metrics/early_late_connectivity_analysis.json` (paths in `research/claims_ledger.md`) or to
`data/raw/ds005048/participants.tsv`.

---

**"Isn't this just the auditory steady-state response, not entrainment?"**
It could be. I measured a stimulation-minus-silence difference in 40-Hz phase locking, and I don't claim
it proves entrainment. What I showed is that the size of that difference in the first two minutes tracks
its size a few minutes later.

**"There's no sham. How do you know the sound caused anything?"**
I don't. Silence always followed sound, so order and time effects aren't separated. That's the first
thing a prospective study should fix, with a sham or a counterbalanced order.

**"Did you pick cycles 4 and 5 after looking?"**
Yes, it was retrospective and not preregistered. Cycles 4–5 are the last pair every participant had
(8 people had only 5 complete cycles). They gave the highest r; the other five windows gave 0.61 to
0.77, all below p = 0.05 after Bonferroni correction.

**"Could volume conduction explain it?"**
I used frontal-minus-posterior bipolar signals and only paired signals that share no electrode. PLI and
weighted PLI, which ignore zero-lag coupling, gave r = 0.78 and 0.66. That lowers the concern; it
doesn't remove it.

**"Is 0.78 driven by a couple of people?"**
Spearman's rank correlation is 0.69. Dropping the two most extreme participants still leaves r = 0.70
(95% CI 0.42 to 0.86).

**"Why subtract silence instead of using raw PLV?"**
Across people, raw PLV in the first block correlated with the last three blocks at every frequency I
tested, r = 0.87 to 0.93, so raw PLV mostly describes the person. Subtracting each person's own silence
removes most of that, and the early-to-later link that remains is much stronger at 40 Hz than at the
six neighbors (0.78 versus at most 0.26).

**"Is it really specific to 40 Hz?"**
It was stronger at 40 Hz than at each of the six neighbors (r = 0.78 versus −0.10 to 0.26). Every
pairwise bootstrap interval excluded zero. With a Bonferroni correction the 39-Hz comparison just
touches zero, so I call it a consistent pattern rather than six separately significant tests.

**"Are these Alzheimer's patients?"**
It's a mixed memory-clinic cohort: 10 cognitively normal, 6 with mild cognitive impairment, 16 mild and
1 moderate Alzheimer's, and 2 whose diagnosis wasn't finalized. Ages 54 to 89.

**"Could the 40-Hz locking just be an artifact from the speakers?"**
I can't rule it out, which is why it's on my last slide. There was no speakers-on-but-silent control.
The sound's energy is near 5 kHz, and 40 Hz is only its on-off rhythm, but electrical pickup could
still reach the EEG, so a prospective study needs an artifact control.

**"Why is your example pair at 0.42 when silence averages about 0.48?"**
The example is one pair, picked as the median by its sound-minus-silence difference, not by level.
Averaged over all 200 pairs, that person was at 0.58 with sound and 0.35 in silence.

**"Why is 40-Hz PLV about 0.48 even in silence?"**
PLV can't reach zero in a finite, narrow-band window, and sources that reach both signals add to it.
That floor applies to sound and silence alike, which is why each cycle is compared with its own silence.

**"Why keep the two participants without a diagnosis?"**
The question is about each person's EEG over time, not diagnosis. Leaving them out gives r = 0.78
with 33 people, so it doesn't change the result.

**"Your title-slide example looks unusually clean."**
It is. That person is one of the stronger responders, and the caption says so. The group plot on
slide 3 and the scatter on slide 5 show everyone.

**"Could this run in real time?"**
Not yet. The public data were cleaned offline over whole recordings. My windows are filtered one at a
time, but that's not a streaming test. That's the next step.

**"Does a bigger response mean the treatment works?"**
Nobody knows yet, and this study can't say. Any link to clinical benefit is untested.

**"Could you use the early value to make a decision?"** *(only if asked)*
In an exploratory check, the early contrast ranked people by whether their later contrast was positive
(AUC 0.83). But a cutoff tested on held-out people was right only about 65% of the time, so it's a
candidate for a prospective test, not a rule.

**"Did AI help with this?"**
Answer consistently with the disclosure you filed with URTC
(`deliverables/venues/mit_urtc_poster_lightning/05_submission_ready/AI_USE_DISCLOSURE.md`).

---

Numbers not to say: 0.570 (a different bootstrap seed), 0.915 (the 8-person subgroup), anything from the
older PAC/TCN project (0.606, 0.212, 72.1%, 82.6%).
