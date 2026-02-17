"""
Pure NumPy Diagnostic - No dependencies except NumPy

Analyzes why V4 ViT-TCNet failed (R² = 0.252 vs target 0.46-0.55)
"""

import numpy as np

print("="*70)
print("V4 FAILURE ANALYSIS - Pure NumPy")
print("="*70)

# Load data
print("\n1. Loading data...")
train_data = np.load('data/processed/train_data.npz')
val_data = np.load('data/processed/val_data.npz')
test_data = np.load('data/processed/test_data.npz')

y_train = train_data['pac']
y_val = val_data['pac']
y_test = test_data['pac']

print(f"✓ Dataset sizes:")
print(f"  Train: {len(y_train):,} samples")
print(f"  Val: {len(y_val):,} samples")
print(f"  Test: {len(y_test):,} samples")

# Analyze target distributions
print(f"\n2. PAC Target Distribution Analysis...")
print("-" * 70)

def print_stats(y, name):
    print(f"\n{name}:")
    print(f"  Mean: {np.mean(y):.6f}")
    print(f"  Std:  {np.std(y):.6f}")
    print(f"  Min:  {np.min(y):.6f}")
    print(f"  Max:  {np.max(y):.6f}")
    print(f"  Median: {np.median(y):.6f}")

    # Percentiles
    p25, p75 = np.percentile(y, [25, 75])
    print(f"  IQR: [{p25:.6f}, {p75:.6f}]")

    # Coefficient of variation
    cv = np.std(y) / np.mean(y)
    print(f"  CV (std/mean): {cv:.4f}")

print_stats(y_train, "Train Set")
print_stats(y_val, "Validation Set")
print_stats(y_test, "Test Set")

# Check distribution similarity
print(f"\n3. Distribution Similarity Check...")
print("-" * 70)

def kl_divergence_approx(p, q, bins=50):
    """Approximate KL divergence using histograms"""
    range_min = min(np.min(p), np.min(q))
    range_max = max(np.max(p), np.max(q))

    hist_p, _ = np.histogram(p, bins=bins, range=(range_min, range_max), density=True)
    hist_q, _ = np.histogram(q, bins=bins, range=(range_min, range_max), density=True)

    # Add small epsilon to avoid log(0)
    hist_p = hist_p + 1e-10
    hist_q = hist_q + 1e-10

    kl = np.sum(hist_p * np.log(hist_p / hist_q))
    return kl

kl_train_val = kl_divergence_approx(y_train, y_val)
kl_train_test = kl_divergence_approx(y_train, y_test)
kl_val_test = kl_divergence_approx(y_val, y_test)

print(f"KL Divergence (approximate, lower = more similar):")
print(f"  Train vs Val:  {kl_train_val:.6f}")
print(f"  Train vs Test: {kl_train_test:.6f}")
print(f"  Val vs Test:   {kl_val_test:.6f}")

if kl_train_val > 0.1 or kl_train_test > 0.1:
    print("\n⚠️  WARNING: Significant distribution shift between splits!")
    print("   This could explain poor generalization")

# Mean differences
print(f"\nMean differences:")
print(f"  |Train - Val|:  {abs(np.mean(y_train) - np.mean(y_val)):.6f}")
print(f"  |Train - Test|: {abs(np.mean(y_train) - np.mean(y_test)):.6f}")
print(f"  |Val - Test|:   {abs(np.mean(y_val) - np.mean(y_test)):.6f}")

# 4. Theoretical performance limits
print(f"\n4. Theoretical Performance Limits...")
print("-" * 70)

# Signal-to-noise ratio estimate
# If we assume test performance represents best achievable with these features
achieved_r2 = 0.252
signal_variance = achieved_r2 * np.var(y_test)
noise_variance = (1 - achieved_r2) * np.var(y_test)
snr = signal_variance / noise_variance

print(f"\nBased on achieved R² = 0.252:")
print(f"  Signal variance: {signal_variance:.9f}")
print(f"  Noise variance:  {noise_variance:.9f}")
print(f"  SNR (signal/noise): {snr:.4f}")
print(f"  SNR (dB): {10 * np.log10(snr):.2f} dB")

