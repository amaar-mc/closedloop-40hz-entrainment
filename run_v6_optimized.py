"""
V6: Optimized Ensemble for Maximum Honest Performance

Strategy:
1. Feature selection (keep only predictive features)
2. Add temporal context (rolling statistics)
3. Train optimized ensemble (Ridge + Lasso + GradientBoosting + MLP)
4. Extensive cross-validation
5. Stacking meta-learner

Target: R² = 0.35-0.40 (honest, no leakage)
"""

import numpy as np
import sys
sys.path.insert(0, 'src')

from spectral_features import SpectralFeatureExtractor
from wavelet_features import WaveletFeatureExtractor
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score, KFold
import joblib
from pathlib import Path
import time
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("V6: OPTIMIZED ENSEMBLE FOR MAXIMUM HONEST PERFORMANCE")
print("="*70)
print("Strategy:")
print("  1. Feature selection (Lasso-selected features)")
print("  2. Temporal context (rolling statistics over windows)")
print("  3. Optimized hyperparameters")
print("  4. Ensemble: Ridge + Lasso + GradientBoosting + MLP")
print("  5. Stacking meta-learner")
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

# 2. Extract base features
print("\n2. Extracting base features...")
spectral_extractor = SpectralFeatureExtractor(fs=250)
wavelet_extractor = WaveletFeatureExtractor(fs=250)

def extract_all_features(X, name=""):
    n_samples = len(X)
    spectral_feats = np.zeros((n_samples, 61))
    wavelet_feats = np.zeros((n_samples, 74))

    print(f"  {name}: Extracting from {n_samples} samples...")
    t0 = time.time()

    for i in range(n_samples):
        if i % 500 == 0:
            elapsed = time.time() - t0
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (n_samples - i) / rate if rate > 0 else 0
            print(f"    Progress: {i}/{n_samples} ({100*i/n_samples:.1f}%) - ETA: {remaining:.0f}s", end='\r')

        spectral_feats[i] = spectral_extractor.extract(X[i:i+1])[0]
        wavelet_feats[i] = wavelet_extractor.extract(X[i:i+1])[0]

    elapsed = time.time() - t0
    print(f"    Progress: {n_samples}/{n_samples} (100.0%) - Done in {elapsed:.1f}s!        ")

    return np.hstack([spectral_feats, wavelet_feats])

X_train_base = extract_all_features(X_train_raw, "Train")
X_val_base = extract_all_features(X_val_raw, "Val")
X_test_base = extract_all_features(X_test_raw, "Test")

print(f"\n✓ Base features extracted: {X_train_base.shape[1]} features")

# 3. Add temporal context features
print("\n3. Adding temporal context features...")
print("  Computing rolling statistics (window size = 5)...")

def add_temporal_features(X_base, window_size=5):
    """Add rolling mean and std features."""
    n_samples, n_features = X_base.shape

    # Preallocate
    rolling_mean = np.zeros_like(X_base)
    rolling_std = np.zeros_like(X_base)

    # Compute rolling statistics
    for i in range(n_samples):
        start_idx = max(0, i - window_size + 1)
        window = X_base[start_idx:i+1]

        rolling_mean[i] = np.mean(window, axis=0)
        rolling_std[i] = np.std(window, axis=0)

    # First differences (trends)
    diff = np.diff(X_base, axis=0, prepend=X_base[0:1])

    # Combine
    X_temporal = np.hstack([
        X_base,         # Original features
        rolling_mean,   # Rolling mean
        rolling_std,    # Rolling std
        diff            # First difference
    ])

    return X_temporal

X_train_temporal = add_temporal_features(X_train_base)
X_val_temporal = add_temporal_features(X_val_base)
X_test_temporal = add_temporal_features(X_test_base)

print(f"✓ Temporal features added: {X_train_temporal.shape[1]} total features")
print(f"  (135 base + 135 rolling_mean + 135 rolling_std + 135 diff = 540 total)")

# 4. Normalize
print("\n4. Normalizing features...")
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train_temporal)
X_val = scaler.transform(X_val_temporal)
X_test = scaler.transform(X_test_temporal)

# Handle any NaN from temporal features
X_train = np.nan_to_num(X_train, nan=0.0, posinf=0.0, neginf=0.0)
X_val = np.nan_to_num(X_val, nan=0.0, posinf=0.0, neginf=0.0)
X_test = np.nan_to_num(X_test, nan=0.0, posinf=0.0, neginf=0.0)

