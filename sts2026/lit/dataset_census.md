# Public dataset census for independent replication of 40 Hz entrainment findings

Compiled 2026-09-30. Results must be frozen by 2026-10-25.
Reference dataset already in hand: OpenNeuro **ds005048**. It has 35 memory-clinic patients, a 5 kHz carrier with 40 Hz 4%-duty clicks, 40 s on / 20 s off blocks, and 19-channel EEG at 250 Hz.

**Verification rule.** Every ID below was fetched live during this census through an API listing, a file listing, an HTTP HEAD or range-GET, or a full download. A "Verified" entry names the test used. Nothing here comes from memory.
**Total downloaded:** about 330 MB (scratchpad only). Nothing was added to the repo.

Legend for the suitability columns:
- (a) individual-difference stability / test-retest
- (b) entrainment vs evoked-superposition (on/offset dynamics, periodic-vs-random controls, multi-frequency resonance)
- (c) aging / diagnosis effects
- (d) closed-loop / forecasting

`++` = directly designed for this. `+` = usable. `–` = not usable.

---

## 1. Main table: open, downloadable now, sorted by usefulness

| # | Dataset (ID / URL) | Modality | N & population | Stimulation | Channels / fs / format | Size | License / access | Verified | a | b | c | d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Chan et al. 2022 (Tsai lab) GENUS human trial**. Harvard Dataverse `doi:10.7910/DVN/56XZ3F` (PLoS One 10.1371/journal.pone.0278412) | Scalp EEG (plus T1/rs-fMRI for the Phase 2A patients) | **Phase 1:** 13 young cognitively normal (CN; 25.6±3.9 y), 12 older CN (64.9±6.3 y), 16 mild AD (75.8±7.9 y, MMSE med 22). **Phase 2A:** 15 mild AD (7 sham, 8 active), EEG at baseline and 3 months | 40 Hz **clicks at 4% duty (same stimulus family as ds005048)**, 40 Hz light flicker, and audiovisual (AV). **Controls:** 25-min session of 1-min baselines alternating with 3-min blocks of periodic vs **random-jitter (±5 ms)** audio / visual / AV, plus a 3-min constant-light test. **AD Phase 1:** 13-min session of 1-min blocks (periodic audio-only, periodic visual, periodic AV, constant noise/light) alternating with 1-min baselines. **Phase 2A:** 5-min session (1-min periodic AV and constant AV, with baselines). Block order varies by subject; use the per-subject `*_Notes.txt`. The Status channel marks block boundaries | BioSemi 32 ch plus EOG and mastoids, 512 Hz, BDF | EEG 4.3 GB (Phase 1 CN 2.9, Phase 1 AD 0.8, Phase 2A 0.6); total 5.4 GB | CC0, open, no login | Downloaded `HG204_EEG3months.bdf` (41 ch, 512 Hz, 300 s, 4 block triggers), notes and demographics. 40 Hz SNR was 4.6 in the periodic-AV minute vs 0.8–1.8 in baseline and constant minutes | ++ (Phase 2A sham arm = 3-month retest in AD; repeated blocks within session) | ++ (periodic vs random-jitter at matched pulse count; on/off every 1–3 min) | ++ (young vs older CN vs mild AD, same protocol) | + (block design with baselines) |
| 2 | **OpenNeuro ds005185** (Ear-EEG Sleep Monitoring 2019, EESM19), `task-ASSR` | Scalp PSG EEG (F3/F4/C3/C4/O1/O2/M1/M2) plus 12 ear-EEG channels | 20 healthy adults, 22–36 y | ~4 min **continuous 40 Hz AM noise** before sleep on **4 separate nights per subject** (80 recordings). The 1-s triggers are only in `sourcedata/*/ASSR/*.mat` (row 36) | 500 Hz; EEGLAB .set/.fdt plus source .mat | ASSR files ≈2.0 GB (full dataset 287 GB; download only `*task-ASSR*`) | CC0 | Downloaded sub-001 ses-001 .set/.fdt/.mat. 241 one-second epochs. F3–O1 inter-trial coherence (ITC) at 40 Hz = 0.69 vs 0.06 at neighbouring frequencies; ear-EEG ITC 0.2–0.4. M2 is noisy, so avoid M2 references | ++ (4 sessions × 20 subjects) | – (no off periods) | – | + (1-s trial series) |
| 3 | **NEMAR nm000166** (M3CV; Huang et al. 2022, NeuroImage), `task-ssaep` | EEG | 95 healthy young adults (21.3±2.2 y), **2 sessions on different days** | **45.38 Hz** AM 1 kHz tone, 2 min continuous (not exactly 40 Hz). Same sessions also include 1-min eyes-open and eyes-closed rest, 10 Hz SSVEP, 22 Hz somatosensory steady state (SSSEP) and 7–15 Hz SSVEP | 64 ch, 250 Hz. Preprocessed 4-s epochs concatenated into pseudo-continuous BrainVision files | ssaep: 1.15 GB for all 95×2; full dataset 21 GB | CC BY 4.0, open (`https://data.nemar.org/nm000166/v1.0.0/…`, use `curl -L`) | Downloaded sub-001 ses-01/02 (120 s each). ITC at the 45.25 Hz bin = 0.35 and 0.23. Epoch order may be shuffled, so do not assume phase continuity across 4-s epochs | ++ (largest test-retest N) | – | – | – |
| 4 | **OpenNeuro ds007648** (EEG) and **ds007663** (MEG), "CrossModal Study" (Brickwedde et al., eLife 10.7554/eLife.106050) | EEG / MEG | EEG: 22 young adults (18–27 y). MEG: 27 young adults (18–31 y). The two samples are independent | Every trial has a **3-s 40 Hz AM tone** (plus a 36 Hz visual tag) in the cue–target interval. About 468 trials at ~6 s spacing | EEG: ANT 63 ch, 500 Hz, BrainVision. MEG: Elekta 306 ch, 1000 Hz, FIF | EEG 7.7 GB (~350 MB/subject). MEG 142 GB (includes a 36 GB derivative .mat) | CC0 | Listed on S3. HEAD 200 on `sub-02_…_eeg.eeg` (360 MB). Events.tsv read | + (split-half over hundreds of trials) | ++ (hundreds of 3-s on/off trains, good for build-up/decay modelling) | – | + (trial-wise prediction) |
| 5 | **Stockholm Univ. figshare `10.17045/sthlmuni.7324898`** (Szychowska & Wiens 2020, Psychophysiology) | EEG | Study 1: N=43. Study 2: N=45. Healthy adults (ages in paper, not README) | **40.96 Hz AM** 500 Hz tone during visual-load task blocks (~29-min recording; triggers ~every 0.5 s) | Study 1 BDF has 8 channels (Nz, Fpz, Fz, FCz, Cz, M1, M2, Cheek) at 1024 Hz | Raw zips 1.17 GB (S1) and 3.17 GB (S2); preprocessed 7.5 / 15 GB | CC BY 4.0 | Extracted `assrs_fp01.bdf` (47 MB) from the remote zip via HTTP range requests and read its events. Single subjects can be pulled without the whole zip (`httpzip` approach) | + | + | – | – |
| 6 | **Stockholm figshare `10.17045/sthlmuni.12582002`** (Szychowska & Wiens 2021, Physiol Behav) | EEG | N=33 healthy adults | **20.48 / 40.96 / 81.92 Hz AM** tones (multi-frequency) | BioSemi BDF | Raw zip 3.08 GB | CC BY 4.0 | README read. Range-GET 206 on the raw zip | + | ++ (resonance across 20/40/80 Hz) | – | – |
| 7 | **OpenNeuro ds007509** (= newer version of **ds006222**, same 69 subjects; Attokaren & Singer, Georgia Tech) | EEG | 69 young adults (18–35 y). Between-subject arms: 40 Hz (n=24), constant light (21), **random flicker (24)** | **1 h continuous 40 Hz audiovisual flicker** during a psychomotor vigilance task (PVT) | BioSemi 32 ch, 512 Hz, EEGLAB | 15.9 GB (~230 MB/subject) | CC0 | S3 listing, participants, eeg.json and events read | + (within-hour drift) | + (random-flicker arm) | – | + (long continuous series) |
| 8 | **OpenNeuro ds006780** (SFARI_EEG multi-paradigm), `task-ASSR` | EEG | 138 children aged 8–13 (44 typically developing, 66 autism, 28 siblings); 123 have ASSR files | 500-ms click trains at **27 Hz and 40 Hz**, jittered ISI 488–788 ms, 15% oddballs | BioSemi 64 ch plus 8 EXG, 512 Hz, BDF | ASSR subset 6.7 GB (~54 MB/subject); full dataset 98 GB | CC0 | S3 listing and sidecar read | + | + (27 vs 40 Hz; short-train onset) | + (autism; developmental, not aging) | – |
| 9 | **Mouse hdEEG ASSR** (Hwang et al. 2019; Sci Data 2020). Zenodo `3949519` (also GIN `doi:10.12751/g-node.e5tyek`; Zenodo 3925288 is a duplicate) | Mouse epidural EEG | 6 PV-Cre mice | Dataset 1: **1-s click trains at 10/20/30/40/50 Hz**, 2-s ISI (3,728 epochs). Dataset 2: 40 Hz clicks plus basal-forebrain PV optogenetics at 4 phase lags (2,654 epochs) | 36 ch, 2 kHz, EEGLAB epochs | 9.24 GB zip; per-animal .fdt 0.28–0.76 GB can be extracted by range request | CC BY 4.0 | Remote zip central directory listed. Range-GET 206 | – | ++ (frequency tuning; phase-locked optogenetics) | – | ++ (phase-dependent causal modulation) |
| 10 | **DANDI 000535** (Allen OpenScope, periodic visual stimulation) | Mouse V1 2-photon calcium imaging (SST, VIP, PV, excitatory cells) | 15 mice, multiple sessions with matched cells | LED **40 Hz flicker vs 8 Hz vs Poisson-random (mean 40 Hz) vs constant**; light onset ~485 s into each session | NWB | 6.8 GB (115 files, median 23 MB) | CC BY 4.0 | Asset API listed. Range-GET 206 | – | ++ (periodic vs rate-matched random at cell-type level) | – | – |
| 11 | **Figshare `10.6084/m9.figshare.23641017`** (1–60 Hz SSVEP; Sci Data 2024, 10.1038/s41597-024-03023-7) | EEG | 30 healthy young adults | Single flicker at **1–60 Hz in 1-Hz steps**, 2 modulation depths | 64 ch, .mat (BIDS EDF per paper) | 21 GB; the API lists 16 files of ~1.3–1.5 GB each | CC BY 4.0 | Figshare API. Range-GET 206 | – | ++ (visual resonance curve through 40 Hz) | – | – |
| 12 | **OpenNeuro ds006036** (AHEPA photic stimulation; same participants as ds004504) | EEG | 88 participants: 36 AD, 23 frontotemporal dementia (FTD), 29 CN (ages 44–79) | Clinical photic stimulation at **5, 10, 15 (up to 30) Hz**, eyes open. No 40 Hz fundamental; 20 Hz second harmonic is at 40 Hz | 19 ch, 500 Hz, EEGLAB; high-cut 70 Hz; derivatives included | 1.13 GB | CC0 | S3 listing, participants and events (`Photo/HV mark`) read | – | + | ++ (AD vs FTD vs CN steady-state driving) | – |
| 13 | **Zenodo `21156618`** (Orange: 40 Hz AM natural/artificial sounds) | EEG | 48 participants in 2 loudness groups of 24 (ages not stated in record) | **10-s 40 Hz sinusoidal AM** of pure tone, cicada, cat purr and brown noise, plus silence. 6–10 s gaps; 2 runs × 50 trials | 24 ch mBrainTrain Smarting, 500 Hz | 2.27 GB (single RAR) | CC BY-NC-ND 4.0 | Record API. Range-GET 206. Not downloaded (budget) | + | ++ (10 s on / 6–10 s off; carrier effects) | – | + |
| 14 | **GIN `jonanyv/jonany_et_al_2025_opm_auditory_gamma`** (Jonany et al. 2026, Brain Stimulation) | OPM-MEG (16 sensors over left auditory cortex) | 19 participants | **40 Hz ASSR** runs without and with phase-lagged AM-tACS. **Stimulus waveform recorded** in LSL/XDF | XDF | 1.7 GB | CC BY 4.0 (LICENSE file) | GIN API plus raw README and LICENSE | + | + | – | ++ (closed-loop phase-dependent modulation) |
| 15 | **OSF `gq73d`** (Hainke et al. 2025 SLEEP; raw data in components `tqjm2`, `9ub4c`, `5xnwj`; derivatives in `gknwy`) | EEG / PSG | 32 young adults | **40 Hz light flicker during sleep** (experimental vs control night), plus a ~22-min session01 with ~1,200 stimulus triggers | 8 EEG ch, EDF | Raw ~65 GB (~1 GB/night); derivatives 28 MB (per-subject SSVEP metrics) | Public OSF | File trees listed. Annotation EDF and header downloaded | + (2 nights) | – | – | + (sleep-stage dependence) |
| 16 | **Zenodo `15008933`** (Kim … Al Borno 2025/26, Sci Rep; vibrotactile vs AV 40 Hz) | EEG | 15 healthy adults | 40 Hz vibrotactile glove vs 40 Hz AV (2 tasks) | OpenBCI 16 ch at **125 Hz** (marginal for 40 Hz), txt plus .set | 0.84 GB | CC BY 4.0 | Downloaded one .set (16 ch, 125 Hz, 355 s) | – | + | – | – |
| 17 | **Zenodo `14967041`** (Fragile X chirp; Pedapati, PLoS One 2025) | Source-localized EEG (68 Desikan ROIs from 128 ch at 1000 Hz) | 36 Fragile X (FXS) + 39 controls | Auditory **chirp** (sweep through gamma) | EEGLAB | 4.88 GB | CC BY 4.0 | Record API with file list | – | + (chirp resonance) | + (clinical) | – |
| 18 | **SEA-AD, AWS Open Data** (`s3://sea-ad-single-cell-profiling`, `…-spatial-transcriptomics`, `…-quantitative-neuropathology`) | Human snRNA-seq, ATAC and spatial data; quantitative neuropathology | 84 donors across the AD pathology (ADNC) spectrum; multiple regions | none (omics) | h5ad / CSV | Very large (MTG h5ad 18–39 GB; metadata CSV 1.1 GB) | Open, no DUA | S3 prefixes and README listed | – | – | + (PV-interneuron vulnerability vs ADNC) | – |
| 19 | **DANDI 001790** (GENUS vasomotion) | Mouse laser-speckle blood-flow imaging | 18 mice aged 18–60 wk | 1 h 40 Hz visual flicker vs constant light | NWB | 62 MB | CC BY 4.0 | Asset API. Range-GET 206 | – | – | – | – |
| 20 | **Zenodo `14178398`** (ASZED, African Schizophrenia EEG) | EEG | 153 participants (76 schizophrenia, 77 controls; ages 19–74) | "40 Hz ASSR" phase is **very short**: subsets 2/3 have 2 × ~2-s ASSR segments; subset 1 Phase 2 (15–120 s) is unlabeled | 19–20 ch, 200/256 Hz, EDF | 0.21 GB | CC BY 4.0 | **Fully downloaded.** Quick check of Phase 2 found median 40 Hz SNR ≈0.3–1.0 (about chance), so usefulness is low | – | – | (+) | – |
| 21 | **OSF `udes2`** (Vilnius; Parciauskaite 2019, PLoS One) | Derived 40 Hz ASSR ERSP/ITPC matrices plus cognitive CSV | 27 young males | 40 Hz click ASSR | .mat (derived only) | 14 MB | Public OSF | ITPC .mat downloaded | (+) | – | – | – |
| 22 | **OSF `gmq34` / `uk9nx`** (Masina et al. 2026; tACS + 40 Hz ASSR) | Derived gamma-PCA text exports, pre/post | ~30 participants | 40 Hz ASSR with/without 40 Hz tACS | txt | 62 MB | Public OSF | File tree and README read | – | – | – | + |

