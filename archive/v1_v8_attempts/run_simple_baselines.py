"""
Simple Baseline Models for PAC Prediction

Tests if features are predictive using simple, well-regularized models.
If these match/beat ViT-TCNet → features are good, model was too complex.
If these also fail → need better features, not better models.

Models tested:
1. Ridge Regression (L2 regularization)
2. Lasso Regression (L1 regularization + feature selection)
3. Elastic Net (L1 + L2)
4. Shallow Neural Net (2 layers, <5k params)

Expected: R² = 0.25-0.35 if features are good
"""

import numpy as np
import sys
sys.path.insert(0, 'src')

from spectral_features import SpectralFeatureExtractor
from wavelet_features import WaveletFeatureExtractor
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
from pathlib import Path
import time

print("="*70)
print("SIMPLE BASELINE MODELS - Testing Feature Quality")
print("="*70)
print("Goal: Determine if features are predictive or need improvement")
print("="*70)

# 1. Load data
print("\n1. Loading data...")
train_data = np.load('data/processed/train_data.npz')
val_data = np.load('data/processed/val_data.npz')
test_data = np.load('data/processed/test_data.npz')

X_train_raw = train_data['windows'].squeeze(1)  # (11736, 7, 500)
y_train = train_data['pac']
X_val_raw = val_data['windows'].squeeze(1)
y_val = val_data['pac']
X_test_raw = test_data['windows'].squeeze(1)
y_test = test_data['pac']

print(f"✓ Train: {X_train_raw.shape}, Val: {X_val_raw.shape}, Test: {X_test_raw.shape}")

# 2. Extract features
print("\n2. Extracting features...")
spectral_extractor = SpectralFeatureExtractor(fs=250)
wavelet_extractor = WaveletFeatureExtractor(fs=250)

def extract_all_features(X, name=""):
    n_samples = len(X)
    spectral_feats = np.zeros((n_samples, 61))
    wavelet_feats = np.zeros((n_samples, 74))

    print(f"  {name}: Extracting from {n_samples} samples...")
    for i in range(n_samples):
        if i % 500 == 0:
            print(f"    Progress: {i}/{n_samples} ({100*i/n_samples:.1f}%)", end='\r')

        # Use 'extract' method, not 'extract_features'
        spectral_feats[i] = spectral_extractor.extract(X[i:i+1])[0]
        wavelet_feats[i] = wavelet_extractor.extract(X[i:i+1])[0]

    print(f"    Progress: {n_samples}/{n_samples} (100.0%) - Done!")
    return np.hstack([spectral_feats, wavelet_feats])

t0 = time.time()
X_train = extract_all_features(X_train_raw, "Train")
X_val = extract_all_features(X_val_raw, "Val")
X_test = extract_all_features(X_test_raw, "Test")
t1 = time.time()

print(f"\n✓ Feature extraction completed in {t1-t0:.1f}s")
print(f"  Features per sample: {X_train.shape[1]}")

# 3. Normalize features
print("\n3. Normalizing features...")
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

# Save scaler
Path('models').mkdir(exist_ok=True)
joblib.dump(scaler, 'models/scaler_v5_simple.pkl')
print("✓ Features normalized and scaler saved")

# 4. Train models
print("\n4. Training Simple Baseline Models...")
print("="*70)

results = {}

# 4a. Ridge Regression
print("\n4a. Ridge Regression (L2 regularization)...")
print("  Cross-validating alpha parameter...")
alphas = np.logspace(-4, 4, 50)
ridge = RidgeCV(alphas=alphas, cv=5)
ridge.fit(X_train, y_train)

ridge_val_pred = ridge.predict(X_val)
ridge_test_pred = ridge.predict(X_test)

ridge_val_r2 = r2_score(y_val, ridge_val_pred)
ridge_test_r2 = r2_score(y_test, ridge_test_pred)
ridge_val_mae = mean_absolute_error(y_val, ridge_val_pred)
ridge_test_mae = mean_absolute_error(y_test, ridge_test_pred)

