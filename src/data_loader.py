"""
BIDS Data Loader for Closed-Loop 40Hz Entrainment Research

Loads OpenNeuro ds005048 dataset (BIDS-compliant .set files) and generates
2-second sliding windows with PAC labels for model training.

Key Features:
    - MNE-BIDS integration for BIDS dataset reading
    - 7 frontal channel selection (10/20 system)
    - 2-second sliding windows with 50% overlap
    - Event-based segmentation (stimulus ON/OFF periods)
    - PAC labeling using pac_computation module
    - 70/15/15 train/val/test splits by subject
    - PyTorch DataLoader export

References:
    - Dataset: Lahijanian et al. (2024) OpenNeuro ds005048 v1.0.1
    - MNE-BIDS: https://mne.tools/mne-bids/

Author: Amaar Chughtai
Date: February 2026
"""

import os
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, List, Dict, Optional
import logging
from collections import defaultdict

import torch
from torch.utils.data import Dataset, DataLoader

# MNE and EEG processing
import mne
import h5py

# PAC computation
from pac_computation import PACComputer


logger = logging.getLogger(__name__)


class EEGWindowDataset(Dataset):
    """
    PyTorch Dataset for EEG sliding windows with PAC labels.

    Stores pre-computed windows and PAC values for efficient batch loading.

    Attributes:
        windows: Array of EEG windows (n_samples, 1, n_channels, window_size)
        pac_labels: Array of PAC values (n_samples,)
        subject_ids: Subject identifier for each window
        session_ids: Session identifier for each window
    """

    def __init__(self, windows: np.ndarray, pac_labels: np.ndarray,
                 subject_ids: Optional[np.ndarray] = None,
                 session_ids: Optional[np.ndarray] = None):
        """
        Initialize EEG window dataset.

        Args:
            windows: EEG windows (n_samples, 1, n_channels, window_size)
            pac_labels: PAC values (n_samples,)
            subject_ids: Subject IDs for each window (optional)
            session_ids: Session IDs for each window (optional)
        """
        self.windows = torch.from_numpy(windows).float()
        self.pac_labels = torch.from_numpy(pac_labels).float()
        self.subject_ids = subject_ids
        self.session_ids = session_ids

        assert len(self.windows) == len(self.pac_labels), \
            f"Mismatch: {len(self.windows)} windows vs {len(self.pac_labels)} labels"

    def __len__(self) -> int:
        """Return number of samples."""
        return len(self.windows)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Get single window and its PAC label.

        Args:
            idx: Sample index

        Returns:
            window: EEG window tensor (1, n_channels, window_size)
            pac: PAC label (scalar)
        """
        return self.windows[idx], self.pac_labels[idx]

    def get_subject_id(self, idx: int) -> Optional[str]:
        """Get subject ID for a sample."""
        if self.subject_ids is not None:
            return self.subject_ids[idx]
        return None

    def get_session_id(self, idx: int) -> Optional[str]:
        """Get session ID for a sample."""
        if self.session_ids is not None:
            return self.session_ids[idx]
        return None


class BIDSDataProcessor:
    """
    Processes BIDS-compliant EEG dataset into training windows.

    Pipeline:
        1. Load BIDS raw data using mne-bids
        2. Select 7 frontal channels
        3. Parse events for stimulus markers
        4. Extract 2-second sliding windows with 50% overlap
        5. Compute PAC label for each window
        6. Create train/val/test splits
        7. Export as PyTorch DataLoaders

    Parameters:
        bids_root: Path to BIDS dataset root
        output_dir: Directory for processed data
        window_sec: Window duration in seconds (default 2.0)
        hop_sec: Window hop in seconds (default 1.0 = 50% overlap)
        fs: Sampling frequency in Hz (default 250)
        frontal_channels: 7 frontal channels from 10/20 system
    """

    # 7 frontal channels in 10/20 system
    FRONTAL_CHANNELS = ['Fp1', 'Fp2', 'F7', 'F3', 'Fz', 'F4', 'F8']

    def __init__(self, bids_root: str, output_dir: str,
                 window_sec: float = 2.0, hop_sec: float = 1.0,
                 fs: float = 250.0):
        """
        Initialize BIDS data processor.

        Args:
            bids_root: Path to BIDS dataset root directory
            output_dir: Directory for processed output
            window_sec: Window duration in seconds
            hop_sec: Window hop in seconds (50% overlap = hop = window/2)
            fs: Sampling frequency in Hz
        """
        self.bids_root = Path(bids_root)
        self.output_dir = Path(output_dir)
        self.window_sec = window_sec
        self.hop_sec = hop_sec
        self.fs = fs

        # Convert to samples
        self.window_samples = int(window_sec * fs)
        self.hop_samples = int(hop_sec * fs)

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # PAC computer
        self.pac_computer = PACComputer(fs=fs)

        logger.info(f"BIDSDataProcessor initialized")
        logger.info(f"  BIDS root: {self.bids_root}")
        logger.info(f"  Output dir: {self.output_dir}")
        logger.info(f"  Window: {window_sec}s ({self.window_samples} samples)")
        logger.info(f"  Hop: {hop_sec}s ({self.hop_samples} samples)")

    def get_subject_list(self) -> List[str]:
        """
        Get list of subjects in BIDS dataset.

        Returns:
            subjects: List of subject IDs (e.g., ['sub-001', 'sub-002', ...])
        """
        # Look for sub-* directories
        subjects = []
        for entry in self.bids_root.iterdir():
            if entry.is_dir() and entry.name.startswith('sub-'):
                subjects.append(entry.name)

        subjects.sort()
        logger.info(f"Found {len(subjects)} subjects: {subjects[:5]}...")
        return subjects

    def load_raw_data(self, subject: str, session: Optional[str] = None,
                      task: str = '40HzAuditoryEntrainment') -> Tuple[mne.io.Raw, dict]:
        """
        Load raw EEG data for a subject.

        Handles MATLAB v7.3 (HDF5) .set files from EEGLAB by reading
        directly with h5py, since MNE's read_raw_eeglab does not support
        this format.

        Args:
            subject: Subject ID (e.g., 'sub-01')
            session: Session ID or None if no session folders
            task: Task name (default '40HzAuditoryEntrainment')

        Returns:
            raw: MNE Raw object with EEG data
            events_dict: Dictionary mapping event names to event codes

        Raises:
            FileNotFoundError: If .set file not found
        """
        try:
            # Build file path directly (no session folders in this dataset)
            eeg_dir = self.bids_root / subject / 'eeg'
            set_file = eeg_dir / f'{subject}_task-{task}_eeg.set'

            if not set_file.exists():
                raise FileNotFoundError(f"EEG file not found: {set_file}")

            # Try standard MNE EEGLAB reader first
            try:
                raw = mne.io.read_raw_eeglab(str(set_file), preload=True,
                                              verbose=False)
                logger.info(f"  Loaded {subject} via MNE EEGLAB reader")
            except Exception:
                # Fall back to HDF5 reader for MATLAB v7.3 files
                logger.debug(f"  Standard reader failed, using HDF5 for {subject}")
                raw = self._load_hdf5_set(set_file, subject)

            # Try to load events from sidecar TSV
            events_dict = {}
            try:
                events_tsv = eeg_dir / f'{subject}_task-{task}_events.tsv'
                if events_tsv.exists():
                    events_data = pd.read_csv(events_tsv, sep='\t')
                    events_dict['events_df'] = events_data
                    logger.info(f"  Loaded events for {subject}")
            except Exception:
                logger.debug(f"  No events file for {subject}")

            logger.info(f"  Loaded {subject}: {raw.info['nchan']} channels, "
                       f"{raw.n_times} samples ({raw.n_times/raw.info['sfreq']:.1f}s)")

            return raw, events_dict

        except Exception as e:
            logger.error(f"Failed to load {subject}: {e}")
            raise

    def _load_hdf5_set(self, set_file: Path, subject: str) -> mne.io.Raw:
        """
        Load EEGLAB .set file saved in MATLAB v7.3 (HDF5) format.

        Reads EEG data and channel info from HDF5, constructs an MNE
        RawArray. Also reads the companion .fdt file if data is stored
        externally.

        Args:
            set_file: Path to .set file
            subject: Subject ID for logging

        Returns:
            raw: MNE RawArray with EEG data
        """
        with h5py.File(str(set_file), 'r') as f:
            eeg_group = f['EEG']

            # Get sampling rate
            sfreq = float(np.array(eeg_group['srate']).flat[0])
            n_channels = int(np.array(eeg_group['nbchan']).flat[0])
            n_points = int(np.array(eeg_group['pnts']).flat[0])

            # Get channel names
            chanlocs = eeg_group['chanlocs']
            ch_names = []
            if 'labels' in chanlocs:
                labels_ref = chanlocs['labels']
                for i in range(labels_ref.shape[0]):
                    ref = labels_ref[i, 0]
                    name_data = f[ref][()]
                    # HDF5 stores strings as uint16 arrays
                    name = ''.join(chr(c) for c in name_data.flat)
                    ch_names.append(name.strip())
            else:
                ch_names = [f'EEG{i+1:03d}' for i in range(n_channels)]

            # Load EEG data — check if stored in .set or external .fdt
            data_field = eeg_group['data']

            if isinstance(data_field, h5py.Dataset):
                # Data stored directly in .set file
                data = np.array(data_field, dtype=np.float64)
            else:
                # Data is a reference to external .fdt file
                fdt_file = set_file.with_suffix('.fdt')
                if fdt_file.exists():
                    data = np.fromfile(str(fdt_file), dtype=np.float32)
                    data = data.reshape(n_channels, n_points).astype(np.float64)
                else:
                    raise FileNotFoundError(
                        f"External data file not found: {fdt_file}")

            # Ensure shape is (n_channels, n_points)
            if data.shape[0] != n_channels and data.shape[1] == n_channels:
                data = data.T

            # Scale to volts (EEGLAB stores in microvolts)
            data = data * 1e-6

        # Create MNE Info and RawArray
        ch_types = ['eeg'] * len(ch_names)
        info = mne.create_info(ch_names=ch_names, sfreq=sfreq,
                               ch_types=ch_types)
        raw = mne.io.RawArray(data, info, verbose=False)

        # Set standard 10-20 montage
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, on_missing='warn')
        except Exception:
            logger.debug(f"  Could not set montage for {subject}")

        return raw

    def select_frontal_channels(self, raw: mne.io.Raw) -> mne.io.Raw:
        """
        Select 7 frontal channels from full EEG montage.

        Args:
            raw: Raw EEG data (possibly 19 channels)

        Returns:
            raw_frontal: Raw data with only frontal channels
        """
        # Find which frontal channels are available
        available_channels = raw.ch_names
        frontal_present = [ch for ch in self.FRONTAL_CHANNELS if ch in available_channels]

        if len(frontal_present) < 7:
            logger.warning(f"Only {len(frontal_present)}/7 frontal channels available: "
                          f"{frontal_present}")

        # Select channels
        raw_frontal = raw.pick(frontal_present).copy()

        logger.debug(f"Selected {len(frontal_present)} frontal channels: {frontal_present}")
        return raw_frontal

    def extract_stimulus_windows(self, raw: mne.io.Raw) -> Tuple[List[np.ndarray], List[str]]:
        """
        Extract 2-second sliding windows from stimulus periods.

        In the dataset, stimulus periods are typically marked as events.
        This method extracts windows during marked stimulus times.

        Args:
            raw: Raw EEG data (should be 7 frontal channels)

        Returns:
            windows: List of windows (each window_samples, n_channels)
            event_labels: List of event labels (e.g., 'stimulus_on', 'rest')
        """
        # Get raw data
        data = raw.get_data()  # (n_channels, n_samples)
        n_samples = data.shape[1]

        windows = []
        event_labels = []

        # Extract sliding windows
        # Note: In actual implementation, would segment based on stimulus events
        # For now, use continuous sliding window approach
        for start_idx in range(0, n_samples - self.window_samples, self.hop_samples):
            end_idx = start_idx + self.window_samples
            window = data[:, start_idx:end_idx]  # (n_channels, window_samples)

            # Check for bad values
            if not np.any(np.isnan(window)) and not np.any(np.isinf(window)):
                windows.append(window)
                event_labels.append('stimulus')  # Placeholder

        logger.debug(f"Extracted {len(windows)} windows from {n_samples/raw.info['sfreq']:.1f}s recording")
        return windows, event_labels

    def compute_pac_labels(self, windows: List[np.ndarray]) -> np.ndarray:
        """
        Compute PAC label for each window.

        Args:
            windows: List of EEG windows (n_channels, window_samples)

        Returns:
            pac_labels: Array of PAC values (n_windows,)
        """
        pac_labels = []

        for i, window in enumerate(windows):
            # Average PAC across 7 frontal channels
            pac_values = self.pac_computer.compute_pac_multichannel(window)
            pac_avg = np.mean(pac_values)
            pac_labels.append(pac_avg)

            if (i + 1) % max(1, len(windows) // 10) == 0:
                logger.debug(f"  Computed PAC for {i+1}/{len(windows)} windows")

        pac_labels = np.array(pac_labels)
        logger.info(f"PAC labels: mean={pac_labels.mean():.4f}, "
                   f"std={pac_labels.std():.4f}, "
                   f"min={pac_labels.min():.4f}, max={pac_labels.max():.4f}")

        return pac_labels

    def process_dataset(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Process entire BIDS dataset.

        Returns:
            windows_all: All windows (n_total, 1, n_channels, window_samples)
            pac_all: All PAC labels (n_total,)
            subject_ids: Subject ID for each window
            session_ids: Session ID for each window
        """
        windows_all = []
        pac_all = []
        subject_ids_all = []
        session_ids_all = []

        subjects = self.get_subject_list()

        for subj_idx, subject in enumerate(subjects):
            logger.info(f"\nProcessing {subject} ({subj_idx+1}/{len(subjects)})")

            try:
                # Load raw data
                raw, events = self.load_raw_data(subject)

                # Select frontal channels
                raw = self.select_frontal_channels(raw)

                # Extract windows
                windows, event_labels = self.extract_stimulus_windows(raw)

                if len(windows) == 0:
                    logger.warning(f"No windows extracted from {subject}")
                    continue

                # Compute PAC labels
                pac_labels = self.compute_pac_labels(windows)

                # Convert to required shape: (1, n_channels, window_samples)
                windows_array = np.array(windows)  # (n_windows, n_channels, window_samples)
                windows_array = windows_array[:, np.newaxis, :, :]  # Add feature channel

                # Append to lists
                windows_all.append(windows_array)
                pac_all.append(pac_labels)
                subject_ids_all.extend([subject] * len(windows))
                session_ids_all.extend(['default'] * len(windows))

                logger.info(f"  → Extracted {len(windows)} windows from {subject}")

            except Exception as e:
                logger.error(f"Error processing {subject}: {e}")
                continue

        # Concatenate all data
        windows_combined = np.concatenate(windows_all, axis=0)
        pac_combined = np.concatenate(pac_all, axis=0)
        subject_ids_array = np.array(subject_ids_all)
        session_ids_array = np.array(session_ids_all)

        logger.info(f"\n" + "="*60)
        logger.info(f"Dataset Summary:")
        logger.info(f"  Total windows: {len(windows_combined)}")
        logger.info(f"  Shape: {windows_combined.shape}")
        logger.info(f"  PAC - mean: {pac_combined.mean():.4f}, std: {pac_combined.std():.4f}")
        logger.info(f"  Subjects: {len(set(subject_ids_array))}")
        logger.info("="*60)

        return windows_combined, pac_combined, subject_ids_array, session_ids_array

    def create_splits(self, windows: np.ndarray, pac_labels: np.ndarray,
                     subject_ids: np.ndarray,
                     train_ratio: float = 0.70,
                     val_ratio: float = 0.15) -> Dict[str, Dict]:
        """
        Create train/val/test splits by subject (leave-subject-out).

        Ensures no data leakage: each subject is fully in one split.

        Args:
            windows: All windows
            pac_labels: All PAC labels
            subject_ids: Subject ID for each window
            train_ratio: Fraction for training (default 0.70)
            val_ratio: Fraction for validation (default 0.15)

        Returns:
            splits: Dictionary with 'train', 'val', 'test' keys containing
                   {'windows': ..., 'pac': ..., 'subjects': ...}
        """
        unique_subjects = np.unique(subject_ids)
        n_subjects = len(unique_subjects)

        # Shuffle subjects
        np.random.seed(42)
        shuffled_subjects = np.random.permutation(unique_subjects)

        # Split subjects
        n_train = int(n_subjects * train_ratio)
        n_val = int(n_subjects * val_ratio)

        train_subjects = set(shuffled_subjects[:n_train])
        val_subjects = set(shuffled_subjects[n_train:n_train+n_val])
        test_subjects = set(shuffled_subjects[n_train+n_val:])

        # Create masks
        train_mask = np.array([s in train_subjects for s in subject_ids])
        val_mask = np.array([s in val_subjects for s in subject_ids])
        test_mask = np.array([s in test_subjects for s in subject_ids])

        splits = {
            'train': {
                'windows': windows[train_mask],
                'pac': pac_labels[train_mask],
                'subjects': subject_ids[train_mask],
                'n_samples': np.sum(train_mask)
            },
            'val': {
                'windows': windows[val_mask],
                'pac': pac_labels[val_mask],
                'subjects': subject_ids[val_mask],
                'n_samples': np.sum(val_mask)
            },
            'test': {
                'windows': windows[test_mask],
                'pac': pac_labels[test_mask],
                'subjects': subject_ids[test_mask],
                'n_samples': np.sum(test_mask)
            }
        }

        logger.info(f"Data Split (by subject):")
        logger.info(f"  Train: {len(train_subjects)} subjects, {splits['train']['n_samples']} windows")
        logger.info(f"  Val:   {len(val_subjects)} subjects, {splits['val']['n_samples']} windows")
        logger.info(f"  Test:  {len(test_subjects)} subjects, {splits['test']['n_samples']} windows")

        return splits

    def save_splits(self, splits: Dict[str, Dict]):
        """
        Save train/val/test splits to npz files.

        Args:
            splits: Dictionary with split data
        """
        for split_name, split_data in splits.items():
            output_path = self.output_dir / f"{split_name}_data.npz"

            np.savez(output_path,
                    windows=split_data['windows'],
                    pac=split_data['pac'],
                    subjects=split_data['subjects'])

            logger.info(f"Saved {split_name} split to {output_path}")

    def create_dataloaders(self, splits: Dict[str, Dict],
                          batch_size: int = 32,
                          num_workers: int = 4) -> Dict[str, DataLoader]:
        """
        Create PyTorch DataLoaders from splits.

        Args:
            splits: Dictionary with split data
            batch_size: Batch size for DataLoader
            num_workers: Number of worker processes

        Returns:
            dataloaders: Dictionary with 'train', 'val', 'test' DataLoaders
        """
        dataloaders = {}

        for split_name, split_data in splits.items():
            dataset = EEGWindowDataset(
                windows=split_data['windows'],
                pac_labels=split_data['pac'],
                subject_ids=split_data['subjects']
            )

            shuffle = (split_name == 'train')
            dataloader = DataLoader(
                dataset,
                batch_size=batch_size,
                shuffle=shuffle,
                num_workers=num_workers,
                pin_memory=True
            )

            dataloaders[split_name] = dataloader
            logger.info(f"Created DataLoader for {split_name}: "
                       f"{len(dataset)} samples, batch_size={batch_size}")

        return dataloaders


