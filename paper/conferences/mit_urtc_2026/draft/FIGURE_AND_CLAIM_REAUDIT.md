# Figure and Claim Re-Audit

**Updated:** 2026-06-25

## Audit Setup

Four independent review passes were used for this revision:

- Figure rigor: checked whether plotted values are sourced, visually interpretable, and honest about uncertainty.
- Numeric trace: re-checked reported metrics against repository artifacts.
- EEG/PAC domain review: challenged physiological wording, artifact risks, and online-availability claims.
- MIT URTC framing review: checked whether the manuscript presents a strong undergraduate-conference contribution without overstating.

## Changes Made

- The stress-test figure now loads bar values directly from
  `archive/experimental/sliding_pac/results/comparison_results.json` instead of hard-coding them.
- The figure explicitly labels the result as a single-seed fixed-split point estimate and states
  `n_test=2,678` with no confidence intervals.
- The manuscript removed the checkpoint-level `R^2 = 0.5844` claim from the main text. The validation
  command prints that checkpoint metadata value, but the paper now reports only the 27,139-parameter
  architecture for the integrated checkpoint so separate generation paths are not collapsed.
- The abstract now states the replay result plainly: forecast-driven decisions stimulate more
  below-median PAC periods but spare fewer above-median PAC periods than a reactive rule.
- PAC language was tightened to define phase-amplitude coupling directly as the dependence of
  `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase, not definitive endogenous coupling or
  therapeutic response.
- The limitations now explicitly state that the `38-42 Hz` amplitude band overlaps the auditory
  stimulation frequency, so estimates may reflect stimulation-locked response or residual artifact.
- Table I is labeled as an original exploratory single-seed ablation.
- The horizon-sweep table was removed because it was a secondary single-seed result under the weaker
  event-summary target definition.
- The benchmark table was removed because it duplicated Figure 1; the exact values remain in the
  result paragraph and figure.
- The figure's internal source filename was replaced with a reader-facing sample-size and uncertainty
  note, and the figure/caption pair is now kept on one page.

## Verdict

The manuscript is substantially more rigorous after this pass. Its strongest claim is no longer
"TCN beats baselines"; the stronger and more defensible contribution is that a high-performing
event-summary PAC forecasting result changes materially when the PAC target is recomputed under a
stricter information boundary. That is a sharper research contribution for MIT URTC because it
shows methodological self-audit, not just model fitting.

Residual risk remains: the work is retrospective, uses one fixed participant split, and does not
validate physiological PAC or a live controller. Those limits are now explicit. Given the current
evidence, the submission reads as a rigorous computational methods paper with a credible chance if
MIT URTC accepts high-school-authored submissions under its student-authorship rules.
