"""
Training Pipeline for Temporal PAC Prediction

Trains the LSTM temporal predictor with:
    - Huber loss (robust to PAC outliers)
    - Cosine annealing LR schedule with warm restarts
    - Gradient clipping (0.5)
    - Early stopping on validation R²
    - Multi-horizon evaluation
    - Comprehensive logging and checkpointing

Subject-based splits prevent data leakage.
PAC is z-score normalized; predictions are denormalized for evaluation.

Author: Amaar Chughtai
Date: February 2026
"""

import os
import sys
import time
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, Tuple, Optional

# Add parent and current directory to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from temporal_dataset import prepare_temporal_data
from temporal_model import TemporalPACPredictor


def compute_metrics(predictions: np.ndarray, targets: np.ndarray) -> Dict[str, float]:
    """
    Compute regression metrics in original (denormalized) PAC scale.

    Returns:
        dict with keys: r2, correlation, mae, rmse, mape
    """
    # R² (coefficient of determination)
    ss_res = np.sum((targets - predictions) ** 2)
    ss_tot = np.sum((targets - targets.mean()) ** 2)
    r2 = 1 - ss_res / (ss_tot + 1e-10)

    # Pearson correlation
    if np.std(predictions) > 1e-10 and np.std(targets) > 1e-10:
        correlation = np.corrcoef(predictions, targets)[0, 1]
    else:
        correlation = 0.0

    # MAE, RMSE
    mae = np.mean(np.abs(predictions - targets))
    rmse = np.sqrt(np.mean((predictions - targets) ** 2))

    # MAPE (avoid division by zero)
    nonzero = np.abs(targets) > 1e-10
    if nonzero.sum() > 0:
        mape = np.mean(np.abs((predictions[nonzero] - targets[nonzero]) / targets[nonzero])) * 100
    else:
        mape = float('inf')

    return {
        'r2': float(r2),
        'correlation': float(correlation),
        'mae': float(mae),
        'rmse': float(rmse),
        'mape': float(mape),
    }


def train_one_epoch(model, loader, optimizer, criterion, device, grad_clip=0.5):
    """Train for one epoch. Returns average loss."""
    model.train()
    total_loss = 0.0
    n_batches = 0

    for batch in loader:
        # Move to device
        batch_gpu = {k: v.to(device) for k, v in batch.items()}
        targets = batch_gpu.pop('target')

        # Forward pass
        predictions = model(batch_gpu).squeeze(1)  # (B,)
        loss = criterion(predictions, targets)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()

        # Gradient clipping
        if grad_clip > 0:
            nn.utils.clip_grad_norm_(model.parameters(), grad_clip)

        optimizer.step()

        total_loss += loss.item()
        n_batches += 1

    return total_loss / n_batches


@torch.no_grad()
def evaluate(model, loader, criterion, device, pac_mean, pac_std):
    """
    Evaluate model on a data split.

    Returns metrics in ORIGINAL PAC scale (denormalized).
    """
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_targets = []

    for batch in loader:
        batch_gpu = {k: v.to(device) for k, v in batch.items()}
        targets = batch_gpu.pop('target')

        predictions = model(batch_gpu).squeeze(1)
        loss = criterion(predictions, targets)
        total_loss += loss.item()

        all_preds.append(predictions.cpu().numpy())
        all_targets.append(targets.cpu().numpy())

    all_preds = np.concatenate(all_preds)
    all_targets = np.concatenate(all_targets)

    # Denormalize to original PAC scale
    preds_original = all_preds * pac_std + pac_mean
    targets_original = all_targets * pac_std + pac_mean

    avg_loss = total_loss / len(loader) if len(loader) > 0 else float('inf')
    metrics = compute_metrics(preds_original, targets_original)
    metrics['loss'] = avg_loss

    return metrics, preds_original, targets_original


