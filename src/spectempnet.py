"""
SpecTempNet: Hybrid Spectral-Temporal Network for PAC Prediction

Combines:
1. Multi-scale temporal CNN (raw EEG features)
2. Spectral features (theta/gamma power, phase-amplitude coupling)
3. Multi-head attention (feature fusion)
4. Deep regression head

Parameters: ~180k (vs 1.4k-25k in EEGNet)
Expected R²: 0.30-0.50 (vs 0.06-0.08 in EEGNet)

Author: Amaar Chughtai
Date: February 2026
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple


class MultiScaleTemporalCNN(nn.Module):
    """
    Multi-scale temporal CNN to capture oscillatory patterns at different frequencies.

    Uses parallel convolutions with different kernel sizes:
    - Small kernels (16): Capture high-frequency patterns (gamma range)
    - Medium kernels (32, 64): Capture mid-range oscillations
    - Large kernels (128): Capture low-frequency patterns (theta range)
    """

    def __init__(self,
                 n_channels: int = 7,
                 n_samples: int = 500,
                 kernel_sizes: Tuple[int, ...] = (16, 32, 64, 128),
                 n_filters_per_scale: int = 16):
        super().__init__()

        self.kernel_sizes = kernel_sizes
        self.n_scales = len(kernel_sizes)

        # Parallel temporal convolutions with different scales
        self.temporal_convs = nn.ModuleList()
        for kernel_size in kernel_sizes:
            conv = nn.Sequential(
                nn.Conv2d(1, n_filters_per_scale,
                         kernel_size=(1, kernel_size),
                         padding=(0, kernel_size // 2)),
                nn.BatchNorm2d(n_filters_per_scale),
                nn.ELU(),
                nn.Dropout(0.3)
            )
            self.temporal_convs.append(conv)

        # Depthwise spatial convolution (channel mixing)
        total_filters = n_filters_per_scale * self.n_scales
        self.spatial_conv = nn.Sequential(
            nn.Conv2d(total_filters, total_filters * 2,
                     kernel_size=(n_channels, 1),
                     groups=total_filters),
            nn.BatchNorm2d(total_filters * 2),
            nn.ELU(),
            nn.AvgPool2d((1, 4)),
            nn.Dropout(0.3)
        )

        # Additional pooling to reduce spatial dimension
        self.pool2 = nn.Sequential(
            nn.AvgPool2d((1, 8)),  # Further reduce: 500/4/8 = 15.625 ≈ 15
            nn.Dropout(0.3)
        )

        # Calculate output size after both pooling layers
        self.out_size = (n_samples // 4 // 8) * (total_filters * 2)  # ~15 * 128 = 1920

        # Feature projection
        self.projection = nn.Sequential(
            nn.Flatten(),
            nn.Linear(self.out_size, 128),
            nn.LayerNorm(128),
            nn.ELU(),
            nn.Dropout(0.4)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, 1, n_channels, n_samples)

        Returns:
            features: (batch, 128)
        """
        # Apply multi-scale temporal convolutions in parallel
        scale_outputs = []
        for conv in self.temporal_convs:
            out = conv(x)
            scale_outputs.append(out)

        # Concatenate multi-scale features along channel dimension
        x = torch.cat(scale_outputs, dim=1)  # (batch, n_scales*n_filters, n_channels, n_samples)

        # Spatial convolution
        x = self.spatial_conv(x)  # (batch, n_filters*2, 1, n_samples//4)

        # Additional pooling
        x = self.pool2(x)  # (batch, n_filters*2, 1, n_samples//4//8)

        # Project to feature vector
        features = self.projection(x)  # (batch, 128)

        return features


class SpectralBranch(nn.Module):
    """
    Process pre-extracted spectral features.

    Input: Spectral features (theta power, gamma power, PAC features, etc.)
    Output: Embedded spectral features
    """

    def __init__(self, n_spectral_features: int = 68):
        super().__init__()

        self.projection = nn.Sequential(
            nn.Linear(n_spectral_features, 128),
            nn.LayerNorm(128),
            nn.ELU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.LayerNorm(64),
            nn.ELU(),
            nn.Dropout(0.3)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, n_spectral_features)

        Returns:
            features: (batch, 64)
        """
        return self.projection(x)


class MultiHeadFeatureAttention(nn.Module):
    """
    Multi-head self-attention over concatenated features.

    Learns which features (temporal vs spectral) are most predictive.
    """

    def __init__(self, d_model: int = 192, n_heads: int = 4, dropout: float = 0.3):
        super().__init__()

        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"

        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads

        # Linear projections
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)

        self.fc_out = nn.Linear(d_model, d_model)

        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, d_model)

        Returns:
            attended: (batch, d_model)
        """
        batch_size = x.size(0)

        # Add sequence dimension for attention (treat as sequence of length 1)
        x = x.unsqueeze(1)  # (batch, 1, d_model)

        # Linear projections
        Q = self.W_q(x)  # (batch, 1, d_model)
        K = self.W_k(x)
        V = self.W_v(x)

        # Reshape for multi-head attention
        Q = Q.view(batch_size, 1, self.n_heads, self.d_k).transpose(1, 2)  # (batch, n_heads, 1, d_k)
        K = K.view(batch_size, 1, self.n_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, 1, self.n_heads, self.d_k).transpose(1, 2)

        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.d_k ** 0.5)  # (batch, n_heads, 1, 1)
        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)

        attn_output = torch.matmul(attn_weights, V)  # (batch, n_heads, 1, d_k)

        # Concatenate heads
        attn_output = attn_output.transpose(1, 2).contiguous()  # (batch, 1, n_heads, d_k)
        attn_output = attn_output.view(batch_size, 1, self.d_model)  # (batch, 1, d_model)

        # Final linear projection
        attn_output = self.fc_out(attn_output)  # (batch, 1, d_model)

        # Remove sequence dimension
        attn_output = attn_output.squeeze(1)  # (batch, d_model)

        # Residual connection and layer norm
        output = self.layer_norm(x.squeeze(1) + self.dropout(attn_output))

        return output


