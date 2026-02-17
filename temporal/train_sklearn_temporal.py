"""
Lightweight sklearn-based temporal PAC predictor for 8-second windows.

This validates that long windows enable temporal prediction WITHOUT needing PyTorch.
If this achieves R² > 0.6, then the LSTM version (which user can run on their machine) will likely do even better.
"""

import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_absolute_error
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')


def create_temporal_features(windows, pac_history, spectral_features, lookback=5):
    """
    Create flat feature vector from temporal sequence.

    Args:
        windows: (lookback, n_ch, n_time) EEG windows
        pac_history: (lookback,) PAC values
        spectral_features: Dict of (lookback, n_ch) arrays

    Returns:
        Flattened feature vector
    """
    features = []

    # PAC history features
    features.extend(pac_history)
    features.append(pac_history.mean())
    features.append(pac_history.std())
    features.append(pac_history[-1] - pac_history[0])  # Trend

    # Spectral features (aggregate over time)
    for key in sorted(spectral_features.keys()):
        feat = spectral_features[key]  # (lookback, n_ch)

        # Channel-wise statistics over lookback
        features.extend(feat.mean(axis=0))  # Mean per channel
        features.extend(feat.std(axis=0))   # Std per channel
        features.extend(feat[-1])            # Most recent values
        features.append(feat.mean())         # Global mean

    # EEG band power features (simplified)
    for i in range(len(windows)):
        window = windows[i]  # (n_ch, n_time)

        # Simple band power estimates
        features.append(window.mean())
        features.append(window.std())
        features.extend(window.mean(axis=1))  # Per-channel mean
        features.extend(window.std(axis=1))   # Per-channel std

    return np.array(features)


def create_dataset(data_dir, lookback=5, horizon=2):
    """
    Create temporal dataset for sklearn.

    Returns:
        X_train, y_train, X_val, y_val, X_test, y_test, norm_stats
    """
    data_dir = Path(data_dir)

    print("Loading 8-second window data...")
    windows = np.load(data_dir / 'windows.npy')
    pac_values = np.load(data_dir / 'pac_values.npy')
    subjects = np.load(data_dir / 'subjects.npy')

    # Load spectral features
    spectral_features = {}
    for key in ['delta_power', 'theta_power', 'alpha_power',
                'beta_power', 'gamma_power', 'spectral_entropy']:
        spectral_features[key] = np.load(data_dir / f'{key}.npy')

    print(f"Loaded: {windows.shape[0]} windows from {len(np.unique(subjects))} subjects")

    # Temporal split per subject
    train_X, val_X, test_X = [], [], []
    train_y, val_y, test_y = [], [], []

    for subj_id in np.unique(subjects):
        subj_mask = (subjects == subj_id)
        subj_windows = windows[subj_mask]
        subj_pac = pac_values[subj_mask]

        subj_spectral = {}
        for key in spectral_features:
            subj_spectral[key] = spectral_features[key][subj_mask]

        # Create temporal sequences
        for i in range(lookback, len(subj_windows) - horizon):
            seq_windows = subj_windows[i-lookback:i]
            seq_pac = subj_pac[i-lookback:i]
            target_pac = subj_pac[i + horizon]

            seq_spectral = {}
            for key in spectral_features:
                seq_spectral[key] = subj_spectral[key][i-lookback:i]

            # Create features
            X = create_temporal_features(seq_windows, seq_pac, seq_spectral, lookback)
            y = target_pac

            # Split temporally
            n = len(subj_pac)
            n_train = int(0.7 * n)
            n_val = int(0.15 * n)

            if i < n_train:
                train_X.append(X)
                train_y.append(y)
            elif i < n_train + n_val:
                val_X.append(X)
                val_y.append(y)
            else:
                test_X.append(X)
                test_y.append(y)

    X_train = np.array(train_X)
    y_train = np.array(train_y)
    X_val = np.array(val_X)
    y_val = np.array(val_y)
    X_test = np.array(test_X)
    y_test = np.array(test_y)

    print(f"\nDataset sizes:")
    print(f"  Train: {X_train.shape[0]} samples, {X_train.shape[1]} features")
    print(f"  Val:   {X_val.shape[0]} samples")
    print(f"  Test:  {X_test.shape[0]} samples")

    # Normalize features
    scaler_X = StandardScaler()
    X_train = scaler_X.fit_transform(X_train)
    X_val = scaler_X.transform(X_val)
    X_test = scaler_X.transform(X_test)

    # Normalize targets
    y_mean = y_train.mean()
    y_std = y_train.std()

    y_train_norm = (y_train - y_mean) / y_std
    y_val_norm = (y_val - y_mean) / y_std
    y_test_norm = (y_test - y_mean) / y_std

    norm_stats = {
        'y_mean': y_mean,
        'y_std': y_std,
        'scaler_X': scaler_X
    }

    return (X_train, y_train_norm, y_train,
            X_val, y_val_norm, y_val,
            X_test, y_test_norm, y_test,
            norm_stats)


