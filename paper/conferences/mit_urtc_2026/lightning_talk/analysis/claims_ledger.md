# Claims ledger: Early and Later EEG Synchronization During 40-Hz Auditory Stimulation (URTC 2026 LT ID-1269)

Generated 2026-09-27. Repo `the repository root` (read-only; nothing modified). Machine-readable twin: `claims_ledger.json`.

- Source of truth: `results/metrics/early_late_connectivity_analysis.json` provenance block: results/metrics/early_late_connectivity_analysis.json::provenance (analysis_script_sha256 ab5cba7df3b4f9f0e3f4e947b94c8bcef3cdf38d73042f968661c1ac1a471da5, statistics_seed 20260809, bootstrap_repetitions 50000).
- validation/analyze_early_late_connectivity.py, validation/analyze_early_response_gate.py, scripts/figures/generate_urtc_response_figure.py are absent from disk and never committed; stored JSON is the source of truth.
- Recomputation method: numpy.random.default_rng(seed).integers(0, n, (50000, n)) participant resampling; Pearson r per replicate; np.percentile 2.5/97.5. This exact method reproduces urtc_response_figure.json frequency_bootstrap_ci95 bit-for-bit with seed 20260812 (shared resample indices across frequencies).
- Rounding: Correlations, CIs, means: 3 decimals (matches abstract). p-values: 2 significant figures in scientific notation when < 0.001.
- Input SHA-256: `results/metrics/early_late_connectivity_analysis.json` 61d1e5531b7d...; `results/metrics/early_late_connectivity_one_cycle_analysis.json` 539bdde948a0...; `results/metrics/early_response_gate.json` 9e3119382a6d...; `results/metrics/urtc_response_figure.json` d8142689dd7d...; `data/raw/ds005048/participants.tsv` 9a053180deeb...
- Scripts: `compute_ledger.py` (recomputations to `computed.json`), `build_ledger.py` (assembles JSON), `render_md.py` (this file).

## Slide-ready numbers (the short list)

| What | Show on slide | Source |
|---|---|---|
| Primary association | **r = 0.780 (95% CI 0.573-0.889), n = 35** | `results/metrics/early_late_connectivity_analysis.json::target_position_sensitivity_plv.cycles_4_to_5` |
| Rank-based | **Spearman rho = 0.688** | `results/metrics/early_late_connectivity_analysis.json::target_position_sensitivity_plv.cycles_4_to_5.raw_association.spearman_rho` |
| p-value (if shown) | **p = 3.3 x 10^-8** | `results/metrics/early_late_connectivity_analysis.json::target_position_sensitivity_plv.cycles_4_to_5.raw_association.pearson_p_two_sided` |
| Group means | **early 0.087 vs later 0.072 PLV; bias -0.015, p = 0.25** | `results/metrics/early_late_connectivity_analysis.json::target_position_sensitivity_plv.cycles_4_to_5.agreement` |
| Stim > silence overall at 40 Hz | **+0.077 PLV (0.045-0.112); 27/35 positive** | `results/metrics/early_late_connectivity_analysis.json::primary_frequency_measures.plv.stimulus_vs_rest` |
| Sign counts | **early > 0: 28/35; later > 0: 22/35; both: 20/35** | `analysis/computed.json (compute_ledger.py)` |
| Alternative measures | **PLI r = 0.775 (0.441-0.904); wPLI r = 0.659 (0.363-0.817)** | `results/metrics/early_late_connectivity_analysis.json::common_position_measure_convergence.measures` |
| Frequency specificity | **40 Hz r = 0.780 vs 35/37/39/41/43/45 Hz r = 0.020/0.249/0.190/0.258/-0.099/0.039** | `results/metrics/early_late_connectivity_analysis.json::common_position_frequency_specificity_plv` |
| Smallest 40 Hz advantage | **+0.522 over 41 Hz (95% CI 0.081-0.649 for the minimum)** | `results/metrics/early_late_connectivity_analysis.json::common_position_frequency_specificity_plv.statistics` |
| Cohort | **35 participants: 10 normal, 6 MCI, 16 mild AD, 1 moderate AD, 2 unlabeled; 17 F / 18 M; age 54-89 (mean 72.7)** | `data/raw/ds005048/participants.tsv` |
| Protocol | **40 s 40-Hz-modulated sound + 20 s silence per cycle; 6 (n=8) or 10 (n=27) cycles** | `events.tsv; results/metrics/early_late_connectivity_analysis.json::protocol_cohorts` |
| Robustness (backup) | **without sub-01 and sub-05: r = 0.699 (0.421-0.862)** | `analysis/computed.json (compute_ledger.py)` |

## 1. Abstract numbers verification

