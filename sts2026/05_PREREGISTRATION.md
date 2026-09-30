# 5. Pre-registration: "Who entrains?" (objective C1)

**Registered:** 2026-09-30. This git commit is the timestamp; it precedes any analysis of held-out EEG.
**Frozen code (sha256):**
- `code/confirmatory.py`: `f802d599a8d543cb0cf336da025d030054f03ccbb44c5471556d1a5e08800b46`
- `code/dv56_io.py`: `411ca95c7602b3839e35ed24153d495d111d6e6967fc65748f44232285d95a98`
- `code/ds005048_io.py`: `0d8265c08a3a9d574095fc9813627ca1f9f53eab102b2fd23b4c8a6d28203c32`

**Environment:** Python 3.11; numpy 2.4.6, scipy 1.17.1, mne 1.13.2, scikit-learn 1.9.1, pandas 3.0.6, fooof 1.1.1.
Seed 20261001.

## 1. Datasets and their status
| Role | Dataset | Status at registration |
|---|---|---|
| Discovery | OpenNeuro ds005048: 35 memory-clinic patients (10 normal, 6 MCI, 17 AD, 2 unlabelled); 40 Hz 4%-duty clicks from loudspeakers; 40 s on / 20 s off | Fully explored (`results/explore_*`). Its numbers are **not** confirmatory |
| **Held-out confirmation** | Harvard Dataverse 56XZ3F (Chan et al. 2022, PLoS One). Phase 1: 13 young CN, 12 older CN, 16 mild AD. Phase 2A: 15 AD, EEG at baseline and 3 months. Same 4%-duty 40 Hz click family. BioSemi 32 channels, 512 Hz | **Not analysed.** Opened so far: file listing, notes, demographics, BDF headers (dates), Status triggers (block timing only). EEG outcome measures computed only for `HG204_EEG3months.bdf`, as a pipeline dry run; the census agent had already opened this file. It is handled by sensitivity S4 |
| Not independent | OpenNeuro ds003800 | Same recordings as ds005048 (r ≈ 1). Not used for confirmation |

## 2. Pre-specified exclusions (decided from metadata only)
- **E06:** the recording was truncated ("Battery Low"), so it has no periodic blocks.
- **E34:** only a 1-hour stimulation file; no standard protocol.
- **HG222 Phase 2A baseline:** byte-identical to HG221's baseline file (md5 `3e056d07…`), a repository error.
- **Blocks noted as having extra stimulation** (description contains "tablet"): not used; the next same-label block is used instead.
- **HG217:** has two periodic-audio blocks; the first is used.
- **Any block with fewer than 20 clean 1-s epochs:** treated as missing.
- Expected analysable n: 13 young CN, 10 older CN, 16 AD (Phase 1), and 14 AD for each retest interval.

## 3. Measure (identical in both datasets)
- **R40** = within-block inter-trial phase coherence (ITC) at 40 Hz minus the mean ITC at 37, 38, 42 and 43 Hz.
  - Computed on non-overlapping 1-s epochs from block onset + 1 s to block end − 0.5 s.
  - Signal: mean of Fz, F3, F4, Cz, C3, C4, after a 1 Hz high-pass and average reference.
  - Hann-windowed DFT.
  - Epochs are rejected if any ROI channel exceeds 200 µV peak-to-peak.
- **Why this measure:** ITC measures how consistently the EEG phase follows the 40 Hz click clock. Subtracting
  the neighbouring frequencies removes the ITC's small-sample bias floor. Each 1-s epoch holds exactly 40
  cycles.
- **R40_1min:** the first 58 clean epochs only, so that 3-min CN blocks and 1-min AD blocks are comparable in
  group tests.
- **Control measure R33:** same computation at 33 Hz (neighbours 30, 31, 35, 36 Hz). No stimulus energy is at
  33 Hz, and it is at least 4 Hz from 40 Hz, so it avoids window leakage.

## 4. Hypotheses, tests and decision rules
Run order: K1 first, then H1, H2, H3, H4.

