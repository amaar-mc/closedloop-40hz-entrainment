"""
Reprocess OpenNeuro ds005048 with longer PAC windows for temporal prediction.

Key changes from original 2-second windows:
- Window length: 8 seconds (2000 samples at 250Hz)
- Hop size: 4 seconds (50% overlap)
- Expected outcome: Temporal autocorrelation > 0.3, enabling R² > 0.6 prediction
"""

import numpy as np
import mne
from scipy import signal
from scipy.stats import entropy
import os
from pathlib import Path
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')


def compute_pac_modulation_index(eeg_window, fs=250, theta_band=(4, 8), gamma_band=(38, 42), n_bins=18):
    """
    Compute Phase-Amplitude Coupling using Modulation Index (MI).

    Args:
        eeg_window: (n_channels, n_samples) array - longer window for stable MI
        fs: Sampling frequency
        theta_band: (low, high) Hz for phase modulation
        gamma_band: (low, high) Hz for amplitude modulation
        n_bins: Number of phase bins for MI calculation

    Returns:
        pac_score: Scalar MI value averaged across channels
    """
    n_channels = eeg_window.shape[0]
    mi_values = []

    for ch in range(n_channels):
        signal_ch = eeg_window[ch]

        # Extract theta phase
        sos_theta = signal.butter(4, theta_band, btype='bandpass', fs=fs, output='sos')
        theta_filtered = signal.sosfiltfilt(sos_theta, signal_ch)
        theta_phase = np.angle(signal.hilbert(theta_filtered))

        # Extract gamma amplitude
        sos_gamma = signal.butter(4, gamma_band, btype='bandpass', fs=fs, output='sos')
        gamma_filtered = signal.sosfiltfilt(sos_gamma, signal_ch)
        gamma_amplitude = np.abs(signal.hilbert(gamma_filtered))

        # Bin gamma amplitude by theta phase
        phase_bins = np.linspace(-np.pi, np.pi, n_bins + 1)
        bin_indices = np.digitize(theta_phase, phase_bins) - 1
        bin_indices = np.clip(bin_indices, 0, n_bins - 1)

        # Mean amplitude per phase bin
        binned_amplitudes = np.zeros(n_bins)
        for i in range(n_bins):
            mask = (bin_indices == i)
            if mask.sum() > 0:
                binned_amplitudes[i] = gamma_amplitude[mask].mean()

        # Normalize to probability distribution
        p = binned_amplitudes / binned_amplitudes.sum()

        # Modulation Index = KL divergence from uniform
        uniform = np.ones(n_bins) / n_bins
        mi = entropy(p, uniform) / np.log(n_bins)  # Normalize to [0, 1]

        mi_values.append(mi)

    # Average across channels
    return np.mean(mi_values)


def extract_spectral_features(eeg_window, fs=250):
    """
    Extract spectral features from EEG window for model input.

    Returns:
        features: Dictionary of spectral features
    """
    n_channels, n_samples = eeg_window.shape

    features = {}

    # Band power in standard bands
    bands = {
        'delta': (1, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30),
        'gamma': (30, 50)
    }

    for band_name, (low, high) in bands.items():
        sos = signal.butter(4, [low, high], btype='bandpass', fs=fs, output='sos')
        powers = []
        for ch in range(n_channels):
            filtered = signal.sosfiltfilt(sos, eeg_window[ch])
            powers.append(np.mean(filtered ** 2))
        features[f'{band_name}_power'] = np.array(powers)

    # Spectral entropy
    entropies = []
    for ch in range(n_channels):
        freqs, psd = signal.welch(eeg_window[ch], fs=fs, nperseg=min(512, n_samples))
        psd_norm = psd / psd.sum()
        entropies.append(entropy(psd_norm))
    features['spectral_entropy'] = np.array(entropies)

    return features


