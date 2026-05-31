# MIT URTC Evidence Map

Use this map as the source-of-truth boundary for manuscript claims. The repository contains multiple
model generations. Do not combine metrics across generations unless the distinction is stated.

## Primary Manuscript Sources

| Claim area | Primary source |
|---|---|
| Raw dataset identity and local participant table | [`../../../data/raw/ds005048/dataset_description.json`](../../../data/raw/ds005048/dataset_description.json), [`../../../data/raw/ds005048/participants.tsv`](../../../data/raw/ds005048/participants.tsv) |
| PAC computation | [`../../../src/pac_computation.py`](../../../src/pac_computation.py) |
| Epoch labeling, window extraction, and subject splits | [`../../../src/data_loader.py`](../../../src/data_loader.py) |
| Causal feature construction and normalization | [`../../../temporal_multiscale/build_multiscale_dataset.py`](../../../temporal_multiscale/build_multiscale_dataset.py) |
| Sequence counts and 24/5/6 split | [`../../../data/processed/multiscale_temporal_lb20_hz5_ts1/metadata.json`](../../../data/processed/multiscale_temporal_lb20_hz5_ts1/metadata.json) |
| Current temporal architecture | [`../../../temporal_multiscale/multiscale_tcn.py`](../../../temporal_multiscale/multiscale_tcn.py) |
| Feature ablation | [`../../../archive/experimental/results/generalization_7ch.json`](../../../archive/experimental/results/generalization_7ch.json) |
| Five-seed PAC+Stim forecasting experiment | [`../../../archive/experimental/results/pac_stim_focused.json`](../../../archive/experimental/results/pac_stim_focused.json) |
| Single-seed horizon sweep | [`../../../archive/experimental/results/horizon_sweep_pac_stim.json`](../../../archive/experimental/results/horizon_sweep_pac_stim.json) |
| Backward-looking PAC stress test | [`../../../archive/experimental/sliding_pac/RESULTS.md`](../../../archive/experimental/sliding_pac/RESULTS.md), [`../../../archive/experimental/sliding_pac/results/comparison_results.json`](../../../archive/experimental/sliding_pac/results/comparison_results.json), [`../../../archive/experimental/sliding_pac/compute_sliding_pac.py`](../../../archive/experimental/sliding_pac/compute_sliding_pac.py) |
| Independent leakage audit and caveats | [`../../../results/rigor_audit/07_leakage_audit.md`](../../../results/rigor_audit/07_leakage_audit.md) |
| Current 12-feature controller integration logic | [`../../../scripts/pipeline/run_12feat_validation.py`](../../../scripts/pipeline/run_12feat_validation.py) |
| Current 12-feature controller replay summary | [`../../../results/metrics/controller_comparison_12feat.json`](../../../results/metrics/controller_comparison_12feat.json) |

## Historical Sources

| Claim area | Source | Usage rule |
|---|---|---|
| Older 73-feature controller replay | [`../../../results/metrics/tcn_validation_results.json`](../../../results/metrics/tcn_validation_results.json) | Historical context only. Do not present its 72.1% alignment or 82.6% low-PAC targeting as results of the final 12-feature checkpoint. |
| Older consolidated report | [`../../../results/RESULTS_REPORT.md`](../../../results/RESULTS_REPORT.md) | Historical context only. It predates the final 12-feature replay. |
| Older broad methodology narrative | [`../../../docs/methodology/CURRENT_METHODOLOGY.md`](../../../docs/methodology/CURRENT_METHODOLOGY.md) | Use code and machine-readable artifacts when this document conflicts with the current checkpoint. |

## Claim Boundaries

- Use **offline replay**, **retrospective evaluation**, or **controller replay** for the N=35
  controller comparison.
- State that controller replay is a full-cohort integration diagnostic across the training,
  validation, and test trajectories, not an additional held-out forecasting test.
- State that the replay measures decision alignment against recorded PAC. It does not model the
  physiological response to counterfactual stimulation decisions.
- Do not claim clinical efficacy, prospective deployment, patient outcomes, or reduced disease
  progression.
- Report held-out-subject prediction and subject-level split methodology explicitly.
- State that the selected temporal input uses PAC trajectory and stimulation-context features.
- Treat the statement that spectral features encode anatomy as a hypothesis consistent with the
  ablation, not a directly proven mechanism.
- Keep the five-seed forecasting experiment separate from the retrained controller-integration
  checkpoint. See [`draft/CLAIM_AUDIT.md`](draft/CLAIM_AUDIT.md).
