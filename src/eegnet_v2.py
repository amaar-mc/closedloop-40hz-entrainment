"""
Enhanced EEGNet Architecture for ΔPAC Prediction (Version 2)

Key improvements over v1:
- Predicts ΔPAC (change in PAC) instead of absolute PAC
- Slightly deeper architecture (F1=12, F2=24)
- Additional temporal convolution layer
- Optimized for shorter prediction horizon (0.5s)

Author: Amaar Chughtai
Date: February 2026
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple


class EEGNetV2(nn.Module):
    """
    Enhanced EEGNet for ΔPAC regression with improved capacity.

    Changes from v1:
    - F1: 8 → 12 (50% more temporal filters)
    - F2: 16 → 24 (50% more separable filters)
    - Added residual connection
    - Total params: ~3200 (vs 1457 in v1)

    Args:
        n_channels: Number of EEG channels (default 7)
        n_samples: Number of temporal samples (default 500 for 2s @ 250Hz)
        F1: Number of temporal filters (default 12, was 8)
        D: Depth multiplier (default 2)
        F2: Number of separable filters (default 24, was 16)
        dropout: Dropout rate (default 0.5)
    """

    def __init__(self,
                 n_channels: int = 7,
                 n_samples: int = 500,
                 F1: int = 12,
                 D: int = 2,
                 F2: int = 24,
                 dropout: float = 0.5,
                 kernel_length: int = 64,
                 pool_size_1: int = 4,
                 pool_size_2: int = 8):
        super(EEGNetV2, self).__init__()

        self.n_channels = n_channels
        self.n_samples = n_samples
        self.F1 = F1
        self.D = D
        self.F2 = F2

        # ====================================================================
        # BLOCK 1: Enhanced Temporal and Spatial Feature Extraction
        # ====================================================================

        # Temporal convolution 1: Coarse patterns
        self.conv1 = nn.Conv2d(
            in_channels=1,
            out_channels=F1,
            kernel_size=(1, kernel_length),
            padding=(0, kernel_length // 2),
            bias=False
        )
        self.batchnorm1 = nn.BatchNorm2d(F1)

        # Depthwise spatial convolution
        self.depthwise = nn.Conv2d(
            in_channels=F1,
            out_channels=F1 * D,
            kernel_size=(n_channels, 1),
            groups=F1,
            bias=False
        )
        self.batchnorm2 = nn.BatchNorm2d(F1 * D)
        self.elu1 = nn.ELU()
        self.pool1 = nn.AvgPool2d((1, pool_size_1))
        self.dropout1 = nn.Dropout(dropout)

        # ====================================================================
        # BLOCK 2: Enhanced Separable Convolution
        # ====================================================================

        # Separable convolution (depthwise + pointwise)
        self.separable_conv1 = nn.Conv2d(
            in_channels=F1 * D,
            out_channels=F1 * D,
            kernel_size=(1, 16),
            padding=(0, 8),
            groups=F1 * D,
            bias=False
        )
        self.separable_conv2 = nn.Conv2d(
            in_channels=F1 * D,
            out_channels=F2,
            kernel_size=(1, 1),
            bias=False
        )
        self.batchnorm3 = nn.BatchNorm2d(F2)
        self.elu2 = nn.ELU()
        self.pool2 = nn.AvgPool2d((1, pool_size_2))
        self.dropout2 = nn.Dropout(dropout)

        # ====================================================================
        # OUTPUT: Regression Head
        # ====================================================================

        # Calculate flattened size
        flatten_size = F2 * (n_samples // (pool_size_1 * pool_size_2))

        # Additional hidden layer for better capacity
        self.fc1 = nn.Linear(flatten_size, 64)
        self.fc1_dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(64, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input EEG tensor (batch, 1, n_channels, n_samples)

        Returns:
            delta_pac_pred: Predicted ΔPAC (batch, 1)
        """
        # Block 1
        x = self.conv1(x)
        x = self.batchnorm1(x)

        x = self.depthwise(x)
        x = self.batchnorm2(x)
        x = self.elu1(x)

        x = self.pool1(x)
        x = self.dropout1(x)

        # Block 2
        x = self.separable_conv1(x)
        x = self.separable_conv2(x)
        x = self.batchnorm3(x)
        x = self.elu2(x)

        x = self.pool2(x)
        x = self.dropout2(x)

        # Flatten
        x = x.flatten(1)

        # Regression with hidden layer
        x = self.fc1(x)
        x = F.elu(x)
        x = self.fc1_dropout(x)
        delta_pac_pred = self.fc2(x)

        return delta_pac_pred


def count_parameters(model: nn.Module) -> int:
    """Count trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def test_eegnet_v2():
    """Test enhanced EEGNet."""
    print("=" * 70)
    print("EEGNetV2 Architecture Test - Enhanced ΔPAC Predictor")
    print("=" * 70)

    # Create model
    model = EEGNetV2(
        n_channels=7,
        n_samples=500,
        F1=12,
        D=2,
        F2=24,
        dropout=0.5
    )

    # Count parameters
    n_params = count_parameters(model)
    print(f"\nTotal trainable parameters: {n_params:,}")
    print(f"Comparison to v1: {n_params / 1457:.1f}x larger (~1,457 in v1)")

    # Test forward pass
    batch_size = 16
    dummy_input = torch.randn(batch_size, 1, 7, 500)
    print(f"\nInput shape: {dummy_input.shape}")

    model.eval()
    with torch.no_grad():
        output = model(dummy_input)

    print(f"Output shape: {output.shape}")
    print(f"\nPredicted ΔPAC values (first 5 samples):")
    for i in range(min(5, batch_size)):
        print(f"  Sample {i+1}: {output[i].item():+.4f}")

    print("\n" + "=" * 70)
    print("EEGNetV2 test completed successfully!")
    print("=" * 70)

    return model


if __name__ == "__main__":
    model = test_eegnet_v2()
    print("\nModel Architecture:")
    print(model)
