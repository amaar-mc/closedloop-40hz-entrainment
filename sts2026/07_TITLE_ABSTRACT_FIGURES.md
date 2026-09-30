# 7. Title, abstract and key figures (FACT SHEET: the student must write the submitted versions)

> **STS rule:** generative AI may not draft the Research Report, the application answers or citations.
> Everything below is a *fact sheet* that pins down what is true and which numbers support it. Write the submitted
> title, abstract and report yourself, in your own words. Keep every number traceable to `results/`.

## Tier earned
**Floor**, with two cross-dataset findings beyond it. Per the pre-registered mapping in `05_PREREGISTRATION.md` §7:
- H1 was tested on two independent cohorts; a third was added under amendment A1.
- The target tier was not reached. The strict H1 criterion was missed narrowly (CI lower bound 0.18 < 0.2), and
  across-visit stability in AD was not established (ICC 0.47, CI includes 0).
- The moonshot (H4) passed formally but was shown to be a recording-noise proxy, so it is withdrawn.

## Title options (all true; ranked)
1. **"Who Responds to 40-Hz Alzheimer's Stimulation? A Pre-Registered Test in Three Independent EEG Cohorts Finds a
   Stable Individual Response and a Recording-Noise Confound"**
2. "The Brain's Response to 40-Hz Therapeutic Sound Is Person-Specific but Not Enhanced in Alzheimer's Disease: A
   Three-Cohort, Pre-Registered EEG Study"
3. (Floor title from the memo) "Measuring Who Responds to 40-Hz Alzheimer's Stimulation: A Reliability Test Across
   Independent EEG Cohorts"

**Avoid (not supported):** "predicts responders", "stable over months", "closed-loop improves therapy",
"forecasts entrainment".

## Abstract fact sheet (250 words; every number is checked against `results/`)
Forty-hertz sensory stimulation is being tested as an Alzheimer's disease (AD) therapy, yet many patients show little EEG response and no trial selects patients by responsiveness. Auditing my earlier closed-loop project, I found that its forecasting accuracy (R² ≈ 0.6) came from block-level labels and a known stimulation schedule: honest per-window theta-gamma coupling was unpredictable (R² ≈ 0.08) and fell during stimulation. I therefore asked whether the brain's response to the 40 Hz click stimulus used in therapy is a stable individual trait. Using a stimulus-locked, noise-floor-corrected phase-locking measure (R40), I analyzed a discovery cohort (35 memory-clinic patients) and, under a pre-registered plan, two independent public cohorts (39 young, older and AD participants from an MIT trial; 20 young adults recorded on four nights). Individual responses were reproducible within a session (discovery ρ = 0.92; held-out ρ = 0.78 between separate blocks, 0.52 within diagnostic groups) and specific to the stimulated rhythm (jittered clicks abolished the response, d_z = 2.7) and frequency (33 Hz control reliability ≈ 0). Stability across sessions was moderate and imprecise (ICC 0.26–0.57 across estimates; several CIs included zero). Contrary to published reports, the response was not enhanced in AD (pooled g = −0.51, 95% CI −1.08 to 0.06). Recording noise lowered measured responses in all three cohorts (ρ = −0.38 to −0.60), and a pre-registered resting-EEG model that appeared to predict responders (r = 0.55) largely tracked this noise (r = 0.22 after control). Screening for 40 Hz responsiveness takes minutes, but comparisons between patients must control for recording noise.

**Number provenance:**
- R² 0.6: README (original claim).
- R² 0.08: `results/audit_pac_forecast.json`.
- ρ 0.92: `confirmatory/results.json → ds005048_discovery_reliability.split_half_odd_even`.
- ρ 0.78 / 0.52: `primary.H1_uncentred` / `primary.H1_primary_A_vs_AV_groupcentred`.
- d_z 2.7: `primary.H2c_periodic_vs_random_CN`.
- ICC 0.26–0.57: `H3a`, `H3b`, `results_h5_primary.json`, `results_h5_S2_no_rejection.json`.
- g −0.51: `exploratory_post/results.json → E3`.
- Noise ρ: E4/E6 and `results_h5_S2_no_rejection.json`.
- r 0.55 → 0.22: `H4` and `E5`.

## Key-figure list (`figures/`, made by `code/make_figures.py` from the results files)
| # | File | Message | Caveat to state in the caption |
|---|---|---|---|
| 1 | `fig1_audit_forecast_artifact.png` | The old PAC "forecast" skill is reproduced by persistence and a zero-parameter schedule lookup on block-level labels; honest per-window PAC gives R² ≈ 0.08 | Audit of your own earlier work. Say so; it is a strength |
| 2 | `fig2_within_session_trait.png` | Individual 40 Hz response reproduces across blocks: discovery ρ 0.92; held-out ρ 0.78 (0.52 within groups) | Within-group CI lower bound 0.18 was just under the pre-registered 0.2 |
| 3 | `fig3_specificity.png` | Rhythm-specific (jitter abolishes it, d_z 2.7) and frequency-specific (33 Hz control reliability ≈ 0 in 3 cohorts) | EESM19 bars use the pre-specified no-rejection sensitivity (S2). Panel B mixes ρ and ICC; label them |
| 4 | `fig4_across_session_stability.png` | Across sessions, ICC 0.41–0.57 with wide CIs | The 4-night EESM19 estimate is a sensitivity analysis; the registered primary was not evaluable |
| 5 | `fig5_noise_confound.png` | Noisier recordings show weaker measured responses in all 3 cohorts | Panel C noise is measured during sound; A–B in silence. Noise may include some neural gamma |
| 6 | `fig6_group_claims.png` | No enhancement in AD or aging (contradicts published claims A01, A02, A04) | Small groups; n.s.; ds005048 grouping was seen during discovery |

## Freeze plan (results freeze on Oct 25, 2026)
- **Oct 1–10:** read and re-run every script yourself (`README` in this folder), and hand-verify 10 citations. Start
  writing the report in your own words.
- **Oct 11:** URTC talk. The PLV result stands; do not present the TCN/controller numbers.
- **Oct 12–24:** optional robustness only, labelled exploratory (e.g., M3CV 95 × 2 days test-retest at 45 Hz). **No
  new confirmatory claims.**
- **Oct 25:** tag the repo `sts-freeze-2026-10-25`. After that, only writing.
