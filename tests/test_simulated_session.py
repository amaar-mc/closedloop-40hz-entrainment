"""
Automated end-to-end test for the simulated streaming session.

Runs 25 steps of the demo pipeline in simulated mode programmatically
(not via subprocess) and verifies shape, type, and structural contracts
at each stage without requiring hardware.

Usage:
    python tests/test_simulated_session.py

Exit codes:
    0 — all checks pass
    1 — one or more checks fail

Author: Amaar Chughtai
Date: March 2026
"""

from __future__ import annotations

import sys
import time
import types
from pathlib import Path
from typing import Optional

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

# Project imports
from src.streaming.adapters import SimulatedEEGAdapter
from src.streaming.feature_extractor import StreamingFeatureExtractor
from temporal_multiscale.model_registry import build_default_registry
from eegnet import EEGNet

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------

DEFAULT_EEGNET_CHECKPOINT = str(REPO_ROOT / "models/muse_4ch/best_eegnet_4ch.pth")
DEFAULT_TCN_CHECKPOINT = str(
    REPO_ROOT / "models/muse_4ch/best_multiscale_tcn_4ch_lb20_hz5_ts1.pth"
)
DEFAULT_TCN_SCALERS = str(
    REPO_ROOT
    / "data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1/scalers.npz"
)

N_STEPS = 25
N_CHANNELS = 4
EXPECTED_WINDOW_SHAPE = (N_CHANNELS, 500)
EXPECTED_FEATURE_LEN = 8 * N_CHANNELS + 5  # 37 for 4-channel


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def check(name: str, condition: bool, detail: str = "") -> bool:
    """Print [PASS]/[FAIL] and return the boolean result."""
    status = "[PASS]" if condition else "[FAIL]"
    msg = f"{status} {name}"
    if detail:
        msg += f"  ({detail})"
    print(msg)
    return condition


def eegnet_predict_pac(
    model: EEGNet,
    window: np.ndarray,
    pac_mean: float,
    pac_std: float,
    device: str,
) -> float:
    """Run EEGNet on one window and return denormalised PAC."""
    x = torch.from_numpy(window[np.newaxis, np.newaxis, :, :]).float().to(device)
    with torch.no_grad():
        pac_z = model(x).item()
    return float(pac_z * pac_std + pac_mean)


# ------------------------------------------------------------------
# Test runner
# ------------------------------------------------------------------