print(f"  Best alpha: {ridge.alpha_:.6f}")
print(f"  Val R²: {ridge_val_r2:.4f}, MAE: {ridge_val_mae:.6f}")
print(f"  Test R²: {ridge_test_r2:.4f}, MAE: {ridge_test_mae:.6f}")

results['Ridge'] = {
    'model': ridge,
    'val_r2': ridge_val_r2,
    'test_r2': ridge_test_r2,
    'val_mae': ridge_val_mae,
    'test_mae': ridge_test_mae
}

joblib.dump(ridge, 'models/ridge_v5.pkl')

# 4b. Lasso Regression
print("\n4b. Lasso Regression (L1 regularization, feature selection)...")
print("  Cross-validating alpha parameter...")
alphas = np.logspace(-7, -3, 50)
lasso = LassoCV(alphas=alphas, cv=5, max_iter=10000)
lasso.fit(X_train, y_train)

lasso_val_pred = lasso.predict(X_val)
lasso_test_pred = lasso.predict(X_test)

lasso_val_r2 = r2_score(y_val, lasso_val_pred)
lasso_test_r2 = r2_score(y_test, lasso_test_pred)
lasso_val_mae = mean_absolute_error(y_val, lasso_val_pred)
lasso_test_mae = mean_absolute_error(y_test, lasso_test_pred)

n_selected = np.sum(np.abs(lasso.coef_) > 1e-6)

print(f"  Best alpha: {lasso.alpha_:.6f}")
print(f"  Features selected: {n_selected}/135")
print(f"  Val R²: {lasso_val_r2:.4f}, MAE: {lasso_val_mae:.6f}")
print(f"  Test R²: {lasso_test_r2:.4f}, MAE: {lasso_test_mae:.6f}")

results['Lasso'] = {
    'model': lasso,
    'val_r2': lasso_val_r2,
    'test_r2': lasso_test_r2,
    'val_mae': lasso_val_mae,
    'test_mae': lasso_test_mae,
    'n_features': n_selected
}

joblib.dump(lasso, 'models/lasso_v5.pkl')

# 4c. Elastic Net
print("\n4c. Elastic Net (L1 + L2 regularization)...")
print("  Cross-validating alpha and l1_ratio...")
alphas = np.logspace(-7, -3, 20)
l1_ratios = [0.1, 0.3, 0.5, 0.7, 0.9]
enet = ElasticNetCV(alphas=alphas, l1_ratio=l1_ratios, cv=5, max_iter=10000)
enet.fit(X_train, y_train)

enet_val_pred = enet.predict(X_val)
enet_test_pred = enet.predict(X_test)

enet_val_r2 = r2_score(y_val, enet_val_pred)
enet_test_r2 = r2_score(y_test, enet_test_pred)
enet_val_mae = mean_absolute_error(y_val, enet_val_pred)
enet_test_mae = mean_absolute_error(y_test, enet_test_pred)

n_selected_enet = np.sum(np.abs(enet.coef_) > 1e-6)

print(f"  Best alpha: {enet.alpha_:.6f}, l1_ratio: {enet.l1_ratio_:.2f}")
print(f"  Features selected: {n_selected_enet}/135")
print(f"  Val R²: {enet_val_r2:.4f}, MAE: {enet_val_mae:.6f}")
print(f"  Test R²: {enet_test_r2:.4f}, MAE: {enet_test_mae:.6f}")

results['ElasticNet'] = {
    'model': enet,
    'val_r2': enet_val_r2,
    'test_r2': enet_test_r2,
    'val_mae': enet_val_mae,
    'test_mae': enet_test_mae,
    'n_features': n_selected_enet
}

joblib.dump(enet, 'models/elasticnet_v5.pkl')

# 4d. Random Forest
print("\n4d. Random Forest (non-linear baseline)...")
print("  Training with conservative hyperparameters...")
rf = RandomForestRegressor(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=10,
    min_samples_split=20,
    max_features='sqrt',
    n_jobs=-1,
    random_state=42
)
rf.fit(X_train, y_train)

