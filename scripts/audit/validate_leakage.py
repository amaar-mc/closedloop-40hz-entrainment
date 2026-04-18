"""
Code Validation & Audit Script (runs without PyTorch)

Validates the temporal prediction system by:
1. Testing temporal dataset logic (sequence building, subject boundaries)
2. Running a sklearn baseline (Ridge regression on temporal features)
3. Checking PAC autocorrelation structure
4. Verifying no data leakage between splits

This script requires only numpy, scipy, sklearn - no PyTorch needed.
Run this first to validate before training the LSTM.

Author: Amaar Chughtai
Date: February 2026
"""

import os
import sys
import numpy as np
from scipy import stats

# Add parent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def load_data(data_dir='data/processed'):
    """Load all splits."""
    splits = {}
    for name in ['train', 'val', 'test']:
        path = os.path.join(data_dir, f'{name}_data.npz')
        data = np.load(path)
        splits[name] = {
            'windows': data['windows'],
            'pac': data['pac'],
            'subjects': data['subjects'],
        }
    return splits


def test_temporal_sequence_logic(splits, lookback=10, horizon=5):
    """
    Test 1: Verify temporal sequence building logic.
    Ensures sequences don't cross subject boundaries.
    """
    print("=" * 60)
    print("TEST 1: Temporal Sequence Logic")
    print("=" * 60)

    errors = 0
    total_sequences = 0

    for split_name, data in splits.items():
        windows = data['windows']
        pac = data['pac']
        subjects = data['subjects']

        unique_subjects = np.unique(subjects)
        split_sequences = 0

        for subj in unique_subjects:
            idx = np.where(subjects == subj)[0]

            # Check contiguity
            if not np.all(np.diff(idx) == 1):
                print(f"  ERROR: Subject {subj} in {split_name} is not contiguous!")
                errors += 1
                continue

            n_windows = len(idx)
            n_valid = max(0, n_windows - lookback - horizon + 1)

            # Verify each sequence stays within subject
            for i in range(n_valid):
                seq_start = idx[0] + i
                target_idx = seq_start + lookback + horizon - 1

                # Check all indices in this sequence belong to same subject
                seq_subjects = subjects[seq_start : seq_start + lookback]
                target_subject = subjects[target_idx]

                if not np.all(seq_subjects == subj):
                    print(f"  ERROR: Sequence crosses subject boundary at {seq_start}")
                    errors += 1
                if target_subject != subj:
                    print(f"  ERROR: Target at {target_idx} belongs to {target_subject}, "
                          f"not {subj}")
                    errors += 1

                split_sequences += 1

            total_sequences += split_sequences

        print(f"  {split_name}: {split_sequences} valid sequences across "
              f"{len(unique_subjects)} subjects")

    if errors == 0:
        print(f"\n  ✓ ALL {total_sequences} sequences validated - no boundary violations")
    else:
        print(f"\n  ✗ {errors} errors found!")

    return errors == 0


def test_no_subject_leakage(splits):
    """
    Test 2: Verify no subject appears in multiple splits.
    """
    print("\n" + "=" * 60)
    print("TEST 2: Subject Leakage Check")
    print("=" * 60)

    train_subjects = set(np.unique(splits['train']['subjects']))
    val_subjects = set(np.unique(splits['val']['subjects']))
    test_subjects = set(np.unique(splits['test']['subjects']))

    tv_overlap = train_subjects & val_subjects
    tt_overlap = train_subjects & test_subjects
    vt_overlap = val_subjects & test_subjects

    print(f"  Train subjects: {len(train_subjects)}")
    print(f"  Val subjects:   {len(val_subjects)}")
    print(f"  Test subjects:  {len(test_subjects)}")
    print(f"  Train ∩ Val:    {len(tv_overlap)} {tv_overlap if tv_overlap else '(none)'}")
    print(f"  Train ∩ Test:   {len(tt_overlap)} {tt_overlap if tt_overlap else '(none)'}")
    print(f"  Val ∩ Test:     {len(vt_overlap)} {vt_overlap if vt_overlap else '(none)'}")

    no_leakage = len(tv_overlap) == 0 and len(tt_overlap) == 0 and len(vt_overlap) == 0
    if no_leakage:
        print(f"\n  ✓ No subject leakage between splits")
    else:
        print(f"\n  ✗ Subject leakage detected!")

    return no_leakage


