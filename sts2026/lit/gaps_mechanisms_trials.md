# Gaps: 40 Hz (GENUS) mechanisms, disputes, human trials, ASSR

Companion to `lit_mechanisms_trials.csv` (70 rows). Row ids are in brackets. Searches and checks ran on 2026-09-30 using PubMed E-utilities, Crossref, the ClinicalTrials.gov API v2, GEO and the OpenNeuro API. "Not found" means not found by these searches. It does not prove a study doesn't exist. Items marked **[speculation]** are my interpretation, not a reported finding.

## 1. Does 40 Hz light reach the hippocampus?

- **Mouse data on hippocampal entrainment conflict, and the two sides never used the same protocol.**
  - Positive: Tsai lab LFP [M06].
  - Negative: silicon probes [D01] and Neuropixels [D04], where phase locking was absent in CA1.
  - Nobody has run a shared-protocol replication across labs with matched luminance, duty cycle, arousal state and recording method. Luminance may matter: high-intensity light (1100-1500 lux) had hippocampal effects in 3xTg mice but 100-500 lux did not [M21].
- **The dispute is partly about what "entrainment" means, and it was never settled in peer review.**
  - The Tsai-lab reply [D03] is still a bioRxiv preprint.
  - No Matters Arising or published reply to Soula 2023 [D01] was found in Crossref or PubMed.
- **Human hippocampal entrainment comes only from epilepsy patients with intracranial electrodes.**
  - n=11 [D05] and n=2 [H01]. No patients with AD pathology were recorded.
  - Task engagement increased entrainment [D05], and competing sound abolished the 40 Hz response [A08].
  - **[speculation]** Behavioral state may reconcile the mouse results: in [D01] the mice found the flicker aversive, while in [D05] the humans were attending to it.
- **Driven 40 Hz responses and native gamma are dissociable, but only one small human study shows it.**
  - In humans, native stimulus-induced gamma was lower in MCI/AD while steady-state responses were not [A07] (MCI n=12, AD n=5).
  - In mice, flicker did not engage native gamma [D01] and preferentially drove fast-spiking interneurons [D04].
  - No study measures both native and driven gamma before and after chronic GENUS in the same AD patients.

## 2. Amyloid and tau: does 40 Hz stimulation clear pathology?

- **Visual-only flicker has failed to reduce amyloid in two independent labs** [D01, D02]. The original visual-cortex result [M01] was never independently replicated using its own protocol.
  - Independent positive results used audiovisual stimulation [M20] or very bright light [M21].
  - **[speculation]** Modality and dose may explain the split. No study has tested this directly.
- **Direct human amyloid evidence is almost absent.**
  - The only amyloid-PET study is an uncontrolled, 10-day study of n=6 with a null result [D06].
  - No controlled 40 Hz sensory trial in the table reports an amyloid-PET change. For [H03], the amyloid outcome is not stated in the abstract, so the full text needs checking.
  - Tau PET: n=4, and that was tACS, not sensory stimulation [T03].
  - Plasma pTau217: n=2 [H02].
  - Plasma AD biomarkers were unchanged in two tACS studies [T05, T06].
- **The only primate study shows CSF amyloid going up, and it has no sham group** [M23] (n=9 aged macaques, auditory only).
  - A rise in CSF Abeta is ambiguous. It could mean clearance into CSF, or it could mean something else.
  - No human study measured CSF Abeta or tau before and after 40 Hz sensory stimulation. The only human CSF study is proteomics in n=5 without FDR correction [H08].

## 3. Clearance, vessels and sleep

- **The glymphatic mechanism rests on two mouse studies, and the method itself is contested.**
  - The two studies: [M10] (Tsai lab, audiovisual) and [M14] (independent lab, visual only, adenosine pathway).
  - Both depend on tracer-based clearance measurements. Those measurements are disputed: [D08] reports clearance is reduced during sleep, while [D09, D10] report it is enhanced.
  - No human study has measured glymphatic or CSF-flow changes under 40 Hz sensory stimulation. **[speculation]** CSF-inflow fMRI or DTI-ALPS could test this.
- **Sleep may be a confound for both clearance and cognition, and nobody has separated it out.**
  - 40 Hz light increased NREM and REM sleep in mice and in children with insomnia [M15].
  - A human trial reported better nighttime sleep [H04].
  - Glymphatic clearance may depend on sleep-stage vasomotion [D09].
  - No study separates a sleep-mediated pathway from a direct 40 Hz effect.
- **Cholinergic signalling has two opposite readings.**
  - The Tsai lab says acetylcholine is required for clearance [M16], but this is a preprint.
  - Soula et al. interpret hippocampal cholinergic activity as a sign that the flicker is aversive [D01].
  - The same observation is used on both sides. No study has tested aversion-matched control stimuli.
