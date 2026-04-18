"""
Train temporal PAC predictor using 8-second windows.

Expected improvement:
- Old (2-sec windows): R² = -0.05, autocorr = 0.06
- New (8-sec windows): R² > 0.6, autocorr > 0.3
"""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import r2_score, mean_absolute_error
from pathlib import Path
import argparse
import json
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Import model architecture
import sys
sys.path.append(str(Path(__file__).parent))
from temporal_model import TemporalPACPredictor


class LongWindowTemporalDataset(Dataset):
    """
    Temporal dataset for 8-second windows with 4-second hop.

    With 4-second hop:
    - horizon=1 → 4 seconds ahead
    - horizon=2 → 8 seconds ahead
    - horizon=3 → 12 seconds ahead
    """
    def __init__(self, windows, pac_values, subject_ids, spectral_features,
                 lookback=5, horizon=2):
        """
        Args:
            lookback: Number of windows to look back (5 windows = 20 seconds history)
            horizon: Number of windows ahead to predict (2 windows = 8 seconds ahead)
        """
        self.lookback = lookback
        self.horizon = horizon

        # Create sequences per subject (don't cross subject boundaries)
        sequences = []

        for subj_id in np.unique(subject_ids):
            subj_mask = (subject_ids == subj_id)
            subj_windows = windows[subj_mask]
            subj_pac = pac_values[subj_mask]

            # Extract spectral features for this subject
            subj_spectral = {}
            for key in spectral_features:
                subj_spectral[key] = spectral_features[key][subj_mask]

            # Create temporal sequences
            for i in range(lookback, len(subj_windows) - horizon):
                seq_windows = subj_windows[i-lookback:i]  # (lookback, ch, time)
                seq_pac = subj_pac[i-lookback:i]  # (lookback,)
                target_pac = subj_pac[i + horizon]  # scalar

                # Spectral features for each window in sequence
                seq_spectral = {}
                for key in spectral_features:
                    seq_spectral[key] = subj_spectral[key][i-lookback:i]  # (lookback, n_ch)

                sequences.append({
                    'eeg': seq_windows,
                    'pac_history': seq_pac,
                    'spectral': seq_spectral,
                    'target': target_pac
                })

        self.sequences = sequences
        print(f"Created {len(sequences)} temporal sequences (lookback={lookback}, horizon={horizon})")

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        seq = self.sequences[idx]

        # Convert to tensors
        eeg = torch.FloatTensor(seq['eeg'])  # (lookback, ch, time)
        pac_history = torch.FloatTensor(seq['pac_history'])  # (lookback,)
        target = torch.FloatTensor([seq['target']])  # scalar

        # Stack spectral features
        spectral_list = []
        for key in sorted(seq['spectral'].keys()):
            spectral_list.append(seq['spectral'][key])  # (lookback, n_ch)

        spectral = torch.FloatTensor(np.stack(spectral_list, axis=-1))  # (lookback, n_ch, n_features)

        return {
            'eeg': eeg,
            'pac_history': pac_history,
            'spectral': spectral,
            'target': target.squeeze()
        }


