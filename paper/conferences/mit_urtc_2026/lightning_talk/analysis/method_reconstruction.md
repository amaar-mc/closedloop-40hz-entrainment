# PLV method reconstruction: URTC 2026 Lightning Talk ID-1269

**Result: exact reproduction.** From the raw ds005048 EEG, every per-participant value in
`results/metrics/early_late_connectivity_analysis.json` that was checked (PLV, PLI and wPLI;
all 7 frequencies; every endpoint family) matches to floating-point precision. The largest
absolute error over all 35 participants and all checked quantities is **3.2e-13**. The
recomputed primary Pearson r is 0.7799681050506172; the JSON has 0.7799681050506133. The
one-cycle companion file `results/metrics/early_late_connectivity_one_cycle_analysis.json`
also reproduces, with a max error of 1.2e-13.

- Script: `reconstruct_plv.py`. It is read-only against the repo. It runs with the repo's
  `.venv-reliability` interpreter (numpy 2.5.1, scipy 1.18.0, pandas 3.0.5), which matches the
  environment recorded in `provenance.environment`. It needs no packages beyond those.
- Per-window table: `reconstructed_window_table.csv` has 919 rows: participant × window, with
  PLV at 7 frequencies plus PLI and wPLI at 40 Hz.
- Per-check errors: `verification_report.json` (`summary`).
- Slide data: `figure_data.json`.

## 1. Data and cycles (verified)

- **Source.** `data/raw/ds005048/sub-XX/eeg/*_eeg.fdt`: float32, 19 channels interleaved in
  column-major (Fortran) order, 250 Hz. The channel order comes from `*_channels.tsv`
  (Fp1 Fp2 F7 F3 Fz F4 F8 T7 C3 Cz C4 T8 P7 P3 Pz P4 P8 O1 O2). The dataset authors had already
  applied average reference, a 1-Hz high-pass and a 50-Hz notch (`*_eeg.json`). No further
  re-referencing or preprocessing was done.
- **Events.** From `*_events.tsv`. The `sample` column is 1-based, so window start = sample − 1.
  For example, the first Stimulus is at sample 1251, which is index 1250, or 5.000 s.
- **Cycle k** is the k-th 40-s Stimulus block plus the Rest that follows it. Stimulus k starts at
  5 + 60(k−1) s. A cycle is **complete** only if its rest lasts the full 20 s.
- **Protocols.** Event files take one of two forms (8 files are identical, and 27 are identical):
  - **sub-01 to sub-08** (6-block protocol, 350-s recordings, 8 participants): 6 stimulation blocks
    and **5 complete cycles**. The 6th block is followed by a truncated 5-s rest at 345–350 s.
  - **sub-09 to sub-35** (10-block protocol, 590-s recordings, 27 participants): 10 stimulation
    blocks and **9 complete cycles**. The final rest is 5 s long (585–590 s).
  - These counts match `protocol_cohorts` {"6": 8, "10": 27}. The truncated 5-s rests are never
    analysed.
- **Early** is cycles 1–2, spanning 5–125 s: the first 120 s after the first stimulus onset.
  **Later** is cycles 4–5, spanning 185–305 s. Cycles 4–5 are the last two cycles that every
  participant has.

## 2. Windows

- Each 40-s stimulation block gives **two non-overlapping 20-s windows**:
  [onset, onset+20 s) and [onset+20 s, onset+40 s).
- Each complete rest gives **one 20-s window**.
- Every window is filtered, Hilbert-transformed and scored on its own. No samples are shared
  between windows, and there is no edge trimming.
- Window counts:
  - 6-block protocol: 12 stimulation + 5 silence = 17 windows.
  - 10-block protocol: 20 stimulation + 9 silence = 29 windows.
  - Total: 8×17 + 27×29 = 919 windows.
- The stimulation windows of the final block, whose rest is truncated, are used only in
  `stimulus_vs_rest` and the absolute-stimulation measures (see §5). They never enter the
  early/later contrasts.

## 3. Signals, filter, phase (verified)

- **25 bipolar sites.** b_ij = frontal_i − posterior_j, with frontal = {Fp1, Fp2, F3, Fz, F4}
  and posterior = {P3, Pz, P4, O1, O2}.
- **200 site pairs.** These are all unordered pairs of bipolar sites that share no electrode:
  25·16/2 = 200. This matches `method_guardrails.n_electrode_disjoint_site_pairs`.
- **Filter.** `scipy.signal.butter(2, [f−0.5, f+0.5], btype="bandpass", fs=250)`.
  - This is a 2nd-order Butterworth prototype, so the band-pass is 4th order.
  - It is applied **zero-phase, forward-backward**, with scipy's default padding, to each
    bipolar signal within each 20-s window.
  - `sosfiltfilt` gives a max error of 3.2e-13 and `filtfilt` (b, a) gives 3.3e-13. Both are
    exact, so the two cannot be told apart.
  - A causal filter does **not** reproduce the values (`sosfilt`/`lfilter`: sub-01 early is
    0.2553 against 0.3271 in the JSON).