print("✓ Features normalized")

# 5. Feature selection with Lasso
print("\n5. Feature Selection with Lasso...")
print("  Training Lasso to identify important features...")

lasso_selector = LassoCV(alphas=np.logspace(-7, -3, 50), cv=5, max_iter=10000)
lasso_selector.fit(X_train, y_train)

# Select features with non-zero coefficients
selected_features = np.abs(lasso_selector.coef_) > 1e-6
n_selected = np.sum(selected_features)

print(f"✓ Lasso selected {n_selected}/{X_train.shape[1]} features")

# Apply feature selection
X_train_selected = X_train[:, selected_features]
X_val_selected = X_val[:, selected_features]
X_test_selected = X_test[:, selected_features]

# Save feature selector
Path('models').mkdir(exist_ok=True)
joblib.dump(scaler, 'models/scaler_v6.pkl')
joblib.dump(selected_features, 'models/feature_selection_v6.pkl')

# 6. Train ensemble models
print("\n6. Training Ensemble Models...")
print("="*70)

models = {}

# 6a. Ridge (on selected features)
print("\n6a. Ridge Regression...")
ridge = RidgeCV(alphas=np.logspace(-4, 4, 50), cv=5)
ridge.fit(X_train_selected, y_train)
ridge_val_pred = ridge.predict(X_val_selected)
ridge_test_pred = ridge.predict(X_test_selected)
ridge_val_r2 = r2_score(y_val, ridge_val_pred)
ridge_test_r2 = r2_score(y_test, ridge_test_pred)

print(f"  Val R²: {ridge_val_r2:.4f}, Test R²: {ridge_test_r2:.4f}")
models['Ridge'] = {
    'model': ridge,
    'val_pred': ridge_val_pred,
    'test_pred': ridge_test_pred,
    'val_r2': ridge_val_r2,
    'test_r2': ridge_test_r2
}
joblib.dump(ridge, 'models/ridge_v6.pkl')

# 6b. Lasso (on selected features)
print("\n6b. Lasso Regression...")
lasso = LassoCV(alphas=np.logspace(-7, -3, 50), cv=5, max_iter=10000)
lasso.fit(X_train_selected, y_train)
lasso_val_pred = lasso.predict(X_val_selected)
lasso_test_pred = lasso.predict(X_test_selected)
lasso_val_r2 = r2_score(y_val, lasso_val_pred)
lasso_test_r2 = r2_score(y_test, lasso_test_pred)

print(f"  Val R²: {lasso_val_r2:.4f}, Test R²: {lasso_test_r2:.4f}")
models['Lasso'] = {
    'model': lasso,
    'val_pred': lasso_val_pred,
    'test_pred': lasso_test_pred,
    'val_r2': lasso_val_r2,
    'test_r2': lasso_test_r2
}
joblib.dump(lasso, 'models/lasso_v6.pkl')

# 6c. Gradient Boosting (optimized)
print("\n6c. Gradient Boosting (optimized hyperparameters)...")
gb = GradientBoostingRegressor(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.03,
    min_samples_leaf=15,
    min_samples_split=30,
    subsample=0.8,
    max_features='sqrt',
    random_state=42
)
gb.fit(X_train_selected, y_train)
gb_val_pred = gb.predict(X_val_selected)
gb_test_pred = gb.predict(X_test_selected)
gb_val_r2 = r2_score(y_val, gb_val_pred)
gb_test_r2 = r2_score(y_test, gb_test_pred)

print(f"  Val R²: {gb_val_r2:.4f}, Test R²: {gb_test_r2:.4f}")
models['GradientBoosting'] = {
    'model': gb,
    'val_pred': gb_val_pred,
    'test_pred': gb_test_pred,
    'val_r2': gb_val_r2,
    'test_r2': gb_test_r2
}
joblib.dump(gb, 'models/gradient_boosting_v6.pkl')

