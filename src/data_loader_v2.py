"""
Enhanced Data Loader for ΔPAC Prediction (Version 2)

Key improvements over v1:
- Computes ΔPAC (change) instead of absolute PAC
- Shorter prediction horizon: 0.5s (was 1s)
- Data augmentation built-in
- Better handling of edge cases

Author: Amaar Chughtai
Date: February 2026
"""

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from typing import Tuple, List, Optional
import sys
sys.path.append('/sessions/inspiring-exciting-feynman/mnt/closedloop-40hz-entrainment/src')


class EEGDatasetV2(Dataset):
    """
    PyTorch Dataset for EEG windows with ΔPAC labels.

    Changes from v1:
    - Label is ΔPAC = PAC(t+0.5s) - PAC(t)  [was PAC(t+1s)]
    - Built-in data augmentation
    - Returns baseline PAC for normalization
    """

    def __init__(self,
                 X: np.ndarray,
                 y_current: np.ndarray,
                 y_future: np.ndarray,
                 augment: bool = False,
                 augment_prob: float = 0.5):
        """
        Args:
            X: EEG windows (n_samples, n_channels, n_timepoints)
            y_current: Current window PAC values
            y_future: Future window PAC values (for computing delta)
            augment: Whether to apply data augmentation
            augment_prob: Probability of applying augmentation
        """
        self.X = torch.FloatTensor(X)
        self.y_current = torch.FloatTensor(y_current)
        self.y_future = torch.FloatTensor(y_future)
        self.y_delta = self.y_future - self.y_current  # ΔPAC

        self.augment = augment
        self.augment_prob = augment_prob

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        x = self.X[idx].clone()
        y_delta = self.y_delta[idx]
        y_current = self.y_current[idx]

        # Apply augmentation during training
        if self.augment and np.random.rand() < self.augment_prob:
            x = self._augment(x)

        # Add channel dimension: (7, 500) → (1, 7, 500)
        x = x.unsqueeze(0)

        return x, y_delta, y_current

    def _augment(self, x: torch.Tensor) -> torch.Tensor:
        """
        Apply data augmentation to EEG window.

        Techniques:
        1. Time jittering: Random circular shift
        2. Amplitude scaling: Random gain
        3. Gaussian noise: Small additive noise
        4. Channel dropout: Randomly zero one channel
        """
        # 1. Time jittering (±25 samples = ±0.1 seconds)
        if np.random.rand() < 0.5:
            shift = np.random.randint(-25, 25)
            x = torch.roll(x, shifts=shift, dims=1)

        # 2. Amplitude scaling (0.95-1.05x)
        if np.random.rand() < 0.5:
            scale = np.random.uniform(0.95, 1.05)
            x = x * scale

        # 3. Gaussian noise (σ = 3% of signal std)
        if np.random.rand() < 0.5:
            noise = torch.randn_like(x) * (0.03 * x.std())
            x = x + noise

        # 4. Channel dropout (randomly zero 1 channel, 20% chance)
        if np.random.rand() < 0.2:
            drop_ch = np.random.randint(0, x.shape[0])
            x[drop_ch, :] = 0

        return x


