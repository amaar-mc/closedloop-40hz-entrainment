# Results and Key Findings

## 1. Horizon Sweep: Where the TCN Adds Value

Separate models were trained to predict PAC at horizons from 1 to 10 seconds. At each horizon, the TCN was compared against persistence (predict the last observed value) and Ridge regression.

| Horizon | Persistence R² | Ridge R²   | TCN R²     | TCN Advantage    |
| ------- | -------------- | ---------- | ---------- | ---------------- |
| 1s      | 0.760          | 0.812      | 0.735      | Baselines win    |
| 2s      | 0.488          | 0.542      | 0.470      | Baselines win    |
| 3s      | 0.234          | 0.254      | 0.277      | +0.04 (TCN wins) |
| **5s**  | **−0.267**     | **−0.393** | **+0.254** | **+0.52 margin** |
| 8s      | −0.276         | −0.211     | 0.240      | +0.52 margin     |
| 10s     | −0.256         | −0.212     | 0.278      | +0.53 margin     |

**Interpretation:** At 1–2 second horizons, PAC changes slowly enough that simply repeating the last value is a strong predictor. At 3+ seconds, baselines collapse to negative R² (worse than predicting the mean). The TCN maintains positive R² of 0.24–0.28 across 5–10 seconds. This +0.5 R² margin is the TCN's value proposition — it is the only model that provides useful predictions at the timescale where a controller needs them for proactive decision-making.

_Figure reference: results/figures/ — horizon sweep data available in models/sweep_multiscale_results.json_

## 2. Closed-Loop Controller Comparison (N = 35 Subjects, Real EEG)

All 35 subjects' recordings were replayed through six controller strategies. Metrics computed per-subject, then aggregated.

| Controller          | Alignment | Low-PAC Stim | High-PAC Rest | Stim % | PAC Gap   |
| ------------------- | --------- | ------------ | ------------- | ------ | --------- |
| Fixed Schedule      | 45.0%     | 61.4%        | 28.6%         | 66.6%  | −6.6      |
| Reactive Threshold  | 64.5%     | 51.7%        | 77.3%         | 36.7%  | +21.1     |
| PI Controller       | 66.1%     | 38.6%        | 93.6%         | 22.0%  | +27.2     |
| **TCN Predictive**  | **72.1%** | **82.6%**    | 61.6%         | 59.7%  | **+30.5** |
| Hybrid TCN+Reactive | 73.8%     | 85.3%        | 62.2%         | 60.8%  | +34.0     |
| Alignment Oracle    | 100.0%    | 100.0%       | 100.0%        | 48.3%  | +33.3     |

**Key observations:**

- **Fixed Schedule stimulates in the wrong direction** — its PAC gap is −6.6 (stimulating more during high-PAC than low-PAC periods), because its timing is uncorrelated with brain state.
- **TCN achieves 91% of oracle performance** on PAC targeting gap (+30.5 vs +33.3).
- **TCN targets 82.6% of low-PAC windows** for stimulation, compared to Reactive's 51.7% — a 60% improvement in therapeutic precision.
- **Reactive wins on high-PAC rest rate** (77.3% vs 61.6%) because it uses less total stimulation (36.7% vs 59.7%).

_Figure: results/figures/controller_comparison.png — grouped bar chart of all six controllers across four metrics_

## 3. Statistical Significance (TCN vs Reactive)

All comparisons use Wilcoxon signed-rank tests with Hedges' g effect sizes and 95% confidence intervals.

| Metric             | TCN   | Reactive | Hedges' g | 95% CI         | p-value |
| ------------------ | ----- | -------- | --------- | -------------- | ------- |
| Epoch Alignment    | 72.1% | 64.5%    | +1.31     | [+0.75, +1.87] | < 0.001 |
| Low-PAC Stim Rate  | 82.6% | 51.7%    | +4.47     | [+3.33, +5.62] | < 0.001 |
| High-PAC Rest Rate | 61.6% | 77.3%    | −2.41     | [−3.14, −1.68] | < 0.001 |
| PAC Targeting Gap  | +30.5 | +21.1    | +1.57     | [+0.98, +2.17] | < 0.001 |
| Mean Lead Time (s) | 0.79  | 0.20     | +0.76     | [+0.25, +1.26] | 0.0003  |
| Clinical Utility   | 0.681 | 0.591    | +0.95     | [+0.43, +1.47] | < 0.001 |

All primary metrics show large effect sizes (g > 0.8). The low-PAC targeting rate shows a very large effect (g = 4.47), reflecting the TCN's dramatically superior ability to concentrate stimulation during therapeutic windows.

**Per-subject consistency:** 35 out of 35 subjects show higher alignment with the TCN controller than with reactive control (binomial p < 0.001).

_Figure: results/figures/per_subject_utility.png — scatter plot showing all 35 points above the diagonal_

## 4. PAC Targeting Quality

The most clinically meaningful metric is the PAC targeting gap: the difference in mean PAC between rest and stimulation periods. A positive gap means stimulation is correctly directed at low-PAC states.

| Controller         | Mean PAC during Stim | Mean PAC during Rest | Gap              | % of Oracle     |
| ------------------ | -------------------- | -------------------- | ---------------- | --------------- |
| Fixed Schedule     | 4.4 × 10⁻⁵           | 3.8 × 10⁻⁵           | −6.6 × 10⁻⁶      | Wrong direction |
| Reactive           | 2.9 × 10⁻⁵           | 5.0 × 10⁻⁵           | +21.1 × 10⁻⁶     | 63%             |
| **TCN Predictive** | **2.9 × 10⁻⁵**       | **6.0 × 10⁻⁵**       | **+30.5 × 10⁻⁶** | **91%**         |
| Oracle             | 2.5 × 10⁻⁵           | 5.8 × 10⁻⁵           | +33.3 × 10⁻⁶     | 100%            |