### Omics of 40 Hz stimulation (GEO, all open; supplementary folders listed on the NCBI FTP)

| GEO | Study | Design | Suppl. size | Use |
|---|---|---|---|---|
| **GSE226822** | Prichard/Garza et al. 2023, Sci Adv ("Brain rhythms control microglial response…") | WT mouse visual cortex: ambient light vs **20 Hz** vs **40 Hz** AV flicker, 1 h, n=4 each | RAW.tar 561 MB | **Frequency-specific** control (40 vs 20 Hz). Best for (iv) |
| **GSE225842** | same paper | 20 Hz vs 40 Hz, n=7 each | 1.1 MB normalized counts | Tiny download; quick replication of a frequency effect |
| **GSE249644** | Murdock et al. 2024, Nature (glymphatic) | 5XFAD cortex snRNA-seq: 1 h multisensory 40 Hz vs none, 4 vs 4 pooled replicates | counts.rds 247 MB + meta | Astrocyte/vascular genes |
| **GSE115244** | Adaikkan et al. 2019, Neuron | Microglia RNA-seq: CK-p25 and P301S ± 40 Hz visual GENUS (43 samples) | 5.4 MB | Microglial response |
| **GSE77471** | Iaccarino et al. 2016, Nature | 5XFAD CA1 **optogenetic** 40 Hz, 1 h, RNA-seq (6 samples) | 0.8 MB DE table | Classic dataset |
| GSE216146 | Tsai lab, chemo brain | Hippocampus scRNA: cisplatin ± 40 Hz AV, 1 h/day × 21 d | h5ad 638 MB | Chronic stimulation |
| GSE240815 | Rodrigues-Amorim et al. 2024 | Cuprizone ± GENUS, corpus callosum (16 samples) | RAW 2.1 GB | Myelin |
| GSE243390 | Down syndrome (Ts65Dn) ± 40 Hz AV, 3 wk | snRNA-seq hippocampus (6 samples) | 57 MB counts | Neurogenesis |

