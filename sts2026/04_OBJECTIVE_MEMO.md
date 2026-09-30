# 4. Objective memo: candidates, scores, recommendation (awaiting approval)

Inputs: the audit (01), the STS benchmark (02), the literature and gaps (03, 134 verified rows), the dataset census,
the PubMed novelty searches (`lit/novelty_searches.md`), and exploratory feasibility runs on the **discovery set
(ds005048) only** (`results/explore_*`). Held-out datasets have **not** been analysed. The one exception is one
56XZ3F Phase 2A file (HG204, 3-month visit), which the census opened to confirm the format. It is excluded from
confirmatory analyses by pre-registration.

## Discovery facts that constrain the choice
- The within-block, stimulus-locked 40 Hz response is robust.
  - ITC over neighbouring frequencies: d_z = 1.17, 32/35 participants.
  - No 20 Hz subharmonic and no 60 Hz response, so the spectrum looks linear.
- The individual 40 Hz response is highly reliable within a session: split-half across blocks r = 0.95.
- It is **not** related to age, MMSE, aperiodic exponent, alpha peak or resting 40 Hz power (all |ρ| ≤ 0.21, n = 35).
- Nominal medians: Normal 0.26, MCI 0.40, mild AD 0.15. This is exploratory, but published studies report the
  response is *increased* in AD (A01, A02).
- Onset/offset dynamics **cannot** be resolved in ds005048: phase is consistent across blocks in only 9/35.
- 56XZ3F has one 1-min audio-only block per older/AD person, so it cannot resolve them either.
- ds003800 is **not** independent: it contains the same recordings.

## Candidates (1 = poor, 5 = excellent)
| # | Candidate (direction) | Novelty (search evidence) | Feasible by Oct 25 | Data access | Fit | Falsifiable | Headline | Total |
|---|---|---|---|---|---|---|---|---|
| **C1** | **WHO ENTRAINS (physiology).** Is the response to the therapeutic 40 Hz click a stable personal trait in older adults and AD (within visit, across visits, over 3 months)? Do age or AD shift it, as published studies claim? Can pre-stimulation EEG predict it? ds005048 → 56XZ3F (+ ds005185 young test-retest) | 3. One dementia reliability study (IND05, one site, 1 week). No cross-cohort test on the therapeutic stimulus. Searches: "ASSR test-retest" 159 hits, mostly young or schizophrenia; "40 Hz dementia responders" 1 hit (a meta-analysis) | 5. Small data, pipeline exists | 5. CC0, no login, 4.3 GB | 5. Direct extension of the URTC stability result | 5. Numeric reliability thresholds; direction predicted by published claims | 4 | **32** |
| C2 | ECHO OR ENTRAINMENT (mechanism). A linear-systems test (onset/offset complementarity, decay vs a superposition null) on young EEG with hundreds of 3-s trains (ds007648) and 500-ms trains (ds006780) | 3–4. Superposition was tested in young adults (EVE06–08); the complementarity test is new. 0 hits for older/AD | 3. 14 GB; dynamics fitting | 4 | 3. Young only; the AD link is indirect | 4 | 4 | 25 |
| C3 | GENUS OMICS (mechanism). Map mouse 40-vs-20-Hz genes (GSE226822/GSE225842) onto human AD cell-type changes (SEA-AD) | 4. 0 PubMed hits | 2. SEA-AD h5ad is 18–39 GB (we have 15 GB RAM); mouse n = 4 per group | 3 | 1. No EEG | 3 | 4 | 17 |
| C4 | MODEL. Fit a PV/E-I network model of the 40 Hz response to young, older and AD group data; predict that AD shows a larger response and slower decay | 3. G4a: no aging/AD model exists | 3 | 5 | 3 | 2. Only group means available, and the model is flexible | 2 | 18 |
| C5 | STRUCTURE (AlphaFold) | 1–2. The only concrete protein lead is the adenosine transporter ENT2 / A2A receptor from a mouse 40 Hz-light paper. A structure prediction answers no open entrainment question and cannot be tested without a wet lab | 3 | 5 | 1 | 1 | 2 (would oversell) | 13 |

**Judgement on C5 (structure):** it does not fit. The evidence points to circuits and cell types (PV/VIP
interneurons, microglia, astrocytes, vasomotion), not to a protein whose structure is unknown and would decide
anything. Using AlphaFold here would be decoration.

