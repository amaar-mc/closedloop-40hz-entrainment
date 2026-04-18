"""
TCN-Integrated Closed-Loop Simulation Validation.

Integrates the trained MultiscaleCausalTCN into the closed-loop simulation
framework, replacing the linear-trend-based Predictive Look-Ahead controller
with a genuine neural-network-based predictive controller.

Compares four control strategies:
    1. Fixed Schedule: 40s ON + 20s OFF (control condition)
    2. Reactive Threshold: Current PAC z-score decisions
    3. TCN-Predictive: Uses RealtimePACForecaster for look-ahead decisions
    4. Oracle: Perfect PAC knowledge (upper bound)

Runs n=50 trials per method across three simulator conditions:
    - Standard EntrainmentSimulator (no fatigue)
    - FatigueAwareSimulator (default fatigue)
    - Population-diverse (randomized subject parameters)

Reports full statistical analysis:
    - Wilcoxon signed-rank tests for pairwise comparisons
    - Hedges' g effect sizes
    - Bootstrap 95% confidence intervals (1000 resamples)

Usage:
    python rigor/experiments/tcn_integrated_simulation.py \\
        --checkpoint-path models/best_multiscale_tcn_lb20_hz1.pth \\
        --data-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean \\
        --output-dir rigor/experiments/tcn_simulation_results

Author: Amaar Chughtai
Date: February 2026
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass, asdict
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_DIR = _PROJECT_ROOT / "src"
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from simulator import EntrainmentSimulator, FatigueAwareSimulator, StimAction  # noqa: E402
from temporal_multiscale.realtime_inference import RealtimePACForecaster  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BOOTSTRAP_N_RESAMPLES: int = 1000
BOOTSTRAP_CI_LEVEL: float = 0.95


# ===================================================================
# Per-trial metrics
# ===================================================================


@dataclass
class TrialMetrics:
    """Metrics extracted from a single simulation trial."""

    pac_mean: float
    pac_std: float
    stimulation_pct: float
    efficiency_ratio: float
    late_session_pac: float

    def to_dict(self) -> Dict[str, float]:
        """Convert to plain dictionary for JSON serialization."""
        return asdict(self)


# ===================================================================
# Statistical helper functions
# ===================================================================


def bootstrap_ci(
    data: np.ndarray,
    statistic_fn: Any = np.mean,
    n_resamples: int = BOOTSTRAP_N_RESAMPLES,
    confidence_level: float = BOOTSTRAP_CI_LEVEL,
    rng: Optional[np.random.Generator] = None,
) -> Tuple[float, float, float]:
    """Compute bootstrap confidence interval.

    Args:
        data: 1-D array of observations.
        statistic_fn: Callable that computes the statistic of interest.
        n_resamples: Number of bootstrap resamples.
        confidence_level: Confidence level (e.g. 0.95 for 95% CI).
        rng: Numpy random generator for reproducibility.

    Returns:
        Tuple of (point_estimate, ci_lower, ci_upper).
    """
    if rng is None:
        rng = np.random.default_rng()

    n = len(data)
    boot_stats = np.empty(n_resamples, dtype=np.float64)
    for i in range(n_resamples):
        sample = rng.choice(data, size=n, replace=True)
        boot_stats[i] = statistic_fn(sample)

    alpha = 1.0 - confidence_level
    ci_lower = float(np.percentile(boot_stats, 100 * alpha / 2))
    ci_upper = float(np.percentile(boot_stats, 100 * (1 - alpha / 2)))
    point = float(statistic_fn(data))
    return point, ci_lower, ci_upper


def hedges_g(group_a: np.ndarray, group_b: np.ndarray) -> float:
    """Compute Hedges' g (bias-corrected Cohen's d).

    Uses pooled standard deviation with Bessel correction.

    Args:
        group_a: Observations for group A.
        group_b: Observations for group B.

    Returns:
        Effect size (positive means group_a > group_b).
    """
    n_a = len(group_a)
    n_b = len(group_b)
    if n_a < 2 or n_b < 2:
        return float("nan")

    mean_diff = float(np.mean(group_a) - np.mean(group_b))
    var_a = float(np.var(group_a, ddof=1))
    var_b = float(np.var(group_b, ddof=1))

    pooled_std = np.sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2))
    if pooled_std < 1e-12:
        return float("nan")

    d = mean_diff / pooled_std

    # Hedge's correction factor J (approximation)
    df = n_a + n_b - 2
    j = 1.0 - 3.0 / (4.0 * df - 1.0)

    return float(d * j)


def pairwise_wilcoxon(
    data_by_method: Dict[str, np.ndarray],
    metric_name: str,
) -> List[Dict[str, Any]]:
    """Run Wilcoxon signed-rank tests for all pairs of methods.

    Args:
        data_by_method: Mapping of method name to 1-D trial metric array.
        metric_name: Name of the metric being compared.

    Returns:
        List of result dictionaries, one per pair.
    """
    results: List[Dict[str, Any]] = []
    method_names = sorted(data_by_method.keys())

    for m_a, m_b in combinations(method_names, 2):
        a = data_by_method[m_a]
        b = data_by_method[m_b]
        n_common = min(len(a), len(b))
        if n_common < 6:
            results.append({
                "method_a": m_a,
                "method_b": m_b,
                "metric": metric_name,
                "statistic": float("nan"),
                "p_value": float("nan"),
                "hedges_g": float("nan"),
                "note": f"Insufficient paired observations (n={n_common})",
            })
            continue

        a_paired = a[:n_common]
        b_paired = b[:n_common]

        diffs = a_paired - b_paired
        if np.all(np.abs(diffs) < 1e-15):
            results.append({
                "method_a": m_a,
                "method_b": m_b,
                "metric": metric_name,
                "statistic": 0.0,
                "p_value": 1.0,
                "hedges_g": 0.0,
                "note": "All differences are zero",
            })
            continue

        stat, p_val = stats.wilcoxon(a_paired, b_paired, alternative="two-sided")
        g = hedges_g(a_paired, b_paired)

        results.append({
            "method_a": m_a,
            "method_b": m_b,
            "metric": metric_name,
            "statistic": float(stat),
            "p_value": float(p_val),
            "hedges_g": float(g),
        })

    return results


# ===================================================================
# Control methods
# ===================================================================


class ControlMethodBase:
    """Base class for control strategies."""

    def __init__(self, name: str) -> None:
        self.name = name

    def reset(self) -> None:
        """Reset state for a new trial."""

    def step(self, pac_current: float) -> int:
        """Return 0 (REST) or 1 (STIMULATE)."""
        raise NotImplementedError


class FixedScheduleControl(ControlMethodBase):
    """Fixed 40s ON + 20s OFF schedule (control condition)."""

    def __init__(
        self,
        stim_duration: int = 40,
        rest_duration: int = 20,
        fs: float = 1.0,
    ) -> None:
        super().__init__("Fixed Schedule")
        self.stim_samples = int(stim_duration * fs)
        self.rest_samples = int(rest_duration * fs)
        self.cycle_samples = self.stim_samples + self.rest_samples
        self.step_count = 0

    def reset(self) -> None:
        self.step_count = 0

    def step(self, pac_current: float) -> int:
        position = self.step_count % self.cycle_samples
        self.step_count += 1
        return int(StimAction.STIMULATE) if position < self.stim_samples else int(StimAction.REST)


class ReactiveThresholdControl(ControlMethodBase):
    """Reactive z-score-based control with rolling baseline."""

    def __init__(
        self,
        window_size: int = 30,
        threshold_std: float = 0.5,
    ) -> None:
        super().__init__("Reactive Threshold")
        self.window_size = window_size
        self.threshold_std = threshold_std
        self.pac_buffer: List[float] = []

    def reset(self) -> None:
        self.pac_buffer = []

    def step(self, pac_current: float) -> int:
        self.pac_buffer.append(pac_current)
        if len(self.pac_buffer) > self.window_size:
            self.pac_buffer.pop(0)

        if len(self.pac_buffer) < max(5, self.window_size // 2):
            return int(StimAction.REST)

        baseline_mean = float(np.mean(self.pac_buffer))
        baseline_std = float(np.std(self.pac_buffer))
        z_score = (pac_current - baseline_mean) / (baseline_std + 1e-8)

        if z_score < -self.threshold_std:
            return int(StimAction.STIMULATE)
        return int(StimAction.REST)


class TCNPredictiveControl(ControlMethodBase):
    """Predictive control using the trained MultiscaleCausalTCN.

    Wraps the RealtimePACForecaster to generate look-ahead predictions
    within the simulation loop. Since the simulator does not produce
    raw EEG (only PAC scalars), the spectral features are synthesized
    as constant vectors. This is acceptable because:
      1. The ablation study shows PAC history features dominate prediction.
      2. Spectral features are constant-ish within a subject session.
      3. The TCN still uses the PAC multiscale and stim context features,
         which are computed from actual simulation state.

    Decision logic:
        - If predicted delta_pac < decline_threshold: STIMULATE preemptively
        - If predicted delta_pac > |decline_threshold|: REST (save energy)
        - Otherwise: Fall back to z-score reactive logic
        - Hysteresis: minimum hold_time before state transitions
    """

    def __init__(
        self,
        forecaster: RealtimePACForecaster,
        window_size: int = 30,
        threshold_std: float = 0.5,
        decline_threshold: float = -0.3,
        hold_time: int = 5,
    ) -> None:
        super().__init__("TCN-Predictive")
        self.forecaster = forecaster
        self.window_size = window_size
        self.threshold_std = threshold_std
        self.decline_threshold = decline_threshold
        self.hold_time = hold_time

        # Internal state
        self.pac_buffer: List[float] = []
        self.action_buffer: List[int] = []
        self.current_state: int = int(StimAction.REST)
        self.time_in_state: int = 0
        self.stim_start_time: Optional[float] = None
        self.last_switch_time: float = 0.0
        self.step_count: int = 0

        # Synthetic spectral features (zero-mean in normalized space)
        # The forecaster expects (n_spectral,) features per step.
        n_spectral = forecaster.feature_dim - 12  # 73 - 12 = 61 typically
        self._synthetic_spectral = np.zeros(n_spectral, dtype=np.float32)

    def reset(self) -> None:
        """Reset controller and forecaster for a new trial."""
        self.forecaster.reset()
        self.pac_buffer = []
        self.action_buffer = []
        self.current_state = int(StimAction.REST)
        self.time_in_state = 0
        self.stim_start_time = None
        self.last_switch_time = 0.0
        self.step_count = 0

    def _compute_stim_context(self) -> Tuple[float, float, float, float, float]:
        """Compute stimulation context features from action history.

        Returns:
            Tuple of (stim_state, time_since_switch_sec, stim_frac_recent,
            cycle_phase_sin, cycle_phase_cos).
        """
        stim_state = float(self.current_state)
        time_since_switch = float(self.step_count - self.last_switch_time)

        # Fraction of stim in recent 20-second window
        recent_window = min(20, len(self.action_buffer))
        if recent_window > 0:
            stim_frac = float(np.mean(self.action_buffer[-recent_window:]))
        else:
            stim_frac = 0.0

        # Protocol cycle phase (60s cycle: 40s on + 20s off)
        t = float(self.step_count)
        cycle = 60.0
        phase = (t % cycle) / cycle
        phase_sin = float(np.sin(2.0 * np.pi * phase))
        phase_cos = float(np.cos(2.0 * np.pi * phase))

        return stim_state, time_since_switch, stim_frac, phase_sin, phase_cos

    def step(self, pac_current: float) -> int:
        """Make stimulation decision using TCN look-ahead prediction.

        Args:
            pac_current: Current PAC value from the simulator.

        Returns:
            Action: 0 (REST) or 1 (STIMULATE).
        """
        self.pac_buffer.append(pac_current)
        if len(self.pac_buffer) > self.window_size:
            self.pac_buffer.pop(0)

        # Compute stim context from action history
        stim_state, tss, stim_frac, phase_sin, phase_cos = (
            self._compute_stim_context()
        )

        # Feed observation to the TCN forecaster
        prediction = self.forecaster.step(
            spectral_features=self._synthetic_spectral,
            pac_current=pac_current,
            stim_state=stim_state,
            time_since_switch_sec=tss,
            stim_frac_recent=stim_frac,
            cycle_phase_sin=phase_sin,
            cycle_phase_cos=phase_cos,
        )

        # Determine desired state
        desired_state: Optional[int] = None

        if prediction is not None:
            delta_pac = prediction["delta_pac"]

            # Proactive: predicted decline -> stimulate early
            if delta_pac < self.decline_threshold:
                desired_state = int(StimAction.STIMULATE)
            # Proactive: predicted rise -> can rest (save energy)
            elif delta_pac > abs(self.decline_threshold):
                desired_state = int(StimAction.REST)

        # Fall back to reactive z-score logic
        if desired_state is None and len(self.pac_buffer) >= max(
            5, self.window_size // 2
        ):
            baseline_mean = float(np.mean(self.pac_buffer))
            baseline_std = float(np.std(self.pac_buffer)) + 1e-8
            z_score = (pac_current - baseline_mean) / baseline_std

            if z_score < -self.threshold_std:
                desired_state = int(StimAction.STIMULATE)
            elif z_score > self.threshold_std:
                desired_state = int(StimAction.REST)

        # No signal -> maintain
        if desired_state is None:
            desired_state = self.current_state

        # Apply hysteresis
        if desired_state != self.current_state:
            if self.time_in_state >= self.hold_time:
                self.current_state = desired_state
                self.time_in_state = 0
                self.last_switch_time = float(self.step_count)
        else:
            self.time_in_state += 1

        self.action_buffer.append(self.current_state)
        self.step_count += 1

        return self.current_state


class OracleControl(ControlMethodBase):
    """Oracle with perfect information (upper bound)."""

    def __init__(self, pac_target: float = 0.2) -> None:
        super().__init__("Oracle")
        self.pac_target = pac_target

    def step(self, pac_current: float) -> int:
        return int(StimAction.STIMULATE) if pac_current < self.pac_target else int(StimAction.REST)


# ===================================================================
# Simulation runner
# ===================================================================


def run_single_trial(
    method: ControlMethodBase,
    simulator_class: type,
    simulator_kwargs: Dict[str, Any],
    duration_sec: int,
    fs: float = 1.0,
    late_session_sec: int = 60,
) -> TrialMetrics:
    """Run one simulation trial and return metrics.

    Args:
        method: Control method instance (will be reset).
        simulator_class: EntrainmentSimulator or FatigueAwareSimulator.
        simulator_kwargs: Constructor kwargs for the simulator.
        duration_sec: Duration in seconds.
        fs: Decision frequency (Hz).
        late_session_sec: Trailing seconds for late-session metric.

    Returns:
        TrialMetrics for this trial.
    """
    sim = simulator_class(**simulator_kwargs)
    method.reset()

    n_steps = int(duration_sec * fs)
    pac_values = np.empty(n_steps, dtype=np.float64)
    actions = np.empty(n_steps, dtype=np.int32)

    for t in range(n_steps):
        pac = sim.pac
        action = method.step(pac)
        sim.step(action)
        pac_values[t] = pac
        actions[t] = action

    pac_mean = float(np.mean(pac_values))
    pac_std = float(np.std(pac_values))
    stimulation_pct = float(100.0 * np.mean(actions))

    if stimulation_pct > 0:
        efficiency_ratio = pac_mean / (stimulation_pct / 100.0)
    else:
        efficiency_ratio = pac_mean

    late_idx = max(0, n_steps - int(late_session_sec * fs))
    late_session_pac = float(np.mean(pac_values[late_idx:]))

    return TrialMetrics(
        pac_mean=pac_mean,
        pac_std=pac_std,
        stimulation_pct=stimulation_pct,
        efficiency_ratio=efficiency_ratio,
        late_session_pac=late_session_pac,
    )


def run_trial_batch(
    methods: List[ControlMethodBase],
    simulator_class: type,
    simulator_kwargs: Dict[str, Any],
    n_trials: int,
    duration_sec: int,
    base_seed: int,
    fs: float = 1.0,
    late_session_sec: int = 60,
    label: str = "",
) -> Dict[str, List[TrialMetrics]]:
    """Run n_trials for each method with reproducible seeds.

    Args:
        methods: List of control method instances.
        simulator_class: Simulator class.
        simulator_kwargs: Base kwargs for the simulator.
        n_trials: Number of trials per method.
        duration_sec: Duration per trial in seconds.
        base_seed: Base seed (trial i uses base_seed + i).
        fs: Decision frequency.
        late_session_sec: Seconds for late-session metric.
        label: Descriptive label for logging.

    Returns:
        Dictionary mapping method name to list of TrialMetrics.
    """
    results: Dict[str, List[TrialMetrics]] = {m.name: [] for m in methods}

    for trial_idx in range(n_trials):
        trial_seed = base_seed + trial_idx
        for method in methods:
            np.random.seed(trial_seed)
            metrics = run_single_trial(
                method=method,
                simulator_class=simulator_class,
                simulator_kwargs=simulator_kwargs,
                duration_sec=duration_sec,
                fs=fs,
                late_session_sec=late_session_sec,
            )
            results[method.name].append(metrics)

        if (trial_idx + 1) % 10 == 0 or trial_idx == 0:
            logger.info(
                "  [%s] Trial %d/%d complete",
                label or simulator_class.__name__,
                trial_idx + 1,
                n_trials,
            )

    return results


def generate_subject_parameters(
    n_subjects: int,
    rng: np.random.Generator,
) -> List[Dict[str, Any]]:
    """Generate randomized simulator parameters for diverse subjects.

    Varies tau_rise, tau_decay, pac_max, noise_std to model inter-individual
    variability observed across the 35 subjects in ds005048.

    Args:
        n_subjects: Number of virtual subjects.
        rng: Numpy random generator.

    Returns:
        List of simulator_kwargs dicts.
    """
    subjects: List[Dict[str, Any]] = []
    for _ in range(n_subjects):
        tau_rise = float(np.clip(rng.normal(0.15, 0.04), 0.05, 0.35))
        tau_decay = float(np.clip(rng.normal(0.10, 0.03), 0.03, 0.25))
        pac_max = float(np.clip(rng.normal(0.30, 0.06), 0.15, 0.50))
        pac_min = 0.05
        noise_std = float(np.clip(rng.normal(0.02, 0.005), 0.005, 0.04))
        subjects.append({
            "tau_rise": tau_rise,
            "tau_decay": tau_decay,
            "pac_max": pac_max,
            "pac_min": pac_min,
            "noise_std": noise_std,
        })
    return subjects


def run_population_diverse(
    methods: List[ControlMethodBase],
    n_subjects: int,
    duration_sec: int,
    base_seed: int,
    fs: float = 1.0,
    late_session_sec: int = 60,
) -> Dict[str, List[TrialMetrics]]:
    """Run one trial per subject with randomized simulator parameters.

    Args:
        methods: Control methods.
        n_subjects: Number of virtual subjects.
        duration_sec: Duration per trial.
        base_seed: Seed for parameter generation.
        fs: Decision frequency.
        late_session_sec: Seconds for late-session metric.

    Returns:
        Dictionary mapping method name to list of TrialMetrics.
    """
    rng = np.random.default_rng(base_seed)
    subject_params = generate_subject_parameters(n_subjects, rng)

    results: Dict[str, List[TrialMetrics]] = {m.name: [] for m in methods}

    for subj_idx, params in enumerate(subject_params):
        trial_seed = base_seed + 10000 + subj_idx
        for method in methods:
            np.random.seed(trial_seed)
            metrics = run_single_trial(
                method=method,
                simulator_class=EntrainmentSimulator,
                simulator_kwargs=params,
                duration_sec=duration_sec,
                fs=fs,
                late_session_sec=late_session_sec,
            )
            results[method.name].append(metrics)

        if (subj_idx + 1) % 10 == 0 or subj_idx == 0:
            logger.info(
                "  [Population-Diverse] Subject %d/%d complete",
                subj_idx + 1,
                n_subjects,
            )

    return results


# ===================================================================
# Analysis and reporting
# ===================================================================

METRIC_FIELDS = [
    "pac_mean",
    "pac_std",
    "stimulation_pct",
    "efficiency_ratio",
    "late_session_pac",
]


def extract_metric_array(
    trial_list: List[TrialMetrics],
    metric_name: str,
) -> np.ndarray:
    """Extract a single metric from a list of TrialMetrics."""
    return np.array([getattr(tm, metric_name) for tm in trial_list], dtype=np.float64)


def compute_summary_stats(
    results: Dict[str, List[TrialMetrics]],
    rng: np.random.Generator,
) -> Dict[str, Dict[str, Any]]:
    """Compute per-method summary statistics with bootstrap CIs.

    Args:
        results: Dictionary mapping method name to trial metrics.
        rng: Random generator for bootstrap reproducibility.

    Returns:
        Nested dictionary with per-metric statistics.
    """
    summaries: Dict[str, Dict[str, Any]] = {}

    for method_name, trials in results.items():
        method_summary: Dict[str, Any] = {"n_trials": len(trials)}
        for metric in METRIC_FIELDS:
            arr = extract_metric_array(trials, metric)
            point, ci_lo, ci_hi = bootstrap_ci(arr, np.mean, rng=rng)
            method_summary[metric] = {
                "mean": point,
                "std": float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
                "ci_lower": ci_lo,
                "ci_upper": ci_hi,
            }
        summaries[method_name] = method_summary

    return summaries


def compute_all_statistics(
    results: Dict[str, List[TrialMetrics]],
    rng: np.random.Generator,
) -> Dict[str, Any]:
    """Compute full statistical analysis suite.

    Args:
        results: Dictionary mapping method name to trial metrics.
        rng: Random generator.

    Returns:
        Dictionary with summary_stats, wilcoxon, and effect_sizes.
    """
    output: Dict[str, Any] = {}

    # Summary statistics with CIs
    output["summary_stats"] = compute_summary_stats(results, rng)

    # Pairwise Wilcoxon signed-rank tests
    wilcoxon_results: Dict[str, Any] = {}
    for metric in METRIC_FIELDS:
        data_by_method = {
            name: extract_metric_array(trials, metric)
            for name, trials in results.items()
        }
        wilcoxon_results[metric] = pairwise_wilcoxon(data_by_method, metric)
    output["wilcoxon"] = wilcoxon_results

    # Hedges' g for all pairwise comparisons
    effect_sizes: Dict[str, Any] = {}
    for metric in METRIC_FIELDS:
        metric_effects: List[Dict[str, Any]] = []
        method_names = sorted(results.keys())
        for m_a, m_b in combinations(method_names, 2):
            a = extract_metric_array(results[m_a], metric)
            b = extract_metric_array(results[m_b], metric)
            g = hedges_g(a, b)
            metric_effects.append({
                "method_a": m_a,
                "method_b": m_b,
                "hedges_g": g,
            })
        effect_sizes[metric] = metric_effects
    output["effect_sizes"] = effect_sizes

    return output


# ===================================================================
# Pretty printing
# ===================================================================


def _fmt_ci(mean: float, ci_lo: float, ci_hi: float, fmt: str = ".4f") -> str:
    """Format a value with its 95% CI."""
    return f"{mean:{fmt}} [{ci_lo:{fmt}}, {ci_hi:{fmt}}]"


def print_summary_table(
    summary_stats: Dict[str, Dict[str, Any]],
    title: str = "Results",
) -> None:
    """Print a formatted summary table to stdout."""
    method_names = sorted(summary_stats.keys())

    header = (
        f"{'Method':<25s} | {'PAC Mean (95% CI)':<32s} | {'Stim% (95% CI)':<32s} | "
        f"{'Efficiency (95% CI)':<32s} | {'Late-Session PAC (95% CI)':<32s}"
    )
    sep = "-" * len(header)

    print(f"\n{title}")
    print(sep)
    print(header)
    print(sep)

    for name in method_names:
        s = summary_stats[name]
        pac = s["pac_mean"]
        stim = s["stimulation_pct"]
        eff = s["efficiency_ratio"]
        late = s["late_session_pac"]

        row = (
            f"{name:<25s} | "
            f"{_fmt_ci(pac['mean'], pac['ci_lower'], pac['ci_upper']):<32s} | "
            f"{_fmt_ci(stim['mean'], stim['ci_lower'], stim['ci_upper'], '.1f'):<32s} | "
            f"{_fmt_ci(eff['mean'], eff['ci_lower'], eff['ci_upper']):<32s} | "
            f"{_fmt_ci(late['mean'], late['ci_lower'], late['ci_upper']):<32s}"
        )
        print(row)

    print(sep)


def print_wilcoxon_table(
    wilcoxon_results: Dict[str, Any],
    metric_name: str = "pac_mean",
) -> None:
    """Print pairwise Wilcoxon p-values."""
    entries = wilcoxon_results.get(metric_name, [])
    if not entries:
        return

    print(f"\nPairwise Wilcoxon signed-rank tests ({metric_name}):")
    print(f"  {'Comparison':<50s} | {'W-stat':>10s} | {'p-value':>12s} | {'Hedge g':>10s}")
    print("  " + "-" * 90)

    for entry in entries:
        label = f"{entry['method_a']} vs {entry['method_b']}"
        p_str = f"{entry['p_value']:.6f}" if not np.isnan(entry["p_value"]) else "N/A"
        g_str = f"{entry['hedges_g']:.4f}" if not np.isnan(entry["hedges_g"]) else "N/A"
        w_str = f"{entry['statistic']:.1f}" if not np.isnan(entry["statistic"]) else "N/A"
        print(f"  {label:<50s} | {w_str:>10s} | {p_str:>12s} | {g_str:>10s}")


def print_tcn_vs_others(
    effect_sizes: Dict[str, Any],
) -> None:
    """Print Hedges' g for TCN-Predictive vs all other methods."""
    print("\nEffect sizes (Hedges' g): TCN-Predictive vs Other Methods")
    print(f"  {'Metric':<25s} | {'vs Fixed':>12s} | {'vs Reactive':>12s} | {'vs Oracle':>12s}")
    print("  " + "-" * 65)

    for metric in METRIC_FIELDS:
        entries = effect_sizes.get(metric, [])
        row_vals: Dict[str, float] = {}

        for e in entries:
            if "TCN-Predictive" in e["method_a"] or "TCN-Predictive" in e["method_b"]:
                # Normalize sign: positive = TCN better
                if "TCN-Predictive" == e["method_a"]:
                    other = e["method_b"]
                    g = e["hedges_g"]
                else:
                    other = e["method_a"]
                    g = -e["hedges_g"]
                row_vals[other] = g

        fixed_g = row_vals.get("Fixed Schedule", float("nan"))
        reactive_g = row_vals.get("Reactive Threshold", float("nan"))
        oracle_g = row_vals.get("Oracle", float("nan"))

        def _fmt_g(g: float) -> str:
            return f"{g:+.4f}" if not np.isnan(g) else "N/A"

        print(
            f"  {metric:<25s} | {_fmt_g(fixed_g):>12s} | "
            f"{_fmt_g(reactive_g):>12s} | {_fmt_g(oracle_g):>12s}"
        )


