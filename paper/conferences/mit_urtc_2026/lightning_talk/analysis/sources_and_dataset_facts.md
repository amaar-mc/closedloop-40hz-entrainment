# URTC 2026 Lightning Talk (ID-1269): background facts and citations

Checked 2026-09-27. Nothing in the repo was changed. Abbreviations used below:

- **SciRep** = Lahijanian, Aghajan & Vahabi 2024, local PDF `ds005048-download/ (local dataset download, outside the repo) s41598-024-63727-z (6).pdf`. "p" numbers are the printed journal page numbers.
- **bioRxiv** = Lahijanian, Aghajan, Vahabi & Afzal, preprint 10.1101/2021.09.30.462389 v2, local PDF `ds005048-download/ (local dataset download, outside the repo) 2021.09.30.462389v2.full.pdf`. "p" numbers are PDF page numbers and "l." numbers are the preprint's own line numbers.
- **README** = `data/raw/ds005048/README`. It is byte-identical to `ds005048-download/ (local dataset download, outside the repo) README`, which I confirmed with `diff`.
- Text versions of the PDFs are in this folder: `scirep_paged.txt` and `biorxiv_paged.txt` (each line is prefixed with its page), plus `pubmed_abstracts.txt`.

Unrelated file: `ds005048-download/ (local dataset download, outside the repo) exmethod.pdf` is *not* about ds005048. It describes an EEG emotion-classification pipeline that uses 1000 Hz EDF music-listening data. Do not cite it.

---

## A. Dataset ds005048: facts from the primary sources

### A1. Identity and citation
| Fact | Value | Source |
|---|---|---|
| Name | "40Hz Auditory Entrainment" | `data/raw/ds005048/dataset_description.json` (`Name`); OpenNeuro GraphQL API (`https://openneuro.org/crn/graphql`, dataset ds005048) |
| Authors | Mojtaba Lahijanian, Hamid Aghajan, Zahra Vahabi | dataset_description.json `Authors`; DataCite record |
| DOI | 10.18112/openneuro.ds005048.v1.0.1 (DataCite, publisher OpenNeuro, publication year 2025). It resolves to https://openneuro.org/datasets/ds005048/versions/1.0.1 | `https://api.datacite.org/dois/10.18112/openneuro.ds005048.v1.0.1`; `curl -I https://doi.org/10.18112/openneuro.ds005048.v1.0.1` returns 302 to that URL |
| Versions | v1.0.0 released 2024-03-21 (files uploaded). v1.0.1 released 2025-04-10, where only "References and Links" was updated, so the data are unchanged | `data/raw/ds005048/CHANGES`; DataCite v1.0.0 record (year 2024) |
| Version cited in the paper | SciRep's Data availability section cites **v1.0.0** | SciRep p13, "Data availability" |
| License | CC0 | dataset_description.json |
| Citation the authors ask for | SciRep paper plus the dataset DOI | dataset_description.json `HowToAcknowledge` |
| BIDS | 1.8.0; files written by bids-matlab-tools 8.0 | dataset_description.json |

### A2. The 40-Hz sound and how it was delivered
All of the following text is identical in SciRep p12 ("Entrainment session and auditory stimulation"), the README ("Entrainment session and auditory stimulation"), and bioRxiv p15 l.430–441 ("Auditory stimulation").
- **Stimulus:** a 5 kHz carrier tone amplitude-modulated by a 40 Hz rectangular wave, described as "40 Hz On and Off cycles". The duty cycle was **4%**: the tone was on for 1 ms of each 25 ms cycle. In effect this is a **40 Hz train of 1-ms, 5-kHz tone pips**, or click-like pulses. It is *not* a sinusoidally amplitude-modulated tone. The stated reasoning is that a 40 Hz tone cannot easily be heard, so the 5 kHz carrier makes the 40 Hz pulse train audible, and the low duty cycle limits the effect of the carrier. The stimulus was generated in MATLAB and played as a .wav file.
- **Delivery:** through **two loudspeakers, not headphones**. They sat in front of the participant, 50 cm apart, pointed at the ears from 50 cm away.
- **Loudness:** reported only as "around −40 dB within a fixed range for all participants", with each participant's volume adjusted to a comfortable level. **Caution:** "−40 dB" has no reference (it is not dB SPL) and cannot be converted to an SPL. Do not put an SPL value on a slide. Because volume was set per participant, loudness varied between participants.
- **Eyes:** open. Participants sat in a quiet room and were told to relax and keep their heads still (SciRep p10–11; README; bioRxiv p15 l.418–420).
- **Pre-task baseline:** a 1-minute eyes-open resting recording was made before the task (SciRep p11; bioRxiv p15 l.420–421). It is **not in the released files**. Each `*_events.tsv` starts with Stimulus at onset 5 s, and `RecordingDuration` is 350 s or 590 s. This is my inference from those files.

