# MIT URTC Submission-Readiness Audit

**Audited:** 2026-05-31  
**Artifact reviewed:** revised [`MANUSCRIPT.md`](MANUSCRIPT.md), generated Word manuscript, PDF proof, latest poster PDFs, repository evidence, and archived experimental artifacts  
**Decision standard:** competitive MIT URTC paper submission by a high-school author

## Direct Verdict

The revised manuscript is rigorous enough to submit as a competitive MIT URTC paper if the
high-school eligibility requirement is satisfied. Acceptance is not predictable, but the paper now
has a defensible and distinctive contribution: it stress-tests an apparently strong retrospective
forecasting pipeline and shows exactly where its conclusion weakens as PAC labels move closer to
online availability.

The original headline result (`R-squared = 0.606`) comes from PAC values computed over complete 20-40
second event periods and assigned back to their constituent two-second windows. For an early window,
the assigned current-PAC feature includes signal samples acquired later in the same event period.
The revised paper no longer treats that result as evidence for a streaming forecaster.

The archived experiment in
[`archive/experimental/sliding_pac`](../../../../archive/experimental/sliding_pac) computes PAC from a
five-second backward-looking window. The revised manuscript now reports this stress test directly.
In the more meaningful task:

| Model | Epoch-summary PAC target | Backward-looking sliding PAC target |
|---|---:|---:|
| Persistence | 0.104 | -0.897 |
| Ridge | 0.260 | **0.216** |
| TCN | **0.554** | 0.212 |

The TCN remains positively predictive on the harder target, but it no longer outperforms Ridge. This
is scientifically useful. The paper's contribution is now the target-definition audit, compact
feature-design result, and disciplined separation of retrospective replay from live validation.

## Poster-Informed Re-Audit

The April poster PDFs were visually inspected in depth:

- [`submission/poster/vfinal_poster.pdf`](../../../../submission/poster/vfinal_poster.pdf)
- [`archive/CSEF_Old/Poster_FINAL/CSEF_FINAL.pdf`](../../../../archive/CSEF_Old/Poster_FINAL/CSEF_FINAL.pdf)

The posters reveal a broader engineering arc: raw-EEG PAC estimation, temporal feature selection,
forecasting, controller replay, and a future streaming path. That system-level story is impressive.
The revised manuscript now states that a broader raw-EEG prototype exists while keeping its validated
scope narrow.

Several poster claims were intentionally not imported:

- `72.1%` alignment and `82.6%` low-PAC targeting came from the older 73-feature replay, not the final
  12-feature checkpoint.
- Fatigue-model results used a trend-based adaptive heuristic, not the TCN.
- Consumer-hardware latency and a complete EEGNet-to-TCN-to-controller loop were not validated
  end-to-end by the manuscript experiments.
- The source cohort includes multiple clinical classifications; it should not be described as 35
  dementia patients.

## MIT URTC Standard

The current public MIT URTC pages still expose 2025 guidance as the latest posted baseline. MIT says
that submissions are evaluated for originality, quality of content, and adherence to conference
themes. Papers are reviewed by faculty, graduate students, and industry professionals. The posted
guidance permits up to five single-spaced pages with a minimum 10-point font.

This project fits URTC's technology themes through signal processing, temporal modeling, and medical
technology. The scientific question is interesting enough for URTC. The issue is whether the evidence
supports the paper's central framing.

Official sources checked:

- <https://urtc.mit.edu/submission>
- <https://urtc.mit.edu/faq>
- <https://urtc.mit.edu/paper_submission_2025.pdf>

## High-School Eligibility Gate

Paper-submission eligibility is unresolved from the manuscript. MIT states that a high-school paper
author must be associated with an undergraduate program, such as an official faculty-mentored
program, informal university-faculty mentorship, or substantial collaboration with an undergraduate
or graduate student. AP, IB, or a high-school-only affiliation is not sufficient.

The manuscript currently lists only Valley Christian High School. Before preparing a paper
submission, confirm the qualifying university connection and state the appropriate affiliation or
acknowledgment accurately. Without that connection, MIT's public FAQ directs high-school authors
toward a poster or lightning talk instead of a paper presentation.

## Reviewer Scorecard