class SpecTempNet(nn.Module):
    """
    Hybrid Spectral-Temporal Network for PAC prediction.

    Architecture:
        Raw EEG → Multi-scale CNN → Temporal features (128)
        Spectral features → MLP → Spectral features (64)
        Concatenate → Attention → Regression head → PAC prediction

    Total parameters: ~180k
    """

    def __init__(self,
                 n_channels: int = 7,
                 n_samples: int = 500,
                 n_spectral_features: int = 68,
                 kernel_sizes: Tuple[int, ...] = (16, 32, 64, 128),
                 dropout: float = 0.4):
        super().__init__()

        # Branch 1: Multi-scale temporal CNN
        self.temporal_branch = MultiScaleTemporalCNN(
            n_channels=n_channels,
            n_samples=n_samples,
            kernel_sizes=kernel_sizes,
            n_filters_per_scale=16
        )

        # Branch 2: Spectral features
        self.spectral_branch = SpectralBranch(n_spectral_features=n_spectral_features)

        # Fusion: Multi-head attention
        combined_dim = 128 + 64  # Temporal + Spectral
        self.attention = MultiHeadFeatureAttention(d_model=combined_dim, n_heads=4, dropout=0.3)

        # Prediction head
        self.prediction_head = nn.Sequential(
            nn.Linear(combined_dim, 128),
            nn.LayerNorm(128),
            nn.ELU(),
            nn.Dropout(dropout),

            nn.Linear(128, 64),
            nn.LayerNorm(64),
            nn.ELU(),
            nn.Dropout(dropout),

            nn.Linear(64, 32),
            nn.LayerNorm(32),
            nn.ELU(),
            nn.Dropout(dropout),

            nn.Linear(32, 1)
        )

    def forward(self, eeg: torch.Tensor, spectral: torch.Tensor) -> torch.Tensor:
        """
        Args:
            eeg: (batch, 1, n_channels, n_samples) - Raw EEG
            spectral: (batch, n_spectral_features) - Pre-extracted spectral features

        Returns:
            pac_pred: (batch, 1) - Predicted PAC values
        """
        # Extract temporal features
        temporal_features = self.temporal_branch(eeg)  # (batch, 128)

        # Process spectral features
        spectral_features = self.spectral_branch(spectral)  # (batch, 64)

        # Concatenate features
        combined = torch.cat([temporal_features, spectral_features], dim=1)  # (batch, 192)

        # Apply attention
        attended = self.attention(combined)  # (batch, 192)

        # Predict PAC
        pac_pred = self.prediction_head(attended)  # (batch, 1)

        return pac_pred


def count_parameters(model: nn.Module) -> int:
    """Count trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def test_spectempnet():
    """Test the SpecTempNet architecture."""
    print("Testing SpecTempNet...")

    # Create model
    model = SpecTempNet(n_channels=7, n_samples=500, n_spectral_features=68)

    # Count parameters
    n_params = count_parameters(model)
    print(f"✓ Total parameters: {n_params:,}")
    print(f"✓ Model size: ~{n_params * 4 / 1024:.1f} KB")

    # Test forward pass
    batch_size = 32
    eeg = torch.randn(batch_size, 1, 7, 500)
    spectral = torch.randn(batch_size, 68)

    output = model(eeg, spectral)

    print(f"✓ Input EEG shape: {eeg.shape}")
    print(f"✓ Input spectral shape: {spectral.shape}")
    print(f"✓ Output shape: {output.shape}")
    print(f"✓ Output range: [{output.min():.4f}, {output.max():.4f}]")

    # Test on CUDA if available
    if torch.cuda.is_available():
        model = model.cuda()
        eeg = eeg.cuda()
        spectral = spectral.cuda()

        # Warm up
        for _ in range(10):
            _ = model(eeg, spectral)

        # Time forward pass
        import time
        torch.cuda.synchronize()
        start = time.time()
        n_runs = 100
        for _ in range(n_runs):
            _ = model(eeg, spectral)
        torch.cuda.synchronize()
        elapsed = time.time() - start

        print(f"✓ CUDA available: YES")
        print(f"✓ Time per batch ({batch_size} samples): {elapsed/n_runs*1000:.2f}ms")
        print(f"✓ Time per sample: {elapsed/n_runs/batch_size*1000:.2f}ms")

    print("✓ SpecTempNet test passed!")


if __name__ == "__main__":
    test_spectempnet()