- **The vasomotion data are thin.**
  - Healthy mice, surface cortex only [M22].
  - VIP-interneuron-driven arterial pulsatility comes from a single lab [M10].
  - Human perfusion data exist only for tACS [T04], not for sensory stimulation.

## 4. Myelin, oligodendrocytes and other cell types

- **Evidence that 40 Hz protects myelin comes from non-AD mouse models and a single sponsor's trial.**
  - Mouse: cuprizone in males only [M11], and chemotherapy models [M12].
  - Human: MRI post hoc analyses of one trial by the sponsor [H06, H07], plus CSF proteomics in n=5 [H08].
  - No study was found that examines oligodendrocytes or myelin under chronic GENUS in an amyloid or tau model.
- **Neurogenesis claims rest on non-AD models.** Down syndrome mice [M13], healthy aging mice [M18], and a 3-week treatment in [M13].
- **Many mechanism studies used male mice only** [M07, M11, M13]. Sex as a variable was flagged as a source of heterogeneity in the most recent review [D13].

## 5. Human efficacy

- **Only one published sham-controlled trial lasting months has more than 50 patients (OVERTURE, n=76) [H05], and it missed its primary efficacy composite (MADCOMS).**
  - The positive signals are nominal secondary or post hoc outcomes: ADCS-ADL, MMSE, brain volume, white matter and corpus callosum.
  - Five papers report data from that one trial, all by sponsor authors [H04, H05, H06, H07, H09].
  - A 2025 meta-analysis (11 studies) found no significant cognitive or ADL effect [H20].
- **The pivotal HOPE trial has finished, but its results are not public** [H14].
  - n=673. Completed 2026-08-17. No results were posted on ClinicalTrials.gov as of the last update (2026-09-09).
  - No topline press release was found up to 2026-09-30.
  - Until results appear, the clinical question is open.
- **Durability evidence is anecdotal.**
  - The only multi-year data are open-label, n=5, with external controls [H02].
  - The mouse chemobrain study showed benefit mainly when treatment was given early [M12].
- **Some people may not respond at all, and no trial has tested this.**
  - About 30% of screened early-AD patients showed no baseline entrainment [H18].
  - In the long-term extension, only patients with late-onset AD kept strong entrainment [H02].
  - A review found that neural response did not reliably predict benefit [H21].
  - No randomized trial has stratified or enriched patients by baseline 40 Hz responsiveness.

## 6. Auditory-only 40 Hz in humans

- **Auditory-only 40 Hz stimulation in people with AD has been measured only in small or uncontrolled studies.**
  - Vibroacoustic sound without EEG [H10] (n=18, non-blinded) and [H11] (n=3).
  - Acute, single-session EEG from one Iranian group, published with open data [H12, H13] (OpenNeuro ds005048 and ds003800).
  - One registered 3-arm MCI trial has registry results only and no paper [H17]. Its episodic-memory change showed no obvious advantage for 40 Hz sound or music over preferred music.
  - No sham-controlled auditory-only RCT in AD combining EEG with a biomarker was found.
- **Preclinical auditory-only evidence is thin.** One 7-day mouse study from one lab [M05], and one primate study without sham [M23]. Auditory-only amyloid reduction [M05] has not been independently replicated in rodents.

## 7. The 40 Hz ASSR as a biomarker

- **Human 40 Hz ASSR is NOT reduced in AD. The small studies that exist show it is increased.**
  - Increased in AD: EEG, 15 AD patients [A01]; MEG [A02].
  - The ASSR also rises with healthy aging [A04], and larger ASSR tracked cognitive decline in older adults [A06].
  - Findings across adulthood are heterogeneous [A05].
  - The only other clinical study used an audiological threshold measure [A03].
  - This contradicts the idea that AD brains "lack" 40 Hz and need it restored. Mice show the opposite: early ASSR loss in APP/PS1 mice [M25], a cross-species mismatch.
- **No study was found relating 40 Hz ASSR to amyloid or tau biomarkers (PET, CSF or plasma), or tracking it longitudinally across the AD continuum.** The studies are small (n=15-35 per group), from 2006-2017, and at mild-AD stages [A01, A02, A03].
- **[speculation]** An elevated ASSR in AD may reflect reduced inhibition [A02]. If so, pushing harder at 40 Hz may not be restorative in everyone. No study has tested this.

## 8. Comparison with tACS

- **Gamma-tACS RCTs showing clinical benefit come mostly from one Italian group** [T01, T02, T06].
  - Biomarker changes are absent [T05, T06] or come from n=4 [T03].
  - No study compares tACS with sensory 40 Hz in the same patients, or combines them against sham. One such combination trial is registered (NCT05251649, status unknown). It was noted from the CT.gov search but has no row in the table.