### A3. Protocol: 40 s stimulation, 20 s silence, and why there are 6 or 10 blocks
- A trial was 40 s of stimulus followed by 20 s of silence. The **short session had 6 trials** and the **long session had 10** (SciRep p12; README).
- **Why two lengths:** the authors "designed short and long sessions ... to accommodate participants who preferred a shorter duration of data gathering" and "to minimize inconvenience for the participants who were less inclined to engage in lengthy procedures" (SciRep p9, "Participants"; README "Introduction"). Session length was therefore **chosen by the participant, not randomized**.
- **Which participants had which session** (my count from `sub-*/eeg/*_events.tsv` and `*_eeg.json`):
  - sub-01 to sub-08 had 6 Stimulus events, with `RecordingDuration` 350 s.
  - sub-09 to sub-35 had 10 Stimulus events, with `RecordingDuration` 590 s.
  - This agrees with the repo's `results/metrics/early_late_connectivity_analysis.json` → `protocol_cohorts` = {"6": 8, "10": 27}.
- **Event timing** (e.g., `sub-01_task-40HzAuditoryEntrainment_events.tsv`): Stimulus onsets at 5, 65, 125, ... s, each 40 s long, and Rest at 45, 105, ... s, each 20 s long. **The last Rest is cut to 5 s** in every file (345 s + 5 s for short sessions, 585 s + 5 s for long). So the final silence period is incomplete for everyone. This does not affect cycles 1–2 or 4–5.
- Event value codes are 1 = Rest and 2 = Stimulus (`task-40HzAuditoryEntrainment_events.json`).
- The bioRxiv version (13 participants, all short sessions) says: "6 trials of 40sec stimulus interleaved by 20sec of rest ... a 340sec (6×40+5×20) EEG signal" (bioRxiv p15 l.439–441).
- **How the 40/20 s timing was chosen:** the authors "separately applied different stimulus and rest cycle durations on a group of young and healthy volunteers and based on the results of that study selected the intervals". They also noted that "the effective cycle duration may be different for each participant and need customized tuning" (bioRxiv p14 l.378–389, Limitations). The published SciRep version dropped this paragraph.
- The order was always stimulation then silence, and **there was no sham condition**. Neither paper describes a sham or counterbalancing.

### A4. EEG acquisition
| Fact | Value | Source |
|---|---|---|
| Channels | **19 monopolar** electrodes, 10–20 system: Fp1, Fp2, F7, F3, Fz, F4, F8, T7, C3, Cz, C4, T8, P7, P3, Pz, P4, P8, O1, O2 | SciRep p10; README; `sub-01/eeg/*_channels.tsv` (all 35 subjects have 19 channels, my count) |
| Sampling rate | **250 Hz** | SciRep p10; `*_eeg.json` `SamplingFrequency`; .set `srate` = 250 |
| Recording reference | **Earlobes for the short session, FCz for the long session**. Both were later re-referenced to the average | SciRep p10; README |
| Impedance | under 20 kΩ | SciRep p10; README |
| Amplifier / manufacturer | **Not reported** in SciRep, bioRxiv, README, or the sidecars | searched all four |
| Site | Ziaeian Hospital, Department of Geriatric Medicine, Tehran, Iran | `*_eeg.json` (`InstitutionName`, `InstitutionalDepartmentName`, `InstitutionAddress`); SciRep p1 affiliations and p9 |
| Line frequency | 50 Hz | `*_eeg.json` `PowerLineFrequency` |
| Ethics | Tehran University of Medical Sciences Review Board, IR.TUMS.MEDICINE.REC.1398.524 | SciRep p9; README |

### A5. Preprocessing already applied by the dataset authors
This matters because the abstract says "offline preprocessing" and because the released files are **not raw**.
- **What the papers say** (SciRep p11; README; bioRxiv p15 l.422–429), following "Makoto's preprocessing pipeline":
  1. high-pass filter above 1 Hz
  2. line-noise removal
  3. rejection of bad channels
  4. interpolation of the rejected channels
  5. re-reference to the average
  6. **artifact subspace reconstruction (ASR)**
  7. re-reference to the average again
  8. **ICA**
  9. dipole fitting
  10. rejection of bad dipoles (sources)

  All of this was done in EEGLAB in MATLAB. SciRep adds that the data were then z-normalized per channel "for further analysis".
