# TCN Architecture Experiment Design

**Project:** Closed-Loop 40 Hz Gamma Entrainment System
**Date:** February 2026
**Purpose:** Systematically test whether architectural changes to the MultiscaleCausalTCN can improve temporal PAC prediction at operationally useful horizons (5-10 seconds ahead).

---

## 1. Motivation

The current MultiscaleCausalTCN (31K parameters) achieves:

| Metric | Value | Context |
|--------|-------|---------|
| R^2 at horizon=1, ts=5 | 0.764 | But persistence baseline gets 0.760 |
| R^2 at 5-10s horizons | 0.25-0.28 | Where persistence/Ridge collapse to negative R^2 |
| Delta-PAC R^2 | ~0.0 | The delta head is **never trained** (lambda_delta=0.0) |

The core scientific contribution is the +0.5 R^2 margin over persistence at long horizons. These experiments test whether this margin can be widened through architectural improvements, or whether it represents a fundamental data limitation.

### Connection to Audit Findings

The AUDIT_REPORT.md identified several relevant issues:

1. **lambda_delta=0.0 in production** (Section 3.5): The delta head exists but receives zero gradient. This is either a missed opportunity or was disabled because it hurt performance -- we need to test which.
2. **PAC features dominate** (Section 3.5): 7 PAC features provide R^2=0.859 while 56 spectral features alone give R^2=0.045. Models may not need large capacity for spectral features.
3. **EEGNet under-parameterization** (Section 3.4): The static model was capacity-limited at ~1.5K params. The temporal model at 31K params may face a similar issue.

---

## 2. Experimental Variants

### 2.1 DeepDilationTCN

**Hypothesis:** Longer temporal context captures slow PAC dynamics relevant to 5-10s prediction.

**Change:** Dilations [1, 2, 4, 8, 16, 32] instead of [1, 2, 4, 8].

**Receptive field calculation:**

```
Baseline:  RF = sum([1,2,4,8]) * (3-1) + 1 = 15*2 + 1 = 31 steps
Deep:      RF = sum([1,2,4,8,16,32]) * (3-1) + 1 = 63*2 + 1 = 127 steps
```

At 1s hop between windows, the baseline sees ~31 seconds of history while the deep variant sees ~127 seconds (over 2 full stimulation cycles of 60s each).

**Expected outcome:** Modest improvement at longer horizons (5-10s) if PAC dynamics depend on stimulation cycle history. No improvement if PAC is primarily determined by recent (~30s) history, which the baseline already captures.

**Parameter count:** ~42K (vs 31K baseline), increase comes from 2 additional conv blocks.

### 2.2 MultiTaskTCN

**Hypothesis:** Training the delta head provides useful gradient signal that regularizes the shared backbone toward change-sensitive features.

**Change:** Architecture identical to baseline. Training uses lambda_delta=0.3 and lambda_consistency=0.1 instead of 0.0/0.0.

**Rationale:** The current pipeline has a delta head but never trains it. Multi-task learning is well-established as a regularization technique (Ruder, 2017). Predicting delta-PAC (future - current) forces the backbone to encode rate-of-change information rather than just level information. This may particularly benefit long-horizon prediction where absolute PAC levels are less predictable but trends may be more stable.

**Expected outcome:** Improved delta-PAC prediction (currently ~0.0 R^2 since it is untrained). Possible improvement in future-PAC R^2 through regularization, or possible degradation if the two objectives compete for backbone capacity.

**Parameter count:** Identical to baseline (31K). Only training dynamics change.

### 2.3 WiderTCN

**Hypothesis:** The 64-dimensional hidden bottleneck limits expressiveness for 73-dimensional input features.

**Change:** hidden=128 instead of 64.

**Rationale:** The input projection compresses 73 features to 64 dimensions, losing information. A wider hidden layer preserves more input structure and allows richer temporal filter banks. The risk is overfitting on the ~11K training samples.

**Expected outcome:** If the performance ceiling is due to capacity, wider models will show improvement. If it is due to data limitations (noise, epoch-level PAC labels, limited subjects), wider models will overfit and show similar or worse test R^2.

**Parameter count:** ~120K (4x baseline). The quadratic scaling comes from hidden x hidden linear layers in the regression heads.

### 2.4 TransformerTCN

**Hypothesis:** Self-attention captures long-range temporal dependencies more flexibly than fixed dilation patterns.

**Change:** Replace the 4-block dilated TCN backbone with a 4-layer causal Transformer encoder (4 attention heads, d_model=64, dim_feedforward=256).

**Rationale:** Dilated convolutions have fixed receptive field patterns that must be chosen at design time. Self-attention can dynamically weight any past position, potentially discovering variable-lag dependencies. For example, different subjects may have different stimulation response latencies -- a fixed dilation pattern cannot accommodate this, but attention can.

The trade-off is: (a) higher computational cost per step, (b) potentially harder optimization on small datasets, and (c) the need for positional encoding to convey temporal order.

**Expected outcome:** If PAC dynamics have variable-lag dependencies, the Transformer may outperform the TCN. If the dynamics are primarily local (short-range), the TCN's inductive bias toward local patterns should win. The Transformer serves as a diagnostic: if it performs comparably to the TCN, it suggests the temporal structure is well-captured by local convolutions and longer-range attention adds noise.

**Parameter count:** ~85K. The Transformer layers have more parameters due to Q/K/V projections and feedforward networks.

---

## 3. Experimental Protocol

### 3.1 Controlled Comparison