## Recommendation: C1, with C2's jitter logic as a built-in control
**Why:**
- It is the only candidate that tests a published clinical-physiology claim on **two independent older-adult/AD
  cohorts with the same therapeutic click stimulus**.
- It builds on the one result of yours that survived the audit.
- It answers a question the field is actively asking: the 30% non-responders (H18), and no trial stratifies by
  response.

### Falsifiable core hypothesis (H1)
> In older adults and people with Alzheimer's disease, the strength of the stimulus-locked 40 Hz response to
> 40 Hz click stimulation is a stable individual trait. Its rank across people replicates between independent
> stimulation blocks within a visit, and across visits separated by weeks to 3 months, in a cohort independent of
> the discovery set.

- **Measure (pre-specified):**
  - R40 = within-block 40 Hz ITC over 1-s epochs, minus the mean ITC at 37/38/42/43 Hz, averaged over
    fronto-central channels. This measure is already frozen from discovery.
- **Success criteria:**
  - In 56XZ3F, cross-block reliability r ≥ 0.5 with the 95% CI lower bound > 0.2 (audio-only block vs
    audiovisual block, same visit).
  - Negative controls behave as expected: R37 reliability ≈ 0, and R40 during constant noise ≈ 0.
- **Kill criteria:**
  - K1: in 56XZ3F, audio R40 is not greater than constant-noise R40 at the group level. The measure fails; switch
    to the pre-specified audiovisual fallback. If that also fails, stop.
  - K2: cross-block reliability r < 0.3. The trait claim is dead; report it as such.

### Secondary, pre-registered (Holm-corrected family)
- **H2a:** Older CN vs young CN. Published direction: older > young (A04).
- **H2b:** Mild AD vs older CN. Published direction: AD > CN (A01, A02); the discovery hint points the other way.
  Two-sided test.
- **H2c:** Periodic vs jittered audio in CN (rhythm specificity). Periodic > jittered.
- **H3:** Stability across visits in AD. Two intervals:
  - Phase 1 visit → Phase 2A baseline (weeks).
  - Phase 2A baseline → 3 months.
  - Report the ICC with CI for sham only (n = 7) and for all (n = 15).
- **H4 (moonshot):**
  - A pre-stimulation EEG model is frozen on ds005048: ridge regression on aperiodic exponent and offset, alpha
    peak, relative 40 Hz power, and age.
  - It predicts R40 in 56XZ3F from each person's pre-stimulation baseline minute: r > 0.3, permutation p < 0.05.
  - Expected to fail, given the discovery results.

### Three tiers and the titles they earn (the student will write the final title)
| Tier | Condition | Title it earns |
|---|---|---|
| **Floor** (still a real contribution) | H1 tested on 2 cohorts, whatever the outcome, plus the audit showing PAC/forecast claims fail | "Measuring Who Responds to 40-Hz Alzheimer's Stimulation: A Reliability Test Across Two Independent EEG Cohorts" |
| **Target** | H1 passes in both cohorts, and H3 shows stability over weeks to months in AD. H2 is reported either way | "Who Entrains? The Brain's Response to 40-Hz Alzheimer's Stimulation Is a Stable Personal Trait Across Two Independent Cohorts" (+ ", Not Predicted by Diagnosis" if H2b is null) |
| **Moonshot** | Target + H4 passes | "One Minute of Resting EEG Predicts Who Responds to 40-Hz Alzheimer's Stimulation Across Independent Cohorts" |

### Plan and timeline (riskiest assumption first)
1. **Oct 1–2.** Pre-register (05) and commit the hash. Download 56XZ3F (4.3 GB).
   - Riskiest assumption, **K1**: is the audio-only 40 Hz response detectable in older/AD 56XZ3F blocks?
   - Checked first, before any hypothesis test.
2. **Oct 3–8.** H1 → H2 → H3 on 56XZ3F. Negative controls, permutation nulls, bootstrap CIs, Holm correction.
3. **Oct 9–13.** H4 moonshot. Your URTC talk is Oct 11.
4. **Oct 14–20.** Optional third dataset: ds005185 (young, 4 nights) for trait stability across nights. Sensitivity
   analyses (reference, channel set, epoch length).
5. **Oct 21–25.** Freeze results, key-figure list and the fact-sheet abstract. You write the report yourself
   (STS AI rule).
