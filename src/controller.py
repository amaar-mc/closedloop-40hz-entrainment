"""
Closed-Loop Controller for Real-Time PAC-Based Neuromodulation

Implements threshold-based decision engine integrating:
- Real-time EEGNet model inference for PAC prediction
- Personalization module for z-score adaptation
- Decision logic with hysteresis to prevent oscillation
- State machine for stimulation control

Decision Logic:
    z < -0.5  → STIMULATE (weak coupling, boost gamma)
    z > +0.5  → REST (strong coupling, prevent habituation)
    -0.5 ≤ z ≤ +0.5 → MAINTAIN (normal coupling, stability)

Hysteresis: 5-second minimum hold time prevents rapid state switching.

Author: Amaar Chughtai
Date: February 2026
"""

import logging
from enum import IntEnum
from typing import Tuple, Optional
import numpy as np
import torch
from pathlib import Path

from eegnet import EEGNet
from personalization import PersonalizationModule

logger = logging.getLogger(__name__)


class StimState(IntEnum):
    """
    Stimulation state enumeration.

    Values:
        STIMULATE = 1: Active 40 Hz stimulation
        REST = 0: No stimulation (rest period)
    """
    STIMULATE = 1
    REST = 0

    def __str__(self):
        return "STIMULATE" if self.value == 1 else "REST"


