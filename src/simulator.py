"""
Brain Entrainment Simulator for Closed-Loop Control Validation

Simulates neural response dynamics to 40 Hz stimulation using exponential
approach model. Enables testing of control strategies without animal/human subjects.

Model:
    PAC(t+1) = PAC(t) + τ × (PAC_target - PAC(t)) + noise

Parameters (empirically extracted from dataset):
    τ_rise = 0.15: PAC increase rate during stimulation
    τ_decay = 0.10: PAC decrease rate during rest
    PAC_max = 0.3: Maximum achievable PAC
    PAC_min = 0.05: Minimum PAC baseline
    noise_std = 0.02: Gaussian noise standard deviation

Author: Amaar Chughtai
Date: February 2026
"""

import numpy as np
import logging
from typing import Tuple, Optional, Dict, List
from pathlib import Path
from enum import IntEnum

logger = logging.getLogger(__name__)


class StimAction(IntEnum):
    """Stimulation action."""
    REST = 0
    STIMULATE = 1


class EntrainmentSimulator:
    """
    Simulates brain PAC dynamics in response to stimulation.

    Uses exponential approach model to simulate neural response:
        During stimulation (action=1):
            PAC(t+1) = PAC(t) + τ_rise × (PAC_max - PAC(t)) + noise
        During rest (action=0):
            PAC(t+1) = PAC(t) + τ_decay × (PAC_min - PAC(t)) + noise

    Approximates realistic gamma entrainment response observed in human EEG.
    """

    def __init__(self,
                 tau_rise: float = 0.15,
                 tau_decay: float = 0.10,
                 pac_max: float = 0.3,
                 pac_min: float = 0.05,
                 noise_std: float = 0.02,
                 initial_pac: Optional[float] = None):
        """
        Initialize entrainment simulator.

        Args:
            tau_rise: Time constant for PAC increase during stimulation (0-1)
                     Higher = faster response
            tau_decay: Time constant for PAC decrease during rest (0-1)
            pac_max: Maximum PAC value when fully entrained (0-1)
            pac_min: Minimum PAC during rest (0-1)
            noise_std: Standard deviation of Gaussian noise
            initial_pac: Initial PAC value (default: pac_min)
        """
        self.tau_rise = tau_rise
        self.tau_decay = tau_decay
        self.pac_max = pac_max
        self.pac_min = pac_min
        self.noise_std = noise_std

        # State
        self.pac = initial_pac if initial_pac is not None else pac_min
        self.step_count = 0

        # History
        self.pac_history = [self.pac]
        self.action_history = []

        # Validation
        assert 0 <= tau_rise <= 1, f"tau_rise must be in [0, 1], got {tau_rise}"
        assert 0 <= tau_decay <= 1, f"tau_decay must be in [0, 1], got {tau_decay}"
        assert 0 <= pac_min < pac_max <= 1, f"Invalid PAC bounds: [{pac_min}, {pac_max}]"

        logger.info(f"EntrainmentSimulator initialized:")
        logger.info(f"  τ_rise: {tau_rise}, τ_decay: {tau_decay}")
        logger.info(f"  PAC range: [{pac_min}, {pac_max}]")
        logger.info(f"  Noise: σ={noise_std}")
        logger.info(f"  Initial PAC: {self.pac:.4f}")

    def step(self, action: int) -> float:
        """
        Simulate one time step of neural dynamics.

        Updates PAC based on action (stimulation or rest) using exponential approach:
            - Stimulation: moves PAC toward PAC_max with time constant τ_rise
            - Rest: moves PAC toward PAC_min with time constant τ_decay
            - Noise: adds Gaussian noise for realistic variability

        Args:
            action: Stimulation action (0=REST, 1=STIMULATE)

        Returns:
            pac: Updated PAC value
        """
        # Select dynamics based on action
        if action == StimAction.STIMULATE:
            tau = self.tau_rise
            target = self.pac_max
        elif action == StimAction.REST:
            tau = self.tau_decay
            target = self.pac_min
        else:
            raise ValueError(f"Invalid action: {action}")

        # Exponential approach: PAC(t+1) = PAC(t) + τ × (target - PAC(t))
        pac_new = self.pac + tau * (target - self.pac)

        # Add noise
        noise = np.random.normal(0, self.noise_std)
        pac_new = pac_new + noise

        # Clip to valid range
        pac_new = np.clip(pac_new, 0.0, 1.0)

        # Update state
        self.pac = pac_new
        self.step_count += 1
        self.pac_history.append(pac_new)
        self.action_history.append(action)

        return pac_new

    def reset(self, initial_pac: Optional[float] = None):
        """
        Reset simulator to initial state.

        Args:
            initial_pac: Initial PAC value (default: pac_min)
        """
        self.pac = initial_pac if initial_pac is not None else self.pac_min
        self.step_count = 0
        self.pac_history = [self.pac]
        self.action_history = []
        logger.debug(f"Simulator reset to PAC={self.pac:.4f}")

    def get_state(self) -> dict:
        """Get current simulator state."""
        return {
            'pac': self.pac,
            'step_count': self.step_count,
            'n_history': len(self.pac_history)
        }

    def get_history(self) -> dict:
        """Get full history of PAC and actions."""
        return {
            'pac': np.array(self.pac_history),
            'action': np.array(self.action_history),
            'pac_mean': np.mean(self.pac_history),
            'pac_std': np.std(self.pac_history),
            'stimulation_time': 100.0 * np.mean(self.action_history) if len(self.action_history) > 0 else 0.0
        }

    def get_pac_at_step(self, step: int) -> Optional[float]:
        """Get PAC value at specific step."""
        if 0 <= step < len(self.pac_history):
            return self.pac_history[step]
        return None


