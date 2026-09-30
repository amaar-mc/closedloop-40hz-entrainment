# Gaps: measuring 40 Hz auditory entrainment in older adults and dementia

Companion to `lit_measurement_methods.csv`. Row IDs such as [PAC03] refer to that table. Date: 2026-09-30.

**How to read this**
- A gap means that our search (Crossref, PubMed, web; about 150 candidates screened) found no study answering the question, or found one that covers only one dataset, modality, species or age group. "Not found" is not proof that no such study exists.
- Lines marked **[SPECULATION]** are our own reasoning. They are not reported findings.
- Lines marked **[PROJECT-INTERNAL]** cite this repository's own unpublished audit in `sts2026/results/audit_pac_forecast.json` (ds005048, n=35). It is not peer-reviewed.
- Most `key_finding` entries come from abstracts, not full texts. Before quoting a number in the paper, check it against the full text.

---

## 1. Is theta-gamma PAC during 40 Hz stimulation a valid entrainment metric?

**Short answer:** It has not been validated. The known pitfalls apply directly, and some of them apply more strongly during rhythmic stimulation than at rest.

**Studies that use theta-gamma coupling as a readout of 40 Hz stimulation:**
- [PAC10]: a conference abstract, n=10 healthy adults, audio-visual stimulation.
- [IND08]: personalized gamma frequencies; the sample size is not given in the abstract.
- [PAC11]: during a 40 Hz ASSR, theta tACS **raised** theta-gamma PAC while **lowering** 40 Hz power and phase locking. So PAC and the strength of the 40 Hz response can move in opposite directions.
- None of these checked their PAC against the controls in [PAC02]–[PAC09].

**Pitfalls, each tied to this project's pipeline (theta 4–8 Hz phase × 38–42 Hz amplitude, 2 s windows, fs = 250 Hz, 7 frontal channels):**

1. **The amplitude band is too narrow.** Theta modulation of a 40 Hz carrier puts side-bands at 40 ± (4–8) Hz, which is 32–36 and 44–48 Hz. Both lie outside a 38–42 Hz filter [PAC02][PAC03]. The filtered envelope therefore cannot carry most of the 4–8 Hz modulation the MI is meant to detect.
   - This follows from the filter arithmetic. Applying it to this project is our inference. It is not a result tested in [PAC03].
2. **The waveform is not sinusoidal.** ds005048 used a 40 Hz *rectangular* amplitude modulation [DAT02].
   - Driven responses to square-wave or click-like input are expected to be non-sinusoidal and rich in harmonics.
   - Such shapes, and the sharp edges at stimulation block onsets and offsets, can produce spurious CFC [PAC04][PAC05][PAC06][PAC07].
