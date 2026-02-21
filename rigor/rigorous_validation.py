"""
Rigorous Statistical Validation of Closed-Loop 40Hz Entrainment Control Strategies

Fixes all statistical issues present in the original src/validation.py:
  1. Proper trial counts (n >= 50) for statistical power
  2. Both EntrainmentSimulator and FatigueAwareSimulator
  3. Correct accumulation of per-trial metrics (no overwrite)
  4. ANOVA on arrays of trial metrics, not single scalars
  5. Cohen's d / Hedges' g from within-group variance with real trial data
  6. Wilcoxon signed-rank tests for pairwise nonparametric comparisons
  7. Bootstrap 95% confidence intervals (1000 resamples)
  8. Reproducible random seeds per trial batch
  9. Population-diverse simulator (randomized tau/pac parameters per subject)
  10. Effect sizes (Hedges' g) for all pairwise comparisons
  11. Detailed JSON output with trial-level data and all statistics
  12. Fatigue severity sweep across multiple fatigue_rate values

Usage:
    python rigor/rigorous_validation.py --n-trials 50 --duration 600 --seed 42

Author: Amaar Chughtai
Date: February 2026
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass, field, asdict
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats

# ---------------------------------------------------------------------------
# Path manipulation so we can import from src/
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SRC_DIR = _PROJECT_ROOT / "src"
sys.path.insert(0, str(_SRC_DIR))

from simulator import EntrainmentSimulator, FatigueAwareSimulator, StimAction  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BOOTSTRAP_N_RESAMPLES: int = 1000
BOOTSTRAP_CI_LEVEL: float = 0.95
FATIGUE_RATES_SWEEP: List[float] = [0.0, 0.004, 0.008, 0.015, 0.025, 0.040]


# ===================================================================
# Control methods (self-contained, no external model dependency)
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
    """Fixed 40 s ON + 20 s OFF schedule (control condition)."""

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


class PredictiveLookAheadControl(ControlMethodBase):
    """Trend-based predictive look-ahead with hysteresis.

    Uses linear regression over a short recent window to estimate the PAC
    slope.  If the trend predicts decline, stimulation is applied proactively.
    This mirrors the simulation-level PredictiveLookAheadControl from
    src/validation.py (not the full TCN pipeline).
    """

    def __init__(
        self,
        window_size: int = 30,
        threshold_std: float = 0.5,
        decline_threshold: float = -0.3,
        hold_time: int = 5,
    ) -> None:
        super().__init__("Predictive Look-Ahead")
        self.window_size = window_size
        self.threshold_std = threshold_std
        self.decline_threshold = decline_threshold
        self.hold_time = hold_time
        self.pac_buffer: List[float] = []
        self.current_state: int = int(StimAction.REST)
        self.time_in_state: int = 0

    def reset(self) -> None:
        self.pac_buffer = []
        self.current_state = int(StimAction.REST)
        self.time_in_state = 0

    def _pac_trend(self, k: int = 5) -> float:
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

    def step(self, pac_current: float) -> int:
        self.pac_buffer.append(pac_current)
        if len(self.pac_buffer) > self.window_size:
            self.pac_buffer.pop(0)

        trend = self._pac_trend()

        if len(self.pac_buffer) < max(5, self.window_size // 2):
            return int(StimAction.REST)

        baseline_mean = float(np.mean(self.pac_buffer))
        baseline_std = float(np.std(self.pac_buffer)) + 1e-8
        z_score = (pac_current - baseline_mean) / baseline_std

        desired_state: Optional[int] = None

        if trend < self.decline_threshold * baseline_std:
            desired_state = int(StimAction.STIMULATE)
        elif trend > abs(self.decline_threshold) * baseline_std:
            desired_state = int(StimAction.REST)
        elif z_score < -self.threshold_std:
            desired_state = int(StimAction.STIMULATE)
        elif z_score > self.threshold_std:
            desired_state = int(StimAction.REST)

        if desired_state is None:
            desired_state = self.current_state

        # Hysteresis
        if desired_state != self.current_state:
            if self.time_in_state >= self.hold_time:
                self.current_state = desired_state
                self.time_in_state = 0
        else:
            self.time_in_state += 1

        return self.current_state


class OracleControl(ControlMethodBase):
    """Oracle with perfect information (upper bound)."""

    def __init__(self, pac_target: float = 0.2) -> None:
        super().__init__("Oracle")
        self.pac_target = pac_target

    def step(self, pac_current: float) -> int:
        return int(StimAction.STIMULATE) if pac_current < self.pac_target else int(StimAction.REST)


# ===================================================================
# Per-trial metrics container
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
        (point_estimate, ci_lower, ci_upper)
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

    Uses pooled standard deviation with Bessel correction and
    the standard Hedge's correction factor J.

    Args:
        group_a: Observations for group A.
        group_b: Observations for group B.

    Returns:
        Effect size (Hedges' g). Positive means group_a > group_b.
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

    The Wilcoxon signed-rank test is a nonparametric paired test that is
    appropriate even for small samples and non-normal distributions.
    When sample sizes differ, the minimum common length is used.

    Args:
        data_by_method: {method_name: 1-D array of trial metric values}.
        metric_name: Name of the metric being compared.

    Returns:
        List of result dicts, one per pair.
    """
    results: List[Dict[str, Any]] = []
    method_names = sorted(data_by_method.keys())

    for m_a, m_b in combinations(method_names, 2):
        a = data_by_method[m_a]
        b = data_by_method[m_b]
        n_common = min(len(a), len(b))
        if n_common < 6:
            # Wilcoxon needs at least ~6 paired obs for meaningful results
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

        # If all differences are zero, Wilcoxon will raise
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
        simulator_kwargs: Keyword arguments for the simulator constructor.
        duration_sec: Duration in seconds.
        fs: Sampling frequency (decisions per second).
        late_session_sec: Number of trailing seconds for late-session PAC.

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
        efficiency_ratio = pac_mean  # All rest, efficiency = pac_mean / 0 -> use raw PAC

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
    """Run n_trials for each method, accumulating all results.

    Each trial uses a distinct but reproducible random seed.

    Args:
        methods: List of control method instances.
        simulator_class: Simulator class to use.
        simulator_kwargs: Base kwargs for the simulator.
        n_trials: Number of trials per method.
        duration_sec: Duration per trial in seconds.
        base_seed: Base random seed (trial i uses base_seed + i).
        fs: Decision frequency in Hz.
        late_session_sec: Seconds for late-session metric.
        label: Descriptive label for logging.

    Returns:
        {method.name: [TrialMetrics, ...]} with n_trials entries per method.
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


# ===================================================================
# Population-diverse simulation
# ===================================================================

def generate_subject_parameters(
    n_subjects: int,
    rng: np.random.Generator,
) -> List[Dict[str, Any]]:
    """Generate randomized simulator parameters for diverse subjects.

    Varies tau_rise, tau_decay, pac_max, noise_std to model inter-individual
    variability observed across the 35 subjects in ds005048.

    Args:
        n_subjects: Number of virtual subjects to generate.
        rng: Numpy random generator.

    Returns:
        List of simulator_kwargs dicts, one per subject.
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
        base_seed: Seed for parameter generation and trials.
        fs: Decision frequency.
        late_session_sec: Seconds for late-session metric.

    Returns:
        {method.name: [TrialMetrics, ...]} with n_subjects entries per method.
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
# Fatigue severity sweep
# ===================================================================

