# STS 2026 workspace: "Who responds to 40-Hz stimulation?"

Read the files in this order:

| # | File | What it is |
|---|---|---|
| 1 | `01_AUDIT.md` | Audit of the earlier TCN/PAC/controller claims (they don't hold) and what survives |
| 2 | `02_STS_BENCHMARK.md` | STS rules (including AI use), judging, and patterns from 20 computational finalist projects; best-fit category (Neuroscience) |
| 3 | `03_LITERATURE_AND_GAPS.md` + `03_LITERATURE_TABLE.csv` | Living literature table (134 rows, 130 verified by DOI/PMID) and named gaps |
| 4 | `04_OBJECTIVE_MEMO.md` | 5 candidate objectives scored; C1 approved |
| 5 | `05_PREREGISTRATION.md` | Pre-registration (commit 5c5eec86) and amendment A1 (commit 54b56881), both before held-out analysis |
| 6 | `06_RESULTS.md` | Confirmatory results, labelled exploratory checks, cross-dataset synthesis, tier status |
| 7 | `07_TITLE_ABSTRACT_FIGURES.md` | Title options, 250-word abstract fact sheet, key-figure list, freeze plan |
| — | `RESEARCH_LOG.md` | Every attempt, dead ends included |
| — | `AI_DISCLOSURE_LOG.md` | What the AI did, and what you must verify and be able to explain |

## Reproduce (CPU only, about 10 minutes after the downloads)
```bash
pip install numpy scipy pandas h5py mne scikit-learn statsmodels matplotlib fooof openpyxl
# data (git-ignored) -> data/raw/: OpenNeuro ds005048 and ds005185 (task-ASSR + sourcedata ASSR) from
# s3://openneuro.org, and Harvard Dataverse doi:10.7910/DVN/56XZ3F (EEG folders + xlsx) -> data/raw/dv56XZ3F
cd sts2026/code
python audit_pac_forecast.py && python audit_block_label_artifact.py        # audit
python confirmatory.py extract primary                                       # pre-registered pipeline
for v in S1_roi_frontocentral S2_no_rejection S3_mastoid_ref; do python confirmatory.py extract $v; done
python confirmatory.py test                                                  # -> results/confirmatory/results.json
python confirmatory_h5.py extract && python confirmatory_h5.py test          # amendment A1 (third dataset)
python explore_post_registration.py && python explore_post_e5.py             # labelled exploratory checks
python make_figures.py                                                       # figures/
```
- Note 1: the S2 run of `confirmatory_h5.py` sets `confirmatory.PTP_UV = inf` (see `RESEARCH_LOG.md`).
- Note 2: the E6 check is an inline script recorded in the log; it writes `results/exploratory_post/results.json`.
- Every script is AI-assisted and says so in its header.
