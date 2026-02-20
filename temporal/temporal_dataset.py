"""
Temporal Dataset Preparation for Future PAC Prediction

Creates sequential (lookback → horizon) pairs from the existing processed data.
Each sample consists of:
    X = {
        'eeg_history': EEG windows [t-lookback : t],         shape: (lookback, 7, 500)
        'pac_history': PAC values  [t-lookback : t],          shape: (lookback,)
        'spectral_history': Spectral features [t-lookback:t], shape: (lookback, 61)
    }
    y = PAC[t + horizon]   (scalar)

Time-based splits: data is already split by subject (no leakage).
Within each subject, windows are temporally contiguous (1-sec hop).

Author: Amaar Chughtai
Date: February 2026
"""

import os
import sys
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from typing import Dict, Tuple, Optional, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from archive.experimental_models.spectral_features import SpectralFeatureExtractor


class TemporalPACDataset(Dataset):
    """
    PyTorch Dataset that creates temporal sequences from contiguous EEG windows.

    For each subject's contiguous block of windows, creates overlapping sequences:
        Input:  windows[i - lookback : i] + pac[i - lookback : i]
        Target: pac[i + horizon]

    This means we need at least (lookback + horizon) consecutive windows per subject.
    """

    def __init__(self,
                 windows: np.ndarray,
                 pac: np.ndarray,
                 subjects: np.ndarray,
                 lookback: int = 10,
                 horizon: int = 5,
                 extract_spectral: bool = True,
                 spectral_cache: Optional[np.ndarray] = None,
                 normalize_pac: bool = True,
                 pac_mean: Optional[float] = None,
                 pac_std: Optional[float] = None):
        """
        Args:
            windows:  (N, 1, 7, 500) raw EEG windows
            pac:      (N,) PAC values
            subjects: (N,) subject IDs (strings)
            lookback: Number of past windows to use as input (seconds)
            horizon:  How many steps ahead to predict (seconds)
            extract_spectral: Whether to extract spectral features
            spectral_cache: Pre-computed spectral features (N, 61) to avoid recomputation
            normalize_pac: Whether to z-score normalize PAC values
            pac_mean: Mean for PAC normalization (use training set mean)
            pac_std:  Std for PAC normalization (use training set std)
        """
        super().__init__()

        self.lookback = lookback
        self.horizon = horizon

        # Squeeze out the extra dimension: (N, 1, 7, 500) → (N, 7, 500)
        if windows.ndim == 4 and windows.shape[1] == 1:
            windows = windows.squeeze(1)
        self.windows = windows
        self.pac_raw = pac.copy()

        # Normalize PAC for training stability
        if normalize_pac:
            if pac_mean is None:
                self.pac_mean = pac.mean()
                self.pac_std = pac.std()
            else:
                self.pac_mean = pac_mean
                self.pac_std = pac_std
            self.pac = (pac - self.pac_mean) / (self.pac_std + 1e-10)
        else:
            self.pac_mean = 0.0
            self.pac_std = 1.0
            self.pac = pac.copy()

        self.subjects = subjects

        # Extract or load spectral features
        if spectral_cache is not None:
            self.spectral = spectral_cache
        elif extract_spectral:
            print("  Extracting spectral features (this may take a minute)...")
            extractor = SpectralFeatureExtractor(fs=250.0)
            self.spectral = extractor.extract(self.windows)
            print(f"  Spectral features shape: {self.spectral.shape}")
        else:
            self.spectral = None

        # Normalize spectral features
        if self.spectral is not None:
            self.spectral_mean = self.spectral.mean(axis=0)
            self.spectral_std = self.spectral.std(axis=0) + 1e-10
            self.spectral = (self.spectral - self.spectral_mean) / self.spectral_std

        # Build valid sequence indices
        self.indices = self._build_indices()
        print(f"  Created {len(self.indices)} temporal sequences "
              f"(lookback={lookback}, horizon={horizon})")

    def _build_indices(self) -> List[Tuple[int, int]]:
        """
        Build list of (sequence_start, target_idx) pairs.

        For each subject block, valid sequences are those where:
            - sequence_start >= block_start
            - sequence_start + lookback - 1 < block_end  (lookback fits)
            - sequence_start + lookback - 1 + horizon < block_end  (target exists)

        Returns:
            indices: List of (seq_start_idx, target_idx) in global array coordinates
        """
        indices = []
        unique_subjects = np.unique(self.subjects)

        for subj in unique_subjects:
            subj_mask = self.subjects == subj
            subj_indices = np.where(subj_mask)[0]

            # Verify contiguity (indices should be consecutive)
            if len(subj_indices) < self.lookback + self.horizon:
                continue  # Not enough windows for this subject

            block_start = subj_indices[0]
            block_end = subj_indices[-1]

            # Verify contiguous block
            assert np.all(np.diff(subj_indices) == 1), \
                f"Subject {subj} windows are not contiguous!"

            # Generate all valid (start, target) pairs
            for i in range(block_start, block_end - self.lookback - self.horizon + 2):
                seq_start = i
                target_idx = i + self.lookback + self.horizon - 1
                if target_idx <= block_end:
                    indices.append((seq_start, target_idx))

        return indices

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        seq_start, target_idx = self.indices[idx]

        # EEG history: (lookback, 7, 500)
        eeg_seq = self.windows[seq_start : seq_start + self.lookback]

        # PAC history: (lookback,)
        pac_seq = self.pac[seq_start : seq_start + self.lookback]

        # Target: PAC at t + horizon (scalar)
        target = self.pac[target_idx]

        sample = {
            'eeg': torch.from_numpy(eeg_seq).float(),
            'pac_history': torch.from_numpy(pac_seq).float(),
            'target': torch.tensor(target, dtype=torch.float32),
        }

        # Add spectral features if available
        if self.spectral is not None:
            spectral_seq = self.spectral[seq_start : seq_start + self.lookback]
            sample['spectral'] = torch.from_numpy(spectral_seq).float()

        return sample

    def get_normalization_stats(self) -> Dict[str, float]:
        """Return normalization parameters for inference / val / test sets."""
        stats = {
            'pac_mean': self.pac_mean,
            'pac_std': self.pac_std,
        }
        if self.spectral is not None:
            stats['spectral_mean'] = self.spectral_mean
            stats['spectral_std'] = self.spectral_std
        return stats


