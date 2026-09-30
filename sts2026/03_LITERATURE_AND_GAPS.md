# 3. Literature and gaps (living document)

**Living table:** [`03_LITERATURE_TABLE.csv`](03_LITERATURE_TABLE.csv)
- 134 unique papers and records; duplicates across the two source tables removed by DOI.
- Columns: paper, method, data, finding, limitation, public data, relevance.
- Verification:
  - 130 rows: DOI matched on Crossref (title, year, journal); PMID confirmed on PubMed where one exists.
  - 4 rows: `partial` (3 trial registrations with no DOI, 1 dataset DOI resolved via DataCite).
  - 0 rows unverified.
- Source tables with category detail: `lit/lit_mechanisms_trials.csv` (M = mechanism, D = dispute, H = human trial, A = human ASSR, T = tACS, O = omics) and `lit/lit_measurement_methods.csv` (PAC, EVE, MEA, IND, AGE, SCZ, MOD, NBM, DAT).
- Full gap analyses: `lit/gaps_mechanisms_trials.md`, `lit/gaps_measurement_methods.md`.
- Dataset census: `lit/dataset_census.md`.
- Novelty searches: `lit/novelty_searches.md`.
- **Update rule:** add a row whenever a new paper is cited. Verify it on Crossref/PubMed before it enters the report. The student must read every paper they cite.

## Coverage
| Area | Rows | Anchor papers (row id) |
|---|---|---|
| 40 Hz / GENUS mechanisms (mouse) | 19 | Iaccarino 2016 (M01), Martorell 2019 (M05), Murdock 2024 (M14) |
| Failed replications and disputes | 14 | Soula 2023 (D01), Tsai-lab reply preprint (D03), human PiB-PET null result (D06) |
| Human trials | 20 | Chan 2022 (H01), OVERTURE / Hajós 2024 (H05), HOPE unreported (H14), 2025 meta-analysis (H20) |
| Human 40 Hz ASSR in aging and AD | 8 + 5 | van Deursen 2011 (A01), Osipova 2006 (A02), Dobri 2023 (A04), lifespan review (A05) |
| Entrainment measurement and pitfalls | 25 | Tort 2010, Aru 2015 (PAC); PLV/PLI/wPLI (MEA); specparam (MEA07) |
| Entrainment vs evoked superposition | 10 | Bohórquez 2008 (EVE06), Notbohm 2016 (EVE02), Duecker 2021 (EVE04) |
| Individual differences and reliability | 7 | McFadden 2014 (IND01), Legget 2017 (IND02), van Deursen 2011 (IND05) |
| Models | 9 | Vierling-Claassen 2008 (MOD02), Metzner 2021 (MOD04), Herrmann 2016 (MOD05) |
| Methods from nearby fields | 11 | normative modeling (NBM01), ComBat (NBM10), reliability paradox (NBM04) |
| Public data / omics | 2 + census | ds005048, Dataverse 56XZ3F, GEO GSE226822 and others (census) |

## Named gaps (question → current evidence → why it is still open)
1. **Is the individual 40 Hz response a stable trait in older adults and AD, across visits and cohorts?**
   Test-retest data exist mainly for young adults and schizophrenia (IND01–IND04). Dementia has one study: a 1-week interval, one site, clicks (IND05). No cross-dataset replication exists (G3a, G3b).
2. **Does the response increase or decrease with age and AD?** The published results conflict:
   - Increased in AD: A01, A02.
   - Increased with age and related to hearing: A04.
   - Induced visual gamma weaker in MCI/AD: A07.
   - Declines in some aging studies: AGE01.
   No study compares young, older and AD groups on the *therapeutic* 4%-duty click in two independent cohorts.
3. **Who does not respond?** About 30% of early-AD patients showed no 40 Hz response (H18, a sponsor-affiliated study). No trial has stratified by responsiveness (mechanism/trials gap 5). No study predicts responsiveness from pre-stimulation EEG.
4. **Is theta-gamma PAC a valid 40 Hz entrainment readout?** The only positive report is a conference abstract (PAC10). There are measurement reasons it fails (PAC02, PAC03, PAC05–PAC09). Our audit found PAC falls during stimulation.
5. **Entrainment or evoked superposition, for auditory stimulation in older adults and AD?** This has been tested only in young adults (EVE06–EVE08). The clean tests are visual only (EVE01, EVE02, EVE04). The only open older-adult data (ds005048, 56XZ3F) have too few on/off events per person for dynamics.
6. **Does auditory 40 Hz stimulation change human AD pathology?** Human amyloid evidence is almost absent (D06), primate CSF amyloid *rose* (M23), and there is no human auditory-only trial with EEG and a sham arm (H10–H13).
7. **Mechanism transfer across species.** All 40 Hz omics come from mice and from two labs (census omics table). Nothing maps 40 Hz-specific genes (40 vs 20 Hz, GSE226822) onto human AD cell-type data (SEA-AD). PubMed novelty search: 0 hits.
8. **Model-based signatures in older adults.** No ASSR network model has been fit to aging or AD (G4a). Our discovery test found no 20 Hz subharmonic in ds005048, so the MOD04 signature is absent at this intensity.
