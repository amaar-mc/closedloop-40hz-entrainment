"""
EEGNet Architecture for PAC Prediction

Implements compact convolutional neural network for EEG-based prediction of
theta-gamma phase-amplitude coupling (PAC).

Based on:
    Lawhern, V. J., et al. (2018). "EEGNet: a compact convolutional neural
    network for EEG-based brain-computer interfaces." Journal of Neural
    Engineering, 15(5), 056013.

Modifications:
    - Output changed from classification to regression (PAC prediction)
    - Input configured for 7 frontal channels @ 250 Hz (500 samples = 2 seconds)
    - Added batch normalization for training stability
    - Dropout rate tuned for PAC regression task

Author: Amaar Chughtai
Date: February 2026
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional


class EEGNet(nn.Module):
    """
    Compact CNN architecture for EEG-based PAC regression.

    Architecture:
        Block 1: Temporal convolution + Depthwise spatial convolution
        Block 2: Separable convolution
        Output: Fully connected regression head

    Input Shape:
        (batch_size, 1, n_channels, n_samples)
        Default: (batch, 1, 7, 500)  # 7 channels, 2 seconds @ 250 Hz

    Output Shape:
        (batch_size, 1)  # Predicted PAC value

    Parameters:
        ~2000 trainable parameters (prevents overfitting with limited data)

    Args:
        n_channels: Number of EEG channels (default 7 for frontal electrodes)
        n_samples: Number of temporal samples per window (default 500)
        F1: Number of temporal filters in Block 1 (default 8)
        D: Depth multiplier for spatial filters (default 2)
        F2: Number of pointwise filters in Block 2 (default 16)
        dropout: Dropout rate for regularization (default 0.5)
        kernel_length: Length of temporal convolution kernel (default 64)
        pool_size_1: Pooling size after Block 1 (default 4)
        pool_size_2: Pooling size after Block 2 (default 8)
    """

    def __init__(self,
                 n_channels: int = 7,
                 n_samples: int = 500,
                 F1: int = 8,
                 D: int = 2,
                 F2: int = 16,
                 dropout: float = 0.5,
                 kernel_length: int = 64,
                 pool_size_1: int = 4,
                 pool_size_2: int = 8):
        super(EEGNet, self).__init__()

        self.n_channels = n_channels
        self.n_samples = n_samples
        self.F1 = F1
        self.D = D
        self.F2 = F2

        # =====================================================================
        # BLOCK 1: Temporal and Spatial Feature Extraction
        # =====================================================================

        # Temporal convolution: Learn frequency-specific patterns
        # Input: (batch, 1, n_channels, n_samples)
        # Output: (batch, F1, n_channels, n_samples)
        self.conv1 = nn.Conv2d(
            in_channels=1,
            out_channels=F1,
            kernel_size=(1, kernel_length),
            padding=(0, kernel_length // 2),
            bias=False
        )
        self.batchnorm1 = nn.BatchNorm2d(F1)

        # Depthwise spatial convolution: Learn spatial filters
        # (One spatial filter per temporal feature)
        # Input: (batch, F1, n_channels, n_samples)
        # Output: (batch, F1*D, 1, n_samples)
        self.depthwise = nn.Conv2d(
            in_channels=F1,
            out_channels=F1 * D,
            kernel_size=(n_channels, 1),
            groups=F1,  # Depthwise: each input channel has its own filter
            bias=False
        )
        self.batchnorm2 = nn.BatchNorm2d(F1 * D)

        # ELU activation (better than ReLU for EEG)
        self.elu1 = nn.ELU()

        # Average pooling: Reduce temporal dimension
        self.pool1 = nn.AvgPool2d((1, pool_size_1))

        # Dropout for regularization
        self.dropout1 = nn.Dropout(dropout)

        # =====================================================================
        # BLOCK 2: Separable Convolution
        # =====================================================================

        # Separable convolution: Further temporal feature extraction
        # Implemented as depthwise + pointwise convolutions
        self.separable_conv1 = nn.Conv2d(
            in_channels=F1 * D,
            out_channels=F1 * D,
            kernel_size=(1, 16),
            padding=(0, 8),
            groups=F1 * D,  # Depthwise
            bias=False
        )
        self.separable_conv2 = nn.Conv2d(
            in_channels=F1 * D,
            out_channels=F2,
            kernel_size=(1, 1),  # Pointwise
            bias=False
        )
        self.batchnorm3 = nn.BatchNorm2d(F2)

        self.elu2 = nn.ELU()
        self.pool2 = nn.AvgPool2d((1, pool_size_2))
        self.dropout2 = nn.Dropout(dropout)

        # =====================================================================
        # OUTPUT LAYER: Regression Head
        # =====================================================================

        # Calculate flattened size after convolutions and pooling
        # After pool1: n_samples // pool_size_1
        # After pool2: (n_samples // pool_size_1) // pool_size_2
        flatten_size = F2 * (n_samples // (pool_size_1 * pool_size_2))

        # Fully connected layer for PAC prediction
        self.fc = nn.Linear(flatten_size, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through EEGNet.

        Args:
            x: Input EEG tensor of shape (batch, 1, n_channels, n_samples)

        Returns:
            pac_pred: Predicted PAC values of shape (batch, 1)
        """
        # BLOCK 1: Temporal + Spatial Feature Extraction
        x = self.conv1(x)           # (batch, F1, n_channels, n_samples)
        x = self.batchnorm1(x)

        x = self.depthwise(x)       # (batch, F1*D, 1, n_samples)
        x = self.batchnorm2(x)
        x = self.elu1(x)

        x = self.pool1(x)           # (batch, F1*D, 1, n_samples//4)
        x = self.dropout1(x)

        # BLOCK 2: Separable Convolution
        x = self.separable_conv1(x) # (batch, F1*D, 1, n_samples//4)
        x = self.separable_conv2(x) # (batch, F2, 1, n_samples//4)
        x = self.batchnorm3(x)
        x = self.elu2(x)

        x = self.pool2(x)           # (batch, F2, 1, n_samples//32)
        x = self.dropout2(x)

        # Flatten
        x = x.flatten(1)            # (batch, F2 * n_samples//32)

        # Regression output
        pac_pred = self.fc(x)       # (batch, 1)

        return pac_pred

    def get_feature_maps(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Extract intermediate feature maps for visualization.

        Args:
            x: Input EEG tensor

        Returns:
            block1_features: Features after Block 1 (temporal+spatial)
            block2_features: Features after Block 2 (separable conv)
        """
        # Block 1
        x = self.conv1(x)
        x = self.batchnorm1(x)
        x = self.depthwise(x)
        x = self.batchnorm2(x)
        x = self.elu1(x)
        x = self.pool1(x)
        block1_features = x.clone()

        # Block 2
        x = self.dropout1(x)
        x = self.separable_conv1(x)
        x = self.separable_conv2(x)
        x = self.batchnorm3(x)
        x = self.elu2(x)
        x = self.pool2(x)
        block2_features = x.clone()

        return block1_features, block2_features


def count_parameters(model: nn.Module) -> int:
    """
    Count number of trainable parameters in model.

    Args:
        model: PyTorch model

    Returns:
        count: Number of trainable parameters
    """
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def test_eegnet():
    """Test EEGNet with example input."""
    print("=" * 60)
    print("EEGNet Architecture Test")
    print("=" * 60)

    # Create model
    model = EEGNet(
        n_channels=7,
        n_samples=500,
        F1=8,
        D=2,
        F2=16,
        dropout=0.5
    )

    # Count parameters
    n_params = count_parameters(model)
    print(f"\nTotal trainable parameters: {n_params:,}")
    print(f"Expected: ~2000 parameters")

    # Test forward pass
    batch_size = 16
    dummy_input = torch.randn(batch_size, 1, 7, 500)
    print(f"\nInput shape: {dummy_input.shape}")
    print(f"  (batch_size, channels, n_channels, n_samples)")

    model.eval()
    with torch.no_grad():
        output = model(dummy_input)

    print(f"\nOutput shape: {output.shape}")
    print(f"  Expected: ({batch_size}, 1)")

    print(f"\nPredicted PAC values (first 5 samples):")
    for i in range(min(5, batch_size)):
        print(f"  Sample {i+1}: {output[i].item():.4f}")

    # Test feature extraction
    block1_feat, block2_feat = model.get_feature_maps(dummy_input)
    print(f"\nFeature map shapes:")
    print(f"  Block 1 (temporal+spatial): {block1_feat.shape}")
    print(f"  Block 2 (separable): {block2_feat.shape}")

    print("\n" + "=" * 60)
    print("EEGNet test completed successfully!")
    print("=" * 60)

    return model


if __name__ == "__main__":
    # Run test
    model = test_eegnet()

    # Print model architecture
    print("\n" + "=" * 60)
    print("Model Architecture Summary")
    print("=" * 60)
    print(model)