def prepare_temporal_data(
    data_dir: str = 'data/processed',
    lookback: int = 10,
    horizon: int = 5,
    batch_size: int = 64,
    num_workers: int = 0,
    extract_spectral: bool = True
) -> Tuple[DataLoader, DataLoader, DataLoader, Dict]:
    """
    Prepare temporal DataLoaders from the existing processed data splits.

    The existing splits are subject-based (no subject appears in multiple splits),
    which prevents data leakage even for temporal prediction.

    Args:
        data_dir: Path to processed data directory
        lookback: Number of past windows (seconds of history)
        horizon: Steps ahead to predict (seconds into future)
        batch_size: Training batch size
        num_workers: DataLoader workers
        extract_spectral: Whether to extract spectral features

    Returns:
        train_loader, val_loader, test_loader, metadata
    """
    print(f"\n{'='*60}")
    print(f"TEMPORAL DATA PREPARATION")
    print(f"  Lookback: {lookback} seconds")
    print(f"  Horizon:  {horizon} seconds ahead")
    print(f"{'='*60}\n")

    # Load existing splits
    print("Loading data splits...")
    train_data = np.load(os.path.join(data_dir, 'train_data.npz'))
    val_data = np.load(os.path.join(data_dir, 'val_data.npz'))
    test_data = np.load(os.path.join(data_dir, 'test_data.npz'))

    # Extract arrays
    splits = {}
    for name, data in [('train', train_data), ('val', val_data), ('test', test_data)]:
        splits[name] = {
            'windows': data['windows'],
            'pac': data['pac'],
            'subjects': data['subjects'],
        }
        n_subj = len(np.unique(data['subjects']))
        print(f"  {name}: {len(data['pac'])} windows, {n_subj} subjects")

    # Compute normalization stats from training set only
    train_pac = splits['train']['pac']
    pac_mean = float(train_pac.mean())
    pac_std = float(train_pac.std())
    print(f"\nPAC normalization: mean={pac_mean:.6f}, std={pac_std:.6f}")

    # Pre-extract spectral features for all splits (with caching)
    spectral_caches = {}
    if extract_spectral:
        extractor = SpectralFeatureExtractor(fs=250.0)
        for name in ['train', 'val', 'test']:
            cache_path = os.path.join(data_dir, f'{name}_spectral_cache.npy')
            if os.path.exists(cache_path):
                print(f"  Loading cached spectral features for {name}...")
                spectral_caches[name] = np.load(cache_path)
            else:
                print(f"  Extracting spectral features for {name}...")
                windows = splits[name]['windows']
                if windows.ndim == 4 and windows.shape[1] == 1:
                    windows = windows.squeeze(1)
                spectral_caches[name] = extractor.extract(windows)
                np.save(cache_path, spectral_caches[name])
                print(f"    Saved cache to {cache_path}")
    else:
        spectral_caches = {'train': None, 'val': None, 'test': None}

    # Create datasets
    print("\nCreating temporal datasets...")

    print("  Train:")
    train_dataset = TemporalPACDataset(
        windows=splits['train']['windows'],
        pac=splits['train']['pac'],
        subjects=splits['train']['subjects'],
        lookback=lookback,
        horizon=horizon,
        extract_spectral=False,
        spectral_cache=spectral_caches['train'],
        normalize_pac=True,
        pac_mean=pac_mean,
        pac_std=pac_std,
    )

    # Get normalization stats from training set
    norm_stats = train_dataset.get_normalization_stats()

    print("  Val:")
    val_dataset = TemporalPACDataset(
        windows=splits['val']['windows'],
        pac=splits['val']['pac'],
        subjects=splits['val']['subjects'],
        lookback=lookback,
        horizon=horizon,
        extract_spectral=False,
        spectral_cache=spectral_caches['val'],
        normalize_pac=True,
        pac_mean=pac_mean,
        pac_std=pac_std,
    )

    print("  Test:")
    test_dataset = TemporalPACDataset(
        windows=splits['test']['windows'],
        pac=splits['test']['pac'],
        subjects=splits['test']['subjects'],
        lookback=lookback,
        horizon=horizon,
        extract_spectral=False,
        spectral_cache=spectral_caches['test'],
        normalize_pac=True,
        pac_mean=pac_mean,
        pac_std=pac_std,
    )

    # Create DataLoaders
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size,
        shuffle=True, num_workers=num_workers,
        drop_last=True, pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size,
        shuffle=False, num_workers=num_workers,
        pin_memory=True
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size,
        shuffle=False, num_workers=num_workers,
        pin_memory=True
    )

    metadata = {
        'lookback': lookback,
        'horizon': horizon,
        'pac_mean': pac_mean,
        'pac_std': pac_std,
        'n_train': len(train_dataset),
        'n_val': len(val_dataset),
        'n_test': len(test_dataset),
        'n_spectral_features': 61 if extract_spectral else 0,
        'spectral_mean': norm_stats.get('spectral_mean'),
        'spectral_std': norm_stats.get('spectral_std'),
    }

    print(f"\n{'='*60}")
    print(f"DATASET SUMMARY")
    print(f"  Train sequences: {len(train_dataset)}")
    print(f"  Val sequences:   {len(val_dataset)}")
    print(f"  Test sequences:  {len(test_dataset)}")
    print(f"  Batch size:      {batch_size}")
    print(f"  Train batches:   {len(train_loader)}")
    print(f"{'='*60}\n")

    return train_loader, val_loader, test_loader, metadata