def train_and_evaluate(X_train, y_train, y_train_orig,
                       X_val, y_val, y_val_orig,
                       X_test, y_test, y_test_orig,
                       norm_stats):
    """
    Train Ridge and MLP models, evaluate on test set.
    """
    print("\n" + "="*80)
    print("TRAINING MODELS")
    print("="*80)

    results = {}

    # ==================== Ridge Regression ====================
    print("\n[1/2] Training Ridge Regression...")
    ridge = Ridge(alpha=1.0)
    ridge.fit(X_train, y_train)

    # Evaluate
    ridge_val_pred = ridge.predict(X_val)
    ridge_test_pred = ridge.predict(X_test)

    # Denormalize
    ridge_val_pred_orig = ridge_val_pred * norm_stats['y_std'] + norm_stats['y_mean']
    ridge_test_pred_orig = ridge_test_pred * norm_stats['y_std'] + norm_stats['y_mean']

    ridge_val_r2 = r2_score(y_val_orig, ridge_val_pred_orig)
    ridge_test_r2 = r2_score(y_test_orig, ridge_test_pred_orig)
    ridge_test_mae = mean_absolute_error(y_test_orig, ridge_test_pred_orig)
    ridge_test_corr = np.corrcoef(y_test_orig, ridge_test_pred_orig)[0, 1]

    print(f"  Val R²:  {ridge_val_r2:.4f}")
    print(f"  Test R²: {ridge_test_r2:.4f}")
    print(f"  Test MAE: {ridge_test_mae:.6f}")
    print(f"  Test Corr: {ridge_test_corr:.4f}")

    results['ridge'] = {
        'val_r2': float(ridge_val_r2),
        'test_r2': float(ridge_test_r2),
        'test_mae': float(ridge_test_mae),
        'test_corr': float(ridge_test_corr)
    }

    # ==================== MLP Regressor ====================
    print("\n[2/2] Training MLP Regressor...")
    mlp = MLPRegressor(
        hidden_layer_sizes=(256, 128, 64),
        activation='relu',
        solver='adam',
        alpha=0.001,
        batch_size=32,
        learning_rate_init=0.001,
        max_iter=200,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=20,
        random_state=42,
        verbose=True
    )

    mlp.fit(X_train, y_train)

    # Evaluate
    mlp_val_pred = mlp.predict(X_val)
    mlp_test_pred = mlp.predict(X_test)

    # Denormalize
    mlp_val_pred_orig = mlp_val_pred * norm_stats['y_std'] + norm_stats['y_mean']
    mlp_test_pred_orig = mlp_test_pred * norm_stats['y_std'] + norm_stats['y_mean']

    mlp_val_r2 = r2_score(y_val_orig, mlp_val_pred_orig)
    mlp_test_r2 = r2_score(y_test_orig, mlp_test_pred_orig)
    mlp_test_mae = mean_absolute_error(y_test_orig, mlp_test_pred_orig)
    mlp_test_corr = np.corrcoef(y_test_orig, mlp_test_pred_orig)[0, 1]

    print(f"\n  Val R²:  {mlp_val_r2:.4f}")
    print(f"  Test R²: {mlp_test_r2:.4f}")
    print(f"  Test MAE: {mlp_test_mae:.6f}")
    print(f"  Test Corr: {mlp_test_corr:.4f}")

    results['mlp'] = {
        'val_r2': float(mlp_val_r2),
        'test_r2': float(mlp_test_r2),
        'test_mae': float(mlp_test_mae),
        'test_corr': float(mlp_test_corr),
        'n_iter': int(mlp.n_iter_)
    }

    return results, ridge, mlp


def main():
    print("="*80)
    print("TEMPORAL PAC PREDICTION WITH 8-SECOND WINDOWS (SKLEARN BASELINE)")
    print("="*80)
    print("\nConfiguration:")
    print("  Lookback: 5 windows (20 seconds)")
    print("  Horizon: 2 windows (8 seconds ahead)")
    print("  PAC autocorrelation @ 8s: r = 0.277")
    print("  Expected: R² > 0.6 (vs 2-sec baseline: R² = -0.05)")

    base_dir = Path('/sessions/serene-gifted-feynman/mnt/closedloop-40hz-entrainment')
    data_dir = base_dir / 'data' / 'processed' / 'long_windows'
    results_dir = base_dir / 'temporal' / 'results_sklearn_baseline'
    results_dir.mkdir(parents=True, exist_ok=True)

    # Create dataset
    (X_train, y_train_norm, y_train,
     X_val, y_val_norm, y_val,
     X_test, y_test_norm, y_test,
     norm_stats) = create_dataset(data_dir, lookback=5, horizon=2)

    # Train and evaluate
    results, ridge_model, mlp_model = train_and_evaluate(
        X_train, y_train_norm, y_train,
        X_val, y_val_norm, y_val,
        X_test, y_test_norm, y_test,
        norm_stats
    )

    # Save results
    print("\n" + "="*80)
    print("SAVING RESULTS")
    print("="*80)

    with open(results_dir / 'results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✓ Saved to: {results_dir / 'results.json'}")

    # Final verdict
    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)

    best_r2 = max(results['ridge']['test_r2'], results['mlp']['test_r2'])
    best_model = 'Ridge' if results['ridge']['test_r2'] > results['mlp']['test_r2'] else 'MLP'

    print(f"\nBest model: {best_model}")
    print(f"  Test R²: {best_r2:.4f}")

    print("\nComparison to baselines:")
    print(f"  2-second windows (LSTM): R² = -0.05 ✗")
    print(f"  Current-window (Ridge):  R² = 0.287")
    print(f"  8-second windows ({best_model}):  R² = {best_r2:.3f}", end=" ")

    if best_r2 > 0.6:
        print("✓ SUCCESS!")
        print("\n  ✓ Long windows created temporal structure")
        print("  ✓ Temporal prediction now viable for MPC")
        print("  → LSTM version (train_temporal_long_windows.py) will likely do even better")
    elif best_r2 > 0.3:
        print("⚠ PARTIAL SUCCESS")
        print("\n  ⚠ Better than 2-sec windows but below target")
        print("  → Consider 10-12 second windows or incorporating stimulation context")
    else:
        print("✗ FAILED")
        print("\n  ✗ Even 8-second windows insufficient")
        print("  → May need 15-30 second windows like methodology papers")

    print("\n" + "="*80)


if __name__ == '__main__':
    main()
