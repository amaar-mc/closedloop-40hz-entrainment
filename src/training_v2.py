"""
Enhanced Training Script for EEGNetV2 (Version 2)

Key improvements over v1:
- Huber loss (robust to outliers)
- Cosine annealing learning rate schedule
- Gradient clipping
- Longer training (150 epochs, patience=20)
- Better metrics tracking

Author: Amaar Chughtai
Date: February 2026
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from typing import Dict, Tuple
import sys
import os
import time
from pathlib import Path

sys.path.append('/sessions/inspiring-exciting-feynman/mnt/closedloop-40hz-entrainment/src')

from eegnet_v2 import EEGNetV2, count_parameters
from data_loader_v2 import load_processed_data_v2


class ModelTrainerV2:
    """
    Enhanced trainer for EEGNetV2 with improved training strategies.
    """

    def __init__(self,
                 model: nn.Module,
                 device: str = 'cuda',
                 learning_rate: float = 0.001,
                 weight_decay: float = 0.0001,
                 max_epochs: int = 150,
                 patience: int = 20,
                 grad_clip: float = 1.0):
        """
        Args:
            model: EEGNetV2 model
            device: 'cuda' or 'cpu'
            learning_rate: Initial learning rate
            weight_decay: L2 regularization
            max_epochs: Maximum training epochs
            patience: Early stopping patience
            grad_clip: Gradient clipping max norm
        """
        self.model = model.to(device)
        self.device = device
        self.max_epochs = max_epochs
        self.patience = patience
        self.grad_clip = grad_clip

        # Huber loss (robust to outliers)
        self.criterion = nn.HuberLoss(delta=1.0)

        # Adam optimizer with weight decay
        self.optimizer = optim.AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay,
            betas=(0.9, 0.999)
        )

        # Cosine annealing schedule
        self.scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
            self.optimizer,
            T_0=10,  # Restart every 10 epochs
            T_mult=2,  # Double period after each restart
            eta_min=1e-6
        )

        # Training state
        self.best_val_loss = float('inf')
        self.best_val_r2 = -float('inf')
        self.patience_counter = 0
        self.train_losses = []
        self.val_losses = []
        self.val_r2_scores = []
        self.learning_rates = []

    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        n_batches = 0

        for batch_idx, (x, y_delta, y_current) in enumerate(train_loader):
            x = x.to(self.device)
            y_delta = y_delta.to(self.device)

            # Forward pass
            pred_delta = self.model(x).squeeze()

            # Compute loss
            loss = self.criterion(pred_delta, y_delta)

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()

            # Gradient clipping
            if self.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.grad_clip
                )

            self.optimizer.step()

            total_loss += loss.item()
            n_batches += 1

        avg_loss = total_loss / n_batches
        return avg_loss

    def validate(self, val_loader: DataLoader) -> Tuple[float, float, float, float]:
        """
        Validate model.

        Returns:
            val_loss, val_r2, val_mae, val_corr
        """
        self.model.eval()
        total_loss = 0.0
        all_preds = []
        all_targets = []

        with torch.no_grad():
            for x, y_delta, y_current in val_loader:
                x = x.to(self.device)
                y_delta = y_delta.to(self.device)

                # Predict
                pred_delta = self.model(x).squeeze()

                # Loss
                loss = self.criterion(pred_delta, y_delta)
                total_loss += loss.item()

                # Store for metrics
                all_preds.append(pred_delta.cpu().numpy())
                all_targets.append(y_delta.cpu().numpy())

        # Aggregate
        val_loss = total_loss / len(val_loader)
        all_preds = np.concatenate(all_preds)
        all_targets = np.concatenate(all_targets)

        # Compute metrics
        val_r2 = self._r2_score(all_targets, all_preds)
        val_mae = np.mean(np.abs(all_targets - all_preds))
        val_corr = np.corrcoef(all_targets, all_preds)[0, 1]

        return val_loss, val_r2, val_mae, val_corr

    def _r2_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute R² score."""
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - y_true.mean()) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        return float(r2)

    def fit(self, train_loader: DataLoader, val_loader: DataLoader,
            save_dir: str = 'models') -> Dict:
        """
        Train model with early stopping.

        Returns:
            training_history: Dict with metrics over epochs
        """
        print(f"\n{'='*70}")
        print(f"Starting Training - EEGNetV2 for ΔPAC Prediction")
        print(f"{'='*70}")
        print(f"Device: {self.device}")
        print(f"Max epochs: {self.max_epochs}")
        print(f"Early stopping patience: {self.patience}")
        print(f"Gradient clipping: {self.grad_clip}")
        print(f"Loss function: Huber Loss (delta=1.0)")
        print(f"{'='*70}\n")

        os.makedirs(save_dir, exist_ok=True)
        best_model_path = os.path.join(save_dir, 'best_eegnet_v2.pth')

        start_time = time.time()

        for epoch in range(1, self.max_epochs + 1):
            epoch_start = time.time()

            # Train
            train_loss = self.train_epoch(train_loader)

            # Validate
            val_loss, val_r2, val_mae, val_corr = self.validate(val_loader)

            # Step scheduler
            self.scheduler.step()
            current_lr = self.optimizer.param_groups[0]['lr']

            # Store metrics
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.val_r2_scores.append(val_r2)
            self.learning_rates.append(current_lr)

            epoch_time = time.time() - epoch_start

            # Print progress
            print(f"Epoch {epoch:3d}/{self.max_epochs} | "
                  f"Time: {epoch_time:5.1f}s | "
                  f"LR: {current_lr:.6f}")
            print(f"  Train Loss: {train_loss:.6f} | "
                  f"Val Loss: {val_loss:.6f}")
            print(f"  Val R²: {val_r2:7.4f} | "
                  f"Val MAE: {val_mae:.6f} | "
                  f"Val Corr: {val_corr:+.4f}")

            # Check for improvement
            improved = False
            if val_r2 > self.best_val_r2:
                self.best_val_r2 = val_r2
                self.best_val_loss = val_loss
                improved = True
                self.patience_counter = 0

                # Save best model
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'val_loss': val_loss,
                    'val_r2': val_r2,
                    'val_mae': val_mae,
                    'val_corr': val_corr,
                }, best_model_path)

                print(f"  ⭐ New best R²! Model saved.")

            else:
                self.patience_counter += 1
                print(f"  No improvement ({self.patience_counter}/{self.patience})")

            print()

            # Early stopping
            if self.patience_counter >= self.patience:
                print(f"Early stopping triggered at epoch {epoch}")
                print(f"Best validation R²: {self.best_val_r2:.4f}")
                break

        total_time = time.time() - start_time
        print(f"\n{'='*70}")
        print(f"Training Completed!")
        print(f"  Total time: {total_time/60:.1f} minutes")
        print(f"  Best epoch: {epoch - self.patience}")
        print(f"  Best val loss: {self.best_val_loss:.6f}")
        print(f"  Best val R²: {self.best_val_r2:.4f}")
        print(f"  Model saved to: {best_model_path}")
        print(f"{'='*70}\n")

        history = {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'val_r2_scores': self.val_r2_scores,
            'learning_rates': self.learning_rates,
            'best_val_r2': self.best_val_r2,
            'best_val_loss': self.best_val_loss,
        }

        return history