def train_temporal_predictor(
    # Data
    data_dir: str = 'data/processed',
    lookback: int = 10,
    horizon: int = 5,
    batch_size: int = 64,

    # Model
    spatial_dim: int = 32,
    lstm_hidden: int = 64,
    lstm_layers: int = 2,
    dropout: float = 0.3,
    bidirectional: bool = True,
    use_spectral: bool = True,
    use_gru: bool = False,

    # Training
    n_epochs: int = 150,
    learning_rate: float = 1e-3,
    weight_decay: float = 1e-3,
    grad_clip: float = 0.5,
    patience: int = 30,

    # Output
    save_dir: str = 'models',
    model_name: str = 'temporal_lstm',
):
    """
    Full training pipeline for temporal PAC prediction.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    print("=" * 70)
    print("TEMPORAL PAC PREDICTION - TRAINING PIPELINE")
    print("=" * 70)
    print(f"\nDevice: {device}")
    if device.type == 'cuda':
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    # ── Data ──────────────────────────────────────────────────────────
    train_loader, val_loader, test_loader, metadata = prepare_temporal_data(
        data_dir=data_dir,
        lookback=lookback,
        horizon=horizon,
        batch_size=batch_size,
        extract_spectral=use_spectral,
    )

    pac_mean = metadata['pac_mean']
    pac_std = metadata['pac_std']

    # ── Model ─────────────────────────────────────────────────────────
    model = TemporalPACPredictor(
        n_channels=7,
        n_samples=500,
        n_spectral_features=metadata.get('n_spectral_features', 61),
        spatial_dim=spatial_dim,
        lstm_hidden=lstm_hidden,
        lstm_layers=lstm_layers,
        dropout=dropout,
        bidirectional=bidirectional,
        use_spectral=use_spectral,
        use_gru=use_gru,
    ).to(device)

    n_params = model.count_parameters()
    param_breakdown = model.count_parameters_by_component()

    print(f"\nModel: TemporalPACPredictor ({'GRU' if use_gru else 'LSTM'})")
    print(f"  Total parameters: {n_params:,}")
    for name, count in param_breakdown.items():
        if name != 'total':
            print(f"  {name}: {count:,}")

    # ── Loss, Optimizer, Scheduler ────────────────────────────────────
    criterion = nn.HuberLoss(delta=1.0)  # delta=1.0 on normalized scale ≈ 1 std

    optimizer = optim.AdamW(
        model.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay,
    )

    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=20, T_mult=2, eta_min=1e-6
    )

    # ── Training Loop ─────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("TRAINING")
    print(f"{'='*70}")
    print(f"  Epochs:      {n_epochs}")
    print(f"  LR:          {learning_rate}")
    print(f"  Weight decay: {weight_decay}")
    print(f"  Grad clip:   {grad_clip}")
    print(f"  Patience:    {patience}")
    print(f"  Horizon:     {horizon} seconds ahead")
    print()

    os.makedirs(save_dir, exist_ok=True)

    best_val_r2 = -float('inf')
    best_epoch = 0
    epochs_without_improvement = 0
    history = {
        'train_loss': [], 'val_loss': [],
        'val_r2': [], 'val_corr': [], 'val_mae': [],
        'lr': [],
    }

    start_time = time.time()

    for epoch in range(1, n_epochs + 1):
        epoch_start = time.time()

        # Train
        train_loss = train_one_epoch(
            model, train_loader, optimizer, criterion, device, grad_clip
        )

        # Validate
        val_metrics, _, _ = evaluate(
            model, val_loader, criterion, device, pac_mean, pac_std
        )

        # Step scheduler
        scheduler.step()
        current_lr = optimizer.param_groups[0]['lr']

        # Record history
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_metrics['loss'])
        history['val_r2'].append(val_metrics['r2'])
        history['val_corr'].append(val_metrics['correlation'])
        history['val_mae'].append(val_metrics['mae'])
        history['lr'].append(current_lr)

        epoch_time = time.time() - epoch_start

        # Check for improvement
        improved = val_metrics['r2'] > best_val_r2
        if improved:
            best_val_r2 = val_metrics['r2']
            best_epoch = epoch
            epochs_without_improvement = 0

            # Save best model
            save_path = os.path.join(save_dir, f'best_{model_name}.pth')
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_r2': best_val_r2,
                'metadata': metadata,
                'config': {
                    'lookback': lookback, 'horizon': horizon,
                    'spatial_dim': spatial_dim, 'lstm_hidden': lstm_hidden,
                    'lstm_layers': lstm_layers, 'dropout': dropout,
                    'bidirectional': bidirectional, 'use_spectral': use_spectral,
                    'use_gru': use_gru,
                },
            }, save_path)
        else:
            epochs_without_improvement += 1

        # Print progress
        marker = " ★ BEST" if improved else ""
        if epoch <= 5 or epoch % 5 == 0 or improved or epoch == n_epochs:
            print(f"Epoch {epoch:3d}/{n_epochs} | "
                  f"Train Loss: {train_loss:.4f} | "
                  f"Val Loss: {val_metrics['loss']:.4f} | "
                  f"Val R²: {val_metrics['r2']:.4f} | "
                  f"Val Corr: {val_metrics['correlation']:.4f} | "
                  f"LR: {current_lr:.2e} | "
                  f"{epoch_time:.1f}s{marker}")

        # Early stopping
        if epochs_without_improvement >= patience:
            print(f"\n  Early stopping at epoch {epoch} "
                  f"(no improvement for {patience} epochs)")
            break

    total_time = time.time() - start_time
    print(f"\nTraining complete in {total_time/60:.1f} minutes")
    print(f"Best Val R²: {best_val_r2:.4f} at epoch {best_epoch}")

    # ── Final Evaluation on Test Set ──────────────────────────────────
    print(f"\n{'='*70}")
    print("FINAL EVALUATION (Test Set)")
    print(f"{'='*70}")

    # Load best model
    checkpoint = torch.load(
        os.path.join(save_dir, f'best_{model_name}.pth'),
        map_location=device, weights_only=False
    )
    model.load_state_dict(checkpoint['model_state_dict'])

    test_metrics, test_preds, test_targets = evaluate(
        model, test_loader, criterion, device, pac_mean, pac_std
    )

    print(f"\n  Test R²:          {test_metrics['r2']:.4f}")
    print(f"  Test Correlation: {test_metrics['correlation']:.4f}")
    print(f"  Test MAE:         {test_metrics['mae']:.6f}")
    print(f"  Test RMSE:        {test_metrics['rmse']:.6f}")
    print(f"  Test MAPE:        {test_metrics['mape']:.1f}%")

    # ── Save Results ──────────────────────────────────────────────────
    # Training history
    np.savez(
        os.path.join(save_dir, f'training_history_{model_name}.npz'),
        **{k: np.array(v) for k, v in history.items()},
        best_val_r2=best_val_r2,
        best_epoch=best_epoch,
    )

    # Test predictions
    np.savez(
        os.path.join(save_dir, f'test_predictions_{model_name}.npz'),
        predictions=test_preds,
        targets=test_targets,
    )

    # Summary JSON
    summary = {
        'model': model_name,
        'task': f'Predict PAC {horizon} seconds ahead',
        'lookback': lookback,
        'horizon': horizon,
        'n_params': n_params,
        'param_breakdown': param_breakdown,
        'best_epoch': best_epoch,
        'best_val_r2': best_val_r2,
        'test_metrics': test_metrics,
        'training_time_minutes': total_time / 60,
        'n_train': metadata['n_train'],
        'n_val': metadata['n_val'],
        'n_test': metadata['n_test'],
        'pac_mean': pac_mean,
        'pac_std': pac_std,
    }

    with open(os.path.join(save_dir, f'summary_{model_name}.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n  Results saved to {save_dir}/")
    print(f"    best_{model_name}.pth")
    print(f"    training_history_{model_name}.npz")
    print(f"    test_predictions_{model_name}.npz")
    print(f"    summary_{model_name}.json")

    # ── Comparison with Previous Approaches ───────────────────────────
    print(f"\n{'='*70}")
    print("COMPARISON WITH PREVIOUS APPROACHES")
    print(f"{'='*70}")
    print(f"  V3-Clean (current-window, Ridge):  R² = 0.287")
    print(f"  V4 (ViT-TCNet, current-window):    R² = 0.252")
    print(f"  V8 (EEGNet, current-window):       R² = 0.222")
    print(f"  Temporal LSTM ({horizon}s ahead):       R² = {test_metrics['r2']:.4f}")

    improvement = (test_metrics['r2'] - 0.287) / 0.287 * 100
    print(f"  Improvement over best baseline:     {improvement:+.1f}%")

    return model, test_metrics, history


def run_multi_horizon_experiment():
    """
    Train models for multiple prediction horizons (1, 3, 5, 10 seconds)
    to characterize the predictability decay curve.
    """
    print("\n" + "=" * 70)
    print("MULTI-HORIZON EXPERIMENT")
    print("=" * 70)

    horizons = [1, 3, 5, 10]
    results = {}

    for h in horizons:
        print(f"\n{'─'*70}")
        print(f"HORIZON = {h} seconds ahead")
        print(f"{'─'*70}")

        _, metrics, _ = train_temporal_predictor(
            horizon=h,
            model_name=f'temporal_lstm_h{h}',
            n_epochs=100,
            patience=25,
        )
        results[h] = metrics

    print(f"\n{'='*70}")
    print("MULTI-HORIZON SUMMARY")
    print(f"{'='*70}")
    print(f"{'Horizon':>10} | {'R²':>8} | {'Correlation':>12} | {'MAE':>10} | {'RMSE':>10}")
    print("-" * 60)
    for h in horizons:
        m = results[h]
        print(f"{h:>8}s  | {m['r2']:>8.4f} | {m['correlation']:>12.4f} | "
              f"{m['mae']:>10.6f} | {m['rmse']:>10.6f}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Train Temporal PAC Predictor')
    parser.add_argument('--data-dir', default='data/processed',
                       help='Path to processed data directory')
    parser.add_argument('--lookback', type=int, default=10,
                       help='Lookback window (seconds)')
    parser.add_argument('--horizon', type=int, default=5,
                       help='Prediction horizon (seconds)')
    parser.add_argument('--batch-size', type=int, default=64,
                       help='Training batch size')
    parser.add_argument('--epochs', type=int, default=150,
                       help='Max training epochs')
    parser.add_argument('--lr', type=float, default=1e-3,
                       help='Learning rate')
    parser.add_argument('--patience', type=int, default=30,
                       help='Early stopping patience')
    parser.add_argument('--use-gru', action='store_true',
                       help='Use GRU instead of LSTM')
    parser.add_argument('--no-spectral', action='store_true',
                       help='Disable spectral features')
    parser.add_argument('--multi-horizon', action='store_true',
                       help='Run multi-horizon experiment')
    parser.add_argument('--save-dir', default='models',
                       help='Directory to save models')

    args = parser.parse_args()

    if args.multi_horizon:
        run_multi_horizon_experiment()
    else:
        train_temporal_predictor(
            data_dir=args.data_dir,
            lookback=args.lookback,
            horizon=args.horizon,
            batch_size=args.batch_size,
            n_epochs=args.epochs,
            learning_rate=args.lr,
            patience=args.patience,
            use_gru=args.use_gru,
            use_spectral=not args.no_spectral,
            save_dir=args.save_dir,
        )
