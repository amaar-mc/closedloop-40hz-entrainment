#!/usr/bin/env python3
"""
SpecTempNet Training Runner (Version 3)

Trains the hybrid spectral-temporal network for PAC prediction.

Key improvements over v1/v2:
- Multi-scale temporal CNN (captures different frequency patterns)
- Explicit spectral features (theta/gamma power, phase-amplitude coupling)
- Multi-head attention (learns feature importance)
- Deeper network (~180k params vs 1.4k-25k)
- Better regularization

Expected: R² = 0.30-0.50 (vs 0.06-0.08 in v1/v2)

Usage:
    python run_training_v3.py

Author: Amaar Chughtai
Date: February 2026
"""

import sys
import os
sys.path.insert(0, 'src')

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from spectral_features import SpectralFeatureExtractor
from spectempnet import SpecTempNet, count_parameters
import time
from pathlib import Path


class EEGDatasetV3(Dataset):
    """
    Dataset with both raw EEG and pre-computed spectral features.
    """

    def __init__(self, X_eeg, X_spectral, y, augment=False):
        self.X_eeg = torch.FloatTensor(X_eeg)
        self.X_spectral = torch.FloatTensor(X_spectral)
        self.y = torch.FloatTensor(y)
        self.augment = augment

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        eeg = self.X_eeg[idx]  # (7, 500)
        spectral = self.X_spectral[idx]  # (68,)
        y = self.y[idx]

        # Add channel dimension to EEG
        eeg = eeg.unsqueeze(0)  # (1, 7, 500)

        # Simple augmentation during training
        if self.augment and np.random.rand() < 0.5:
            # Time jitter
            if np.random.rand() < 0.5:
                shift = np.random.randint(-25, 25)
                eeg = torch.roll(eeg, shifts=shift, dims=2)

            # Amplitude scaling
            if np.random.rand() < 0.5:
                scale = np.random.uniform(0.95, 1.05)
                eeg = eeg * scale

        return eeg, spectral, y


def load_and_preprocess_data(data_dir='data/processed'):
    """
    Load processed data and extract spectral features.
    """
    print("\n" + "="*70)
    print("Loading Data & Extracting Spectral Features (V3)")
    print("="*70)

    # Load data
    train_data = np.load(os.path.join(data_dir, 'train_data.npz'))
    val_data = np.load(os.path.join(data_dir, 'val_data.npz'))
    test_data = np.load(os.path.join(data_dir, 'test_data.npz'))

    X_train = train_data['windows'].squeeze(1)  # (n, 7, 500)
    y_train = train_data['pac']

    X_val = val_data['windows'].squeeze(1)
    y_val = val_data['pac']

    X_test = test_data['windows'].squeeze(1)
    y_test = test_data['pac']

    print(f"✓ Loaded EEG data")
    print(f"  Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")

    # Extract spectral features
    print(f"\nExtracting spectral features...")
    extractor = SpectralFeatureExtractor(fs=250.0)

    print(f"  Processing training set...")
    X_train_spectral = extractor.extract(X_train)

    print(f"  Processing validation set...")
    X_val_spectral = extractor.extract(X_val)

    print(f"  Processing test set...")
    X_test_spectral = extractor.extract(X_test)

    print(f"✓ Spectral features extracted: {X_train_spectral.shape[1]} features per sample")

    # Compute normalization statistics
    pac_mean = y_train.mean()
    pac_std = y_train.std()

    spectral_mean = X_train_spectral.mean(axis=0)
    spectral_std = X_train_spectral.std(axis=0) + 1e-8

    print(f"\nNormalization statistics:")
    print(f"  PAC: mean={pac_mean:.6f}, std={pac_std:.6f}")
    print(f"  Spectral features: mean={spectral_mean[:5]}, std={spectral_std[:5]}")

    # Normalize
    y_train_norm = (y_train - pac_mean) / pac_std
    y_val_norm = (y_val - pac_mean) / pac_std
    y_test_norm = (y_test - pac_mean) / pac_std

    X_train_spectral_norm = (X_train_spectral - spectral_mean) / spectral_std
    X_val_spectral_norm = (X_val_spectral - spectral_mean) / spectral_std
    X_test_spectral_norm = (X_test_spectral - spectral_mean) / spectral_std

    # Create datasets
    train_dataset = EEGDatasetV3(X_train, X_train_spectral_norm, y_train_norm, augment=True)
    val_dataset = EEGDatasetV3(X_val, X_val_spectral_norm, y_val_norm, augment=False)
    test_dataset = EEGDatasetV3(X_test, X_test_spectral_norm, y_test_norm, augment=False)

    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=0, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False, num_workers=0, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False, num_workers=0, pin_memory=True)

    stats = {
        'pac_mean': float(pac_mean),
        'pac_std': float(pac_std),
        'spectral_mean': spectral_mean,
        'spectral_std': spectral_std
    }

    print(f"\n✓ Data loaders created:")
    print(f"  Train batches: {len(train_loader)} (batch_size=32)")
    print(f"  Val batches: {len(val_loader)} (batch_size=64)")
    print(f"  Test batches: {len(test_loader)} (batch_size=64)")
    print("="*70 + "\n")

    return train_loader, val_loader, test_loader, stats


