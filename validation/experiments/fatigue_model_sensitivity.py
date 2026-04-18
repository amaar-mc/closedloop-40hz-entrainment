"""
Fatigue Model Sensitivity Analysis for Closed-Loop 40Hz Entrainment

Addresses the critique: "the simulation's fatigue model was constructed to behave
in a way that favors adaptive scheduling."

Tests whether the adaptive scheduling advantage (Predictive Look-Ahead vs Fixed
Schedule) is robust across FOUR fundamentally different fatigue model assumptions:

  1. ExponentialDecay     -- Current model: responsiveness decays exponentially
                            with cumulative stim time, recovers during rest
  2. StepFunction         -- Responsiveness drops suddenly after N continuous
                            seconds of stimulation, recovers to 80% during rest
  3. HeterogeneousPopulation -- 50% of subjects have NO fatigue, 50% have HIGH
                            fatigue (rate=0.025), matching the real data's
                            49/51% habituation split
  4. SaturationModel      -- PAC ceiling decays over total session time
                            (synaptic adaptation), partial recovery during rest

For each fatigue model:
  - n=50 trials, 600 seconds each, seed=42
  - Compares Fixed Schedule vs Predictive Look-Ahead
  - Reports: mean efficiency, Wilcoxon p-value, Hedges' g, bootstrap 95% CI

Usage:
    python rigor/experiments/fatigue_model_sensitivity.py

Author: Amaar Chughtai
Date: February 2026
"""

from __future__ import annotations

import json
import logging
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_SRC_DIR = _PROJECT_ROOT / "src"
_RIGOR_DIR = _PROJECT_ROOT / "rigor"
sys.path.insert(0, str(_SRC_DIR))
sys.path.insert(0, str(_RIGOR_DIR))

