"""
Simple Diagnostic Analysis - No external ML libraries required

Investigates why V4 ViT-TCNet failed to improve beyond R² = 0.252
"""

import numpy as np
import torch
import sys
sys.path.insert(0, 'src')

from spectral_features import SpectralFeatureExtractor
from wavelet_features import WaveletFeatureExtractor

print("="*70)
print("DIAGNOSTIC ANALYSIS: V4 Failure Investigation")
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
print(f"\nPAC Target Statistics:")
print(f"  Train - Mean: {y_train.mean():.6f}, Std: {y_train.std():.6f}")
print(f"         Range: [{y_train.min():.6f}, {y_train.max():.6f}]")
print(f"  Val   - Mean: {y_val.mean():.6f}, Std: {y_val.std():.6f}")
print(f"  Test  - Mean: {y_test.mean():.6f}, Std: {y_test.std():.6f}")

# Check if PAC distributions are similar
print(f"\n📊 Distribution similarity:")
print(f"  Train vs Val mean difference: {abs(y_train.mean() - y_val.mean()):.6f}")
print(f"  Train vs Test mean difference: {abs(y_train.mean() - y_test.mean()):.6f}")

# Extract features for a subsample
print("\n2. Extracting features (subsample)...")
spectral_extractor = SpectralFeatureExtractor(fs=250)
wavelet_extractor = WaveletFeatureExtractor(fs=250)

def extract_all_features(X, max_samples=500):
    n_samples = min(len(X), max_samples)
    spectral_feats = np.zeros((n_samples, 61))
    wavelet_feats = np.zeros((n_samples, 74))

    print(f"  Extracting from {n_samples} samples...")
    for i in range(n_samples):
        if i % 100 == 0:
            print(f"    {i}/{n_samples}...", end='\r')
        spectral_feats[i] = spectral_extractor.extract_features(X[i])
        wavelet_feats[i] = wavelet_extractor.extract_features(X[i])

    print(f"    {n_samples}/{n_samples}... Done!")
    return np.hstack([spectral_feats, wavelet_feats])

X_train_feats = extract_all_features(X_train, max_samples=500)
y_train_sub = y_train[:500]

print(f"✓ Features extracted: {X_train_feats.shape[1]} features from {X_train_feats.shape[0]} samples")

# 3. Feature quality analysis
print("\n3. Feature Quality Analysis...")
print("-" * 70)

# Check for NaN/Inf
nan_count = np.sum(~np.isfinite(X_train_feats))
print(f"NaN/Inf values in features: {nan_count}")

if nan_count > 0:
    print("  ⚠️  WARNING: Invalid values detected!")
    nan_features = np.where(np.any(~np.isfinite(X_train_feats), axis=0))[0]
    print(f"  Features with NaN/Inf: {len(nan_features)}")

# Check feature variance
variances = np.var(X_train_feats, axis=0)
zero_var = variances < 1e-10
print(f"\nZero-variance features: {np.sum(zero_var)}/135")

if np.sum(zero_var) > 0:
    print("  ⚠️  WARNING: Constant features detected!")

low_var = (variances > 0) & (variances < 0.01)
print(f"Very low variance features (<0.01): {np.sum(low_var)}/135")

# Check feature statistics
print(f"\nFeature statistics:")
print(f"  Mean of means: {np.mean(X_train_feats):.6f}")
print(f"  Mean of stds: {np.mean(np.std(X_train_feats, axis=0)):.6f}")
print(f"  Max feature value: {np.max(X_train_feats):.6f}")
print(f"  Min feature value: {np.min(X_train_feats):.6f}")

# 4. Correlation analysis
print("\n4. Feature-Target Correlation Analysis...")
print("-" * 70)

# Compute correlations manually
correlations = []
for i in range(X_train_feats.shape[1]):
    feat = X_train_feats[:, i]
    target = y_train_sub

    # Pearson correlation
    feat_centered = feat - np.mean(feat)
    target_centered = target - np.mean(target)
    corr = np.sum(feat_centered * target_centered) / (np.sqrt(np.sum(feat_centered**2) * np.sum(target_centered**2)))
    correlations.append(corr)

correlations = np.array(correlations)
abs_corr = np.abs(correlations)

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
for i in range(35):
    feature_names.append(f'CWT_{i}')
for i in range(21):
    feature_names.append(f'WPD_{i}')
for i in range(14):
    feature_names.append(f'Sync_{i}')
for i in range(4):
    feature_names.append(f'CrossCh_{i}')

print(f"\nCorrelation statistics:")
print(f"  Max |correlation|: {np.max(abs_corr):.4f}")
print(f"  Mean |correlation|: {np.mean(abs_corr):.4f}")
print(f"  Median |correlation|: {np.median(abs_corr):.4f}")

print(f"\nFeatures with |correlation| > 0.1: {np.sum(abs_corr > 0.1)}/135")
print(f"Features with |correlation| > 0.2: {np.sum(abs_corr > 0.2)}/135")
print(f"Features with |correlation| > 0.3: {np.sum(abs_corr > 0.3)}/135")

