# Testing Patterns

**Analysis Date:** 2026-03-05

## Test Framework

**Runner:**
- No dedicated test framework (no pytest, unittest, or tox in `requirements.txt`)
- Uses manual test functions with `if __name__ == "__main__":` blocks
- Audit scripts serve as structured validation suites

**Assertion Library:**
- Python standard `assert` statements
- `scipy.stats` for statistical validation (t-tests, ANOVA)
- numpy comparisons for numerical checks (`np.all`, `np.isfinite`)

**Run Commands:**
```bash
# Module-level smoke tests (run individual files)
python src/eegnet.py                    # test_eegnet(): forward pass, shape, params
python src/controller.py                # test_controller(): 60-step synthetic simulation
python src/preprocessing.py             # test_preprocessing(): synthetic signal pipeline
python src/personalization.py           # test_personalization(): z-score computation
python src/simulator.py                 # validate_simulator_dynamics(): step response

# End-to-end smoke test (reduced epochs)
python src/training.py --data_dir data/processed --output_dir models --epochs 5 --batch_size 64

# Pre-training audit gate (REQUIRED before temporal training)
python temporal/validate_code.py

# Post-training dataset audits
python temporal_multiscale/audit_multiscale_pipeline.py --dataset-dir data/processed/multiscale_temporal_lb20_hz5_ts1
python temporal_multiscale/comprehensive_submission_audit.py --dataset-dir data/processed/multiscale_temporal_lb20_hz1_ts5
python temporal_multiscale/checkpoint_deployment_audit.py --checkpoint models/best_multiscale_tcn_lb20_hz1_ts5.pth

# Rigorous statistical validation (50+ trials)
python rigor/rigorous_validation.py --n-trials 50 --duration 600 --seed 42

# Full closed-loop demo (integration test)
python run_closed_loop_demo.py --duration 600 --n-trials 10
python run_tcn_validation.py
```

## Test File Organization

**Location:**
- Co-located with source (no separate `tests/` directory)
- Each core module in `src/` contains an internal `test_*()` function
- Dedicated audit scripts live in `temporal/` and `temporal_multiscale/`
- Rigorous validation in `rigor/`

**Naming:**
- Inline tests: `test_eegnet()`, `test_controller()`, `test_preprocessing()`, `test_personalization()`
- Audit functions: `run_audit()`, `audit_code()`
- Validation scripts: `validate_code.py`, `rigorous_validation.py`
- No `test_*.py` or `*_test.py` file naming convention

**Structure:**
```
src/
  eegnet.py                 # test_eegnet() at bottom
  controller.py             # test_controller() at bottom
  preprocessing.py          # test_preprocessing() at bottom
  personalization.py        # test_personalization() at bottom
  simulator.py              # validate_simulator_dynamics() at bottom
  utils.py                  # __main__ block with utility tests
  training.py               # main() serves as smoke test with --epochs flag

temporal/
  validate_code.py          # 6-test validation suite (REQUIRED pre-training gate)

temporal_multiscale/
  audit_multiscale_pipeline.py       # Dataset integrity audit
  comprehensive_submission_audit.py  # Ablation + baselines + shuffle sanity
  checkpoint_deployment_audit.py     # Robustness to PAC feature corruption

rigor/
  rigorous_validation.py    # 50+ trial statistical validation with bootstrap CI
```

## Test Categories

### 1. Module Smoke Tests (Unit-Level)

Each `src/` module has a `test_*()` function that verifies basic correctness when run directly.

**Pattern from `src/eegnet.py`:**
```python
def test_eegnet():
    """Test EEGNet with example input."""
    print("=" * 60)
    print("EEGNet Architecture Test")
    print("=" * 60)

    model = EEGNet(n_channels=7, n_samples=500, F1=8, D=2, F2=16, dropout=0.5)
    n_params = count_parameters(model)
    print(f"Total trainable parameters: {n_params:,}")

    batch_size = 16
    dummy_input = torch.randn(batch_size, 1, 7, 500)
    model.eval()
    with torch.no_grad():
        output = model(dummy_input)

    print(f"Output shape: {output.shape}")
    # Implicit assertion: would crash if shapes wrong

    block1_feat, block2_feat = model.get_feature_maps(dummy_input)
    print(f"Feature map shapes: Block1={block1_feat.shape}, Block2={block2_feat.shape}")
    return model

if __name__ == "__main__":
    model = test_eegnet()
```