# ===================================================================
# JSON serialization
# ===================================================================


def _make_serializable(obj: Any) -> Any:
    """Recursively convert numpy types and dataclasses for JSON."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {str(k): _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_serializable(v) for v in obj]
    if isinstance(obj, TrialMetrics):
        return obj.to_dict()
    if isinstance(obj, float) and np.isnan(obj):
        return None
    if isinstance(obj, float) and np.isinf(obj):
        return None
    return obj


# ===================================================================
# Main entry point
# ===================================================================


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(
        description="TCN-Integrated Closed-Loop Simulation Validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python rigor/experiments/tcn_integrated_simulation.py \\\n"
            "    --checkpoint-path models/best_multiscale_tcn_lb20_hz1.pth \\\n"
            "    --data-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean\n"
        ),
    )
    p.add_argument(
        "--checkpoint-path",
        type=str,
        required=True,
        help="Path to trained TCN checkpoint (.pth file).",
    )
    p.add_argument(
        "--data-dir",
        type=str,
        required=True,
        help="Path to multiscale temporal dataset directory (contains scalers.npz).",
    )
    p.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).resolve().parent / "tcn_simulation_results"),
        help="Directory for output JSON file.",
    )
    p.add_argument(
        "--n-trials",
        type=int,
        default=50,
        help="Number of trials per method per condition (default: 50).",
    )
    p.add_argument(
        "--duration",
        type=int,
        default=600,
        help="Simulation duration in seconds per trial (default: 600).",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Base random seed for reproducibility (default: 42).",
    )
    p.add_argument(
        "--decline-threshold",
        type=float,
        default=-0.3,
        help="TCN delta_pac threshold for preemptive stimulation (default: -0.3).",
    )
    return p.parse_args()


def main() -> None:
    """Run the full TCN-integrated simulation validation."""
    args = parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    checkpoint_path = Path(args.checkpoint_path)
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    n_trials: int = args.n_trials
    duration_sec: int = args.duration
    base_seed: int = args.seed

    print("=" * 72)
    print("TCN-INTEGRATED CLOSED-LOOP SIMULATION VALIDATION")
    print("=" * 72)
    print(f"  Checkpoint:      {checkpoint_path}")
    print(f"  Data dir:        {data_dir}")
    print(f"  Output dir:      {output_dir}")
    print(f"  n_trials:        {n_trials}")
    print(f"  duration_sec:    {duration_sec}")
    print(f"  base_seed:       {base_seed}")
    print(f"  decline_thresh:  {args.decline_threshold}")

    # ------------------------------------------------------------------
    # Validate inputs
    # ------------------------------------------------------------------
    missing_files: List[str] = []
    if not checkpoint_path.exists():
        missing_files.append(f"Checkpoint: {checkpoint_path}")
    scalers_path = data_dir / "scalers.npz"
    if not scalers_path.exists():
        missing_files.append(f"Scalers: {scalers_path}")

    if missing_files:
        print("\nERROR: The following required files are missing:")
        for f in missing_files:
            print(f"  - {f}")
        print(
            "\nTo generate these files:\n"
            "  1. Build dataset: python temporal_multiscale/build_multiscale_dataset.py\n"
            "  2. Train model:   python temporal_multiscale/train_multiscale_tcn.py"
        )
        sys.exit(1)

    # ------------------------------------------------------------------
    # Load TCN forecaster
    # ------------------------------------------------------------------
    print("\nLoading TCN forecaster...")
    forecaster = RealtimePACForecaster(
        checkpoint_path=str(checkpoint_path),
        scalers_path=str(scalers_path),
        device="cpu",  # Simulation runs on CPU for reproducibility
    )
    print(f"  Lookback:    {forecaster.lookback}")
    print(f"  Feature dim: {forecaster.feature_dim}")

    # ------------------------------------------------------------------
    # Instantiate control methods
    # ------------------------------------------------------------------
    rng = np.random.default_rng(base_seed)
    np.random.seed(base_seed)

    methods: List[ControlMethodBase] = [
        FixedScheduleControl(stim_duration=40, rest_duration=20),
        ReactiveThresholdControl(window_size=30, threshold_std=0.5),
        TCNPredictiveControl(
            forecaster=forecaster,
            window_size=30,
            threshold_std=0.5,
            decline_threshold=args.decline_threshold,
            hold_time=5,
        ),
        OracleControl(pac_target=0.2),
    ]

    # Master results container
    all_output: Dict[str, Any] = {
        "meta": {
            "n_trials": n_trials,
            "duration_sec": duration_sec,
            "base_seed": base_seed,
            "methods": [m.name for m in methods],
            "checkpoint_path": str(checkpoint_path),
            "scalers_path": str(scalers_path),
            "decline_threshold": args.decline_threshold,
            "bootstrap_resamples": BOOTSTRAP_N_RESAMPLES,
            "bootstrap_ci_level": BOOTSTRAP_CI_LEVEL,
        },
    }

    t_start = time.time()

    # ------------------------------------------------------------------
    # 1. Standard EntrainmentSimulator (no fatigue)
    # ------------------------------------------------------------------
    logger.info("\n[1/3] Running standard EntrainmentSimulator trials...")
    print("\n[1/3] Standard EntrainmentSimulator...")
    std_sim_kwargs: Dict[str, Any] = {
        "tau_rise": 0.15,
        "tau_decay": 0.10,
        "pac_max": 0.3,
        "pac_min": 0.05,
        "noise_std": 0.02,
    }
    std_results = run_trial_batch(
        methods=methods,
        simulator_class=EntrainmentSimulator,
        simulator_kwargs=std_sim_kwargs,
        n_trials=n_trials,
        duration_sec=duration_sec,
        base_seed=base_seed,
        label="Standard",
    )
    std_statistics = compute_all_statistics(std_results, rng)

    all_output["standard_simulator"] = {
        "simulator": "EntrainmentSimulator",
        "simulator_kwargs": std_sim_kwargs,
        "trial_data": {
            name: [tm.to_dict() for tm in trials]
            for name, trials in std_results.items()
        },
        "statistics": std_statistics,
    }

    print_summary_table(
        std_statistics["summary_stats"],
        "Standard EntrainmentSimulator Results",
    )
    for metric in ["pac_mean", "efficiency_ratio"]:
        print_wilcoxon_table(std_statistics["wilcoxon"], metric)
    print_tcn_vs_others(std_statistics["effect_sizes"])

    # ------------------------------------------------------------------
    # 2. FatigueAwareSimulator
    # ------------------------------------------------------------------
    logger.info("\n[2/3] Running FatigueAwareSimulator trials...")
    print("\n[2/3] FatigueAwareSimulator...")
    fat_sim_kwargs: Dict[str, Any] = {
        "tau_rise": 0.15,
        "tau_decay": 0.10,
        "pac_max": 0.3,
        "pac_min": 0.05,
        "noise_std": 0.02,
        "fatigue_rate": 0.008,
        "recovery_rate": 0.03,
        "max_fatigue": 0.7,
    }
    fat_results = run_trial_batch(
        methods=methods,
        simulator_class=FatigueAwareSimulator,
        simulator_kwargs=fat_sim_kwargs,
        n_trials=n_trials,
        duration_sec=duration_sec,
        base_seed=base_seed + 50000,
        label="Fatigue",
    )
    fat_statistics = compute_all_statistics(fat_results, rng)

    all_output["fatigue_simulator"] = {
        "simulator": "FatigueAwareSimulator",
        "simulator_kwargs": fat_sim_kwargs,
        "trial_data": {
            name: [tm.to_dict() for tm in trials]
            for name, trials in fat_results.items()
        },
        "statistics": fat_statistics,
    }

    print_summary_table(
        fat_statistics["summary_stats"],
        "FatigueAwareSimulator Results",
    )
    for metric in ["pac_mean", "efficiency_ratio"]:
        print_wilcoxon_table(fat_statistics["wilcoxon"], metric)
    print_tcn_vs_others(fat_statistics["effect_sizes"])

    # ------------------------------------------------------------------
    # 3. Population-diverse simulation
    # ------------------------------------------------------------------
    logger.info("\n[3/3] Running population-diverse simulation...")
    print("\n[3/3] Population-Diverse Simulation...")
    pop_results = run_population_diverse(
        methods=methods,
        n_subjects=n_trials,
        duration_sec=duration_sec,
        base_seed=base_seed + 100000,
    )
    pop_statistics = compute_all_statistics(pop_results, rng)

    all_output["population_diverse"] = {
        "simulator": "EntrainmentSimulator (randomized parameters)",
        "n_subjects": n_trials,
        "trial_data": {
            name: [tm.to_dict() for tm in trials]
            for name, trials in pop_results.items()
        },
        "statistics": pop_statistics,
    }

    print_summary_table(
        pop_statistics["summary_stats"],
        "Population-Diverse Simulation Results",
    )
    for metric in ["pac_mean", "efficiency_ratio"]:
        print_wilcoxon_table(pop_statistics["wilcoxon"], metric)
    print_tcn_vs_others(pop_statistics["effect_sizes"])

    # ------------------------------------------------------------------
    # Final timing and save
    # ------------------------------------------------------------------
    elapsed = time.time() - t_start
    all_output["meta"]["elapsed_seconds"] = round(elapsed, 2)

    output_path = output_dir / "tcn_integrated_simulation_results.json"
    serializable = _make_serializable(all_output)
    with open(output_path, "w") as f:
        json.dump(serializable, f, indent=2)

    # ------------------------------------------------------------------
    # Consolidated summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("CONSOLIDATED SUMMARY")
    print("=" * 72)
    print(f"Trials per method per condition: {n_trials}")
    print(f"Simulation duration: {duration_sec}s")
    print(f"Random seed: {base_seed}")
    print(f"Bootstrap resamples: {BOOTSTRAP_N_RESAMPLES}")
    print(f"Confidence level: {BOOTSTRAP_CI_LEVEL * 100:.0f}%")
    print(f"Elapsed time: {elapsed:.1f}s")
    print(f"Results: {output_path}")

    # Cross-condition summary for TCN-Predictive vs other methods
    print("\nTCN-Predictive vs Fixed Schedule -- Summary Across Conditions:")
    print(
        f"  {'Condition':<30s} | {'PAC Mean Hedge g':>18s} | "
        f"{'Efficiency Hedge g':>20s}"
    )
    print("  " + "-" * 75)

    for condition_key, condition_label in [
        ("standard_simulator", "Standard (no fatigue)"),
        ("fatigue_simulator", "Fatigue (default)"),
        ("population_diverse", "Population-diverse"),
    ]:
        cond = all_output[condition_key]["statistics"]["effect_sizes"]
        pac_g = float("nan")
        eff_g = float("nan")

        for e in cond.get("pac_mean", []):
            if "TCN-Predictive" in e["method_a"] and "Fixed" in e["method_b"]:
                pac_g = e["hedges_g"]
            elif "Fixed" in e["method_a"] and "TCN-Predictive" in e["method_b"]:
                pac_g = -e["hedges_g"]

        for e in cond.get("efficiency_ratio", []):
            if "TCN-Predictive" in e["method_a"] and "Fixed" in e["method_b"]:
                eff_g = e["hedges_g"]
            elif "Fixed" in e["method_a"] and "TCN-Predictive" in e["method_b"]:
                eff_g = -e["hedges_g"]

        pac_str = f"{pac_g:+.4f}" if not np.isnan(pac_g) else "N/A"
        eff_str = f"{eff_g:+.4f}" if not np.isnan(eff_g) else "N/A"
        print(f"  {condition_label:<30s} | {pac_str:>18s} | {eff_str:>20s}")

    # TCN-Predictive vs linear-trend Predictive (cross-reference)
    print(
        "\nNote: Compare these results against rigor/rigorous_validation.py"
    )
    print(
        "to assess whether the TCN-based predictor improves over the"
    )
    print(
        "linear-trend-based Predictive Look-Ahead controller."
    )

    print("\n" + "=" * 72)
    logger.info("Results saved to %s", output_path)


if __name__ == "__main__":
    main()