def compute_r2(y_true, y_pred):
    """Compute R² score."""
    ss_res = ((y_true - y_pred) ** 2).sum()
    ss_tot = ((y_true - y_true.mean()) ** 2).sum()
    r2 = 1 - ss_res / ss_tot
    return float(r2)


def train_epoch(model, loader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    n_batches = 0

    for eeg, spectral, y in loader:
        eeg = eeg.to(device)
        spectral = spectral.to(device)
        y = y.to(device)

        # Forward
        y_pred = model(eeg, spectral).squeeze()

        # Loss
        loss = criterion(y_pred, y)

        # Backward
        optimizer.zero_grad()
        loss.backward()

        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        optimizer.step()

        total_loss += loss.item()
        n_batches += 1

    return total_loss / n_batches


def evaluate(model, loader, criterion, device):
    """Evaluate on validation/test set."""
    model.eval()
    total_loss = 0
    y_true_list = []
    y_pred_list = []

    with torch.no_grad():
        for eeg, spectral, y in loader:
            eeg = eeg.to(device)
            spectral = spectral.to(device)
            y = y.to(device)

            y_pred = model(eeg, spectral).squeeze()
            loss = criterion(y_pred, y)

            total_loss += loss.item()
            y_true_list.append(y.cpu().numpy())
            y_pred_list.append(y_pred.cpu().numpy())

    y_true = np.concatenate(y_true_list)
    y_pred = np.concatenate(y_pred_list)

    r2 = compute_r2(y_true, y_pred)
    mae = np.abs(y_true - y_pred).mean()
    corr = np.corrcoef(y_true, y_pred)[0, 1] if len(y_true) > 1 else 0.0

    return total_loss / len(loader), r2, mae, corr


def main():
    print("\n" + "="*80)
    print("SPECTEMPNET TRAINING (Version 3)")
    print("="*80)
    print("\nHybrid Spectral-Temporal Architecture:")
    print("  ✓ Multi-scale temporal CNN (different freq patterns)")
    print("  ✓ Explicit spectral features (theta/gamma power, PAC)")
    print("  ✓ Multi-head attention (feature fusion)")
    print("  ✓ Deep regression head (~180k parameters)")
    print("\nTarget: R² > 0.30 (vs 0.06-0.08 in v1/v2)")
    print("="*80 + "\n")

    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    # Load data
    train_loader, val_loader, test_loader, stats = load_and_preprocess_data()

    # Create model (61 features: MI removed for clean prediction)
    print("Creating SpecTempNet model...")
    model = SpecTempNet(n_channels=7, n_samples=500, n_spectral_features=61)
    model = model.to(device)

    n_params = count_parameters(model)
    print(f"  Total parameters: {n_params:,}")
    print(f"  Model size: ~{n_params * 4 / 1024:.1f} KB\n")

    # Loss & optimizer
    criterion = nn.SmoothL1Loss()  # Robust to outliers
    optimizer = optim.AdamW(model.parameters(), lr=0.0003, weight_decay=0.0005)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=7
    )

    # Training loop
    print("="*70)
    print("Starting Training")
    print("="*70)
    print(f"Max epochs: 200")
    print(f"Early stopping patience: 25")
    print(f"Learning rate: 0.0003")
    print(f"Loss: SmoothL1Loss")
    print("="*70 + "\n")

    best_val_r2 = -np.inf
    best_epoch = 0
    patience_counter = 0
    patience = 25

    history = {
        'train_loss': [],
        'val_loss': [],
        'val_r2': [],
        'val_mae': [],
        'val_corr': [],
        'lr': []
    }

    start_time = time.time()

    for epoch in range(200):
        epoch_start = time.time()

        # Train
        train_loss = train_epoch(model, train_loader, criterion, optimizer, device)

        # Evaluate
        val_loss, val_r2, val_mae, val_corr = evaluate(model, val_loader, criterion, device)

        # Learning rate
        current_lr = optimizer.param_groups[0]['lr']
        scheduler.step(val_loss)

        # Save history
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['val_r2'].append(val_r2)
        history['val_mae'].append(val_mae)
        history['val_corr'].append(val_corr)
        history['lr'].append(current_lr)

        epoch_time = time.time() - epoch_start

        # Print progress
        print(f"Epoch {epoch+1:3d}/200 | Time: {epoch_time:5.1f}s | LR: {current_lr:.6f}")
        print(f"  Train Loss: {train_loss:.6f} | Val Loss: {val_loss:.6f}")
        print(f"  Val R²: {val_r2:7.4f} | Val MAE: {val_mae:.6f} | Val Corr: {val_corr:+.4f}")

        # Check for improvement
        if val_r2 > best_val_r2:
            best_val_r2 = val_r2
            best_epoch = epoch
            patience_counter = 0

            # Save best model
            Path('models').mkdir(exist_ok=True)
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_r2': val_r2,
                'val_loss': val_loss
            }, 'models/best_spectempnet_v3.pth')

            print(f"  ⭐ New best R²! Model saved.")
        else:
            patience_counter += 1
            print(f"  No improvement ({patience_counter}/{patience})")

        print()

        # Early stopping
        if patience_counter >= patience:
            print(f"Early stopping triggered at epoch {epoch+1}")
            break

    total_time = time.time() - start_time

    # Save history
    np.savez('models/training_history_v3.npz',
             train_loss=history['train_loss'],
             val_loss=history['val_loss'],
             val_r2=history['val_r2'],
             val_mae=history['val_mae'],
             val_corr=history['val_corr'],
             lr=history['lr'],
             best_val_r2=best_val_r2,
             best_epoch=best_epoch)

    # Save stats
    np.savez('models/spectempnet_stats_v3.npz', **stats)

    print("\n" + "="*70)
    print("Training Completed!")
    print("="*70)
    print(f"  Total time: {total_time/60:.1f} minutes")
    print(f"  Best epoch: {best_epoch + 1}")
    print(f"  Best val R²: {best_val_r2:.4f}")
    print(f"  Model saved to: models/best_spectempnet_v3.pth")
    print("="*70 + "\n")

    # Evaluate on test set
    print("Evaluating on test set...")
    checkpoint = torch.load('models/best_spectempnet_v3.pth')
    model.load_state_dict(checkpoint['model_state_dict'])

    test_loss, test_r2, test_mae, test_corr = evaluate(model, test_loader, criterion, device)

    print(f"\nTest Set Performance:")
    print(f"  Test Loss: {test_loss:.6f}")
    print(f"  Test R²: {test_r2:.4f}")
    print(f"  Test MAE: {test_mae:.6f}")
    print(f"  Test Correlation: {test_corr:+.4f}")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    input("Press Enter to start training (or Ctrl+C to cancel)...")
    main()