class ClosedLoopController:
    """
    Real-time closed-loop controller for adaptive neuromodulation.

    Integrates trained EEGNet model with personalization module to make
    adaptive stimulation decisions based on current brain state.

    State Variables:
        current_state: Current stimulation state (STIMULATE or REST)
        time_in_state: How long (seconds) in current state
        hold_time: Minimum hold time before allowing state transitions
        z_low: Threshold for weak coupling (default -0.5)
        z_high: Threshold for strong coupling (default +0.5)

    Operation:
        1. Receive EEG window (2 seconds, 7 channels)
        2. Predict PAC using EEGNet model
        3. Update rolling baseline (personalization)
        4. Compute z-score: z = (PAC - μ_baseline) / σ_baseline
        5. Make decision based on z-score thresholds
        6. Apply hysteresis (5-second minimum hold)
        7. Return action + diagnostics
    """

    def __init__(self,
                 model_path: str,
                 device: str = 'cpu',
                 z_low: float = -0.5,
                 z_high: float = 0.5,
                 hold_time_sec: float = 5.0,
                 decision_rate_hz: float = 1.0):
        """
        Initialize closed-loop controller.

        Args:
            model_path: Path to trained EEGNet checkpoint (.pth)
            device: 'cuda' or 'cpu'
            z_low: Z-score threshold for weak coupling (default -0.5)
            z_high: Z-score threshold for strong coupling (default +0.5)
            hold_time_sec: Minimum hold time before state change (default 5.0)
            decision_rate_hz: Decision update rate in Hz (default 1.0 = 1 decision/sec)
        """
        self.device = device
        self.z_low = z_low
        self.z_high = z_high
        self.hold_time_sec = hold_time_sec
        self.decision_rate_hz = decision_rate_hz
        self.hold_samples = int(hold_time_sec * decision_rate_hz)

        # Load model
        logger.info(f"Loading EEGNet model from {model_path}")
        self.model = EEGNet(n_channels=7, n_samples=500).to(device)

        checkpoint = torch.load(model_path, map_location=device, weights_only=False)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()

        # Load PAC normalization stats so we can denormalize model output.
        # training.py z-scores targets: z = (pac - mean) / std, so we invert.
        self.pac_mean = checkpoint.get('pac_mean', 0.0)
        self.pac_std = checkpoint.get('pac_std', 1.0)
        logger.info(f"PAC denorm: mean={self.pac_mean:.6f}, std={self.pac_std:.6f}")
        logger.info("Model loaded and set to eval mode")

        # Personalization module
        self.personalization = PersonalizationModule(
            window_size=30,  # 30-second baseline window
            min_samples=10   # Need at least 10 samples before z-scores
        )

        # State tracking
        self.current_state = StimState.REST  # Start in rest state
        self.time_in_state = 0  # How long in current state
        self.state_history = []
        self.pac_history = []
        self.zscore_history = []
        self.action_history = []

        logger.info(f"ClosedLoopController initialized:")
        logger.info(f"  Model path: {model_path}")
        logger.info(f"  Device: {device}")
        logger.info(f"  Z-score thresholds: [{z_low}, {z_high}]")
        logger.info(f"  Hold time: {hold_time_sec}s ({self.hold_samples} decisions)")

    def step(self, eeg_window: np.ndarray) -> Tuple[StimState, float, Optional[float]]:
        """
        Execute one control step.

        Processes incoming EEG window and makes stimulation decision.

        Args:
            eeg_window: 2-second EEG window (7 channels, 500 samples)
                       Or (1, 7, 500) with feature channel

        Returns:
            action: Stimulation state (StimState.STIMULATE or .REST)
            pac_pred: Predicted PAC value
            z_score: Computed z-score (None if personalization not ready)
        """
        # Ensure correct shape for model
        if eeg_window.ndim == 2:
            # (n_channels, n_samples) -> (1, 1, n_channels, n_samples)
            eeg_tensor = torch.from_numpy(eeg_window[np.newaxis, np.newaxis, :, :]).float()
        elif eeg_window.ndim == 3 and eeg_window.shape[0] == 1:
            # (1, n_channels, n_samples) -> (1, 1, n_channels, n_samples)
            eeg_tensor = torch.from_numpy(eeg_window[np.newaxis, :, :, :]).float()
        else:
            raise ValueError(f"Invalid window shape: {eeg_window.shape}")

        eeg_tensor = eeg_tensor.to(self.device)

        # Predict PAC using model (output is z-normalized; denormalize)
        with torch.no_grad():
            pac_z = self.model(eeg_tensor).squeeze().item()

        pac_pred = pac_z * self.pac_std + self.pac_mean
        pac_pred = np.clip(pac_pred, 0.0, 1.0)

        # Compute z-score BEFORE updating baseline so the current value
        # doesn't contaminate its own z-score computation.
        z_score = self.personalization.compute_zscore(pac_pred)

        # Update personalization baseline for future z-scores
        self.personalization.update(pac_pred)

        # Make decision
        action = self._make_decision(z_score)

        # Update state tracking
        self.state_history.append(int(action))
        self.pac_history.append(pac_pred)
        self.zscore_history.append(z_score if z_score is not None else np.nan)
        self.action_history.append(action)

        # Update time in state
        if action == self.current_state:
            self.time_in_state += 1
        else:
            self.time_in_state = 1

        return action, pac_pred, z_score

    def _make_decision(self, z_score: Optional[float]) -> StimState:
        """
        Make stimulation decision based on z-score.

        Logic:
            - If z-score not ready (None), MAINTAIN current state
            - z < z_low: STIMULATE
            - z > z_high: REST
            - z_low ≤ z ≤ z_high: MAINTAIN
            - Apply hysteresis: only transition if hold time exceeded

        Args:
            z_score: Current z-score (None if not enough baseline data)

        Returns:
            action: Decision (STIMULATE or REST)
        """
        if z_score is None:
            # Not enough baseline data - maintain current state
            return self.current_state

        if z_score < self.z_low:
            # Weak coupling: STIMULATE
            desired_state = StimState.STIMULATE
        elif z_score > self.z_high:
            # Strong coupling: REST
            desired_state = StimState.REST
        else:
            # Normal coupling: MAINTAIN
            return self.current_state

        # Apply hysteresis — only transition if hold time has been met.
        # State tracking (time_in_state) is updated in step(), not here.
        if desired_state != self.current_state:
            if self.time_in_state >= self.hold_samples:
                self.current_state = desired_state
            # else: stay in current state until hold time expires

        return self.current_state

    def reset(self):
        """
        Reset controller for new session.

        Clears all state, baseline, and history.
        """
        self.personalization.reset()
        self.current_state = StimState.REST
        self.time_in_state = 0
        self.state_history = []
        self.pac_history = []
        self.zscore_history = []
        self.action_history = []
        logger.info("Controller reset for new session")

    def get_state(self) -> dict:
        """
        Get current controller state.

        Returns:
            state: Dictionary with current state information
        """
        return {
            'current_state': int(self.current_state),
            'current_state_name': str(self.current_state),
            'time_in_state': self.time_in_state,
            'baseline_ready': self.personalization.is_ready(),
            'n_decisions': len(self.action_history)
        }

    def get_history(self) -> dict:
        """
        Get full history of decisions and measurements.

        Returns:
            history: Dictionary with PAC, z-scores, and actions
        """
        return {
            'pac': np.array(self.pac_history),
            'zscore': np.array(self.zscore_history),
            'action': np.array(self.state_history),
            'n_stimulate': int(np.sum(self.state_history)),
            'n_rest': int(len(self.state_history) - np.sum(self.state_history)),
            'pct_stimulate': 100.0 * np.mean(self.state_history) if len(self.state_history) > 0 else 0.0
        }

    def get_baseline_stats(self) -> dict:
        """
        Get personalization baseline statistics.

        Returns:
            stats: Dictionary with mean, std, n_samples
        """
        mean, std = self.personalization.get_baseline_stats()
        return {
            'mean': mean,
            'std': std,
            'n_samples': self.personalization.get_buffer_size(),
            'ready': self.personalization.is_ready()
        }


