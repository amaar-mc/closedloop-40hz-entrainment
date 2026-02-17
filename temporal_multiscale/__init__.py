"""
Multiscale Temporal PAC Prediction Module.

This module adds a leakage-safe, low-latency pipeline for predicting:
1) future PAC (at horizon h), and
2) delta PAC (PAC[t+h] - PAC[t]),
from multiscale EEG-derived features plus stimulation-context signals.
"""