## 9. Devices and consumer products

- **Commercial "invisible" 40 Hz lamps may not entrain at all.** One lamp was tested and showed none [D11]. No other consumer products were checked with EEG in this search.

---

## Public 40 Hz omics datasets

All accessions were checked through GEO (and the OpenNeuro API for EEG) on 2026-09-30. For every GEO series, the supplementary-file URL returned HTTP 200 on NCBI's https FTP mirror, so the files can be downloaded directly with no access request. All are mouse. **No human or primate 40 Hz omics dataset was found.**

| Accession | Row | Species / model | Tissue | Stimulation | Assay / n | Files (directly downloadable?) |
|---|---|---|---|---|---|---|
| GSE77471 | M01 | Mouse 5XFAD | Hippocampus CA1 | Optogenetic 40 Hz (not sensory), 1 h | Bulk RNA-seq, 6 samples | Differential-expression table, 0.8 MB (yes; raw data in SRA SRP069184) |
| GSE115244 | M06 | Mouse CK-p25, Tau P301S, WT | Visual cortex (microglia per summary) | Chronic visual GENUS vs no stimulation | RNA-seq, 43 samples | RAW.tar, 5.6 MB (yes) |
| GSE249644 | M10 | Mouse 5XFAD, 6 months | Cortex | 1 h audiovisual 40 Hz then 1 h rest vs no stimulation | snRNA-seq (10x), 8 libraries = 4 pools of 3 mice per group | counts.rds 259 MB + meta.rds (yes, R format) |
| GSE240815 | M11 | Mouse C57BL/6J male, cuprizone and normal diet | Corpus callosum | Long-term audiovisual GENUS vs no stimulation | snRNA-seq (10x), 16 mice, ~37k nuclei | RAW.tar, 2.2 GB (yes) |
| GSE216146 | M12 | Mouse, cisplatin vs PBS | Hippocampus | Audiovisual GENUS vs no stimulation | scRNA-seq, 12 samples | h5ad 669 MB + mtx/genes/metadata (yes) |
| GSE243390 | M13 | Mouse Ts65Dn male | Hippocampus | 3 weeks of 1 h/day audiovisual 40 Hz vs ambient | snRNA-seq (10x), 6 samples | Seurat RData, 60 MB (yes) |
| GSE226822 | M08 | Mouse WT male | Visual cortex | 1 h ambient vs 20 Hz vs 40 Hz audiovisual | Bulk RNA-seq, n=4/group, 12 samples | RAW.tar, 588 MB (yes) |
| GSE225842 | M08 | Mouse WT (B6SJL background) | Visual cortex | 1 h 20 Hz vs 40 Hz | Bulk RNA-seq, 14 samples (n=7/group) | Normalized-counts CSV, 1.2 MB (yes) |
| GSE255004 | M19 (linkage UNCONFIRMED) | Mouse WT and 5xFAD | Visual cortex and hippocampus | Light, 10, 20 and 40 Hz flicker; 3 time points | Transcriptomic counts, 176 samples | Raw-count CSV, 3.1 MB (yes) |
| OpenNeuro ds005048 | H12 | Human older adults with dementia | Scalp EEG (not omics) | 40 Hz auditory | EEG, 35 subjects, ~373 MB | Yes (BIDS) |
| OpenNeuro ds003800 | H13 | Human, normal aging and mild AD | Scalp EEG (not omics) | 40 Hz auditory chirp | EEG, 13 subjects | Yes (BIDS) |

Notes on this table:

- **GSE255004's link to a paper is unconfirmed.** GEO has no PubMed link for it, and its title ("Sensory Flicker Stimulation of 5xFAD Mice Activates Immune Pathways in a Frequency and Time Dependent Manner") differs from the title of [M19]. The design (Singer-lab style: frequency x duration, visual cortex and hippocampus) matches, but the link needs confirming before you cite it.
- **Gaps in the omics data:**
  - Only GSE255004 and GSE226822/GSE225842 include non-40 Hz frequency controls.
  - Only GSE115244 covers chronic stimulation in a neurodegeneration model.
  - There is no single-nucleus dataset of the **hippocampus** in an **amyloid** model after chronic 40 Hz stimulation.
  - Every dataset comes from the Tsai lab (MIT) or the Singer lab (Georgia Tech/Emory).
- **Not found in GEO** (PubMed-to-GEO link empty): [M05] Martorell 2019, [M07] Garza 2020, [M19] by direct link, and the human CSF proteomics [H08]. For [H08], a PRIDE/ProteomeXchange deposit was not checked.