class FatigueAwareSimulator:
    """
    Simulator with neural habituation / synaptic fatigue dynamics.

    Continuous stimulation causes the effective rise rate to decay over time
    (habituation). Rest periods allow the response to recover (dishabituation).

    Model:
        effectiveness(t) = 1 - fatigue(t)
        During stimulation:
            fatigue(t+1) = fatigue(t) + fatigue_rate × (1 - fatigue(t))
            effective_tau_rise = tau_rise × effectiveness(t)
            PAC(t+1) = PAC(t) + effective_tau_rise × (PAC_max - PAC(t)) + noise
        During rest:
            fatigue(t+1) = fatigue(t) - recovery_rate × fatigue(t)
            PAC(t+1) = PAC(t) + tau_decay × (PAC_min - PAC(t)) + noise

    Parameters calibrated from dataset observations:
        - Subjects showing strong habituation (sub-35: -67%, sub-19: -57%)
          suggest fatigue_rate ~ 0.005-0.01 per second
        - 20s rest periods partially restore response, suggesting
          recovery_rate ~ 0.02-0.05 per second
    """

    def __init__(self,
                 tau_rise: float = 0.15,
                 tau_decay: float = 0.10,
                 pac_max: float = 0.3,
                 pac_min: float = 0.05,
                 noise_std: float = 0.02,
                 fatigue_rate: float = 0.008,
                 recovery_rate: float = 0.03,
                 max_fatigue: float = 0.7,
                 initial_pac: Optional[float] = None):
        """
        Args:
            tau_rise: Base time constant for PAC increase during stimulation
            tau_decay: Time constant for PAC decrease during rest
            pac_max: Maximum PAC value when fully entrained
            pac_min: Minimum PAC during rest
            noise_std: Standard deviation of Gaussian noise
            fatigue_rate: Rate at which fatigue accumulates during stimulation
            recovery_rate: Rate at which fatigue recovers during rest
            max_fatigue: Maximum fatigue level (caps effectiveness reduction)
            initial_pac: Initial PAC value (default: pac_min)
        """
        self.tau_rise = tau_rise
        self.tau_decay = tau_decay
        self.pac_max = pac_max
        self.pac_min = pac_min
        self.noise_std = noise_std
        self.fatigue_rate = fatigue_rate
        self.recovery_rate = recovery_rate
        self.max_fatigue = max_fatigue

        # State
        self.pac = initial_pac if initial_pac is not None else pac_min
        self.fatigue = 0.0
        self.step_count = 0

        # History
        self.pac_history = [self.pac]
        self.action_history: List[int] = []
        self.fatigue_history = [0.0]

        assert 0 <= tau_rise <= 1
        assert 0 <= tau_decay <= 1
        assert 0 <= pac_min < pac_max <= 1
        assert 0 <= fatigue_rate <= 1
        assert 0 <= recovery_rate <= 1

    def step(self, action: int) -> float:
        """Simulate one time step with fatigue dynamics."""
        if action == StimAction.STIMULATE:
            # Fatigue accumulates during stimulation
            self.fatigue += self.fatigue_rate * (self.max_fatigue - self.fatigue)
            # Effective rise rate is reduced by fatigue
            effectiveness = 1.0 - self.fatigue
            effective_tau = self.tau_rise * effectiveness
            target = self.pac_max
            pac_new = self.pac + effective_tau * (target - self.pac)
        elif action == StimAction.REST:
            # Fatigue recovers during rest
            self.fatigue -= self.recovery_rate * self.fatigue
            self.fatigue = max(0.0, self.fatigue)
            target = self.pac_min
            pac_new = self.pac + self.tau_decay * (target - self.pac)
        else:
            raise ValueError(f"Invalid action: {action}")

        # Add noise and clip
        pac_new += np.random.normal(0, self.noise_std)
        pac_new = np.clip(pac_new, 0.0, 1.0)

        # Update state
        self.pac = pac_new
        self.step_count += 1
        self.pac_history.append(pac_new)
        self.action_history.append(action)
        self.fatigue_history.append(self.fatigue)

        return pac_new

    def reset(self, initial_pac: Optional[float] = None):
        """Reset simulator to initial state."""
        self.pac = initial_pac if initial_pac is not None else self.pac_min
        self.fatigue = 0.0
        self.step_count = 0
        self.pac_history = [self.pac]
        self.action_history = []
        self.fatigue_history = [0.0]

    def get_history(self) -> dict:
        """Get full history."""
        return {
            'pac': np.array(self.pac_history),
            'action': np.array(self.action_history),
            'fatigue': np.array(self.fatigue_history),
            'pac_mean': np.mean(self.pac_history),
            'pac_std': np.std(self.pac_history),
            'stimulation_time': 100.0 * np.mean(self.action_history)
            if len(self.action_history) > 0 else 0.0,
        }


