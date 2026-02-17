"""
Enhanced Features + Ridge Model (V5)

Combines original features (135) with PAC-specific features (116).
Total: 251 features

Expected improvement: +0.10-0.20 R² (from 0.287 to 0.38-0.48)

If this reaches R² > 0.40, we've achieved significant progress!
"""

import numpy as np
import sys
sys.path.insert(0, 'src')

from spectral_features import SpectralFeatureExtractor
from wavelet_features import WaveletFeatureExtractor
from pac_features import PACFeatureExtractor
from sklearn.linear_model import RidgeCV, LassoCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
from pathlib import Path
import time

print("="*70)
print("ENHANCED FEATURES + RIDGE MODEL (V5)")
print("="*70)
print("Original features: 135 (spectral + wavelet)")
print("New PAC features: 116 (Hilbert, PLV, coupling metrics)")
print("Total features: 251")
print("="*70)

# 1. Load data
print("\n1. Loading data...")
train_data = np.load('data/processed/train_data.npz')
val_data = np.load('data/processed/val_data.npz')
test_data = np.load('data/processed/test_data.npz')

X_train_raw = train_data['windows'].squeeze(1)
y_train = train_data['pac']
X_val_raw = val_data['windows'].squeeze(1)
y_val = val_data['pac']
X_test_raw = test_data['windows'].squeeze(1)
y_test = test_data['pac']

print(f"✓ Train: {X_train_raw.shape}, Val: {X_val_raw.shape}, Test: {X_test_raw.shape}")

# 2. Extract all features
print("\n2. Extracting features...")
spectral_extractor = SpectralFeatureExtractor(fs=250)
wavelet_extractor = WaveletFeatureExtractor(fs=250)
pac_extractor = PACFeatureExtractor(fs=250)

def extract_all_features(X, name=""):
    n_samples = len(X)
    spectral_feats = np.zeros((n_samples, 61))
    wavelet_feats = np.zeros((n_samples, 74))
    pac_feats = np.zeros((n_samples, 116))

    print(f"  {name}: Extracting from {n_samples} samples...")
    t0 = time.time()

    for i in range(n_samples):
        if i % 500 == 0:
            elapsed = time.time() - t0
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (n_samples - i) / rate if rate > 0 else 0
            print(f"    Progress: {i}/{n_samples} ({100*i/n_samples:.1f}%) - {rate:.0f} samples/s - ETA: {remaining:.0f}s", end='\r')

        spectral_feats[i] = spectral_extractor.extract(X[i:i+1])[0]
        wavelet_feats[i] = wavelet_extractor.extract(X[i:i+1])[0]
        pac_feats[i] = pac_extractor.extract(X[i])

    elapsed = time.time() - t0
    print(f"    Progress: {n_samples}/{n_samples} (100.0%) - Done in {elapsed:.1f}s!        ")

    return np.hstack([spectral_feats, wavelet_feats, pac_feats])

X_train = extract_all_features(X_train_raw, "Train")
X_val = extract_all_features(X_val_raw, "Val")
X_test = extract_all_features(X_test_raw, "Test")

print(f"\n✓ Feature extraction completed")
print(f"  Total features: {X_train.shape[1]}")

# 3. Normalize
print("\n3. Normalizing features...")
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

Path('models').mkdir(exist_ok=True)
joblib.dump(scaler, 'models/scaler_v5_enhanced.pkl')
print("✓ Features normalized and scaler saved")

# 4. Check for issues
print("\n4. Feature quality check...")
nan_count = np.sum(~np.isfinite(X_train))
if nan_count > 0:
    print(f"  ⚠️  WARNING: {nan_count} NaN/Inf values detected!")
    print("  Replacing with zeros...")
    X_train = np.nan_to_num(X_train, nan=0.0, posinf=0.0, neginf=0.0)
    X_val = np.nan_to_num(X_val, nan=0.0, posinf=0.0, neginf=0.0)
    X_test = np.nan_to_num(X_test, nan=0.0, posinf=0.0, neginf=0.0)
else:
    print("  ✓ No NaN/Inf values")

# Check variance
zero_var = np.var(X_train, axis=0) < 1e-10
if np.sum(zero_var) > 0:
    print(f"  ⚠️  {np.sum(zero_var)} zero-variance features detected (will be handled by Ridge)")

