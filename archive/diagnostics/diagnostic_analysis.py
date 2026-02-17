"""
Diagnostic Analysis for V4 ViT-TCNet Failure

This script investigates why the model plateaued at R² = 0.252
and identifies what's actually predictive in the data.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LassoCV, RidgeCV
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, 'src')

from spectral_features import SpectralFeatureExtractor
from wavelet_features import WaveletFeatureExtractor

print("="*70)
print("DIAGNOSTIC ANALYSIS: Why did V4 fail?")
print("="*70)

# Load data
print("\n1. Loading data...")
train_data = np.load('data/processed/train_data.npz')
val_data = np.load('data/processed/val_data.npz')
test_data = np.load('data/processed/test_data.npz')

X_train = train_data['windows'].squeeze(1)  # (11736, 7, 500)
y_train = train_data['pac']
X_val = val_data['windows'].squeeze(1)
y_val = val_data['pac']
X_test = test_data['windows'].squeeze(1)
y_test = test_data['pac']

print(f"✓ Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
print(f"  PAC range: [{y_train.min():.6f}, {y_train.max():.6f}]")
print(f"  PAC mean±std: {y_train.mean():.6f}±{y_train.std():.6f}")

# Extract features
print("\n2. Extracting features...")
spectral_extractor = SpectralFeatureExtractor(fs=250)
wavelet_extractor = WaveletFeatureExtractor(fs=250)

def extract_all_features(X):
    n_samples = len(X)
    spectral_feats = np.zeros((n_samples, 61))
    wavelet_feats = np.zeros((n_samples, 74))

    for i in range(n_samples):
        spectral_feats[i] = spectral_extractor.extract_features(X[i])
        wavelet_feats[i] = wavelet_extractor.extract_features(X[i])

    return np.hstack([spectral_feats, wavelet_feats])

X_train_feats = extract_all_features(X_train[:1000])  # Subsample for speed
y_train_sub = y_train[:1000]
X_val_feats = extract_all_features(X_val)
X_test_feats = extract_all_features(X_test)

print(f"✓ Features extracted: {X_train_feats.shape[1]} features")

# Normalize
scaler = StandardScaler()
X_train_feats = scaler.fit_transform(X_train_feats)
X_val_feats = scaler.transform(X_val_feats)
X_test_feats = scaler.transform(X_test_feats)

# 3. Test simple models
print("\n3. Testing simple models (baseline comparison)...")
print("-" * 70)

# Linear models with regularization
print("\n3a. Ridge Regression (L2 regularization)...")
ridge = RidgeCV(alphas=np.logspace(-3, 3, 20))
ridge.fit(X_train_feats, y_train_sub)
ridge_val_r2 = ridge.score(X_val_feats, y_val)
ridge_test_r2 = ridge.score(X_test_feats, y_test)
print(f"  Val R²: {ridge_val_r2:.4f}, Test R²: {ridge_test_r2:.4f}")

print("\n3b. Lasso Regression (L1 regularization, feature selection)...")
lasso = LassoCV(alphas=np.logspace(-6, -1, 20), cv=3, max_iter=5000)
lasso.fit(X_train_feats, y_train_sub)
lasso_val_r2 = lasso.score(X_val_feats, y_val)
lasso_test_r2 = lasso.score(X_test_feats, y_test)
n_selected = np.sum(np.abs(lasso.coef_) > 1e-6)
print(f"  Val R²: {lasso_val_r2:.4f}, Test R²: {lasso_test_r2:.4f}")
print(f"  Features selected: {n_selected}/135")

print("\n3c. Random Forest (non-linear baseline)...")
rf = RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_leaf=10,
                           n_jobs=-1, random_state=42)
rf.fit(X_train_feats, y_train_sub)
rf_val_r2 = rf.score(X_val_feats, y_val)
rf_test_r2 = rf.score(X_test_feats, y_test)
print(f"  Val R²: {rf_val_r2:.4f}, Test R²: {rf_test_r2:.4f}")

# 4. Feature importance analysis
print("\n4. Feature Importance Analysis...")
print("-" * 70)

# Get feature names
feature_names = []
# Spectral features (61)
bands = ['delta', 'theta', 'alpha', 'beta', 'gamma']
for ch in range(7):
    for band in bands:
        feature_names.append(f'ch{ch}_{band}_power')
for ch in range(7):
    for band in bands:
        feature_names.append(f'ch{ch}_{band}_rel_power')
for band in bands:
    feature_names.append(f'avg_{band}_power')
feature_names.append('spectral_entropy')

# Wavelet features (74)
wavelet_groups = {
    'CWT': 35,
    'WPD': 21,
    'Sync': 14,
    'CrossChannel': 4
}
for group, count in wavelet_groups.items():
    for i in range(count):
        feature_names.append(f'{group}_{i}')

# Random Forest feature importance
importances = rf.feature_importances_
indices = np.argsort(importances)[::-1]

print("\nTop 20 most important features (Random Forest):")
for i in range(20):
    idx = indices[i]
    print(f"  {i+1:2d}. {feature_names[idx]:30s}: {importances[idx]:.4f}")

# Correlation with target
print("\nTop 20 features by absolute correlation with PAC:")
correlations = np.array([stats.pearsonr(X_train_feats[:, i], y_train_sub)[0]
                        for i in range(X_train_feats.shape[1])])
corr_indices = np.argsort(np.abs(correlations))[::-1]

for i in range(20):
    idx = corr_indices[i]
    print(f"  {i+1:2d}. {feature_names[idx]:30s}: {correlations[idx]:+.4f}")

# 5. Analyze prediction distributions
print("\n5. Prediction Distribution Analysis...")
print("-" * 70)

ridge_pred = ridge.predict(X_test_feats)
rf_pred = rf.predict(X_test_feats)

print(f"\nTarget (PAC) statistics:")
print(f"  Mean: {y_test.mean():.6f}, Std: {y_test.std():.6f}")
print(f"  Range: [{y_test.min():.6f}, {y_test.max():.6f}]")

print(f"\nRidge predictions:")
print(f"  Mean: {ridge_pred.mean():.6f}, Std: {ridge_pred.std():.6f}")
print(f"  Range: [{ridge_pred.min():.6f}, {ridge_pred.max():.6f}]")
print(f"  Correlation with target: {np.corrcoef(ridge_pred, y_test)[0,1]:.4f}")

print(f"\nRandom Forest predictions:")
print(f"  Mean: {rf_pred.mean():.6f}, Std: {rf_pred.std():.6f}")
print(f"  Range: [{rf_pred.min():.6f}, {rf_pred.max():.6f}]")
print(f"  Correlation with target: {np.corrcoef(rf_pred, y_test)[0,1]:.4f}")

# 6. Check for data quality issues
print("\n6. Data Quality Checks...")
print("-" * 70)

# Check for NaN/Inf
print(f"\nNaN/Inf in features: {np.any(~np.isfinite(X_train_feats))}")
print(f"NaN/Inf in targets: {np.any(~np.isfinite(y_train_sub))}")

# Check feature variance
zero_var = np.var(X_train_feats, axis=0) < 1e-10
print(f"\nZero-variance features: {np.sum(zero_var)}")
if np.sum(zero_var) > 0:
    print("  Zero-variance features:")
    for idx in np.where(zero_var)[0][:10]:
        print(f"    {feature_names[idx]}")

# Check feature correlations
print(f"\nFeature correlation matrix...")
corr_matrix = np.corrcoef(X_train_feats.T)
high_corr = np.sum(np.abs(corr_matrix) > 0.95) - X_train_feats.shape[1]  # exclude diagonal
print(f"  Highly correlated pairs (>0.95): {high_corr // 2}")

# 7. Summary and recommendations
print("\n" + "="*70)
print("SUMMARY AND RECOMMENDATIONS")
print("="*70)

print("\n📊 Model Performance Comparison:")
print(f"  Ridge Regression:     Test R² = {ridge_test_r2:.4f}")
print(f"  Random Forest:        Test R² = {rf_test_r2:.4f}")
print(f"  V4 ViT-TCNet:         Test R² = 0.2521")
print(f"  V3 Clean (baseline):  Test R² = 0.2360")

if ridge_test_r2 > 0.25:
    print("\n✓ GOOD NEWS: Simple Ridge beats ViT-TCNet!")
    print("  → The features ARE predictive, but complex models overfit")
    print("  → Recommendation: Use simpler models with better regularization")
else:
    print("\n❌ BAD NEWS: Even simple models struggle")
    print("  → The features may not capture PAC dynamics well enough")
    print("  → Recommendation: Focus on feature engineering, not model complexity")

print("\n🔍 Key Findings:")
if rf_test_r2 > ridge_test_r2 + 0.02:
    print("  1. Non-linearity helps → Consider shallow neural nets")
else:
    print("  1. Linear relationships dominate → Ridge/Lasso sufficient")

if n_selected < 50:
    print(f"  2. Only {n_selected}/135 features selected by Lasso → Feature redundancy")
else:
    print(f"  2. Most features ({n_selected}/135) are useful → Need all information")

print("\n💡 Next Steps:")
print("  1. Try ensemble of simple models (Ridge + RF)")
print("  2. Add more domain-specific features (e.g., direct phase coupling)")
print("  3. Use cross-validation for hyperparameter tuning")
print("  4. Consider temporal models (LSTM, but shallow)")
print("  5. Investigate if problem is fundamentally limited by EEG noise")

print("\n" + "="*70)