def run_fatigue_sweep(
    methods: List[ControlMethodBase],
    fatigue_rates: List[float],
    n_trials: int,
    duration_sec: int,
    base_seed: int,
    fs: float = 1.0,
    late_session_sec: int = 60,
) -> Dict[float, Dict[str, List[TrialMetrics]]]:
    """Run trial batches at each fatigue rate.

    Args:
        methods: Control methods.
        fatigue_rates: List of fatigue_rate values to sweep.
        n_trials: Trials per method per fatigue level.
        duration_sec: Duration per trial.
        base_seed: Base random seed.
        fs: Decision frequency.
        late_session_sec: Seconds for late-session metric.

    Returns:
        {fatigue_rate: {method.name: [TrialMetrics, ...]}}
    """
    sweep_results: Dict[float, Dict[str, List[TrialMetrics]]] = {}

    for fr in fatigue_rates:
        logger.info("  Fatigue rate = %.4f", fr)
        sim_kwargs: Dict[str, Any] = {
            "tau_rise": 0.15,
            "tau_decay": 0.10,
            "pac_max": 0.3,
            "pac_min": 0.05,
            "noise_std": 0.02,
            "fatigue_rate": fr,
            "recovery_rate": 0.03,
            "max_fatigue": 0.7,
        }
        batch = run_trial_batch(
            methods=methods,
            simulator_class=FatigueAwareSimulator,
            simulator_kwargs=sim_kwargs,
            n_trials=n_trials,
            duration_sec=duration_sec,
            base_seed=base_seed + int(fr * 100000),
            fs=fs,
            late_session_sec=late_session_sec,
            label=f"Fatigue={fr:.3f}",
        )
        sweep_results[fr] = batch

    return sweep_results