- **Phase.** Instantaneous phase φ = angle of `scipy.signal.hilbert` applied to the filtered
  20-s window.
- **Frequencies.** f = 40 Hz (primary). The controls are 35, 37, 39, 41, 43 and 45 Hz, each a
  ±0.5-Hz band.

## 4. Connectivity measures (verified)

For a site pair (a, b), let z be the analytic signals and Δφ = φ_a − φ_b, taken over the
5000 samples of one window. Each window's value is the **mean over the 200 pairs**.

| Measure | Definition per pair | Max error vs JSON |
|---|---|---|
| PLV | \|mean_t exp(iΔφ)\| | 2.7e-14 (primary early/late) |
| PLI | \|mean_t sign(Im(z_a·conj z_b))\|, which is the same as \|mean sign(sin Δφ)\| | 0 (clean run) |
| wPLI (Vinck et al. 2011) | \|mean_t Im(z_a·conj z_b)\| / mean_t \|Im(z_a·conj z_b)\| | 1.5e-14 |

## 5. Participant-level quantities (all verified)

Here C_k = PLV_stim(k) − PLV_silence(k). PLV_stim(k) is the mean of cycle k's two 20-s
stimulation windows, and PLV_silence(k) is the following 20-s rest window.

| JSON block | Definition | Max error |
|---|---|---|
| `target_position_sensitivity_plv.cycles_4_to_5` (**abstract's primary**), `common_position_measure_convergence.measures.{plv,pli,wpli}`, `common_position_frequency_specificity_plv` | early = mean(C_1, C_2); later = mean(C_4, C_5) | ≤1.1e-13 |
| `target_position_sensitivity_plv.cycles_a_to_b` | later = mean(C_a, C_b). n = 35 for 3–4 and 4–5; n = 27 for 5–6 through 8–9 | ≤2.7e-14 |
| `*.stimulus_vs_rest` | mean over **all** stimulation windows, including the final block whose rest is truncated (12 or 20 windows), minus the mean over complete rest windows (5 or 9). Using only complete-cycle stimulation windows does not reproduce it (error 0.0198). | ≤9.0e-14 |
| `frequency_controls_plv.*.response_gain_early_to_late` | early = mean(C_1, C_2); later = mean of the **last two complete cycles**. That is C_4, C_5 for sub-01 to sub-08 and C_8, C_9 for sub-09 to sub-35, so the later position depends on the protocol. | ≤1.1e-13 |
| `*.response_gain_learning_curve.k` (k = 1, 2) | early = mean(C_1..C_k); later = last two complete cycles, as in the row above | ≤5.0e-14 |
| `*.absolute_stimulation_connectivity_learning_curve.k` (k = 1, 2, 3) | early = mean **absolute** stimulation PLV over both 20-s windows of stimulation blocks 1..k. Later = mean absolute stimulation PLV over both windows of the **last three stimulation blocks in the recording**: blocks 4–6 (6-block protocol) or 8–10 (10-block protocol). This includes the final block whose rest is truncated (`--late-absolute-blocks 3`). Silence is not subtracted. Using only complete-cycle blocks does not reproduce it (error 0.063). | ≤1.4e-13 |
| `frequency_controls_plv.*.absolute_first_block_to_late_blocks` | same as the k = 1 row above, computed at each frequency | ≤3.2e-13 |

Cross-checks:

- `early_response_gate.json` has 22 participants with later > 0 and 28 with early > 0. The
  reconstruction gives the same counts.
- Grand-mean cycle-1 40-Hz stimulation PLV is 0.568662. This equals the JSON's
  `absolute_first_block_to_late_blocks.agreement.early_mean`.

### Interpretation of the non-primary blocks

**What each block measures:**

- `response_gain_*` is the stimulation − silence contrast. It is the same kind of measure as the
  primary endpoint, but its "later" is the last two cycles of each session. It is not the common
  cycles 4–5 position.
  - `frequency_specificity_plv.primary_correlation` = 0.737 is this version.
  - The abstract's r = 0.780 is the common-position version, cycles 4–5.
- `absolute_*` is the raw stimulation-window PLV level with no silence baseline. It compares the
  first block (or first k blocks) with the session's last three stimulation blocks.

**Is the "absolute PLV is stable at every frequency, but the contrast is stable only at 40 Hz"
reading right? Confirmed.**

- **Absolute PLV is stable at every frequency.**
  `absolute_first_block_to_late_blocks.raw_association.pearson_r` is 0.867, 0.888, 0.894,
  **0.928**, 0.875, 0.908 and 0.928 at 35, 37, 39, **40**, 41, 43 and 45 Hz.
- **The contrast is stable only at 40 Hz.**
  - `response_gain_early_to_late` r is −0.090, 0.011, −0.163, **0.737**, −0.193, 0.046 and
    −0.046 at the same frequencies.
  - At the common cycles-4–5 position (`common_position_frequency_specificity_plv`), r is 0.020,
    0.249, 0.190, **0.780**, 0.258, −0.099 and 0.039.

**Why this happens.** The reconstruction also computed a common-position check that is not in
the JSON (`verification_report.json → not_in_json_common_position_absolute_plv`):

- Absolute stimulation PLV in cycles 1–2 correlates with cycles 4–5 at r = 0.93–0.96 at every
  frequency.
- Absolute **silence** PLV does too, at r = 0.87–0.93.
- Within the same cycles 1–2, stimulation and silence absolute PLV correlate at r = 0.91–0.97 at
  the control frequencies, but only **0.755 at 40 Hz**.
- Mean early stimulation − silence contrast:
  - 40 Hz: 0.0867
  - 35 Hz: 0.0214
  - 37 Hz: 0.0158
  - 39 Hz: 0.0155
  - 41 Hz: 0.0121
  - 43 Hz: 0.0024
  - 45 Hz: 0.0089

So absolute PLV is dominated by a participant-specific level that does not depend on the
stimulus. That level is present during silence and at every frequency near 40 Hz. Absolute
stability therefore does not show a stimulus response. Subtracting the following silence removes
this shared level. What remains is noise at the control frequencies, where r ≈ 0. At 40 Hz, it is
a participant-specific stimulus-locked component that persists within the session. The data
cannot say what causes the shared level. Possible causes include volume conduction or shared
sources and the finite-sample PLV floor.

## 6. Slide description (3 sentences)

"For each participant, I formed 25 frontal-minus-posterior bipolar EEG signals and split the
session into independent 20-second windows: two per 40-second stimulation block and one per
20-second silence. In each window, the signals were narrowly filtered at 40 Hz (±0.5 Hz), and
phase-locking value measured how consistently the phase difference stayed fixed across 200 pairs
of bipolar signals that share no electrode. Each cycle's response was stimulation PLV minus the
following silence PLV, and I correlated the mean response in cycles 1–2 (first 120 s) with that
in cycles 4–5."

## 7. Figure data notes (`figure_data.json`)

- **(a) Per-window 40-Hz PLV** for three participants, plus one alternate:
  - sub-01 (strong; early 0.327, later 0.276; 5 cycles)
  - sub-24 (moderate; 0.118 and 0.121; 9 cycles)
  - sub-09 (near zero / negative; −0.012 and −0.018; 9 cycles)
  - Alternate: sub-32 (strong, 9 cycles; 0.251 and 0.261)
  - Each entry also has its per-cycle contrasts and the matching JSON values.
- **(b) Snippet pair, sub-01, cycle 1.** Stimulation window 5–25 s; silence window 45–65 s.
  - Pair: Fp2−Pz versus F4−O2. It was chosen as the pair whose stimulation − silence PLV
    difference is at the median across the 200 pairs.
  - Pair PLV: 0.422 in the stimulation window and 0.163 in the silence window. The 200-pair
    window means are 0.575 and 0.348.
  - **Caveat for the slide.** With a filter only 1 Hz wide, the phase difference drifts on a
    timescale of about 1 s. Over the requested 0.3-s snippet (10–10.3 s into each window), the
    snippet-only PLV is about 0.97 in **both** conditions, so a 0.3-s trace cannot show the
    difference. Use the included whole-window phase-difference series (50-Hz decimated) or the
    36-bin phase-difference histograms to show the dispersion that PLV measures.
  - Signal units are those stored in the .fdt. `channels.tsv` lists them as n/a; the EEGLAB
    convention is µV.
- **(c) Grand average** at 40, 35 and 45 Hz, over n = 35, for cycles 1–5: mean ± SEM of
  stimulation PLV, silence PLV and their contrast.
  - The 40-Hz contrast by cycle is 0.082, 0.092, 0.101, 0.084 and 0.059.
  - At 35 Hz the contrast runs from 0.010 to 0.029, and at 45 Hz from −0.024 to 0.021.

## 8. Not reconstructed / remaining uncertainty

- **Summary statistics.** Bootstrap CIs, grouped out-of-fold, LOPO, the permutation p and ICC
  were not re-run. Only the per-participant values they are computed from, and the Pearson r,
  were verified.
- **Filtering routine.** `sosfiltfilt` and `filtfilt` both reproduce the values, so which one
  the original used cannot be decided. Both are "zero-phase 2nd-order Butterworth".
- **Channel order.** It was taken from `channels.tsv` without reading the HDF5 `.set` labels.
  The exact match confirms the order indirectly.
- **Original code.** The original script (sha256 `ab5cba7d…` in `provenance`) is not available.
  This is a functional equivalent, not the original code.
