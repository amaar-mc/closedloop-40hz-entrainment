# MIT URTC Manuscript Editorial Review

**Reviewed:** 2026-05-31  
**Scope:** current MIT URTC web guidance, manuscript credibility, high-school positioning, and
submission-proof polish

## Official Review Context

MIT URTC's public site still exposes the 2025 cycle as its latest published submission baseline.
The active submission page says that reviewers consider originality, quality of content, and
adherence to conference themes. The FAQ says that faculty members, graduate students, and industry
professionals review submissions. The technical paper must remain within five single-spaced pages
with a minimum 10-point font.

For a high-school author, manuscript quality is not the only gate. The paper-presentation route
requires a university connection. The FAQ says that an official faculty-mentored research program,
informal mentorship by university faculty, or substantial collaboration with an undergraduate or
graduate student may qualify. AP, IB, and other college-level high-school programs do not qualify
by themselves. Without a qualifying connection, the available routes are poster presentation or
lightning talk. The homepage also states that minors must be accompanied by an adult throughout the
conference.

Official sources:

- <https://urtc.mit.edu/>
- <https://urtc.mit.edu/submission>
- <https://urtc.mit.edu/faq>
- <https://urtc.mit.edu/paper_submission_2025.pdf>
- <https://urtc.mit.edu/conference-template-letter.docx>

## Manuscript Assessment

### What Already Works

- The paper has a defensible technical center: cross-participant PAC forecasting with a compact
  temporally ordered feature set.
- It reports a mixed controller result rather than hiding it. That increases credibility.
- The methods expose participant-level splitting, train-only normalization, stored-series
  future-index ordering, and the repeated-label caveat.
- The paper separates the five-seed forecasting experiment from the separately retrained
  controller-integration checkpoint.
- The clinical boundary is clear: this is retrospective computation, not evidence of treatment
  efficacy.

### Changes Applied

- Reworked the title to foreground the verified contribution: cross-participant PAC forecasting
  for offline evaluation of adaptive auditory entrainment.
- Added a standalone OpenNeuro dataset citation for `ds005048` version `1.0.1`.
- Replaced generic or overly polished phrases with direct technical wording tied to the repository
  evidence.
- Rewrote the preprocessing paragraph to distinguish the source study's Makoto pipeline, the
  released-file metadata, and the repository's additional local conditioning stage.
- Clarified that controller replay uses all 35 trajectories across the full cohort. It is an
  integration diagnostic, not an extra held-out forecasting test.
- Clarified that replay stimulation-context features come from the nominal recorded protocol,
  rather than from counterfactual controller decisions.
- Tightened the abstract and conclusion while preserving the quantitative result and the negative
  controller finding.
- Replaced the visible abstract and keyword double-hyphen labels with colons.
- Clarified that complete-event PAC summaries are assigned back to constituent windows. The revised
  manuscript does not treat stored-series indexing as proof of online PAC-feature availability.
- Added the replay controller's warm-up, rolling-window, z-score, forecast-change, fallback, and
  minimum-hold settings.
- Changed the proof layout to follow the linked IEEE-style template opening: full-width
  title/author/abstract block, then two-column body text.

## Remaining Submission Gates

1. Confirm the author's qualifying university connection for the paper-presentation route.
2. Confirm adult accompaniment if the presenter will still be a minor.
3. Refresh the official site when Fall 2026 dates, tracks, portal details, and template are posted.
4. Resolve the current conflict between the 2025 guideline PDF's title-page language and the linked
   Word template before final submission.
5. Perform a final author ownership pass: read the paper aloud, verify that every technical sentence
   can be explained in a live question-and-answer session, and rewrite any sentence that does not
   sound like the author's normal technical voice.