**Pattern from `src/controller.py`:**
```python
def test_controller():
    """Test controller with synthetic EEG and simulated PAC."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = Path(tmpdir) / 'test_model.pth'
        model = EEGNet()
        torch.save({'model_state_dict': model.state_dict(), ...}, model_path)

        controller = ClosedLoopController(model_path=str(model_path), device='cpu')

        np.random.seed(42)
        for step in range(60):
            eeg_window = np.random.randn(7, 500) * 0.1
            eeg_window += 0.5 * np.sin(2*np.pi*6*np.arange(500)/250)
            action, pac_pred, z_score = controller.step(eeg_window)

        history = controller.get_history()
        # Print summary stats
```

**What these tests verify:**
- Forward pass does not crash
- Output shapes are correct
- Parameter counts match expectations
- State management works (reset, history tracking)
- No NaN/Inf in outputs

### 2. Pre-Training Validation Gate

**File:** `temporal/validate_code.py`

This is a **REQUIRED** gate before any temporal model training. Run it before training any LSTM or TCN.

**Tests included:**

| Test | Function | What it checks |
|------|----------|---------------|
| 1 | `test_temporal_sequence_logic()` | Sequences don't cross subject boundaries; contiguity within subjects |
| 2 | `test_no_subject_leakage()` | No subject appears in multiple splits (train/val/test disjoint) |
| 3 | `test_pac_autocorrelation()` | PAC temporal structure characterization (informational, not pass/fail) |
| 4 | `run_sklearn_temporal_baseline()` | Ridge regression baseline with PAC history + EEG stats |
| 5 | `run_multi_horizon_baseline()` | Ridge baseline at horizons 1-20s (establishes comparison floor) |
| 6 | `audit_code()` | Static analysis: checks file existence, key patterns in source code |

**Validation pattern:**
```python
def main():
    splits = load_data(data_dir)
    results = {}
    results['sequences'] = test_temporal_sequence_logic(splits)
    results['no_leakage'] = test_no_subject_leakage(splits)
    autocorrs = test_pac_autocorrelation(splits)
    results['baseline_r2'], _ = run_sklearn_temporal_baseline(splits)
    horizon_results = run_multi_horizon_baseline(splits)
    results['code_audit'] = audit_code()

    all_pass = all(v for k, v in results.items() if isinstance(v, bool))
    if not all_pass:
        print("Some validations failed")
```

**Key detail:** Test 6 (`audit_code()`) does **static analysis** of source files -- checks for required patterns like `squeeze(1)`, `assert np.all(np.diff`, `normalize_pac`, `HuberLoss`, `clip_grad_norm`, etc.

### 3. Dataset Integrity Audits

**File:** `temporal_multiscale/audit_multiscale_pipeline.py`

Validates the built multiscale temporal dataset.

**Checks:**
1. **Subject-level split integrity** -- no overlap between train/val/test subjects
2. **Temporal causality** -- `target_idx > end_idx` for all sequences (no future leakage)
3. **Shape and finite-value checks** -- consistent sample counts, no NaN/Inf in features/targets
4. **Normalization sanity** -- train features approximately N(0,1), val/test means allowed to drift
5. **Metadata consistency** -- lookback in metadata matches data dimensions

**Output format:**
```
[PASS] No subject overlap across train/val/test.
[PASS] train: temporal causality indices valid.
[PASS] train: sample counts consistent (8234).
[PASS] train.x_seq: finite check passed
[PASS] Train normalization sanity OK: mean_abs=0.0012, avg|std-1|=0.0034
[PASS] Lookback matches metadata (20).

AUDIT RESULT
PASS
```