_Figure: results/figures/pac_targeting_gap.png — bar chart with oracle reference line_

## 5. Threshold Robustness

The TCN controller's delta-z threshold parameter was swept from 0.1 to 1.0 to verify that results are not artifacts of threshold tuning.

| Delta-z | Alignment | Low-PAC Stim | PAC Gap |
| ------- | --------- | ------------ | ------- |
| 0.1     | 59.6%     | 51.2%        | 12.4    |
| 0.2     | 68.5%     | 72.9%        | 26.3    |
| 0.3     | 73.7%     | 84.9%        | 32.4    |
| 0.4     | 73.9%     | 85.3%        | 33.7    |
| 0.5     | 73.7%     | 85.3%        | 33.8    |
| 0.8     | 73.8%     | 85.3%        | 34.0    |
| 1.0     | 73.8%     | 85.3%        | 34.0    |

Performance plateaus at delta-z ≥ 0.3 and exceeds reactive baseline at all thresholds ≥ 0.2. The primary results (reported at delta-z = 0.5) are not sensitive to this parameter.

_Figure: results/figures/threshold_sensitivity.png — line plot showing plateau behavior_

## 6. Habituation Analysis (Real Data)

PAC trajectories were analyzed across stimulation blocks for all 35 subjects:

- **First block mean PAC:** 0.000996
- **Last block mean PAC:** 0.001040
- **Paired t-test:** t(34) = −0.616, p = 0.542 (not significant at population level)
- **Subjects showing PAC decline (habituation):** 17/35 (48.6%)
- **Subjects showing PAC increase (facilitation):** 18/35 (51.4%)

Individual variability is large: subject-level changes range from −66.8% (strong habituation) to +149.1% (strong facilitation). This heterogeneity validates the fundamental premise of adaptive control — a single fixed protocol cannot serve both groups.

## 7. Fatigue Sensitivity (Simulation)

Adaptive vs. fixed scheduling was tested across six fatigue severity levels (fatigue rate 0.0 to 0.04), 10 trials per condition:

| Fatigue Rate     | Fixed Efficiency | Adaptive Efficiency | Gain  | p-value      |
| ---------------- | ---------------- | ------------------- | ----- | ------------ |
| 0.000 (none)     | 5.38             | 5.40                | +0.4% | 0.492 (n.s.) |
| 0.004 (mild)     | 5.29             | 5.36                | +1.3% | 0.020        |
| 0.008 (moderate) | 5.22             | 5.33                | +2.1% | 0.010        |
| 0.015 (mod-high) | 5.10             | 5.23                | +2.6% | 0.010        |
| 0.025 (high)     | 4.97             | 5.18                | +4.3% | 0.002        |
| 0.040 (severe)   | 4.82             | 5.09                | +5.7% | 0.010        |

The adaptive advantage is non-significant without fatigue, but grows monotonically with fatigue severity — reaching +5.7% under severe habituation. Results hold across four different fatigue model assumptions (linear decay, exponential tau=30s, exponential tau=60s, power law): +6.9% to +19.0%, all p < 10⁻¹³.

## 8. Data Integrity Verification

| Check                          | Result                                            |
| ------------------------------ | ------------------------------------------------- |
| Subject leakage between splits | PASS — no overlap                                 |
| Temporal causality in features | PASS — all features use only past/current values  |
| Normalization leakage          | PASS — scalers fit on training data only          |
| Shuffle-label sanity           | R² = −0.332 (confirms model learns real patterns) |
| Persistence baseline           | Matches expected values at all horizons           |
| Random seed reproducibility    | All seeds fixed (seed = 42)                       |

## 9. Limitations

1. **Offline replay, not live closed-loop.** Validation uses post-hoc replay of recorded EEG. Real-time latency and system integration were not tested.
2. **Single dataset.** All results derive from one cohort of 35 Iranian dementia patients. Cross-population generalization is unknown.
3. **Short sessions.** Recording sessions were 6–10 minutes. Clinical protocols run 30–60 minutes, and long-term habituation dynamics may differ.
4. **Static PAC ceiling.** Eight architectures converged at R² ≈ 0.287 for static prediction, suggesting a fundamental limit of 7 frontal channels at 250 Hz.
5. **PAC as proxy.** PAC is a validated biomarker, but the clinical outcome (amyloid clearance, cognitive improvement) was not measured.
6. **Heuristic controller thresholds.** The z-score thresholds and hysteresis parameters were set by domain knowledge, not optimized via reinforcement learning.

## Publication Figures

All figures available in `results/figures/` as paired PNG (300 DPI) and PDF:

| Figure                | Description                                                                           |
| --------------------- | ------------------------------------------------------------------------------------- |
| controller_comparison | Grouped bar chart: 6 controllers × 4 metrics with error bars and statistical brackets |
| pac_targeting_gap     | PAC gap by controller with oracle reference line                                      |
| per_subject_utility   | Scatter: TCN vs Reactive utility for all 35 subjects (all above diagonal)             |
| stim_vs_alignment     | Stimulation % vs alignment % efficiency trade-off                                     |
| threshold_sensitivity | Line plot: performance across delta-z thresholds showing plateau                      |
| timeline_example      | Real EEG trajectory with TCN vs Reactive decision overlay                             |
