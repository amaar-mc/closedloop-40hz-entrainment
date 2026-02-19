"""
Lightweight multiscale causal TCN for future PAC and delta-PAC prediction.

Design constraints:
- Causal temporal modeling (real-time safe).
- Low parameter count for fast closed-loop inference.
- Multi-head regression: predict future PAC and delta PAC jointly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import torch
import torch.nn as nn
import torch.nn.functional as F


class CausalDSConvBlock(nn.Module):
    """Residual depthwise-separable causal temporal block."""

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
        # GroupNorm(1, C) == LayerNorm over channels — more stable with
        # small batches and cross-subject distribution shifts than BatchNorm.
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
    """Take last timestep from causal TCN output.

    For a causal architecture the last position already sees the full
    receptive field, so this preserves strict temporal ordering without
    weighting future-adjacent steps.
    """

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, C, T)
        return x[:, :, -1]  # (B, C)


@dataclass
class ModelConfig:
    n_features: int
    hidden: int = 64
    kernel_size: int = 3
    dilations: List[int] | None = None
    dropout: float = 0.1
    pool_type: str = "attention"  # "attention" or "last_step"

    def __post_init__(self) -> None:
        if self.dilations is None:
            self.dilations = [1, 2, 4, 8]


class MultiscaleCausalTCN(nn.Module):
    """
    Causal multiscale TCN with two regression heads.

    Input:
        x_seq: (B, T, F)
    Output:
        dict:
            future: (B,)
            delta:  (B,)
    """

    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        self.cfg = cfg

        self.in_proj = nn.Sequential(
            nn.Linear(cfg.n_features, cfg.hidden),
            nn.LayerNorm(cfg.hidden),
            nn.SiLU(),
        )

        blocks = []
        for d in cfg.dilations:
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
            self.pool = LastStepPool()
        else:
            self.pool = AttentionPool1D(cfg.hidden)

        self.future_head = nn.Sequential(
            nn.Linear(cfg.hidden, cfg.hidden),
            nn.SiLU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.hidden, 1),
        )
        self.delta_head = nn.Sequential(
            nn.Linear(cfg.hidden, cfg.hidden),
            nn.SiLU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.hidden, 1),
        )

    def forward(self, x_seq: torch.Tensor) -> Dict[str, torch.Tensor]:
        # x_seq: (B, T, F)
        x = self.in_proj(x_seq)  # (B, T, H)
        x = x.transpose(1, 2)    # (B, H, T)
        x = self.tcn(x)
        z = self.pool(x)         # (B, H)
        future = self.future_head(z).squeeze(-1)
        delta = self.delta_head(z).squeeze(-1)
        return {"future": future, "delta": delta}

    def freeze_backbone(self) -> None:
        """Freeze all layers except the future and delta regression heads.

        Useful for per-subject fine-tuning: keeps learned temporal
        representations fixed while adapting the output mapping.
        """
        for name, param in self.named_parameters():
            if "future_head" not in name and "delta_head" not in name:
                param.requires_grad = False

    def unfreeze_all(self) -> None:
        """Unfreeze all parameters (reverses ``freeze_backbone``)."""
        for param in self.parameters():
            param.requires_grad = True

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

