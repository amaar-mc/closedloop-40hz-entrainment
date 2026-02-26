# Testing Patterns

**Analysis Date:** 2026-02-26

## Test Framework

**Runner:**
- No dedicated test framework installed (pytest, unittest not in requirements.txt)
- Uses manual test functions with `if __name__ == "__main__":` blocks

**Assertion Library:**
- Python standard `assert` statements
- Also uses scipy.stats, numpy comparisons for scientific validation

**Run Commands:**
```bash
# Test individual modules
python src/eegnet.py                    # Runs test_eegnet()
python src/training.py --data_dir ... --epochs 5  # Smoke test with reduced epochs
python src/controller.py                # Runs test_controller()

# Pre-training audit (REQUIRED gate)
python temporal/validate_code.py        # Validates leakage, causality, subject splits

# Post-training audits
python temporal_multiscale/audit_multiscale_pipeline.py         # Dataset integrity
python temporal_multiscale/comprehensive_submission_audit.py     # Ablations + baselines
python temporal_multiscale/checkpoint_deployment_audit.py        # Robustness to noise

# No automated test runner (no pytest, no tox config)
```

## Test File Organization

**Location:**
- Co-located with source (NOT separated in `tests/` directory)
- Each module `foo.py` contains internal `test_foo()` function

**Naming:**
- Functions: `test_*()` pattern: `test_eegnet()`, `test_controller()`, `test_temporal_sequence_logic()`
- No `*_test.py` or `test_*.py` files at module level
- Audit/validation scripts: standalone scripts in `temporal/` and `temporal_multiscale/`

**Structure:**
```
src/
├── eegnet.py           # Contains test_eegnet()
├── training.py         # Contains main() entry point (smoke test)
├── controller.py       # Contains test_controller()
├── simulator.py        # Contains test_simulator()
└── utils.py            # Contains main() for utility tests

temporal/
├── validate_code.py    # test_temporal_sequence_logic(), test_leakage(), etc.
└── ...

temporal_multiscale/
├── audit_multiscale_pipeline.py      # run_audit()
├── comprehensive_submission_audit.py # main()
├── checkpoint_deployment_audit.py    # main()
└── ...
```

## Test Structure

**Suite Organization:**

Example from `src/eegnet.py`:
```python
def test_eegnet():
    """Test EEGNet with example input."""
    print("=" * 60)
    print("EEGNet Architecture Test")
    print("=" * 60)

    # Create model
    model = EEGNet(...)

    # Count parameters
    n_params = count_parameters(model)
    print(f"Total trainable parameters: {n_params:,}")

    # Test forward pass
    batch_size = 16
    dummy_input = torch.randn(batch_size, 1, 7, 500)
    model.eval()
    with torch.no_grad():
        output = model(dummy_input)

    # Validate output
    print(f"Output shape: {output.shape}")
    assert output.shape == (batch_size, 1), f"Wrong shape: {output.shape}"

    # Test feature extraction
    block1_feat, block2_feat = model.get_feature_maps(dummy_input)
    print(f"Feature map shapes: Block1={block1_feat.shape}, Block2={block2_feat.shape}")

    return model

if __name__ == "__main__":
    model = test_eegnet()
```

Example from `temporal/validate_code.py`:
```python
def test_temporal_sequence_logic(splits, lookback=10, horizon=5):
    """Test 1: Verify temporal sequence building logic."""
    print("=" * 60)
    print("TEST 1: Temporal Sequence Logic")
    print("=" * 60)

    errors = 0
    total_sequences = 0

    for split_name, data in splits.items():
        # ... validation logic
        if condition_failure:
            errors += 1
            print(f"  ERROR: {details}")
        else:
            print(f"  ✓ {split_name} passed")

    if errors > 0:
        raise RuntimeError(f"{errors} validation errors found")
    return True

def main():
    splits = load_data()
    test_temporal_sequence_logic(splits)
    test_leakage(splits)
    test_pac_autocorrelation(splits)
    print("\nAll validation tests passed!")

if __name__ == "__main__":
    main()
```

**Patterns:**
- Setup: Create fixtures (dummy data, models, configs)
- Execute: Run operation under test
- Verify: Assert expected outputs, shapes, ranges
- Cleanup: (implicit via garbage collection; no manual teardown)
- Report: Print section headers, results, error summaries