- **Sidecar metadata:** `SoftwareFilters` = "1Hz high pass filter, 50Hz notch filter" and `EEGReference` = "average" (every `*_eeg.json`).
- **What the released .set files show.** I opened them read-only with h5py in the scratch venv; they are MATLAB v7.3 files. Findings:
  - Every `setname` has the form "S<n>_Clean", so these are the authors' **cleaned** data.
  - Summing the 19 channels gives 0 at every sample (checked on sub-01, 09, 22, 30), which confirms the **average reference**.
  - The data are **not z-normalized**. Channel standard deviations range from about 1.4 to 10 (sub-01, 09, 22, 30), so the per-channel normalization happened only in the authors' own analysis.
  - Every file has ICA weights (`icaweights` is 19×15 to 19×18). However, `reject.gcompreject` is all zeros and no `pop_subcomp` call appears in any file's history. **So there is no record that independent components were removed from the channel data**, though this cannot be proven either way because the stored histories are partial.
  - The EEGLAB `history` field records ASR (`pop_clean_rawdata`, `BurstCriterion`) with **thresholds that differ between participants: 3, 5, 7, or 10 SD**. For example, sub-01 used 10, sub-02 used 7, sub-22 to sub-30 mostly used 5, and sub-17 and sub-29 used 3.
  - Some histories also show a 1–70 Hz band-pass (`pop_eegfiltnew`, locutoff 1 / hicutoff 70; sub-01, sub-14, sub-15, sub-16). Others show channel rejection and interpolation.
  - Histories are incomplete for many subjects (often only reref and ASR are logged), so **the exact preprocessing for each participant cannot be fully reconstructed**.
  - **Privacy note:** the history strings include original set names that look like participant surnames. Do not show `EEG.history` on slides or in shared material.
- **For the talk:** the recordings were cleaned by the dataset authors over each whole recording before release. That cleaning (ASR and ICA fitted on the full session) used future samples, and the ASR settings differed between participants. This is exactly what "offline preprocessing" refers to in the limitations. The repo JSON says the same thing: `early_late_connectivity_analysis.json` → `method_guardrails.source_preprocessing_note` ("The public EEG had already undergone whole-recording offline preprocessing; ... not a streaming-causal validation").

### A6. Participants, diagnosis, age, MMSE
- **Recruitment:** "Thirty-five volunteers (17 females, 54–89 years of age) were recruited from referrals to the memory clinic of Ziaeian Hospital in Tehran with memory performance complaints" (SciRep p9, "Participants").
- **How diagnosis was made:** a neuropsychologist from the Department of Geriatric Medicine did the clinical procedures. Cognitive status was quantified with the **MMSE**. "A neurologist examined the probable AD state in each participant according to the latest guideline of the **NIA-AA**" (SciRep p9, ref 61). bioRxiv p14 l.398–405 adds that a FAST functional assessment was done; it also says "neurophysiologist" where SciRep says "neuropsychologist".
- **Exclusion criteria:** history of stroke, TBI, schizophrenia, major depressive disorder, or ECT in the prior 6 months, or other neurodegenerative disease (PD, MSA, CBD, PSP) (SciRep p9–10).
- **Two participants excluded in the source paper:** "Two participants (P6 and P13) were excluded from the study as the diagnosis of their status required further examination" (SciRep p10). In `participants.tsv`, sub-06 and sub-13 have Group "-" and MMSE "-". **The source paper analyzed 33 participants** (for example, its paired t-tests have t32). **This talk analyzes all 35.** The repo provenance records `source_exclusions: ["sub-06","sub-13"]` together with `n_participants: 35`. Expect a Q&A question on this. "Mixed memory-clinic cohort" is an accurate description.
- **Counts from `participants.tsv`** (my tabulation of all 35):
  - Groups: Mild AD 16, Normal 10, MCI 6, Moderate AD 1, unlabeled 2.
  - Sex: 18 male, 17 female.
  - Age: 54–89 years, mean 72.7, SD 9.1, median 75.
  - MMSE (n = 33): 13–30, mean 22.3, SD 4.9, median 23.