from simulator import StimAction  # noqa: E402
from rigorous_validation import (  # noqa: E402
    ControlMethodBase,
    FixedScheduleControl,
    PredictiveLookAheadControl,
    TrialMetrics,
    bootstrap_ci,
    hedges_g,
    BOOTSTRAP_N_RESAMPLES,
    BOOTSTRAP_CI_LEVEL,
    _make_serializable,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
N_TRIALS: int = 50
DURATION_SEC: int = 600
BASE_SEED: int = 42
LATE_SESSION_SEC: int = 60
FS: float = 1.0  # 1 decision per second


# ===================================================================
# Fatigue Model Simulators
# ===================================================================

class ExponentialDecaySimulator:
    """Fatigue Model 1: Exponential Decay (current baseline model).

    Responsiveness decays exponentially with cumulative stimulation time.
    Fatigue accumulates as: f(t+1) = f(t) + rate * (max_fatigue - f(t))
    during stimulation, and recovers as: f(t+1) = f(t) - recovery * f(t)
    during rest. Effective rise rate is tau_rise * (1 - fatigue).

    This is functionally identical to the existing FatigueAwareSimulator
    from src/simulator.py, re-implemented here for self-containment.

    Args:
        tau_rise: Base time constant for PAC increase during stimulation.
        tau_decay: Time constant for PAC decrease during rest.
        pac_max: Maximum achievable PAC value.
        pac_min: Minimum PAC baseline.
        noise_std: Gaussian noise standard deviation.
        fatigue_rate: Rate of fatigue accumulation during stimulation.
        recovery_rate: Rate of fatigue recovery during rest.
        max_fatigue: Maximum fatigue level (caps effectiveness reduction).
    """

    name: str = "ExponentialDecay"

    def __init__(
        self,
        tau_rise: float = 0.15,
        tau_decay: float = 0.10,
        pac_max: float = 0.3,
        pac_min: float = 0.05,
        noise_std: float = 0.02,
        fatigue_rate: float = 0.008,
        recovery_rate: float = 0.03,
        max_fatigue: float = 0.7,
    ) -> None:
        self.tau_rise = tau_rise
        self.tau_decay = tau_decay
        self.pac_max = pac_max
        self.pac_min = pac_min
        self.noise_std = noise_std
        self.fatigue_rate = fatigue_rate
        self.recovery_rate = recovery_rate
        self.max_fatigue = max_fatigue

        self.pac: float = pac_min
        self.fatigue: float = 0.0

    def step(self, action: int) -> float:
        """Simulate one time step with exponential fatigue dynamics."""
        if action == StimAction.STIMULATE:
            self.fatigue += self.fatigue_rate * (self.max_fatigue - self.fatigue)
            effectiveness = 1.0 - self.fatigue
            effective_tau = self.tau_rise * effectiveness
            pac_new = self.pac + effective_tau * (self.pac_max - self.pac)
        else:
            self.fatigue -= self.recovery_rate * self.fatigue
            self.fatigue = max(0.0, self.fatigue)
            pac_new = self.pac + self.tau_decay * (self.pac_min - self.pac)

        pac_new += np.random.normal(0, self.noise_std)
        self.pac = float(np.clip(pac_new, 0.0, 1.0))
        return self.pac

    def get_description(self) -> str:
        """Return human-readable model description."""
        return (
            f"Exponential decay: fatigue_rate={self.fatigue_rate}, "
            f"recovery_rate={self.recovery_rate}, max_fatigue={self.max_fatigue}"
        )


class StepFunctionSimulator:
    """Fatigue Model 2: Step Function (sudden drop after continuous stim).

    Responsiveness is full (1.0) until the subject has been stimulated
    continuously for `threshold_sec` seconds, at which point effectiveness
    drops to `drop_effectiveness` (e.g., 0.3). During rest, effectiveness
    recovers toward `rest_recovery_target` (e.g., 0.8) at a linear rate.

    This models neural habituation as a sudden threshold phenomenon rather
    than a gradual exponential process. Some neuroscience literature
    suggests thalamocortical neurons exhibit abrupt adaptation after
    sustained periodic stimulation.

    Args:
        tau_rise: Base time constant for PAC increase during stimulation.
        tau_decay: Time constant for PAC decrease during rest.
        pac_max: Maximum achievable PAC value.
        pac_min: Minimum PAC baseline.
        noise_std: Gaussian noise standard deviation.
        threshold_sec: Continuous stim seconds before sudden drop.
        drop_effectiveness: Effectiveness after threshold is crossed.
        rest_recovery_target: Maximum effectiveness recoverable during rest.
        recovery_rate_per_sec: Linear recovery rate per second of rest.
    """

    name: str = "StepFunction"

    def __init__(
        self,
        tau_rise: float = 0.15,
        tau_decay: float = 0.10,
        pac_max: float = 0.3,
        pac_min: float = 0.05,
        noise_std: float = 0.02,
        threshold_sec: float = 30.0,
        drop_effectiveness: float = 0.3,
        rest_recovery_target: float = 0.8,
        recovery_rate_per_sec: float = 0.02,
    ) -> None:
        self.tau_rise = tau_rise
        self.tau_decay = tau_decay
        self.pac_max = pac_max
        self.pac_min = pac_min
        self.noise_std = noise_std
        self.threshold_sec = threshold_sec
        self.drop_effectiveness = drop_effectiveness
        self.rest_recovery_target = rest_recovery_target
        self.recovery_rate_per_sec = recovery_rate_per_sec

        self.pac: float = pac_min
        self.continuous_stim_sec: float = 0.0
        self.effectiveness: float = 1.0
        self.fatigued: bool = False

    def step(self, action: int) -> float:
        """Simulate one time step with step-function fatigue."""
        if action == StimAction.STIMULATE:
            self.continuous_stim_sec += 1.0 / FS
            # Check if threshold crossed
            if self.continuous_stim_sec >= self.threshold_sec and not self.fatigued:
                self.fatigued = True
                self.effectiveness = self.drop_effectiveness
            effective_tau = self.tau_rise * self.effectiveness
            pac_new = self.pac + effective_tau * (self.pac_max - self.pac)
        else:
            # Rest resets the continuous stim counter
            self.continuous_stim_sec = 0.0
            # Recover effectiveness toward target
            if self.fatigued:
                self.effectiveness = min(
                    self.rest_recovery_target,
                    self.effectiveness + self.recovery_rate_per_sec * (1.0 / FS),
                )
                # Once recovered to target, allow re-triggering
                if self.effectiveness >= self.rest_recovery_target - 1e-6:
                    self.fatigued = False
            pac_new = self.pac + self.tau_decay * (self.pac_min - self.pac)

        pac_new += np.random.normal(0, self.noise_std)
        self.pac = float(np.clip(pac_new, 0.0, 1.0))
        return self.pac

    def get_description(self) -> str:
        """Return human-readable model description."""
        return (
            f"Step function: threshold={self.threshold_sec}s, "
            f"drop_to={self.drop_effectiveness}, "
            f"rest_recovery_target={self.rest_recovery_target}"
        )


class HeterogeneousPopulationSimulator:
    """Fatigue Model 3: Heterogeneous Population (bimodal fatigue).

    Models the real dataset observation that approximately 49% of subjects
    show NO habituation while 51% show significant habituation.
    Each simulated trial randomly assigns subjects to one of two groups:
      - No-fatigue group (50%): exponential dynamics with fatigue_rate=0
      - High-fatigue group (50%): exponential dynamics with fatigue_rate=0.025

    The `is_high_fatigue` flag is determined at construction time by the
    caller (the trial runner randomizes this).

    Args:
        tau_rise: Base time constant for PAC increase during stimulation.
        tau_decay: Time constant for PAC decrease during rest.
        pac_max: Maximum achievable PAC value.
        pac_min: Minimum PAC baseline.
        noise_std: Gaussian noise standard deviation.
        is_high_fatigue: Whether this subject is in the high-fatigue group.
        high_fatigue_rate: Fatigue rate for the high-fatigue group.
        recovery_rate: Recovery rate during rest (high-fatigue group only).
        max_fatigue: Maximum fatigue level for high-fatigue group.
    """

    name: str = "HeterogeneousPopulation"

    def __init__(
        self,
        tau_rise: float = 0.15,
        tau_decay: float = 0.10,
        pac_max: float = 0.3,
        pac_min: float = 0.05,
        noise_std: float = 0.02,
        is_high_fatigue: bool = False,
        high_fatigue_rate: float = 0.025,
        recovery_rate: float = 0.03,
        max_fatigue: float = 0.7,
    ) -> None:
        self.tau_rise = tau_rise
        self.tau_decay = tau_decay
        self.pac_max = pac_max
        self.pac_min = pac_min
        self.noise_std = noise_std
        self.is_high_fatigue = is_high_fatigue
        self.fatigue_rate = high_fatigue_rate if is_high_fatigue else 0.0
        self.recovery_rate = recovery_rate
        self.max_fatigue = max_fatigue

        self.pac: float = pac_min
        self.fatigue: float = 0.0

    def step(self, action: int) -> float:
        """Simulate one time step with bimodal fatigue profile."""
        if action == StimAction.STIMULATE:
            if self.fatigue_rate > 0:
                self.fatigue += self.fatigue_rate * (self.max_fatigue - self.fatigue)
            effectiveness = 1.0 - self.fatigue
            effective_tau = self.tau_rise * effectiveness
            pac_new = self.pac + effective_tau * (self.pac_max - self.pac)
        else:
            if self.fatigue_rate > 0:
                self.fatigue -= self.recovery_rate * self.fatigue
                self.fatigue = max(0.0, self.fatigue)
            pac_new = self.pac + self.tau_decay * (self.pac_min - self.pac)

        pac_new += np.random.normal(0, self.noise_std)
        self.pac = float(np.clip(pac_new, 0.0, 1.0))
        return self.pac

    def get_description(self) -> str:
        """Return human-readable model description."""
        group = "HIGH fatigue" if self.is_high_fatigue else "NO fatigue"
        return (
            f"Heterogeneous population ({group}): "
            f"fatigue_rate={self.fatigue_rate}, recovery_rate={self.recovery_rate}"
        )


class SaturationModelSimulator:
    """Fatigue Model 4: Saturation / Synaptic Adaptation.

    Models long-term synaptic adaptation where the effective PAC ceiling
    decreases asymptotically over total session time (regardless of whether
    stimulation is ON or OFF, but faster during stimulation). This
    represents progressive synaptic resource depletion.

    Ceiling dynamics:
      During stim:  ceiling(t+1) = ceiling(t) - depletion_rate * (ceiling(t) - floor)
      During rest:  ceiling(t+1) = ceiling(t) + restoration_rate * (pac_max - ceiling(t))

    PAC target is min(ceiling, pac_max) during stimulation.

    Args:
        tau_rise: Base time constant for PAC increase during stimulation.
        tau_decay: Time constant for PAC decrease during rest.
        pac_max: Maximum achievable PAC value (initial ceiling).
        pac_min: Minimum PAC baseline.
        noise_std: Gaussian noise standard deviation.
        depletion_rate: Rate at which the ceiling drops during stimulation.
        restoration_rate: Rate at which the ceiling recovers during rest.
        floor: Minimum possible ceiling value (irreducible adaptation).
    """

    name: str = "SaturationModel"

    def __init__(
        self,
        tau_rise: float = 0.15,
        tau_decay: float = 0.10,
        pac_max: float = 0.3,
        pac_min: float = 0.05,
        noise_std: float = 0.02,
        depletion_rate: float = 0.003,
        restoration_rate: float = 0.001,
        floor: float = 0.12,
    ) -> None:
        self.tau_rise = tau_rise
        self.tau_decay = tau_decay
        self.pac_max = pac_max
        self.pac_min = pac_min
        self.noise_std = noise_std
        self.depletion_rate = depletion_rate
        self.restoration_rate = restoration_rate
        self.floor = floor

        self.pac: float = pac_min
        self.ceiling: float = pac_max  # Current effective PAC ceiling

    def step(self, action: int) -> float:
        """Simulate one time step with saturation ceiling dynamics."""
        if action == StimAction.STIMULATE:
            # Ceiling depletes during stimulation
            self.ceiling -= self.depletion_rate * (self.ceiling - self.floor)
            effective_target = self.ceiling
            pac_new = self.pac + self.tau_rise * (effective_target - self.pac)
        else:
            # Ceiling partially restores during rest
            self.ceiling += self.restoration_rate * (self.pac_max - self.ceiling)
            pac_new = self.pac + self.tau_decay * (self.pac_min - self.pac)

        pac_new += np.random.normal(0, self.noise_std)
        self.pac = float(np.clip(pac_new, 0.0, 1.0))
        return self.pac

    def get_description(self) -> str:
        """Return human-readable model description."""
        return (
            f"Saturation model: depletion_rate={self.depletion_rate}, "
            f"restoration_rate={self.restoration_rate}, floor={self.floor}"
        )


# ===================================================================
# Trial runner (adapted from rigorous_validation.run_single_trial)
# ===================================================================

def run_single_trial(
    method: ControlMethodBase,
    simulator: Any,
    duration_sec: int,
    fs: float = 1.0,
    late_session_sec: int = LATE_SESSION_SEC,
) -> TrialMetrics:
    """Run one simulation trial and return metrics.

    Args:
        method: Control method instance (will be reset at start).
        simulator: A simulator instance with .pac attribute and .step() method.
        duration_sec: Duration in seconds.
        fs: Sampling frequency (decisions per second).
        late_session_sec: Trailing seconds for late-session PAC metric.

    Returns:
        TrialMetrics for this trial.
    """
    method.reset()

    n_steps = int(duration_sec * fs)
    pac_values = np.empty(n_steps, dtype=np.float64)
    actions = np.empty(n_steps, dtype=np.int32)

    for t in range(n_steps):
        pac = simulator.pac
        action = method.step(pac)
        simulator.step(action)
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


# ===================================================================
# Fatigue model configuration and factory
# ===================================================================

@dataclass
class FatigueModelConfig:
    """Configuration for a fatigue model experiment."""

    name: str
    description: str
    factory_kwargs: Dict[str, Any]


def create_simulator(model_name: str, trial_rng: np.random.Generator, **kwargs: Any) -> Any:
    """Factory function to create a simulator instance for a given fatigue model.

    Args:
        model_name: One of "ExponentialDecay", "StepFunction",
                    "HeterogeneousPopulation", "SaturationModel".
        trial_rng: Random generator for trial-specific randomization
                   (used by HeterogeneousPopulation to assign group).
        **kwargs: Additional keyword arguments passed to the simulator.

    Returns:
        A simulator instance.
    """
    if model_name == "ExponentialDecay":
        return ExponentialDecaySimulator(**kwargs)
    elif model_name == "StepFunction":
        return StepFunctionSimulator(**kwargs)
    elif model_name == "HeterogeneousPopulation":
        is_high = bool(trial_rng.random() < 0.5)
        return HeterogeneousPopulationSimulator(is_high_fatigue=is_high, **kwargs)
    elif model_name == "SaturationModel":
        return SaturationModelSimulator(**kwargs)
    else:
        raise ValueError(f"Unknown fatigue model: {model_name}")


# ===================================================================
# Experiment runner
# ===================================================================

@dataclass
class PairwiseResult:
    """Result of a pairwise comparison between two control methods."""

    fatigue_model: str
    metric: str
    method_a: str
    method_b: str
    mean_a: float
    mean_b: float
    ci_a: Tuple[float, float]
    ci_b: Tuple[float, float]
    difference: float
    relative_gain_pct: float
    wilcoxon_statistic: float
    wilcoxon_p_value: float
    hedges_g: float
    n_trials: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dict."""
        d = asdict(self)
        d["ci_a"] = list(d["ci_a"])
        d["ci_b"] = list(d["ci_b"])
        return d


def run_fatigue_model_experiment(
    model_name: str,
    model_kwargs: Dict[str, Any],
    n_trials: int,
    duration_sec: int,
    base_seed: int,
) -> Dict[str, Any]:
    """Run a full experiment for one fatigue model.

    Compares Fixed Schedule vs Predictive Look-Ahead across n_trials.

    Args:
        model_name: Fatigue model identifier.
        model_kwargs: Kwargs for the simulator factory.
        n_trials: Number of trials.
        duration_sec: Duration per trial in seconds.
        base_seed: Base seed for reproducibility.

    Returns:
        Dictionary containing trial data, summary stats, and pairwise tests.
    """
    methods = [
        FixedScheduleControl(stim_duration=40, rest_duration=20),
        PredictiveLookAheadControl(
            window_size=30,
            threshold_std=0.5,
            decline_threshold=-0.3,
            hold_time=5,
        ),
    ]

    results: Dict[str, List[TrialMetrics]] = {m.name: [] for m in methods}
    rng = np.random.default_rng(base_seed)

    for trial_idx in range(n_trials):
        trial_seed = base_seed + trial_idx
        trial_rng = np.random.default_rng(trial_seed)

        for method in methods:
            # Set numpy global seed for noise reproducibility
            np.random.seed(trial_seed)
            sim = create_simulator(model_name, trial_rng, **model_kwargs)
            metrics = run_single_trial(
                method=method,
                simulator=sim,
                duration_sec=duration_sec,
                fs=FS,
            )
            results[method.name].append(metrics)

        if (trial_idx + 1) % 25 == 0 or trial_idx == 0:
            logger.info(
                "  [%s] Trial %d/%d",
                model_name,
                trial_idx + 1,
                n_trials,
            )

    # Compute summary statistics
    metric_names = [
        "pac_mean", "pac_std", "stimulation_pct",
        "efficiency_ratio", "late_session_pac",
    ]

    summary_stats: Dict[str, Dict[str, Any]] = {}
    for method_name, trials in results.items():
        method_summary: Dict[str, Any] = {"n_trials": len(trials)}
        for metric in metric_names:
            arr = np.array(
                [getattr(tm, metric) for tm in trials], dtype=np.float64
            )
            point, ci_lo, ci_hi = bootstrap_ci(arr, np.mean, rng=rng)
            method_summary[metric] = {
                "mean": point,
                "std": float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
                "ci_lower": ci_lo,
                "ci_upper": ci_hi,
            }
        summary_stats[method_name] = method_summary

    # Pairwise comparison: Predictive vs Fixed
    pairwise_results: List[PairwiseResult] = []
    fixed_name = "Fixed Schedule"
    pred_name = "Predictive Look-Ahead"

    for metric in metric_names:
        arr_fixed = np.array(
            [getattr(tm, metric) for tm in results[fixed_name]], dtype=np.float64
        )
        arr_pred = np.array(
            [getattr(tm, metric) for tm in results[pred_name]], dtype=np.float64
        )

        # Wilcoxon signed-rank (paired)
        diffs = arr_pred - arr_fixed
        if np.all(np.abs(diffs) < 1e-15):
            w_stat, p_val = 0.0, 1.0
        else:
            w_stat, p_val = stats.wilcoxon(arr_pred, arr_fixed, alternative="two-sided")

        g = hedges_g(arr_pred, arr_fixed)

        mean_fixed = float(np.mean(arr_fixed))
        mean_pred = float(np.mean(arr_pred))
        diff = mean_pred - mean_fixed
        rel_gain = 100.0 * diff / abs(mean_fixed) if abs(mean_fixed) > 1e-12 else 0.0

        _, ci_lo_f, ci_hi_f = bootstrap_ci(arr_fixed, np.mean, rng=rng)
        _, ci_lo_p, ci_hi_p = bootstrap_ci(arr_pred, np.mean, rng=rng)

        pairwise_results.append(PairwiseResult(
            fatigue_model=model_name,
            metric=metric,
            method_a=pred_name,
            method_b=fixed_name,
            mean_a=mean_pred,
            mean_b=mean_fixed,
            ci_a=(ci_lo_p, ci_hi_p),
            ci_b=(ci_lo_f, ci_hi_f),
            difference=diff,
            relative_gain_pct=rel_gain,
            wilcoxon_statistic=float(w_stat),
            wilcoxon_p_value=float(p_val),
            hedges_g=float(g),
            n_trials=n_trials,
        ))

    return {
        "model_name": model_name,
        "model_kwargs": model_kwargs,
        "summary_stats": summary_stats,
        "pairwise_comparisons": [pr.to_dict() for pr in pairwise_results],
        "trial_data": {
            name: [tm.to_dict() for tm in trials]
            for name, trials in results.items()
        },
    }


# ===================================================================
# Summary table printer
# ===================================================================

def print_summary_table(all_results: Dict[str, Dict[str, Any]]) -> None:
    """Print a formatted summary table across all fatigue models.

    Args:
        all_results: {model_name: experiment_result_dict}
    """
    print("\n" + "=" * 120)
    print("FATIGUE MODEL SENSITIVITY ANALYSIS -- SUMMARY")
    print("=" * 120)
    print(
        f"{'Fatigue Model':<28s} | {'Metric':<18s} | "
        f"{'Predictive':>12s} | {'Fixed':>12s} | "
        f"{'Gain%':>8s} | {'Wilcoxon p':>12s} | "
        f"{'Hedges g':>10s} | {'Sig?':>5s}"
    )
    print("-" * 120)

    key_metrics = ["efficiency_ratio", "pac_mean", "late_session_pac"]

    for model_name in [
        "ExponentialDecay", "StepFunction",
        "HeterogeneousPopulation", "SaturationModel",
    ]:
        result = all_results.get(model_name)
        if result is None:
            continue

        for pw in result["pairwise_comparisons"]:
            if pw["metric"] not in key_metrics:
                continue

            p_val = pw["wilcoxon_p_value"]
            sig = "***" if p_val < 0.001 else (
                "**" if p_val < 0.01 else (
                    "*" if p_val < 0.05 else "ns"
                )
            )

            print(
                f"{model_name:<28s} | {pw['metric']:<18s} | "
                f"{pw['mean_a']:>12.4f} | {pw['mean_b']:>12.4f} | "
                f"{pw['relative_gain_pct']:>+7.1f}% | "
                f"{p_val:>12.6f} | "
                f"{pw['hedges_g']:>+10.4f} | {sig:>5s}"
            )

    print("-" * 120)


def print_robustness_verdict(all_results: Dict[str, Dict[str, Any]]) -> None:
    """Print a cross-model robustness assessment.

    Args:
        all_results: {model_name: experiment_result_dict}
    """
    print("\n" + "=" * 80)
    print("ROBUSTNESS VERDICT")
    print("=" * 80)

    model_order = [
        "ExponentialDecay", "StepFunction",
        "HeterogeneousPopulation", "SaturationModel",
    ]

    n_models = 0
    n_significant_efficiency = 0
    n_positive_gain = 0
    efficiency_gains: List[float] = []
    hedges_g_values: List[float] = []

    for model_name in model_order:
        result = all_results.get(model_name)
        if result is None:
            continue
        n_models += 1

        for pw in result["pairwise_comparisons"]:
            if pw["metric"] == "efficiency_ratio":
                efficiency_gains.append(pw["relative_gain_pct"])
                hedges_g_values.append(pw["hedges_g"])
                if pw["wilcoxon_p_value"] < 0.05:
                    n_significant_efficiency += 1
                if pw["relative_gain_pct"] > 0:
                    n_positive_gain += 1

    print(f"\nFatigue models tested:                          {n_models}")
    print(f"Models where Predictive has higher efficiency:   {n_positive_gain}/{n_models}")
    print(f"Models with p < 0.05 for efficiency:             {n_significant_efficiency}/{n_models}")

    if efficiency_gains:
        print(f"\nEfficiency gain (Predictive vs Fixed) across models:")
        for i, model_name in enumerate(model_order):
            if i < len(efficiency_gains):
                g_str = f"{efficiency_gains[i]:+.1f}%"
                hg_str = f"g={hedges_g_values[i]:+.3f}"
                print(f"  {model_name:<28s}  {g_str:>8s}  ({hg_str})")

        mean_gain = np.mean(efficiency_gains)
        print(f"\n  Mean efficiency gain across models: {mean_gain:+.1f}%")
        mean_g = np.mean(hedges_g_values)
        abs_g = abs(mean_g)
        if abs_g < 0.2:
            interp = "negligible"
        elif abs_g < 0.5:
            interp = "small"
        elif abs_g < 0.8:
            interp = "medium"
        else:
            interp = "large"
        print(f"  Mean Hedges' g across models:       {mean_g:+.3f} ({interp})")

    if n_significant_efficiency == n_models:
        conclusion = (
            "ROBUST: The adaptive scheduling advantage is statistically significant "
            f"(p < 0.05) under ALL {n_models} fatigue model assumptions tested."
        )
    elif n_significant_efficiency > n_models // 2:
        conclusion = (
            f"PARTIALLY ROBUST: The advantage is significant under "
            f"{n_significant_efficiency}/{n_models} models. The result depends "
            f"somewhat on fatigue model assumptions."
        )
    elif n_positive_gain == n_models:
        conclusion = (
            f"DIRECTIONALLY CONSISTENT: Predictive outperforms Fixed in all "
            f"{n_models} models, but significance is achieved in only "
            f"{n_significant_efficiency}/{n_models}."
        )
    else:
        conclusion = (
            f"NOT ROBUST: The advantage is significant under only "
            f"{n_significant_efficiency}/{n_models} models. The simulation "
            f"result IS sensitive to fatigue model assumptions."
        )

    print(f"\nConclusion: {conclusion}")
    print("=" * 80)


# ===================================================================
# Main entry point
# ===================================================================

def main() -> None:
    """Run the fatigue model sensitivity experiment."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("=" * 72)
    logger.info("FATIGUE MODEL SENSITIVITY ANALYSIS")
    logger.info("=" * 72)
    logger.info("  n_trials      = %d", N_TRIALS)
    logger.info("  duration_sec  = %d", DURATION_SEC)
    logger.info("  base_seed     = %d", BASE_SEED)
    logger.info("=" * 72)

    t_start = time.time()

    # Define fatigue model configurations
    fatigue_models: List[FatigueModelConfig] = [
        FatigueModelConfig(
            name="ExponentialDecay",
            description=(
                "Current model: responsiveness decays exponentially with "
                "cumulative stim time, recovers during rest"
            ),
            factory_kwargs={
                "fatigue_rate": 0.008,
                "recovery_rate": 0.03,
                "max_fatigue": 0.7,
            },
        ),
        FatigueModelConfig(
            name="StepFunction",
            description=(
                "Responsiveness drops suddenly after 30s continuous stimulation, "
                "recovers to 80% during rest"
            ),
            factory_kwargs={
                "threshold_sec": 30.0,
                "drop_effectiveness": 0.3,
                "rest_recovery_target": 0.8,
                "recovery_rate_per_sec": 0.02,
            },
        ),
        FatigueModelConfig(
            name="HeterogeneousPopulation",
            description=(
                "50% of subjects have NO fatigue, 50% have HIGH fatigue "
                "(rate=0.025), matching real data's 49/51% habituation split"
            ),
            factory_kwargs={
                "high_fatigue_rate": 0.025,
                "recovery_rate": 0.03,
                "max_fatigue": 0.7,
            },
        ),
        FatigueModelConfig(
            name="SaturationModel",
            description=(
                "PAC ceiling decays over session time (synaptic adaptation), "
                "partial recovery during rest"
            ),
            factory_kwargs={
                "depletion_rate": 0.003,
                "restoration_rate": 0.001,
                "floor": 0.12,
            },
        ),
    ]

    # Offset seeds per model to avoid correlated noise sequences
    seed_offsets = {
        "ExponentialDecay": 0,
        "StepFunction": 10000,
        "HeterogeneousPopulation": 20000,
        "SaturationModel": 30000,
    }

    all_results: Dict[str, Dict[str, Any]] = {}

    for i, config in enumerate(fatigue_models):
        logger.info(
            "\n[%d/%d] Running fatigue model: %s",
            i + 1,
            len(fatigue_models),
            config.name,
        )
        logger.info("  Description: %s", config.description)

        model_seed = BASE_SEED + seed_offsets.get(config.name, i * 10000)

        result = run_fatigue_model_experiment(
            model_name=config.name,
            model_kwargs=config.factory_kwargs,
            n_trials=N_TRIALS,
            duration_sec=DURATION_SEC,
            base_seed=model_seed,
        )
        result["description"] = config.description
        all_results[config.name] = result

    elapsed = time.time() - t_start

    # Print results
    print_summary_table(all_results)
    print_robustness_verdict(all_results)

    # Save results to JSON
    output_path = Path(__file__).resolve().parent / "fatigue_model_sensitivity_results.json"
    output_data = {
        "meta": {
            "experiment": "fatigue_model_sensitivity",
            "n_trials": N_TRIALS,
            "duration_sec": DURATION_SEC,
            "base_seed": BASE_SEED,
            "elapsed_seconds": round(elapsed, 2),
            "methods_compared": ["Fixed Schedule", "Predictive Look-Ahead"],
            "fatigue_models": [
                {"name": c.name, "description": c.description, "kwargs": c.factory_kwargs}
                for c in fatigue_models
            ],
        },
        "results": all_results,
    }

    serializable = _make_serializable(output_data)
    with open(output_path, "w") as f:
        json.dump(serializable, f, indent=2)

    logger.info("\nResults saved to %s", output_path)
    logger.info("Total elapsed time: %.1f seconds", elapsed)

    print(f"\nElapsed time: {elapsed:.1f}s")
    print(f"Results saved: {output_path}")


if __name__ == "__main__":
    main()