# ===================================================================
# Analysis and reporting
# ===================================================================

METRIC_FIELDS = ["pac_mean", "pac_std", "stimulation_pct", "efficiency_ratio", "late_session_pac"]


def extract_metric_array(
    trial_list: List[TrialMetrics],
    metric_name: str,
) -> np.ndarray:
    """Extract a single metric from a list of TrialMetrics into an array."""
    return np.array([getattr(tm, metric_name) for tm in trial_list], dtype=np.float64)


def compute_summary_stats(
    results: Dict[str, List[TrialMetrics]],
    rng: np.random.Generator,
) -> Dict[str, Dict[str, Any]]:
    """Compute per-method summary statistics with bootstrap CIs.

    Args:
        results: {method_name: [TrialMetrics, ...]}.
        rng: Random generator for bootstrap reproducibility.

    Returns:
        {method_name: {metric_name: {mean, ci_lower, ci_upper, std}, ...}}
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


def compute_anova(
    results: Dict[str, List[TrialMetrics]],
    metric_name: str,
) -> Dict[str, Any]:
    """Run one-way ANOVA on a metric across all methods.

    Passes full arrays (not scalars) to scipy.stats.f_oneway.

    Args:
        results: {method_name: [TrialMetrics, ...]}.
        metric_name: Which metric to test.

    Returns:
        {f_statistic, p_value, method_means}
    """
    groups = []
    method_means: Dict[str, float] = {}
    for method_name in sorted(results.keys()):
        arr = extract_metric_array(results[method_name], metric_name)
        groups.append(arr)
        method_means[method_name] = float(np.mean(arr))

    if len(groups) < 2 or any(len(g) < 2 for g in groups):
        return {"f_statistic": float("nan"), "p_value": float("nan"), "method_means": method_means}

    f_stat, p_val = stats.f_oneway(*groups)
    return {
        "f_statistic": float(f_stat),
        "p_value": float(p_val),
        "method_means": method_means,
    }


def compute_all_statistics(
    results: Dict[str, List[TrialMetrics]],
    rng: np.random.Generator,
) -> Dict[str, Any]:
    """Compute full statistical analysis suite.

    Args:
        results: {method_name: [TrialMetrics, ...]}.
        rng: Random generator.

    Returns:
        Dictionary with summary_stats, anova, wilcoxon, and effect_sizes.
    """
    output: Dict[str, Any] = {}

    # Summary statistics with CIs
    output["summary_stats"] = compute_summary_stats(results, rng)

    # ANOVA for each metric
    anova_results: Dict[str, Any] = {}
    for metric in METRIC_FIELDS:
        anova_results[metric] = compute_anova(results, metric)
    output["anova"] = anova_results

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
    """Print a nicely formatted summary table to stdout."""
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


def print_effect_sizes_predictive_vs_fixed(
    effect_sizes: Dict[str, Any],
) -> None:
    """Print Hedges' g for Predictive vs Fixed across all metrics."""
    print("\nEffect sizes (Hedges' g): Predictive Look-Ahead vs Fixed Schedule")
    print(f"  {'Metric':<25s} | {'Hedge g':>10s} | {'Interpretation':<20s}")
    print("  " + "-" * 60)

    for metric in METRIC_FIELDS:
        entries = effect_sizes.get(metric, [])
        for e in entries:
            if (
                ("Fixed" in e["method_a"] and "Predictive" in e["method_b"])
                or ("Predictive" in e["method_a"] and "Fixed" in e["method_b"])
            ):
                g = e["hedges_g"]
                # Sign convention: positive = first method > second
                if "Fixed" in e["method_a"]:
                    g = -g  # Flip so positive = Predictive > Fixed

                abs_g = abs(g)
                if np.isnan(abs_g):
                    interp = "N/A"
                elif abs_g < 0.2:
                    interp = "negligible"
                elif abs_g < 0.5:
                    interp = "small"
                elif abs_g < 0.8:
                    interp = "medium"
                else:
                    interp = "large"

                print(f"  {metric:<25s} | {g:>10.4f} | {interp:<20s}")
                break