def create_dataloaders(data_dir, lookback=5, horizon=2, batch_size=32):
    """
    Create train/val/test dataloaders with temporal split.

    Args:
        data_dir: Path to processed long_windows data
        lookback: Windows to look back
        horizon: Windows ahead to predict
        batch_size: Batch size

    Returns:
        train_loader, val_loader, test_loader, normalization_stats
    """
    data_dir = Path(data_dir)

    print("Loading long-window data...")
    windows = np.load(data_dir / 'windows.npy')
    pac_values = np.load(data_dir / 'pac_values.npy')
    subjects = np.load(data_dir / 'subjects.npy')

    # Load spectral features
    spectral_features = {}
    for key in ['delta_power', 'theta_power', 'alpha_power',
                'beta_power', 'gamma_power', 'spectral_entropy']:
        spectral_features[key] = np.load(data_dir / f'{key}.npy')

    print(f"Loaded data: {windows.shape[0]} windows from {len(np.unique(subjects))} subjects")

    # Temporal split per subject (70% train, 15% val, 15% test)
    train_windows, val_windows, test_windows = [], [], []
    train_pac, val_pac, test_pac = [], [], []
    train_subjects, val_subjects, test_subjects = [], [], []
    train_spectral = {k: [] for k in spectral_features}
    val_spectral = {k: [] for k in spectral_features}
    test_spectral = {k: [] for k in spectral_features}

    for subj_id in np.unique(subjects):
        subj_mask = (subjects == subj_id)
        subj_windows = windows[subj_mask]
        subj_pac = pac_values[subj_mask]

        n = len(subj_pac)
        n_train = int(0.7 * n)
        n_val = int(0.15 * n)

        # Split temporally (no shuffle)
        train_windows.append(subj_windows[:n_train])
        val_windows.append(subj_windows[n_train:n_train+n_val])
        test_windows.append(subj_windows[n_train+n_val:])

        train_pac.append(subj_pac[:n_train])
        val_pac.append(subj_pac[n_train:n_train+n_val])
        test_pac.append(subj_pac[n_train+n_val:])

        train_subjects.extend([subj_id] * n_train)
        val_subjects.extend([subj_id] * n_val)
        test_subjects.extend([subj_id] * (n - n_train - n_val))

        for key in spectral_features:
            subj_feature = spectral_features[key][subj_mask]
            train_spectral[key].append(subj_feature[:n_train])
            val_spectral[key].append(subj_feature[n_train:n_train+n_val])
            test_spectral[key].append(subj_feature[n_train+n_val:])

    # Concatenate
    train_windows = np.concatenate(train_windows)
    val_windows = np.concatenate(val_windows)
    test_windows = np.concatenate(test_windows)

    train_pac = np.concatenate(train_pac)
    val_pac = np.concatenate(val_pac)
    test_pac = np.concatenate(test_pac)

    train_subjects = np.array(train_subjects)
    val_subjects = np.array(val_subjects)
    test_subjects = np.array(test_subjects)

    for key in spectral_features:
        train_spectral[key] = np.concatenate(train_spectral[key])
        val_spectral[key] = np.concatenate(val_spectral[key])
        test_spectral[key] = np.concatenate(test_spectral[key])

    print(f"\nSplit sizes:")
    print(f"  Train: {len(train_pac)} windows")
    print(f"  Val: {len(val_pac)} windows")
    print(f"  Test: {len(test_pac)} windows")

    # Normalize PAC using training statistics
    pac_mean = train_pac.mean()
    pac_std = train_pac.std()

    train_pac = (train_pac - pac_mean) / pac_std
    val_pac = (val_pac - pac_mean) / pac_std
    test_pac = (test_pac - pac_mean) / pac_std

    print(f"\nPAC normalization: mean={pac_mean:.4f}, std={pac_std:.4f}")

    # Create datasets
    train_dataset = LongWindowTemporalDataset(
        train_windows, train_pac, train_subjects, train_spectral,
        lookback=lookback, horizon=horizon
    )

    val_dataset = LongWindowTemporalDataset(
        val_windows, val_pac, val_subjects, val_spectral,
        lookback=lookback, horizon=horizon
    )

    test_dataset = LongWindowTemporalDataset(
        test_windows, test_pac, test_subjects, test_spectral,
        lookback=lookback, horizon=horizon
    )

    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    normalization_stats = {
        'pac_mean': pac_mean,
        'pac_std': pac_std
    }

    return train_loader, val_loader, test_loader, normalization_stats