| Dimension | Assessment | Rationale |
|---|---|---|
| Originality and theme fit | Strong | The combination of PAC forecasting, cross-participant evaluation, and controller replay is relevant and ambitious. |
| Writing and polish | Strong | The manuscript is concise, bounded, professional, and free of inflated clinical claims. |
| Reference hygiene | Strong | The six citations are primary or appropriate sources, and the dataset is formally cited. |
| Participant-split hygiene | Strong | The stored dataset uses disjoint 24/5/6 participant splits and train-only normalization. |
| Central forecasting rigor | Strongly bounded | The revised paper reports both the event-summary benchmark and the backward-looking PAC stress test instead of hiding the availability limitation. |
| Causal-model evidence | Preliminary but useful | The backward-looking PAC experiment retains positive held-out signal, but its TCN is approximately tied with Ridge and needs replication. |
| Controller evidence | Bounded but preliminary | Replay is diagnostic only, uses all 35 trajectories, uses nominal recorded context, and does not model physiological response to counterfactual actions. |
| Statistical robustness | Partial | Five seeds address initialization variance, not participant-split sensitivity. A single held-out split is too narrow for a strong generalization claim. |
| Presentation | Strong | The four-page proof is clean, within the limit, and includes a compact figure explaining the target-definition stress test. |
| Paper eligibility | Unresolved | The required university relationship is not visible in the paper. |

## Remaining Gates and Next Experiments

### 1. Confirm paper-track eligibility

The qualifying university connection remains the only administrative stop-ship issue. State the
relationship accurately in the submission metadata and manuscript acknowledgment if it exists.

### 2. Continue the live-available PAC benchmark

The archived sliding-PAC result should become the starting point, not an appendix-level caveat. A
submission-strength analysis should compare several backward-looking PAC context windows, such as
five, eight, and ten seconds, and should use a genuinely streaming-compatible filter implementation.

The archived experiment uses backward-bounded input segments, so it avoids future samples beyond the
prediction timestamp. However, it computes each segment with `filtfilt`, a zero-phase offline filter.
That is not itself a production streaming estimator. The paper should separate:

1. offline causal-bounded benchmark construction;
2. streaming estimator implementation;
3. model comparison on the same live-available target.

### 3. Report whether a nonlinear model adds value

On the existing sliding-PAC experiment, Ridge (`R-squared = 0.216`) slightly exceeds the TCN
(`R-squared = 0.212`). That is a legitimate result. It does not support a claim that the TCN is
necessary. Retrain and compare persistence, Ridge, and TCN under the corrected target definition.
Select the simplest model supported by the evidence.

### 4. Measure participant-split sensitivity

The current five-seed study varies model initialization while holding the six-person test split
fixed. Add grouped cross-validation or repeated participant-level splits. Report the distribution of
test performance across held-out participants and splits.

### 5. Add transition-specific evaluation

The epoch-summary target repeats within event periods, and `82.2%` of five-step pairs have identical
current and target PAC. Report model performance specifically where PAC or stimulation state changes.
The repository contains a transition-analysis starting point, but the primary paper does not yet
report a transition-specific TCN comparison for its selected checkpoint.

### 6. Keep replay subordinate to forecasting validation

The replay is useful only as an engineering diagnostic. The predictive policy increases low-PAC
targeting but reduces high-PAC rest specificity and lowers balanced alignment from `64.5%` to `62.2%`
relative to the reactive baseline. Retain this as an honest negative or mixed result. Do not frame it
as evidence that a predictive controller improves stimulation.

## Strong Recommended Improvements

1. Run an independent raw-to-results rebuild and retain machine-readable provenance for the final
   tables.
2. Add one compact figure showing the distinction between complete-event retrospective PAC,
   backward-looking PAC, temporal forecasting, and offline replay.
3. Replace the current headline with the strongest result that survives the corrected target
   definition.
4. State explicitly that stimulation-context features may encode the recorded schedule. Separate
   schedule prediction from biomarker prediction with component ablations.
5. Confirm MIT's Fall 2026 template when posted. The current linked Word template and the older
   guideline PDF do not agree on first-page structure.

## What Is Already Working

The manuscript has several qualities worth preserving:

- It distinguishes held-out forecasting from all-trajectory replay.
- It reports the controller tradeoff instead of hiding the weaker balanced-alignment result.
- It discloses the complete-event PAC limitation directly.
- It avoids therapeutic-efficacy claims.
- It uses participant-level splits and train-only normalization.
- It is concise, readable, and within the currently posted page limit.

## Recommended Submission Position

Submit the revised paper as a paper-track entry if the high-school eligibility requirement is
satisfied. Position it as an honest retrospective systems study that identifies why an apparently
strong forecast weakens under a more realistic target definition. Do not position it as a validated
closed-loop therapy or a deployable nonlinear controller.

MIT does not publish acceptance rates, so an admission probability cannot be estimated responsibly.
