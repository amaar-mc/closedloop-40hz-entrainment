"""
Training Pipeline for EEGNet PAC Prediction Model

Implements model training with:
- MSE loss and Adam optimizer (lr=0.001, weight_decay=1e-4)
- ReduceLROnPlateau scheduler (factor=0.5, patience=5)
- Early stopping (patience=15)
- Model checkpointing (save best val loss)
- Data augmentation (time shifting, amplitude scaling, Gaussian noise)
- Comprehensive logging and metrics tracking

Training loop handles GPU/CPU, mixed precision (optional), and graceful error recovery.

Author: Amaar Chughtai
Date: February 2026
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import numpy as np

# Ensure src/ is on the import path when run as script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau

from tqdm import tqdm

# Import project modules
from eegnet import EEGNet
from utils import setup_logging, ensure_dir, count_parameters, compute_regression_metrics


logger = logging.getLogger('closed_loop_entrainment')


class DataAugmentor:
    """
    Applies data augmentation to EEG windows.

    Augmentation strategies:
        1. Time shifting: +/-100-500 ms shift
        2. Amplitude scaling: 0.8-1.2x scaling
        3. Gaussian noise: SNR 20-30 dB
    """

    def __init__(self, fs: float = 250.0, max_shift_ms: float = 100.0):
        """
        Initialize augmentor.

        Args:
            fs: Sampling frequency (Hz)
            max_shift_ms: Maximum time shift in milliseconds
        """
        self.fs = fs
        self.max_shift_samples = int(max_shift_ms * fs / 1000.0)

    def time_shift(self, window: np.ndarray) -> np.ndarray:
        """
        Randomly shift window in time along the last axis.

        Args:
            window: EEG window, any shape with time as last dim
                    e.g. (1, n_channels, n_samples) or (n_channels, n_samples)

        Returns:
            shifted: Time-shifted window (same shape)
        """
        shift = np.random.randint(-self.max_shift_samples, self.max_shift_samples + 1)
        if shift == 0:
            return window.copy()
        # Use zero-padding instead of np.roll to avoid wrap-around artifacts
        # where the end of the signal wraps to the beginning.
        shifted = np.zeros_like(window)
        if shift > 0:
            shifted[..., shift:] = window[..., :-shift]
        else:
            shifted[..., :shift] = window[..., -shift:]
        return shifted

    def amplitude_scaling(self, window: np.ndarray,
                         scale_range: Tuple[float, float] = (0.8, 1.2)) -> np.ndarray:
        """
        Randomly scale amplitude.

        Args:
            window: EEG window
            scale_range: (min_scale, max_scale)

        Returns:
            scaled: Amplitude-scaled window
        """
        scale = np.random.uniform(scale_range[0], scale_range[1])
        return window * scale

    def add_gaussian_noise(self, window: np.ndarray,
                          snr_db_range: Tuple[float, float] = (20.0, 30.0)) -> np.ndarray:
        """
        Add Gaussian noise at specified SNR.

        Args:
            window: EEG window
            snr_db_range: (min_snr, max_snr) in dB

        Returns:
            noisy: Window with added noise
        """
        snr_db = np.random.uniform(snr_db_range[0], snr_db_range[1])
        snr_linear = 10 ** (snr_db / 10.0)

        # Estimate signal power
        signal_power = np.mean(window ** 2)
        noise_power = signal_power / snr_linear

        # Add noise
        noise = np.sqrt(noise_power) * np.random.randn(*window.shape)
        noisy = window + noise

        return noisy

    def augment(self, window: np.ndarray, augmentation_prob: float = 0.5) -> np.ndarray:
        """
        Apply random augmentations.

        Args:
            window: Input window
            augmentation_prob: Probability to apply each augmentation

        Returns:
            augmented: Augmented window
        """
        augmented = window.copy()

        # Time shifting
        if np.random.rand() < augmentation_prob:
            augmented = self.time_shift(augmented)

        # Amplitude scaling
        if np.random.rand() < augmentation_prob:
            augmented = self.amplitude_scaling(augmented)

        # Gaussian noise
        if np.random.rand() < augmentation_prob:
            augmented = self.add_gaussian_noise(augmented)

        return augmented


class ModelTrainer:
    """
    Handles model training, validation, and checkpointing.

    Features:
        - Gradient descent with Adam optimizer
        - Learning rate scheduling with ReduceLROnPlateau
        - Early stopping based on validation loss
        - Best model checkpointing
        - Training metrics logging
        - GPU/CPU support
    """

    def __init__(self,
                 model: nn.Module,
                 device: str,
                 learning_rate: float = 0.001,
                 weight_decay: float = 1e-4,
                 patience_lr: int = 5,
                 patience_early_stop: int = 15):
        """
        Initialize trainer.

        Args:
            model: PyTorch model
            device: 'cuda' or 'cpu'
            learning_rate: Initial learning rate
            weight_decay: L2 regularization
            patience_lr: Patience for LR scheduler
            patience_early_stop: Patience for early stopping
        """
        self.model = model
        self.device = device
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.patience_lr = patience_lr
        self.patience_early_stop = patience_early_stop

        # Loss function
        self.criterion = nn.MSELoss()

        # Optimizer
        self.optimizer = optim.Adam(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )

        # Learning rate scheduler
        self.scheduler = ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=patience_lr
        )

        # Tracking
        self.train_losses = []
        self.val_losses = []
        self.best_val_loss = float('inf')
        self.best_epoch = 0
        self.patience_counter = 0

        logger.info(f"ModelTrainer initialized:")
        logger.info(f"  Device: {device}")
        logger.info(f"  LR: {learning_rate}, Weight Decay: {weight_decay}")
        logger.info(f"  Early stopping patience: {patience_early_stop}")

    def train_epoch(self, train_loader: DataLoader, augmentor: Optional[DataAugmentor] = None) -> float:
        """
        Train for one epoch.

        Args:
            train_loader: Training DataLoader
            augmentor: Optional data augmentor

        Returns:
            epoch_loss: Average training loss
        """
        self.model.train()
        total_loss = 0.0
        n_batches = 0

        pbar = tqdm(train_loader, desc="Training", leave=False)

        for batch_x, batch_y in pbar:
            # Data augmentation on CPU before GPU transfer
            if augmentor is not None:
                batch_x_np = batch_x.numpy()
                for i in range(len(batch_x_np)):
                    batch_x_np[i] = augmentor.augment(batch_x_np[i])
                batch_x = torch.from_numpy(batch_x_np).float()

            batch_x = batch_x.to(self.device)  # (batch, 1, n_channels, n_samples)
            batch_y = batch_y.to(self.device)  # (batch,)

            # Forward pass
            self.optimizer.zero_grad()
            output = self.model(batch_x)  # (batch, 1)
            output = output.squeeze(-1)    # (batch,)

            # Compute loss
            loss = self.criterion(output, batch_y)

            # Backward pass
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()

            # Track loss
            total_loss += loss.item()
            n_batches += 1

            pbar.set_postfix({'loss': total_loss / n_batches})

        epoch_loss = total_loss / n_batches
        return epoch_loss

    def validate(self, val_loader: DataLoader) -> Tuple[float, Dict[str, float]]:
        """
        Validate model on validation set.

        Args:
            val_loader: Validation DataLoader

        Returns:
            val_loss: Validation loss
            metrics: Dictionary with regression metrics
        """
        self.model.eval()
        total_loss = 0.0
        all_preds = []
        all_targets = []

        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)

                # Forward pass
                output = self.model(batch_x).squeeze(-1)

                # Compute loss
                loss = self.criterion(output, batch_y)
                total_loss += loss.item()

                # Store predictions
                all_preds.append(output.cpu().numpy())
                all_targets.append(batch_y.cpu().numpy())

        # Compute metrics
        val_loss = total_loss / len(val_loader)
        preds = np.concatenate(all_preds)
        targets = np.concatenate(all_targets)
        metrics = compute_regression_metrics(targets, preds)

        return val_loss, metrics

    def train(self,
              train_loader: DataLoader,
              val_loader: DataLoader,
              epochs: int = 100,
              checkpoint_dir: str = 'models',
              augment: bool = True,
              checkpoint_extra: Optional[Dict] = None) -> Dict:
        """
        Full training loop with early stopping and checkpointing.

        Args:
            train_loader: Training DataLoader
            val_loader: Validation DataLoader
            epochs: Maximum number of epochs
            checkpoint_dir: Directory to save checkpoints
            augment: Whether to use data augmentation
            checkpoint_extra: Extra data to include in checkpoints (e.g. normalization params)

        Returns:
            history: Dictionary with training history
        """
        ensure_dir(checkpoint_dir)
        augmentor = DataAugmentor() if augment else None

        logger.info(f"\n" + "="*60)
        logger.info(f"Starting training for {epochs} epochs")
        logger.info(f"="*60)

        for epoch in range(1, epochs + 1):
            # Train
            train_loss = self.train_epoch(train_loader, augmentor)
            self.train_losses.append(train_loss)

            # Validate
            val_loss, metrics = self.validate(val_loader)
            self.val_losses.append(val_loss)

            # Log metrics
            logger.info(f"Epoch {epoch}/{epochs}")
            logger.info(f"  Train Loss: {train_loss:.6f}")
            logger.info(f"  Val Loss:   {val_loss:.6f}")
            logger.info(f"  Val R2:     {metrics['r2']:.4f}")
            logger.info(f"  Val MAE:    {metrics['mae']:.6f}")

            # Learning rate scheduling
            self.scheduler.step(val_loss)

            # Early stopping and checkpointing
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.best_epoch = epoch
                self.patience_counter = 0

                # Save checkpoint
                checkpoint_path = Path(checkpoint_dir) / 'best_eegnet.pth'
                self._save_checkpoint(checkpoint_path, epoch, val_loss,
                                      extra=checkpoint_extra)
                logger.info(f"  [BEST] New best model saved (Val Loss: {val_loss:.6f})")

            else:
                self.patience_counter += 1
                logger.info(f"  No improvement ({self.patience_counter}/{self.patience_early_stop})")

                if self.patience_counter >= self.patience_early_stop:
                    logger.info(f"\nEarly stopping at epoch {epoch}")
                    break

        logger.info(f"\n" + "="*60)
        logger.info(f"Training completed!")
        logger.info(f"  Best epoch: {self.best_epoch}")
        logger.info(f"  Best val loss: {self.best_val_loss:.6f}")
        logger.info("="*60)

        return {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'best_epoch': self.best_epoch,
            'best_val_loss': self.best_val_loss
        }

    def _save_checkpoint(self, path: str, epoch: int, val_loss: float,
                         extra: Optional[Dict] = None):
        """Save model checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'val_loss': val_loss,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses
        }
        if extra:
            checkpoint.update(extra)
        torch.save(checkpoint, path)

    def load_checkpoint(self, path: str):
        """Load model checkpoint."""
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.train_losses = checkpoint['train_losses']
        self.val_losses = checkpoint['val_losses']
        logger.info(f"Loaded checkpoint from {path}")