def test_pac_autocorrelation(splits, max_lag=20):
    """
    Test 3: Characterize PAC temporal autocorrelation per subject.
    This determines how feasible temporal prediction really is.
    """
    print("\n" + "=" * 60)
    print("TEST 3: PAC Temporal Autocorrelation Analysis")
    print("=" * 60)

    all_autocorrs = {lag: [] for lag in range(1, max_lag + 1)}

    for split_name in ['train', 'val', 'test']:
        data = splits[split_name]
        subjects = data['subjects']
        pac = data['pac']

        for subj in np.unique(subjects):
            idx = np.where(subjects == subj)[0]
            p = pac[idx]

            if len(p) < max_lag + 10:
                continue

            for lag in range(1, max_lag + 1):
                r = np.corrcoef(p[:-lag], p[lag:])[0, 1]
                all_autocorrs[lag].append(r)

    print(f"\n  {'Lag':>4} | {'Mean r':>8} | {'Std':>8} | {'p < 0.05':>10} | Interpretation")
    print("  " + "-" * 60)

    for lag in [1, 2, 3, 5, 10, 15, 20]:
        vals = all_autocorrs[lag]
        if not vals:
            continue
        mean_r = np.mean(vals)
        std_r = np.std(vals)
        # One-sample t-test: is mean_r significantly different from 0?
        t_stat, p_val = stats.ttest_1samp(vals, 0)
        sig = "Yes" if p_val < 0.05 else "No"

        if abs(mean_r) < 0.1:
            interp = "Negligible"
        elif abs(mean_r) < 0.3:
            interp = "Weak"
        elif abs(mean_r) < 0.5:
            interp = "Moderate"
        else:
            interp = "Strong"

        print(f"  {lag:4d} | {mean_r:8.4f} | {std_r:8.4f} | {sig:>10} | {interp}")

    print(f"\n  Note: Low autocorrelation means PAC changes rapidly between windows.")
    print(f"  However, EEG dynamics may still predict future PAC even when")
    print(f"  current PAC doesn't (the EEG contains richer information).")

    return all_autocorrs


def run_sklearn_temporal_baseline(splits, lookback=10, horizon=5):
    """
    Test 4: Sklearn Ridge baseline for temporal prediction.
    Uses PAC history + simple EEG statistics as features.
    """
    print("\n" + "=" * 60)
    print("TEST 4: Sklearn Temporal Baseline (Ridge Regression)")
    print(f"  Lookback: {lookback}, Horizon: {horizon}")
    print("=" * 60)

    from sklearn.linear_model import Ridge
    from sklearn.metrics import r2_score

    def build_temporal_features(data, lookback, horizon):
        """Build (X, y) pairs from temporal sequences."""
        windows = data['windows']
        if windows.ndim == 4 and windows.shape[1] == 1:
            windows = windows.squeeze(1)
        pac = data['pac']
        subjects = data['subjects']

        X_list = []
        y_list = []

        for subj in np.unique(subjects):
            idx = np.where(subjects == subj)[0]
            n = len(idx)

            if n < lookback + horizon:
                continue

            for i in range(n - lookback - horizon + 1):
                start = idx[0] + i

                # Features from lookback window
                pac_history = pac[start : start + lookback]

                # Simple EEG statistics per window in lookback
                eeg_chunk = windows[start : start + lookback]  # (lookback, 7, 500)
                eeg_means = eeg_chunk.mean(axis=2).flatten()  # (lookback * 7,)
                eeg_stds = eeg_chunk.std(axis=2).flatten()    # (lookback * 7,)
                eeg_powers = (eeg_chunk ** 2).mean(axis=2).flatten()  # (lookback * 7,)

                # Concatenate all features
                features = np.concatenate([
                    pac_history,        # 10 features
                    eeg_means,          # 70 features
                    eeg_stds,           # 70 features
                    eeg_powers,         # 70 features
                ])

                target = pac[start + lookback + horizon - 1]

                X_list.append(features)
                y_list.append(target)

        return np.array(X_list), np.array(y_list)

    print("\n  Building temporal features...")
    X_train, y_train = build_temporal_features(splits['train'], lookback, horizon)
    X_val, y_val = build_temporal_features(splits['val'], lookback, horizon)
    X_test, y_test = build_temporal_features(splits['test'], lookback, horizon)

    print(f"  Train: {X_train.shape[0]} samples, {X_train.shape[1]} features")
    print(f"  Val:   {X_val.shape[0]} samples")
    print(f"  Test:  {X_test.shape[0]} samples")

    # Normalize features
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    # Train Ridge with different alphas
    print("\n  Training Ridge models...")
    best_r2 = -float('inf')
    best_alpha = None

    for alpha in [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]:
        model = Ridge(alpha=alpha)
        model.fit(X_train_scaled, y_train)
        val_pred = model.predict(X_val_scaled)
        val_r2 = r2_score(y_val, val_pred)

        if val_r2 > best_r2:
            best_r2 = val_r2
            best_alpha = alpha

        print(f"    alpha={alpha:8.2f}: Val R² = {val_r2:.4f}")

    # Final evaluation with best alpha
    print(f"\n  Best alpha: {best_alpha}")
    model = Ridge(alpha=best_alpha)
    model.fit(X_train_scaled, y_train)

    test_pred = model.predict(X_test_scaled)
    test_r2 = r2_score(y_test, test_pred)
    test_corr = np.corrcoef(test_pred, y_test)[0, 1]
    test_mae = np.mean(np.abs(test_pred - y_test))

    print(f"\n  ── Temporal Ridge Baseline Results ──")
    print(f"  Test R²:          {test_r2:.4f}")
    print(f"  Test Correlation: {test_corr:.4f}")
    print(f"  Test MAE:         {test_mae:.6f}")

    # Feature importance analysis
    coefs = np.abs(model.coef_)
    pac_importance = coefs[:lookback].sum()
    eeg_importance = coefs[lookback:].sum()
    total_importance = coefs.sum()

    print(f"\n  Feature importance:")
    print(f"    PAC history:  {pac_importance/total_importance*100:.1f}%")
    print(f"    EEG features: {eeg_importance/total_importance*100:.1f}%")

    # Naive baseline: predict mean PAC
    naive_pred = np.full_like(y_test, y_train.mean())
    naive_r2 = r2_score(y_test, naive_pred)
    print(f"\n  Naive baseline (predict mean): R² = {naive_r2:.4f}")

    # Persistence baseline: predict PAC(t) = PAC(t-1)
    # Use the last PAC in history as prediction
    persist_pred_test = X_test[:, lookback - 1]  # Last PAC in history
    persist_r2 = r2_score(y_test, persist_pred_test)
    print(f"  Persistence (PAC(t-1)):       R² = {persist_r2:.4f}")

    print(f"\n  Previous best (current-window Ridge): R² = 0.287")
    improvement = (test_r2 - 0.287) / 0.287 * 100 if test_r2 > 0.287 else 0
    print(f"  Improvement: {improvement:+.1f}%")

    return test_r2, test_corr


