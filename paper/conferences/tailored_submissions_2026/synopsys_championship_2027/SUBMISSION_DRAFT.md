<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 Synopsys Championship 2027 · priority #5
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G2 · 28% to submission · **eligibility:** ok · label: `senior-year-fair`  
> **Deadline:** no date posted  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# Synopsys Championship / ISEF Pathway 2027 Draft

## Venue Fit

**Submission type:** local Santa Clara Valley science fair project; possible ISEF pathway if advanced.  
**Eligibility:** Santa Clara County grades 6-12; high-school students may enter individual projects. For 2027, work must be done between 2026-01-01 and March 2027, with no more than 12 months total project time.  
**Rules caveat:** comply with ISEF rules, SRC/IRB/RRI rules, continuation rules, and adult-sponsor requirements. Because this uses public de-identified data and does not diagnose or treat illness, frame it as computational biomedical signal processing.

## Recommended Category

Computational Biology and Bioinformatics, Biomedical Engineering, or Systems Software, depending on the 2027 category list. Choose the category that sends the project to judges comfortable with EEG and ML validation.

## Recommended Title

Auditing EEG Forecasting Targets for Future Adaptive Auditory Stimulation

## Abstract Draft

Adaptive stimulation systems need brain-signal features that can be measured before stimulation decisions are made. This project tested whether a frontal EEG phase-amplitude-coupling feature could be forecast across participants during 40 Hz auditory stimulation, and whether the conclusion changed when the target was made more realistic for future online use.

I used OpenNeuro `ds005048`, a public EEG dataset containing 35 memory-clinic participants exposed to 40 Hz auditory stimulation. Seven frontal channels were used to compute frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase. Participants were split into 24 training, 5 validation, and 6 held-out test participants. A compact 12-feature temporal convolutional network predicted PAC five seconds ahead using PAC history and stimulation context.

In the first benchmark, complete-event PAC labels were assigned to shorter windows. Under that definition, the model achieved five-seed mean held-out `R^2 = 0.606`, outperforming persistence at `R^2 = 0.104`. I then found that early windows could receive PAC labels computed using later samples from the same event. A stricter stress test recomputed PAC only from five-second backward-looking EEG contexts. This increased unique held-out test targets from 104 to 2678 and removed repeated adjacent targets. Under the stricter definition, model performance dropped to `R^2 = 0.212` and did not exceed Ridge regression at `R^2 = 0.216`.

The results show that target definition can matter more than model complexity. This work supports further validation of streaming EEG features before adaptive auditory stimulation is tested prospectively.

## Submission Strategy

- Start ISEF Rules Wizard early.
- Treat this as a continuation/new-work question if earlier research artifacts are used.
- Do not make diagnosis, treatment, or medical-device claims.
- Emphasize independent computational analysis, public de-identified data, and methodological validation.

## Official Sources

- `https://science-fair.org/`
- `https://science-fair.org/rules-and-registration/requirements/`
- `https://science-fair.org/students-parents/important-dates/`
- `https://www.societyforscience.org/isef/affiliated-fair-network/`