**Exit behavior:** Returns `bool`; `main()` raises `SystemExit(1)` on failure.

### 4. Submission-Grade Audit

**File:** `temporal_multiscale/comprehensive_submission_audit.py`

Production-quality audit covering:

1. **Basic integrity** (subject overlap + temporal causality) -- same as audit_multiscale_pipeline
2. **Persistence baseline** -- predicts future PAC = last observed PAC (R^2 floor)
3. **Feature ablations** (Ridge regression on test set):
   - Full features
   - No PAC-derived features (spectral + context only)
   - PAC-only features
   - Spectral-only features
4. **Label-shuffle sanity** -- shuffle training labels, verify R^2 collapses to ~0

**Verdict logic:**
```python
integrity_ok = no_subject_overlap and temporal_causality_ok
shuffle_ok = shuffle_label_sanity_r2 < 0.05
passes_submission_gate = integrity_ok and shuffle_ok
```

**Output:** JSON report saved to `models/comprehensive_audit_multiscale_ts5.json`

### 5. Deployment Robustness Audit

**File:** `temporal_multiscale/checkpoint_deployment_audit.py`

Tests trained checkpoint under degraded inference conditions:

1. **Baseline** -- standard inference (as trained)
2. **PAC features zeroed** -- sets all PAC-derived features to 0 (simulates no PAC oracle)
3. **PAC features corrupted** -- adds Gaussian noise at sigma = [0.1, 0.25, 0.5, 1.0]

**Purpose:** Quantifies how much performance depends on PAC-history oracle quality. If R^2 drops sharply with PAC zeroed, the model is overly dependent on PAC features (deployment risk).

**Output:** JSON report with R^2/correlation for each scenario.

### 6. Rigorous Statistical Validation

**File:** `rigor/rigorous_validation.py`

Full statistical validation of closed-loop control strategies with proper trial counts.

**Fixes over `src/validation.py`:**
- 50+ trials per method (vs. 1-3)
- Both `EntrainmentSimulator` and `FatigueAwareSimulator`
- ANOVA on arrays of trial metrics (not single scalars)
- Hedges' g effect sizes for pairwise comparisons
- Wilcoxon signed-rank tests (nonparametric)
- Bootstrap 95% confidence intervals (1000 resamples)
- Reproducible per-trial seeds
- Population-diverse simulator (randomized parameters per subject)
- Fatigue severity sweep across multiple `fatigue_rate` values

**Output:** `rigor/rigorous_validation_results.json` with trial-level data and all statistics.

### 7. Real-Data TCN Validation

**File:** `run_tcn_validation.py`

Integration test that runs all controller variants on real EEG data (N=35 subjects).

**Controllers tested:**
1. Fixed Schedule (replays original protocol)
2. Reactive (z-score threshold)
3. TCN Predictive (pure TCN delta prediction)
4. Hybrid TCN+Reactive
5. PI Controller
6. Alignment Oracle

**Metrics:**
- Epoch alignment (stim during low-PAC, rest during high-PAC)
- Transition anticipation (lead time)
- Stimulation efficiency
- Clinical utility composite
- Wilcoxon signed-rank tests and Hedges' g for pairwise comparisons

## Test Data Patterns

**Synthetic Data (for module tests):**
```python
# Synthetic EEG window
eeg_window = np.random.randn(7, 500) * 0.1
eeg_window += 0.5 * np.sin(2*np.pi*6*np.arange(500)/250)  # Add theta

# Synthetic PAC time series
np.random.seed(42)
pac_values = 0.15 + np.random.randn(100) * 0.02

# Dummy model checkpoint
model = EEGNet()
torch.save({'model_state_dict': model.state_dict(), ...}, tmpdir / 'test_model.pth')
```

