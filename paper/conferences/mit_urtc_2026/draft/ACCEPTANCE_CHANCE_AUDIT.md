# MIT URTC Acceptance-Chance Audit

**Audited:** 2026-05-31  
**Updated:** 2026-06-23  
**Scope:** current manuscript, generated DOCX and PDF proof, repository evidence, poster artifacts,
current public MIT URTC materials, IEEE Boston's 2025 call for submissions, the official 2025
technical-paper schedule, and an independent report from _The Tech_

## Direct Verdict

Under the facts currently documented in the repository, the paper track is not yet available: the
project materials state that the work was conducted independently with no institutional lab or
university mentor. MIT URTC's published high-school paper rule requires a genuine qualifying
university relationship. That is an administrative stop, not a manuscript-quality issue.

If the stored information is incomplete and the author genuinely satisfies the high-school
paper-presentation rule, this manuscript has a good shot at technical-paper acceptance. It is
competitive, not guaranteed. It is substantially stronger as an honest retrospective systems paper
than as a claim of a validated closed-loop therapy. It is not yet a strong best-paper candidate
because the closer-to-online benchmark is single-seed, uses one participant split, and does not show
a nonlinear advantage over Ridge regression.

## External Standard

### Official MIT URTC submission criteria

The currently published URTC submission page still exposes 2025 dates. It states that:

- technical papers are evaluated for originality, quality of content, and adherence to conference
  themes;
- reviewers include faculty members, graduate students, and industry professionals;
- papers may be included in IEEE Xplore if accepted and presented; and
- technical papers must be no longer than five single-spaced pages with a minimum 10-point font.

The public FAQ states that high-school students may submit paper presentations when they are
affiliated with an undergraduate program, informally mentored by university faculty, or working
directly and substantially with undergraduate or graduate students. AP, IB, and other
high-school-only college-level programs do not qualify by themselves.

### IEEE Boston call for submissions

IEEE Boston's 2025 call for submissions describes URTC as a venue for school projects, research,
innovations, or case studies that advance technology for humanity. It confirms peer review and the
five-page, 10-point technical-paper format. This manuscript fits that applied student-research
standard.

### Independent acceptance context

An October 30, 2025 report in _The Tech_ states that URTC received 319 submissions and accepted 189
in 2025, approximately 59%. That figure is conference-wide, not a published paper-track acceptance
rate, so it should not be treated as a probability for this manuscript. It does establish that URTC
is selective but not a low-single-digit admissions lottery.

### Recent accepted-paper comparison

The official 2025 technical-paper schedule includes work in adjacent areas:

- `Hybrid EEG Biomarker Fusing Riemannian Geometry and Spectral features for Dementia Diagnosis and
Severity Assessment`, presented by a high-school student;
- `End-to-End Hyperbolic Graph Neural Networks for Brain Age Prediction with MEG Data`;
- `Predicting Joint Torque from Spike Trains`; and
- `Improving Brain State Classification using Physics-Informed Convolutional Neural Networks`.

The present manuscript belongs in that technical neighborhood. Its differentiator is not merely the
use of a neural network. It is the decision to audit target construction, quantify a failure mode,
and narrow the engineering claim when the harder benchmark changes the model-selection result.

## Manuscript Audit

### What is strong

| Dimension                   | Assessment       | Evidence                                                                                                                                                                                  |
| --------------------------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Theme fit                   | Strong           | EEG signal processing, temporal forecasting, machine learning, neural networks, sensing, and medical technology fit URTC's published fields.                                              |
| Originality                 | Strong for URTC  | The paper studies PAC forecasting for adaptive 40 Hz auditory entrainment and foregrounds the information-boundary audit.                                                                 |
| Claim discipline            | Strong           | The manuscript distinguishes retrospective stored-series forecasting, bounded PAC stress testing, and offline replay from streaming deployment or therapeutic efficacy.                   |
| Data-split hygiene          | Strong           | The stored benchmark uses disjoint 24/5/6 participant splits and train-only normalization.                                                                                                |
| Reference hygiene           | Strong           | Eight concise references resolve to primary or appropriate sources, including the versioned OpenNeuro dataset and EEG/PAC caveat sources.                                                 |
| Presentation                | Re-export needed | The current DOCX uses MIT's linked template with 10-point-or-larger manuscript text, two tables, and one figure. The Word PDF must be regenerated after the 2026-06-25 abstract revision. |
| High-school differentiation | Strong           | Independent construction of the pipeline and the self-critical audit are impressive for the author's stage.                                                                               |

### What reviewers may challenge

