"""
Model registry for hot-swapping temporal PAC prediction models by name.

Provides:
- TemporalModel: runtime_checkable Protocol that all predictors must satisfy.
- TCNTemporalModel: thin adapter wrapping RealtimePACForecaster.
- ModelRegistry: name-keyed store with register/get/available operations.
- build_default_registry(): factory that creates a registry with the 4-channel
  TCN pre-registered as "tcn".

Design intent: inference code (controller, Streamlit app) calls registry.get("tcn")
and never has if/else branches over model types.  XGBoost and Transformer will be
registered as additional names in Phase 12 without any changes here.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from temporal_multiscale.realtime_inference import RealtimePACForecaster

try:
    from typing import Protocol, runtime_checkable
except ImportError:  # Python < 3.8 fallback (not expected in this codebase)
    from typing_extensions import Protocol, runtime_checkable  # type: ignore[assignment]

# Default checkpoint paths for the 4-channel Muse-mapped TCN (Phase 10 output).
DEFAULT_TCN_CHECKPOINT = "models/muse_4ch/best_multiscale_tcn_4ch_lb20_hz5_ts1.pth"
DEFAULT_TCN_SCALERS = (
    "data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1/scalers.npz"
)


@runtime_checkable
class TemporalModel(Protocol):
    """
    Protocol that every temporal PAC predictor must satisfy.

    All methods are causal: they use only current and past observations.
    """

    def step(
        self,
        spectral_features: np.ndarray,
        pac_current: float,
        stim_state: float,
        time_since_switch_sec: float,
        stim_frac_recent: float,
    ) -> dict | None:
        """
        Advance the model by one step and return a prediction when ready.

        Args:
            spectral_features: 1-D float32 array of spectral features extracted
                from the current EEG window (length = feature_dim - 12).
            pac_current: Scalar PAC estimate for the current window.
            stim_state: 0.0 (REST) or 1.0 (STIMULATE).
            time_since_switch_sec: Seconds since the last rest<->stim transition.
            stim_frac_recent: Fraction of recent history in stimulation state.

        Returns:
            None until enough history is accumulated (lookback windows).
            dict with keys {"future_pac", "delta_pac", "current_pac",
            "implied_future_from_delta"} once the buffer is full.
        """
        ...

    def reset(self) -> None:
        """Clear all internal rolling state (e.g. after a session break)."""
        ...


class TCNTemporalModel:
    """
    Adapter that wraps RealtimePACForecaster to satisfy the TemporalModel Protocol.

    Delegates all prediction logic to the underlying forecaster without changing
    its API.  The adapter exists so the registry has a uniform interface — the
    forecaster's cycle_phase_sin/cos arguments are always passed as default values
    (0.0, 1.0) because the protocol does not expose them.

    Args:
        checkpoint_path: Path to the .pth checkpoint produced by train_multiscale_tcn.py.
        scalers_path: Path to the scalers.npz containing feature/target statistics.
        device: PyTorch device string (e.g. "cpu", "mps", "cuda:0").
            Defaults to auto-detection.
    """

    def __init__(
        self,
        checkpoint_path: str = DEFAULT_TCN_CHECKPOINT,
        scalers_path: str = DEFAULT_TCN_SCALERS,
        device: Optional[str] = None,
    ) -> None:
        self.forecaster = RealtimePACForecaster(
            checkpoint_path=checkpoint_path,
            scalers_path=scalers_path,
            device=device,
        )

    @property
    def lookback(self) -> int:
        """Number of history windows required before predictions are produced."""
        return self.forecaster.lookback

    @property
    def feature_dim(self) -> int:
        """Total feature vector length (spectral + PAC-derived + stim context)."""
        return self.forecaster.feature_dim

    def step(
        self,
        spectral_features: np.ndarray,
        pac_current: float,
        stim_state: float,
        time_since_switch_sec: float,
        stim_frac_recent: float,
    ) -> dict | None:
        """Delegate to RealtimePACForecaster.step() with fixed cycle-phase defaults."""
        return self.forecaster.step(
            spectral_features=spectral_features,
            pac_current=pac_current,
            stim_state=stim_state,
            time_since_switch_sec=time_since_switch_sec,
            stim_frac_recent=stim_frac_recent,
            cycle_phase_sin=0.0,
            cycle_phase_cos=1.0,
        )

    def reset(self) -> None:
        """Clear the rolling buffer in the underlying forecaster."""
        self.forecaster.reset()


class ModelRegistry:
    """
    Name-keyed registry for TemporalModel instances.

    Models are validated at registration time against the TemporalModel Protocol.
    Retrieval raises a descriptive KeyError listing available names.

    Example:
        registry = ModelRegistry()
        registry.register("tcn", TCNTemporalModel(...))
        model = registry.get("tcn")
        result = model.step(...)
    """

    def __init__(self) -> None:
        self._models: dict[str, TemporalModel] = {}

    def register(self, name: str, model: TemporalModel) -> None:
        """
        Register a model under a name.

        Args:
            name: Lookup key (e.g. "tcn", "xgboost", "transformer").
            model: An object satisfying the TemporalModel Protocol.

        Raises:
            TypeError: If model does not satisfy TemporalModel Protocol.
        """
        if not isinstance(model, TemporalModel):
            raise TypeError(
                f"Cannot register '{name}': object does not satisfy the "
                f"TemporalModel Protocol (requires step() and reset() methods)."
            )
        self._models[name] = model

    def get(self, name: str) -> TemporalModel:
        """
        Retrieve a registered model by name.

        Args:
            name: The registered model name.

        Returns:
            The TemporalModel registered under name.

        Raises:
            KeyError: If name is not registered. Error message includes available names.
        """
        if name not in self._models:
            available = self.available()
            raise KeyError(
                f"Model '{name}' not found in registry. "
                f"Available: {available}"
            )
        return self._models[name]

    def available(self) -> list[str]:
        """Return sorted list of registered model names."""
        return sorted(self._models.keys())


def build_default_registry(
    tcn_checkpoint_path: str = DEFAULT_TCN_CHECKPOINT,
    tcn_scalers_path: str = DEFAULT_TCN_SCALERS,
    device: Optional[str] = None,
) -> ModelRegistry:
    """
    Factory that returns a ModelRegistry with the 4-channel TCN pre-registered.

    The TCN is registered as "tcn".  XGBoost and Transformer will be added in
    Phase 12 by calling registry.register("xgboost", ...) — no changes to this
    file are needed.

    Args:
        tcn_checkpoint_path: Path to TCN checkpoint (.pth).
        tcn_scalers_path: Path to scalers file (.npz).
        device: PyTorch device override.

    Returns:
        Populated ModelRegistry with "tcn" registered.
    """
    registry = ModelRegistry()
    tcn_model = TCNTemporalModel(
        checkpoint_path=tcn_checkpoint_path,
        scalers_path=tcn_scalers_path,
        device=device,
    )
    registry.register("tcn", tcn_model)
    return registry
