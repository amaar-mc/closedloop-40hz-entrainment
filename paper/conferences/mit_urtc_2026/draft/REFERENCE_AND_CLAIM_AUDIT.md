# MIT URTC Reference and Claim Audit

**Audited:** 2026-05-31
**Updated:** 2026-06-23
**Scope:** manuscript references, background claims, repository-backed methods, reported metrics, and
editorial wording

## Reference Audit

| Ref. | Primary source                                                                          | Verification result                                                                                                                                                                                        |
| ---- | --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [1]  | Iaccarino et al., _Nature_ (2016), doi:10.1038/nature20587                              | Verified. Supports the statement that induced 40 Hz activity reduced amyloid burden and altered microglial response in 5XFAD mice.                                                                         |
| [2]  | Lahijanian et al., _Scientific Reports_ (2024), doi:10.1038/s41598-024-63727-z          | Verified. Supports the memory-clinic cohort, 19 monopolar EEG channels at 250 Hz, 40 Hz auditory entrainment background, frontoparietal synchrony statement, and reported Makoto preprocessing pipeline.   |
| [3]  | OpenNeuro `ds005048`, version `1.0.1`, doi:10.18112/openneuro.ds005048.v1.0.1           | Added as a standalone dataset citation. The article's data-availability section links the earlier `1.0.0` release; the repository uses the local `1.0.1` release identified in `dataset_description.json`. |
| [4]  | Soleimani et al., _Translational Psychiatry_ (2023), doi:10.1038/s41398-023-02565-5     | Verified. Supports the general closed-loop neuromodulation context.                                                                                                                                        |
| [5]  | Tort et al., _Journal of Neurophysiology_ (2010), doi:10.1152/jn.00106.2010             | Verified. Supports the modulation-index method, Kullback-Leibler divergence formulation, and 18 phase-bin construction.                                                                                    |
| [6]  | Hipp and Siegel, _Frontiers in Human Neuroscience_ (2013), doi:10.3389/fnhum.2013.00338 | Added. Supports the warning that cranial and ocular muscle activity can confound sensor-level gamma-band EEG.                                                                                              |
| [7]  | Aru et al., _Current Opinion in Neurobiology_ (2015), doi:10.1016/j.conb.2014.08.002    | Supports the caution that cross-frequency coupling estimates can be confounded by nonstationarity, filtering, waveform shape, and other non-coupling effects.                                              |
| [8]  | Bai et al., arXiv:1803.01271 (2018)                                                     | Verified. Supports the use of temporal convolutional networks for causal sequence modeling.                                                                                                                |

## Repository Claim Audit

| Manuscript claim                                                                                                                     | Local evidence                                                                                    | Status                                |
| ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- | ------------------------------------- |
| OpenNeuro release `ds005048` version `1.0.1`                                                                                         | `data/raw/ds005048/dataset_description.json`                                                      | Verified                              |
| 35 participants; 19 recorded channels; 250 Hz sampling                                                                               | dataset files, source article, `paper/data/key_results.md`                                        | Verified                              |
| Seven frontal channels: `Fp1`, `Fp2`, `F7`, `F3`, `Fz`, `F4`, `F8`                                                                   | `src/data_loader.py`                                                                              | Verified                              |
| Local additional conditioning: `0.5-80 Hz` band-pass, `50 Hz` notch, threshold masking, common-average rereferencing                 | `src/preprocessing.py`, `src/data_loader.py`                                                      | Verified                              |
| Event-period PAC labels, two-second windows, one-second hop                                                                          | `src/data_loader.py`                                                                              | Verified                              |
| Tort modulation index: theta `4-8 Hz`, gamma `38-42 Hz`, 18 bins                                                                     | `src/pac_computation.py`                                                                          | Verified                              |
| 20-step stored-series lookback; five-step future index; train-only normalization                                                     | `temporal_multiscale/build_multiscale_dataset.py`                                                 | Verified                              |
| 12 selected inputs: seven PAC features and five stimulation-context features                                                         | `temporal_multiscale/build_multiscale_dataset.py`, `paper/data/key_results.md`                    | Verified                              |
| Participant split: 24 training, 5 validation, 6 held-out test                                                                        | `results/rigor_audit/07_leakage_audit.md`                                                         | Verified                              |
| Temporal samples: 11,160 training, 2,605 validation, 2,678 test                                                                      | `results/rigor_audit/07_leakage_audit.md`                                                         | Verified                              |
| Single-seed ablation: 73 features `R^2 = -0.025`; 12 features `R^2 = 0.558`                                                          | `archive/experimental/results/generalization_7ch.json`                                            | Verified as held-out test performance |
| Five-seed selected-model mean `R^2 = 0.606`, range `0.558-0.647`                                                                     | `archive/experimental/results/pac_stim_focused.json`                                              | Verified as held-out test performance |
| Current integrated checkpoint architecture: 12 inputs, 27,139 parameters                                                             | `models/best_12feat_tcn_lb20_hz5_ts1.pth`, `scripts/pipeline/run_12feat_validation.py --no-train` | Verified                              |
| Replay: predictive strategy improves low-PAC coverage but reduces above-median-PAC rest rate and does not improve balanced alignment | `results/metrics/controller_comparison_12feat.json`                                               | Verified                              |
| Repeated-label caveat: 82.2% identical current and target PAC; cross-event persistence `R^2 = -0.272`                                | `results/rigor_audit/07_leakage_audit.md`                                                         | Verified                              |

## Editorial Audit

The manuscript was revised to:

- cite the OpenNeuro dataset formally;
- separate the source study's Makoto preprocessing from the repository's additional local
  conditioning stage;
- state the animal-model and human EEG background claims more precisely;
- state the PAC value as a scalar frontal EEG timing target rather than definitive physiological
  coupling evidence;
- remove the visible double-hyphen abstract and keyword labels;
- replace generic or inflated phrases with direct technical wording;
- cite the gamma-band cranial/ocular artifact warning;
- remove the horizon-sweep table and the benchmark table that duplicated Figure 1;
- describe replay as an offline controller diagnostic rather than a closed feedback-loop
  experiment;
- keep held-out forecasting results separate from full-cohort replay results; and
- preserve the mixed controller outcome rather than implying treatment efficacy.

## Important Boundaries

- The forecasting results are held-out participant results, not clinical outcomes.
- The replay includes all 35 recorded trajectories and is not an additional held-out forecasting
  test.
- Replay cannot model physiological responses to counterfactual stimulation timing.
- Complete-event PAC values are assigned back to constituent windows. The sequence targets are
  future-indexed within the stored series, but online availability of PAC inputs has not been
  established.
- The repeated event-period PAC labels make transition-specific forecasting a priority for future
  work.
- An older leakage-audit sentence labels the `-0.025` to `0.606` comparison as validation
  performance. Submission prose uses the underlying held-out test artifacts and the correct
  held-out test wording.
- The validation command prints checkpoint metadata `test_r2=0.5844`; the manuscript avoids that
  collapsed checkpoint-performance claim because the forecasting, stress-test, and replay results
  are presented as separate generation paths.