def train_epoch(model, train_loader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    n_batches = 0

    for batch in train_loader:
        eeg = batch['eeg'].to(device)
        pac_history = batch['pac_history'].to(device)
        spectral = batch['spectral'].to(device)
        target = batch['target'].to(device)

        optimizer.zero_grad()

        # Forward pass
        output = model(eeg, pac_history, spectral)
        loss = criterion(output.squeeze(), target)

        # Backward pass
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
        optimizer.step()

        total_loss += loss.item()
        n_batches += 1

    return total_loss / n_batches


def evaluate(model, loader, device, pac_mean, pac_std):
    """Evaluate model and return metrics in original scale."""
    model.eval()
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for batch in loader:
            eeg = batch['eeg'].to(device)
            pac_history = batch['pac_history'].to(device)
            spectral = batch['spectral'].to(device)
            target = batch['target'].to(device)

            output = model(eeg, pac_history, spectral)

            all_preds.append(output.cpu().numpy())
            all_targets.append(target.cpu().numpy())

    preds = np.concatenate(all_preds).flatten()
    targets = np.concatenate(all_targets).flatten()

    # Denormalize to original scale
    preds_orig = preds * pac_std + pac_mean
    targets_orig = targets * pac_std + pac_mean

    # Compute metrics
    r2 = r2_score(targets_orig, preds_orig)
    mae = mean_absolute_error(targets_orig, preds_orig)
    corr = np.corrcoef(targets_orig, preds_orig)[0, 1]

    return r2, mae, corr, preds_orig, targets_orig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lookback', type=int, default=5,
                        help='Windows to look back (5 = 20 sec history)')
    parser.add_argument('--horizon', type=int, default=2,
                        help='Windows ahead to predict (2 = 8 sec ahead)')
    parser.add_argument('--epochs', type=int, default=150)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--hidden_size', type=int, default=128)
    parser.add_argument('--num_layers', type=int, default=2)
    args = parser.parse_args()

    print("="*80)
    print("TEMPORAL PAC PREDICTION WITH LONG WINDOWS (8-SECOND)")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Lookback: {args.lookback} windows ({args.lookback * 4} seconds)")
    print(f"  Horizon: {args.horizon} windows ({args.horizon * 4} seconds ahead)")
    print(f"  Epochs: {args.epochs}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Learning rate: {args.lr}")
    print(f"  Hidden size: {args.hidden_size}")
    print(f"  LSTM layers: {args.num_layers}")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\nDevice: {device}")

    # Data paths
    base_dir = Path('/sessions/serene-gifted-feynman/mnt/closedloop-40hz-entrainment')
    data_dir = base_dir / 'data' / 'processed' / 'long_windows'
    results_dir = base_dir / 'temporal' / 'results_long_windows'
    results_dir.mkdir(parents=True, exist_ok=True)

    # Create dataloaders
    train_loader, val_loader, test_loader, norm_stats = create_dataloaders(
        data_dir,
        lookback=args.lookback,
        horizon=args.horizon,
        batch_size=args.batch_size
    )

    # Initialize model
    model = TemporalPACPredictor(
        n_channels=7,
        n_timepoints=2000,  # 8 seconds at 250Hz
        hidden_size=args.hidden_size,
        num_layers=args.num_layers
    ).to(device)

    print(f"\nModel architecture:")
    print(f"  Parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Training setup
    criterion = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    # Training loop
    print("\n" + "="*80)
    print("TRAINING")
    print("="*80)

    best_val_r2 = -np.inf
    best_epoch = 0
    patience = 30
    patience_counter = 0

    history = {
        'train_loss': [],
        'val_r2': [],
        'val_mae': [],
        'val_corr': []
    }

    for epoch in range(args.epochs):
        # Train
        train_loss = train_epoch(model, train_loader, criterion, optimizer, device)

        # Validate
        val_r2, val_mae, val_corr, _, _ = evaluate(
            model, val_loader, device,
            norm_stats['pac_mean'], norm_stats['pac_std']
        )

        scheduler.step()

        # Log
        history['train_loss'].append(train_loss)
        history['val_r2'].append(val_r2)
        history['val_mae'].append(val_mae)
        history['val_corr'].append(val_corr)

        print(f"Epoch {epoch+1:3d}/{args.epochs} | "
              f"Loss: {train_loss:.4f} | "
              f"Val R²: {val_r2:7.4f} | "
              f"Val MAE: {val_mae:.4f} | "
              f"Val Corr: {val_corr:.4f}")

        # Save best model
        if val_r2 > best_val_r2:
            best_val_r2 = val_r2
            best_epoch = epoch + 1
            patience_counter = 0

            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_r2': val_r2,
                'args': vars(args),
                'norm_stats': norm_stats
            }, results_dir / 'best_model.pt')
        else:
            patience_counter += 1

        if patience_counter >= patience:
            print(f"\nEarly stopping at epoch {epoch+1}")
            break

    # Load best model and evaluate on test set
    print("\n" + "="*80)
    print("TEST SET EVALUATION")
    print("="*80)

    checkpoint = torch.load(results_dir / 'best_model.pt')
    model.load_state_dict(checkpoint['model_state_dict'])

    test_r2, test_mae, test_corr, test_preds, test_targets = evaluate(
        model, test_loader, device,
        norm_stats['pac_mean'], norm_stats['pac_std']
    )

    print(f"\nBest model (epoch {best_epoch}):")
    print(f"  Validation R²: {best_val_r2:.4f}")
    print(f"  Test R²: {test_r2:.4f}")
    print(f"  Test MAE: {test_mae:.4f}")
    print(f"  Test Correlation: {test_corr:.4f}")

    # Save results
    results = {
        'best_epoch': int(best_epoch),
        'best_val_r2': float(best_val_r2),
        'test_r2': float(test_r2),
        'test_mae': float(test_mae),
        'test_corr': float(test_corr),
        'config': vars(args),
        'normalization': norm_stats,
        'history': {k: [float(x) for x in v] for k, v in history.items()}
    }

    with open(results_dir / 'training_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    np.save(results_dir / 'test_predictions.npy', test_preds)
    np.save(results_dir / 'test_targets.npy', test_targets)

    print(f"\n✓ Results saved to: {results_dir}")

    # Final verdict
    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)

    if test_r2 > 0.6:
        print(f"✓ SUCCESS! Test R² = {test_r2:.3f} > 0.6")
        print("  Long windows created temporal structure → LSTM can predict future PAC")
    elif test_r2 > 0.3:
        print(f"⚠ PARTIAL SUCCESS: Test R² = {test_r2:.3f}")
        print("  Better than 2-sec windows (R²=-0.05) but below target (0.6)")
        print("  Consider: longer windows (10-12s) or incorporating stimulation context")
    else:
        print(f"✗ FAILED: Test R² = {test_r2:.3f} < 0.3")
        print("  PAC still lacks temporal structure even with 8-second windows")
        print("  May need 15-30 second windows like methodology papers")

    print("="*80)


if __name__ == '__main__':
    main()
