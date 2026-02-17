"""
Temporal PAC Prediction Models

LSTM and GRU architectures for predicting future PAC from EEG history.

Architecture overview:
    1. SpatialEncoder: Lightweight CNN that encodes each 2-sec EEG window
       into a compact feature vector (7ch × 500 samples → 32-dim embedding)
    2. TemporalPredictor: LSTM/GRU that processes the sequence of embeddings
       (+ spectral features + PAC history) to predict future PAC

Design principles:
    - Small model (<30k parameters) to prevent overfitting on ~10k sequences
    - Bidirectional LSTM for capturing both past→future and contextual patterns
    - PAC history as direct input (autoregressive component)
    - Layer normalization for training stability
    - Multi-horizon capable (predict 1, 3, 5, 10 seconds ahead)

Author: Amaar Chughtai
Date: February 2026
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, Tuple


class SpatialEncoder(nn.Module):
    """
    Lightweight spatial encoder for individual EEG windows.

    Reduces (7, 500) → (spatial_dim,) per window using depthwise-separable
    convolutions (inspired by EEGNet but much smaller).

    Parameters: ~2k
    """

    def __init__(self, n_channels: int = 7, n_samples: int = 500,
                 spatial_dim: int = 32, dropout: float = 0.3):
        super().__init__()
        self.spatial_dim = spatial_dim

        # Temporal convolution: capture frequency patterns
        self.temporal_conv = nn.Sequential(
            nn.Conv1d(n_channels, 16, kernel_size=25, padding=12),
            nn.BatchNorm1d(16),
            nn.ELU(),
            nn.AvgPool1d(4),  # 500 → 125
            nn.Dropout(dropout),
        )

        # Depthwise spatial convolution
        self.spatial_conv = nn.Sequential(
            nn.Conv1d(16, 32, kernel_size=15, padding=7, groups=16),
            nn.BatchNorm1d(32),
            nn.ELU(),
            nn.AvgPool1d(5),  # 125 → 25
            nn.Dropout(dropout),
        )

        # Global average pooling → spatial_dim
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        self.projection = nn.Linear(32, spatial_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, n_channels, n_samples) single EEG window

        Returns:
            embedding: (batch, spatial_dim)
        """
        out = self.temporal_conv(x)     # (batch, 16, 125)
        out = self.spatial_conv(out)     # (batch, 32, 25)
        out = self.global_pool(out)      # (batch, 32, 1)
        out = out.squeeze(2)             # (batch, 32)
        out = self.projection(out)       # (batch, spatial_dim)
        return out