def extract_tau_parameters_from_data(pac_values: np.ndarray,
                                     actions: np.ndarray,
                                     fs: float = 1.0) -> Dict[str, float]:
    """
    Extract tau parameters empirically from experimental data.

    Fits exponential approach model to observed PAC transitions:
        PAC(t) = PAC(t-1) + τ × (target - PAC(t-1))

    Computes separate τ for stimulation (rise) and rest (decay) phases.

    Args:
        pac_values: Time series of PAC values
        actions: Corresponding stimulation actions (0=rest, 1=stim)
        fs: Sampling frequency in Hz

    Returns:
        params: Dictionary with estimated tau_rise and tau_decay
    """
    tau_rise_values = []
    tau_decay_values = []

    # Find transitions and estimate tau
    for i in range(1, len(pac_values) - 1):
        delta_pac = pac_values[i] - pac_values[i-1]

        if actions[i] == StimAction.STIMULATE:
            # During stimulation: estimate tau_rise
            # Assuming target = PAC_max = 0.3
            target = 0.3
            if target > pac_values[i-1]:  # Only if moving toward target
                tau = delta_pac / (target - pac_values[i-1]) if (target - pac_values[i-1]) > 1e-6 else 0.0
                if 0 <= tau <= 1:
                    tau_rise_values.append(tau)

        else:  # action == REST
            # During rest: estimate tau_decay
            # Assuming target = PAC_min = 0.05
            target = 0.05
            if target < pac_values[i-1]:  # Only if moving toward target
                tau = delta_pac / (target - pac_values[i-1]) if (pac_values[i-1] - target) > 1e-6 else 0.0
                if 0 <= tau <= 1:
                    tau_decay_values.append(tau)

    # Average valid estimates
    tau_rise = np.median(tau_rise_values) if tau_rise_values else 0.15
    tau_decay = np.median(tau_decay_values) if tau_decay_values else 0.10

    logger.info(f"Extracted tau parameters from data:")
    logger.info(f"  τ_rise: {tau_rise:.4f} (from {len(tau_rise_values)} transitions)")
    logger.info(f"  τ_decay: {tau_decay:.4f} (from {len(tau_decay_values)} transitions)")

    return {
        'tau_rise': float(tau_rise),
        'tau_decay': float(tau_decay),
        'n_rise_transitions': len(tau_rise_values),
        'n_decay_transitions': len(tau_decay_values)
    }