def print_fatigue_sweep_table(
    sweep_stats: Dict[float, Dict[str, Dict[str, Any]]],
) -> None:
    """Print fatigue sweep efficiency comparison."""
    print("\nFatigue Severity Sweep: Efficiency Ratio (PAC Mean / Stim Fraction)")
    print(
        f"  {'Fatigue Rate':<15s} | {'Fixed Sched':>14s} | {'Reactive':>14s} | "
        f"{'Predictive':>14s} | {'Oracle':>14s} | {'Pred/Fixed Gain':>16s}"
    )
    print("  " + "-" * 100)

    for fr in sorted(sweep_stats.keys()):
        stats_at_fr = sweep_stats[fr]
        row_vals: Dict[str, float] = {}
        for method_name, mstats in stats_at_fr.items():
            eff = mstats.get("efficiency_ratio", {}).get("mean", float("nan"))
            row_vals[method_name] = eff

        fixed_eff = row_vals.get("Fixed Schedule", float("nan"))
        reactive_eff = row_vals.get("Reactive Threshold", float("nan"))
        predictive_eff = row_vals.get("Predictive Look-Ahead", float("nan"))
        oracle_eff = row_vals.get("Oracle", float("nan"))

        if fixed_eff > 0 and not np.isnan(fixed_eff) and not np.isnan(predictive_eff):
            gain_pct = 100.0 * (predictive_eff - fixed_eff) / fixed_eff
            gain_str = f"{gain_pct:+.1f}%"
        else:
            gain_str = "N/A"

        print(
            f"  {fr:<15.4f} | {fixed_eff:>14.4f} | {reactive_eff:>14.4f} | "
            f"{predictive_eff:>14.4f} | {oracle_eff:>14.4f} | {gain_str:>16s}"
        )


# ===================================================================
# JSON serialization helper
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

