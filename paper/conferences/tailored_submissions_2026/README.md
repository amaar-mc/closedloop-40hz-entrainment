# Tailored Submission Workspace, 2026

**Created:** 2026-06-14  
**Purpose:** venue-specific drafts for presenting the EEG/PAC forecasting project during the 2026-2027 college-application cycle.

## Use Order

1. `mit_urtc_poster_lightning/` - best immediate MIT-branded presentation route if paper-track eligibility is not clean.
2. `bmes_high_school_poster_expo/` - best high-school biomedical-engineering poster target.
3. `sccur_2026/` - useful California conference presentation line if the faculty-guided eligibility condition can be satisfied.
4. `ieee_spmb_2026/` - strongest near-term professional technical venue, but due 2026-07-01 and needs the tightest technical polish.
5. `regeneron_sts_2027/` - not a conference presentation, but highest college-application upside.
6. `aan_neuroscience_prize/` - neuroscience-specific award target; monitor for current application opening.
7. `jshs_norcal_2027/` - strong high-school research competition for winter/spring 2027.
8. `sfn_late_breaking_2026/` - only submit if genuinely new analysis is completed after the regular abstract deadline.
9. `sigma_xi_showcase_2027/` - lower-stress online presentation backup.
10. `bci_meeting_2027/` and `bci_award_2026/` - later/stretch neurotechnology options.
11. `synopsys_championship_2027/` - local Santa Clara Valley science fair / ISEF pathway for senior year.
12. `aises_2026/` - only if the Indigenous-centered/community-impact framework fits honestly.
13. `sacnas_ndistem_2026/` - likely ineligible as a 17-year-old high-school student; keep only as contingency if eligibility is confirmed.
14. `icassp_2027/` - high-reach signal-processing paper target; do not submit as-is.

## Global Claim Rules

- Say "retrospective," "offline replay," "target-definition audit," and "scalar frontal EEG timing target."
- Do not say "therapy," "clinical validation," "patient benefit," or "deployed closed loop."
- Do not claim the TCN beats Ridge under the backward-looking PAC target.
- Keep the event-summary and backward-looking PAC results separate.
- Use historical controller numbers only if clearly labeled historical; default to current 12-feature replay.
- Do not list a mentor, university, AI Club, lab, or affiliation unless it is real and specific to this work.
- For STS and JSHS, treat these files as planning scaffolds only. Their rules restrict or require disclosure of generative-AI writing, so do not submit generated text verbatim.

## Core Result Block

- Dataset: OpenNeuro `ds005048` v1.0.1, 35 memory-clinic participants, 19-channel EEG at 250 Hz.
- Local feature set: seven frontal channels, theta phase `4-8 Hz`, gamma amplitude `38-42 Hz`, averaged modulation-index PAC feature.
- Split: 24 train, 5 validation, 6 held-out test participants.
- Event-summary benchmark: 12-feature TCN test `R^2 = 0.558` single seed; five-seed mean `R^2 = 0.606`, range `0.558-0.647`, persistence `R^2 = 0.104`.
- Backward-looking PAC stress test: unique held-out targets `104 -> 2,678`; adjacent repeated targets `96.2% -> 0.0%`; TCN `R^2 = 0.212`; Ridge `R^2 = 0.216`.
- Controller replay: predictive policy increased low-PAC stimulation coverage `73.8%` vs reactive `51.7%`, but reduced above-median-PAC rest rate `50.7%` vs `77.3%`; balanced alignment lower than reactive `62.2%` vs `64.5%`.

## Source Baseline

- Main manuscript: `../mit_urtc_2026/draft/MANUSCRIPT.md`
- Claim boundaries: `../mit_urtc_2026/EVIDENCE_MAP.md`
- Results reference: `../../data/key_results.md`
- Venue matrix: `../CONFERENCE_APPLICATION_MATRIX_2026.md`

## Official Source Links Checked

- MIT URTC submission and FAQ: `https://urtc.mit.edu/submission`, `https://urtc.mit.edu/faq`
- BMES 2026 High School Poster Expo and general abstracts: `https://www.bmes.org/2026/annualmeeting/high-school-poster-expo`, `https://www.bmes.org/2026/annualmeeting/abstracts`
- SCCUR 2026: `https://www.sccur.org/`, `https://research.sdsu.edu/sccur-2026`, `https://www.sccur.org/abstracts`
- IEEE SPMB 2026: `https://www.ieeespmb.org/2026/`, `https://isip.piconepress.com/conferences/ieee_spmb/2026/html/guidelines.shtml`
- STS, AAN, JSHS, SfN, Sigma Xi, BCI Meeting, BCI Award: official pages linked in the venue-specific drafts.
- AISES, SACNAS, Synopsys/ISEF, and ICASSP: official pages linked in the venue-specific drafts.
