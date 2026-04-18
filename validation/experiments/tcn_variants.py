"""
TCN Architecture Variants for Temporal PAC Prediction Experiments.

Tests four architectural hypotheses against the baseline MultiscaleCausalTCN
(31K params, R^2=0.25-0.28 at 5-10s horizons):

    DeepDilationTCN: Deeper dilation stack [1,2,4,8,16,32] for 4x larger
        receptive field (186 vs 44 steps). Hypothesis: longer temporal context
        captures slow PAC dynamics that matter at 5-10s prediction horizons.

    MultiTaskTCN: Same architecture as baseline but actually trains the
        delta-PAC head (lambda_delta=0.3, lambda_consistency=0.1). The
        production pipeline sets lambda_delta=0.0, never training this head.
        Hypothesis: joint delta prediction provides gradient signal that
        regularizes the shared backbone toward change-sensitive features.

    WiderTCN: hidden=128 instead of 64 (approximately 4x parameters).
        Hypothesis: the hidden bottleneck limits expressiveness for the
        73-dimensional input; wider layers can learn richer temporal filters.

    TransformerTCN: Replaces the dilated-convolution backbone with a causal
        Transformer encoder (4 layers, 4 heads). Hypothesis: self-attention
        captures long-range temporal dependencies more flexibly than fixed
        dilation patterns, particularly for non-stationary PAC dynamics.

All variants share the same forward interface:
    Input:  x_seq (B, T, F)
    Output: dict with 'future' (B,) and 'delta' (B,) keys

Author: Amaar Chughtai
Date: February 2026
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List

import torch
import torch.nn as nn
import torch.nn.functional as F

# ---------------------------------------------------------------------------
# Shared building blocks (from temporal_multiscale/multiscale_tcn.py)
# ---------------------------------------------------------------------------


class CausalDSConvBlock(nn.Module):
    """Residual depthwise-separable causal temporal block.

    Applies causal padding so the output at position t depends only on
    inputs at positions <= t. Uses GroupNorm(1, C) (equivalent to LayerNorm
    over channels) for stability under cross-subject distribution shifts.
    """

    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dilation: int = 1,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.pad = (kernel_size - 1) * dilation
        self.depthwise = nn.Conv1d(
            channels,
            channels,
            kernel_size=kernel_size,
            dilation=dilation,
            groups=channels,
            bias=False,
        )
        self.pointwise = nn.Conv1d(channels, channels, kernel_size=1, bias=False)
        self.norm = nn.GroupNorm(1, channels)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        x = F.pad(x, (self.pad, 0))
        x = self.depthwise(x)
        x = self.pointwise(x)
        x = self.norm(x)
        x = F.silu(x)
        x = self.dropout(x)
        return F.silu(x + residual)


class AttentionPool1D(nn.Module):
    """Attention pooling over time axis."""

    def __init__(self, channels: int) -> None:
        super().__init__()
        self.score = nn.Conv1d(channels, 1, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, C, T)
        logits = self.score(x)  # (B, 1, T)
        weights = torch.softmax(logits, dim=-1)
        pooled = (x * weights).sum(dim=-1)  # (B, C)
        return pooled


class LastStepPool(nn.Module):
    """Take last timestep from causal output.

    For a causal architecture the last position already sees the full
    receptive field, so this preserves strict temporal ordering.
    """

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, C, T)
        return x[:, :, -1]  # (B, C)


# ---------------------------------------------------------------------------
# Configurations
# ---------------------------------------------------------------------------


@dataclass
class ModelConfig:
    """Configuration shared across all TCN variants.

    Attributes:
        n_features: Number of input features per timestep.
        hidden: Hidden dimension of the temporal backbone.
        kernel_size: Kernel size for depthwise convolutions.
        dilations: Dilation factors for the TCN stack.
        dropout: Dropout probability.
        pool_type: Temporal pooling strategy ("attention" or "last_step").
    """

    n_features: int
    hidden: int = 64
    kernel_size: int = 3
    dilations: List[int] | None = None
    dropout: float = 0.1
    pool_type: str = "attention"

    def __post_init__(self) -> None:
        if self.dilations is None:
            self.dilations = [1, 2, 4, 8]


@dataclass
class TransformerConfig:
    """Extended configuration for the Transformer-based variant.

    Attributes:
        n_features: Number of input features per timestep.
        hidden: Hidden dimension (d_model for the Transformer).
        n_heads: Number of attention heads.
        n_layers: Number of Transformer encoder layers.
        dim_feedforward: Feedforward dimension in each Transformer layer.
        dropout: Dropout probability.
        pool_type: Temporal pooling strategy ("attention" or "last_step").
        max_seq_len: Maximum sequence length for positional encoding.
    """

    n_features: int
    hidden: int = 64
    n_heads: int = 4
    n_layers: int = 4
    dim_feedforward: int = 256
    dropout: float = 0.1
    pool_type: str = "attention"
    max_seq_len: int = 128


# ---------------------------------------------------------------------------
# Helper: parameter counting
# ---------------------------------------------------------------------------


def _count_parameters(model: nn.Module) -> int:
    """Count trainable parameters in a model."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# ---------------------------------------------------------------------------