- **Group by session:** the 8 short-session participants are 3 Normal, 4 Mild AD, and 1 unlabeled (sub-06). **All MCI participants and the Moderate AD participant had long sessions.** So session length is confounded with the original reference electrode and partly with diagnostic group.
- **Labels and MMSE scores that look inconsistent** (flag only; diagnosis came from a neurologist, not an MMSE cutoff): sub-21 is "Mild AD" with MMSE 30, sub-24 is "Moderate AD" with MMSE 23, and sub-19 is "MCI" with MMSE 13.
- The SciRep demographic table is in the Supplementary Material (Table 1), which is not stored locally. The per-participant table in bioRxiv Table 1 (p15) covers the first 13 participants only and matches `participants.tsv` for S1–S13.

### A7. Source-paper findings that are useful context (SciRep)
- The source paper also used frontal–parietal PLV at 40 Hz. It built bipolar sites from Fp1, Fp2, F3, Fz, F4 and P3, Pz, P4, O1, O2, giving 25 F2P sites. It used a second-order Butterworth filter with ±0.5 Hz bandwidth and 20 s windows, and excluded site pairs that share an electrode (SciRep p11–12). **The talk's channel sets, filter, and window match this**: `early_late_connectivity_analysis.json` → `provenance` has frontal_channels, posterior_channels, half_bandwidth 0.5, filter_order 2, analysis_window_sec 20, and `method_guardrails.n_bipolar_frontal_posterior_sites` 25. Cite Lahijanian 2024 as the source of this montage.
- It reported that "such stimulation does not necessarily cause notable entrained oscillatory activity in all brains" (SciRep p3). This is the heterogeneity that motivates an individual-level readout.
- Its Figure 4a caption says: "no cumulative effect is observed over the entire duration of the task" (SciRep p11). This is consistent with comparing early and later cycles.
- In its limitations, the source paper says "it is essential to evaluate the predictive potential of the ER index in determining the efficacy of the therapy" (SciRep p8, "Limitations and future directions").

---

## B. References checked (Crossref metadata and PubMed abstracts)

Metadata came from the Crossref API (`https://api.crossref.org/works/<DOI>`). Abstracts came from PubMed E-utilities and are saved in `pubmed_abstracts.txt`.

**Core references (all verified):**
1. Iaccarino HF, Singer AC, Martorell AJ, Rudenko A, Gao F, Gillingham TZ, Mathys H, Seo J, Kritskiy O, Abdurrob F, Adaikkan C, Canter RG, Rueda R, Brown EN, Boyden ES, Tsai LH. Gamma frequency entrainment attenuates amyloid load and modifies microglia. *Nature*. 2016;540(7632):230–235. doi:10.1038/nature20587. PMID 27929004.
   - Content: optogenetic 40 Hz drive of FS-PV interneurons, **plus 40 Hz light flicker** (not sound), reduced Aβ1-40/42 in the visual cortex of AD-model mice.
   - Author Corrections: *Nature* 562:E1 (2018), doi:10.1038/s41586-018-0351-4; and *Nature* 636:E2 (2024-11-26), doi:10.1038/s41586-024-08343-7. The 2024 correction updated the first author's name to **Hunter F. Iaccarino** (per the search-result summary of the correction page). "Iaccarino HF" remains correct.
2. Martorell AJ, Paulson AL, Suk HJ, Abdurrob F, Drummond GT, Guan W, Young JZ, Kim DNW, Kritskiy O, Barker SJ, Mangena V, Prince SM, Brown EN, Chung K, Boyden ES, Singer AC, Tsai LH. Multi-sensory gamma stimulation ameliorates Alzheimer's-associated pathology and improves cognition. *Cell*. 2019;177(2):256–271.e22. doi:10.1016/j.cell.2019.02.014. PMID 30879788.
   - Content: 7 days of auditory 40 Hz stimulation improved memory and reduced amyloid in the auditory cortex and hippocampus of 5XFAD mice. Combined auditory and visual stimulation reduced amyloid in mPFC.
3. Chan D, Suk HJ, Jackson BL, Milman NP, Stark D, Klerman EB, Kitchener E, Fernandez Avalos VS, de Weck G, Banerjee A, Beach SD, Blanchard J, Stearns C, Boes AD, Uitermarkt B, Gander P, Howard M 3rd, Sternberg EJ, Nieto-Castanon A, Anteraper S, Whitfield-Gabrieli S, Brown EN, Boyden ES, Dickerson BC, Tsai LH. Gamma frequency sensory stimulation in mild probable Alzheimer's dementia patients: Results of feasibility and pilot studies. *PLOS ONE*. 2022;17(12):e0278412. doi:10.1371/journal.pone.0278412. PMID 36454969.
   - Content: a Phase 1 feasibility study and a Phase 2A single-blind, randomized, placebo-controlled pilot (n = 15, 3 months). 40 Hz light and sound was well tolerated and induced EEG entrainment. Exploratory outcomes favored the active group.
   - Conflict of interest: Tsai and Boyden are Cognito co-founders.
