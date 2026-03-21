"""
Tests for temporal_multiscale/model_registry.py.

Verifies:
1. ModelRegistry registers and retrieves a TCN model by name "tcn".
2. registry.available() lists registered model names.
3. registry.get("nonexistent") raises KeyError with available model list.
4. TCNTemporalModel wraps RealtimePACForecaster and exposes step() and reset().
5. TCNTemporalModel.step() returns None initially, dict after lookback warmup.
6. isinstance(tcn_model, TemporalModel) returns True (runtime_checkable Protocol).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Allow running from repo root as: python tests/test_model_registry.py
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from temporal_multiscale.model_registry import (
    ModelRegistry,
    TCNTemporalModel,
    TemporalModel,
    build_default_registry,
)

TCN_CHECKPOINT = str(ROOT / "models/muse_4ch/best_multiscale_tcn_4ch_lb20_hz5_ts1.pth")
TCN_SCALERS = str(
    ROOT / "data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1/scalers.npz"
)

# 4-channel model: 49 total features - 12 non-spectral = 37 spectral features.
SPECTRAL_DIM = 37
PASS_COUNT = 0
FAIL_COUNT = 0


def _assert(condition: bool, message: str) -> None:
    global PASS_COUNT, FAIL_COUNT
    if condition:
        print(f"  [PASS] {message}")
        PASS_COUNT += 1
    else:
        print(f"  [FAIL] {message}")
        FAIL_COUNT += 1


def test_registry_register_and_get() -> None:
    """Test 1: ModelRegistry registers and retrieves a TCN model by name."""
    print("\nTest 1: registry.get('tcn') returns the registered model")
    registry = ModelRegistry()
    tcn = TCNTemporalModel(checkpoint_path=TCN_CHECKPOINT, scalers_path=TCN_SCALERS)
    registry.register("tcn", tcn)
    retrieved = registry.get("tcn")
    _assert(retrieved is tcn, "retrieved model is the same object that was registered")


def test_registry_available() -> None:
    """Test 2: registry.available() lists registered model names."""
    print("\nTest 2: registry.available() returns sorted list of names")
    registry = ModelRegistry()
    tcn = TCNTemporalModel(checkpoint_path=TCN_CHECKPOINT, scalers_path=TCN_SCALERS)
    registry.register("tcn", tcn)
    registry.register("tcn_v2", tcn)  # Re-registering same object is valid
    names = registry.available()
    _assert(isinstance(names, list), "available() returns a list")
    _assert(names == sorted(names), "available() list is sorted")
    _assert("tcn" in names, "'tcn' appears in available() list")
    _assert("tcn_v2" in names, "'tcn_v2' appears in available() list")


def test_registry_get_nonexistent_raises_key_error() -> None:
    """Test 3: registry.get('nonexistent') raises KeyError with available model list."""
    print("\nTest 3: registry.get('nonexistent') raises KeyError")
    registry = ModelRegistry()
    tcn = TCNTemporalModel(checkpoint_path=TCN_CHECKPOINT, scalers_path=TCN_SCALERS)
    registry.register("tcn", tcn)
    raised = False
    try:
        registry.get("nonexistent_model")
    except KeyError as exc:
        raised = True
        err_str = str(exc)
        _assert(raised, "KeyError is raised for missing model name")
        _assert("tcn" in err_str, "KeyError message lists available models")
        return
    _assert(raised, "KeyError is raised for missing model name")


def test_tcn_temporal_model_wraps_forecaster() -> None:
    """Test 4: TCNTemporalModel wraps RealtimePACForecaster and exposes step/reset."""
    print("\nTest 4: TCNTemporalModel exposes step() and reset() via Protocol")
    tcn = TCNTemporalModel(checkpoint_path=TCN_CHECKPOINT, scalers_path=TCN_SCALERS)
    _assert(hasattr(tcn, "step"), "TCNTemporalModel has step() method")
    _assert(hasattr(tcn, "reset"), "TCNTemporalModel has reset() method")
    _assert(hasattr(tcn, "lookback"), "TCNTemporalModel exposes lookback property")
    _assert(hasattr(tcn, "feature_dim"), "TCNTemporalModel exposes feature_dim property")
    _assert(tcn.lookback == 20, f"lookback == 20 (got {tcn.lookback})")
    _assert(tcn.feature_dim == 49, f"feature_dim == 49 (got {tcn.feature_dim})")


def test_tcn_step_returns_none_then_dict() -> None:
    """Test 5: step() returns None until lookback windows accumulated, then dict."""
    print("\nTest 5: step() returns None for first (lookback-1) calls, dict after")
    tcn = TCNTemporalModel(checkpoint_path=TCN_CHECKPOINT, scalers_path=TCN_SCALERS)
    lookback = tcn.lookback
    rng = np.random.default_rng(42)

    none_count = 0
    for i in range(lookback - 1):
        feats = rng.standard_normal(SPECTRAL_DIM).astype(np.float32)
        result = tcn.step(
            spectral_features=feats,
            pac_current=0.00004,
            stim_state=0.0,
            time_since_switch_sec=5.0,
            stim_frac_recent=0.3,
        )
        if result is None:
            none_count += 1

    _assert(none_count == lookback - 1, f"step() returned None for first {lookback-1} calls")

    # The lookback-th call should return a dict.
    feats = rng.standard_normal(SPECTRAL_DIM).astype(np.float32)
    result = tcn.step(
        spectral_features=feats,
        pac_current=0.00004,
        stim_state=0.0,
        time_since_switch_sec=5.0,
        stim_frac_recent=0.3,
    )
    _assert(result is not None, f"step() returns dict after {lookback} accumulated windows")
    _assert(isinstance(result, dict), "return value is a dict")
    _assert("future_pac" in result, "'future_pac' key present in result")
    _assert("delta_pac" in result, "'delta_pac' key present in result")
    _assert("current_pac" in result, "'current_pac' key present in result")

    # reset() should clear buffer so next call returns None again.
    tcn.reset()
    feats = rng.standard_normal(SPECTRAL_DIM).astype(np.float32)
    after_reset = tcn.step(
        spectral_features=feats,
        pac_current=0.00004,
        stim_state=0.0,
        time_since_switch_sec=5.0,
        stim_frac_recent=0.3,
    )
    _assert(after_reset is None, "step() returns None after reset()")


def test_isinstance_temporal_model_protocol() -> None:
    """Test 6: isinstance(tcn_model, TemporalModel) returns True."""
    print("\nTest 6: isinstance check against runtime_checkable TemporalModel Protocol")
    tcn = TCNTemporalModel(checkpoint_path=TCN_CHECKPOINT, scalers_path=TCN_SCALERS)
    _assert(isinstance(tcn, TemporalModel), "TCNTemporalModel passes isinstance(TemporalModel)")


def test_registry_rejects_non_temporal_model() -> None:
    """Bonus: register() rejects objects that don't satisfy TemporalModel Protocol."""
    print("\nBonus: register() raises TypeError for non-TemporalModel objects")
    registry = ModelRegistry()
    raised = False
    try:
        registry.register("bad", object())  # type: ignore[arg-type]
    except TypeError:
        raised = True
    _assert(raised, "TypeError raised when registering non-TemporalModel object")


def test_build_default_registry() -> None:
    """build_default_registry() returns registry with 'tcn' pre-registered."""
    print("\nBonus: build_default_registry() creates registry with TCN pre-registered")
    registry = build_default_registry(
        tcn_checkpoint_path=TCN_CHECKPOINT,
        tcn_scalers_path=TCN_SCALERS,
    )
    _assert("tcn" in registry.available(), "'tcn' registered in default registry")
    model = registry.get("tcn")
    _assert(isinstance(model, TemporalModel), "registry model satisfies TemporalModel protocol")


if __name__ == "__main__":
    test_registry_register_and_get()
    test_registry_available()
    test_registry_get_nonexistent_raises_key_error()
    test_tcn_temporal_model_wraps_forecaster()
    test_tcn_step_returns_none_then_dict()
    test_isinstance_temporal_model_protocol()
    test_registry_rejects_non_temporal_model()
    test_build_default_registry()

    print(f"\n{'='*50}")
    print(f"Results: {PASS_COUNT} PASS, {FAIL_COUNT} FAIL")
    if FAIL_COUNT > 0:
        sys.exit(1)
    else:
        print("All tests passed.")
        sys.exit(0)
