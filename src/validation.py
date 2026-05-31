"""
Validation and Comparison Framework for Closed-Loop Control Strategies.

Compares four neuromodulation approaches using simulated brain dynamics:

1. Fixed Schedule (control): 40s ON + 20s OFF — standard clinical protocol.
2. Reactive Threshold: Current PAC-based z-score decisions — no prediction.
3. Predictive Look-Ahead: Uses a trained TCN (RealtimePACForecaster) to
   forecast future PAC 5-10s ahead and make proactive stimulation decisions.
   Falls back to a trend-based heuristic when no TCN model is provided.
4. Oracle: Perfect PAC knowledge — theoretical upper bound.

Metrics:
- PAC improvement (%): Change from baseline
- PAC variance ratio: Variability reduction
- Stimulation time (%): Energy efficiency
- Efficiency ratio: PAC gain per unit stimulation
- R² score: Model prediction accuracy
- Statistical significance: ANOVA, Tukey HSD, Cohen's d

Typical usage:
    validator = SimulationValidator(output_dir='results/figures')
    validator.add_method(FixedScheduleControl())
    validator.add_method(ReactiveThresholdControl())
    validator.add_method(PredictiveLookAheadControl())      # trend fallback
    validator.add_method(OracleControl())
    validator.run_all(duration_sec=360, n_trials=5)
    validator.plot_comparison()

Author: Amaar Chughtai
Date: February 2026
"""

import argparse
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass, asdict

import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from controller import ClosedLoopController, StimState
from simulator import EntrainmentSimulator, FatigueAwareSimulator, StimAction, extract_tau_parameters_from_data
from utils import compute_regression_metrics, ensure_dir

# Optional: TCN forecaster for PredictiveLookAheadControl
try:
    from temporal_multiscale.realtime_inference import RealtimePACForecaster
except ImportError:
    RealtimePACForecaster = None

logger = logging.getLogger(__name__)


@dataclass
class ValidationMetrics:
    """Container for validation metrics."""
    # PAC metrics
    pac_mean: float
    pac_std: float
    pac_improvement: float  # % increase from baseline
    pac_variance_ratio: float  # Post/Pre variance

    # Efficiency metrics
    stimulation_time: float  # % of time stimulating
    efficiency_ratio: float  # PAC improvement per unit stimulation time

    # Prediction metrics (for predictive method only)
    r2_score: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None

    # Summary
    method_name: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


class ControlMethodBase:
    """Abstract base class for all control strategies.

    Subclasses must implement :meth:`step` which receives the current PAC
    value and returns a binary stimulation decision (0 = REST, 1 = STIMULATE).
    The :meth:`reset` method is called before each trial to clear internal
    state.
    """

    def __init__(self, name: str):
        """Initialize control method.

        Args:
            name: Human-readable name for logging and plot labels.
        """
        self.name = name

    def reset(self):
        """Reset method state for a new trial."""
        pass

    def step(self, pac_current: float) -> int:
        """Make a stimulation decision.

        Args:
            pac_current: Current PAC value.

        Returns:
            action: 0 = REST, 1 = STIMULATE.
        """
        raise NotImplementedError


class FixedScheduleControl(ControlMethodBase):
    """Fixed 40s ON + 20s OFF schedule (control condition)."""

    def __init__(self, stim_duration: int = 40, rest_duration: int = 20, fs: float = 1.0):
        """
        Initialize fixed schedule.

        Args:
            stim_duration: Stimulation duration in seconds
            rest_duration: Rest duration in seconds
            fs: Sampling frequency in Hz
        """
        super().__init__("Fixed Schedule (40s ON / 20s OFF)")
        self.stim_samples = int(stim_duration * fs)
        self.rest_samples = int(rest_duration * fs)
        self.cycle_samples = self.stim_samples + self.rest_samples
        self.step_count = 0

    def reset(self):
        """Reset to start of cycle."""
        self.step_count = 0

    def step(self, pac_current: float) -> int:
        """
        Determine action based on fixed schedule.

        Args:
            pac_current: Current PAC (unused for fixed schedule)

        Returns:
            action: 0=REST, 1=STIMULATE
        """
        position_in_cycle = self.step_count % self.cycle_samples
        self.step_count += 1

        action = 1 if position_in_cycle < self.stim_samples else 0
        return action