## Mocking

**Framework:**
- Not used (no unittest.mock, no pytest fixtures)
- Instead: **Synthetic data and temporary directories**

**Patterns:**

Synthetic data generation (from `src/controller.py::test_controller()`):
```python
np.random.seed(42)
baseline_pac = 0.15

for step in range(60):
    # Generate synthetic EEG window
    eeg_window = np.random.randn(7, 500) * 0.1  # Gaussian noise
    eeg_window += 0.5 * np.sin(2*np.pi*6*np.arange(500)/250)  # Theta

    # Make decision
    action, pac_pred, z_score = controller.step(eeg_window)

    # Validate
    assert action in [StimState.STIMULATE, StimState.REST]
```

Temporary file handling (from `src/controller.py::test_controller()`):
```python
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmpdir:
    model_path = Path(tmpdir) / 'test_model.pth'

    # Create and save dummy checkpoint
    model = EEGNet()
    checkpoint = {'model_state_dict': model.state_dict(), ...}
    torch.save(checkpoint, model_path)

    # Use in test
    controller = ClosedLoopController(model_path=str(model_path), device='cpu')
    # ... test operations
    # Cleanup automatic on exit
```

Data fixtures (from `temporal_multiscale/audit_multiscale_pipeline.py`):
```python
def _load_npz(path: Path) -> Dict[str, np.ndarray]:
    if not path.exists():
        raise FileNotFoundError(path)
    return dict(np.load(path, allow_pickle=True))

def run_audit(dataset_dir: Path) -> bool:
    train = _load_npz(dataset_dir / "train_multiscale.npz")
    val = _load_npz(dataset_dir / "val_multiscale.npz")
    test = _load_npz(dataset_dir / "test_multiscale.npz")
    # ... validation against real data
```

**What to Mock:**
- Optional dependencies (e.g., tensorpac):
  ```python
  try:
      from tensorpac import Pac
      TENSORPAC_AVAILABLE = True
  except ImportError:
      TENSORPAC_AVAILABLE = False
  ```

**What NOT to Mock:**
- Core computation (PAC, filtering, model inference)
- Data loading/validation (use real or synthetic data)
- Model state (use actual checkpoints or dummy tensors)

## Fixtures and Factories

**Test Data:**

Example data factory from `src/training.py`:
```python
# Create example training data
train_data = np.load(Path(args.data_dir) / 'train_data.npz')
train_dataset = EEGWindowDataset(
    windows=train_data['windows'],
    pac_labels=pac_train_norm
)
train_loader = DataLoader(
    train_dataset,
    batch_size=args.batch_size,
    shuffle=True,
    num_workers=args.num_workers,
    pin_memory=pin_memory
)
```

Example synthetic data factory from `src/simulator.py::test_simulator()`:
```python
def test_simulator():
    """Test simulator dynamics."""
    sim = EntrainmentSimulator(tau_rise=0.15, tau_decay=0.10)

    # Simulate 100 steps with alternating actions
    for step in range(100):
        action = 1 if step % 2 == 0 else 0  # Alternate stim/rest
        pac = sim.step(action)

        # Verify PAC stays within bounds
        assert 0 <= pac <= 1, f"PAC out of bounds: {pac}"

    return sim
```

**Location:**
- No separate fixture files
- Defined inline in test functions or at module level
- Shared fixtures in `utils.py` (e.g., `get_device()`, `ensure_dir()`)

## Coverage

**Requirements:**
- Not enforced (no coverage config, no CI gates)

**View Coverage:**
- No automated coverage reports
- Manual inspection: test functions verify critical paths (forward pass, training loop, decision logic)

## Test Types

**Unit Tests:**
- Scope: Single function/class in isolation
- Approach: Create minimal input, verify output shape/type/range
- Example: `test_eegnet()` verifies forward pass shape, parameter count, feature extraction

**Integration Tests:**
- Scope: Multi-component pipelines (data loading → training → validation)
- Approach: End-to-end smoke test with reduced epochs
- Example from CLAUDE.md:
  ```bash
  python src/training.py --data_dir data/processed --epochs 5 --batch_size 64
  ```
- Validates: Data I/O, model initialization, optimizer, checkpointing

