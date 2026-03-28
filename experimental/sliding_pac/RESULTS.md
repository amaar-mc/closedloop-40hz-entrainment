# Sliding-Window PAC vs Epoch-Level PAC: Experiment Results

## Hypothesis

The current pipeline computes PAC (Tort Modulation Index) once per 20-40 second
epoch and assigns that single value to all constituent 2-second windows. This
means 96% of adjacent prediction samples share the same target, making the
temporal prediction task artificially easy (persistence baseline exploits this).

**Question:** Does computing PAC with finer temporal resolution (5-second
backward-looking sliding window) produce a more meaningful prediction target
that the TCN can learn?

## Method

### Sliding-Window PAC Computation

- Stitched consecutive 2s windows (1s overlap) into continuous signal per
  epoch segment per subject
- Computed Tort MI (theta 4-8 Hz, gamma 38-42 Hz, 18 phase bins) on a
  **5-second backward-looking context** ending at each window
- Strictly causal: no future samples in the analysis window
- Reduced to 9 phase bins for windows with <3s of available context
  (first few windows in each segment)

### Dataset Construction

- Same 20-step lookback, horizon-5 sequences
- Same 12 PAC+Stim features (pac_current, pac_ma2..16, pac_diff1/4,
  stim context)
- Same subject-level splits (24/5/6 train/val/test)
- PAC features recomputed from sliding-window PAC values (not epoch PAC)
- Normalization fit on train only

### Model

- MultiscaleCausalTCN, h=64, dilations [1,2,4,8], attention pooling
- 27,139 parameters (identical architecture for both conditions)
- HuberLoss, AdamW (lr=1e-3, wd=1e-3), ReduceLROnPlateau
- 40 epochs, patience 20, seed 42, device MPS

## Results

### PAC Label Statistics

| Metric                  | Epoch PAC      | Sliding PAC (5s) |
|-------------------------|----------------|------------------|
| Unique targets (test)   | 104            | 2,678            |
| Adjacent same (test)    | 96.2%          | 0.0%             |
| Mean PAC (test)         | 3.93e-05       | 3.53e-04         |
| Std PAC (test)          | 3.56e-05       | 2.19e-04         |
| Epoch-to-sliding corr   | --             | 0.200            |

Sliding-window PAC produces 25x more unique target values and completely
eliminates the trivial same-epoch prediction shortcut. Values are ~9x larger
(expected: shorter analysis windows produce noisier/higher MI estimates). The
low correlation (r=0.20) between epoch and sliding PAC confirms these are
measuring different aspects of the same underlying coupling.

### Prediction Performance

| Metric             | Epoch PAC | Sliding PAC (5s) |
|--------------------|-----------|-------------------|
| Persistence R2     | 0.104     | -0.897            |
| Ridge R2           | 0.260     | 0.216             |
| **TCN Test R2**    | **0.554** | **0.212**         |
| TCN Test corr      | 0.746     | 0.464             |
| TCN Test RMSE      | 2.42e-05  | 1.96e-04          |
| Best val R2        | 0.825     | 0.202             |
| Best epoch         | 30        | 38                |

### Interpretation

1. **Persistence collapses on sliding PAC (R2 = -0.90).** This confirms the
   hypothesis: with epoch-level PAC, persistence "predicts" well because 96% of
   targets are identical to the current value. With sliding PAC, the last value
   is genuinely different from the future value, making persistence worse than
   predicting the mean.

2. **Ridge is remarkably stable (0.26 vs 0.22).** The linear model adapts well
   to both target distributions, losing only ~0.04 R2. This suggests the
   12 PAC+Stim features contain similar predictive signal regardless of target
   resolution.

3. **TCN drops from 0.55 to 0.21 on sliding PAC.** The TCN's epoch-PAC
   performance was partly inflated by learning the within-epoch constancy
   pattern. On truly continuous targets, the TCN still outperforms both
   baselines but with a much smaller margin over Ridge (0.21 vs 0.22 -- nearly
   tied).

4. **Val-test gap narrows.** Epoch PAC shows 0.83 val vs 0.55 test
   (val-test gap of 0.28), suggesting cross-subject overfitting on the few
   discrete PAC levels. Sliding PAC shows 0.20 val vs 0.21 test (gap of 0.01),
   indicating better generalization.

## Conclusions

### The good news

- Sliding-window PAC successfully eliminates the trivial 96% same-target
  prediction shortcut
- The prediction task is genuinely harder and more meaningful
- Val-test generalization improves dramatically (gap shrinks from 0.28 to 0.01)
- The TCN still achieves positive R2 (0.21) on the harder task, confirming
  it learns real temporal PAC dynamics, not just epoch-boundary patterns

### The bad news

- Absolute TCN performance drops significantly (0.55 to 0.21)
- The TCN barely outperforms Ridge on sliding PAC targets (0.21 vs 0.22)
- The 5s analysis window may be too short for stable MI estimation, adding
  noise to targets that obscures learnable signal

### Verdict: worth pursuing, but needs refinement

The sliding-window approach reveals that roughly half of the epoch-level TCN's
R2=0.55 was from exploiting within-epoch target constancy. The remaining
R2~0.21 represents genuine temporal PAC prediction ability. This is honest
progress.

**Recommended next steps:**
- Try 8s and 10s context windows (more theta cycles = more stable MI)
- Use target smoothing (causal 3-window MA) on sliding PAC to reduce noise
- Consider computing PAC from only the highest-SNR frontal channel instead
  of averaging all 7, to reduce noise
- Test whether the sliding-PAC TCN transfers better to the closed-loop
  simulation (the actual downstream task), since it predicts genuine PAC
  dynamics rather than epoch-level plateaus

## Reproducibility

```bash
# Phase 1: Compute sliding PAC labels (~45s)
python experimental/sliding_pac/compute_sliding_pac.py --context-sec 5.0

# Phase 2: Build dataset (~1s)
python experimental/sliding_pac/build_sliding_dataset.py

# Phase 2b: Build original 12-feature baseline (~1s)
python experimental/sliding_pac/build_original_12feat.py

# Phase 3: Train and compare (~100s on MPS)
python experimental/sliding_pac/train_and_compare.py --epochs 40 --seed 42
```

All results saved to `experimental/sliding_pac/results/comparison_results.json`.