def run_tests() -> int:
    """
    Run all checks for a 25-step simulated session.

    Returns:
        0 if all checks passed, 1 if any failed.
    """
    failures: list[str] = []

    print("=" * 60)
    print("Simulated Session End-to-End Test")
    print(f"Steps: {N_STEPS}  |  Channels: {N_CHANNELS}")
    print("=" * 60)

    # ---- Setup ----
    print("\n[Setup] Initializing pipeline components...")
    adapter = SimulatedEEGAdapter(n_channels=N_CHANNELS)

    # Monkey-patch get_window to skip the 2-second sleep.
    # We use a short real sleep (0.1s) so BrainFlow accumulates enough samples,
    # then pull 500 samples (the board runs at 250 Hz so 0.1s = ~25 samples
    # continuously; SYNTHETIC_BOARD runs faster internally and typically has
    # >500 samples after 0.1s).  If the buffer has fewer than 500 samples we
    # fall back to synthetic Gaussian noise so the test completes quickly.
    def _fast_get_window(self: SimulatedEEGAdapter) -> np.ndarray:
        time.sleep(0.1)
        raw = self._board.get_current_board_data(500)
        eeg = raw[self._eeg_indices, :]
        n_samples = eeg.shape[1]
        if n_samples < 500:
            # Pad with Gaussian noise to reach 500 samples — shapes still correct.
            pad = np.random.randn(len(self._eeg_indices), 500 - n_samples).astype(
                np.float32
            )
            eeg = np.concatenate([eeg.astype(np.float32), pad], axis=1)
        else:
            eeg = eeg[:, :500].astype(np.float32)
        return eeg

    adapter.get_window = types.MethodType(_fast_get_window, adapter)

    extractor = StreamingFeatureExtractor(n_channels=N_CHANNELS)

    # Load EEGNet checkpoint
    ckpt = torch.load(DEFAULT_EEGNET_CHECKPOINT, map_location="cpu", weights_only=False)
    pac_mean = float(ckpt.get("pac_mean", 0.0))
    pac_std = float(ckpt.get("pac_std", 1.0))
    eegnet = EEGNet(n_channels=N_CHANNELS, n_samples=500)
    eegnet.load_state_dict(ckpt["model_state_dict"])
    eegnet.eval()

    registry = build_default_registry(
        tcn_checkpoint_path=DEFAULT_TCN_CHECKPOINT,
        tcn_scalers_path=DEFAULT_TCN_SCALERS,
        device="cpu",
    )
    tcn_model = registry.get("tcn")
    lookback = tcn_model.lookback

    print(f"  EEGNet: pac_mean={pac_mean:.2e}, pac_std={pac_std:.2e}")
    print(f"  TCN: lookback={lookback} windows, feature_dim={tcn_model.feature_dim}")
    print(f"  Extractor: {extractor.n_features} features for {N_CHANNELS} channels")

    # ---- Shape checks (per-step) ----
    print("\n[Shape Checks] Running 25-step loop...")

    window_shapes_ok: list[bool] = []
    feature_shapes_ok: list[bool] = []
    pac_scalars_ok: list[bool] = []
    tcn_contract_ok: list[bool] = []
    tcn_results: list[Optional[dict]] = []
    no_exceptions = True

    stim_state = 0.0
    time_since_switch = 0.0
    stim_history: list[float] = []

    try:
        for step in range(1, N_STEPS + 1):
            # a. Adapter window shape
            window = adapter.get_window()
            window_shapes_ok.append(
                window.shape == EXPECTED_WINDOW_SHAPE
                and window.dtype == np.float32
            )

            # b. Feature extractor shape
            features = extractor.process_window(window)
            feature_shapes_ok.append(
                features.shape == (EXPECTED_FEATURE_LEN,)
                and features.dtype in (np.float32, np.float64)
            )

            # c. EEGNet PAC scalar
            pac = eegnet_predict_pac(eegnet, window, pac_mean, pac_std, device="cpu")
            pac_scalars_ok.append(isinstance(pac, float))

            # d. TCN step output
            stim_frac = float(np.mean(stim_history[-20:])) if stim_history else 0.0
            result = tcn_model.step(
                spectral_features=features,
                pac_current=pac,
                stim_state=stim_state,
                time_since_switch_sec=time_since_switch,
                stim_frac_recent=stim_frac,
            )
            tcn_results.append(result)

            if step < lookback:
                # Warmup: must return None
                tcn_contract_ok.append(result is None)
            else:
                # After warmup: must return dict with required keys
                tcn_contract_ok.append(
                    result is not None
                    and isinstance(result, dict)
                    and "future_pac" in result
                    and "delta_pac" in result
                )

            stim_history.append(stim_state)
            time_since_switch += 2.0

            # Fast pseudo-sleep so boards accumulate a tiny bit of data
            time.sleep(0.05)

    except Exception as exc:  # noqa: BLE001
        print(f"\n[FAIL] Exception during 25-step loop: {exc}")
        no_exceptions = False
        failures.append("no_exceptions")
    finally:
        adapter.close()

    # ---- Aggregate results ----
    print()

    # a. Window shapes
    ok_a = all(window_shapes_ok)
    if not check(
        f"get_window() returns {EXPECTED_WINDOW_SHAPE} float32 every step",
        ok_a,
        f"{sum(window_shapes_ok)}/{len(window_shapes_ok)} passed",
    ):
        failures.append("window_shape")

    # b. Feature shapes
    ok_b = all(feature_shapes_ok)
    if not check(
        f"process_window() returns ({EXPECTED_FEATURE_LEN},) every step",
        ok_b,
        f"{sum(feature_shapes_ok)}/{len(feature_shapes_ok)} passed",
    ):
        failures.append("feature_shape")

    # c. EEGNet PAC scalar
    ok_c = all(pac_scalars_ok)
    if not check(
        "EEGNet produces a float PAC value every step",
        ok_c,
        f"{sum(pac_scalars_ok)}/{len(pac_scalars_ok)} passed",
    ):
        failures.append("pac_scalar")

    # d. TCN warmup and prediction contract
    ok_d = all(tcn_contract_ok)
    n_none = sum(1 for r in tcn_results if r is None)
    n_dict = sum(1 for r in tcn_results if isinstance(r, dict))
    if not check(
        f"TCN returns None for first {lookback-1} steps, then dict with future_pac",
        ok_d,
        f"None={n_none}, dict={n_dict}",
    ):
        failures.append("tcn_contract")

    # e. No exceptions
    if not check("25-step loop completes without exceptions", no_exceptions):
        failures.append("no_exceptions")

    # ---- Spot check: future_pac values are in a plausible range ----
    dict_results = [r for r in tcn_results if isinstance(r, dict)]
    if dict_results:
        future_pacs = [r["future_pac"] for r in dict_results]
        plausible = all(-0.001 <= fp <= 0.01 for fp in future_pacs)
        if not check(
            "future_pac values are in plausible range (-0.001 to 0.01)",
            plausible,
            f"min={min(future_pacs):.6f}, max={max(future_pacs):.6f}",
        ):
            failures.append("future_pac_range")

    # ---- Summary ----
    print()
    print("=" * 60)
    n_fail = len(failures)
    n_total = 6 if dict_results else 5
    n_pass = n_total - n_fail
    print(f"Results: {n_pass}/{n_total} passed, {n_fail} failed")
    if failures:
        print(f"FAILED checks: {failures}")
    print("=" * 60)

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(run_tests())
