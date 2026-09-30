# Research log: STS 2026 re-direction

Every attempt goes here, dead ends included, in one or two lines each.
Format: date | step | what was done | result | files.

| Date | Step | Attempt | Result | Files |
|---|---|---|---|---|
| 2026-09-30 | setup | Checked compute; downloaded OpenNeuro ds005048 from its S3 mirror (183 files, 357 MB) | 4 CPU / 15 GB / no GPU; data OK | `data/raw/ds005048` (git-ignored) |
| 2026-09-30 | audit | Wrote an independent reader for .fdt/.tsv | Works for 35/35 | `code/ds005048_io.py` |
| 2026-09-30 | audit | Per-window (2 s) Tort MI plus 40-Hz SNR; lag-1 autocorrelation; stim vs rest; honest forecast R² | MI lag-1 r = 0.04; MI stim < rest (d_z −0.40); SNR stim > rest (d_z 0.72); best honest R² about 0.08 at every horizon | `code/audit_pac_forecast.py`, `results/audit_pac_forecast.json` |
| 2026-09-30 | audit | Rebuilt the original block-level labels; scored persistence and a zero-parameter schedule lookup | Persistence R² 0.745 at 1 s (repo 0.76, so the reconstruction matches); schedule lookup R² 0.41 at 5 s, 0.35 at 10 s | `code/audit_block_label_artifact.py`, `results/audit_block_label_artifact.json` |
| 2026-09-30 | audit | Read the replay metric code | Alignment is scored against recorded labels, so no counterfactual; the utility composite is hand-weighted | `01_AUDIT.md` |
| 2026-09-30 | DEAD END | Rescuing the within-session "forecast then control" idea with honest per-window measures | Killed. Per-window MI and SNR are near-white (lag-1 r ≈ 0.04), so there is no forecastable within-session dynamic at 2-s resolution | — |
| 2026-09-30 | explore (discovery ds005048) | Stimulus-locked 40-Hz ITC over 1-s epochs; onset/offset 40-Hz envelope; links to age/MMSE | ITC40 stim 0.10 vs 37/43-Hz 0.046 (the bias floor); stim − rest (matched n) d_z 0.53, p 3e-4, 28/35. Envelope step only about 3–5%. ITC gain vs age ρ −0.23 (p 0.19), vs MMSE ρ 0.10 (p 0.56) | `code/explore_ds005048_response.py`, `results/explore_ds005048_*.{json,csv}` |
| 2026-09-30 | DEAD END (on this dataset) | Per-subject onset/offset time constants to test "entrainment vs superposition" | SNR too low: loudspeaker delivery at a low level gives about a 3–5% envelope change, so per-subject fits are infeasible. Needs headphone ASSR data | — |
| 2026-09-30 | data | Checked whether OpenNeuro ds003800 (same lab, 13 older adults) is independent of ds005048 | **Not independent.** Demographics match sub-01 to 13; Cz cross-correlation r = 0.96–1.00 at a 5-s offset, including sub-09 to 13 (the first 340 s of the long sessions). Only new content: a 1-min eyes-open pre-stimulation rest recording (11/13) | `data/raw/ds003800` (git-ignored) |
| 2026-09-30 | literature | Two verified literature tables (70 + 70 rows), gap files, STS benchmark | See `lit/`, `02_STS_BENCHMARK.md` | `lit/*.csv`, `lit/gaps_*.md` |
| 2026-09-30 | explore (discovery) | Onset/offset complementarity test, block-wise and subject-pooled | **Dead end on ds005048.** Noise ≫ signal; cross-block phase consistency median 0.25 (9/35 > 0.5) | `code/explore_onset_offset.py` |
| 2026-09-30 | explore (discovery) | 20/40/60-Hz within-block ITC (subharmonic = nonlinearity test, MOD04) | 40 Hz d_z 1.17 (32/35); 20 Hz and 60 Hz no response (20 Hz slightly below floor, d_z −0.33) | `code/explore_subharmonic.py`, `results/explore_subharmonic_ds005048.json` |
| 2026-09-30 | explore (discovery) | Reliability of R40 plus candidate predictors (FOOOF aperiodic, IAF, rel. 40 Hz, age, MMSE) | Split-half r = 0.95 (Spearman-Brown 0.97); no predictor with \|ρ\| > 0.21; negative control R37 ≈ 0 for all | `code/explore_predictors_ds005048.py`, `results/explore_predictors_ds005048.*` |
| 2026-09-30 | data | Read 56XZ3F notes and demographics only (no EEG) | CN: 3-min periodic vs jittered audio/visual/AV blocks. AD Phase 1: one 1-min audio block. Phase 2A: AV at baseline and 3 months. APOE and cognition available | `lit/dataset_census.md` |
| 2026-09-30 | literature | Merged the two verified tables → 134 unique rows | 130 verified, 4 partial | `03_LITERATURE_TABLE.csv`, `03_LITERATURE_AND_GAPS.md` |
| 2026-09-30 | objective | 5 candidates scored; C1 "Who entrains" recommended | **Awaiting student approval** | `04_OBJECTIVE_MEMO.md` |
| 2026-09-30 | objective | **Student approved C1** "Who entrains" | — | `04_OBJECTIVE_MEMO.md` |
| 2026-09-30 | data | Downloaded 56XZ3F (93 BDF, 4.3 GB; size-verified; 2 retried). Found HG222 baseline = HG221 baseline (identical md5) | Exclusion pre-specified | `data/raw/dv56XZ3F` (git-ignored) |
| 2026-09-30 | pipeline | Notes/trigger block parser for all 56XZ3F files (timing only). Fixed 3 parser bugs (unnumbered headers, '*' in header, split recordings) | 76 recordings parse; triggers used where their count matches, else nominal notes times | `code/dv56_io.py`, `results/dv56_schedules.json` |
| 2026-09-30 | pipeline | Dry run on the excluded HG204 3-month file. Found 37-Hz control biased by Hann leakage from 40 Hz → moved control to 33 Hz | Pipeline OK | `code/confirmatory.py` |
| 2026-09-30 | discovery (frozen pipeline) | ds005048 R40 reliability | Odd/even ρ 0.92 [0.81, 0.97]; single block vs single block ρ 0.68 [0.41, 0.85]; R33 control ρ 0.04 | `results/confirmatory/ds005048_subjects_primary.csv` |
| 2026-09-30 | **pre-registration** | Hypotheses, tests, thresholds, exclusions, sensitivity analyses; code hashes | Committed before any held-out outcome analysis | `05_PREREGISTRATION.md` |
| 2026-09-30 | **confirmatory** | Frozen pipeline on 56XZ3F (all pre-registered tests + S1–S3) | K1 pass; H1 partial (ρ 0.52 [0.18, 0.76]); H2a/b n.s., opposite direction to published claims; H2c pass; H3a not met, H3b met; H4 formally passed | `results/confirmatory/results.json`, `06_RESULTS.md` |
| 2026-09-30 | exploratory (post-registration) | Artifact checks: strobe-covered silence, unconnected EXG, topography | No artifact evidence; auditory-like topography | `code/explore_post_registration.py`, `results/exploratory_post/` |
| 2026-09-30 | exploratory (post-registration) | Recording-noise confound (35–45 Hz power in silence) | Trait survives (partial ρ 0.49). **H4 is a noise artifact** (pred vs noise r −0.89; partial r 0.22). AD < CN explained by noise | `code/explore_post_e5.py` |
| 2026-09-30 | DEAD END | Moonshot "resting EEG predicts responders" | Withdrawn: the predictor indexes recording noise | — |
| 2026-09-30 | amendment A1 | Registered H5 on ds005185 (commit 54b56881) before analysis | — | `05_PREREGISTRATION.md` §9 |
| 2026-09-30 | confirmatory A1 | H5 primary | Not evaluable: the 200 µV rule rejected too many epochs in 16/80 dry-electrode sessions (n = 5 complete). Secondary 2-night ICC 0.41 [−0.09, 0.80] | `results/confirmatory/results_h5*.json` |
| 2026-09-30 | sensitivity (pre-specified S2) | H5 without rejection | 4-night ICC 0.57 [0.31, 0.78]; noise-adjusted 0.69; R33 0.05 | `results_h5_S2_no_rejection.json` |
| 2026-09-30 | exploratory E6 | Noise check in ds005048 | Noise vs R40 ρ −0.38; the AD effect is not explained by noise here (so the 56XZ3F result does not replicate) | `results/exploratory_post/results.json` |