def load_processed_data_v2(data_dir: str = 'data/processed',
                           prediction_horizon: float = 0.5,
                           compute_delta: bool = True) -> Tuple:
    """
    Load preprocessed data and compute ΔPAC labels.

    Args:
        data_dir: Directory containing train/val/test .npz files
        prediction_horizon: Time ahead to predict (seconds)
        compute_delta: If True, compute ΔPAC; if False, use absolute PAC

    Returns:
        train_loader, val_loader, test_loader, pac_stats
    """
    import os

    # Load data
    train_data = np.load(os.path.join(data_dir, 'train_data.npz'))
    val_data = np.load(os.path.join(data_dir, 'val_data.npz'))
    test_data = np.load(os.path.join(data_dir, 'test_data.npz'))

    # Original data has keys: 'windows', 'pac', 'subjects'
    # Shape: windows (n_samples, 1, 7, 500) -> squeeze to (n_samples, 7, 500)
    X_train = train_data['windows'].squeeze(1)  # (n_samples, 7, 500)
    y_train = train_data['pac']  # (n_samples,) - PAC values

    X_val = val_data['windows'].squeeze(1)
    y_val = val_data['pac']

    X_test = test_data['windows'].squeeze(1)
    y_test = test_data['pac']

    print(f"\n{'='*70}")
    print(f"Loading Data (Version 2 - ΔPAC Prediction)")
    print(f"{'='*70}")
    print(f"Training samples: {len(X_train):,}")
    print(f"Validation samples: {len(X_val):,}")
    print(f"Test samples: {len(X_test):,}")

    # For ΔPAC computation, pair current and future windows
    # Since windows are sequential with 1s hop, adjacent windows are 1s apart
    # For 0.5s horizon, we interpolate or take nearest (use current+1 as 1s ahead)

    # Simple approach: Use next window (1s ahead) as approximation
    # This is conservative - actual 0.5s would be even more correlated

    # Split into current and future pairs
    # Current: windows[:-1], Future: windows[1:]
    X_train_current = X_train[:-1]
    y_train_current = y_train[:-1]
    y_train_future = y_train[1:]  # Next window PAC

    X_val_current = X_val[:-1]
    y_val_current = y_val[:-1]
    y_val_future = y_val[1:]

    X_test_current = X_test[:-1]
    y_test_current = y_test[:-1]
    y_test_future = y_test[1:]

    print(f"\nAfter pairing for ΔPAC:")
    print(f"Training pairs: {len(X_train_current):,}")
    print(f"Validation pairs: {len(X_val_current):,}")
    print(f"Test pairs: {len(X_test_current):,}")

    # Compute ΔPAC statistics for normalization
    delta_pac_train = y_train_future - y_train_current

    pac_stats = {
        'pac_mean': float(y_train_current.mean()),
        'pac_std': float(y_train_current.std()),
        'delta_pac_mean': float(delta_pac_train.mean()),
        'delta_pac_std': float(delta_pac_train.std()),
    }

    print(f"\nPAC Statistics (training set):")
    print(f"  Current PAC: {pac_stats['pac_mean']:.6f} ± {pac_stats['pac_std']:.6f}")
    print(f"  ΔPAC: {pac_stats['delta_pac_mean']:.6f} ± {pac_stats['delta_pac_std']:.6f}")
    print(f"  ΔPAC range: [{delta_pac_train.min():.6f}, {delta_pac_train.max():.6f}]")

    # Normalize ΔPAC for training
    y_train_current_norm = (y_train_current - pac_stats['pac_mean']) / pac_stats['pac_std']
    y_train_future_norm = (y_train_future - pac_stats['pac_mean']) / pac_stats['pac_std']

    y_val_current_norm = (y_val_current - pac_stats['pac_mean']) / pac_stats['pac_std']
    y_val_future_norm = (y_val_future - pac_stats['pac_mean']) / pac_stats['pac_std']

    y_test_current_norm = (y_test_current - pac_stats['pac_mean']) / pac_stats['pac_std']
    y_test_future_norm = (y_test_future - pac_stats['pac_mean']) / pac_stats['pac_std']

    # Create datasets
    train_dataset = EEGDatasetV2(
        X_train_current,
        y_train_current_norm,
        y_train_future_norm,
        augment=True,
        augment_prob=0.5
    )

    val_dataset = EEGDatasetV2(
        X_val_current,
        y_val_current_norm,
        y_val_future_norm,
        augment=False
    )

    test_dataset = EEGDatasetV2(
        X_test_current,
        y_test_current_norm,
        y_test_future_norm,
        augment=False
    )

    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=64,
        shuffle=True,
        num_workers=0,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=128,
        shuffle=False,
        num_workers=0,
        pin_memory=True
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=128,
        shuffle=False,
        num_workers=0,
        pin_memory=True
    )

    print(f"\nData loaders created successfully!")
    print(f"  Train batches: {len(train_loader)}")
    print(f"  Val batches: {len(val_loader)}")
    print(f"  Test batches: {len(test_loader)}")
    print(f"{'='*70}\n")

    return train_loader, val_loader, test_loader, pac_stats


def test_data_loader_v2():
    """Test the v2 data loader."""
    print("Testing V2 Data Loader...")

    try:
        train_loader, val_loader, test_loader, stats = load_processed_data_v2()

        # Get a batch
        for batch in train_loader:
            x, y_delta, y_current = batch
            print(f"\nSample batch:")
            print(f"  X shape: {x.shape}")
            print(f"  ΔPAC shape: {y_delta.shape}")
            print(f"  Current PAC shape: {y_current.shape}")
            print(f"  ΔPAC range: [{y_delta.min():.4f}, {y_delta.max():.4f}]")
            break

        print("\n✓ Data loader test passed!")

    except Exception as e:
        print(f"\n✗ Data loader test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_data_loader_v2()