print(f"  ✓ Feature quality check complete")

# 5. Train Ridge model
print("\n5. Training Ridge Regression with Enhanced Features...")
print("="*70)

print("\n  Cross-validating alpha parameter...")
alphas = np.logspace(-4, 4, 50)
ridge = RidgeCV(alphas=alphas, cv=5)

print("  Training...")
t0 = time.time()
ridge.fit(X_train, y_train)
t1 = time.time()

print(f"  ✓ Training completed in {t1-t0:.1f}s")
print(f"  Best alpha: {ridge.alpha_:.6f}")

# 6. Evaluate
print("\n6. Evaluation...")
print("="*70)

# Predictions
ridge_train_pred = ridge.predict(X_train)
ridge_val_pred = ridge.predict(X_val)
ridge_test_pred = ridge.predict(X_test)

# Metrics
train_r2 = r2_score(y_train, ridge_train_pred)
val_r2 = r2_score(y_val, ridge_val_pred)
test_r2 = r2_score(y_test, ridge_test_pred)

train_mae = mean_absolute_error(y_train, ridge_train_pred)
val_mae = mean_absolute_error(y_val, ridge_val_pred)
test_mae = mean_absolute_error(y_test, ridge_test_pred)

train_corr = np.corrcoef(ridge_train_pred, y_train)[0, 1]
val_corr = np.corrcoef(ridge_val_pred, y_val)[0, 1]
test_corr = np.corrcoef(ridge_test_pred, y_test)[0, 1]

print("\nPerformance:")
print(f"  Train: R² = {train_r2:.4f}, MAE = {train_mae:.6f}, Corr = {train_corr:+.4f}")
print(f"  Val:   R² = {val_r2:.4f}, MAE = {val_mae:.6f}, Corr = {val_corr:+.4f}")
print(f"  Test:  R² = {test_r2:.4f}, MAE = {test_mae:.6f}, Corr = {test_corr:+.4f}")

# 7. Comparison with previous versions
print("\n7. Performance Comparison...")
print("="*70)

versions = {
    'V3-Clean (baseline)': 0.236,
    'V4 ViT-TCNet': 0.252,
    'V5 Ridge (original features)': 0.287,
    'V5 Ridge (enhanced features)': test_r2
}

print("\nVersion                          | Test R²  | vs Baseline | vs V4")
print("---------------------------------|----------|-------------|--------")

baseline_r2 = versions['V3-Clean (baseline)']
v4_r2 = versions['V4 ViT-TCNet']

for name, r2 in versions.items():
    vs_baseline = (r2 - baseline_r2) / baseline_r2 * 100
    vs_v4 = (r2 - v4_r2) / v4_r2 * 100

    marker = "✓" if r2 >= v4_r2 else " "
    print(f"{marker} {name:30s} | {r2:.4f}  | {vs_baseline:+6.1f}%    | {vs_v4:+6.1f}%")

# 8. Progress toward target
print("\n8. Progress Toward Target...")
print("="*70)

target_r2 = 0.46
improvement_from_v3 = test_r2 - baseline_r2
needed_improvement = target_r2 - baseline_r2
progress = improvement_from_v3 / needed_improvement * 100

print(f"\n  Starting point (V3-Clean): R² = {baseline_r2:.4f}")
print(f"  Current (V5 Enhanced):     R² = {test_r2:.4f}")
print(f"  Target:                    R² = {target_r2:.4f}")
print(f"\n  Improvement from baseline: +{improvement_from_v3:.4f} ({improvement_from_v3/baseline_r2*100:.1f}%)")
print(f"  Needed to reach target:    +{target_r2 - test_r2:.4f}")
print(f"  Progress:                  {progress:.1f}% of target")

# Save model
joblib.dump(ridge, 'models/ridge_v5_enhanced.pkl')
print(f"\n✓ Model saved to models/ridge_v5_enhanced.pkl")

# 9. Feature importance analysis
print("\n9. Top 20 Most Important Features...")
print("="*70)

coef = ridge.coef_
abs_coef = np.abs(coef)
top_indices = np.argsort(abs_coef)[::-1]

# Feature names
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