class TemporalPACPredictor(nn.Module):
    """
    LSTM-based temporal predictor for future PAC values.

    Takes a sequence of EEG embeddings + PAC history and predicts
    PAC at a future time step.

    Architecture:
        For each timestep t in [0, lookback):
            feature_t = [spatial_encoder(eeg_t), spectral_t, pac_t]
        lstm_input = stack(feature_0, ..., feature_{lookback-1})
        lstm_out = LSTM(lstm_input)
        pac_future = regression_head(lstm_out[-1])

    Total parameters: ~15-25k (varies with config)
    """

    def __init__(self,
                 n_channels: int = 7,
                 n_samples: int = 500,
                 n_spectral_features: int = 61,
                 spatial_dim: int = 32,
                 lstm_hidden: int = 64,
                 lstm_layers: int = 2,
                 dropout: float = 0.3,
                 bidirectional: bool = True,
                 use_spectral: bool = True,
                 use_gru: bool = False):
        """
        Args:
            n_channels: Number of EEG channels
            n_samples: Samples per window (500 for 2-sec @ 250Hz)
            n_spectral_features: Number of spectral features (61)
            spatial_dim: Dimensionality of spatial encoder output
            lstm_hidden: LSTM hidden state size
            lstm_layers: Number of LSTM layers
            dropout: Dropout rate
            bidirectional: Use bidirectional LSTM
            use_spectral: Include spectral features in input
            use_gru: Use GRU instead of LSTM
        """
        super().__init__()

        self.use_spectral = use_spectral
        self.bidirectional = bidirectional
        self.lstm_hidden = lstm_hidden
        self.lstm_layers = lstm_layers

        # Spatial encoder for raw EEG
        self.spatial_encoder = SpatialEncoder(
            n_channels=n_channels,
            n_samples=n_samples,
            spatial_dim=spatial_dim,
            dropout=dropout
        )

        # Compute input dimension for LSTM
        # spatial_dim (EEG embedding) + 1 (PAC history) + optional spectral
        input_dim = spatial_dim + 1  # +1 for PAC history value
        if use_spectral:
            input_dim += n_spectral_features

        # Input projection with layer norm
        self.input_proj = nn.Sequential(
            nn.Linear(input_dim, lstm_hidden),
            nn.LayerNorm(lstm_hidden),
            nn.ELU(),
            nn.Dropout(dropout),
        )

        # LSTM or GRU
        RNN = nn.GRU if use_gru else nn.LSTM
        self.rnn = RNN(
            input_size=lstm_hidden,
            hidden_size=lstm_hidden,
            num_layers=lstm_layers,
            dropout=dropout if lstm_layers > 1 else 0,
            bidirectional=bidirectional,
            batch_first=True,
        )

        # Output dimension depends on bidirectional
        rnn_out_dim = lstm_hidden * (2 if bidirectional else 1)

        # Regression head
        self.regression_head = nn.Sequential(
            nn.Linear(rnn_out_dim, 64),
            nn.LayerNorm(64),
            nn.ELU(),
            nn.Dropout(dropout),
            nn.Linear(64, 32),
            nn.LayerNorm(32),
            nn.ELU(),
            nn.Dropout(dropout / 2),
            nn.Linear(32, 1),
        )

    def forward(self, batch: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Args:
            batch: Dictionary with keys:
                'eeg':         (B, lookback, 7, 500) - EEG history
                'pac_history': (B, lookback) - PAC history
                'spectral':    (B, lookback, 61) - optional spectral features

        Returns:
            pac_pred: (B, 1) - Predicted future PAC value
        """
        eeg = batch['eeg']               # (B, L, 7, 500)
        pac_hist = batch['pac_history']   # (B, L)

        B, L, C, S = eeg.shape

        # Encode each EEG window through spatial encoder
        # Reshape: (B*L, C, S)
        eeg_flat = eeg.reshape(B * L, C, S)
        spatial_embeddings = self.spatial_encoder(eeg_flat)  # (B*L, spatial_dim)
        spatial_embeddings = spatial_embeddings.reshape(B, L, -1)  # (B, L, spatial_dim)

        # Build per-timestep feature vectors
        # [spatial_embedding, pac_value, (optional) spectral_features]
        features = [
            spatial_embeddings,            # (B, L, spatial_dim)
            pac_hist.unsqueeze(2),         # (B, L, 1)
        ]

        if self.use_spectral and 'spectral' in batch:
            features.append(batch['spectral'])  # (B, L, 61)

        # Concatenate features per timestep
        combined = torch.cat(features, dim=2)  # (B, L, input_dim)

        # Project to LSTM input space
        projected = self.input_proj(combined)  # (B, L, lstm_hidden)

        # LSTM forward pass
        rnn_out, _ = self.rnn(projected)  # (B, L, rnn_out_dim)

        # Use the last timestep output for prediction
        last_output = rnn_out[:, -1, :]  # (B, rnn_out_dim)

        # Regression head
        pac_pred = self.regression_head(last_output)  # (B, 1)

        return pac_pred

    def count_parameters(self) -> int:
        """Count total trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def count_parameters_by_component(self) -> Dict[str, int]:
        """Count parameters per component."""
        components = {
            'spatial_encoder': sum(p.numel() for p in self.spatial_encoder.parameters()),
            'input_proj': sum(p.numel() for p in self.input_proj.parameters()),
            'rnn': sum(p.numel() for p in self.rnn.parameters()),
            'regression_head': sum(p.numel() for p in self.regression_head.parameters()),
        }
        components['total'] = sum(components.values())
        return components


class MultiHorizonPredictor(nn.Module):
    """
    Extension: Predict PAC at multiple future horizons simultaneously.

    Shares the same encoder + LSTM backbone but has separate prediction
    heads for different horizons (e.g., 1, 3, 5, 10 seconds ahead).

    This enables the closed-loop controller to plan ahead at multiple
    time scales.
    """

    def __init__(self,
                 horizons: list = [1, 3, 5, 10],
                 **kwargs):
        super().__init__()
        self.horizons = horizons

        # Shared backbone (same as TemporalPACPredictor minus regression head)
        self.spatial_encoder = SpatialEncoder(
            n_channels=kwargs.get('n_channels', 7),
            n_samples=kwargs.get('n_samples', 500),
            spatial_dim=kwargs.get('spatial_dim', 32),
            dropout=kwargs.get('dropout', 0.3),
        )

        use_spectral = kwargs.get('use_spectral', True)
        n_spectral = kwargs.get('n_spectral_features', 61) if use_spectral else 0
        spatial_dim = kwargs.get('spatial_dim', 32)
        lstm_hidden = kwargs.get('lstm_hidden', 64)
        lstm_layers = kwargs.get('lstm_layers', 2)
        dropout = kwargs.get('dropout', 0.3)
        bidirectional = kwargs.get('bidirectional', True)

        input_dim = spatial_dim + 1 + n_spectral
        self.use_spectral = use_spectral

        self.input_proj = nn.Sequential(
            nn.Linear(input_dim, lstm_hidden),
            nn.LayerNorm(lstm_hidden),
            nn.ELU(),
            nn.Dropout(dropout),
        )

        self.rnn = nn.LSTM(
            input_size=lstm_hidden,
            hidden_size=lstm_hidden,
            num_layers=lstm_layers,
            dropout=dropout if lstm_layers > 1 else 0,
            bidirectional=bidirectional,
            batch_first=True,
        )

        rnn_out_dim = lstm_hidden * (2 if bidirectional else 1)

        # Separate heads per horizon
        self.heads = nn.ModuleDict()
        for h in horizons:
            self.heads[f'h{h}'] = nn.Sequential(
                nn.Linear(rnn_out_dim, 32),
                nn.LayerNorm(32),
                nn.ELU(),
                nn.Dropout(dropout / 2),
                nn.Linear(32, 1),
            )

    def forward(self, batch: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """Returns dict mapping horizon → prediction."""
        eeg = batch['eeg']
        pac_hist = batch['pac_history']
        B, L, C, S = eeg.shape

        eeg_flat = eeg.reshape(B * L, C, S)
        spatial = self.spatial_encoder(eeg_flat).reshape(B, L, -1)

        features = [spatial, pac_hist.unsqueeze(2)]
        if self.use_spectral and 'spectral' in batch:
            features.append(batch['spectral'])

        combined = torch.cat(features, dim=2)
        projected = self.input_proj(combined)
        rnn_out, _ = self.rnn(projected)
        last = rnn_out[:, -1, :]

        predictions = {}
        for h in self.horizons:
            predictions[f'h{h}'] = self.heads[f'h{h}'](last)

        return predictions


def test_temporal_model():
    """Test the temporal prediction model."""
    print("=" * 60)
    print("TESTING TEMPORAL PAC PREDICTOR")
    print("=" * 60)

    # Create model
    model = TemporalPACPredictor(
        n_channels=7,
        n_samples=500,
        n_spectral_features=61,
        spatial_dim=32,
        lstm_hidden=64,
        lstm_layers=2,
        dropout=0.3,
        bidirectional=True,
        use_spectral=True,
    )

    # Parameter count
    param_counts = model.count_parameters_by_component()
    print(f"\nParameter counts:")
    for name, count in param_counts.items():
        print(f"  {name}: {count:,}")
    print(f"  Total: {model.count_parameters():,}")

    # Test forward pass
    B, L = 16, 10  # batch=16, lookback=10
    batch = {
        'eeg': torch.randn(B, L, 7, 500),
        'pac_history': torch.randn(B, L),
        'spectral': torch.randn(B, L, 61),
    }

    output = model(batch)
    print(f"\nForward pass:")
    print(f"  Input EEG shape:     {batch['eeg'].shape}")
    print(f"  Input PAC shape:     {batch['pac_history'].shape}")
    print(f"  Input spectral shape:{batch['spectral'].shape}")
    print(f"  Output shape:        {output.shape}")
    print(f"  Output range:        [{output.min():.4f}, {output.max():.4f}]")

    # Test without spectral features
    model_no_spec = TemporalPACPredictor(use_spectral=False)
    batch_no_spec = {
        'eeg': torch.randn(B, L, 7, 500),
        'pac_history': torch.randn(B, L),
    }
    out_no_spec = model_no_spec(batch_no_spec)
    print(f"\n  No-spectral model params: {model_no_spec.count_parameters():,}")
    print(f"  No-spectral output shape: {out_no_spec.shape}")

    # Test GRU variant
    model_gru = TemporalPACPredictor(use_gru=True)
    out_gru = model_gru(batch)
    print(f"\n  GRU model params: {model_gru.count_parameters():,}")
    print(f"  GRU output shape: {out_gru.shape}")

    # Test multi-horizon
    print("\nTesting MultiHorizonPredictor...")
    mh_model = MultiHorizonPredictor(horizons=[1, 3, 5, 10])
    mh_out = mh_model(batch)
    print(f"  Multi-horizon outputs:")
    for key, val in mh_out.items():
        print(f"    {key}: {val.shape}")

    # Gradient check
    loss = output.sum()
    loss.backward()
    grad_norms = {}
    for name, param in model.named_parameters():
        if param.grad is not None:
            grad_norms[name] = param.grad.norm().item()
    print(f"\n  Gradient check: {len(grad_norms)} parameters have gradients")
    print(f"  Max gradient norm: {max(grad_norms.values()):.4f}")
    print(f"  Min gradient norm: {min(grad_norms.values()):.6f}")

    print("\n✓ Temporal model test passed!")


if __name__ == "__main__":
    test_temporal_model()