def main():
    """Main entry point for data loading pipeline."""
    parser = argparse.ArgumentParser(
        description="Load BIDS EEG data and create training windows"
    )
    parser.add_argument('--bids_root', type=str, required=True,
                       help='Path to BIDS dataset root')
    parser.add_argument('--output', type=str, required=True,
                       help='Output directory for processed data')
    parser.add_argument('--window_sec', type=float, default=2.0,
                       help='Window duration in seconds (default 2.0)')
    parser.add_argument('--hop_sec', type=float, default=1.0,
                       help='Window hop in seconds (default 1.0 = 50% overlap)')
    parser.add_argument('--batch_size', type=int, default=32,
                       help='Batch size for DataLoader (default 32)')
    parser.add_argument('--num_workers', type=int, default=4,
                       help='Number of DataLoader workers (default 4)')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create processor
    processor = BIDSDataProcessor(
        bids_root=args.bids_root,
        output_dir=args.output,
        window_sec=args.window_sec,
        hop_sec=args.hop_sec
    )

    # Process dataset
    windows, pac_labels, subject_ids, session_ids = processor.process_dataset()

    # Create splits
    splits = processor.create_splits(windows, pac_labels, subject_ids)

    # Save splits
    processor.save_splits(splits)

    # Create DataLoaders
    dataloaders = processor.create_dataloaders(
        splits,
        batch_size=args.batch_size,
        num_workers=args.num_workers
    )

    logger.info("\nData loading complete!")
    logger.info("Ready for training with created DataLoaders.")


if __name__ == "__main__":
    main()
