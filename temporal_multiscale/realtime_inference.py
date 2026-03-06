"""
Realtime inference wrapper for the multiscale causal TCN.

This utility keeps rolling state and produces low-latency predictions once
enough history is available.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import torch

from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN


class RealtimePACForecaster:
    """
    Realtime PAC forecaster with causal rolling buffer.

    Expected per-step inputs (1 Hz decision rate):
    - spectral_features: shape (61,) from current EEG window
    - pac_current: current PAC estimate
    - stim_state: 0 or 1
    - time_since_switch_sec: seconds from latest rest<->stim transition
    - stim_frac_recent: fraction of stim in recent history window
    - cycle_phase_sin/cos: optional 60-second protocol phase features
    """

    def __init__(
        self,
        checkpoint_path: str = "models/best_multiscale_tcn.pth",
        scalers_path: str = "data/processed/multiscale_temporal/scalers.npz",
        device: Optional[str] = None,
    ) -> None:
        ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
        cfg_dict = ckpt["cfg"]
        cfg = ModelConfig(**cfg_dict)

        self.model = MultiscaleCausalTCN(cfg)
        self.model.load_state_dict(ckpt["model_state_dict"])
        self.model.eval()

        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model.to(self.device)

        s = np.load(scalers_path)
        self.feature_mean = s["feature_mean"].astype(np.float32)
        self.feature_std = s["feature_std"].astype(np.float32)
        self.yf_mean = float(s["y_future_mean"])
        self.yf_std = float(s["y_future_std"])
        self.yd_mean = float(s["y_delta_mean"])
        self.yd_std = float(s["y_delta_std"])

        self.lookback = int(ckpt["metadata"]["lookback"])
        self.feature_dim = int(cfg.n_features)
        self.seq_buffer: deque[np.ndarray] = deque(maxlen=self.lookback)
        self.pac_buffer: deque[float] = deque(maxlen=max(self.lookback, 32))

    def reset(self) -> None:
        self.seq_buffer.clear()
        self.pac_buffer.clear()

    def _pac_features(self, pac_current: float) -> np.ndarray:
        hist = list(self.pac_buffer) + [pac_current]

        def mean_last(k: int) -> float:
            k = min(k, len(hist))
            return float(np.mean(hist[-k:])) if k > 0 else float(pac_current)

        ma2 = mean_last(2)
        ma4 = mean_last(4)
        ma8 = mean_last(8)
        ma16 = mean_last(16)
        diff1 = float(pac_current - hist[-2]) if len(hist) >= 2 else 0.0
        diff4 = float(pac_current - hist[-5]) if len(hist) >= 5 else 0.0
        return np.array([pac_current, ma2, ma4, ma8, ma16, diff1, diff4], dtype=np.float32)

    def _build_step_feature(
        self,
        spectral_features: np.ndarray,
        pac_current: float,
        stim_state: float,
        time_since_switch_sec: float,
        stim_frac_recent: float,
        cycle_phase_sin: float = 0.0,
        cycle_phase_cos: float = 1.0,
    ) -> np.ndarray:
        spectral_features = np.asarray(spectral_features, dtype=np.float32).reshape(-1)
        # 7 PAC-derived features + 5 stimulation context features = 12 non-spectral
        n_non_spectral = 7 + 5
        if spectral_features.shape[0] != (self.feature_dim - n_non_spectral):
            raise ValueError(
                f"Expected spectral length {self.feature_dim - n_non_spectral}, "
                f"got {spectral_features.shape[0]}"
            )

        pac_feats = self._pac_features(pac_current)
        ctx = np.array(
            [
                float(stim_state),
                float(min(max(time_since_switch_sec / 60.0, 0.0), 1.0)),
                float(min(max(stim_frac_recent, 0.0), 1.0)),
                float(cycle_phase_sin),
                float(cycle_phase_cos),
            ],
            dtype=np.float32,
        )
        x = np.concatenate([spectral_features, pac_feats, ctx]).astype(np.float32)
        x = (x - self.feature_mean) / (self.feature_std + 1e-8)
        return x

    @torch.no_grad()
    def step(
        self,
        spectral_features: np.ndarray,
        pac_current: float,
        stim_state: float,
        time_since_switch_sec: float,
        stim_frac_recent: float,
        cycle_phase_sin: float = 0.0,
        cycle_phase_cos: float = 1.0,
    ) -> Optional[Dict[str, float]]:
        """
        Add one new observation and return prediction when ready.
        """
        x_step = self._build_step_feature(
            spectral_features=spectral_features,
            pac_current=float(pac_current),
            stim_state=float(stim_state),
            time_since_switch_sec=float(time_since_switch_sec),
            stim_frac_recent=float(stim_frac_recent),
            cycle_phase_sin=float(cycle_phase_sin),
            cycle_phase_cos=float(cycle_phase_cos),
        )
        self.seq_buffer.append(x_step)
        self.pac_buffer.append(float(pac_current))

        if len(self.seq_buffer) < self.lookback:
            return None

        x_seq = np.stack(self.seq_buffer, axis=0)[None, ...]  # (1, T, F)
        x_tensor = torch.from_numpy(x_seq).float().to(self.device)
        out = self.model(x_tensor)
        future_norm = float(out["future"].item())
        delta_norm = float(out["delta"].item())

        future_raw = future_norm * self.yf_std + self.yf_mean
        delta_raw = delta_norm * self.yd_std + self.yd_mean

        return {
            "future_pac": float(future_raw),
            "delta_pac": float(delta_raw),
            "current_pac": float(pac_current),
            "implied_future_from_delta": float(pac_current + delta_raw),
        }