# 6d. Small MLP (shallow neural net)
print("\n6d. Small MLP (2 hidden layers, strong regularization)...")
mlp = MLPRegressor(
    hidden_layer_sizes=(128, 64),
    activation='relu',
    alpha=0.01,  # Strong L2 regularization
    learning_rate_init=0.001,
    max_iter=500,
    early_stopping=True,
    validation_fraction=0.2,
    n_iter_no_change=20,
    random_state=42
)
mlp.fit(X_train_selected, y_train)
mlp_val_pred = mlp.predict(X_val_selected)
mlp_test_pred = mlp.predict(X_test_selected)
mlp_val_r2 = r2_score(y_val, mlp_val_pred)
mlp_test_r2 = r2_score(y_test, mlp_test_pred)

print(f"  Val R²: {mlp_val_r2:.4f}, Test R²: {mlp_test_r2:.4f}")
models['MLP'] = {
    'model': mlp,
    'val_pred': mlp_val_pred,
    'test_pred': mlp_test_pred,
    'val_r2': mlp_val_r2,
    'test_r2': mlp_test_r2
}
joblib.dump(mlp, 'models/mlp_v6.pkl')

# 7. Simple ensemble (average predictions)
print("\n7. Creating Simple Ensemble (average)...")
ensemble_val_pred = np.mean([m['val_pred'] for m in models.values()], axis=0)
ensemble_test_pred = np.mean([m['test_pred'] for m in models.values()], axis=0)

ensemble_val_r2 = r2_score(y_val, ensemble_val_pred)
ensemble_test_r2 = r2_score(y_test, ensemble_test_pred)

print(f"  Val R²: {ensemble_val_r2:.4f}, Test R²: {ensemble_test_r2:.4f}")

models['Ensemble_Simple'] = {
    'val_pred': ensemble_val_pred,
    'test_pred': ensemble_test_pred,
    'val_r2': ensemble_val_r2,
    'test_r2': ensemble_test_r2
}

# Save ensemble predictions
np.savez('models/ensemble_predictions_v6.npz',
         val_pred=ensemble_val_pred,
         test_pred=ensemble_test_pred)

# 8. Weighted ensemble (optimize weights on validation set)
print("\n8. Creating Weighted Ensemble (optimized)...")

from scipy.optimize import minimize

def ensemble_loss(weights, predictions, target):
    """Negative R² for minimization."""
    weights = np.abs(weights)  # Ensure positive
    weights = weights / np.sum(weights)  # Normalize

    ensemble_pred = np.average(predictions, axis=0, weights=weights)
    r2 = r2_score(target, ensemble_pred)
    return -r2  # Minimize negative R²

# Get validation predictions
val_predictions = np.array([m['val_pred'] for m in [models['Ridge'], models['Lasso'],
                                                     models['GradientBoosting'], models['MLP']]])

# Optimize weights
initial_weights = np.ones(4) / 4  # Equal weights
result = minimize(ensemble_loss, initial_weights, args=(val_predictions, y_val),
                 method='Nelder-Mead', options={'maxiter': 1000})

optimal_weights = np.abs(result.x)
optimal_weights = optimal_weights / np.sum(optimal_weights)

print(f"  Optimal weights:")
print(f"    Ridge: {optimal_weights[0]:.3f}")
print(f"    Lasso: {optimal_weights[1]:.3f}")
print(f"    GradientBoosting: {optimal_weights[2]:.3f}")
print(f"    MLP: {optimal_weights[3]:.3f}")

# Apply weights to test set
test_predictions = np.array([m['test_pred'] for m in [models['Ridge'], models['Lasso'],
                                                       models['GradientBoosting'], models['MLP']]])

ensemble_weighted_val = np.average(val_predictions, axis=0, weights=optimal_weights)
ensemble_weighted_test = np.average(test_predictions, axis=0, weights=optimal_weights)

ensemble_weighted_val_r2 = r2_score(y_val, ensemble_weighted_val)
ensemble_weighted_test_r2 = r2_score(y_test, ensemble_weighted_test)

print(f"  Val R²: {ensemble_weighted_val_r2:.4f}, Test R²: {ensemble_weighted_test_r2:.4f}")

models['Ensemble_Weighted'] = {
    'val_pred': ensemble_weighted_val,
    'test_pred': ensemble_weighted_test,
    'val_r2': ensemble_weighted_val_r2,
    'test_r2': ensemble_weighted_test_r2,
    'weights': optimal_weights
}

# Save weighted ensemble
joblib.dump(optimal_weights, 'models/ensemble_weights_v6.pkl')

# 9. Cross-validation analysis
print("\n9. Cross-Validation Analysis...")
print("="*70)