# Shared regression heads
# ---------------------------------------------------------------------------


def _make_regression_head(hidden: int, dropout: float) -> nn.Sequential:
    """Two-layer MLP head: hidden -> hidden -> 1."""
    return nn.Sequential(
        nn.Linear(hidden, hidden),
        nn.SiLU(),
        nn.Dropout(dropout),
        nn.Linear(hidden, 1),
    )


# ---------------------------------------------------------------------------
# Variant A: DeepDilationTCN
# ---------------------------------------------------------------------------


class DeepDilationTCN(nn.Module):
    """Causal TCN with extended dilation stack for larger receptive field.

    Default dilations [1, 2, 4, 8, 16, 32] yield a receptive field of
    (sum(dilations) * (kernel_size - 1) + 1) = (63 * 2 + 1) = 127 steps
    with kernel_size=3, compared to 31 steps for the baseline [1,2,4,8].

    Scientific rationale: PAC dynamics at 5-10s horizons may depend on
    temporal context spanning 30-60 seconds of EEG history (at 2s windows
    with 1s hop). The baseline receptive field of ~44 steps covers only
    ~44 seconds, while the deeper stack covers ~127 steps (~2 minutes),
    capturing full stimulation on/off cycles (40s on + 20s off = 60s).

    Input:  x_seq (B, T, F)
    Output: dict with 'future' (B,) and 'delta' (B,) keys
    """

    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        self.cfg = cfg

        # Override dilations to the deep stack if not specified
        dilations = cfg.dilations if cfg.dilations is not None else [1, 2, 4, 8, 16, 32]

        self.in_proj = nn.Sequential(
            nn.Linear(cfg.n_features, cfg.hidden),
            nn.LayerNorm(cfg.hidden),
            nn.SiLU(),
        )

        blocks: list[nn.Module] = []
        for d in dilations:
            blocks.append(
                CausalDSConvBlock(
                    channels=cfg.hidden,
                    kernel_size=cfg.kernel_size,
                    dilation=d,
                    dropout=cfg.dropout,
                )
            )
        self.tcn = nn.Sequential(*blocks)

        if cfg.pool_type == "last_step":
            self.pool: nn.Module = LastStepPool()
        else:
            self.pool = AttentionPool1D(cfg.hidden)

        self.future_head = _make_regression_head(cfg.hidden, cfg.dropout)
        self.delta_head = _make_regression_head(cfg.hidden, cfg.dropout)

    def forward(self, x_seq: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Forward pass.

        Args:
            x_seq: Input tensor of shape (B, T, F).

        Returns:
            Dictionary with 'future' and 'delta' predictions, each (B,).
        """
        x = self.in_proj(x_seq)  # (B, T, H)
        x = x.transpose(1, 2)    # (B, H, T)
        x = self.tcn(x)
        z = self.pool(x)         # (B, H)
        future = self.future_head(z).squeeze(-1)
        delta = self.delta_head(z).squeeze(-1)
        return {"future": future, "delta": delta}

    def count_parameters(self) -> int:
        """Count trainable parameters."""
        return _count_parameters(self)


# ---------------------------------------------------------------------------
# Variant B: MultiTaskTCN
# ---------------------------------------------------------------------------


class MultiTaskTCN(nn.Module):
    """Baseline TCN architecture with multi-task training enabled.

    Architecturally identical to MultiscaleCausalTCN but designed to be
    trained with lambda_delta > 0 and lambda_consistency > 0, unlike the
    production config which sets both to 0.0.

    This variant does NOT change architecture -- it tests whether the
    existing delta head, when properly trained, provides useful gradient
    signal to the shared backbone.

    Recommended training hyperparameters:
        lambda_delta = 0.3
        lambda_consistency = 0.1

    Scientific rationale: Multi-task learning regularizes shared
    representations. Predicting delta-PAC (change from current to future)
    forces the backbone to learn features sensitive to PAC dynamics rather
    than just PAC level. This is especially relevant at longer horizons
    where absolute PAC prediction degrades but relative changes may remain
    more predictable.

    Input:  x_seq (B, T, F)
    Output: dict with 'future' (B,) and 'delta' (B,) keys
    """

    # Class-level recommended training hyperparameters (not model params,
    # but stored here for experiment runner convenience).
    RECOMMENDED_LAMBDA_DELTA: float = 0.3
    RECOMMENDED_LAMBDA_CONSISTENCY: float = 0.1

    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        self.cfg = cfg

        self.in_proj = nn.Sequential(
            nn.Linear(cfg.n_features, cfg.hidden),
            nn.LayerNorm(cfg.hidden),
            nn.SiLU(),
        )

        blocks: list[nn.Module] = []
        for d in (cfg.dilations or [1, 2, 4, 8]):
            blocks.append(
                CausalDSConvBlock(
                    channels=cfg.hidden,
                    kernel_size=cfg.kernel_size,
                    dilation=d,
                    dropout=cfg.dropout,
                )
            )
        self.tcn = nn.Sequential(*blocks)

        if cfg.pool_type == "last_step":
            self.pool: nn.Module = LastStepPool()
        else:
            self.pool = AttentionPool1D(cfg.hidden)

        self.future_head = _make_regression_head(cfg.hidden, cfg.dropout)
        self.delta_head = _make_regression_head(cfg.hidden, cfg.dropout)

    def forward(self, x_seq: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Forward pass.

        Args:
            x_seq: Input tensor of shape (B, T, F).

        Returns:
            Dictionary with 'future' and 'delta' predictions, each (B,).
        """
        x = self.in_proj(x_seq)  # (B, T, H)
        x = x.transpose(1, 2)    # (B, H, T)
        x = self.tcn(x)
        z = self.pool(x)         # (B, H)
        future = self.future_head(z).squeeze(-1)
        delta = self.delta_head(z).squeeze(-1)
        return {"future": future, "delta": delta}

    def count_parameters(self) -> int:
        """Count trainable parameters."""
        return _count_parameters(self)


# ---------------------------------------------------------------------------
# Variant C: WiderTCN
# ---------------------------------------------------------------------------


class WiderTCN(nn.Module):
    """Causal TCN with doubled hidden dimension (128 vs baseline 64).

    The wider hidden layer approximately quadruples parameter count because
    both depthwise and pointwise convolutions scale with channel count, and
    the regression heads scale quadratically (hidden x hidden).

    Scientific rationale: The 73-feature input is projected to 64 hidden
    dimensions, which may be a bottleneck. PAC dynamics emerge from complex
    interactions between spectral features, PAC history, and stimulation
    context. A wider representation may capture more of these interactions,
    especially cross-feature correlations that are compressed away in the
    narrower baseline.

    Note: This variant intentionally accepts a standard ModelConfig but
    enforces hidden=128 internally if the config specifies a different
    value, unless the config already sets hidden >= 128. This ensures the
    experiment tests the width hypothesis specifically.

    Input:  x_seq (B, T, F)
    Output: dict with 'future' (B,) and 'delta' (B,) keys
    """

    # Minimum hidden dimension for this variant.
    MIN_HIDDEN: int = 128

    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        self.cfg = cfg
        hidden = max(cfg.hidden, self.MIN_HIDDEN)

        self.in_proj = nn.Sequential(
            nn.Linear(cfg.n_features, hidden),
            nn.LayerNorm(hidden),
            nn.SiLU(),
        )

        blocks: list[nn.Module] = []
        for d in (cfg.dilations or [1, 2, 4, 8]):
            blocks.append(
                CausalDSConvBlock(
                    channels=hidden,
                    kernel_size=cfg.kernel_size,
                    dilation=d,
                    dropout=cfg.dropout,
                )
            )
        self.tcn = nn.Sequential(*blocks)

        if cfg.pool_type == "last_step":
            self.pool: nn.Module = LastStepPool()
        else:
            self.pool = AttentionPool1D(hidden)

        self.future_head = _make_regression_head(hidden, cfg.dropout)
        self.delta_head = _make_regression_head(hidden, cfg.dropout)

    def forward(self, x_seq: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Forward pass.

        Args:
            x_seq: Input tensor of shape (B, T, F).

        Returns:
            Dictionary with 'future' and 'delta' predictions, each (B,).
        """
        x = self.in_proj(x_seq)  # (B, T, H)
        x = x.transpose(1, 2)    # (B, H, T)
        x = self.tcn(x)
        z = self.pool(x)         # (B, H)
        future = self.future_head(z).squeeze(-1)
        delta = self.delta_head(z).squeeze(-1)
        return {"future": future, "delta": delta}

    def count_parameters(self) -> int:
        """Count trainable parameters."""
        return _count_parameters(self)


# ---------------------------------------------------------------------------
# Variant D: TransformerTCN
# ---------------------------------------------------------------------------


class CausalSinusoidalPE(nn.Module):
    """Sinusoidal positional encoding for sequence models.

    Fixed (non-learned) encoding following Vaswani et al. (2017). Registered
    as a buffer so it moves to the correct device automatically.
    """

    def __init__(self, d_model: int, max_len: int = 512) -> None:
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float32).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float32)
            * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # (1, max_len, d_model)
        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to input.

        Args:
            x: Input tensor of shape (B, T, D).

        Returns:
            Tensor of shape (B, T, D) with positional encoding added.
        """
        return x + self.pe[:, : x.size(1), :]


class TransformerTCN(nn.Module):
    """Causal Transformer encoder for temporal PAC prediction.

    Replaces the dilated convolution backbone with a multi-head self-
    attention mechanism under a causal mask, allowing each position to
    attend only to itself and earlier positions.

    Architecture:
        1. Linear projection:  F -> d_model
        2. Sinusoidal positional encoding
        3. N layers of causal TransformerEncoderLayer
        4. Attention/last-step pooling over time
        5. Separate future and delta regression heads

    Scientific rationale: Dilated causal convolutions have fixed receptive
    field patterns determined at construction time. Self-attention can
    dynamically weight any past position, potentially discovering
    variable-lag dependencies in PAC dynamics (e.g., different subjects
    may have different stimulation response latencies). The trade-off is
    higher computational cost and potentially harder optimization for
    small datasets.

    Input:  x_seq (B, T, F)
    Output: dict with 'future' (B,) and 'delta' (B,) keys
    """

    def __init__(self, cfg: TransformerConfig) -> None:
        super().__init__()
        self.cfg = cfg

        self.in_proj = nn.Sequential(
            nn.Linear(cfg.n_features, cfg.hidden),
            nn.LayerNorm(cfg.hidden),
            nn.SiLU(),
        )

        self.pos_enc = CausalSinusoidalPE(cfg.hidden, max_len=cfg.max_seq_len)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=cfg.hidden,
            nhead=cfg.n_heads,
            dim_feedforward=cfg.dim_feedforward,
            dropout=cfg.dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,  # Pre-LN for training stability
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=cfg.n_layers,
            enable_nested_tensor=False,
        )

        # Pooling over time dimension (expects B, C, T for conv-based pools)
        if cfg.pool_type == "last_step":
            self.pool: nn.Module = LastStepPool()
        else:
            self.pool = AttentionPool1D(cfg.hidden)

        self.future_head = _make_regression_head(cfg.hidden, cfg.dropout)
        self.delta_head = _make_regression_head(cfg.hidden, cfg.dropout)

    def _generate_causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """Generate upper-triangular causal attention mask.

        Returns:
            Boolean mask of shape (T, T) where True means "block attention".
            Position i can attend to positions 0..i.
        """
        mask = torch.triu(
            torch.ones(seq_len, seq_len, device=device, dtype=torch.bool),
            diagonal=1,
        )
        return mask

    def forward(self, x_seq: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Forward pass.

        Args:
            x_seq: Input tensor of shape (B, T, F).

        Returns:
            Dictionary with 'future' and 'delta' predictions, each (B,).
        """
        B, T, F = x_seq.shape

        x = self.in_proj(x_seq)      # (B, T, H)
        x = self.pos_enc(x)          # (B, T, H)

        causal_mask = self._generate_causal_mask(T, x.device)
        x = self.transformer(x, mask=causal_mask, is_causal=True)  # (B, T, H)

        # Pooling expects (B, C, T) for conv-based attention pool
        x = x.transpose(1, 2)        # (B, H, T)
        z = self.pool(x)             # (B, H)

        future = self.future_head(z).squeeze(-1)
        delta = self.delta_head(z).squeeze(-1)
        return {"future": future, "delta": delta}

    def count_parameters(self) -> int:
        """Count trainable parameters."""
        return _count_parameters(self)


# ---------------------------------------------------------------------------
# Registry for experiment runner
# ---------------------------------------------------------------------------

# Maps variant name to (model_class, config_factory) pairs.
# The config_factory takes n_features and returns a config object.
VARIANT_REGISTRY: Dict[str, tuple] = {
    "deep_dilation": (
        DeepDilationTCN,
        lambda n_feat: ModelConfig(
            n_features=n_feat,
            hidden=64,
            kernel_size=3,
            dilations=[1, 2, 4, 8, 16, 32],
            dropout=0.1,
            pool_type="attention",
        ),
    ),
    "multitask": (
        MultiTaskTCN,
        lambda n_feat: ModelConfig(
            n_features=n_feat,
            hidden=64,
            kernel_size=3,
            dilations=[1, 2, 4, 8],
            dropout=0.1,
            pool_type="attention",
        ),
    ),
    "wider": (
        WiderTCN,
        lambda n_feat: ModelConfig(
            n_features=n_feat,
            hidden=128,
            kernel_size=3,
            dilations=[1, 2, 4, 8],
            dropout=0.1,
            pool_type="attention",
        ),
    ),
    "transformer": (
        TransformerTCN,
        lambda n_feat: TransformerConfig(
            n_features=n_feat,
            hidden=64,
            n_heads=4,
            n_layers=4,
            dim_feedforward=256,
            dropout=0.1,
            pool_type="attention",
            max_seq_len=128,
        ),
    ),
}


def build_variant(name: str, n_features: int) -> nn.Module:
    """Instantiate a model variant by name.

    Args:
        name: One of the keys in VARIANT_REGISTRY.
        n_features: Number of input features per timestep.

    Returns:
        Instantiated model.

    Raises:
        KeyError: If the variant name is not in the registry.
    """
    if name not in VARIANT_REGISTRY:
        raise KeyError(
            f"Unknown variant '{name}'. Available: {sorted(VARIANT_REGISTRY.keys())}"
        )
    cls, config_factory = VARIANT_REGISTRY[name]
    cfg = config_factory(n_features)
    return cls(cfg)
