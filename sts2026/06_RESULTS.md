# 6. Results (confirmatory first, then labelled exploratory). Status: in progress, freeze on Oct 25

All numbers are read from `results/confirmatory/results.json` (pre-registered pipeline, sha256 `f802d599…`) and
`results/exploratory_post/results.json` (post-registration checks). Nothing is typed in by hand.

## A. Pre-registered tests on the held-out cohort (Harvard Dataverse 56XZ3F)
| Test | Result | Pre-registered verdict |
|---|---|---|
| **K1** gate: 40 Hz sound drives a measurable response | R40(periodic audio) − R40(silence): median +0.53; 37/39 positive; p < 1e-4 | **Pass** |
| **H1** trait (primary: audio block vs AV block, group-centred Spearman) | ρ = 0.52 [0.18, 0.76], permutation p = 0.001, n = 39 | **Partial.** ρ ≥ 0.5 met; CI lower bound 0.18 < 0.2 |
| H1 uncentred / by group | ρ = 0.79 [0.64, 0.87]. Young 0.80 (n = 13); older CN 0.19 (n = 10); AD 0.46 (n = 16) | Reported |
| NC1: 33 Hz control reliability | ρ = 0.08 [−0.25, 0.42] | Null, as required |
| NC2: non-rhythmic sound (jitter / constant noise) | median R40 −0.01, p = 0.33 | Null, as required |
| NC3: silence block vs silence block | ρ = 0.31 [0.00, 0.55], p = 0.052 | Borderline; not null. See E2 |
| H2a: older vs young CN | older lower; g = −0.53 [−1.84, 0.23]; Holm p = 0.16 | n.s. Direction **opposite** to published claim A04 |
| H2b: AD vs older CN | AD lower; g = −0.61 [−1.67, 0.12]; Holm p = 0.16 | n.s. Direction **opposite** to published claims A01/A02 |
| H2c: periodic vs jittered clicks (CN) | d_z = 2.72; mean difference 0.56 [0.48, 0.64]; Holm p < 1e-4 | **Pass.** The response is rhythm-specific |
| H3a: stability Phase 1 → Phase 2A baseline (0–4 months, pre-treatment) | ICC = 0.47 [−0.02, 0.78], n = 14, Holm p = 0.10 | **Not met** |
| H3b: stability baseline → 3 months (on active/sham treatment) | ICC = 0.55 [0.11, 0.86], n = 14, Holm p = 0.07 | **Met** (ICC ≥ 0.5, CI > 0). S4 without HG204: 0.50 [0.01, 0.85] |
| **H4** moonshot: resting EEG predicts response across cohorts | r = 0.55, permutation p = 0.0002 (train ds005048 n = 35 → test n = 39) | **Formally passed.** Invalidated by E5, see below |
| Sensitivity S1/S2/S3 for H1 | ρ = 0.61 [0.32, 0.82] / 0.53 [0.21, 0.77] / 0.50 [0.20, 0.72] | S1 and S2 meet the success rule; S3 is at the boundary |

**Discovery cohort (ds005048, same frozen pipeline):**
- Odd vs even blocks: ρ = 0.92 [0.81, 0.97].
- Single block vs single block: ρ = 0.68 [0.41, 0.85].
- 33 Hz control: ρ = 0.04.

## B. Exploratory checks after registration (labelled; not confirmatory)
| Check | Result | What it means |
|---|---|---|
| E2a: strobe artifact | Silent blocks with the covered strobe at 40 Hz: R40 median −0.03, vs 0 Hz strobe blocks: p = 0.43 | No light or electrical leakage from the strobe |
| E2b: unconnected EXG inputs during clicks | R40 ≈ 0.00 | No amplifier-level 40 Hz pickup (weak test: the inputs are near-flat) |
| E2c: topography | Maximum at Fz, FC2, Cz, FC1, plus the posterior pole; temporal sites low | Consistent with an auditory-cortex generator |
| E4: recording-noise confound on the trait | Gamma-band (35–45 Hz) power in silence vs R40: ρ = −0.52 overall, −0.17 within groups. H1 partialling out noise: ρ = 0.49 [0.14, 0.76] (group-centred); 0.71 uncentred | **The trait survives noise control** |
| E5: noise and H4 | H4 prediction vs noise: r = −0.89. H4 partialling out noise: r = 0.22 (0.11 within groups) | **H4 predicts recording noise, not neural responsiveness.** The moonshot claim is withdrawn |
| E5: noise and group differences | AD recordings are noisier (median log power −1.44 vs −1.85 for older CN). With noise in the model, the AD effect goes from −0.15 (p = 0.13) to −0.05 (p = 0.65) | The nominal AD < CN difference is explained by noise. This is a caution for published ITC/power comparisons in AD |
| E1: H4 within groups | Group-centred r = 0.34 (permutation p = 0.016); AD r = 0.43; older CN −0.05 | Superseded by E5 |
| E3: pooled AD vs control across both cohorts | g = −0.51 [−1.08, 0.06]; Q = 0.11 (consistent) | Neither cohort supports "enhanced in AD". Noise confound applies |