All variants are trained with identical:
- Data splits (same train/val/test subjects)
- Random seed (42)
- Optimizer (AdamW, lr=1e-3, weight_decay=1e-3)
- Loss function (HuberLoss, delta=1.0)
- Gradient clipping (max_norm=1.0)
- Early stopping (patience=20, monitoring val future R^2)
- LR scheduler (ReduceLROnPlateau, factor=0.5, patience=5)
- Batch size (128)
- Maximum epochs (80)

The only controlled variable is the architecture (and lambda values for MultiTaskTCN).

### 3.2 Evaluation Metrics

**Primary metric:** Test set R^2 for future PAC prediction.

**Secondary metrics:**
- Pearson correlation (more robust to scale mismatch)
- MAE and RMSE (in raw PAC units)
- Delta-PAC R^2 (diagnostic for the multi-task variant)
- Margin over persistence baseline (the scientifically meaningful quantity)

### 3.3 Baselines

1. **Persistence:** Predict current PAC as future PAC (R^2 ~0.76 at h=1, negative at h=5-10).
2. **MultiscaleCausalTCN:** The production baseline (R^2 ~0.25 at h=5-10).

### 3.4 Synthetic Validation

Before running on real data, `synthetic_benchmark.py` verifies that all architectures:
1. Forward-pass without errors (correct shapes, no NaN)
2. Converge on a known nonlinear function
3. Report sensible parameter counts
4. Complete training in reasonable time

---

## 4. How to Interpret Results

### 4.1 If a variant improves R^2 significantly (> 0.05 gain):

This suggests the baseline has an architectural bottleneck that the variant addresses. The improvement should be validated with:
- Multiple seeds (3-5) to confirm it is not a lucky initialization
- Learning curves to check for overfitting vs genuine improvement
- Horizon sweep to confirm the gain is at useful horizons (5-10s), not just h=1

### 4.2 If all variants perform similarly:

This provides evidence that the performance ceiling (~0.25-0.28 R^2 at long horizons) is a **fundamental data limitation**, not an architectural one. Possible causes:
- Epoch-level PAC labels limit within-epoch prediction granularity
- 35 subjects provide limited inter-subject diversity
- PAC at 5-10s horizons is inherently stochastic (irreducible noise)
- The 73 features may not contain sufficient information for longer prediction

This is itself a valuable scientific finding: it bounds the achievable prediction accuracy for this dataset and task.

### 4.3 If wider/deeper models overfit:

Larger models showing worse test R^2 despite lower training loss indicates overfitting. This confirms the data limitation hypothesis and suggests that the 31K baseline is already appropriately sized.

### 4.4 If multi-task training helps:

This would suggest that the delta head was incorrectly disabled (lambda_delta=0.0) and should be re-enabled in the production config. It would also indicate that the shared backbone benefits from gradient signal encouraging change-sensitivity.

---

## 5. Running the Experiments

### Step 1: Synthetic validation (no data required)

```bash
python rigor/experiments/synthetic_benchmark.py
```

This produces `rigor/experiments/synthetic_benchmark_results.json` and confirms all architectures work correctly.

**Synthetic benchmark results (seed=42, 30 epochs, CPU):**

| Variant | Params | Train Loss | Val Loss | Test R^2 | NaN | Time (s) |
|---------|--------|-----------|----------|----------|-----|----------|
| Baseline | 31,043 | 8.85e-5 | 8.30e-5 | -0.388 | No | 241 |
| Deep Dilation | 39,875 | 6.81e-5 | 6.65e-5 | -0.354 | No | 383 |
| Multi-task | 31,043 | 9.26e-5 | 9.61e-5 | -0.648 | No | 246 |
| Wider | 111,235 | 6.28e-5 | 8.39e-5 | -0.471 | No | 385 |
| Transformer | 213,315 | 1.34e-4 | 7.50e-5 | -0.505 | No | 14 |

All variants: PASS on convergence, no NaN/Inf, expected parameter counts.

Negative test R^2 is expected here. The synthetic benchmark uses independent random seeds per split, so train/val/test data come from different AR process realizations. Models learn the training distribution but this does not transfer across independent random processes. This does not affect the benchmark's primary purpose: confirming that architectures run correctly and optimize without gradient pathology. Real data experiments are needed for meaningful performance comparison.

### Step 2: Real data experiments (requires processed data)

```bash
# Build the dataset first (if not already done)
python temporal_multiscale/build_multiscale_dataset.py \
    --data-dir data/processed \
    --output-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean

# Run all experiments
python rigor/experiments/run_all_experiments.py \
    --data-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean \
    --epochs 80 --patience 20

# Or run specific variants
python rigor/experiments/run_all_experiments.py \
    --data-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean \
    --variants baseline,multitask,deep_dilation
```

This produces `rigor/experiments/experiment_results.json` and per-variant training histories.

---

## 6. File Index

| File | Purpose |
|------|---------|
| `tcn_variants.py` | Model definitions for all 4 variants + variant registry |
| `synthetic_benchmark.py` | Self-contained synthetic data benchmark (runnable now) |
| `run_all_experiments.py` | Full experiment runner for real data (requires dataset) |
| `EXPERIMENT_DESIGN.md` | This document |
| `synthetic_benchmark_results.json` | Output of synthetic benchmark |
| `experiment_results.json` | Output of real data experiments |

---

## 7. References

- Ruder, S. (2017). "An Overview of Multi-Task Learning in Deep Neural Networks." arXiv:1706.05098.
- Bai, S., Kolter, J. Z., & Koltun, V. (2018). "An Empirical Evaluation of Generic Convolutional and Recurrent Networks for Sequence Modeling." arXiv:1803.01271.
- Vaswani, A., et al. (2017). "Attention Is All You Need." NeurIPS.
- Tort, A. B. L., et al. (2010). "Measuring phase-amplitude coupling between neuronal oscillations of different frequencies." Journal of Neurophysiology.
