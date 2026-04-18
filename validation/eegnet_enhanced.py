"""
Enhanced EEGNet Architectures for PAC Prediction Capacity Experiments

Tests whether the R^2=0.287 performance ceiling of the original EEGNet (~2K params)
is due to under-parameterization by scaling up model capacity in two stages:

    EEGNetEnhanced (~35K params, ~24x original):
        - Longer temporal kernel (125 = 500ms, one full theta cycle at 4-8 Hz)
        - More temporal filters (F1=16 vs 8)
        - More pointwise filters (F2=32 vs 16)
        - 2-layer regression head with ELU nonlinearity

    EEGNetLarge (~141K params, ~97x original):
        - Even larger filter banks (F1=32, F2=64)
        - 3-layer regression head
        - Tests diminishing returns from additional capacity

If larger models converge to a similar R^2, this provides evidence that the
performance ceiling is a fundamental data limitation (epoch-level PAC labeling,
limited inter-subject variability) rather than a model capacity bottleneck.

Based on:
    Lawhern, V. J., et al. (2018). "EEGNet: a compact convolutional neural
    network for EEG-based brain-computer interfaces." Journal of Neural
    Engineering, 15(5), 056013.

Author: Amaar Chughtai
Date: February 2026
"""

import torch
import torch.nn as nn
from typing import Tuple


