<!-- SUBMISSION-STATUS:START (auto-managed; edit paper/conferences/_tracker/submission_tracker.json, not this block) -->

> ### 📋 MIT URTC 2026 (poster/lightning) · priority #4
>
> **Doc status:** DRAFT — working draft, not submission-ready  
> **Artifact type:** submission draft (abstract/summary) · **Canonical:** yes (primary submission file)  
> **Venue phase:** gate G8 · 89% to submission · **eligibility:** ok · label: `strong-default`  
> **Deadline:** no date posted  
> **Source of truth for claims:** `paper/data/key_results.md` · **Tracker:** `paper/conferences/_tracker/submission_dashboard.html`  
> **Last labeled:** 2026-07-17 (auto — do not hand-edit this block)

<!-- SUBMISSION-STATUS:END -->

# MIT URTC Poster / Lightning Draft

## Venue Fit

**Best submission type:** Poster or lightning talk if paper-track university affiliation is not clean.  
**2026 status:** IEEE Boston lists URTC 2026 but says detailed information will be posted soon. The live URTC site still exposes 2025 deadlines and high-school eligibility language. Keep this draft under 1000 words and adapt to the current portal once 2026 submissions open.  
**Track fit:** Technology of Computation, Technology of Engineering, Technology of Humanity.  
**Acceptance strategy:** emphasize student-built technical work, honest evidence boundaries, and why the failure-mode audit matters.

## Recommended Title

Auditing PAC Forecast Targets During 40 Hz Auditory Stimulation

## Abstract Draft

Fixed 40 Hz auditory stimulation protocols define the sound schedule, but not whether the participant's measured EEG response is strengthening, fading, or being dominated by artifact. I built a retrospective computational benchmark to test whether frontal phase-amplitude coupling (PAC), the dependence of `38-42 Hz` EEG amplitude on `4-8 Hz` theta phase, can be forecast across participants during auditory stimulation, and whether that conclusion changes when the PAC target is made closer to online availability.

The analysis used OpenNeuro dataset `ds005048` version `1.0.1`, containing auditory-stimulation EEG from 35 memory-clinic participants. I selected seven frontal channels, computed PAC as a scalar frontal EEG timing target, and split participants into 24 training, 5 validation, and 6 held-out test participants. Each temporal sample used a 20-second stored-series history and predicted PAC five seconds ahead.

In the initial event-summary benchmark, a compact 12-feature temporal convolutional network improved held-out test performance from `R^2 = -0.025` for a 73-feature candidate representation to `R^2 = 0.558`. Across five training seeds on the same participant split, mean TCN performance was `R^2 = 0.606`, compared with `R^2 = 0.104` for a persistence baseline. However, those PAC labels were computed over complete 20-40 second event periods and assigned back to shorter windows, so early-window inputs could include information from later samples in the same event.

To test this limitation, I recomputed PAC from five-second backward-looking EEG contexts. This increased unique held-out targets from 104 to 2,678 and reduced adjacent target repetition from 96.2 percent to zero. Under this stricter target definition, TCN performance dropped from `R^2 = 0.554` to `R^2 = 0.212` and no longer exceeded Ridge regression at `R^2 = 0.216`. Offline controller replay showed a related tradeoff: the predictive policy stimulated more low-PAC periods than a reactive threshold policy, 73.8 percent versus 51.7 percent, but rested during fewer high-PAC periods, 50.7 percent versus 77.3 percent.

These findings do not validate a live treatment system. They show that target construction and information availability can control the apparent success of an EEG forecasting model. The project identifies the next engineering requirements for adaptive auditory stimulation: streaming-compatible PAC estimation, repeated participant-split validation, and controller objectives that balance low-PAC coverage against unnecessary stimulation during above-median-PAC periods.

## Lightning Talk Version

I tested whether frontal EEG PAC can be forecast during 40 Hz auditory stimulation and found that the answer depends strongly on target definition. A compact TCN looked strong on event-summary PAC labels, with five-seed mean held-out `R^2 = 0.606`, but when PAC was recomputed from backward-looking EEG windows, TCN performance dropped to `R^2 = 0.212` and did not beat Ridge regression. The main contribution is therefore not a claim of deployed clinical closed-loop control; it is an information-boundary audit showing what must be fixed before PAC forecasts can be trusted in adaptive stimulation systems.

## Submit / Do Not Submit Notes

- Submit this as poster/lightning if no qualifying university relationship exists for paper track.
- Do not submit the paper track unless the high-school eligibility rule is genuinely satisfied.
- If asked for novelty, lead with "target-definition stress test of a cross-participant PAC forecaster," not "TCN model."

## Official Sources

- `https://urtc.mit.edu/submission`
- `https://urtc.mit.edu/faq`
- `https://ieeeboston.org/events/2026-undergraduate-research-technology-conference-urtc/`
