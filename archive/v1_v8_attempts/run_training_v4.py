#!/usr/bin/env python3
"""
ViT-TCNet Training Runner (Version 4)

Implements state-of-the-art improvements for PAC prediction:
- ViT-TCNet architecture (pre-trained ViT + TCN)
- Wavelet features (CWT + WPD) in addition to spectral features
- Enhanced data augmentation (time warp, magnitude warp, etc.)
- Huber loss (robust to outliers)
- Progressive dropout and improved regularization

Expected improvement: R² = 0.46-0.55 (vs 0.236 in v3-clean)

Based on research from:
- "Fusing Pretrained ViTs with TCNet for Enhanced EEG Regression" (2024)
- "EEG Data Augmentation Based on Improved GAN" (2024)
- "Adaptive cross-frequency coupling networks" (2024)

Usage:
    python run_training_v4.py

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
from wavelet_features import WaveletFeatureExtractor
from data_augmentation import EEGAugmentation
from vit_tcnet import ViTTCNet, count_parameters
import time
from pathlib import Path


class EEGDatasetV4(Dataset):
    """
    Dataset with raw EEG, spectral features, and wavelet features.
    Includes data augmentation.
    """

    def __init__(self, X_eeg, X_spectral, X_wavelet, y, augment=False):
        self.X_eeg = X_eeg  # Keep as numpy for augmentation
        self.X_spectral = torch.FloatTensor(X_spectral)
        self.X_wavelet = torch.FloatTensor(X_wavelet)
        self.y = torch.FloatTensor(y)
        self.augment_flag = augment

        if augment:
            self.augmenter = EEGAugmentation(
                time_warp=True,
                magnitude_warp=True,
                time_shift=True,
                gaussian_noise=True,
                channel_dropout=True
            )

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        eeg = self.X_eeg[idx]  # (7, 500)
        spectral = self.X_spectral[idx]
        wavelet = self.X_wavelet[idx]
        y = self.y[idx]

        # Apply augmentation to raw EEG
        if self.augment_flag:
            eeg = self.augmenter(eeg)

        # Convert to tensor
        eeg = torch.FloatTensor(eeg)

        # Add channel dimension
        eeg = eeg.unsqueeze(0)  # (1, 7, 500)

        return eeg, spectral, wavelet, y


def load_and_preprocess_data(data_dir='data/processed'):
    """
    Load processed data and extract both spectral and wavelet features.
    """
    print("\n" + "="*70)
    print("Loading Data & Extracting Features (V4)")
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
    spectral_extractor = SpectralFeatureExtractor(fs=250.0)

    print(f"  Processing training set...")
    X_train_spectral = spectral_extractor.extract(X_train)

    print(f"  Processing validation set...")
    X_val_spectral = spectral_extractor.extract(X_val)

    print(f"  Processing test set...")
    X_test_spectral = spectral_extractor.extract(X_test)

    print(f"✓ Spectral features extracted: {X_train_spectral.shape[1]} features per sample")

    # Extract wavelet features
    print(f"\nExtracting wavelet features...")
    wavelet_extractor = WaveletFeatureExtractor(fs=250.0)

    print(f"  Processing training set...")
    X_train_wavelet = wavelet_extractor.extract(X_train)

    print(f"  Processing validation set...")
    X_val_wavelet = wavelet_extractor.extract(X_val)

    print(f"  Processing test set...")
    X_test_wavelet = wavelet_extractor.extract(X_test)

    print(f"✓ Wavelet features extracted: {X_train_wavelet.shape[1]} features per sample")
    print(f"✓ Total features: {X_train_spectral.shape[1] + X_train_wavelet.shape[1]}")

    # Compute normalization statistics
    pac_mean = y_train.mean()
    pac_std = y_train.std()

    spectral_mean = X_train_spectral.mean(axis=0)
    spectral_std = X_train_spectral.std(axis=0) + 1e-8

    wavelet_mean = X_train_wavelet.mean(axis=0)
    wavelet_std = X_train_wavelet.std(axis=0) + 1e-8

    print(f"\nNormalization statistics:")
    print(f"  PAC: mean={pac_mean:.6f}, std={pac_std:.6f}")
    print(f"  Spectral: mean={spectral_mean[:3]}, std={spectral_std[:3]}")
    print(f"  Wavelet: mean={wavelet_mean[:3]}, std={wavelet_std[:3]}")

    # Normalize
    y_train_norm = (y_train - pac_mean) / pac_std
    y_val_norm = (y_val - pac_mean) / pac_std
    y_test_norm = (y_test - pac_mean) / pac_std

    X_train_spectral_norm = (X_train_spectral - spectral_mean) / spectral_std
    X_val_spectral_norm = (X_val_spectral - spectral_mean) / spectral_std
    X_test_spectral_norm = (X_test_spectral - spectral_mean) / spectral_std

    X_train_wavelet_norm = (X_train_wavelet - wavelet_mean) / wavelet_std
    X_val_wavelet_norm = (X_val_wavelet - wavelet_mean) / wavelet_std
    X_test_wavelet_norm = (X_test_wavelet - wavelet_mean) / wavelet_std

    # Create datasets
    train_dataset = EEGDatasetV4(
        X_train, X_train_spectral_norm, X_train_wavelet_norm, y_train_norm, augment=True
    )
    val_dataset = EEGDatasetV4(
        X_val, X_val_spectral_norm, X_val_wavelet_norm, y_val_norm, augment=False
    )
    test_dataset = EEGDatasetV4(
        X_test, X_test_spectral_norm, X_test_wavelet_norm, y_test_norm, augment=False
    )

    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=0, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False, num_workers=0, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False, num_workers=0, pin_memory=True)

    stats = {
        'pac_mean': float(pac_mean),
        'pac_std': float(pac_std),
        'spectral_mean': spectral_mean,
        'spectral_std': spectral_std,
        'wavelet_mean': wavelet_mean,
        'wavelet_std': wavelet_std
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

    for eeg, spectral, wavelet, y in loader:
        eeg = eeg.to(device)
        spectral = spectral.to(device)
        wavelet = wavelet.to(device)
        y = y.to(device)

        # Forward
        y_pred = model(eeg, spectral, wavelet).squeeze()

        # Loss
        loss = criterion(y_pred, y)

        # Backward
        optimizer.zero_grad()
        loss.backward()

        # Gradient clipping (tighter for stability)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)

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
        for eeg, spectral, wavelet, y in loader:
            eeg = eeg.to(device)
            spectral = spectral.to(device)
            wavelet = wavelet.to(device)
            y = y.to(device)

            y_pred = model(eeg, spectral, wavelet).squeeze()
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
    print("VIT-TCNET TRAINING (Version 4)")
    print("="*80)
    print("\nState-of-the-Art Architecture:")
    print("  ✓ ViT-TCNet (Vision Transformer + Temporal Convolutional Network)")
    print("  ✓ Wavelet features (CWT + WPD) + spectral features")
    print("  ✓ Enhanced data augmentation (time warp, magnitude warp, etc.)")
    print("  ✓ Huber loss (robust to outliers)")
    print("  ✓ Progressive dropout + improved regularization")
    print("\nTarget: R² = 0.46-0.55 (vs 0.236 in v3-clean)")
    print("Expected training time: ~1 hour")
    print("="*80 + "\n")

    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    # Load data
    train_loader, val_loader, test_loader, stats = load_and_preprocess_data()

    # Create model
    print("Creating ViT-TCNet model...")
    model = ViTTCNet(
        n_channels=7,
        n_samples=500,
        n_spectral_features=61,
        n_wavelet_features=74,
        dropout=0.4
    )
    model = model.to(device)

    n_params = count_parameters(model)
    print(f"  Total parameters: {n_params:,}")
    print(f"  Model size: ~{n_params * 4 / 1024 / 1024:.1f} MB\n")

    # Loss & optimizer
    # Huber loss is more robust to outliers than MSE/SmoothL1
    criterion = nn.HuberLoss(delta=0.3)

    optimizer = optim.AdamW(
        model.parameters(),
        lr=0.0003,
        weight_decay=0.001,  # 2× higher than v3
        betas=(0.9, 0.999)
    )

    # Cosine annealing with warm restarts
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=20, T_mult=2, eta_min=1e-6
    )

    # Training loop
    print("="*70)
    print("Starting Training")
    print("="*70)
    print(f"Max epochs: 200")
    print(f"Early stopping patience: 30")
    print(f"Learning rate: 0.0003 (cosine annealing)")
    print(f"Loss: HuberLoss (delta=0.3)")
    print(f"Weight decay: 0.001")
    print("="*70 + "\n")

    best_val_r2 = -np.inf
    best_epoch = 0
    patience_counter = 0
    patience = 30  # More patience for larger model

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
        scheduler.step()

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
            }, 'models/best_vit_tcnet_v4.pth')

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
    np.savez('models/training_history_v4.npz',
             train_loss=history['train_loss'],
             val_loss=history['val_loss'],
             val_r2=history['val_r2'],
             val_mae=history['val_mae'],
             val_corr=history['val_corr'],
             lr=history['lr'],
             best_val_r2=best_val_r2,
             best_epoch=best_epoch)

    # Save stats
    np.savez('models/vit_tcnet_stats_v4.npz', **stats)

    print("\n" + "="*70)
    print("Training Completed!")
    print("="*70)
    print(f"  Total time: {total_time/60:.1f} minutes")
    print(f"  Best epoch: {best_epoch + 1}")
    print(f"  Best val R²: {best_val_r2:.4f}")
    print(f"  Improvement over V3-Clean: {(best_val_r2 - 0.236) / 0.236 * 100:+.1f}%")
    print(f"  Model saved to: models/best_vit_tcnet_v4.pth")
    print("="*70 + "\n")

    # Evaluate on test set
    print("Evaluating on test set...")
    checkpoint = torch.load('models/best_vit_tcnet_v4.pth')
    model.load_state_dict(checkpoint['model_state_dict'])

    test_loss, test_r2, test_mae, test_corr = evaluate(model, test_loader, criterion, device)

    print(f"\nTest Set Performance:")
    print(f"  Test Loss: {test_loss:.6f}")
    print(f"  Test R²: {test_r2:.4f}")
    print(f"  Test MAE: {test_mae:.6f}")
    print(f"  Test Correlation: {test_corr:+.4f}")

    # Comparison with V3-Clean
    print(f"\n📊 Performance Comparison:")
    print(f"  V3-Clean (baseline):  R² = 0.236, Corr = 0.50")
    print(f"  V4 ViT-TCNet:        R² = {test_r2:.3f}, Corr = {test_corr:.2f}")
    print(f"  Improvement:          {(test_r2 - 0.236) / 0.236 * 100:+.1f}% R², {(test_corr - 0.50) / 0.50 * 100:+.1f}% Corr")

    if test_r2 >= 0.45:
        print(f"\n✅ SUCCESS! Achieved target R² ≥ 0.45")
    elif test_r2 >= 0.35:
        print(f"\n⚠️  Good progress, but below target. Consider Phase 3 improvements.")
    else:
        print(f"\n❌ Below expectations. Investigate training dynamics.")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    input("Press Enter to start training (or Ctrl+C to cancel)...")
    main()
