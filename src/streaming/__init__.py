"""
Streaming EEG modules for closed-loop inference.

Provides:
- StreamingFeatureExtractor: causal sosfilt-based spectral feature extraction
- SimulatedEEGAdapter: BrainFlow SYNTHETIC_BOARD for hardware-free development (Plan 03)
- RealEEGAdapter: Muse 2 integration (Plan 03)
"""

from src.streaming.feature_extractor import StreamingFeatureExtractor

__all__ = ["StreamingFeatureExtractor"]

# Hardware adapters are implemented in Plan 03 — import conditionally so
# this package remains importable before adapters.py exists.
try:
    from src.streaming.adapters import RealEEGAdapter, SimulatedEEGAdapter
    __all__ += ["SimulatedEEGAdapter", "RealEEGAdapter"]
except ModuleNotFoundError:
    pass