Other animal resource: **Soula et al. 2023** (Nat Neurosci, 40 Hz light does not entrain native gamma). NYU Data Catalog entry 10678 says "Free to All" via **Globus**, which needs a free Globus login. The transfer was not tested.

---

## 2. Gated by a DUA, login or request (not usable by Oct 25 unless noted)

| Resource | What it has | Gate | Verified | Note |
|---|---|---|---|---|
| **AMP SCZ** (NIMH Data Archive, NDA; `nda.nih.gov/ampscz`) | **40 Hz ASSR** plus MMN, P300 and rest in ~2,500 clinical-high-risk youths and controls, **baseline and 2-month retest** | NDA DUA plus institutional signing (weeks) | EEG SOP Zenodo `10472226`. Protocol paper (npj Schizophr 2025, PMC12144291) confirms 40 Hz ASSR | Best large test-retest ASSR, but not reachable in time |
| ROSMAP / AD Knowledge Portal (Synapse `syn3219045`, `syn2580853`) | Human AD omics | Synapse DUA | Synapse REST API returned entity names | Use SEA-AD (open) instead |
| Cam-CAN (`camcan-archive.mrc-cbu.cam.ac.uk`) | Lifespan MEG with passive tones (not steady-state) | DUA | Access page 200 | No 40 Hz stimulation |
| TDBRAIN (brainclinics.com) | Resting EEG, 1,274 patients | Registration/DUA | Page 200 | Rest only |
| MOUS (Donders DSC_3011020.09_236) | Language MEG/fMRI | Donders DUA | Page 200 | No ASSR |
| B-SNIP / COGS-2 (NDA) | Psychosis EEG | NDA DUA | Not verified to contain 40 Hz ASSR | Skip |
| Vilnius chirp data (Mockevičius 2023, Sensors 10.3390/s23052826: 80 young adults, 30–60 Hz click-chirps, 64 ch; Parciauskaite 2021/2023, J Pers Med) | Individual gamma frequency (IGF) from chirps | **"Available on request… not publicly available due to privacy restrictions"** (data-availability statements read via Europe PMC) | Yes | Only the derived 40 Hz ASSR set `udes2` is public |
| Japan older adults, 40 Hz AM safety study (PMC12564345) | Older-adult 40 Hz AM | On request (ethics) | DAS read | – |
| Metropolit Birth Cohort ASSR, ages 61–68 (PMC11832718) | 40 Hz ASSR vs cognitive decline | Restricted | DAS read | Would be ideal for (iii); not available |
| Human hippocampal 40 Hz visual iEEG (Commun Biol 2025, PMC12397345) | 40 Hz flicker, intracranial | On request | DAS read | Source data only |
| IGF-music study (Sci Rep 2025, PMC12589466) | Chirp-music IGF | Not shareable | DAS read | – |