def main() -> None:
    """Run the full rigorous validation pipeline."""

    parser = argparse.ArgumentParser(
        description="Rigorous statistical validation of closed-loop control strategies",
    )
    parser.add_argument(
        "--n-trials",
        type=int,
        default=50,
        help="Number of trials per method per condition (min 50 recommended, 100 preferred)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=600,
        help="Simulation duration in seconds per trial",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Base random seed for reproducibility",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(_PROJECT_ROOT / "rigor" / "rigorous_validation_results.json"),
        help="Path for output JSON file",
    )
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    n_trials: int = args.n_trials
    duration_sec: int = args.duration
    base_seed: int = args.seed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 72)
    logger.info("RIGOROUS VALIDATION OF CLOSED-LOOP CONTROL STRATEGIES")
    logger.info("=" * 72)
    logger.info("  n_trials      = %d", n_trials)
    logger.info("  duration_sec  = %d", duration_sec)
    logger.info("  base_seed     = %d", base_seed)
    logger.info("  output_path   = %s", output_path)
    logger.info("=" * 72)

    rng = np.random.default_rng(base_seed)

    # Set global seed for initial determinism
    np.random.seed(base_seed)

    # Instantiate control methods
    methods: List[ControlMethodBase] = [
        FixedScheduleControl(stim_duration=40, rest_duration=20),
        ReactiveThresholdControl(window_size=30, threshold_std=0.5),
        PredictiveLookAheadControl(
            window_size=30,
            threshold_std=0.5,
            decline_threshold=-0.3,
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
            "bootstrap_resamples": BOOTSTRAP_N_RESAMPLES,
            "bootstrap_ci_level": BOOTSTRAP_CI_LEVEL,
        },
    }

    t_start = time.time()

    # ------------------------------------------------------------------
    # 1. Standard EntrainmentSimulator (no fatigue)
    # ------------------------------------------------------------------
    logger.info("\n[1/4] Running standard EntrainmentSimulator trials...")
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

    print_summary_table(std_statistics["summary_stats"], "Standard EntrainmentSimulator Results")
    for metric in ["pac_mean", "efficiency_ratio"]:
        print_wilcoxon_table(std_statistics["wilcoxon"], metric)
    print_effect_sizes_predictive_vs_fixed(std_statistics["effect_sizes"])

    # ------------------------------------------------------------------
    # 2. FatigueAwareSimulator (default fatigue)
    # ------------------------------------------------------------------
    logger.info("\n[2/4] Running FatigueAwareSimulator trials...")
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

    print_summary_table(fat_statistics["summary_stats"], "FatigueAwareSimulator Results")
    for metric in ["pac_mean", "efficiency_ratio"]:
        print_wilcoxon_table(fat_statistics["wilcoxon"], metric)
    print_effect_sizes_predictive_vs_fixed(fat_statistics["effect_sizes"])

    # ------------------------------------------------------------------
    # 3. Population-diverse simulation
    # ------------------------------------------------------------------
    logger.info("\n[3/4] Running population-diverse simulation...")
    pop_results = run_population_diverse(
        methods=methods,
        n_subjects=n_trials,  # One trial per virtual subject
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

    print_summary_table(pop_statistics["summary_stats"], "Population-Diverse Simulation Results")
    for metric in ["pac_mean", "efficiency_ratio"]:
        print_wilcoxon_table(pop_statistics["wilcoxon"], metric)

    # ------------------------------------------------------------------
    # 4. Fatigue severity sweep
    # ------------------------------------------------------------------
    logger.info("\n[4/4] Running fatigue severity sweep...")
    sweep_results = run_fatigue_sweep(
        methods=methods,
        fatigue_rates=FATIGUE_RATES_SWEEP,
        n_trials=n_trials,
        duration_sec=duration_sec,
        base_seed=base_seed + 200000,
    )

    # Compute stats at each fatigue level
    sweep_stats: Dict[float, Dict[str, Dict[str, Any]]] = {}
    sweep_output: Dict[str, Any] = {}
    for fr, fr_results in sweep_results.items():
        fr_statistics = compute_all_statistics(fr_results, rng)
        sweep_stats[fr] = fr_statistics["summary_stats"]
        sweep_output[str(fr)] = {
            "fatigue_rate": fr,
            "trial_data": {
                name: [tm.to_dict() for tm in trials]
                for name, trials in fr_results.items()
            },
            "statistics": fr_statistics,
        }

    all_output["fatigue_sweep"] = {
        "fatigue_rates": FATIGUE_RATES_SWEEP,
        "levels": sweep_output,
    }

    print_fatigue_sweep_table(sweep_stats)

    # ------------------------------------------------------------------
    # Final timing and save
    # ------------------------------------------------------------------
    elapsed = time.time() - t_start
    all_output["meta"]["elapsed_seconds"] = round(elapsed, 2)

    logger.info("\nTotal elapsed time: %.1f seconds", elapsed)
    logger.info("Saving results to %s", output_path)

    serializable = _make_serializable(all_output)
    with open(output_path, "w") as f:
        json.dump(serializable, f, indent=2)

    logger.info("Done. Results saved to %s", output_path)

    # ------------------------------------------------------------------
    # Final consolidated summary
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

    # Quick cross-condition summary for Predictive vs Fixed
    print("\nPredictive Look-Ahead vs Fixed Schedule -- Summary Across Conditions:")
    print(f"  {'Condition':<30s} | {'PAC Mean Hedge g':>18s} | {'Efficiency Hedge g':>20s}")
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
            if "Fixed" in e["method_a"] and "Predictive" in e["method_b"]:
                pac_g = -e["hedges_g"]  # Flip: positive = Predictive > Fixed
            elif "Predictive" in e["method_a"] and "Fixed" in e["method_b"]:
                pac_g = e["hedges_g"]
        for e in cond.get("efficiency_ratio", []):
            if "Fixed" in e["method_a"] and "Predictive" in e["method_b"]:
                eff_g = -e["hedges_g"]
            elif "Predictive" in e["method_a"] and "Fixed" in e["method_b"]:
                eff_g = e["hedges_g"]

        pac_str = f"{pac_g:+.4f}" if not np.isnan(pac_g) else "N/A"
        eff_str = f"{eff_g:+.4f}" if not np.isnan(eff_g) else "N/A"
        print(f"  {condition_label:<30s} | {pac_str:>18s} | {eff_str:>20s}")

    print("\n" + "=" * 72)


if __name__ == "__main__":
    main()