class PredictiveLookAheadController:
    """
    Predictive closed-loop controller using a trained TCN to forecast
    future PAC at multiple horizons and make proactive stimulation decisions.

    Decision logic:
        - If predicted PAC trajectory is declining -> start stimulation early
        - If predicted PAC trajectory is rising -> delay stimulation
        - Falls back to reactive z-score logic when baseline is not yet ready

    Integrates with the realtime TCN inference wrapper for low-latency
    predictions.
    """

    def __init__(
        self,
        forecaster,
        z_low: float = -0.5,
        z_high: float = 0.5,
        hold_time_sec: float = 5.0,
        decision_rate_hz: float = 1.0,
        decline_threshold: float = -0.3,
    ):
        """
        Initialize predictive look-ahead controller.

        Args:
            forecaster: RealtimePACForecaster instance (from realtime_inference.py)
            z_low: Z-score threshold for weak coupling
            z_high: Z-score threshold for strong coupling
            hold_time_sec: Minimum hold time before state change
            decision_rate_hz: Decision update rate in Hz
            decline_threshold: If predicted delta_pac < this, preemptively stimulate
        """
        self.forecaster = forecaster
        self.z_low = z_low
        self.z_high = z_high
        self.hold_time_sec = hold_time_sec
        self.decision_rate_hz = decision_rate_hz
        self.hold_samples = int(hold_time_sec * decision_rate_hz)
        self.decline_threshold = decline_threshold

        # Personalization baseline
        self.personalization = PersonalizationModule(
            window_size=30,
            min_samples=10,
        )

        # State
        self.current_state = StimState.REST
        self.time_in_state = 0
        self.state_history = []
        self.pac_history = []
        self.zscore_history = []
        self.predicted_future_history = []
        self.predicted_delta_history = []

        logger.info("PredictiveLookAheadController initialized")
        logger.info(f"  Z thresholds: [{z_low}, {z_high}]")
        logger.info(f"  Hold time: {hold_time_sec}s")
        logger.info(f"  Decline threshold: {decline_threshold}")

    def step(
        self,
        spectral_features: np.ndarray,
        pac_current: float,
        stim_state: float,
        time_since_switch_sec: float,
        stim_frac_recent: float,
        cycle_phase_sin: float = 0.0,
        cycle_phase_cos: float = 1.0,
    ):
        """
        Execute one control step with look-ahead prediction.

        Args:
            spectral_features: (61,) from current EEG window
            pac_current: Current PAC estimate
            stim_state: Current stimulation state (0 or 1)
            time_since_switch_sec: Seconds since last state switch
            stim_frac_recent: Fraction of stim in recent window
            cycle_phase_sin: Protocol phase sin component
            cycle_phase_cos: Protocol phase cos component

        Returns:
            action: StimState decision
            pac_current: Current PAC value (passthrough)
            prediction: Dict with future_pac, delta_pac, or None if not ready
        """
        # Compute z-score BEFORE updating baseline so the current value
        # doesn't contaminate its own z-score computation.
        z_score = self.personalization.compute_zscore(pac_current)
        self.personalization.update(pac_current)

        # Get TCN prediction
        prediction = self.forecaster.step(
            spectral_features=spectral_features,
            pac_current=pac_current,
            stim_state=stim_state,
            time_since_switch_sec=time_since_switch_sec,
            stim_frac_recent=stim_frac_recent,
            cycle_phase_sin=cycle_phase_sin,
            cycle_phase_cos=cycle_phase_cos,
        )

        # Make decision
        action = self._make_decision(z_score, prediction)

        # Track history
        self.state_history.append(int(action))
        self.pac_history.append(pac_current)
        self.zscore_history.append(z_score if z_score is not None else np.nan)
        if prediction is not None:
            self.predicted_future_history.append(prediction["future_pac"])
            self.predicted_delta_history.append(prediction["delta_pac"])
        else:
            self.predicted_future_history.append(np.nan)
            self.predicted_delta_history.append(np.nan)

        # Update time in state
        if action == self.current_state:
            self.time_in_state += 1
        else:
            self.time_in_state = 1

        return action, pac_current, prediction

    def _make_decision(self, z_score, prediction):
        """
        Make proactive stimulation decision using predicted PAC trajectory.

        Priority:
          1. If prediction available → use look-ahead logic
          2. Else → fall back to reactive z-score logic
          3. Always respect hysteresis hold time
        """
        desired_state = None

        if prediction is not None:
            delta_pac = prediction["delta_pac"]
            future_pac = prediction["future_pac"]
            current_pac = prediction["current_pac"]

            # Proactive: predicted decline → stimulate early
            if delta_pac < self.decline_threshold:
                desired_state = StimState.STIMULATE

            # Proactive: predicted rise → can rest (save energy)
            elif delta_pac > abs(self.decline_threshold):
                desired_state = StimState.REST

            # Within dead zone → use z-score if available
            elif z_score is not None:
                if z_score < self.z_low:
                    desired_state = StimState.STIMULATE
                elif z_score > self.z_high:
                    desired_state = StimState.REST

        elif z_score is not None:
            # No prediction yet → reactive fallback
            if z_score < self.z_low:
                desired_state = StimState.STIMULATE
            elif z_score > self.z_high:
                desired_state = StimState.REST

        # No signal → maintain
        if desired_state is None:
            return self.current_state

        # Apply hysteresis — only transition if hold time has been met.
        # State tracking (time_in_state) is updated in step(), not here.
        if desired_state != self.current_state:
            if self.time_in_state >= self.hold_samples:
                self.current_state = desired_state

        return self.current_state

    def reset(self):
        """Reset controller and forecaster for a new session."""
        self.forecaster.reset()
        self.personalization.reset()
        self.current_state = StimState.REST
        self.time_in_state = 0
        self.state_history = []
        self.pac_history = []
        self.zscore_history = []
        self.predicted_future_history = []
        self.predicted_delta_history = []
        logger.info("PredictiveLookAheadController reset")

    def get_history(self) -> dict:
        """Get full history of decisions, measurements, and predictions."""
        return {
            "pac": np.array(self.pac_history),
            "zscore": np.array(self.zscore_history),
            "action": np.array(self.state_history),
            "predicted_future": np.array(self.predicted_future_history),
            "predicted_delta": np.array(self.predicted_delta_history),
            "n_stimulate": int(np.sum(self.state_history)) if self.state_history else 0,
            "n_rest": int(len(self.state_history) - np.sum(self.state_history))
            if self.state_history
            else 0,
            "pct_stimulate": 100.0 * np.mean(self.state_history)
            if self.state_history
            else 0.0,
        }