rf_val_pred = rf.predict(X_val)
rf_test_pred = rf.predict(X_test)

rf_val_r2 = r2_score(y_val, rf_val_pred)
rf_test_r2 = r2_score(y_test, rf_test_pred)
rf_val_mae = mean_absolute_error(y_val, rf_val_pred)
rf_test_mae = mean_absolute_error(y_test, rf_test_pred)

print(f"  Val R²: {rf_val_r2:.4f}, MAE: {rf_val_mae:.6f}")
print(f"  Test R²: {rf_test_r2:.4f}, MAE: {rf_test_mae:.6f}")

results['RandomForest'] = {
    'model': rf,
    'val_r2': rf_val_r2,
    'test_r2': rf_test_r2,
    'val_mae': rf_val_mae,
    'test_mae': rf_test_mae
}

joblib.dump(rf, 'models/random_forest_v5.pkl')

# 4e. Gradient Boosting
print("\n4e. Gradient Boosting (non-linear + boosting)...")
print("  Training with conservative hyperparameters...")
gb = GradientBoostingRegressor(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    min_samples_leaf=10,
    subsample=0.8,
    random_state=42
)
gb.fit(X_train, y_train)

gb_val_pred = gb.predict(X_val)
gb_test_pred = gb.predict(X_test)

gb_val_r2 = r2_score(y_val, gb_val_pred)
gb_test_r2 = r2_score(y_test, gb_test_pred)
gb_val_mae = mean_absolute_error(y_val, gb_val_pred)
gb_test_mae = mean_absolute_error(y_test, gb_test_pred)

print(f"  Val R²: {gb_val_r2:.4f}, MAE: {gb_val_mae:.6f}")
print(f"  Test R²: {gb_test_r2:.4f}, MAE: {gb_test_mae:.6f}")

results['GradientBoosting'] = {
    'model': gb,
    'val_r2': gb_val_r2,
    'test_r2': gb_test_r2,
    'val_mae': gb_val_mae,
    'test_mae': gb_test_mae
}

joblib.dump(gb, 'models/gradient_boosting_v5.pkl')

# 5. Ensemble (average predictions)
print("\n4f. Ensemble (average of all models)...")
ensemble_val_pred = (ridge_val_pred + lasso_val_pred + enet_val_pred + rf_val_pred + gb_val_pred) / 5
ensemble_test_pred = (ridge_test_pred + lasso_test_pred + enet_test_pred + rf_test_pred + gb_test_pred) / 5

ensemble_val_r2 = r2_score(y_val, ensemble_val_pred)
ensemble_test_r2 = r2_score(y_test, ensemble_test_pred)
ensemble_val_mae = mean_absolute_error(y_val, ensemble_val_pred)
ensemble_test_mae = mean_absolute_error(y_test, ensemble_test_pred)

print(f"  Val R²: {ensemble_val_r2:.4f}, MAE: {ensemble_val_mae:.6f}")
print(f"  Test R²: {ensemble_test_r2:.4f}, MAE: {ensemble_test_mae:.6f}")

results['Ensemble'] = {
    'val_r2': ensemble_val_r2,
    'test_r2': ensemble_test_r2,
    'val_mae': ensemble_val_mae,
    'test_mae': ensemble_test_mae
}

# Save ensemble predictions for stacking
np.savez('models/ensemble_predictions_v5.npz',
         val_pred=ensemble_val_pred,
         test_pred=ensemble_test_pred)

# 6. Summary and comparison
print("\n" + "="*70)
print("RESULTS SUMMARY")
print("="*70)

print("\n📊 Performance Comparison:")
print("\nModel              | Val R²  | Test R² | Test MAE  | vs V4 ViT-TCNet")
print("-------------------|---------|---------|-----------|------------------")

baseline_r2 = 0.236  # V3-clean
v4_r2 = 0.252  # V4 ViT-TCNet