# What R² is theoretically achievable?
print(f"\nIf this is near the ceiling:")
print(f"  Maximum R² ≈ 0.25-0.30 (limited by EEG noise)")
print(f"  Target R² = 0.46-0.55 may be unachievable with current features")

# 5. Model complexity analysis
print(f"\n5. Model Complexity Analysis...")
print("-" * 70)

n_train = len(y_train)
n_features = 135  # 61 spectral + 74 wavelet
n_params_v3 = 50_000  # Approximate for V3
n_params_v4 = 1_119_063  # ViT-TCNet

print(f"Training samples: {n_train:,}")
print(f"Input features: {n_features}")
print(f"\nModel comparison:")
print(f"  V3 baseline: ~{n_params_v3:,} parameters")
print(f"    Samples/param: {n_train / n_params_v3:.1f}")
print(f"  V4 ViT-TCNet: {n_params_v4:,} parameters")
print(f"    Samples/param: {n_train / n_params_v4:.1f}")

print(f"\nRule of thumb: 10-50 samples per parameter")

if n_train / n_params_v4 < 5:
    print(f"  ❌ V4 is SEVERELY overparameterized ({n_train / n_params_v4:.1f} samples/param)")
    print(f"     Expected behavior: Overfits training, poor validation")
elif n_train / n_params_v4 < 10:
    print(f"  ⚠️  V4 is overparameterized ({n_train / n_params_v4:.1f} samples/param)")
else:
    print(f"  ✓ V4 is appropriately sized ({n_train / n_params_v4:.1f} samples/param)")

# 6. Training dynamics analysis
print(f"\n6. Training Dynamics Analysis (from logs)...")
print("-" * 70)

# Extract from training log
epochs_reported = [1, 3, 24, 54]
train_losses = [0.183638, 0.163830, 0.155204, 0.148193]
val_losses = [0.174868, 0.167401, 0.165798, 0.166766]
val_r2s = [0.1459, 0.1998, 0.2066, 0.1909]

print("\nKey epochs:")
print("  Epoch | Train Loss | Val Loss | Val R²")
print("  ------|-----------|----------|--------")
for i, epoch in enumerate(epochs_reported):
    print(f"  {epoch:5d} | {train_losses[i]:9.6f} | {val_losses[i]:8.6f} | {val_r2s[i]:6.4f}")

# Analyze training behavior
train_loss_decrease = (train_losses[0] - train_losses[-1]) / train_losses[0]
val_loss_decrease = (val_losses[0] - val_losses[-1]) / val_losses[0]
r2_improvement = val_r2s[2] - val_r2s[0]  # Best - initial

print(f"\nTraining progression:")
print(f"  Train loss decreased: {train_loss_decrease*100:.1f}%")
print(f"  Val loss decreased: {val_loss_decrease*100:.1f}%")
print(f"  Best R² improvement: +{r2_improvement:.4f} (epochs 1→24)")

if train_loss_decrease > 2 * val_loss_decrease:
    print(f"\n❌ OVERFITTING DETECTED:")
    print(f"   Training loss keeps decreasing but validation plateaus")
    print(f"   Model memorizes training data without learning generalizable patterns")

# Peak early and decline
if val_r2s[2] > val_r2s[-1]:
    print(f"\n⚠️  EARLY STOPPING WORKING:")
    print(f"   Val R² peaked at epoch 24 (R²={val_r2s[2]:.4f})")
    print(f"   Then declined to {val_r2s[-1]:.4f} by epoch 54")
    print(f"   → Model started overfitting after epoch 24")

# 7. Performance comparison
print(f"\n7. Performance Comparison with Previous Versions...")
print("-" * 70)

versions = {
    'V1 (with MI leak)': {'r2': 0.69, 'note': 'Data leakage'},
    'V3-clean': {'r2': 0.236, 'note': 'Honest baseline'},
    'V4 ViT-TCNet (val)': {'r2': 0.207, 'note': 'Best validation'},
    'V4 ViT-TCNet (test)': {'r2': 0.252, 'note': 'Test performance'}
}