def test_controller():
    """Test controller with synthetic EEG and simulated PAC."""
    logger.info("="*60)
    logger.info("ClosedLoopController Test")
    logger.info("="*60)

    # Create dummy model checkpoint for testing
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = Path(tmpdir) / 'test_model.pth'

        # Create and save a model
        model = EEGNet()
        checkpoint = {
            'epoch': 0,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': {},
            'val_loss': 0.0
        }
        torch.save(checkpoint, model_path)

        # Create controller
        controller = ClosedLoopController(
            model_path=str(model_path),
            device='cpu',
            z_low=-0.5,
            z_high=0.5,
            hold_time_sec=5.0
        )

        logger.info("\nSimulating 60 decisions with synthetic PAC...")

        # Simulate 60 one-second decisions
        np.random.seed(42)
        baseline_pac = 0.15

        for step in range(60):
            # Generate synthetic EEG window
            eeg_window = np.random.randn(7, 500) * 0.1  # Gaussian noise
            eeg_window += 0.5 * np.sin(2*np.pi*6*np.arange(500)/250)  # Theta

            # Make decision
            action, pac_pred, z_score = controller.step(eeg_window)

            if (step + 1) % 10 == 0:
                logger.info(f"Step {step+1}:")
                logger.info(f"  PAC: {pac_pred:.4f}")
                logger.info(f"  Z-score: {z_score:.2f}" if z_score is not None else "  Z-score: N/A")
                logger.info(f"  Action: {action}")

        # Summary
        logger.info("\n" + "="*60)
        logger.info("Simulation Summary")
        logger.info("="*60)

        history = controller.get_history()
        logger.info(f"Total decisions: {len(controller.action_history)}")
        logger.info(f"Stimulation: {history['n_stimulate']} ({history['pct_stimulate']:.1f}%)")
        logger.info(f"Rest: {history['n_rest']} ({100-history['pct_stimulate']:.1f}%)")

        baseline = controller.get_baseline_stats()
        logger.info(f"\nBaseline stats:")
        logger.info(f"  Mean PAC: {baseline['mean']:.4f}" if baseline['mean'] is not None else "  Mean PAC: N/A")
        logger.info(f"  Std PAC: {baseline['std']:.4f}" if baseline['std'] is not None else "  Std PAC: N/A")
        logger.info(f"  Samples: {baseline['n_samples']}")
        logger.info(f"  Ready: {baseline['ready']}")

        logger.info("\n" + "="*60)
        logger.info("Controller test completed!")
        logger.info("="*60)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    test_controller()
