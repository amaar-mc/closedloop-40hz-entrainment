# MIT URTC 2026 Lightning Talk ID-1269

**Early and Later EEG Synchronization During 40-Hz Auditory Stimulation**
Amaar Chughtai, Valley Christian High School. Presented October 11, 2026.

## Files

| File | What it is |
|---|---|
| `URTC2026_LT-ID1269_Chughtai.pptx` | **The deck (master copy).** Native PowerPoint: real text boxes, native equations (double-click to edit), figures as 300-dpi images, and the script in the speaker notes. |
| `URTC2026_LT-ID1269_Chughtai.pdf` | Camera-ready PDF. Export it from PowerPoint after editing (see below). |
| `SPEAKER_SCRIPT.md` | The talk as spoken, about 4:13 with slide changes, leaving time for one question. |
| `QA_PREP.md` | Short, number-backed answers to the questions most likely to come up. |
| `source_pptx/` | Builder for the PowerPoint deck: figures (`make_figures_v2.py`), slides (`build_native.js`), native equations (`omml.py`, `inject_math.py`). |
| `source/` | The earlier HTML/KaTeX build of the first design (kept for reference). |
| `previous/` | The first design: the web-style PDF and its image-only PPTX. Do not upload these. |
| `analysis/` | Reconstruction of the PLV analysis, the claims ledger, and dataset and literature facts. |

URTC rules this follows (2026 Lightning Talk guidelines): at most 7 slides counting title and ending,
5 minutes including questions, `.pdf` or `.ppt` on a flash drive, large legible type.

## Exporting the camera-ready PDF

In PowerPoint: File > Export > File Format: PDF, choose **Best for printing** (the other option uploads
the deck to a Microsoft online service), and save as `URTC2026_LT-ID1269_Chughtai.pdf` in this folder.
Bring both the PDF and the PPTX on the flash drive; present from the PDF.

## Rebuild from the results

`./build_pptx.sh` regenerates the figures and the deck from `results/metrics/` and `analysis/`.
It overwrites the PPTX, so once you have edited the deck in PowerPoint, keep the PPTX as the master
and do not rerun it.

## Where the numbers come from

Every statistic is read from `results/metrics/early_late_connectivity_analysis.json` (the primary
analysis) or computed from its per-participant arrays; nothing is typed in by hand.
`analysis/claims_ledger.md` lists each number with its JSON path.

| Slide | Claim | Source |
|---|---|---|
| 3 | Sound minus silence, whole session: +0.077, 95% CI 0.045 to 0.112, 27 of 35 | `primary_frequency_measures.plv.stimulus_vs_rest` |
| 3 | Group-mean PLV per 20-s window | `analysis/reconstructed_window_table.csv` |
| 4 | Raw PLV, block 1 vs last three blocks: 0.87 ≤ r ≤ 0.93 at every frequency | `frequency_controls_plv.*.absolute_first_block_to_late_blocks` |
| 5 | r = 0.780, 95% CI [0.573, 0.889], n = 35 | `target_position_sensitivity_plv.cycles_4_to_5` |
| 5 | Spearman 0.688; Lin 0.771; mean change −0.015 (p = 0.25); limits of agreement −0.16 to +0.13 | same node: `raw_association`, `agreement` |
| 5 | Without the most influential person (sub-05), r = 0.747 | `analysis/computed.json` → `item3_derived.drop_top1_cooks`, from the per-participant values |
| 6 | Neighboring frequencies: −0.10 ≤ r ≤ 0.26; smallest gap 0.52, 95% CI [0.08, 0.65] | `common_position_frequency_specificity_plv`; whiskers from `results/metrics/urtc_response_figure.json` |
| 6 | PLI 0.78, wPLI 0.66 | `common_position_measure_convergence.measures` |
| 6 | Later windows 3–4 to 8–9: 0.61 ≤ r ≤ 0.78, all Bonferroni p < 0.05 | `target_position_sensitivity_plv`, `target_position_multiplicity_plv` |

Cohort counts come from `data/raw/ds005048/participants.tsv`.

## About the analysis code

The script that produced the results JSON (`validation/analyze_early_late_connectivity.py`) was never
committed and is no longer on disk. `analysis/reconstruct_plv.py` rebuilds the analysis from the raw
OpenNeuro ds005048 EEG and reproduces every per-participant value in the JSON to within 3 × 10⁻¹³
(PLV, PLI, wPLI, all seven frequencies). `analysis/method_reconstruction.md` documents the verified
method and `analysis/verification_report.json` records the check.

## Before submitting

- Confirm the author name matches the CMT submission exactly (the deck uses "Amaar Chughtai").
- Keep the AI-use disclosure consistent with what was filed
  (`deliverables/venues/mit_urtc_poster_lightning/05_submission_ready/AI_USE_DISCLOSURE.md`).
- Export the PDF from PowerPoint (above), then copy the PDF and PPTX to the root of a flash drive, and arrive 15 minutes early to load them.