4. Lahijanian M, Aghajan H, Vahabi Z. Auditory gamma-band entrainment enhances default mode network connectivity in dementia patients. *Sci Rep*. 2024;14:13153. doi:10.1038/s41598-024-63727-z. Published online 2024-06-07; received 2023-07-11; accepted 2024-05-31 (SciRep p13).
   - Dataset: Lahijanian M, Aghajan H, Vahabi Z. 40Hz Auditory Entrainment [dataset]. OpenNeuro; 2025. v1.0.1. doi:10.18112/openneuro.ds005048.v1.0.1. (v1.0.0, 2024, doi:10.18112/openneuro.ds005048.v1.0.0, has the same data.)
   - Optional preprint: Lahijanian M, Aghajan H, Vahabi Z, Afzal A. Gamma entrainment improves synchronization deficits in dementia patients. bioRxiv 2021. doi:10.1101/2021.09.30.462389. The title is from the PDF; I did not check the preprint's metadata against Crossref.
5. Lachaux JP, Rodriguez E, Martinerie J, Varela FJ. Measuring phase synchrony in brain signals. *Hum Brain Mapp*. 1999;8(4):194–208. doi:10.1002/(SICI)1097-0193(1999)8:4<194::AID-HBM4>3.0.CO;2-C. (PLV)
6. Stam CJ, Nolte G, Daffertshofer A. Phase lag index: Assessment of functional connectivity from multi channel EEG and MEG with diminished bias from common sources. *Hum Brain Mapp*. 2007;28(11):1178–1193. doi:10.1002/hbm.20346. (PLI)
7. Vinck M, Oostenveld R, van Wingerden M, Battaglia F, Pennartz CMA. An improved index of phase-synchronization for electrophysiological data in the presence of volume-conduction, noise and sample-size bias. *NeuroImage*. 2011;55(4):1548–1565. doi:10.1016/j.neuroimage.2011.01.055. (wPLI)

**State of the field as of 2026-09-27:**
8. Soula M, Martín-Ávila A, Zhang Y, Dhingra A, Nitzan N, Sadowski MJ, Gan WB, Buzsáki G. Forty-hertz light stimulation does not entrain native gamma oscillations in Alzheimer's disease model mice. *Nat Neurosci*. 2023;26(4):570–578. doi:10.1038/s41593-023-01270-2. PMID 36879142.
   - Content: in APP/PS1 and 5xFAD mice, 40 Hz **light** flicker did not engage native gamma oscillations in visual cortex, entorhinal cortex, or hippocampus. It produced no reliable changes in plaques, microglia, or Aβ40/42.
   - Scope: visual stimulation only; auditory stimulation was not tested.
9. Murdock MH, Yang CY, Sun N, Pao PC, Blanco-Duque C, Kahn MC, Kim T, Lavoie NS, Victor MB, Islam MR, Galiana F, Leary N, Wang S, Bubnys A, Ma E, Akay LA, Sneve M, Qian Y, Lai C, McCarthy MM, Kopell N, Kellis M, Piatkevich KD, Boyden ES, Tsai LH. Multisensory gamma stimulation promotes glymphatic clearance of amyloid. *Nature*. 2024;627(8002):149–156. doi:10.1038/s41586-024-07132-6. PMID 38418876.
   - Content: in 5XFAD mice, multisensory 40 Hz stimulation increased CSF influx and ISF efflux. Blocking glymphatic clearance abolished amyloid removal. VIP interneurons were implicated.
10. Hajós M, Boasso A, Hempel E, et al. Safety, tolerability, and efficacy estimate of evoked gamma oscillation in mild to moderate Alzheimer's disease. *Front Neurol*. 2024;15:1343588. doi:10.3389/fneur.2024.1343588. PMID 38515445. This is the OVERTURE trial, NCT03556280.
    - Design: randomized, double-blind, sham-controlled, 6 months, n = 76.
    - Results: safe and well tolerated. **There was no separation between active and sham on the primary efficacy outcome (MADCOMS) or on CDR-SB or ADAS-Cog14.** ADCS-ADL, MMSE, and whole-brain volume showed nominally significant reductions in progression.
    - Conflict of interest: the authors are Cognito employees.
    - Company press materials instead quote "76%/77%/69% reductions". Do not use those numbers on a slide.
