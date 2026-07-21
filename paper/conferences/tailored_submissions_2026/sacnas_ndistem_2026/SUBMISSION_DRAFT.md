<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 SACNAS NDiSTEM 2026 · priority #17
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G2 · 22% to submission · **eligibility:** blocked · label: `expired-this-cycle`  
> **Deadline:** 2026-07-10 (passed)  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# SACNAS NDiSTEM 2026 Research Presentation Draft

## Venue Fit

**Submission type:** student research presentation.  
**Deadline:** summer application deadline 2026-07-10 at 5:00 PM PDT; notification 2026-08-14.  
**Official eligibility problem:** SACNAS requires applicants to be at least 18 at the time of the conference and to be community college, undergraduate, post-baccalaureate, graduate, or postdoctoral researchers. That likely excludes a 17-year-old high-school senior.  
**PI approval problem:** SACNAS requires approval from the principal investigator for submission and abstract publication. Independent work without a real PI should not be forced into this venue.

## Verdict

Default recommendation: skip. Use this only if SACNAS confirms that you are eligible and you have a real PI/mentor who can approve the abstract.

## 250-Word Contingency Abstract

Adaptive neurotechnology requires EEG features that are available before stimulation decisions are made. I tested this requirement in a retrospective forecasting benchmark using OpenNeuro `ds005048`, a public 40 Hz auditory-stimulation EEG dataset with 35 memory-clinic participants. Seven frontal channels were used to compute frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase. Participants were split into 24 training, 5 validation, and 6 held-out test participants. A compact 12-feature temporal convolutional network used PAC-history and stimulation-context inputs to forecast PAC five seconds ahead.

Under complete-event PAC summaries assigned back to shorter windows, the selected TCN reached five-seed mean held-out `R^2 = 0.606`, compared with `R^2 = 0.104` for persistence. I then identified a target-availability limitation: complete-event labels could assign early windows values computed from later EEG samples. Recomputing PAC from five-second backward-looking contexts increased unique held-out targets from 104 to 2678 and reduced adjacent target repetition from 96.2 percent to zero. Under this stricter benchmark, TCN performance dropped to `R^2 = 0.212` and did not exceed Ridge regression at `R^2 = 0.216`. These results show that target definition can substantially change apparent EEG forecasting performance and should be audited before retrospective models are treated as adaptive control components.

## Official Sources

- `https://www.sacnas.org/conference/research-presentations`
- `https://sacnas.secure-platform.com/`