---

## 3. Checked and not useful, not independent, or not existing (do not re-search)

- **ds003800 "Auditory Gamma Entrainment": NOT independent of ds005048.** Its 13 participants are ds005048 sub-01…13, with identical demographics and MMSE. The coordinator measured Cz cross-correlation r = 0.96–1.00 at a 5-s offset. Its only new content is a 1-min eyes-open pre-stimulation rest for 11 of 13. Same Tehran lab and ethics ID.
- ds003805: same lab, n=1 (40 Hz audio, 20 Hz flicker, AV), 40 s per condition.
- ds004504 (AHEPA AD/FTD/CN, 88): eyes-closed rest only. Usable as a rest reference; stimulation data are in ds006036.
- ds002778 and ds003490 (Parkinson's rest / 3-stim oddball), ds003655 (verbal working memory), ds003690 (young/older auditory reaction time; "40 Hz" is only a filter mention), ds004796 (PEARL-Neuro, AD-risk genes; rest, MSIT, Sternberg), ds005385 (608-subject lifespan rest), ds005420 (older women, rest), ds006466 (older adults, oddball), ds007427 (PSEN1 carriers, rest), ds004148 (test-retest rest/tasks): **no 40 Hz stimulation**. Rest-only aging/AD references at most.
- ds005408, ds005340, ds007721, ds008065, ds006735: auditory brainstem response (ABR) paradigms. ds005408 uses **Poisson click trains at an average 40 Hz rate**, but there is no periodic condition and the data are 40 GB, so they are not an ASSR.
- ds006468 (MEG-SCANS): the "chirps" are brief broadband up-chirps used for signal quality, not modulation chirps.
- ds002734, ds002739, ds008083, ds007688, ds007753, ds007763, ds006923, ds008834, ds000246: "40 Hz" appears only as a filter cutoff.
- ds004493 (40 Hz checkerboard, CSF flow): fMRI only. ds006407 (mouse optogenetic 40 Hz): fMRI only. ds004959 (rat 40 Hz electrical stimulation): fMRI only.
- HBN EEG releases ds005505–ds005516: "flicker" mentions but no 40 Hz steady-state stimulation.
- SSVEP BCI sets on NEMAR (nm000118–nm000131, nm000273, nm000338) and PhysioNet `mssvepdb`: all frequencies ≤33 Hz. eldBETA (nm000130, 100 elderly participants) uses 8–12 Hz only.
- PhysioNet: `earndb` and `earh` (ABR/OAE), `auditory-eeg` (music). No ASSR anywhere on PhysioNet (all 729 projects scanned).
- Zenodo 852303 (Guérit 2017, co-modulated ASSR): 80–100 Hz region, 49 GB. Zenodo 5513267: pABR. Zenodo 17190899 / 22815513: click-train pattern study with no description; not 40 Hz ASSR as far as can be told. Zenodo 12099874: MEG AD bicoherence, rest. Zenodo 22746385: a software "digital twin" record, not data.
- Figshare 907898 (McFadden 2014 test-retest 40 Hz ASSR): paper tables only. Figshare 27225894: 17 KB xlsx of ITPC values in 3–6-year-olds. Figshare 31958058, 21283209, 17170397 and 28341854: supplementary PDF/DOCX only.
- OSF `pf49s` (invisible 40 Hz flicker does not entrain), `8nvs6` (attention and 40 Hz): PDF only. OSF `bpcr3`: 2 MB zip, not inspected, likely a tiny pilot.
- Borealis `doi:10.5683/SP3/FF5F9M` (iGluSnFR 2–72 Hz flicker, mouse): metadata only (0-byte file list).
- Harvard Dataverse `doi:10.7910/DVN/GDGIVG` (longitudinal MCI EEG): derived xlsx only, no ASSR. `doi:10.34894/HYEP15` (40 Hz binaural beats): psychological measures only.
- DANDI searches ("auditory steady", "click train", "5xFAD", "Alzheimer"): no auditory 40 Hz dandisets. Allen Visual Coding has no 40 Hz flicker; only OpenScope 000535 does.
- GEO: nothing found for Martorell 2019 (auditory GENUS, Cell) under author or title search.
- Mendeley Data: the API search parameter is ignored; a web search found no ASSR datasets.
- LEMON (fcon_1000, open): resting only.

---

## 4. Recommendation (best 2–3 independent replication datasets per question)

- **(i) Who entrains to 40 Hz sound, and is it stable?**
  1. **ds005185**: 20 subjects × 4 sessions of continuous 40 Hz AM. Pull only the ~2 GB ASSR files.
  2. **M3CV nm000166**: 95 subjects × 2 days at 45.38 Hz; 1.15 GB.
  3. **Dataverse 56XZ3F Phase 2A sham arm**: AD patients, baseline vs 3 months.
- **(ii) Is the 40 Hz response true entrainment or evoked superposition?**
  1. **Dataverse 56XZ3F**: periodic vs ±5 ms random-jitter blocks with 1-min baselines, same click stimulus as ds005048.
  2. **ds007648**: ~468 three-second 40 Hz trains per subject, for build-up/decay modelling.
  3. **Stockholm ASSR2 (20/40/80 Hz)** for resonance, or the **mouse hdEEG 10–50 Hz** set for a cross-species version.
- **(iii) Aging/AD association of the 40 Hz response.**
  1. **Dataverse 56XZ3F Phase 1**: 13 young vs 12 older CN vs 16 mild AD, same 40 Hz protocol. This is the only open older-adult/AD 40 Hz auditory dataset found besides ds005048.
  2. **ds006036**: AD/FTD/CN photic driving at 5–30 Hz, with a 40 Hz harmonic.
  3. The true older-adult ASSR cohorts (Metropolit, Japan, AMP SCZ) are gated.
- **(iv) Cross-species / omics link.**
  1. **GSE226822 / GSE225842**: 40 vs 20 Hz vs light, which controls for frequency.
  2. **DANDI 000535**: 40 Hz vs rate-matched Poisson flicker at cell-type level.
  3. **Mouse hdEEG ASSR** (40 Hz auditory, PV phase-locked). Add **SEA-AD** (open) for human PV-interneuron loss vs AD stage.
- **Priority for the Oct 25 freeze.** Download 56XZ3F EEG (4.3 GB, or Phase 2A + Phase 1 AD alone at 1.4 GB) and the ds005185 ASSR subset first. Both are CC0 and need no login.

---

### Access snippets (tested)

- OpenNeuro file: `curl -O https://s3.amazonaws.com/openneuro.org/<dsID>/<path>`. List with `?list-type=2&prefix=<dsID>/`.
- NEMAR: `curl -L -O https://data.nemar.org/nm000166/v1.0.0/sub-001/ses-01/eeg/sub-001_ses-01_task-ssaep_eeg.eeg`. The manifest is at `/nm000166/v1.0.0/manifest.json`.
- Dataverse file: `curl -L -o NAME https://dataverse.harvard.edu/api/access/datafile/<fileId>`. Get file IDs from `/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/56XZ3F`.
- Figshare/Zenodo zips support HTTP range requests, so single subjects can be pulled from remote zips (a Python `zipfile` over an HTTP range reader worked for the Stockholm and mouse zips). RAR files (Zenodo 21156618) cannot be read this way.
