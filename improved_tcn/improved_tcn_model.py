"""
ImprovedTCN: Causal TCN with temporal multi-head self-attention and three-head output.

Architecture additions over MultiscaleCausalTCN:
- Temporal self-attention (TransformerEncoder, causal mask) between TCN and pooling.
- Third regression head: smoothed auxiliary PAC prediction for cleaner gradient signal.
- Toggle use_self_attention=False for ablation studies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------------------------------------------------------------------------
# Copied from temporal_multiscale/multiscale_tcn.py — do NOT import from there.
# This module is standalone to avoid contaminating the audited pipeline.
# ---------------------------------------------------------------------------

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
        # Double-SiLU preserved exactly from baseline — changing this would
        # require retraining and re-validation of all checkpoints.
        return F.silu(x + residual)


class AttentionPool1D(nn.Module):
    """Attention pooling over time axis."""

    def __init__(self, channels: int) -> None:
        super().__init__()
        self.score = nn.Conv1d(channels, 1, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, C, T)
        logits = self.score(x)           # (B, 1, T)
        weights = torch.softmax(logits, dim=-1)
        pooled = (x * weights).sum(dim=-1)  # (B, C)
        return pooled


class LastStepPool(nn.Module):
    """Take last timestep from causal TCN output.

    For a causal architecture the last position already sees the full
    receptive field, preserving strict temporal ordering.
    """

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, C, T)
        return x[:, :, -1]  # (B, C)


# ---------------------------------------------------------------------------
# ImprovedTCN
# ---------------------------------------------------------------------------

@dataclass
class ImprovedModelConfig:
    n_features: int
    hidden: int = 64
    kernel_size: int = 3
    dilations: List[int] = field(default_factory=lambda: [1, 2, 4, 8])
    dropout: float = 0.1
    pool_type: str = "attention"   # "attention" or "last_step"
    n_attn_heads: int = 4          # multi-head self-attention heads
    attn_layers: int = 1           # number of self-attention encoder layers
    use_self_attention: bool = True  # False to ablate attention block


class ImprovedTCN(nn.Module):
    """
    Causal TCN with temporal multi-head self-attention and three regression heads.

    Input:
        x_seq: (B, T, F)
    Output:
        dict:
            future: (B,)  — normalized future PAC prediction (primary head)
            delta:  (B,)  — normalized delta-PAC prediction
            smooth: (B,)  — auxiliary smoothed PAC prediction (training only)
    """

    def __init__(self, cfg: ImprovedModelConfig) -> None:
        super().__init__()
        self.cfg = cfg

        # 1. Input projection: linear → LayerNorm → SiLU
        self.in_proj = nn.Sequential(
            nn.Linear(cfg.n_features, cfg.hidden),
            nn.LayerNorm(cfg.hidden),
            nn.SiLU(),
        )

        # 2. Causal dilated depthwise-separable TCN blocks
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

        # 3. Temporal self-attention (causal) between TCN and pooling
        if cfg.use_self_attention:
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=cfg.hidden,
                nhead=cfg.n_attn_heads,
                dim_feedforward=cfg.hidden * 2,
                dropout=cfg.dropout,
                batch_first=True,
                norm_first=True,  # pre-norm for stable gradients
            )
            self.temporal_self_attention: nn.Module = nn.TransformerEncoder(
                encoder_layer, num_layers=cfg.attn_layers
            )
        else:
            self.temporal_self_attention = nn.Identity()

        # 4. Pooling
        if cfg.pool_type == "last_step":
            self.pool: nn.Module = LastStepPool()
        else:
            self.pool = AttentionPool1D(cfg.hidden)

        # 5. Three regression heads
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
        # Auxiliary head: predicts smoothed version of future PAC.
        # Provides a cleaner gradient signal during training — the backbone
        # learns to capture underlying PAC trend, not just instantaneous noise.
        self.smooth_head = nn.Sequential(
            nn.Linear(cfg.hidden, cfg.hidden),
            nn.SiLU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.hidden, 1),
        )

    def _make_causal_mask(self, T: int, device: torch.device) -> torch.Tensor:
        """Upper-triangular boolean mask: True = masked (no attending to future)."""
        return torch.triu(torch.ones(T, T, device=device), diagonal=1).bool()

    def forward(self, x_seq: torch.Tensor) -> Dict[str, torch.Tensor]:
        # x_seq: (B, T, F)
        x = self.in_proj(x_seq)   # (B, T, H)
        x = x.transpose(1, 2)     # (B, H, T) for TCN
        x = self.tcn(x)            # (B, H, T)

        if self.cfg.use_self_attention:
            T = x.shape[2]
            x_t = x.transpose(1, 2)  # (B, T, H) for attention
            causal_mask = self._make_causal_mask(T, x.device)
            x_t = self.temporal_self_attention(x_t, mask=causal_mask)  # (B, T, H)
            x = x_t.transpose(1, 2)  # (B, H, T) for pooling
        # else: identity block skips attention entirely

        z = self.pool(x)   # (B, H)

        future = self.future_head(z).squeeze(-1)   # (B,)
        delta = self.delta_head(z).squeeze(-1)     # (B,)
        smooth = self.smooth_head(z).squeeze(-1)   # (B,)

        return {"future": future, "delta": delta, "smooth": smooth}

    def freeze_backbone(self) -> None:
        """Freeze all layers except the three regression heads.

        Useful for per-subject fine-tuning.
        """
        for name, param in self.named_parameters():
            if not any(head in name for head in ["future_head", "delta_head", "smooth_head"]):
                param.requires_grad = False

    def unfreeze_all(self) -> None:
        """Unfreeze all parameters (reverses freeze_backbone)."""
        for param in self.parameters():
            param.requires_grad = True

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    torch.manual_seed(0)

    test_cases = [
        ("7ch (108 features)", ImprovedModelConfig(n_features=108)),
        ("4ch (69 features)",  ImprovedModelConfig(n_features=69)),
    ]

    all_pass = True
    for label, cfg in test_cases:
        model = ImprovedTCN(cfg)
        model.eval()
        B, T = 4, 20
        x = torch.randn(B, T, cfg.n_features)
        with torch.no_grad():
            out = model(x)

        # Shape checks
        for key in ("future", "delta", "smooth"):
            if key not in out:
                print(f"[FAIL] {label}: missing key '{key}' in output")
                all_pass = False
                continue
            if out[key].shape != (B,):
                print(f"[FAIL] {label}: key '{key}' shape {out[key].shape}, expected ({B},)")
                all_pass = False

        n_params = model.count_parameters()
        # Expect more than baseline 31K due to attention layers
        if n_params < 31000:
            print(f"[FAIL] {label}: param count {n_params:,} unexpectedly low (< 31K)")
            all_pass = False

        print(f"  {label}: n_params={n_params:,}, output shapes OK")

    # Test use_self_attention=False ablation toggle
    cfg_no_attn = ImprovedModelConfig(n_features=108, use_self_attention=False)
    model_no_attn = ImprovedTCN(cfg_no_attn)
    model_no_attn.eval()
    with torch.no_grad():
        out_no_attn = model_no_attn(torch.randn(4, 20, 108))
    for key in ("future", "delta", "smooth"):
        if out_no_attn[key].shape != (4,):
            print(f"[FAIL] no-attention ablation: key '{key}' shape mismatch")
            all_pass = False
    print(f"  no-attention ablation (108 features): n_params={model_no_attn.count_parameters():,}, output shapes OK")

    if all_pass:
        print("[PASS] improved_tcn_model self-test")
    else:
        print("[FAIL] improved_tcn_model self-test — see above")
        sys.exit(1)