for model_name, result in results.items():
    val_r2 = result['val_r2']
    test_r2 = result['test_r2']
    test_mae = result['test_mae']
    improvement = (test_r2 - v4_r2) / v4_r2 * 100

    marker = ""
    if test_r2 > v4_r2:
        marker = "✓"
    elif test_r2 > v4_r2 - 0.01:
        marker = "~"
    else:
        marker = " "

    print(f"{marker} {model_name:16s} | {val_r2:.4f} | {test_r2:.4f} | {test_mae:.6f} | {improvement:+.1f}%")

print(f"\n  V3-Clean (baseline) |  N/A    | {baseline_r2:.4f} |    N/A    | N/A")
print(f"  V4 ViT-TCNet        | 0.2066  | {v4_r2:.4f} | 0.606208  | baseline")

# Find best model
best_model_name = max(results.items(), key=lambda x: x[1]['test_r2'])[0]
best_test_r2 = results[best_model_name]['test_r2']

print("\n" + "="*70)
print("ANALYSIS AND CONCLUSIONS")
print("="*70)

print(f"\n🏆 Best model: {best_model_name} (Test R² = {best_test_r2:.4f})")

if best_test_r2 > v4_r2 + 0.01:
    print("\n✅ SIMPLE MODELS WIN!")
    print("  → Simple models significantly outperform ViT-TCNet")
    print("  → The features ARE predictive")
    print("  → V4 failed due to overparameterization/overfitting")
    print("  → Recommendation: Use simple models or small neural nets")

elif best_test_r2 > v4_r2 - 0.01:
    print("\n~ SIMPLE MODELS MATCH ViT-TCNet")
    print("  → Simple and complex models perform similarly")
    print("  → Features are moderately predictive")
    print("  → V4's complexity didn't help (and hurt due to overfitting)")
    print("  → Recommendation: Use simple models (simpler, faster, same performance)")

else:
    print("\n❌ ALL MODELS STRUGGLE")
    print("  → Even simple models can't break R² = 0.30")
    print("  → Features don't capture PAC dynamics well enough")
    print("  → Problem: Feature engineering, not model architecture")
    print("  → Recommendation: Add domain-specific PAC features")

# Feature importance from best linear model
if best_model_name in ['Ridge', 'Lasso', 'ElasticNet']:
    print(f"\n📌 Feature Analysis ({best_model_name}):")
    coef = results[best_model_name]['model'].coef_

    # Get feature names
    feature_names = []
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

    for i in range(35):
        feature_names.append(f'CWT_{i}')
    for i in range(21):
        feature_names.append(f'WPD_{i}')
    for i in range(14):
        feature_names.append(f'Sync_{i}')
    for i in range(4):
        feature_names.append(f'CrossCh_{i}')

    abs_coef = np.abs(coef)
    top_indices = np.argsort(abs_coef)[::-1]

    print(f"  Top 10 features:")
    for i in range(10):
        idx = top_indices[i]
        print(f"    {i+1:2d}. {feature_names[idx]:30s}: {coef[idx]:+.6f}")

print("\n🎯 NEXT STEPS:")

if best_test_r2 > 0.35:
    print("  1. ✓ Features are good! Try shallow neural net (2-3 layers, <10k params)")
    print("  2. Use the best simple model for deployment (fast, interpretable)")
    print("  3. Try stacking: train meta-model on ensemble predictions")

elif best_test_r2 > 0.28:
    print("  1. Features are okay but could be better")
    print("  2. Add domain-specific PAC features:")
    print("     - Direct theta phase extraction (Hilbert transform)")
    print("     - Direct gamma amplitude extraction")
    print("     - Phase-locking value (PLV)")
    print("     - MI computed properly (without data leakage)")
    print("  3. Try feature selection to remove noise")

else:
    print("  1. ❌ Current features insufficient - need better feature engineering")
    print("  2. Add strong PAC-specific features:")
    print("     - Hilbert transform for instantaneous phase/amplitude")
    print("     - Bispectrum (frequency-frequency coupling)")
    print("     - Nonlinear coupling metrics")
    print("     - Multi-taper spectral coherence")
    print("  3. Consider if target PAC values are reliable/measurable")

print("\n" + "="*70)