11. Chan D, de Weck G, Jackson BL, et al. Gamma sensory stimulation in mild Alzheimer's dementia: An open-label extension study. *Alzheimers Dement*. 2025;21(10):e70792. doi:10.1002/alz.70792. PMID 41137616.
    - Design: n = 5, 2 years of daily 40 Hz audiovisual stimulation.
    - Results: three women with late-onset AD kept strong EEG entrainment and declined less than matched registry controls. The other two did not show that benefit. Plasma was available for only 2 participants.
12. **HOPE pivotal trial (Cognito Therapeutics, Spectris), NCT05637801.**
    - ClinicalTrials.gov API (`https://clinicaltrials.gov/api/v2/studies/NCT05637801`, status verified 2026-09, last update posted 2026-09-09) lists it as "A Randomized, Double-blind, Sham-controlled Pivotal Study". Overall status is **COMPLETED**: primary completion 2026-06-22, study completion 2026-08-17, actual enrollment **673**. **hasResults = false.**
    - Cognito's clinical-studies page (https://www.cognitotx.com/clinical-studies) says "fully enrolled" with 673 participants at 70 US sites and gives no results.
    - A 2026-03-17 AD/PD press release (https://www.biospace.com/press-releases/cognito-therapeutics-presents-new-data-on-spectris-in-alzheimers-disease-at-ad-pd-2026) presented only OVERTURE EEG analyses.
    - Earlier releases gave expected topline timing as "2026" (https://www.businesswire.com/news/home/20250701375054/en/). The primary endpoint is a composite of ADCS-ADL and MMSE, according to secondary press coverage; I did not confirm this on the registry.
    - **UNCERTAIN:** my searches up to 2026-09-27 found **no public topline HOPE result**. Say "results pending" or "not yet reported". Do not state a positive or negative outcome.

**Flags:**
- Iaccarino 2016 used light, not sound. Cite Martorell 2019 for the auditory stimulation work.
- Soula 2023 tested light only. Present it as "mixed replication", not as "auditory stimulation fails".
- Most positive human data come from small, industry-affiliated studies. Pivotal efficacy results have not been published.

---

## C. Recommended slide sentences

**Motivation slide.** Pick one version.
- Full: "Forty-hertz light and sound reduced Alzheimer's-like pathology in mice [Iaccarino 2016; Martorell 2019], but findings have not replicated consistently [Soula 2023], and human efficacy remains unproven: small trials show safety and EEG entrainment [Chan 2022; Hajós 2024], while pivotal results are still pending (HOPE, NCT05637801)."
- Short: "40-Hz sensory stimulation reduced Alzheimer's-like pathology in mice [Iaccarino 2016; Martorell 2019], but replication is mixed [Soula 2023] and benefit in patients is not yet established [Chan 2022; Hajós 2024]."
- Avoid: "reduces amyloid in patients", "improves cognition in AD", or "shown effective". The README's "shown effective in improving several symptoms" goes beyond the evidence.

**Why an early readout matters.**
- "Not every brain entrains to 40-Hz sound [Lahijanian 2024], so an EEG measure taken within the first minutes of a session could, if validated prospectively, help decide whether and how to adjust stimulation for each person."
- Supporting evidence:
  - SciRep p3: stimulation "does not necessarily cause notable entrained oscillatory activity in all brains".
  - SciRep p8: the predictive value of an entrainment index for therapy efficacy has not yet been evaluated.
  - bioRxiv p14 l.378–389: effective cycle duration "may be different for each participant and need customized tuning".
  - Chan 2025: entrainment and apparent benefit differed between individuals.
- Keep "if validated prospectively". The talk shows within-session tracking only. It does not show that the readout predicts clinical benefit or that adaptive stimulation works, which matches the abstract's final sentence.

**Methods-slide wording that is safe to use:**
- "Speaker-delivered 40-Hz train of 1-ms, 5-kHz tone pips (4% duty cycle), eyes open; 40 s on / 20 s silence; 6 or 10 cycles (participant-chosen session length); 19-channel EEG at 250 Hz, cleaned by the dataset authors (1 Hz high-pass, line-noise removal, ASR, average reference) [Lahijanian 2024]."
- "35 memory-clinic participants: 10 cognitively normal, 6 MCI, 17 AD (16 mild, 1 moderate), 2 unclassified; age 54–89; MMSE 13–30 (n = 33)" (`participants.tsv`).