def main():
    """Main entry point for training pipeline."""
    parser = argparse.ArgumentParser(
        description="Train EEGNet model for PAC prediction"
    )
    parser.add_argument('--data_dir', type=str, required=True,
                       help='Directory with preprocessed data (train/val npz files)')
    parser.add_argument('--output_dir', type=str, default='models',
                       help='Directory for model checkpoints')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=64,
                       help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--weight_decay', type=float, default=1e-4,
                       help='L2 regularization')
    parser.add_argument('--device', type=str, default='cuda',
                       help='Device: cuda or cpu')
    parser.add_argument('--no-augment', dest='augment', action='store_false',
                       help='Disable data augmentation')
    parser.set_defaults(augment=True)
    parser.add_argument('--num_workers', type=int, default=0,
                       help='Number of DataLoader workers (0 for Windows compatibility)')

    args = parser.parse_args()

    # Ensure output directory exists and setup logging
    ensure_dir(args.output_dir)
    setup_logging(log_file=f"{args.output_dir}/training.log")

    # Device
    if torch.cuda.is_available():
        device = args.device
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        device = 'mps'
    else:
        device = 'cpu'
    logger.info(f"Using device: {device}")
    pin_memory = (device != 'cpu')

    # Load data
    logger.info(f"\nLoading data from {args.data_dir}...")
    train_data = np.load(Path(args.data_dir) / 'train_data.npz')
    val_data = np.load(Path(args.data_dir) / 'val_data.npz')

    # Z-score normalize PAC targets using training set statistics.
    # Raw PAC values (~0.001 range) produce vanishingly small MSE gradients;
    # normalizing them lets the model learn meaningful signal structure.
    pac_train_raw = train_data['pac']
    pac_mean = float(pac_train_raw.mean())
    pac_std = float(pac_train_raw.std())
    logger.info(f"PAC normalization: mean={pac_mean:.6f}, std={pac_std:.6f}")

    pac_train_norm = (pac_train_raw - pac_mean) / pac_std
    pac_val_norm = (val_data['pac'] - pac_mean) / pac_std

    # Create datasets
    from data_loader import EEGWindowDataset

    train_dataset = EEGWindowDataset(
        windows=train_data['windows'],
        pac_labels=pac_train_norm
    )
    val_dataset = EEGWindowDataset(
        windows=val_data['windows'],
        pac_labels=pac_val_norm
    )

    logger.info(f"Training set: {len(train_dataset)} samples")
    logger.info(f"Validation set: {len(val_dataset)} samples")

    # Create DataLoaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=pin_memory
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=pin_memory
    )

    # Create model
    logger.info("\nCreating EEGNet model...")
    model = EEGNet(n_channels=7, n_samples=500).to(device)
    n_params = count_parameters(model)
    logger.info(f"EEGNet parameters: {n_params:,}")

    # Create trainer
    trainer = ModelTrainer(
        model=model,
        device=device,
        learning_rate=args.lr,
        weight_decay=args.weight_decay,
        patience_early_stop=15
    )

    # Train (store normalization params in checkpoint for inference denormalization)
    history = trainer.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=args.epochs,
        checkpoint_dir=args.output_dir,
        augment=args.augment,
        checkpoint_extra={'pac_mean': pac_mean, 'pac_std': pac_std}
    )

    logger.info("\nTraining complete! Best model saved to checkpoint.")


if __name__ == "__main__":
    main()
