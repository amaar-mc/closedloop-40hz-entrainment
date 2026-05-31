"""
End-to-end streaming inference demo for closed-loop 40 Hz entrainment.

Runs the full inference pipeline in the terminal without hardware:
    SimulatedEEGAdapter -> StreamingFeatureExtractor -> EEGNet PAC
    -> TCN future PAC -> PersonalizationModule z-score -> stimulus decision

Usage:
    python scripts/demo_streaming.py --steps 30 --source simulated
    python scripts/demo_streaming.py --source muse --steps 5  # falls back to simulated

Author: Amaar Chughtai
Date: March 2026
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

# Project imports (after sys.path setup)
from src.streaming.adapters import SimulatedEEGAdapter
from src.streaming.feature_extractor import StreamingFeatureExtractor
from temporal_multiscale.model_registry import build_default_registry
from eegnet import EEGNet
from personalization import PersonalizationModule

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------

DEFAULT_EEGNET_CHECKPOINT = str(REPO_ROOT / "models/muse_4ch/best_eegnet_4ch.pth")
DEFAULT_TCN_CHECKPOINT = str(
    REPO_ROOT / "models/muse_4ch/best_multiscale_tcn_4ch_lb20_hz5_ts1.pth"
)
DEFAULT_TCN_SCALERS = str(
    REPO_ROOT
    / "data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1/scalers.npz"
)

# Stimulation state as float for model context (REST=0.0, STIMULATE=1.0).
STATE_REST: float = 0.0
STATE_STIMULATE: float = 1.0

# Z-score thresholds matching ClosedLoopController defaults.
Z_LOW: float = -0.5
Z_HIGH: float = 0.5


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def auto_device() -> str:
    """Return 'mps' if available, else 'cuda' if available, else 'cpu'."""
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def load_eegnet(
    checkpoint_path: str, n_channels: int, device: str
) -> tuple[EEGNet, float, float]:
    """
    Load 4-channel EEGNet from checkpoint.

    Returns:
        model: EEGNet in eval mode on device.
        pac_mean: Mean used for z-score denormalisation (0.0 if not in checkpoint).
        pac_std: Std used for z-score denormalisation (1.0 if not in checkpoint).
    """
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    pac_mean = float(checkpoint.get("pac_mean", 0.0))
    pac_std = float(checkpoint.get("pac_std", 1.0))

    model = EEGNet(n_channels=n_channels, n_samples=500)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    model.to(device)
    return model, pac_mean, pac_std


def eegnet_predict_pac(
    model: EEGNet,
    window: np.ndarray,
    pac_mean: float,
    pac_std: float,
    device: str,
) -> float:
    """
    Run EEGNet on a (n_channels, 500) window and return denormalised PAC.

    Args:
        model: Loaded EEGNet in eval mode.
        window: (n_channels, 500) float32 EEG window.
        pac_mean: Mean used to denormalise model output.
        pac_std: Std used to denormalise model output.
        device: PyTorch device string.

    Returns:
        pac: Denormalised PAC scalar (clipped to >= 0).
    """
    x = torch.from_numpy(window[np.newaxis, np.newaxis, :, :]).float().to(device)
    with torch.no_grad():
        pac_z = model(x).item()
    pac = pac_z * pac_std + pac_mean
    return float(max(pac, 0.0))


def make_decision(
    pac_current: float,
    z_score: Optional[float],
    stim_state: float,
    time_in_state: int,
    hold_steps: int,
) -> float:
    """
    Reactive z-score stimulus decision with hysteresis hold.

    Args:
        pac_current: Current PAC value (unused directly — kept for future use).
        z_score: Current z-score or None if baseline not ready.
        stim_state: Current state (0.0 = REST, 1.0 = STIMULATE).
        time_in_state: Steps spent in the current state.
        hold_steps: Minimum hold time before a transition is allowed.

    Returns:
        new_stim_state: Updated state (0.0 or 1.0).
    """
    if z_score is None:
        return stim_state

    if z_score < Z_LOW:
        desired = STATE_STIMULATE
    elif z_score > Z_HIGH:
        desired = STATE_REST
    else:
        return stim_state

    if desired != stim_state and time_in_state >= hold_steps:
        return desired
    return stim_state


def format_state(stim_state: float) -> str:
    return "STIMULATE" if stim_state == STATE_STIMULATE else "REST"


# ------------------------------------------------------------------
# Argument parsing
# ------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Closed-loop 40 Hz entrainment streaming demo",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=30,
        help="Number of 2-second inference steps to run",
    )
    parser.add_argument(
        "--source",
        choices=["simulated", "muse"],
        default="simulated",
        help="EEG source adapter",
    )
    parser.add_argument(
        "--model",
        default="tcn",
        help="TemporalModel name from ModelRegistry (default: tcn)",
    )
    parser.add_argument(
        "--n-channels",
        type=int,
        default=4,
        help="Number of EEG channels",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="PyTorch device (default: auto-detect: mps > cuda > cpu)",
    )
    parser.add_argument(
        "--no-sleep",
        action="store_true",
        help="Skip 2-second sleep between windows (for testing)",
    )
    return parser.parse_args()


# ------------------------------------------------------------------
# Main demo loop
# ------------------------------------------------------------------


def run_demo(args: argparse.Namespace) -> None:
    device = args.device if args.device is not None else auto_device()
    print(f"\n=== Closed-Loop 40 Hz Entrainment Demo ===")
    print(f"Device: {device}  |  Source: {args.source}  |  Model: {args.model}")
    print(f"Channels: {args.n_channels}  |  Steps: {args.steps}")
    print("=" * 50)

    # --- Handle --source muse (attempt BLE; fall back to simulated) ---
    if args.source == "muse":
        print(
            "\nWARNING: Muse 2 BLE integration was attempted but is not viable on this "
            "system.\nFalling back to simulated mode. See 11-03-SUMMARY.md for details.\n"
        )

    # --- Create EEG adapter ---
    print("Initializing SimulatedEEGAdapter...")
    adapter = SimulatedEEGAdapter(n_channels=args.n_channels)
    # Reduce adapter sleep to 0.1s if --no-sleep requested (monkey-patch).
    # We still need a brief pause so BrainFlow's SYNTHETIC_BOARD buffer accumulates
    # 500 samples; at its native rate >500 samples accumulate in ~0.1s.  If the
    # buffer has fewer than 500 samples we pad with Gaussian noise so shapes remain
    # correct and the test / demo loop completes quickly.
    if args.no_sleep:
        import types

        def _fast_get_window(self: SimulatedEEGAdapter) -> np.ndarray:
            import time as _time
            _time.sleep(0.1)
            raw = self._board.get_current_board_data(500)
            eeg = raw[self._eeg_indices, :]
            n_samp = eeg.shape[1]
            if n_samp < 500:
                pad = np.random.randn(len(self._eeg_indices), 500 - n_samp).astype(
                    np.float32
                )
                eeg = np.concatenate([eeg.astype(np.float32), pad], axis=1)
            else:
                eeg = eeg[:, :500].astype(np.float32)
            return eeg

        adapter.get_window = types.MethodType(_fast_get_window, adapter)

    # --- Feature extractor ---
    extractor = StreamingFeatureExtractor(n_channels=args.n_channels)
    print(f"StreamingFeatureExtractor ready: {extractor.n_features} features")

    # --- EEGNet (static PAC predictor) ---
    print("Loading EEGNet 4-channel checkpoint...")
    eegnet, pac_mean, pac_std = load_eegnet(
        DEFAULT_EEGNET_CHECKPOINT, args.n_channels, device
    )
    print(f"EEGNet loaded  (pac_mean={pac_mean:.6f}, pac_std={pac_std:.6f})")

    # --- TCN (future PAC forecaster) ---
    print(f"Loading TCN via ModelRegistry (model='{args.model}')...")
    registry = build_default_registry(
        tcn_checkpoint_path=DEFAULT_TCN_CHECKPOINT,
        tcn_scalers_path=DEFAULT_TCN_SCALERS,
        device=device,
    )
    tcn_model = registry.get(args.model)
    lookback = tcn_model.lookback
    print(f"TCN loaded  (lookback={lookback} windows)")

    # --- PersonalizationModule for z-score ---
    personalization = PersonalizationModule(window_size=30, min_samples=10)

    # --- State tracking ---
    stim_state = STATE_REST
    time_in_state = 0
    time_since_switch = 0.0
    # Simple 20-window stim-fraction tracker
    stim_history: list[float] = []
    STIM_HISTORY_WINDOW = 20
    hold_steps = 5  # 5-step hysteresis (5 × 2s = 10s)

    # Summary accumulators
    pac_values: list[float] = []
    all_decisions: list[str] = []
    warmup_count = 0

    print("\n" + "-" * 80)
    print(
        f"{'Step':>4}  {'PAC':>10}  {'Future PAC':>12}  {'Z-score':>10}  {'Decision':>10}"
    )
    print("-" * 80)

    try:
        for step in range(1, args.steps + 1):
            # 1. Get raw EEG window (sleeps 2s unless --no-sleep)
            window = adapter.get_window()  # (n_channels, 500)

            # 2. Spectral features
            features = extractor.process_window(window)  # (37,) for 4ch

            # 3. EEGNet static PAC
            pac_current = eegnet_predict_pac(eegnet, window, pac_mean, pac_std, device)

            # 4. TCN future PAC prediction
            stim_frac_recent = (
                float(np.mean(stim_history[-STIM_HISTORY_WINDOW:]))
                if stim_history
                else 0.0
            )
            prediction = tcn_model.step(
                spectral_features=features,
                pac_current=pac_current,
                stim_state=stim_state,
                time_since_switch_sec=time_since_switch,
                stim_frac_recent=stim_frac_recent,
            )

            # 5. z-score from rolling baseline (compute before update)
            z_score = personalization.compute_zscore(pac_current)
            personalization.update(pac_current)

            # 6. Stimulus decision
            new_state = make_decision(
                pac_current=pac_current,
                z_score=z_score,
                stim_state=stim_state,
                time_in_state=time_in_state,
                hold_steps=hold_steps,
            )

            # 7. Update state tracking
            if new_state == stim_state:
                time_in_state += 1
            else:
                stim_state = new_state
                time_in_state = 1
                time_since_switch = 0.0
            time_since_switch += 2.0  # 2-second windows

            stim_history.append(stim_state)

            # 8. Formatted output
            future_pac_str = (
                f"{prediction['future_pac']:.6f}"
                if prediction is not None
                else "warmup"
            )
            z_str = f"{z_score:+.3f}" if z_score is not None else "calibrating"
            decision_str = format_state(stim_state)

            print(
                f"{step:>4}  {pac_current:>10.6f}  {future_pac_str:>12}  "
                f"{z_str:>10}  {decision_str:>10}"
            )

            # Accumulators
            pac_values.append(pac_current)
            all_decisions.append(decision_str)
            if prediction is None:
                warmup_count += 1

    finally:
        adapter.close()

    # Summary
    n_stim = sum(1 for d in all_decisions if d == "STIMULATE")
    pct_stim = 100.0 * n_stim / len(all_decisions) if all_decisions else 0.0
    mean_pac = float(np.mean(pac_values)) if pac_values else 0.0

    print("-" * 80)
    print("\n=== Session Summary ===")
    print(f"Total steps   : {args.steps}")
    print(f"Warmup steps  : {warmup_count}  (TCN needs {lookback} windows)")
    print(f"Stimulation   : {n_stim}/{args.steps} steps  ({pct_stim:.1f}%)")
    print(f"Mean PAC      : {mean_pac:.6f}")
    print("======================\n")


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

if __name__ == "__main__":
    args = parse_args()
    run_demo(args)