# Top correlated features
top_indices = np.argsort(abs_corr)[::-1]
print(f"\n📊 Top 15 features by absolute correlation:")
for i in range(15):
    idx = top_indices[i]
    print(f"  {i+1:2d}. {feature_names[idx]:30s}: {correlations[idx]:+.4f} (|r|={abs_corr[idx]:.4f})")

# 5. Baseline prediction analysis
print("\n5. Baseline Prediction Analysis...")
print("-" * 70)

print("\nNaive baselines:")

# Baseline 1: Predict mean
mean_baseline_r2 = 1 - np.sum((y_test - y_test.mean())**2) / np.sum((y_test - y_test.mean())**2)
print(f"  Predict mean: R² = {mean_baseline_r2:.4f} (always 0.0 by definition)")

# Baseline 2: Use best single feature
best_feat_idx = top_indices[0]
print(f"\n  Best single feature: {feature_names[best_feat_idx]} (r={correlations[best_feat_idx]:+.4f})")

# Simple linear regression with best feature
feat_train = X_train_feats[:, best_feat_idx]
target_train = y_train_sub

# Compute slope and intercept
mean_feat = np.mean(feat_train)
mean_target = np.mean(target_train)
slope = np.sum((feat_train - mean_feat) * (target_train - mean_target)) / np.sum((feat_train - mean_feat)**2)
intercept = mean_target - slope * mean_feat

print(f"    y = {slope:.6f} * x + {intercept:.6f}")

# R² of single feature on training data
pred_train = slope * feat_train + intercept
ss_res = np.sum((target_train - pred_train)**2)
ss_tot = np.sum((target_train - mean_target)**2)
r2_single = 1 - ss_res / ss_tot
print(f"    Training R² (single feature): {r2_single:.4f}")

# 6. Model complexity analysis
print("\n6. Model Complexity vs Data Size...")
print("-" * 70)

n_train = len(X_train)
n_features = 135
n_params_vit = 1_119_063

print(f"Training samples: {n_train:,}")
print(f"Input features: {n_features}")
print(f"ViT-TCNet parameters: {n_params_vit:,}")
print(f"Samples per parameter: {n_train / n_params_vit:.2f}")

if n_train / n_params_vit < 10:
    print("\n⚠️  CRITICAL: Severe overfitting risk!")
    print("   Typical rule of thumb: 10-50 samples per parameter")
    print(f"   You have {n_train / n_params_vit:.1f} samples per parameter")
    print("   → Model is WAY too complex for dataset size")

# 7. Summary
print("\n" + "="*70)
print("DIAGNOSTIC SUMMARY")
print("="*70)

print("\n🔍 Key Findings:")

if nan_count > 0:
    print("  ❌ 1. Data quality issues: NaN/Inf values detected")
else:
    print("  ✓ 1. Data quality: No NaN/Inf values")

if np.max(abs_corr) < 0.3:
    print(f"  ❌ 2. Weak correlations: Max |r| = {np.max(abs_corr):.4f}")
    print("       → Features don't capture PAC dynamics well")
elif np.max(abs_corr) < 0.5:
    print(f"  ⚠️  2. Moderate correlations: Max |r| = {np.max(abs_corr):.4f}")
    print("       → Features are somewhat predictive, but not strong")
else:
    print(f"  ✓ 2. Strong correlations: Max |r| = {np.max(abs_corr):.4f}")

if n_train / n_params_vit < 5:
    print(f"  ❌ 3. Model too complex: {n_train / n_params_vit:.2f} samples/param")
    print("       → 1.1M parameters for 11k samples = severe overfitting")
elif n_train / n_params_vit < 10:
    print(f"  ⚠️  3. Model complexity: {n_train / n_params_vit:.2f} samples/param")
    print("       → Overfitting risk (need 10+ samples/param)")
else:
    print(f"  ✓ 3. Model size appropriate: {n_train / n_params_vit:.2f} samples/param")

print("\n💡 ROOT CAUSE:")
if np.max(abs_corr) < 0.3:
    print("  PRIMARY: Features don't capture PAC dynamics")
    print("  → Focus on feature engineering, not model architecture")
elif n_train / n_params_vit < 5:
    print("  PRIMARY: Model way too complex for dataset size")
    print("  → Use simpler models (Ridge, small MLP)")
else:
    print("  UNCLEAR: Both features and model seem reasonable")
    print("  → Need deeper investigation")

print("\n🎯 RECOMMENDATIONS:")
print("  1. ⭐ Try much simpler models first (Ridge, Lasso)")
print("  2. Add direct PAC computation features")
print("  3. Use cross-validation to avoid overfitting")
print("  4. Consider ensemble methods")
print("  5. If simple models also fail → problem may be fundamentally limited")

print("\n" + "="*70)
