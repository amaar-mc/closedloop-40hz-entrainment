"""
Streaming EEG adapter modules for closed-loop inference.

Provides hardware-agnostic EEG data sources:
- SimulatedEEGAdapter: BrainFlow SYNTHETIC_BOARD for hardware-free development
- RealEEGAdapter: Muse 2 integration (implemented in Plan 03)
"""

from src.streaming.adapters import RealEEGAdapter, SimulatedEEGAdapter

__all__ = ["SimulatedEEGAdapter", "RealEEGAdapter"]