class ReactiveThresholdControl(ControlMethodBase):
    """Reactive control based on current PAC vs. baseline with hysteresis."""

    def __init__(self, window_size: int = 30, threshold_std: float = 0.5,
                 hold_time: int = 5):
        """
        Initialize reactive control.

        Args:
            window_size: Baseline window size in samples
            threshold_std: Threshold in standard deviations
            hold_time: Minimum steps in current state before switching
        """
        super().__init__("Reactive Threshold (No Prediction)")
        self.window_size = window_size
        self.threshold_std = threshold_std
        self.hold_time = hold_time
        self.pac_buffer: list = []
        self.current_state = StimAction.REST
        self.time_in_state = 0

    def reset(self):
        """Reset baseline buffer and state."""
        self.pac_buffer = []
        self.current_state = StimAction.REST
        self.time_in_state = 0

    def step(self, pac_current: float) -> int:
        """
        Make reactive decision based on current PAC.

        Maintains current state in the dead zone (matching ClosedLoopController
        behavior in controller.py) and applies hysteresis.

        Args:
            pac_current: Current PAC value

        Returns:
            action: 0=REST, 1=STIMULATE
        """
        # Update baseline
        self.pac_buffer.append(pac_current)
        if len(self.pac_buffer) > self.window_size:
            self.pac_buffer.pop(0)

        # Need minimum samples for baseline
        if len(self.pac_buffer) < max(5, self.window_size // 2):
            self.time_in_state += 1
            return self.current_state

        # Compute z-score
        baseline_mean = np.mean(self.pac_buffer)
        baseline_std = np.std(self.pac_buffer)
        z_score = (pac_current - baseline_mean) / (baseline_std + 1e-8)

        # Make decision — maintain current state in the dead zone
        if z_score < -self.threshold_std:
            desired_state = StimAction.STIMULATE
        elif z_score > self.threshold_std:
            desired_state = StimAction.REST
        else:
            # Dead zone: maintain current state (not default to REST)
            self.time_in_state += 1
            return self.current_state

        # Apply hysteresis
        if desired_state != self.current_state and self.time_in_state >= self.hold_time:
            self.current_state = desired_state
            self.time_in_state = 0
        else:
            self.time_in_state += 1

        return self.current_state


class PredictiveLookAheadControl(ControlMethodBase):
    """Predictive look-ahead control for proactive stimulation scheduling.

    When a trained RealtimePACForecaster is provided, this controller uses
    the TCN to predict future PAC 5-10 seconds ahead and makes proactive
    stimulation decisions based on predicted trajectory (delta_pac).

    When no forecaster is available (the default in simulation), it falls
    back to a trend-based heuristic that estimates PAC trajectory from the
    recent slope of observed PAC values.

    Decision logic (both modes):
        - Predicted/estimated decline -> stimulate early (proactive)
        - Predicted/estimated rise -> rest (save energy)
        - Neither -> fall back to reactive z-score thresholding
        - Hysteresis: minimum hold_time before state transitions

    Args:
        forecaster: Optional RealtimePACForecaster instance. When provided,
            the step() method accepts spectral_features as a keyword argument
            and uses the TCN for look-ahead predictions.
        window_size: Baseline window for z-score computation (samples).
        threshold_std: Z-score threshold for reactive fallback decisions.
        decline_threshold: Threshold for predicted PAC decline (negative
            value). Used as a fraction of baseline_std in trend mode, or
            directly as a delta_pac threshold in TCN mode.
        hold_time: Minimum samples in current state before switching.
    """

    def __init__(
        self,
        forecaster=None,
        window_size: int = 30,
        threshold_std: float = 0.5,
        decline_threshold: float = -0.3,
        hold_time: int = 5,
    ):
        super().__init__("Predictive Look-Ahead")
        self.forecaster = forecaster
        self.window_size = window_size
        self.threshold_std = threshold_std
        self.decline_threshold = decline_threshold
        self.hold_time = hold_time
        self.pac_buffer: list = []
        self.action_buffer: list = []
        self.current_state = StimAction.REST
        self.time_in_state = 0

    @property
    def has_forecaster(self) -> bool:
        """Whether a trained TCN forecaster is available."""
        return self.forecaster is not None

    def reset(self):
        """Reset state for a new trial."""
        self.pac_buffer = []
        self.action_buffer = []
        self.current_state = StimAction.REST
        self.time_in_state = 0
        if self.forecaster is not None:
            self.forecaster.reset()

    def _pac_trend(self, k: int = 5) -> float:
        """Compute recent PAC slope over last *k* steps (trend fallback).

        Uses ordinary least-squares linear regression on the most recent
        *k* PAC values to estimate the instantaneous rate of change.

        Returns:
            slope: PAC units per step. Positive means rising, negative
                means declining.
        """
        if len(self.pac_buffer) < k:
            return 0.0
        recent = self.pac_buffer[-k:]
        x = np.arange(k, dtype=np.float64)
        y = np.array(recent, dtype=np.float64)
        x_mean = x.mean()
        y_mean = y.mean()
        denom = np.sum((x - x_mean) ** 2)
        if denom < 1e-12:
            return 0.0
        return float(np.sum((x - x_mean) * (y - y_mean)) / denom)

    def step(self, pac_current: float, spectral_features: Optional[np.ndarray] = None) -> int:
        """Make a stimulation decision using look-ahead prediction.

        When a TCN forecaster is available *and* spectral_features are
        provided, the controller delegates prediction to the trained model.
        Otherwise it falls back to the trend-based heuristic.

        Args:
            pac_current: Current PAC value.
            spectral_features: Optional (61,) spectral feature vector from
                the current EEG window.  Required for TCN-based prediction;
                ignored when using the trend fallback.

        Returns:
            action: 0 = REST, 1 = STIMULATE.
        """
        self.pac_buffer.append(pac_current)
        if len(self.pac_buffer) > self.window_size:
            self.pac_buffer.pop(0)

        # Not enough history -- use reactive fallback
        if len(self.pac_buffer) < max(5, self.window_size // 2):
            self.action_buffer.append(int(StimAction.REST))
            return StimAction.REST

        baseline_mean = np.mean(self.pac_buffer)
        baseline_std = np.std(self.pac_buffer) + 1e-8
        z_score = (pac_current - baseline_mean) / baseline_std

        # -----------------------------------------------------------------
        # Determine desired state via look-ahead logic
        # -----------------------------------------------------------------
        desired_state = None

        # Try TCN-based prediction first
        if self.forecaster is not None and spectral_features is not None:
            # Derive stimulation-context features from action history
            stim_state = float(self.current_state)
            time_since_switch = float(self.time_in_state)
            n_recent = min(len(self.action_buffer), 30)
            stim_frac = (
                float(np.mean(self.action_buffer[-n_recent:]))
                if n_recent > 0
                else 0.0
            )

            prediction = self.forecaster.step(
                spectral_features=spectral_features,
                pac_current=pac_current,
                stim_state=stim_state,
                time_since_switch_sec=time_since_switch,
                stim_frac_recent=stim_frac,
            )

            if prediction is not None:
                delta_pac = prediction["delta_pac"]

                # Proactive: predicted decline -> stimulate early
                if delta_pac < self.decline_threshold:
                    desired_state = StimAction.STIMULATE
                # Proactive: predicted rise -> can rest
                elif delta_pac > abs(self.decline_threshold):
                    desired_state = StimAction.REST

        # Fall back to trend-based heuristic when TCN unavailable or
        # when TCN prediction is not yet ready (lookback not filled).
        # Use a fixed threshold (decline_threshold is in PAC-per-step units)
        # to avoid the sigma-scaling instability where sensitivity increases
        # as PAC stabilizes.
        if desired_state is None and self.forecaster is None:
            trend = self._pac_trend()
            trend_thresh = abs(self.decline_threshold) * 0.01  # fixed scale
            if trend < -trend_thresh:
                desired_state = StimAction.STIMULATE
            elif trend > trend_thresh:
                desired_state = StimAction.REST

        # Reactive z-score fallback when neither look-ahead method fired
        if desired_state is None:
            if z_score < -self.threshold_std:
                desired_state = StimAction.STIMULATE
            elif z_score > self.threshold_std:
                desired_state = StimAction.REST

        if desired_state is None:
            desired_state = self.current_state

        # -----------------------------------------------------------------
        # Apply hysteresis
        # -----------------------------------------------------------------
        if desired_state != self.current_state:
            if self.time_in_state >= self.hold_time:
                self.current_state = desired_state
                self.time_in_state = 0
            # Hold time not met — stay, but don't increment time_in_state
            # (we only count consecutive time in the *current* state)
        else:
            self.time_in_state += 1

        self.action_buffer.append(int(self.current_state))
        return self.current_state


class OracleControl(ControlMethodBase):
    """Oracle: perfect knowledge of optimal PAC (theoretical upper bound)."""

    def __init__(self, pac_target: float = 0.2):
        """
        Initialize oracle control.

        Args:
            pac_target: Target PAC value
        """
        super().__init__("Oracle (Perfect Information)")
        self.pac_target = pac_target

    def step(self, pac_current: float) -> int:
        """
        Make optimal decision based on perfect information.

        Args:
            pac_current: Current PAC value

        Returns:
            action: 0=REST, 1=STIMULATE
        """
        # Always stim if below target, rest if above
        return StimAction.STIMULATE if pac_current < self.pac_target else StimAction.REST


class SimulationValidator:
    """
    Validates and compares control strategies using simulation.

    Workflow:
        1. Initialize simulator with brain dynamics
        2. Run each control method through same simulation
        3. Collect metrics (PAC, efficiency, stability)
        4. Statistical comparison (ANOVA, effect sizes)
        5. Generate comparison plots
    """

    def __init__(self, output_dir: str = 'results/figures'):
        """
        Initialize validator.

        Args:
            output_dir: Directory for saving results
        """
        self.output_dir = Path(output_dir)
        ensure_dir(self.output_dir)

        self.methods = []
        self.results = {}

        logger.info(f"SimulationValidator initialized")
        logger.info(f"  Output: {self.output_dir}")

    def add_method(self, method: ControlMethodBase):
        """Add control method to comparison."""
        self.methods.append(method)
        logger.info(f"Added method: {method.name}")

    def run_simulation(self,
                      method: ControlMethodBase,
                      duration_sec: int = 360,
                      fs: float = 1.0,
                      tau_rise: float = 0.15,
                      tau_decay: float = 0.10,
                      seed: Optional[int] = None,
                      use_fatigue: bool = False,
                      fatigue_rate: float = 0.008,
                      recovery_rate: float = 0.03,
                      max_fatigue: float = 0.7,
                      spectral_features: Optional[np.ndarray] = None) -> ValidationMetrics:
        """
        Run simulation for a single control method.

        Seeds the RNG before each run so that every method faces the same
        noise realization for a given seed, enabling fair comparisons.

        Args:
            method: Control method to test.
            duration_sec: Simulation duration in seconds.
            fs: Sampling frequency (decisions per second).
            tau_rise: PAC rise time constant.
            tau_decay: PAC decay time constant.
            seed: Random seed for reproducibility. When set, each method
                faces the same noise realization for a given trial.
            use_fatigue: If True, use FatigueAwareSimulator instead of
                the basic EntrainmentSimulator.
            fatigue_rate: Fatigue accumulation rate (only with use_fatigue).
            recovery_rate: Fatigue recovery rate (only with use_fatigue).
            max_fatigue: Maximum fatigue level (only with use_fatigue).
            spectral_features: Optional array of shape ``(n_steps, 61)``
                with per-step spectral features for TCN-based controllers.

        Returns:
            metrics: Validation metrics for this run.
        """
        logger.info(f"\nRunning simulation: {method.name}")
        logger.info(f"  Duration: {duration_sec}s")

        # Seed RNG so every method gets the same noise for a given trial
        if seed is not None:
            np.random.seed(seed)

        # Initialize simulator — use fatigue-aware variant when requested
        if use_fatigue:
            sim = FatigueAwareSimulator(
                tau_rise=tau_rise,
                tau_decay=tau_decay,
                pac_max=0.3,
                pac_min=0.05,
                noise_std=0.02,
                fatigue_rate=fatigue_rate,
                recovery_rate=recovery_rate,
                max_fatigue=max_fatigue,
            )
        else:
            sim = EntrainmentSimulator(
                tau_rise=tau_rise,
                tau_decay=tau_decay,
                pac_max=0.3,
                pac_min=0.05,
                noise_std=0.02
            )

        # Initialize method
        method.reset()

        # Run simulation
        n_steps = int(duration_sec * fs)
        pac_values = []
        actions = []

        # Determine whether to pass spectral features
        _pass_spectral = (
            isinstance(method, PredictiveLookAheadControl)
            and spectral_features is not None
        )

        for step in range(n_steps):
            # Current PAC
            pac = sim.pac

            # Make decision -- pass spectral features when available
            if _pass_spectral:
                feat_idx = min(step, spectral_features.shape[0] - 1)
                action = method.step(pac, spectral_features=spectral_features[feat_idx])
            else:
                action = method.step(pac)

            # Execute action in simulator
            sim.step(action)

            # Track
            pac_values.append(pac)
            actions.append(action)

        pac_values = np.array(pac_values)
        actions = np.array(actions)

        # Compute metrics — use first 10 seconds as baseline (not just pac[0])
        n_baseline = min(10, len(pac_values))
        baseline_pac = float(np.mean(pac_values[:n_baseline]))
        pac_improvement = 100.0 * (np.mean(pac_values) - baseline_pac) / (baseline_pac + 1e-8)
        pac_variance_ratio = np.var(pac_values[-100:]) / (np.var(pac_values[:100]) + 1e-8)
        stimulation_time = 100.0 * np.mean(actions)
        efficiency_ratio = pac_improvement / (stimulation_time + 1e-8) if stimulation_time > 0 else 0.0

        metrics = ValidationMetrics(
            pac_mean=float(np.mean(pac_values)),
            pac_std=float(np.std(pac_values)),
            pac_improvement=float(pac_improvement),
            pac_variance_ratio=float(pac_variance_ratio),
            stimulation_time=float(stimulation_time),
            efficiency_ratio=float(efficiency_ratio),
            method_name=method.name
        )

        logger.info(f"  PAC: mean={metrics.pac_mean:.4f}, std={metrics.pac_std:.4f}")
        logger.info(f"  PAC improvement: {metrics.pac_improvement:.2f}%")
        logger.info(f"  Stimulation time: {metrics.stimulation_time:.1f}%")
        logger.info(f"  Efficiency ratio: {metrics.efficiency_ratio:.4f}")

        # Store history (last trial only — for plotting)
        self.results[method.name] = {
            'pac_values': pac_values,
            'actions': actions,
            'metrics': metrics
        }

        return metrics

    def run_all(self, duration_sec: int = 360, n_trials: int = 1,
                base_seed: int = 42, **sim_kwargs) -> Dict[str, list]:
        """
        Run all methods multiple times with matched noise per trial.

        Each trial uses the same seed for every method so comparisons are
        fair (identical noise realizations). Multi-trial metrics are
        accumulated in the returned dict; ``self.results`` retains the last
        trial for plotting.

        Args:
            duration_sec: Simulation duration per trial.
            n_trials: Number of trials per method.
            base_seed: Starting seed; trial *i* uses ``base_seed + i``.
            **sim_kwargs: Forwarded to ``run_simulation`` (e.g. use_fatigue).

        Returns:
            results: ``{method_name: [ValidationMetrics, ...]}``
        """
        all_results: Dict[str, list] = {m.name: [] for m in self.methods}

        for trial in range(n_trials):
            seed = base_seed + trial
            logger.info(f"\n{'='*60}")
            logger.info(f"Trial {trial+1}/{n_trials} (seed={seed})")
            logger.info("=" * 60)

            for method in self.methods:
                metrics = self.run_simulation(
                    method, duration_sec=duration_sec, seed=seed, **sim_kwargs
                )
                all_results[method.name].append(metrics)

        # Store accumulated metrics for statistical_comparison
        self._all_trial_metrics = all_results
        return all_results

    def statistical_comparison(self, metric_name: str = 'pac_improvement') -> dict:
        """
        Compare methods using statistical tests on multi-trial data.

        Uses accumulated trial metrics from ``run_all`` when available,
        falling back to single-trial ``self.results`` otherwise.

        Args:
            metric_name: Metric to compare.

        Returns:
            stats_result: Statistical test results.
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Statistical Comparison: {metric_name}")
        logger.info("=" * 60)

        # Prefer multi-trial data from run_all
        data_by_method: Dict[str, List[float]] = {}
        if hasattr(self, '_all_trial_metrics') and self._all_trial_metrics:
            for method_name, metrics_list in self._all_trial_metrics.items():
                data_by_method[method_name] = [
                    getattr(m, metric_name) for m in metrics_list
                ]
        else:
            # Fallback: single-trial from self.results
            for method_name, results in self.results.items():
                if isinstance(results, dict) and 'metrics' in results:
                    metrics = results['metrics']
                    data_by_method[method_name] = [getattr(metrics, metric_name)]

        if len(data_by_method) < 2:
            logger.warning("Need at least 2 methods for comparison")
            return {}

        groups = list(data_by_method.values())

        # ANOVA requires n > 1 per group for within-group variance
        min_group_size = min(len(g) for g in groups)
        if min_group_size < 2:
            logger.warning(
                f"Only {min_group_size} trial(s) per group — ANOVA requires "
                f"n >= 2. Run with n_trials >= 2 for valid statistics."
            )
            return {
                'f_statistic': float('nan'),
                'p_value': float('nan'),
                'method_means': {k: float(np.mean(v)) for k, v in data_by_method.items()},
            }

        f_stat, p_value = stats.f_oneway(*groups)

        logger.info(f"One-way ANOVA:")
        logger.info(f"  F-statistic: {f_stat:.4f}")
        logger.info(f"  p-value: {p_value:.6f}")

        # Effect size (Cohen's d) for 2-group comparison
        if len(groups) == 2:
            g0, g1 = np.array(groups[0]), np.array(groups[1])
            mean_diff = abs(np.mean(g0) - np.mean(g1))
            pooled_std = np.sqrt((np.var(g0, ddof=1) + np.var(g1, ddof=1)) / 2)
            cohens_d = mean_diff / (pooled_std + 1e-8)
            logger.info(f"  Cohen's d: {cohens_d:.4f}")

        return {
            'f_statistic': float(f_stat),
            'p_value': float(p_value),
            'method_means': {k: float(np.mean(v)) for k, v in data_by_method.items()},
        }

    def plot_comparison(self, output_name: str = 'validation_comparison.png'):
        """
        Generate comparison plots.

        Args:
            output_name: Output filename
        """
        if not self.results:
            logger.warning("No results to plot")
            return

        n_methods = len(self.results)
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        methods = list(self.results.keys())
        colors = plt.cm.Set2(np.linspace(0, 1, n_methods))

        # 1. PAC time series
        ax = axes[0, 0]
        for color, method_name in zip(colors, methods):
            pac_values = self.results[method_name]['pac_values']
            time = np.arange(len(pac_values)) / 60  # Convert to minutes
            ax.plot(time, pac_values, label=method_name, color=color, alpha=0.7)

        ax.set_xlabel('Time (minutes)')
        ax.set_ylabel('Phase-Amplitude Coupling')
        ax.set_title('PAC Dynamics Over Time')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

        # 2. PAC improvement
        ax = axes[0, 1]
        pac_improvements = [self.results[m]['metrics'].pac_improvement for m in methods]
        bars = ax.bar(range(n_methods), pac_improvements, color=colors, edgecolor='black')
        ax.set_ylabel('PAC Improvement (%)')
        ax.set_title('PAC Improvement vs. Baseline')
        ax.set_xticks(range(n_methods))
        ax.set_xticklabels([m.split('(')[0].strip() for m in methods], rotation=15, ha='right')
        ax.grid(axis='y', alpha=0.3)

        for bar, val in zip(bars, pac_improvements):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.1f}%', ha='center', va='bottom', fontsize=9)

        # 3. Efficiency ratio
        ax = axes[1, 0]
        efficiency = [self.results[m]['metrics'].efficiency_ratio for m in methods]
        bars = ax.bar(range(n_methods), efficiency, color=colors, edgecolor='black')
        ax.set_ylabel('Efficiency Ratio')
        ax.set_title('PAC Improvement per Unit Stimulation Time')
        ax.set_xticks(range(n_methods))
        ax.set_xticklabels([m.split('(')[0].strip() for m in methods], rotation=15, ha='right')
        ax.grid(axis='y', alpha=0.3)

        # 4. Stimulation time
        ax = axes[1, 1]
        stim_times = [self.results[m]['metrics'].stimulation_time for m in methods]
        bars = ax.bar(range(n_methods), stim_times, color=colors, edgecolor='black')
        ax.set_ylabel('Stimulation Time (%)')
        ax.set_title('Energy Efficiency')
        ax.set_xticks(range(n_methods))
        ax.set_xticklabels([m.split('(')[0].strip() for m in methods], rotation=15, ha='right')
        ax.set_ylim([0, 100])
        ax.grid(axis='y', alpha=0.3)

        for bar, val in zip(bars, stim_times):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.1f}%', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        output_path = self.output_dir / output_name
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved validation comparison to {output_path}")
        plt.close()


def main():
    """Main entry point for validation."""
    parser = argparse.ArgumentParser(
        description="Validate closed-loop control strategies"
    )
    parser.add_argument('--output_dir', type=str, default='results/figures',
                       help='Output directory for results')
    parser.add_argument('--duration', type=int, default=360,
                       help='Simulation duration in seconds')
    parser.add_argument('--n_trials', type=int, default=3,
                       help='Number of trials per method')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create validator
    validator = SimulationValidator(output_dir=args.output_dir)

    # Add methods to compare
    validator.add_method(FixedScheduleControl())
    validator.add_method(ReactiveThresholdControl())
    validator.add_method(PredictiveLookAheadControl())
    validator.add_method(OracleControl())

    # Run validation with matched seeds per trial
    all_results = validator.run_all(
        duration_sec=args.duration,
        n_trials=args.n_trials,
        base_seed=42,
    )

    # Statistical comparison
    validator.statistical_comparison('pac_improvement')

    # Generate plots
    validator.plot_comparison()

    logger.info("\n" + "="*60)
    logger.info("Validation complete!")
    logger.info("="*60)


if __name__ == "__main__":
    main()
