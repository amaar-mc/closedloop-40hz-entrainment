"""
TRIBE V2 Integration Module for Closed-Loop 40Hz Entrainment

Integrates Meta's TRIBE V2 brain foundation model with the closed-loop
gamma entrainment system. Provides a biophysically grounded simulation
that bridges fMRI cortical predictions to EEG-level oscillatory dynamics.

Architecture:
    40 Hz Auditory Stimulus
        → TRIBE V2 Cortical Predictions (fMRI, ~20k vertices)
        → ROI Extraction (auditory + frontal cortex)
        → Neural Mass Model (Wilson-Cowan → theta/gamma oscillations)
        → EEG Forward Model (source → 7 frontal channels)
        → PAC Computation (Tort MI)
        → Closed-Loop Controller

Author: Amaar Chughtai
Date: April 2026
"""

from tribe_v2.neural_mass import WilsonCowanModel, NeuralMassConfig
from tribe_v2.alzheimer_model import AlzheimerProfile, ALZHEIMER_PROFILES
from tribe_v2.enhanced_simulator import TribeEnhancedSimulator
from tribe_v2.cortical_model import CorticalResponseModel

__all__ = [
    "WilsonCowanModel",
    "NeuralMassConfig",
    "AlzheimerProfile",
    "ALZHEIMER_PROFILES",
    "TribeEnhancedSimulator",
    "CorticalResponseModel",
]