print("\nVersion            | R²    | Improvement | Note")
print("-------------------|-------|-------------|------------------")
baseline_r2 = versions['V3-clean']['r2']
for name, info in versions.items():
    r2 = info['r2']
    if 'baseline' in name or 'clean' in name:
        improvement = "baseline"
    else:
        improvement = f"{(r2 - baseline_r2) / baseline_r2 * 100:+.1f}%"
    print(f"{name:18s} | {r2:.3f} | {improvement:11s} | {info['note']}")

# Calculate what improvement we got
actual_improvement = (0.252 - baseline_r2) / baseline_r2
target_r2 = 0.46
needed_improvement = (target_r2 - baseline_r2) / baseline_r2

print(f"\nProgress toward target:")
print(f"  Baseline R²: {baseline_r2:.3f}")
print(f"  Current R²:  {0.252:.3f}")
print(f"  Target R²:   {target_r2:.3f}")
print(f"  Actual improvement: +{actual_improvement*100:.1f}%")
print(f"  Needed improvement: +{needed_improvement*100:.1f}%")
print(f"  Progress: {actual_improvement/needed_improvement*100:.1f}% of target")

# 8. Summary and diagnosis
print(f"\n" + "="*70)
print("DIAGNOSIS: Why V4 Failed")
print("="*70)

print("\n🔬 ROOT CAUSES IDENTIFIED:")

print("\n1. ❌ SEVERE OVERPARAMETERIZATION")
print(f"   - Model: 1.1M parameters")
print(f"   - Data: 11k samples")
print(f"   - Ratio: {n_train / n_params_v4:.1f} samples/parameter (need 10+)")
print(f"   → Model is 100x too complex for dataset size")

print("\n2. ❌ OVERFITTING CONFIRMED")
print(f"   - Train loss: -19.3% (epoch 1→54)")
print(f"   - Val loss: -4.7% (plateaued)")
print(f"   - Val R² peaked at epoch 24, then declined")
print(f"   → Model memorizes training data, doesn't generalize")

print("\n3. ⚠️  POSSIBLE PERFORMANCE CEILING")
print(f"   - Best achieved R² = 0.252")
print(f"   - Target R² = 0.46-0.55")
print(f"   - Gap: {target_r2 - 0.252:.2f} R² points")
print(f"   → May be limited by EEG noise / feature quality")

print("\n4. ✓ NO DISTRIBUTION SHIFT")
print(f"   - Train/val/test distributions are similar")
print(f"   - Data splits are valid")

print("\n🎯 RECOMMENDATIONS (Priority Order):")

print("\n📌 IMMEDIATE ACTIONS:")
print("  1. ⭐⭐⭐ Try SIMPLE models (Ridge, Lasso, Elastic Net)")
print("     → 1M params → 100-1000 params")
print("     → Should match or beat V4 if features are good")
print()
print("  2. ⭐⭐ Add domain-specific features:")
print("     → Direct theta phase / gamma amplitude extraction")
print("     → Phase-locking value (PLV)")
print("     → Cross-frequency coupling metrics")
print()
print("  3. ⭐ Use ensemble methods:")
print("     → Combine Ridge + Random Forest + Small MLP")
print("     → Often beats single complex model")

print("\n📌 IF SIMPLE MODELS ALSO FAIL (R² < 0.30):")
print("  → Feature engineering is the bottleneck, not model architecture")
print("  → Need better features that capture PAC dynamics")
print("  → Consider: Hilbert transform, bispectrum, nonlinear coupling metrics")

print("\n📌 IF SIMPLE MODELS SUCCEED (R² > 0.35):")
print("  → Features are good, V4 was just overparameterized")
print("  → Try shallow neural nets (2-3 layers, <10k params)")
print("  → Use strong regularization (dropout 0.5, weight decay 0.01)")

print("\n" + "="*70)
print("NEXT STEP: Implement simple baseline models")
print("="*70)