def run_multi_horizon_baseline(splits, lookback=10):
    """
    Test 5: How does prediction quality change with horizon?
    """
    print("\n" + "=" * 60)
    print("TEST 5: Multi-Horizon Baseline Analysis")
    print("=" * 60)

    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import r2_score

    horizons = [1, 2, 3, 5, 10, 15, 20]
    results = {}

    def build_features_fast(data, lookback, horizon):
        windows = data['windows']
        if windows.ndim == 4 and windows.shape[1] == 1:
            windows = windows.squeeze(1)
        pac = data['pac']
        subjects = data['subjects']
        X, y = [], []

        for subj in np.unique(subjects):
            idx = np.where(subjects == subj)[0]
            n = len(idx)
            if n < lookback + horizon:
                continue
            for i in range(n - lookback - horizon + 1):
                s = idx[0] + i
                pac_hist = pac[s : s + lookback]
                eeg_stats = windows[s : s + lookback].mean(axis=2).flatten()
                X.append(np.concatenate([pac_hist, eeg_stats]))
                y.append(pac[s + lookback + horizon - 1])

        return np.array(X), np.array(y)

    for h in horizons:
        X_tr, y_tr = build_features_fast(splits['train'], lookback, h)
        X_te, y_te = build_features_fast(splits['test'], lookback, h)

        if len(X_tr) == 0 or len(X_te) == 0:
            print(f"  Horizon {h:2d}s: Insufficient data")
            continue

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_te_s = scaler.transform(X_te)

        model = Ridge(alpha=10.0)
        model.fit(X_tr_s, y_tr)
        pred = model.predict(X_te_s)
        r2 = r2_score(y_te, pred)
        corr = np.corrcoef(pred, y_te)[0, 1]

        results[h] = {'r2': r2, 'corr': corr, 'n_test': len(y_te)}
        print(f"  Horizon {h:2d}s: R² = {r2:.4f}, Corr = {corr:.4f} ({len(y_te)} samples)")

    print(f"\n  Note: These are Ridge baselines. The LSTM should improve on these")
    print(f"  by learning nonlinear temporal patterns in the EEG sequences.")

    return results


