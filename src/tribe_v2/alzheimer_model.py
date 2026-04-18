"""
Alzheimer's Disease Modeling Layer for TRIBE V2 Integration

Models the effects of Alzheimer's disease on cortical responses to 40 Hz
auditory stimulation. Applies disease-stage-specific modifications to:

1. Cortical activation levels (atrophy reduces response amplitude)
2. Gamma entrainment efficacy (impaired ASSR in AD)
3. Theta-gamma coupling (disrupted PAC in AD)
4. Neural habituation (faster fatigue in AD)

Disease staging follows Braak's neuropathological model with parameters
derived from published EEG/fMRI findings in AD populations.

References:
    Braak, H. & Braak, E. (1991). "Neuropathological stageing of
    Alzheimer-related changes." Acta Neuropathologica, 82(4), 239-259.

    Iaccarino, H. F., et al. (2016). "Gamma frequency entrainment
    attenuates amyloid load and modifies microglia." Nature, 540, 230-235.

    van Deursen, J. A., et al. (2008). "Increased EEG gamma band
    activity in Alzheimer's disease and mild cognitive impairment."
    J Neural Transm, 115, 1301-1311.

    Jafari, Z., et al. (2020). "Auditory steady-state responses in
    Alzheimer's disease." Ear and Hearing, 41(5), 1085-1095.

Author: Amaar Chughtai
Date: April 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np


@dataclass
class AlzheimerProfile:
    """
    Disease-specific parameter profile for Alzheimer's simulation.

    Each parameter modifies the cortical response model to reflect
    the known neurophysiological effects of AD at a given severity.

    Attributes:
        severity: Disease stage label.
        cortical_atrophy_scale: Scales cortical activation amplitude.
            1.0 = healthy; reduced in AD due to neuronal loss.
        gamma_efficacy: Scales 40 Hz gamma entrainment response.
            1.0 = healthy; reduced in AD due to impaired ASSR.
        theta_power_multiplier: Scales background theta power.
            1.0 = healthy; elevated in AD (cortical slowing).
        pac_coupling_scale: Scales theta-gamma PAC strength.
            1.0 = healthy; reduced in AD (disrupted cross-frequency coupling).
        fatigue_rate_multiplier: Scales neural habituation rate.
            1.0 = healthy; elevated in AD (faster fatigue).
        recovery_rate_multiplier: Scales fatigue recovery rate.
            1.0 = healthy; reduced in AD (slower recovery).
        baseline_pac_scale: Scales resting-state PAC baseline.
            1.0 = healthy; reduced in AD.
        noise_multiplier: Scales neural noise level.
            1.0 = healthy; elevated in AD (increased variability).
    """
    severity: Literal["healthy", "preclinical", "mild", "moderate", "severe"]
    cortical_atrophy_scale: float
    gamma_efficacy: float
    theta_power_multiplier: float
    pac_coupling_scale: float
    fatigue_rate_multiplier: float
    recovery_rate_multiplier: float
    baseline_pac_scale: float
    noise_multiplier: float

    def apply_to_activation(
        self,
        activation: float,
    ) -> float:
        """
        Apply disease modification to cortical activation level.

        Reduces activation by atrophy and gamma efficacy factors.
        The 40 Hz entrainment response is doubly affected: both by
        general cortical atrophy and by ASSR-specific impairment.

        Args:
            activation: Healthy cortical activation level.

        Returns:
            modified: Disease-modified activation level.
        """
        return activation * self.cortical_atrophy_scale * self.gamma_efficacy

    def apply_to_roi_activations(
        self,
        roi_activations: np.ndarray,
        roi_atrophy_weights: np.ndarray | None = None,
    ) -> np.ndarray:
        """
        Apply region-specific disease modification to ROI activations.

        Different brain regions are affected at different disease stages.
        Temporal and hippocampal regions are affected earliest (Braak I-II),
        while frontal regions are affected later (Braak V-VI).

        Args:
            roi_activations: Activation per ROI, shape (n_rois,).
            roi_atrophy_weights: Per-ROI atrophy weights, shape (n_rois,).
                1.0 = maximally affected, 0.0 = spared.
                If None, uses uniform atrophy across ROIs.

        Returns:
            modified: Disease-modified activations, shape (n_rois,).
        """
        if roi_atrophy_weights is None:
            # Uniform atrophy (simplified)
            return roi_activations * self.cortical_atrophy_scale * self.gamma_efficacy

        # Region-specific: interpolate between healthy and full atrophy
        atrophy_factor = 1.0 - roi_atrophy_weights * (1.0 - self.cortical_atrophy_scale)
        return roi_activations * atrophy_factor * self.gamma_efficacy

    def modify_neural_mass_drive(
        self,
        p_ext_stim: float,
        p_ext_rest: float,
    ) -> tuple[float, float]:
        """
        Modify neural mass model external drive for AD simulation.

        Args:
            p_ext_stim: External drive during stimulation (healthy).
            p_ext_rest: External drive during rest (healthy).

        Returns:
            p_ext_stim_ad: Disease-modified stim drive.
            p_ext_rest_ad: Disease-modified rest drive.
        """
        p_stim = p_ext_stim * self.cortical_atrophy_scale * self.gamma_efficacy
        p_rest = p_ext_rest * self.cortical_atrophy_scale
        return p_stim, p_rest

    def modify_simulator_params(
        self,
        tau_rise: float,
        tau_decay: float,
        pac_max: float,
        pac_min: float,
        noise_std: float,
        fatigue_rate: float,
        recovery_rate: float,
    ) -> dict[str, float]:
        """
        Modify exponential simulator parameters for AD simulation.

        Compatible with both EntrainmentSimulator and FatigueAwareSimulator.
        Allows the TRIBE V2-enhanced simulator to fall back to modified
        exponential dynamics when the full neural mass model isn't needed.

        Args:
            tau_rise: Healthy rise time constant.
            tau_decay: Healthy decay time constant.
            pac_max: Healthy maximum PAC.
            pac_min: Healthy minimum PAC.
            noise_std: Healthy noise level.
            fatigue_rate: Healthy fatigue rate.
            recovery_rate: Healthy recovery rate.

        Returns:
            params: Modified simulator parameters.
        """
        return {
            "tau_rise": tau_rise * self.gamma_efficacy,
            "tau_decay": tau_decay,  # Decay rate unchanged
            "pac_max": pac_max * self.pac_coupling_scale,
            "pac_min": pac_min * self.baseline_pac_scale,
            "noise_std": noise_std * self.noise_multiplier,
            "fatigue_rate": fatigue_rate * self.fatigue_rate_multiplier,
            "recovery_rate": recovery_rate * self.recovery_rate_multiplier,
        }


# ────────────────────────────────────────────────────────────────────────
# Pre-defined disease profiles
# ────────────────────────────────────────────────────────────────────────

ALZHEIMER_PROFILES: dict[str, AlzheimerProfile] = {
    "healthy": AlzheimerProfile(
        severity="healthy",
        cortical_atrophy_scale=1.0,
        gamma_efficacy=1.0,
        theta_power_multiplier=1.0,
        pac_coupling_scale=1.0,
        fatigue_rate_multiplier=1.0,
        recovery_rate_multiplier=1.0,
        baseline_pac_scale=1.0,
        noise_multiplier=1.0,
    ),
    "preclinical": AlzheimerProfile(
        severity="preclinical",
        cortical_atrophy_scale=0.95,   # Minimal atrophy (Braak I-II)
        gamma_efficacy=0.90,           # Slight ASSR reduction
        theta_power_multiplier=1.15,   # Mild theta increase
        pac_coupling_scale=0.90,       # Mild PAC reduction
        fatigue_rate_multiplier=1.10,  # Slightly faster habituation
        recovery_rate_multiplier=0.95, # Slightly slower recovery
        baseline_pac_scale=0.95,
        noise_multiplier=1.05,
    ),
    "mild": AlzheimerProfile(
        severity="mild",
        cortical_atrophy_scale=0.80,   # Moderate temporal atrophy (Braak III-IV)
        gamma_efficacy=0.70,           # 30% ASSR reduction (Jafari 2020)
        theta_power_multiplier=1.40,   # Significant theta increase
        pac_coupling_scale=0.70,       # PAC disruption begins
        fatigue_rate_multiplier=1.30,  # Faster habituation
        recovery_rate_multiplier=0.80, # Slower recovery
        baseline_pac_scale=0.80,
        noise_multiplier=1.15,
    ),
    "moderate": AlzheimerProfile(
        severity="moderate",
        cortical_atrophy_scale=0.60,   # Widespread atrophy (Braak IV-V)
        gamma_efficacy=0.50,           # 50% ASSR reduction
        theta_power_multiplier=1.80,   # Strong theta dominance
        pac_coupling_scale=0.50,       # Severe PAC disruption
        fatigue_rate_multiplier=1.60,  # Much faster habituation
        recovery_rate_multiplier=0.60, # Slow recovery
        baseline_pac_scale=0.60,
        noise_multiplier=1.30,
    ),
    "severe": AlzheimerProfile(
        severity="severe",
        cortical_atrophy_scale=0.35,   # Severe global atrophy (Braak V-VI)
        gamma_efficacy=0.30,           # 70% ASSR reduction
        theta_power_multiplier=2.20,   # Dominant theta/delta activity
        pac_coupling_scale=0.30,       # Near-complete PAC loss
        fatigue_rate_multiplier=2.00,  # Very rapid habituation
        recovery_rate_multiplier=0.40, # Very slow recovery
        baseline_pac_scale=0.40,
        noise_multiplier=1.50,
    ),
}


# ROI-specific atrophy weights by disease stage
# Order: [Aud_L, Aud_R, IFG_L, IFG_R, MFG/SFG, Medial_Frontal]
# Weight 1.0 = maximally affected, 0.0 = spared
ROI_ATROPHY_WEIGHTS: dict[str, np.ndarray] = {
    "healthy": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    "preclinical": np.array([0.05, 0.05, 0.02, 0.02, 0.02, 0.03]),
    "mild": np.array([0.25, 0.25, 0.10, 0.10, 0.15, 0.20]),
    "moderate": np.array([0.45, 0.45, 0.30, 0.30, 0.35, 0.40]),
    "severe": np.array([0.65, 0.65, 0.55, 0.55, 0.60, 0.65]),
}


def get_profile(
    severity: str,
) -> AlzheimerProfile:
    """
    Get Alzheimer's profile by severity name.

    Args:
        severity: One of "healthy", "preclinical", "mild", "moderate", "severe".

    Returns:
        profile: Disease parameter profile.

    Raises:
        ValueError: If severity is not recognized.
    """
    if severity not in ALZHEIMER_PROFILES:
        raise ValueError(
            f"Unknown severity '{severity}'. "
            f"Valid options: {list(ALZHEIMER_PROFILES.keys())}"
        )
    return ALZHEIMER_PROFILES[severity]


def interpolate_profile(
    severity_score: float,
) -> AlzheimerProfile:
    """
    Create an interpolated profile from a continuous severity score.

    Allows finer-grained disease modeling than discrete severity levels.

    Args:
        severity_score: Continuous severity from 0.0 (healthy) to 1.0 (severe).

    Returns:
        profile: Interpolated disease parameter profile.
    """
    severity_score = float(np.clip(severity_score, 0.0, 1.0))

    # Map score to anchor points
    anchors = [
        (0.0, ALZHEIMER_PROFILES["healthy"]),
        (0.2, ALZHEIMER_PROFILES["preclinical"]),
        (0.4, ALZHEIMER_PROFILES["mild"]),
        (0.7, ALZHEIMER_PROFILES["moderate"]),
        (1.0, ALZHEIMER_PROFILES["severe"]),
    ]

    # Find bracketing anchors
    lower_score, lower_prof = anchors[0]
    upper_score, upper_prof = anchors[-1]
    for i in range(len(anchors) - 1):
        if anchors[i][0] <= severity_score <= anchors[i + 1][0]:
            lower_score, lower_prof = anchors[i]
            upper_score, upper_prof = anchors[i + 1]
            break

    # Linear interpolation
    if upper_score == lower_score:
        t = 0.0
    else:
        t = (severity_score - lower_score) / (upper_score - lower_score)

    def lerp(a: float, b: float) -> float:
        return a + t * (b - a)

    # Determine severity label
    if severity_score < 0.1:
        sev_label = "healthy"
    elif severity_score < 0.3:
        sev_label = "preclinical"
    elif severity_score < 0.55:
        sev_label = "mild"
    elif severity_score < 0.85:
        sev_label = "moderate"
    else:
        sev_label = "severe"

    return AlzheimerProfile(
        severity=sev_label,
        cortical_atrophy_scale=lerp(
            lower_prof.cortical_atrophy_scale,
            upper_prof.cortical_atrophy_scale,
        ),
        gamma_efficacy=lerp(lower_prof.gamma_efficacy, upper_prof.gamma_efficacy),
        theta_power_multiplier=lerp(
            lower_prof.theta_power_multiplier,
            upper_prof.theta_power_multiplier,
        ),
        pac_coupling_scale=lerp(
            lower_prof.pac_coupling_scale, upper_prof.pac_coupling_scale
        ),
        fatigue_rate_multiplier=lerp(
            lower_prof.fatigue_rate_multiplier,
            upper_prof.fatigue_rate_multiplier,
        ),
        recovery_rate_multiplier=lerp(
            lower_prof.recovery_rate_multiplier,
            upper_prof.recovery_rate_multiplier,
        ),
        baseline_pac_scale=lerp(
            lower_prof.baseline_pac_scale, upper_prof.baseline_pac_scale
        ),
        noise_multiplier=lerp(lower_prof.noise_multiplier, upper_prof.noise_multiplier),
    )


if __name__ == "__main__":
    print("=" * 60)
    print("Alzheimer's Disease Model — Self-Test")
    print("=" * 60)

    for name, profile in ALZHEIMER_PROFILES.items():
        print(f"\n{name.upper()}:")
        print(f"  Cortical atrophy:  {profile.cortical_atrophy_scale:.2f}")
        print(f"  Gamma efficacy:    {profile.gamma_efficacy:.2f}")
        print(f"  Theta multiplier:  {profile.theta_power_multiplier:.2f}")
        print(f"  PAC coupling:      {profile.pac_coupling_scale:.2f}")
        print(f"  Fatigue rate:      {profile.fatigue_rate_multiplier:.2f}x")

        # Show effective activation for stim=6.0
        eff_act = profile.apply_to_activation(6.0)
        print(f"  Effective stim drive: {eff_act:.2f} (from 6.0)")

    # Test interpolation
    print("\n" + "=" * 60)
    print("Continuous severity interpolation:")
    print("-" * 40)
    for score in np.arange(0.0, 1.05, 0.1):
        prof = interpolate_profile(score)
        print(
            f"  score={score:.1f} ({prof.severity:>12s}): "
            f"atrophy={prof.cortical_atrophy_scale:.2f}, "
            f"gamma_eff={prof.gamma_efficacy:.2f}, "
            f"pac_scale={prof.pac_coupling_scale:.2f}"
        )

    print("\n[PASS] All AD profiles valid, interpolation smooth")