class EEGNetEnhanced(nn.Module):
    """
    Enhanced EEGNet with increased capacity (~35K parameters, ~24x original).

    Key differences from the original EEGNet (~2K params):
        - kernel_length=125 (500ms at 250 Hz = 1 full theta cycle at 4-8 Hz)
        - F1=16 temporal filters (2x original)
        - F2=32 pointwise filters (2x original)
        - 2-layer regression head with ELU nonlinearity and dropout

    Architecture:
        Block 1: Temporal conv (F1=16, kernel=125) + Depthwise spatial (D=2)
        Block 2: Separable conv (F2=32)
        Head:    Linear(flatten, 64) -> ELU -> Dropout(0.25) -> Linear(64, 1)

    Input Shape:
        (batch_size, 1, n_channels, n_samples)
        Default: (batch, 1, 7, 500)  # 7 frontal channels, 2s @ 250 Hz

    Output Shape:
        (batch_size, 1)  # Predicted PAC value

    Args:
        n_channels: Number of EEG channels (default 7 for frontal electrodes).
        n_samples: Number of temporal samples per window (default 500).
        F1: Number of temporal filters in Block 1 (default 16).
        D: Depth multiplier for spatial filters (default 2).
        F2: Number of pointwise filters in Block 2 (default 32).
        dropout: Dropout rate for conv blocks (default 0.5).
        kernel_length: Length of temporal convolution kernel (default 125).
        pool_size_1: Pooling size after Block 1 (default 4).
        pool_size_2: Pooling size after Block 2 (default 8).
    """

    def __init__(self,
                 n_channels: int = 7,
                 n_samples: int = 500,
                 F1: int = 16,
                 D: int = 2,
                 F2: int = 32,
                 dropout: float = 0.5,
                 kernel_length: int = 125,
                 pool_size_1: int = 4,
                 pool_size_2: int = 8):
        super(EEGNetEnhanced, self).__init__()

        self.n_channels = n_channels
        self.n_samples = n_samples
        self.F1 = F1
        self.D = D
        self.F2 = F2

        # =====================================================================
        # BLOCK 1: Temporal and Spatial Feature Extraction
        # =====================================================================

        # Temporal convolution: kernel_length=125 captures a full theta cycle
        # (4-8 Hz -> period 125-250ms -> 125 samples at 250 Hz covers 500ms)
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

        # Depthwise spatial convolution: learn spatial filters per temporal feature
        # Input: (batch, F1, n_channels, n_samples)
        # Output: (batch, F1*D, 1, n_samples)
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

        # =====================================================================
        # BLOCK 2: Separable Convolution
        # =====================================================================

        # Depthwise temporal convolution
        self.separable_conv1 = nn.Conv2d(
            in_channels=F1 * D,
            out_channels=F1 * D,
            kernel_size=(1, 16),
            padding=(0, 8),
            groups=F1 * D,
            bias=False
        )
        # Pointwise convolution
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

        # =====================================================================
        # OUTPUT LAYER: 2-Layer Regression Head
        # =====================================================================

        # Flattened feature size after convolutions and pooling
        flatten_size = F2 * (n_samples // (pool_size_1 * pool_size_2))

        self.head = nn.Sequential(
            nn.Linear(flatten_size, 64),
            nn.ELU(),
            nn.Dropout(0.25),
            nn.Linear(64, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through EEGNetEnhanced.

        Args:
            x: Input EEG tensor of shape (batch, 1, n_channels, n_samples).

        Returns:
            Predicted PAC values of shape (batch, 1).
        """
        # Block 1: Temporal + Spatial
        x = self.conv1(x)
        x = self.batchnorm1(x)
        x = self.depthwise(x)
        x = self.batchnorm2(x)
        x = self.elu1(x)
        x = self.pool1(x)
        x = self.dropout1(x)

        # Block 2: Separable Convolution
        x = self.separable_conv1(x)
        x = self.separable_conv2(x)
        x = self.batchnorm3(x)
        x = self.elu2(x)
        x = self.pool2(x)
        x = self.dropout2(x)

        # Flatten + regression head
        x = x.flatten(1)
        pac_pred = self.head(x)

        return pac_pred

    def get_feature_maps(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Extract intermediate feature maps for visualization.

        Args:
            x: Input EEG tensor.

        Returns:
            block1_features: Features after Block 1 (temporal+spatial).
            block2_features: Features after Block 2 (separable conv).
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


class EEGNetLarge(nn.Module):
    """
    Large EEGNet with ~141K parameters for capacity ceiling experiments.

    Key differences from EEGNetEnhanced:
        - F1=32 temporal filters (4x original)
        - F2=64 pointwise filters (4x original)
        - 3-layer regression head: flatten -> 128 -> 64 -> 1

    This model deliberately over-parameterizes for a dataset of ~17K windows
    to test whether additional capacity yields diminishing returns,
    providing evidence for a fundamental data limitation ceiling.

    Architecture:
        Block 1: Temporal conv (F1=32, kernel=125) + Depthwise spatial (D=2)
        Block 2: Separable conv (F2=64)
        Head:    Linear(flatten, 128) -> ELU -> Dropout(0.3)
                 -> Linear(128, 64) -> ELU -> Dropout(0.3)
                 -> Linear(64, 1)

    Input Shape:
        (batch_size, 1, n_channels, n_samples)
        Default: (batch, 1, 7, 500)

    Output Shape:
        (batch_size, 1)

    Args:
        n_channels: Number of EEG channels (default 7).
        n_samples: Number of temporal samples per window (default 500).
        F1: Number of temporal filters in Block 1 (default 32).
        D: Depth multiplier for spatial filters (default 2).
        F2: Number of pointwise filters in Block 2 (default 64).
        dropout: Dropout rate for conv blocks (default 0.5).
        kernel_length: Length of temporal convolution kernel (default 125).
        pool_size_1: Pooling size after Block 1 (default 4).
        pool_size_2: Pooling size after Block 2 (default 8).
    """

    def __init__(self,
                 n_channels: int = 7,
                 n_samples: int = 500,
                 F1: int = 32,
                 D: int = 2,
                 F2: int = 64,
                 dropout: float = 0.5,
                 kernel_length: int = 125,
                 pool_size_1: int = 4,
                 pool_size_2: int = 8):
        super(EEGNetLarge, self).__init__()

        self.n_channels = n_channels
        self.n_samples = n_samples
        self.F1 = F1
        self.D = D
        self.F2 = F2

        # =====================================================================
        # BLOCK 1: Temporal and Spatial Feature Extraction
        # =====================================================================

        self.conv1 = nn.Conv2d(
            in_channels=1,
            out_channels=F1,
            kernel_size=(1, kernel_length),
            padding=(0, kernel_length // 2),
            bias=False
        )
        self.batchnorm1 = nn.BatchNorm2d(F1)

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

        # =====================================================================
        # BLOCK 2: Separable Convolution
        # =====================================================================

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

        # =====================================================================
        # OUTPUT LAYER: 3-Layer Regression Head
        # =====================================================================

        flatten_size = F2 * (n_samples // (pool_size_1 * pool_size_2))

        self.head = nn.Sequential(
            nn.Linear(flatten_size, 128),
            nn.ELU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ELU(),
            nn.Dropout(0.3),
            nn.Linear(64, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through EEGNetLarge.

        Args:
            x: Input EEG tensor of shape (batch, 1, n_channels, n_samples).

        Returns:
            Predicted PAC values of shape (batch, 1).
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

        # Flatten + regression head
        x = x.flatten(1)
        pac_pred = self.head(x)

        return pac_pred

    def get_feature_maps(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Extract intermediate feature maps for visualization.

        Args:
            x: Input EEG tensor.

        Returns:
            block1_features: Features after Block 1.
            block2_features: Features after Block 2.
        """
        x = self.conv1(x)
        x = self.batchnorm1(x)
        x = self.depthwise(x)
        x = self.batchnorm2(x)
        x = self.elu1(x)
        x = self.pool1(x)
        block1_features = x.clone()

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
        model: PyTorch model.

    Returns:
        Number of trainable parameters.
    """
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def _print_layer_params(model: nn.Module) -> None:
    """
    Print per-layer parameter counts for a model.

    Args:
        model: PyTorch model.
    """
    for name, param in model.named_parameters():
        if param.requires_grad:
            print(f"  {name:45s}  {param.numel():>8,}  {list(param.shape)}")


def test_eegnet_enhanced() -> None:
    """Test EEGNetEnhanced with example input and print architecture details."""
    print("=" * 70)
    print("EEGNetEnhanced Architecture Test (~35K params)")
    print("=" * 70)

    model = EEGNetEnhanced(
        n_channels=7,
        n_samples=500,
        F1=16,
        D=2,
        F2=32,
        dropout=0.5,
        kernel_length=125,
    )

    n_params = count_parameters(model)
    print(f"\nTotal trainable parameters: {n_params:,}")
    print(f"Target: ~35K parameters (24x original EEGNet)")
    print(f"\nPer-layer breakdown:")
    _print_layer_params(model)

    # Test forward pass
    batch_size = 16
    dummy_input = torch.randn(batch_size, 1, 7, 500)
    print(f"\nInput shape:  {dummy_input.shape}")
    print(f"  (batch_size=16, 1, n_channels=7, n_samples=500)")

    model.eval()
    with torch.no_grad():
        output = model(dummy_input)

    print(f"Output shape: {output.shape}")
    print(f"  Expected:   ({batch_size}, 1)")

    print(f"\nPredicted PAC values (first 5 samples):")
    for i in range(min(5, batch_size)):
        print(f"  Sample {i + 1}: {output[i].item():.6f}")

    # Test feature extraction
    block1_feat, block2_feat = model.get_feature_maps(dummy_input)
    print(f"\nFeature map shapes:")
    print(f"  Block 1 (temporal+spatial): {block1_feat.shape}")
    print(f"  Block 2 (separable):        {block2_feat.shape}")

    print("\n" + "=" * 70)
    print("EEGNetEnhanced test completed successfully!")
    print("=" * 70)


def test_eegnet_large() -> None:
    """Test EEGNetLarge with example input and print architecture details."""
    print("\n" + "=" * 70)
    print("EEGNetLarge Architecture Test (~141K params)")
    print("=" * 70)

    model = EEGNetLarge(
        n_channels=7,
        n_samples=500,
        F1=32,
        D=2,
        F2=64,
        dropout=0.5,
        kernel_length=125,
    )

    n_params = count_parameters(model)
    print(f"\nTotal trainable parameters: {n_params:,}")
    print(f"Target: ~141K parameters (97x original EEGNet)")
    print(f"\nPer-layer breakdown:")
    _print_layer_params(model)

    # Test forward pass
    batch_size = 16
    dummy_input = torch.randn(batch_size, 1, 7, 500)
    print(f"\nInput shape:  {dummy_input.shape}")
    print(f"  (batch_size=16, 1, n_channels=7, n_samples=500)")

    model.eval()
    with torch.no_grad():
        output = model(dummy_input)

    print(f"Output shape: {output.shape}")
    print(f"  Expected:   ({batch_size}, 1)")

    print(f"\nPredicted PAC values (first 5 samples):")
    for i in range(min(5, batch_size)):
        print(f"  Sample {i + 1}: {output[i].item():.6f}")

    # Test feature extraction
    block1_feat, block2_feat = model.get_feature_maps(dummy_input)
    print(f"\nFeature map shapes:")
    print(f"  Block 1 (temporal+spatial): {block1_feat.shape}")
    print(f"  Block 2 (separable):        {block2_feat.shape}")

    print("\n" + "=" * 70)
    print("EEGNetLarge test completed successfully!")
    print("=" * 70)


def test_all() -> None:
    """Run all architecture tests and print comparative summary."""
    # Import original EEGNet for comparison
    import sys
    import os
    src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
    sys.path.insert(0, src_dir)
    from eegnet import EEGNet

    test_eegnet_enhanced()
    test_eegnet_large()

    # Comparative summary
    print("\n" + "=" * 70)
    print("COMPARATIVE SUMMARY")
    print("=" * 70)

    original = EEGNet(n_channels=7, n_samples=500)
    enhanced = EEGNetEnhanced(n_channels=7, n_samples=500)
    large = EEGNetLarge(n_channels=7, n_samples=500)

    models = {
        "EEGNet (original)": original,
        "EEGNetEnhanced":    enhanced,
        "EEGNetLarge":       large,
    }

    print(f"\n{'Model':<25s}  {'Parameters':>12s}  {'Multiplier':>10s}")
    print("-" * 50)
    original_params = count_parameters(original)
    for name, model in models.items():
        n_params = count_parameters(model)
        multiplier = n_params / original_params
        print(f"{name:<25s}  {n_params:>12,}  {multiplier:>9.1f}x")

    print(f"\nAll models accept input shape: (batch, 1, 7, 500)")
    print(f"All models produce output shape: (batch, 1)")
    print("=" * 70)


if __name__ == "__main__":
    test_all()