| ID | Hypothesis | Test | Success / kill |
|---|---|---|---|
| **K1 (gate; riskiest assumption)** | Periodic 40 Hz sound drives a measurable response in 56XZ3F | R40(periodic audio) > R40(first silent baseline), one-sided Wilcoxon, all Phase-1 participants | Pass if p < 0.05. If it fails, re-run H1/H2 with periodic AV as the response (fallback). If K1b (AV) also fails: **stop**; the measure does not transfer |
| **H1 (core)** | The individual response is a trait: people who respond strongly in one 40 Hz block respond strongly in another | Spearman ρ between R40(periodic audio) and R40(periodic AV), same visit, with each value centred on its group median (young/older/AD). Permutation p (10,000), bootstrap 95% CI | **Success:** ρ ≥ 0.5 and CI lower bound > 0.2. **Kill:** ρ < 0.3 means the trait claim is rejected. In between: "partial". Also reported: uncentred ρ, and ρ within each group |
| H2a | Published claim (A04): 40 Hz synchrony is larger in older than young adults | Mann–Whitney on R40_1min(periodic audio), older CN vs young CN; Hedges g with bootstrap CI; Cliff's δ | Two-sided; Holm across H2a–c; α = 0.05 |
| H2b | Published claims (A01, A02): the 40 Hz response is enhanced in AD | Same, AD vs older CN | The discovery hint (AD < Normal in ds005048) is reported but not used |
| H2c | The response is rhythm-specific | Paired Wilcoxon: R40(periodic audio) vs R40(jittered audio), CN only | Periodic > jittered expected |
| H3a | Stability over months in AD, before treatment | ICC(3,1): R40(periodic AV) at Phase 1 visit vs Phase 2A baseline (intervals 0–4 months, from BDF dates). Bootstrap CI; permutation Spearman | **Success:** ICC ≥ 0.5 and CI lower bound > 0. Holm across H3a/b |
| H3b | Stability over 3 months, during active or sham treatment | Same, Phase 2A baseline vs 3 months | As H3a. Sham vs active change is exploratory only (n = 7/8) |
| H4 (moonshot) | Pre-stimulation EEG predicts who responds, across cohorts | Ridge (α = 1) on z-scored [aperiodic exponent, aperiodic offset, alpha peak, relative 40 Hz power, age], trained on ds005048 (silence windows), tested on 56XZ3F (first silent baseline block of Phase 1) against R40(periodic audio) | **Success:** Pearson r ≥ 0.3 and one-sided permutation p < 0.05. Expected to fail (discovery: no feature has \|ρ\| > 0.21) |

## 5. Negative controls (should come out null)
- **NC1:** R33 reliability between the audio and AV blocks. Expect |ρ| < 0.3.
- **NC2:** R40 in non-rhythmic sound blocks (jittered audio in CN, constant noise in AD). Expect a median near 0.
- **NC3:** R40 reliability between two silent baseline blocks. Expect ≈ 0.
- **NC4:** permutation nulls for every correlation.

## 6. Pre-specified sensitivity analyses (reported; they do not change the decision rules)
- **S1:** ROI = Fz, FC1, FC2, Cz.
- **S2:** no epoch rejection.
- **S3:** linked-mastoid reference.
- **S4:** H3b without HG204.
- **S5:** Pearson in place of Spearman (reported alongside).

## 7. Tier mapping (from the objective memo)
- **Floor:** H1 tested on 2 cohorts, whatever the result.
- **Target:** H1 success in 56XZ3F (ds005048 discovery ρ = 0.68 single block vs single block; 0.92 split-half)
  plus H3a success.
- **Moonshot:** Target plus H4 success.

## 8. Deviations
Any change after the original commit (5c5eec86) is listed here with its date and reason. Results from a deviated
analysis are labelled **exploratory**.

- **2026-09-30. No deviations** to sections 1–7. Post-registration validity checks (artifact, recording-noise
  confound) were added and are reported as **exploratory** in `06_RESULTS.md` §B.

## 9. Amendment A1: H5, a third independent dataset (registered 2026-09-30, after the 56XZ3F results, before any ds005185 outcome)
**Reason.** In 56XZ3F, stability across *separate visits* was the weakest link (H3a not met, n = 14).
ds005185 (EESM19) gives 20 young adults with ~4 min of continuous 40 Hz AM noise on 4 separate nights.

- **Status of ds005185 at registration.** Opened so far: file listings, the README, participants, and channel
  names. For every session: trigger counts and lengths from the source `.mat`, and header length of the `.set`.
  No EEG outcome has been computed.
  - 80 sessions.
  - 4 have no stimulus triggers (sub-007 ses-003, sub-014 ses-002, sub-019 ses-004, sub-020 ses-004) and are
    excluded (fewer than 200 triggers).
  - 16 subjects therefore have all 4 nights.
- **Code:** `code/confirmatory_h5.py`, sha256 `4cf95c2358ddd6b3b0d601479e4fbff726e9b9c37f0a7350918d5105f17cec1d`.
- **Measure:** R40 as in §3.
  - Epochs are locked to the 1-s stimulus triggers.
  - ROI = mean(F3, F4, C3, C4) − mean(O1, O2). Fz/Cz do not exist here and the reference is unspecified.
  - Bad (NaN) channels are dropped.
- **H5 (primary):** across-night ICC(3,1) of R40 over the 4 nights, complete cases (n = 16).
  - **Success:** ICC ≥ 0.5 and bootstrap 95% CI lower bound > 0.2.
  - **Kill:** ICC < 0.3.
- **Secondary:**
  - ICC over each subject's first two valid nights (n = 20).
  - ICC after regressing out session noise (log power at 35–38 and 42–45 Hz during stimulation).
- **Negative control:** R33 ICC. |ICC| < 0.3 expected.
- **Limitation, stated in advance:** young healthy adults only. This tests *whether the 40 Hz response is a
  stable personal trait across days*, not anything about AD.