## A2. Pre-registered amendment A1: H5, third independent dataset (ds005185, 20 young adults × 4 nights)
| Test | Result | Verdict |
|---|---|---|
| H5 primary (200 µV rejection as registered) | Too many epochs were rejected in 16/80 dry-electrode home recordings, leaving 5 subjects with all 4 nights. ICC 0.73 with an undefined CI | **Not evaluable.** The rejection rule did not transfer to dry electrodes |
| H5 secondary: first two valid nights (n = 20) | ICC = 0.41 [−0.09, 0.80]; ρ = 0.35 | Not met |
| H5 under pre-specified sensitivity S2 (no rejection), 4 nights, n = 16 | ICC = 0.57 [0.31, 0.78]. Noise-adjusted: 0.69 [0.51, 0.82]. First two nights (n = 20): 0.26 [−0.18, 0.67] | **Meets the success rule** (sensitivity analysis only) |
| NC: R33 ICC | 0.05 [−0.10, 0.22] (S2) | Null, as required |
| Noise vs R40 across sessions | ρ = −0.60 | Noise lowers the measured response |

## B2. Discovery-cohort noise check (exploratory, E6)
- Silence gamma noise vs R40 in ds005048: ρ = −0.38 (p = 0.026).
- Trait with noise partialled out: split-half ρ = 0.93.
- AD − Normal difference: −0.08 without noise, −0.10 with noise (both n.s.). **Noise does not explain the AD trend
  in this cohort.** So the "noise explains AD < CN" result from 56XZ3F does **not** replicate.

## B3. Cross-dataset synthesis (what holds up in more than one dataset)
| Claim | ds005048 (discovery) | 56XZ3F (held-out) | ds005185 (held-out) | Status |
|---|---|---|---|---|
| The 40 Hz response is rhythm- and frequency-specific | 33 Hz control ρ 0.04 | Jittered clicks d_z 2.7; 33 Hz control null | 33 Hz control ICC 0.05 | **Holds (3/3)** |
| Individual response is stable within a session | ρ 0.92 split-half; 0.68 block vs block | ρ 0.79 (uncentred), 0.52 (group-centred; CI lower 0.18) | — | **Holds (2/2); primary strict rule narrowly missed** |
| ... and survives noise control | 0.93 | 0.49 (group-centred), 0.71 (uncentred) | 0.69 | **Holds** |
| Stability across sessions (days to months) | — | ICC 0.47 (0–4 mo, n.s.); 0.55 (3 mo) | 0.57 (S2); 0.26–0.41 (two nights) | **Moderate, imprecise.** Suggestive, not established |
| Recording noise lowers measured response | ρ −0.38 | ρ −0.52 | ρ −0.60 | **Holds (3/3)**; a confound for comparisons |
| 40 Hz response enhanced in AD (published claims A01/A02) | AD < Normal, n.s. | AD < older CN, n.s. | — | **Not supported** (pooled g −0.51 [−1.08, 0.06]) |
| Resting EEG predicts responders (H4) | train | r 0.55, but 0.22 after noise control | — | **Withdrawn** (a noise proxy) |

## C. Tier status (pre-registered mapping)
- **Floor: reached.** H1 was tested on 2 independent cohorts.
- **Target: not reached under the strict rule.** H1 CI lower bound 0.18 < 0.2, and H3a not met.
- **Moonshot: not reached.** H4 passed formally but is a noise artifact.
- **Across-session evidence (amendment A1):** primary not evaluable; the S2 sensitivity meets the rule. This does not
  lift the tier under the pre-registered mapping.
- **Why the target was not reached:**
  - Within-session trait reliability replicated, but the group-centred primary CI lower bound was 0.18 (needed > 0.2).
  - Across-visit stability in AD was not established (ICC 0.47, CI includes 0).
