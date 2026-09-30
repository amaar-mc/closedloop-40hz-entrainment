# 1. Audit of the current project (as of 2026-09-30)

Scope: README.md, FINDINGS.md, `paper/conferences/mit_urtc_2026/`, and the code behind the numbers
(`src/data_loader.py`, `temporal_multiscale/build_multiscale_dataset.py`,
`scripts/pipeline/run_tcn_validation.py`). I re-ran the key numbers independently from the raw OpenNeuro
ds005048 files with new code (`sts2026/code/audit_*.py`, results in `sts2026/results/audit_*.json`).
**Compute:** 4 CPU cores, 15 GB RAM, no GPU, about 30 GB disk. That is enough for EEG/MEG re-analysis,
signal-processing models and small networks, but not for training large models.

## Real strengths (keep and defend)
| Strength | Evidence |
|---|---|
| **Early vs later 40-Hz PLV response is stable within a session and specific to 40 Hz** (URTC result) | r = 0.78 [0.57, 0.89], n = 35. Neighbouring frequencies (35–45 Hz) give r ≈ 0. Reproduced from raw EEG to 3e-13 (`lightning_talk/analysis/verification_report.json`). |
| Stimulus response exists and is measurable | My check: 40-Hz SNR rises during sound vs silence, d_z = 0.72, p = 7e-5, 26/35 participants. |
| Engineering hygiene | Subject-level splits, causal filters in the TCN, leakage checks, seeds, a claims ledger. |
| Honest framing already present | The URTC write-up says "offline replay" and "not a trial". |

## Weaknesses, ranked by how fast a skeptical PhD judge finds them
1. **The PAC "forecast" is mostly a label artifact.** `data_loader.py` (l. 399–420) gives every 2-s window
   (1-s hop) inside a 20–40-s block the modulation index (MI) of the *whole block*. That MI is computed from
   samples that lie in the *future* of most windows.
   - Rebuilding those labels reproduces the repo's persistence R² at 1 s (0.745 vs 0.76).
   - A **zero-parameter "schedule lookup"** gets R² = 0.81 / 0.41 / 0.35 at 1 / 5 / 10 s. It keeps the
     current label if the block has not ended, or else uses the mean of past blocks of the next type.
   - It works because the TCN's inputs include the 60-s schedule phase (`cycle_phase_sin/cos`,
     `time_since_switch`), so the future stimulation state is known.
   - **With honest per-window PAC, nothing is forecastable.**
     - Lag-1 autocorrelation of window MI is 0.04.
     - The best pooled R² at every horizon from 2 to 10 s is about 0.08, and it comes from the subject's
       running mean.
     - Persistence scores R² ≈ −0.7.
     - (`audit_pac_forecast.json`)
2. **Theta–gamma PAC does not measure entrainment here.** 40-Hz sound slightly *lowers* 4–8 Hz × 38–42 Hz MI
   (d_z = −0.40, p = 0.039; only 14/35 go up), while 40-Hz SNR rises. PAC at 38–42 Hz during a 40-Hz click
   train is also a known pitfall: sharp periodic stimulus-locked waveforms create spurious coupling.
   A 2-s window holds only about 8–16 theta cycles, so MI is dominated by estimation bias.
3. **Replay "closed-loop validation" is not closed-loop.**
   - The recorded EEG was produced by the fixed 40/20 schedule, so no controller decision can change it.
   - "Alignment" and "low-PAC targeting" only score whether decisions match below-median recorded labels
     (`evaluate_epoch_alignment`). These are the same artifact-laden labels as in item 1.
   - The objective "stimulate when PAC is low" is assumed; it is not justified clinically.
   - "35/35 benefit" uses a hand-weighted composite (`compute_clinical_utility`).
4. **The simulator results are circular.** Adaptive scheduling beats fixed only under fatigue models the
   project wrote itself. Real-data habituation is n.s. (p = 0.54).
5. **Inconsistent numbers across documents.**
   - TCN test R² appears as 0.606 (README), 0.25–0.28 at 5–10 s (FINDINGS §4.2.2), and 0.170 (FINDINGS §10).
   - The "feature-selection breakthrough" (−0.025 → 0.606) is explained by item 1: the spectral
     features did not carry the label shortcut.
6. **One dataset, one site, no sham, participant-chosen session length.** Session length is confounded with
   reference electrode and partly with diagnosis. The source paper excluded sub-06 and sub-13; the URTC
   analysis includes them.
7. **No clinical link.** Nothing relates the EEG measures to MMSE or diagnosis. The human efficacy evidence
   for 40 Hz itself is mixed: OVERTURE missed its primary endpoint, and HOPE is unreported as of 2026-09-27.

## Do the metrics measure what is claimed?
| Claim | Metric | Measures it? |
|---|---|---|
| "Forecasts entrainment 3–10 s ahead" | R² on block-level MI labels with schedule inputs | **No.** It measures the schedule and the label construction. |
| "Predictive controller beats reactive" | Alignment to the median of recorded labels | **No.** There is no counterfactual EEG. |
| "Entrainment" | Theta–gamma MI | **No.** It goes down with 40-Hz sound. |
| "Stable individual 40-Hz response" | Stimulus − silence PLV, early vs later | **Mostly yes.** Remaining caveats: volume conduction, whole-session ASR cleaning, one site. |

## What a judge attacks first, and the one-line answer we need
1. "Your R² comes from the schedule." **Concede.** Show the audit and pivot.
2. "Is PAC even entrainment?" **No.** Use stimulus-locked measures (ITC/PLV/SNR).
3. "Replay can't validate a controller." **Agree.** Stop claiming control.
4. "Does it replicate anywhere else?" **Not yet.** This is what the new objective must fix.

**Verdict:** retire the TCN/controller headline. The defensible core is the stable, frequency-specific,
individual 40-Hz response. The new objective should build on that, on independent data. Finding and
documenting item 1 yourself is itself a strength to show judges, because it shows scientific integrity.
