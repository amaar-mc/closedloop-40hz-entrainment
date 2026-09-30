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