| Claim | Slide form | Full-precision value | Source (file :: JSON path) | Status |
|---|---|---|---|---|
| Pearson r = 0.780 | **0.780** | `0.7799681050506133` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.raw_association.pearson_r` | PASS |
| Participant-bootstrap 95% CI 0.573-0.889 | **0.573-0.889** | `[0.5729443967567032, 0.8894133393115364]` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.bootstrap.raw_correlation_ci95` | PASS |
| | *note* | 50,000 participant resamples (provenance.bootstrap_repetitions); percentile interval. | | |
| n = 35 participants | **35** | `35` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.n_participants` | PASS |
| | *note* | Also top-level n_participants = 35; provenance.subjects lists sub-01..sub-35 (sub-06, sub-13 included despite provenance.source_exclusions; see section 4). | | |
| Early cycles 1-2 vs nonoverlapping later cycles 4-5 | **cycles 1-2 vs 4-5** | `["mean stimulation-to-following-rest PLV contrast in the first 2 complete cycles", "mean stimulation-to-following-rest PLV contrast in complete cycles 4-5", [4, 5]]` | `results/metrics/early_late_connectivity_analysis.json` :: `primary_endpoint.early_measurement / primary_endpoint.later_measurement / common_position_measure_convergence.target_cycles` | PASS |
| | *note* | Command args --early-response-cycles 2 --late-response-cycles 2. Cycle = 40 s stim + 20 s silence (events.tsv), so cycles 1-2 = first 120 s. Cycle 3 is a gap, so windows do not overlap. | | |
| Six neighboring frequencies tested | **35, 37, 39, 41, 43, 45 Hz** | `[35.0, 37.0, 39.0, 41.0, 43.0, 45.0]` | `results/metrics/early_late_connectivity_analysis.json` :: `common_position_frequency_specificity_plv.statistics.control_frequencies_hz` | PASS |
| Stronger at 40 Hz than all six (point estimates) | **40 Hz r 0.780 vs controls -0.099 to 0.258** | `{"35_hz": 0.7604201087793999, "37_hz": 0.530594829266835, "39_hz": 0.5898780426081796, "41_hz": 0.5215259979155702, "43_hz": 0.8793064402544227, "45_hz": 0.7405162028153248}` | `results/metrics/early_late_connectivity_analysis.json` :: `common_position_frequency_specificity_plv.statistics.pairwise_participant_bootstrap.*.primary_minus_control` | PASS (with caveat) |
| | *note* | All six differences > 0; all six pairwise 95% CIs exclude 0; minimum-difference CI [0.081, 0.649] excludes 0; but Bonferroni familywise CI for 39 Hz is [-0.008, 1.168] (includes 0). See section 5. | | |
| Two alternative synchronization measures remain positive | **PLI r = 0.775; wPLI r = 0.659** | `{"pli": 0.7752465870604393, "wpli": 0.6590238903318351}` | `results/metrics/early_late_connectivity_analysis.json` :: `common_position_measure_convergence.measures.{pli,wpli}.raw_association.pearson_r` | PASS |
| Each cycle = 40 s sound + 20 s silence | **40 s / 20 s** | `{"stim_durations": [40.0]}` | `data/raw/ds005048/sub-*/eeg/*_events.tsv; data/raw/ds005048/README` :: `events.tsv duration column` | PASS |
| | *note* | Last rest in every file is truncated (<20 s), so 6-block sessions have 5 complete cycles and 10-block sessions have 9. | | |
| Frontal and posterior electrodes | **Fp1, Fp2, F3, Fz, F4 / P3, Pz, P4, O1, O2** | `[["Fp1", "Fp2", "F3", "Fz", "F4"], ["P3", "Pz", "P4", "O1", "O2"]]` | `results/metrics/early_late_connectivity_analysis.json` :: `provenance.frontal_channels / provenance.posterior_channels` | PASS |
| | *note* | method_guardrails: 25 bipolar frontal-posterior sites, 200 electrode-disjoint site pairs, shared-electrode pairs excluded. | | |
| OpenNeuro ds005048, mixed memory-clinic cohort | **OpenNeuro ds005048** | `"doi:10.18112/openneuro.ds005048.v1.0.1"` | `data/raw/ds005048/dataset_description.json; participants.tsv` :: `DatasetDOI` | PASS |
| | *note* | Source paper: Lahijanian, Aghajan & Vahabi, Sci Rep 14:13153 (2024), doi:10.1038/s41598-024-63727-z; recruited from memory-clinic referrals, Ziaeian Hospital, Tehran. | | |

### Which 40 Hz CI to show

- Abstract CI: `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.bootstrap.raw_correlation_ci95` = `[0.5729443967567032, 0.8894133393115364]` -> **0.573-0.889**.
- Figure CI: `results/metrics/urtc_response_figure.json` :: `frequency_bootstrap_ci95.3` = `[0.5699351603054275, 0.8891381562415653]` (seed 20260812) -> would round to 0.570-0.889.
- The figure CIs were reproduced bit-for-bit (max abs diff 2.2e-16) with default_rng(20260812), 50,000 shared participant resamples, percentile interval. The same method with other seeds gives lower bounds 0.5699-0.5743 and upper bounds 0.8887-0.8896, so the 0.5729 vs 0.5699 gap is Monte Carlo seed noise, not a different analysis.
- **Decision:** Show the abstract CI 0.573-0.889 everywhere (slides, script). It is the accepted-abstract number and comes from the primary analysis artifact whose provenance block is the source of truth. If the 7-frequency figure reuses urtc_response_figure.json CIs, the 0.003 difference in the lower whisker is invisible at slide scale, so the existing figure can be used as long as its 40 Hz bar is not numerically labeled from that JSON (or regenerate the 40 Hz bar with the primary CI). Never print 0.570 on a slide or say it aloud; it would contradict the abstract.

## 2. Primary endpoint (40 Hz PLV contrast, cycles 1-2 -> cycles 4-5, n = 35)

| Claim | Slide form | Full-precision value | Source (file :: JSON path) |
|---|---|---|---|
| Pearson r | **0.780** | `0.7799681050506133` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.raw_association.pearson_r` |
| Pearson p (two-sided) | **3.3 x 10^-8** | `3.3301323334229766e-08` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.raw_association.pearson_p_two_sided` |
| Spearman rho | **0.688** | `0.6882352941176471` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.raw_association.spearman_rho` |
| Spearman p | **4.9 x 10^-6** | `4.89283613442688e-06` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.raw_association.spearman_p_two_sided` |
| Bootstrap 95% CI for r | **0.573-0.889** | `[0.5729443967567032, 0.8894133393115364]` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.bootstrap.raw_correlation_ci95` |
| Lin concordance (CCC) | **0.771** | `0.7706912506318437` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.agreement.lin_concordance` |
| Lin CCC 95% CI | **0.560-0.864** | `[0.5595715298402135, 0.8639209808918644]` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.bootstrap.lin_concordance_ci95` |
| ICC(A,1) absolute agreement | **0.776** | `0.7755830499685145` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.agreement.icc_absolute_agreement_a_1` |
| ICC(A,1) 95% CI | **0.566-0.867** | `[0.5662336178182809, 0.8670825568293905]` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.bootstrap.icc_absolute_agreement_a_1_ci95` |
| ICC(C,1) consistency | **0.777** | `0.7773412945999778` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.agreement.icc_consistency_c_1` |
| Early (cycles 1-2) mean contrast, PLV units | **0.087** | `0.08667767577588244` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.agreement.early_mean` |
| Later (cycles 4-5) mean contrast | **0.072** | `0.07183919143805745` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.agreement.late_mean` |
| Bias (later - early) | **-0.015** | `-0.014838484337824972` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.agreement.late_minus_early_bias` |
| SD of differences | **0.075** | `0.07537673789229422` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.agreement.difference_standard_deviation` |
| Bland-Altman 95% limits | **-0.163 to 0.133** | `[-0.16257689060672165, 0.1328999219310717]` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.agreement.bland_altman_limits_95` |
| Paired t | **-1.165** | `-1.1646253162120588` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.agreement.paired_t_test.t` |
| Paired t p (df 34) | **0.252** | `0.25227748441001135` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.agreement.paired_t_test.p_two_sided` |
| Wilcoxon signed-rank p | **0.115** | `0.11478191410424188` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.agreement.wilcoxon_signed_rank.p_two_sided` |
| Grouped 6-fold OOF R2: calibration (linear fit on training participants) | **0.480** | `0.4802525297854314` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.grouped_oof.metrics.calibration.r2` |
| Grouped OOF R2: persistence (later = early) | **0.572** | `0.5720134657923778` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.grouped_oof.metrics.persistence.r2` |
| Grouped OOF R2: population mean (training mean) | **-0.090** | `-0.0899709713016974` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.grouped_oof.metrics.population_mean.r2` |
| Persistence R2 bootstrap 95% CI | **0.092-0.755** | `[0.09164709755037789, 0.7552002068357445]` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.bootstrap.persistence_r2_ci95` |
| LOPO calibration R2 | **0.547** | `0.5465349651335771` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.leave_one_participant_out_calibration.r2` |
| LOPO calibration correlation | **0.740** | `0.7400495516872534` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.leave_one_participant_out_calibration.correlation` |
| Split-seed sensitivity of calibration R2 (6 seeds) | **0.466-0.558** | `{"2026": 0.4802525297854314, "42": 0.5064275746477822, "123": 0.5425359053359294, "456": 0.5514384860546317, "789": 0.46597232776407316, "2024": 0.5581826066741638}` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.split_seed_sensitivity.*.r2` |
| Split-seed sensitivity of calibration OOF correlation | **0.694-0.748** | `{"2026": 0.6962541052350805, "42": 0.7176408589929751, "123": 0.7384592152289142, "456": 0.7430090364514785, "789": 0.694159825052837, "2024": 0.7477327404383936}` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.split_seed_sensitivity.*.correlation` |
| 6-block cohort r (n=8) | **0.915** | `0.9147581505980016` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.protocol_cohorts.6_stimulation_blocks.pearson_r` |
| 6-block cohort p | **0.0015** | `0.0014511478608739675` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.protocol_cohorts.6_stimulation_blocks.pearson_p_two_sided` |
| 10-block cohort r (n=27) | **0.687** | `0.6867895502903452` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.protocol_cohorts.10_stimulation_blocks.pearson_r` |
| 10-block cohort p | **7.6 x 10^-5** | `7.611524985639644e-05` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.protocol_cohorts.10_stimulation_blocks.pearson_p_two_sided` |
| 10-block cohort Spearman | **0.594** | `0.594017094017094` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.protocol_cohorts.10_stimulation_blocks.spearman_rho` |

Interpretation:
- No systematic early-to-later shift: bias -0.015 PLV units, paired t p = 0.252.
- Individual agreement is moderate: Bland-Altman limits -0.163 to +0.133 are wide relative to the mean contrast (~0.07-0.09).
- In participant-held-out folds, simple persistence (later = early) R2 0.572 beat a fitted calibration line (0.480) and the training mean (-0.090). The early value carries participant-specific information; the fitted line adds nothing over persistence.
- The 6-block cohort r = 0.915 rests on n = 8 and contains the two highest-leverage participants (sub-01, sub-05); do not present it as a finding.

## 3. Derived from per-participant arrays

| Claim | Slide form | Full-precision value | Source (file :: JSON path) |
|---|---|---|---|
| Early contrast > 0 | **28/35** | `28` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.early_positive` (from `target_position_sensitivity_plv.cycles_4_to_5.values.early`) |
| Later contrast > 0 | **22/35** | `22` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.late_positive` (from `target_position_sensitivity_plv.cycles_4_to_5.values.late`) |
| | *note* | Matches early_response_gate.json endpoint.n_later_positive = 22. | |
| Both > 0 | **20/35** | `20` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.both_positive` |
| Both <= 0 | **5/35** | `5` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.both_nonpositive` |
| Sign agreement | **25/35 (71%)** | `25` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.sign_agreement` |
| Early > 0 but later <= 0 | **8** | `["sub-02", "sub-06", "sub-07", "sub-13", "sub-23", "sub-28", "sub-29", "sub-33"]` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.early_positive_subjects_nonpos_late` |
| Early <= 0 but later > 0 | **2** | `["sub-11", "sub-12"]` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.early_nonpos_subjects_late_pos` |
| Early contrast min / median / max | **-0.088 (sub-34) / 0.053 / 0.327 (sub-01)** | `{"min": -0.08849421851407357, "min_subject": "sub-34", "max": 0.3271073626245781, "max_subject": "sub-01", "median": 0.05328691630671101, "mean": 0.08667767577588244, "sd": 0.10...` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.early_summary` |
| Later contrast min / median / max | **-0.102 (sub-27) / 0.034 / 0.444 (sub-05)** | `{"min": -0.10167791644807372, "min_subject": "sub-27", "max": 0.4439160076630827, "max_subject": "sub-05", "median": 0.034016075260869, "mean": 0.07183919143805745, "sd": 0.1174...` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.late_summary` |
| OLS later ~ early | **slope 0.847, intercept -0.002** | `{"intercept": -0.0015576395682788571, "slope": 0.8467789468203363}` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.ols_late_on_early` |
| Highest leverage (hat) participants | **sub-01 h=0.174 (on the line, Cook's D ~0); sub-05 h=0.154 (Cook's D 0.646, studentized resid 2.66); sub-17 h=0.120** | `[{"subject": "sub-01", "early": 0.3271073626245781, "late": 0.2758706285252828, "hat": 0.1737326371907666, "cooks_d": 4.434883937395182e-06, "studentized_resid": 0.0064949486291...` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.leverage_rank[0:3]` |
| Most influential (Cook's D) | **sub-05 D=0.646; sub-11 D=0.216 (both above 4/n = 0.114)** | `[{"subject": "sub-05", "early": 0.31028792891081086, "late": 0.4439160076630827, "hat": 0.1541333116943245, "cooks_d": 0.645622487130419}, {"subject": "sub-11", "early": -0.0353...` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.cooks_rank[0:2]` |
| r without sub-01 (top leverage) | **r = 0.754, CI 0.511-0.880, n=34** | `{"n": 34, "pearson_r": 0.7543211782894056, "pearson_p": 2.5753125792254213e-07, "spearman_rho": 0.6601986249045072, "spearman_p": 2.153758601970954e-05, "bootstrap_ci95_seed2026...` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.drop_top1_leverage` |
| r without sub-05 (top Cook's D) | **r = 0.747, CI 0.505-0.887, n=34** | `{"n": 34, "pearson_r": 0.7472312533238115, "pearson_p": 3.8379025211137375e-07, "spearman_rho": 0.6601986249045072, "spearman_p": 2.153758601970954e-05, "bootstrap_ci95_seed2026...` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.drop_top1_cooks` |
| r without sub-01 and sub-05 (top-2 leverage) | **r = 0.699, CI 0.421-0.862, Spearman 0.628, n=33** | `{"n": 33, "pearson_r": 0.6991535815129069, "pearson_p": 6.001648011646334e-06, "spearman_rho": 0.6283422459893049, "spearman_p": 9.026095226722187e-05, "bootstrap_ci95_seed20260...` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.drop_top2_leverage` |
| r without sub-05 and sub-11 (top-2 Cook's D) | **r = 0.803, n=33** | `{"n": 33, "pearson_r": 0.8029664267238803, "pearson_p": 1.88041750602038e-08, "spearman_rho": 0.71524064171123, "spearman_p": 2.9036412295699875e-06, "bootstrap_ci95_seed2026080...` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.drop_top2_cooks` |
| Spearman (full sample, rank-based robustness) | **rho = 0.688** | `0.6882352941176471` | `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.cycles_4_to_5.raw_association.spearman_rho` |
| r on 33 participants with diagnosis labels (excl. sub-06, sub-13) | **r = 0.776, CI 0.571-0.887, Spearman 0.701** | `{"n": 33, "pearson_r": 0.7762504184719423, "pearson_p": 1.1042756502605531e-07, "spearman_rho": 0.7005347593582888, "spearman_p": 5.64937604938382e-06, "bootstrap_ci95_seed20260...` | `analysis/computed.json (compute_ledger.py)` :: `item3_derived.drop_unlabeled_sub06_sub13` |
| Diagnosis strata (descriptive only) | **Normal r 0.824 (n=10); pooled MCI/AD r 0.765 (n=23)** | `{"normal": {"pearson_r": 0.8242494607485127, "spearman_rho": 0.8424242424242423}, "pooled_mci_mild_ad_moderate_ad": {"pearson_r": 0.7651694019275322, "spearman_rho": 0.645256916...` | `results/metrics/early_response_gate.json` :: `diagnosis_subgroups.{normal,pooled_mci_mild_ad_moderate_ad}.continuous_early_late_association` |
| | *note* | Per-group recomputation (computed.json item3_by_group_descriptive): MCI r 0.949 (n=6), Mild AD r 0.693 / Spearman 0.347 (n=16). Do not present subgroup results; Holm-adjusted moderation p = 1.0 (early_response_gate.json mmse_and_diagnosis_exploration.tests.diagnosis_moderation_of_early_late_association). | |

**Robustness statement (backup slide / Q&A):** The association does not depend on one point: removing the single most influential participant (sub-05) gives r = 0.747; removing both highest-leverage participants (sub-01, sub-05) gives r = 0.699 (95% CI 0.421-0.862); rank-based Spearman rho = 0.688 on all 35. sub-01 has high leverage but lies on the regression line (Cook's D ~ 0), so excluding it lowers r only through reduced range. Both sub-01 and sub-05 are 6-block participants, which is why the 6-block cohort r (0.915, n=8) is inflated.

## 4. Cohort composition and protocol

| Claim | Slide form | Full-precision value | Source (file :: JSON path) |
|---|---|---|---|
| Group counts | **Normal 10, MCI 6, Mild AD 16, Moderate AD 1, unlabeled 2** | `{"Normal": 10, "Mild AD": 16, "-": 2, "MCI": 6, "Moderate AD": 1}` | `data/raw/ds005048/participants.tsv` :: `Group column` |
| Group membership | **see value** | `{"Normal": ["sub-01", "sub-03", "sub-08", "sub-09", "sub-10", "sub-12", "sub-22", "sub-25", "sub-26", "sub-31"], "Mild AD": ["sub-02", "sub-04", "sub-05", "sub-07", "sub-11", "s...` | `data/raw/ds005048/participants.tsv` :: `Group column` |
| Sex | **17 female, 18 male** | `{"Female": 17, "Male": 18}` | `data/raw/ds005048/participants.tsv` :: `Gender column` |
| | *note* | Matches source paper: 'Thirty-five volunteers (17 females, 54-89 years of age)' (Sci Rep 2024 Methods). | |
| Age | **mean 72.7 (SD 9.1), range 54-89 years** | `{"mean": 72.68571428571428, "sd_ddof1": 9.106466443820949, "min": 54.0, "max": 89.0, "median": 75.0}` | `data/raw/ds005048/participants.tsv` :: `Age column` |
| Per-group age/MMSE | **Normal MMSE 24-30; MCI 13-26; Mild AD 13-30; Moderate AD 23 (n=1); unlabeled: no MMSE** | `{"Normal": {"n": 10, "female": 5, "male": 5, "age_mean": 65.9, "age_min": 54.0, "age_max": 81.0, "mmse_min": 24.0, "mmse_max": 30.0, "mmse_mean": 27.0}, "Mild AD": {"n": 16, "fe...` | `data/raw/ds005048/participants.tsv` :: `Age, MMSE by Group` |
| MMSE overall (n=33 labeled) | **13-30, mean 22.3 (SD 4.9)** | `{"n": 33, "min": 13.0, "max": 30.0, "mean": 22.303030303030305, "sd_ddof1": 4.863671764243865}` | `data/raw/ds005048/participants.tsv` :: `MMSE column` |
| 6-block (short session) subjects | **sub-01..sub-08 (n=8)** | `["sub-01", "sub-02", "sub-03", "sub-04", "sub-05", "sub-06", "sub-07", "sub-08"]` | `data/raw/ds005048/sub-*/eeg/*_events.tsv` :: `count(trial_type == Stimulus) == 6` |
| | *note* | Matches results/metrics/early_late_connectivity_analysis.json protocol_cohorts.6 = 8. | |
| 10-block (long session) subjects | **sub-09..sub-35 (n=27)** | `["sub-09", "sub-10", "sub-11", "sub-12", "sub-13", "sub-14", "sub-15", "sub-16", "sub-17", "sub-18", "sub-19", "sub-20", "sub-21", "sub-22", "sub-23", "sub-24", "sub-25", "sub-2...` | `data/raw/ds005048/sub-*/eeg/*_events.tsv` :: `count(trial_type == Stimulus) == 10` |
| | *note* | Identical to target_position_sensitivity_plv.cycles_5_to_6.values.subject; matches protocol_cohorts.10 = 27. | |
| 6-block group labels | **3 Normal, 4 Mild AD, 1 unlabeled** | `{"sub-01": "Normal", "sub-02": "Mild AD", "sub-03": "Normal", "sub-04": "Mild AD", "sub-05": "Mild AD", "sub-06": "-", "sub-07": "Mild AD", "sub-08": "Normal"}` | `data/raw/ds005048/participants.tsv` :: `Group for sub-01..08` |
| Complete cycles | **6-block: 5 complete cycles; 10-block: 9** | `{"six_block": [5], "ten_block": [9]}` | `events.tsv` :: `Rest rows with duration >= 20 s` |
| | *note* | Why cycles 4-5 is the common later window: it is the last pair of non-overlapping complete cycles every participant has after skipping cycle 3. | |
| provenance.source_exclusions | **sub-06, sub-13** | `["sub-06", "sub-13"]` | `results/metrics/early_late_connectivity_analysis.json` :: `provenance.source_exclusions` |
| | *note* | These two lack Group/MMSE labels. They ARE included in all n=35 analyses (present in every values.subject array). The flag appears to be used only for 'source_comparable_t_test' (n=33) in stimulus_vs_rest blocks; the exact semantics lived in the lost script. METHODOLOGY.md in ds005048-download/ (local dataset download, outside the repo)  describes them as 'incomplete diagnosis'. | |
| Dataset preprocessing (by dataset authors) | **offline-preprocessed public EEG** | `"1 Hz high-pass; line-noise removal; bad-channel rejection/interpolation; average reference; ASR; re-average; ICA; dipole fitting; bad-dipole rejection (EEGLAB, Makoto pipeline)...` | `data/raw/ds005048/README` :: `EEG recording and preprocessing` |
| | *note* | More than '1 Hz HP + 50 Hz notch': includes ASR and ICA-based cleaning. Short sessions referenced to earlobes, long sessions to FCz at recording; both re-referenced to average. | |
| Stimulus | **40-Hz-modulated 5 kHz tone** | `"5 kHz carrier amplitude-modulated by 40 Hz rectangular wave, 4% duty cycle (1 ms on per 25 ms); 40 s trials with 20 s silence; short session 6 trials, long 10"` | `data/raw/ds005048/README` :: `Entrainment session and auditory stimulation` |

## 5. Frequency specificity (common position, cycles 4-5)

| Hz | r | Spearman | Pearson p | 95% CI recomputed (seed 20260809, 50k) | 95% CI stored in urtc_response_figure.json (seed 20260812) | Slide CI |
|---|---|---|---|---|---|---|
| 35 | **0.020** | -0.065 | 0.911 | -0.366 to 0.361 | -0.365 to 0.360 | -0.366 to 0.361 |
| 37 | **0.249** | 0.179 | 0.149 | -0.188 to 0.604 | -0.192 to 0.603 | -0.188 to 0.604 |
| 39 | **0.190** | 0.176 | 0.274 | -0.215 to 0.556 | -0.214 to 0.553 | -0.215 to 0.556 |
| 40 | **0.780** | 0.688 | 3.3e-8 | 0.571-0.889 | 0.570-0.889 | 0.573-0.889 (abstract CI) |
| 41 | **0.258** | 0.290 | 0.134 | -0.085 to 0.597 | -0.080 to 0.594 | -0.085 to 0.597 |
| 43 | **-0.099** | -0.013 | 0.570 | -0.427 to 0.279 | -0.429 to 0.276 | -0.427 to 0.279 |
| 45 | **0.039** | -0.032 | 0.822 | -0.394 to 0.394 | -0.387 to 0.391 | -0.394 to 0.394 |

r sources: `results/metrics/early_late_connectivity_analysis.json` :: `common_position_frequency_specificity_plv.statistics.primary_correlation` (40 Hz) and `...pairwise_participant_bootstrap.<f>_hz.control_correlation`; per-participant arrays `common_position_frequency_specificity_plv.values.{early,late}_by_frequency`.

Pairwise 40 Hz minus control (paired participant bootstrap):

| Control | Difference | 95% CI stored | 95% CI recomputed | Bonferroni familywise CI stored | Bonferroni recomputed | Familywise excludes 0? |
|---|---|---|---|---|---|---|
| 35_hz | **0.760** | 0.311-1.191 | 0.306-1.195 | 0.140-1.308 | 0.146-1.317 | yes |
| 37_hz | **0.531** | 0.165-0.966 | 0.164-0.968 | 0.058-1.126 | 0.064-1.132 | yes |
| 39_hz | **0.590** | 0.148-1.031 | 0.145-1.034 | -0.008 to 1.168 | -0.009 to 1.174 | **NO** |
| 41_hz | **0.522** | 0.159-0.875 | 0.156-0.873 | 0.049-0.998 | 0.043-1.001 | yes |
| 43_hz | **0.879** | 0.498-1.208 | 0.496-1.209 | 0.370-1.324 | 0.364-1.327 | yes |
| 45_hz | **0.741** | 0.293-1.219 | 0.294-1.221 | 0.138-1.384 | 0.144-1.382 | yes |

Stored paths: `common_position_frequency_specificity_plv.statistics.pairwise_participant_bootstrap.<f>_hz.{primary_minus_control,bootstrap_ci95,bonferroni_familywise_ci95}`.

| Claim | Slide form | Full-precision value | Source (file :: JSON path) |
|---|---|---|---|
| Minimum 40-vs-control difference (vs 41 Hz) | **0.522** | `0.5215259979155702` | `results/metrics/early_late_connectivity_analysis.json` :: `common_position_frequency_specificity_plv.statistics.minimum_primary_minus_control` |
| Bootstrap CI of minimum difference | **0.081-0.649** | `[0.08085866453222793, 0.6492234957392824]` | `results/metrics/early_late_connectivity_analysis.json` :: `common_position_frequency_specificity_plv.statistics.bootstrap_minimum_difference_ci95` |
| Recomputed minimum-difference CI (seed 20260809) | **0.083-0.647** | `[0.08311145998131661, 0.6473295276277178]` | `analysis/computed.json (compute_ledger.py)` :: `item5_frequency.min_diff_boot_ci95_recomputed` |
| Paired frequency-label randomization p | **2.0 x 10^-5** | `1.999980000199998e-05` | `results/metrics/early_late_connectivity_analysis.json` :: `common_position_frequency_specificity_plv.statistics.paired_frequency_label_randomization_p` |
| | *note* | = (1 + 1 exceedance)/(100,000 + 1). Null: frequency labels exchangeable within participant. | |
| Randomization exceedances | **1** | `1` | `results/metrics/early_late_connectivity_analysis.json` :: `common_position_frequency_specificity_plv.statistics.randomization_exceedances` |
| Share of bootstrap replicates where 40 Hz has the largest r | **99.2%** | `0.9924` | `analysis/computed.json (compute_ledger.py)` :: `item5_frequency.prop_boot_40_is_max` |
| Stored seed for this block | **20269809** | `20269809` | `results/metrics/early_late_connectivity_analysis.json` :: `common_position_frequency_specificity_plv.statistics.seed` |

**Flag (39 Hz):** 39 Hz Bonferroni familywise CI (6 comparisons, 0.417/99.583 percentiles) is [-0.008, 1.168] stored and [-0.009, 1.174] recomputed; it includes 0. All other five familywise CIs exclude 0. Pairwise (unadjusted) 95% CIs exclude 0 for all six. The simultaneous minimum-difference CI [0.081, 0.649] excludes 0 and is the most direct test of 'stronger than all six', but it is a different construction from the Bonferroni intervals, so do not claim 'significant after familywise correction for every frequency'.

**Safe wording:**
- SLIDE: 'Early-later association: 40 Hz r = 0.78 vs r = -0.10 to 0.26 at six neighboring frequencies'
- SPOKEN: 'The association was stronger at 40 Hz than at each of the six neighboring frequencies we tested.'
- If asked about statistics: 'Each pairwise bootstrap interval excluded zero, and the smallest 40-Hz advantage, over 41 Hz, was 0.52 with a 95% interval of 0.08 to 0.65. With a Bonferroni correction, the 39-Hz comparison's interval just touches zero, so I describe it as a consistent pattern rather than six separately significant tests.'
- AVOID: 'significantly stronger than every control frequency after correction', 'specific to 40 Hz', 'only at 40 Hz'.

Recomputed per-frequency CIs (seed 20260809) differ from urtc_response_figure.json (seed 20260812) by at most ~0.01 at any bound; pairwise and minimum-difference CIs differ from stored (seed 20269809) by <= 0.01. All conclusions identical.

## 6. Alternative synchronization measures (cycles 1-2 -> 4-5)

| Measure | r | p | Spearman (p) | 95% CI stored | 95% CI recomputed (seed 20260809) | ICC(A,1) | early>0 / later>0 | JSON path |
|---|---|---|---|---|---|---|---|---|
| PLV | **0.780** | 3.3 x 10^-8 | 0.688 (4.9e-6) | 0.573-0.889 | 0.571-0.889 | 0.776 | 28/22 | `common_position_measure_convergence.measures.plv` |
| PLI | **0.775** | 4.5 x 10^-8 | 0.601 (1.4e-4) | 0.441-0.904 | 0.438-0.904 | 0.740 | 22/26 | `common_position_measure_convergence.measures.pli` |
| WPLI | **0.659** | 1.7 x 10^-5 | 0.515 (0.0016) | 0.363-0.817 | 0.364-0.816 | 0.589 | 21/26 | `common_position_measure_convergence.measures.wpli` |

PLI and wPLI discard zero-lag coupling, so they are less sensitive to volume conduction/common reference than PLV. Positive association under both argues against a purely zero-lag artifact but does not rule out all shared-source explanations. Stored CIs (main analysis) and recomputed CIs (seed 20260809) agree to within 0.003.

## 7. Target-position sensitivity (early = cycles 1-2)

| Later window | n | r | 95% CI | p | Bonferroni p (6 tests) | Spearman (p) |
|---|---|---|---|---|---|---|
| 3-4 | 35 | **0.774** | 0.571-0.891 | 4.8e-8 | 2.9 x 10^-7 | 0.671 (1.0e-5) |
| 4-5 | 35 | **0.780** | 0.573-0.889 | 3.3e-8 | 2.0 x 10^-7 | 0.688 (4.9e-6) |
| 5-6 | 27 | **0.709** | 0.402-0.886 | 3.5e-5 | 2.1 x 10^-4 | 0.592 (0.0011) |
| 6-7 | 27 | **0.692** | 0.413-0.854 | 6.3e-5 | 3.8 x 10^-4 | 0.599 (9.6e-4) |
| 7-8 | 27 | **0.701** | 0.401-0.855 | 4.6e-5 | 2.7 x 10^-4 | 0.531 (0.0044) |
| 8-9 | 27 | **0.608** | 0.196-0.807 | 7.8e-4 | 0.0047 | 0.366 (0.060) |

Source: `results/metrics/early_late_connectivity_analysis.json` :: `target_position_sensitivity_plv.<pos>` and `target_position_multiplicity_plv.positions.<pos>`. Cycles 3-4 and 4-5 use all 35; cycles 5-6 onward exist only for the 27 ten-block participants, so later positions confound position with a smaller, different subsample. All six Bonferroni p < 0.05 (target_position_multiplicity_plv.all_bonferroni_p_below_0_05 = true). r declines from 0.78 (4-5) to 0.61 (8-9, Spearman 0.37, p = 0.06). Cycles 3-4 is immediately adjacent to the early window (no gap cycle), so it is the least independent later position. The primary position (4-5) was chosen as the common position, retrospectively (primary_endpoint.selection_rationale says not preregistered).

## 8. Stimulation vs silence, whole session

Definition: participant mean(stimulation) - mean(complete 20-second rest) (whole session, all complete windows).

- **40 Hz PLV (primary block)** `results/metrics/early_late_connectivity_analysis.json` :: `primary_frequency_measures.plv.stimulus_vs_rest`: mean diff `0.07677384655314717`, bootstrap CI `[0.044676696955981636, 0.11237276180552597]`, t(34) = `4.370888047366045`, p = `0.00011053183580441616`, Wilcoxon p = `7.843656931072474e-06`, positive 27/35; n=33 source-comparable t = 4.376, p = 1.21e-04.
- Slide: **stimulation > silence at 40 Hz: +0.077 PLV (95% CI 0.045-0.112), 27/35 participants, p = 1.1 x 10^-4**

| Frequency | Mean diff | 95% CI | t | p | n positive / 35 |
|---|---|---|---|---|---|
| 35_hz | 0.014 | 0.006-0.022 | 3.284 | 0.0024 | 24 |
| 37_hz | 0.001 | -0.007 to 0.009 | 0.227 | 0.821 | 13 |
| 39_hz | 0.012 | 0.004-0.020 | 2.844 | 0.0075 | 25 |
| 40_hz | 0.077 | 0.045-0.113 | 4.371 | 1.1 x 10^-4 | 27 |
| 41_hz | 0.007 | -0.002 to 0.016 | 1.541 | 0.133 | 20 |
| 43_hz | 0.002 | -0.008 to 0.011 | 0.377 | 0.709 | 18 |
| 45_hz | -0.0005 | -0.008 to 0.007 | -0.113 | 0.911 | 17 |

Source: `frequency_controls_plv.<f>.stimulus_vs_rest`. 40 Hz PLI / wPLI: PLI +0.020 (CI 0.007-0.036), p = 0.0096, 26/35 positive; WPLI +0.026 (CI 0.008-0.047), p = 0.015, 23/35 positive (`primary_frequency_measures.{pli,wpli}.stimulus_vs_rest`).

40 Hz CI differs slightly between primary_frequency_measures.plv ([0.0447, 0.1124]) and frequency_controls_plv.40_hz ([0.0450, 0.1127]): same data, different bootstrap draws; use the primary block. 35 Hz (+0.014, p=0.002) and 39 Hz (+0.012, p=0.007) also show small positive differences, about 1/5-1/6 of the 40 Hz effect; neighboring frequencies are comparison bands, not true nulls. 27/35 positive at 40 Hz vs 13-25/35 at controls.

## 9. Absolute stimulation PLV stability vs contrast stability

| Frequency | Absolute stim PLV r (first block -> late blocks) | 95% CI | Mean abs PLV first / late | Contrast r (cycles 1-2 -> last 2 cycles) | 95% CI | Contrast r (cycles 1-2 -> 4-5) |
|---|---|---|---|---|---|---|
| 35_hz | 0.867 | 0.762-0.935 | 0.515 / 0.498 | -0.090 | -0.378 to 0.261 | 0.020 |
| 37_hz | 0.888 | 0.804-0.945 | 0.519 / 0.482 | 0.011 | -0.365 to 0.393 | 0.249 |
| 39_hz | 0.894 | 0.832-0.946 | 0.505 / 0.484 | -0.163 | -0.417 to 0.108 | 0.190 |
| 40_hz | 0.928 | 0.865-0.963 | 0.569 / 0.546 | 0.737 | 0.494-0.859 | 0.780 |
| 41_hz | 0.875 | 0.777-0.937 | 0.496 / 0.480 | -0.193 | -0.440 to 0.121 | 0.258 |
| 43_hz | 0.908 | 0.840-0.950 | 0.496 / 0.473 | 0.046 | -0.277 to 0.418 | -0.099 |
| 45_hz | 0.928 | 0.876-0.963 | 0.494 / 0.468 | -0.046 | -0.416 to 0.299 | 0.039 |

Sources: `frequency_controls_plv.<f>.absolute_first_block_to_late_blocks`, `frequency_controls_plv.<f>.response_gain_early_to_late`, `common_position_frequency_specificity_plv`.

- Definitions: absolute_first_block_to_late_blocks: stimulation-window PLV (not a contrast) in the first stimulation block vs the late blocks (command arg --late-absolute-blocks 3, i.e. last 3 blocks of each participant's own session). response_gain_early_to_late: stimulation-minus-following-rest contrast, cycles 1-2 vs each participant's last 2 non-overlapping complete cycles (protocol-dependent position; cf. one-cycle file primary_endpoint.target wording). Exact block definitions lived in the lost script.
- What it shows: Absolute stimulation PLV is highly stable at every frequency (r 0.87-0.93), with no 40 Hz advantage, so raw frontal-posterior phase consistency is largely a stable participant trait (anatomy, electrode/reference geometry, volume conduction, broadband state). Subtracting the following silence removes that trait: the stimulation-silence contrast is stable only at 40 Hz (0.74 last-2-cycles; 0.78 cycles 4-5) and near zero at controls (-0.19 to 0.05 last-2-cycles; -0.10 to 0.26 cycles 4-5). This is why the talk uses the contrast rather than raw PLV.
- What it does not show: It does not prove the 40 Hz contrast is neural entrainment rather than a stimulus-locked artifact (no sham, fixed stim-then-silence order, no auditory-artifact control), does not show the contrast is independent of absolute PLV level, and does not show test-retest reliability across sessions. High absolute-PLV stability should not be quoted as evidence for the response measure.

## 10. early_response_gate.json (Q&A only, keep off slides)

| Claim | Slide form | Full-precision value | Source (file :: JSON path) |
|---|---|---|---|
| AUC (early contrast discriminating later contrast > 0) | **0.832** | `0.8321678321678322` | `results/metrics/early_response_gate.json` :: `continuous_discrimination.auc` |
| AUC stratified bootstrap 95% CI | **0.682-0.948** | `[0.6818181818181818, 0.9475524475524476]` | `results/metrics/early_response_gate.json` :: `continuous_discrimination.bootstrap.ci` |
| Label permutation p (100,000) | **7.2 x 10^-4** | `0.0007199928000719992` | `results/metrics/early_response_gate.json` :: `continuous_discrimination.label_permutation.p_two_sided` |
| Outcome prevalence | **22 later-positive / 13 later-nonpositive** | `[22, 13]` | `results/metrics/early_response_gate.json` :: `endpoint.n_later_positive / n_later_nonpositive` |
| Zero threshold sensitivity | **20/22 = 0.909 (Wilson 0.722-0.975)** | `{"estimate": 0.9090909090909091, "numerator": 20, "denominator": 22, "ci": [0.7218505315839417, 0.9747045710090046], "ci_method": "Wilson score; descriptive conditional interval...` | `results/metrics/early_response_gate.json` :: `fixed_zero_threshold.metrics.sensitivity` |
| Zero threshold specificity | **5/13 = 0.385 (Wilson 0.177-0.645)** | `{"estimate": 0.38461538461538464, "numerator": 5, "denominator": 13, "ci": [0.17709707797762575, 0.6447710848733431], "ci_method": "Wilson score; descriptive conditional interva...` | `results/metrics/early_response_gate.json` :: `fixed_zero_threshold.metrics.specificity` |
| Zero threshold PPV / NPV | **0.714 / 0.714** | `[0.7142857142857143, 0.7142857142857143]` | `results/metrics/early_response_gate.json` :: `fixed_zero_threshold.metrics.{positive,negative}_predictive_value` |
| LOPO Youden sensitivity / specificity | **15/22 = 0.682 / 8/13 = 0.615; balanced accuracy 0.649; no CI (overlapping training sets)** | `[0.6818181818181818, 0.6153846153846154]` | `results/metrics/early_response_gate.json` :: `leave_one_participant_out_youden_threshold.metrics` |

Guardrails:
- Early cycles 1-2 PLV contrast discriminates whether the same offline neural contrast is positive at common-position cycles 4-5.
- The analysis does not establish patient benefit, cognitive benefit, diagnosis, prospective performance, or a validated decision rule.
- Zero threshold was chosen post hoc (fixed_zero_threshold.threshold_status); Wilson CIs exclude threshold-selection uncertainty.
- Outcome is a neural label (later contrast > 0), not a clinical outcome. Specificity at zero is low (0.385).
- LOPO-fitted threshold performance (balanced accuracy 0.649) is the honest held-out estimate; it is modest.
- Keep off slides. Use only if asked 'could you use this to decide something?'

## 11. DO NOT SAY

| Avoid | Why | Say instead |
|---|---|---|
| Early EEG predicts later response / predictive biomarker | Retrospective, same-session, endpoint chosen after seeing the data; held-out calibration adds nothing over persistence. | Early and later contrasts were associated within the same session (r = 0.78). |
| Predicts clinical benefit / identifies responders to therapy / useful for treatment | No clinical or cognitive outcome was analyzed; single session. | Any relationship to clinical benefit is untested. |
| Proves 40 Hz entrainment / neural entrainment | No sham, fixed stim-then-silence order, stimulus-locked artifact not excluded; neighboring frequencies also show small stim-silence differences. | Stimulation-silence differences in 40-Hz phase-locking. |
| Stimulation causes / increases synchronization; enhances connectivity | Fixed order without sham; silence always follows stimulation. | Synchronization was higher during stimulation than during the following silence. |
| Reliable / reproducible / test-retest reliable measure | Only within one session; cross-session reproducibility untested (abstract says so). | Consistent within a session; reproducibility across sessions is untested. |
| Generalizes to Alzheimer's patients / works in AD | n = 35 mixed memory-clinic cohort from one site; 10 cognitively normal, 2 unlabeled; subgroup analyses descriptive only. | In a mixed memory-clinic cohort of 35 participants. |
| Enables closed-loop / adaptive / individualized stimulation now | Offline preprocessed data (ASR/ICA on whole recordings), not streaming-causal (method_guardrails.source_preprocessing_note). | Supports prospective evaluation of an early within-session measure. |
| Specific to 40 Hz / only at 40 Hz / significant vs every frequency after correction | 39 Hz Bonferroni familywise CI includes 0. | Stronger at 40 Hz than at each of six neighboring frequencies. |
| Early response equals later response / no change over time | Absence of a significant bias (p = 0.25) is not equivalence; Bland-Altman limits are wide (-0.16 to +0.13). | No systematic shift in the group mean; individual values varied. |
| Screening gate / 91% sensitivity classifier | Post hoc threshold, neural outcome label, specificity 0.38, LOPO balanced accuracy 0.65. | (Q&A only) An early threshold is a candidate for prospective testing. |
| Diagnosis or MMSE moderates the effect / works better in normals | All Holm-adjusted p >= 0.86; subgroups small. | No evidence of moderation by diagnosis or MMSE in this sample (exploratory). |
| Brain-wide / network / default mode network synchronization | Measure is frontal-posterior scalp electrode pairs, sensor level. | Frontal-posterior scalp EEG synchronization. |
| Real-time / online measurement | Offline analysis of preprocessed recordings. | Offline analysis of public recordings. |
| Quoting the figure CI 0.570-0.889 or the 6-block r = 0.915 | Figure CI is a different bootstrap seed; 6-block r rests on n=8 and contains the two highest-leverage points. | Use 0.573-0.889 and the full-sample r. |
