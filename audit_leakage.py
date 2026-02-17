"""
Critical audit: Check if spectral features include target PAC
"""
import numpy as np
import sys
sys.path.insert(0, 'src')

from spectral_features import SpectralFeatureExtractor

print('='*70)
print('AUDIT: Testing if spectral features leak target PAC')
print('='*70)

# Load train data
train = np.load('data/processed/train_data.npz')
X_eeg = train['windows'].squeeze(1)  # (n, 7, 500)
y_pac = train['pac']  # (n,)

print(f'\nLoaded {len(y_pac)} samples')

# Extract spectral features for first 1000 samples (faster)
n_test = min(1000, len(y_pac))
extractor = SpectralFeatureExtractor(fs=250.0)

print(f'Extracting spectral features for {n_test} samples...')
X_spectral = extractor.extract(X_eeg[:n_test])

# The MI features are in positions 35, 39, 43, 47, 51, 55, 59 (every 4th starting at 35)
# Because pac_features_flat has shape (7*4,) and MI is the first of each group of 4
mi_indices = [35 + i*4 for i in range(7)]  # [35, 39, 43, 47, 51, 55, 59]

print(f'\nMI feature indices: {mi_indices}')
print(f'Extracting MI features for 7 channels...')

# Extract MI features
mi_features = X_spectral[:, mi_indices]  # (n_test, 7)

# Compute mean MI across channels
mi_mean = mi_features.mean(axis=1)  # (n_test,)

# Get target PAC
pac_target = y_pac[:n_test]

# Compute correlation
correlation = np.corrcoef(mi_mean, pac_target)[0, 1]
r2_if_using_mi = correlation ** 2

print(f'\n❌ CRITICAL RESULT:')
print(f'  Correlation between mean(MI features) and target PAC: {correlation:.4f}')
print(f'  R² if predicting PAC from mean(MI): {r2_if_using_mi:.4f}')

print(f'\n  Observed test R²: 0.6925')
print(f'  Expected if using MI directly: ~{r2_if_using_mi:.4f}')

if correlation > 0.7:
    print(f'\n⚠️⚠️⚠️  DATA LEAKAGE CONFIRMED!')
    print(f'  The spectral features include MI (Modulation Index),')
    print(f'  which is essentially the target PAC!')
    print(f'  The model is learning to extract and average the MI features.')
    print(f'  This is NOT a genuine prediction - it\'s using the answer!')
else:
    print(f'\n  MI and PAC are not strongly correlated.')
    print(f'  The high R² is likely legitimate.')

# Additional check: Linear regression using ONLY MI features
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

lr = LinearRegression()
lr.fit(mi_features, pac_target)
pac_pred_from_mi = lr.predict(mi_features)
r2_from_mi_only = r2_score(pac_target, pac_pred_from_mi)

print(f'\n❌ VERIFICATION: Linear regression using ONLY MI features')
print(f'  R² = {r2_from_mi_only:.4f}')

if r2_from_mi_only > 0.5:
    print(f'  ⚠️  Can achieve R² > 0.5 using ONLY MI features!')
    print(f'  This confirms the high performance is due to data leakage.')

print('\n' + '='*70)