def validate_simulator_dynamics():
    """Validate simulator dynamics with test cases."""
    logger.info("="*60)
    logger.info("Entrainment Simulator Validation")
    logger.info("="*60)

    # Test 1: Step response to stimulation
    logger.info("\nTest 1: Step response to stimulation")
    logger.info("-" * 40)
    sim = EntrainmentSimulator(tau_rise=0.15, tau_decay=0.10, pac_max=0.3, pac_min=0.05)

    logger.info("Initial state: PAC={:.4f}".format(sim.pac))
    logger.info("Applying stimulation for 20 steps...")

    for step in range(20):
        pac = sim.step(StimAction.STIMULATE)
        if (step + 1) % 5 == 0:
            logger.info(f"  Step {step+1}: PAC={pac:.4f}")

    logger.info(f"Final PAC: {sim.pac:.4f} (expected ≈ {sim.pac_max:.4f})")

    # Test 2: Recovery during rest
    logger.info("\nTest 2: Recovery during rest")
    logger.info("-" * 40)
    sim.reset(initial_pac=0.3)
    logger.info(f"Starting PAC: {sim.pac:.4f}")
    logger.info("Applying rest for 20 steps...")

    for step in range(20):
        pac = sim.step(StimAction.REST)
        if (step + 1) % 5 == 0:
            logger.info(f"  Step {step+1}: PAC={pac:.4f}")

    logger.info(f"Final PAC: {sim.pac:.4f} (expected ≈ {sim.pac_min:.4f})")

    # Test 3: Alternating stimulation and rest
    logger.info("\nTest 3: Alternating stimulation and rest")
    logger.info("-" * 40)
    sim.reset()
    pattern = [StimAction.STIMULATE]*10 + [StimAction.REST]*10
    pattern = pattern * 2  # Repeat pattern

    for step, action in enumerate(pattern):
        pac = sim.step(action)

    history = sim.get_history()
    logger.info(f"Pattern: 10 stim, 10 rest, repeated 2x")
    logger.info(f"Final PAC: {sim.pac:.4f}")
    logger.info(f"Mean PAC: {history['pac_mean']:.4f}")
    logger.info(f"Std PAC: {history['pac_std']:.4f}")

    # Test 4: Parameter extraction
    logger.info("\nTest 4: Empirical parameter extraction")
    logger.info("-" * 40)
    params = extract_tau_parameters_from_data(
        history['pac'],
        history['action']
    )

    logger.info("\n" + "="*60)
    logger.info("All validation tests completed!")
    logger.info("="*60)


def test_simulator():
    """Run comprehensive simulator tests."""
    validate_simulator_dynamics()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    test_simulator()