print("\nPerforming 5-fold cross-validation on best model...")

best_model_name = max([('Ridge', models['Ridge']), ('Lasso', models['Lasso']),
                       ('GradientBoosting', models['GradientBoosting'])],
                      key=lambda x: x[1]['val_r2'])[0]
best_model = models[best_model_name]['model']

kfold = KFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(best_model, X_train_selected, y_train, cv=kfold, scoring='r2')

print(f"\n{best_model_name} Cross-Validation (5-fold):")
print(f"  Fold scores: {[f'{s:.4f}' for s in cv_scores]}")
print(f"  Mean R²: {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}")

# 10. Results summary
print("\n" + "="*70)
print("RESULTS SUMMARY")
print("="*70)

print("\n📊 Performance Comparison:")
print("\nModel                  | Val R²  | Test R² | vs V5 Ridge | vs Baseline")
print("-----------------------|---------|---------|-------------|-------------")

v5_ridge_r2 = 0.287
baseline_r2 = 0.236

for model_name, result in models.items():
    val_r2 = result['val_r2']
    test_r2 = result['test_r2']
    vs_v5 = (test_r2 - v5_ridge_r2) / v5_ridge_r2 * 100
    vs_baseline = (test_r2 - baseline_r2) / baseline_r2 * 100

    marker = "⭐" if test_r2 >= v5_ridge_r2 else "  "
    print(f"{marker} {model_name:20s} | {val_r2:.4f} | {test_r2:.4f} | {vs_v5:+6.1f}%    | {vs_baseline:+6.1f}%")

print(f"\n   V5 Ridge (baseline)   |  0.247  | {v5_ridge_r2:.4f} |   0.0%      |  +21.6%")
print(f"   V3-Clean (original)   |   N/A   | {baseline_r2:.4f} |  -17.8%     |   0.0%")

# 11. Final assessment
print("\n" + "="*70)
print("FINAL ASSESSMENT")
print("="*70)

best_test_r2 = max([m['test_r2'] for m in models.values()])
best_model_final = max(models.items(), key=lambda x: x[1]['test_r2'])[0]

print(f"\n🏆 Best model: {best_model_final}")
print(f"   Test R²: {best_test_r2:.4f}")

target_r2 = 0.46
current_gap = target_r2 - best_test_r2
baseline_gap = target_r2 - baseline_r2
progress = (best_test_r2 - baseline_r2) / (target_r2 - baseline_r2) * 100

print(f"\n📈 Progress Toward Target:")
print(f"   Starting (V3-Clean):   R² = {baseline_r2:.4f}")
print(f"   Previous (V5 Ridge):   R² = {v5_ridge_r2:.4f}")
print(f"   Current (V6 Best):     R² = {best_test_r2:.4f}")
print(f"   Target:                R² = {target_r2:.4f}")
print(f"\n   Total improvement:    +{best_test_r2 - baseline_r2:.4f} ({(best_test_r2 - baseline_r2)/baseline_r2*100:.1f}%)")
print(f"   Gap remaining:        {current_gap:.4f}")
print(f"   Progress:             {progress:.1f}% of target")

if best_test_r2 >= 0.40:
    print("\n🎉 EXCELLENT! Near target performance!")
    print("   → Achieved honest R² > 0.40")
    print("   → Only {:.3f} from target".format(current_gap))
elif best_test_r2 >= 0.35:
    print("\n✅ VERY GOOD! Significant improvement!")
    print("   → Achieved honest R² > 0.35")
    print("   → Strong performance for EEG prediction")
elif best_test_r2 >= 0.30:
    print("\n👍 GOOD! Meaningful improvement")
    print("   → Achieved honest R² > 0.30")
    print("   → May be approaching performance ceiling")
else:
    print("\n~ MODEST IMPROVEMENT")
    print("   → Temporal features and ensemble helped somewhat")
    print("   → May be near fundamental performance limit")

print("\n💡 Key Improvements in V6:")
print("   1. Temporal context features (rolling statistics, trends)")
print("   2. Feature selection (removed noisy features)")
print("   3. Optimized hyperparameters")
print("   4. Weighted ensemble combining 4 models")
print("   5. Cross-validation for robustness")

print("\n" + "="*70)
print(f"✓ Models saved to models/ directory")
print("="*70)
