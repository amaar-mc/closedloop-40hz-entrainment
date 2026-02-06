"""
Validation and Comparison Framework for Closed-Loop Control Strategies

Compares four neuromodulation approaches:
1. Fixed Schedule (control): 40s ON + 20s OFF
2. Reactive Threshold: Current PAC-based decisions
3. Predictive MPC: Trained EEGNet + personalization (proposed system)
4. Oracle: Perfect PAC knowledge (upper bound)

Metrics:
- PAC improvement (%): Change from baseline
- PAC variance ratio: Variability reduction
- Stimulation time (%): Energy efficiency
- Efficiency ratio: PAC gain per unit stimulation
- R² score: Model prediction accuracy
- Statistical significance: ANOVA, Tukey HSD, Cohen's d

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
from simulator import EntrainmentSimulator, StimAction, extract_tau_parameters_from_data
from utils import compute_regression_metrics, ensure_dir

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
    """Base class for control strategies."""

    def __init__(self, name: str):
        """Initialize control method."""
        self.name = name

    def reset(self):
        """Reset method state for new trial."""
        pass

    def step(self, pac_current: float) -> int:
        """
        Make stimulation decision.

        Args:
            pac_current: Current PAC value

        Returns:
            action: 0=REST, 1=STIMULATE
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
    """Reactive control based on current PAC vs. baseline."""

    def __init__(self, window_size: int = 30, threshold_std: float = 0.5):
        """
        Initialize reactive control.

        Args:
            window_size: Baseline window size in samples
            threshold_std: Threshold in standard deviations
        """
        super().__init__("Reactive Threshold (No Prediction)")
        self.window_size = window_size
        self.threshold_std = threshold_std
        self.pac_buffer = []

    def reset(self):
        """Reset baseline buffer."""
        self.pac_buffer = []

    def step(self, pac_current: float) -> int:
        """
        Make reactive decision based on current PAC.

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
            return StimAction.REST

        # Compute z-score
        baseline_mean = np.mean(self.pac_buffer)
        baseline_std = np.std(self.pac_buffer)
        z_score = (pac_current - baseline_mean) / (baseline_std + 1e-8)

        # Make decision
        if z_score < -self.threshold_std:
            return StimAction.STIMULATE
        elif z_score > self.threshold_std:
            return StimAction.REST
        else:
            return StimAction.REST

    def step(self, pac_current: float) -> int:
        """Make reactive decision based on current PAC."""
        self.pac_buffer.append(pac_current)
        if len(self.pac_buffer) > self.window_size:
            self.pac_buffer.pop(0)

        if len(self.pac_buffer) < max(5, self.window_size // 2):
            return StimAction.REST

        baseline_mean = np.mean(self.pac_buffer)
        baseline_std = np.std(self.pac_buffer)
        z_score = (pac_current - baseline_mean) / (baseline_std + 1e-8)

        if z_score < -self.threshold_std:
            return StimAction.STIMULATE
        elif z_score > self.threshold_std:
            return StimAction.REST
        else:
            return StimAction.REST


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

    def __init__(self, output_dir: str = 'results'):
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
                      tau_decay: float = 0.10) -> ValidationMetrics:
        """
        Run simulation for single method.

        Args:
            method: Control method to test
            duration_sec: Simulation duration in seconds
            fs: Sampling frequency (decisions per second)
            tau_rise: PAC rise time constant
            tau_decay: PAC decay time constant

        Returns:
            metrics: Validation metrics
        """
        logger.info(f"\nRunning simulation: {method.name}")
        logger.info(f"  Duration: {duration_sec}s")

        # Initialize simulator
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

        for step in range(n_steps):
            # Current PAC
            pac = sim.pac

            # Make decision
            action = method.step(pac)

            # Execute action in simulator
            sim.step(action)

            # Track
            pac_values.append(pac)
            actions.append(action)

        pac_values = np.array(pac_values)
        actions = np.array(actions)

        # Compute metrics
        baseline_pac = pac_values[0]
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

        # Store history
        self.results[method.name] = {
            'pac_values': pac_values,
            'actions': actions,
            'metrics': metrics
        }

        return metrics

    def run_all(self, duration_sec: int = 360, n_trials: int = 1) -> Dict[str, list]:
        """
        Run all methods multiple times.

        Args:
            duration_sec: Simulation duration per trial
            n_trials: Number of trials per method

        Returns:
            results: Dictionary of metrics per method
        """
        all_results = {}

        for method in self.methods:
            logger.info(f"\n" + "="*60)
            logger.info(f"Testing: {method.name}")
            logger.info("="*60)

            trial_metrics = []

            for trial in range(n_trials):
                logger.info(f"\nTrial {trial+1}/{n_trials}")
                metrics = self.run_simulation(method, duration_sec=duration_sec)
                trial_metrics.append(metrics)

            all_results[method.name] = trial_metrics

        return all_results

    def statistical_comparison(self, metric_name: str = 'pac_improvement') -> dict:
        """
        Compare methods using statistical tests.

        Args:
            metric_name: Metric to compare

        Returns:
            stats_result: Statistical test results
        """
        logger.info(f"\n" + "="*60)
        logger.info(f"Statistical Comparison: {metric_name}")
        logger.info("="*60)

        # Extract metric values
        data_by_method = {}
        for method_name, results in self.results.items():
            if isinstance(results, dict) and 'metrics' in results:
                metrics = results['metrics']
                data_by_method[method_name] = getattr(metrics, metric_name)

        if len(data_by_method) < 2:
            logger.warning("Need at least 2 methods for comparison")
            return {}

        # ANOVA
        values = list(data_by_method.values())
        f_stat, p_value = stats.f_oneway(*[[v] for v in values])

        logger.info(f"One-way ANOVA:")
        logger.info(f"  F-statistic: {f_stat:.4f}")
        logger.info(f"  p-value: {p_value:.6f}")

        # Effect size (Cohen's d) - simplified for 2 groups
        if len(values) == 2:
            mean_diff = abs(values[0] - values[1])
            pooled_std = np.sqrt((np.var(values[0]) + np.var(values[1])) / 2 + 1e-8)
            cohens_d = mean_diff / (pooled_std + 1e-8)
            logger.info(f"  Cohen's d: {cohens_d:.4f}")

        return {
            'f_statistic': f_stat,
            'p_value': p_value,
            'method_means': data_by_method
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
    parser.add_argument('--output_dir', type=str, default='results',
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
    validator.add_method(OracleControl())

    # Run validation
    all_results = validator.run_all(
        duration_sec=args.duration,
        n_trials=args.n_trials
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