**Data Validation Tests:**
- Scope: Dataset integrity, causality, leakage detection
- Approach: Load splits, check subject boundaries, temporal causality, normalization
- Example: `temporal/validate_code.py::test_temporal_sequence_logic()`
  - Verifies: No subject-level leakage, sequences stay within subjects, valid indices
  - Returns: bool, raises SystemExit(1) on failure

**Pipeline Audits (Pre-training Gate):**
- Run `temporal/validate_code.py` BEFORE temporal training (required gate per CLAUDE.md)
- Validates: Subject splits, temporal sequence logic, PAC autocorrelation, baseline comparison
- Entry point: `if not ok: raise SystemExit(1)`

**Audit/Validation Scripts:**
- Location: `temporal_multiscale/{audit, comprehensive_submission, checkpoint_deployment}_*.py`
- Checks: Dataset metadata consistency, shape validation, finite-value checks, normalization sanity
- Output: Human-readable pass/fail log with diagnostics

**E2E Tests:**
- Not formally structured
- Implemented as standalone demo scripts: `run_closed_loop_demo.py`, `run_fatigue_sensitivity.py`
- Validates: Full closed-loop control workflow, simulation, baseline comparison

## Common Patterns

**Async Testing:**
- Not used (single-threaded Python, no async/await)

**Error Testing:**

Assertion-based error cases (from `src/simulator.py::__init__()`):
```python
assert 0 <= tau_rise <= 1, f"tau_rise must be in [0, 1], got {tau_rise}"
assert 0 <= tau_decay <= 1, f"tau_decay must be in [0, 1], got {tau_decay}"
assert 0 <= pac_min < pac_max <= 1, f"Invalid PAC bounds: [{pac_min}, {pac_max}]"
```

Exception testing (from `temporal_multiscale/build_multiscale_dataset.py`):
```python
def _load_spectral_cache(base_dir: Path, split: str, n_rows: int) -> np.ndarray:
    cache_path = base_dir / f"{split}_spectral_cache.npy"
    if not cache_path.exists():
        raise FileNotFoundError(
            f"Missing spectral cache: {cache_path}. "
            "Generate it first with existing temporal pipeline."
        )
    spectral = np.load(cache_path).astype(np.float64)
    if spectral.shape[0] != n_rows:
        raise ValueError(
            f"Spectral rows ({spectral.shape[0]}) do not match split rows ({n_rows}) "
            f"for {split}."
        )
    return spectral
```

Range/shape validation (from `temporal_multiscale/audit_multiscale_pipeline.py`):
```python
def _finite_check(name: str, arr: np.ndarray) -> Tuple[bool, str]:
    if not np.all(np.isfinite(arr)):
        n_bad = int(np.size(arr) - np.sum(np.isfinite(arr)))
        return False, f"{name}: {n_bad} non-finite values found"
    return True, f"{name}: finite check passed"
```

**Logging-Based Validation:**

From `temporal_multiscale/audit_multiscale_pipeline.py::run_audit()`:
```python
print("=" * 80)
print("MULTISCALE PIPELINE AUDIT")
print("=" * 80)

ok_all = True

# Subject leakage check
tr_sub = set(train["subjects"].tolist())
va_sub = set(val["subjects"].tolist())
overlap_tv = tr_sub & va_sub
if overlap_tv:
    ok_all = False
    print(f"[FAIL] Subject leakage detected: {sorted(overlap_tv)}")
else:
    print("[PASS] No subject overlap across train/val/test.")

# Temporal causality
for split_name, split in [("train", train), ("val", val), ("test", test)]:
    if not np.all(split["target_idx"] > split["end_idx"]):
        ok_all = False
        print(f"[FAIL] {split_name}: found target_idx <= end_idx")
    else:
        print(f"[PASS] {split_name}: temporal causality indices valid.")

print("\n" + "=" * 80)
print("AUDIT RESULT")
print("=" * 80)
print("PASS" if ok_all else "FAIL")
return ok_all
```

**Smoke Testing (Integration):**

From CLAUDE.md:
```bash
# Full pipeline with reduced epochs for smoke test
python src/training.py \
  --data_dir data/processed \
  --output_dir models \
  --epochs 5 \           # Reduced from 100
  --batch_size 64
```

Validates: Data loading, model forward/backward, optimizer, checkpointing all work end-to-end without hanging.

---

*Testing analysis: 2026-02-26*
