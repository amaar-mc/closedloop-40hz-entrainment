"""
Debug Data Leakage

Identify which features are causing R² = 0.9999 perfect prediction.
"""

import numpy as np
import joblib
from sklearn.metrics import r2_score

print("="*70)
print("DEBUG: Data Leakage Investigation")
print("="*70)

# Load the trained model
ridge = joblib.load('models/ridge_v5_enhanced.pkl')
scaler = joblib.load('models/scaler_v5_enhanced.pkl')

print(f"\n✓ Model loaded")
print(f"  Total features: {len(ridge.coef_)}")
print(f"  Model alpha: {ridge.alpha_:.6f}")

# Load test data
test_data = np.load('data/processed/test_data.npz')
y_test = test_data['pac']

print(f"✓ Test data loaded: {len(y_test)} samples")

# Load the features that were used for training
# (We'll load them from somewhere or recompute a small sample)
print("\nStrategy: Test each feature group individually")
print("-"*70)

# We'll use feature indices to test different groups
n_features = len(ridge.coef_)
print(f"\nTotal features in model: {n_features}")

# Feature group definitions
feature_groups = {
    'Spectral (0-60)': (0, 61),
    'Wavelet (61-134)': (61, 135),
    'PAC features (135-250)': (135, 251)
}

# Get feature importance
coef = ridge.coef_
abs_coef = np.abs(coef)

print("\n📊 Coefficient Statistics by Feature Group:")
print("-"*70)

for group_name, (start, end) in feature_groups.items():
    group_coef = abs_coef[start:end]
    print(f"\n{group_name}:")
    print(f"  Mean |coef|: {np.mean(group_coef):.9f}")
    print(f"  Max |coef|:  {np.max(group_coef):.9f}")
    print(f"  Sum |coef|:  {np.sum(group_coef):.9f}")
    print(f"  % of total:  {100 * np.sum(group_coef) / np.sum(abs_coef):.1f}%")

# Find top features
print("\n📌 Top 30 Features by Absolute Coefficient:")
print("-"*70)

top_indices = np.argsort(abs_coef)[::-1]

for i in range(30):
    idx = top_indices[i]

    # Determine which group
    if idx < 61:
        group = "Spectral"
        local_idx = idx
    elif idx < 135:
        group = "Wavelet"
        local_idx = idx - 61
    else:
        group = "PAC"
        local_idx = idx - 135

    print(f"  {i+1:2d}. Feature {idx:3d} ({group:8s} #{local_idx:3d}): {coef[idx]:+.9f} (|coef|={abs_coef[idx]:.9f})")

# Check PAC feature breakdown
print("\n📊 PAC Feature Group Breakdown (135-250):")
print("-"*70)

pac_feature_sizes = [
    ('PAC_MI (direct MI)', 7),
    ('PAC_corr', 7),
    ('PreferredPhase', 7),
    ('PhaseConsistency', 7),
    ('ThetaPLV', 21),
    ('GammaCorr', 21),
    ('CouplingProfile', 18),
    ('ThetaGammaAmpCorr', 7),
    ('ThetaAsymmetry', 7),
    ('BurstPhaseMean', 7),
    ('BurstPhaseStd', 7)
]

start_idx = 135
for group_name, size in pac_feature_sizes:
    end_idx = start_idx + size
    group_coef = abs_coef[start_idx:end_idx]

    print(f"\n{group_name} (features {start_idx}-{end_idx-1}):")
    print(f"  Mean |coef|: {np.mean(group_coef):.9f}")
    print(f"  Max |coef|:  {np.max(group_coef):.9f}")
    print(f"  Sum |coef|:  {np.sum(group_coef):.9f}")

    start_idx = end_idx

# Hypothesis: Check if PAC_MI features directly leak the target
print("\n" + "="*70)
print("HYPOTHESIS TEST: Do PAC features leak the target?")
print("="*70)

print("\nThe PAC_MI features (135-141) compute Modulation Index directly.")
print("If target PAC was computed using MI, these features = target!")
print("\nChecking coefficient pattern...")

pac_mi_coefs = coef[135:142]  # First 7 PAC features (direct MI)
pac_corr_coefs = coef[142:149]  # Next 7 (PAC correlation)

print(f"\nPAC_MI coefficients (should be ~1 if leaking):")
for i, c in enumerate(pac_mi_coefs):
    print(f"  Channel {i}: {c:+.9f}")

print(f"\nPAC_corr coefficients:")
for i, c in enumerate(pac_corr_coefs):
    print(f"  Channel {i}: {c:+.9f}")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)

pac_coef_sum = np.sum(abs_coef[135:])  # All PAC features
total_coef_sum = np.sum(abs_coef)
pac_percentage = 100 * pac_coef_sum / total_coef_sum

print(f"\nPAC features account for {pac_percentage:.1f}% of total coefficient magnitude")

if pac_percentage > 80:
    print("\n❌ SEVERE DATA LEAKAGE CONFIRMED")
    print("   PAC features dominate the model")
    print("   They are directly computing what we're trying to predict")
elif pac_percentage > 50:
    print("\n⚠️  SIGNIFICANT DATA LEAKAGE LIKELY")
    print("   PAC features have excessive influence")
else:
    print("\n~ MODERATE CONTRIBUTION")
    print("   PAC features help but don't dominate")
    print("   May not be pure leakage")

print("\n💡 RECOMMENDATION:")
print("   Remove PAC features (135-250) and retrain")
print("   Use only spectral + wavelet features (0-134)")
print("   Expected honest R²: ~0.287 (from previous result)")

print("\n" + "="*70)