**Real Data (for audits and validation):**
```python
# Load preprocessed splits
train = np.load('data/processed/train_data.npz')  # keys: windows, pac, subjects
val = np.load('data/processed/val_data.npz')
test = np.load('data/processed/test_data.npz')

# Load temporal dataset
d = np.load('data/processed/multiscale_temporal/train_multiscale.npz', allow_pickle=True)
# keys: x_seq, y_future, y_delta, y_future_norm, y_delta_norm, subjects,
#        start_idx, end_idx, target_idx, last_pac, feature_names
```

**Temporary Files:**
```python
import tempfile
with tempfile.TemporaryDirectory() as tmpdir:
    model_path = Path(tmpdir) / 'test_model.pth'
    # ... create, use, auto-cleanup
```

## Mocking Approach

**Not used:** No `unittest.mock`, no pytest fixtures, no dependency injection.

**Instead:**
- Synthetic data generation for isolated tests
- Temporary directories for file I/O tests
- Try/except wrappers for optional dependencies
- Real data for integration audits

**What NOT to mock:**
- Core computation (PAC, filtering, model inference)
- Data loading/validation (use real or synthetic data)
- Model state (use actual checkpoints or dummy tensors)

## Coverage

**Requirements:** Not enforced (no coverage config, no CI gates, no CI pipeline).

**Implicit Coverage:**
- Module smoke tests cover: forward pass, shape correctness, state management
- Audit scripts cover: data integrity, normalization, causality, leakage
- Validation scripts cover: end-to-end closed-loop control performance
- No coverage reporting tool configured

## Test Output Conventions

**Console Output:**
```
================================================================
TEST 1: Temporal Sequence Logic
================================================================
  train: 8234 valid sequences across 24 subjects
  val:   1725 valid sequences across 5 subjects
  test:  1822 valid sequences across 6 subjects

  ALL 11781 sequences validated - no boundary violations
```

**Pass/Fail Format:**
- Audit scripts: `[PASS]` / `[FAIL]` prefix
- Validate scripts: checkmark/cross with description
- Final verdict: `"PASS"` or `"FAIL"` printed at end
- Exit code: `SystemExit(1)` on failure

**JSON Reports:**
- Audit scripts write structured JSON with all metrics
- Files: `models/comprehensive_audit_*.json`, `models/deployment_audit_*.json`, `rigor/rigorous_validation_results.json`

## When to Run What

| Scenario | Required Tests |
|----------|---------------|
| Changed `src/eegnet.py` | `python src/eegnet.py` + reduced-epoch training smoke test |
| Changed `src/controller.py` | `python src/controller.py` + `python run_closed_loop_demo.py` |
| Changed `src/preprocessing.py` | `python src/preprocessing.py` + rebuild data + retrain |
| Changed `temporal_multiscale/` | `python temporal/validate_code.py` + `python temporal_multiscale/audit_multiscale_pipeline.py` |
| Before temporal training | `python temporal/validate_code.py` (REQUIRED gate) |
| After temporal training | `audit_multiscale_pipeline.py` + `comprehensive_submission_audit.py` |
| Before submission/release | `comprehensive_submission_audit.py` + `checkpoint_deployment_audit.py` + `rigor/rigorous_validation.py` |
| Changed data pipeline | Rebuild dataset + all audits |

## Adding New Tests

**For a new `src/` module:**
1. Add a `test_{module_name}()` function at the bottom of the file
2. Wire it into `if __name__ == "__main__":` block
3. Test with synthetic data; verify shapes, ranges, no crashes
4. Print section headers with `"=" * 60` for visual separation

**For a new audit:**
1. Create standalone script in `temporal_multiscale/` or `rigor/`
2. Use `argparse` for CLI arguments with sensible defaults
3. Return `bool` from `run_audit()` function
4. Write JSON report for machine-readable results
5. Call `raise SystemExit(1)` in `main()` on failure
6. Use `[PASS]`/`[FAIL]` prefix format for console output

**For new validation scripts:**
1. Create top-level `run_*.py` script
2. Load data, run all controller variants, compute metrics
3. Report per-subject and aggregate statistics
4. Include baseline comparisons (persistence, Ridge, fixed schedule)

---

*Testing analysis: 2026-03-05*