def process_subject(subject_id, raw_data_dir, window_length=8.0, hop_size=4.0):
    """
    Process one subject with longer PAC windows.

    Args:
        subject_id: Subject number (1-13)
        raw_data_dir: Path to ds005048 directory
        window_length: PAC window length in seconds (8.0)
        hop_size: Window hop in seconds (4.0 for 50% overlap)

    Returns:
        windows: (n_windows, n_channels, n_samples) EEG windows
        pac_values: (n_windows,) PAC scores
        spectral_features: Dictionary of feature arrays
        timestamps: (n_windows,) timestamp for each window
    """
    subject_path = Path(raw_data_dir) / f'sub-{subject_id:02d}' / 'eeg' / \
                   f'sub-{subject_id:02d}_task-40HzAuditoryEntrainment_eeg.set'

    print(f"\nProcessing subject {subject_id:02d}...")
    print(f"Loading: {subject_path}")

    # Load EEGLAB .set file (Matlab v7.3 format requires h5py)
    try:
        # Try MNE first
        raw = mne.io.read_raw_eeglab(subject_path, preload=True, verbose=False)
        data = raw.get_data()
        fs = int(raw.info['sfreq'])
        n_channels = data.shape[0]
    except Exception as e:
        # Fallback to h5py for Matlab v7.3
        import h5py

        with h5py.File(subject_path, 'r') as f:
            # EEGLAB structure in HDF5
            data = f['EEG']['data'][()]  # (n_channels, n_timepoints)
            fs = int(f['EEG']['srate'][()])
            n_channels = data.shape[0]

            # If data is transposed
            if data.shape[0] > data.shape[1]:
                data = data.T

    print(f"  Sampling rate: {fs} Hz")
    print(f"  Channels: {n_channels}")
    print(f"  Duration: {data.shape[1] / fs:.1f} seconds")

    # Window parameters
    window_samples = int(window_length * fs)
    hop_samples = int(hop_size * fs)

    # Sliding window extraction
    windows_list = []
    pac_list = []
    spectral_dict = {k: [] for k in ['delta_power', 'theta_power', 'alpha_power',
                                      'beta_power', 'gamma_power', 'spectral_entropy']}
    timestamps = []

    n_windows = (data.shape[1] - window_samples) // hop_samples + 1
    print(f"  Creating {n_windows} windows (length={window_length}s, hop={hop_size}s)")

    for i in range(n_windows):
        start = i * hop_samples
        end = start + window_samples

        if end > data.shape[1]:
            break

        window = data[:, start:end]

        # Compute PAC
        pac = compute_pac_modulation_index(window, fs=fs)

        # Extract features
        features = extract_spectral_features(window, fs=fs)

        windows_list.append(window)
        pac_list.append(pac)
        timestamps.append(start / fs)

        for key in spectral_dict:
            spectral_dict[key].append(features[key])

    windows = np.array(windows_list)
    pac_values = np.array(pac_list)
    timestamps = np.array(timestamps)

    # Convert spectral features to arrays
    spectral_features = {k: np.array(v) for k, v in spectral_dict.items()}

    print(f"  ✓ Created {len(pac_values)} windows")
    print(f"  PAC range: [{pac_values.min():.4f}, {pac_values.max():.4f}]")
    print(f"  PAC mean: {pac_values.mean():.4f} ± {pac_values.std():.4f}")

    return windows, pac_values, spectral_features, timestamps


def compute_temporal_autocorrelation(pac_values, lags=[1, 2, 3, 5, 10]):
    """
    Compute PAC autocorrelation at various lags.

    With 4-second hop size:
    - lag=1 → 4 seconds ahead
    - lag=2 → 8 seconds ahead
    - lag=5 → 20 seconds ahead
    """
    print("\n" + "="*60)
    print("TEMPORAL AUTOCORRELATION ANALYSIS")
    print("="*60)

    for lag in lags:
        if lag >= len(pac_values):
            continue

        r = np.corrcoef(pac_values[:-lag], pac_values[lag:])[0, 1]
        print(f"PAC autocorrelation at lag={lag} ({lag*4}s ahead): r = {r:.3f}")

    print("="*60)