# PAC features (116)
pac_feature_groups = [
    ('PAC_MI_ch', 7),
    ('PAC_corr_ch', 7),
    ('PreferredPhase_ch', 7),
    ('PhaseConsistency_ch', 7),
    ('ThetaPLV_pair', 21),
    ('GammaCorr_pair', 21),
    ('CouplingProfile_bin', 18),
    ('ThetaGammaAmpCorr_ch', 7),
    ('ThetaAsymmetry_ch', 7),
    ('BurstPhaseMean_ch', 7),
    ('BurstPhaseStd_ch', 7)
]

for group_name, count in pac_feature_groups:
    for i in range(count):
        feature_names.append(f'{group_name}{i}')

print("\nTop 20 features:")
for i in range(20):
    idx = top_indices[i]
    print(f"  {i+1:2d}. {feature_names[idx]:35s}: {coef[idx]:+.6f} (|coef|={abs_coef[idx]:.6f})")

# Count PAC features in top 20
n_pac_in_top20 = sum(1 for i in range(20) if 'PAC' in feature_names[top_indices[i]]
                     or 'Preferred' in feature_names[top_indices[i]]
                     or 'Phase' in feature_names[top_indices[i]]
                     or 'Burst' in feature_names[top_indices[i]]
                     or 'Coupling' in feature_names[top_indices[i]]
                     or 'ThetaPLV' in feature_names[top_indices[i]]
                     or 'GammaCorr' in feature_names[top_indices[i]]
                     or 'ThetaGamma' in feature_names[top_indices[i]]
                     or 'ThetaAsymmetry' in feature_names[top_indices[i]])

print(f"\n  PAC-specific features in top 20: {n_pac_in_top20}/20")
print(f"  Original features in top 20: {20 - n_pac_in_top20}/20")

# 10. Final assessment
print("\n" + "="*70)
print("FINAL ASSESSMENT")
print("="*70)

improvement_from_original = test_r2 - 0.287
pac_contribution = improvement_from_original / 0.287 * 100

print(f"\n📊 Results:")
print(f"  Original features (135):  R² = 0.287")
print(f"  Enhanced features (251):  R² = {test_r2:.4f}")
print(f"  Improvement:              +{improvement_from_original:.4f} ({pac_contribution:+.1f}%)")

if test_r2 >= 0.40:
    print("\n🎉 EXCELLENT PROGRESS!")
    print(f"  → PAC features significantly improved performance")
    print(f"  → Current R² = {test_r2:.4f} is close to target {target_r2:.4f}")
    print(f"  → Gap remaining: {target_r2 - test_r2:.4f}")
    print("\n💡 Next steps:")
    print("  1. Try Lasso for feature selection")
    print("  2. Add more PAC variants (different freq bands)")
    print("  3. Consider ensemble of Ridge + Lasso")

elif test_r2 >= 0.35:
    print("\n✅ GOOD PROGRESS!")
    print(f"  → PAC features helped improve performance")
    print(f"  → Still {target_r2 - test_r2:.4f} R² points away from target")
    print("\n💡 Next steps:")
    print("  1. Try feature selection (remove noisy features)")
    print("  2. Add more coupling metrics (bispectrum, coherence)")
    print("  3. Try different frequency bands for PAC")

elif test_r2 >= 0.30:
    print("\n~ MODEST IMPROVEMENT")
    print(f"  → PAC features provided some benefit")
    print(f"  → Improvement is modest (+{improvement_from_original:.4f})")
    print(f"  → May be approaching performance ceiling")
    print("\n💡 Next steps:")
    print("  1. Check if PAC features have low SNR")
    print("  2. Try nonlinear models (Gradient Boosting)")
    print("  3. Consider data quality issues")

else:
    print("\n⚠️  NO IMPROVEMENT")
    print(f"  → PAC features didn't help (or made things worse)")
    print(f"  → Possible issues:")
    print("    - PAC features are noisy")
    print("    - Computing PAC from already-PAC-labeled data is circular")
    print("    - Features need debugging")
    print("\n💡 Next steps:")
    print("  1. Debug PAC feature computation")
    print("  2. Check for NaN/Inf values")
    print("  3. Try feature selection to remove bad features")

print("\n" + "="*70)