| Risk                                                                                     | Severity            | Why it matters                                                                                                                                                              |
| ---------------------------------------------------------------------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| High-school paper eligibility is not satisfied by the documented independent-work record | Stop-ship           | The current public rule requires a qualifying university relationship for a high-school paper presentation.                                                                 |
| The corrected backward-looking benchmark is single-seed                                  | High                | The strongest scientific interpretation depends on one retraining run.                                                                                                      |
| Only one participant split is evaluated                                                  | High                | Five model seeds measure initialization variance, not sensitivity to which six participants are held out.                                                                   |
| The corrected TCN does not outperform Ridge                                              | High but acceptable | Backward-looking PAC gives TCN `R-squared = 0.212` and Ridge `R-squared = 0.216`. The paper must remain a target-definition audit, not a nonlinear-model superiority claim. |
| Stimulation-context features may encode the recorded protocol schedule                   | High                | The corrected target still needs PAC-only, stimulation-only, and combined ablations to separate biomarker dynamics from schedule prediction.                                |
| The closer-to-online PAC benchmark is not a production streaming estimator               | Medium              | Its contexts are backward-bounded, but PAC still uses zero-phase filtering.                                                                                                 |
| Controller replay is diagnostic only                                                     | Medium              | Replay includes all 35 trajectories, uses nominal recorded stimulation-state features, and cannot model counterfactual physiological response.                              |
| End-to-end rebuild was not rerun during this audit                                       | Medium              | Machine-readable outputs and code were inspected, but the archived sliding-PAC experiment should be rebuilt before final submission if time permits.                        |
| 2026 deadline and authenticated portal instructions are not public                       | Medium              | The URTC2026 CMT route exists, but MIT's public page still exposes the 2025 deadline and detailed guideline PDF.                                                            |

## Repository Verification

The manuscript's key values match the source artifacts:

| Manuscript value                                                                                 | Source verification                                                                                             |
| ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| Event-summary five-seed TCN mean `R-squared = 0.606`, range `0.558-0.647`                        | Recomputed from the five seed entries in `archive/experimental/results/pac_stim_focused.json`: mean `0.605953`. |
| Event-summary stress-test TCN `R-squared = 0.554`                                                | `archive/experimental/sliding_pac/results/comparison_results.json`                                              |
| Backward-looking TCN `R-squared = 0.212`; Ridge `R-squared = 0.216`                              | Same comparison artifact                                                                                        |
| Unique test targets `104 -> 2,678`; adjacent identical targets `96.2% -> 0.0%`                   | Same comparison artifact                                                                                        |
| Predictive replay balanced alignment `62.2%`; low-PAC stimulation `73.8%`; high-PAC rest `50.7%` | `results/metrics/controller_comparison_12feat.json`                                                             |
| Reactive replay balanced alignment `64.5%`; low-PAC stimulation `51.7%`; high-PAC rest `77.3%`   | Same replay artifact                                                                                            |

The source pipeline confirms the central event-summary limitation: `src/data_loader.py` computes PAC
once from the full 20-40 second event and assigns that value to each constituent sliding window. The
revised manuscript reports that limitation directly.

## Recommended Submission Position

Submit as a paper only if the high-school eligibility relationship is genuine and documented
accurately. Position the paper as:

> a retrospective systems study showing why target-definition audits are necessary before
> forecasting models are treated as components of adaptive neural-stimulation systems.

Do not position it as a validated closed-loop therapy, a live-streaming implementation, or evidence
that a TCN is necessary.

## Highest-Value Improvements Before Submission

1. Confirm the qualifying university relationship. If it does not exist, use the poster or lightning
   talk route permitted by MIT's FAQ.
2. Repeat the backward-looking benchmark across multiple random seeds and repeated participant-level
   splits or grouped cross-validation.
3. Add backward-looking PAC-only, stimulation-context-only, and combined-feature ablations.
4. Evaluate 5-, 8-, and 10-second backward contexts with a streaming-compatible filter.
5. Preserve the current two-table/one-figure layout; add uncertainty only if a corrected-target
   multi-seed or repeated-split result is generated.
6. Rebuild the archived sliding-PAC experiment from raw processed windows and preserve a clean
   reproducibility log.
7. Confirm the deadline, track, presenter limit, and author rules in the authenticated URTC2026 CMT
   portal before submission.

## Sources

- MIT URTC submission page: <https://urtc.mit.edu/submission>
- MIT URTC FAQ: <https://urtc.mit.edu/faq>
- MIT URTC 2025 paper guidelines: <https://urtc.mit.edu/paper_submission_2025.pdf>
- IEEE Boston 2025 call for submissions:
  <https://ieeeboston.org/wp-content/uploads/2025/06/2025-IEEE-MIT-URTC.pdf>
- Official 2025 technical-paper schedule:
  <https://drive.google.com/file/d/1uUHdaXFJeAz8ocFRRaTW9gRNLxCVh_cU/view?usp=sharing>
- _The Tech_, October 30, 2025:
  <https://thetech.com/2025/10/30/mit-11th-urtc>