def main():
    """
    Main reprocessing pipeline.
    """
    print("="*80)
    print("REPROCESSING OPENNEURO DS005048 WITH 8-SECOND PAC WINDOWS")
    print("="*80)
    print("\nParameters:")
    print("  Window length: 8 seconds (2000 samples at 250Hz)")
    print("  Hop size: 4 seconds (50% overlap)")
    print("  Expected: ~20 theta cycles per window → stable MI")
    print("  Expected: Autocorrelation > 0.3 → temporal predictability")
    print()

    # Paths
    base_dir = Path('/sessions/serene-gifted-feynman/mnt/closedloop-40hz-entrainment')
    raw_data_dir = base_dir / 'data' / 'raw' / 'ds005048'
    output_dir = base_dir / 'data' / 'processed' / 'long_windows'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process all subjects
    all_windows = []
    all_pac = []
    all_spectral = {k: [] for k in ['delta_power', 'theta_power', 'alpha_power',
                                     'beta_power', 'gamma_power', 'spectral_entropy']}
    all_subjects = []
    all_timestamps = []

    # Find all subject directories
    subject_dirs = sorted([d for d in raw_data_dir.glob('sub-*') if d.is_dir()])
    n_subjects = len(subject_dirs)

    print(f"Found {n_subjects} subjects in {raw_data_dir}\n")

    for subject_dir in subject_dirs:
        subject_id = int(subject_dir.name.split('-')[1])

        try:
            windows, pac, spectral, timestamps = process_subject(
                subject_id, raw_data_dir,
                window_length=8.0,
                hop_size=4.0
            )

            all_windows.append(windows)
            all_pac.append(pac)
            all_subjects.extend([subject_id] * len(pac))
            all_timestamps.append(timestamps)

            for key in all_spectral:
                all_spectral[key].append(spectral[key])

        except Exception as e:
            print(f"  ✗ Error processing subject {subject_id:02d}: {e}")
            continue

    # Concatenate all subjects
    print("\n" + "="*80)
    print("CONCATENATING ALL SUBJECTS")
    print("="*80)

    windows_array = np.concatenate(all_windows, axis=0)
    pac_array = np.concatenate(all_pac, axis=0)
    subjects_array = np.array(all_subjects)

    spectral_features = {}
    for key in all_spectral:
        spectral_features[key] = np.concatenate(all_spectral[key], axis=0)

    print(f"\nTotal dataset:")
    print(f"  Windows: {windows_array.shape}")
    print(f"  PAC values: {pac_array.shape}")
    print(f"  Subjects: {len(np.unique(subjects_array))}")
    print(f"  PAC mean: {pac_array.mean():.4f} ± {pac_array.std():.4f}")

    # CRITICAL: Check temporal autocorrelation
    compute_temporal_autocorrelation(pac_array, lags=[1, 2, 3, 5, 10])

    # Save processed data
    print("\n" + "="*80)
    print("SAVING PROCESSED DATA")
    print("="*80)

    np.save(output_dir / 'windows.npy', windows_array)
    np.save(output_dir / 'pac_values.npy', pac_array)
    np.save(output_dir / 'subjects.npy', subjects_array)

    for key, values in spectral_features.items():
        np.save(output_dir / f'{key}.npy', values)

    # Save metadata
    metadata = {
        'window_length_sec': 8.0,
        'hop_size_sec': 4.0,
        'sampling_rate_hz': 250,
        'n_windows': len(pac_array),
        'n_subjects': len(np.unique(subjects_array)),
        'window_shape': windows_array.shape[1:],
        'pac_mean': float(pac_array.mean()),
        'pac_std': float(pac_array.std()),
    }

    import json
    with open(output_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✓ Saved to: {output_dir}")
    print(f"  - windows.npy: {windows_array.shape}")
    print(f"  - pac_values.npy: {pac_array.shape}")
    print(f"  - subjects.npy: {subjects_array.shape}")
    print(f"  - spectral features: {list(spectral_features.keys())}")
    print(f"  - metadata.json")

    print("\n" + "="*80)
    print("REPROCESSING COMPLETE")
    print("="*80)
    print("\nNext step: Run temporal training with this new dataset")
    print("Expected performance: R² > 0.6 (vs previous R² = -0.05)")


if __name__ == '__main__':
    main()