3. **Phase clustering.** Stimulation locks phase to the stimulus. That bias inflates or deflates PAC [PAC09], so it should differ between stimulation and rest windows. This confounds any stim-vs-rest contrast of PAC.
4. **Short windows.** A 2 s window holds only 8–16 theta cycles. All PAC indices depend on data length and SNR [PAC08][PAC01], and without per-window surrogate normalization the window-to-window variance is large.
5. **A theta oscillation must exist.** It has to be shown, for example as a periodic peak above the aperiodic 1/f in specparam [MEA07], before "theta phase" is meaningful [PAC02].
6. **[PROJECT-INTERNAL]** On ds005048:
   - Window-level MI was slightly **lower** during stimulation than at rest (Cohen's dz = −0.40, Wilcoxon p = 0.039, 14/35 subjects positive).
   - 40 Hz SNR was clearly **higher** (dz = +0.72, p = 7e-5, 26/35 positive).
   - The lag-1 autocorrelation of window PAC was about 0.04, which is close to unpredictable.
   - A subject-mean baseline alone gave pooled R² ≈ 0.08. Adding the known stimulation schedule added essentially nothing (0.0796 → 0.0800).
   - Together these say that PAC, as computed, does not follow the stimulation. The 40 Hz SNR does.

**Specific gaps:**
- **G1a.** No study, in any species, has tested whether theta-gamma PAC during 40 Hz *auditory* stimulation survives all of the following:
  - a wide amplitude band, at least ±8 Hz around 40 Hz [PAC03];
  - waveform or harmonic controls [PAC05][PAC07];
  - removal of the evoked, phase-locked part before PAC is computed [MEA04];
  - phase-clustering debiasing [PAC09];
  - a non-rhythmic (jittered) sound control [EVE02].
- **G1b.** The only positive 40 Hz theta-gamma PAC report [PAC10] is a small conference abstract in healthy adults, from the group that later released ds005048. No peer-reviewed replication in older adults or dementia was found.
- **G1c. [SPECULATION]** A defensible replacement readout: per-window 40 Hz SNR against neighboring bins [MEA05], computed on the aperiodic-corrected spectrum [MEA07], plus ITPC [MEA06]. Keep PAC only as a secondary, artifact-controlled analysis.

---

## 2. Has "true entrainment vs evoked superposition" been tested for 40 Hz AUDITORY stimulation in older adults or dementia?

**Short answer:** No study found. Every direct test is in young adults, and most are visual.

**What exists, by condition:**

| Evidence | Modality | Population | Rows |
|---|---|---|---|
| Superposition explains the *steady* 40 Hz ASSR (deconvolved ABR/MLR) | Auditory, clicks | Young normal-hearing adults | [EVE06][EVE07][EVE08] |
| Superposition fails for the ASSR *onset* | Auditory | Young adults | [EVE07] |
| Nonlinear reset (250 ms suppression that superposition cannot explain) | Auditory MEG | Young adults | [MEA08] |
| Arnold-tongue test (rhythmic vs jittered, frequency × intensity) supports entrainment | Visual alpha | Young adults | [EVE02] |
| Superposition suffices, no entrainment | Visual | Young adults | [EVE01] |
| Gamma flicker coexists with, but does not entrain, endogenous gamma | Visual MEG | Young adults | [EVE04] |
| 40 Hz light does not engage native gamma | Visual | AD model mice | [EVE09] |
| No 40 Hz oscillation *after* stimulation offset | Audio-visual EEG | Population not given in abstract | [EVE12] |
| Behavioral echoes found only at 6–8 Hz; nothing at 40 Hz | Auditory behavior | Adults | [EVE11] |
| Frequency sweep ("resonance" near 40 Hz) | Auditory chirp; visual flicker | Healthy adults | [EVE10]; [EVE05] |

**Older-adult data that bear on the question indirectly:**
- The auditory 40 Hz response has two components, and only the later one shrinks with age [AGE03].
- ASSR amplitude *rises* in older adults and relates to hearing and GABA [AGE04].
- 40 Hz power is higher in AD than in MCI or controls [IND05].
- None of these separates entrainment from superposition.

**Specific gaps:**
- **G2a.** No auditory 40 Hz study in older adults or dementia has used any of these designs:
  - a jittered or arrhythmic control [EVE02];
  - a rate × intensity (Arnold-tongue) map [EVE02][MOD05];
  - deconvolution-based superposition prediction [EVE06]–[EVE08];
  - a perturbation or reset probe [MEA08];
  - post-offset persistence [EVE11][EVE12].
- **G2b.** The superposition account rests on middle-latency responses (Pa/Pb) [EVE06]. Age and hearing loss change those responses. Whether superposition fits equally well in older ears is untested.
- **G2c.** ds005048 can only partly address the question [DAT02]. It has one stimulation frequency, one intensity, no jitter and one session. It does allow:
  - onset build-up and offset decay time constants of the 40 Hz envelope, at 40–80 ms resolution;
  - whether 40 Hz ITPC persists for more than a few cycles after block offset.
- **G2c [SPECULATION].** Superposition predicts decay within about one MLR duration after the last cycle. An entrained oscillator predicts a longer, exponentially decaying "ring-down". A null result would favor superposition but would not rule out a weakly damped oscillator.
- **G2d. [SPECULATION]** With fs = 250 Hz, harmonics of a rectangular-AM response at 80 and 120 Hz sit close to Nyquist (125 Hz). The 160 and 200 Hz harmonics could alias to 90 and 50 Hz if the amplifier's anti-alias filtering was weak. Check the recording's hardware filter before interpreting spectra away from 40 Hz.

---

## 3. Are individual differences in the 40 Hz response stable across sessions and datasets?

**Short answer:** Stability is established for young healthy adults at about one week. It has been measured once in dementia. It has never been tested across datasets, and never for "individual optimal frequency".

**Evidence:**
- **Healthy young adults: good reliability.**
  - ITPC is more reliable than evoked power: ICC ~0.86–0.96 for ITPC vs 0.61–0.82 for power in [IND04]; the same ordering holds in [IND01][IND02].
  - Clicks give more consistent responses than AM noise [IND01][IND02].
  - G-coefficients above 0.6 for 40 Hz measures in schizophrenia and controls [IND03].
- **Dementia: one study** [IND05]. One site, a 1-week interval, correlations r ≈ 0.68–0.83, n=55 across AD, MCI and controls, click trains.
  - No ICC, no G-theory or hierarchical reliability [NBM03], and no AM-tone data.
- **Individual optimal frequency:** reported for older adults with auditory stimulation [IND06, a preprint] and visual stimulation [IND07], and for younger adults [IND08].
  - In every case the optimum was picked and evaluated in the *same* session. That is circular unless cross-validated.
  - No study re-measures a person's optimum on a second day.
- **Aging direction conflicts:**
  - Phase-locking index and evoked amplitude *decline* with age (20–58 years, males) [AGE01].
  - Amplitude *increases* in older adults [AGE04].
  - A 2026 systematic review calls the aging evidence heterogeneous and sparse [AGE05].
  - Metric choice (phase-locked vs total power [MEA04][AGE01]) and hearing level [AGE04] are likely moderators.

**Specific gaps:**
- **G3a.** No test-retest or ICC for *AM-tone* 40 Hz responses in dementia. This is the stimulus type used in ds005048 and most therapy devices. The only dementia reliability data use clicks [IND05].
- **G3b.** No study checks whether a person's 40 Hz response rank holds up **across datasets, devices or sites**. Harmonization (ComBat [NBM10], Riemannian re-centering [NBM11]) and normative modeling [NBM01][NBM02] have been applied to resting EEG only, never to steady-state features.
- **G3c.** No normative lifespan model of 40 Hz response vs age and hearing exists [AGE05]. Without one, a dementia patient's "weak" or "strong" 40 Hz response cannot be judged against age-matched peers.
- **G3d.** The reliability paradox [NBM04]: a strong group-level 40 Hz effect (e.g., SNR dz = 0.72 in ds005048, [PROJECT-INTERNAL]) does not imply a stable per-person ranking. A within-session split-half or hierarchical reliability estimate [NBM03] of per-window 40 Hz SNR/ITPC in ds005048 is feasible and apparently unreported.
- **G3e.** Case-control 40 Hz effects in the best-studied disorder are moderate: g ≈ −0.46 to −0.58 [SCZ02], and the changes are not disorder-specific [SCZ03].
  - **[SPECULATION]** With n ≈ 35 split across 4 diagnostic labels, ds005048 is underpowered for group or brain–cognition correlations. Results should be framed as within-subject stim-vs-rest effects.
- **G3f.** Medication and hearing covariates are rarely modeled. Lorazepam increases the 40 Hz ASSR, while memantine (a common AD drug) had no detectable effect [SCZ04]. Hearing loss correlates with ASSR amplitude in older adults [AGE04].

---

## 4. Does any mechanistic model make a falsifiable prediction testable in public human EEG/MEG?

**Short answer:** Yes, for a few models. But no model has been fitted to or tested on 40 Hz data from older adults or dementia.

**Candidates, and what public data could test them:**
- **[MOD04] Metzner & Steuber 2021, beat-skipping.**
  - Prediction: with prolonged GABA decay, 40 Hz drive produces a strong **20 Hz subharmonic**, but only within a band of input strengths.
  - Testable now, partly, in ds005048: is there 20 Hz power or ITPC during 40 Hz stimulation above rest, and does it scale with dementia severity (MMSE)?
  - The intensity dependence needs a loudness sweep, which ds005048 does not have.
  - **[SPECULATION]** A link between AD and prolonged inhibition is not established here. Treat this as a test of the model's signature, not of AD pathophysiology.
  - Related models: [MOD02] predicts the same pattern (40 Hz loss with 20 Hz gain) from longer inhibitory decay; [MOD03] is an open model that could be refit.
- **[MOD05] Herrmann et al. 2016 and [MOD09] Kuramoto, Arnold tongue.**
  - Prediction: the locking range widens with stimulus intensity around the intrinsic frequency, and phase locking falls outside the tongue.
  - Needs data at several rates × intensities.
  - Public multi-rate ASSR data found here are in mice only [DAT03: 10–50 Hz clicks].
  - Human multi-rate datasets were not found in this search. The dataset-census agent should check.
  - The older-adult frequency-sweep studies [IND06][IND07] fit this design but do not appear to have public data.
- **[MOD07] DCM with a canonical microcircuit.**
  - Fitted to 40 Hz ASSR in 108 people with schizophrenia; pyramidal self-inhibition explained the group differences.
  - The same pipeline could run on ds005048.
  - **[SPECULATION]** It becomes falsifiable only if the expected direction of change in AD (for example, lower pyramidal gain vs interneuron loss) is pre-registered before fitting.
  - [MOD08] shows that this model type can explain individual gamma differences and can be validated with a drug.
- **Superposition model [EVE06]–[EVE08] as the null mechanism.**
  - Prediction: the steady 40 Hz response equals the transient MLR convolved with the stimulus train. So response phase and amplitude should follow MLR latencies and amplitudes, and the response should vanish quickly after offset.
  - A full test needs jittered sequences for deconvolution. ds005048 supports only the offset-decay part (see G2c).
- **Pharmacology [SCZ04] with GABA [AGE04].**
  - Prediction: more GABA-A drive gives a larger 40 Hz ASSR.
  - **[SPECULATION]** This is testable in any public dementia dataset that records benzodiazepine use. ds005048's participants.tsv lists only gender, age, group and MMSE, so it cannot test this.

**Specific gaps:**
- **G4a.** No ASSR network model has been parameterized for aging or AD, for example with changed PV-interneuron or GABA kinetics, or with hearing-loss input.
- **G4b.** No published study compares an oscillator model with a superposition model for 40 Hz auditory data in any older-adult dataset. Such a comparison exists for music-rate entrainment in young adults (Doelling 2019, PNAS 10.1073/pnas.1816414116, verified but not in the table).
- **G4c.** The best-supported falsifiable prediction that ds005048 can test right away is the 20 Hz subharmonic signature [MOD04][MOD02]. The limitation is that only one intensity was used.

---

## 5. Other specific gaps (short)

- **G5. Connectivity under volume conduction.**
  - The frontal-parietal "DMN synchrony" result on ds005048 [DAT01] used PLV. PLV is inflated by volume conduction and by a shared 40 Hz driven input [MEA01].
  - No re-analysis with wPLI or imaginary coherence [MEA02][MEA03] was found.
  - Nor was a comparison against a surrogate made by shifting stimulation phase between channels.
- **G6. SNR on the aperiodic background.**
  - No dementia 40 Hz study reports the response relative to the specparam aperiodic fit [MEA07] or with neighbor-bin statistics [MEA05].
  - This matters because the 1/f slope changes with age, and the change is not a 40 Hz effect.
- **G7. Closed-loop / state-dependent 40 Hz stimulation.**
  - Phase-locked closed-loop auditory stimulation works for sleep slow oscillations [NBM06][NBM07].
  - Real-time phase estimation with uncertainty exists [NBM09], and Bayesian optimization of stimulation parameters exists for tACS [NBM05].
  - None has been applied to gating or tuning 40 Hz sensory stimulation with an EEG objective in older adults. This is the project's niche.
  - Caveat: the project's own audit found window-level PAC unpredictable ([PROJECT-INTERNAL], section 1), so any closed-loop target should be the 40 Hz response itself.
- **G8. Analytic flexibility.**
  - Multi-analyst variability in EEG is large [NBM12].
  - No 40 Hz entrainment study reports a multiverse over reference, filter, window, metric (SNR / ITPC / PAC) and channel set.
  - A small multiverse on ds005048 would be new and cheap.
- **G9. Stimulus waveform.**
  - Rectangular vs sinusoidal AM changes the 40 Hz response and alpha suppression (Han 2023, Cogn Neurodyn 10.1007/s11571-022-09834-x, verified but not in the table).
  - Clicks give more reliable responses than noise [IND01][IND02].
  - Waveform is not standardized across dementia studies. That limits pooling across datasets.

---

## Verification notes

- 70 rows in total.
- **69 rows `verified = yes`.** Their DOI resolved in the Crossref REST API, and the first author, year, title and journal in the table were taken from that Crossref record. The expected title fragment was checked against it.
  - One title (EVE05) was retyped by hand because of an encoding glitch in the Crossref record.
- **1 row `partial`:** DAT02, the OpenNeuro dataset. Its DOI is a DataCite DOI, verified through the DataCite API; it is not in Crossref. Its paper, DAT01, is Crossref-verified.
- **67 rows have a PMID.** Each was matched through a PubMed esearch on the DOI. Lachaux 1999 (MEA01) was matched by title, author and year, then confirmed with esummary.
- **3 rows have no PMID:**
  - IND06: a Research Square preprint, not peer-reviewed.
  - PAC10: a meeting abstract, not peer-reviewed.
  - DAT02: a dataset.
- **0 rows `UNVERIFIED`.** All 140 DOIs checked during screening resolved in Crossref.
- Extra verified references are cited only in the `notes` column or in this file: Osipova 2006, Park 2022, Cardin 2009, Marquand 2019, Lorenz 2017, Matsuda & Komaki 2017, Johnson 2007, Griskova-Bulanova 2020, Lahijanian 2021 bioRxiv, Doelling 2019 and Han 2023.