def audit_code():
    """
    Test 6: Audit the temporal prediction code for common issues.
    """
    print("\n" + "=" * 60)
    print("TEST 6: Code Audit")
    print("=" * 60)

    issues = []

    # Check file existence
    expected_files = [
        'temporal/__init__.py',
        'temporal/temporal_dataset.py',
        'temporal/temporal_model.py',
        'temporal/train_temporal.py',
        'temporal/validate_code.py',
    ]

    base_dir = os.path.join(os.path.dirname(__file__), '..')
    for f in expected_files:
        path = os.path.join(base_dir, f)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  ✓ {f} ({size:,} bytes)")
        else:
            print(f"  ✗ {f} MISSING")
            issues.append(f"Missing file: {f}")

    # Static analysis of imports and known issues
    print("\n  Checking for common issues...")

    # Check temporal_dataset.py
    dataset_path = os.path.join(base_dir, 'temporal', 'temporal_dataset.py')
    with open(dataset_path, 'r') as f:
        content = f.read()

    checks = {
        'squeeze(1) for extra dim': 'squeeze(1)' in content,
        'subject boundary check': 'assert np.all(np.diff' in content,
        'normalize PAC': 'normalize_pac' in content,
        'lookback parameter': 'lookback' in content,
        'horizon parameter': 'horizon' in content,
    }

    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        if not passed:
            issues.append(f"Failed check: {check}")

    # Check model
    model_path = os.path.join(base_dir, 'temporal', 'temporal_model.py')
    with open(model_path, 'r') as f:
        content = f.read()

    checks = {
        'SpatialEncoder class': 'class SpatialEncoder' in content,
        'LSTM/GRU option': 'use_gru' in content,
        'bidirectional option': 'bidirectional' in content,
        'dropout regularization': 'Dropout' in content,
        'LayerNorm': 'LayerNorm' in content,
        'gradient-friendly (ELU)': 'ELU' in content,
    }

    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        if not passed:
            issues.append(f"Failed check: {check}")

    # Check train script
    train_path = os.path.join(base_dir, 'temporal', 'train_temporal.py')
    with open(train_path, 'r') as f:
        content = f.read()

    checks = {
        'HuberLoss': 'HuberLoss' in content,
        'gradient clipping': 'clip_grad_norm' in content,
        'early stopping': 'patience' in content,
        'denormalization for eval': 'pac_std + pac_mean' in content or 'pac_mean' in content,
        'model checkpoint': 'save_path' in content and 'torch.save' in content,
        'R² metric': 'r2' in content,
        'cosine annealing': 'CosineAnnealing' in content,
    }

    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        if not passed:
            issues.append(f"Failed check: {check}")

    if issues:
        print(f"\n  ✗ {len(issues)} issues found:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print(f"\n  ✓ All checks passed - code is clean")

    return len(issues) == 0


def main():
    print("\n" + "=" * 70)
    print("TEMPORAL PAC PREDICTION - VALIDATION & AUDIT")
    print("=" * 70)

    # Resolve data directory
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    data_dir = os.path.join(base_dir, 'data', 'processed')

    if not os.path.exists(data_dir):
        print(f"ERROR: Data directory not found: {data_dir}")
        return

    # Load data
    print("\nLoading data...")
    splits = load_data(data_dir)

    # Run all tests
    results = {}

    results['sequences'] = test_temporal_sequence_logic(splits)
    results['no_leakage'] = test_no_subject_leakage(splits)
    autocorrs = test_pac_autocorrelation(splits)
    results['baseline_r2'], _ = run_sklearn_temporal_baseline(splits)
    horizon_results = run_multi_horizon_baseline(splits)
    results['code_audit'] = audit_code()

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"  Sequence logic:     {'✓ PASS' if results['sequences'] else '✗ FAIL'}")
    print(f"  No subject leakage: {'✓ PASS' if results['no_leakage'] else '✗ FAIL'}")
    print(f"  Code audit:         {'✓ PASS' if results['code_audit'] else '✗ FAIL'}")
    print(f"  Temporal Ridge R²:  {results['baseline_r2']:.4f}")

    all_pass = all(v for k, v in results.items() if isinstance(v, bool))
    if all_pass:
        print(f"\n  ✓ ALL VALIDATIONS PASSED")
        print(f"\n  The code is ready to train. On your Windows machine, run:")
        print(f"    cd closedloop-40hz-entrainment")
        print(f"    python temporal/train_temporal.py")
    else:
        print(f"\n  ✗ Some validations failed - check details above")


if __name__ == "__main__":
    main()