def main():
    """Main training script."""
    # Configuration
    config = {
        'data_dir': 'data/processed',
        'model_dir': 'models',
        'device': 'cuda' if torch.cuda.is_available() else 'cpu',
        'learning_rate': 0.001,
        'weight_decay': 0.0001,
        'max_epochs': 150,
        'patience': 20,
        'grad_clip': 1.0,
    }

    print("="*70)
    print("EEGNetV2 Training for ΔPAC Prediction")
    print("="*70)
    print(f"Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print("="*70)

    # Check device
    if config['device'] == 'cuda':
        print(f"\n✓ CUDA available")
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print(f"\n⚠ CUDA not available, using CPU (will be slow)")

    # Load data
    print(f"\nLoading data...")
    train_loader, val_loader, test_loader, pac_stats = load_processed_data_v2(
        data_dir=config['data_dir']
    )

    # Create model
    print(f"\nCreating EEGNetV2 model...")
    model = EEGNetV2(
        n_channels=7,
        n_samples=500,
        F1=12,
        D=2,
        F2=24,
        dropout=0.5
    )

    n_params = count_parameters(model)
    print(f"  Total parameters: {n_params:,}")
    print(f"  Model size: ~{n_params * 4 / 1024:.1f} KB")

    # Create trainer
    trainer = ModelTrainerV2(
        model=model,
        device=config['device'],
        learning_rate=config['learning_rate'],
        weight_decay=config['weight_decay'],
        max_epochs=config['max_epochs'],
        patience=config['patience'],
        grad_clip=config['grad_clip']
    )

    # Train
    history = trainer.fit(
        train_loader=train_loader,
        val_loader=val_loader,
        save_dir=config['model_dir']
    )

    # Save history
    history_path = os.path.join(config['model_dir'], 'training_history_v2.npz')
    np.savez(history_path, **history)
    print(f"Training history saved to: {history_path}")

    # Save PAC stats
    stats_path = os.path.join(config['model_dir'], 'pac_stats_v2.npz')
    np.savez(stats_path, **pac_stats)
    print(f"PAC statistics saved to: {stats_path}")

    print(f"\n{'='*70}")
    print(f"✓ Training pipeline completed successfully!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
