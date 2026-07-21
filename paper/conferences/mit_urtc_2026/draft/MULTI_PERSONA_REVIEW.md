# MIT URTC Multi-Persona Manuscript Review

**Reviewed:** 2026-06-03  
**Artifact reviewed:** `MANUSCRIPT.md`, generated DOCX/PDF proof, poster PDFs, repository metrics,
archived backward-looking PAC artifacts, MIT URTC public guidance, and accepted-paper context

## Reviewer Tracks

Five independent review tracks were used before the final edit pass:

| Track                       | Persona                       | Primary question                                                                       |
| --------------------------- | ----------------------------- | -------------------------------------------------------------------------------------- |
| MIT URTC fit                | Conference reviewer           | Does this fit URTC paper expectations, especially for a high-school author?            |
| Statistical rigor           | Skeptical ML reviewer         | Are the results supported by the split design, baselines, and uncertainty evidence?    |
| EEG/PAC domain validity     | Neuroscience methods reviewer | Are PAC, entrainment, and controller claims biologically and methodologically bounded? |
| Language and AI markers     | Technical editor              | Does the writing sound inflated, generic, or machine-generated?                        |
| Layout and first-impression | Proceedings reviewer          | Does the manuscript look clean, dense, and reviewer-friendly?                          |

## Consensus Verdict

The paper is technically competitive for MIT URTC only if the high-school paper-track eligibility
requirement is genuinely satisfied. Without a qualifying university relationship, the paper track is
administratively blocked by the public FAQ, regardless of manuscript quality.

Technically, the strongest version of the manuscript is not a claim that a TCN validates a live
closed-loop auditory controller. The strongest version is a retrospective systems study showing that
an apparently strong PAC forecaster weakens when the target definition moves closer to online
availability. That is a more rigorous and more distinctive contribution.

## Adopted Edits

- Shortened the title and narrowed it to PAC forecasts during 40 Hz auditory stimulation.
- Rewrote the abstract around the target-definition stress test, including the Ridge result that
  slightly exceeds the TCN in the backward-looking benchmark.
- Reframed 40 Hz auditory stimulation as the recorded stimulation protocol, not proof of clinical
  entrainment or therapeutic efficacy.
- Added a PAC-interpretation caveat: the modulation-index values are retrospective EEG-derived
  targets, not definitive physiological theta-gamma coupling evidence.
- Added Aru et al. as a reference for cross-frequency-coupling interpretation risks.
- Made feature selection explicitly exploratory because the 12-feature representation was selected
  from the benchmark.
- Clarified that five training seeds estimate initialization variability on one fixed participant
  split, not participant-split sensitivity.
- Recast controller replay as a low-PAC-coverage/high-PAC-rest calibration problem rather than
  improved closed-loop control.
- Removed remaining inflated language and avoided visible double-hyphen phrasing.
- Fixed PDF ordered-list rendering so numbered lists display with periods.

## Rejected or Deferred Suggestions

- Do not import the poster's older `72.1%` and `82.6%` controller headlines; those belong to an older
  73-feature replay and would conflict with the final 12-feature checkpoint.
- Do not claim consumer-hardware latency or an EEGNet-to-TCN-to-controller loop has been validated
  end-to-end. The manuscript does not support that.
- Do not present the backward-looking PAC benchmark as a validated streaming estimator. It is closer
  to online availability than complete-event back-assignment, but still uses bounded offline
  processing and short PAC contexts.
- Do not claim the TCN is necessary under the corrected target definition. Ridge is slightly better
  in the current single-seed stress test.

## Reviewer Risk Register

| Risk                                               | Severity            | Current handling                                                                      |
| -------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------- |
| High-school paper eligibility is not visible       | Stop-ship           | The audit documents flag this as the only administrative blocker.                     |
| Corrected benchmark is single-seed                 | High                | Manuscript calls it a stress test and avoids treating it as final model selection.    |
| One participant split                              | High                | Manuscript states the limitation and does not claim split-insensitive generalization. |
| PAC interpretability                               | High                | Added explicit retrospective-target caveat and cross-frequency-coupling reference.    |
| TCN does not beat Ridge in corrected benchmark     | High but acceptable | Paper is framed as a target-definition audit, not nonlinear superiority.              |
| Controller replay is not counterfactual physiology | Medium              | Replay section states it is a diagnostic, not a prospective experiment.               |
| AI-generated language                              | Low after edits     | Remaining prose is technical, bounded, and specific to repository evidence.           |

## Final Submission Position

Submit as a paper only if the qualifying high-school university relationship exists and is stated
accurately. Position the manuscript as:

> a retrospective systems study showing why information-boundary and target-definition audits are
> necessary before PAC forecasts are treated as components of adaptive neural-stimulation systems.

That position is more credible and more impressive than overstating a live closed-loop claim. It
shows technical ambition, self-critique, and research maturity.