def test_temporal_dataset():
    """Test the temporal dataset creation."""
    print("=" * 60)
    print("TESTING TEMPORAL DATASET")
    print("=" * 60)

    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')

    # Quick test: load data and check structure
    train_data = np.load(os.path.join(data_dir, 'train_data.npz'))
    windows = train_data['windows']
    pac = train_data['pac']
    subjects = train_data['subjects']

    print(f"\nRaw data shapes:")
    print(f"  windows:  {windows.shape}")
    print(f"  pac:      {pac.shape}")
    print(f"  subjects: {subjects.shape}")
    print(f"  Unique subjects: {np.unique(subjects)}")

    # Create small dataset without spectral features for speed
    print("\nCreating dataset (no spectral features for speed)...")
    dataset = TemporalPACDataset(
        windows=windows,
        pac=pac,
        subjects=subjects,
        lookback=10,
        horizon=5,
        extract_spectral=False,
        normalize_pac=True,
    )

    # Check a sample
    sample = dataset[0]
    print(f"\nSample 0:")
    print(f"  eeg shape:         {sample['eeg'].shape}")
    print(f"  pac_history shape: {sample['pac_history'].shape}")
    print(f"  target:            {sample['target'].item():.4f}")

    # Verify temporal ordering
    seq_start, target_idx = dataset.indices[0]
    print(f"\n  Sequence indices: [{seq_start}:{seq_start+10}] → target at {target_idx}")
    print(f"  Subject at start:  {subjects[seq_start]}")
    print(f"  Subject at target: {subjects[target_idx]}")
    assert subjects[seq_start] == subjects[target_idx], "Subject mismatch!"
    print(f"  ✓ Same subject confirmed")

    # Check DataLoader
    loader = DataLoader(dataset, batch_size=32, shuffle=True)
    batch = next(iter(loader))
    print(f"\nBatch shapes:")
    print(f"  eeg:         {batch['eeg'].shape}")
    print(f"  pac_history: {batch['pac_history'].shape}")
    print(f"  target:      {batch['target'].shape}")

    # Compute PAC autocorrelation per subject to understand temporal structure
    print(f"\nPAC temporal autocorrelation (per subject):")
    autocorrs = {1: [], 5: [], 10: []}
    for subj in np.unique(subjects)[:5]:  # First 5 subjects
        idx = np.where(subjects == subj)[0]
        p = pac[idx]
        if len(p) > 20:
            for lag in [1, 5, 10]:
                if len(p) > lag:
                    r = np.corrcoef(p[:-lag], p[lag:])[0, 1]
                    autocorrs[lag].append(r)

    for lag, vals in autocorrs.items():
        if vals:
            print(f"  Lag {lag:2d} ({lag} sec): mean r = {np.mean(vals):.4f} "
                  f"± {np.std(vals):.4f}")

    print("\n✓ Temporal dataset test passed!")


if __name__ == "__main__":
    test_temporal_dataset()
